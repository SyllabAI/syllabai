# Clean-and-Verify Protocol for QP/MS Markdown (Stage B)

**Status:** Proposal v1.1 — grammar contract RATIFIED against `GlmOcrMarkdownParser` v1.2.0 (syllabai-parser `5c93317` tree, 2026-09-17); protocol execution itself not yet run
**Date:** 2026-09-17
**Tracker row:** T-C17 (registered in the master workbook TODO.md, content-ops track)
**Governing spec sections:** Master Spec §8 (canonical document format), §9 (content-processing architecture), §10 (question bank), ADR-021 (Markdown as durable interchange; PostgreSQL canonical)
**Related rows:** T-C02/T-C03 (GLM-OCR bridge + pair CLI), T-C04 (batch gate), T-C06 (corpus converter — this protocol is an upstream input), T-C16 (corpus_ops tooling — sibling proposal), T-C13 (bench — downstream consumer of the cleaned corpus)
**Code touchpoints:** `syllabai-parser` → `tools/glmocr/health.py`, `tools/glmocr/atomize.py`, `tools/glmocr/conformance.py`, `GlmOcrPairCli`; `syllabai-core` → `GlmOcrIngestionService` (T-C02), `ContentIngestionService` (T-013)

---

## 1. Problem (evidence, not vibes)

The GLM-OCR markdown corpus carries non-question and non-marking content that the
extractors then have to tolerate. The parser README's own honesty notes record the
consequence: the real 4CH0/1C January 2012 pair yields **27 draft questions from a
20-question paper ("boilerplate spillover")**, and `GLM_OCR_CONTENT.md` states plainly
that *"source Markdown is not itself semantic validation."* Every downstream consumer —
the question extractors, the mark-scheme extractor, the atomizer, the health gate,
eventually the retrieval bench — inherits that noise.

Today the pipeline's answer is `reviewRequired=true` and human review. That is correct
as a safety property and insufficient as a content-operations strategy: the noise is
*known, mechanical, and located* (covers, instruction pages, formula sheets, data
booklets, marking-guidance preambles), which makes it suitable for a disciplined
removal pass **before** extraction, not after.

This protocol defines that pass. It has never been run; the corpus currently in
`SyllabAI/Past-Papers` (`paper 1/`, `paper 2/`) is raw GLM-OCR output with operator
image cleanup only.

## 2. What this protocol is — and is not

**It is:**

- a **subtractive** editing pass over QP/MS markdown plus a **bounded, logged** local-repair pass;
- a **verification protocol** with objective, machine-checkable acceptance gates;
- a **provenance-preserving** operation: the raw artifact is frozen, the cleaned artifact
  is a new derived artifact with its own checksum and a sidecar report linking both.

**It is not:**

- re-authoring, paraphrasing, or "improving" question content;
- a change to the GLM-OCR output grammar (see §3);
- semantic validation: cleaning can never promote anything out of
  `SUGGESTED`/`reviewRequired`; the teacher/SME validation gates remain the only
  promotion path (Master Spec §7, T-C02 bridge contract);
- a replacement for the operator image-cleanup loop (Stage A / T-C16) — cleaning
  assumes image references are already final.

**The one-sentence rule:** *the agent deletes blocks and repairs local defects; it never
rewrites the document.*

## 3. The grammar contract — invariants that MUST survive cleaning

The Java parser (`GlmOcrMarkdownParser` v1.2.0) and its Python behavioral twin
(`tools/glmocr/canonical.py`) are calibrated to the GLM-OCR output grammar. A cleaned
file that silently violates the grammar shifts extraction calibration for every future
session. The contract below is **ratified against the parser source** (2026-09-17): each
invariant cites the parser behavior that enforces it. The following survive **verbatim
in structure**:

1. **Heading hierarchy** — the parser recognizes headings via `^#{1,6}\s+(.+?)\s*$`
   (levels 1–6, one whitespace, trimmed). Question headings (`## Question N` / numbering
   lines in both printed styles `1:` and `1 `) and part headings (`### (a)`, `(a)(i)`,
   roman parts) keep their exact level and printed label.
2. **Marks notation** — inline `(N)` markers stay *exactly as printed* (the MS extractor
   splits mark points on them; the CMC convention "never guess marks" applies downstream).
   Part labels `(a)`–`(h)` and roman `(i)`-style labels are additionally **structural
   predicates** inside the parser's bounded scans (`PART_LABEL = ^\([a-h]\)\s`,
   `ROMAN_LABEL = ^\([ivx]+\)\s`) — their printed form, including the space after the
   closing paren, is load-bearing for parsing behavior, not just display.
3. **QWC markers** — ratified corpus reality (real-corpus syntax report §identity):
   QWC asterisks are *inline printed text* — `*(c) Diagram 1 shows…` (June Q18) and
   `*14` (1A MS). The parser has **no QWC node**; it has no space after `*`, so such
   lines parse as PARAGRAPH and survive verbatim. Danger case: the parser's list-item
   rule is `^[-*]\s+(.+)$` — a line-initial `*` **followed by a space** reclassifies the
   line as a LIST_ITEM. Cleaning must never insert a space between a leading QWC
   asterisk and its label, never convert an existing `* (a)` form, and never reflow a
   QWC line onto a bullet when removing adjacent blocks.
4. **HTML islands** — image divs, tables (including rowspan/colspan, which the parser
   records in raw HTML but does not expand — v1 grid only), and centered divs stay
   well-formed; a table block is edited as a whole block or not at all.
5. **Image island exact shape** — the parser recognizes a figure **only** via the
   single-line form `^<div[^>]*>\s*<img\s+src='([^']+)'(?:\s+alt='([^']*)')?\s*/>\s*</div>\s*$`:
   single-quoted `src`, optional single-quoted `alt`, self-closing `<img/>`, one line.
   A reformatted image line (double quotes, split across lines, non-self-closing) does
   not error — it silently degrades to a raw-HTML PARAGRAPH and the figure element is
   lost. Cleaning never re-quotes, re-wraps, or "pretty-prints" image lines.
6. **Display math fences** — `$$ … $$` pairs stay balanced. Ratified behavior: the
   parser's bounded scans now drop an orphan `$$` opener and re-parse the span as flow
   (counted as `orphanMathFences` in provenance) — so an unbalanced fence no longer
   swallows the following questions, but the equations in that span **are lost as
   equations** (they land as paragraphs). The structural-repair pass on the real corpus
   fixed exactly this class; balancing remains the fix (§7.1.1).
7. **Single-line `$$..$$` spans (P-11)** — a line fully covered by lazy `$$..$$` spans
   yields one equation per span; a line mixing math spans with prose falls through to
   paragraph flow with the raw line preserved (counted as `greedyMathLines`). Cleaning
   must not merge, split, or "normalize" such lines in either direction.
8. **Marking vocabulary** — `allow / accept / ignore / reject / not accept / ECF /
   dependent on / or / any two from` and IC-table structure stay verbatim. The
   `Total for Question/paper` printed wording is likewise load-bearing: the parser uses
   it as a bounded-scan boundary (`TOTAL_LINE`), and B.0 captures it before cover
   stripping (§4).
9. **HTML entities are the parser's to decode** — entity decoding (P-9: full-Unicode
   numeric decode; surrogate/out-of-range code points stay literal; `<br>` → newline
   inside table cells, which identity regexes depend on) is the ONE normalization the
   adapter performs, and it is deterministic. Cleaning must NOT pre-decode entities:
   a pre-decoded clean file shifts `entityDecodedLines` provenance and risks breaking
   the P-9 fail-safe symmetry with the Python twin. Entities pass through untouched.
10. **Image references** — a cleaned file references exactly the same asset set as its
   raw parent minus nothing (image cleanup is Stage A's job; cleaning must not orphan
   or rename assets).

**Corollary:** there is no "aggressive cleanup mode". If a removal or fix cannot be
expressed within this grammar, it becomes an operator escalation (§7.2), not an edit.
Second corollary: blank-line discipline — the parser treats an empty line as a flow
boundary; removing a block must not glue two otherwise-separate lines together (a
removed block is replaced by nothing or by the blank lines it already had, never by
joining text).

## 4. Phase B.0 — pre-clean capture (before anything is deleted)

Several removed pages carry data the verification tooling needs later. Capture them
into the clean-report sidecar **first**, from the raw file:

- **Paper totals** — the printed total-mark box on QP covers and the MS paper-total
  line. `health.py` and `GlmOcrMarkReconciliation` compare *printed* totals; once the
  cover is gone, the sidecar is the surviving witness.
- **Per-question printed totals** (QP right-margin marks) — captured verbatim per
  question label.
- **Session/paper identity as printed** — board line, qualification, paper reference,
  session string. If the cover is the only place identity appears and OCR made it
  unrecoverable, that is an operator-escalation item (identity is never inferred —
  `AGENT.md` rule 2; the pair CLI's `--paper-code/--session-label` overrides exist for
  exactly this).
- **Raw checksums** — SHA-256 of both raw files, recorded before the first edit.

## 5. Removal checklist — Question Paper

| Remove | Rationale | Notes |
|---|---|---|
| Cover page block | candidate name/centre/number fields, barcode bands, printed total box (after B.0 capture) | the single largest spillover source |
| General instructions pages ("answer ALL the questions", BLANK PAGE frames, do-not-write markers) | zero content value | |
| Formula sheet / data booklet pages | reference furniture, not assessment content | if a question *depends* on a data value, the value is printed in the question itself |
| Periodic table page | reference furniture | |
| Page headers/footers and page-number furniture text | noise | keep any `page` provenance if the corpus convention carries it |
| Answer-line runs (dotted/underscore rules) | optional — remove only when structurally inert (never splits a part block) | when in doubt, keep: they are cheap |

| Keep (never remove) | |
|---|---|
| Question numbers, parts, sub-parts, their labels and order | |
| Per-part and per-question printed marks; paper total lives in the sidecar | |
| QWC `*` markers; command words | |
| Figures, tables, `$$` math, chemical/equation content | |
| Any text inside a question block, including stimulus passages | when in doubt whether text belongs to a question, keep it and flag for review |

## 6. Removal checklist — Mark Scheme

| Remove | Rationale |
|---|---|
| Cover page block | |
| Generic marking-guidance preamble pages (how to apply the scheme, abbreviations legend **only if** no later mark point uses the abbreviations) | if any abbreviation/symbol is used by later mark points, the legend page is **kept** (or the used subset copied adjacent to first use — copy is the preferred, less invasive form) |
| Examiner-use grids, notes about the paper process | |
| Page furniture | |

| Keep (never remove) | |
|---|---|
| The marking tables themselves — all three observed IC table shapes | |
| Mark points with `(N)` markers, dependent-on chains, ECF, Or / any-two-from vocabulary | |
| Allowed / not-allowed / accept / ignore answer columns verbatim | |
| QWC tables and per-question totals; paper total captured to sidecar | |

## 7. Fix taxonomy

### 7.1 Agent may fix autonomously (all logged per-fix in the clean report)

1. **Unbalanced `$$` display-math fences** — the exact defect class the 2026-09-11
   structural-repair pass fixed on the real corpus (7 files); repair by fence balancing
   only, never by editing the math content.
2. **Truncated HTML table blocks** — close/reopen a table only when the printed MS/QP
   structure makes the intended rows unambiguous; otherwise escalate.
3. **Page-split duplication** — an answer/mark point repeated across a page boundary
   (the user-visible example: an answer "no." appearing twice because of a page split);
   deduplicate only when the two occurrences are byte-identical or trivially
   whitespace-different.
4. **Local LaTeX defects with unambiguous intent** — e.g. a stray `\frac` without braces
   where the printed paper fixes intent; intent must be reconstructible from the same
   file, not inferred from subject knowledge.
5. **Heading-level slips** — a part heading emitted at the wrong level by OCR, where the
   printed label sequence makes the level unambiguous.
6. **Mojibake artifacts** — byte-level double-encoding debris with a single
   unambiguous decode (e.g. a UTF-8 sequence rendered as latin-1). Scope note per the
   ratified contract §3.9: this does NOT include HTML entities, which the parser owns
   and cleaning leaves untouched.

### 7.2 Operator escalation (never agent-fixed)

- Missing questions, parts, or MS entries ("something is missing entirely") — reported,
  never reconstructed.
- Ambiguous or conflicting marks that change totals.
- Unrecoverable paper/session identity.
- Figures referenced but absent from `assets/` (Stage A's residual ledger decides; the
  cleaner records and moves on).
- Any fix that would require subject-matter judgment rather than document-internal
  evidence.

**Escalation output:** a proposals file per session (`clean-proposals.json`) with the
evidence, the proposed fix, and an explicit `awaiting_operator` state. Operator verdicts
are recorded back into the clean report — the same ratify/promote pattern the corpus
tooling already uses (cf. the c10/c12 operator review gates in `syllabai-resources`).

## 8. Output artifacts & provenance

Per session folder, additive to the existing layout (nothing in place is destroyed):

```
<session>/
  QP.md  MS.md          ← RAW, frozen at Stage A checksums (untouched by this protocol)
  clean/
    QP.md  MS.md        ← cleaned pair; the sole ingestion/atomization input from now on
    clean-report.json   ← provenance + operations + captured totals + fix log
    clean-proposals.json← open escalations (deleted from the folder once resolved)
```

`clean-report.json` (deterministic, insertion-ordered):

```json
{
  "schema": "clean-report-1.0",
  "session": "2012-Jan",
  "raw":    {"qp_sha256": "…", "ms_sha256": "…"},
  "clean":  {"qp_sha256": "…", "ms_sha256": "…"},
  "captured_totals": {"qp_paper_total": 120, "ms_paper_total": 120,
                      "per_question_totals": {"1": 8, "2": 6, "…": 0}},
  "identity_as_printed": {"board": "Edexcel", "paper_reference": "4CH0/1C",
                          "session": "January 2012"},
  "operations": [{"op": "remove-block", "target": "cover-page", "qp_lines": "1-58"},
                 {"op": "fix-fence",   "target": "$$", "qp_line": 214}],
  "escalations": [{"id": "P-001", "kind": "missing-ms-entry", "detail": "…",
                   "state": "awaiting_operator"}],
  "gate_results": {"G1": "pass", "G2": "pass", "G3": "pass", "G4": "pass", "G5": "pass"}
}
```

The cleaned file is a **derived artifact** in the ADR-021 sense: PostgreSQL and the
validation gates stay canonical; the raw MD remains the provenance root; the clean
report is the auditable bridge. A future canonical re-ingest must be able to rebuild
exactly what was ingested from `raw + report + tool version`.

## 9. Acceptance gates — the objective definition of "clean"

A session is CLEANED only when all gates pass. Any FAIL blocks ingestion of the cleaned
pair (the T-C02 bridge's fail-loud validation provides the second layer).

- **G1 — Parse parity:** `GlmOcrPairCli` runs clean end-to-end on the cleaned pair and
  produces the five-file bundle.
- **G2 — Health:** `tools/glmocr/health.py` on the cleaned pair reports **zero
  FAIL-class findings** (part-mark sums vs captured totals, QP↔MS total agreement using
  the B.0-captured witnesses, question↔entry mapping, asset integrity).
- **G3 — Extraction diff vs raw (the core gate):** comparing drafts from raw vs clean
  (drafts carry positional element ids `e%06d` derived from the interleaved reading
  order, so ids/orders SHIFT under removal by construction — the diff compares
  question/part/marks structure, never element ids; the clean pair is a new derived
  document with its own content-derived `documentId`):
  - question count **strictly lower or equal**, and the reduction is explainable
    line-by-line as removed boilerplate (spillover questions disappearing is the point);
  - the set of `(question_number, part_label, marks)` that exist in BOTH drafts is
    **identical in marks** — cleaning may remove phantom entries, never change real ones;
  - MS mark-point count equal-or-lower with the same explainability constraint;
  - **no new warnings** of any class except the documented `boilerplate-removed` class;
  - `paperTotalConflict = false` (or unchanged, if it was already a reviewed conflict).
- **G4 — Provenance completeness:** clean-report fully populated; raw checksums match
  Stage A's manifest; every operation has a line-range target; every escalation is
  either resolved or explicitly `awaiting_operator`.
- **G5 — Grammar conformance (ratified, machine-checkable):** cleaned files pass the
  same fixture-mode canonical parse as raw, and the parse's **provenance honesty
  counters go to zero**: `unterminatedTableBlocks`, `orphanMathFences`,
  `unclosedCenterDivs`, `greedyMathLines` must be ABSENT from the clean parse's
  provenance params (the parser emits them only when non-zero). Any counter that was
  non-zero in the raw parse must either reach zero via a §7.1 fix (each such fix is
  logged in the clean report) or block with an escalation. Supporting counters must be
  explainable: `signedUrlFigureRefs` unchanged (§3.10), `entityDecodedLines` changed
  only by removed blocks, `sourceLineCount` delta == removed/inserted lines per the
  operations ledger. Spot-check: re-run `tools/glmocr/conformance.py` fixtures through
  the *cleaning tooling's* post-conditions — the fixtures themselves are sealed and
  untouched.

Gate G3 is implemented as a deterministic diff script (`tools/corpus_ops/clean_diff.py`,
T-C16) so the gate is machine-checkable in CI, not an agent's self-assessment.

## 10. Operator loop

1. Agent runs B.0 → clean → gates on a session; emits report + proposals.
2. Operator reviews proposals (and spot-checks one removed block per class on first
   sessions — sampling tightens as evidence accumulates).
3. Operator verdicts recorded; gates re-run; session marked CLEANED in the batch audit
   (same shape as the T-C04 batch audit report).
4. Only CLEANED sessions feed `GlmOcrPairCli` → core ingestion and `atomize.py`.

## 11. CI integration

- `clean_diff.py` + `health.py` + gate evaluation run as a new job in the parser
  workflow, over `corpus/` fixtures first, then over an operator-designated corpus
  slice.
- The gate script is deterministic and stdlib-only, mirroring the `ocr_batch` testing
  discipline (mocked IO, no network).

## 12. Non-goals

- No difficulty/type/spec-point tagging here (that is T-C18, post-validation metadata).
- No re-OCR, no image operations, no manifest mutation (Stage A / T-C16 owns those).
- No change to the canonical §8 contract or the extraction drafts' schemas.
- No serving-path involvement — this is offline content-operations.

## 13. Honesty notes and open questions

- Grammar contract §3 was ratified against `GlmOcrMarkdownParser` v1.2.0 source on
  2026-09-17 (syllabai-parser tree `5c93317`): invariants re-anchored to the parser's
  actual regexes and bounded-scan predicates; image-island exact-shape (§3.5), P-11
  span discipline (§3.7), entity-ownership (§3.9), and the QWC asterisk/list-item
  interaction (§3.3) were added or corrected as part of that pass; gate G5 was
  upgraded from prose to the parser's provenance honesty counters. Residual honesty
  gap: the ratification covers the Java adapter; the Python twin
  (`tools/glmocr/canonical.py`) is asserted to mirror it via the conformance suite
  (16/16) but was not independently re-read line-by-line in this pass.
- The G3 "explainability" requirement is currently human-audited; automating it fully
  (mapping every removed line to a removal class) is desirable and unproven.
- Cleaning changes document checksums by construction; the corpus repositories must
  agree on which artifact (`raw` vs `clean/QP.md`) the *next* manifest generation
  records — proposed answer: manifests keep raw as the provenance root and add an
  additive `clean` block per session (T-C16 §7).
