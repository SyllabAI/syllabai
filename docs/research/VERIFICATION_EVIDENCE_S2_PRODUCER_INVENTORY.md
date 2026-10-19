# S2 — Producer Inventory and Event Coverage (Verification Evidence Gate)

**Status:** S2 RECORD — gate S2 of the addendum's substrate acceptance gates (§G). Audit artifact; PROPOSED, non-binding until S1 review.
**Date:** 2026-10-19.
**Owner:** SyllabAI learner evidence / learner model (lane w0a, session web-e79a3bd8-5bc9-4aae-abe2-eb5f5d3964dd).
**Parent artifact:** [VERIFICATION_EVIDENCE_GATE_PROPOSAL.md](./VERIFICATION_EVIDENCE_GATE_PROPOSAL.md) (this repository, PR #23), addendum §G gate S2.
**Classifier under audit:** `SyllabAI/syllabai-v2` PR #190 — `apps/api/src/services/learner-model/verification-evidence.ts` (PROTOTYPE / DO-NOT-MERGE).

## 0. Verdict

**S2 verdict: PARTIAL.**

Three of eight classifier-input families have **no producer anywhere in the current implementation** (assistance served, answer/solution exposure, transfer-assessment designation). Two families have real producers with material gaps (grading state, SpecificationPoint anchors). Three are implemented with caveats (identity, event lifecycle mechanics, producer identity). Per gate S2's own law — "any unmapped input keeps the classifier at PROTOTYPE" — the PoC remains PROTOTYPE.

**Not BLOCKED:** the evidence base is sufficient to design the missing producers — every gap below is traced to a concrete serving or marking seam where the producer would live (§4), and the substrate tables the addendum already provisioned (`telemetry_events`, `attempts`, `question_spec_points`) need no schema invention to host the missing event classes. **Not PASS:** no producer exists today that could authoritatively assert `assistance=NONE`, `ANSWER_EXPOSED`, or a transfer designation, so `INDEPENDENT_SUCCESS` and `TRANSFER_SUCCESS` are unclassifiable from real events.

This verdict is a producer-feasibility finding, not a test result. The PoC's unit suite and CI passing does not move it (§8).

## 1. Sources of record (exact SHAs, refreshed first-hand at audit start)

| Artifact | SHA | Note |
|---|---|---|
| Canonical proposal (PR #23 head) | `e71c13167db1f4fe88b5abf1a5dfa50eb9ae98ba` | Unchanged from prior observation; 4 commits stacked on canonical main `36223c6` |
| v2 PoC (PR #190 head) | `3c908519d534fcd3de88e6ff211d73ea517ff776` | Unchanged from prior observation; 3 commits (`ec671ea`, `32af4ce`, `3c90851`) on merge-base `3cdbfdd` |
| v2 origin/main at audit time | `6c84af6f36f50e7996e4de76beba4ea5b394c5c2` | Advanced +49 commits since the addendum's basis `6eaeaa21` (T-MIG-133 books wave, #195/#197/#198/#199/#200) |
| Canonical main | `36223c63e456fb2ef941e9e2410611959f539c29` | PR #23 base |

**Drift check (first-hand):** `git diff --stat 6eaeaa21..6c84af6` over every producer-relevant path — `apps/api/src/services/assessment/`, `services/questions/`, `services/learner/`, `services/learner-model/`, `services/teachermarking/`, `services/selfmark/`, `services/smartmark/`, `services/cla/`, `routes/questions/`, `routes/assessment/`, `routes/teachermarking.ts`, `routes/smartmark/`, `packages/db/src/schema/`, `packages/contracts/src/assessment.ts` — is **empty**. Every addendum §A claim was nevertheless re-verified first-hand at `6c84af6` (§4); two citation corrections of record: the engagement context resolver lives at `apps/api/src/services/cla/context-resolver.ts` (the addendum abbreviated its path), and its verified line anchors are :306-310 / :515 / :564.

**Method:** read-only. Every claim below carries the file and verified line region at the SHA of record. Line numbers are exact for regions read this audit; where a symbol spans a range, the enclosing verified region is given. Inference and unresolved questions are labelled.

## 2. The classifier input set (what S2 must map)

From `verification-evidence.ts` @ PR #190 head, the pure classifier consumes one `VerificationAttempt` per attempt plus the same shape for priors, and one policy value:

| # | Input family | Classifier field(s) |
|---|---|---|
| R1 | Authoritative grading state and correctness | `correct: boolean \| null` |
| R2 | Learner, attempt, canonical question identity | `attemptId`, `questionId` (+ learner linkage implicit) |
| R3 | Canonical SpecificationPoint anchors and validation state | `specificationPointIds: string[]` |
| R4 | Assistance served (hints, step-by-step, teacher support) | `assistance: NONE \| HINT \| STEP_BY_STEP \| TEACHER_SUPPORT \| ANSWER_EXPOSED \| UNKNOWN` |
| R5 | Answer/solution exposure (submit-embedded + reveal endpoints) | `answerExposedBeforeAttempt: boolean`, `assistance=ANSWER_EXPOSED` |
| R6 | Explicit transfer-assessment designation | `isTransferAssessment: boolean` |
| R7 | Server timestamps, event identity, ordering, idempotency, correction/late-event behavior | `occurredAt` (current + priors), `policy.minimumTransferDelayMs`, prior ordering |
| R8 | Producer identity and audit provenance | (cross-cutting: every field's trustworthiness) |

## 3. Coverage matrix (summary)

Status vocabulary: `IMPLEMENTED` (real application-controlled producer on a live serving path), `PARTIAL` (real producer with a material gap enumerated below), `SCHEMA_ONLY` (table/type declared, zero writers), `NO_PRODUCER_FOUND` (exhaustive source search found no producer), `UNVERIFIED` (could not be established this audit).

| # | Input | Status | Producer of record (v2 @ `6c84af6`) | Provenance | Linkage | Next gate |
|---|---|---|---|---|---|---|
| R1 | Grading state / correctness | **PARTIAL** | MCQ: `submit.ts` MCQ insert + `publishMcq` → `createLearnerModelEvidencePublisher` → `updateOnAssessmentEvidence`. Graded lanes: marking lanes mark, but `publishGraded` has **no real implementation** (claim-true noops only) | Server marking/submit path (application-authored) | attemptId+learnerId+questionId on both events; graded event omits anchors | S4 (+S3 event shape) |
| R2 | Learner/attempt/question identity | **IMPLEMENTED** | `attempts` table (uuid PKs, FKs to `users`/`questions`); both evidence events carry all three ids | Application inserts, uuid PKs | Direct; question **version** not pinned (note) | None (version pinning rides S3) |
| R3 | SpecificationPoint anchors + validation | **PARTIAL** | `question_spec_points` (canonical read at event time for MCQ); `publishGraded` payload **omits anchors**; validation state not carried on events | Canonical KG join table (role PRIMARY\|SECONDARY, AI\|HUMAN_VALIDATED) | question↔node, read at event time (MCQ only) | S3 (state carriage, graded-lane anchors); F.5 unchanged |
| R4 | Assistance served | **NO_PRODUCER_FOUND** | Nothing. `tutor_topic_engagements` is topic-level learner-INTENT telemetry (fire-and-forget, no attempt/question columns); **no conversation persistence exists at all** (zero chat/messages tables) | — | none at attempt level | S1 decision + S3 (C.1/C.3) + S4 (C.4) |
| R5 | Answer/solution exposure | **NO_PRODUCER_FOUND** | Nothing. `correctOptionLabel` rides submit/history responses unrecorded; mark-scheme reveal persists nothing and receives no learner/attempt identity | — | reveal path has none today | S3 (B contract) + S4 |
| R6 | Transfer designation | **NO_PRODUCER_FOUND** | Nothing. Zero schema/contract/route surface (only an LLM prompt phrase and content YAML vocabulary match "transfer") | — | — | S1 (F.3) + S3 + S4 |
| R7 | Timestamps / event identity / ordering / idempotency / corrections | **PARTIAL** | `attempts.created_at` server-written; `telemetry_events` (uuid PK, `schema_version`) written fail-loud post-state-update; once-only `evidence_emitted` guarded flip | Server clock; publisher code identity not recorded | per-attempt via payload only | S3 (idempotency keys, correction/quarantine classes); S6 tests |
| R8 | Producer identity / audit provenance | **PARTIAL** | `attempts.provenance` = app-assigned surface constant (`web-quiz-v0[-timed]`); telemetry payloads carry **no attemptId and no producer field**; engagements carry surface/model/classifier_version | Surface-granularity only | telemetry rows not traceable to attempts | S3 (payload contract) |

## 4. Producer traces (per input, source-backed)

### R1 — Authoritative grading state and correctness — PARTIAL

**MCQ lane: IMPLEMENTED, live, fail-loud.** The MCQ submit inserts the attempt with `marking_state='AUTO_GRADED'` and the real `correct` value (`apps/api/src/services/assessment/submit.ts:208-217`), then publishes the evidence event through the Observer seam (`submit.ts:246-269` region: `publishMcq({...})` carrying attemptId, learnerId, questionId, chosenOptionId, correct, marksAwarded, primary/secondary topic nodes, specPointNodeIds, expressed/observed misconception ids, questionType, optionCount, selfDoubtFlag, occurredAt). The live composition binds the real publisher: `buildAssessmentRouters` wires `createLearnerModelEvidencePublisher(sql)` (`apps/api/src/routes/assessment/index.ts:387-392`), which resolves BKT params and runs `updateOnAssessmentEvidence` + the struggle engine, failing the submit on write defects (routes/assessment/index.ts:340-372, "fail-loud" law in source). The once-only `evidence_emitted` guarded flip follows a `fired` claim (`submit.ts:270-275` region). The `frozenParityEvidencePublisher` (`async () => true`, emits nothing) is exported as the E-2 test double only (routes/assessment/index.ts:305-318) — not the live wiring.

**Graded lanes (structured / smart mark / human mark / self mark): marked but never published.** Structured submission lands the attempt at `marking_state='PENDING'` with a non-null placeholder `correct=false` and `marks_awarded=null` (`submit.ts:362-371`). Marking lanes then write real marking state (`HUMAN_MARKED` / `SMART_MARKED` / `SELF_MARKED` per the `ck_attempt_marking_state` check, `packages/db/src/schema/schema.ts:236`) and call `fireEvidence` → `publisher.publishGraded(...)` (`apps/api/src/services/teachermarking/index.ts:665,730-756`). **No real `publishGraded` implementation exists in non-test source**: the teachermarking router defaults to `{ publishGraded: async () => true }` (routes/teachermarking.ts:402 — "the graded-evidence publisher stays noop until the evidence wave owns…"), smartmark does the same (routes/smartmark/index.ts), and selfmark defaults to claim-false (`apps/api/src/services/selfmark/index.ts:55`). The claim-true default flips `evidence_emitted=true` while **nothing is emitted** — a consume-and-drop posture. The two marking telemetry types that would record marking completions, `HUMAN_MARK_RECORDED` and `SMART_MARK_COMPLETED`, are admitted by the `telemetry_events` check constraint (`schema.ts:148`) but have **zero application writers** (repo-wide search: schema/migration files only) — `SCHEMA_ONLY`.

**Consequences for the classifier.** `attempts.correct` is `boolean().notNull()` (`schema.ts:210`) — the classifier's `correct === null` (NOT_YET_GRADED) state is **unpopulatable from a raw row read**; ungraded-ness must be derived from the `marking_state` lifecycle exactly as addendum D.1 requires, or a PENDING row reads as "incorrect". Graded-lane attempts cannot feed BKT/BDT or the classifier with authoritative correctness today. The graded event's `correct` is derived as `marksAwarded >= marksTotal` (`teachermarking/index.ts:744`) — a full-marks-only correctness law encoded in the producer candidate, not ruled on educationally (adjacent to F.2; recorded here as producer semantics, F.2 itself stays UNRESOLVED).

### R2 — Learner, attempt, canonical question identity — IMPLEMENTED

`attempts` (`schema.ts:205-237`): uuid PK; `learner_id` → `users` (cascade), `question_id` → `questions`; indexes on (learner_id, created_at desc) and question_id. Both evidence events carry all three identities (`AssessmentEvidenceEvent`, `apps/api/src/services/learner-model/model-update.ts:280-292`; graded event, `teachermarking/index.ts:735-746`). Producer provenance is application insert paths only; uuids are server-generated (`defaultModelUpdateClock.newId()`, `model-update.ts:294-301`). **Note (not a gap for S2):** attempts pin the question id, not a `question_versions` head — version skew between attempt time and later content reads is possible (the mark-scheme reveal reads the version head at reveal time, `apps/api/src/services/questions/reveal.ts:110-117`). Whether attempt-level content pinning is required is an S3 design question, recorded there.

### R3 — Canonical SpecificationPoint anchors and validation state — PARTIAL

The canonical substrate matches addendum D.3 exactly: `question_spec_points` (`schema.ts:811-839`) — `question_id`, `spec_point_node_id` → `knowledge_nodes`, `role` (PRIMARY|SECONDARY check), `provenance` and `validation_state` (AI_VALIDATED|HUMAN_VALIDATED checks), `uq_question_spec_point`. The MCQ producer reads `specPointNodeIds` at event time and carries them on the evidence event (submit.ts region :246-269) — the "read at event time, never re-derived" law is satisfiable today for MCQ. **Gaps:** (a) the graded-lane `publishGraded` payload **omits spec anchors entirely** (`teachermarking/index.ts:735-746` — only secondary topic nodes ride), so graded attempts carry no anchor evidence; (b) the event carries bare node ids — **validation state is not carried**, so a classifier consuming events cannot distinguish AI_VALIDATED from HUMAN_VALIDATED anchors without a re-read (which would violate "read at event time"); (c) F.5 (the knowledge-node type enum lacks `SPEC_POINT`; spec points legally ride another node type) remains UNRESOLVED and is not re-litigated here. Empty anchor sets are correctly failed closed by the PoC (`specificationPointIds.length === 0` blocks transfer).

### R4 — Assistance served (hints, step-by-step, teacher support) — NO_PRODUCER_FOUND

**The negative result, positively evidenced:**

1. **No attempt-level assistance substrate exists.** `tutor_topic_engagements` (`schema.ts:929-956`) has no attempt-id and no question-id column; `context_reference` is a polymorphic uuid whose meaning is discriminated only by `context_kind` (`KG_TOPIC` → knowledge-node id, `apps/api/src/services/cla/context-resolver.ts:306-310`; `PAST_PAPER_QUESTION` → question id, :515; `QUESTION_PART` → part id, :564; consumers convert part→question via `questionIdByPartId`, `apps/api/src/services/cla/service.ts:488-491`). Linking a row to a specific attempt is impossible from the row alone, exactly as the addendum §A/G3 records.
2. **`signal_type` is learner INTENT, never what was served** — the check constraint admits exactly six intent values (TOPIC_ENGAGEMENT, EXPLANATION_REQUEST, DOUBT_SIGNAL, MISCONCEPTION_RELATED, PREREQUISITE_HELP, CLARIFICATION_REQUEST; `schema.ts:954`). No hint-served / worked-solution-served / support-served row type exists.
3. **Recording is fire-and-forget by documented law** (re-verified at `6c84af6`): both telemetry sinks `.catch(() => { /* a lost engagement row never corrupts the delivered answer */ })` (`apps/api/src/services/learner/engagement-recorder.ts`, verified :140-190 region) — a lost row is unobservable; absence of a recorded hint is NOT evidence that no hint was served.
4. **No conversation persistence exists at all.** The schema contains **zero** conversation/message/chat/exchange tables (repo-wide schema search). Hints and worked solutions served in tutor/CLA conversation leave no record of any kind — this is stronger than "not linked to attempts": the served content is not recorded anywhere.
5. **The attempt-level event that does exist carries no assistance dimension** (R1): `AssessmentEvidenceEvent` (`model-update.ts:280-292`) has no assistance/exposure field.
6. **Teacher support:** the marking lanes persist marks and marking state but publish nothing (R1) and record no assistance-classified linkage; no `TEACHER_SUPPORT` grounding producer exists.
7. **An explicit `NONE` assertion has no producer either** — the classifier's `INDEPENDENT_SUCCESS` gate requires `assistance === "NONE"` (verification-evidence.ts), but with fire-and-forget recording nothing can authoritatively assert a negative. `UNKNOWN` is the only honest value for every attempt today; the PoC's fail-closed default (`ASSISTANCE_UNKNOWN_OR_UNVERIFIED` → ATTEMPTED) is the correct behavior under the current substrate.

**Classification of the negative:** assistance-at-attempt-level is **not instrumented** (the serving pipelines exist and would be the producers under addendum C.4, but emit nothing) — this is distinct from "served but not observed" and from "verified absent". No claim is made that hints are never served; the claim is that no producer records them.

### R5 — Answer/solution exposure — NO_PRODUCER_FOUND

Two exposure surfaces, zero records:

1. **Submit-embedded:** the MCQ submit response carries `correctOptionLabel` (`submit.ts:278-286` region: computed from `optionRows.find((o) => o.is_correct)?.label`, returned on the wire view), and attempt history serves it again (`apps/api/src/services/assessment/history.ts:249` region). Per addendum B.3 this IS an exposure of type `SUBMIT_RESPONSE_CORRECT_OPTION` — and no exposure event is emitted under the same condition that makes the field non-null.
2. **Mark-scheme reveal:** `GET /questions/:id/mark-scheme` (`apps/api/src/routes/questions/index.ts:152-161`, verified) parses the id and calls `module.reveal.reveal(id)` — **only the question id crosses the boundary**; no learner, session, or attempt identity reaches the service. `MarkSchemeReveal.reveal` (`apps/api/src/services/questions/reveal.ts:100-135`, verified) reads servability, version head, newest scheme, applies the validation-state policy switch, and projects a view — **no row of any kind is written**; a served reveal (200) and a withheld one (204) are indistinguishable in the data model.

Zero `ANSWER_EXPOSURE_*` event types exist in the `telemetry_events` check constraint (`schema.ts:148`). The classifier's `answerExposedBeforeAttempt` is therefore unpopulatable from real events; manufacturing it from timing/proximity would violate invariants 3 and 4.

### R6 — Explicit transfer-assessment designation — NO_PRODUCER_FOUND

Exhaustive search across schema, contracts, routes, and services finds **no transfer-designation surface of any kind**. The only "transfer" matches in application source are: an LLM prompt phrasing in the tutor service (`apps/api/src/services/tutor/context.ts:199` — "Encourage transfer to a nearby exam-style task", a recommendation nudge, not a designation) and domain vocabulary inside content YAMLs (e.g. heat transfer in science content). No assessment/quiz metadata field, no contract field, no route. `isTransferAssessment` is unpopulatable except as constant-false. F.2 (prior eligibility) and F.3 (delay and distinctness) remain UNRESOLVED and are preserved as such.

### R7 — Server timestamps, event identity, ordering, idempotency, corrections/late events — PARTIAL

**What exists and is real:** server-side timestamps on attempts (`created_at`, written from the application clock at insert, `submit.ts:216,370`); `telemetry_events` with uuid PK and a `schema_version` column (`schema.ts:133-149`); fail-loud telemetry written after each state write (`model-update.ts:218-241` "fail-loud… no-silent-skip", verified); the once-only guarded `evidence_emitted` flip as a genuine idempotency mechanism at the publisher seam (submit.ts:270-275; `teachermarking/index.ts:750-755`); marking-state lifecycle corrections (OVERRIDDEN) that do not rewrite raw attempts (compatible with invariant 5); a disclosed clock-skew precedent in the CLA engagement sink ("disclosed: the v2 CLA event carries no instant", `engagement-recorder.ts` verified region).

**What is missing for grounding events:** (a) **no idempotency key on telemetry writes** — `writeTelemetry` uses `clock.newId()` fresh per insert (`model-update.ts:233-235`), so a retried publish inserts a duplicate row; there is no natural-key uniqueness on (event_type, attempt, …); (b) **no declared ordering key** beyond `occurred_at` btree indexes — within-attempt ordering is receive-order by construction; (c) graded-lane `occurredAt` is the **marking instant** (`this.clock.now()` at fire time, `teachermarking/index.ts:746`), not the attempt instant — late evidence is the norm on those lanes and must be classified under D.4 chronology rules, not assumed contemporaneous; (d) **no quarantine store and no correction-event class** — D.4's INVALID/SUPPRESSED states and linked-correction semantics exist only as contract prose.

### R8 — Producer identity and audit provenance — PARTIAL

`attempts.provenance` is an application-assigned surface constant — `web-quiz-v0` / `web-quiz-v0-timed` (`submit.ts:206,358`) — surface identity, not client-declared, but also not producer-component identity. The research telemetry payloads (`BktTelemetryPayload`, `BdtTelemetryPayload`, `model-update.ts:182-213`) carry node ids, probabilities, correctness, format and decay fields but **no attemptId and no producer identity field** — a telemetry row cannot be traced back to the attempt that caused it (only learner + time + node). Engagement rows carry producer-ish identity (surface, answer_model, classifier_version, `schema.ts:936-943`). The live publisher's identity exists only at code level (`createLearnerModelEvidencePublisher`). For the auditability the addendum requires (B.2/D.2 "producer identity"), the event payload contracts need producer identity, schema version discipline, and attempt linkage — S3 work.

## 5. Verified gaps versus unverified assumptions

**Verified gaps (first-hand source evidence above):**

| # | Gap | Evidence | Blocks |
|---|---|---|---|
| V1 | No assistance producer at any level; no conversation persistence at all | R4.1-6 | `HINT`/`STEP_BY_STEP`/`TEACHER_SUPPORT`/`NONE` |
| V2 | No exposure producer on either surface | R5.1-2, B.3 | `ANSWER_EXPOSED`, `answerExposedBeforeAttempt` |
| V3 | No transfer designation surface | R6 | `TRANSFER_SUCCESS` |
| V4 | Graded lanes mark but publish no evidence (claim-true noop; evidence_emitted flipped without emission) | R1 | authoritative correctness for graded attempts |
| V5 | Graded-lane events omit spec anchors; validation state not carried on any event | R3 | anchor-trusted classification off events |
| V6 | No telemetry idempotency key, ordering key, quarantine, or correction class | R7 | D.2/D.4 laws |
| V7 | Telemetry payloads lack attemptId + producer identity | R8 | audit chain |
| V8 | `correct` non-null placeholder; NOT_YET_GRADED derivable only from marking_state | R1 | safe PENDING handling |

**Unverified assumptions (declared, not filled):** (a) production runtime behavior — this audit is source-level; no staging or production data was read; (b) whether any out-of-repo writer (script, cron, console) writes the SCHEMA_ONLY event types — searched the repository only; (c) question-version skew impact (R2 note) — flagged, not measured; (d) the 49-commit drift window's *deployed* state (the deployed api bundle may lag origin/main — posture of record says the books route pre-dated the last redeploy; not audited here, irrelevant to source-level S2). None of these change the verdict: the verified gaps are all in-source and decisive.

## 6. Gate evaluation (the five S2 questions, per input)

| # | Real producer? | Application-controlled + auditable? | Links to attempt + canonical SPs? | Retries/async/late/contradiction safe? | Evidence still needed |
|---|---|---|---|---|---|
| R1 grading | Yes for MCQ; **no** for graded lanes (noop) | Yes (server-authored, fail-loud) | Yes (event ids); anchors missing on graded events | Partially: guarded flip yes; no idempotency key; late-marking instant unclassified | Real graded publisher; D.4 chronology for marking-instant events |
| R2 identity | Yes | Yes (server uuids) | Yes (direct FKs) | Yes (immutable inserts) | Version-pinning decision (S3) |
| R3 anchors | Yes for MCQ read; not carried on graded events | Yes (canonical table) | Yes (read at event time) | Yes (stable canonical rows) | Validation-state carriage; F.5 unchanged |
| R4 assistance | **No** | — | — | — | Everything (C.1-C.4) |
| R5 exposure | **No** | — | — | — | Everything (B.1-B.7) |
| R6 transfer | **No** | — | — | — | Everything (+F.2/F.3 rulings) |
| R7 lifecycle | Partial | Yes (fail-loud) | Via payload only | **No** (duplicate-on-retry, no quarantine/correction) | Idempotency keys, ordering keys, quarantine, corrections |
| R8 provenance | Partial | Surface-level only | Telemetry not attempt-traceable | — | Payload contract (attemptId + producer + version) |

## 7. Concrete S3 prerequisites (design inputs; nothing here authorizes implementation)

1. Event table contract for `VERIFICATION_EVIDENCE` / `ASSISTANCE_SERVED` / `ANSWER_EXPOSURE_{REQUESTED,SERVED}` as canonical data-model work (invariant 8) — including natural keys (B.5: `(attempt_id, exposure_type)`), event-id idempotency, and retention per B.7.
2. Producer payload law: attemptId + producer identity + schema version on every grounding event (closes V7).
3. Ungraded-derivation law: `correct` read only through the marking-state lifecycle (closes V8's risk).
4. Graded-lane publication decision: bind a real `publishGraded` (with anchors + full-marks-law review) or formally park graded lanes out of classifier scope (closes V4 honestly rather than by the current claim-true-noop).
5. Anchor validation-state carriage or a declared read-at-classification rule (closes V5).
6. Reveal-path identity injection design (B.4) with the content-selection law unchanged.
7. Chronology rules for marking-instant vs attempt-instant events (D.4), incl. late evidence as linked corrections.
8. Quarantine/INVALID/SUPPRESSED representation (D.1/D.4) — excluded-but-retained, alertable (S7).
9. The C.4 attempt-linkage pathway for conversational surfaces (server-resolved context kind + reference + response mode copied onto the event), with topic-level engagement telemetry unchanged.
10. Version-pinning decision for attempt↔question content (R2 note).
11. F.1-F.5 rulings by the named reviewers (S1) — this audit preserves all five as UNRESOLVED; no educational-policy decision is made or assumed here.
12. Confirmation that no new schema is added merely to complete the PoC (promotion gate 5 / S3's own law).

## 8. Checks actually run this audit (exact results)

| Check | Command / method | Result |
|---|---|---|
| PR head refresh | `git fetch` + `rev-parse` on both repos at audit start | #23 `e71c131…` unchanged; #190 `3c90851…` unchanged; v2 main advanced to `6c84af6…` |
| Drift check | `git diff --stat 6eaeaa21..6c84af6` on all producer-relevant paths | Empty (no producer-path drift) |
| Producer absence searches | Repo-wide `rg` (non-test source): `publishGraded` impls; `HUMAN_MARK_RECORDED`/`SMART_MARK_COMPLETED`/`CLA_EXCHANGE_COMPLETED`/`STRUGGLE_INFERRED` writers; `transfer` across schema/contracts/routes/services; conversation/chat tables in schema | No real `publishGraded` impl (3 noop sites); zero writers for all four telemetry types; transfer = prompt phrase + content YAMLs only; zero chat tables |
| Addendum re-verification | Line-region reads of routes/questions/index.ts, reveal.ts, submit.ts, history.ts, engagement-recorder.ts, cla/context-resolver.ts, cla/service.ts, schema.ts at `6c84af6` | All §A claims hold; two citation corrections recorded (§1) |
| PoC classifier suite (first-hand) | `bun test apps/api/test/learner/verification-evidence.test.ts` at PR #190 worktree, bun 1.3.14, frozen lockfile install exit 0 | **12 pass / 0 fail** (24 expects), exit 0 |
| Model-update suite (first-hand) | `bun test apps/api/test/learner/model-update.test.ts` at same worktree | **26 pass / 0 fail** (79 expects), exit 0 |
| CI of record (not re-run) | PR #190 branch run [39108437035](https://github.com/SyllabAI/syllabai-v2/actions/runs/39108437035) recorded in the proposal | Cited of record; explicitly NOT treated as S2 evidence |

## 9. Scope confirmation

No production code, schema, migration, learner state, deployment posture, or BKT/BDT behavior was changed by this audit. Both PRs remain unmerged; the proposal remains PROPOSED; the PoC remains PROTOTYPE / DO-NOT-MERGE with `masteryMutation: "NONE"` intact; F.1-F.5 remain UNRESOLVED; topic-level engagement is not promoted; transfer designation was not inferred from anything. Archived `syllabai-core` / `syllabai-hub` were not written. This artifact and the two-line indexing/proposal pointers are the only writes.
