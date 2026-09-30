# Bank-wave evidence — documents-v2-aligned bank supersession (2026-09-26)

Operator directive: "Proceed" (continuation of "run rw-9b on the 13 clear pairs",
trace 1a0d92b411af5051). This wave is the bank half staged by rw-9b's report
("Flags for the next waves" 1–2 + the glmocr-row supersession for the cleared pairs).

## Scope (derive-locked, not trusted)

Inputs: `reparse_g17_report.json` (13 clear pairs = 15 corrected − 1c-201906/1c-202206
G1-FAILs), `bankwave_probe.py`/`bankwave_probe2.py` (fresh read-only DB probes:
bank-content generations, row-level validation states, guard counts, subject
bindings, FK delete rules), `drive_state.json` (per-paper execution record).

| class | papers | disposition |
|---|---|---|
| REPLACE ×11 | 2c-202206 (R-derived content, 09-24 drive) + 10 glmocr-sourced cleared pairs (1c-202001/0101/0201/0301/0306, 2c-201906/0200 1/0201/0301/0306 — note: 2c-201906 old refs were dangling) | archive → guards → delete → POST corrected-C draft (g17 atoms, v2 doc refs) |
| NEW ×1 | 4ch1-2c-202011 (4CH1/2C November 2020 — ep row ABSENT since the paper was MS-only pre-repair) | POST (no delete) |
| MERGE ×2 | 4CH1/2C Summer 2022 + 4CH1/2CR Summer 2022 duplicate-sitting rows (June 2022 rows are the canonical same-sitting registrations) | archive → guards → delete (no POST) |
| REPOINT ×1 | 4CH1/2CR June 2022 ep pointers + 7 qv + 7 ms source refs: uuid-PK form → varchar document_id form (app-visible; rw-9b left this pair out of scope by design) | guarded UPDATE |
| SKIP ×1 | **4ch1-2c-202101 (4CH1/2C January 2021): NOT TOUCHED — 7 qv + 7 ms rows are teacher-VALIDATED and 3 learner attempts (OVERRIDDEN, web-structured-v1) + 14 answers + 14 human_marks hang off them. Standing discipline: zero teacher-validated rows destroyed; no blind deletes.** Supersession needs an operator decision (version-bump path or re-validation flow). | untouched, flagged |

## Drafts

`tools/pdflane/atoms_to_draft.py` (parser-g6 @ 2e4ba19, the audited G8/A1 converter,
unchanged) over the g17 closure-verified atoms. Identity pinned to the 09-24 drive
discipline: board=Edexcel, qualification=4CH1, subject=Chemistry (resolves to
subjects.code `4CH1CHEMISTRY`), unit=<variant>; sessionLabel/paperCode from the
g17 inputs (== the live ep identities); QP/MS document ids = the rw-9b v2
documents (checksum-pinned to corpus HEAD manifests). externalRef convention
`4ch1/past-papers/<yyyy>-<mm>/4CH1-<variant>#q<n>`. Gates before build:
envelope marksVerified=True, questionCount == g17 census; per-paper marks sums
close at 110 (1C) / 70 (2C).

## Execution (scripts/bankwave_drive.py, resumable, fail-closed)

Every destructive step: full row archive FIRST (`archives/*.archive.json`,
13 files — 11 REPLACE + 2 MERGE), inline guard assertion (attempts / answers /
human_marks / smart_mark_results / agreement_evals all 0 — DB FK NO ACTION rules
back this), then delete in FK-safe order (mark_points → bridge records →
questions cascade → exam_papers), commit, then `POST /api/v1/teacher/content/past-papers`
(201) with per-paper verify (ep pointers on v2, qv/ms sources on v2, all rows
SUGGESTED, extraction_method `pdflane-atoms-draft-v1`, counts == draft).
Audit tables (content_review_audit / teacher_validation_events) were never
deleted; referencing rows are inside the archives. One defect found and fixed
en route: mark_points→question_part_id FK is NO ACTION, so mark_points need an
explicit delete before the questions cascade (the A1 recipe did the same).

## Post-gates (scripts/bankwave_verify.py, ALL PASS)

- 12/12 driven papers row-level verified; per-paper marks sums == closure totals.
- Merged rows absent (Summer 2022 gone); documents axis untouched.
- 2CR June 2022 fully app-visible (varchar form), bank-wide uuid-form ep pointers 0.
- 4CH1/2C January 2021 delta 0 (VALIDATED rows + learner activity intact).
- Driven papers carry zero refs off the v2 documents.
- Bank-wide unresolvable source-ref values (glmocr-era, pre-existing): qv 4 /
  ms 13 distinct — unchanged by this wave outside its scope.

## Totals (derive-locked from archives + ingested summaries)

| table | pre | post | net |
|---|---|---|---|
| exam_papers | 105 | 104 | −1 (+1 NEW, −2 MERGE) |
| questions | 1,540 | 1,533 | −7 (REPLACE net 0, NEW +7, MERGE −14) |
| mark_schemes | — | 1,418 | one scheme per question (v1) |
| mark_points | 5,197 | 5,271 | +74 |
| glm_ocr_bridge_records | 72 | 64 | −8 (deleted with their papers, archived) |

Attempts / smart_mark_results / agreement_evals / human_marks deltas: **0**
outside the untouched SKIP paper (whose rows are intact by assertion).

## Provenance chain (per driven paper)

corrected corpus bytes (F10 repair, sha-pinned) → G6 identity gate → g17
closure-verified atoms (marksVerified=true) → deterministic draft converter →
bank rows → rw-9b v2 documents (same checksum pins) → 349/349 embedded chunks.
Every hop checksum- or count-verified.
