# Architecture Discussion Sync — 2026-09-07

This document is a durable index of the major architecture/product decisions established during the 2026-09-07 design discussions. It exists so a future human or agent can recover the **current direction** without relying on chat history.

## 1. Product direction

SyllabAI is a syllabus-grounded adaptive learning platform, not a generic AI tutor or PDF chatbot.

Core loop:

```text
Official curriculum
→ structured syllabus
→ knowledge/prerequisite graph
→ resources + exam questions
→ student attempt
→ assessment evidence
→ learner model
→ diagnosis
→ targeted intervention
→ reassessment
→ learner model update
→ next-best learning step
```

Core philosophy:

> AI proposes; evidence and validation determine truth.

## 2. Subject-first student architecture — ADR-014

Students are organized around explicit subject enrollments. A student can begin with zero subjects and add a subject through:

```text
Board
→ Qualification
→ Subject
→ CurriculumVersion
→ Subject Workspace
```

The subject workspace contains the relevant academic capabilities:

```text
Overview / Dashboard
Revision Notes
Exam Questions
Past Papers
Flashcards
Target Test
Mock Exams
Smart Lesson
Tutor
Knowledge Graph
```

The canonical curriculum hierarchy is:

```text
Board
→ Qualification
→ Subject
→ CurriculumVersion
→ Unit/Section
→ Topic/SubTopic
→ SpecificationPoint
```

`SpecificationPoint` is a first-class official learning-objective anchor. Preserve code, wording, ordering, curriculum version, provenance and applicability. Resources and QuestionParts may map to multiple SpecificationPoints. Learner state is an overlay and never mutates official curriculum.

Canonical detail: `SUBJECT_ARCHITECTURE.md`.

## 3. Teacher/classroom/LMS architecture — ADR-015

Teachers are subject-scoped and use the same underlying subject graph, content system, question bank, assessment model and learning-evidence substrate as students.

Teacher capabilities include Classes, Assignments, Test Builder, Mock Exams, Announcements, Knowledge Graph, At-Risk Students, reporting, Teacher AI Assistant and Data Assistant.

There are two interface modes over one identity/learner model:

```text
Independent student
  → subject workspace

Classroom-enrolled student
  → same subject workspace
  → Announcements + Assignments + My Results/Feedback
```

The teacher Knowledge Graph is a lens over the shared graph. `NOT_TAUGHT` and `LOW_MASTERY` are distinct semantics. Class aggregates must expose distributions/evidence and allow authorized drill-down to individual learner evidence.

Teacher AI Assistant and Data Assistant are separate. At-Risk Students is evidence-first and inspectable. Backend authorization, not frontend hiding, is the security boundary.

Canonical detail: `TEACHER_ARCHITECTURE.md`.

## 4. Question Attempt & Learning Evidence — ADR-016

Question interaction is a foundational cross-cutting subsystem.

Invariant:

```text
Immutable assessment evidence
≠
Mutable learner review state
≠
Derived learner mastery
```

Canonical Question/QuestionPart identity is shared across Past Papers, Target Tests, Test Builder, Mock Exams, Teacher Assignments, Smart Lessons and future generated variants.

Attempts preserve, where applicable, canonical question/part identity, session/source provenance, raw marks, timing, confidence, answer evidence, marking method, attempt number and AI execution metadata.

Review state such as problematic, doubt, self-doubt and resolved is separate from attempts. UI actions never directly perform arithmetic on mastery.

Rejected deterministic brainstorm rules:

```text
flag → mastery -0.02
resolve → mastery +0.01
self-doubt → halve mastery gain
```

A completed paper is not proof that every question was attempted. Skipped questions remain detectable.

Smart Mark and ordinary test submission are evidence producers. Review Hub, spaced review, recommendations, KG inference and teacher analytics consume the same evidence substrate.

Canonical detail: `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` and `LEARNING_EVIDENCE_AGENT_ADDENDUM.md`.

## 5. Learning-first recommendation system — ADR-017

Recommendations are **Next Best Learning Action**, not an engagement-maximizing social feed.

Objective:

> Maximize expected learning progress and appropriate syllabus coverage subject to pedagogical, curriculum, authorization, validation and learner-safety constraints.

Canonical cascade:

```text
Learner evidence/state
→ subject/specification graph
→ constrained candidate generation
→ content-based expansion
→ optional learned ranking
→ constrained exploration/diversification
→ next-best learning action
→ interaction
→ learning evidence
```

Rule-based recommendations are the baseline. Content similarity is candidate expansion. Collaborative filtering and learned ranking are future experiments that cannot override hard constraints. Fixed 10% epsilon-greedy and arbitrary interaction-count thresholds are rejected as product/scientific constants.

Reasons must be derived from structured evidence and reason codes; LLMs cannot invent recommendation facts.

Educational video discovery is subject-scoped and validated. YouTube watch time is telemetry, not mastery.

Canonical detail: `RECOMMENDATION_SYSTEM_ARCHITECTURE.md`, `RECOMMENDATION_SYSTEM_AGENT_ADDENDUM.md` and `ADR_017_LEARNING_FIRST_RECOMMENDATION_SYSTEM.md`.

## 6. Mock Exam Generator — ADR-018

The Mock Exam Generator is a **paper-blueprint engine**, not an “ask an LLM to write a realistic exam” feature.

The canonical architecture is:

```text
Board / Qualification / Subject / CurriculumVersion / PaperCode
→ versioned Exam Blueprint
→ validated Question Bank / Assessment Blocks
→ constraint-based assembly
→ hard-constraint validation
→ blueprint fidelity report
→ interactive/PDF rendering
→ learner attempts
→ Learning Evidence
→ learner model / diagnosis / future prediction evaluation
```

Blueprint identity is:

```text
Board
→ Qualification
→ Subject
→ CurriculumVersion
→ PaperCode
→ PaperVariant / PaperType
→ BlueprintVersion
```

Blueprints preserve or infer with provenance:
- total marks
- duration
- calculator policy
- sections/structure
- internal choice
- assessment objectives
- SpecificationPoint coverage
- question/part types
- command words
- practical/data/graph requirements
- formula/data-sheet rules
- mark-allocation patterns
- difficulty evidence
- reuse policy
- assessment-block constraints

Important distinction:

```text
Official board rule
≠
Historical corpus pattern
```

Historical frequencies must not be presented as official requirements unless directly supported by official evidence.

### Assessment blocks

Parts sharing a stem, graph, table, data set, diagram or passage may need an atomic `AssessmentBlock` / `QuestionGroup`. Do not independently shuffle dependent parts.

### Constraint solver

The paper is assembled under explicit hard constraints and soft optimization objectives. Knapsack/CP-SAT/integer programming/dynamic programming are implementation options, not architecture requirements.

Hard constraints are separately enforced. A scalar “realism/fidelity” score can never hide a hard failure.

### Difficulty and timing

Difficulty is contextual evidence (e.g. success rate, awarded-mark ratio, discrimination, timing where approved, sample size and context). UI bands may be derived. Bloom is optional metadata, not board truth.

Universal `marks × 1.5 minutes` is rejected.

### Modes

```text
Exam Simulation
  → exam validity/fidelity dominates

Adaptive Diagnostic Mock
  → blueprint validity remains a hard floor
  → learner evidence influences valid item selection
```

Problem Buster is separate and is not an exam simulator.

### AI variants

AI question variants are later and higher-risk:

```text
Validated source
→ generation
→ deterministic structural checks
→ numeric/domain/unit validation
→ answer + mark-scheme validation
→ provenance + model/prompt metadata
→ human review where required
→ VALIDATED
```

Numeric mutation is not trivial and must not bypass validation.

### Research use

Mocks may later evaluate prediction calibration and readiness by comparing predicted vs actual performance at overall, SpecificationPoint and question levels. No predicted grade may be fabricated before a validated model exists.

Canonical detail: `MOCK_EXAM_GENERATOR_ARCHITECTURE.md`, `MOCK_EXAM_GENERATOR_AGENT_ADDENDUM.md` and `DECISION_018_MOCK_EXAM_GENERATOR.md`.

## 7. Feature tracker consequences

Existing feature identities were preserved:

- F-049 Target Test
- F-050 Test Builder
- F-051 Mock Exam Generator (Exam Blueprint)
- F-053 Timed Exam Mode
- F-055 Question Attempt / Learning Evidence
- F-047 Smart Mark
- F-168 Specification-point question tagging

F-051 is expanded rather than duplicated. New supporting rows are registered in `backlog/mock-exam-generator-feature-addendum.tsv`:

- F-169 Exam Blueprint Registry & Versioning
- F-170 Assessment Block / Shared Context Modeling
- F-171 Mock Blueprint Fidelity Validation
- F-172 Personalized Mock Allocation
- F-173 Validated AI Question Variant Pipeline
- F-174 Mock Prediction & Readiness Evaluation

## 8. Architectural integration

All four recently formalized systems share the same academic substrate:

```text
Subject / CurriculumVersion / SpecificationPoint graph
                ↓
       Canonical Question Bank
                ↓
     Assessment + Learning Evidence
          ↙            ↘
 Teacher lens          Learner lens
          ↘            ↙
       Diagnosis / Recommendation
                ↓
           Next action
```

Mock exams do not create a parallel learner history. Teacher analytics do not create a parallel curriculum. Recommendations do not create a parallel question-tracking system.

## 9. Cycle-1 scope guard

These discussions define the **long-term architecture**. They do not expand the current pilot.

Cycle 1 remains:

```text
Edexcel IAL Chemistry
~50 retake-path students
8 weeks
Tutor + Assessor agents only
predictions P1–P8
```

Any feature not explicitly marked `Cycle 1` in the definitive tracker remains outside the execution cut.

## 10. Agent handoff rule

Before implementing any of these areas, the agent should read:

1. `MASTER_SPEC.md`
2. the definitive feature tracker/current addenda
3. the architecture document for the feature being changed
4. `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` for assessment/evidence changes
5. the relevant research paper section for scientific/evaluation changes
6. the relevant ADR and agent addendum

Do not rely on chat memory as a substitute for these documents.