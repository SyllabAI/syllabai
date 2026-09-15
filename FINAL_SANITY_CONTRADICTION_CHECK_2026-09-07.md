> **HISTORICAL SNAPSHOT — annotated 2026-09-15.** This is a point-in-time record of 2026-09-07, preserved verbatim. Any statement here that "Cycle 1 = Edexcel IAL Chemistry" — and every scope statement derived from it — was superseded by **ADR-019 (2026-09-11)**: the Cycle-1 pilot subject is now **Edexcel International GCSE Chemistry (4CH1)**. Read as history, not as current scope; current scope lives in `MASTER_SPEC.md` section 39a and ADR-019.

# Final Sanity & Contradiction Check — 2026-09-07

**Status:** PASS WITH CONTROLLED DOCUMENTATION FOLLOW-UPS

This is the final control-plane audit after the 2026-09-07 subject-first, teacher/LMS, learning-evidence, recommendation, and Mock Exam Generator architecture discussions.

## Executive result

The four newly formalized architecture layers are internally consistent:

```text
Subject/Curriculum/SpecificationPoint graph
        ↓
Canonical Question / QuestionPart substrate
        ↓
Assessment + Learning Evidence
     ↙             ↘
Teacher lens      Learner lens
     ↘             ↙
  Diagnosis / Recommendation
        ↓
   Next learning action
```

Mock Exams sit on this same substrate rather than creating a parallel assessment-history or learner model:

```text
Versioned Exam Blueprint
→ validated question/assessment-block candidates
→ hard-constraint assembly
→ fidelity validation
→ paper/session
→ QuestionAttempt / Learning Evidence
→ learner model / diagnosis / next action
```

No contradiction was found between these architectural layers or the Cycle-1 scope guard.

## Checks performed

### 1. Feature identity / duplication

**PASS.** Existing feature identity is preserved:

- F-049 Target Test
- F-050 Test Builder
- F-051 Mock Exam Generator (Exam Blueprint)
- F-053 Timed Exam Mode
- F-055 Question Attempt / Learning Evidence
- F-168 Specification-Point Question Tagging

Mock Exam Generator is an extension of F-051, not a duplicate.

The supporting mock rows are now consistently numbered:

- F-171 Exam Blueprint Registry & Versioning
- F-172 Assessment Block / Shared Context Modeling
- F-173 Mock Blueprint Fidelity Validation
- F-174 Personalized Mock Allocation
- F-175 Validated AI Question Variant Pipeline
- F-176 Mock Prediction & Readiness Evaluation

### 2. Subject/curriculum isolation

**PASS.** All four architecture discussions use the canonical boundary:

```text
Board → Qualification → Subject → CurriculumVersion → SpecificationPoint
```

Mock blueprint identity extends that boundary with paper identity and blueprint version. Teacher and learner features remain scoped to the same subject/curriculum context.

### 3. Curriculum truth vs learner state

**PASS.** Official curriculum and learner state remain separated. SpecificationPoint is an authoritative curriculum anchor; mastery, misconception, confidence, fluency, exposure, and review state are overlays. No new architecture layer mutates official curriculum nodes.

### 4. Question identity / learning evidence

**PASS.** Mock attempts reuse canonical Question/QuestionPart identity and the existing Learning Evidence subsystem. There is no second mock-only attempt ledger. Raw awarded/max marks remain canonical. Paper completion does not imply all questions were attempted.

### 5. Teacher vs student graph

**PASS.** Teacher Knowledge Graph remains a lens/aggregation over the shared graph. `NOT_TAUGHT` is not `LOW_MASTERY`. Teacher authorization remains server-side and class-scoped in the long-term model; T-029's cohort implementation remains a pilot shortcut rather than the final Class entity model.

### 6. Recommendation architecture

**PASS.** Recommendations remain Next Best Learning Action, not engagement optimization. Mock allocation may consume recommendation/learner evidence, but blueprint hard constraints remain authoritative for Exam Simulation and a validity floor for Adaptive Diagnostic Mock.

### 7. AI-generated assessment content

**PASS.** AI variants are explicitly later and gated. Source lineage, model/provider/prompt metadata, deterministic/domain checks, answer/mark-scheme validation, review state, and serving validation remain required. Plausible LLM output is not treated as official exam truth.

### 8. Exam authenticity vs historical analysis

**PASS.** Official board rules and historical corpus-derived patterns remain separate evidence classes. Historical frequency is not automatically elevated to an official board constraint.

### 9. Difficulty and timing semantics

**PASS.** Difficulty is contextual evidence; a simple 1–5 UI band may be derived but is not canonical truth. Bloom is optional analytical annotation. Universal `marks × 1.5 minutes` timing is rejected.

### 10. Cycle-1 scope

**PASS.** The architecture additions are documented as long-term/Cycle-2+ work and do not expand the pilot:

```text
Edexcel IAL Chemistry
~50 retake-path students
8 weeks
Tutor + Assessor only
predictions P1–P8
```

The Master Spec explicitly keeps mock-exam blueprints outside the Cycle-1 cut.

## Documentation consistency

### Fixed during this audit

1. `ARCHITECTURE_DISCUSSION_SYNC_2026-09-07.md` had stale mock IDs; fixed to F-171…F-176.
2. `PROJECT_CONTEXT.md` had stale mock IDs; fixed to F-171…F-176.
3. `PROJECT_CONTEXT.md` had stale Master Spec version `v1.1`; fixed to `v1.2.0`.
4. `PROJECT_CONTEXT.md` described DECISIONS only through ADR-017; fixed to ADR-001…ADR-018.
5. `DECISIONS.md` did not yet register ADR-018; ADR-018 is now registered in the consolidated ledger.
6. The project context now records the mock architecture and feature addendum as canonical long-term project knowledge.

### Remaining controlled synchronization gap

The checked-in `MASTER_SPEC.md` is substantively on version 1.2.0 and already contains the major architecture reconciliations. Its documentation index in **section 43** still lists the ADR series only through ADR-017 and does not list the dedicated mock-exam architecture documents.

This is an **indexing/documentation staleness issue, not an architectural contradiction**. It should be corrected in the next controlled Master Spec edit.

The same controlled revision should list:
- `DECISION_018_MOCK_EXAM_GENERATOR.md`
- `MOCK_EXAM_GENERATOR_ARCHITECTURE.md`
- `MOCK_EXAM_GENERATOR_AGENT_ADDENDUM.md`
- `ARCHITECTURE_DISCUSSION_SYNC_2026-09-07.md`

## Feature tracker / workbook status

The canonical text-form mock feature addendum contains F-051 and F-171…F-176. The checked-in binary master workbook is a separate controlled artifact and remains an older snapshot; it was not silently rewritten during this audit.

The local mock-architecture workbook snapshot generated during the earlier sync included the superseded F-169…F-174 numbering, so it is explicitly **not authoritative**. The corrected GitHub TSV is authoritative until the next controlled master-workbook synchronization folds F-171…F-176 into `backlog/syllabai-master-project.xlsx` and restores XLSX/TSV parity.

## Agent-governance status

`AGENT.md` already catches mock work through the question/assessment/evidence reading trigger and enforces the general provenance/evidence rules. The dedicated mock architecture and addendum are also registered in `PROJECT_CONTEXT.md`.

A dedicated mock-reading bullet in `AGENT.md` would be useful redundancy, but its absence is not a semantic architecture contradiction.

## Final verdict

**Architecture:** coherent.

**Cross-feature boundaries:** coherent.

**Feature IDs:** corrected and coherent in the current GitHub addendum/index.

**Cycle-1 guard:** intact.

**Evidence/learner-model semantics:** intact.

**Teacher/student graph separation:** intact.

**Recommendation/mock integration:** coherent.

**Known residual:** Master Spec section 43 needs a controlled index update; the binary master workbook needs a controlled sync to absorb F-171…F-176.

No unresolved architecture contradiction is currently known in the 2026-09-07 decision set. Remaining work is documentation/index synchronization, not a reversal of the architectural decisions.
