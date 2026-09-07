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

**Status:** Accepted
**Date:** 2026-09-03

Repositories are `syllabai`, `syllabai-core`, `syllabai-web`, `syllabai-parser`, plus the public `Past-Papers` corpus repository described in the current Master Spec and Project Context. The former syllabai-knowledge/-assessment/-learner-model/-ai/-research/-infrastructure repos become strongly-separated modules inside the `syllabai-core` monolith. They graduate to repositories only when a genuine runtime/lifecycle boundary appears. Rationale: solo + AI-agent development; many repos of mostly-empty stubs create process overhead at pilot scale.

## ADR-013: License wall for external code and data

**Status:** Accepted
**Date:** 2026-09-03

Only permissively licensed code/data (MIT, Apache-2.0, ISC, ODbL with attribution) may be embedded in SyllabAI. BSL 1.1, AGPL, GPL, source-available, and custom/community licenses are reference-only. **SurrealDB is reference-only** (BSL 1.1). Also reference-only: Chat2DB, PageLM, Blockify, SurfSense, open-knowledge, Leantime. Surya model weights and the SocraticLM dataset carry separate non-permissive terms.

## ADR-014: Subject-first student experience and first-class specification points

**Status:** Accepted
**Date:** 2026-09-07

SyllabAI's long-term student product is organized around **subject enrollments**, not a single mixed-subject dashboard. A student can begin with zero subjects, then add courses through `Board → Qualification → Subject → Curriculum/Specification Version`. Each enrolled subject becomes a self-contained workspace containing its academic resources, assessment tools, tutor context, learner state, and subject knowledge graph.

The curriculum model is extended from `Subject → Unit → Topic → SubTopic` to:

```text
Board → Qualification → Subject → CurriculumVersion
  → Unit/Section → Topic/SubTopic → SpecificationPoint
```

A `SpecificationPoint` is a first-class curriculum/knowledge anchor for the official numbered learning objectives found in detailed board specifications. It preserves official code, verbatim objective statement, ordering, curriculum version, source provenance, and applicability metadata. Agents must not flatten these objectives into generic tags or invent numbering.

Resources such as Revision Notes, Flashcards, and Smart Lesson steps should map to specification points. Future QuestionVersion/QuestionPart tagging may map one question to multiple specification points and must preserve uncertainty/review state. This extends F-152 rather than replacing it.

The stable curriculum graph and mutable learner state remain separate. Mastery, misconception, confidence, procedural fluency, evidence, and review state are overlays keyed to the relevant subject/curriculum graph nodes; they never mutate official curriculum content.

The detailed decision and implementation blueprint is canonical in `SUBJECT_ARCHITECTURE.md`.

**Scope guard:** this ADR changes the product architecture, not the active pilot scope. Cycle 1 remains Edexcel IAL Chemistry under ADR-010. IGCSE Chemistry is a supported target architecture/example, not authorization to begin IGCSE bulk ingestion.

## ADR-015: Role-aware teacher/classroom LMS layer over the shared subject graph

**Status:** Accepted
**Date:** 2026-09-07

SyllabAI's long-term product includes a role-specific **Teacher/Classroom/LMS layer** built over the same Board → Qualification → Subject → CurriculumVersion → SpecificationPoint graph, question bank, content system, assessment evidence, and learner-model substrate used by students.

Teachers are subject-scoped. Clicking a taught subject opens a teacher workspace containing subject resources plus teacher workflows such as Classes, Assignments, Test Builder, Mock Exams, Announcements, Knowledge Graph, At-Risk Students, reports, Teacher AI Assistant, and Data Assistant. Smart Lesson remains primarily a student-facing adaptive workflow unless a later decision adds a teacher-specific variant.

There are two student interface modes over one identity and learner model:

```text
Independent student
  └── subject workspace

Classroom-enrolled student
  └── same subject workspace
       └── Announcements + Assignments + My Results/Feedback
```

Class enrollment is an additional capability/authorization relationship, not a second account or second learner model.

The teacher Knowledge Graph is a **different lens over the same graph**, not a separate curriculum graph. It adds a teaching-coverage overlay and class-level aggregation of learner state. `NOT_TAUGHT` is semantically distinct from `LOW_MASTERY`; grey nodes may indicate absent teaching coverage, while taught nodes may be colored by class understanding. Class aggregates should preserve distributions, evidence counts, and misconception prevalence rather than relying on mean mastery alone. Teachers must be able to drill down from class node → affected students → individual student graph → evidence → teacher action.

The Teacher AI Assistant and Data Assistant are separate capabilities:
- Teacher AI Assistant: grounded academic/content/teaching copilot.
- Data Assistant: authorized structured analytics assistant that summarizes class/student evidence and never invents marks, counts, dates, or risk labels.

At-Risk Students is evidence-first. Every flag must be inspectable and should expose contributing evidence plus the relevant rule/model version. Teacher-facing AI-generated questions/resources remain drafts until they satisfy the project's validation/content-serving policy.

The existing F-050 Test Builder remains the canonical feature identity for teacher test creation. The new requirement is an **evidence-driven enhancement**, not a duplicate feature: specification-point, skill, misconception, class-weakness and teaching-coverage targeting may augment the existing builder while retaining manual question selection, reuse/edit behavior and PDF export.

`T-029` is a minimal current teacher review surface, not the complete teacher product. Its Cycle-1-era roster implementation intentionally uses the enabled STUDENT cohort because a persistent Class domain entity is not yet part of the pilot. Future Class Management must introduce the explicit class/membership model rather than treating the pilot shortcut as final architecture.

The complete teacher/classroom/LMS blueprint is canonical in `TEACHER_ARCHITECTURE.md`.

**Scope guard:** ADR-015 defines the long-term product architecture and does not expand Cycle 1. Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010.
