# Verification Evidence Gate Proposal

**Status:** PROPOSED — not an accepted architecture change.
**Date:** 2026-10-18
**Owner:** SyllabAI learner evidence / learner model.
**Implementation PoC:** [syllabai-v2 PR #190](https://github.com/SyllabAI/syllabai-v2/pull/190).

## Decision question

Should SyllabAI maintain an explicit, provenance-backed verification-evidence view alongside BKT/BDT so product and recommendation layers can distinguish an attempted answer, supported success, independent success, and delayed transfer success?

## Current source-verified v2 findings

- The v2 assessment evidence event drives BKT skill-state and BDT misconception updates. The current event includes correctness, canonical topic/SpecificationPoint anchors, question identity/type, misconception tags and timestamp.
- The event contract does not include a first-class, application-authored assistance/solution-exposure field or a transfer-assessment designation.
- The v2 tutor reads the governed learner model; deterministic NBA selects bounded next actions; InterventionRun preserves diagnosis/state references and bounded intervention execution.
- The model updater documents a concurrency seam: optimistic-lock conflict handling is not ported, so concurrent updates may lose a version bump. This is a separate hardening issue, not solved by this proposal.

The implementation evidence and detailed gap analysis are recorded in the linked v2 PoC. The PoC branch's full v2 CI passed in run [39108437035](https://github.com/SyllabAI/syllabai-v2/actions/runs/39108437035), including typecheck, full API/package tests, golden self-check, retrieval eval harness, zero-core census gate and Hub build. This is code/CI verification only, not evidence of educational outcome gains or production integration.

## Proposed semantics

A parallel evidence classification may use:

- `ATTEMPTED`: incorrect, ungraded, or support provenance unknown.
- `SUPPORTED_SUCCESS`: correct after a recorded hint, step-by-step support, teacher support, or answer/solution exposure.
- `INDEPENDENT_SUCCESS`: correct with explicit, trusted `assistance=NONE` and no prior answer exposure.
- `TRANSFER_SUCCESS`: independent correct on an explicitly designated transfer assessment, using a distinct canonical question linked to at least one same SpecificationPoint as prior evidence, after an explicitly configured delay.

The delay is an experiment parameter requiring versioning and evaluation; this proposal does not declare a scientifically correct threshold. These labels are evidence descriptions, not mastery scores or causal claims.

## Invariants

1. **No replacement of BKT/BDT.** The ladder is a parallel evidence view, not a new mastery model.
2. **No direct mastery mutation.** Classification alone never updates mastery, the authoritative KG, or SpecificationPoint semantics.
3. **Trusted provenance only.** Assistance, answer exposure, transfer designation, question identity and SpecificationPoint mapping must come from application-controlled validated data, never free-form LLM assertions.
4. **Fail closed.** Unknown assistance, missing SpecificationPoint anchors, ungraded evidence, duplicate/same-question attempts, invalid chronology, or insufficient delay cannot yield transfer success.
5. **Immutable attempt evidence.** Corrections and interpretations remain linked records; raw attempt history is not silently rewritten.
6. **Governed update boundary.** Any future learner-state transition stays inside the v2 application/learner-model layer, with provenance and audit.
7. **No Git-native learner store.** GitLearnOS contributes design patterns only; SyllabAI's canonical learner record remains in its governed application/database model.

## What is strong / weak / could fail

**Strong:** SyllabAI already has canonical question/part identity, SpecificationPoint anchors, BKT/BDT, deterministic next-best-action selection, and InterventionRun snapshots. The proposal can be tested as a narrow additive layer.

**Weak:** current assessment evidence does not yet capture all the trusted assistance/exposure facts needed for reliable classification. A pure classifier with fabricated or inferred inputs would create false confidence.

**Failure modes:** hint usage is not recorded; answer reveal and attempt chronology are ambiguous; transfer questions have bad/missing SpecificationPoint mapping; repeated variants are incorrectly treated as novel; model state is updated from labels outside governed application logic.

**Must remain unchanged:** curriculum truth, SpecificationPoints, immutable attempts, the learner-state overlay, BKT/BDT calibration, validated-content serving gates, and bounded InterventionRun orchestration.

## Promotion gates

Do not promote beyond PROPOSED until all of these pass:

1. CI typecheck and full test suite pass on [v2 PR #190](https://github.com/SyllabAI/syllabai-v2/pull/190).
2. A schema/source audit confirms reliable app-authored support and answer-exposure provenance; if not, stop at the pure prototype.
3. Adversarial scenario and property tests cover unknown support, answer exposure, repeated question, delayed distinct transfer question, unrelated SpecificationPoints, contradictory evidence and concurrent attempts.
4. A frozen held-out evaluation reports false-positive rates for independent/transfer success and separately measures BKT calibration.
5. Any persistent representation is specified in the canonical data model/ADR before production wiring; no new schema should be added just to make the PoC appear complete.

## Decision

**No production adoption yet.** Review the PoC and evidence-provenance feasibility first. The next decision is whether a separate verification-evidence record belongs in the existing attempt/learner-model contract—not whether to replace BKT.

---

## Addendum 2026-10-19 — Provenance substrate contract (G1 exposure, G3 assistance, event lifecycle) — PROPOSED

**Status:** PROPOSED. This addendum defines requirements and acceptance gates for the missing provenance producers. It implements nothing: no migration, no endpoint change, no production wiring, no classifier integration, no mastery-policy change.
**Basis:** Learner Evidence Provenance Audit of syllabai-v2 (lane w0a, session web-e79a3bd8, operator traces 1a1504bb00f7092d → 1a150f55320989cd). Every v2 code fact restated below was re-verified first-hand against `SyllabAI/syllabai-v2` `origin/main` @ `6eaeaa21` on 2026-10-19. The classifier PoC is v2 PR #190 (`poc/verification-evidence-gate` @ `32af4ced`, PROTOTYPE / DO-NOT-MERGE).
**Why:** Promotion gate 2 above ("a schema/source audit confirms reliable app-authored support and answer-exposure provenance") fails today for a substrate reason, not a classifier reason. The four evidence labels are only as trustworthy as the producer events beneath them; this addendum specifies those producers and the gates they must pass before the classifier can leave PROTOTYPE.

### A. Source-verified producer gaps (re-verified 2026-10-19, syllabai-v2 @ 6eaeaa21)

**G1 — answer and mark-scheme exposure is unrecorded.**

- The mark-scheme reveal path persists nothing and is learner-blind: `GET /questions/:id/mark-scheme` (`apps/api/src/routes/questions/index.ts:152-161`) passes only the question id to `MarkSchemeReveal.reveal(questionId)` (`apps/api/src/services/questions/reveal.ts:100-135`), which reads, projects, and returns a view or null. No learner, session, or attempt identity reaches the service; no row of any kind is written. A served reveal and a withheld one (204/404) are indistinguishable in the data model.
- The correct answer is exposed in-band by submission itself: the MCQ submit response carries `correctOptionLabel` (`apps/api/src/services/assessment/submit.ts:279,286`), and attempt history serves it again (`apps/api/src/services/assessment/history.ts:249`). No exposure event is recorded on either surface — the exposure is implicit in a response field and evaporates.
- Consequence: `answerExposedBeforeAttempt` in the PoC classifier is currently unpopulatable from real events. Fabricating it from proximity or timing would violate invariant 3 (trusted provenance only) and invariant 4 (fail closed).

**G3 — assistance provenance does not exist at attempt level.**

- The only assistance-adjacent substrate is `tutor_topic_engagements`, written by the engagement recorder (`apps/api/src/services/learner/engagement-recorder.ts`). Rows are topic-scoped — `(learner_id, node_id, occurred_at, evidence_count, refused, answer_model, signal_type, surface, response_mode, context_kind, context_reference, classifier_version)` — with no attempt id and no question id column. Linking an engagement row to a specific attempt is not possible from the row alone.
- Recording is post-delivery fire-and-forget by documented law: both telemetry sinks swallow write failures (`engagement-recorder.ts:149,181`, the §22 append-guard class). A lost row is unobservable; absence of a recorded hint is therefore NOT evidence that no hint was served.
- `context_reference` is kind-polymorphic: a knowledge-node id for `KG_TOPIC` (`context-resolver.ts:307`), a question id for `PAST_PAPER_QUESTION` (`context-resolver.ts:515`), a question-part id for `QUESTION_PART` (`context-resolver.ts:564`; consumers convert part→question via `questionIdByPartId`, `apps/api/src/services/cla/service.ts:488-489`). The row's `context_kind` column carries the discriminator, but nothing validates that consumers interpret a reference per its kind.
- `FREE_TUTOR` rows carry `response_mode/context_kind/context_reference = null` — unlinked by construction.
- `signal_type` is a learner-INTENT taxonomy (`TOPIC_ENGAGEMENT`, `EXPLANATION_REQUEST`, `DOUBT_SIGNAL`, `CLARIFICATION_REQUEST`, `PREREQUISITE_HELP`, `MISCONCEPTION_RELATED`; classifier `tutor-signals/v2`, deterministic precedence). It records what the learner asked for — never what support was actually served. No hint-served / worked-solution-served / answer-exposed row type exists.
- The assessment evidence event that reaches BKT/BDT (`publishMcq`, `apps/api/src/services/assessment/submit.ts:246-269`) carries no assistance, exposure, or transfer dimension. Graded lanes do not publish model evidence at all; attempts there are held at `marking_state PENDING`, so ungraded-ness must be derived from the marking-state lifecycle, not from the `correct` column's placeholder value.

### B. G1 contract — answer and mark-scheme exposure evidence (PROPOSED)

Exposure becomes a first-class, append-only event class. Two event kinds are required; neither may be inferred from the other.

**B.1 Requested vs served.**

- `ANSWER_EXPOSURE_REQUESTED`: a learner surface asked for the answer or mark scheme (the endpoint was invoked). This event alone proves intent, never exposure.
- `ANSWER_EXPOSURE_SERVED`: the server actually delivered answer content to the learner (a response carrying the answer was committed to the wire). Only `SERVED` may ground the classifier's `ANSWER_EXPOSED` assistance level or its `answerExposedBeforeAttempt` input. A 204 (policy-withheld), a 404 (unservable), a failed, or a partial reveal yields `REQUESTED` — never `SERVED`. Content must not be presumed exposed merely because an endpoint was called.

**B.2 Required fields (both kinds).** Learner id; session id (the learner surface session; where a surface has no session entity today, the producer contract must name its stand-in explicitly rather than silently omitting it); question id; attempt id when an attempt context exists (the mark-scheme reveal path has none today — see B.4); the exposed resource identity (question id / question version / mark-scheme id / option id for submit-embedded exposure); exposure type (enum: `SUBMIT_RESPONSE_CORRECT_OPTION`, `MARK_SCHEME_REVEAL`; extensible only by contract revision); server timestamp; provenance (the application component that witnessed the delivery); event schema version; request id for tracing and idempotency.

**B.3 The submit-embedded answer is exposure.** `correctOptionLabel` in the submit response (`submit.ts:279-286`) and in attempt history (`history.ts:249`) IS an answer exposure of type `SUBMIT_RESPONSE_CORRECT_OPTION`. The exposure event must be emitted under exactly the same condition that makes the field non-null in the response (same attempt, same delivery), linked to that attempt id, so that "the learner saw the correct option label at submit time" is queryable per attempt. The mark-scheme endpoint is not the only exposure surface and must not be modeled as such.

**B.4 Attempt linkage where none exists today.** The reveal path currently receives no learner or attempt identity. The contract requires the reveal producer to carry learner identity (from the authenticated session) and, when the caller holds one, the attempt id — while the service's content-selection law stays unchanged. A served reveal with no attempt in scope records the attempt id as absent; the before-or-after-attempt question is then resolved by the chronology rules of D.4, never by assumption.

**B.5 Idempotency and duplicate delivery.** Every event carries a unique event id; re-delivery of the same event id is a no-op. Submit-embedded exposure additionally carries the natural key `(attempt_id, exposure_type)` — one exposure per attempt per type; a conflicting second row with the same natural key is rejected or deduplicated, never double-counted.

**B.6 Failed and partial reveals.** A requested reveal that withholds (policy 204), fails (5xx), or partially serves records the outcome on the `REQUESTED` event (`WITHHELD` / `FAILED` / `PARTIAL`) and emits no `SERVED` event for content not actually delivered. Exact partial-delivery semantics are fixed per surface by the producer implementation review (gate S4), not improvised per caller.

**B.7 Retention, privacy, auditability.** Exposure events are append-only and immutable (invariant 5). They store resource identities and event metadata, not content blobs. They are learner-personal data: retention follows the platform learner-data retention policy (named by the S1 review), and they exist precisely for audit — the exposure history that independence classification depends on must be reconstructible per learner.

### C. G3 contract — assistance provenance (PROPOSED)

**C.1 Minimal controlled taxonomy.** The authoritative attempt-level assistance enum, aligned with the PoC's `AssistanceLevel` so the contract and the PROTOTYPE speak the same language:

| Value | Meaning | Grounding event required |
|---|---|---|
| `NONE` | An authoritative producer asserts no assistance was served for this attempt | a per-attempt assistance record carrying an explicit none assertion |
| `HINT` | A hint was served | a hint-served event linked to the attempt |
| `STEP_BY_STEP` | Step-by-step guidance or a worked solution was served | the corresponding served event linked to the attempt |
| `TEACHER_SUPPORT` | Teacher or human support reached the attempt | the marking/feedback producer's linkage |
| `ANSWER_EXPOSED` | The answer or mark scheme was exposed before (or at) the attempt | a G1 `ANSWER_EXPOSURE_SERVED` event (section B) |
| `UNKNOWN` | Assistance is uninstrumented or not determinable | (the fail-closed default) |

`UNKNOWN` is the honest default for every attempt whose assistance provenance is not instrumented. Absence of a recorded hint must classify as `UNKNOWN`, never as `NONE` — the fire-and-forget law makes absence unprovable.

**C.2 Authoritative events.** Assistance facts come only from application-controlled producers: the tutor/CLA serving pipeline (what the server actually delivered, mode-tagged), the reveal path (section B), the marking lanes (teacher feedback), and the attempt pipeline itself. Free-form chat text, LLM self-reports, and client assertions are not authoritative (invariant 3).

**C.3 Linkage.** Every assistance event links: learner id, question id, attempt id (directly, or deterministically via a declared rule), the canonical SpecificationPoint anchors of the question read from `question_spec_points` at event time (never re-derived), event id, event version, server timestamp, and producer identity. The existing `tutor_topic_engagements` rows cannot ground attempt-level assistance: topic scope + fire-and-forget + intent semantics disqualify them. They remain topic-level telemetry, and this contract explicitly forbids promoting topic-level engagement into attempt-level assistance evidence without the linkage pathway below.

**C.4 Producer pathway for conversational surfaces (PROPOSED design direction).** Where the CLA/tutor serves a hint or worked solution in a question context, the serving pipeline emits an attempt-level `ASSISTANCE_SERVED` event at delivery time: the server-resolved context kind + reference (question id for `PAST_PAPER_QUESTION`, part id for `QUESTION_PART`) and the response mode are copied onto the event, and the attempt linkage is made by the producer at the moment both facts are in scope. If no attempt exists yet at serving time, the event records learner + question + timestamp and the linkage resolves under D.4 chronology rules — never by inference from semantic similarity. Topic-level engagement recording continues unchanged as telemetry.

**C.5 Retries and asynchronous processing.** Assistance events are idempotent by event id: retries and at-least-once delivery deduplicate. Async pipelines stamp the delivery instant, not the enqueue instant; where only an enqueue instant exists, the skew is recorded explicitly on the event (the engagement recorder's disclosed CLA clock-skew is the honesty precedent). A retried delivery that arrives after an attempt was classified does not retroactively mutate the persisted label (invariant 5) — it lands as a linked correction event that a review audit can see.

### D. Event lifecycle and learner-state safety (PROPOSED)

**D.1 Evidence states.** Verification evidence for an attempt is exactly one of:

- `PENDING` — the attempt exists but is not yet authoritatively graded. Graded-ness is derived from the marking-state lifecycle (`marking_state` AUTO_GRADED for instant MCQ, PENDING for graded lanes, with the guarded `evidence_emitted` flip); the `correct` column's non-null placeholder must never be read as a grade.
- `GRADED_CORRECT` / `GRADED_INCORRECT` — an authoritative grade is recorded.
- `INVALID` — the attempt failed a validation gate (malformed provenance, unresolvable anchors, impossible chronology); excluded from classification, retained for audit.
- `SUPPRESSED` — excluded by policy (duplicate delivery, quality flag); retained and auditable, never silently deleted.

**D.2 Identity, ordering, idempotency, concurrency.** Every event carries: a unique event id (duplicate delivery = no-op), the attempt id, an event schema version, a server-side timestamp, producer identity, and a declared ordering key. Within an attempt, ordering follows the attempt-local sequence where the producer has one, else server receive order with the skew disclosed. Concurrent writers follow the append-only law: the first committed event wins per natural key; conflicts surface as audit events, never silent overwrites. The model updater's documented optimistic-lock concurrency gap (base proposal, "Current source-verified v2 findings") is a hardening prerequisite for any producer writing near the model boundary.

**D.3 SpecificationPoint linkage and validation.** Canonical anchors come only from `question_spec_points` (schema: `question_id`, `spec_point_node_id` → knowledge_nodes, `role` PRIMARY|SECONDARY, `provenance` and `validation_state` AI_VALIDATED|HUMAN_VALIDATED, unique pair). Events carry anchor ids read at event time; classification validates that anchors exist and parse before use; empty or unresolvable anchors fail closed (no transfer; a reason code for independence — never a guessed anchor).

**D.4 Missing, late, contradictory, or malformed provenance.**

- Missing (no event): the classifier input defaults to its fail-closed value (`UNKNOWN` assistance; exposure unprovable, so no unexposed assertion may be manufactured).
- Late (arrives after classification): lands as a linked correction event; a persisted label is not retroactively rewritten; downstream consumers see the correction.
- Contradictory (e.g. a served exposure event after an asserted none): the contradiction is recorded as a first-class audit fact and the attempt's independence claim is voided to the conservative label.
- Malformed (unparseable timestamp, unknown event version, broken references): the event is quarantined — excluded, retained, alerted on. Unknown schema versions fail closed and are never best-effort parsed.

**D.5 Boundary to BKT/BDT and learner state.** The evidence ladder is a parallel view: classification never writes mastery (the PoC's `masteryMutation: "NONE"` is the law, not a stub). Assessment evidence reaches BKT/BDT through the existing governed publisher seam (`publishMcq` → `updateOnAssessmentEvidence`); any future wiring that lets evidence labels influence learner state must (a) stay inside the v2 application/learner-model layer, (b) carry provenance and audit, and (c) pass its own review gate (S3) — the ladder's existence must not silently change what BKT/BDT consume.

**D.6 How exposure and assistance affect independent success.** `INDEPENDENT_SUCCESS` requires: an authoritative correct grade; assistance `NONE` backed by an authoritative none assertion; no `ANSWER_EXPOSURE_SERVED` for the question's content before the attempt (and none embedded in the submit itself — B.3), within the exposure window the policy defines (window definition is open decision F.1); anchors present. Any other correct attempt is `ATTEMPTED` or `SUPPORTED_SUCCESS`.

**D.7 Transfer supply and validation.** `TRANSFER_SUCCESS` additionally requires:

- an explicit transfer designation supplied by an application producer (assessment/quiz metadata). No transfer designation exists anywhere in v2 today; it must be created by a reviewed producer, never inferred;
- a versioned experiment parameter for the minimum delay — declared, versioned, and evaluated per the base proposal; no numeric default is invented here;
- question distinctness (a different canonical question id) and canonical SpecificationPoint overlap via `question_spec_points`;
- a prior that is itself trusted success evidence — the audit's F-5 finding: a prior graded-incorrect, answer-exposed, or assistance-UNKNOWN attempt cannot ground transfer. The PoC patch (v2 commit `804b3632` on branch `audit/evidence-provenance`, PROTOTYPE / DO-NOT-MERGE) encodes this fail-closed prior rule as a candidate implementation; the educational ruling itself remains open (F.2).

### E. Standing invariants (unchanged by this addendum)

1. SyllabAI remains authoritative for curriculum and educational semantics.
2. SpecificationPoints remain canonical anchors.
3. Learner state is an overlay on curriculum truth.
4. Raw conversation remains history/audit data.
5. Extracted evidence is provenance-bearing.
6. Chat output cannot directly mutate mastery or the canonical KG.
7. Unknown provenance fails closed; it is never fabricated.
8. External/provider-specific infrastructure cannot become the canonical data model.

### F. Open educational decisions (UNRESOLVED — none may be settled by implementation convenience or by passing tests)

1. **Independence after assistance or exposure.** What qualifies as independent success once a learner has received assistance or seen the answer — a cooling-off period, a distinct-question rule, a different question family? Required reviewers: educational-policy owner + curriculum authority.
2. **Prior-evidence eligibility for transfer.** Does a prior graded-but-incorrect attempt count as prior evidence for a transfer claim? The PoC patch encodes "no" as a candidate; no authoritative contract exists. Required reviewers: educational-policy owner.
3. **Transfer delay and question distinctness.** What minimum delay and distinctness rules are required? The delay must become a versioned, evaluated experiment parameter; no scientific threshold is declared here. Required reviewers: educational-policy owner + learner-model owner.
4. **The exact submit-time exposure event.** What precisely constitutes answer exposure when the answer is embedded in the submit response (B.3) — the `correctOptionLabel` field alone, or also the marks breakdown and implication reveal? Required reviewers: educational-policy owner + assessment product owner.
5. **SpecificationPoint representation.** How should the canonical SpecificationPoint concept be represented when the knowledge-node type enum does not include `SPEC_POINT`? The DB constraint admits SUBJECT/UNIT/TOPIC/SUBTOPIC/MISCONCEPTION/CONCEPT while the graph-as-code resources declare a SPEC_POINT node family and `question_spec_points` references knowledge-node rows — the node type under which spec points legally ride is unrecorded architecture debt. Required reviewers: curriculum/KG authority.

### G. Substrate acceptance gates (extend, and must not bypass, the promotion gates above)

- **S1 — Contract review and educational-policy decisions.** This addendum reviewed; F.1–F.5 decided by the named reviewers; a decision contradicting the PoC's encoded candidates is recorded as a contract revision, not a silent override.
- **S2 — Producer inventory and event coverage.** An authoritative inventory maps every classifier input (assistance, exposure, transfer designation, anchors, grading) to a named producer and event; any unmapped input keeps the classifier at PROTOTYPE.
- **S3 — Schema/API design and migration review.** Event tables and contract schemas reviewed as canonical data model work (invariant 8); migrations reviewed; no schema is added merely to make the PoC appear complete (promotion gate 5).
- **S4 — Producer implementation.** Producers implemented with the idempotency, ordering, and failure laws of this addendum; reviewed against the S2 inventory.
- **S5 — Integration and adversarial tests.** Integration tests cover the true producer paths; adversarial tests cover unknown support, exposure-before-attempt, duplicate delivery, reordering, concurrent attempts, contradictory provenance, and malformed events (the PoC's scenario matrix is the floor, not the ceiling).
- **S6 — Replay, idempotency, ordering, and failure-mode tests.** Deterministic replay of an event stream yields identical classifications; duplicate, late, out-of-order, and malformed events never change a label beyond the D.4 laws.
- **S7 — Telemetry and observability.** Quarantines, contradictions, dedupe hits, and producer losses are observable; a silent-loss posture (the current fire-and-forget law) is not acceptable for grounding events.
- **S8 — Staged rollout and rollback.** Producers roll out behind explicit enablement with a rollback that leaves no half-written event classes; classification reads fail closed during rollout gaps.
- **S9 — Empirical verification before promotion.** A frozen held-out evaluation measures false-positive rates for independent and transfer success (promotion gate 4); a green test suite alone never establishes educational correctness.

### H. Non-goals of this addendum

No migrations, endpoint changes, production wiring, classifier integration, or mastery-policy changes are authorized. The PoC remains PROTOTYPE / DO-NOT-MERGE. Nothing here merges v2 PR #190, changes the deploy posture, or alters BKT/BDT.

### I. S2 record (2026-10-19) — gate S2 discharged: PARTIAL

Gate S2 (producer inventory and event coverage) was executed against v2 `origin/main` @ `6c84af6f` (addendum basis `6eaeaa21` re-verified; zero producer-path drift in the 49-commit window) and PoC PR #190 @ `3c908519`. **Verdict: PARTIAL** — grading (MCQ), identity, and anchor substrates have real application-controlled producers; assistance served, answer/solution exposure, and transfer designation have **no producer anywhere in the implementation**; graded-lane evidence publication is a claim-true noop; telemetry lacks idempotency keys, quarantine, and producer identity. Per §G/S2's own law the classifier stays at PROTOTYPE. Full coverage matrix, producer traces, verified gaps (V1–V8), and S3 prerequisites: [VERIFICATION_EVIDENCE_S2_PRODUCER_INVENTORY.md](./VERIFICATION_EVIDENCE_S2_PRODUCER_INVENTORY.md). F.1–F.5 remain UNRESOLVED.
