# PROJECT_CONTEXT.md — SyllabAI Context Map

## What SyllabAI is

SyllabAI is a syllabus-grounded adaptive learning platform for IGCSE/IAL exam preparation in the Bangladesh English-medium context. Its defining idea is not ordinary document chat; it is **diagnosis + grounded tutoring + learner modeling + assessment**, instrumented as a research platform.

## Research source documents

- `papers/paper_a_conceptual_model.pdf`: conceptual model and struggle typology.
- `papers/paper_b_system_design.pdf`: SyllabAI architecture and pre-registered system design.

## Canonical project documents

- `MASTER_SPEC.md`: engineering truth (v1.1, merged & verified 2026-09-03).
- `AGENT.md`: agent behavior.
- `DECISIONS.md`: architecture decision records (ADR-001…014).
- `SUBJECT_ARCHITECTURE.md`: canonical subject-first product boundary and specification-point graph model (2026-09-07).
- `WORKLOG.md`: history.
- `PROGRESS.md`: current state.
- `TODO.md`: current work queue (Cycle 1 first).
- `REPOSITORY_RESEARCH.md`: external repository dossier (section 0 = integration verdicts).
- `PLATFORM_RESEARCH.md`: verified platform/free-tier research.
- `backlog/syllabai-master-project.xlsx`: definitive feature/project tracker (Cycle column = pilot cut).
- `backlog/subject-architecture-feature-addendum.xlsx`: feature-tracker addendum for the 2026-09-07 subject-first/specification-point decision; integrate these rows into the definitive workbook on the next controlled tracker sync.

## Repositories (ADR-012)

| Repo | Contains |
|---|---|
| `syllabai` | this pack — spec, ADRs, backlog, research, papers |
| `syllabai-core` | Java 25 / Spring Boot 4.1 / Spring AI 2.0 modular monolith (all domain modules) |
| `syllabai-web` | Next.js 16 / React 19 / TypeScript frontend (Vercel) |
| `syllabai-parser` | polyglot offline content pipeline (opendataloader-pdf in-process; MinerU/Surya offline) |

Domain modules (identity, curriculum, knowledge, content, assessment, smartmark, learner, tutor, diagnostic, recommendation, teacher, research/telemetry, infrastructure) live **inside `syllabai-core`** as strongly-separated packages and graduate to repositories only when a genuine runtime/lifecycle boundary appears.

## Approved technology direction

- Backend: **Java 25 + Spring Boot 4.1.x + Spring AI 2.0.x** (Maven, Spring Security, JPA, Flyway).
- Frontend: **Next.js 16.x + React 19.x + TypeScript** on **Vercel**.
- Data: **Neon PostgreSQL + pgvector**; KG as relational graph tables behind `KnowledgeGraphRepository` (Neo4j-portable).
- Java hosting: **Render free Docker** (cold starts accepted; no local filesystem state).
- Object storage: **Cloudflare R2** (free tier, no credit card).
- LLM: **free-tier chain Groq (llama-3.3-70b) → Gemini 2.5 Flash → OpenRouter** behind `LlmProvider` (ADR-009); embeddings via Gemini embedding API.
- Core architecture: modular monolith; multi-repo only for web/parser/main pack.
- License wall: permissive-only embeds (ADR-013); SurrealDB struck (BSL 1.1).

## Central system loop

```text
content → knowledge → learner state → diagnosis → intervention → assessment → learner update
```

## Central research constructs

Four layers: Content Knowledge · Exam Literacy · Learning Strategy · Self-Regulation.
Six struggle types: 1 Prerequisite gap · 2 Surface engagement · 3 Exam literacy · 4 Metacognitive · 5 Motivational · 6 Instructional environment. Research-proposed splits: 3a/3b, 5a/5b.

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

Resources map to specification points. Future QuestionVersion/QuestionPart tagging may map one item to multiple specification points; multi-topic coverage and uncertainty must be preserved. Learner state (mastery, misconceptions, confidence, fluency, review/decay, evidence) overlays the curriculum graph and does not mutate official curriculum content.

**Canonical detail:** `SUBJECT_ARCHITECTURE.md`.

## Execution scope

Cycle 1 (authoritative, Master Spec §39a): Edexcel IAL Chemistry, ~50 students, 8 weeks, Tutor + Assessor agents only, predictions P1–P8. Cycle-1 rows in the backlog define the cut; everything else is Cycle 2+.

The subject-first architecture is broader than Cycle 1 and does **not** authorize IGCSE bulk ingestion or other scope expansion by itself. IGCSE Chemistry is an important target course/example for the long-term platform architecture.

## Important engineering insight

The papers remain the authority for scientific definitions. The Master Spec is the engineering translation. `SUBJECT_ARCHITECTURE.md` is the canonical product/graph decision for subject scoping and specification-point granularity. Agents should not reread the entire papers for every ordinary task, but they must reread the relevant sections for research-sensitive changes.
