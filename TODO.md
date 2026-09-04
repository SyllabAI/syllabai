# TODO.md — SyllabAI Master Work Queue (Cycle 1 first)

**Scope guard:** only rows marked `Cycle 1` in `backlog/syllabai-master-project.xlsx` belong in the current execution window. The 12-spine critical path is F-020 → F-032 → F-033 → F-040 → F-041/F-043 → F-047 → F-055 → F-137/F-138 → F-148 → F-160.

## Wave 0 — foundations (this week)

- [x] T-001 Bootstrap `syllabai-core`: Spring Boot 4.1.x + Java 25 + Spring AI 2.0 skeleton, Maven, package structure per Master Spec §30. (F-002, F-008)
- [x] T-002 Flyway + Neon connection; pgvector extension enabled; dev profile with local Postgres via Docker Compose.
- [x] T-003 Spring Security + JWT auth skeleton; RBAC roles (STUDENT, TEACHER, ADMIN). (F-012, F-013)
- [x] T-004 REST conventions: `/api/v1` base, DTO boundaries, springdoc OpenAPI, error handling. (F-122)
- [x] T-005 `syllabai-web`: Next.js 16 + TypeScript + Tailwind scaffold on Vercel; API client typed from OpenAPI.
- [x] T-006 CI: GitHub Actions (build + test) on `syllabai-core` and `syllabai-web`.
- [x] T-007 Object storage adapter + Cloudflare R2 free bucket for past-paper PDFs. (F-021, F-149)

## Wave 1 — knowledge & content fabric

- [x] T-008 Canonical document format schema (JSON) + `DocumentParser` contract. (F-134, F-147) — syllabai-parser @ a43ad24, schema 1.0, 23/23 tests
- [x] T-009 In-process opendataloader-pdf integration (Maven) for text PDFs; bounding boxes retained. — opendataloader-pdf-core 2.5.7 (Apache-2.0, Central) 
- [x] T-010 Syllabus ingestion: Edexcel IAL Chemistry spec → curriculum tables → KG seed. (F-020, F-032) — parser `edexcel-numbered-outline-v1` (deterministic, per-node §17 provenance; real Pearson 2018 spec: 6 units / 20 topics / 15 subtopics) + core `CurriculumIngestionService` (idempotent, all-SUGGESTED) + teacher validation gate; prerequisites stay teacher-curated (never derived from an outline)
- [x] T-011 Past-paper + mark-scheme ingestion bridge: parser draft JSON → all-SUGGESTED content bank (paper/version/parts/scheme/points), teacher validation workflow, ingestion-anchor KG topic. Live-verified on real 4CH0/1C Jan 2012 (27 q / 62 parts / 33 points). Misconception/distractor links on structured items: Wave 3 (needs validated content). (F-028, F-029, F-152)
- [x] T-012 `KnowledgeGraphRepository` with recursive-CTE traversals; prerequisite queries. (F-032, F-135)
- [x] T-013 pgvector embedding pipeline (Gemini embeddings) over mark schemes/notes. (F-039, F-136) — core @ V11: canonical document store + deterministic chunking + Gemini text-embedding-004 (768-dim, `EmbeddingProvider` port, no failover by design) + HNSW cosine search; 121 unit tests + ContentPipelineIT

## Wave 2 — learner & assessment engine

- [x] T-014 `AssessmentEvidence` contract + attempt logging with timing, confidence, doubt flags. (F-053, F-055, F-056, F-153)
- [x] T-015 BKT engine with configurable params (L0=0.1, slip=0.1, guess=0.25, T=0.1) + parameter registry. (F-138)
- [x] T-016 Learner state aggregate: mastery, misconceptions, fluency (timed-vs-untimed gap, V8), confidence + self-doubt evidence. (F-137, F-033) — exam-literacy aggregate deferred to Wave 4 (needs marked structured data first)
- [x] T-017 BDT misconception engine driven by distractor evidence. (F-140)
- [x] T-018 Ebbinghaus decay nightly job (τ 30/90/365) + review-schedule feed. (F-159)
- [x] T-019 Timed vs untimed paired conditions + procedural_fluency_gap (V8 skill_states column, recomputed per node on evidence; null until paired). (F-162)
- [x] T-020 Learning-log telemetry: Paper B §3.5 fields, append-only event store. (F-160)
- [x] T-021 Smart Mark pipeline: candidate generation (LLM, pinned prompt v1) → deterministic bounds/coverage/mark-sum validation → append-only results; blank answers deterministic (no LLM). LLM never final truth. (F-047)
- [x] T-022 Human mark override + κ agreement gate: per-point paired Cohen's κ, threshold 0.60 recorded per evaluation, fail-closed gate; pre-gate smart marks provisional, post-gate authoritative; overrides never re-fire BKT. (F-144, F-161)

## Wave 3 — tutor & diagnostic intelligence

- [x] T-023 `LlmProvider` + free chain (Groq → Gemini → OpenRouter) with failover and rate tracking. (F-148, F-163)
- [x] T-024 KA-RAG orchestration: intent → KG context → hybrid retrieval → grounded generation. (F-040) — v0 foundation: deterministic intent (VALIDATED nodes only), KG+vector RRF fusion (rank-only, k=60), NoReranker Strategy, learner-state context assembly, grounded generation (prompt tutor-grounded/v1, free-LLM chain), citations with deep links, KA_RAG_COMPLETED telemetry (V12), deterministic refusal on empty evidence; POST /api/v1/tutor/ask (backend surface — chat UI stays T-025)
- [ ] T-025 Tutor chat UI with verbatim citations + PDF deep-links. (F-041, F-043, F-022)
- [ ] T-026 Tutor policy: diagnosis-aware intervention selection (Scientific-learning-skills prompts). — v0.2 on branch `codex/session-6-diagnosis-policy` (session-6 audited + hardened: compile break fixed, precedence documented, teacher-override reads, 195/195 unit; merge blocked on CI with Docker ITs)
- [ ] T-027 Struggle inference v0: rule-based signals over learning log. (F-141) — v0.2 on branch `codex/session-6-diagnosis-policy` (prereq-gap / 3b fluency / 5a self-doubt; supersede-keeps-history, 7-day expiry enforced on reads, Map.entry NPE fixed; unsupported types never emitted, tested)
- [ ] T-028 Mastery map UI (KG visualizer, simplified 2D first) + student dashboard. (F-036, F-060, F-034)

## Wave 4 — pilot hardening

- [ ] T-029 Teacher minimal surface: class list, Smart Mark review queue, overrides.
- [ ] T-030 Research export (anonymized) + experiment registry v0. (F-146, F-154)
- [ ] T-031 Render deployment (Docker, keep-alive, cold-start UX) + Vercel production env. (F-001, F-156)
- [ ] T-032 Cycle-1 pilot readiness review against Master Spec §39a exit criteria.

## Deferred (do not start — Cycle 2+)

DAT / teacher analytics depth · gamification · mock-exam blueprints & Mock Drop · spaced-repetition scheduler UI · PWA/offline/mobile · community features · multimodal input · handwriting OCR · podcast/voice · LTI/white-labeling · full recommender · MLE/EM BKT recalibration (stretch: Apache Commons Math).

## Program-management tasks

- [ ] P-001 Review `PROGRESS.md` + update `WORKLOG.md` after each substantial task (protocol in `AGENT.md`).
- [ ] P-002 Update backlog row status/owner as work lands (spreadsheet is definitive).
- [ ] P-003 Re-verify Groq/Gemini free-tier limits at build time (limits drift).
- [ ] P-004 Pin exact opendataloader-pdf version + record license check in worklog.
