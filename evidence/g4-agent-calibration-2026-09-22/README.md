# G-4 Agent Calibration Round — EXECUTED 2026-09-22

**PROVENANCE: `AGENT_MARKING`.** Every marking decision in this round was produced by
the operating agent (LLM-driven), NOT by a human teacher or pilot staff. This record is
an **ENGINEERING / AGENT CALIBRATION**. It is not, and must never be reported as,
teacher calibration, and it does **not** satisfy the κ release gate (F-161 / Master
Spec §15), which by ADR-025/ADR-027 requires a genuine human reference marking.

## What executed (all through legitimate production surfaces)

1. **Regeneration path (runbook-sanctioned).** The session-96 κ sample is teacher-queue
   data; no teacher credentials exist in this environment and ADR-025 forbids
   provisioning any. The rebuilt runbook's own fallback was executed instead: a fresh
   TEST learner `pilot.g4agent@syllabai-test.dev` (public register API, STUDENT role;
   the documented session-58/96 pattern) generated **7 structured attempts × 26 part
   answers** on the SAME CELLS as the original sample (4CH1 S1-c ×2, S2-e ×1, S1-f ×1 —
   recorded substitution; details in `round_record.json`).
2. **Learner answers authored** under the documented round-001 simulated-learner profile
   (mid-ability; controlled inputs, honestly labeled in `round_record.json`).
3. **BLIND AGENT MARKING.** 26 per-point decisions were made from the learner-revealed
   scheme surface (point ref + text + marks) against the learner answer ONLY — no Smart
   Mark output existed for these fresh attempts at decision time. Decisions were frozen
   to `agent_decisions.json` (sha256 `255265d7608d0c5e6d5a3e6f1468ea6cb0b5fe996836815e09c63a9e1eeafef6`,
   stamped into `blind_worksheet.json`) BEFORE any Smart Mark call. No production
   `HumanMark` row was written anywhere (a teacher endpoint is the only writer, and
   writing agent decisions there would fabricate human provenance).
4. **Smart Mark executed** on all 7 attempts via the student surface
   (`POST /api/v1/learners/me/attempts/{id}/smart-mark`) — the SAME pipeline the teacher
   queue runs. All 7 returned 200: G-2 VALIDATED-only selection satisfied (all schemes
   VALIDATED), model `openai/gpt-oss-120b`, deterministic validators active, per-part
   `authoritative=false` pre-gate (honest gated state — see
   `release_state_per_part.json`). 25/26 parts produced validation-passed results; 1
   part (5-mark explain question) produced an `UNPARSEABLE_OUTPUT` refusal row —
   fail-closed worked as designed; recorded, not retried.
5. **κ computed OFFLINE** with an exact port of `KappaAgreementService.cohenKappa`
   (repo `14b5e3d`), pairing exactly as `TeacherMarkingService.evaluateAgreement` pairs
   (per common markPointId, smart side = breakdown `awarded` boolean, validation-passed
   runs only). n=25 (1 pair dropped by the honest refusal).

## κ results (same frozen dataset, two declared conventions)

| Convention | κ | observed | expected | n | gate (≥0.60) |
|---|---|---|---|---|---|
| A — "point fully earned" (as frozen) | **0.3119** | 0.76 | 0.6512 | 25 | **NO** |
| B — production-mirror "any credit = 1" | **1.0000** | 1.00 | 0.8528 | 25 | YES |

Convention B re-reads the SAME frozen rationales under the semantic the production code
actually pairs against (`TeacherMarkingService.java` 176–189: any credit on a point →
`awarded=true` → smart=1). No decision was changed after seeing Smart Mark output; the
derivation is mechanical per-rationale and documented in `kappa_final.json`.

## Findings

1. **Gate-critical convention gap (FIXED in the runbook).** Step 1's "awarded = 1, not
   awarded = 0" was ambiguous on bundled multi-mark points (SME schemes bundle whole
   parts into one multi-mark point). The same blind judgments read κ=0.31 under "fully
   earned" and κ=1.00 under the production-mirror "any credit" convention. A human round
   under the wrong convention would record a spuriously failing (or passing) gate row.
   **Fix:** runbook ADDENDUM (2026-09-22) pins the marker convention: any credit = 1.
2. **Marking-quality signal (agent-vs-pipeline, 25/25).** Under the production's own
   convention, the pipeline's per-point award decisions matched the independent blind
   agent marker on EVERY paired point, and every partial-credit tally (3/4 isotope slip,
   1/3 method mark, 1/2 Mr-half, 1/2 flame-colour, 2/3 ratio, 3/4 cost-reasons) matched
   the marker's sub-item analysis. This is an engineering consistency result on a
   simulated-learner sample — it is NOT a κ release claim and carries no human validity.
3. **One `UNPARSEABLE_OUTPUT`** on the longest part (5-mark multi-sentence explain).
   Honest refusal, answer stayed PENDING-with-refusal-row, pair dropped from κ. Recorded
   per Step 2 ("do not retry into a different outcome"). No code change made; if future
   rounds show clustering on long parts, that is a candidate-generation follow-up.
4. **Small-sample honesty:** n=25 point decisions from 26 parts (bundled points), a
   simulated learner, an agent marker. Width applies to every number above.

## Remaining release gate (unchanged, now de-risked)

The production κ gate row (`POST /teacher/marking/kappa/evaluate`) must come from a
GENUINE HUMAN reference marking under ADR-027 D3 (pilot-staff authorization). Smallest
remaining action: **the operator/pilot teacher executes runbook Steps 0–3** (~30–60 min)
with the newly pinned marker convention (any credit = 1) on the session-96 sample (or a
regenerated sample), then Steps 4's closed-loop checks. The gate stays fail-closed until
that row exists and passes.

## Artifacts (this directory)

- `round_record.json` — attempts, cells, substitution + authoring-profile disclosures
- `blind_worksheet.json` — 26 rows: part prompts, learner answers, scheme points (no smart data), freeze stamp
- `agent_decisions.json` + `.sha256` — the frozen AGENT_MARKING decisions + rationales
- `smart_results.json` — production pipeline responses for all 7 attempts (breakdowns, scheme state, models, refusals)
- `release_state_per_part.json` — per-part `authoritative` flags (pre-gate false everywhere)
- `kappa_final.json` — both convention computations + per-point pairing detail
- `SHA256SUMS`

Companion (outside this repo): `download/g4-kappa-calibration/G4_KAPPA_CALIBRATION_RUNBOOK.md`
ADDENDUM 2026-09-22 (marker convention pinned); driver scripts under project `scripts/`
(`g4_execute.py`, `g4_author_answers.py`, `g4_freeze_decisions.py`, `g4_final_analysis.py`,
`g4_package_evidence.py` — tokens env-only, never committed).
