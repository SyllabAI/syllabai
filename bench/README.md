# bench/ — T-C13 Retrieval Benchmark (gold set + harness probes)

Spec: `RETRIEVAL_BENCHMARK_HARNESS_SPEC.md` (RATIFIED v1.0). Evidence: `evidence/bench-001/`.

Layout:
- `gold/` — frozen gold set **gold-v1** (120 queries, 12 classes, per-class files + manifest + SHA256SUMS). Read-only after freeze; tuning requires a versioned re-freeze (v2), never in-place mutation.
- `gold_check.py` — deterministic validator. Run: `python3 bench/gold_check.py evidence/bench-001/snapshot bench/gold --selftest` (validates all anchors resolve into the snapshot; selftest proves 6/6 corruption classes are detected).
- `gold_generate.py` — deterministic generator that produced gold-v1 from the snapshot (sha256-derived selection, no RNG; label rules R1/R2/R3 recorded in the gold manifest). Env overrides: `BENCH_SNAPSHOT`, `BENCH_GOLD_OUT`.
- `bproxy_score.py` — Run-1 harness-internal BM25 probe (Okapi k1=1.2 b=0.75), ALL-chunks vs VALIDATED-only scopes. Env overrides: `BENCH_SNAPSHOT`, `BENCH_GOLD`, `BENCH_RUN_OUT`. Output lands in `evidence/bench-001/runs/<run-id>/` with SHA256SUMS.
- `gold_spotcheck.py` — Ruling-3 owner spot-check worksheet generator (T-C13 §10 ruling 3): 20% stratified + 100% classes 4/5/6 from frozen gold-v1, sha256-seeded no-RNG selection (seed = sha256(manifest.json)[:16]), outputs under `evidence/bench-001/governance/` (worksheet.md + worksheet.csv + sample.json). Determinism proven byte-identical across regenerate cycles.
- `r3_interactive/build_r3_interactive.py` — renders the recorded sample as an OFFLINE interactive review page (`evidence/bench-001/governance/ruling-3-spot-check-interactive.html`): imports gold_spotcheck's own fail-closed logic, cross-checks the re-derived sample against the recorded sample.json, embeds resolved evidence; owner verdicts autosave in-browser and export as ruling-3-owner-verdicts-<seed>.json + marked worksheet CSV. The exported verdicts — never the page itself — are the recorded owner evidence.

State (2026-09-17, late): M0 DONE (gold-v1 frozen, validator green incl. negatives), M1 DONE (Run 1 B-proxy + Run 2 A0 recorded), Ruling-3 owner spot-check worksheet generated (`evidence/bench-001/governance/`). All Python artifacts LOCAL VERIFIED; result/sample outputs proven byte-identical across regenerate cycles. Java harness/retrieval artifacts are unit-green in the bootstrapped lane (core `99be333` = T-C14); Docker-ITs remain on the CI route.
