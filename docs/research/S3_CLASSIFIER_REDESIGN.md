# Gate S3 — Verification-Evidence Classifier Redesign (the F.1(b) retake law; F.2/F.4 semantics; chronology + test-pin design)

## Provenance

| Field | Value |
|---|---|
| Ordered by | Operator "Proceed" (trace `1a15566f177d24d9`, chat `1148fa2b`, 2026-10-19), continuing the S3 order (trace `1a1553a3531f7da1`) |
| Policy inputs | §J.9 rulings of record (`bb778ee`, operator trace `1a154694538f9511`); D.6 precision revision (same commit); §D event-lifecycle law (D.1/D.2/D.4); S2 §7 twelve prerequisites (`8c32913`); F.5 data-path audit of record (`e263a81`, PR #26) |
| Cited v2 head | `syllabai-v2` origin/main @ `acf3ddb23a7a27a3faf1be7b13cbca0e3415cbc7`, fetched first-hand this round. Delta `89962a5..acf3ddb` = `.syllabai` receipts/tasks/worklog only (6 files) — **app code unchanged; `verification-evidence.ts` byte-identical (158 lines)**; every line citation below re-verified at this head |
| Status | **PROPOSED design of record — decides nothing, implements nothing.** Docs-only; the classifier remains PROTOTYPE per gate S2's law until S4 producers land; nothing here executes before curriculum/KG + educational-policy authority review. Per §G/S1's law every departure from an encoded candidate below is a recorded contract revision, never a silent override |

**Path corrections of record (first-hand @ `acf3ddb`):** the B.3 surfaces moved since the S2 citation — now `apps/api/src/services/assessment/submit.ts` (was `src/routes/`) and `services/assessment/history.ts`; line numbers stable (`submit.ts:279,286`; `history.ts:249`). The F.2 test pin lives at `apps/api/test/learner/verification-evidence.test.ts:105` (S2/§J.2 cited the basename without the `learner/` directory; line matches exactly).

---

## §1 Executive verdict

**F.1(b) is implementable, but not with today's input.** The encoded law evaluates exposure **attempt-locally**: `answerExposedBeforeAttempt` is a caller-supplied boolean on the attempt itself (`verification-evidence.ts:35-36`, consumed at `:89`), and the transfer gate excludes only the literal same `questionId` (`:126`). Under that law, exposure recorded on attempt N of question Q constrains nothing about attempt N+1 of Q — the caller simply passes `false` again. That is precisely the hole ruling F.1(b) closes: *"Once a student has seen the answer to a question, retaking that same question cannot establish independent success."*

The redesign adds exactly one new input — a **per-learner, per-question exposure chronology** assembled by a specified derivation law (§4) — and one new gate (§3, Gate 2). It deliberately changes nothing else: the F.2 prior gate is already the decided law (§6.1, zero classifier change), F.4's reading (b) field semantics are already the law (§6.2, zero classifier change), the ladder's four rungs, the fail-closed defaults, and `masteryMutation: "NONE"` (`:55/:85/:93` and throughout) all stand untouched.

**Substrate reality (first-hand, disclosed):** `attempts` (`schema.ts:205-268`) carries **no** exposure/assistance columns and **only one instant** (`createdAt`); `telemetry_events` (`schema.ts:133-150`) carries **no** exposure/assistance event types (its check admits 14 types, none of them `ANSWER_EXPOSURE_SERVED`/`ASSISTANCE_SERVED`), no attempt-linkage column, no producer-identity column, and no idempotency key beyond the row PK. The classifier has **zero production call sites** (verified by grep at `acf3ddb`). Consequence: the chronology is empty by construction today and Gate 2 is inert until S4 builds the producers; what this design delivers is the **contract S4 implements** — event shapes, the derivation law, the gate ordering, and the test pins — sized against S2 §7's twelve prerequisites (§9).

## §2 The superseded law and the exact delta

**What is superseded (of record, §J.9 disposition):** the attempt-local law `:89-104` is superseded **for same-question retakes after recorded exposure**. Nothing wider. In particular:

- **Unchanged — this attempt's own inputs.** Assistance gates (`:97-104`: support → `SUPPORTED_SUCCESS`; `UNKNOWN` → `ATTEMPTED` fail-closed, `:106-112`) and the attempt-local exposure gate (`:89-95`) remain the law for what happened *inside the attempt's own session*, per F.4/D.6-revised.
- **Unchanged — the transfer gate's decided structure.** Distinct question (`:126`), strict prior chronology + delay (`:135-138`), versioned delay parameter (`:43-49`), SP overlap — F.3 ratified these as-is.
- **Unchanged — the ladder and both invariants.** Four rungs; classification never writes mastery.

**The delta:** a second, *history-scoped* exposure gate that no caller assertion can bypass, plus the chronology contract that feeds it. The supersession is recorded, not silent: the F.1(b) contract revision was entered of record in §J.9 at `bb778ee` before any code moves (none has moved — verified above).

**One tension surfaced, not resolved here (PF-1):** the current prior gate (`:131-134`) rejects incorrect, ungraded, exposed, and `UNKNOWN`-assistance priors — but **admits HINT/STEP_BY_STEP/TEACHER_SUPPORT-assisted correct priors** as transfer baselines (only exposure and `UNKNOWN` are checked). The §J.9 F.3 ruling requires transfer "supported by **qualifying** prior success"; whether support-assisted priors *qualify* was not decided by any ruling. Per the no-silent-reinterpretation law this design **does not change** the encoded behavior and flags it for the educational-policy authority as open item PF-1.

## §3 Redesigned law — Gate 2 (the retake gate)

**New input (per attempt):**

```ts
interface ExposureChronologyEntry {
  exposureId: string;        // event id — the idempotency key of record (D.2)
  questionId: string;        // canonical question identity (§5)
  occurredAt: string;        // server-side instant (D.2); ISO-8601 parseable, else excluded per D.4
  phase: "PRE_SUBMIT" | "POST_SUBMIT";   // derived by the §4 law, never caller-asserted
  linkedAttemptId: string | null;        // set when the exposure rode a submit response (B.3/B.4) or history re-reveal
}
```

The classifier signature gains `exposureChronology: readonly ExposureChronologyEntry[]` (entries already scoped to the same learner; assembly is the caller's duty under §4's law). **Gate ordering:** Gate 1 (existing attempt-local gates, `:89-112`, unchanged) → **Gate 2 (new)** → transfer gate (`:123-138` unchanged except the prior-side composition below).

**Gate 2 law.** Let `B` be the current attempt, `tB` its classification instant = `attempts.createdAt` (the only server-authoritative instant in the substrate; disclosed). A chronology entry `E` **blocks** `B` iff all hold:

1. `E.questionId` resolves to the **same canonical question identity** as `B.questionId` (§5 — version changes do not escape);
2. `E.occurredAt <= tB` (conservative at ties; D.2 declared ordering key breaks equal instants when the producer supplied one);
3. **NOT** (`E.linkedAttemptId === B.attemptId` **AND** `E.phase === "POST_SUBMIT"`) — the F.4 exemption: B's own post-submission reveal is feedback, does not invalidate B, and is exempt for B only;
4. `E` is well-formed and not quarantined/INVALID/SUPPRESSED (D.1/D.4 — excluded events cannot block; the residual is stated in §4).

If any entry blocks B and B's own-session inputs were clean (Gate 1 passed), the correct response lands as **`SUPPORTED_SUCCESS`** with reason code **`RETAKE_AFTER_RECORDED_EXPOSURE`**. Rung rationale: D.6-revised says any other correct attempt is `ATTEMPTED` or `SUPPORTED_SUCCESS`; the exposure-dominates precedent (`:89-92`) maps defeated independence to `SUPPORTED_SUCCESS`; `ATTEMPTED` would erase a true success signal. The rung assignment is a **PROPOSED decision point (DP-1)** — the rulings deny independence but do not name the rung.

**Gate 2 also precedes the transfer gate.** A transfer-tagged attempt on an exposed question is blocked a fortiori (transfer is the stronger claim).

**Prior-side composition (F.1(b)×F.3).** A prior attempt whose independence was defeated by Gate 2 **does not qualify** as prior success for transfer: F.1(b) defines what cannot be independent success; F.3's "qualifying prior success" inherits that definition — otherwise the transfer gate launders the exposure the retake gate exists to catch. This composition is decided-policy arithmetic, recorded as **PROPOSED for authority confirmation (DP-2)** because the rulings do not spell it out. Observable behavior when it fires: `INDEPENDENT_SUCCESS` + `TRANSFER_GATE_NOT_MET` (existing codes; the classifier's reason-code surface stays minimal — detail belongs in audit events).

**Explicitly out of F.1(b)'s scope (recorded edges):**
- *Past assistance (HINT/STEP_BY_STEP/TEACHER_SUPPORT) on the same question does NOT trigger Gate 2* — the ruling's letter is "seen the answer to a question". Whether past support should also block a retake is open item **PF-2** (conservative extension available to the authority; not enacted here).
- *Exposure on a different question does not block* — pin 5 (§7). The ruling's "ideally on a different item" is advisory preference, encoded nowhere as a gate.

## §4 The chronology intake — event contract and derivation law

**Events of record** (consumed by the chronology): `ANSWER_EXPOSURE_SERVED` per B.1 — **`SERVED` only grounds; `REQUESTED` never enters** — plus assistance events at level `ANSWER_EXPOSED` (C.2), which are answer exposure by another surface and block identically. HINT/STEP_BY_STEP/TEACHER_SUPPORT assistance events do not enter the chronology (§3 edge PF-2).

**Substrate and required contract (discharges S2 §7 items 1–2, 7–9 at the design level):**

| Requirement | Law | Substrate fact @ `acf3ddb` |
|---|---|---|
| Event identity + idempotency | unique event id; duplicate delivery = no-op (D.2); natural key `(attempt_id, exposure_type)` for attempt-linked events per B.5 — repeated history re-reveals of the same attempt's answer collapse to one recorded exposure (the gate needs existence, not multiplicity) | `telemetry_events.id` is a PK but nothing enforces dedupe; S2 V7 stands |
| Payload law | every grounding event carries `attemptId` (nullable for non-submit surfaces), `producerIdentity`, `schemaVersion`, `questionId` (§5 identity), `phase` inputs | `payload` jsonb exists but is unstructured; `schemaVersion` column exists (`:137`); S2 §7.2 |
| New event types | `ANSWER_EXPOSURE_SERVED` + `ASSISTANCE_SERVED` added to `ck_telemetry_type` (or a dedicated evidence-events table per S2 §7.1 — **DP-3, authority decision**; this design constrains both shapes, mandates neither) | check constraint admits 14 types, neither present |
| Attempt linkage | `linkedAttemptId` resolved server-side at emission; conversational surfaces follow C.4's pathway | no linkage column today |
| Instants | `occurredAt` server-side (D.2). Attempt classification instant = `attempts.createdAt`. **Marking-instant vs attempt-instant:** grading later than submission never moves `tB`; a late-corrected grade flows through the marking-state lifecycle (D.1), not the chronology | only `createdAt` exists on `attempts` |
| Phase derivation | `POST_SUBMIT` iff served under exactly the condition that made the submit response non-null (B.3's law, `submit.ts:279,286`) or re-served from attempt history (`history.ts:249`); `PRE_SUBMIT` iff served in-session before irrevocable finalization or from any non-submit surface. Derived from the emission site, never asserted by callers | surfaces verified; both currently unrecorded (S2 R5) |
| Late events | land as linked correction events; a persisted label is not retroactively rewritten (D.4); the landed correction enters the chronology for **every later** attempt | D.4 law |
| Quarantine | malformed/unparseable events are quarantined and **do not block** (D.1/D.4) — the classifier reads only well-formed history. **Residual, disclosed:** until S4 makes exposure emission durable, absence of records proves nothing; the retake gate is exactly as trustworthy as the producers behind it (and is inert today) | S2 R4/R5 |
| Contradiction | caller-asserted `answerExposedBeforeAttempt=false` while a `PRE_SUBMIT`-phase event linked to the same attempt exists → recorded as a first-class audit contradiction; the attempt's independence claim voids to the conservative label (D.4) | new pin 4 (§7) |

## §5 Question identity law (F.1(b) same-question / F.3 distinctness)

**Canonical identity = `questions.id`.** Verified at `acf3ddb`: no variant/family fields exist anywhere in the question data model (S2's finding, re-confirmed); `question_versions` rows are content revisions **of the same identity** (`question_versions.questionId` → `questions.id`).

- **Retake law reads identity, not version:** a retake after a content revision is still a retake. Edge disclosed: a substantively rewritten question (new expected answer) is over-blocked by identity-law; resolution proposal — substantive rewrites mint a **new question row** (identity discipline: never mutate a served question in place, the same never-rewrite-in-place shape the F.5 audit §7 adopted for node rows). Flagged as **DP-4**.
- **F.3 distinctness = different canonical `questionId`** (current `:126`, unchanged). **Ceiling of record:** with no variant/family data model, "genuinely different question" is checkable only as identity inequality; two near-identical stems mapping to the same SP pass as distinct today. Lifting that ceiling needs a question-relationship substrate (S4/S9 scope; S9's 24h/7d delay experiment is the natural evaluation vehicle).

## §6 F.2 and F.4 — the no-change changes

**6.1 F.2 (prior-evidence eligibility): zero classifier change.** The encoded prior gate (`:131-134` — `correct !== true` `:131`, empty anchors `:132`, exposed `:133`, and `UNKNOWN` priors `:134` all rejected) **is** the decided law; the executable form is test pin "an incorrect, exposed, or provenance-unknown prior can never ground transfer" (`apps/api/test/learner/verification-evidence.test.ts:105`, verified at `acf3ddb`). Past failures remain diagnostic evidence in the learner's history (BKT/BDT untouched). The only prior-side change in this design is the Gate-2 composition (§3, DP-2).

**6.2 F.4 (submit-time reveal): zero classifier change.** The field's semantics — "exposed **before** this attempt" (`:35-36`) — are ratified reading (b) of record: the attempt's own post-finalization reveal does not block its own independence, while the recorded B.3 event feeds later attempts. D.6's revised text (`bb778ee`) is the contract; the event-layer realization is §4's phase law. The chronology is where F.4's "feeds later attempts" becomes mechanical.

## §7 Test pins (S4 implementation scope; the design names the executable forms)

1. **Retake gate core:** exposure on Q at t0; fresh unassisted, own-session-clean correct attempt on Q at t1 > t0 → `SUPPORTED_SUCCESS` / `RETAKE_AFTER_RECORDED_EXPOSURE`, never `INDEPENDENT_SUCCESS`.
2. **F.4 exemption:** B's own post-submit reveal (linked, `POST_SUBMIT`) does not block B; the same event blocks every later attempt on Q.
3. **Pre-finalization phase:** reveal served before irrevocable finalization, linked to B → B is `SUPPORTED_SUCCESS` via the existing attempt-local gate (law preserved, now chronology-corroborated).
4. **Chronology beats assertion:** caller passes `answerExposedBeforeAttempt=false`; chronology carries a recorded exposure on Q before the attempt → not independent. (Same-attempt contradiction → D.4 conservative void + audit event.)
5. **Distinct-question non-blocking:** exposure on Q1; clean attempt on Q2 → Gate 2 silent; independence possible.
6. **Transfer composition:** prior "success" on SP X that is itself a Gate-2-defeated retake → transfer not grounded → `INDEPENDENT_SUCCESS` + `TRANSFER_GATE_NOT_MET`.
7. **Backward compatibility:** empty chronology ⇒ behavior byte-identical to the current classifier (the gate is inert, not absent).
8. **Existing pins unchanged:** F.2 prior pin (`:105`), assistance fail-closed pins, duplicate-prior/reordering determinism, unparseable-timestamp skip, invalid-policy rejection.
9. **Idempotency:** duplicate exposure-event delivery yields a single chronology entry (D.2/B.5).
10. **Late correction:** exposure landing after B's classification leaves B's persisted label unrewritten; the next attempt on Q is blocked.

## §8 Governance — what this design does not do

No code, schema, seed, or policy text changed (docs-only commit). The classifier stays PROTOTYPE per S2's law; no producers built (S4); no migration executed (F.5 §7 remains skeleton pending the curriculum/KG authority); BKT/BDT and `masteryMutation: "NONE"` untouched; no threshold invented (24h/7d remain S9 candidates per F.3). Open decision points for the authorities: **DP-1** Gate-2 rung assignment (proposed `SUPPORTED_SUCCESS`); **DP-2** F.1(b)×F.3 defeated-prior composition (proposed: blocked); **DP-3** chronology substrate (telemetry_events types vs dedicated evidence-events table per S2 §7.1); **DP-4** question-rewrite identity discipline; **PF-1** support-assisted transfer priors (recorded tension, unchanged behavior); **PF-2** past-support retake extension (ruling letter says no gate; conservative extension available).

## §9 S2 §7 twelve-prerequisite crosswalk (status after this design)

| # | Prerequisite (S2 §7) | Status |
|---|---|---|
| 1 | Event table contract | **Specified** (§4); shape choice = DP-3; implementation S4 + authority |
| 2 | Producer payload law | **Specified** (§4: attemptId + producer identity + schemaVersion + questionId) |
| 3 | Ungraded-derivation law | Unchanged; marking-state lifecycle law stands (D.1); pins 8 |
| 4 | Graded-lane publication decision | **Not discharged** — explicitly out of scope; remains open for the authority |
| 5 | Anchor validation-state carriage | Chronology is question-identity-scoped; SP anchors remain per D.3; "canonical" checkability blocked on the F.5 §7 authority review (audit §6 anchor-type hole) |
| 6 | Reveal-path identity injection (B.4) | Consumed (§4 linkage); B.4 design still owed by S4 |
| 7 | Chronology rules (marking vs attempt instant; late events) | **Discharged** (§4 instants + late-event rows) |
| 8 | Quarantine/INVALID/SUPPRESSED representation | **Consumed** (§4; excluded events do not block; audit surface) |
| 9 | C.4 attempt-linkage pathway | Contract carries `linkedAttemptId`; conversational-surface wiring = S4 |
| 10 | Version-pinning decision | **Proposed** (§5 identity law; DP-4) |
| 11 | F.1–F.5 rulings | DECIDED of record (`bb778ee`); this design implements the classifier share |
| 12 | No new schema merely for the PoC | Honored: design constrains both substrate options, mandates neither (DP-3) |

## §10 Stop state (S3, 2026-10-19)

Classifier redesign **designed, not implemented**: Gate 2 law, chronology contract, identity law, F.2/F.4 no-change records, ten test pins, and the S2 §7 crosswalk are of record (this document). S3 still owes: (b) the F.3 transfer-gate design consolidation as its own deliverable if the authority wants the full S9 preregistration shape, (d) the producer design for assistance/exposure/transfer (S4 input), and — gating all implementation — authority review of this document's DP-1–DP-4 plus the F.5 §7 migration contract. Remaining S3 item (c) per the F.5 audit §8 (S2 §7 crosswalk) is discharged at §9 above to the design level. No code, schema, seed, or policy text changed by this lane; the classifier remains PROTOTYPE; zero DB access this round.
