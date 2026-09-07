# SyllabAI — Question Attempt & Learning Evidence Architecture

**Status:** Accepted architecture direction
**Date:** 2026-09-07
**Canonical feature IDs:** F-055, F-056, F-057, F-058, F-059
**Related features:** F-029, F-033, F-047, F-050, F-054, F-078, F-091, F-153, F-154, F-168
**Research authority:** `papers/paper_b_system_design.pdf`, especially §3.5 and §3.13

## 1. Purpose

The old brainstorming concept called the **Question Attempt Logger & Learning Log** is promoted to a foundational SyllabAI subsystem. Its purpose is not merely to remember whether a learner has solved a question. It is the canonical **question-level learning evidence layer** connecting assessment activity to learner modeling, diagnosis, recommendations, Knowledge Graph overlays, teacher analytics, and research telemetry.

The system must capture every meaningful learner-question interaction across all relevant question surfaces:

- Past papers
- Target Tests
- Test Builder quizzes
- Mock exams
- Teacher assignments
- Smart Lesson practice
- Future generated/variant questions

The same canonical question/question-part identity must persist across these surfaces. A source session changes the context of an attempt; it does not create a new academic question identity.

## 2. Architectural principle

> **Attempt history is immutable evidence. Review state is mutable learner state. Mastery is an inference, not a UI flag.**

The pipeline is:

```text
Question / QuestionPart
        ↓
Learner interaction
        ↓
Question Attempt Evidence
        ├── awarded marks / maximum marks
        ├── answer evidence
        ├── timing
        ├── confidence
        ├── source/session provenance
        ├── attempt number
        └── marking metadata
                ↓
        AssessmentEvidence
                ↓
         Learner Model / Diagnosis
                ↓
        Student KG overlay
                ↓
   Recommendation / intervention
                ↓
         new learning attempt
```

A separate review-state path runs alongside it:

```text
Attempt Evidence
      ↓
Problem / Doubt / Self-doubt
      ↓
Question Review State
      ↓
Review / Tutor / Practice
      ↓
Resolved-for-now
      ↓
Later retrieval evidence
```

A learner clicking **Flag**, **Resolved**, or **I am unsure** must never directly mutate official curriculum data or deterministically add/subtract a mastery score.

## 3. Why this matters

Paper B §3.5 explicitly defines the Learning Log as a research instrument and states that the richer schema is intentionally broader than immediate student feedback because it supports analysis of the project's struggle types. The paper also gives a concrete product rationale: a learner may complete about 80% of a paper, leave the hardest 20%, later see the paper again, assume it was already completed, and skip those unanswered questions. Without question-level logging, the missing work becomes invisible.

Therefore a “completed paper” state must never be treated as proof that all questions were attempted.

## 4. Canonical evidence model

### 4.1 Question identity

A canonical question may contain multiple parts:

```text
Question
 ├── QuestionPart A
 ├── QuestionPart B
 └── QuestionPart C
```

Where practical, evidence should be attached to `QuestionPart`, because marking and specification coverage are often part-specific. Whole-question summaries may be derived.

A QuestionPart may assess multiple SpecificationPoints:

```text
QuestionPart B
 ├── assesses → SpecificationPoint 2.3
 ├── assesses → SpecificationPoint 2.4
 └── assesses → SpecificationPoint 3.1
```

Never force a multi-concept question into one topic solely for convenience.

### 4.2 Immutable attempt record

The canonical attempt event should contain, as applicable:

```text
attemptId
learnerId
questionId / questionPartId
sourceSessionId
sourceType
subjectId / curriculumVersionId
attemptedAt
attemptNumber
awardedMarks
maximumMarks
timeTakenSeconds
confidence
answerText / answer artifact reference
markingMethod
autoLogged
AI provider/model/prompt metadata when AI marking is involved
```

`score` or percentage may be derived from `awardedMarks / maximumMarks`. It must not replace the raw mark evidence.

### 4.3 Review state

Problem/doubt state is separate from the immutable attempt history. It may include:

```text
problematic
flaggedAt
doubtType
selfDoubt
resolved
resolvedAt
reviewPriority
```

Recommended doubt types initially include:

```text
concept
calculation
wording
command_word
procedure
other
```

The list can be extended without redesigning attempts.

## 5. Source/session semantics

A single canonical Question may appear in multiple contexts:

```text
Past Paper 2022
Target Test #41
Teacher Assignment #17
Mock Exam #3
```

These are different **sessions**, not different academic identities. Consequently:

- Attempt history is shared across sources.
- “Previously attempted” checks canonical question identity.
- Source/session is retained for analytics and provenance.
- A generated test must not copy a question into a new identity merely because the test is new.

## 6. Previously-attempted behavior

Whenever a question is rendered, the platform should be able to show a subtle state such as:

```text
Previously attempted · 3 attempts
Last: 2026-09-05 · 4/6
Best: 2026-08-31 · 5/6
Confidence: Low
Problem flagged: Yes
```

For question parts, part-level state should be shown where the UI and data allow it.

The system should also surface **unattempted/skipped parts** when a learner encounters the same paper again.

Teacher-controlled retakes may intentionally override the warning without deleting evidence.

Bulk actions such as “mark paper completed” must not fabricate successful question attempts. A completion state is a session summary, not question-level evidence.

## 7. Review Hub

The Review Hub is a subject-scoped consumer of evidence APIs. It should not contain a second learner model.

Core areas:

1. **Problematic Questions** — unresolved question review states; actions: Tutor/AI explanation, Practice Similar, Review, Resolve.
2. **Attempt History** — chronological evidence filtered by subject, topic/specification point, date, source, marks, confidence and timing.
3. **Measured Weak Areas** — learner-model facts, clearly separated from recommendations.
4. **Due Reviews** — scheduler output.

The UI must preserve the difference between:

```text
FACT: “You scored 3/8 on six recent Mole Calculation parts.”

RECOMMENDATION: “Practice Mole Calculations with a Target Test.”
```

## 8. Mark-scheme integration

Every question surface should provide fast access to the appropriate official mark scheme/model answer without forcing the learner away from the attempt context.

This applies to:

- Past Paper viewer
- Target Test
- Test Builder
- Mock Exam
- Teacher Assignment

The parsed display must preserve provenance and should support LaTeX/structured formatting when applicable.

## 9. Smart Mark integration

Smart Mark is an automatic evidence producer, not a separate tracking system.

After Smart Mark evaluates a learner response:

```text
Student answer
      ↓
Smart Mark
      ├── AI mark / feedback
      └── attempt evidence event
```

The attempt should record the marking method and AI execution metadata. A teacher/human override should preserve the original AI evidence and record the human decision separately where the assessment model supports it.

AI-marking evidence must remain distinguishable from validated human marks for calibration research.

## 10. Test Builder / Target Test / Mock integration

Whenever a test submission contains an existing canonical question:

```text
submission
  ↓
question IDs
  ↓
automatic attempt evidence
```

No manual “log this question” action should be required for normal completed submissions.

Target Test and mock generation should be able to use attempt history to avoid accidental repetition, deliberately revisit weak/problematic material, or balance coverage.

## 11. Knowledge Graph integration

Question evidence maps through QuestionPart → SpecificationPoint(s) / concepts into learner-state inference.

```text
QuestionPart
   ↓
SpecificationPoint(s)
   ↓
Assessment Evidence
   ↓
Learner Model
   ↓
Mastery / misconception / fluency / confidence
   ↓
Student KG overlay
```

The old brainstorm proposed rules such as:

```text
flag → mastery -0.02
resolve → mastery +0.01
self-doubt → halve mastery gain
```

These constants are **not canonical and must not be implemented as deterministic rules**. Self-report is evidence. The learner model decides its weight relative to assessed performance and other signals.

In particular:

- Flagging does not itself prove knowledge decreased.
- Resolution does not itself prove mastery increased.
- Correct + high confidence is different evidence from correct + self-doubt.
- Repeated successful retrievals provide stronger mastery evidence than a single “Resolved” click.

## 12. Recommendation integration

Recommendation signals may include:

- repeated low-mark attempts
- unresolved problem states
- self-doubt
- repeated failure on the same SpecificationPoint
- stale unresolved flags
- due review state
- prerequisite weakness
- time/untimed performance divergence

Recommendation logic should require meaningful evidence before acting on self-reported signals, to reduce flag-spam/gaming.

Recommendation output remains distinct from learner-state facts.

## 13. Problem Buster

The old brainstorming idea of a “Problem Buster” paper is retained as a future high-value workflow.

It should not merely recycle the exact flagged questions. It should be able to construct a remediation set from:

```text
flagged question
     ↓
SpecificationPoint(s)
     ↓
misconception / prerequisite diagnosis
     ↓
similar questions
     ↓
Target Test
```

Exact question reuse is appropriate for deliberate review; generated variants are useful when the goal is transfer rather than recognition.

## 14. Spaced review

The initial implementation may use a simple interval policy such as 1/3/7/14/30 days, but this is explicitly an MVP fallback.

The long-term scheduler should incorporate evidence such as:

- recency
- number of retrievals
- success/failure trajectory
- mastery estimate
- confidence
- difficulty
- previous review outcomes
- unresolved problem state
- time since last successful retrieval

The scheduler must be replaceable and must not store derived scheduling logic inside immutable attempts.

## 15. Teacher analytics

Teacher-facing analytics consume the same evidence substrate within authorized class scope.

Useful aggregates include:

- most-flagged questions
- most common doubt types
- unresolved problem counts
- question resolution rate
- repeated-failure patterns
- specification points with concentrated difficulty
- class confidence-vs-performance divergence
- at-risk signals based on evidence

A teacher view should be able to drill down:

```text
Class
 ↓
SpecificationPoint
 ↓
Question / QuestionPart
 ↓
Affected learners
 ↓
Authorized learner evidence
```

Every aggregate should have a meaningful time window and evidence lineage. The Data Assistant must not invent statistics.

## 16. Research telemetry

Paper B §3.5 explicitly includes richer fields than the immediate product UI requires, including IRT parameters and keystroke timing for research purposes. Such collection is subject to research/privacy governance and must not be introduced casually into the production learner experience.

The research layer should therefore distinguish:

```text
Product-critical evidence
Research-only telemetry
```

Research-only telemetry must be versioned, privacy-aware, and explicitly justified by a research question or evaluation protocol.

## 17. Data integrity rules

1. Attempt history is append-only/immutable at the domain level.
2. Corrected marking creates a new decision/evidence record rather than erasing history.
3. Canonical Question/QuestionPart IDs remain stable across sessions.
4. Source session/context is preserved.
5. Awarded and maximum marks are preserved when marking is applicable.
6. Confidence is stored as learner self-report, not as assessor truth.
7. Flags/resolution are review state, not direct mastery state.
8. Curriculum nodes are never mutated with learner state.
9. Teacher aggregates obey class/subject authorization.
10. Research telemetry cannot silently become a product dependency.

## 18. Suggested API contract

The exact endpoints remain an implementation decision, but the domain contracts should support operations equivalent to:

```text
POST   /api/v1/learners/me/question-attempts
GET    /api/v1/learners/me/question-attempts
GET    /api/v1/learners/me/questions/{questionId}/attempt-state
PATCH  /api/v1/learners/me/question-review/{questionId}
GET    /api/v1/learners/me/review-hub
GET    /api/v1/learners/me/review-due
```

Backend code belongs in `syllabai-core` according to the modular-monolith policy. The frontend consumes domain APIs; learner-state mutation does not belong in UI code.

## 19. Recommended persistence model

Conceptual tables/entities:

```text
question_attempt
question_review_state
assessment_evidence
review_schedule_state
```

A minimal attempt row may resemble:

```sql
question_attempt (
  attempt_id,
  learner_id,
  question_id,
  question_part_id,
  source_session_id,
  source_type,
  subject_id,
  curriculum_version_id,
  attempted_at,
  attempt_number,
  awarded_marks,
  maximum_marks,
  time_taken_seconds,
  confidence,
  answer_reference,
  marking_method,
  auto_logged,
  ai_execution_reference
)
```

A review-state record may contain:

```sql
question_review_state (
  learner_id,
  question_id,
  problematic,
  doubt_type,
  self_doubt,
  resolved,
  flagged_at,
  resolved_at,
  review_priority,
  updated_at
)
```

The exact physical schema may change; the semantic separation must remain.

## 20. Acceptance criteria

The subsystem is complete enough for a production path when:

- A question can be attempted and an immutable attempt is recorded.
- The same question appearing in another source is recognized as previously attempted.
- Smart Mark and test submission automatically produce attempt evidence.
- Learners can flag questions and record doubt/self-doubt without corrupting assessment history.
- Resolved status clears review urgency without pretending to prove mastery.
- Question-part evidence can map to multiple SpecificationPoints.
- Review Hub reads from evidence/review APIs and deep-links to the source question.
- Knowledge Graph state is updated through the learner model, not UI-side arithmetic.
- Teacher analytics aggregate the same evidence under authorization controls.
- Research telemetry can be versioned separately from product-critical evidence.
- No “completed paper” path fabricates question attempts.

## 21. Scope

This architecture is the long-term product and research substrate. It does **not** expand Cycle 1 by itself. Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010. Implementation work must be staged according to the active backlog/cycle.
