# SyllabAI Content Package v0.1 Specification

**Status:** PROPOSED  
**Date:** 2026-09-15  
**Related architecture:** `CONTENT_COMPILER_AND_PACKAGE_ARCHITECTURE.md`

## 1. Purpose

Define the smallest practical contract for a portable SyllabAI content package. v0.1 is a reproducibility/QA/distribution artifact, not a production database replacement.

## 2. Package layout

```text
syllabai-content-<scope>-<version>/
├── MANIFEST.json
├── content/
│   ├── revision-notes/
│   └── papers/
└── database/
    └── content.sqlite
```

An archive may wrap the directory as `.zip` or another explicitly versioned distribution format.

## 3. MANIFEST.json minimum contract

```json
{
  "packageFormat": "syllabai-content",
  "packageVersion": "0.1",
  "scope": "4CH1",
  "buildId": "...",
  "compilerVersion": "...",
  "schemaVersion": "...",
  "createdAt": "...",
  "status": "VALIDATED",
  "artifacts": [
    {
      "path": "content/...",
      "sha256": "...",
      "type": "REVISION_NOTE"
    }
  ]
}
```

The exact field names may evolve before implementation, but package identity, schema/compiler version, scope, lifecycle status and source/artifact hashes are mandatory concepts.

## 4. Revision Note artifact contract

Every packaged Revision Note must have stable identity and provenance sufficient to relate it to the canonical resource/domain representation.

Minimum frontmatter concepts:

```yaml
id: <stable-resource-id>
type: revision_note
status: HUMAN_VALIDATED
subject: <subject>
qualification: <qualification>
curriculum_version: <version>
specification_points:
  - <spec-point-id>
source:
  type: <source-type>
  provenance_id: <id>
version: <integer>
```

The package must preserve the note body without silently changing educational meaning.

## 5. QP/MS artifact contract

Each packaged QP/MS Markdown artifact must be traceable to the source document and parser run.

Minimum metadata concepts:

```yaml
document_type: QUESTION_PAPER | MARK_SCHEME
paper_id: <stable-paper-id>
source_sha256: <sha256>
parser: <parser-name>
parser_version: <version>
status: PARSED | REVIEW_REQUIRED | VALIDATED
```

Where a QP and MS are paired, the relationship must be explicit and identity-based rather than inferred from filenames alone.

## 6. SQLite schema v0.1

The first package schema should be deliberately small. Initial tables:

```text
package_metadata
resource
resource_version
resource_provenance
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
```

The schema must retain lifecycle/provenance state and stable IDs. It must not create a second semantic representation that can diverge from the canonical domain model.

KG tables are deferred from v0.1 unless a concrete bounded package requires them; the first package should prove the compiler/package mechanism before attempting a complete graph projection.

## 7. Build rules

A v0.1 compiler must:

1. Verify source artifact identity before import.
2. Preserve source SHA-256 values.
3. Record parser/compiler versions.
4. Preserve validation lifecycle state.
5. Reject missing required provenance.
6. Never promote `SUGGESTED`, `REVIEW_REQUIRED` or quarantined assessment content to learner-servable state.
7. Produce a manifest containing hashes for packaged artifacts.
8. Fail closed on identity collisions or ambiguous required relationships.

## 8. Reconstruction test

The first acceptance test is:

```text
known source snapshot
        ↓
compile
        ↓
package
        ↓
clean environment
        ↓
restore package
        ↓
inspect identities + provenance + lifecycle
```

Acceptance requires semantic equivalence of the packaged corpus to the source snapshot for the tested scope. Byte-for-byte package determinism is a later goal and must not be claimed until verified.

## 9. v0.1 non-goals

- replacing PostgreSQL;
- live multi-user writes against SQLite;
- canonical learner state;
- canonical authoritative KG storage;
- generic MarkdownDB dependency;
- bulk corpus migration before the bounded proof succeeds;
- making package existence equivalent to learner-serving eligibility.

## 10. Status

**PROPOSED.** This specification authorizes design/prototype work only. Production adoption requires implementation evidence and explicit promotion to `ACCEPTED`/`VERIFIED`.
