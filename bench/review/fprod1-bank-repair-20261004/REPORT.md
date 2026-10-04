# F-PROD-1 bank-repair lane — the 4 print-pass defect rows repaired to the printed totals (2026-10-04)

**Status:** EXECUTED — production V61 applied `2026-10-04T02:14:31.79Z`, post-flight **ALL PASS**. The four defect rows referred out by the print pass now serve the printed totals in both bank tables.
**Authority chain:** print-pass referral (`bench/review/fprod1-print-pass-20261004/REPORT.md` P3, records `2ffbbb3`) → operator word **"repair the 4 bank entries"** (trace `1a1047d4ad41baf9`) → method = the laneD standard (`bench/review/psaxis-review-2026-09-28/bank-defect-lane-20261002/`, the 2026-10-02 bank-defect lane that repaired the same "banked as 1" defect class) → write channel = core Flyway V61, the V60 census-gated precedent (PR syllabai-core **#79**, head `f482af2` CI success, merged **`e222e455`**, post-merge main CI success).

## The four repairs

| ref | paper / session | QN | bank (before) | printed total | delta |
|---|---|---|---:|---:|---:|
| `q10-6d968517` | 4CH0/1C June 2013 | Q10 | 1 | **13** | +12 |
| `q11-8b9f4957` | 4CH0/1C June 2017 | Q11 | 1 | **11** | +10 |
| `q12-23323bab` | 4CH0/1C June 2018 | Q12 | 1 | **11** | +10 |
| `q11-b4e24b82` | 4CH0/1CR June 2017 | Q11 | 1 | **9** | +8 |

Total marks delta **+40** (asserted exactly, in-tx, on both `questions` and `question_versions`).

## Evidence per the laneD standard (fail-closed; any gate miss aborts)

1. **Bank prestate pinned** (probe, SELECT-only on COW branch): each ref resolves to exactly 1 row; `qv.marks=1 AND q.marks=1`, VALIDATED, version 1, parts present but 0-mark (the partial-ingest shape: 10/5/12/11 parts, Σ0), 1 scheme each carrying 2/4/10/8 mark_points. Paper rows VALIDATED.
2. **Byte identity**: all 8 serving QP/MS documents (4 papers × QP+MS) **checksum-matched to the corpus prints** (`syllabai-pastpapers` @ `b8d53f75`, chemistry/4ch0; bytes identical to the print-pass substrate `1f7e8355`). Bridge rows for the 4 papers: SUPERSEDED (REJECTED bridge docs, 0-chunk) — the serving lineage is untouched by that state.
3. **QP echo** (local `pdftotext -layout` over the checksum-matched bytes): `(Total for Question 10 = 13 marks)` / `11` / `11` / `(Total for Question 11 = 9 marks)` — mechanical re-parse in the plan builder.
4. **MS corroboration, DB side**: the serving MS chunks carry the printed totals — ingest-time atom lines (`Question 10 printed total: 13 marks` in 1C-2013 chunk 21; `Question 11 printed total: 9 marks` in 1CR-2017 chunk 17 — with Q14 absent, exactly the print pass's "14/15 printed" finding) and plain text totals (`(Total for Question 11 = 11 marks)` 1C-2017 chunk 22; `Total for Question 12 = 11 marks` 1C-2018 chunk 24). Local MS prints read the same block totals (verified with block-boundary context for the two bare-`Total`-format 2013/1CR MSs).
5. **Variant attribution** (laneD substrate = ingested chunk text): bank stem+part tokens (publisher copyright footers and LaTeX command names normalized out, applied identically to all variants) vs each variant's ingested serving-QP chunk text — own-variant **0.9825 / 0.9904 / 1.0 / 1.0**, cross-variant margins **0.386 / 0.279 / n/a / 0.458** (gate ≥0.90 + ≥0.02). 1C June 2018: no 1CR-2018 print bytes exist in the corpus AND no such `exam_papers` row exists in the DB — the discriminator is structurally absent, so attribution there rests on the own score (1.0) plus `qv.source_document_id` provenance (recorded in the plan).
6. **Provenance**: all four qv carry `source_document_id` = their own paper's serving QP doc (the checksum-matched prints), method `glm-ocr-qp-v1+glm-ocr-ms-v1`, ingested 2026-09-14.

**Plan pinned pre-write**: `bankrepair_plan.json` sha256 `5cda1a0d5afcb44c5cb8e7120dcdac719914846bc401d23c0e0c77a7bf3712ae` (builder `bankrepair_build_plan.py`, SELECT-only inputs).

## Execution

- **Migration `V61__fprod1_bank_marks_repair.sql`** (branch `fprod1-bank-repair` @ `6a40a6d` → gate fixed `f482af2` → **PR syllabai-core #79** → merged **`e222e455`**): census-gated `DO` block — identity gate (V15 discipline: fresh/test DBs never claim campaign identity → no-op by construction; the first CI run failed exactly here on the seeded IT DBs, fixed before merge and recorded honestly), exact census pins (papers 91V/13R · qv 1526 = 1465V/59S/2R · questions 1526/954 active · parts 7183/Σ9068 · schemes 1504 = 1360V/144S · mp 5883 · bridge 10 OK + 49 SUPERSEDED + 0 RR), audit **monotonic floor** 5586 (teacher traffic may append benign rows between probe and deploy — exact-max pinning was deliberately NOT carried over from laneD's same-session tx), then 8 double-condition-guarded UPDATEs (id + external_ref + paper join + `marks = 1`), `GET DIAGNOSTICS` = 1 each, in-tx after-image asserts and marks-sum delta == +40 on both tables; any RAISE aborts the deploy.
- Local offline suite on the pushed head: **1259 / 0 failures / 0 errors / 2 skipped** (JDK 25.0.4.1 Corretto + Maven 3.9.9, T-C59 recipe; toolchain restored this session after sandbox loss — one transient first-run error, immediate clean re-run, no code change). Head CI success; post-merge main CI success.
- **Deploy + post-flight** (`bankrepair_postflight.py`, fresh COW poll branch, SELECT-only, deleted after): V61 `success=true` installed `2026-10-04T02:14:31.79Z`; the 4 rows read `qv.marks == q.marks == 13/11/11/9`, VALIDATED; marks sums 11713 on both tables (pre 11673, delta +40); every census pin unchanged (states, parts, schemes, points, papers, bridge); **POST-FLIGHT: ALL PASS**. (One verify-script bug — a dict-vs-int compare on the mp count — briefly showed FAIL on the first post-flight run; the data was green throughout; corrected and re-run for a clean receipt.)

## Scope discipline

Marks only. `question_parts`, `mark_schemes`, `mark_points`, validation states, audit, and the serving document/chunk layer are untouched (count pins prove zero collateral). No state flips; no audit rows written by the lane. The partial-scheme shape (parts 0-mark, 2/4/10/8 points) remains the sparse-scheme structural residue's business, unchanged policy.

The worksheet v3 (`fprod1_review_worksheet_v3_print_pass.csv`, sha `419521e6…`) stays byte-frozen as the adjudication record; this pack is the defect-closure receipt for its 4 `defect(bank-repair lane)` rows.

## Files

`REPORT.md` (this file) · `bankrepair_plan.json` (sha-pinned evidence + before/after images) · `bankrepair_probe.py` / `bankrepair_probe2.py` / `bankrepair_probe3.py` + their `_output.txt` / `_result.json` · `bankrepair_build_plan.py` · `bankrepair_postflight.py` + `postflight_output.txt` / `postflight_result.json` · `SHA256SUMS`.

Scripts are also the session workspace `/home/z/my-project/scripts/bankrepair20261004/` (not credential-bearing; the Neon API key lived only in the session env file `/home/z/my-project/.env-session`, purged post-lane).

## Remaining open (F-PROD-1 surface)

- P2's 3 narrowed rows (`qp-total-printed-ms-total-unprinted`, the 2016-family MS format fact) — print-evidence boundary, no serving risk, unchanged.
- The engine-grade grid-layout lane (sparse-scheme structural residue) — unchanged.
- Secrets rotation (GH_PAT + RENDER_KEY + Neon) — standing operator item.
