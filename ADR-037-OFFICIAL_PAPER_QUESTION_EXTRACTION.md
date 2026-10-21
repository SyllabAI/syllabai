# ADR-037: Official-paper questions are EXTRACTED, never regenerated — the past-paper → serving-schema conversion is verbatim-first with fail-closed gates, and LLM output is confined to tagging and linking

**Status:** Proposal v0.2 — drafted 2026-10-20 outside the repo (operator chat trace `1a15a8439ed5ed31`); full-corpus evidence now attached (see §7 addendum): **all 16 series of 4CH1/1C in `syllabai-pastpapers` converted — 14/16 all-gates PASS, 169 questions, 930 parts, 1754/1760 marks, MCQs keyed everywhere except two honest 2020-01 refusals, negative controls 3/3 on every series, independent-parse cross-diff 161/161 marks agree.** Outputs + converter + agent kit promoted to `syllabai-resources/Official-ExamQuestion/` (AGENTS.md / LEDGER.md / CANARIES.json / run_all.sh / CHANGELOG.md). Still awaiting operator GO before a tracker row is claimed and the remaining 4CH1 variants (2C–4C) plus new courses are scheduled.

> **Status amendment (2026-10-21, docs reconciliation pass — operator directive trace `1a15e714070287a9`):** execution has proceeded in the system of record while this file still reads "awaiting GO": converter v0.6/v0.7 waves wired 16 official 4CH1/1C question sets into the v2 hub bundle and made markPoints persist per point (`SyllabAI/syllabai-v2` PRs #239 + #249, merged 2026-10-21; 169/169 questions anchored). The wiring record is `syllabai-v2/docs/ADR-037-OFFICIAL_PAPERS_WIRING.md` (restored 2026-10-21 after an accidental 404-body overwrite at `045bcd7040`; original content preserved at `743b53e5b8`). The GO-gated items below — the tracker row claim (satisfied in part by the F-178 tracker row) and the remaining 4CH1 variants (2C–4C) plus new-course scheduling — REMAIN OPEN pending operator adjudication; nothing here resolves the GO question. Body below preserved verbatim.

**Date:** 2026-10-20
**Scope:** new derived corpus `syllabai-resources/Official-ExamQuestion/` + one converter script `syllabai-resources/scripts/official_examq_extract.py`. Consumes frozen `syllabai-pastpapers` artifacts. **No change to `syllabai-pastpapers`** (byte-frozen archive of record), **no change to `SME-ExamQuestion/`** (licensed Save-My-Exams corpus), no app/hub code, no schema migration.
**Related:** ADR-021 (Markdown as durable interchange); `CLEAN_VERIFY_PROTOCOL_QP_MS_MARKDOWN.md` (Stage-B gates G1–G5 incl. G3.2b printed-total identity — this ADR consumes its output as the source layer); T-C06 corpus converter; T-C16 corpus_ops tooling; T-C17 clean-and-verify (first execution, fail-closed precedent); `SME-ExamQuestion/igcse-chemistry-19/README.md` (schema lineage `syllabai.sme-exam-questions/1.0`, spec-point registry `spec_point_index.json` / `spec_point_resolution.json`).

---

## 1. Problem (evidence, not vibes)

We need full-paper question coverage (every official past-paper question in the serving schema) that the licensed SME corpus cannot provide: the Save-My-Exams scrape is topic-organized, covers 524 questions (not all papers), and records `source_paper` provenance on only a fraction of parts (14/40 in a sampled topic). The tempting shortcut is a general-purpose LLM tool (NotebookLM was tried) fed the official PDFs.

A one-paper audit (2026-10-20, claimed "June 2020 4CH1/1C") against the official corpus found the free-form-generation failure profile in full:

- **Identity failure:** no June 2020 series exists for 4CH1 (COVID-cancelled). The content is **November 2020** — the registry manifest itself records `series.printed: "November 2020; June 2020"` (Pearson re-used the cancelled June papers for the autumn sitting), which is exactly why third-party archives mislabel it. Printed text cannot be trusted for identity; the registry must win.
- **Answer keys ≈ faithful** (0.016 s⁻¹, 62.5 s, 693 J, −65.0 kJ/mol, 2.05 g, 87.5 %, 212 g, even `ALLOW N₂` all match the official MS) — while **question text is ~half rewritten or fabricated**: every stem of Q1(a) paraphrased (official asks by *atomic number / proton count / configuration*, the output invented equivalent-but-wrong phrasings); 3(a)(i)–(iii) replaced by different sub-questions ("most reactive" vs official "which metal could be **gold**"); 9(a)(ii) wholesale replaced (official: *"Suggest why the reaction makes the cakes increase in size"*); 4(b)(ii) replaced with an invented indicator MCQ.
- **Fabricated numbers that survive answer-only checks:** official crucible table 29.75/26.50 g became 28.25/25.00 g — **same difference (3.25 g), same answer**; a thermometer *diagram* became invented readings 27.3/24.4 that contradict the paper's own ΔT = 3.3.
- **Hallucinated context:** "reaction between **zinc** and copper(II) sulfate" — the official Q8 is the dissolving of anhydrous CuSO₄; no zinc exists in the question.
- **Structural drift:** 4(c)(iii) printed 3 marks → emitted 2 (parts sum 9 vs stated 10); a 3-mark 9(d)(i) invented, duplicating 9(c)(ii) (parts sum 15 vs official 12); MCQ 9(a)(i) 4 options → 3 (D dropped).
- **Total figure loss:** 7+ tables/diagrams gone; `topic.json` had zero asset fields, so every "the data provided" reference dangles.

Verdict: the *answers* ground well, the *questions* do not. For an exam-prep product this is the worst failure mode — plausible-looking papers that are not the real papers, with subtly wrong marks. Free-form generation is disqualified as the conversion mechanism; the mechanism must make fabrication *structurally impossible and mechanically detectable*.

## 2. The one-sentence rule

**The converter extracts; it never authors.** Every character of `problem_md` / `solution_md` / `choices[].text_md` is copied from the verified source layer (QP/MS markdown over the sha256-verified PDFs); LLM participation is confined to *labels* (spec codes, command words, difficulty) and *links* (part↔answer, part↔asset), and every label is registry-validated or queued for human review. Anything the rules cannot place is flagged, never guessed — fail-closed, per T-C17 precedent.

## 3. What this is — and is not

**It is:**
- a deterministic extraction pass over `syllabai-pastpapers` QP/MS (PDF bytes → layout text → structured parts) producing `syllabai.official-paper-questions/1.0` documents;
- a verification protocol with six machine-checkable gates (§4) plus negative controls, in the CLEAN_VERIFY tradition;
- provenance-preserving: source PDFs stay frozen in `syllabai-pastpapers`; the derived corpus carries `paper_id` + `sha256` + page anchors back to them.

**It is not:**
- re-authoring, paraphrasing, or "improving" question content (the exact failure of §1);
- a replacement for CLEAN_VERIFY Stage B (it consumes Stage-B-verified markdown; G-GATE G3.2b printed-total identity is re-checked downstream at question level);
- a change to the SME corpus or its license posture;
- semantic validation: extraction can never promote a part past `extracted` status — human review (figures always; flagged items) remains the only promotion path to `verified`, mirroring Master Spec §7 teacher/SME gates.

## 4. The gates (fail-closed; each exists because §1 shows the failure it catches)

| Gate | Property | Catches (from the audit) | Pass condition |
|------|----------|--------------------------|----------------|
| **G0 identity** | paper is what the registry says | "June 2020" mislabel | `paper_id` from `manifest.yaml`; sha256(QP) and sha256(MS) match manifest materials; series/qualification/variant consistent; question count and paper total match registry expectations |
| **G1 structure** | marks add up | 4(c)(iii) 3→2; invented 9(d)(i) | for every question: Σ part marks = printed `(Total for Question N = M marks)`; Σ question totals = paper total (110 for 4CH1/1C) |
| **G2 verbatim** | text is copied, not generated | Q1(a) paraphrases; 9(a)(ii) swap | per part: emitted `problem_md` normalized 5-gram overlap vs source region ≥ 0.95; by construction ~1.0 — the gate exists so any future LLM-touching pass fails loudly |
| **G3 MCQ integrity** | options as printed | 9(a)(i) D dropped; invented 4(b)(ii) | every MCQ part carries the board-standard option set (Edexcel IGCSE: exactly A–D = 4) and exactly one correct choice once MS-linked; unlinked → `review`, never auto-keyed |
| **G4 figure resolution** | every visual reference resolves | 7+ dropped tables/diagrams | every `table/diagram/grid/graph/apparatus` mention maps to an asset record (page-anchored crop in production; `crop-required` stub in prototype); dangling mention = FAIL |
| **G5 answer linkage** | every part has an MS anchor | answers detached from altered questions | per-part linkage into the official MS text; coverage ≥ 0.8 PASS, 0.5–0.8 REVIEW, < 0.5 FAIL; unmatched parts are listed, never silently dropped |
| **G6 registry codes** | labels are real | invented spec codes | every emitted `spec_point_codes[]` member exists in `spec_point_index.json`; untagged parts carry `tagging: "pending-llm"`, never fabricated codes |

**Negative controls (mandatory per session):** inject N1 a +1 mark, N2 a one-word paraphrase, N3 a fake spec code; all three MUST be DETECTED by G1/G2/G6 respectively, else the run is void (T-C17 negative-control discipline).

## 5. Accepted (proposal)

- **New schema `syllabai.official-paper-questions/1.0`.** Paper-level: `paper_id` (registry paper_id), `source {qp_sha256, ms_sha256, series, printed}`, `paper_info {code, session, total_marks, time}`, `questions[]` → `parts[]` with `part_number, marks, command_word, question_type, problem_md, choices[], solution_md|answer_status, source_page, assets[], spec_point_codes[], tagging, review`. Deliberately shaped like `syllabai.sme-exam-questions/1.0` (same consumers) but with **hard provenance on every part** (page anchor + paper sha) and **no `difficulty` until a tagging pass is accepted** — difficulty in the audit output was pure invention.
- **Storage placement (the operator's question, answered):** derived question banks live in **`syllabai-resources/Official-ExamQuestion/<spec-folder>/<series>/<paper>/`** (`topic.json`, `questions.md`, `assets/`, `validation-report.json`), mirroring the `SME-ExamQuestion/` layout and the `igcse-chemistry-19` course spine. **They do NOT go into `syllabai-pastpapers`.** Rationale: pastpapers is the byte-frozen archive of record (identity layer, LICENSE-DATA restrictions on official bytes) — mixing derived, editable teaching content into it would break the one-way derivation `pastpapers → resources` that CLEAN_VERIFY and the corpus ledger already assume. `resources` is where serving content lives and where the retrieval layer already looks. The converter script lives in `syllabai-resources/scripts/` beside `sme_examq_scrape.py`.
- **Verbatim extraction policy:** layout text (pdftotext/Stage-B markdown) is segmented by deterministic markers only (printed footers, `(a)`/`(i)` markers, A–D option runs, standalone `(n)` marks). Text between markers is copied; furniture (page furniture, watermarks, dotted answer lines, "BLANK PAGE", "Turn over") is removed by pattern list.
- **MS linkage is positional, not semantic:** MS rows are matched by `(question, part, roman)` markers into `answer_raw`; free-text rendering into `solution_md` happens only from matched regions, else `answer_status: "unmatched"` + review.
- **Figures are page-anchored:** each part records `source_page` (text-anchor search over the PDF, PyMuPDF); figure mentions emit asset records with the anchor page so the crop pass (pdfium/mupdf) and human check are one bounded queue.
- **SME corpus is the independent cross-check:** where an SME part carries `source_paper` provenance (e.g. `Nov1C`), align it against the extracted official part and diff — Save-My-Exams text is a human re-typeset of the same question, so disagreements route to review rather than to a "truth".
- **Human review queue is enumerated, finite, and receipted:** figures (always), unmatched answers, verbatim < 0.95, MCQ key conflicts, mark-sum mismatches. Nothing else reaches a human.
- **Rollout:** 4CH1 first (16 series × up to 4 variants ≈ 55 papers), one paper proven end-to-end (this ADR's prototype), then the board-layout generalization pass before any second subject.

## 6. Consequences

- Fabrication becomes structurally impossible at the text layer and mechanically detectable at the label layer; every published paper carries a gate receipt, so "is this the real paper?" is answerable by machine, forever.
- The review burden is quantified instead of vibes-based: prototype run on 4CH1/1C 2020-11 = 10 questions / 64 parts extracted, marks invariant 10/10 PASS (Σ = 110), verbatim 64/64 PASS, 6/6 MCQ parts printed-and-keyed, MS linkage 62/64 (97%) with 2 parts in review, 17 figure assets awaiting the crop pass — a finite, enumerated human queue instead of an audit.
- Cost shifts from "trust the model" to deterministic compute + bounded human review (~30–60 min/paper, dominated by figure crops); no per-paper LLM generation spend for content, LLM spend confined to future tagging passes over already-verified text.
- Two-layer storage adds a sync duty: `Official-ExamQuestion` documents must cite registry sha256s, and re-ingestion of a corrected PDF (pastpapers `repair:` history exists) must orphan derived documents — handled by storing `qp_sha256` and failing G0 on mismatch.
- **UNVERIFIED until a multi-series run:** (a) extraction recall on series with different layouts (2019-06 first-sitting format, 2025+ modular 4XCH1), (b) MS linkage coverage on extended-response questions (6-mark describe loops), (c) 4SD0 double-award shared-paper handling (same bytes, two qualifications), (d) figure-crop precision from page anchors alone. Each is a scheduled gate in the tracker row, not an assumption.

---

## 7. Corpus-run addendum (2026-10-21, converter v0.3) — 4CH1/1C complete

The pipeline was executed over **all 16 series of 4CH1/1C present in `syllabai-pastpapers`** (2019-06 → 2026-06; note 2020-06 never ran — COVID). Results:

| metric | value |
|---|---|
| series converted | 16/16 (2019-06, 2020-01, 2020-11, 2021-01, 2021-06, 2021-11, 2022-01, 2022-06, 2023-01, 2023-06, 2023-11, 2024-06, 2024-11, 2025-06, 2025-11, 2026-06) |
| questions / parts | 169 / 930 |
| marks extracted | 1754/1760 (6 marks = 2019-06 Q7, lost to rasterized archive pages — attributed, never invented) |
| all-gates PASS | 14/16 series |
| honest terminal states | 2020-01 G3 FAIL (interleaved MS rows; wrong auto-key refused — canary-locked), 2019-06 G1/G5 REVIEW (rasterized pages) |
| MCQ keys | every printed MCQ keyed except the two 2020-01 refusals |
| negative controls | 3/3 DETECTED on every series |
| independent-parse cross-diff | 161/161 part marks agree with the repo's own `parsed/` layer (2024-06, 2025-06, 2026-06) |

Question counts vary 9–15 across the era (2019-06: 15; 2023-01: 12; 2026-06: 9) — all verified against printed footers summing to 110 and recorded in the per-series count registry.

**Self-improvement machinery** (this run earned its keep): four new cross-series patterns were found and fixed generically — MS indent drift (F11), 2021+ 'is not THE correct answer' phrasing (F12), manifest schema v2 (F13), rebuttal-style MCQ mark schemes with elimination keying (F14) — each recorded in `Official-ExamQuestion/LEDGER.md`, each guarded by a machine-checkable assertion in `CANARIES.json` (11/11 hold), and the whole corpus re-run after every fix so a gain on one series cannot silently regress another. Any future agent starts from `Official-ExamQuestion/AGENTS.md` (protocol), `run_all.sh` (one-command regeneration + canary gate), and `CHANGELOG.md` (converter history).

**Still UNVERIFIED (unchanged from §6, plus what the 1C run cannot prove):** papers 2C–4C (extended-response density differs), modular 4XCH1, 4SD0 shared papers, legacy 4CH0, figure-crop precision from page anchors alone, and the LLM tagging pass (labels only) for series other than the 2020-11 demo seeds.
