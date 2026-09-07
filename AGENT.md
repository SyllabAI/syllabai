# AGENT.md - SyllabAI Agent Operating Manual

## Mission

You are working on **SyllabAI**, a research-informed adaptive learning platform whose application backend is Java/Spring Boot and whose web frontend is Next.js/React. Your job is not merely to make code compile. Your job is to preserve the project's architecture, research meaning, evidence traceability, and project state while making measurable progress.

## Mandatory reading order

Before making substantial changes:

1. Read `MASTER_SPEC.md`.
2. Read the relevant rows in the definitive project spreadsheet (`backlog/syllabai-master-project.xlsx`, TSV export alongside it).
3. Read the relevant repository/module documentation.
4. Read `PROJECT_CONTEXT.md` if the task is cross-cutting or unclear.
5. Read `SUBJECT_ARCHITECTURE.md` for any product, curriculum, content-linking, assessment-tagging, knowledge-graph, student-dashboard, teacher-subject-workspace, or subject-enrollment task.
6. Read `TEACHER_ARCHITECTURE.md` for any teacher, class, classroom-student, LMS, Test Builder, assignment, announcement, teacher-analytics, teacher-AI, Data Assistant, At-Risk Students, teaching-coverage, class-KG, or teacher-to-student-graph task.
7. Read `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` and `LEARNING_EVIDENCE_AGENT_ADDENDUM.md` for any work involving questions, attempts, assessment evidence, Smart Mark, Test Builder/Target Tests, mocks, learner telemetry, review/flags, spaced review, recommendation inputs, question-level Knowledge Graph behavior, Review Hub, or teacher question-level analytics.
8. Read the relevant section of the research papers when the task changes research constructs, hypotheses, metrics, operational definitions, or learning-model behavior.

The Master Spec is the **engineering source of truth**, but it does **not** replace the papers for research claims. Agents do not need to reread both papers for ordinary CRUD/UI/infrastructure work. They must reread the relevant paper section for research-sensitive work.

## Source hierarchy

1. Research papers: scientific claims/hypotheses/operational definitions.
2. MASTER_SPEC.md: engineering architecture and technology decisions.
3. Spreadsheet: feature inventory and execution state.
4. REPOSITORY_RESEARCH.md: external implementation references.
5. DECISIONS.md: explicit architecture decisions.
6. SUBJECT_ARCHITECTURE.md: canonical product boundary and specification-point model for subject-first work.
7. TEACHER_ARCHITECTURE.md: canonical teacher/classroom/LMS product layer over the shared subject/knowledge architecture.
8. QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md: canonical question-level evidence and Learning Log architecture.
9. LEARNING_EVIDENCE_AGENT_ADDENDUM.md: mandatory implementation rules for question attempts, review state and evidence integrations.
10. WORKLOG/PROGRESS/TODO: living execution state and history.

Do not silently resolve conflicts. Record them and update the appropriate source through a documented decision.

---

## Project repositories

```text
syllabai           (main repo - spec, ADRs, backlog, research dossiers, papers)
syllabai-web       (Next.js 16 / React 19 / TypeScript, Vercel)
syllabai-core      (Java 25 / Spring Boot 4.1 / Spring AI 2.0 modular monolith)
syllabai-parser    (polyglot offline content pipeline)
Past-Papers        (raw corpus asset repo - IAL/IGCSE Edexcel QP/MS PDFs; no code)
```

All domain modules (identity, curriculum, knowledge, content, assessment, smartmark, learner, tutor, diagnostic, recommendation, teacher, research/telemetry, infrastructure) live **inside `syllabai-core`** as strongly-separated packages. They graduate to separate repositories only when a genuine runtime/lifecycle boundary appears (ADR-012).

## Core technology constraints

- Java 25
- Spring Boot 4.1.x + Spring AI 2.0.x
- Maven
- Next.js 16.x / React 19.x / TypeScript
- Vercel for web frontend
- Neon PostgreSQL + pgvector by default
- Render/Docker for free-tier Java deployment
- Cloudflare R2 (free tier, no credit card) for object storage
- Default LLM chain: Groq → Gemini 2.5 Flash → OpenRouter free models (all free, no card)
- Provider-neutral interfaces for LLM, vector, graph, parser, object storage, etc.

Do not add a paid-only dependency merely for convenience. Do not embed code or data from non-permissive licenses (BSL/AGPL/GPL/source-available/custom) — those repos are reference-only (ADR-013).

---

# Worklog / Progress / TODO protocol

These files are mandatory living project records.

## `WORKLOG.md`

Append chronological entries. Never rewrite history.

Each entry should contain:

```text
Date/time
Agent/session
Task
Files changed
What was learned
Implementation completed
Findings
Mistakes / regressions
Breakthroughs / useful insights
Tests/verification
Open questions
Next action
```

### Important rule

**Repeat important findings, mistakes, and breakthroughs.** Do not assume a future agent will infer them from code or git history.

Examples:

```text
Finding: pgvector works for the current retrieval path; no second vector DB is justified yet.

Mistake: business logic was placed in a controller; moved it into the application service.

Breakthrough: separating AssessmentEvidence from LearnerState allowed Smart Mark and BKT to remain decoupled.
```

Repeat high-impact items again in `PROGRESS.md` when they materially change the architecture or project direction.

## `PROGRESS.md`

Maintain the current state, not a chronological log.

It should include:
- overall completion estimate (qualitative or numeric, if meaningful)
- repositories status
- major subsystems complete/in-progress/blocked
- current architectural state
- latest findings
- latest mistakes/regressions
- latest breakthroughs
- current risks
- next highest-value work

Update it whenever a substantial task is completed.

## `TODO.md`

Keep actionable tasks only.

Every item should have:
- task ID when useful
- description
- repository
- priority
- dependencies
- status
- acceptance criterion

Remove or mark tasks complete; do not leave stale tasks that are obviously finished.

---

# Spreadsheet protocol

`backlog/syllabai-master-project.xlsx` is the **definitive feature/project tracker**. The `Cycle` column marks the Paper B Cycle-1 pilot cut; rows marked `Cycle 1` are the authoritative execution scope (Master Spec section 39a).

Agents must:
- find the feature ID before coding a feature;
- update status after meaningful progress;
- update dependencies if discovered;
- record repository/module ownership;
- add a new row if a missing capability is discovered;
- avoid duplicating features under different names;
- preserve the original source row where useful;
- keep research linkage and validation metrics current.

The spreadsheet is not a substitute for code or docs; it is the execution index.

---

# Subject-first architecture protocol

`SUBJECT_ARCHITECTURE.md` is mandatory reading for any work that changes how students choose, view, study, practice, assess, or visualize a subject.

The long-term product boundary is:

```text
Student
  └── Subject Enrollment
       └── Board → Qualification → Subject → Curriculum/Specification Version
            └── Subject Workspace
                 ├── Overview / Dashboard
                 ├── Revision Notes
                 ├── Exam Questions
                 ├── Past Papers
                 ├── Flashcards
                 ├── Target Test
                 ├── Mock Exams
                 ├── Smart Lesson
                 ├── Tutor
                 └── Knowledge Graph
```

A student may begin with zero subjects. Do not assume every student is enrolled in every course.

The curriculum hierarchy is:

```text
Board → Qualification → Subject → CurriculumVersion
  → Unit/Section → Topic/SubTopic → SpecificationPoint
```

`SpecificationPoint` is a first-class canonical curriculum/knowledge anchor for official numbered learning objectives such as `1.1`, `1.2`, `1.3`. Preserve official code, wording, ordering, version, provenance, and explicitly stated applicability metadata. Do not replace specification points with generic topic tags.

Resources should map to specification points. Future QuestionVersion/QuestionPart tagging may map one item to multiple specification points; never force multi-topic coverage into a single tag. Uncertainty and review state must remain explicit.

Learner state is a separate time-aware overlay on the subject graph: mastery, misconceptions, confidence, procedural fluency, exposure/evidence, and review/decay. Never mutate official curriculum nodes with student-specific state.

The subject-first architecture is broader than the current pilot. **Cycle 1 remains Edexcel IAL Chemistry** under ADR-010. The IGCSE Chemistry examples in `SUBJECT_ARCHITECTURE.md` do not authorize IGCSE bulk ingestion or other scope expansion.

When an agent discovers a new subject-scoped capability, it must be added to the definitive tracker (or recorded in the current feature-tracker addendum pending the next controlled workbook sync) rather than existing only in prose.

---

# Teacher / classroom architecture protocol

`TEACHER_ARCHITECTURE.md` is mandatory reading for any work involving:

- teacher subject dashboards/workspaces
- classes and class membership
- classroom-enrolled student experiences
- Assignments and submission portals
- Test Builder or teacher-created assessments
- Announcements
- teacher resource access
- Teacher AI Assistant
- Teacher Data Assistant
- At-Risk Students / early warning
- class Knowledge Graph heatmaps
- teaching coverage / taught-state overlays
- individual student graphs viewed by teachers
- teacher analytics or class aggregation

The core product principle is:

```text
Student = individual learner lens
Teacher = teaching/class lens
Shared substrate = same Board → Qualification → Subject → CurriculumVersion → SpecificationPoint graph + assessment/evidence system
```

Teacher and student interfaces must not create duplicate curricula or parallel graph models. A class graph is an aggregation/lens over individual learner state and the shared subject graph.

`NOT_TAUGHT` is semantically different from `LOW_MASTERY`. Grey teacher-graph nodes represent absent teaching coverage, not weak student understanding. Taught nodes may use class-understanding bands based on measured evidence.

At-Risk Students must be evidence-first and inspectable. Data Assistant must answer from authorized structured data and expose scope/time window/data freshness; it must not hallucinate statistics. Teacher AI Assistant is a separate grounded academic copilot for teaching/resource creation.

`T-029` is the current minimal teacher review surface. Its Cycle-1-era cohort roster shortcut is not the final Class domain model.

The teacher architecture is long-term and **does not expand Cycle 1** merely because these capabilities are documented.

---

# Question / Learning Evidence architecture protocol

`QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` is mandatory reading for any question-level or assessment-interaction work.

The key invariant is:

```text
Immutable assessment evidence
        ≠
Mutable learner review state
        ≠
Derived learner mastery
```

Agents must:

- preserve canonical Question/QuestionPart identity across Past Papers, Target Tests, Test Builder, Mock Exams, Teacher Assignments and Smart Lessons;
- prefer QuestionPart-level evidence when marking or SpecificationPoint coverage is part-specific;
- preserve `awardedMarks` and `maximumMarks` rather than only a normalized percentage;
- preserve source/session provenance, attempt number, timing, confidence, answer evidence, marking method and AI execution metadata as applicable;
- auto-log normal test submissions and Smart Mark attempts;
- make “previously attempted” work across all question sources;
- keep skipped/unattempted questions detectable even when a paper session is marked complete;
- store problematic/doubt/self-doubt/resolved state as learner review state around immutable evidence;
- never implement the old brainstorming `flag → mastery -0.02`, `resolve → mastery +0.01`, or “self-doubt halves mastery gain” rules as deterministic learner-model arithmetic;
- never let UI button clicks directly mutate learner mastery;
- keep Review Hub, spaced review, recommendations, KG learner-state inference and teacher analytics on the same evidence substrate rather than creating parallel tracking tables/models;
- distinguish product-critical evidence from research-only telemetry such as IRT or keystroke timing.

**Research-sensitive rule:** Paper B §3.5 explicitly defines the Learning Log and its rich telemetry schema and explains the 80%-of-a-paper / skipped-hard-questions failure mode. Any change to these semantics requires checking the relevant Paper B section.

---

# Engineering rules

## 1. Preserve boundaries

UI does not own business rules. Controllers do not own domain logic. Provider-specific code does not leak into domain services.

## 2. Prefer contracts

Use interfaces for replaceable concerns:

```java
KnowledgeGraphRepository
VectorStore
DocumentParser
ObjectStorage
LlmProvider
EmbeddingProvider
AssessmentStrategy
LearnerModel
```

## 3. Do not overuse inheritance

Prefer composition and interfaces unless inheritance represents a genuine domain relationship.

## 4. Do not silently change scientific semantics

If an implementation change affects BKT, BDT, struggle types, Smart Mark evaluation, telemetry, or research outcomes, stop and consult the relevant paper section and `DECISIONS.md`.

## 5. Preserve provenance

Generated educational claims should remain traceable to source documents/evidence.

## 5a. Respect the license wall

Code or data may be embedded only from permissively licensed projects (MIT/Apache-2.0/ISC/ODbL-with-attribution). SurrealDB (BSL 1.1), Chat2DB, PageLM, Blockify, SurfSense, open-knowledge (GPL), Leantime (AGPL) are reference-only. Surya model weights and the SocraticLM dataset have separate non-permissive terms. When in doubt, check `REPOSITORY_RESEARCH.md` section 0 and record the decision.

## 5b. Guard the free-tier budget

LLM calls go through the provider chain with rate tracking (Master Spec section 26.1). Do not add features that assume paid-model quality or throughput; do not silently switch providers inside a registered experiment.

## 6. Record AI execution metadata

Where AI output matters, preserve model/provider/version and prompt/version metadata.

## 7. Treat external repository claims as references

Do not copy architecture blindly from DeepTutor, MinerU, Cognee, etc. Use them as implementation references behind SyllabAI's contracts.

---

# Coding workflow

```text
Understand task
  ↓
Locate feature in spreadsheet
  ↓
Read Master Spec sections
  ↓
Read SUBJECT_ARCHITECTURE.md when subject/product/curriculum/graph related
  ↓
Read TEACHER_ARCHITECTURE.md when teacher/class/LMS/teacher-KG/analytics related
  ↓
Read QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md when question/assessment/evidence related
  ↓
Read research section if needed
  ↓
Inspect existing code/tests
  ↓
Implement smallest coherent change
  ↓
Run tests/static checks
  ↓
Verify user-visible behavior where applicable
  ↓
Update docs
  ↓
Update WORKLOG
  ↓
Update PROGRESS
  ↓
Update TODO
  ↓
Update spreadsheet / current feature addendum
```

## Before finishing any task

Ask internally:
- Did I preserve the architecture?
- Did I add tests?
- Did I update the relevant project-management row?
- Did I document a new finding/mistake/breakthrough?
- Did I introduce a new assumption?
- Does that assumption require a research-paper check?
- If subject-scoped: did I preserve Board/Qualification/Subject/CurriculumVersion isolation?
- If curriculum-scoped: did I preserve official SpecificationPoint numbering and provenance?
- If teacher-scoped: did I enforce class/teacher authorization at the backend?
- If analytics-scoped: can every aggregate/flag be traced to evidence and a time window?
- If question/evidence-scoped: did I preserve immutable attempt history, raw marks, canonical QuestionPart identity, source/session provenance and separation from learner review state?

---

# Common mistakes to avoid

- Turning SyllabAI into a generic RAG chatbot.
- Treating free-tier LLM limits as production capacity, or hard-depending on a paid model.
- Copying code from reference-only repositories past the license wall (ADR-013).
- Pulling Cycle-2+ features (gamification, DAT, mock-exam blueprints, mobile) into the Cycle-1 pilot.
- Coupling the domain layer to OpenAI, Pinecone, Neo4j, MinerU, etc.
- Putting PDFs or uploads on ephemeral Render storage.
- Exposing JPA entities directly through APIs.
- Treating frontend role checks as authorization.
- Updating learner state directly from UI code.
- Using one topic for multi-topic exam questions.
- Treating BKT mastery as the complete learner model.
- Labeling students "at risk" without evidence.
- Presenting research hypotheses as validated facts.
- Introducing microservices without a real boundary justification.
- Adding paid infrastructure under the free-tier constraint without an explicit decision.
- Updating code without updating worklog/progress/TODO/spreadsheet state.
- Treating Unit/Topic/SubTopic as the maximum useful curriculum granularity when the official specification provides numbered learning objectives.
- Using free-form filenames/topic strings as the authoritative subject identity.
- Mutating curriculum nodes with learner-specific mastery or diagnostic state.
- Treating the teacher graph as a second curriculum graph instead of an authorized aggregation/overlay.
- Treating NOT_TAUGHT as equivalent to LOW_MASTERY.
- Using an LLM to invent class statistics, marks, attendance, risk labels, or evidence.
- Exposing student data to a teacher solely because the student and teacher share a subject; class/teaching authorization must still be checked.
- Treating a paper-completion flag as proof that every question was attempted.
- Storing learner mastery as a direct consequence of “flagged” or “resolved” UI actions.
- Recreating question identities separately for Past Papers, Test Builder, Target Tests, mocks or assignments.
- Reducing question evidence to a single float when raw awarded/max marks are available.
- Building a second parallel question-tracking system for the Review Hub, Teacher Hub or recommendation engine.

---

# Findings / mistakes / breakthroughs memory rule

At the end of every substantial task, explicitly record at least one of the following when applicable:

### Finding
A verified fact that changes how the system should be built.

### Mistake
An implementation error, failed approach, misleading assumption, or regression.

### Breakthrough
A useful architectural simplification, algorithmic insight, reusable pattern, or unexpectedly successful solution.

Repeat important items in subsequent progress updates until they are no longer operationally relevant.

---

# Research integrity

Never fabricate evidence.

Differentiate:
- source-derived fact
- implementation decision
- maintainer-reported capability
- unvalidated project hypothesis
- observed test result
- inference

When external research is needed because a technology/version/pricing/security fact may have changed, verify it from a current authoritative source and record the source in the relevant documentation.

---

# Definition of done

A task is not done merely because code exists.

It is done when:
- implementation is complete;
- tests pass;
- integration boundaries remain clean;
- security/privacy requirements are respected;
- telemetry/provenance exists where relevant;
- documentation is synchronized;
- `WORKLOG.md`, `PROGRESS.md`, and `TODO.md` are updated;
- the definitive spreadsheet row is updated.
