# 4CH1/1CR — June 2020 — bridge REVIEW_REQUIRED dossier

- **Bridge record:** `40d11d8c-129d-4744-862e-d38f65dc00e9` · created 2026-09-14 11:39:35.455548+00 · extraction glm-ocr-qp-v1+glm-ocr-ms-v1 · reconciliation **REVIEW_REQUIRED** · 31 findings
- **IDENTITY SPLIT (the lane's sub-finding):** the bridge record anchors to the campaign-era import `QP 373fe651-97e0-5a09-8958-b83745f38d5b` / `MS 0991194d-8747-57a1-a698-4382ce535424` — those rows are now REJECTED (0 chunks) / REJECTED (0 chunks). The SERVING documents are a different import lineage: QP `9579c4e9-c2c0-5d92-accd-4c8eb13d4ce2` VALIDATED v1 (15/15 chunks@rev2) · MS `67a9e55a-452a-566d-b424-ae31e8db3358` VALIDATED v1 (17/17 chunks@rev2). The findings below describe the bridge import's QP/MS DRAFTS — the printed papers are the same physical documents, so print-total verification remains valid against them.
- **Paper:** validation_state **VALIDATED** (serving at the chunk layer)
- **Bank census:** 10 questions (0 active) · latest versions: 10 VALIDATED / 0 SUGGESTED / 0 REJECTED · total banked marks 56
- **Review items (actionable):** 6 · informational: 0 reconciliation matches · 1 QP warnings · 24 MS warnings

## Review items (fill the verdict column; full-worksheet CSV carries the same rows)

| Q | class | bridge detail | QP | MS | bank serves | pre-adjudication | verdict |
|---|---|---|---|---|---|---|---|
| 1 | **qp-only** | Q1: QP total 6 vs MS total unknown (qp-only) | 6 | — | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| 10 | **qp-only** | Q10: QP total 13 vs MS total unknown (qp-only) | 13 | — | bank serves 13 (v1, VALIDATED, INACTIVE) | bank serves 13 (v1, VALIDATED, INACTIVE) | ☐ |
| 2 | **qp-only** | Q2: QP total 5 vs MS total unknown (qp-only) | 5 | — | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| 4 | **qp-only** | Q4: QP total 14 vs MS total unknown (qp-only) | 14 | — | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| 7 | **qp-only** | Q7: QP total 13 vs MS total unknown (qp-only) | 13 | — | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| paper | **identity-mismatch** | Qpaper: QP total unknown vs MS total unknown (identity-mismatch) | — | — | paper-level identity row (both paper totals unreadable to the parser) | paper-level identity row (both paper totals unreadable to the parser) | ☐ |

Verdict vocabulary: MS-print-verified | gap-accepted | defect(bank-repair lane)

## Draft warnings (informational — parser notes on the QP/MS drafts, not itemized for verdict)

**MS_WARNING** ×24 — top patterns:

- ×4 — `#(a): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×4 — `#(c)(i): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×3 — `#(a)(i): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×2 — `#(b)(i): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×1 — `#(a)(iii): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×1 — `orphan row before first entry: Question number`

**QP_WARNING** ×1 — top patterns:

- ×1 — `unclassified heading: empirical formula =`

