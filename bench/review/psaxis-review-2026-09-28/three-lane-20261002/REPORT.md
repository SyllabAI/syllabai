# THREE-LANE EXECUTION — 7-qv MARKS REPAIR + PRINTED-MS RE-EXTRACTION + ING APP MIGRATION (2026-10-02)

**Authorization:** operator IM trace `1a0f87c3239f8891` — "7-qv marks repair lane
(printed-QP evidence), printed-MS re-OCR for the 56, ING app migration" — the
three open items named by the 2026-10-01 residue-closure closeout. All three
executed in one session; every DB write fail-closed (dry-run first); no
validation-state flips anywhere; teacher_validation_events 0; audit tail
untouched (4047).

## Lane A — 7-qv marks-vs-printed repair (printed-QP evidence) — COMMITTED

The 7 defect qv (residue class "MS internally consistent, bank qv.marks
wrong"; all 4CH0/1C sittings 2013–2015, all banked marks=1):

| qv | sitting | QN | bank → printed |
|---|---|---|---|
| q03-6d968517 | June 2013 | 3 | 1 → 7 |
| q04-8d584ee1 | January 2015 | 4 | 1 → 9 |
| q11-8d584ee1 | January 2015 | 11 | 1 → 14 |
| q06-1da77322 | June 2014 | 6 | 1 → 6 |
| q15-1da77322 | June 2014 | 15 | 1 → 15 |
| q05-e280d9c6 | June 2015 | 5 | 1 → 15 |
| q08-e280d9c6 | June 2015 | 8 | 1 → 14 |

**Evidence chain (double, independent):**
1. MS-side: v2-gated parse of the ingested MS chunks (rows sum == printed
   total; both total formats + the older `(Total marks for Question N = M
   marks)` variant recognized). Version attribution: (R) vs regular resolved
   per sitting — the (R) docs' differing totals (e.g. 2013 Q3=12) failed the
   gates and were excluded; the bank stems attribute to the regular versions.
2. QP-side ("printed-QP evidence"): the source QP PDFs (Past-Papers repo;
   **all downloaded PDFs sha256-match the DB documents.checksum
   byte-exactly** — `src_pdf_SHA256SUMS.txt`, 25 files) parsed via
   `pdftotext -layout`; each question's printed `(Total for Question N = M
   marks)` echo must equal the MS total. 7/7 pass (G2). The rich text layers
   made rasterization unnecessary (the O1 raster+tesseract route was
   implemented as the thin-page fallback and did not need to fire).

**Repair scope:** `question_versions.marks` + `questions.marks` := printed
total (Task-66-TX-B marks-arithmetic class; no state flips, no audit rows —
mechanics precedent). **Parts NOT written:** 2013–2015 print layouts defeat
unambiguous per-part mapping, and per the 35-lane anti-fabrication precedent
("no honest part mapping from the flattened MS") the printed part structure
is recorded in the plan as evidence only.

Plan pinned pre-write: `laneA_plan.json` sha `7a131db17940c12a…`; dry-run
green then commit; independent fresh-connection verify ALL PASS (values,
stems byte-unchanged, per-paper banked-sum deltas exact: +6/+21/+19/+27,
census pins unchanged).

## Lane B — printed-MS re-extraction for the 56 sparse qv — COMMITTED (+13 schemes / +94 points; sparse 56 → 43)

Every one of the 56 was re-attacked through three gated routes (in order):

- **chunks** — v2-gated parse of the ingested MS chunks (rows sum == printed
  total == qv.marks, exactly one total, no pipeline-FAILED flag);
- **chunks+qp-total** — rows verbatim from chunks where the corpus has no
  total line (2016-era MSs print no per-question totals); the closing total
  comes from the printed QP echo, gated sum(rows) == qp-total == qv.marks;
- **print** — full re-parse of the printed MS PDF via the deterministic
  `pdflane parse_ms` grid parser (the engine that produced the corpus, with
  its failsafe accounting), QP printed totals supplied for arithmetic
  recovery; acceptance additionally requires faithful row texts.

**13 entries filled** (8 chunks + 4 chunks+qp-total + 1 print): all 7
Lane-A-repaired qv + 6 newly-extractable (1CR-2016 Q7, 2C-2019 Q2/Q8/Q9,
1C-2019 Q7, 2CR-2021 Q8). Inserted in the house shape: mark_schemes
version_label '1', **SUGGESTED** (no self-validation; joins the teacher
lane), source_document_id = the parseable MS document, extraction_method
`ms-chunk-gated-extraction-v2` / `ms-chunk-qp-gated-extraction-v2` /
`ms-print-gated-extraction-v1` per route; mark_points verbatim row texts,
part links/acceptance NULL, confidence 1.0. One fail-closed tx (dry-run
green first): schemes 1455 → 1468 (SUGGESTED 95 → 108), mark_points 5558 →
5652. Plan pinned pre-write: `laneB_plan.json` sha `f4e1d2e114d9d2d0…`;
fresh-connection verify ALL PASS (per-entry point counts/sums, states,
fidelity spot-checks, sparse recount 43, pins).

**43 qv remain sparse**, documented by sharper measured classes (`skipped`
array in the plan, per-group try evidence):

- **~14 NEW bank-defect candidates** (Task-66-TX-B class, surfaced by this
  pass but NOT executed — they need their own printed-evidence repair lane /
  operator mandate): best-evidenced are 1CR-2013 Q8 (printed 14, bank 8), Q9
  (14, 1), 2CR-2014 Q3 (9, 5), 1CR-2022 Q11 (10, 1) — double-evidenced
  (chunk total == QP echo). A cluster on 1CR/2CR-2016 (Q1/Q9/Q10/Q11/Q12,
  Q6 …) shows bank marks matching NEITHER version's print consistently —
  suspected version misalignment of the extracted bank rows, a distinct
  defect class that must not be "repaired" by guessing a version.
- **~26 structural parse failures** on 2015–2019 layouts (print grid parse
  closes with sum != total under all three routes — capped groups,
  level-marked grids, displaced cells beyond the engine's recovery).

## Lane C — ING app migration — PR #42 MERGED (deploy-held execution)

`SyllabAI/syllabai-core#42` (squash-merged as `93850118…`; CI build SUCCESS
on head `36c66b6`):

- **V57__ing_node_removal.sql**: `questions.primary_topic_node_id` becomes
  nullable (the anchor-column semantics change the closeout named); archived
  questions lose their ING anchors (honest absence — re-pointing would
  fabricate); the 57 retained ING nodes are then deleted under fail-closed
  guards (questions any-state, KG edges, skill_states, review_schedules)
  that abort the boot loudly on any unexpected reference.
- **Question.java**: anchor field nullable; every read path already tolerates
  null (ServableQuestionService/SmartLessonService null-check;
  ClaContextResolver + NextBestAction degrade via existing NotFound/skip
  paths) — verified by reading each call site.
- **V57IngNodeRemovalIT** (Testcontainers, full Flyway chain): fresh-DB
  post-shape; in-place repair of a simulated pre-migration state; guard
  fail-closed on an active anchor + an edge reference; idempotent
  re-application.
- **Reversibility:** before-images of all 104 original ING nodes remain
  pinned in `bank-residue-closure-20261001/ing_plan.json` (sha `9d53e3fa…`)
  — reversible by INSERT.
- Execution timing: Flyway applies V57 at the next core deploy; until then
  the census still shows ING 57 (knowledge_nodes 492 → 435 expected).

## Post-lane census — ALL PINS MATCH

`census_bundle_20261002.json`: papers 90V/14R · qv 1533 (states unchanged) ·
questions 961 active · qsp 2637 · qt 1725 · schemes 1468 (1360V + 108S) ·
mp 5652 · sparse 43 · kn 492 (ING 57 pre-deploy) · edges 730 ·
skill_states 185 · review_schedules 120 · docs 567V/305S/147R · audit 4047 ·
tve 0. Drift vs expectation: NONE.

## Files

`REPORT.md` (this file) · `VERIFY_OUTPUTS.md` (verbatim session captures) ·
`laneA_plan.json` + `laneB_plan.json` (+ `SHA256SUMS`) ·
`census_bundle_20261002.json` · `src_pdf_SHA256SUMS.txt` (25 source PDFs,
all matching documents.checksum). Scripts (session workspace):
`laneA_build_plan.py`, `laneA_apply.py`, `laneA_verify.py`, `laneB_recon.py`,
`laneB_docs.py`, `laneB_build_plan.py`, `laneB_apply.py`, `laneB_verify.py`,
`census_20261002.py` — all DB-lane scripts SELECT-only except the two
fail-closed apply transactions.

## Remaining open (updated)

- **New bank-defect repair lane** (~14 candidates incl. the 1CR/2CR-2016
  version-misalignment cluster) — printed-evidence gated, operator mandate.
- **Structural parse residue (~26 qv)** — needs engine-grade work on
  2015–2019 mark-grid layouts (capped groups, level-marked grids) before
  those schemes can fill honestly.
- §C children VALIDATE_ALL; sibling supersession sign-offs — unchanged.
- V57 executes at next core deploy; post-deploy census re-pin (kn 435).
