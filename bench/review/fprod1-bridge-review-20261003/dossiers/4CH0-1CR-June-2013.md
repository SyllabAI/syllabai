# 4CH0/1CR — June 2013 — bridge REVIEW_REQUIRED dossier

- **Bridge record:** `8ffe0f38-e993-46de-90ba-22d1a80cb10a` · created 2026-09-14 11:27:06.393476+00 · extraction glm-ocr-qp-v1+glm-ocr-ms-v1 · reconciliation **REVIEW_REQUIRED** · 76 findings
- **IDENTITY SPLIT (the lane's sub-finding):** the bridge record anchors to the campaign-era import `QP 57202de4-25eb-5bae-b3e4-7d128464d1d2` / `MS 37de7d90-dbc8-5691-919a-b9c45482a22e` — those rows are now REJECTED (0 chunks) / REJECTED (0 chunks). The SERVING documents are a different import lineage: QP `2f52e30b-1dc7-5b6a-8e0e-84ddb845ce8a` VALIDATED v1 (24/24 chunks@rev2) · MS `8936b097-52a6-57f7-a6cb-b464c6524d49` VALIDATED v1 (21/21 chunks@rev2). The findings below describe the bridge import's QP/MS DRAFTS — the printed papers are the same physical documents, so print-total verification remains valid against them.
- **Paper:** validation_state **VALIDATED** (serving at the chunk layer)
- **Bank census:** 11 questions (0 active) · latest versions: 11 VALIDATED / 0 SUGGESTED / 0 REJECTED · total banked marks 120
- **Review items (actionable):** 8 · informational: 4 reconciliation matches · 2 QP warnings · 62 MS warnings

## Review items (fill the verdict column; full-worksheet CSV carries the same rows)

| Q | class | bridge detail | QP | MS | bank serves | pre-adjudication | verdict |
|---|---|---|---|---|---|---|---|
| 11 | **qp-only** | Q11: QP total 9 vs MS total unknown (qp-only) | 9 | — | bank serves 9 (v1, VALIDATED, INACTIVE) | bank serves 9 (v1, VALIDATED, INACTIVE) | ☐ |
| 4 | **qp-only** | Q4: QP total 10 vs MS total unknown (qp-only) | 10 | — | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| 5 | **mismatch** | Q5: QP total 11 vs MS total 16 (mismatch) | 11 | 16 | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| 6 | **qp-only** | Q6: QP total 16 vs MS total unknown (qp-only) | 16 | — | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| 7 | **mismatch** | Q7: QP total 16 vs MS total 9 (mismatch) | 16 | 9 | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| 8 | **qp-only** | Q8: QP total 8 vs MS total unknown (qp-only) | 8 | — | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| 9 | **gap** | Q9: QP total unknown vs MS total unknown (gap) | — | — | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| paper | **identity-mismatch** | Qpaper: QP total unknown vs MS total unknown (identity-mismatch) | — | — | paper-level identity row (both paper totals unreadable to the parser) | paper-level identity row (both paper totals unreadable to the parser) | ☐ |

Verdict vocabulary: MS-print-verified | gap-accepted | defect(bank-repair lane)

## Reconciliation matches (4 — informational, totals agree)

Q1: QP total 8 vs MS total 8 (match); Q10: QP total 15 vs MS total 15 (match); Q2: QP total 6 vs MS total 6 (match); Q3: QP total 12 vs MS total 12 (match)

## Draft warnings (informational — parser notes on the QP/MS drafts, not itemized for verdict)

**MS_WARNING** ×62 — top patterns:

- ×11 — `#(a): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×6 — `#(d): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×6 — `#(e)(iv): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×4 — `#(b): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×3 — `orphan row before first entry: Total`
- ×3 — `#(a)(iii): bare integer cell "#" skipped (rubric/rowspan ambiguity)`

**QP_WARNING** ×2 — top patterns:

- ×1 — `unclassified heading: THE PERIODIC TABLE`
- ×1 — `unclassified heading: Letter`

