# Run 005 — C hybrid arm, first recorded run (the retrieval fabric orchestrator)

**Status:** RECORDED — production hybrid arm on record (deterministic, offline replay, zero API calls; snapshot snap-001).
**Arm:** C hybrid — PRODUCTION retrieval fabric (com.syllabai.retrieval.RetrievalFabric: explicit arms [pgvector, bm25], central BoundaryPolicy, shipped ReciprocalRankFusion k=60, rank-only, NoReranker) over arm A's production vector path and arm B's production lexical path; chunk+query vectors replayed from the frozen artifact embed-backfill-snap-001, zero API calls at run time
**Executor:** production code over real Postgres migrated V1..V28 (Flyway), corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served through the production EmbeddingProvider port; no retrieval SQL changed, no fusion code written (the shipped ReciprocalRankFusion runs unchanged) — code `c05efb98355ada8a3328c2781148072b556c8c24`.
**Date:** 2026-09-20 | **Gold:** gold-v1 frozen | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Fabric provenance

- Orchestrator: the registered gap CLOSED — `RetrievalFabric` composes the explicit arms [pgvector, bm25] (never injection-implied, E-1 forward note), applies the serving boundary ONCE centrally pre-fusion, and fuses with the shipped `ReciprocalRankFusion` k=60 — no new fusion code, no retrieval SQL changed. Per-arm candidate bound 20.
- Frozen artifact `embed-backfill-snap-001`: model `gemini-embedding-001` @ 768 dims; verified fail-closed against this run's frozen inputs before anything ran; SHA-256 echo in results.json `embedding_artifact.sha256_echo`.

## Overall (chunk axis, n=44 labeled queries)

- **C served (fabric over components as they stand, ALL denominator, 2333 embedded chunks):** recall@5 0.0065 · recall@10 0.0075 · recall@20 0.0087 · mrr 0.0568 · ndcg@10 0.074 · evidence_precision@10 0.0159 · false_positive_rate@10 0.9841
- **C compliant (central VALIDATED gate pre-fusion, 27 reachable chunks — the T-C05-closed configuration):** recall@5 0.0087 · recall@10 0.0087 · recall@20 0.0087 · mrr 0.0568 · ndcg@10 0.077 · evidence_precision@10 0.0182 · false_positive_rate@10 0.35
- **B (run-003, production lexical, VALIDATED-served):** evidence_precision@10 0.0068 · false_positive_rate@10 0.0023 · mrr 0.0682 · ndcg@10 0.0682 · recall@10 0.0032 · recall@20 0.0032 · recall@5 0.0032
- **A served (run-004, production vector, ALL denominator):** evidence_precision@10 0.0136 · false_positive_rate@10 0.9864 · mrr 0.0108 · ndcg@10 0.0526 · recall@10 0.0064 · recall@20 0.0075 · recall@5 0.0054
- **A compliant view (run-004, post-hoc VALIDATED-only filter):** evidence_precision@10 0.0159 · false_positive_rate@10 0.3477 · mrr 0.0152 · ndcg@10 0.0633 · recall@10 0.0075 · recall@20 0.0075 · recall@5 0.0075

## Per class (C served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| enumerate_paper | 0.0716 | 0.083 | 0.0955 | 0.625 | 0.8139 | 0.175 | 0.825 |
| fetch_null_code | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| fetch_paper_code | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |

## Per class (C compliant view — T-C05-closed configuration)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| enumerate_paper | 0.0955 | 0.0955 | 0.0955 | 0.625 | 0.8472 | 0.2 | 0.3 |
| fetch_null_code | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.16 |
| fetch_paper_code | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3829 |

## S8 gate arithmetic (ratified v1.0; ruling 1: ALL denominator = served view)

- (a) Recall@10: **0.0075** vs floor 0.3249 -> FAIL

- (b) MRR: **0.0568** vs floor 0.2964 -> FAIL

- (c) nDCG@10: **0.074** vs floor 0.4799 -> FAIL

- (d) SpecificationPoint resolution: not scoreable (zero chunk-to-SP HUMAN_VALIDATED rows — named data gap; nothing to regress).
- (e) p95 latency: not evaluable from records (A0 p95 not recorded); this run records retrieval-only p50/p95; a deployed hybrid adds the production query-embedding round-trip.
- (f) Validation boundary: served view surfaced **2040** non-VALIDATED hits (the T-C20 vector-surface gap) — hard fail per §5.1 for the as-served configuration; the compliant view audited **0** by construction.
- (g) Per-class regression: trivially satisfied vs the zero A0 baseline.
- **VERDICT: NOT PROMOTED**

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS (served view): 2040. **Named finding, not a silent patch:** the production vector surface predates T-C05; the compliant view's central pre-fusion gate (this run's new production capability) audited ZERO violations across all 120 queries — the gate is the T-C20 closure shape.
- Zero-result queries (served): 0/120.
- Compliant-starved queries: 6 (served non-empty but every eligible-rank hit sits on a non-VALIDATED paper).
- SpecificationPoint resolution: NOT SCOREABLE (zero HUMAN_VALIDATED chunk-to-SP mapping rows; T-C06/F-168 substrate pending) — recorded as a named data gap, never fabricated.

## Reading

- The fabric is production code but NOT a serving default: nothing in production constructs a RetrievalFabric; promotion happens in the owning lane with its own verification discipline after the owner accepts a verdict.
- C vs A/B: fusion rewards agreement; read the dual view against the recorded arms. The compliant view is the configuration a promotion would actually serve; the served view is the production-truth measurement the ratified gate runs on.
- Determinism: no clocks in scoring (latency is an ops field, measured outside rankings); aggregates byte-identical across the double pass.
