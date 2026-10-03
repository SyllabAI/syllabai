# 4CH0/2C — January 2013 — bridge REVIEW_REQUIRED dossier

- **Bridge record:** `e920ac9f-baed-4995-9574-208279d4ce58` · created 2026-09-14 11:51:32.205866+00 · extraction glm-ocr-qp-v1+glm-ocr-ms-v1 · reconciliation **REVIEW_REQUIRED** · 31 findings
- **IDENTITY SPLIT (the lane's sub-finding):** the bridge record anchors to the campaign-era import `QP 51fea326-2aca-522c-a134-2c43604b0ea9` / `MS 2c568fdb-1720-5516-a830-0bf747013d43` — those rows are now REJECTED (0 chunks) / REJECTED (0 chunks). The SERVING documents are a different import lineage: QP `ba3b57e8-0dd1-5939-a2f2-ae06a583f880` VALIDATED v1 (11/11 chunks@rev2) · MS `2b53b180-78d6-5ca8-bbf5-46e3e86033a5` VALIDATED v1 (8/8 chunks@rev2). The findings below describe the bridge import's QP/MS DRAFTS — the printed papers are the same physical documents, so print-total verification remains valid against them.
- **Paper:** validation_state **VALIDATED** (serving at the chunk layer)
- **Bank census:** 7 questions (0 active) · latest versions: 7 VALIDATED / 0 SUGGESTED / 0 REJECTED · total banked marks 60
- **Review items (actionable):** 3 · informational: 4 reconciliation matches · 2 QP warnings · 22 MS warnings

## Review items (fill the verdict column; full-worksheet CSV carries the same rows)

| Q | class | bridge detail | QP | MS | bank serves | pre-adjudication | verdict |
|---|---|---|---|---|---|---|---|
| 1 | **mismatch** | Q1: QP total 4 vs MS total 8 (mismatch) | 4 | 8 | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| 2 | **qp-only** | Q2: QP total 4 vs MS total unknown (qp-only) | 4 | — | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |
| 3 | **gap** | Q3: QP total unknown vs MS total unknown (gap) | — | — | question not in the structured bank — chunk-layer serving unaffected | question not in the structured bank — chunk-layer serving unaffected | ☐ |

Verdict vocabulary: QP-print-right | MS-print-right | both-wrong(see notes)

## Reconciliation matches (4 — informational, totals agree)

Q4: QP total 11 vs MS total 11 (match); Q5: QP total 12 vs MS total 12 (match); Q6: QP total 11 vs MS total 11 (match); Q7: QP total 10 vs MS total 10 (match)

## Draft warnings (informational — parser notes on the QP/MS drafts, not itemized for verdict)

**MS_WARNING** ×22 — top patterns:

- ×5 — `#(c): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×3 — `#(b): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×2 — `orphan row before first entry: #(a)(i)(ii)`
- ×2 — `#(a)(iv): bare integer cell "#" skipped (rubric/rowspan ambiguity)`
- ×1 — `orphan row before first entry: A`
- ×1 — `orphan row before first entry: M#- no regular pattern overall(particles/they are)more clos`

**QP_WARNING** ×2 — top patterns:

- ×1 — `unclassified heading: Amount of carbonate reacted = mol`
- ×1 — `unclassified heading: Relative formula mass = .`

