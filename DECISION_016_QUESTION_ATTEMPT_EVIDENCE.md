# ADR-016 — Question Attempt & Learning Evidence as a First-Class Subsystem

**Status:** Accepted  
**Date:** 2026-09-07  
**Supersedes:** The older brainstorming interpretation of the Question Attempt Logger as simple progress tracking.

## Decision

SyllabAI will treat question-level learner interaction as a first-class **Question Attempt & Learning Evidence** subsystem, also called the **Learning Log** in Paper B.

The subsystem is the canonical bridge between the assessment/question domain and:

- learner modeling
- diagnostic inference
- Knowledge Graph learner overlays
- recommendation and intervention
- spaced review
- student Review Hub
- teacher/class evidence analytics
- research telemetry

## Core semantic separation

```text
Immutable assessment evidence
        ≠
Mutable learner review state
        ≠
Derived learner mastery
```

A question attempt records what happened. A review state records how the learner currently relates to the question (problematic, doubtful, resolved, etc.). Mastery is inferred by the learner model from evidence and must not be directly mutated by UI actions.

## Canonical identity

Question identity is independent of presentation context. The same canonical Question/QuestionPart may appear in:

- Past Paper
- Target Test
- Test Builder quiz
- Mock Exam
- Teacher Assignment
- Smart Lesson
- future generated/variant sessions

A source session is provenance/context. It is not a new question identity.

## Granularity

Evidence should use QuestionPart granularity whenever feasible. QuestionPart → SpecificationPoint is many-to-many because a single part may assess multiple official learning objectives.

Raw assessment evidence must preserve `awardedMarks` and `maximumMarks`; a normalized percentage can be derived but is not sufficient as the canonical record.

## Learner self-report

Confidence, self-doubt, problem flags and resolution are valid learner signals, particularly for research on metacognition, but they are not assessor truth.

The following older deterministic rules are rejected:

```text
flag → mastery -0.02
resolve → mastery +0.01
self-doubt → halve mastery gain
```

The learner model may use such signals probabilistically/configurably, but fixed arithmetic from a button click is not canonical.

## Research basis

Paper B §3.5 defines the Learning Log as a research-instrument component and intentionally specifies richer fields than the product UI immediately requires. It also gives the concrete failure mode in which a learner completes roughly 80% of a paper, repeatedly leaves the hardest questions, later mistakes the paper for completed work, and skips those questions again. Question-level logging plus skipped-question resurfacing is therefore both a product requirement and a research-relevant telemetry mechanism.

## Scope guard

This ADR defines long-term architecture and research instrumentation; it does not expand Cycle 1. Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010.

## Canonical detail

See `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` and `LEARNING_EVIDENCE_AGENT_ADDENDUM.md`.