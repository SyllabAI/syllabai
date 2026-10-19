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

### J. S1 decision preparation (2026-10-19) — F.1–F.5 briefs for human adjudication — PROPOSED

**Status:** PROPOSED decision-preparation record for gate S1 (§G: "Contract review and educational-policy decisions"). It **decides nothing**: F.1–F.5 remain **UNRESOLVED**; every recommendation below is labeled **PROPOSED** and becomes policy only when the §F-named reviewers record a decision of their own. No agent may impersonate a human reviewer or make binding educational decisions. Per §G/S1's own law, a reviewer decision contradicting a PoC-encoded candidate is recorded as a contract revision, never a silent override.
**Prepared by:** lane w0a, session web-e79a3bd8-5bc9-4aae-abe2-eb5f5d3964dd, operator trace 1a1536e9184645dd, 2026-10-19.

**Sources of record (exact SHAs, refreshed first-hand at preparation start):**

| Artifact | SHA | Method class |
|---|---|---|
| Canonical proposal + addendum (§F wording quoted verbatim from here) | PR #23 head `e71c131`; carried at `8c32913` (PR #24 head, branch `s2-producer-inventory`) | Direct repository evidence |
| S2 producer-inventory record | `8c32913` (`VERIFICATION_EVIDENCE_S2_PRODUCER_INVENTORY.md`) | Direct repository evidence |
| v2 classifier source, schema, tests (merged PoC) | v2 `origin/main` `26d98da` (merged PoC head `3c90851` verified ancestor first-hand) | Direct repository evidence |
| Decision-existence sweep | canonical `origin/main` `3e84070` (`git grep`: zero F-resolution markers); PR #23 + PR #24 conversation pages fetched 2026-10-19: zero formal reviews, zero F-rulings, both DRAFT | Direct repository/page evidence |
| Operator governance acts (context, not re-litigated) | v2 PR #190 merge `7d19dbe` @ 2026-10-19T08:53:48Z under operator promotion order trace `1a1535a2687b6c39`; promotion receipt `2cfef43` | Repository evidence of operator acts |

**The v2 PoC merge is not educational-policy acceptance.** PR #190's merge integrated PROTOTYPE code under an operator promotion order; the classifier's own header still reads "PROPOSED proof of concept" (`verification-evidence.ts:2` @ `26d98da`) and its candidates remain candidates. `masteryMutation: "NONE"` is intact (`:55`); BKT/BDT are untouched.

**J.0 Brief format.** Each brief states: the exact §F question (verbatim); educational stakes; source evidence (file:line at the SHAs above); options with consequences and failure modes (including defer); the **PROPOSED** recommendation with rationale and its explicit relation to the PoC's encoded candidates (RATIFY = aligns with the encoded behavior; REVISE = a contract revision per §G/S1); required reviewers exactly as documented in §F (roles only — no names invented); acceptance criteria that make the decision implementable; and a semantics classification (curriculum / learner-evidence / technical representation).

#### J.1 — F.1 Independence after assistance or exposure

**Exact question (§F.1, verbatim):** "What qualifies as independent success once a learner has received assistance or seen the answer — a cooling-off period, a distinct-question rule, a different question family?" Required reviewers: educational-policy owner + curriculum authority.

**Why it matters.** `INDEPENDENT_SUCCESS` is the label the decision question (top of this proposal) expects product and recommendation layers to trust most, so its decay rule defines the ladder's reporting value. Ruled too strictly, the label permanently punishes scaffolding that pedagogy intends to fade; ruled too loosely, exposure washes out instantly and the label inflates — the base proposal's own failure-mode list warns against fabricated confidence. The ruling also fixes the retake law: what the recorded exposure of question Q means for later attempts on Q.

**Source evidence.** D.6 (independence requires no exposure "within the exposure window the policy defines (window definition is open decision F.1)"); PoC per-attempt law: exposure or support on the current attempt → `SUPPORTED_SUCCESS` (`verification-evidence.ts:89-104`), `UNKNOWN` assistance → `ATTEMPTED` fail-closed (`:106-112`); prior-attempt exposure/`UNKNOWN` blocks `TRANSFER_SUCCESS` (`:133-134`) — but past assistance/exposure does **not** otherwise constrain a later attempt's independent label (the encoded law is attempt-local); C.1 (absence of a recorded hint is `UNKNOWN`, never `NONE`); B.3 (submit-embedded exposure is a first-class exposure event linked to its attempt); S2 record R4/R5 (no assistance/exposure producers exist — every real attempt is `UNKNOWN` → `ATTEMPTED` today, so this ruling is unexercisable until S4 producers land).

**Options and consequences.**
- **A. Attempt-local (PoC status quo).** Independence is judged per attempt; history matters only through the transfer gate. Pro: fail-closed, simple, no new parameters, already adversarially tested. Con/failure: no scaffolding-fade story — a learner aided yesterday is "independent" today on the same SpecificationPoint once producers exist (reporting-inflation risk); mitigated only by the B.3 exposure record being queryable per learner (the contract already requires it).
- **B. Cooling-off window.** A versioned window after the latest exposure/assistance event during which independence is blocked on that SpecificationPoint. Pro: the pedagogically standard fading-scaffolding shape; parameterizable; S9-evaluable. Con: needs event chronology (D.4) plus a per-learner, per-SP exposure/assistance query (producer + S3 retention/audit work); window too short inflates, too long starves the label; adds a second versioned parameter beside the F.3 delay.
- **C. Distinct-question rule (no time dimension).** Independence requires a question different from the assisted/exposed one. Pro: simple; canonical question ids exist. Con: variant leakage — no question variant/family fields exist in the v2 schema or contracts (first-hand grep @ `26d98da`), so "distinct" cannot exclude near-duplicates; effectively defers the real rule.
- **D. Defer / unresolved.** Behaviorally identical to A but leaves D.6's F.1 pointer dangling and S3 unsizable — strictly worse than A.

**PROPOSED recommendation: A now, with B's machinery explicitly reserved (RATIFY).** Ratify the PoC's encoded per-attempt law as the recorded v1 semantics, and record that any window or family upgrade path (B/C) must arrive as a versioned, evaluated experiment parameter (the F.3 pattern) at S9 evaluation — never as an implicit behavior change. Rationale: with zero producers in place (S2), every attempt is `UNKNOWN` → `ATTEMPTED` regardless of the ruling; ratifying the encoded law unblocks S3 design while keeping the educational question open and measurable. Explicitly NOT a decision: this recommendation lapses entirely when the named reviewers rule otherwise.

**Acceptance criteria:** D.6's "(window definition is open decision F.1)" replaced by the decided rule (or by an explicit "per-attempt-local; window machinery reserved to a versioned parameter, pending" sentence); a written retake law — whether the recorded submit-embedded exposure of question Q may block later attempts on Q (recommended shape: yes, resolved by D.4 chronology on event instants, never by assumption); an S9 false-positive measurement plan for the chosen rule.

**Semantics classification:** learner-evidence semantics (label meaning); touches assessment retake policy (product); the reserved window parameter is technical representation.

#### J.2 — F.2 Prior-evidence eligibility for transfer

**Exact question (§F.2, verbatim):** "Does a prior graded-but-incorrect attempt count as prior evidence for a transfer claim? The PoC patch encodes 'no' as a candidate; no authoritative contract exists." Required reviewers: educational-policy owner.

**Why it matters.** The transfer claim's evidentiary base decides what `TRANSFER_SUCCESS` can be cited for downstream. A "yes" ruling makes transfer labels ride partly on failure evidence; a "no" keeps transfer rare but precise. Either way the ruling must be authoritative before S3 sizes the prior-evidence contract and S5 writes its adversarial cases.

**Source evidence.** D.7 bullet 4 (a prior must be "itself trusted success evidence"; the earlier provenance audit's F-5 finding — distinct from decision F.5 — that a graded-incorrect, answer-exposed, or assistance-UNKNOWN prior cannot ground transfer; PoC patch commit `804b3622` encoded the fail-closed prior rule as a candidate; "the educational ruling itself remains open (F.2)"); merged classifier fail-closed prior law `verification-evidence.ts:127-134` (`prior.correct !== true → rejected`, covering both ungraded-null and incorrect priors; exposed and `UNKNOWN` priors rejected), executable test pin "an incorrect, exposed, or provenance-unknown prior can never ground transfer" (`verification-evidence.test.ts:105`); S2 R1 (graded-lane evidence publication is a claim-true noop — today only MCQ priors could ever be trusted successes, so F.2's practical scope is MCQ-until-S4).

**Options and consequences.**
- **A. "No" — only a trusted prior SUCCESS grounds transfer (PoC candidate).** Pro: fail-closed (invariant 4); transfer claims rest on verified success; zero code delta (already encoded and tested). Con: ignores instruction-gain narratives (fail → reteach → independent transfer yields no transfer label); labels stay rare.
- **B. "Yes with conditions" — a graded-incorrect prior counts as evidence the SpecificationPoint was taught, so transfer measures post-teaching generalization.** Pro: matches teach→retest cycles; richer signal. Con: `TRANSFER_SUCCESS` partly grounded in failure evidence — semantically strained; inflates the label; requires rewriting D.7's requirement text (recorded contract revision) + classifier change + new S5 adversarial cases; risks rewarding "failed fast, moved on" patterns.
- **C. Remediation-gated eligibility — an incorrect prior counts only when followed by recorded remediation.** Pro: principled middle; ties eligibility to evidence of intervention. Con: depends on an attempt/SP-level remediation-linkage producer that does not exist today (InterventionRun exists as orchestration; the linkage is unbuilt — S2 found no such producer); heaviest S3/S4 lift.
- **D. Defer.** Leaves D.7's open parenthetical in place; S3 cannot size the prior contract; worst option.

**PROPOSED recommendation: A (RATIFY).** Adopt the PoC's fail-closed prior law as the recorded v1 contract; record B as the primary S9 evaluation candidate (run both eligibility laws over the frozen held-out evaluation and compare false-positive profiles) and C as a producer-dependent future extension. Rationale: invariant 4 (fail closed); the encoded candidate is already adversarially tested; switching later is exactly the recorded-contract-revision path §G/S1 provides. A reviewer choice of B or C is a contract revision + classifier revision (S3/S4 scope), never a silent override.

**Acceptance criteria:** D.7 bullet 4's closing sentence ("the educational ruling itself remains open (F.2)") replaced by the decided eligibility law; if A: no classifier change — the existing test pin remains the law's executable form; if B/C: contract revision text + classifier change + enumerated S5 adversarial cases (remediation linkage, regraded priors, contested grades).

**Semantics classification:** learner-evidence semantics (pure); no curriculum or technical-representation change.

#### J.3 — F.3 Transfer delay and question distinctness

**Exact question (§F.3, verbatim):** "What minimum delay and distinctness rules are required? The delay must become a versioned, evaluated experiment parameter; no scientific threshold is declared here." Required reviewers: educational-policy owner + learner-model owner.

**Why it matters.** The delay separates "remembering the specific answer" from "having the skill"; distinctness defines what counts as a different question. Together they decide whether `TRANSFER_SUCCESS` is measurable at all — promotion gate 4 requires an S9 false-positive measurement for transfer, which cannot run without a decided distinctness law and a (possibly "unset") delay parameter.

**Source evidence.** Base §Proposed semantics ("The delay is an experiment parameter requiring versioning and evaluation; this proposal does not declare a scientifically correct threshold"); D.7 (versioned parameter; "a different canonical question id"; canonical SpecificationPoint overlap via `question_spec_points`); classifier `:43-49` (`minimumTransferDelayMs` — "Proposed experiment parameter. No scientific default is imposed here; callers must choose and version this threshold before evaluation"), `:126` (question-id distinctness), `:135-138` (strict prior chronology + delay + SP overlap); first-hand grep @ `26d98da`: **no question variant/family fields exist** in the v2 schema or contracts, so variant-level distinctness has no data model today; F.1 interplay (any cooling-off window shares this exact machinery — see J.1).

**Options and consequences.**
- **A. Pick a numeric threshold now.** Contradicts the proposal's own law (no scientific threshold declared; gate 4 demands evaluation first); any number picked today is decoration, not policy.
- **B. Ratify the structure, parameterize the value.** Decide the LAW (distinct canonical question id + at least one shared SpecificationPoint + strictly-earlier trusted prior + minimum delay as a named, versioned, owned parameter) and record the numeric value as **experiment configuration for the S9 evaluation** with an explicit not-a-scientific-claim label. Pro: implementable now; honest; S9-runnable. Con: until a value is chosen, `TRANSFER_SUCCESS` cannot fire (acceptably fail-closed); parameter governance must exist (learner-model owner).
- **C. Stronger distinctness (variant/family ban).** Not implementable today (no variant metadata exists — fact above); would require content-model work (S3, invariant 8) plus a curation decision. Record as a future revision only if variant metadata ever lands.
- **D. Defer.** Leaves the gate unmeasurable and S3 unsizable.

**PROPOSED recommendation: B (RATIFY the structure, parameterize the value).** The PoC encodes exactly this structure, so ratification requires no classifier change; the numeric choice is delegated to the named reviewers as a versioned experiment decision with an S9 evaluation plan attached. Candidate starting points for the reviewers' choice — 24h and 7d — are offered as evaluation seeds only, not recommendations and not policy. This is the recommendation shape the base proposal itself mandates.

**Acceptance criteria:** named parameter with owner (learner-model owner) and versioning home; an initial value recorded as experiment configuration, or an explicit "transfer disabled until a value is chosen" state; D.7's requirement text marked decided; an S9 evaluation plan naming the transfer false-positive metric under the chosen value.

**Semantics classification:** the structure = learner-evidence semantics; the numeric value = versioned experiment parameter (explicitly not educational-policy truth, per the base proposal's own words); the distinctness law = learner-evidence + technical representation.

#### J.4 — F.4 The exact submit-time exposure event

**Exact question (§F.4, verbatim):** "What precisely constitutes answer exposure when the answer is embedded in the submit response (B.3) — the `correctOptionLabel` field alone, or also the marks breakdown and implication reveal?" Required reviewers: educational-policy owner + assessment product owner.

**Why it matters.** B.3 makes the submit-embedded answer a first-class exposure; the boundary of "exposure" drives the SUPPORTED/INDEPENDENT boundary (F.1) and any future window. Too narrow a definition → exposure escapes the record and independence inflates (false positives); too broad → every MCQ attempt is recorded as "exposed" and the ladder collapses toward `ATTEMPTED`/`SUPPORTED_SUCCESS` for all of MCQ, destroying the label's value.

**Source evidence.** B.1 (`REQUESTED` vs `SERVED`; only `SERVED` grounds the classifier), B.2 (exposure-type enum opens with `SUBMIT_RESPONSE_CORRECT_OPTION` and `MARK_SCHEME_REVEAL`), B.3 (verbatim law: the exposure event must be emitted "under exactly the same condition that makes the field non-null"), the two surfaces `submit.ts:278-286` + `history.ts:249` (S2 R5), and D.6's independence requirement — which carries a **temporal ambiguity the reviewers must resolve**: quoted, independence requires "no `ANSWER_EXPOSURE_SERVED` for the question's content before the attempt (and none embedded in the submit itself — B.3), within the exposure window the policy defines". Two readings: **(a)** the attempt's own submit-embedded reveal counts as exposure *for that attempt* — then every MCQ attempt whose response carries `correctOptionLabel` at scoring time is `SUPPORTED_SUCCESS`, and MCQ can never be `INDEPENDENT_SUCCESS`; **(b)** the attempt's own post-response result reveal does not block its own independence — the response was committed before the reveal and the classifier's field is "exposed **before** this attempt" (`verification-evidence.ts:35-36`) — while the recorded B.3 event feeds later attempts, retakes, and the F.1 window. The merged PoC encodes reading (b) via field semantics; D.6's parenthetical as literally written leans toward (a). Surfaced here per the no-silent-reinterpretation law: **either reading requires a one-sentence D.6 precision revision, recorded as a contract revision (§G/S1), before S3 fixes the exposure contract.**

**Options and consequences.**
- **A. Narrow content: `correctOptionLabel` alone.** Pro: minimal; exactly what B.3 names. Con: if marks breakdowns or per-option markers also discriminate the answer, exposure escapes the record → false independence.
- **B. Broad content: label + marks breakdown + implication reveals.** Pro: safe-side capture. Con: over-capture — a marks total that does not discriminate would still be recorded as exposure, inflating `SUPPORTED_SUCCESS`/`ATTEMPTED` and starving the ladder; per-surface judgment is unavoidable anyway.
- **C. Enumerated-per-surface content contract.** Define exposure as "response content from which the correct answer or its direct implication is derivable", enumerated per surface at producer review (the B.6 pattern: fixed per surface at S4, never improvised per caller). Initial enumeration for the MCQ submit surface: `correctOptionLabel`; per-option correctness markers; marks breakdown **only when it discriminates the correct option** (e.g., per-option marks). Attempt history mirrors the submit surface; mark-scheme reveal is already `SERVED`-typed content (B.1).
- **D. Defer.** Leaves B.2's enum with one member and the S4 producer contract unsizable.

**PROPOSED recommendation: C for content, temporal reading (b) for the attempt's own result-reveal (RATIFY the PoC's field semantics), with the D.6 precision revision recorded either way.** Rationale: C is the only shape both safe-side and extensible without re-litigating per caller; reading (b) preserves the ladder's meaning for MCQ (whose result reveal is inherent to scoring) while the recorded B.3 event still feeds retakes and the F.1 window. If the reviewers rule reading (a), that is a contract revision that also re-scopes the classifier's exposure-input semantics (S3/S4) — and MCQ independence becomes impossible by law, which must then be an explicit, accepted consequence.

**Acceptance criteria:** a per-surface enumeration table (initial: MCQ submit, attempt history, mark-scheme reveal) fixed at S4 producer review; D.6 revised to the decided temporal reading (recorded revision); B.3's "same condition" emission law wired to the enumeration; the B.7 retention policy named (see J.7 riders).

**Semantics classification:** learner-evidence semantics + assessment product policy (what a response carries); the enumeration contract itself is technical representation.

#### J.5 — F.5 SpecificationPoint representation

**Exact question (§F.5, verbatim):** "How should the canonical SpecificationPoint concept be represented when the knowledge-node type enum does not include `SPEC_POINT`? The DB constraint admits SUBJECT/UNIT/TOPIC/SUBTOPIC/MISCONCEPTION/CONCEPT while the graph-as-code resources declare a SPEC_POINT node family and `question_spec_points` references knowledge-node rows — the node type under which spec points legally ride is unrecorded architecture debt." Required reviewers: curriculum/KG authority.

**Why it matters.** Transfer's SP-overlap law (D.7; classifier `:138`) and the anchors' canonicality (standing invariant 2: "SpecificationPoints remain canonical anchors") are only as meaningful as the underlying representation. With the carrier type unrecorded, anchor sets cannot be validated *as spec points*, overlap computations cannot be defended as canonical, and the S2 V5 gap (validation-state carriage) has no settled representation to close into.

**Source evidence (first-hand @ `26d98da`).** The DB check constraint `ck_node_type` admits exactly SUBJECT/UNIT/TOPIC/SUBTOPIC/MISCONCEPTION/CONCEPT — no `SPEC_POINT` (`packages/db/src/schema/schema.ts:33`); the graph-as-code asset self-declares `node_families: [TOPIC, SUBTOPIC, SPEC_POINT]` with `spec_points: 182` (`apps/api/src/services/teacher/concept-graph/specification_points.yaml` meta block); hub-side retrieval/citation vocabularies carry a `SPEC_POINT` kind (`apps/hub/src/lib/ai/retrieval.ts:38`, `apps/hub/src/lib/citation-map.ts:54`); `question_spec_points` references `knowledge_nodes` rows (S2 R3). The concept is real across content and citation layers while its canonical DB representation is genuinely unrecorded. **Which node_type the 182 anchors actually ride in seeded data was NOT established in this preparation** — that data audit is the F.5 review's first input (it needs DB read access or the seed-loader mapping; neither was exercised here, keeping this task read-only on learner state and schema).

**Options and consequences.**
- **A. Ratify an existing type as the legal carrier.** Requires the data audit above to know what is actually in use. Pro: zero schema change; debt recorded. Con: the enum cannot distinguish spec points from genuine topics/subtopics; nothing enforces spec-point-ness; the debt becomes permanent structure.
- **B. Extend the enum with `SPEC_POINT`.** Pro: first-class representation matching the graph-as-code truth and the hub vocabularies; enforceable. Con: migration + backfill for existing anchor rows; touches the curation pipeline's output contract (loader + validators); must follow invariant-8 discipline (canonical data-model work, reviewed — S3 scope, not this task).
- **C. Separate canonical `spec_points` table.** Pro: cleanest separation from the KG hierarchy. Con: largest restructure; `question_spec_points` FK re-targeting; departs from the current graph-as-code resource shape.
- **D. Defer.** The debt stays unrecorded; S3 cannot size anchor validation or close S2 V5.

**PROPOSED recommendation: B as the durable direction, gated on the data audit (REVISE — this one requires contract/schema work, not ratification).** Record the F.5 ruling shape as: "SPEC_POINT becomes a first-class node type via S3 canonical data-model work; interim: the data audit names what the anchors ride today, and that mapping is documented in the ADR that lands the migration." Explicitly NOT authorized to implement here (no schema work in this task). A curriculum/KG authority ruling for A is equally legitimate — the requirement is only that the carrier type becomes recorded canonical semantics rather than folklore.

**Acceptance criteria:** a written data-model sentence (ADR or schema review note) naming the canonical representation; if B/C: migration scope enumerated for S3, with the S2 V5 gap (anchor validation-state carriage) closed in the same pass; `question_spec_points` semantics documented against the named representation.

**Semantics classification:** curriculum semantics (what a SpecificationPoint is) + technical representation (enum/table); the ruling directs S3 and changes no behavior by itself.

#### J.6 Cross-checks (required review topics vs what the sources settle)

| Review topic | Settled by the canonical sources | Still open |
|---|---|---|
| Authoritative correctness incl. pending/ungraded + later corrections | D.1 evidence states (grading derived from the marking-state lifecycle; the `correct` placeholder must never be read as a grade); immutable-attempt law (invariant 5); S2 R1/V8 (the placeholder is real; graded lanes publish nothing) | Nothing at F-level — the derivation law is contract text awaiting S3 implementation; no educational ruling owed |
| Independent vs supported success | D.6 + classifier `:89-112` (exposure dominates; support → `SUPPORTED_SUCCESS`; `UNKNOWN` → `ATTEMPTED` fail-closed) | F.1 (past-support decay/window); the D.6 temporal ambiguity surfaced in J.4 |
| Assistance/exposure representation when missing or only partially observed | C.1 (`UNKNOWN` honest default; absence ≠ `NONE`), D.4 (missing/late/contradictory/malformed laws), B.1/B.6 (`REQUESTED` vs `SERVED`; partial/failed reveals record outcomes, never `SERVED`) | F.4 (exact submit-time exposure content + temporal reading); producer coverage itself (S2: `NO_PRODUCER_FOUND` ×3) |
| Evidence sufficient to claim transfer (distinct questions, SP overlap, delay, prior eligibility) | D.7 + classifier transfer gate `:123-148` (distinct question, SP overlap, strict chronology, trusted prior, explicit designation) | F.2 (prior eligibility), F.3 (delay value, distinctness depth), F.5 (representation) |
| Educational policy vs versioned experiment parameter vs technical detail | Base §Proposed semantics + F.3's own text (delay = experiment parameter); D.1–D.4 = technical laws; §F = the policy questions | The per-rule classification itself is what S1 ratifies — J.1–J.5 propose a classification each; the reviewers confirm or correct |

#### J.7 Status table and S1 checklist

| Decision | Status of record | Recommendation | Authority of record |
|---|---|---|---|
| F.1 | **UNRESOLVED** | PROPOSED: attempt-local now (ratify PoC); window machinery reserved (J.1) | None — no authorized reviewer decision exists (PR #23/#24 zero reviews; main @ `3e84070` zero F-markers) |
| F.2 | **UNRESOLVED** | PROPOSED: ratify the fail-closed "no" (J.2) | None — same evidence |
| F.3 | **UNRESOLVED** | PROPOSED: ratify structure, parameterize the value (J.3) | None — same evidence |
| F.4 | **UNRESOLVED** | PROPOSED: enumerated-per-surface exposure; temporal reading (b) with a recorded D.6 revision (J.4) | None — same evidence |
| F.5 | **UNRESOLVED** | PROPOSED: `SPEC_POINT` as first-class type via S3, gated on a data audit (J.5) | None — same evidence |
| ACCEPTED | — | — | **None.** No F.1–F.5 item carries an authorized decision of record as of 2026-10-19. |

**S1 checklist riders (from the proposal's own text, not new F-items):**
1. Gate S1's first clause — "This addendum reviewed" — means §B–§E themselves require the named reviewers' review; this preparation does not substitute for it.
2. B.7 requires the S1 review to **name the platform learner-data retention policy** for exposure events; §F names no reviewer role for it — the S1 chair must assign one from SyllabAI's governance roster (not invented here).
3. Every accepted decision that contradicts a PoC-encoded candidate is a recorded contract revision (§G/S1 law) and must be paired with the contract/classifier change it entails (S3/S4 scope) — never a silent override.

#### J.8 Operator-channel review intake (2026-10-19, post PR #25) — five PROPOSED recommendations — status unchanged

**Provenance.** Received via operator message (trace `1a15449eb2951bd1`, chat `1148fa2b`) after PR #25 publication (head `eaa52ab`). Recorded post-rollback from origin (the local clone was destroyed after publication; the pushed branch is the record of §J.0–J.7). The message carries its own decision-status table keeping F.1–F.5 **UNRESOLVED** — honored of record — and was delivered with external research citation metadata (PubMed) supporting the F.3 delay-threshold caution; recorded as provenance, neither endorsed nor adjudicated by this lane. Freshness re-check at intake: PR #23, #24, #25 all draft with **zero formal reviews** (re-verified first-hand post-rollback); no authorized reviewer decision exists. The five recommendations below are transcribed verbatim from the message (paste artifacts — favicon markup, a stray "+1" fragment — removed; wording otherwise untouched). This intake does not establish whether the operator channel holds any §F-named reviewer role; that attribution is for the reviewers and operator to record.

**F.1 — When is success independent?** PROPOSED.
Recommendation: require a new, unassisted attempt after exposure; waiting alone is insufficient.
- A hint was given: the assisted answer is `SUPPORTED_SUCCESS`, not independent success.
- The correct answer was revealed: repeating the same question later is not enough to prove independent performance.
- To earn `INDEPENDENT_SUCCESS`, require a subsequent correct response with no assistance and no answer exposure before or during that attempt.
- Prefer a genuinely different question when the aim is to establish capability beyond remembering the answer to a specific item.
Why: repeating a question after seeing its answer can measure memory for the answer rather than independent problem-solving. However, a new question is not automatically a transfer test; it must still be educationally aligned.
Trade-off: this is stricter than the prototype's attempt-local rule and requires a clear distinction between evidence of answering independently now and evidence of broader learning.

**F.2 — Can a past failure be the transfer baseline?** PROPOSED.
Recommendation: no — not as positive evidence of previously demonstrated competence.
An incorrect attempt can establish that the student attempted the skill and did not demonstrate correctness on that occasion. It should not count as a qualifying prior success when claiming later transfer.
A later correct answer on a new question may still be valid positive evidence. It should be classified according to what the student actually demonstrated, rather than treating the earlier failure as proof that a skill was previously mastered.
Important distinction: a past failure remains useful diagnostic evidence. Rejecting it as a successful transfer baseline does not mean discarding it from the learner's history.

**F.3 — What counts as real transfer?** PROPOSED.
Recommendation: require both meaningful item difference and a delayed, independent demonstration — but leave the exact time threshold for evidence-based evaluation.
A transfer claim should require:
1. A distinct question, not a reworded copy or merely shuffled answer choices.
2. A defensible relationship to the same canonical SpecificationPoint or intended skill, established through curriculum semantics rather than embedding similarity alone.
3. An independent, correct response with no disqualifying assistance or answer exposure.
4. A meaningful delay between the relevant learning/exposure event and the transfer assessment.
5. A qualifying prior success, if the intended policy defines transfer as evidence of carrying an already demonstrated skill into a new context.
Treat 24 hours and 7 days as possible evaluation conditions, not settled educational law. Research supports the importance of testing across different examples and contexts, but it does not establish a universal delay that proves transfer in every subject.
Trade-off: a rule that is too weak overclaims learning; one that is too strict can leave learners without sufficient opportunities to demonstrate it. S9 should evaluate candidate thresholds and item-distinctness criteria before numeric values become policy.

**F.4 — Does the result's answer count as exposure?** PROPOSED — needs explicit resolution.
Recommendation: distinguish answer exposure before submission from feedback delivered after submission.
- If the student sees the correct answer before submitting, the attempt is answer-exposed and should not qualify as independent success.
- If the system reveals the correct answer only after the response has been irrevocably submitted, that later feedback should not retroactively invalidate the response just submitted.
- The response must nevertheless record the answer-exposure event so that later attempts can be classified correctly.
- If the submit response contains the correct answer before the student can finalize their answer, it is exposure for that attempt.
Why this distinction matters: if every MCQ result includes the correct option only after submission, treating post-submit feedback as pre-submit exposure would make ordinary MCQ assessment unable to demonstrate independent correctness. Conversely, ignoring answers actually shown before submission would overstate independence.
The canonical wording reportedly contains a temporal ambiguity. This recommendation must therefore be treated as a proposed precision revision to D.6, not a silent reinterpretation of the existing text.

**F.5 — Where should SpecificationPoints live?** PROPOSED.
Recommendation: make SpecificationPoints first-class canonical curriculum entities, with an explicit persisted representation and stable identity.
They should not be represented merely as text labels, embeddings, inferred retrieval nodes, or an undocumented use of an unrelated node type. Assessment and learning evidence should refer to stable SpecificationPoint identities, preserving provenance and validation status.
Before changing the schema, require a data-path audit tracing real SpecificationPoints through: canonical graph-as-code assets; the loader and its type mapping; database constraints and persisted rows; API and Hub reads; assessment/evidence anchor references.
Then the curriculum/KG authority should decide the canonical representation and migration contract. A dedicated `SPEC_POINT` type is my preferred proposal, conditional on confirming the actual persisted representation and migration implications.
Trade-off: adding a first-class type may improve integrity and prevent ambiguous anchors, but a schema change without a verified migration and compatibility plan could break existing content and evidence references.

**Decision status as delivered (verbatim from the message):**

| Decision | Recommendation | Official status |
|---|---|---|
| F.1 | New unassisted attempt; prefer a distinct item for stronger evidence | `UNRESOLVED` |
| F.2 | Past failure cannot qualify as prior successful evidence | `UNRESOLVED` |
| F.3 | Distinct item + independent correctness + meaningful delay; thresholds evaluated | `UNRESOLVED` |
| F.4 | Distinguish pre-submit exposure from post-submit feedback; explicitly revise ambiguous wording | `UNRESOLVED` |
| F.5 | First-class canonical SpecificationPoint identity, after data-path audit | `UNRESOLVED` |

**Central principle, verbatim:** "SyllabAI must not confuse a correct answer, independent performance, and transfer of learning. They are different claims and need different evidence. The classifier can help encode an approved contract; it cannot decide that contract on behalf of the curriculum, assessment, or learner-model authorities."

**Cross-check against §J.1–J.5 and the PoC's encoded candidates (this lane's analysis, PROPOSED — adds no decision):**

| Decision | vs §J recommendation | vs PoC encoded candidate | Consequence if this position is ratified |
|---|---|---|---|
| F.1 | **DIVERGES.** J.1 proposed ratifying the attempt-local law now and reserving window/retake machinery; the review wants the stricter retake law recorded at S1 itself (same-question repeat after recorded exposure insufficient; a new unassisted attempt required; a distinct item preferred for capability claims). J.1's acceptance criteria already carried the retake-law shape as a deliverable, so the divergence is timing and finality, not shape. | Supersedes the attempt-local candidate for the same-question retake case — the encoded law has no question-identity memory (`verification-evidence.ts:89-104` @ `26d98da`). | Contract revision to §F.1/D.6; classifier change: per-learner, per-question exposure chronology (D.4 machinery) plus question-identity comparison; test pins updated; S3/S4 scope grows. Unexercisable either way until S4 producers exist (S2: zero assistance/exposure producers — every real attempt is `UNKNOWN` → `ATTEMPTED`). |
| F.2 | **ALIGNS** with J.2 (ratify the fail-closed "no"); adds the diagnostic-preservation note. | Matches the encoded prior gate (`:127-134`) and its test pin (`verification-evidence.test.ts:105`). | No classifier change; contract text records the eligibility law. |
| F.3 | **ALIGNS** with J.3 (structure ratified, value parameterized). The five conditions map onto the encoded transfer gate (`:126` distinct question; `:135-138` SP overlap + chronology; `:127-134` trusted prior; `:43-49` versioned delay). "24 hours and 7 days as possible evaluation conditions, not settled educational law" restates the versioned-parameter law. | Matches; additionally pins curriculum semantics — not embedding similarity — as the source of the SP relationship (the invariant law). | No structural change; S9 evaluation design for candidate thresholds and item-distinctness criteria. |
| F.4 | **ALIGNS** with J.4: temporal reading (b) — post-submit feedback does not retroactively invalidate its own attempt — plus a recorded D.6 precision revision, which the review states explicitly ("not a silent reinterpretation"). Adds the pre-finalization case as exposure for that attempt. | Matches the encoded field semantics ("exposed **before** this attempt", `:35-36`); the pre-finalization case is B.3's own law (exposure event under exactly the condition that makes the field non-null). | D.6 one-sentence precision revision recorded (required either way per J.4); B.3 producer design unchanged. |
| F.5 | **ALIGNS** with J.5 (first-class `SPEC_POINT` preferred, gated on a data audit); the review specifies the full audit chain (graph-as-code → loader/type mapping → DB constraints/rows → API/Hub reads → anchor references) and the migration-contract caution — a richer scope than J.5's "first input" framing. | Not encoded (representation debt, not classifier logic). | Data-path audit first (F.5 review's first input per J.5); curriculum/KG authority decides representation and migration contract; schema work is S3 scope, outside this record's authority. |

**Status after intake (2026-10-19): unchanged.** F.1–F.5 remain **UNRESOLVED**; **ACCEPTED: none**. The record now carries two PROPOSED positions per decision — the §J.1–J.5 lane recommendations and this §J.8 operator-channel review — **converged on F.2, F.3, F.4, F.5** and **divergent on F.1** (attempt-local-now vs a stricter retake law recorded at S1). The divergence is a governance-timing and finality choice that belongs to the §F-named reviewers; both positions stand before them. Neither position is policy until a named reviewer records a decision of their own; a ratified F.1 of the reviewed shape is a recorded contract revision with the classifier/S3/S4 consequences listed above (§G/S1 law), never a silent override.

**Stop state:** S1 prepared for human adjudication — F.1–F.5 UNRESOLVED, recommendations PROPOSED, no decision made or implied by this lane. S3 has not been started.
