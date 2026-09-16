> **VERIFICATION-HORIZON NOTICE — added 2026-09-15.** This dossier was verified in the first days of the project (2026-09-02/04). Free-tier limits, plans, quotas and licensing terms are time-sensitive and are now past their re-verification horizon (TODO item P-003 requires re-verify at build time). Re-check every time-sensitive claim against the provider before relying on it.

# SyllabAI Platform & Technology Research

**Verified:** 2026-09-02  
**Purpose:** Record the current technology/deployment research that underpins the SyllabAI Master Specification.

## Final recommendation

| Concern | Decision | Why |
|---|---|---|
| Web frontend | Next.js 16.3.x + React 19.x | Strong fit for Vercel; current 16.3 line is Active LTS and includes recent navigation/developer/agent improvements. |
| Java backend | Java 25 + Spring Boot 4.1.x | Meets Advanced OOP requirement; current Spring Boot 4.1.1 supports Java 17-26. |
| Java AI framework | Spring AI 2.0.x | GA 2026-06-12; requires Spring Boot 4.x (Boot 3.x reached EOL 2026-06-30); pgvector support + OpenAI-compatible endpoints (Groq). Source: https://spring.io/blog/2026/06/12/spring-ai-2-0-0-GA-available-now |
| Relational database | Neon PostgreSQL | Free plan is $0 with no credit card required and provides serverless/autoscaling/branching-oriented Postgres. |
| Vector search | pgvector on Neon | Avoids a separate vector DB; Neon documents pgvector support directly. |
| Java hosting | Render free Docker web service | Supports Docker and free web services; no-card free-tier route, but accepts cold starts and ephemeral filesystem. |
| Frontend hosting | Vercel Hobby | Natural fit for Next.js; free Hobby plan has included usage quotas. |
| Binary storage | Cloudflare R2 or other S3-compatible store | Current R2 free tier includes 10 GB-month standard storage, 1M Class A ops and 10M Class B ops; egress is free. |
| LLM inference | Groq llama-3.3-70b → Gemini 2.5 Flash → OpenRouter free models | $0, no credit card, verified 2026-09 (ADR-009). Paid providers allowed behind `LlmProvider` for experiments. |
| Embeddings | Gemini embedding API free tier | Primary `EmbeddingProvider`; dimension/model recorded alongside vectors. |
| CI | GitHub Actions | Standard GitHub-hosted runners are free for public repositories; private repos have included quotas. |

## Current evidence

### Spring Boot / Java

Spring Boot 4.1.1 requires at least Java 17 and supports up to Java 26. Maven 3.6.3+ and current Gradle 8/9 lines are supported. Source: https://docs.spring.io/spring-boot/system-requirements.html

**Decision:** Java 25 + Spring Boot 4.1.x.

### Next.js

The official Next.js project states that Next.js 16.3 is available, and its current security guidance says to upgrade to 16.3.3 (Active LTS) as of August 25, 2026. The 16.3 line includes instant navigations, partial prefetching and other performance/agent improvements. Source: https://nextjs.org/blog

**Decision:** Next.js 16.3.x, keeping minor/patch updates current within the compatible release line.

### Vercel

The Vercel Hobby plan is free and includes defined monthly resource allowances. The Vercel documentation also exposes usage controls/visibility. Sources: https://vercel.com/docs/plans/hobby and https://vercel.com/docs/pricing/manage-and-optimize-usage

**Decision:** Host the Next.js frontend on Vercel. Keep the Spring Boot API outside Vercel.

### Neon

Neon's current Free plan is $0, explicitly states no credit card is required, and currently includes 100 projects, 100 CU-hours per month per project, 0.5 GB storage per project, up to 2 CU, plus autoscaling, branching, read replicas and limited time-travel/restore. Source: https://neon.com/pricing

Neon also documents native pgvector support, allowing embeddings to be stored and searched inside PostgreSQL without a separate vector database. Source: https://neon.com/docs/ai/ai-concepts

**Decision:** Neon PostgreSQL + pgvector is the default SyllabAI data layer.

### Render

Render's Free web services can deploy Docker-based applications. Free instances spin down after 15 minutes of inactivity, may take about one minute to wake, have 750 free instance hours per workspace per month, and have ephemeral filesystems. Render also states that free instances are intended for testing/hobby use rather than production applications. Sources: https://render.com/docs/free and https://render.com/docs/docker

**Decision:** Render is the free/no-card Java hosting target for the academic project. The application must not depend on local filesystem persistence and must tolerate cold starts.

### Cloudflare R2

Current R2 pricing provides a free monthly allowance of 10 GB-month standard storage, 1 million Class A requests and 10 million Class B requests, with free Internet egress. Source: https://developers.cloudflare.com/r2/pricing/

**Decision:** Keep object storage behind an interface; R2 is a strong candidate for PDFs and other binary source materials.

### LLM / embedding free tiers (added in merge, verified 2026-09)

Groq's free developer tier requires no credit card and is the strongest free inference option: ~30 requests/minute, ~14,400 requests/day, ~30K tokens/minute, OpenAI-compatible API (`llama-3.3-70b-versatile` and other models). Sources: https://console.groq.com/docs/rate-limits and 2026 tier summaries.

Google Gemini 2.5 Flash maintains a free tier (~10 RPM / ~250 RPD class; volatile — re-verify at build time). The Gemini embedding API offers a separate free quota (~1,500 requests/day class).

OpenRouter offers ~50 requests/day on its no-card tier (rising to ~1,000/day after a one-time $10 top-up — acceptable as a tertiary fallback, not required).

Pilot budget check: 50 students × ~20 tutor queries/day ≈ 1,000 requests/day — comfortably inside Groq's free budget with room for Smart Mark batch runs queued off-peak.

**Decision (ADR-009):** default chain Groq → Gemini 2.5 Flash → OpenRouter behind `LlmProvider`/`EmbeddingProvider`, with health/rate tracking and per-experiment pinning.

### LLM provider chain — model drift register (added 2026-09-17)

The chain ORDER (ADR-009: Groq → Gemini → OpenRouter) is stable and accepted; the model IDENTIFIERS have drifted with provider catalog churn. States are recorded separately — do not claim deployed runtime state from YAML alone.

| Provider | DOCUMENTED (this dossier, 2026-09-02) | CONFIGURED (syllabai-core `application.yml` @ 8e1d27b) | DEPLOYED (Render runtime) | VERIFIED LIVE |
|---|---|---|---|---|
| Groq | `llama-3.3-70b-versatile` (retired for this key's account — catalog probe 2026-09-14) | `${SYLLABAI_GROQ_MODEL:openai/gpt-oss-120b}` (env-bridged) | Unknown from repository evidence — Render may set `SYLLABAI_GROQ_MODEL` | Not re-verified in the authoring environment (no credentials) |
| Gemini | `2.5 Flash` (no longer available to accounts created after its retirement window — YAML finding 2026-09-14) | `gemini-3.6-flash` (hard-coded) | Presumed = CONFIGURED (no env bridge defined); unverified | Not re-verified |
| OpenRouter | "free models" (`llama-3.3-70b-instruct:free` retired; free inventory rotated) | `nvidia/nemotron-3-super-120b-a12b:free` (probe-verified 200 / 2.4 s against the production key 2026-09-14) | Presumed = CONFIGURED; unverified | 2026-09-14 probe recorded in the YAML comment — predates this register |

Re-verification rule (ADR-009): free-tier catalogs drift weekly — verify at build time and record the probe (provider, model, timestamp, result) here.

### License correction — SurrealDB (struck)

SurrealDB is **not** Apache-2.0, contrary to the v1.0 repository dossier. Its core is licensed under the **Business Source License 1.1** (not open source; commercial/production use restricted; GitHub license field returns NOASSERTION). Sources: https://surrealdb.com and the BSL 1.1 text in the repository.

**Decision (ADR-013):** SurrealDB is struck from all candidate tiers. PostgreSQL (Neon) + pgvector remains the sole default substrate. `lfnovo/open-notebook` (which uses SurrealDB internally) stays a reference architecture only — usable locally as an internal mining tool, never embedded or deployed as SyllabAI infrastructure.

### GitHub Actions

GitHub states that standard GitHub-hosted runners are free for public repositories; private repositories receive plan-dependent free quotas and charges may apply beyond those quotas. Source: https://docs.github.com/en/actions/concepts/billing-and-usage

**Decision:** Use GitHub Actions for CI/CD, keeping public infrastructure repositories free where appropriate and monitoring private-repo quota.

## Alternatives considered

### Supabase

Supabase Free currently includes PostgreSQL, 500 MB database, 5 GB egress, 1 GB file storage, 50,000 MAU and two active projects, but free projects pause after one week of inactivity. Source: https://supabase.com/pricing

**Why not default:** Supabase is excellent and remains an approved alternative, especially if integrated auth/storage becomes more important than keeping a plain Postgres-first architecture. Neon better matches the current SyllabAI separation of concerns and pgvector requirement.

### Railway

Railway provides a trial/free-credit model but is less aligned with a strict no-credit-card/no-billing-dependency requirement for this project.

**Decision:** Do not make Railway the baseline.

### Neo4j

Still allowed through the graph abstraction, but not required as a separately hosted P0 dependency. PostgreSQL graph tables reduce infrastructure while preserving a clean domain interface.

### Pinecone / Weaviate

Still allowed through `VectorStore`, but not the default. pgvector keeps the system simpler and avoids a second paid/free-tier dependency.

## Important cost separation

Infrastructure AND default LLM inference now sit on verified free tiers (ADR-009), so the Cycle-1 pilot runs at **$0 with no credit card**. Paid providers remain available behind the `LlmProvider` abstraction for experiments that specifically need them; free-tier limits are not a production SLA and must be re-verified at build time.

## Final platform topology

```text
Browser
  ↓
Vercel / Next.js
  ↓ HTTPS
Render / Spring Boot / Java 25
  ↓
Neon PostgreSQL + pgvector
  │
  ├── application data
  ├── knowledge graph
  ├── learner state
  ├── assessments
  ├── telemetry
  └── embeddings
  ↓
Object storage (R2/S3-compatible)

Specialist processing:
MinerU / OpenDataLoader / Surya / anydoc / pdf-inspector

AI (free chain, ADR-009):
Groq llama-3.3-70b (primary) / Gemini 2.5 Flash / OpenRouter / Ollama — behind LlmProvider + EmbeddingProvider
```

## Constraints to retain

- Free-tier limits are not a production SLA.
- Render free services sleep and restart.
- Local files on Render are ephemeral.
- Vercel Hobby has usage limits and plan constraints.
- Neon Free has bounded compute/storage.
- AI inference may incur external cost.
- Data/source/model licensing must be checked separately from infrastructure pricing.

## FreeLLMAPI — primary-source research (added 2026-09-17)

**Status: PROPOSED / EXPERIMENTAL — researched, NOT implemented, NOT accepted for production learner traffic (ADR-023).** Subject: `tashfeenahmed/freellmapi`. Primary sources: repository README, LICENSE, `docs/en/architecture/00-high-level-index.md` (incl. its maintained per-provider ToS review), retrieved 2026-09-17.

**Architecture.** Self-hosted, single-user, local-first OpenAI-compatible proxy/aggregator (TypeScript, Node 20+, Express on :3001; Docker Compose or desktop app). Routes ONE /v1 endpoint over ~34 free providers (its signed catalog tracks 474 model families / 635 free endpoints) using YOUR OWN free-tier keys: provider keys AES-256-GCM-encrypted in local SQLite, decrypted in-memory per request. Flow: Express proxy → Router (highest-priority model with a healthy key under all its rate limits) → provider SDK. NOT a hosted request service — prompts/completions never transit freellmapi.co; the only outbound dependency is a twice-daily SIGNED model-catalog sync (Ed25519-pinned; the free build trails ~30 days; the paid "Premium" tier only accelerates that feed — the router stays MIT/free either way).

**Licensing.** MIT for the router + dashboard; Premium is a paid catalog-feed service, not a license change.

**Terms-of-Service considerations.** The project maintains a per-provider ToS review (May 2026): Groq / Cerebras / Mistral / OpenRouter "likely OK" for a private single-user proxy; Google Gemini "caution" (2026 clause narrowing to professional/business purposes); NVIDIA NIM and GitHub Models "caution" (evaluation/prototyping scope); Cohere flagged "avoid". The project's own rules of thumb: one account per provider, no reselling, no endpoint sharing, no free tier as a paid production backend. Its own disclaimer states the software is "for personal experimentation and learning, not production."

**Privacy.** Keys and analytics stay local; no prompt/key telemetry reaches the catalog server (per project docs); response cache and prompt compression are opt-in. Self-hosting is the only mode — the privacy posture is adequate when self-hosted, and only self-hosted.

**Operational model.** One more always-on service (Render Docker service or equivalent) with persistent SQLite storage; health probes, cooldowns on 429/5xx, RPM/RPD/TPM/TPD ledger, six routing strategies, 30-minute sticky sessions. Project-stated limitations: no frontier models, variable latency, no SLA, effective intelligence dips late in the day.

**API compatibility.** OpenAI-compatible `/v1/chat/completions` including tools and structured outputs — Spring AI's `OpenAiChatModel` can point at it via `base-url` (the same adapter path as Groq/OpenRouter). No SyllabAI code exists for it (correctly, per ADR-023).

**Failure behavior.** Internal per-model failover with cooldowns and learned per-key ceilings — a router INSIDE what would be a single SyllabAI chain member; opaque to `FailoverLlmChain` observability (the chain sees one member, not the internal model switches).

**Quota behavior.** Per-key RPM/RPD/TPM/TPD counters that learn providers' reported ceilings; routing stays under the caps of the keys you feed it. No quota is created — it only aggregates the same free tiers SyllabAI can use directly.

**Security.** Local login-gated dashboard; keys encrypted at rest; the endpoint must not be reachable by third parties (single-user assumption — sharing it violates the ToS rules of thumb above).

**SyllabAI suitability.** Marginal for production: SyllabAI already uses the same underlying free tiers DIRECTLY through its own chain (classification, budgets, cooldowns, experiment pinning — all observable and platform-owned). Inserting FreeLLMAPI adds a second routing layer with duplicated semantics and reduced per-provider observability, plus a second always-on service to operate, in exchange for capacity from providers SyllabAI has not yet registered. Its own "not production" disclaimer does not meet the pilot's reliability bar for learner-serving traffic.

**Known unknowns.** (1) Multi-key behavior (bulk import exists — account-pooling temptation; ADR-023 rejects it); (2) behavior under sustained SyllabAI-shaped load (never benchmarked here); (3) catalog-sync behavior when offline or blocked; (4) structured-output fidelity across heterogeneous internal models against SmartMark's strict-JSON contract.

**Verdict.** PROPOSED / EXPERIMENTAL — keep out of production. If ever promoted: existing `SpringAiChatModelAdapter` + OpenAI-compatible base-url, optional chain member, experiment-pinnable, benchmarked via the Slice-G harness, fresh ToS review at promotion time.
