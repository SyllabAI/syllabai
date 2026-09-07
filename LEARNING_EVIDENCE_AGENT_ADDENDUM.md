# Agent Addendum — Question Attempt & Learning Evidence

This document is mandatory reading for work involving questions, assessment attempts, Smart Mark, Test Builder, Target Test, mocks, learner telemetry, Knowledge Graph learner state, recommendations, Review Hub, spaced review, or teacher question-level analytics.

## Canonical architecture

Read `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` before implementation. The canonical feature IDs are F-055 through F-059, with integration through F-029, F-033, F-047, F-050, F-054, F-078, F-091, F-153, F-154 and F-168.

For recommendation-specific work, also read `RECOMMENDATION_SYSTEM_ARCHITECTURE.md` and `RECOMMENDATION_SYSTEM_AGENT_ADDENDUM.md`.

## Non-negotiable rules

1. Treat Question Attempt history as immutable evidence, not a mutable status table.
2. Preserve raw awarded marks and maximum marks; percentages are derived.
3. Prefer QuestionPart-level evidence because marking and SpecificationPoint coverage may be part-specific.
4. Preserve canonical question identity across Past Papers, Test Builder, Target Tests, mocks, Smart Lessons and teacher assignments. Source/session is provenance, not identity.
5. Keep learner review state (problematic, doubt, self-doubt, resolved, review priority) separate from immutable attempts whenever practical.
6. A flag is a self-report signal, not an automatic mastery penalty.
7. “Resolved” means the urgent review state was cleared; it does not prove mastery.
8. Never implement the old brainstorming `-0.02` flag penalty or `+0.01` resolution bonus as deterministic learner-model rules.
9. Never let UI code directly update learner mastery.
10. A “paper completed” flag must not fabricate question attempts; skipped/unattempted questions must remain detectable.
11. Smart Mark auto-logging and test-submission auto-logging must preserve marking method and AI execution metadata.
12. Human marking overrides must preserve the original AI evidence where applicable.
13. Recommendation outputs must remain distinct from measured learner facts.
14. Teacher aggregates require class/subject authorization, an explicit time window, and evidence lineage.
15. Research-only telemetry such as IRT or keystroke timing requires explicit research/privacy justification; do not add it casually to product-critical flows.

## Recommendation integration rule

The Learning Log is a downstream-outcome substrate for recommendations. A recommendation is not validated merely because a learner clicked or watched it. Where possible, evaluate recommendations against subsequent assessment evidence, retrieval success, prerequisite correction, retention and syllabus coverage. Read the recommendation architecture before modifying ranking or exploration behavior.

## Research-sensitive requirement

Paper B §3.5 defines the Learning Log as a research-instrument component and explicitly includes attempt identifier, student identifier, question identifier, source session, timestamp, score, time taken, confidence, attempt number, automatic logging, answer text, problematic flag, doubt type, resolved state/time, self-doubt, plus richer IRT and keystroke-timing fields. Paper B also gives the 80%-of-a-paper / skipped-hard-questions rationale. Any change to these semantics must be checked against the paper before coding.

## Scope

This is long-term product architecture, not a Cycle-1 scope expansion. Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010.
