# 4CH0/1CR — June 2017 — bridge REVIEW_REQUIRED dossier

- **Bridge record:** `3a268d6f-4cb5-408a-82c7-ce777a5d07bd` · created 2026-09-14 11:33:22.461605+00 · extraction glm-ocr-qp-v1+glm-ocr-ms-v1 · reconciliation **REVIEW_REQUIRED** · 34 findings
- **IDENTITY SPLIT (the lane's sub-finding):** the bridge record anchors to the campaign-era import `QP b4e24b82-2908-53e6-be5f-a587bf1716de` / `MS 3c333fce-057f-554c-be1f-1964834aa10c` — those rows are now REJECTED (0 chunks) / REJECTED (0 chunks). The SERVING documents are a different import lineage: QP `c6437e05-c992-5844-b3d2-a71991795044` VALIDATED v1 (21/21 chunks@rev2) · MS `7195d701-ad3b-5667-8d4c-1dd743021e27` VALIDATED v1 (24/24 chunks@rev2). The findings below describe the bridge import's QP/MS DRAFTS — the printed papers are the same physical documents, so print-total verification remains valid against them.
- **Paper:** validation_state **VALIDATED** (serving at the chunk layer)
- **Bank census:** 15 questions (0 active) · latest versions: 15 VALIDATED / 0 SUGGESTED / 0 REJECTED · total banked marks 97
- **Review items (actionable):** 6 · informational: 10 reconciliation matches · 2 QP warnings · 16 MS warnings

## Review items (fill the verdict column; full-worksheet CSV carries the same rows)

| Q | class | bridge detail | QP | MS | bank serves | pre-adjudication | verdict |
|---|---|---|---|---|---|---|---|
| 10 | **qp-only** | Q10: QP total 7 vs MS total unknown (qp-only) | 7 | — | bank serves 7 (v1, VALIDATED, INACTIVE) | bank serves 7 (v1, VALIDATED, INACTIVE) | ☐ |
| 14 | **qp-only** | Q14: QP total 10 vs MS total unknown (qp-only) | 10 | — | bank serves 10 (v1, VALIDATED, INACTIVE) | bank serves 10 (v1, VALIDATED, INACTIVE) | ☐ |
| 11 | **ms-only** | Q11: QP total unknown vs MS total 9 (ms-only) | — | 9 | bank serves 1 (v1, VALIDATED, INACTIVE) | bank serves 1 (v1, VALIDATED, INACTIVE) | ☐ |
| 3 | **ms-only** | Q3: QP total unknown vs MS total 8 (ms-only) | — | 8 | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| 9 | **ms-only** | Q9: QP total unknown vs MS total 7 (ms-only) | — | 7 | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| paper | **identity-mismatch** | Qpaper: QP total unknown vs MS total unknown (identity-mismatch) | — | — | paper-level identity row (both paper totals unreadable to the parser) | paper-level identity row (both paper totals unreadable to the parser) | ☐ |

Verdict vocabulary: MS-print-verified | gap-accepted | defect(bank-repair lane)

## Reconciliation matches (10 — informational, totals agree)

Q1: QP total 5 vs MS total 5 (match); Q12: QP total 9 vs MS total 9 (match); Q13: QP total 7 vs MS total 7 (match); Q15: QP total 6 vs MS total 6 (match); Q2: QP total 6 vs MS total 6 (match); Q4: QP total 5 vs MS total 5 (match); Q5: QP total 12 vs MS total 12 (match); Q6: QP total 15 vs MS total 15 (match); Q7: QP total 6 vs MS total 6 (match); Q8: QP total 6 vs MS total 6 (match)

## Draft warnings (informational — parser notes on the QP/MS drafts, not itemized for verdict)

**MS_WARNING** ×16 — top patterns:

- ×2 — `#(c)(i): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×2 — `#(b)(i): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×1 — `orphan row before first entry: M# the bromine/liquid evaporates/the particles escape(from `
- ×1 — `#(b): extra integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×1 — `orphan row before first entry: Li`
- ×1 — `orphan row before first entry: melting point`

**QP_WARNING** ×2 — top patterns:

- ×1 — `unclassified heading: volume of sodium hydroxide =`
- ×1 — `Q#: incomplete MCQ option set folded into stem`

