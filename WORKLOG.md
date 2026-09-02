# WORKLOG.md — SyllabAI Chronological Work Log

## 2026-09-02 — Project pack bootstrap (external assistant)

**Task:** Establish canonical engineering context for SyllabAI.

**Completed:**
- consolidated research-paper concepts into the Master Technical Specification (v1.0);
- defined Java 25 + Spring Boot 4.1.x backend; Next.js 16 frontend on Vercel; Neon PostgreSQL + pgvector;
- defined multi-repository, modular-monolith architecture;
- added learner-model, diagnostic, Smart Mark, provenance, research, and experiment architecture;
- converted the feature inventory into a definitive project-management workbook (158 rows).

**Findings:** the full architecture is broader than a chatbot (learner model, assessment, diagnostics, KG, provenance, telemetry are equally structural); Paper B's storage proposal simplifies operationally to PostgreSQL + pgvector behind abstractions; specialist parsers belong behind contracts, not inside Java.

## 2026-09-03 — Verification, merge, and repository bootstrap

**Task:** Independently verify the v1.0 pack, merge corrections, and stand up the GitHub repositories.

**Completed:**
- verified platform claims with 7 fresh searches: Spring Boot 4.1.1 (Java 17-26) ✅, Spring Boot 3.x EOL 2026-06-30 ✅, Spring AI 2.0 GA (requires Boot 4.x) ✅, Next.js 16.3.3 Active LTS (2026-08-25 security release) ✅, Cloudflare R2 free tier no-credit-card ✅, Groq free tier ~14.4K req/day no-card ✅, **SurrealDB = BSL 1.1, NOT Apache-2.0 ❌ (v1.0 dossier error)**;
- merged pack → v1.1: free-LLM chain added (Groq → Gemini 2.5 Flash → OpenRouter, ADR-009); Cycle-1 pilot scope locked (ADR-010, Master Spec §39a); polyglot policy (ADR-011); 4 repos (ADR-012); license wall (ADR-013); SurrealDB struck everywhere;
- merged backlog → v2: 160 rows; ADDED F-159 decay job, F-160 learning-log telemetry, F-161 Smart Mark κ gate, F-162 timed-vs-untimed fluency gap, F-163 free-LLM chain; PATCHED 10 legacy rows (F-001 AWS→Render/Vercel/Neon, F-008 Celery→Spring jobs, F-020/F-032/F-033/F-034/F-039/F-040/F-122 stack-contradiction fixes, F-047 κ metric); removed blank rows F-110/112/114; added `Cycle` column (34 Cycle-1 rows, 12-spine);
- integrated 38-repo Java-fit analysis into `REPOSITORY_RESEARCH.md` section 0 (verdicts: USE-DIRECT opendataloader-pdf/os-taxonomy/Scientific-learning-skills/pdfcn/A11Y.md; OFFLINE mineru/surya/anydoc/pdf-inspector; REFERENCE DeepTutor/get-it/Understand-Anything/open-notebook; WATCH zvec/helix-db/pgcontext; STRUCK SurrealDB);
- created GitHub repositories (private): `syllabai`, `syllabai-core`, `syllabai-web`, `syllabai-parser`; pushed this pack to `syllabai` (main repo).

**Mistakes / regressions:**
- Mistake (inherited from v1.0, corrected): SurrealDB recommended as Tier-A "Apache-2.0" backend — verified BSL 1.1 and struck (ADR-013). Any future doc claiming permissive licensing of an external repo must cite the license text, not the dossier.
- Mistake (caught pre-merge): v1.0 backlog contradicted its own ADRs (Neo4j rows vs ADR-005 Postgres graph; Celery row vs ADR-001 Java; Pinecone row vs ADR-004). All fixed and marked `PATCHED v2`.

**Breakthroughs / useful insights:**
- opendataloader-pdf is Java + Apache-2.0 on Maven Central — runs in-process inside `syllabai-core`; no separate parsing service for text PDFs; bounding boxes feed the citation chain.
- Pilot LLM budget fits Groq free tier: 50 students × ~20 queries/day ≈ 1K req/day vs ~14.4K/day capacity.
- Nothing in the 38-repo set implements BKT/BDT/IRT/telemetry/Smart Mark — the scientific core is greenfield Java, which is exactly the course project's showcase.

**Open questions:**
- Exact Edexcel IAL Chemistry content licensing posture for a private pilot (fine; re-check before any public flip).
- Gemini 2.5 Flash free-tier stability at build time (re-verify).
- κ-gate marker capacity for double-marking (recruiting task, Wave 4).

**Next action:** TODO T-001 — bootstrap `syllabai-core` (Spring Boot 4.1 + Java 25 + Spring AI 2.0 skeleton).

---

## 2026-09-03 — Build session: Wave 0 + science core (T-001…T-018, T-020, T-023)

**Repos / commits:**

- `syllabai-core` @ `71f873d` — T-001…T-007 + T-012/T-014…T-018/T-020/T-023 (see core README "Implemented so far").
- `syllabai-web` @ `3c410ed` — T-005 Learner Workbench (login, practice, mastery map, my state).

**What landed:**

- Java 25 + Spring Boot 4.1.1 + Spring AI 2.0.1 modular monolith; 13-module package map per ADR-012.
- Flyway V1–V7: identity (roles/users/user_roles), curriculum + KG nodes/edges, question bank + attempts, learner states, research telemetry/registries, seed (Edexcel IAL Chemistry WCH11: 3 topics × 2 subtopics, 4 documented misconceptions, 8 MCQs with distractor→misconception tags, model registry v1-cycle1 rows).
- JWT auth + RBAC; springdoc OpenAPI; global error handling; GH Actions CI (JDK 25).
- Science: BKT engine (paper params, config + model_versions registry), BDT engine (prior 0.3), Ebbinghaus decay (τ 30/90/365 by band, floor, review threshold) + nightly job; evidence contract as domain events (Observer): attempts → `AssessmentEvidenceRecordedEvent` → learner model + telemetry.
- KG: recursive-CTE prerequisite closure, subtree, misconceptions; tree/prereq/misconception endpoints.
- LLM: `LlmProvider` port + Spring AI adapters + `FailoverLlmChain` (Groq → Gemini → OpenRouter, health/cooldown/failover, admin health endpoint) — app boots with zero keys.
- Storage: `ObjectStorage` port + local + R2 (S3 SDK) adapters.
- Web: single-page workbench, typed API client, mobile-first responsive, a11y, CI (lint + type-checked build).

**Mistakes / regressions (caught and fixed):**

- MISCONCEPTION_OF edge direction inverted in `KnowledgeEdgeRepository` query → misconceptions silently absent from trees; fixed + re-verified.
- Spring AI autoconfig requires keys at boot → excluded all model autoconfigs; manual provider construction.
- Unauthenticated requests returned 403 via the /error dispatch → permitted `/error` + explicit 401 entry point.
- BKT/BDT unit-test expected values initially wrong (my arithmetic, not the engine) — corrected against hand-computed posteriors.
- Web `apiPath()` double-`?` when the path already carried a query (tree 404) — fixed with `&`-aware separator.

**Verification:**

- `mvn verify`: 32/32 unit tests green.
- Live end-to-end smoke (portable Postgres 17.11 + `local` profile): login → tree → prerequisites (depth-3 chain) → wrong answer (BKT 0.1131, BDT 0.75 exact) → correct answer (0.3832) → telemetry rows; RBAC 401/403; OpenAPI reachable; browser-verified via agent-browser (login, quiz submit, misconception alert, mastery map, state views, mobile viewport).

**Next action:** Wave 1 — T-008/T-009 canonical format + opendataloader-pdf; T-010/T-011 ingestion; T-013 pgvector; then T-019/T-021/T-022.
