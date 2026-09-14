# Content Package v0.1 Implementation Status

**Status: IMPLEMENTED / VERIFIED — bounded real-corpus v0.1 reconstruction proof**
**Scope: bounded proof only**
**Architecture note: the Content Compiler / Portable Content Package architecture (ADR_021, `CONTENT_COMPILER_AND_PACKAGE_ARCHITECTURE.md`) remains PROPOSED. This evidence covers the bounded v0.1 compiler/package/reconstruction proof, not the broader architectural claims (corpus-wide migration, KG projection, distribution at scale).**

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

**Bounded real-corpus v0.1 reconstruction proof: IMPLEMENTED / VERIFIED** (CI-executed, machine-generated verdicts, committed source materials, deterministic provenance binding). This promotes the *bounded proof* only.

The broader Content Compiler / Portable Content Package architecture remains **PROPOSED** until its remaining claims (corpus-wide compilation, KG projection policy, distribution/versioning at scale, canonical-store integration) are separately proven and reviewed.

No claim of general byte-for-byte package determinism is made. Two consecutive compiles of the real inventory produced byte-identical packages in the verification environment (observed, recorded, not contractual).

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

Promote the architecture itself (ADR_021) from PROPOSED only via a reviewed decision covering the remaining architectural claims. A corpus-wide migration must NOT start on the strength of this bounded proof.
