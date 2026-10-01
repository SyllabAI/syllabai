# Run 005-c-r8 — C hybrid re-record (T-C40 ④ calibration gate: MIN_COSINE 0.50, §8.1 v1.1 dual-view bars)

**Status:** RECORDED — production hybrid arm on record (deterministic, offline replay, zero API calls; snapshot snap-006 (frozen snapshot)).
**Arm:** C hybrid — PRODUCTION retrieval fabric (com.syllabai.retrieval.RetrievalFabric: explicit arms [pgvector, bm25], central BoundaryPolicy, shipped ReciprocalRankFusion k=60, rank-only, NoReranker) over arm A's production vector path and arm B's production lexical path; chunk+query vectors replayed from the frozen artifact embed-backfill-snap-006-preload-copy, zero API calls at run time
**Executor:** production code over a real Flyway-migrated Postgres, corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served through the production EmbeddingProvider port; no retrieval SQL changed, no fusion code written (the shipped ReciprocalRankFusion runs unchanged) — code `06297f2`.
**Date:** 2026-10-01 | **Gold:** gold-v5 (120 queries; frozen) | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Fabric provenance

- Orchestrator: the registered gap CLOSED — `RetrievalFabric` composes the explicit arms [pgvector, bm25] (never injection-implied, E-1 forward note), applies the serving boundary ONCE centrally pre-fusion, and fuses with the shipped `ReciprocalRankFusion` k=60 — no new fusion code, no retrieval SQL changed. Per-arm candidate bound 20.
- Frozen artifact `embed-backfill-snap-006-preload-copy`: model `gemini-embedding-001` @ 768 dims; verified fail-closed against this run's frozen inputs before anything ran; SHA-256 echo in results.json `embedding_artifact.sha256_echo`.

## Overall (chunk axis, n=89 labeled queries)

- **C served (fabric over components as they stand, ALL denominator, 4181 embedded chunks):** recall@5 0.0386 · recall@10 0.0515 · recall@20 0.0717 · mrr 0.0559 · ndcg@10 0.0871 · evidence_precision@10 0.0146 · false_positive_rate@10 0.9854
- **C compliant (central VALIDATED gate pre-fusion, 437 reachable chunks — the T-C05-closed configuration):** recall@5 0.0386 · recall@10 0.0515 · recall@20 0.0717 · mrr 0.0559 · ndcg@10 0.0871 · evidence_precision@10 0.0146 · false_positive_rate@10 0.9854
- **A0 (run-002, zero-vector baseline):** evidence_precision@10 0.0 · false_positive_rate@10 0.0 · mrr 0.0 · ndcg@10 0.0 · recall@10 0.0 · recall@20 0.0 · recall@5 0.0
- **B (run-003, production lexical, VALIDATED-served):** evidence_precision@10 0.0045 · false_positive_rate@10 0.0112 · mrr 0.0449 · ndcg@10 0.0449 · recall@10 0.0247 · recall@20 0.0247 · recall@5 0.0247
- **A served (run-004, production vector, ALL denominator):** evidence_precision@10 0.0146 · false_positive_rate@10 0.9854 · mrr 0.0313 · ndcg@10 0.0684 · recall@10 0.0515 · recall@20 0.0717 · recall@5 0.0273
- **A compliant view (run-004, post-hoc VALIDATED-only filter):** evidence_precision@10 0.0146 · false_positive_rate@10 0.9854 · mrr 0.0313 · ndcg@10 0.0684 · recall@10 0.0515 · recall@20 0.0717 · recall@5 0.0273

## Per class (C served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.02 | 0.02 | 0.02 | 0.1 | 0.1 | 0.01 | 0.99 |
| conceptual | 0.0385 | 0.0385 | 0.0385 | 0.0 | 0.0485 | 0.0077 | 0.9923 |
| exam_question | 0.5 | 0.5 | 0.5 | 0.625 | 0.6577 | 0.075 | 0.925 |
| factual | 0.0364 | 0.0364 | 0.1455 | 0.0 | 0.063 | 0.0182 | 0.9818 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 0.0 | 0.0 | 0.02 | 0.0 | 0.0 | 0.0 | 1.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.0 | 0.0 | 0.0333 | 0.0 | 0.0 | 0.0 | 1.0 |
| vague_learner | 0.0 | 0.125 | 0.125 | 0.0 | 0.0833 | 0.025 | 0.975 |
| why_wrong | 0.0333 | 0.0983 | 0.0983 | 0.1476 | 0.2464 | 0.05 | 0.95 |

## Per class (C compliant view — T-C05-closed configuration)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.02 | 0.02 | 0.02 | 0.1 | 0.1 | 0.01 | 0.99 |
| conceptual | 0.0385 | 0.0385 | 0.0385 | 0.0 | 0.0485 | 0.0077 | 0.9923 |
| exam_question | 0.5 | 0.5 | 0.5 | 0.625 | 0.6577 | 0.075 | 0.925 |
| factual | 0.0364 | 0.0364 | 0.1455 | 0.0 | 0.063 | 0.0182 | 0.9818 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 0.0 | 0.0 | 0.02 | 0.0 | 0.0 | 0.0 | 1.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.0 | 0.0 | 0.0333 | 0.0 | 0.0 | 0.0 | 1.0 |
| vague_learner | 0.0 | 0.125 | 0.125 | 0.0 | 0.0833 | 0.025 | 0.975 |
| why_wrong | 0.0333 | 0.0983 | 0.0983 | 0.1476 | 0.2464 | 0.05 | 0.95 |

## S8 gate arithmetic (§8 v1.1 re-index 2026-10-01, spec §8.1; ruling 1: ALL denominator = served view; VALIDATED bars on the compliant view; v1.0 reference retained)

- (a) ALL bars, served view — Recall@10: **0.0515** vs floor 0.192 -> FAIL

- (b) ALL bars, served view — MRR: **0.0559** vs floor 0.1237 -> FAIL

- (c) ALL bars, served view — nDCG@10: **0.0871** vs floor 0.2316 -> FAIL

- (a2) VALIDATED bars, compliant view — Recall@10: **0.0515** vs floor 0.0734 -> FAIL

- (b2) VALIDATED bars, compliant view — MRR: **0.0559** vs floor 0.1184 -> FAIL

- (c2) VALIDATED bars, compliant view — nDCG@10: **0.0871** vs floor 0.1683 -> FAIL

- (d) SpecificationPoint resolution: not scoreable (zero chunk-to-SP HUMAN_VALIDATED rows — named data gap; nothing to regress).
- (e) p95 latency: not evaluable from records (A0 p95 not recorded); this run records retrieval-only p50/p95; a deployed hybrid adds the production query-embedding round-trip.
- (f) Validation boundary: served view surfaced **0** non-VALIDATED hits (the T-C20 vector-surface gap) — hard fail per §5.1 for the as-served configuration; the compliant view audited **0** by construction.
- (g) Per-class regression: trivially satisfied vs the zero A0 baseline.
- **VERDICT: NOT PROMOTED**

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS (served view): 0. **Named finding, not a silent patch:** the production vector surface predates T-C05; the compliant view's central pre-fusion gate (this run's new production capability) audited ZERO violations across all 120 queries — the gate is the T-C20 closure shape.
- Zero-result queries (served): 0/120.
- Compliant-starved queries: 0 (served non-empty but every eligible-rank hit sits on a non-VALIDATED paper).
- SpecificationPoint resolution: SCORED (spec_resolution_hv) — full-coverage 0.5618 · micro-average 0.9167 over 84 gold points on 89 scored queries (served ALL-denominator view; the HV-mapped notes chunks are SUGGESTED content, so a near-zero number on a compliant view is honest production truth — see the section's dual-view caveat). First §8(d)-scoreable run: this run sets the chunk-arm baseline.
## Reading

- The fabric is production code but NOT a serving default: nothing in production constructs a RetrievalFabric; promotion happens in the owning lane with its own verification discipline after the owner accepts a verdict.
- C vs A/B: fusion rewards agreement; read the dual view against the recorded arms. The compliant view is the configuration a promotion would actually serve; the served view is the production-truth measurement the ratified gate runs on.
- Determinism: no clocks in scoring (latency is an ops field, measured outside rankings); aggregates byte-identical across the double pass.
