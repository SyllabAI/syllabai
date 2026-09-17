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

---

## Phase-5 — five-gate pilot-readiness review (T-032, executed 2026-09-17, session 92)

Mandate: the operator's Phase-5 directive — a fresh reconciliation gate
against CURRENT GitHub state and machine evidence, not a restatement of
prior records. GitHub is canonical; every claim below points at the
artifact that establishes it. No r3 artifact was mutated; no experiment
re-run; production touched read-only.

**Canonical heads at review time (fetched 2026-09-17 ~08:50Z):**
core `8eed5e6f3fd3ce749147ef6568c9cf3a2b897d68`, web
`012f88cb692682c971e4dffa979274f4371f52c1`, parser
`8d2e4dbc5d593cb7345435cad8247afd8489fdb5`, tracker
`a7bc9616685e2e392c24266fe5665bb1daf1fdc8` (post-session-91 errata).

### Gate 1 — CI: PASS

All three rails verified at their CURRENT heads; in every case the
successful run's `head_sha` equals the current `origin/main` and ZERO
newer runs exist (the run tested the head, not a predecessor):

| rail | head | run | conclusion | artifact/step truth |
|---|---|---|---|---|
| core | `8eed5e6` | `35162299609` (rn 217, push, 2026-09-16T23:26:30Z) | success | test-reports artifact parsed: **surefire 646 tests / 0 fail / 0 err / 1 skip** (91 classes) + **failsafe 81 tests / 0 fail / 0 err / 0 skip** (23 IT classes); the 1 skip = `DatabaseIsolationGuardTest` env-guard (documented no-test-DB skip) |
| web | `012f88c` | `35161624427` (rn 91, push, 23:17:15Z) | success | build job, 11 steps all success incl. Lint + Production build (type-checked, standalone copy exercised) |
| parser | `8d2e4db` | `35159090681` (rn 54, push, 22:44:03Z) | success | 3 jobs all success — build (`mvn -B verify`), conformance harness (16/16 sealed suite), content-package-proof (real-corpus reconstruction) — 26 steps, 0 failed |

Pilot-named ITs green in the core artifact: EvidenceStateConcurrencyIT
4/4, MultipartMarkingFlowIT 2/2, RevisionNoteFlowIT 2/2, SmartLessonFlowIT
5/5, NextBestActionFlowIT 1/1, ClassAnalyticsFlowIT 2/2,
WeaknessTargetingFlowIT 2/2, MarkingQueueFlowIT 3/3, InterventionRunFlowIT
2/2, ConceptGraphSeedFlowIT 2/2, LexicalBoundaryIT 2/2,
ChunkLexicalSearchIT 3/3. (Counts grew from the session-85 baseline
581+74 because the concurrent T-C07/T-C14/T-C19 lanes added tests; the
runbook's spot-check set is fully covered.)

**Moving-target re-verification (concurrent lanes pushed during the
record push, 2026-09-17 ~09:2xZ):** core advanced `8eed5e6` → `b0be54da`
(PR #20 — embedding backfill runner + hermetic replay IT; **ZERO src/main
delta**, test-side only, runtime-identical) and parser advanced
`8d2e4db` → `7b8bcbab` (corpus-ops tooling only, T-C16 owner-gated lane);
web unchanged. Both new heads re-verified GREEN at exactly those SHAs —
core run `35204682298` (rn 220; artifact truth re-parsed: surefire
646/0/0/1 + failsafe 84/0/0/0 across 24 IT classes, incl.
EmbedBackfillReplayIT 3/3; all pilot-named ITs green; the same 1
env-guard skip) and parser run `35205554680`. Because the core delta is
test-only, the Gate-3 deployed-lineage analysis (route-set + V28 +
runtime surface) is unaffected by the advance. Conclusion unchanged.

### Gate 2 — r3: PASS

The frozen round record verified, not restated:

- **Zero mutation:** `evidence/cycle-001-r3/` (README + 11 artifacts)
  exists in exactly ONE commit (`037bb2d`, 2026-09-16); the only later
  tracker commit (`a7bc961`, session-91 errata) touched PROGRESS.md and
  bench run-003-b files only — verified by `git log --name-only`.
- **Verdict** (`verdict.json`, sha256 `974bfda972fe41db…`): **PASS** —
  A1–A9 and I1–I6 all HOLDS.
- **Final stored values confirmed:** attempts 3 → 6, correct 2 → 4,
  version v3 → v6; mastery `0.3135593220338984 → 0.7735556015738249`
  (A4: stored = frozen BKT recursion over the true mark order, zero
  DECAY_APPLIED); class mean `0.1384718719 → 0.1959714068` = exactly the
  monitor's contribution (A7, measured stays 8).
- **Zero CLA contamination** (A8/I2): 17 answers touched, all the
  monitor's; the CLA lane's 2 PENDING attempts (d57bdd56, 6361becb)
  byte-identical.
- **Exactly-one-completing-mark semantics** (A1, amended per the frozen
  P.6 Amendment #1): once-per-node, after the (n−1)th part mark,
  settled-total correctness; completing marks 23:18:10.875 / 23:18:17.354
  / 23:18:25.330.
- **Manifest integrity re-derived this session:** the committed file at
  web `012f88c` (= the mark run `35161655716`'s exact checkout,
  head_sha `012f88cb69`) canonicalizes (sorted keys, minus the embedded
  `manifestSha256` field) to sha256
  `d995b9c77bc4d6e9eb061be4de0dae2ff9ad35f8b9ca428d9d7ca6041f3eb633` —
  reproduced locally, verified in-run by `s2_cycle_mark.py`'s sha check,
  embedded in-file, and recorded in the verdict + mark artifacts. (The
  raw-file hash differs by design — canonicalization, not content.)
- **Phase runs cross-checked on GitHub:** after-infra-fail `35160859448`
  (failure @ `1c9c4a3`, pre-mutation cold-start), after `35161163357`,
  dump `35161328200`, mark `35161655716` (@ `012f88c`), final
  `35161751482` (@ `012f88c`) — all success as recorded.
- **I6 single-shot holds at review time:** the newest
  `s2-evidence-cycle` run is still the round's `final`
  (`35161751482`) — zero dispatches after the round.
- The frozen spec carries status EXECUTED/PASS + P.6 Amendment #1 with
  its non-weakening justification; protocol semantics untouched.

### Gate 3 — production lineage: PASS-WITH-NOTES

Fresh probes this session (2026-09-17 ~09:0xZ):

- **Health:** `/actuator/health` → 200 `{"status":"UP"}`.
- **Route-set fingerprint:** live OpenAPI = **97 paths, EXACTLY equal**
  to the source-derived controller route set at core `8eed5e6`
  (zero divergence in either direction; includes the `56f1475`
  mark-scheme-reveal route). `/actuator` root = 401 (locked);
  `/actuator/info` = 200 `{}` — **no build identity is exposed**.
- **Flyway:** live `flyway_schema_history` (read-only SQL) = 28 entries,
  max successful **V28** (`content lexical search`, installed
  2026-09-16T22:31:29Z). V28 exists only in the `99be333`+ lineage →
  the deployed build carries the T-C14-head lineage; the evidence fix
  chain is an ancestor of every candidate build and was behaviorally
  production-verified by the r3 round itself.
- **Live stored state:** the monitor's `skill_states` row read TODAY =
  6 attempts / 4 correct / mastery `0.7735556015738249` / v6 — exactly
  the r3 final values (no drift, no unexplained post-round mutation).
- **`CURRENT_GITHUB_HEAD > DEPLOYED_PRODUCTION_HEAD` is NOT observably
  true** at any external surface (routes, schema, stored state all
  equal).

NOTES (recorded, not concealed):
1. **Exact-SHA pinning is operator-gated** (Render API credential-gated
   by design; `/actuator/info` empty) — the operator Render Events check
   for the `8eed5e6` deploy stands as the confirmation path. The
   deployed runtime is pinned by API+schema evidence to the
   [`99be333`..`8eed5e6`] three-commit window, whose ONLY src/main delta
   is `ChunkLexicalRepository`/`Bm25Retriever` retrieval internals —
   benchmark-lane code with zero `List<RetrievalProvider>` consumer
   sites (session-91 errata's verified statement), i.e. not wired into
   any serving path, so no pilot-relevant behavioral difference exists
   within the window.

### Gate 4 — t0 / scientific baseline: PASS

- **Phase-4 t0** (`t0-phase4-capture.json` sha256 `8e53f72ddd8d12aa…`):
  integrity CLEAN (0 duplicate rows / 0 projection mismatches / 0
  settled-without-evidence); verdict (`t0-phase4-verdict.json` sha256
  `4998a2d189687be5…`): **PASS** — `unexplained: []`, whitelist **W1
  (capture identity)** + **W2 (decay replication)** only, post-S3
  telemetry `{}` (none). S0 and S3 captures CLEAN at both boundaries.
- **Measurement-side read-only:** the instrument is read-only by
  construction (session-level `default_transaction_read_only=on` +
  60 s statement timeout; zero mutating statements in `t0_capture.sql`).
- **Read-only path re-verified LIVE this session:** connected as
  `t0_readonly`; `UPDATE … WHERE 1=0` → BLOCKED ("cannot execute UPDATE
  in a read-only transaction"); grants on `skill_states` = SELECT only;
  DSN-level `default_transaction_read_only=on`.
- **Credential hygiene:** `t0_readonly` appears in tracked content ONLY
  as role-name/provenance metadata (capture `db_user` fields + docs);
  zero DSN/password/`napi_` material in any of the four repos (git grep
  clean); the DSN exists only as an untracked 0600 file in a
  remote-less sandbox repo — never pushed, never committed.

### Gate 5 — operational/security readiness: PASS-WITH-NOTES

- **Pilot Monitor (public ops repo):** run `35183824707` (scheduled,
  2026-09-17T04:56:45Z, head `5e37777`) — success; job log:
  "**SUMMARY: 15/15 checks green (0 failing, 2 advisory)**"; secrets
  preflight (fail-closed) green; monitor-account secrets present.
- **Secrets configured and working:** PILOT_MONITOR_*/PILOT_TEACHER_* in
  the web repo are proven working by the r3 phase runs themselves
  (after/dump/mark/final all authenticated through them).
- **Fail-closed authentication (fresh probes):** 401 on six real routes
  (POST attempts, marking queue-v2, intervention-runs, learner state,
  human-mark, admin chain-health); monitor's teacher-guard 401.
- **LLM chain healthy:** today's monitor probe shows `tutor: 200` with
  the full answer/citations/evidenceCount/model/provider/topics shape —
  the session-67 LLM-key wipe is resolved.
- **No unresolved pilot-blocking operator dependency:** the historic
  blockers (Actions quota, DSN input, LLM keys) are all closed with
  machine evidence.

NOTES (recorded, not concealed):
1. **SECURITY/OPS follow-up — the production DB password exposed during
   Session 75 has NOT been rotated.** Neon operations history (complete
   2026-09-13 → now) contains zero password-reset operations after the
   2026-09-15 reveal; the only post-S75 credential operation is the
   `t0_readonly` role creation (2026-09-16 23:00–23:01Z). The S75
   standing recommendation ("rotate at the next convenient maintenance
   window — Render env update + Neon reset together") remains
   UNEXECUTED. Not pilot-blocking (the exposed value survived only in
   operator-side session artifacts destroyed by sandbox resets; the
   app's env holds the session-67-rotated value; the pilot's own DB
   path is the SELECT-only `t0_readonly` role), but it is scheduled
   follow-up work, not a closed item.
2. Ops-repo `PILOT_TEACHER_*` unset → teacher checks advisory-skip there
   (recovery path documented in the ops README; the web repo's copies
   are proven working).
3. κ gate has zero paired samples (by design until T-C04 mixed-award
   marking accumulates) — Smart Mark stays advisory; human marks
   authoritative.
4. Stale `DEPLOYMENT.md` §4 monitor-account references (audit finding 5)
   remain a standalone docs follow-up.

### Decision

**PILOT READY — PASS-WITH-NOTES.** The runbook's Phase-5 precondition
trio is fully satisfied (three CI rails green at head + r3 PASS + t0
PASS), and the five gates return 3× PASS + 2× PASS-WITH-NOTES with zero
FAILED and zero BLOCKED. The audit's CI=NO → **YES** collapse is
executed on this record. Residual UNVERIFIED items (exact-SHA deployment
pinning; DB password rotation) are recorded above as follow-ups, not
concealed.

**Explicit non-goals preserved:** T-C14 Arm B stays benchmark-gated
(recorded run-003-b: recall@10 ≈ 0.074, MRR ≈ 0.1224, precision@10 ≈
0.0122, 106/120 gold queries zero-candidate under the recorded all-terms
form; SpecificationPoint resolution unscoreable — zero HUMAN_VALIDATED
chunk→spec mappings exist); T-C16 stays owner-gated for corpus mutation
(dogfood the next OCR batch first); Gemini/File Search is not
production-selected; retrieval production-readiness is NOT claimed by
this decision. "Pilot ready" means the closed-loop evidence pilot
(population ~50 retake-path students, 8 weeks, per the pilot plan) may
proceed to its next controlled step on the deployed surface.

**Next engineering workstreams (post-readiness, per the operator's
directive):** (1) T-C13/T-C14 retrieval benchmark improvement — the
Arm-B quality gap + the missing HUMAN_VALIDATED chunk→SpecificationPoint
mapping data; (2) T-C16 corpus-ops dogfood on the next OCR batch before
any Past-Papers mutation; (3) deployment/security residuals — operator
Render Events exact-SHA confirmation, the neondb_owner password
rotation (Render env + Neon reset together), optional ops-repo
PILOT_TEACHER_* population, and the stale DEPLOYMENT.md §4 references.

