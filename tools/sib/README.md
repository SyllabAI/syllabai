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
* **Stdlib-only core (proven by test)** — PyYAML is used when present
  (guarded); `yamlmini.py` provides a tested deterministic YAML-subset
  fallback for manifests/registries/front matter. The full suite passes with
  PyYAML import-blocked.

```bash
# run the test suite (126 tests; with PyYAML import-blocked: 124 passed +
# 2 expected skips -- the PyYAML-parity tests)
python3 -m tools.sib.tests.run_all

# CLI
python3 -m tools.sib.cli --help
```

Filename contract (SIB_ARTIFACT_SCHEMA_V1.md §1, PROPOSED/DEFINED
2026-10-01): `<SUBJECT>_<SPECIFICATION>_<ARTIFACT_ID>_<SLUG>.md` — slot 2 is
the specification code (`4CH1`); the qualification is metadata only.
Registry ids in `curriculum_registry.yaml` must be quoted (`- "2.30"`);
unquoted float-typed ids fail closed instead of being silently coerced into
a different identifier.
