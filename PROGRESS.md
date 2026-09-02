# PROGRESS.md — Current SyllabAI State

**Last updated:** 2026-09-03

## Overall state

- Planning phase: **complete and converged** (stack verified, backlog merged, scope locked).
- Repositories: **bootstrapped on GitHub** (`syllabai`, `syllabai-core`, `syllabai-web`, `syllabai-parser` — private).
- Implementation: **not yet started** (next: TODO T-001, core skeleton).

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

- Finding: Spring Boot 3.x reached EOL 2026-06-30; Spring AI 2.0 requires Boot 4.x — v1.0 pack's Java 25/Boot 4.1 picks were correct and more current than earlier plans.
- Mistake (external, caught): v1.0 dossier listed SurrealDB as Apache-2.0 Tier-A backend — actually BSL 1.1; struck via ADR-013 before any code depended on it.
- Breakthrough: opendataloader-pdf is Java + Apache-2.0 on Maven Central — the parsing layer runs **in-process inside the Spring Boot monolith**, eliminating a whole service for text PDFs.

## Next highest-value work

TODO T-001 → T-007 (Wave 0 foundations): core skeleton, Flyway/Neon, security, REST conventions, web scaffold, CI, R2 adapter. Then T-008+ content fabric.
