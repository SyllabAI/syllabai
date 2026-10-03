# 4CH0/2CR — June 2017 — bridge REVIEW_REQUIRED dossier

- **Bridge record:** `8f6ff0a6-1c5d-4344-abd4-12981c9c3b73` · created 2026-09-14 11:57:14.125644+00 · extraction glm-ocr-qp-v1+glm-ocr-ms-v1 · reconciliation **REVIEW_REQUIRED** · 21 findings
- **IDENTITY SPLIT (the lane's sub-finding):** the bridge record anchors to the campaign-era import `QP c8e045a4-c04b-5493-aa15-ca13b23aee5f` / `MS c5c34898-8a0a-533c-bf24-68eb258f7fab` — those rows are now REJECTED (0 chunks) / REJECTED (0 chunks). The SERVING documents are a different import lineage: QP `e9ebba09-cfa9-5fcf-86ad-f4624448f4f5` VALIDATED v1 (13/13 chunks@rev2) · MS `a03f9ddf-8f22-54ea-aa64-68e8304bca9a` VALIDATED v1 (12/12 chunks@rev2). The findings below describe the bridge import's QP/MS DRAFTS — the printed papers are the same physical documents, so print-total verification remains valid against them.
- **Paper:** validation_state **VALIDATED** (serving at the chunk layer)
- **Bank census:** 8 questions (0 active) · latest versions: 8 VALIDATED / 0 SUGGESTED / 0 REJECTED · total banked marks 60
- **Review items (actionable):** 3 · informational: 6 reconciliation matches · 1 QP warnings · 11 MS warnings

## Review items (fill the verdict column; full-worksheet CSV carries the same rows)

| Q | class | bridge detail | QP | MS | bank serves | pre-adjudication | verdict |
|---|---|---|---|---|---|---|---|
| 4 | **mismatch** | Q4: QP total 9 vs MS total 6 (mismatch) | 9 | 6 | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| 5 | **qp-only** | Q5: QP total 6 vs MS total unknown (qp-only) | 6 | — | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| paper | **identity-mismatch** | Qpaper: QP total unknown vs MS total unknown (identity-mismatch) | — | — | paper-level identity row (both paper totals unreadable to the parser) | paper-level identity row (both paper totals unreadable to the parser) | ☐ |

Verdict vocabulary: QP-print-right | MS-print-right | both-wrong(see notes)

## Reconciliation matches (6 — informational, totals agree)

Q1: QP total 5 vs MS total 5 (match); Q2: QP total 4 vs MS total 4 (match); Q3: QP total 6 vs MS total 6 (match); Q6: QP total 10 vs MS total 10 (match); Q7: QP total 12 vs MS total 12 (match); Q8: QP total 8 vs MS total 8 (match)

## Draft warnings (informational — parser notes on the QP/MS drafts, not itemized for verdict)

**MS_WARNING** ×11 — top patterns:

- ×4 — `orphan row before first entry: Question`
- ×2 — `#(a): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×1 — `orphan row before first entry: #(c)(i)(ii)`
- ×1 — `orphan row before first entry: (d)(i)(ii)`
- ×1 — `orphan row before first entry: #(a)(i)(ii)`
- ×1 — `total conflict for question #: # (first) vs # (in-table bare-total row)`

**QP_WARNING** ×1 — top patterns:

- ×1 — `Q#: incomplete MCQ option set folded into stem`

