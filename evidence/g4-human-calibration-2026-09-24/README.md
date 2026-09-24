# G-4 HUMAN CALIBRATION ROUND — EXECUTED 2026-09-24 (session 118)

The genuine human κ reference round prescribed by
`HUMAN_CALIBRATION_EXECUTION_PACKAGE_2026-09-22.md` was executed end-to-end.
The marker was the operator / pilot teacher (`pilot.teacher@syllabai-test.dev`),
marking **BLIND** from `HUMAN_MARKING_PACKET_2026-09-23.md` (scheme text +
learner answer only; no Smart Mark breakdown was ever surfaced pre-decision).
The agent's role was strictly mechanical: verification, transcription
(typing-only), API calls, and record-keeping. Every judgment in the human side
below is the operator's.

## Verdict

- **Gate row (ALL scope): κ = 1.0, observedAgreement = 1.0, n = 113, threshold 0.60, passed = TRUE** —
  persisted 2026-09-24T11:58:56Z, row id `490d9dce-eb03-4a75-97b1-998c19536fd7`
  (`kappa_row_20260924.json`; `kappa/latest` readback identical). Supersedes the
  unvouchable pre-existing passed row by newest-`computedAt` (the recorded
  keep-and-document decision from session 117).
- **Sample-only slice (the 26 operator blind pairs): 26/26 agree, κ = 1.0**
  (production-mirror any-credit convention; smart_yes = human_yes = 24) —
  `sample_only_agreement_20260924.json`.
- **Honesty note on n=113:** the ALL-scope row includes 87 pre-existing pairs
  whose provenance cannot be vouched (superseded-by-inclusion, not erased).
  The sample-only artifact is preserved for any future scoped-gate decision.
- **Step 4 closed loop: PASS.** Fresh structured attempt by the probe STUDENT
  learner on `sme-eq-1-3-atomic-structure-q0` → student smart-mark returned
  `authoritative=true` on all 5 parts, reflecting the new gate row
  (`step4_student_probe_20260924.json`, attempt `5b3e6896-…`).

## Execution record

| Step | Result |
|---|---|
| 0.3 κ-row preflight | Resolved session 117 (keep-and-document); superseded by this round's row |
| 0.4 sample | Path B verified live: 26 SMART_MARKED answers across the frozen round's 7 attempts; (attemptId, partLabel, partMarks) triple set matches `blind_worksheet.json` exactly (`path_b_answer_ids.json`) |
| 0.5 worksheet | `g4_worksheet.py dump-record` (new harness mode: frozen record × live answerIds; the deployed AnswerMarkingView carries no markPoints) |
| 1 human marks | Operator's 26 decision lines transcribed verbatim (`operator_decisions_raw_2026-09-23.txt`), validated (all refs covered, marks in bounds), submitted: **26 human marks recorded, 0 skipped**. One 401 on the first attempt (expired day-old token; zero writes, retried after re-login) |
| 2 smart batch | 26/26 `SKIPPED_ALREADY_MARKED` (idempotent, expected; `smart_mark_batch_response.json`) |
| 3 κ gate | Row above (HTTP 201) |
| 4 closed loop | Student-surface probe PASS (see above) |

## Files

- `HUMAN_MARKING_PACKET_2026-09-23.md` — the blind packet the operator marked from
- `operator_decisions_raw_2026-09-23.txt` — the operator's reply, verbatim, unedited
- `g4_worksheet_20260923.csv` (+ `.pre_fill_backup`) — filled worksheet / untouched copy
- `path_b_answer_ids.json` — live answerId resolution for the frozen sample
- `batch_req.json`, `smart_mark_batch_response.json` — Step 2 (outcome rows only, no breakdowns)
- `kappa_row_20260924.json`, `kappa_latest_readback.json` — Step 3 gate row + readback
- `sample_only_agreement_20260924.json` — the 26-pair offline computation
- `step4_student_probe_20260924.json` — Step 4 probe verdict

## Defects found during execution (for the core lane)

- `GET /api/v1/teacher/marking/queue-v2?state=SMART_MARKED` returns **HTTP 500
  internal_error** in production (controller accepts the value; the v1
  `GET /teacher/marking/answers?state=SMART_MARKED` works and was used instead).
  Not fixed here — logged for a focused core change with its own regression test.

## Provenance

- Marker: operator / pilot teacher (human, blind). Agent: mechanical executor only.
- No threshold change, no fail-closed bypass, no AI-generated judgment recorded
  as human evidence at any point.
- Local artifact snapshot: `download/g4-kappa-calibration/` (same files, plus the
  patched `g4_worksheet.py` with the `dump-record` mode).
