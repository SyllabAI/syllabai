# DECISIONS.md - SyllabAI Architecture Decision Records

## ADR-001: Java is the core backend language

**Status:** Accepted  
**Date:** 2026-09-02

SyllabAI's application backend will be Java 25 + Spring Boot 4.1.x. This satisfies the Advanced Object Oriented Programming requirement and provides a strong domain-oriented architecture.

Specialist OCR/document/ML workloads may live in independent repos and runtimes behind stable contracts.

## ADR-002: Next.js for the web frontend

**Status:** Accepted

Use Next.js 16.x + React 19.x + TypeScript for the website. Deploy the frontend to Vercel. Do not move the Spring Boot backend into Vercel functions.

## ADR-003: Multi-repository architecture

**Status:** Accepted

Separate genuinely independent subsystems such as parsing, learner modeling, knowledge tooling, assessment, AI, research, and infrastructure. Keep the main application a modular monolith rather than premature microservices.

## ADR-004: Neon PostgreSQL + pgvector

**Status:** Accepted

Use Neon PostgreSQL as the default hosted system of record and pgvector as the default vector layer. This keeps the free architecture simple and avoids an unnecessary dedicated vector database.

## ADR-005: PostgreSQL-backed knowledge graph first

**Status:** Accepted

Represent the curriculum/knowledge graph using relational graph tables and recursive queries initially. Hide the graph behind an interface so Neo4j/HelixDB/etc. can be introduced without changing domain logic.

## ADR-006: Render for free Java backend hosting

**Status:** Accepted with constraint

Use a Dockerized Spring Boot service on Render's free tier under the no-credit-card requirement. Accept cold starts/ephemeral filesystem limitations. Design the application so no important state depends on the instance filesystem.

## ADR-007: Master Spec vs research papers

**Status:** Accepted

The Master Spec is the engineering source of truth. The papers remain authoritative for research claims, definitions, hypotheses, and evaluation design. Agents read the relevant paper section when scientific meaning changes.

## ADR-008: Spreadsheet as definitive feature tracker

**Status:** Accepted

The definitive workbook records feature IDs, status, priority, dependencies, implementation repo, validation metrics, and other execution metadata. Any newly discovered capability must be added there rather than left only in prose.

## ADR-009: Free-tier LLM provider chain ($0, no credit card)

**Status:** Accepted
**Date:** 2026-09-03

All AI inference for the Cycle-1 pilot runs on verified free tiers behind `LlmProvider`: Groq `llama-3.3-70b-versatile` (primary, ~14,400 req/day, OpenAI-compatible), Gemini 2.5 Flash (fallback), OpenRouter free models (tertiary). Embeddings: Gemini embedding API. Automatic failover with per-experiment provider pinning. Paid providers stay allowed for experiments that need them; no Cycle-1 feature may hard-depend on a paid model. Verified limits recorded in `PLATFORM_RESEARCH.md`. Re-verify limits at build time — free tiers drift.

## ADR-010: Cycle-1 pilot scope (execution override)

**Status:** Accepted
**Date:** 2026-09-03

The authoritative execution scope is Paper B's Cycle-1 pilot: Edexcel IAL Chemistry, ~50 retake-path students, 8 weeks, Tutor + Assessor agents only, predictions P1–P8. Backlog rows marked `Cycle 1` (34 rows; 12-spine critical path) define the cut. The build waves remain the full-system roadmap, but Cycle 2+ features must not be pulled into Cycle 1. Exit criteria in Master Spec §39a (κ ≥ 0.60 Smart Mark gate; Paper B §3.5 telemetry fields live).

## ADR-011: Polyglot policy — Java preferred, best language wins per component

**Status:** Accepted
**Date:** 2026-09-03

Java (25, Spring Boot 4.1, Spring AI 2.0) owns the domain core — the Advanced OOP course requirement and the strongest domain-model fit. Components where another ecosystem is clearly better may use that language: web frontend in TypeScript (Next.js), offline OCR/ML parsing in Python/Rust (MinerU/Surya) inside `syllabai-parser`. Where the choice is a tie, Java wins (e.g. opendataloader-pdf — Java + Apache-2.0, embeddable in-process via Maven, no extra runtime).

## ADR-012: Four repositories now; module repos deferred

**Status:** Accepted (supersedes the 10-repo tree in spec v1.0 §3)
**Date:** 2026-09-03

Repositories: `syllabai` (main pack), `syllabai-core`, `syllabai-web`, `syllabai-parser`. The former syllabai-knowledge/-assessment/-learner-model/-ai/-research/-infrastructure repos become strongly-separated modules inside the `syllabai-core` monolith. They graduate to repositories only when a genuine runtime/lifecycle boundary appears. Rationale: solo + AI-agent development; 10 repos of mostly-empty stubs is process overhead with zero payoff at pilot scale.

## ADR-013: License wall for external code and data

**Status:** Accepted
**Date:** 2026-09-03

Only permissively licensed code/data (MIT, Apache-2.0, ISC, ODbL with attribution) may be embedded in SyllabAI. BSL 1.1, AGPL, GPL, source-available-with-conditions, and custom/community licenses are reference-only. **SurrealDB is struck from all tiers** (spec v1.0 dossier listed it as "Apache-2.0" — verified false: it is BSL 1.1; surrealdb.com and GitHub confirm). Also reference-only: Chat2DB, PageLM, Blockify, SurfSense, open-knowledge, Leantime. Surya model weights (modified-OpenRAIL) and the SocraticLM dataset (CC-BY-NC) carry separate non-permissive terms — inspiration, never redistribution.
