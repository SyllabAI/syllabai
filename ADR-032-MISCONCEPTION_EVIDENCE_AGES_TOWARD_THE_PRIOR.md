# ADR-032: Misconception evidence ages toward the base rate — BDT posteriors are anchors, relaxation is computed at read

**Status:** Accepted. Implemented on `syllabai-core` @ `fb8600f` on branch `fix/med2-misconception-staleness` (15 main files + 10 test files, +537/−136); full unit suite **1110 tests, 0 failures, 0 errors, 2 skipped** (live-gated benchmark) on Temurin JDK 25.0.4.1 + Maven 3.9.16 — BUILD SUCCESS. Patch exported as `med2-fix-misconception-staleness.patch` (base: main @ `69365ff`). Opened as **PR #43**; branch head `7b97726` moves three IT assertions to read-computation tolerance and adds an IT-level staleness leg — CI `core-ci` **green** (run 36914443516) including the failsafe IT suite (162 ITs, testcontainers pgvector).
**Date:** 2026-10-02
**Scope:** `syllabai-core` learner BDT read semantics and all misconception read surfaces (NBA, Tutor policy/context, Smart Lesson, learner + class knowledge graphs, learner state API, CLA tool brief, teacher analytics). No schema migration, no BKT/BDT update math changes, no evidence-emission contract changes, no nightly job. Resolves deep-audit finding **MED-2** (misconceptions never decay) and applies the S3-1 "one semantics everywhere" rule to misconception banding.

## Context

The deep audit (2026-10-01) flagged MED-2: a BDT posterior is written once per evidence event and then frozen forever. `MisconceptionState.probability` documented itself as "current P(misconception held)" but behaved as "P(held) at the moment of the last evidence". Consequences observable in the product:

- A learner who expressed a misconception eight months ago (P_e = 0.9) still fires NBA `MISCONCEPTION_SUSPECTED`/`STUDY_CORRECTIVE` actions, tutor `MISCONCEPTION_REMEDIATION` plans and teacher-class "active signal" counters at full strength — as if the diagnosis were fresh.
- Ordering is stale-biased: surfaces sort by raw probability, so the stale 0.9 outranks a fresher 0.6.
- Conversely a refuted misconception (P_e = 0.05) stays 0.05 forever; nothing in the model allows relapse, which the learning-sciences literature considers real.

Master Spec §11 specifies forgetting decay for **BKT mastery only** (30/90/365-day τ bands); the BDT section says only that probabilities are "driven by diagnostic evidence". The time semantics of BDT state were therefore an open design decision, not a spec violation to revert to.

The audit's S1 finding (ADR-031) already established the architectural law this decision must obey: **learner-model time effects are computed at read from stable anchors and never persisted** — persisted relaxation reintroduces write-back compounding, anchor staleness and optimistic-lock churn.

## Accepted

1. **Evidence ages; beliefs do not evaporate.** The stored `probability` is redefined (javadoc-pinned) as the **evidence-anchored posterior P_e** at `lastEvidenceAt` — an anchor pair `(P_e, lastEvidenceAt)`, exactly analogous to mastery's `(P₀, lastPracticedAt)`. It is never rewritten by reads.
2. **Relaxation toward the population prior, not toward zero.** Readers compute
   `effective = prior + (P_e − prior) · e^(−age/τ_s)` with `age = now − lastEvidenceAt` (clamped at zero) and `τ_s = LearnerProperties.Bdt.stalenessTauDays`, default **180 days**. Decaying toward zero was rejected on semantics (see Rejected): what goes stale is the *diagnostic evidence*, so the belief about the *current* learner relaxes to the base rate. The relaxation is **symmetric**: stale confirmations lose prescribing force, stale refutations drift back up (relapse is modelled); the next related attempt re-runs the BDT update and re-anchors the row.
3. **τ_s = 180 days default.** A stale diagnosis keeps prescribing force for roughly a term (0.808 @ 30d, 0.664 @ 90d, 0.521 @ 180d — just above the 0.5 threshold) and re-qualifies as "needs evidence" after about a year (0.379 @ 365d). Gentler than the fastest mastery band (30d) because beliefs outlive facts; configurable, and a natural candidate for S2 recalibration.
4. **Computed at read, never persisted; no nightly job.** Same architecture as ADR-031. With the anchor stable, the exponential semigroup acts on the *deviation from prior* (`(effective₁ − prior) = dev·e^(−t₁/τ_s)`), so any number of recompositions equal the exact single-relaxation curve. There is deliberately no `APPLY_FORGETTING_DECAY`-style job for misconceptions, no new telemetry event, no schema change.
5. **One semantics everywhere (the S3-1 lesson).** Every gate, ranking and display surface consumes the relaxed value: `BdtEngine.relaxedToPrior(...)` is the single formula; `LearnerModelService.misconceptionReadings(learnerId)` returns `MisconceptionReading(state, effective)` **sorted by effective descending**; the two teacher-side services that aggregate repository rows directly (`ClassAnalyticsService`, `ClassKnowledgeGraphService`) call the same engine function per row. `LearnerStateController`'s JSON shape is unchanged — `probability` now carries the relaxed value, `lastEvidenceAt` lets clients show evidence age.
6. **`evidenceCount` stays raw.** It counts collected evidence and is displayed as-is ("from N evidence item(s)").

## Rejected

- **Time-decay toward zero** (mirroring mastery forgetting on the value itself): semantically backwards. An unaddressed misconception does not fade on a clock; decay-to-zero would *auto-resolve* unaddressed diagnoses and silently stop remediation without any corrective evidence — the opposite of what the product owes the learner.
- **Nightly persisted relaxation** (a misconception pass in `NightlyDecayJob` writing relaxed values back): reintroduces the entire S1 bug class — compounding through repeated write-back, anchor staleness, band/threshold feedback, optimistic-lock churn — for zero additional correctness, since the read-side computation is exact.
- **Binary recency gate at consumers** ("active only if evidence younger than X days"): a cliff instead of a graded relaxation; policy scattered across nine files; ordering would still be stale-biased because ranking keys would remain raw probabilities; and it hides the continuous confidence story from display surfaces.
- **Per-misconception τ_s**: uncalibratable at Cycle-1 data volume; one global τ_s keeps the knob count at one until S2 says otherwise.

## Consequences / migration notes

- **No schema migration; no data backfill.** Existing rows are already correct anchors `(P_e, lastEvidenceAt)`; only their interpretation changes.
- **Product behaviour shift:** stale diagnoses gradually stop firing remediation (NBA legs, tutor plans, Smart Lesson, teacher "active signal" counters, CLA brief). Surfaces may show *fewer* active misconceptions than before — this is the fix, not a regression. Learners with genuinely active misconceptions are unaffected while evidence is fresh.
- **API note:** `GET /learner/state` and the knowledge-graph views keep their field names; `probability`/`misconceptionProbability` values may now be *lower* than previously returned for stale rows (and *higher* for stale refutations drifting toward the prior). Clients that persisted or compare raw historical values should segment analytics at the deploy date, as with ADR-031's P₀ discontinuity.
- **Telemetry:** `MisconceptionUpdatedEvent` is untouched (evidence-path semantics); no discontinuity there. Any analytics that tracked "active misconception count" over time will show a step change at deploy.
- **Threshold duplication remains** (TutorPolicyService/LearnerContextAssembler constants vs `activeThreshold` property vs the CLA brief's literal 0.5) — unchanged by this ADR and left as a small follow-up; all of them now gate on the relaxed value, so semantics are consistent even where the knob is duplicated.

## Evidence

- Red/green: `scripts/med2_staleness_red_green_sim.py` — the same scenario under both semantics (RED: raw 0.9 gates REMEDIATION at every age and outranks fresh 0.6; GREEN: 0.808 @ 30d, 0.664 @ 90d, 0.521 @ 180d, 0.379 @ 365d — re-qualifies at ~a year; ordering pin flips to fresh-first with stale at 0.4975 @ 200d).
- Engine pins (`BdtEngineTest`): fresh identity, future-dated (clock-skew) clamp, ancient → prior, exact `e^−1` deviation scaling at `age = τ_s`, semigroup on the deviation (two relaxations ≡ one), symmetric refutation drift, τ validation.
- Funnel pins (`MisconceptionStalenessTest`): repository returns raw-ordered rows `[stale 0.9, fresh 0.6]`; readings come back effective-ordered `[fresh 0.6, stale 0.4975]`; stale below the 0.5 threshold; `save`/`saveAll` never invoked on the read path.
- Consumer pins (`TutorPolicyServiceTest` + migrated suites): a year-old 0.9 no longer triggers `MISCONCEPTION_REMEDIATION` (EXPLANATION instead) while fresh active evidence still does; all nine consumer suites green under the readings contract.
- CI (run 36914443516, JDK 25): full `core-ci` green — unit suite plus 162 failsafe ITs on testcontainers pgvector. The first CI run (36912867703 @ `fb8600f`) failed 2 ITs that pinned exact double equality (0.75) on the now read-computed value (observed ε 2.2e-8 / 1.9e-9 from the seed→read wall-clock gap — a flake by construction under computed-at-read); commit `7b97726` replaces them with `isCloseTo(0.75, within 1e-4)` and pins the staleness leg end-to-end: backdating ONLY `last_evidence_at` relaxes the read to ≈0.448 < 0.5, flips `misconceptionActive` false and drops the T-033 `MISCONCEPTION_SUSPECTED` action — no write anywhere on the read path.
- Executed for real on JDK 25: full unit suite **1110 / 0 / 0 / 2 skipped — BUILD SUCCESS** (branch `fix/med2-misconception-staleness`, commit `fb8600f`).
