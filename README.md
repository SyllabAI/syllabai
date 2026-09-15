# SyllabAI

Research-informed adaptive learning platform for IGCSE/IAL exam preparation, built on a four-layer model of student struggle (Paper A) and a pre-registered system design (Paper B). **Diagnosis + grounded tutoring + learner modeling + assessment — not a chat-with-PDF app.**

This is the **main repository**: the master project pack (specification, decisions, backlog, research dossiers, papers). Code lives in the sibling repositories below.

## Repository map

| Repo | Role | Stack |
|---|---|---|
| `syllabai` (this) | Master project pack: spec, ADRs, backlog, research, papers | Markdown + spreadsheet |
| `syllabai-core` | Backend modular monolith — all domain modules | Java 25 · Spring Boot 4.1 · Spring AI 2.0 |
| `syllabai-web` | Web frontend | Next.js 16 · React 19 · TypeScript · Vercel |
| `syllabai-parser` | Offline content pipeline (polyglot) | Java (opendataloader-pdf in-process) · GLM-OCR Python tooling (MinerU/Surya deferred) |
| `syllabai-pastpapers` | Canonical exam-material corpus — manifests, SHA-256 provenance, ledgers | Markdown/YAML corpus + Python ingestion tooling |
| `syllabai-resources` | RAG revision-note corpus + T-C09/T-C11 mapping/graph QA | Markdown corpus + Python governance scripts |
| `syllabai-teacher-workbench` | Teacher validation workbench: staged decision importer, evidence packs, release/verification tooling | Next.js 16 · React 19 · Vercel (readonly mirror mode) |
| `Past-Papers` | Raw operator-collected source PDFs (pre-normalization) | PDFs |

**Polyglot policy (ADR-011):** Java is preferred and owns the domain core (course requirement); other languages are welcome where they are clearly better — TypeScript for the frontend, Python/Rust for OCR/ML parsing tooling.

**Platform:** Neon PostgreSQL + pgvector (data) · Render free tier (Java) · Vercel Hobby (web) · Cloudflare R2 (binaries) · Free LLM chain Groq → Gemini 2.5 Flash → OpenRouter (ADR-009). **$0 total, no credit card.**

## Start here

1. `MASTER_SPEC.md` — engineering source of truth (v1.3.0 — 2026-09-11 Cycle-1 scope revision per ADR-019; originally merged & verified 2026-09-03 as v1.1; Addenda 1.4 (Learner Interaction Memory) & 1.5 (Contextual Learning Assistant), 2026-09-15, govern the newest layers)
2. `AGENT.md` — operating manual for coding/research agents
3. `backlog/syllabai-master-project.xlsx` — **definitive feature tracker** (TSV export alongside; `Cycle` column = Paper B Cycle-1 pilot cut; green = Cycle 1, amber = critical-path spine)
4. `DECISIONS.md` — architecture decision records (ADR-001…022; ADR-021 mirrored from its standalone file)
5. `REPOSITORY_RESEARCH.md` — external repo dossier (section 0 = verified integration verdicts & license corrections)
6. `ARCHITECTURE_REFERENCE_REGISTER.md` — curated architecture/UX/orchestration reference list (OpenHuman added 2026-09-05)
7. `PLATFORM_RESEARCH.md` — verified platform/free-tier research
8. `papers/` — scientific source material (Paper A conceptual model, Paper B system design)
9. `PROJECT_CONTEXT.md` / `PROGRESS.md` / `TODO.md` / `WORKLOG.md` — living project state

## Execution scope

**Cycle 1 = the course project**: Edexcel International GCSE Chemistry (4CH1) — subject scope moved from IAL Chemistry by ADR-019 (2026-09-11) — ~50 retake-path students, 8 weeks, Tutor + Assessor agents only (Paper B's own Cycle-1 definition). 34 backlog rows, 12 of them the critical-path spine. Everything else is Cycle 2+. See Master Spec §39a.

## Source hierarchy (do not silently resolve conflicts)

1. `papers/` — scientific claims, hypotheses, operational definitions
2. `MASTER_SPEC.md` — engineering architecture
3. `backlog/` — feature inventory & execution state
4. `REPOSITORY_RESEARCH.md` — external references
5. `DECISIONS.md` — explicit decisions
6. `WORKLOG/PROGRESS/TODO` — living state

## Traceability

`backlog/syllabai-original-v0.tsv` preserves the original feature sheet; the merged tracker records every patch in its `Agent Notes` column (v2 additions/fixes are marked `ADDED v2` / `PATCHED v2`).
