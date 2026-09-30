# Run 003 — B lexical arm, first recorded run (T-C14 / T-C13)

**Status:** RECORDED — production lexical arm on record (LOCAL VERIFIED; deterministic, offline, snapshot snap-001).
**Arm:** B lexical — PRODUCTION T-C14 provider (ChunkLexicalRepository SQL: websearch_to_tsquery('english') over V28 content_tsv GIN, ts_rank_cd, T-C07 scope EXISTS predicate, T-C05 VALIDATED-paper serving, identity tie-break document_id/chunk_index) — Bm25Retriever port, NoReranker
**Executor:** production code over real Postgres migrated V1..V28 (Flyway), corpus loaded from the frozen snapshot; no scorer reimplemented. Arm = retrieval.Bm25Retriever through the RetrievalProvider fabric contract over ChunkLexicalRepository.searchServingEligible (T-C05 VALIDATED-only guard) — code `5f7e834774a44bc18b2c21cbed0da7b0e9c72c35`.
**Date:** 2026-09-17 | **Gold:** gold-v1 frozen | **Determinism:** double retrieval pass, byte-identical aggregates.

## Overall (chunk axis, n=98 labeled queries)

- **B (VALIDATED-served corpus, 296 chunks):** recall@5 0.074 · recall@10 0.074 · recall@20 0.074 · mrr 0.1224 · ndcg@10 0.1224 · evidence_precision@10 0.0122 · false_positive_rate@10 0.0102
- **A0 chunk axis (run-002):** all zeros by production truth (0/2,333 embedded) — every chunk-emitting arm beats it by construction; the honest comparison for B is against the B-proxy lexical probes above (same formulas, different scorer) until arm A lands.

## Per class (B, VALIDATED-served scope)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.125 | 0.125 | 0.125 | 0.5 | 0.5 | 0.05 | 0.0 |
| conceptual | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| exam_question | 0.75 | 0.75 | 0.75 | 0.875 | 0.875 | 0.0875 | 0.0 |
| factual | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.125 |
| misconception | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| prerequisite | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| vague_learner | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| why_wrong | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS: 0 (the T-C05 VALIDATED-only predicate held under the real run).
- SpecificationPoint resolution: NOT SCOREABLE for arm B — zero HUMAN_VALIDATED chunk→spec mapping rows in the snapshot (concept_attachments = 0; T-C06/F-168 substrate pending). Recorded as a named data gap, never fabricated.
- Zero-result queries: 106/120 (lexical scorer found no match — honest empties, scored as real zeros).

## Reading

- B runs the PRODUCTION SQL (tsvector/ts_rank_cd) — no scorer port; the only modeling is the corpus loader (checksums + ordinals preserved verbatim).
- Query form: the production bare-word (AND) form leaves 106/120 gold queries with zero candidates — the all-terms requirement starves natural-language questions. A term-union (OR) diagnostic measured better in-session (appendix), but adopting it after seeing frozen-set numbers would violate the anti-tuning rule; it is recorded as a finding for the dev-subset/gold-v2 route.
- B vs B-proxy: same frozen set and compliant corpus, different lexical scorers (Postgres cover-density vs Okapi BM25) — B's chunk axis is BELOW the B-proxy probe on the VALIDATED-only view; that is an honest instrument finding (IDF-weighted term-summing beats pure coverage here), recorded for the hybrid (C) verdict, not a promotion argument either way.
- B vs B-proxy ALL view: the AF-2 boundary gap (0.2954 ALL vs 0.1449 VALIDATED-only) stands; B serves the compliant scope, so gold evidence on SUGGESTED papers is structurally unreachable for it.
- B is a benchmarkable capability, NOT a serving default: Bm25Retriever is not a Spring bean and nothing in production references it; promotion requires §8 gate arithmetic on a hybrid arm (C) after A lands.
## Errata (2026-09-17 — applied post-record, annotation-only; session 91)

- **E-1 — the "not a Spring bean" phrase is false; the conclusion stands, the stated mechanism is corrected.** The Reading section says "Bm25Retriever is not a Spring bean and nothing in production references it". The first half is wrong: `Bm25Retriever` IS a Spring `@Component` (at the recorded base `5f7e834` and at HEAD `8eed5e6` alike). The true and sufficient statement is that **nothing consumes it**: zero production sites inject the `RetrievalProvider` port (`List<RetrievalProvider>` has no consumer at HEAD), and the serving path (`ClaService`) wires the legacy `VectorRetriever`/`KnowledgeRetriever` ports directly — so BM25 enters no serving path and remains NOT a serving default. Forward note for the future fabric orchestrator: a provider-collecting orchestrator would pick this bean up automatically; arm promotion must stay explicit, never injection-implied.
- **E-2 — the pinned code SHA is a base pin, not the exact executed tree.** The Executor line pins `5f7e834774a44bc18b2c21cbed0da7b0e9c72c35`, but committed `5f7e834` contains neither the bench harness (`ArmB`/`Run003B` do not exist there) nor `ChunkLexicalRepository.searchServingEligible` — it cannot be the exact executed state. The run executed from the working tree = `5f7e834` + the uncommitted delta that was pushed verbatim as `8eed5e6` (943 insertions: `searchServingEligible`, the `Bm25Retriever` switch to it, `ArmB`, `Run003B`, `BenchSnapshot`, `LexicalBoundaryIT`, test stubs). What survives the imprecision: the determinism double-pass was byte-identical as recorded; the VALIDATED-only boundary behavior is independently verified at `8eed5e6` by `LexicalBoundaryIT` 2/2 + `ChunkLexicalSearchIT` 3/3 in core-ci `35162299609`; the corpus loader is checksum-verified. `results.json.code_version` carries the same base-SHA semantics and is deliberately left untouched (measured-data artifact). Pre-errata `RUN_REPORT.md` SHA-256: `4b97ef878c8100c2750cd2c5cc21f252671aa6209528db13027d7c14a8b2045a` (as pinned by the original `SHA256SUMS` at master `037bb2d8`); the manifest is regenerated below to pin the amended bytes.
- Neither erratum changes any measured value, verdict, or boundary claim — strictly annotation precision (non-weakening, the P.6 Amendment #1 standard).
