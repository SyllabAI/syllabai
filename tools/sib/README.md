# tools/sib — SIB v1 Validator & Ingestion Scaffolding

Deterministic validator, manifest governance and ingestion boundary for
Subject Intelligence Build (SIB-1.0) research artifacts.

**Read first:** `docs/research/SIB_VALIDATOR_IMPLEMENTATION_V1.md`
(implementation record: coverage, divergences, component status ledger).
The SIB protocol/schema documents themselves are the canonical source
(currently on PR `agent-chatgpt/subject-intelligence-build-v1`).

Key properties:

* **Pure validation** — validation never mutates artifacts, manifests,
  curriculum, KG, learner state or assessment truth.
* **Governed lifecycle** — `GENERATED → QA_PASSED → STAGED → PUBLISHED`
  (and `GENERATED → QA_FAILED`); staging/publication are explicit,
  evidence-gated, path-confined actions.
* **Deterministic** — byte-identical reports/chunks for identical input;
  no clocks or randomness in identity.
* **Stdlib-only core** — PyYAML is used when present (guarded), with a
  tested parity fallback parser.

```bash
# run the test suite (102 tests)
python3 -m tools.sib.tests.run_all

# CLI
python3 -m tools.sib.cli --help
```
