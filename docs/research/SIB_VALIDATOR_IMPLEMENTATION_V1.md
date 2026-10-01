# SIB Validator & Ingestion Scaffolding — Implementation Record (v1)

**Tooling status:** IMPLEMENTED (this document, `tools/sib/`)
**SIB architecture status:** PROPOSED — unchanged by this work
**Implements:** `docs/research/SUBJECT_INTELLIGENCE_BUILD_V1.md` + `docs/research/SIB_ARTIFACT_SCHEMA_V1.md` (both currently on open PR `agent-chatgpt/subject-intelligence-build-v1`)
**Implements NOT:** artifact generation, NotebookLM integration, Subject Tutor retrieval, canonical-KG/mastery/assessment changes.

---

## 1. What this is

The deterministic landing zone and validation boundary that NotebookLM-generated
SIB artifacts will use when the 4CH1 Subject Intelligence Library is eventually
built. It validates, it never mutates canonical truth, and it never promotes
research into educational correctness:

> Validation is evidence that structural requirements are satisfied; it is not
> educational correctness.

Pipeline boundary implemented:

```text
NotebookLM / external research
    -> SIB Markdown artifacts        artifacts/   (landing zone; status GENERATED)
    -> artifact parser               tools/sib/frontmatter.py
    -> schema validation             tools/sib/artifact_validator.py
    -> provenance validation         artifact_validator + source_manifest.yaml
    -> curriculum-anchor validation  tools/sib/anchors.py
    -> QA result                     qa-reports/<ARTIFACT_ID>.qa.json  (deterministic JSON)
    -> STAGED                        staged/     (explicit operator action)
    -> PUBLISHED research library    published/  (explicit operator action)
```

## 2. Layout (per subject library, e.g. `research/sib/CHEMISTRY_4CH1/`)

| Path | Role | Mutator |
|---|---|---|
| `manifest.yaml` | subject inventory: applicability, status, gaps, backlog | operator |
| `source_manifest.yaml` | operator source-provenance declarations (id list) | operator |
| `curriculum_registry.yaml` | OPTIONAL pinned spec-point id list (e.g. from `syllabai-resources` `graph/specification_points.yaml`) for anchor resolution | operator |
| `artifacts/` | landing zone — NotebookLM output arrives here as GENERATED | operator drop |
| `qa-reports/` | deterministic QA JSON per artifact | `sib qa` |
| `staged/` | QA-passed, awaiting publication decision | `sib stage` |
| `published/` | published research library | `sib publish` |
| `chunks/` | deterministic chunk JSONL per artifact | `sib chunks` |

All writes are confined to the library root (path traversal raises
`SIB-ING-001`); the library API exposes no canonical-write surface at all.

## 3. Validation coverage

* **Metadata (§2 task):** all 15 required front-matter fields
  (`SIB-META-001/002/003/004`), protocol pin `SIB-1.0`, version/date format,
  `generated_by` vocabulary.
* **Identity:** artifact-id shape + 95-taxonomy membership (`SIB-IDENT-001/002`),
  family membership (`-003`), filename identity (`-004`) and canonical-filename
  INFO (`-005`), applicability (`-006`), duplicate artifact IDs (`-007`),
  duplicate/invalid/mis-family record IDs (`-008/009/010`), version shape (`-011`).
* **Sections:** the 7 universal sections (`SIB-SECT-001`).
* **Status:** lifecycle membership (`SIB-STATUS-001`), landing artifacts
  self-declaring `QA_PASSED/STAGED/PUBLISHED` rejected as unsupported
  publication (`-003`); transition legality enforced in
  `lifecycle.py` (exact table: `GENERATED→QA_PASSED→STAGED→PUBLISHED`,
  `GENERATED→QA_FAILED`, both `QA_FAILED` and `PUBLISHED` terminal).
* **Temporal/source semantics:** boolean temporal scope, empty-scope
  rejection (`SIB-TEMP-001`), current/legacy contradiction detection (`-002`),
  non-canonical label warning (`-003`), mixed scope without explicit
  CURRENT — AUTHORITATIVE / LEGACY — HISTORICAL labeling (`-004`),
  source-basis requirement (`SIB-SRC-001`). Current and legacy claims are
  never merged; contradictions are flagged, not resolved.
* **Provenance:** `provenance.notebook` / `provenance.source_manifest`
  concrete-reference checks (`SIB-PROV-001`, template placeholders rejected),
  optional cross-check against `source_manifest.yaml` (`SIB-PROV-002`);
  incomplete provenance is `QA_FAILED` with a machine-readable reason.
  The validator never invents source identifiers.
* **Curriculum anchors:** shape validation
  (`1.1`–`99.999.99` Edexcel-numbered style; malformed dotted tokens inside
  anchor fields are `ERROR SIB-ANCH-001`), registry resolution when supplied
  (`SIB-ANCH-004` INFO resolved / `-002` WARNING unresolved),
  registry-absent reported as INFO (`-003`). Unresolved references are
  reported, never repaired; SpecificationPoints are never created.
* **Manifest:** required fields incl. provenance (`SIB-MANI-002`),
  duplicates (`-003`), unknown ids (`-004`), row statuses (`-005`),
  NOT_APPLICABLE×{QA_PASSED,STAGED,PUBLISHED} impossibility (`-006`),
  REQUIRED-without-file (`-007`), manifest/artifact disagreement + files
  without rows (`-008`), publication without QA evidence (`-009`),
  declared source gaps (`-011` WARNING) and backlog (`-012` INFO).
  `OPTIONAL` / `NOT_APPLICABLE` are first-class; the 95 slots are inventory,
  not obligations — a one-row manifest validates. The ingestion boundary
  mirrors the manifest rule locally: NOT_APPLICABLE artifacts pass QA as
  valid inventory but are refused at staging (they never advance to
  QA_PASSED/STAGED/PUBLISHED through the pipeline).

## 4. Determinism

* Identical input → byte-identical QA JSON, validator JSON, chunk JSONL and
  counts (proved by tests running 5× and across different temp roots).
* Issue lists are sorted by `(code, artifact_id, record_id, field, message)`;
  JSON output uses `sort_keys=True`.
* No timestamps or random UUIDs participate in identity anywhere. QA reports
  carry `content_sha256` (SHA-256 of the artifact text) for observable
  change detection (schema §8).
* PyYAML and the stdlib fallback parser produce identical metadata for the
  SIB subset (quoted scalars stay strings; dates canonicalize to ISO strings);
  parity is tested.

## 5. Chunk metadata (task §9)

`tools/sib/chunking.py` splits artifacts at record boundaries
(`### FAM-NNN — …`) and universal-section boundaries. Every chunk preserves
the envelope: `artifact_id, record_id, subject, qualification, specification,
curriculum_version, research_family, temporal_scope, source_scope, status,
curriculum_anchor_refs, provenance` (+ `artifact_version`). Chunk ids are
`<ARTIFACT_ID>:sec:<HEADING_SLUG>` / `<ARTIFACT_ID>:rec:<RECORD_ID>`; text is
bound by SHA-256. This is SIB-specific research chunking — no generic RAG
pipeline is introduced or replaced.

## 6. Usage

```bash
# library-level
python3 -m tools.sib.cli qa       <lib> <lib>/artifacts/<file>.md
python3 -m tools.sib.cli stage    <lib> <lib>/artifacts/<file>.md
python3 -m tools.sib.cli publish  <lib> <lib>/staged/<file>.md
python3 -m tools.sib.cli chunks   <lib> <lib>/artifacts/<file>.md
python3 -m tools.sib.cli report   <lib>

# single-artifact / manifest validation (pure, no writes)
python3 -m tools.sib.cli validate-artifact <file.md> --library <lib>
python3 -m tools.sib.cli validate-manifest <lib>
```

Exit code 0 = QA passed / action performed; 1 = rejected. JSON output is
sorted-key and byte-stable for identical input.

## 7. Tests / CI

* Suite: `python3 -m tools.sib.tests.run_all` — stdlib `unittest` only,
  repo-conventional standalone runner. 126 tests cover valid artifacts
  (full/optional/NOT_APPLICABLE/current/legacy), every rejection path above,
  determinism (repeated runs, cross-path byte-equality), and the runtime
  boundary (self-publication rejection, path-traversal refusal, no canonical
  write surface, purity of validation -- proven against the pure
  `validate_artifact` layer, with `qa_artifact`'s governed report write
  tested separately).
* **Stdlib-only is proven, not claimed:** the entire suite passes with PyYAML
  import-blocked (CI `setup-python` images do not ship it); the ONLY 2 skips
  under the blocker are the two PyYAML-parity tests, which by definition
  require PyYAML (expected skips, marked in-code).
  `tools/sib/yamlmini.py` provides a deterministic YAML-subset loader
  (manifests, source manifests, registries, front matter) used when PyYAML is
  absent; parity is tested. Registry ids must be QUOTED strings
  (`- "2.30"`) — unquoted ids lose trailing zeros to YAML float typing and
  now FAIL CLOSED (`build_registry` raises ValueError) instead of being
  silently coerced into a different identifier (2.30 ≠ 2.3).
* CI: `.github/workflows/sib-validator-ci.yml` runs the suite on every push/PR
  touching `tools/sib/**`.

## 8. Reconciliation record (2026-10-01)

1. **Filename contract — RESOLVED (PROPOSED/DEFINED), no longer a divergence.**
   `SIB_ARTIFACT_SCHEMA_V1.md` §1 previously showed template
   `<SUBJECT>_<QUALIFICATION>_<ARTIFACT_ID>_<SLUG>.md` beside the example
   `CHEMISTRY_4CH1_MIS-01_…` (slot 2 = specification code). The schema doc now
   defines the canonical template as
   `<SUBJECT>_<SPECIFICATION>_<ARTIFACT_ID>_<SLUG>.md`; template and example
   agree, and this implementation already matched that contract. The
   qualification stays a required front-matter field and never enters the
   filename. Pinned by deterministic tests
   (`test_canonical_filename_template_is_specification_based`,
   `test_canonical_filename_agrees_with_specification_slot`). Recorded while
   the SIB architecture remains PROPOSED — no status promotion.
2. **Branch reconciliation.** Both PR #13 (protocol/schema/prompts) and this
   branch were reconciled against current `main` (`5bbb764`) by merging main
   in; the earlier not-mergeable report on PR #13 was stale GitHub
   mergeability state after main advanced twice — the only overlapping file
   (`PROJECT_CONTEXT.md`) auto-merges and now carries both the SIB doc
   bullets and the newer main-side corrections.
3. **Landing-status rule (still a documented divergence).** The schema does
   not state which status a landing artifact file may declare; the protocol
   ("NotebookLM-generated output begins as GENERATED") is implemented as:
   landing artifacts must declare `GENERATED` (or `QA_FAILED`);
   `QA_PASSED/STAGED/PUBLISHED` in the landing zone is `ERROR
   SIB-STATUS-003`. Staging tooling rewrites status when moving files across
   the boundary.

## 9. Component status ledger

| Component | Status |
|---|---|
| SIB v1 protocol / architecture | PROPOSED (unchanged; owner: PR #13 docs) |
| Filename convention | PROPOSED/DEFINED (schema §1; slot 2 = specification) |
| Artifact validator (schema v1) | IMPLEMENTED (see §7 for exact verified test counts) |
| Manifest validator | IMPLEMENTED |
| Provenance validation | IMPLEMENTED (operator source_manifest cross-check) |
| Temporal / source semantics | IMPLEMENTED |
| Curriculum-anchor validation | IMPLEMENTED (shape + optional registry resolution; never mutates) |
| STAGED/PUBLISHED governed boundary | IMPLEMENTED (path-confined, evidence-gated; QA evidence re-verified at publish; evidence content-bound at stage) |
| SIB chunk metadata model | IMPLEMENTED (deterministic) |
| 4CH1 SIB artifact generation | BLOCKED (explicitly out of scope; awaits PR #13 acceptance) |
| Subject Tutor retrieval integration | BLOCKED (separate runtime decision) |
