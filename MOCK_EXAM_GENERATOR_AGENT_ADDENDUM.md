# Mock Exam Generator — Agent Implementation Addendum

**Applies to:** `SyllabAI/syllabai-core`, `SyllabAI/syllabai-web`, `SyllabAI/syllabai-parser`, and project-control work
**Canonical architecture:** `MOCK_EXAM_GENERATOR_ARCHITECTURE.md`
**Decision:** ADR-018

## When this addendum must be read

Read this document before implementing or materially changing:

- Mock Exam Generator (F-051)
- exam-paper blueprint analysis
- paper assembly/selection algorithms
- personalized mocks
- assessment blocks/shared-stem grouping
- AI question variants used in mocks
- mock-paper rendering/export
- mock prediction/readiness evaluation
- any code that chooses a question set intended to resemble a formal board examination

## Implementation rules

### 1. Start from an exact blueprint identity

Never use a single global “Chemistry exam” blueprint. Scope it to Board → Qualification → Subject → CurriculumVersion → PaperCode → PaperType/Variant and version it.

### 2. Inspect existing feature IDs first

The canonical existing feature is **F-051 Mock Exam Generator (Exam Blueprint)**. Extend it; do not create another mock-generator feature with a duplicate purpose.

Important adjacent existing features:

- F-049 Target Test
- F-050 Test Builder
- F-053 Timed Exam Mode
- F-055 Question Attempt Logger / Learning Evidence
- F-047 Smart Mark
- F-168 Specification-point question tagging

New supporting capabilities are tracked in `backlog/mock-exam-generator-feature-addendum.tsv` rather than replacing F-051.

### 3. Use the canonical question model

Selection must operate on the canonical Question/QuestionPart model with SpecificationPoint, assessment objective, command word, question type, difficulty evidence, skill/misconception links, provenance and validation state.

Do not create a parallel “mock question” entity that loses canonical identity.

### 4. Treat assessment blocks as first-class where needed

A part that depends on a shared graph/table/data/passage/diagram/stem belongs to an AssessmentBlock/QuestionGroup. The solver should preserve these dependencies.

### 5. Separate hard constraints from optimization objectives

Hard constraints are validity requirements. Soft objectives improve fidelity or targeting.

Never let an optimization score hide a failed hard constraint.

### 6. Do not use universal timing heuristics

`marks × 1.5 minutes` is rejected as a universal rule. Prefer explicit paper duration and validated evidence-backed timing estimates.

### 7. Difficulty is contextual evidence

Store the evidence and context behind difficulty estimates. A 1–5 or similar UI band may be derived for convenience. Bloom annotations are optional and must not be treated as board truth.

### 8. Personalization cannot invalidate the exam

Learner targeting may influence item selection in Adaptive Diagnostic Mock mode, but Exam Simulation mode must prioritize exam validity. Mandatory paper structure remains a hard floor.

### 9. AI generation is a gated pipeline

The sequence is:

```text
validated source
→ generation
→ deterministic checks
→ numerical/domain validation
→ answer/mark-scheme alignment
→ provenance + model/prompt metadata
→ human review where required
→ VALIDATED
→ learner serving
```

Never serve an AI-generated/modified item merely because an LLM produced plausible text.

### 10. Never make the rendered PDF the source of truth

The canonical assessment model is the source. PDF/interactive output is a projection.

### 11. Mock attempts use the existing evidence system

All mock attempts must auto-log through the canonical Question Attempt & Learning Evidence subsystem. Preserve QuestionPart identity, marks, provenance, timing, confidence and marking method where applicable.

A completed paper must not imply all questions were attempted.

### 12. No fabricated predicted grades

Prediction/readiness UI must remain explicit about unavailable models. Never create a number because a dashboard card expects one.

### 13. Preserve reproducibility

Generated mocks must retain enough metadata to reproduce or audit the paper:

- blueprint version
- candidate-selection/generation policy version
- question IDs and versions
- variant lineage
- generation timestamp
- validation result
- actor/process provenance

### 14. Fail loudly on unsatisfiable constraints

A solver that cannot satisfy the required blueprint should return a structured failure or a clearly labeled degraded candidate for human review. It must not silently loosen hard rules.

## Research-sensitive work

Changes affecting prediction, difficulty estimation, historical paper analytics, time estimation, adaptive mock policy or research telemetry may alter project constructs or evaluation methods. Check the relevant research-paper section before changing scientific semantics.

## Cycle-1 guard

F-051 and its supporting features are long-term architecture unless the definitive workbook explicitly marks a specific row `Cycle 1`. Documentation alone does not expand the pilot scope.