# ADR-033: BKT emission is format-aware — guess priced per question format; the calibration instrument ships

**Status:** Accepted. Implemented on `syllabai-core` @ `fae913f` on branch `fix/s2-format-aware-emission` (base: main @ `4ecbdc0`; 9 main files + 6 test files). Full unit suite **1119 tests, 0 failures, 0 errors, 2 skipped** (live-gated benchmark) on Temurin JDK 25.0.4.1 + Maven 3.9.16 — BUILD SUCCESS. Red/green: `scripts/s2_emission_red_green_sim.py`. Patch: `s2-fix-format-aware-emission.patch`.
**Date:** 2026-10-02
**Scope:** `syllabai-core` evidence contract (+2 event fields), learner BKT emission resolution, research calibration read surface. No schema migration, no BktEngine math changes, no slip/l0/learnRate changes, no read-surface response-shape changes. Resolves deep-audit finding **S2** (calibration) — **re-derived from source 2026-10-02**: the original audit report text was lost to an environment reset; the finding below is mechanical and re-verified against `main @ 4ecbdc0`.

## Context (the re-derived finding)

The deep audit of the learner model (2026-10-01) named S2 "calibration". Durable traces after the reset — ADR-031/032 ("a natural candidate for S2 recalibration"), `BktEngine.mastered()`'s own javadoc ("Master Spec leaves banding as a v0 heuristic **pending calibration**"), and Master Spec §BKT's explicit promise of "**monthly parameter recalibration**" (§5.5 charters the research layer with "calibration") — all point at the same debt. Re-derivation from source found two concrete halves:

1. **The emission model was format-blind.** Every marked attempt updated BKT with the same `guess=0.25, slip=0.1` — but 0.25 is exactly the **four-option MCQ** guess base; the paper parameter was silently a format constant. `AssessmentEvidenceRecordedEvent` carried only a boolean `correctness` while `Question.Type` distinguishes MCQ_SINGLE / SHORT_ANSWER / STRUCTURED. Consequences, live on the hub's Smart-Mark structured path:
   - A correct structured answer at l₀=0.1 read **0.357** mastery; the same performance with a structured-appropriate guess (0.01) reads **0.918** — a **2.57× under-credit**. Structured-heavy learners sat low-biased: review over-scheduling, NBA weak-mastery over-firing, teacher heatmaps reading low.
   - A wrong structured answer was **over-forgiven** (prior 0.5 → 0.206 instead of 0.183): a worked answer treated as if a quarter of non-knowers produce one.
   - 3- and 5-option MCQs were mispriced in opposite directions (1/N ≠ 0.25).
2. **The calibration loop had no instrument.** Nothing anywhere measured predicted-vs-observed — the mis-calibration was invisible *by construction*, although `BKT_UPDATED` telemetry has carried `priorMastery` (the pre-attempt forecast) next to `correctness` since V5.

The partial-credit rule in `EvidencePublisher.publishGraded` (full marks = correct, else wrong) was reviewed and is **documented, deliberate, and conservative** — unchanged here; relaxing it to graded evidence is a separate product decision.

## Accepted

1. **Guess is priced per format; slip, l₀ and T stay global.** The evidence event carries `questionType` + `optionCount` (both already in the publisher's hand — `question.options()` is materialized on the MCQ path). `LearnerModelService.effectiveParams` resolves: **MCQ_SINGLE → 1/optionCount** (the paper's 0.25 is exactly N=4), **SHORT_ANSWER → 0.05**, **STRUCTURED → 0.01** (new lenient properties). Null/blank/unknown format → paper default 0.25, so untyped or future evidence keeps exact prior behaviour — a strict refinement, never a behaviour change for untyped events. Slip stays global (mistakes happen in every format). `BktEngine` math is untouched; the resolution composes through `BktParams`.
2. **The calibration instrument ships with the fix.** `LearnerModelCalibrationService` aggregates the `BKT_UPDATED` stream into **Brier**, **ECE** and ten equal-width per-band records (count, mean predicted, observed accuracy, mean Brier, signed calibration error), read-only over telemetry; malformed rows are skipped honestly; optional `nodeId` filter. Exposed at `GET /api/v1/research/learner-model/calibration` behind **TEACHER/ADMIN** (new `/api/v1/research/**` SecurityConfig matcher — aggregates span all learners, never student-visible). Honesty caveat on the report: samples are *node-outcomes*, not independent learners (one marked attempt updates every node it honestly tests) — descriptive, not i.i.d. statistics.
3. **Retuning stays data-gated.** "Monthly parameter recalibration" now has its measurement; actually retuning slip/τ bands/τ_s from production data remains the S2 follow-up once post-deploy calibration data accumulates. The new knobs (`shortAnswerGuess`, `structuredGuess`) and every existing one are lenient-defaulted and overridable per environment.

## Rejected

- **Format-aware `slip`** (e.g. higher slip for timed structured papers): no research basis at Cycle-1 volume; one knob at a time.
- **Graded/partial-credit BKT updates** (using `marksAwarded/marksTotal` as a soft outcome): changes the evidence semantics the §12 contract documents ("conservative, BKT-safe"); a product decision, not a calibration fix.
- **P(correct) read mapping** (surfaces displaying `P·(1−slip) + (1−P)·guess` instead of P(known)): would change every read contract at once — the S3-1 "one semantics everywhere" rule argues for exactly one such decision, made deliberately, not smuggled into a calibration fix.
- **Backfilling historical mastery** by replaying attempts under the new emission: the evidence stream is replayable in principle but the write-back-era S1 corruption makes reconstructed anchors unreliable (same conclusion as ADR-031's deferred backfill); next-attempt self-healing is accepted.

## Consequences / migration notes

- **No schema migration.** The event is in-JVM; telemetry payload is jsonb (new fields are optional and untyped consumers ignore them); properties are lenient-defaulted.
- **Behaviour shift is immediate and upward for structured-active learners** (the under-credit is removed): mastery jumps at the learner's *next* attempt; band assignment (τ selection) and review scheduling follow at the same moment. Analytics comparing raw historical mastery should segment at the deploy date.
- **MCQ pricing changes for N ≠ 4** (3-option items read slightly lower, 5-option slightly higher on a correct answer); 4-option MCQs are bit-identical to the old path (1/4 = 0.25).
- **The calibration report becomes the gate for all future parameter retunes** (τ bands, τ_s, slip): no constant moves without a before/after Brier/ECE comparison.

## Evidence

- Red/green: `scripts/s2_emission_red_green_sim.py` — structured learner trajectories (0.357 vs 0.918 after one correct answer; review-threshold crossing 2 vs 1 attempts; mastered-band crossing 3 vs 1), over-forgiveness (0.206 vs 0.183 from prior 0.5), MCQ option-count equity (3/4/5-option rows), and the invisibility argument.
- Emission pins (`LearnerModelServiceTest`): structured-correct → 0.918182; 5-option MCQ → 0.4 exactly; 4-option MCQ ≡ paper-default path (0.3832); wrong-structured → 0.182569; untyped legacy events keep the paper default.
- Publisher pins (`EvidencePublisherTest`): structured event carries `("STRUCTURED", 0)`; a 3-option MCQ event carries `("MCQ_SINGLE", 3)` — the live count, not a hardcoded four-option assumption.
- Calibration pins (`LearnerModelCalibrationServiceTest`): hand-computed fixture — Brier 0.3616002, ECE 0.3798, per-band records (bin [0.9,1.0] mean predicted 0.9745 vs observed 0.5 → calibration error −0.4745), nodeId filter, malformed-row skip, honest empty report.
- Executed for real on JDK 25: full unit suite **1119 / 0 / 0 / 2 skipped — BUILD SUCCESS** (branch `fix/s2-format-aware-emission`, commit `fae913f`). IT suite runs in CI (PR gate) as with ADR-031/032.
