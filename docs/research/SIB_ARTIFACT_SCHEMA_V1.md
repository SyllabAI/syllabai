# SIB Artifact Schema v1

**Status:** PROPOSED  
**Protocol:** SIB v1

## 1. Filename

Canonical filename:

`<SUBJECT>_<QUALIFICATION>_<ARTIFACT_ID>_<SLUG>.md`

Example:

`CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md`

## 2. Required front matter

Every artifact must begin with YAML front matter:

```yaml
---
sib_protocol: SIB-1.0
artifact_id: MIS-01
artifact_version: 1.0
subject: Chemistry
qualification: International GCSE
specification: 4CH1
curriculum_version: "2017"

research_family: misconception_intelligence
applicability: REQUIRED

temporal_scope:
  current: true
  legacy: true

source_scope:
  specification: true
  textbook: true
  question_papers: true
  mark_schemes: true
  examiner_reports: true
  supplementary: true

status: GENERATED
generated_by: notebooklm
generated_at: YYYY-MM-DD

provenance:
  notebook: "<subject notebook identifier>"
  source_manifest: "<source manifest identifier>"
---
```

Fields may be extended, but the required fields above must not be removed.

## 3. Universal sections

Every artifact must contain:

1. Purpose
2. Scope
3. Executive Summary
4. Main Analysis
5. Evidence / Source Basis
6. Limitations / Coverage Gaps
7. Research Status

Family-specific sections follow.

## 4. Claim conventions

Where practical, claims should identify:
- subject/topic;
- SpecificationPoint(s);
- concept(s);
- source evidence;
- current/legacy temporal scope;
- assessment context;
- confidence or strength where the research format supports it.

Do not invent SpecificationPoint IDs. If the corpus does not support a precise mapping, say so.

## 5. Current vs legacy

Legacy evidence must be explicitly labelled.

Use:
- CURRENT — AUTHORITATIVE
- LEGACY — HISTORICAL
- SUPPLEMENTARY
- RESEARCH / INFERRED

A historical observation must not be phrased as current curriculum truth without current evidence.

## 6. Machine-readable research records

When an artifact contains repeated records, use stable IDs:

`MIS-001`, `MIS-002`, etc.

Each record should preserve provenance and subject anchors.

Example:

```markdown
### MIS-001 — [short name]

**Concepts:** ...
**Specification Points:** ...
**Temporal scope:** CURRENT
**Assessment context:** ...
**Misconception:** ...
**Why it occurs:** ...
**Correct understanding:** ...
**Typical manifestation:** ...
**Diagnostic signals:** ...
**Intervention ideas:** ...
**Evidence:** ...
```

## 7. No silent normalization

Do not silently:
- merge distinct concepts;
- convert legacy terminology into current terminology;
- infer a prerequisite as canonical;
- turn co-occurrence into a pedagogical dependency;
- treat semantic similarity as educational truth.

Such findings remain research claims until governed by SyllabAI validation.

## 8. Determinism

Repeated ingestion of the same artifact must preserve:
- artifact ID;
- metadata;
- record IDs;
- source references;
- temporal labels.

Content may be regenerated, but the pipeline must make changes observable through hashes/diffs.

## 9. Chunking expectations

The final Markdown is authored for semantic chunking, not arbitrary fixed-size splitting.

Prefer boundaries around:
- one research claim;
- one misconception;
- one question archetype;
- one concept explanation;
- one procedure;
- one tutor pattern.

Chunks should retain artifact ID, record ID, subject, qualification, temporal scope and relevant curriculum anchors in metadata.

## 10. Runtime eligibility

A research artifact/chunk is Tutor-servable only when its SyllabAI publication status permits serving.

NotebookLM output alone does not confer runtime eligibility.
