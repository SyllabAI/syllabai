# Stage B Agent Task Brief — Clean-and-Verify One Session Pair

**Status:** Active brief — execute against one session at a time
**Date:** 2026-09-17
**Authority:** This brief operationalizes `CLEAN_VERIFY_PROTOCOL_QP_MS_MARKDOWN.md` (T-C17). The protocol wins on any conflict with this brief.
**Tracker row:** T-C17 (master workbook TODO.md, content-ops track)
**Sibling tooling:** `CORPUS_OPS_TOOLING_DESIGN.md` (T-C16) owns Stage A/A′ (intake/scrub/verify). This brief never touches those responsibilities.

---

## 0. Mission

You are the Stage B cleaning agent. You receive **one session folder** containing a raw
question paper and mark scheme pair (`QP.md`, `MS.md`, `assets/`) that has already been
through Stage A (images downloaded, operator deletions scrubbed, manifest current).
You produce a **cleaned pair** under `clean/` plus a machine-checkable provenance
report, and you **stop at the operator gate**. You do not ingest, atomize, tag,
promote, or serve anything.

The one-sentence rule, from the protocol: *you delete blocks and repair local defects;
you never rewrite the document.*

## 1. Inputs (all must be present; stop and report if any is missing)

- `<session>/QP.md`, `<session>/MS.md` — raw pair, frozen (you never edit in place)
- `<session>/assets/` — final image set (Stage A output; read-only for you)
- The paper-level `MANIFEST.json` (or `assets-report.json` sidecar) — for checksum
  cross-check in B.0
- The ratified grammar contract — T-C17 §3 (read it before the first edit of every
  session; it is short)

## 2. Outputs (exactly these; nothing else in the tree changes)

```
<session>/
  QP.md  MS.md                      ← untouched by you
  clean/
    QP.md  MS.md                    ← the cleaned pair
    clean-report.json               ← schema clean-report-1.0 (T-C17 §8)
    clean-proposals.json            ← only if escalations exist
```

## 3. Non-negotiable rules (violation = throw the run away and restart)

1. **Subtractive-only + bounded repair.** You remove whole blocks and apply the §7.1
   fix taxonomy. You never re-author, paraphrase, reorder, or "improve" question or
   mark-point content. A fix not expressible inside the grammar contract becomes an
   escalation, never an edit.
2. **Grammar contract §3 survives verbatim.** Highlights you will be tested on:
   - image islands stay in the exact single-line form
     `<div …><img src='…' alt='…' /></div>` — never re-quote, re-wrap, or split them;
   - a leading QWC asterisk keeps zero space before its label (`*(c)`, `*14`) — never
     turn one into a `* ` bullet (the parser reads `^[-*]\s+` as a list item);
   - `(N)` marks, part labels `(a)`–`(h)` / roman, and `Total for Question/paper`
     lines keep their exact printed form — they are the parser's structural
     boundaries;
   - `$$` fences stay balanced; single-line `$$..$$` spans are not merged, split, or
     mixed with prose;
   - HTML entities pass through untouched (the parser owns decoding; §3.9);
   - table blocks are edited whole or not at all; `<br>` inside cells is never
     flattened.
3. **B.0 before any deletion.** Printed paper totals, per-question totals, identity
   as printed, and raw SHA-256 checksums are captured into the report from the raw
   files first. Once the cover is gone, the sidecar is the only witness.
4. **Never infer or repair paper/session identity.** Unrecoverable identity is an
   escalation. The pair CLI's explicit override flags exist for the operator, not
   for you.
5. **Assets are read-only.** No image deletion, renaming, or manifest mutation —
   that is Stage A (T-C16). If a reference points at a missing asset, record and
   move on (§7.2).
6. **Validation state never changes through you.** Nothing you produce promotes
   anything out of `SUGGESTED`/`reviewRequired`.
7. **Honest failure.** If you cannot complete a phase, emit the partial report with
   `gate_results` marking the blocked gates FAIL and stop. Never mark a gate PASS
   that you did not actually run.

## 4. Procedure (per session, in order)

**Step B.0 — pre-clean capture.** From the raw files, before any edit: SHA-256 of
both files (cross-check against the manifest — a mismatch is a hard stop); printed
QP paper total and MS paper total; per-question printed totals; identity as printed
(board, paper reference, session string). Write these into `clean-report.json` now,
not at the end.

**Step B.1 — structural read.** Walk the raw pair and build a private block map:
cover blocks, instruction pages, formula-sheet/data-booklet/periodic-table pages,
question blocks with their printed labels, MS marking tables and guidance preambles.
Do not edit yet. Identify every block you intend to remove with its line range and
its removal class (T-C17 §5/§6 tables).

**Step B.2 — removal pass.** Apply the §5 (QP) and §6 (MS) checklists. Rules of
engagement: remove whole blocks only; respect the blank-line corollary (a removed
block is replaced by nothing or its own blank lines — never glue text together);
when in doubt whether text belongs to a question, keep it and flag for review;
answer-line runs stay unless provably structurally inert. Log every removal as an
operation with line-range target in the report as you go.

**Step B.3 — repair pass.** Apply §7.1 fixes only (fence balancing, unambiguous
table closure, byte-identical page-split dedup, reconstructible-from-file LaTeX
defects, unambiguous heading-level slips, mojibake — NOT entity decoding). Every
fix logged per-fix. Anything else → `clean-proposals.json` with evidence,
proposed fix, and `state: awaiting_operator`.

**Step B.4 — gate run.** Execute the gates in the protocol's §9 order and record
verbatim results in `gate_results`:
- G1 `GlmOcrPairCli` end-to-end on `clean/` → five-file bundle;
- G2 `tools/glmocr/health.py` on the cleaned pair → zero FAIL-class findings;
- G3 the raw-vs-clean draft diff (`clean_diff.py`, T-C16) — question count
  lower-or-equal and line-explainable; surviving `(question, part, marks)` identical;
  no new warning classes; element-id shift expected and ignored by the diff;
- G4 report completeness — raw checksums match the manifest, every operation has a
  line target, every escalation resolved or `awaiting_operator`;
- G5 provenance honesty counters — `unterminatedTableBlocks`, `orphanMathFences`,
  `unclosedCenterDivs`, `greedyMathLines` absent from the clean parse;
  `signedUrlFigureRefs` unchanged; `entityDecodedLines` and `sourceLineCount`
  deltas explainable from the operations ledger.

**Step B.5 — stop.** Emit report + proposals and end your turn with a summary the
operator can act on: gates table, removal counts per class, fix counts per class,
open escalations. The operator reviews proposals, records verdicts, re-runs gates,
and only then does the session feed ingestion. You never re-run after an operator
verdict without being asked.

## 5. Self-check before you declare done

- [ ] Raw files byte-identical to session start (`git status` / checksum re-verify)
- [ ] B.0 captured before first deletion (report timestamps/line refs prove it)
- [ ] Every removed line accounted for in the operations ledger with a class
- [ ] Zero edits outside the §5/§6/§7.1 vocabularies
- [ ] Image island count in clean == raw (you removed no images)
- [ ] QWC asterisk lines still have zero space after `*`
- [ ] `$$` fence count is even in both cleaned files
- [ ] All five gate results recorded with real (not asserted) outputs
- [ ] Escalations file matches the report's escalation list
- [ ] Your summary states gate results honestly, including any FAIL

## 6. Anti-examples (things an eager agent gets wrong)

- Rewriting `<img src='x'/>` to `![](x)` or double quotes → figure lost silently (G5
  would catch it via `signedUrlFigureRefs` — but never rely on the gate to catch what
  the rule forbids).
- "Cleaning up" `*(c)` into `- (c)` because it looks like a bullet → part label
  reclassified, extraction shifts.
- Decoding `&gt;` to `>` in body text → §3.9 violation, provenance drift.
- Dropping the MS abbreviation legend because it "looks like a preamble" while later
  mark points still use the abbreviations → §6 requires the legend be kept or the
  used subset copied adjacent to first use (copy preferred).
- Fixing an ambiguous table by guessing rows → §7.2 escalation, not an edit.
- Marking G2 PASS because "the clean looked fine" without running `health.py`.

## 7. Context you operate in (so you do not invent scope)

- Downstream of you: only CLEANED sessions feed `GlmOcrPairCli` → T-C02 ingestion →
  T-013 chunking, and `atomize.py` per-sitting exports. The cleaned pair becomes the
  sole ingestion input; the raw pair remains the provenance root (ADR-021).
- Out of scope for you, always: Stage A image/manifest work (T-C16), difficulty/type/
  spec-point tagging (T-C18 — post-validation metadata, never created during
  cleaning), retrieval/embeddings (T-C07/T-C13), and any frontend or serving path.
- First production runs are sampled: expect the operator to spot-check one removed
  block per removal class on early sessions; tight, evidence-first output is how the
  sampling loosens.
