# Run 004 — A semantic arm, first recorded run (embedding backfill + arm A)

**Status:** RECORDED — production semantic arm on record (LOCAL VERIFIED; deterministic, offline replay, zero API calls; snapshot snap-001).
**Arm:** A semantic — PRODUCTION vector serving path (ContentRetrievalService → ChunkVectorRepository.search: pgvector 1-(embedding <=> q) cosine over V11 vector(768), T-C07 scope EXISTS predicate; ContentVectorRetriever cosine floor 0.15, kind-agnostic) — chunk+query vectors replayed from the frozen artifact embed-backfill-snap-001, zero API calls at run time, NoReranker
**Executor:** production code over real Postgres migrated V1..V28 (Flyway), corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served from it through the production EmbeddingProvider port; no scorer reimplemented, no retrieval SQL changed — code `fb2bffa5872cbe083f5cc5726a3ac55df83da26a`.
**Date:** 2026-09-17 | **Gold:** gold-v1 frozen | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Embedding backfill provenance

- Artifact `embed-backfill-snap-001`: model `gemini-embedding-001` @ 768 dims, task types RETRIEVAL_DOCUMENT (chunks) / RETRIEVAL_QUERY (queries); computed through the PRODUCTION EmbeddingProvider bean path and stored through the real ChunkVectorRepository.storeEmbedding, then frozen (SHA256SUMS) — compute-once-freeze-forever. Verified fail-closed against this run's frozen inputs before anything ran.
- The codebase default `text-embedding-004` is RETIRED (404, probed 2026-09-17 with a valid key); the artifact used the successor `gemini-embedding-001` at explicit outputDimensionality=768 (vector(768)-compatible). The production default repair is a separately registered row, not part of this benchmark slice.
- Artifact SHA-256 echo: results.json `embedding_artifact.sha256_echo`.

## Overall (chunk axis, n=98 labeled queries)

- **A served (production vector surface, T-C07-scoped, 2333 embedded chunks):** recall@5 0.1204 · recall@10 0.1806 · recall@20 0.2515 · mrr 0.1226 · ndcg@10 0.2418 · evidence_precision@10 0.0571 · false_positive_rate@10 0.9429
- **A compliant view (post-hoc VALIDATED-only filter of the served top-20, 27 reachable chunks):** recall@5 0.1087 · recall@10 0.1128 · recall@20 0.1128 · mrr 0.159 · ndcg@10 0.2107 · evidence_precision@10 0.0296 · false_positive_rate@10 0.2806
- **B (run-003-b, production lexical, VALIDATED-served scope):** evidence_precision@10 0.0122 · false_positive_rate@10 0.0102 · mrr 0.1224 · ndcg@10 0.1224 · recall@10 0.074 · recall@20 0.074 · recall@5 0.074
- **A0 chunk axis (run-002):** all zeros by production truth (0/2,333 embedded at the time) — superseded by this run once the backfill artifact landed.

## Per class (A served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.15 | 0.15 | 0.25 | 0.3642 | 0.4193 | 0.06 | 0.94 |
| conceptual | 0.0769 | 0.0923 | 0.0923 | 0.0 | 0.0842 | 0.0385 | 0.9615 |
| exam_question | 0.5625 | 0.75 | 0.875 | 0.5709 | 0.6021 | 0.1 | 0.9 |
| factual | 0.0917 | 0.2333 | 0.3 | 0.0 | 0.2396 | 0.0917 | 0.9083 |
| mark_scheme | 0.0 | 0.025 | 0.025 | 0.0 | 0.0361 | 0.0125 | 0.9875 |
| misconception | 0.14 | 0.16 | 0.325 | 0.0 | 0.2851 | 0.06 | 0.94 |
| multi_spec_point | 0.0 | 0.0 | 0.0857 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.0833 | 0.15 | 0.2167 | 0.0 | 0.2459 | 0.075 | 0.925 |
| vague_learner | 0.0 | 0.075 | 0.1625 | 0.0 | 0.049 | 0.0375 | 0.9625 |
| why_wrong | 0.13 | 0.2 | 0.24 | 0.3806 | 0.4232 | 0.07 | 0.93 |

## Per class (A compliant view — comparable scope with arm B)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.15 | 0.15 | 0.15 | 0.475 | 0.5062 | 0.06 | 0.35 |
| conceptual | 0.0192 | 0.0192 | 0.0192 | 0.0 | 0.0485 | 0.0077 | 0.3154 |
| exam_question | 0.75 | 0.75 | 0.75 | 0.6354 | 0.6952 | 0.0875 | 0.375 |
| factual | 0.0333 | 0.05 | 0.05 | 0.0 | 0.113 | 0.025 | 0.2667 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2625 |
| misconception | 0.04 | 0.04 | 0.04 | 0.0 | 0.0877 | 0.02 | 0.17 |
| multi_spec_point | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2714 |
| prerequisite | 0.0333 | 0.0333 | 0.0333 | 0.0 | 0.0731 | 0.0167 | 0.2833 |
| vague_learner | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2625 |
| why_wrong | 0.17 | 0.19 | 0.19 | 0.575 | 0.6287 | 0.08 | 0.25 |

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS (served view): 2026. **Named finding, not a silent patch:** the production vector surface (ChunkVectorRepository.search) enforces the T-C07 curriculum-scope predicate but predates T-C05 — the VALIDATED-paper predicate exists only on the lexical serving-eligible surface (ChunkLexicalRepository.searchServingEligible). The served view is the production truth; a compliant vector surface is registered as follow-up. This run changes nothing in serving.
- SpecificationPoint resolution: NOT SCOREABLE for arm A — zero HUMAN_VALIDATED chunk→spec mapping rows in the snapshot (concept_attachments = 0; T-C06/F-168 substrate pending). Recorded as a named data gap, never fabricated.
- Zero-result queries: 0/120 (all top-20 hits below the production cosine floor 0.15 — honest empties, scored as real zeros).
- Compliant-starved queries: 10 (served non-empty but every hit sits on a non-VALIDATED paper — the boundary gap's user-visible shape).

## Reading

- Arm A drives the PRODUCTION vector serving path (ContentRetrievalService → ChunkVectorRepository.search pgvector cosine; ContentVectorRetriever floor 0.15, kind-agnostic) — no retrieval SQL or scorer was reimplemented or changed. The only stubbed surface is the embedding CALL itself, replayed from the frozen artifact through the production EmbeddingProvider port (compute-once-freeze-forever).
- Served vs compliant view: the served view scores over the T-C07-scoped corpus (production truth, boundary finding included); the compliant view is a post-hoc VALIDATED-only filter of the same served top-20 — comparable in SCOPE with arm B, but it is NOT a serving simulation (a compliant vector surface would re-rank within the compliant corpus). Treat cross-arm comparisons as evaluation context for the §8 gate arithmetic, not as promotion evidence.
- A vs B: arm B's numbers come from run-003-b (production lexical arm, VALIDATED-served scope, same frozen gold, same formulas). Any hybrid (arm C) verdict requires the orchestrator, which does not exist yet (the retrieval fabric has port + 4 adapters and ZERO consumers — the registered gap).
- Determinism: query vectors are frozen artifact rows keyed by the stripped query text (fail-closed on any unseen text via a deliberately non-IllegalStateException — the production retriever degrades IllegalStateException to an honest empty, which would silently corrupt the measurement); chunk vectors are float4-exact artifact rows re-stored through the real storeEmbedding. No clocks, no randomness; aggregates byte-identical across the double pass.
