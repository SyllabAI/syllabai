# Run 004 — A semantic arm, first recorded run (embedding backfill + arm A)

**Status:** RECORDED — production semantic arm on record (LOCAL VERIFIED; deterministic, offline replay, zero API calls; snapshot snap-001).
**Arm:** A semantic — PRODUCTION vector serving path (ContentRetrievalService → ChunkVectorRepository.search: pgvector 1-(embedding <=> q) cosine over V11 vector(768), T-C07 scope EXISTS predicate; ContentVectorRetriever cosine floor 0.15, kind-agnostic) — chunk+query vectors replayed from the frozen artifact embed-backfill-snap-001, zero API calls at run time, NoReranker
**Executor:** production code over real Postgres migrated V1..V28 (Flyway), corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served from it through the production EmbeddingProvider port; no scorer reimplemented, no retrieval SQL changed — code `c05efb98355ada8a3328c2781148072b556c8c24`.
**Date:** 2026-09-20 | **Gold:** gold-v1 frozen | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Embedding backfill provenance

- Artifact `embed-backfill-snap-001`: model `gemini-embedding-001` @ 768 dims, task types RETRIEVAL_DOCUMENT (chunks) / RETRIEVAL_QUERY (queries); computed through the PRODUCTION EmbeddingProvider bean path and stored through the real ChunkVectorRepository.storeEmbedding, then frozen (SHA256SUMS) — compute-once-freeze-forever. Verified fail-closed against this run's frozen inputs before anything ran.
- The codebase default `text-embedding-004` is RETIRED (404, probed 2026-09-17 with a valid key); the artifact used the successor `gemini-embedding-001` at explicit outputDimensionality=768 (vector(768)-compatible). The production default repair is a separately registered row, not part of this benchmark slice.
- Artifact SHA-256 echo: results.json `embedding_artifact.sha256_echo`.

## Overall (chunk axis, n=44 labeled queries)

- **A served (production vector surface, T-C07-scoped, 2333 embedded chunks):** recall@5 0.0054 · recall@10 0.0064 · recall@20 0.0075 · mrr 0.0108 · ndcg@10 0.0526 · evidence_precision@10 0.0136 · false_positive_rate@10 0.9864
- **A compliant view (post-hoc VALIDATED-only filter of the served top-20, 27 reachable chunks):** recall@5 0.0075 · recall@10 0.0075 · recall@20 0.0075 · mrr 0.0152 · ndcg@10 0.0633 · evidence_precision@10 0.0159 · false_positive_rate@10 0.3477
- **B (run-003-b, production lexical, VALIDATED-served scope):** evidence_precision@10 0.0068 · false_positive_rate@10 0.0023 · mrr 0.0682 · ndcg@10 0.0682 · recall@10 0.0032 · recall@20 0.0032 · recall@5 0.0032
- **A0 chunk axis (run-002):** all zeros by production truth (0/2,333 embedded at the time) — superseded by this run once the backfill artifact landed.

## Per class (A served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| enumerate_paper | 0.0591 | 0.0705 | 0.083 | 0.119 | 0.5786 | 0.15 | 0.85 |
| fetch_null_code | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| fetch_paper_code | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |

## Per class (A compliant view — comparable scope with arm B)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| enumerate_paper | 0.083 | 0.083 | 0.083 | 0.1667 | 0.6959 | 0.175 | 0.3 |
| fetch_null_code | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.16 |
| fetch_paper_code | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.38 |

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS (served view): 2040. **Named finding, not a silent patch:** the production vector surface (ChunkVectorRepository.search) enforces the T-C07 curriculum-scope predicate but predates T-C05 — the VALIDATED-paper predicate exists only on the lexical serving-eligible surface (ChunkLexicalRepository.searchServingEligible). The served view is the production truth; a compliant vector surface is registered as follow-up. This run changes nothing in serving.
- SpecificationPoint resolution: NOT SCOREABLE for arm A — zero HUMAN_VALIDATED chunk→spec mapping rows in the snapshot (concept_attachments = 0; T-C06/F-168 substrate pending). Recorded as a named data gap, never fabricated.
- Zero-result queries: 0/120 (all top-20 hits below the production cosine floor 0.15 — honest empties, scored as real zeros).
- Compliant-starved queries: 6 (served non-empty but every hit sits on a non-VALIDATED paper — the boundary gap's user-visible shape).

## Reading

- Arm A drives the PRODUCTION vector serving path (ContentRetrievalService → ChunkVectorRepository.search pgvector cosine; ContentVectorRetriever floor 0.15, kind-agnostic) — no retrieval SQL or scorer was reimplemented or changed. The only stubbed surface is the embedding CALL itself, replayed from the frozen artifact through the production EmbeddingProvider port (compute-once-freeze-forever).
- Served vs compliant view: the served view scores over the T-C07-scoped corpus (production truth, boundary finding included); the compliant view is a post-hoc VALIDATED-only filter of the same served top-20 — comparable in SCOPE with arm B, but it is NOT a serving simulation (a compliant vector surface would re-rank within the compliant corpus). Treat cross-arm comparisons as evaluation context for the §8 gate arithmetic, not as promotion evidence.
- A vs B: arm B's numbers come from run-003-b (production lexical arm, VALIDATED-served scope, same frozen gold, same formulas). Any hybrid (arm C) verdict requires the orchestrator, which does not exist yet (the retrieval fabric has port + 4 adapters and ZERO consumers — the registered gap).
- Determinism: query vectors are frozen artifact rows keyed by the stripped query text (fail-closed on any unseen text via a deliberately non-IllegalStateException — the production retriever degrades IllegalStateException to an honest empty, which would silently corrupt the measurement); chunk vectors are float4-exact artifact rows re-stored through the real storeEmbedding. No clocks, no randomness; aggregates byte-identical across the double pass.
