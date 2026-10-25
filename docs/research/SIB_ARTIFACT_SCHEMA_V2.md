# SIB Artifact Schema v2 — provider-neutral generation provenance

**Status:** PROPOSED
**Protocol:** SIB v1 (front matter `sib_protocol: SIB-1.0` is unchanged — this is a
schema-version change, not a protocol-version change)
**Defined:** 2026-10-25, SIB-GEN run of record (trace `1a1726b6684c4055`)
**Supersedes:** the *provenance shape* of `SIB_ARTIFACT_SCHEMA_V1.md` §2. Every other
V1 rule (filename contract, lifecycle, sections, claim conventions, current/legacy,
records, determinism, chunking, runtime eligibility) carries forward unchanged.

## 0. Why v2 exists

Schema V1 hardcoded the NotebookLM authoring path into the provenance contract:
`generated_by: notebooklm` and a `provenance` block requiring `notebook` +
`source_manifest`. The 2026-10-25 SIB-GEN decision of record changed the runtime
generator to the **provider-neutral Z.ai agent pipeline** (grounded by the SIB source
resolver / evidence packs / run manifests — `docs/research/SIB_ZAI_PROMPTS_V1.md`).
NotebookLM is retained as an OPTIONAL-HIS research path, so the schema must accept
both provenance shapes without weakening any V1 guarantee.

Design constraints held from V1:

* **No required field is removed.** All 15 V1 metadata fields stay required.
* **The deterministic builtin front-matter fallback still works.** `provenance`
  therefore stays a **one-level mapping** (no deeper nesting; flat keys below).
  `tools/sib/frontmatter.py` parses exactly this subset without PyYAML.
* **The validator owns every lifecycle transition**; landing artifacts may declare
  only `GENERATED` (or `QA_FAILED` post-QA). Unchanged.

## 1. `generated_by` vocabulary (extended, none removed)

```text
notebooklm   NotebookLM/Gemini Notebook authoring path (OPTIONAL-HIS going forward)
zai_agent    the Z.ai agent SIB pipeline (generator of record, 2026-10-25 SIB-GEN)
agent        generic agent drop (pre-V2 spelling; remains valid)
operator     operator drop
human        human drop
```

## 2. V2 provenance shape (generator-shape)

Required for `generated_by: zai_agent` (and accepted for `agent`):

```yaml
status: GENERATED
generated_by: zai_agent
generated_at: "2026-10-25"

provenance:
  source_manifest: "CHEMISTRY_4CH1 source_manifest.yaml v1.2"
  generation_run_id: "SIB-CHEMISTRY_4CH1-CUR-01-RUN-001"
  generator_provider: "z.ai"
  generator_model: "<actual model identifier used>"
  generator_agent_version: "SIB_ZAI_PROMPTS_V1"
  resources_revision: "<syllabai-resources git commit sha>"
  pastpapers_revision: "<syllabai-pastpapers git commit sha, if used>"
```

Field law:

| Field | Requirement | Meaning |
|---|---|---|
| `source_manifest` | **required** (as in V1) | must be declared by the operator source manifest when one is supplied to the validator — the cross-check that refuses invented identifiers is unchanged |
| `generation_run_id` | **required** | run-record identifier of record (`<LIBRARY>-<ARTIFACT-ID>-RUN-<NNN>` convention; the run receipt lives in `<LIBRARY>/runs/`) |
| `generator_provider` | **required** | the generating service, e.g. `z.ai` — deliberately kept separate from the model |
| `generator_model` | **required** | the **actual** model identifier used for this run; never assume it is constant across runs |
| `generator_agent_version` | recommended | the prompt-pack/agent version pin (e.g. `SIB_ZAI_PROMPTS_V1`) |
| `resources_revision` / `pastpapers_revision` | recommended | git commit SHAs of the canonical source repos at generation time |
| `notebook` | **not required** in V2 | may still appear for a run that consulted an OPTIONAL-HIS NotebookLM notebook; extra fields are never rejected |

## 3. Shape law (which provenance shape applies when)

```text
generated_by: notebooklm             -> V1 notebook-shape: notebook + source_manifest
generated_by: zai_agent | agent      -> V2 generator-shape: source_manifest +
                                        generation_run_id + generator_provider +
                                        generator_model
generated_by: operator | human       -> source_manifest required; notebook optional
                                        (deliberate, tested relaxation of the V1
                                        NotebookLM-era requirement — operator drops
                                        are not NotebookLM drops)
```

The provenance block itself is **always required**. Placeholder values
(`<...>`, `none`, `unknown`, `tbd`) fail exactly as in V1 — the V2 placeholder
tokens (`<run identifier>`, `<model identifier>`, `<provider>`, …) are added to the
validator's placeholder set.

## 4. What v2 deliberately does NOT change

* The 15 required metadata fields, universal sections, lifecycle, and all V1 §3–§11 law.
* The validator's role boundary: a green validation report remains a **structural
  verdict**, never proof of educational correctness (V1 §3 rule 7/8).
* The source-manifest cross-check: `provenance.source_manifest` must reference an
  identifier the operator's manifest actually declares — in both shapes.
* Determinism observability: content may be regenerated, but changes must be
  observable; V2 adds the run-record pairing (evidence-pack hash + artifact hash in
  `runs/<RUN_ID>/`) that makes regeneration explainable.
