# ADR-027: Teacher-marking-surface scoping — classroom-authorization visibility; independent learners are teacher-invisible; teacher marking never blocks the independent flow

**Status:** Accepted
**Date:** 2026-09-20
**Extends:** ADR-015 (role-aware teacher/classroom LMS layer), TEACHER_ARCHITECTURE.md §4/§7.2/§8, F-161 (Smart Mark agreement gate)
**Binds:** the T-029 marking surface (`TeacherMarkingQueueService` / `TeacherMarkingController`) and the future classroom-lane marking surface

## Context

ADR-015 fixes the two student interface modes over ONE identity and ONE learner model — independent student and classroom-enrolled student — and is explicit that class enrollment is "an additional capability/authorization relationship, not a second account or second learner model." TEACHER_ARCHITECTURE §7.2 places teacher review/override inside the classroom submission portal (`Assignment → Submissions → Smart Mark where enabled → Teacher review/override → Feedback + result`). TEACHER_ARCHITECTURE §8 states the authorization rule without qualification: "A teacher must only be able to access classes and students covered by their authorization scope."

The implemented T-029 marking surface does not yet enforce that rule at the marking boundary. `TeacherMarkingQueueService.markingQueue()` reads `answers.findByMarkingState(state)` globally: every answer in a marking state — from ANY learner, independent or classroom-enrolled — is visible to any teacher-role user, and the same is true of the throughput metrics and the Run-Smart-Mark batch input validation. This is survivable today only because no Class/Enrollment entity exists yet: ADR-015 documents the pilot shortcut by name ("the Cycle-1-era roster implementation intentionally uses the enabled STUDENT cohort because a persistent Class domain entity is not yet part of the pilot").

Meanwhile the Smart Mark release path (F-161, Master Spec §15/Cycle-1 exit criteria) requires paired smart/human mark-point decisions (Cohen's κ ≥ 0.60) sourced from teacher double-marking — a pilot-time human activity with zero paired samples recorded so far (by design, pre-pilot). The independent learner's flow, by contrast, is teacher-less by construction: self-mark via the View Answer mark-scheme reveal, or Smart Mark, with evidence semantics κ-gated and fail-closed.

Left implicit, these three facts conflict at the moment the classroom lane lands: a global queue read and an authorization-scoped product cannot coexist. This record removes the ambiguity NOW, before the classroom lane is built.

## Decision

**D1 — Marking surfaces are authorization-scoped. Classroom-enrolled learners only.**
Every teacher-facing surface that exposes learner answer content — the marking queue (all states), throughput metrics that identify learners, the Run-Smart-Mark batch, human-mark/override views, and any κ drill-down that reveals answers — shows ONLY answers from learners enrolled in classes assigned to the requesting teacher. An independent learner (no class enrollment) never appears on any teacher surface. This closes TEACHER_ARCHITECTURE §8 at the marking boundary; it is not a UI nicety but an authorization requirement with the same rank as the existing backend RBAC (TeacherRouteSecurityIT).

**D2 — Teacher marking is NEVER a blocking step for an independent learner.**
The independent flow contains no human marking dependency, no queue wait state, and no teacher-visible artifact. Resolution paths: self-mark (View Answer reveals that question's mark scheme to the learner) or Smart Mark. Evidence semantics are unchanged and remain fail-closed (F-161/DECISION_016): SMART_MARKED stays provisional until the κ gate has passed; after the gate passes, Smart Mark marks drive evidence exactly as ratified — with no teacher in the loop. An independent learner's answer MAY remain SMART_MARKED indefinitely; that is a correct terminal state, not a stuck one.

**D3 — Paired κ calibration decisions originate exclusively where a human marker holds authorization.**
Under D1, human marks — and therefore κ pairings — can only arise from answers inside classroom scope. This is accepted, not worked around: the calibration sample is drawn from classroom-enrolled learners' answers (today: pilot staff marking under the pilot-staff authorization umbrella per the session-96 marking runbook; after the classroom lane: real enrollments). No mechanism may fabricate human marks on independent answers for calibration, and no independent answer is excluded from anything it needs — independent learners are consumers of the gate, never its sample population.

**D4 — Visibility is computed live from current enrollment + teacher class assignments; no snapshots.**
Enrolling a previously independent learner grants the newly authorized teacher PROSPECTIVE visibility of that learner's marking-relevant answers from that point; un-enrolling revokes prospective visibility. Nothing is retroactively erased: HumanMark rows are append-only audit history (Master Spec honesty rule), and past marks remain in the calibration set they were legitimately collected under. No visibility snapshots, no denormalized "visible_to" caches — the enrollment join is the single source of truth.

**D5 — Everything downstream is untouched.**
The marking state machine (`PENDING → SMART_MARKED → HUMAN_MARKED/OVERRIDDEN`, MCQ `AUTO_GRADED`), the evidence contract (first authoritative mark fires BKT once, overrides never re-fire), the κ gate math and threshold, the learner model, and T-029's historical acceptance criteria (TEACHER_ARCHITECTURE §20: T-029 is a foundation, not the complete teacher product) are all unchanged by this record. This is a scoping decision, not a semantics change.

## Interim rule (pre-class-layer) — binding, not advisory

Until the explicit Class/membership entity exists (deferred by ADR-015's own scope guard), the marking queue legitimately operates in **pilot-scope mode**: every pilot learner is covered by pilot-staff authorization, so the current global read happens to coincide with the authorization boundary. This is the SAME documented shortcut as the ADR-015 roster note and expires with it. The binding consequences:

1. When the classroom lane introduces the Class/membership model, the marking surface MUST ship enrollment-scoped in the SAME milestone — a global `findByMarkingState` read behind a live authorization model is a defect, not a cleanup item.
2. Until then, no new teacher-role account may be provisioned beyond the pilot-staff set, because today's queue read grants exactly pilot-scope-wide visibility.
3. The queue's learner-visibility gap is recorded as a known, time-boxed shortcut here — it must not be re-derived from scratch or "fixed" ad hoc in a different direction by another lane.

## Implementation notes (for the lane that lands the Class entity)

- `TeacherMarkingQueueService`: replace the global `findByMarkingState` reads (queue + throughput + pending-by-paper) with an enrollment-scoped path (teacher → authorized classes → enrolled learners → attempts → answers). Grouping/ordering semantics (§7 deterministic ordering) are orthogonal and unchanged.
- `smartMarkBatch`: validate scope per requested answer ID; out-of-scope IDs report the honest `SKIPPED`-family outcome with an explicit reason (never silently dropped, never fabricated) — consistent with the batch's existing honesty rules.
- κ endpoints already support paper scope; enrollment scope composes upstream of it (the human sample itself is scope-filtered by D1/D3), so no gate-math change is needed.
- No schema change is required by THIS record; the Class/membership schema belongs to the classroom lane under ADR-015's "design through the existing modular-monolith contracts" clause.

## Compliance

- ADR-015 — two modes, one identity/learner model; classroom as authorization overlay; explicit pilot-shortcut precedent this ADR inherits and time-boxes.
- TEACHER_ARCHITECTURE §4 (modes), §7.2 (teacher review lives in the classroom submission portal), §8 (authorization scope — the rule D1 enforces), §20 (T-029 as foundation).
- F-161 / Master Spec §15 + Cycle-1 exit criteria — κ gate untouched; calibration sourcing made explicit and honest under D3.
- DECISION_016 / QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md — evidence contract untouched; marking method provenance unchanged.
- Master Spec honesty rule — D4's no-erasure clause and the interim rule's explicit time-box.

**Scope guard:** this record decides WHO can see learner answers on teacher surfaces and WHEN teacher marking is required (only inside classroom scope, never for independent learners). It does not design the Class entity, does not change marking states, gate math, or evidence semantics, and does not authorize any Cycle-1 scope expansion. Any future conflict between this record and the classroom lane's implementation re-opens this ADR, not the implementation.
