# PROJECT_CONTEXT.md — SyllabAI Context Map

## What SyllabAI is

SyllabAI is a syllabus-grounded adaptive learning platform for IGCSE/IAL exam preparation in the Bangladesh English-medium context. Its defining idea is not ordinary document chat; it is **diagnosis + grounded tutoring + learner modeling + assessment**, instrumented as a research platform.

## Research source documents

- `papers/paper_a_conceptual_model.pdf`: conceptual model and struggle typology.
- `papers/paper_b_system_design.pdf`: SyllabAI architecture and pre-registered system design.

## Canonical project documents

- `MASTER_SPEC.md`: engineering truth (v1.2.1; 2026-09-07 architecture synchronization + 2026-09-08 ADR-018 documentation sync).
- `AGENT.md`: agent behavior and mandatory implementation workflow.
- `DECISIONS.md`: architecture decision records (ADR-001…018 in the consolidated ledger).
- `DECISION_018_MOCK_EXAM_GENERATOR.md`: ADR-018 for the blueprint-driven Mock Exam Generator.
- `ARCHITECTURE_DISCUSSION_SYNC_2026-09-07.md`: consolidated durable index of the subject-first, teacher/classroom, learning-evidence, recommendation and mock-exam architecture discussions.
- `SUBJECT_ARCHITECTURE.md`: canonical subject-first product boundary and specification-point graph model (2026-09-07).
- `TEACHER_ARCHITECTURE.md`: canonical teacher/classroom/LMS product model layered over the shared subject/graph/evidence substrate (2026-09-07).
- `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md`: canonical Question Attempt / Learning Log and question-level evidence architecture (2026-09-07).
- `LEARNING_EVIDENCE_AGENT_ADDENDUM.md`: mandatory implementation rules for question-attempt evidence, review state, Smart Mark/test auto-logging, KG integration and teacher/research analytics.
- `RECOMMENDATION_SYSTEM_ARCHITECTURE.md`: canonical learning-first recommendation architecture.
- `RECOMMENDATION_SYSTEM_AGENT_ADDENDUM.md`: mandatory recommendation implementation rules.
- `ADR_017_LEARNING_FIRST_RECOMMENDATION_SYSTEM.md`: ADR-017 decision record.
- `MOCK_EXAM_GENERATOR_ARCHITECTURE.md`: canonical blueprint-driven mock-exam architecture.
- `MOCK_EXAM_GENERATOR_AGENT_ADDENDUM.md`: mandatory implementation rules for F-051 and related mock features.
- `WORKLOG.md`: history.
- `PROGRESS.md`: current state.
- `TODO.md`: current work queue (Cycle 1 first).
- `REPOSITORY_RESEARCH.md`: external repository dossier (section 0 = integration verdicts).
- `PLATFORM_RESEARCH.md`: verified platform/free-tier research.
- `backlog/syllabai-master-project.xlsx`: definitive feature/project tracker (Cycle column = pilot cut).
- `backlog/subject-architecture-feature-addendum.tsv`: committed text-form feature tracker addendum for the 2026-09-07 subject-first/specification-point decision.
- `backlog/teacher-lms-feature-addendum.tsv`: committed text-form feature addendum for the 2026-09-07 teacher/classroom/LMS architecture discussion. It extends existing F-050/F-072/F-073/F-074/F-075 and records genuinely new gaps without duplicating existing feature IDs.
- `backlog/learning-evidence-feature-addendum.tsv`: committed feature-tracker addendum for F-055/F-056/F-057/F-058/F-059 and their integrations; folded into the master workbook in session 17 (2026-09-07) as decision notes and priority updates — it remains the detailed supplement, not a competing inventory.
- `backlog/recommendation-system-feature-addendum.tsv`: committed feature-tracker addendum for the learning-first recommendation architecture; folded into the master workbook in session 17 (2026-09-07) as decision notes and priority updates — it remains the detailed supplement, not a competing inventory.
- `backlog/mock-exam-generator-feature-addendum.tsv`: committed feature-tracker addendum extending F-051 with F-171…F-176; folded into the master workbook in session 18 (2026-09-08: F-051 updated in place, six rows appended, TSV/XLSX parity 181=181) — it remains the detailed supplement, not a competing inventory.

## Repositories

The current repository set is:

| Repo | Contains |
|---|---|
| `syllabai` | this pack — spec, ADRs, backlog, research, papers |
| `syllabai-core` | Java 25 / Spring Boot 4.1 / Spring AI 2.0 modular monolith (all domain modules) |
| `syllabai-web` | Next.js 16 / React 19 / TypeScript frontend (Vercel) |
| `syllabai-parser` | polyglot offline content pipeline (opendataloader-pdf in-process; MinerU/Surya offline) |
| `Past-Papers` | public official-content corpus repo for IAL/IGCSE Edexcel QP/MS PDFs; no application code |

Domain modules (identity, curriculum, knowledge, content, assessment, smartmark, learner, tutor, diagnostic, recommendation, teacher, research/telemetry, infrastructure) live **inside `syllabai-core`** as strongly-separated packages and graduate to repositories only when a genuine runtime/lifecycle boundary appears.

## Approved technology direction

- Backend: **Java 25 + Spring Boot 4.1.x + Spring AI 2.0.x** (Maven, Spring Security, JPA, Flyway).
- Frontend: **Next.js 16.x + React 19.x + TypeScript** on **Vercel**.
- Data: **Neon PostgreSQL + pgvector**; KG as relational graph tables behind `KnowledgeGraphRepository` (Neo4j-portable).
- Java hosting: **Render free Docker** (cold starts accepted; no local filesystem state).
- Object storage: **Cloudflare R2** (free tier, no credit card).
- LLM: **free-tier chain Groq (llama-3.3-70b) → Gemini 2.5 Flash → OpenRouter** behind `LlmProvider` (ADR-009); embeddings via Gemini embedding API.
- Core architecture: modular monolith; multi-repo only for web/parser/main pack/corpus.
- License wall: permissive-only embeds (ADR-013); SurrealDB struck (BSL 1.1).

## Central system loop

```text
content → knowledge → learner state → diagnosis → intervention → assessment → learner update
```

For teacher-facing workflows, this expands into:

```text
class evidence → class/student graph → teacher action → assignment/test/resource → new evidence → updated aggregation
```

For question-level learning evidence, the canonical loop is:

```text
question/question-part
  → learner attempt
  → immutable QuestionAttempt / Learning Log evidence
  → AssessmentEvidence
  → learner model + diagnosis
  → KG overlay + recommendation
  → review / intervention
  → new attempt
```

For mock examinations, the assessment loop is:

```text
Board / paper identity
  → versioned exam blueprint
  → validated candidate pool / assessment blocks
  → constrained mock assembly
  → blueprint fidelity validation
  → interactive/PDF paper
  → QuestionAttempt evidence
  → learner model / diagnosis
  → future mock or next-best action
```

`QuestionAttempt` is an evidence event, not merely a completion flag. Learner review state (problematic, doubt, self-doubt, resolved, review priority) is a separate mutable state around the immutable evidence. Mastery is an inference produced by the learner model; UI actions must not directly add/subtract mastery.

## Central research constructs

Four layers: Content Knowledge · Exam Literacy · Learning Strategy · Self-Regulation. Six struggle types: 1 Prerequisite gap · 2 Surface engagement · 3 Exam literacy · 4 Metacognitive · 5 Motivational · 6 Instructional environment. Research-proposed splits: 3a/3b, 5a/5b.

## Product architecture — subject-first

The student experience is organized around explicit **subject enrollments**. A new student may have zero subjects. Adding one follows:

```text
Board → Qualification → Subject → Curriculum / Specification Version
```

Each enrolled subject is a self-contained academic workspace containing Overview, Revision Notes, Exam Questions, Past Papers, Flashcards, Target Test, Mock Exams, Smart Lesson, Tutor, and Knowledge Graph.

The curriculum graph is more granular than the old Unit/Topic/SubTopic model:

```text
Board → Qualification → Subject → CurriculumVersion
  → Unit/Section → Topic/SubTopic → SpecificationPoint
```

`SpecificationPoint` is a first-class node for the official numbered learning objectives in detailed specifications (e.g. `1.1`, `1.2`, `1.3`). It is the canonical bridge between official syllabus content, the user's specification-point-based Revision Notes, future question tagging, assessment evidence, and learner-state overlays.

Resources map to specification points. Future QuestionVersion/QuestionPart tagging may map one item to multiple SpecificationPoints; multi-topic coverage and uncertainty must be preserved. Learner state (mastery, misconceptions, confidence, fluency, review/decay, evidence) overlays the curriculum graph and does not mutate official curriculum content.

### Teacher and classroom layer

Teachers are also subject-scoped. A teacher enters a specific Board → Qualification → Subject → CurriculumVersion workspace and gets access to resource families plus teacher-only workflows such as Classes, Assignments, Test Builder, Mock Exams, Announcements, Knowledge Graph, At-Risk Students, reports and two distinct AI surfaces: Teacher AI Assistant and Data Assistant.

There are two student interface modes over one identity/learner model:

```text
Independent student
  └── subject learning workspace

Classroom-enrolled student
  └── same subject workspace
       └── Announcements + Assignments + My Results/Feedback
```

The class relationship is an overlay/capability layer, not a second student account or second learner model.

Teacher Knowledge Graph is a different **lens**, not a separate curriculum graph:

```text
same subject graph
     ├── student lens: individual learner state
     └── teacher lens: teaching coverage + class aggregate + drill-down
```

Teacher graph semantics must distinguish `NOT_TAUGHT` from low understanding. Grey nodes may mean no teaching coverage recorded; taught nodes can be colored by measured class understanding. Class views should expose distributions, not averages alone, and support drill-down into authorized individual student graphs.

Teacher Data Assistant is analytics/evidence-oriented; Teacher AI Assistant is academic/content/lesson-creation-oriented. Neither may fabricate facts. At-Risk Students must expose evidence and the rule/model version behind a flag.

**Canonical detail:** `SUBJECT_ARCHITECTURE.md` + `TEACHER_ARCHITECTURE.md`.

## Learning evidence / Learning Log architecture

The Question Attempt & Learning Evidence subsystem is a foundational cross-cutting layer. Its detailed contract is canonical in `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` and `LEARNING_EVIDENCE_AGENT_ADDENDUM.md`.

Important implementation facts:

- Preserve canonical Question and QuestionPart identity across Past Papers, Target Tests, Test Builder, Mock Exams, Teacher Assignments and Smart Lessons.
- Prefer QuestionPart-level evidence because a part may map to multiple SpecificationPoints and may carry its own marking evidence.
- Preserve `awardedMarks` + `maximumMarks`; percentages are derived.
- Preserve source/session provenance, attempt number, timing, confidence, answer evidence, marking method and AI execution metadata where applicable.
- Smart Mark and normal test submission should auto-log attempts.
- “Previously attempted” must work across all question sources.
- A paper-completed flag is not equivalent to every question being attempted; skipped questions must remain detectable.
- Problematic/doubt/self-doubt/resolved state is learner review state around immutable attempts.
- Flagging or resolution is never a deterministic mastery update. The old brainstorm `-0.02/+0.01` rule is rejected.
- Review Hub, spaced review, recommendations, KG learner-state inference and teacher analytics all consume the same evidence substrate; do not create parallel tracking models.
- Research-only telemetry (such as IRT or keystroke timing) must be versioned, privacy-aware and explicitly justified by the research protocol.

The research basis is Paper B §3.5 (“The Learning Log”) and §3.13, including the explicit reason for preserving rich attempt telemetry and the 80%-of-a-paper / skipped-hard-questions failure mode.

## Learning-first recommendation architecture

Recommendations are a **Next Best Learning Action** system rather than an engagement-maximizing feed.

The canonical cascade is:

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

Hard boundaries include subject/curriculum isolation, validated/servable content, authorization, prerequisite safety and teacher-pinned/assigned work where applicable. Rule-based recommendation is the deterministic baseline; collaborative and learned ranking are later experiments and cannot override hard constraints. Fixed random epsilon-greedy exploration and arbitrary interaction-count thresholds are not product/scientific constants.

Recommendation reasons are structured, evidence-backed and auditable. Educational video discovery is subject-scoped and validated; watch time is telemetry, not mastery.

**Canonical detail:** `RECOMMENDATION_SYSTEM_ARCHITECTURE.md` + `RECOMMENDATION_SYSTEM_AGENT_ADDENDUM.md` + `ADR_017_LEARNING_FIRST_RECOMMENDATION_SYSTEM.md`.

## Mock Exam Generator architecture

The Mock Exam Generator is a **blueprint-driven paper construction system**, not simply an LLM prompt that writes a plausible exam.

Its canonical identity is:

```text
Board
→ Qualification
→ Subject
→ CurriculumVersion
→ PaperCode
→ PaperVariant / PaperType
→ BlueprintVersion
```

The blueprint may contain official structural rules and evidence-backed historical patterns, but those categories must remain distinguishable. Historical frequency does not automatically become board truth.

Paper construction uses a validated candidate pool and explicit constraint solving:

```text
Blueprint
→ candidates / assessment blocks
→ hard constraints
→ soft optimization objectives
→ candidate paper
→ fidelity validation
→ valid paper
```

AssessmentBlock / QuestionGroup is required where parts depend on common data, graphs, diagrams, passages or shared stems. The solver must not invalidate assessment semantics by shuffling dependent parts independently.

Difficulty is contextual evidence. A simple 1–5 UI band may be derived, but it is not the canonical truth. Bloom is optional annotation. Universal `marks × 1.5 minutes` is rejected.

Two explicit mock policies are recognized:

```text
Exam Simulation
  → blueprint fidelity dominates

Adaptive Diagnostic Mock
  → blueprint validity remains a hard floor
  → learner evidence influences valid item selection
```

AI-generated/modified variants use a gated validation pipeline and retain source lineage + AI execution metadata. Unvalidated variants cannot be learner-served.

Every mock attempt uses the existing Question Attempt / Learning Evidence subsystem. A completed paper does not imply every question was attempted.

Mock prediction/readiness evaluation is a future research capability. The UI must not fabricate predicted grades.

**Canonical detail:** `MOCK_EXAM_GENERATOR_ARCHITECTURE.md` + `MOCK_EXAM_GENERATOR_AGENT_ADDENDUM.md` + `DECISION_018_MOCK_EXAM_GENERATOR.md`.

## Feature tracker consequences from the 2026-09-07 discussions

Existing feature identities were preserved and extended rather than duplicated:

- Subject architecture: existing subject/curriculum features plus specification-point extension.
- Teacher architecture: existing F-050/F-072/F-073/F-074/F-075 family extended; no duplicate teacher features.
- Learning evidence: F-055/F-056/F-057/F-058/F-059 plus related assessment/recommendation integrations.
- Recommendation: existing F-087–F-093 family extended with learning-first constraints and evaluation.
- Mock exams: **F-051 remains canonical** and is extended by F-171…F-176 in `backlog/mock-exam-generator-feature-addendum.tsv`.

## Execution scope

Cycle 1 (authoritative, Master Spec §39a as amended by ADR-019): Edexcel International GCSE Chemistry (4CH1) — subject scope moved from Edexcel IAL Chemistry by operator decision, 2026-09-11 — ~50 students, 8 weeks, Tutor + Assessor agents only, predictions P1–P8. Cycle-1 rows in the backlog define the cut; everything else is Cycle 2+.

The subject-first, teacher/classroom, learning-evidence, recommendation and mock-exam architectures are broader than Cycle 1 and **do not authorize bulk ingestion of any further qualification (e.g. IAL) or implementation of long-term features inside the pilot unless the tracker explicitly marks them `Cycle 1`.**

## Important engineering insight

The papers remain the authority for scientific definitions and research constructs. The Master Spec is the engineering translation. `SUBJECT_ARCHITECTURE.md` is the canonical product/graph decision for subject scoping and specification-point granularity. `TEACHER_ARCHITECTURE.md` is the canonical teacher/classroom/LMS product-layer decision. `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` is the canonical question-level evidence decision. `RECOMMENDATION_SYSTEM_ARCHITECTURE.md` is the canonical learning-first action-selection decision. `MOCK_EXAM_GENERATOR_ARCHITECTURE.md` is the canonical blueprint/constraint-based mock-exam decision.

Agents should not reread the entire papers for every ordinary task, but they must reread the relevant sections for research-sensitive changes. `ARCHITECTURE_DISCUSSION_SYNC_2026-09-07.md` is the durable cross-cutting discussion index; it does not replace the more detailed canonical documents.
