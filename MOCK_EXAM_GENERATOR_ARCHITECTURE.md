# Mock Exam Generator Architecture — SyllabAI

**Status:** Accepted long-term architecture
**Decision:** ADR-018
**Date:** 2026-09-07
**Scope:** Long-term platform architecture; does not expand Cycle 1

## 1. Purpose

SyllabAI's Mock Exam Generator is an **exam-blueprint-driven assessment assembly system**, not simply an LLM that writes a plausible-looking test.

The system must be able to reconstruct and version the intended structure of a real examination paper, select or generate assessment content under explicit constraints, validate the resulting paper against the blueprint, render a learner-usable paper, and feed resulting attempt evidence back into the learner model.

The central pipeline is:

```text
Board
→ Qualification
→ Subject
→ CurriculumVersion
→ PaperCode / PaperType
→ Versioned Exam Blueprint
→ Validated Question Bank
→ Constraint-Based Paper Assembly
→ Blueprint Validation / Fidelity Report
→ Rendered Mock Exam
→ Learner Attempt
→ Learning Evidence
→ Learner Model / Diagnosis
→ Next Mock or Intervention
```

The Mock Exam Generator shares the question bank and assessment substrate with Test Builder, but they are different product policies.

```text
Test Builder
  = human-directed assessment construction

Mock Exam Generator
  = exam-blueprint-directed assessment construction
```

Do not collapse the two features into one undifferentiated generator.

## 2. Source-of-truth hierarchy

Exam construction must distinguish three kinds of truth:

1. **Official exam evidence:** board specifications, official assessment materials, official past papers, mark schemes and other validated board evidence.
2. **Derived blueprint analytics:** statistically/research-derived patterns reconstructed from a corpus of official papers.
3. **AI-generated content:** candidate material that is never authoritative until it passes the project's validation/content-serving policy.

The system must preserve provenance for every blueprint rule and every question selected into a generated paper.

AI may propose content. Deterministic validation and, where required, human review decide whether it is servable.

## 3. Blueprint identity and versioning

A blueprint is always scoped to the exact assessment identity:

```text
Board
→ Qualification
→ Subject
→ CurriculumVersion
→ PaperCode
→ PaperVariant / PaperType
→ BlueprintVersion
```

A blueprint must be versioned. Re-running analytics against a new corpus, changing a weighting rule, or correcting a structural interpretation must create a new blueprint version rather than silently mutating an existing one.

Minimum blueprint fields:

- total marks
- duration
- calculator policy
- section structure
- question / part structure
- internal-choice rules
- assessment-objective allocation
- SpecificationPoint coverage targets
- question-type constraints
- command-word distribution
- practical/data/graph/experimental representation where applicable
- formula/data-sheet rules
- mark-allocation patterns
- difficulty distribution or evidence-backed difficulty bands
- reuse policy
- assessment-block/grouping rules
- any board/paper-specific structural invariants
- source corpus and provenance
- analytics method/version
- validation state

A blueprint is not considered authoritative merely because a statistical model produced it. It must have an explicit validation state and provenance.

## 4. Official evidence versus inferred patterns

Some characteristics can be read directly from official paper structure; others must be inferred from historical papers.

Examples of direct structural evidence:

- total marks
- duration
- section count
- internal-choice mechanism
- calculator policy
- allowed materials
- explicit paper instructions
- recurring question/part structure

Examples of inferred patterns:

- historical SpecificationPoint/topic coverage
- distribution of question types
- empirical difficulty distribution
- command-word mix
- historical assessment-objective distribution where not explicitly documented
- common mark-allocation patterns

Inferred patterns must carry corpus size, source range and analysis/version metadata. Do not present a historical frequency as a board requirement unless the board actually specifies it.

## 5. Canonical question model

The generator consumes the canonical question/assessment model:

```text
Question
└── QuestionPart
    ├── MarkPoints
    ├── SpecificationPoint(s)
    ├── AssessmentObjective(s)
    ├── CommandWord(s)
    ├── QuestionType
    ├── Difficulty Evidence
    ├── Cognitive Demand
    ├── Skill / Misconception Links
    └── Provenance / Validation State
```

`QuestionPart → SpecificationPoint` is many-to-many.

Do not flatten a multi-part question into one topic when different parts test different specification points.

Difficulty is an evidence-backed attribute, not an immutable universal 1–5 truth. The storage model should retain the underlying evidence and context, such as:

- proportion correct
- awarded-mark ratio
- discrimination where available
- response-time behavior where available and research-approved
- sample size
- corpus/paper context
- model/estimation version

A simple UI difficulty band may be derived from that evidence. A Bloom taxonomy label may be retained as an optional analytical annotation, but it is not an exam-board truth.

## 6. Assessment blocks / shared context

Introduce an explicit **AssessmentBlock / QuestionGroup** concept where question parts share a stem, graph, table, data set, diagram, passage or experimental scenario.

This prevents invalid operations such as independently shuffling or substituting a question part that depends on context introduced by another part.

Examples:

```text
AssessmentBlock
├── shared stimulus/data/diagram
├── QuestionPart A
├── QuestionPart B
└── QuestionPart C
```

The solver should normally select blocks, not arbitrary independent parts, whenever the original assessment semantics require shared context.

## 7. Candidate pool

The generator must select from a **validated/servable question pool**.

Candidate metadata should support filtering by:

- board / qualification / subject / curriculum version
- PaperCode compatibility
- SpecificationPoint(s)
- assessment objective
- question type
- command word
- difficulty evidence/band
- calculator requirements
- practical/data representation
- assessment block
- prior learner exposure
- reuse policy
- provenance
- validation state
- copyright/licensing/servability constraints

Unvalidated questions must never reach a learner-facing mock.

## 8. Constraint-based assembly

Paper generation is a constrained optimization problem:

```text
Versioned Blueprint
        ↓
Validated Candidate Pool
        ↓
Constraint Solver / Selection Policy
        ↓
Candidate Paper
        ↓
Validation
        ↓
Valid Paper
```

Hard constraints may include:

- exact total marks
- duration / time budget where modeled
- mandatory section structure
- assessment-objective bounds
- required SpecificationPoint coverage
- question/part type bounds
- internal-choice rules
- calculator policy
- practical/data requirements
- assessment-block integrity
- forbidden combinations
- reuse limits
- content validation state

Soft objectives may include:

- blueprint fidelity
- learner-targeting value for personalized modes
- diversity
- representative difficulty
- reduced inappropriate repetition
- balanced skill coverage
- historical pattern similarity

Knapsack, integer programming, CP-SAT, dynamic programming or another solver may be used. The algorithm itself is not the architectural commitment; **constraint validity and inspectability are**.

The system must fail explicitly when constraints are unsatisfiable. It must not quietly violate a hard rule to make a paper come out looking complete.

## 9. Time modelling

Do not encode a universal `marks × 1.5 minutes` rule.

Time estimates vary by paper and item context. Where estimated item time is used, it should be an evidence-backed attribute or a board/paper-specific rule with provenance.

At paper level, the system should prefer validated historical completion-time evidence and explicit paper duration over a universal marks multiplier.

## 10. Blueprint fidelity validation

Every generated mock receives a machine-readable fidelity report.

Example dimensions:

```text
Total marks                 ✓ / ✗
Duration                    ✓ / ✗ / estimated
Assessment objectives       % match
Specification coverage      % match
Section structure           % match
Difficulty distribution     % match
Question type distribution  % match
Command-word distribution  % match
Calculator policy           ✓ / ✗
Assessment-block integrity  ✓ / ✗
Internal choice rules       ✓ / ✗
Reuse policy                ✓ / ✗
```

A summary score may be provided for ranking or research dashboards, but a scalar score must never hide hard-constraint violations. A paper with an excellent aggregate score but an invalid calculator policy is invalid.

The fidelity implementation should preserve component-level deviations and reasons.

## 11. Exam-authentic versus personalized modes

The system should support explicit modes with different objective weights.

### Exam Simulation

Primary goal: reproduce the intended exam conditions.

```text
Blueprint fidelity dominates
Learner targeting = limited
```

This mode is appropriate for readiness assessment and prediction research.

### Adaptive Diagnostic Mock

Primary goal: obtain high-value diagnostic evidence while staying within valid assessment boundaries.

```text
Blueprint validity remains a hard floor
Learner targeting has greater weight
```

This mode can preferentially allocate valid items to SpecificationPoints associated with uncertainty, weak evidence, misconceptions or fluency gaps.

### Problem Buster

Problem Buster is separate. It is a deliberately adaptive remediation assessment and must not be marketed or evaluated as a board-authentic mock exam.

## 12. Personalized mock allocation

A personalized mock can combine:

```text
Blueprint
+
Learner model
+
Question Attempt / Learning Evidence
+
SpecificationPoint coverage
+
Misconceptions
+
Procedural fluency gaps
+
Exam date / planning state
+
Teacher assignment or priority
→
personalized candidate weighting
```

Personalization may affect **which valid questions** are chosen and how optional capacity is allocated, but it must not silently invalidate mandatory exam structure.

The learner model is used as a selection signal, not as a license to break the blueprint.

## 13. AI-generated / AI-modified variants

AI-generated question variants are a later, higher-risk capability. The safe pipeline is:

```text
Validated Source Question
→ Variant Specification
→ AI Variant Generation
→ Deterministic Structural Checks
→ Numerical / Unit / Domain Validation
→ Answer + Mark-Scheme Validation
→ Provenance + AI Execution Metadata
→ Human Review when required
→ VALIDATED / REJECTED
→ Learner serving only after validation
```

Do not treat numerical mutation as a trivial operation. Changing a number can alter:

- answer range
- arithmetic complexity
- unit handling
- graph shape
- physical/chemical plausibility
- required marking points
- difficulty
- distractor behavior
- internal consistency

A variant must retain lineage to its source question and record the generation model/provider/version and prompt/version where applicable.

AI-generated questions cannot become canonical board truth simply because the generated wording looks plausible.

## 14. Rendering and learner experience

A generated mock must be renderable to both:

- interactive assessment UI
- print/PDF paper with a corresponding answer/mark scheme representation

Rendering must preserve:

- section/part order
- marks
- instructions
- diagrams/tables/data
- internal-choice semantics
- page/footing requirements where applicable
- timing information
- question identity/provenance

The rendered artifact is a projection of the canonical assessment model, not a separate source of truth.

## 15. Learning evidence integration

Every learner attempt on a mock feeds the canonical Question Attempt & Learning Evidence subsystem.

The evidence must retain:

- mock/session provenance
- canonical Question/QuestionPart identity
- awarded/max marks
- attempt number
- timing
- confidence where collected
- answer/marking evidence
- marking method
- AI execution metadata when applicable

A mock-completion flag does not imply that every question was attempted.

The generated mock therefore participates in the same loop as every other assessment surface:

```text
Mock
→ Attempt Evidence
→ Learner Model
→ Diagnosis
→ Intervention / Next Best Action
→ Later Assessment
```

No parallel “mock history” learner model should be created.

## 16. Prediction and readiness research

Mock exams can serve as a research/evaluation instrument.

Where the project has a predicted-performance model, the system should compare:

```text
Predicted performance
→ Mock allocation
→ Actual mock performance
→ Prediction error / calibration
```

Useful future metrics include:

- overall prediction error
- calibration
- topic/SpecificationPoint-level prediction error
- question-level prediction error
- readiness classification quality
- correlation with later official/pilot assessment outcomes

These are evaluation constructs, not reasons to fabricate a predicted grade in the UI. The current implementation must render an explicit not-implemented state until the model is actually available.

## 17. Reuse, exposure and novelty

A mock generator must distinguish:

- exact canonical question reuse
- same-source question reuse
- source-family similarity
- AI-generated variant lineage
- learner exposure

The generator should support policies such as:

- unseen-paper simulation
- controlled reuse for diagnostic tests
- variant-based reuse after sufficient separation

Exact repeated questions may be appropriate for some practice modes but can contaminate exam-readiness measurement. Reuse policy must therefore be explicit and auditable.

## 18. Relationship to other features

### Test Builder — F-050
Human-directed construction. Teachers choose content, filters and structure. The builder may consume blueprint metadata and evidence-driven filters but must remain a teacher-controlled product.

### Target Test — F-049
Learner-directed targeted practice. Weak SpecificationPoints and evidence drive selection. It is not required to reproduce a formal exam blueprint.

### Timed Exam Mode — F-053
Provides timing behavior for applicable assessment sessions. It is a shared assessment capability rather than a separate paper-generation algorithm.

### Smart Mark — F-047
Marks generated mock attempts through the same validated assessment/marking pipeline.

### Question Attempt Evidence / Learning Log — F-055+
The canonical evidence sink for every mock attempt.

### Problem Buster
Adaptive remediation, not exam-authentic paper generation.

## 19. Security, authorization and integrity

Teacher-created or teacher-assigned content must respect class/teacher authorization. Students must never be able to discover restricted teacher resources merely because those resources entered a candidate pool.

Generated papers should carry:

- blueprint version
- generation policy/version
- question IDs/versions
- provenance
- validation state
- generation timestamp
- responsible actor or process

If any component is invalid after generation, the paper must be quarantined rather than silently served.

## 20. Implementation boundary

The architecture remains inside `syllabai-core` as part of the modular monolith, primarily under `assessment`, with contracts shared with `content`, `curriculum`, `knowledge`, `learner`, `teacher`, and `research/telemetry`.

No dedicated mock-generation microservice is justified at this stage.

Suggested application contracts:

```text
ExamBlueprintRepository
BlueprintAnalysisService
BlueprintValidationService
QuestionCandidateRepository
AssessmentBlockResolver
MockPaperAssembler
MockPaperValidator
MockVariantGenerator
MockVariantValidator
MockRenderService
MockPredictionEvaluator
```

Keep solver implementation behind an internal strategy/port so the domain model does not depend on one optimization library.

## 21. Non-negotiable rules for future agents

1. Do not implement F-051 as an LLM prompt that says “make a realistic exam.”
2. Do not duplicate F-050 Test Builder.
3. Do not treat historical topic frequency as an official board rule without evidence.
4. Do not use universal marks-to-time multiplication.
5. Do not discard multi-specification coverage.
6. Do not independently shuffle assessment parts that share required context.
7. Do not serve unvalidated AI-generated/modified questions.
8. Do not directly mutate learner mastery when a mock is generated, completed or flagged.
9. Do not invent predicted grades until a validated prediction model exists.
10. Preserve blueprint versioning, question provenance and generation-policy version for reproducibility.
11. Validate hard constraints separately from soft fidelity objectives.
12. Keep Exam Simulation and Adaptive Diagnostic Mock explicit as distinct policies.

## 22. Scope guard

This architecture is intentionally broader than the active pilot. **Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010.** Documenting the mock architecture does not authorize moving Mock Exam Generator implementation into Cycle 1.
