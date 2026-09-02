# PROGRESS.md — Current SyllabAI State

**Last updated:** 2026-09-03 (Wave 0 + science core landed)

## Overall state

- Planning phase: **complete and converged** (stack verified, backlog merged, scope locked).
- Repositories: **bootstrapped on GitHub** (`syllabai`, `syllabai-core`, `syllabai-web`, `syllabai-parser` — private).
- Implementation: **started and green** — Wave 0 foundations (T-001…T-007) plus the science core (T-012, T-014…T-018, T-020, T-023) are implemented, unit-tested (32/32) and **live-verified end-to-end** against a real Postgres.
- `syllabai-core` @ `71f873d`: Spring Boot 4.1.1 / Java 25 / Spring AI 2.0.1; Flyway V1–V7 (identity, KG, assessment, learner, research + Edexcel IAL Chemistry WCH11 seed + 8 misconception-tagged MCQs); JWT RBAC (401/403 verified); recursive-CTE prerequisite closure; BKT/BDT/Ebbinghaus engines with paper parameters; evidence contract via domain events; free-LLM chain (boots with zero API keys); ObjectStorage (local + R2); CI.
- `syllabai-web` @ `3c410ed`: Next.js 16 Learner Workbench — login/register, practice player (confidence/doubt/timed), mastery map (tree + bars + prerequisite chain), my-state view; browser-verified against the live backend.

## Completed planning work

- Two research papers reviewed and translated into the engineering model (Master Spec v1.0 by external assistant).
- Independent verification pass (2026-09-03): Spring Boot 4.1/Java 25/Next 16.3/R2 confirmed; Spring Boot 3.x EOL + Spring AI 2.0 GA discovered; **SurrealDB "Apache-2.0" claim found false (BSL 1.1) and struck**; free-LLM strategy added (Groq → Gemini → OpenRouter, no credit card).
- Pack merged to v1.1: corrections applied to MASTER_SPEC / AGENT / DECISIONS / PLATFORM_RESEARCH / REPOSITORY_RESEARCH (section 0 verdicts).
- Backlog merged to v2: 160 rows; 5 research-fidelity rows added (F-159…F-163); 10 legacy rows fixed (Neo4j/Celery/FastAPI/Pinecone/AWS → actual stack); 3 blank artifacts removed; `Cycle` column added; **34 Cycle-1 rows, 12-spine critical path**.
- 38-repo research independently analyzed for Java/stack fit and licenses; verdicts integrated (opendataloader-pdf = in-process Java embed; zvec/HelixDB/pgcontext = watch; SurrealDB/PageLM/Chat2DB/open-knowledge/leantime/blockify = license wall).

## Current architecture (locked)

Java 25 + Spring Boot 4.1 + Spring AI 2.0 modular monolith (`syllabai-core`) · Next.js 16 on Vercel (`syllabai-web`) · polyglot offline parser (`syllabai-parser`) · Neon PostgreSQL + pgvector · Render free tier · Cloudflare R2 · free-LLM chain Groq → Gemini 2.5 Flash → OpenRouter (ADR-009) · license wall ADR-013 · 4 repos (ADR-012) · Cycle-1 pilot scope (ADR-010).

## Current known risks

- Free-tier cold starts (Render) and free-tier LLM rate drift — mitigated by keep-alive, provider chain, off-peak batching.
- Cycle-1 scope is ambitious (34 rows / 8 weeks) — the 12-spine critical path defines what must not slip; non-spine Cycle-1 rows may flex.
- Smart Mark κ ≥ 0.60 gate depends on human double-marking capacity — recruit markers early.
- Edexcel content licensing: pilot use under institution/own-use terms; verify redistribution posture before any public repo flip.
- BKT/BDT and struggle inference are research components — validation via simulation before deployment (F-139), never assumed.

## Latest findings / decisions

- Verified live (2026-09): the full science loop runs correctly — wrong answer on the mole/grams distractor produced BKT 0.1131 → 0.3832 and BDT 0.3 → 0.75/0.95, exactly matching hand-computed posteriors; telemetry observer logged ATTEMPT_SUBMITTED + SELF_DOUBT_FLAGGED.
- Fixed during live verification: MISCONCEPTION_OF edge direction was inverted in one repository query (misconceptions silently missing from trees); 403→401 error dispatch; CORS origin patterns for gateway previews.
- Spring AI 2.0 model autoconfiguration activates even without API keys — all model autoconfigs are excluded and providers are constructed manually in `LlmChainConfig` (§26.1 chain stays in our control).

- Finding: Spring Boot 3.x reached EOL 2026-06-30; Spring AI 2.0 requires Boot 4.x — v1.0 pack's Java 25/Boot 4.1 picks were correct and more current than earlier plans.
- Mistake (external, caught): v1.0 dossier listed SurrealDB as Apache-2.0 Tier-A backend — actually BSL 1.1; struck via ADR-013 before any code depended on it.
- Breakthrough: opendataloader-pdf is Java + Apache-2.0 on Maven Central — the parsing layer runs **in-process inside the Spring Boot monolith**, eliminating a whole service for text PDFs.

## Next highest-value work

Wave 1 — content fabric: T-008 (canonical document format), T-009 (opendataloader-pdf in-process), T-010/T-011 (Edexcel IAL spec + past-paper ingestion in `syllabai-parser`), T-013 (pgvector embeddings). Then Wave 2 remainder: T-019, T-021 Smart Mark, T-022 κ-gate workflow, and integration tests with Testcontainers in CI.
