# SyllabAI ERD / EERD — Current Data Model and Canonical Target Model

**Prepared:** 2026-09-14  
**Purpose:** authoritative visual data-model review for the current SyllabAI architecture  
**Source baseline:** `SyllabAI/syllabai` main + `SyllabAI/syllabai-core` main as inspected on 2026-09-14.

## 1. Important interpretation

This package deliberately contains **two models**:

1. **Current ERD** — the relational model actually represented by the current `syllabai-core` database migrations through V18. It is the implementation baseline.
2. **Target EERD** — the canonical domain model implied by the current Master Spec and architecture addenda. It includes the subject-first product, first-class SpecificationPoint hierarchy, resource mappings, explicit student subject enrollment, and subtype semantics that are not yet all present as physical tables.

This distinction is essential. The project architecture has advanced faster than the physical schema in several areas. The target EERD must not be mistaken for a claim that every target entity is already implemented.

## 2. Current implementation snapshot

### Current core database substrate

The current core migration chain reaches **V18**. Major implemented areas are:

- identity: `users`, `roles`, `user_roles`
- curriculum/KG: `curriculum_versions`, `subjects`, `knowledge_nodes`, `knowledge_edges`
- assessment: `questions`, `question_topics`, `question_options`, `attempts`
- multipart assessment/marking: `exam_papers`, `question_versions`, `question_parts`, `mark_schemes`, `mark_points`, `answers`, `smart_mark_results`, `human_marks`, `smart_mark_agreement_evaluations`
- learner model: `skill_states`, `misconception_states`, `review_schedules`
- research/telemetry: `experiments`, `model_versions`, `prompt_versions`, `telemetry_events`
- content/RAG: `documents`, `document_chunks`
- diagnosis: `struggle_inferences`
- GLM-OCR audit bridge: `glm_ocr_bridge_records`
- teacher validation audit: `teacher_validation_events`
- campaign safety: `campaign_db_identity`

### Important implementation characteristics

- PostgreSQL is the system of record; the KG is relational (`knowledge_nodes` + `knowledge_edges`) and traversed with recursive SQL.
- Several learner references (`learner_id`) are application-level references rather than explicit database foreign keys in the current schema. The current ERD renders these as logical/dashed relationships.
- `question_versions` are immutable assessment snapshots; `question_parts` and mark-point decomposition support structured marking.
- Smart Mark is append-only at the result level. Human marking is separately recorded, and κ agreement is a release gate rather than a replacement for the human-mark record.
- `documents` are canonical parser outputs; `document_chunks` carry deterministic chunk provenance and pgvector embeddings.
- GLM-OCR evidence is deliberately preserved separately from the canonical content/assessment rows so reconciliation conflicts remain review-visible.
- Teacher validation events form an append-only audit trail and do not store or mutate the ingestion evidence itself.

## 3. Canonical target model

The current architecture defines the academic hierarchy as:

`Board → Qualification → Subject → CurriculumVersion → Unit/Section → Topic/SubTopic → SpecificationPoint`

`SpecificationPoint` is a first-class curriculum object. It preserves the official numbered learning objective, verbatim source statement, ordering, applicability and provenance. It is not a generic tag.

Student academic state is a separate overlay:

`Student → SubjectEnrollment → CurriculumVersion → Curriculum/KG → LearnerState`

The learner overlay contains mastery, misconceptions, confidence, procedural fluency, evidence history and review/decay state. It must never mutate the official curriculum nodes.

Questions and learning resources can map to one or more SpecificationPoints with confidence, provenance and validation state. This permits future tagging such as `1.2`, `1.3`, etc. without forcing multi-concept questions into a single topic.

## 4. EERD specialization decisions

The EERD uses enhanced-ER concepts where they clarify the domain:

- `USER` is a supertype with `STUDENT_PROFILE`, `TEACHER_PROFILE`, and `ADMIN_PROFILE` subtypes.
- `CURRICULUM_NODE` is a conceptual supertype for `UNIT`, `TOPIC`, `SUBTOPIC`, `SPECIFICATION_POINT`, `CONCEPT`, and `MISCONCEPTION`.
- `LEARNING_RESOURCE` is a conceptual supertype for `REVISION_NOTE`, `FLASHCARD`, and `SMART_LESSON_STEP`.
- Associative entities represent many-to-many mappings, especially `QUESTION_SPEC_POINT` and `RESOURCE_SPEC_POINT`.
- `QUESTION → QUESTION_VERSION → QUESTION_PART` is intentionally not collapsed: a question identity can have immutable content snapshots, and a structured question can contain multiple independently markable parts.
- `ATTEMPT → ANSWER → SMART_MARK_RESULT / HUMAN_MARK` preserves the distinction between learner evidence, AI candidate marking and human/authoritative marking.

## 5. Major gaps revealed by comparing implementation and target architecture

### G1 — Subject enrollment is not yet a physical domain boundary

The target product requires a student to start with zero subjects and explicitly add `Board → Qualification → Subject → CurriculumVersion`. The current schema has `subjects`, but it does not yet have a `subject_enrollments` table that scopes a student's academic state and workspace.

**Implication:** this is a future schema change, not merely a frontend routing change. It should become the authorization boundary for subject-scoped reads/writes.

### G2 — Board and Qualification are denormalized today

`curriculum_versions` currently stores `board` and `qualification` as text fields. The target EERD normalizes these into `BOARD → QUALIFICATION → SUBJECT → CURRICULUM_VERSION`.

**Implication:** do not casually migrate this while current ingestion is active. Introduce the normalized model with explicit provenance/identity rules and a controlled migration.

### G3 — SpecificationPoint is architectural but not yet a dedicated physical entity

The current KG node enum includes `SUBJECT`, `UNIT`, `TOPIC`, `SUBTOPIC`, `MISCONCEPTION`, and `CONCEPT`; there is no `SPECIFICATION_POINT` node type in the current migration chain.

**Implication:** the next curriculum/KG evolution should add specification-point semantics without destroying the current validated graph. The official numbering and source provenance must remain first-class.

### G4 — Question-to-specification-point mapping is not yet implemented

Current `question_topics` provides topic-level mappings. The target model needs a separate point-level associative mapping so a `QuestionVersion` or `QuestionPart` can map to multiple official specification points with validation/provenance.

### G5 — Resources are not yet a unified relational domain

The target architecture treats Revision Notes, Flashcards, Smart Lesson steps and future resources as mappings onto the same curriculum anchors. Current database migrations primarily model canonical documents and retrieval chunks, not a unified `LearningResource` hierarchy.

### G6 — The learner overlay is already real, but not yet explicitly subject-scoped

`skill_states`, `misconception_states`, `review_schedules`, and diagnostic inference rows are keyed to learner + KG node. Once multi-subject enrollment is introduced, subject/curriculum isolation must be guaranteed by graph-node ownership and/or explicit enrollment-aware authorization rather than relying on callers to supply the correct node.

### G7 — Current README/spec drift exists

The current `syllabai-core` README still describes the migration state as V1–V14, while the actual main branch contains migrations through V18. The Master Spec also describes a seven-repository map, while the current GitHub organization contains an additional `syllabai-teacher-workbench` repository.

These are documentation-sync issues, not reasons to distort the ERD. The diagrams use the current database and current repository state observed directly from GitHub.

## 6. Design rule for future schema work

Do not make every product feature its own disconnected data island.

The intended dependency direction is:

```text
Official specification
        ↓
Curriculum / SpecificationPoint graph
        ↓
Questions + Resources + Mark Schemes
        ↓
Attempts + Assessment Evidence
        ↓
Learner Overlay
        ↓
Diagnosis / Recommendation / Smart Lesson / Tutor
```

This keeps the student's Chemistry experience coherent: the same SpecificationPoint can anchor its revision note, flashcards, past-paper questions, mark points, learner mastery, misconception state, Target Test selection and Smart Lesson progression.

## 7. Files

- `SyllabAI_ERD_Current.svg` — current implementation ERD.
- `SyllabAI_ERD_Current.png` — raster preview.
- `SyllabAI_EERD_Target.svg` — enhanced target domain model.
- `SyllabAI_EERD_Target.png` — raster preview.
- `erd_current.dot` — Graphviz source for the current ERD.
- `eerd_target.dot` — Graphviz source for the target EERD.
