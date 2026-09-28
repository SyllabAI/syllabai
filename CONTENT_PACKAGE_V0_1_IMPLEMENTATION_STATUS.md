# Content Package v0.1 Implementation Status

**Status: IMPLEMENTED / VERIFIED — the v0.1 contract proven at two scopes: the bounded real-corpus reconstruction proof (below) + the hub-corpus tooling over all 49 courses (ADR-029 tranche 4.12, hub `0c589de`)**
**Scope: v0.1 compiler/package/verification contract; no serving change**
**ADR-021: ACCEPTED since 2026-09-29** (operator decision, chat bb263437, trace 1a0e9f879a8d8fe1; the ADR's promotion gate — implementation evidence + bounded reproducibility tests — satisfied by the two evidence bodies below, re-verified GREEN at current main on promotion day: parser-ci run `36161511189` @ `55166af`, hub-ci run `36487846248` @ `9a00eb1` with the selftest step green; promotion record in the ADR file + DECISIONS.md). **Architecture note: the architecture companion (`CONTENT_COMPILER_AND_PACKAGE_ARCHITECTURE.md`) remains PROPOSED** — corpus-wide COMPILATION is now proven at hub scale (tranche 4.12), but corpus-wide migration, KG projection policy, distribution at scale and canonical-store integration remain staged until separately proven.

## Current implementation

The proof lives in `SyllabAI/syllabai-parser` under `tools/content-package-v0.1/`:

- SQLite schema for the v0.1 derived package (`schema.sql`; `mark_point.question_part_id` nullable to mirror the production question-level-point shape);
- package manifest contract example;
- dependency-free bounded compiler/reconstruction harness (`compile_proof.py`), now supporting both the synthetic-fixture shape and the production shape (per-version mark schemes, question-level points);
- semantic reconstruction checks for Revision Note, SpecificationPoint mapping, QP/MS, question/part/mark-point identity;
- SHA-256 provenance checks;
- fail-closed lifecycle and relationship checks;
- negative regression tests (synthetic fixture, unchanged);
- **real-corpus proof** (`real_corpus/run_proof.py`) — the next gate below, executed;
- CI execution of both proofs (`parser-ci` → `content-package-proof` job).

## Real-corpus evidence (the previous "next gate" — now executed)

The synthetic fixture was deliberately NOT expanded. The real proof uses real canonical content:

- **One real Revision Note** — verbatim from `SyllabAI/syllabai-resources` ("Relative atomic mass", sha256 `88d99b91f0f7cbf4cb399cc0f5cb7be164af55367ba415c2551eabd918058e1a`), with operator-`HUMAN_VALIDATED` SpecificationPoint mappings **4CH1-1.16 / 4CH1-1.17** (2026-09-11).
- **One real learner-servable QP/MS pair** — production paper `cfccc663-8aef-4a20-90b4-1205b3e740b5` (Edexcel International GCSE Chemistry, "Summer 2019", 7 question versions, every version carrying a VALIDATED mark scheme = complete marking contract), exported through the sanctioned teacher-API workflow (`SyllabAI/syllabai-web` run **34899656801**, PILOT_TEACHER_* used in-workflow only, never printed).
- **Deterministic provenance binding** — the OCR canonical document ids (`97798258-…` QP, `ef754010-…` MS) equal the production paper's document-id columns; documentId = CanonicalIdentity(checksum|engine|version), enforced by `CanonicalDocumentValidator` at ingestion; the canonical bundle verifies against the workbench snapshot `SHA256SUMS` ledger. The PDF→bundle link is recorded honestly as IDENTITY_INFERRED.
- **Reconstruction proof** — compile → package (Markdown artifacts + SQLite + MANIFEST) → clean room (package directory alone) → semantic reconstruction compared against the production records: identities, provenance, lifecycle, relationships and the complete marking contract all equal (`R3.1–R3.9`).
- **Negative gates, fail-closed with no package created** — bad source checksum, missing provenance, incomplete QP/MS pairing, scheme-less question version (a REAL scheme-less version from the SUGGESTED "4CH0/2CR June 2014" export, promoted to VALIDATED), invalid lifecycle (SUGGESTED paper) — each rejected for the asserted expected reason (`N1–N5`).
- **CI evidence** — `parser-ci` run **34903192847** at parser main `a0a599b`: `content-package-proof` job success, real-corpus verdict **GREEN 17/17** (job log retained in the verification workspace; `R2b` consecutive-compile byte equality observed `True` and recorded as an observation, not a determinism claim).

Verdict line (verbatim from CI): `REAL-CORPUS PROOF VERDICT: GREEN 17/17`.

## Repository ownership

- `SyllabAI/syllabai`: architecture, decisions, canonical cross-project contracts.
- `SyllabAI/syllabai-parser`: offline content/package proof implementation.
- `SyllabAI/syllabai-resources`: durable validated resource corpus.
- `SyllabAI/syllabai-pastpapers`: normalized assessment corpus (source-PDF manifests).
- `SyllabAI/syllabai-core`: canonical operational/domain state in PostgreSQL.
- `SyllabAI/syllabai-teacher-workbench`: durable campaign/protective snapshots (provenance ledger for the OCR canonical bundle).

## Verification status

**Bounded real-corpus v0.1 reconstruction proof: IMPLEMENTED / VERIFIED** (CI-executed, machine-generated verdicts, committed source materials, deterministic provenance binding; re-verified at current parser main `55166af`, parser-ci run `36161511189`, `content-package-proof` job GREEN). This promoted the *bounded proof* only.

**Hub-corpus v0.1 tooling (2026-09-29, ADR-029 tranche 4.12): IMPLEMENTED / VERIFIED** — the same contract at production scale: hub `0c589de` `tools/content-package/` compiles all 49 courses / 346 artifacts / 82.8 MB → `MANIFEST.json` (identity + per-artifact SHA-256 + counts + findings) + verbatim content copies + SQLite v0.1 projection; gates `G1`–`G5`/`V1`–`V8`/`R1`–`R4` fail closed; NO serving change (PostgreSQL + `content/` remain operational truth). CI-enforced selftest (compile + verify + restore + determinism + tamper, ~3.4s) re-verified GREEN at hub main `9a00eb1` (run `36487846248`). Evidence: `download/s135/`.

On these two bodies ADR-021 was promoted PROPOSED → ACCEPTED on 2026-09-29 (operator decision). The broader architecture companion remains **PROPOSED** — its remaining claims (KG projection policy, distribution/versioning at scale, canonical-store integration) are staged until separately proven; corpus-wide compilation is now proven at hub scale, corpus-wide MIGRATION remains unauthorized.

Determinism: two consecutive compiles of the parser real inventory produced byte-identical packages in the verification environment (observed, recorded). The hub-corpus tooling strengthens this to a CI-enforced gate — byte-identical SQLite across consecutive compiles + clock-free buildId, verified in every hub-ci run (selftest determinism step).

## Explicit non-goals

- replacing PostgreSQL;
- making SQLite the authoritative educational KG;
- storing learner state as canonical truth;
- bypassing validation or serving gates (the compiler refuses incomplete marking contracts regardless of SQLite representability);
- adopting MarkdownDB;
- broad corpus migration on the strength of the bounded proof alone;
- treating the proof corpus as anything other than the two real artifacts it names.

## Known gaps (recorded, not hidden)

- The production `documents` table has no rows for campaign-imported papers, so the teacher provenance endpoint fail-closed 404s for them; the real proof's source identity is served by the committed snapshot bundle instead, and the exporter refuses a positive case whose provenance cannot be established.
- The PDF→OCR-bundle link is identity-inferred (naming + mark structure), not cryptographic; it is recorded with that status and not promoted.
- The collector's legacy-spec directory labels (`4ch0-…`) differ from the authoritative paper identity (`4CH1/2CR`); the production record and pastpapers manifest are authoritative.

## Next gate

~~Promote the architecture itself (ADR_021) from PROPOSED only via a reviewed decision covering the remaining architectural claims.~~ **EXECUTED 2026-09-29**: ADR-021 promoted PROPOSED → ACCEPTED by the operator decision (chat bb263437, trace 1a0e9f879a8d8fe1) — a reviewed decision that covers the remaining architectural claims by scoping them OUT of acceptance: they stay staged in `CONTENT_COMPILER_AND_PACKAGE_ARCHITECTURE.md` (PROPOSED) until separately proven. The prohibition holds and is restated by the promotion: a corpus-wide migration must NOT start — neither on the bounded proof nor on the hub-corpus tooling; PostgreSQL remains canonical. The forward gates are the architecture companion's staged claims: KG projection policy, distribution/versioning at scale, canonical-store integration.
