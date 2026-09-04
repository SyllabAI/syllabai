# PROGRESS.md — Current SyllabAI State

**Last updated:** 2026-09-04 (build session 4 — T-013 retrieval spine: canonical document store, deterministic chunking, Gemini embeddings, pgvector cosine search; The-Brain repo assessed)

## Overall state

- Planning phase: **complete and converged** (stack verified, backlog merged, scope locked).
- Repositories: **bootstrapped on GitHub** (`syllabai`, `syllabai-core`, `syllabai-web`, `syllabai-parser` — private).
- Implementation: **started and green** — Wave 0 foundations (T-001…T-007) plus the science core (T-012, T-014…T-018, T-020, T-023) are implemented, unit-tested (60/60) and **live-verified end-to-end** against a real Postgres.
- **Audit fixes 1–3 landed (session 2, core @ `508d95d`):** BDT correct answers now weaken monitored misconceptions; experiment pinning is real and fail-loud (config + experiments registry); all six V5 telemetry event types are emitted.
- `syllabai-core` @ `1803988`: Spring Boot 4.1.1 / Java 25 / Spring AI 2.0.1; Flyway V1–V10 (V8 multi-part assessment + marking, V9 telemetry marking events, V10 prompt/model registry); Flyway V1–V7 (identity, KG, assessment, learner, research + Edexcel IAL Chemistry WCH11 seed + 8 misconception-tagged MCQs); JWT RBAC (401/403 verified); recursive-CTE prerequisite closure; BKT/BDT/Ebbinghaus engines with paper parameters; evidence contract via domain events; free-LLM chain (boots with zero API keys); ObjectStorage (local + R2); CI.
- `syllabai-web` @ `3b1b5cd`: Next.js 16 Learner Workbench — login/register, practice player (MCQ + structured multi-part with pending-marks feedback, confidence/doubt/timed), mastery map (tree + bars + prerequisite chain), my-state view (incl. fluency-gap Δ); browser-verified against the live backend.
- `syllabai-parser` @ `a43ad24`: canonical document format (schema 1.0) + in-process OpenDataLoader adapter (Apache-2.0, opendataloader-pdf-core 2.5.7) + structure extractors v0; verified on the real 4CH0/1C Jan 2012 corpus (23/23 tests).
- **Build session 3 (content/assessment-first):** V8 multi-part assessment model (ExamPaper/QuestionVersion/QuestionPart/MarkScheme/MarkPoint/Answer/SmartMarkResult/HumanMark + κ evaluations); structured submission with timed/untimed pairing and single-fire evidence; Smart Mark as a Strategy pipeline (candidate generation → deterministic bounds/coverage/mark-sum validation → append-only results — LLM never final truth); Cohen's κ release gate (≥ 0.60, fail-closed, per-point pairing, threshold recorded); T-011 ingestion bridge (parser draft JSON → all-SUGGESTED content, teacher validation workflow, ingestion-anchor topic, idempotent); ServableQuestionSpec (unvalidated content never serves); fluency gap in skill states; Testcontainers integration test in CI. 91/91 unit tests.
- **Live-verified (session 3):** real 4CH0 draft ingested (27 q / 62 parts / 33 mark points) → version+scheme validated → student sees only validated structured question → timed structured submit → deterministic blank-answer smart mark → human mark (evidence once, BKT update, fluency gap paired) → κ = 1.00 gate PASSED → second smart mark authoritative (evidence without human) → telemetry SMART_MARK_COMPLETED / HUMAN_MARK_RECORDED. Browser: structured player submit → pending-marks panel; My-state renders Δ.
- **Audit fix 4:** experiment-pin model precedence hardened (pin > caller model > provider default); LlmResponse reports the model actually used; telemetry can no longer misattribute pinned-request models.
- **Build session 4 (T-013 retrieval spine, content-first):** V11 content module — canonical document store (parser schema 1.0 verbatim JSONB, checksum-idempotent, §8 invariants re-validated core-side), deterministic chunking (page+reading_order, block boundaries, element_ids provenance), `EmbeddingProvider` port + Gemini text-embedding-004 (768-dim; RETRIEVAL_DOCUMENT/RETRIEVAL_QUERY; **no failover by design** — a mixed-model index is inconsistent), `document_chunks.embedding vector(768)` + HNSW cosine search, teacher content APIs (ingest / embed / search), model-registry seed `content-embedding` (§19). 121/121 unit tests locally; `ContentPipelineIT` runs the real 4CH0/1C Jan 2012 fixtures end-to-end in CI (deterministic hashing embeddings — no network). The `spring-ai-google-genai-embedding` artifact was verified from Central before the adapter was written (chat starter does not pull it).
- **The-Brain (Hastur-HP, MIT) assessed:** 3D force-graph KG explorer + LightRAG/RAG-Anything pipeline dashboard — Tier-A reference for T-028 mastery-map UI and ingestion job/progress UX; not adoptable as runtime (Python/Docker/Neo4j, not free-tier-hostable). Verdict recorded in REPOSITORY_RESEARCH.md.

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
- Audit fix session (2026-09-03, external audit verified line-by-line first): BDT `updateOnCorrect` was dead code (correct options never tagged) — evidence now carries the monitored misconception set so correct answers weaken them (live: 0.9545→0.875 exact); experiment pinning implemented fail-loud (`ExperimentPinResolver` port, config + V5 registry); `BKT_UPDATED`/`BDT_UPDATED`/`REVIEW_SCHEDULED`/`DECAY_APPLIED` telemetry now flow; decay job review-threshold double-decay fixed.
- Spring AI 2.0 model autoconfiguration activates even without API keys — all model autoconfigs are excluded and providers are constructed manually in `LlmChainConfig` (§26.1 chain stays in our control).

- Finding: Spring Boot 3.x reached EOL 2026-06-30; Spring AI 2.0 requires Boot 4.x — v1.0 pack's Java 25/Boot 4.1 picks were correct and more current than earlier plans.
- Mistake (external, caught): v1.0 dossier listed SurrealDB as Apache-2.0 Tier-A backend — actually BSL 1.1; struck via ADR-013 before any code depended on it.
- Breakthrough: opendataloader-pdf is Java + Apache-2.0 on Maven Central — the parsing layer runs **in-process inside the Spring Boot monolith**, eliminating a whole service for text PDFs.

## Next highest-value work

**T-010 core-side syllabus ingestion** (parser-side CurriculumDraft extractor exists; IAL Chemistry spec → curriculum tables + KG seed) and the Past-Papers corpus batch run (parser CLI over the 689 MB corpus → canonical JSONs → teacher ingestion API). Then Wave 3: T-024 KA-RAG orchestration (hybrid KG + vector retrieval — its prerequisite T-013 landed in session 4), T-025 tutor chat UI with citations, T-027 struggle inference v0. Wave 4: T-029 teacher marking UI (APIs exist), T-031 Render deployment. LLM keys needed for real Smart Mark runs (Groq/Gemini free tier, ADR-009) — the no-key path fails honestly by design.
