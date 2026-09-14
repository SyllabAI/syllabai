# Content Compiler and Portable Content Package Architecture

**Status:** PROPOSED  
**Date:** 2026-09-15  
**Scope:** Revision Notes, parsed/OCR QP/MS artifacts, portable content/QA/research bundles

## 1. Decision summary

SyllabAI should treat **Markdown as a durable, versionable content/interchange representation** for Revision Notes and parser/OCR-derived question-paper (QP) and mark-scheme (MS) artifacts.

PostgreSQL remains the **canonical operational/domain representation** for validated educational content and runtime relationships.

SyllabAI should introduce a **SyllabAI-specific SQLite Content Package** as a derived, portable, reproducible corpus/QA/research/distribution format. SQLite is not a replacement for PostgreSQL and is not an authoritative learner, curriculum, or KG store.

Generic MarkdownDB is **not adopted as a core dependency**. Its general Markdown indexing pattern may be referenced during implementation research, but SyllabAI's semantics, provenance, validation and domain model remain SyllabAI-owned.

## 2. Why this fits the existing architecture

The project already uses Markdown in content workflows, including revision-note corpus material and GLM-OCR QP/MS outputs. This proposal formalizes that existing pattern rather than introducing a competing content model.

The design preserves the existing invariants:

- SyllabAI owns curriculum and educational semantics.
- SpecificationPoints remain first-class canonical anchors.
- Validated assessment content is the only learner-servable assessment content.
- Authoritative educational KG semantics remain distinct from retrieval-derived structures.
- Embeddings and retrieval indexes are projections/signals, not educational truth.
- PostgreSQL remains the production operational source for the domain model.
- External retrieval providers remain subordinate to SyllabAI provenance and validation.

## 3. Representation layers

```text
                    OFFICIAL / AUTHORING SOURCES
                               |
                               v
                     Parser / OCR / Authoring
                               |
                               v
                    Canonical Markdown Artifact
                               |
                    validation / normalization
                               |
                               v
                     SyllabAI Domain Objects
                         /               \
                        /                 \
                       v                   v
                 PostgreSQL            SQLite Package
                 runtime truth       portable projection
                       |                   |
                       v                   v
             KG / assessment /      QA / offline / research /
             learner / Tutor        replay / distribution
                       |
                       v
                Retrieval projections
             pgvector / BM25 / providers
```

Markdown, PostgreSQL and SQLite are therefore **not three independent sources of truth**. The domain semantics are canonical; Markdown and SQLite are controlled representations/projections.

## 4. Revision Notes

Revision Notes are suitable for Git-versioned Markdown authoring and durable content interchange.

A note should carry machine-readable frontmatter containing, at minimum:

- stable note identity;
- resource/content type;
- lifecycle/validation status;
- subject and qualification;
- curriculum/specification version where applicable;
- SpecificationPoint mappings;
- concept/KG references where validated;
- source/provenance reference;
- content version.

The Markdown body remains human-readable and should not duplicate domain data unnecessarily. Rich structured semantics belong in the validated domain model and/or explicit frontmatter fields when they are required to make the artifact independently identifiable.

Recommended lifecycle:

```text
Markdown authoring/import
        -> schema/frontmatter validation
        -> provenance validation
        -> educational mapping validation
        -> normalization
        -> PostgreSQL projection
        -> retrieval projections
```

A note must not become learner-servable merely because a Markdown file exists. Existing content validation/serving gates remain authoritative.

## 5. QP/MS Markdown

Parser/OCR Markdown should be treated as a reproducible parser artifact, not merely an unstructured text dump.

A QP/MS artifact should preserve:

- document identity;
- source PDF identity and SHA-256 provenance;
- parser/OCR implementation and version;
- source paper/session identity;
- document type (QP or MS);
- structural question/part boundaries where extracted;
- parser findings and reconciliation metadata where applicable;
- validation status.

Recommended corpus shape:

```text
paper/<paper-id>/
  manifest.yaml
  question-paper.pdf
  question-paper.md
  mark-scheme.pdf
  mark-scheme.md
```

The Markdown is an evidence-bearing intermediate representation. It must not silently overwrite or invent assessment semantics. Structural ambiguity should remain observable through findings/review state until resolved by the governed ingestion pipeline.

## 6. SQLite Content Package

The SQLite artifact is a **compiled projection/package**, not a generic Markdown index.

A future package may contain tables/projections such as:

```text
resource
resource_version
resource_provenance

specification
specification_point

revision_note
revision_note_specification_point

paper
paper_question
question_part
mark_scheme
mark_point
mark_point_question_part

parser_run
validation_finding

kg_node
kg_edge
```

Only validated/approved semantics should be represented as authoritative package projections. Staged, quarantined, suggested or review-required content must retain explicit lifecycle state and must never be mistaken for learner-servable content.

The package should be accompanied by a manifest containing at least:

- package schema version;
- package build/compiler version;
- source artifact identities and hashes;
- creation timestamp;
- included corpus/version scope;
- validation/build status;
- deterministic-build metadata where feasible.

## 7. Portable bundle

A distribution bundle may eventually take the form:

```text
syllabai-content-<scope>-<version>.zip
|
+-- content/
|   +-- revision-notes/*.md
|   +-- papers/*/*.md
|   +-- manifests/*.yaml
|
+-- database/
|   +-- content.sqlite
|
+-- MANIFEST.json
```

This is especially useful for:

- sandbox/reset recovery;
- parser and ingestion QA;
- reproducible evaluation corpora;
- agent-local development;
- offline tooling;
- transfer between environments;
- evidence/replay of a known corpus snapshot.

The bundle is a **derived snapshot**. It does not replace the canonical repositories or production database.

## 8. Compiler contract

The long-term implementation should be treated as a Content Compiler rather than a generic database synchronizer:

```text
source PDFs / authored Markdown / structured source
        |
        v
identity + provenance
        |
        v
parse / normalize
        |
        v
validate
        |
        v
map to SyllabAI domain semantics
        |
        +----> PostgreSQL projection
        |
        +----> Markdown artifact / normalized artifact
        |
        +----> SQLite Content Package
        |
        +----> retrieval indexes
```

The compiler must be deterministic where practical, preserve source identity, and fail closed when required provenance or validation invariants are not satisfied.

## 9. Reconstruction and reproducibility goals

A package should make it possible to reconstruct a known local working corpus without re-running expensive OCR/parser stages when the source artifacts and package are valid.

Target invariant:

```text
same source identities
+ same compiler/schema version
+ same accepted validation state
        => equivalent package/domain projection
```

Byte-for-byte determinism is desirable for package artifacts but is not assumed until implemented and tested.

## 10. SQLite boundaries

SQLite is appropriate for:

- portable content packages;
- local/offline content inspection;
- parser intermediate state where a relational local store helps;
- reproducible retrieval/evaluation datasets;
- QA/replay fixtures;
- derived indexes and caches.

SQLite is not appropriate as:

- production multi-user canonical application storage;
- canonical learner state;
- authoritative curriculum/KG truth;
- the sole source of assessment validation state;
- an independent semantic model allowed to diverge from PostgreSQL.

## 11. MarkdownDB decision

**Status: REJECTED as a core SyllabAI dependency.**

A generic Markdown-to-SQL indexing library solves a useful generic problem, but it does not define SyllabAI's educational semantics, provenance, SpecificationPoint relationships, assessment identity, validation lifecycle or serving gates.

If a concrete navigation/indexing need emerges, SyllabAI may evaluate such a library as an implementation component behind the Content Package contract. Adoption would require license compatibility, benchmark evidence and no leakage of provider/library semantics into the canonical domain model.

## 12. Security and serving boundary

Portable packages can contain educational content and provenance but must not bypass production authorization or serving gates.

Importing a package into a development or QA environment must not implicitly publish content to learners. Learner serving remains governed by the same validated-content and paper/question serving boundaries used by PostgreSQL-backed production flows.

## 13. Initial implementation scope

Do not build the complete compiler immediately. Start with a narrow v0.1 proof:

1. Define Revision Note frontmatter schema.
2. Define QP/MS artifact manifest schema.
3. Define SQLite package schema for a bounded corpus.
4. Implement package manifest/hash generation.
5. Compile a small known-good corpus.
6. Reconstruct the same corpus in a fresh environment.
7. Verify identity/provenance preservation and validation-state preservation.
8. Only then consider broad corpus packaging or runtime consumption.

The first implementation should optimize for **reproducibility and provenance**, not maximum schema coverage.

## 14. Status

**PROPOSED.** This document records the accepted direction for further design work only. It does not by itself authorize production migration, replacement of PostgreSQL, or bulk corpus reprocessing.
