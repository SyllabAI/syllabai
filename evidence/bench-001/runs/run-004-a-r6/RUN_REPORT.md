# Run 004 — A semantic arm, first recorded run (embedding backfill + arm A)

**Status:** RECORDED — production semantic arm on record (LOCAL VERIFIED; deterministic, offline replay, zero API calls; snapshot snap-005).
**Arm:** A semantic — PRODUCTION vector serving path (ContentRetrievalService → ChunkVectorRepository.searchServingEligible: pgvector 1-(embedding <=> q) cosine over V11 vector(768), T-C07 scope EXISTS predicate + T-C05/T-C20 VALIDATED-only serving gate; ContentVectorRetriever cosine floor 0.15, kind-agnostic) — chunk+query vectors replayed from the frozen artifact embed-backfill-snap-005, zero API calls at run time, NoReranker
**Executor:** production code over a real Flyway-migrated Postgres, corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served from it through the production EmbeddingProvider port; no scorer reimplemented — the retrieval surface is the T-C20 serving-eligible production path (the historical run-004-a record predates that gate and is preserved unchanged) — code `05f2621690843123758fe271bdfcacae9b4ed220`.
**Date:** 2026-09-28 | **Gold:** gold-v3 (120 queries; frozen) | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Embedding backfill provenance

- Artifact `embed-backfill-snap-005`: model `gemini-embedding-001` @ 768 dims, task types RETRIEVAL_DOCUMENT (chunks) / RETRIEVAL_QUERY (queries); computed through the PRODUCTION EmbeddingProvider bean path and stored through the real ChunkVectorRepository.storeEmbedding, then frozen (SHA256SUMS) — compute-once-freeze-forever. Verified fail-closed against this run's frozen inputs before anything ran.
- The codebase default `text-embedding-004` is RETIRED (404, probed 2026-09-17 with a valid key); the artifact used the successor `gemini-embedding-001` at explicit outputDimensionality=768 (vector(768)-compatible). The production default repair is a separately registered row, not part of this benchmark slice.
- Artifact SHA-256 echo: results.json `embedding_artifact.sha256_echo`.

## Overall (chunk axis, n=89 labeled queries)

- **A served (production vector surface, T-C07-scoped, 4181 embedded chunks):** recall@5 0.0627 · recall@10 0.074 · recall@20 0.0852 · mrr 0.035 · ndcg@10 0.1166 · evidence_precision@10 0.0213 · false_positive_rate@10 0.9787
- **A compliant view (post-hoc VALIDATED-only filter of the served top-20, 322 reachable chunks):** recall@5 0.0627 · recall@10 0.074 · recall@20 0.0852 · mrr 0.035 · ndcg@10 0.1166 · evidence_precision@10 0.0213 · false_positive_rate@10 0.9787
- **B (run-003-b, production lexical, VALIDATED-served scope):** evidence_precision@10 0.0045 · false_positive_rate@10 0.0112 · mrr 0.0449 · ndcg@10 0.0449 · recall@10 0.0247 · recall@20 0.0247 · recall@5 0.0247
- **A0 chunk axis (run-002):** all zeros by production truth (0/2,333 embedded at the time) — superseded by this run once the backfill artifact landed.

## Per class (A served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.02 | 0.02 | 0.02 | 0.0333 | 0.05 | 0.01 | 0.99 |
| conceptual | 0.0385 | 0.0385 | 0.0538 | 0.0 | 0.0769 | 0.0077 | 0.9923 |
| exam_question | 0.5 | 0.5 | 0.5 | 0.2708 | 0.3904 | 0.075 | 0.925 |
| factual | 0.0545 | 0.1455 | 0.1636 | 0.0 | 0.2121 | 0.0364 | 0.9636 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 0.02 | 0.02 | 0.06 | 0.0 | 0.0387 | 0.01 | 0.99 |
| multi_spec_point | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.05 | 0.05 | 0.0667 | 0.0 | 0.1053 | 0.025 | 0.975 |
| vague_learner | 0.125 | 0.125 | 0.125 | 0.0 | 0.1077 | 0.025 | 0.975 |
| why_wrong | 0.0983 | 0.0983 | 0.0983 | 0.17 | 0.2905 | 0.05 | 0.95 |

## Per class (A compliant view — comparable scope with arm B)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.02 | 0.02 | 0.02 | 0.0333 | 0.05 | 0.01 | 0.99 |
| conceptual | 0.0385 | 0.0385 | 0.0538 | 0.0 | 0.0769 | 0.0077 | 0.9923 |
| exam_question | 0.5 | 0.5 | 0.5 | 0.2708 | 0.3904 | 0.075 | 0.925 |
| factual | 0.0545 | 0.1455 | 0.1636 | 0.0 | 0.2121 | 0.0364 | 0.9636 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 0.02 | 0.02 | 0.06 | 0.0 | 0.0387 | 0.01 | 0.99 |
| multi_spec_point | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.05 | 0.05 | 0.0667 | 0.0 | 0.1053 | 0.025 | 0.975 |
| vague_learner | 0.125 | 0.125 | 0.125 | 0.0 | 0.1077 | 0.025 | 0.975 |
| why_wrong | 0.0983 | 0.0983 | 0.0983 | 0.17 | 0.2905 | 0.05 | 0.95 |

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS (served view): 0. **T-C20 CLOSED — zero is the contract:** the production vector surface (ChunkVectorRepository.searchServingEligible via ContentRetrievalService) now enforces the T-C07 curriculum-scope predicate AND the VALIDATED-only serving gate, mirroring the lexical surface (ChunkLexicalRepository.searchServingEligible). Any non-zero count here is a REGRESSION, not a finding. The historical run-004-a record — which surfaced the finding because the vector surface then predated T-C05 — is preserved unchanged.
- SpecificationPoint resolution: SCORED (spec_resolution_hv) — full-coverage 0.0 · micro-average 0.0 over 84 gold points on 89 scored queries (served ALL-denominator view; the HV-mapped notes chunks are SUGGESTED content, so a near-zero number on a compliant view is honest production truth — see the section's dual-view caveat). First §8(d)-scoreable run: this run sets the chunk-arm baseline.
- Zero-result queries: 0/120 (all top-20 hits below the production cosine floor 0.15 — honest empties, scored as real zeros).
- Compliant-starved queries: 0 (served non-empty but every hit sits on a non-VALIDATED paper — expected 0 post-T-C20; non-zero means the gate and the audit disagree, investigate).

## Reading

- Arm A drives the PRODUCTION vector serving path (ContentRetrievalService → ChunkVectorRepository.searchServingEligible pgvector cosine; ContentVectorRetriever floor 0.15, kind-agnostic) — no scorer was reimplemented; the retrieval surface is the T-C20 serving-eligible gate. The only stubbed surface is the embedding CALL itself, replayed from the frozen artifact through the production EmbeddingProvider port (compute-once-freeze-forever).
- Served vs compliant view: post-T-C20 both views score the VALIDATED-only surface — the served view is production truth, the compliant view an independent post-hoc filter retained as the cross-check (agreement expected; disagreement is itself a defect signal). Cross-arm comparisons remain evaluation context for the §8 gate arithmetic, not promotion evidence.
- A vs B: arm B's numbers come from run-003-b (production lexical arm, VALIDATED-served scope, same frozen gold, same formulas). Any hybrid (arm C) verdict requires the orchestrator, which does not exist yet (the retrieval fabric has port + 4 adapters and ZERO consumers — the registered gap).
- Determinism: query vectors are frozen artifact rows keyed by the stripped query text (fail-closed on any unseen text via a deliberately non-IllegalStateException — the production retriever degrades IllegalStateException to an honest empty, which would silently corrupt the measurement); chunk vectors are float4-exact artifact rows re-stored through the real storeEmbedding. No clocks, no randomness; aggregates byte-identical across the double pass.
