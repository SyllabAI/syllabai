# Run 004 — A semantic arm, first recorded run (embedding backfill + arm A)

**Status:** RECORDED — production semantic arm on record (LOCAL VERIFIED; deterministic, offline replay, zero API calls; snapshot snap-003).
**Arm:** A semantic — PRODUCTION vector serving path (ContentRetrievalService → ChunkVectorRepository.searchServingEligible: pgvector 1-(embedding <=> q) cosine over V11 vector(768), T-C07 scope EXISTS predicate + T-C05/T-C20 VALIDATED-only serving gate; ContentVectorRetriever cosine floor 0.15, kind-agnostic) — chunk+query vectors replayed from the frozen artifact embed-backfill-snap-001, zero API calls at run time, NoReranker
**Executor:** production code over real Postgres migrated V1..V28 (Flyway), corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served from it through the production EmbeddingProvider port; no scorer reimplemented — the retrieval surface is the T-C20 serving-eligible production path (the historical run-004-a record predates that gate and is preserved unchanged) — code `45f6774d7e3f6e575afa4a03d70fbb4724f93df6`.
**Date:** 2026-09-27 | **Gold:** gold-v1 frozen | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Embedding backfill provenance

- Artifact `embed-backfill-snap-001`: model `gemini-embedding-001` @ 768 dims, task types RETRIEVAL_DOCUMENT (chunks) / RETRIEVAL_QUERY (queries); computed through the PRODUCTION EmbeddingProvider bean path and stored through the real ChunkVectorRepository.storeEmbedding, then frozen (SHA256SUMS) — compute-once-freeze-forever. Verified fail-closed against this run's frozen inputs before anything ran.
- The codebase default `text-embedding-004` is RETIRED (404, probed 2026-09-17 with a valid key); the artifact used the successor `gemini-embedding-001` at explicit outputDimensionality=768 (vector(768)-compatible). The production default repair is a separately registered row, not part of this benchmark slice.
- Artifact SHA-256 echo: results.json `embedding_artifact.sha256_echo`.

## Overall (chunk axis, n=89 labeled queries)

- **A served (production vector surface, T-C07-scoped, 3831 embedded chunks):** recall@5 0.0 · recall@10 0.0 · recall@20 0.0 · mrr 0.0 · ndcg@10 0.0 · evidence_precision@10 0.0 · false_positive_rate@10 0.0
- **A compliant view (post-hoc VALIDATED-only filter of the served top-20, 0 reachable chunks):** recall@5 0.0 · recall@10 0.0 · recall@20 0.0 · mrr 0.0 · ndcg@10 0.0 · evidence_precision@10 0.0 · false_positive_rate@10 0.0
- **B (run-003-b, production lexical, VALIDATED-served scope):** evidence_precision@10 0.0 · false_positive_rate@10 0.0 · mrr 0.0 · ndcg@10 0.0 · recall@10 0.0 · recall@20 0.0 · recall@5 0.0
- **A0 chunk axis (run-002):** all zeros by production truth (0/2,333 embedded at the time) — superseded by this run once the backfill artifact landed.

## Per class (A served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| conceptual | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| exam_question | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| factual | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| misconception | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| prerequisite | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| vague_learner | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| why_wrong | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Per class (A compliant view — comparable scope with arm B)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| conceptual | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| exam_question | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| factual | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| misconception | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| prerequisite | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| vague_learner | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| why_wrong | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS (served view): 0. **T-C20 CLOSED — zero is the contract:** the production vector surface (ChunkVectorRepository.searchServingEligible via ContentRetrievalService) now enforces the T-C07 curriculum-scope predicate AND the VALIDATED-only serving gate, mirroring the lexical surface (ChunkLexicalRepository.searchServingEligible). Any non-zero count here is a REGRESSION, not a finding. The historical run-004-a record — which surfaced the finding because the vector surface then predated T-C05 — is preserved unchanged.
- SpecificationPoint resolution: NOT SCOREABLE for arm A — zero HUMAN_VALIDATED chunk→spec mapping rows in the snapshot (concept_attachments = 0; T-C06/F-168 substrate pending). Recorded as a named data gap, never fabricated.
- Zero-result queries: 120/120 (all top-20 hits below the production cosine floor 0.15 — honest empties, scored as real zeros).
- Compliant-starved queries: 0 (served non-empty but every hit sits on a non-VALIDATED paper — expected 0 post-T-C20; non-zero means the gate and the audit disagree, investigate).

## Reading

- Arm A drives the PRODUCTION vector serving path (ContentRetrievalService → ChunkVectorRepository.searchServingEligible pgvector cosine; ContentVectorRetriever floor 0.15, kind-agnostic) — no scorer was reimplemented; the retrieval surface is the T-C20 serving-eligible gate. The only stubbed surface is the embedding CALL itself, replayed from the frozen artifact through the production EmbeddingProvider port (compute-once-freeze-forever).
- Served vs compliant view: post-T-C20 both views score the VALIDATED-only surface — the served view is production truth, the compliant view an independent post-hoc filter retained as the cross-check (agreement expected; disagreement is itself a defect signal). Cross-arm comparisons remain evaluation context for the §8 gate arithmetic, not promotion evidence.
- A vs B: arm B's numbers come from run-003-b (production lexical arm, VALIDATED-served scope, same frozen gold, same formulas). Any hybrid (arm C) verdict requires the orchestrator, which does not exist yet (the retrieval fabric has port + 4 adapters and ZERO consumers — the registered gap).
- Determinism: query vectors are frozen artifact rows keyed by the stripped query text (fail-closed on any unseen text via a deliberately non-IllegalStateException — the production retriever degrades IllegalStateException to an honest empty, which would silently corrupt the measurement); chunk vectors are float4-exact artifact rows re-stored through the real storeEmbedding. No clocks, no randomness; aggregates byte-identical across the double pass.
