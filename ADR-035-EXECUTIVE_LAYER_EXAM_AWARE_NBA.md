# ADR-035: The executive layer — exam-aware next-best-action (the study planner), and what deliberately stays out of scope

**Status:** Proposed. This ADR is a *decision request*, not a landed design: no code accompanies it, and the NBA engine is byte-untouched at `nba-rules/v1.3`. It becomes Accepted only when the operator rules on **D1 (exam-date ownership)** — see Decision requested.
**Date:** 2026-10-04
**Scope (if accepted):** `syllabai-core` recommendation module (`RecommendationProperties`, `NextBestActionService` tier ordering, reason codes), a small teacher-facing exam-entry surface beside the assignment controller, one Master Spec §22 route row, and the assignments→NBA seam. Nothing else. Explicitly OUT of scope, by this ADR: notification/delivery infrastructure, learner-entered study timetables, streaks or any nudge that writes derived state, plan persistence, and the parent-facing surface (parked — see Rejected/Parked).
**Operator authority:** lane T-C76 ("go", trace 1a1030b349bc03c9) produced this draft as R2 of the executive-half proposal; the operator's gate is recorded in `.syllabai/tasks/T-C76.yaml`.

## Context

A gap analysis of what a human tutor does besides teaching (operator thread, 2026-10-04) found the platform has automated the **cognitive half** of tutoring to a high governance standard — diagnosis (BDT/struggle inferences/ADR-032), feedback (ADR-025 Smart Mark, ADR-027 queue), spaced retrieval (V18 + ADR-031) — while the **executive half** (planning, accountability, momentum) is thin and the **relational half** (motivation, safeguarding) is deliberately almost empty. The executive half is attractive precisely because it is all deterministic: none of it needs the LLM, so none of it can violate rule 6 or the chat non-disclosure contract.

First-hand recon before this ADR (all verified on core `ab33709`):

- **No exam-date entity exists anywhere** — no `ExamSession`, no `exam_date` column. The planner's central input has no source of truth and no owner.
- **Assignments are not an NBA input** (`Assignment` appears zero times in `NextBestActionService`): the two executive modules that exist do not talk to each other. A planner that says "revise electrolysis tonight" while a due assignment on electrolysis sits unseen would be dishonest scheduling.
- **No notification channel exists** (no SMTP/push/email; in-app SSE is the tutor stream only) — a "nudge loop" without a channel is either in-app-only (thin) or a new infrastructure project with its own PII/provider ADR.
- **The dashboard already surfaces due reviews** ("Due reviews — the forgetting-decay schedule") and now the agenda endpoint (`GET /api/v1/learners/me/agenda`, core PR #74) composes reviews + assignments + NBA in one read — the accountability *surfacing* slice is done.
- **The binding constraint is unchanged:** retrieval recall@10 remains 6.3× short of floor and refusal 27–31% (run-005-c-r8 / RAG review). An executive layer schedules the learner's time; it does not make the tutor worth the time. This ADR is therefore sequenced *after* the operator-gated retrieval queue in priority, and its acceptance must not be mistaken for a learning-outcome intervention.

## Proposal (the honest slice)

1. **Exam entries, teacher-owned.** A minimal `exam_entry` concept: `{ subject root (KG subject node), title, date, optional class target }`, entered by the teacher (the assignment-controller precedent: same role boundary, same request-shape discipline). v1 carries **at most one next exam per subject root** — the planner is deadline-aware, not a calendar. Learners never enter exam dates (teens will not enter timetables honestly; garbage-in corrupts every tier downstream).
2. **Time-pressure is a deterministic tier multiplier, not a new brain.** `nba-rules/v2.0` keeps the exact tier semantics and ordering rules of v1.3 and adds one factor: with `days_to_exam = date − asOf`, actions on topics inside the exam's subtree gain a bounded urgency weight with *published, deterministic* edges (same inputs + same clock ⇒ same output — the ADR-017 determinism contract is restated, not relaxed). Without any exam entry the output of v2.0 is byte-identical to v1.3 (the graph-stage precedent: "no applicable relationship ⇒ existing behaviour preserved by design").
3. **The assignments→NBA seam.** Due/undone visible assignments (the same V51 filter the agenda uses) become a tier input so scheduled revision never ignores assigned work. Assignment completion stays what it is today — append-only completion evidence, never mastery (the AssignmentFlowIT honesty pin holds).
4. **Reason codes gain a deadline family** (`EXAM_IMMINENT`, `ASSIGNMENT_DUE`) with evidence-derived details — never LLM-invented, never causal (F-093 unchanged).
5. **No plan persistence.** The planner is computed at read (the ADR-031 doctrine generalizes: derived schedules are recomputed, never stored). If a stored, evolving "revision plan" is ever wanted, that is a future ADR with its own write-path analysis.

## Decision requested

- **D1 — exam-date ownership (the gate):** ① teacher-per-class entry (classes already scope the KG via `ClassKnowledgeGraphService`; least new surface, matches how assignments already target), ② curriculum-level import from subject metadata (single source per subject, but no owner in the current ingestion contract), or ③ per-learner entry (rejected by this ADR — garbage-in). The wrong owner choice is the expensive mistake; everything else in this ADR is cheap and reversible.
- **D2 (consequential, smaller):** whether the teacher surface rides `syllabai-core` (this ADR's assumption, the assignment precedent) or the hub.

## Rejected / Parked (recorded so the gaps stop being rediscovered)

- **Notifications/push/email:** no channel, no demand evidence, real cost (third-party provider, PII). Any future nudge *delivery* needs its own ADR; in-app surfacing (already landed via the agenda) is the only form this project has evidence for.
- **Streaks / engagement nudges that write state:** engagement is evidence, not competence (the LIM/TutorSignalPolicy doctrine) — a streak is a derived-state liability with zero pedagogical evidence behind it. Rejected outright under the current honesty rules.
- **Learner-entered availability/timetables:** garbage-in; rejected with D1.
- **Parent-facing surface — PARKED, preconditions named:** (a) a pilot school asks (demand evidence), (b) a new-actor ADR exists — `Role.PARENT`, parent↔child linkage entity, school-mediated binding, minors'-data consent and opt-out, class-scoping rules (none of these exist; `Role` = LEARNER/TEACHER/ADMIN), (c) the executive read model it would expose is stable. Until all three hold, this is the best-documented parked item in the tracker, not an oversight.
