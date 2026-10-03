# 4CH0/2CR — June 2013 — bridge REVIEW_REQUIRED dossier

- **Bridge record:** `0e8cfd65-1e35-4143-9a51-fa7739a81c46` · created 2026-09-14 11:51:41.727684+00 · extraction glm-ocr-qp-v1+glm-ocr-ms-v1 · reconciliation **REVIEW_REQUIRED** · 42 findings
- **IDENTITY SPLIT (the lane's sub-finding):** the bridge record anchors to the campaign-era import `QP cdfcbae1-e909-5fab-877f-572b29981d28` / `MS 70b23e58-60f0-5b96-8337-da490e265a66` — those rows are now REJECTED (0 chunks) / REJECTED (0 chunks). The SERVING documents are a different import lineage: QP `33ba399c-4640-5b04-b1bb-b520fa2ba94c` VALIDATED v1 (11/11 chunks@rev2) · MS `1d17abcc-fb53-5115-b266-911fbab52ab9` VALIDATED v1 (10/10 chunks@rev2). The findings below describe the bridge import's QP/MS DRAFTS — the printed papers are the same physical documents, so print-total verification remains valid against them.
- **Paper:** validation_state **VALIDATED** (serving at the chunk layer)
- **Bank census:** 6 questions (0 active) · latest versions: 6 VALIDATED / 0 SUGGESTED / 0 REJECTED · total banked marks 42
- **Review items (actionable):** 2 · informational: 5 reconciliation matches · 2 QP warnings · 33 MS warnings

## Review items (fill the verdict column; full-worksheet CSV carries the same rows)

| Q | class | bridge detail | QP | MS | bank serves | pre-adjudication | verdict |
|---|---|---|---|---|---|---|---|
| 5 | **ms-only** | Q5: QP total unknown vs MS total 19 (ms-only) | — | 19 | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| paper | **identity-mismatch** | Qpaper: QP total unknown vs MS total unknown (identity-mismatch) | — | — | paper-level identity row (both paper totals unreadable to the parser) | paper-level identity row (both paper totals unreadable to the parser) | ☐ |

Verdict vocabulary: QP-print-verified | gap-accepted | defect(bank-repair lane)

## Reconciliation matches (5 — informational, totals agree)

Q1: QP total 5 vs MS total 5 (match); Q2: QP total 7 vs MS total 7 (match); Q3: QP total 8 vs MS total 8 (match); Q4: QP total 9 vs MS total 9 (match); Q6: QP total 12 vs MS total 12 (match)

## Draft warnings (informational — parser notes on the QP/MS drafts, not itemized for verdict)

**MS_WARNING** ×33 — top patterns:

- ×14 — `#(a): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×6 — `#: bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×2 — `#(b): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×2 — `#(c): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×2 — `#(d): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×1 — `orphan row before first entry: #(c)i`

**QP_WARNING** ×2 — top patterns:

- ×2 — `Q#: incomplete MCQ option set folded into stem`

