# F-PROD-1 — OPERATOR DISPOSITION (2026-10-03): REVIEWED / GOVERNANCE BLOCKED

**Status:** `REVIEWED / GOVERNANCE BLOCKED` — explicitly **not** `PASS` and **not** `CLOSED`. The packet itself remains what it was: the designed input to the teacher's item-by-item act.
**Authority:** operator review of this packet at the pinned commit `762896b` (REPORT.md, `fprod1_review_worksheet.csv`, dossiers, F-PROD-1b sub-finding), disposition issued in operator trace `1a10282dec107275` ("PARTIALLY COMPLETABLE — NO-GO FOR STATUS CLEARING").
**Additive integrity:** this file and `fprod1_review_worksheet_v2_gap_accepted.csv` are NEW files appended to the packet directory. The original 37 packet files (including the pinned worksheet and `SHA256SUMS`) are byte-untouched since `762896b` (`git diff 762896b..HEAD` on this directory is empty). They sit outside the original `SHA256SUMS` pin; the v2 worksheet's own digest is recorded below.

## The disposition, verbatim in substance

1. **No teacher verdicts are fabricated for print-dependent rows.** The packet defines the item-by-item review as the operator/teacher's act, and the packet's artifacts do not contain the underlying printed-page evidence. The verdicts that require a print stay open.
2. **0 production writes from this review. No bridge statuses blindly cleared.** A blind SQL "clear REVIEW_REQUIRED" pass is explicitly rejected.
3. **The blocker is F-PROD-1b bridge identity semantics, not parser quality.** Status clearing is NO-GO until the operator decides one of the three recorded options: (a) re-point bridge records to serving documents; (b) mark the old bridge findings superseded; (c) rebuild the bridges on the serving lineage. That decision is the next governed design/repair lane — not decided by this record.
4. **The unbanked parse-gap rows are closable from the packet's own evidence** — `gap-accepted` is the terminal parse-gap disposition for questions that never entered the structured bank (nothing serves from them; chunk-layer serving unaffected), per REPORT protocol item 4.

## Arithmetic verification (worksheet-derived, recorded honestly)

The operator's table grouped the 176 rows as 113 closable + 33 banked + 7 mismatch + 23 identity-mismatch. The worksheet (`fprod1_review_worksheet.csv`) shows those buckets are **not disjoint**: exactly one `mismatch` row is also banked — 4CH1/1C June 2019 Q13 (QP 12 vs MS 9, bank serves 12 = the QP side), pre-flagged in REPORT protocol Priority 1. The operator's 63 therefore double-counts that one row. The disjoint re-grouping, verified against the worksheet:

| bucket | rows | disposition under this record |
|---|---:|---|
| Unbanked parse gaps (`qp-only` 96 / `ms-only` 10 / `gap` 8) | **114** | `gap-accepted` — closed per the operator's class ruling |
| Banked parse-side findings | **32** | print verification required (bank total vs authoritative print) |
| Genuine QP/MS `mismatch` (incl. the one banked row, Q13) | **7** | print adjudication required (verdict names the authoritative print) |
| Paper `identity-mismatch` | **23** | `paper-totals-verified` requires the two printed paper totals to agree |
| **Total** | **176** | |

So the corrected pair is **114 closable / 62 print-dependent** (not 113/63). The direction and every substantive conclusion of the operator's disposition are unaffected; only the bucket arithmetic is corrected by the one pre-flagged row.

## What this record executed

- **`fprod1_review_worksheet_v2_gap_accepted.csv`** (new): same 176 rows, same order, original columns untouched. The 114 unbanked parse-gap rows carry `teacher_verdict=gap-accepted` with `teacher_notes` provenance citing trace `1a10282dec107275` (class-level disposition; per-row countersignature remains available but is not required — the operator ruled the class terminal). The 62 print-dependent rows carry a **blank** `teacher_verdict` and a `teacher_notes` entry stating the print requirement in the REPORT's own protocol vocabulary.
- Recorded as DATA in the records repo per REPORT protocol item 5. **No endpoint was called; no `reconciliation_status` changed** (none exists that could — protocol item 5).
- `sha256(fprod1_review_worksheet_v2_gap_accepted.csv) = 0b1739cab0e91928aa20ebb17c9ea5f30b432cc619ee717907b363851e36d1a9`

## What stays open after this record

1. **62 print-dependent rows** — the genuine teacher adjudication, working paper-by-paper from the dossiers against the prints (or the corpus's checksum-verified PDFs; REPORT protocol item 4b: the identity split does not block the review, verdicts are made against the prints). Priority order per REPORT: the 7 mismatches first, then the 23 identity rows, then the 32 banked parse-side rows.
2. **F-PROD-1b design decision** (the governance blocker): re-point / mark-superseded / rebuild — the operator's call, then a governed, operator-gated SQL action lane afterwards if a status clearing is still wanted, with the completed worksheet as its evidence base.
3. The workbench read-model refresh and the two non-blocking cross-lane notes in the REPORT remain separate follow-up lanes, unchanged by this disposition.
