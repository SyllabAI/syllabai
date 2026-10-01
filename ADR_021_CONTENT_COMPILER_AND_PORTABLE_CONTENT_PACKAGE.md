# ADR-021: Content Compiler and Portable Content Package

**Status:** Accepted  
**Date:** 2026-09-15 (proposed) · 2026-09-29 (accepted)

## Context

SyllabAI already uses Markdown in content workflows, including Revision Notes and GLM-OCR-derived QP/MS artifacts. The project also uses PostgreSQL as the canonical operational store and retrieval projections such as pgvector.

The system needs a durable, human-readable content representation and a portable corpus artifact without creating a second canonical database or weakening provenance/validation boundaries.

## Decision

1. **Markdown is a first-class durable content/interchange representation** for Revision Notes and parser/OCR-derived QP/MS artifacts.
2. **PostgreSQL remains the canonical operational/domain representation** for validated educational content and runtime relationships.
3. SyllabAI will design a **SyllabAI-specific SQLite Content Package** as a derived portable/reproducible corpus, QA, research and distribution format.
4. SQLite packages are not authoritative learner state, curriculum truth, KG truth, or production multi-user storage.
5. Generic **MarkdownDB is not adopted as a core dependency**. It may be evaluated later behind the package contract if a concrete need exists.
6. A package or Markdown artifact does not bypass existing validation, authorization or learner-serving gates.

## Consequences

### Positive

- Revision Notes can be human-readable, Git-versioned, reviewable and reproducible.
- QP/MS parser output becomes an explicit evidence-bearing artifact rather than an opaque intermediate.
- Agents can restore a known content snapshot after sandbox resets without necessarily rerunning OCR/parser stages.
- A SQLite package can support offline QA, evaluation, replay and controlled distribution.
- Retrieval providers can consume derived representations without becoming the canonical educational store.

### Risks

- Multiple representations can drift if they become independently editable.
- A generic Markdown indexing dependency could leak implementation semantics into the domain model.
- Package schemas can become an accidental second database if not governed as projections.
- Packaging unvalidated assessment content could create a serving-boundary bypass.

### Controls

- Domain semantics remain canonical in SyllabAI's validated model/PostgreSQL.
- Markdown and SQLite are controlled artifacts/projections.
- Stable IDs, source SHA-256, parser/compiler versions and lifecycle state are preserved.
- Package builds fail closed on required identity/provenance/validation failures.
- Learner serving continues to require the existing validation gates.
- Promotion from `PROPOSED` requires implementation evidence and bounded reproducibility tests.

## Initial implementation boundary

The first implementation should be a bounded **Content Package v0.1** proof covering:

- Revision Note frontmatter;
- QP/MS artifact manifests;
- a deliberately small SQLite schema;
- package manifest and SHA-256 generation;
- clean-environment reconstruction;
- identity/provenance/lifecycle verification.

Do not perform a broad corpus migration or replace PostgreSQL until this proof is successful and explicitly promoted.

## Canonical documents

- `CONTENT_COMPILER_AND_PACKAGE_ARCHITECTURE.md` — architecture and boundaries.
- `CONTENT_PACKAGE_V0_1.md` — initial package contract.

## Scope

This ADR does not change Cycle-1 product scope and does not authorize bulk ingestion, learner-serving changes, or a production database migration.

## Promotion record

**2026-09-29 — PROPOSED → ACCEPTED** (operator decision, chat bb263437, trace 1a0e9f879a8d8fe1). The ADR's own gate — "Promotion from `PROPOSED` requires implementation evidence and bounded reproducibility tests" — is satisfied by two executed, CI-verified evidence bodies, both re-verified GREEN at current main on promotion day:

1. **Bounded real-corpus v0.1 reconstruction proof** (`SyllabAI/syllabai-parser` `tools/content-package-v0.1/`, recorded in `CONTENT_PACKAGE_V0_1_IMPLEMENTATION_STATUS.md`): one real Revision Note (operator-`HUMAN_VALIDATED` spec mappings) + one real learner-servable VALIDATED QP/MS pair (complete marking contract), compile → package (Markdown + SQLite + MANIFEST with SHA-256) → clean-room semantic reconstruction (`R3.1`–`R3.9` all equal), negative gates fail closed with no package created (`N1`–`N5`), deterministic provenance binding. parser-ci `content-package-proof` job GREEN — re-verified run `36161511189` at parser main `55166af`.
2. **Hub-corpus v0.1 tooling — the full production corpus** (ADR-029 tranche 4.12, hub `0c589de`, evidence `download/s135/`): `tools/content-package/` compiles all 49 courses / 346 artifacts / 82.8 MB → `MANIFEST.json` (identity + per-artifact SHA-256 + counts + findings) + verbatim content copies + SQLite v0.1 projection; gates `G1`–`G5`/`V1`–`V8`/`R1`–`R4` fail closed; byte-deterministic SQLite + clock-free buildId enforced in CI (selftest: compile + verify + restore + determinism + tamper); NO serving change — PostgreSQL + `content/` remain the operational truth. Selftest step re-verified GREEN at hub main `9a00eb1` (hub-ci run `36487846248`). Evidence: `download/s136/`.

**Scope of acceptance:** the six decision points above and the bounded v0.1 package contract as implemented. **Not authorized by this promotion:** bulk corpus migration, replacement of PostgreSQL, package-driven learner serving, or the broader architecture claims (KG projection policy, distribution/versioning at scale, canonical-store integration) — those remain staged in `CONTENT_COMPILER_AND_PACKAGE_ARCHITECTURE.md` (which stays PROPOSED) until separately proven. Any future scope growth re-opens the record, not this promotion.
