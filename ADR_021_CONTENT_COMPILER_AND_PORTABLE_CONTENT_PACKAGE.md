# ADR-021: Content Compiler and Portable Content Package

**Status:** Proposed  
**Date:** 2026-09-15

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
