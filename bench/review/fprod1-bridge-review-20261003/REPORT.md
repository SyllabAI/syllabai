# F-PROD-1 — the 25-paper REVIEW_REQUIRED bridge review batch (teacher review packet)

**Status:** REVIEW PACKET RECORDED — the item-by-item teacher review is the operator's act; this packet is its designed input (ContentReviewService.validateAllForPaper's own guard language: "review its findings item-by-item"). Zero production writes in this lane.
**Date:** 2026-10-03 | **Authority:** operator directive "1a101959c4bc29ad" trace `1a101959c4bc29ad` ("F-PROD-1's 25-paper review batch"), closing the standing item from the wave-1 PRODUCTION run (T-C41 ① close-out finding F-PROD-1, 2026-10-02).
**The finding being discharged (wave-1 REPORT):** "25 papers serve while carrying unresolved REVIEW_REQUIRED bridge findings — 4CH0/1C ×7, 4CH0/1CR ×3, 4CH0/2C ×5, 4CH0/2CR ×3, 4CH1/1C ×3, 4CH1/1CR ×2, 4CH1/2CR ×2. All 25 bridge REVIEW_REQUIRED papers in production are VALIDATED and serving … these papers either pre-date the bridge gate or were validated with force=true. The bridge findings need item-by-item workbench review by the teacher."

## Method (read-only by construction)

- Production is never touched: extraction ran on a **copy-on-write Neon review branch** (`fprod1-review-ro`, `br-purple-sun-a5huwldd`'s child `br-purple-sun-a5906j1t`), created from production, queried SELECT-only, and **deleted after extraction** — the branch's throwaway credential dies with it. The production roles' credentials were never revealed, reset, or used (the console API surface exposes no reveal/update routes for existing roles — probed and recorded).
- Transport quirks honored (records WORKLOG precedents): `api.neon.tech` has no public A record → control plane via `console.neon.tech/api/v2`; SQL over the Neon serverless HTTP `/sql` transport (psql absent). DB identity gates PASS: `current_database()=neondb`, `campaign_db_identity` row alive (`T-C04-CAMPAIGN`).
- **Production truth confirmed 2026-10-03:** 59 bridge records = 25 `REVIEW_REQUIRED` + 34 `OK` — the F-PROD-1 roster reproduces exactly, unchanged since the wave-1 finding.
- **NEW SUB-FINDING (F-PROD-1b, this lane) — the bridge is identity-detached from serving:** every one of the 25 REVIEW_REQUIRED records anchors to the campaign-era GLM-OCR import's document ids, and in ALL 25 cases those ids DIFFER from the paper's serving canonical document ids (`exam_papers.question_paper_document_id` / `mark_scheme_document_id`). The bridge-linked rows are superseded imports (REJECTED, 0 chunks); the serving docs are a different lineage, all VALIDATED and rev2-complete (0 anomalies across the 25). The drift is NOT REVIEW_REQUIRED-specific: 24 of the 34 OK records drift the same way (49/59 overall) — the re-ingest waves created fresh document identities while the bridge records stayed on the campaign import. Consequences: (a) the findings remain honest PRINT-time reconciliation notes (same printed papers), so the review protocol is unaffected; (b) the REVIEW_REQUIRED gate mechanically blocks validate-all on these papers forever, yet it guards an import that no longer serves — the gate is attached to the wrong lineage; (c) any future status-clearing lane must FIRST decide the identity semantics (re-point bridge records to serving docs vs mark them superseded vs rebuild bridges on the serving lineage) — recorded as an open design item for the operator, not decided by this lane.
- Scripts persisted beside this pack (`fprod1_bridge_probe.py`, `fprod1_bank_probe.py` + their JSON outputs `fprod1_probe_result.json` / `fprod1_bank_result.json`); no credentials anywhere in the pack (env-file pattern, session-only).

## What the findings are (1,366 total across the 25 papers)

| source | severity | n | meaning |
|---|---|---:|---|
| RECONCILIATION | qp-only | 121 | QP question total parsed, MS side unparsed |
| RECONCILIATION | match | 69 | QP vs MS totals agree (informational) |
| RECONCILIATION | mismatch | 7 | **QP vs MS totals genuinely conflict** |
| RECONCILIATION | identity-mismatch | 23 | paper-level identity rows (paper totals unreadable both sides) |
| RECONCILIATION | ms-only | 14 | MS total parsed, QP side unparsed |
| RECONCILIATION | gap | 11 | both sides unparsed |
| QP_WARNING | warning | 57 | parser notes on the QP draft (unclassified headings etc.) |
| MS_WARNING | warning | 1,064 | parser notes on the MS drafts (boilerplate/guidance vocabulary) |

**Actionable review load: 176 rows** (mismatch 7 · identity-mismatch 23 · qp-only 121 · ms-only 14 · gap 11). Of these, **33 sit on questions that exist in the structured bank** (each carries the bank's current served marks + state beside the two print totals); the other 143 describe parse gaps on questions that never entered the bank — chunk-layer serving is unaffected by them, and the verdict vocabulary lets the teacher accept a verified parse gap explicitly instead of leaving it open.

## The review protocol

1. **Work paper-by-paper** (`dossiers/`, ordered by priority below), or row-by-row in `fprod1_review_worksheet.csv` (same rows, verdict + notes columns blank for the teacher).
2. **Priority 1 — the 7 `mismatch` rows** (real print conflicts; one banked: 4CH1/1C June 2019 Q13, QP 12 vs MS 9, bank serves 12 = the QP side, VALIDATED): check the printed QP and MS for that question; the verdict names which print is authoritative.
3. **Priority 2 — the 23 `identity-mismatch` paper rows**: the parser could not read EITHER paper total, so the QP↔MS identity check never ran; verdict `paper-totals-verified` requires the two printed paper totals to agree (the 2026-10-02 folder-mislabel audit's lesson: checksums + page-1 content are the identity, folder names are not).
4. **Priority 3 — the 146 parse-side rows** (`qp-only`/`ms-only`/`gap`): for banked rows, verify the bank's total against the authoritative print; for unbanked rows, `gap-accepted` is an honest terminal verdict (the question was never extracted; nothing serves from it).
4b. **The identity split does NOT block the review:** the findings describe the bridge import's drafts of the same printed papers; verdicts are made against the PRINTS (or the corpus's checksum-verified PDFs), not against either import lineage.
5. **What happens after the verdicts:** the completed worksheet is recorded as data in the records repo. There is NO endpoint today that flips a bridge record's `reconciliation_status` — a status clearing, if the operator wants one, is a governed SQL action lane afterwards (the wave kit / bank-defect tx pattern), operator-gated, with the completed worksheet as its evidence base.

## Cross-lane checks recorded

- **Bank-defect repair lane (2026-10-02) overlap: NONE.** Its four repaired questions (4CH1/1CR 2013 Q9, 4CH1/1CR 2022 Q11, 4CH1/1CR 2016 Q1, 4CH1/1C 2016 Q10) sit on 4CH1 paper sessions that are NOT among these 25 REVIEW_REQUIRED papers (whose 4CH1 members are 1C 2019/2020/2024, 1CR 2019/2020, 2CR 2019/2023). The two lanes are disjoint.
- **Serving state of the 25 (verified on the SERVING docs, not the bridge rows):** every paper is VALIDATED with both serving documents VALIDATED and every chunk embedded at rev2 (0 anomalies across the 25; per-paper counts in the dossiers) — they are live serving content, which is why the doctrine treats unreviewed findings as a governance debt, not a theoretical one. See the F-PROD-1b sub-finding above for the identity split behind this.
- **Structured-bank state: all 249 questions on these papers have `active=false`** — the papers serve at the CHUNK layer (tutor evidence), and none of their structured question items are live learner-facing rows. The bridge findings therefore guard chunk-layer correctness today, and the bank rows' future re-activation.
- **Workbench review surface is stale by design boundary:** its derived dataset (`data/review`, campaign-era, 34 REVIEW_REQUIRED sessions on a different code distribution) does not match production; this packet IS the fresh production truth. Refreshing the workbench read model from a production snapshot is a separate follow-up lane, not part of this review.

## The 25-paper roster (bank census × bridge findings)

| paper | session | questions (active) | qv VALIDATED | banked marks | actionable findings | dossier |
|---|---|---|---:|---:|---:|---|
| 4CH0/1C | January 2013 | 10 (0) | 10 | 120 | 2 | `4CH0-1C-January-2013.md` |
| 4CH0/1C | June 2012 | 13 (0) | 13 | 94 | 11 | `4CH0-1C-June-2012.md` |
| 4CH0/1C | June 2013 | 11 (0) | 11 | 81 | 9 | `4CH0-1C-June-2013.md` |
| 4CH0/1C | June 2015 | 11 (0) | 11 | 120 | 12 | `4CH0-1C-June-2015.md` |
| 4CH0/1C | June 2016 | 16 (0) | 16 | 105 | 14 | `4CH0-1C-June-2016.md` |
| 4CH0/1C | June 2017 | 11 (0) | 11 | 102 | 3 | `4CH0-1C-June-2017.md` |
| 4CH0/1C | June 2018 | 15 (0) | 15 | 104 | 4 | `4CH0-1C-June-2018.md` |
| 4CH0/1CR | June 2013 | 11 (0) | 11 | 120 | 8 | `4CH0-1CR-June-2013.md` |
| 4CH0/1CR | June 2016 | 12 (0) | 12 | 120 | 13 | `4CH0-1CR-June-2016.md` |
| 4CH0/1CR | June 2017 | 15 (0) | 15 | 97 | 6 | `4CH0-1CR-June-2017.md` |
| 4CH0/2C | January 2013 | 7 (0) | 7 | 60 | 3 | `4CH0-2C-January-2013.md` |
| 4CH0/2C | June 2013 | 7 (0) | 7 | 60 | 3 | `4CH0-2C-June-2013.md` |
| 4CH0/2C | June 2015 | 6 (0) | 6 | 43 | 5 | `4CH0-2C-June-2015.md` |
| 4CH0/2C | June 2017 | 5 (0) | 5 | 32 | 3 | `4CH0-2C-June-2017.md` |
| 4CH0/2C | June 2018 | 9 (0) | 9 | 53 | 9 | `4CH0-2C-June-2018.md` |
| 4CH0/2CR | June 2013 | 6 (0) | 6 | 42 | 2 | `4CH0-2CR-June-2013.md` |
| 4CH0/2CR | June 2016 | 7 (0) | 7 | 60 | 8 | `4CH0-2CR-June-2016.md` |
| 4CH0/2CR | June 2017 | 8 (0) | 8 | 60 | 3 | `4CH0-2CR-June-2017.md` |
| 4CH1/1C | June 2019 | 15 (0) | 15 | 110 | 16 | `4CH1-1C-June-2019.md` |
| 4CH1/1C | June 2020 | 10 (0) | 10 | 62 | 7 | `4CH1-1C-June-2020.md` |
| 4CH1/1C | June 2024 | 10 (0) | 10 | 61 | 6 | `4CH1-1C-June-2024.md` |
| 4CH1/1CR | June 2019 | 10 (0) | 10 | 98 | 10 | `4CH1-1CR-June-2019.md` |
| 4CH1/1CR | June 2020 | 10 (0) | 10 | 56 | 6 | `4CH1-1CR-June-2020.md` |
| 4CH1/2CR | June 2019 | 7 (0) | 7 | 48 | 6 | `4CH1-2CR-June-2019.md` |
| 4CH1/2CR | June 2023 | 7 (0) | 7 | 58 | 7 | `4CH1-2CR-June-2023.md` |

