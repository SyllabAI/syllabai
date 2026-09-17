# bench/ — T-C13 Retrieval Benchmark (gold set + harness probes)

Spec: `RETRIEVAL_BENCHMARK_HARNESS_SPEC.md` (Draft v0.1, ratification pending). Evidence: `evidence/bench-001/`.

Layout:
- `gold/` — frozen gold set **gold-v1** (120 queries, 12 classes, per-class files + manifest + SHA256SUMS). Read-only after freeze; tuning requires a versioned re-freeze (v2), never in-place mutation.
- `gold_check.py` — deterministic validator. Run: `python3 bench/gold_check.py evidence/bench-001/snapshot bench/gold --selftest` (validates all anchors resolve into the snapshot; selftest proves 6/6 corruption classes are detected).
- `gold_generate.py` — deterministic generator that produced gold-v1 from the snapshot (sha256-derived selection, no RNG; label rules R1/R2/R3 recorded in the gold manifest). Env overrides: `BENCH_SNAPSHOT`, `BENCH_GOLD_OUT`.
- `bproxy_score.py` — Run-1 harness-internal BM25 probe (Okapi k1=1.2 b=0.75), ALL-chunks vs VALIDATED-only scopes. Env overrides: `BENCH_SNAPSHOT`, `BENCH_GOLD`, `BENCH_RUN_OUT`. Output lands in `evidence/bench-001/runs/<run-id>/` with SHA256SUMS.

State (2026-09-17): M0 DONE (gold-v1 frozen, validator green incl. negatives), M1 PARTIAL (Run 1 B-proxy recorded; A0 baseline + B/C arms await a Java 25/Maven lane — see the prepared package). All Python artifacts LOCAL VERIFIED; results.json proven byte-identical across regenerate cycles.
