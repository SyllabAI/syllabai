# Run 005 — C hybrid arm, first recorded run (the retrieval fabric orchestrator)

**Status:** RECORDED — production hybrid arm on record (deterministic, offline replay, zero API calls; snapshot snap-001).
**Arm:** C hybrid — PRODUCTION retrieval fabric (com.syllabai.retrieval.RetrievalFabric: explicit arms [pgvector, bm25], central BoundaryPolicy, shipped ReciprocalRankFusion k=60, rank-only, NoReranker) over arm A's production vector path and arm B's production lexical path; chunk+query vectors replayed from the frozen artifact embed-backfill-snap-001, zero API calls at run time
**Executor:** production code over real Postgres migrated V1..V28 (Flyway), corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served through the production EmbeddingProvider port; no retrieval SQL changed, no fusion code written (the shipped ReciprocalRankFusion runs unchanged) — code `c05efb98355ada8a3328c2781148072b556c8c24`.
**Date:** 2026-09-17 | **Gold:** gold-v1 frozen | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Fabric provenance

- Orchestrator: the registered gap CLOSED — `RetrievalFabric` composes the explicit arms [pgvector, bm25] (never injection-implied, E-1 forward note), applies the serving boundary ONCE centrally pre-fusion, and fuses with the shipped `ReciprocalRankFusion` k=60 — no new fusion code, no retrieval SQL changed. Per-arm candidate bound 20.
- Frozen artifact `embed-backfill-snap-001`: model `gemini-embedding-001` @ 768 dims; verified fail-closed against this run's frozen inputs before anything ran; SHA-256 echo in results.json `embedding_artifact.sha256_echo`.

## Overall (chunk axis, n=98 labeled queries)

- **C served (fabric over components as they stand, ALL denominator, 2333 embedded chunks):** recall@5 0.1459 · recall@10 0.1908 · recall@20 0.2515 · mrr 0.167 · ndcg@10 0.2775 · evidence_precision@10 0.0582 · false_positive_rate@10 0.9418
- **C compliant (central VALIDATED gate pre-fusion, 27 reachable chunks — the T-C05-closed configuration):** recall@5 0.1087 · recall@10 0.1128 · recall@20 0.1128 · mrr 0.1913 · ndcg@10 0.235 · evidence_precision@10 0.0296 · false_positive_rate@10 0.2878
- **A0 (run-002, zero-vector baseline):** evidence_precision@10 0.0 · false_positive_rate@10 0.0 · mrr 0.0 · ndcg@10 0.0 · recall@10 0.0 · recall@20 0.0 · recall@5 0.0
- **B (run-003, production lexical, VALIDATED-served):** evidence_precision@10 0.0122 · false_positive_rate@10 0.0102 · mrr 0.1224 · ndcg@10 0.1224 · recall@10 0.074 · recall@20 0.074 · recall@5 0.074
- **A served (run-004, production vector, ALL denominator):** evidence_precision@10 0.0571 · false_positive_rate@10 0.9429 · mrr 0.1226 · ndcg@10 0.2418 · recall@10 0.1806 · recall@20 0.2515 · recall@5 0.1204
- **A compliant view (run-004, post-hoc VALIDATED-only filter):** evidence_precision@10 0.0296 · false_positive_rate@10 0.2806 · mrr 0.159 · ndcg@10 0.2107 · recall@10 0.1128 · recall@20 0.1128 · recall@5 0.1087

## Per class (C served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.15 | 0.15 | 0.25 | 0.5559 | 0.5631 | 0.06 | 0.94 |
| conceptual | 0.0769 | 0.0923 | 0.0923 | 0.0 | 0.0842 | 0.0385 | 0.9615 |
| exam_question | 0.875 | 0.875 | 0.875 | 0.875 | 0.8597 | 0.1125 | 0.8875 |
| factual | 0.0917 | 0.2333 | 0.3 | 0.0 | 0.2396 | 0.0917 | 0.9083 |
| mark_scheme | 0.0 | 0.025 | 0.025 | 0.0 | 0.0361 | 0.0125 | 0.9875 |
| misconception | 0.14 | 0.16 | 0.325 | 0.0 | 0.2851 | 0.06 | 0.94 |
| multi_spec_point | 0.0 | 0.0 | 0.0857 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.0833 | 0.15 | 0.2167 | 0.0 | 0.2459 | 0.075 | 0.925 |
| vague_learner | 0.0 | 0.075 | 0.1625 | 0.0 | 0.049 | 0.0375 | 0.9625 |
| why_wrong | 0.13 | 0.2 | 0.24 | 0.3806 | 0.4232 | 0.07 | 0.93 |

## Per class (C compliant view — T-C05-closed configuration)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.15 | 0.15 | 0.15 | 0.6 | 0.6 | 0.06 | 0.35 |
| conceptual | 0.0192 | 0.0192 | 0.0192 | 0.0 | 0.0485 | 0.0077 | 0.3077 |
| exam_question | 0.75 | 0.75 | 0.75 | 0.875 | 0.875 | 0.0875 | 0.375 |
| factual | 0.0333 | 0.05 | 0.05 | 0.0 | 0.113 | 0.025 | 0.2667 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3625 |
| misconception | 0.04 | 0.04 | 0.04 | 0.0 | 0.0877 | 0.02 | 0.17 |
| multi_spec_point | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2714 |
| prerequisite | 0.0333 | 0.0333 | 0.0333 | 0.0 | 0.0731 | 0.0167 | 0.2833 |
| vague_learner | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2625 |
| why_wrong | 0.17 | 0.19 | 0.19 | 0.575 | 0.6287 | 0.08 | 0.25 |

## S8 gate arithmetic (ratified v1.0; ruling 1: ALL denominator = served view)

- (a) Recall@10: **0.1908** vs floor 0.3249 -> FAIL

- (b) MRR: **0.167** vs floor 0.2964 -> FAIL

- (c) nDCG@10: **0.2775** vs floor 0.4799 -> FAIL

- (d) SpecificationPoint resolution: not scoreable (zero chunk-to-SP HUMAN_VALIDATED rows — named data gap; nothing to regress).
- (e) p95 latency: not evaluable from records (A0 p95 not recorded); this run records retrieval-only p50/p95; a deployed hybrid adds the production query-embedding round-trip.
- (f) Validation boundary: served view surfaced **2027** non-VALIDATED hits (the T-C20 vector-surface gap) — hard fail per §5.1 for the as-served configuration; the compliant view audited **0** by construction.
- (g) Per-class regression: trivially satisfied vs the zero A0 baseline.
- **VERDICT: NOT PROMOTED**

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS (served view): 2027. **Named finding, not a silent patch:** the production vector surface predates T-C05; the compliant view's central pre-fusion gate (this run's new production capability) audited ZERO violations across all 120 queries — the gate is the T-C20 closure shape.
- Zero-result queries (served): 0/120.
- Compliant-starved queries: 10 (served non-empty but every eligible-rank hit sits on a non-VALIDATED paper).
- SpecificationPoint resolution: NOT SCOREABLE (zero HUMAN_VALIDATED chunk-to-SP mapping rows; T-C06/F-168 substrate pending) — recorded as a named data gap, never fabricated.

## Reading

- The fabric is production code but NOT a serving default: nothing in production constructs a RetrievalFabric; promotion happens in the owning lane with its own verification discipline after the owner accepts a verdict.
- C vs A/B: fusion rewards agreement; read the dual view against the recorded arms. The compliant view is the configuration a promotion would actually serve; the served view is the production-truth measurement the ratified gate runs on.
- Determinism: no clocks in scoring (latency is an ops field, measured outside rankings); aggregates byte-identical across the double pass.
