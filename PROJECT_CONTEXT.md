# PROJECT_CONTEXT.md — SyllabAI Context Map

## What SyllabAI is

SyllabAI is a syllabus-grounded adaptive learning platform for IGCSE/IAL exam preparation in the Bangladesh English-medium context. Its defining idea is not ordinary document chat; it is **diagnosis + grounded tutoring + learner modeling + assessment**, instrumented as a research platform.

## Research source documents

- `papers/paper_a_conceptual_model.pdf`: conceptual model and struggle typology.
- `papers/paper_b_system_design.pdf`: SyllabAI architecture and pre-registered system design.

## Canonical project documents

- `MASTER_SPEC.md`: engineering truth (v1.1, merged & verified 2026-09-03).
- `AGENT.md`: agent behavior.
- `DECISIONS.md`: architecture decision records (ADR-001…013).
- `WORKLOG.md`: history.
- `PROGRESS.md`: current state.
- `TODO.md`: current work queue (Cycle 1 first).
- `REPOSITORY_RESEARCH.md`: external repository dossier (section 0 = integration verdicts).
- `PLATFORM_RESEARCH.md`: verified platform/free-tier research.
- `backlog/syllabai-master-project.xlsx`: definitive feature/project tracker (Cycle column = pilot cut).

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

## Execution scope

Cycle 1 (authoritative, Master Spec §39a): Edexcel IAL Chemistry, ~50 students, 8 weeks, Tutor + Assessor agents only, predictions P1–P8. Cycle-1 rows in the backlog define the cut; everything else is Cycle 2+.

## Important engineering insight

The papers remain the authority for scientific definitions. The Master Spec is the engineering translation. Agents should not reread the entire papers for every ordinary task, but they must reread the relevant sections for research-sensitive changes.
