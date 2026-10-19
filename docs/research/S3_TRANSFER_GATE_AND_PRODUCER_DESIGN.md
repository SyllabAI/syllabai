# Gate S3 — Transfer-Gate Design Consolidation (F.3 + S9 preregistration shape) and Producer Design for the NO_PRODUCER_FOUND families (S4 input)

## Provenance

| Field | Value |
|---|---|
| Ordered by | Operator "continue S3" (trace `1a1557fcdb6d091d`, chat `1148fa2b`, 2026-10-19), continuing the S3 order (trace `1a1553a3531f7da1`) |
| Policy inputs | §J.9 F.3 ruling of record (`bb778ee`); D.7 (transfer supply and validation); §G S9 definition; §J.3 option-B acceptance criteria; G1 exposure contract (B.1–B.7) and G3 assistance contract (C.1–C.5); S2 producer inventory R4/R5/R6 negatives + V1/V2/V3/V6/V7 + R7/R8 partials (`8c32913`); classifier redesign of record (`0e85cf5` — Gate 2, chronology contract §4, identity law §5, DP-1..4/PF-1/PF-2) |
| Cited v2 head | `syllabai-v2` origin/main @ `3a05332c5370b84e24f20bf9ffbbaf371f701c56`, fetched first-hand this round. Delta `acf3ddb..3a05332` = Hub books/corpus-pdf only (4 files); **`verification-evidence.ts` byte-identical** — every published citation holds |
| Drift findings of record | (1) the CLA context-kind union now includes **`SPECIFICATION_POINT`** (`context-resolver.ts:23,461-494`; `context.ts:21`) — absent from the S2 record; (2) **`tutor_sessions` + `tutor_session_turns` tables now exist** — S2 R4.4's "zero conversation persistence" is materially outdated at the session-turn metadata level, though turns still carry no question/attempt linkage and no served-content record (verified shape below) |
| Status | **PROPOSED design of record — decides nothing, implements nothing.** Docs-only; the classifier stays PROTOTYPE per S2's law; no producer, schema, or policy change is authorized by this document. Authorities own the DP items (§10) |

**Sandbox-rollback disclosure:** the sandbox was recycled for the **fourth** time at round start (`syllabai-canonical`, `.creds`, and the `download/s3-design/` insurance patches destroyed locally). No work was lost — `s3-design` @ `0e85cf5` was already on origin (pushed last round, first-hand re-verified); the clone was re-cut from origin and the insurance patches re-generated from the of-record PAT delivery (fp16 `a8ccee736aa8c75b`).

---

# Part I — The transfer gate, consolidated (F.3)

## §1 Executive verdict

`TRANSFER_SUCCESS` is currently **unreachable by design, and that is the honest state**: the encoded gate (`verification-evidence.ts:123-142`) is structurally what F.3 ratified, but three of its inputs have no producers (S2 R4/R5/R6 — re-verified negative at `3a05332` by repo-wide grep: only the classifier and its test mention `isTransferAssessment`/`ANSWER_EXPOSURE`/`ASSISTANCE_SERVED`), the delay parameter has no chosen value of record, and the S9 evaluation that promotion requires has no preregistration. Part I consolidates the complete gate law with each condition traced to its ruling, its encoded line, and the producer that must supply it (Part II); Part II designs those producers. The two parts are one dependency chain: **the gate is runnable exactly when P1–P3 land and the authority records a delay value.**

## §2 The consolidated gate law — eight conditions, one chain

`TRANSFER_SUCCESS` requires ALL of (evaluation order = code order `:123-142`; reason codes surface the first failing condition):

| # | Condition | Ruling / contract | Encoded | Supplied by | Current state |
|---|---|---|---|---|---|
| C1 | Current attempt authoritatively correct | D.1 marking-state lifecycle | `:81-87` (NOT_YET_GRADED/INCORRECT) | grading producer (R1) | MCQ real; graded lanes noop (V4 — open, S2 §7.4) |
| C2 | Current attempt independent | D.6-revised + F.1(b) | Gate 1 `:89-112` + Gate 2 (chronology, classifier doc §3) | P1 + P2 via the chronology | Gate 2 inert (chronology empty by construction) |
| C3 | Explicit transfer designation | D.7 bullet 1; F.3 | `:123` (`isTransferAssessment`) | **P3** (§9) | No surface exists (R6, re-verified) |
| C4 | Distinct canonical question id | F.3 "genuinely different question" | `:126` | identity law (classifier doc §5) | Checkable as identity inequality only — ceiling of record |
| C5 | Qualifying prior success | F.2 + F.3; F.1(b)×F.3 composition | `:131-134` (+ DP-2) | P1/P2 for the prior's own gates | Law decided; inputs unpopulatable |
| C6 | Canonical SpecificationPoint overlap | F.3; D.3 | `:132,138` | `question_spec_points` (R3) | Exists (7,351 rows); "canonical" checkability blocked on F.5 §7 authority review |
| C7 | Strict prior chronology | D.7 bullet 3 | `:136` | attempts instants | Law holds |
| C8 | Minimum delay | F.3; D.7 bullet 2 | `:43-49` + `:137` | **authority-recorded value** (§3) | No value of record → cannot fire |

**The design changes no condition.** It names the missing suppliers and the state each must reach.

## §3 The delay parameter — governance home and of-record state

Per §J.3 option B (ratified by the F.3 ruling's "not fixed policy thresholds") and D.7 bullet 2:

1. **Named parameter, named owner:** `minimumTransferDelayMs`, owned by the learner-model owner (the §J.3 acceptance-criteria assignment).
2. **Versioning home (DP-5):** v2 already carries a first-class experiment entity — `experiments` (`experiment_key` unique, `name`, `hypothesis`, `status` DRAFT/RUNNING/PAUSED/COMPLETED/ARCHIVED, `params` jsonb; verified shape at `3a05332`). The design proposes the S9 delay arms live there as experiment rows (`experiment_key` e.g. `transfer-delay-s9`), with the chosen pre-experiment value (if any) recorded as an experiment param — **PROPOSED for the learner-model owner; the classifier itself stays parameter-agnostic** (it takes `VerificationPolicy` as an argument, `:43-49`).
3. **State of record until then: transfer disabled.** The §J.3 acceptance criteria explicitly admit "an explicit 'transfer disabled until a value is chosen' state" — that is the current state and this design records it: with no value of record, C8 cannot pass and `TRANSFER_SUCCESS` cannot fire in any environment. Fail-closed, honest, and reversible only by a recorded authority decision.
4. **No numeric default is invented here** (D.7 bullet 2 verbatim law).

## §4 S9 preregistration shape (what the frozen evaluation must fix before it runs)

Per §G S9 ("a frozen held-out evaluation measures false-positive rates for independent and transfer success … a green test suite alone never establishes educational correctness"), §J.1's acceptance criteria (S9 false-positive plan for the retake rule), and §J.3's (transfer FP metric under the chosen value):

1. **Prerequisite:** S4 producers P1–P3 landed and publishing (Part II) — the evaluation is unrunnable over an empty chronology; the dependency is stated, not assumed.
2. **Frozen held-out set:** attempts with producer-complete chronology coverage, fixed and versioned before any arm runs; set-construction rule recorded (inclusion/exclusion per D.1 states — quarantined/INVALID/SUPPRESSED excluded; coverage rate disclosed).
3. **Arms (per the F.3 ruling verbatim):** delay = **24 hours** and delay = **7 days** as candidate values — evaluated, never pre-adopted. A no-delay arm is not admitted (F.3 requires "a delayed assessment").
4. **Metrics, operationally defined without inventing psychology:**
   - *Independence false positives:* attempts whose constructed chronology contains a same-question recorded exposure before the attempt instant (Gate 2's blocking condition, known by construction) yet the classifier labels `INDEPENDENT_SUCCESS` — zero is the only passing rate.
   - *Transfer false positives:* transfer-designated attempts whose C1–C8 inputs are defective **by construction** (defective prior per F.2/DP-2, distinctness violation, delay-arm violation, anchor mismatch) yet the classifier labels `TRANSFER_SUCCESS`.
   - *Health metrics:* chronology coverage rate per learner/question; quarantine rate (D.4); none-assertion coverage rate (§7) — disclosed alongside the FP rates, since a gate over empty chronology trivially "passes".
5. **Preregistration discipline:** set, arms, metrics, and analysis are frozen and recorded before the first run; results land as an evaluation record against the `experiments` row (DP-5); promotion gate 4 per §G S9.

## §5 What Part I does not do

No classifier change (all eight conditions already encoded); no value chosen for the delay; no experiment executed; no designation surface created (Part II designs it); no claim that C1's graded-lane gap (V4) is closed — it remains the authority's open S2 §7.4 decision, orthogonal to P1–P3.

---

# Part II — Producer design for the three NO_PRODUCER_FOUND families (S4 input)

## §6 Common producer law (all three families)

The negatives of record are re-verified and stable: repo-wide grep at `3a05332` finds zero emission sites for exposure/assistance/transfer events in application code — only the classifier and its test reference the vocabulary. The S2-cited surfaces are line-stable at `3a05332` (spot-verified this round: `engagement-recorder.ts:166,198` fire-and-forget sinks; `model-update.ts:234` `clock.newId()` fresh-per-insert; `tutor/context.ts:199` the "Encourage transfer" prompt nudge; `ck_tte_signal`'s six intent values; GET mark-scheme reveal at `routes/questions/index.ts:150` → `services/questions/reveal.ts:100` `reveal()` — no row written, 200/204 indistinguishable in the data model).

Every producer below obeys the shared contract (closing V6/V7 for these families):

- **Event fields (D.2/B.2/C.3):** unique event id (idempotency key — retries dedupe, never `clock.newId()` per insert); learner id; attempt linkage (direct `attemptId`, or declared-rule linkage per C.4, or explicitly absent); canonical question id; **producer identity** (the emitting component, not the surface constant); event schema version; server-side **delivery** instant (C.5 — async pipelines stamp delivery, disclosed skew otherwise); declared ordering key where the producer has one.
- **Natural keys (B.5/C.5):** exposure — `(attempt_id, exposure_type)`, first commit wins; assistance — `(attempt_id, assistance_type)` for attempt-scoped serving events.
- **Grounding discipline:** only `SERVED` grounds (B.1); only application-controlled producers are authoritative (C.2/invariant 3) — no LLM self-report, no client assertion, no timing/proximity inference; negatives are asserted only by an explicit producer record (C.1's none assertion), never inferred from silence.
- **Lifecycle (D.4):** late events land as linked corrections — persisted labels are never retroactively rewritten; malformed events quarantine, excluded-but-retained; contradictory provenance voids to the conservative label as a first-class audit fact.
- **Substrate (DP-3, carried):** `telemetry_events` type-extension vs a dedicated evidence-events table — this design constrains both shapes and mandates neither; the `ck_telemetry_type` check (14 values, verified) admits neither `ANSWER_EXPOSURE_*` nor `ASSISTANCE_SERVED` today.
- **Retention (B.7, DP-6):** events carry resource identities and metadata, never content blobs; learner-personal; the concrete retention policy naming is an authority deliverable.

## §7 P1 — Exposure producer (closes V2; feeds the chronology = Gate 2 and C2)

**Surfaces of record (three, all verified):**

1. **Submit response** — `services/assessment/submit.ts:279,286`: `correctOptionLabel` computed at `:279`, returned at `:286`. Emission law (B.3): an `ANSWER_EXPOSURE_SERVED` event of type `SUBMIT_RESPONSE_CORRECT_OPTION` under **exactly** the condition that makes the field non-null, same attempt, same delivery; `linkedAttemptId` = the attempt; **phase = `POST_SUBMIT`** (the label rides the response to irrevocable submission — this is F.4's "shown only after submission is feedback"; the D.6-revised pre-finalization case is a different surface shape and does not arise on this path as written).
2. **Attempt history re-reveal** — `services/assessment/history.ts:249`: same event type, `linkedAttemptId` = the historical attempt, phase `POST_SUBMIT`; the B.5 natural key collapses repeated views of the same attempt's answer into one recorded exposure (the chronology needs existence, not multiplicity).
3. **Mark-scheme reveal** — `routes/questions/index.ts:150` → `services/questions/reveal.ts:100`: requires **B.4 identity injection first** (today only the question id crosses the boundary — the producer contract carries learner identity from the authenticated session and attempt id when the caller holds one, with the content-selection law unchanged); `type = MARK_SCHEME_REVEAL`; a 200 serve emits `SERVED`; a 204/404/failure emits `ANSWER_EXPOSURE_REQUESTED` with outcome `WITHHELD`/`FAILED`/`PARTIAL` (B.6) and never `SERVED`; phase `POST_SUBMIT` when attempt-linked, else `linkedAttemptId` absent and the chronology rules resolve (B.4/D.4 — never by assumption).

`REQUESTED` events are emitted on endpoint invocation for both kinds (B.1) — intent evidence, never grounding. **Unblocks:** the classifier-doc chronology (§4) in full, Gate 2 observability, and C2's exposure half. The `correctOptionLabel` field semantics and response shape stay untouched (B.3's law adds an event, not a behavior change).

## §8 P2 — Assistance producer (closes V1; feeds Gate 1 and the NONE assertion)

**The hard problem of record (S2 R4.7):** with fire-and-forget recording (verified sinks `engagement-recorder.ts:166,198`), absence of a recorded hint is unprovable either way — nothing can authoritatively assert `NONE`, so every attempt is `UNKNOWN` → `ATTEMPTED` (the fail-closed behavior is correct under this substrate). The producer design has two halves:

1. **Serving events (C.4 pathway):** where the tutor/CLA serves a hint, worked solution, or step-by-step guidance **in a question context**, the serving pipeline emits an attempt-level `ASSISTANCE_SERVED` event at **delivery time** (C.5): the server-resolved context kind + reference and the response mode are copied onto the event. The context-kind union has grown since S2 — it now includes `SPECIFICATION_POINT` (`context-resolver.ts:23,461-494`), so the event contract must carry all four kinds (`KG_TOPIC`, `SPECIFICATION_POINT`, `PAST_PAPER_QUESTION`, `QUESTION_PART`) with the question resolved for `QUESTION_PART` via the existing `questionIdByPartId` (`cla/service.ts:273,492`). Linkage: `PAST_PAPER_QUESTION`/`QUESTION_PART` link direct; topic/spec-point contexts record learner + question-when-resolvable + timestamp and resolve under D.4 — never by semantic-similarity inference (C.4 verbatim law). `tutor_session_turns` (new since S2; shape verified: `sessionId`, `seq`, `role`, `evidenceCount`, `refused`, `answerModel/Provider` — **no question id, no attempt id, no served-content or response-mode record**) is correlation scaffolding, not a grounding source; topic-level engagement stays telemetry (C.3's promotion ban).
2. **The per-attempt none assertion (C.1):** assembled at attempt finalization by an application producer that queries the attempt-scoped assistance event set (attempt-linked events plus declared-rule-linked ones) between attempt-open and submit instants, and emits an explicit assistance record: the resulting level, or a **none assertion** when the set is empty *and* every serving surface in scope is instrumented. The assertion's validity is **conditional on instrumentation coverage** — until coverage is complete, the honest value stays `UNKNOWN`. **DP-7:** the educational-policy authority must certify surface coverage before none assertions may ground `INDEPENDENT_SUCCESS` at scale; the classifier needs no change (it already fails closed on `UNKNOWN`).
3. **Teacher support (`TEACHER_SUPPORT`):** grounded by the marking/feedback linkage (C.1 table) — which today publishes nothing (V4); P2 consumes marking linkage when the graded-lane publisher decision (S2 §7.4) lands, and until then `TEACHER_SUPPORT` stays unassertable (fail-closed).

## §9 P3 — Transfer-designation producer (closes V3; feeds C3)

D.7 bullet 1: "an explicit transfer designation supplied by an application producer (assessment/quiz metadata). No transfer designation exists anywhere in v2 today; it must be created by a reviewed producer, never inferred." Re-verified: the only "transfer" text in application source is the tutor prompt nudge (`tutor/context.ts:199` — a recommendation, **not** a designation; the vocabulary collision is recorded so no future audit mistakes one for the other). The schema inventory at `3a05332` (all 60+ tables enumerated) contains no assessment/quiz entity beyond `exam_papers` / `assignments` / the attempt pipeline itself.

**Design:** the designation is first-class, application-controlled metadata on the **assessment entity** — proposed home: `exam_papers` (it already carries identity, provenance, and validation-state patterns; an attempt's paper is reachable via `questions.examPaperId`), with `assignments` as the alternative if the authority prefers. Contract:

- Explicit `transfer_designation` boolean (never null, never inferred), plus `designated_by` (producer identity), `designated_at`, `designation_version`, and optional pre-declared target SPs;
- Set **at authoring time** by the assessment owner; never at runtime, never by LLM or learner input (invariant 3);
- Read at event time onto the attempt's evidence record (D.3 discipline) — the classifier's `isTransferAssessment` consumes only this;
- Interaction with S9: designation-gated cohorts are the experiment's enrollment mechanism (§4.2), which is why the designation must exist **before** the evaluation can run.

## §10 Open decision points (cumulative for the authorities)

Carried: **DP-1** (Gate-2 rung), **DP-2** (defeated-prior composition), **DP-3** (chronology substrate), **DP-4** (question-rewrite identity discipline), **PF-1** (support-assisted transfer priors), **PF-2** (past-support retake extension). New this document: **DP-5** — the delay-parameter and S9-arm versioning home (proposed: the `experiments` entity, §3.2); **DP-6** — retention policy naming per B.7; **DP-7** — instrumentation-coverage certification for none assertions (§8.2); **DP-8** — P3's designation home (proposed: `exam_papers`, §9).

## §11 S4 implementation order (dependency-true; nothing executes before authority review)

1. Event substrate per DP-3 + idempotency/ordering/quarantine primitives (V6) — everything depends on this;
2. **P1** exposure on all three surfaces + B.4 identity injection → chronology live → Gate 2 observable, C2 complete;
3. **P2** assistance (C.4 serving events + none assertion) → Gate 1 inputs real, `UNKNOWN`→`NONE` becomes assertable where coverage allows;
4. **P3** designation per DP-8 → C3 real, transfer gate runnable;
5. Classifier wiring: intake + chronology assembly + the ten pins (classifier doc §7);
6. Graded-lane publication decision (S2 §7.4, V4) — orthogonal, authority-owned;
7. S9 preregistration freeze (§4) → arms → evaluation record → promotion gate 4.

## §12 Stop state (S3, 2026-10-19)

All three S3 design deliverables are now of record: the F.5 data-path audit (`e263a81`), the classifier redesign (`0e85cf5`), and this document's transfer-gate consolidation + producer designs. S3's design scope is **complete**; what remains is authority review (F.5 §7 migration contract; DP-1..8; PF-1/2) and S4 implementation in the §11 order. No code, schema, seed, or policy text changed by this lane; the classifier stays PROTOTYPE; no DB was accessed this round; BKT/BDT and `masteryMutation: "NONE"` untouched.
