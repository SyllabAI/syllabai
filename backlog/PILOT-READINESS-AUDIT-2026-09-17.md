# Pilot Readiness Audit — the learner journey, transition by transition (2026-09-17, Session 80)

**Mandate:** the operator's Pilot Readiness Hardening directive — no new
product functionality; audit the complete learner journey for scientific
and operational readiness. For each transition: authoritative source,
provenance, validation gate, failure behavior, learner-visible behavior,
observability, determinism, and whether a bad/partial input can corrupt
downstream state. The standing concern is explicit: **the dangerous
failures are not obvious UI failures** — the system can look healthy while
producing subtly wrong learner-state evidence (the multi-part marking
defect class, session-72).

**Method:** fresh code-level review this session of every owning service
at the current lineages (core `efea4e5` = deployed `02643ed` + docs;
web `022d9ba`), composed with the standing verification records (named
regression tests, ITs, the S75 reconciliation, the frozen r3 protocol, the
t0 instrument's local execution validation, and today's live monitor run
`35080761751`: 15/15 green). No production writes were made by this audit
(read-only probes and code review only).

**Lineage audited:** core `02643ed` (540 unit green / 18-IT suite committed),
web main, parser `8142574`, resources `020cc92`, ops `04d7d68`.

---

## T1 — Curriculum (subjects → the learner's surface)

- **Authoritative source:** `curriculum` package (`CurriculumController`,
  `Subject`, `CurriculumVersion`) over the Flyway-seeded schema (V2, V6);
  subjects and their KG roots are DB rows, not config.
- **Provenance:** subject ids + `knowledgeNodeId` root links; the probe
  verifies 4 subjects / 2 with KG root live.
- **Validation gate:** `CurriculumIngestionIT`; curriculum versions are
  ingested through the review workflow, never hand-edited.
- **Failure behavior:** missing subject → 404; no fallback curriculum.
- **Learner-visible:** the subjects list on login; honest-empty subjects
  (4CH1 pre-activation) render as empty, never fake content.
- **Observability:** probe's `learner` check (subjects count + rooted
  count) every 6 h.
- **Determinism:** static seeded data; deterministic.
- **Partial/bad input:** not learner-writable; the risk is content-side
  (handled at T2/T3 gates). **Verdict: GREEN.**

## T2 — SpecificationPoint → knowledge nodes (the KG)

- **Authoritative source:** `knowledge/KnowledgeGraphService` over
  `knowledge_nodes` (V16+), seeded from `concept-graph/*.yaml` through
  teacher activation — the ONLY path that promotes edges to
  HUMAN_VALIDATED.
- **Provenance:** node ids, codes (`4CH1-S2-f`…), validation states; 153
  HUMAN_VALIDATED edges with per-batch operator verdict records
  (T-C11 batches 1–4, SHA256SUMS-pinned).
- **Validation gate:** activation is idempotent and re-verified (0 nodes /
  0 edges on repeat — proven live repeatedly); `ConceptGraphSeedFlowIT`,
  `ConceptGraphRemediationFlowIT`.
- **Failure behavior:** unactivated subject → no rooted KG → honest-empty
  learner surface (fail-closed, no synthetic graph).
- **Learner-visible:** topic tree, concept graph views.
- **Observability:** probe's teacher concept-graph check (153 edges) once
  teacher creds are set; T0.2 population census at capture.
- **Determinism:** yaml → DB seeding is deterministic (regeneration
  byte-identical, proven in T-C11 gates).
- **Partial/bad input:** quarantine/SUGGESTED content cannot enter the KG
  serving path without the human validation gate (T-C04 discipline; 758
  SUGGESTED question versions serve zero — proven by real API test).
  **Verdict: GREEN.**

## T3 — Validated question (serving boundary)

- **Authoritative source:** `ServableQuestionSpec` — ONE rule, reused by
  every serving surface: active AND (non-structured OR current version
  VALIDATED) AND paper not REJECTED/FLAGGED.
- **Provenance:** `questions`/`question_versions` with validation states,
  paper lineage; servable inventory replicated in SQL by t0 T0.10 with the
  SAME rule (cross-verified).
- **Validation gate:** the write path enforces it too
  (`AssessmentService.submit/submitStructured` — an unvalidated question
  is not even attemptable; fail-closed 404, no state echo). The V20 paper
  gate (`assertPaperAllowsServing`) blocks REJECTED/FLAGGED papers at both
  read and write.
- **Failure behavior:** 404 (indistinguishable from nonexistent — no
  content leak); unknown root → 404 (f7adea7); missing param → 400
  (5991187). All probe-verified live.
- **Learner-visible:** practice lists per subject; cross-subject
  contamination check runs every 6 h (4CH1 vs others, overlap 0).
- **Observability:** probe checks `learner-practice` + `contamination`.
- **Determinism:** list order stable (difficulty-ordered surfaces).
- **Partial/bad input:** a version that is current-but-unvalidated cannot
  serve; paper-level rejection overrides per-question state. The known
  fail-open caveat (path filters) is a CI-cost concern, not a serving
  concern. **Verdict: GREEN.**

## T4 — Attempt (submission)

- **Authoritative source:** `AssessmentService` — the only writer of
  attempts/answers.
- **Provenance:** per-attempt `provenance` strings (`web-quiz-v0`,
  `web-structured-v1[-timed]`) — the field t0 T0.5 aggregates by; response
  time / confidence / self-doubt / timed condition recorded.
- **Validation gate:** `submitStructured` is all-parts-or-nothing:
  duplicate part answers AND missing part answers are rejected (400) BEFORE
  any write; part set comes from the current version only.
- **Failure behavior:** unvalidated/serving-blocked → 404 pre-write; bad
  part set → 400 with zero rows written (transactional).
- **Learner-visible:** attempt id + per-part PENDING states returned; the
  UI shows "awaiting marking".
- **Observability:** attempts/answers rows are the evidence substrate;
  t0 T0.5 counts by marking_state × evidence_emitted.
- **Determinism:** submission itself deterministic; LLM never in this path.
- **Partial/bad input:** **the corruption class that bit us before is
  structurally closed here** — a partial submission is refused atomically;
  the multi-part defect was downstream (T5/T6), not here.
  **Verdict: GREEN.**

## T5 — Mark (human authority)

- **Authoritative source:** `TeacherMarkingService.recordHumanMark` —
  human marks are THE authoritative grade; Smart Mark is advisory until
  κ ≥ 0.60 (gate: `KappaAgreementService`, persisted evaluations).
- **Provenance:** `HumanMark` rows (marker id, per-point decisions for κ
  pairing, comments); `HumanMarkRecordedEvent` with revising flag.
- **Validation gate:** marks outside the part bound (0..part marks) →
  409 Conflict (server-enforced, not manifest-trusted); the marking queue
  (`TeacherMarkingQueueService`) drives the mark→next chain
  (`MarkingQueueFlowIT`).
- **Failure behavior:** out-of-bound refused; unknown answer 404; override
  semantics explicit (`revising` = evidence already fired).
- **Learner-visible:** settled totals + per-part marks in history; the
  `correct:null` honesty for PENDING (fixed `cff5d2f`, regression-pinned).
- **Observability:** `log.info` per mark; κ evaluations persisted with
  threshold + sample size.
- **Determinism:** marking itself deterministic; κ computed from paired
  decisions (deterministic given the pairs).
- **Partial/bad input:** a mark for one part while others PENDING is
  ALLOWED (the queue is part-by-part) — and this is exactly where the
  defect used to live. Now: evidence waits for the COMPLETING mark
  (`noneMatch PENDING` guard); totals recompute from all answers each
  time. Verified by `MultipartMarkingFlowIT` + the named regression set +
  live r2 round (17/17) + S75 reconciliation. **Verdict: GREEN** (the
  strongest-verified transition in the chain).

## T6 — Learning evidence (the event contract)

- **Authoritative source:** `EvidencePublisher` — the single emission
  point (Master Spec §12).
- **Provenance:** event carries attempt id, question id, topicNodeIds
  (primary ∪ secondary — `topicNodeIds()` static, replicated exactly by
  t0 T0.7), correctness, marks total/awarded, conditions, misconceptions
  expressed/observed, provenance, `occurredAt`.
- **Validation gate:** once-only guard (`markEvidenceEmitted`) — MCQ
  fires at submit (else IllegalStateException), structured fires at first
  authoritative completing mark; overrides NEVER re-fire (BKT/BDT safe).
- **Failure behavior:** fail-closed: evidence not emitted until the
  attempt is fully settled; a missing emission is caught by T0.7's
  settled-without-evidence invariant (empty required).
- **Learner-visible:** indirectly — this is the causal input to state.
- **Observability:** ATTEMPT_SUBMITTED + BKT_UPDATED (+ BDT_UPDATED)
  telemetry with FULL payload (prior/posterior included — the
  reconciliation substrate).
- **Determinism:** pure function of the settled attempt + question
  mapping; `Instant.now()` timestamps only.
- **Partial/bad input:** the historical defect (partial-total emission
  with `correct=false`) is fixed (`fe01b87`) + regression-tested +
  reconciled (S75) + re-verified by the frozen r3 protocol's A1/A2.
  **Verdict: GREEN.**

## T7 — Learner state (BKT/BDT projection)

- **Authoritative source:** `LearnerModelService` — the ONLY writer of
  `skill_states`/`misconception_states` (plus `NightlyDecayJob` for
  decay), reacting to evidence events (`@Order(10)` — before diagnosis).
- **Provenance:** every write leaves BKT_UPDATED/BDT_UPDATED/DECAY_APPLIED
  telemetry with prior→posterior; `version` column (optimistic lock)
  increments.
- **Validation gate:** the T0.7 whole-projection audit (at every t0
  capture): stored counters == evidence-derived counters per
  learner×topic, replicating `topicNodeIds()` exactly. Negative-control
  proven (injected contamination detected).
- **Failure behavior:** concurrent evidence-vs-decay → optimistic-lock
  409 → decay batch self-heals next night (never applied twice);
  evidence wins.
- **Learner-visible:** mastery map, history-derived status.
- **Observability:** telemetry per transition; t0 T0.4 full matrix.
- **Determinism:** BKT engine is a pure function (Corbett & Anderson;
  params l0=0.1, slip=0.1, guess=0.25, T=0.1 — production values, frozen
  into the r3 protocol P.4).
- **Partial/bad input:** unknown topic node in an event → row created with
  l0 prior (honest cold start); decay NEVER touches counters
  (code-verified: `applyDecay` writes mastery only) — the audit's basis is
  decay-safe by construction. **Verdict: GREEN.**

## T8 — Weakness (class read model)

- **Authoritative source:** `ClassAnalyticsService` (policy
  `class-analytics/v1`) — read-only over stored state.
- **Provenance:** per-topic aggregates with learners_measured; UNMEASURED
  is honest `null` — nothing fabricated (probe checks this live).
- **Validation gate:** `ClassAnalyticsFlowIT`; t0 T0.3 replicates the read
  model in SQL (mean of STORED mastery, bands 0.45/0.8, weak = mean <
  0.45) and cross-checks.
- **Failure behavior:** no measured learners → nulls + UNMEASURED bands;
  no synthetic scores anywhere (weakness-targeting probe asserts
  known-reasons only).
- **Learner-visible:** teacher class view; feeds Smart Lesson/test
  builder inputs.
- **Observability:** probe's class-analytics honesty check every 6 h.
- **Determinism:** deterministic ordering (measured first, weakest mean
  first, then name).
- **Partial/bad input:** read-only — cannot corrupt; worst case is a
  stale read (bounded by transactional consistency).
  **Verdict: GREEN.**

## T9 — Smart Lesson (the explainable action)

- **Authoritative source:** `SmartLessonService` v2 (policy
  `smart-lesson/v2`) — deterministic ladder: prerequisite gate → active
  misconception (with validated remediation if REMEDIATED_BY edge exists)
  → review due → mastery-based practice → tutor-engaged →
  INSUFFICIENT_COVERAGE.
- **Provenance:** every action carries reasonCode + targetNodeId + an
  evidence trace (facts with measured values and attempt counts).
- **Validation gate:** `SmartLessonFlowIT` + the S-H 33/33 evaluation +
  in-browser verification (session-77 CLA lane) + probe check (policy,
  action shape, evidence non-empty).
- **Failure behavior:** unknown/foreign topic → 404; no measured state →
  honest cold-start INSUFFICIENT_COVERAGE (the monitor's own expected
  state — used as the r3 A6 baseline).
- **Learner-visible:** the lesson card with its reason and evidence.
- **Observability:** probe `smart-lesson` check; t0 T0.9 inputs +
  decay-replication labeled as replication.
- **Determinism:** every sort key is total (probability, freshness, code;
  mean, code) — no ambient-order dependence.
- **Partial/bad input:** missing skill state → treated as unmeasured, not
  as zero; decay-adjusted value computed from stored raw (never
  fabricated). **Verdict: GREEN.**

## T10 — Targeted test (and the intervention lane)

- **Authoritative source:** `TestBuilderService`
  (`test-builder-weakness/v1`) — reuses `ServableQuestionService`, so a
  generated test can NEVER contain unvalidated content; hard caps (50
  questions / 200 marks), difficulty-ordered, marks-targeted greedy
  (deterministic).
- **Provenance:** weakness options carry policy id + explicit known
  reasons only; the class-weakness path is read-only.
- **Validation gate:** `WeaknessTargetingFlowIT`; the E2 intervention
  lane (session-78): `InterventionRunFlowIT` + live 10/10 on production
  (auth gate, deterministic cold-start, lifecycle, ownership, terminal
  freeze).
- **Failure behavior:** no practice action / unknown root → 404
  fail-closed; foreign run → indistinguishable 404; state conflicts →
  named 409s.
- **Learner-visible:** printable test; intervention runs with honest
  evidence-by-reference.
- **Observability:** intervention_run records (t0 T0.10); zero skill-row
  writes across the lifecycle (live-proven).
- **Determinism:** assembly order deterministic; intervention hash stable.
- **Partial/bad input:** late evidence attachment after terminal state →
  fails closed (409). **Verdict: GREEN.**

## T11 — New evidence (the re-attempt loop)

- Same authoritative path as T4 (the loop is the design: targeted
  remediation re-attempts the weak topic's servable questions).
- The r2 round executed this live (3 questions, 17 part-marks, honest
  review of probe placeholders); r3's frozen protocol re-verifies it with
  pre-registered assertions. Deterministic question selection (weakest
  targetable topic rule — the workflow's existing order, not a new one).
- **Verdict: GREEN — r3 CONFIRMED LIVE 2026-09-17** (round PASS per the frozen
  P.5 rules: `evidence/cycle-001-r3/`; the deterministic selection held
  (4CH1-S2-f, the r2 trio re-attempted), 17/17 marks applied zero conflicts,
  A1–A9/I1–I6 all hold).

## T12 — Updated learner state (the closed loop)

- The loop's closing edge: new evidence → projection → audit. Verified
  end-to-end by: the S75 whole-projection audit (1 contaminated row found
  and repaired at bit-exact precision — proving the audit WORKS on real
  data), the t0 instrument's standing T0.7 gate, and the r3 protocol's
  A3–A7 assertions.
- **The four independent tripwires against "healthy-looking but silently
  wrong" state** (the operator's stated concern):
  1. T0.7 projection audit at every capture (counters vs evidence).
  2. Event-level telemetry with prior→posterior per update (mismatch
     visible without re-derivation).
  3. The 6-hourly probe's scoping/contamination/honesty checks.
  4. The frozen r3 assertions (formula-anchored, not outcome-anchored).
  A corruption must defeat all four to pass unnoticed — each observes a
  different surface (stored counters, event stream, live API shape,
  formula reconstruction).
- **Verdict: GREEN.**

---

## Findings

1. **(Protocol refinement — RESOLVED in the r3 freeze)** production's
   nightly decay job WRITES stored mastery (48 h idle grace). A naive
   "mastery == BKT(S75 value, r3 sequence)" assertion would false-FAIL
   after any decay run. Resolution: r3 protocol P.2-A4 pre-registers the
   decay-aware prior rule (prior = S0-captured value; DECAY_APPLIED
   telemetry counted in reconstruction); T0.7's counter basis verified
   decay-safe in code (`applyDecay` writes mastery only). No product
   change required — the system is correct; the measurement protocol now
   matches it.
2. **(Observation, no action)** `updateFluencyGaps` runs one aggregate
   query per topic node per evidence event — bounded (1–3 nodes/question),
   a free-tier latency note only, not a correctness risk.
3. **(Known-open, non-blocking, by design)** κ gate has zero paired
   samples until real mixed-award marking accumulates (T-C04); Smart Mark
   stays advisory; human marks authoritative.
4. **(Known-open, non-blocking)** `PILOT_TEACHER_*` monitor secrets unset
   (optional; teacher checks advisory-skip; recovery path documented in
   the ops README).
5. **(Known-open, non-blocking, pre-existing)** core `DEPLOYMENT.md` §4
   monitor-account references predate the migration + re-provisioning
   (stale docs, standalone follow-up; not learner-facing).
6. **(Live-state anchor)** today's dispatched monitor run `35080761751`
   (2026-09-16T09:40Z): 15/15 green — the journey's live surfaces are
   healthy at the audited lineage.

## Journey verdict

**12/12 transitions GREEN at the audited lineages; zero blockers found;
zero product changes required by this audit.** The multi-part corruption
class that motivated the audit is closed at four layers (atomic submission
refusal, completing-mark evidence guard, counter-based projection audit,
formula-anchored r3 assertions). The pilot's remaining gates are the
external ones: CI restoration (sentinel window 2026-09-27). The live r3
round PASSED 2026-09-17 (A1–A9/I1–I6 all hold, verdict record
`evidence/cycle-001-r3/verdict.json`) and the Phase-4 t0 capture is CLEAN
with expected-diff PASS (`evidence/cycle-001-r3/t0-phase4-*.json`) — the
fix chain is app-level PRODUCTION VERIFIED, closing the audit's last open
product gate.
