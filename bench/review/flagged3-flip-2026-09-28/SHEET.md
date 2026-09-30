# Operator mini-sheet — flagged3 flip (#207 / #278 / #291 → VALIDATE)

**Batch:** `flagged3-flip-2026-09-28` · **Decision authority:** operator Nawaf Al Hussain
Khondokar · **Named instruction:** "flip #207/#278/#291 to VALIDATE" (IM trace
`1a0e7865c3b35715`, 2026-09-28) · **Basis:** source verification REPORT.md 3/3 faithful
(sha256 `23ead2a7…`), the flag drivers being the sheet-renderer artifact plus the honest
spec-skip — both explained, neither a content fault.

| sheet # | documents.id (UUID) | kind | pre-state | decision | external_ref | bank marks | spec pts |
|---|---|---|---|---|---|---|---|
| 207 | `1c15d529-661b-53a7-a8ed-a934328e6afb` | EXTERNAL_QUESTIONS | FLAGGED | **VALIDATE** | `4ch1/past-papers/2020-01/4CH1-2C#q3` | 11 | 0 |
| 278 | `ee882008-88ca-5952-af9c-5505c8f76661` | EXTERNAL_QUESTIONS | FLAGGED | **VALIDATE** | `4ch1/past-papers/2020-06/4ch1-2CR#q1` | 5 | 0 |
| 291 | `1195ca6c-0ecd-5890-b63e-4c2df7ebddba` | EXTERNAL_QUESTIONS | FLAGGED | **VALIDATE** | `4ch1/past-papers/2023-01/4CH1-2CR#q1` | 4 | 0 |

Machine-readable source of truth: `flip_decisions.json` (this sheet is its human view).
The spec linkage stays **none** for all 3 — the T-C27 "3 honest skips" stand; the flip
adopts the operator's judgment on content authenticity and does not fabricate linkage.

## Write contract (identical in kind to the proven 298-row wave import, run `a5d13c0a…`)

- `documents.validation_state`: FLAGGED → VALIDATED for exactly the 3 UUIDs above.
- `content_review_audit`: one row each — action `VALIDATE`, target_type `question`
  (the same vocabulary the wave import used), from_state `FLAGGED`, to_state
  `VALIDATED`, detail carrying the operator trace, both sha256 pins, and the batch id.
- Nothing else. No content, chunk, embedding, or bank writes; `document_chunks` has no
  state column — card serving state derives from the parent document via the JOIN.

## Census gate

| EXTERNAL_QUESTIONS documents | before | after |
|---|---|---|
| VALIDATED | 296 | **299** |
| SUGGESTED | 80 | 80 |
| FLAGGED | 3 | **0** |
| REJECTED | 0 | 0 |

The importer aborts unless production shows the exact "before" census — if anything
moved since the snap-005 freeze, re-verify first; the flip never runs on drift.

**Census correction 2026-09-28:** figures above re-probed live (the kit author held no
production credentials; the original 306V/747S were derived, not probed) — the probed
census is 296V/80S/3F before → 299V/80S/0F after. Decision and delta unchanged.

