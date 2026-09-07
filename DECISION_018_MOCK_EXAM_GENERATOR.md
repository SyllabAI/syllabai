# ADR-018 — Blueprint-Driven Mock Exam Generator

**Status:** Accepted
**Date:** 2026-09-07
**Decision scope:** Long-term platform architecture; Cycle-1 scope unchanged

## Context

The project discussion around mock exams proposed reconstructing an exam-board pattern from past papers, selecting questions with constraints, rendering a paper, and eventually generating numeric variants with AI.

The useful architectural insight is that this is not primarily a text-generation problem. It is an **assessment blueprint reconstruction and constrained paper assembly problem** with an optional gated question-generation layer.

The system also needs to coexist correctly with F-050 Test Builder, F-049 Target Test, F-053 Timed Exam Mode, F-047 Smart Mark and the F-055+ Question Attempt / Learning Evidence subsystem.

## Decision

SyllabAI will treat the Mock Exam Generator as a **versioned exam-blueprint-driven assessment system**.

The canonical flow is:

```text
Board / Qualification / Subject / CurriculumVersion / PaperCode
→ versioned ExamBlueprint
→ validated QuestionBank / AssessmentBlocks
→ constrained paper assembly
→ hard-constraint validation
→ blueprint fidelity report
→ interactive + PDF rendering
→ learner attempts
→ canonical Learning Evidence
→ learner model / prediction / diagnosis
```

### Blueprint identity

Blueprints are scoped and versioned by:

```text
Board
→ Qualification
→ Subject
→ CurriculumVersion
→ PaperCode
→ PaperVariant / PaperType
→ BlueprintVersion
```

### Blueprint content

Blueprints preserve or derive, with provenance:

- marks
- duration
- calculator policy
- structure and sections
- internal choice
- assessment-objective distribution
- SpecificationPoint coverage
- question/part types
- command words
- practical/data/graph representation
- formula/data-sheet rules
- mark-allocation patterns
- difficulty patterns
- reuse policy
- assessment-block constraints

Historical analytics are not silently converted into official board requirements.

### Assembly policy

Question selection uses explicit constraints. Hard constraints and soft objectives remain separate.

Hard constraints can cover structure, marks, duration, AO bounds, SpecificationPoint coverage, question types, calculator rules, internal choice, assessment-block integrity, validation state and reuse rules.

Soft objectives can optimize blueprint fidelity, learner targeting, diversity, representative difficulty and repetition control.

The solver implementation (knapsack, CP-SAT, integer programming, etc.) is replaceable. The invariant is that the result is inspectably valid.

### Assessment blocks

An `AssessmentBlock` / `QuestionGroup` concept is required where multiple parts depend on common data, a graph, diagram, passage, stimulus or stem. Dependent parts cannot be independently shuffled or substituted when doing so changes the assessment semantics.

### Difficulty and timing

Difficulty is stored as contextual evidence and may be summarized into derived bands. Bloom taxonomy is optional metadata, not exam truth. A universal `marks × 1.5 minutes` timing rule is rejected.

### Personalization

Two explicit policies are recognized:

- **Exam Simulation:** blueprint validity/fidelity dominates; personalization is limited.
- **Adaptive Diagnostic Mock:** blueprint validity remains a hard floor while learner evidence has more influence over valid item selection.

Problem Buster remains a separate remediation workflow.

### AI variants

AI-generated or AI-modified questions are not authoritative until validated through a gated pipeline:

```text
validated source
→ generation
→ deterministic checks
→ domain/numeric/unit validation
→ answer + mark-scheme alignment
→ provenance + AI execution metadata
→ human review where required
→ VALIDATED
```

Numeric mutation is explicitly treated as high risk because it can alter answer ranges, difficulty, units, physical/chemical validity, graphs, distractors and marking points.

### Evidence and learner model

Mock attempts use the existing canonical Question/QuestionPart identity and Learning Evidence subsystem. No parallel “mock mastery” model is introduced.

A paper completion event never implies that all questions were attempted.

Predicted grades/readiness values must not be fabricated. Prediction is a future validated research/evaluation capability.

## Consequences

### Positive

- Exam generation becomes auditable and reproducible.
- F-051 can share assessment infrastructure with Test Builder without becoming the same feature.
- Official board constraints remain distinguishable from historical patterns.
- Personalized mocks can target learning evidence without silently breaking exam validity.
- AI-generated variants can be added later without contaminating canonical question truth.
- Mock outcomes naturally feed learner modeling, recommendation and prediction research through the existing evidence layer.

### Costs / risks

- Blueprint analysis requires careful corpus interpretation and versioning.
- Constraint solving is more complex than random question selection.
- AI variants require stronger validation than ordinary prose generation.
- Good fidelity metrics need component-level inspection, not a single “looks realistic” score.

## Rejected alternatives

1. **LLM-only mock generation:** rejected because it cannot guarantee exact marks, structural validity, specification coverage, internal-choice rules or provenance.
2. **Universal historical topic-weight rules:** rejected because frequency is not automatically a board requirement and may vary by corpus/version.
3. **Universal marks-to-time formula:** rejected as too coarse for board/paper/item context.
4. **Direct numeric mutation of existing questions:** rejected without the validation pipeline above.
5. **Duplicate mock feature separate from F-051:** rejected; F-051 remains canonical and is extended by supporting features.
6. **Microservice for mock generation:** rejected for now; keep within the `assessment` module of the modular monolith.

## Relationship to other decisions

- ADR-014: subject-first / SpecificationPoint architecture provides the curriculum identity.
- ADR-015: teacher/classroom authorization applies to teacher-created/assigned mock content.
- ADR-016: all learner attempts use the immutable-evidence / review-state / derived-mastery separation.
- ADR-017: mock-generated assessment outcomes are eligible inputs to learning-first next-best-action policies, subject to their evidence quality.

## Scope guard

This ADR documents the long-term product architecture. It does **not** expand the active Cycle-1 pilot. Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010.