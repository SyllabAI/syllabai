# Run 005-d-r1 — D hybrid+rerank arm (arm C + the pre-registered lexical-precision reranker; §8.1 v1.1 dual-view bars; the rank-quality lane's first recorded run)

**Status:** RECORDED — production hybrid arm + downstream reranker on record (deterministic, offline replay, zero API calls; snapshot snap-007 (frozen snapshot)).
**Arm:** D hybrid+rerank — the arm-C production fabric (com.syllabai.retrieval.RetrievalFabric: explicit arms [pgvector, bm25], central BoundaryPolicy, shipped ReciprocalRankFusion k=60, rank-only) with the LexicalPrecisionReranker applied DOWNSTREAM of fusion behind the production EvidenceReranker port (registry row D; pre-registered design: the rank-quality-lane charter) over arm A's production vector path and arm B's production lexical path; chunk+query vectors replayed from the frozen artifact embed-backfill-snap-007-preload, zero API calls at run time.
**Executor:** production code over a real Flyway-migrated Postgres, corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served through the production EmbeddingProvider port; no retrieval SQL changed, no fusion code written (the shipped ReciprocalRankFusion runs unchanged); the bench-scope reranker runs as a pure post-fusion reorder (deterministic, zero API calls, no boundary interaction) — code `d1d56cd39eb0812efd47817ecfe7fab37e7d8a50` (branch feat/t-c63-arm-d, rebased over core main 5a8d57f; the same Run005C orchestrator in its env-gated arm-D mode — BENCH_RUN_ID=run-005-d BENCH_ARM_D_RERANKER=lexical_precision — default path byte-identical by construction, suite 1202 green).
**Date:** 2026-10-02 | **Gold:** gold-v5 (120 queries; frozen) | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Why this run exists (the commission)

The rank-quality lane (T-C63, operator commission trace `1a0fc8c1e8b73939`) attacks the binding constraint run-005-c-r9 recorded: the wave unlock moved pool coverage (recall@10 doubled; the first §8.1 bar PASS), but MRR 0.0700 at recall@20 0.1612 priced the gold evidence at median depth ~14 — found, not ranked. The charter (rank-quality-lane-2026-10-02) pre-registered arm D's instrument BEFORE any run (spec §9 anti-gaming): a deterministic BM25-style query×content rescoring of the fused pool (per-query pool IDF, k1=1.2, **b=0** — no length normalization, declared because a length penalty would demote exactly the spec-mapped notes carriers §8(d) prices; no kind awareness; no gold knowledge), behind the PRODUCTION `EvidenceReranker` port (T-024), strictly downstream of fusion, with the pre-fusion boundary untouched (§8(f) structurally unaffected). Same frozen inputs as r9 — snap-007 × gold-r9 × preload-r9, no re-freeze: the comparison basis is the recorded r9 fabric.

## Fabric provenance

- Orchestrator: `RetrievalFabric` composes the explicit arms [pgvector, bm25] (never injection-implied, E-1 forward note), applies the serving boundary ONCE centrally pre-fusion, and fuses with the shipped `ReciprocalRankFusion` k=60 — no new fusion code, no retrieval SQL changed. Per-arm candidate bound 20. MIN_COSINE = 0.50 (the T-C42 calibrated floor) — unchanged since r8.
- Reranker: `LexicalPrecisionReranker` — pre-registered in the T-C63 charter before this run; implements the production port; bench-scope by design (the harness measures; promotion is an owning-lane decision behind the same port).
- Frozen artifact `embed-backfill-snap-007-preload`: model `gemini-embedding-001` @ 768 dims; verified fail-closed against this run's frozen inputs before anything ran; SHA-256 echo in results.json `embedding_artifact.sha256_echo`. The disposable execution environment is the T-C59 recipe (user-space PostgreSQL 17.11 + pgvector 0.8.0 Debian-native debs — the docker-layer binaries' stack-smash defect re-confirmed and the dpkg -x fix re-applied; JDK 25.0.4.1, Maven 3.9.9; cluster re-attached to the r9-replayed data dir, corpus 4,510 embedded chunks at rev 2 re-verified by the run's fail-closed checks).

## Overall (chunk axis, n=89 labeled queries)

- **D served (fabric + rerank, ALL denominator, 4510 embedded chunks):** recall@5 0.1279 · recall@10 0.1463 · recall@20 0.1612 · mrr 0.0936 · ndcg@10 0.1816 · evidence_precision@10 0.0427 · false_positive_rate@10 0.9573
- **D compliant (central VALIDATED gate pre-fusion, 702 reachable chunks — the T-C05-closed configuration):** identical to served (production arms gate internally at rev2 — the as-served stream IS the compliant configuration, the r9 finding unchanged).
- **r9 → r10 (the rank-quality unlock, measured):** recall@5 **0.0616 → 0.1279 (+107.6%)** · recall@10 **0.1043 → 0.1463 (+40.3%)** · recall@20 **0.1612 → 0.1612 (±0.0%)** · mrr **0.0700 → 0.0936 (+33.7%)** · ndcg@10 **0.1113 → 0.1816 (+63.2%)** · evidence_precision@10 0.0303 → 0.0427.
- **Set-identity proof:** the reranked top-20 is a PERMUTATION of r9's fused top-20 on **89/89 queries** (per-query ref sets compared from the recorded bytes). The reranker changed ordering and nothing else — every recall@10/MRR/nDCG movement below rank 20's boundary is pure rank-quality lift; recall@20's exact invariance is a set-level theorem of this run, not a coincidence.
- Prior arms (the recorded context block, identical to r9's): A0 (run-002) all zeros · B (run-003, gold-v1 × snap-001 era) mrr 0.1224 · A served (run-004, gold-v1 × snap-001 era) recall@10 0.1806 — different snapshot/gold generations; read as registry context, not as a same-basis comparison.

## Per class (D served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.085 | 0.085 | 0.085 | 0.25 | 0.2631 | 0.0425 | 0.9575 |
| conceptual | 0.0256 | 0.1538 | 0.1949 | 0.0 | 0.1154 | 0.0197 | 0.9803 |
| exam_question | 0.9 | 1.0 | 1.0 | 0.75 | 0.7954 | 0.1 | 0.9 |
| factual | 0.1273 | 0.2273 | 0.2273 | 0.0 | 0.3025 | 0.0205 | 0.9795 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 0.0 | 0.12 | 0.12 | 0.0 | 0.1018 | 0.0 | 1.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0286 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.0 | 0.0333 | 0.0833 | 0.0 | 0.0453 | 0.0 | 1.0 |
| vague_learner | 0.0 | 0.25 | 0.25 | 0.0 | 0.2016 | 0.025 | 0.975 |
| why_wrong | 0.2167 | 0.1067 | 0.1067 | 0.2833 | 0.3151 | 0.0533 | 0.9467 |

The reranker's lifts: **vague_learner recall@10 0.000 → 0.2500** (r9's pool-composition loss fully recovered — its gold was in the pool, unrated), why_wrong MRR 0.1091 → 0.2833 and nDCG@10 0.1533 → 0.3151, misconception recall@10 0.000 → 0.1200, factual recall@10 0.1727 → 0.2273 with nDCG nearly doubling (0.1798 → 0.3025), conceptual nDCG 0.0708 → 0.1154, exam_question MRR 0.6607 → 0.7500 (recall@10 stays 1.00). mark_scheme and multi_spec_point stay at their recorded substrate-absent/sparse floors (exclusion reason unchanged since r8).

## S8 gate arithmetic (§8 v1.1 re-index 2026-10-01, spec §8.1; ruling 1: ALL denominator = served view; VALIDATED bars on the compliant view; v1.0 reference retained)

- (a) ALL bars, served view — Recall@10: **0.1463** vs floor 0.192 -> FAIL (needs +31.2% from here)
- (b) ALL bars, served view — MRR: **0.0936** vs floor 0.1237 -> FAIL (needs +32.2%)
- (c) ALL bars, served view — nDCG@10: **0.1816** vs floor 0.2316 -> FAIL (needs +27.5%)
- (a2) VALIDATED bars, compliant view — Recall@10: **0.1463** vs floor 0.0734 -> PASS (held from r9)
- (b2) VALIDATED bars, compliant view — MRR: **0.0936** vs floor 0.1184 -> FAIL (needs +26.5%; r9 stood at 0.0700 — the gap closed by 42% of its width)
- (c2) VALIDATED bars, compliant view — nDCG@10: **0.1816** vs floor 0.1683 -> PASS — **the second §8.1 bar PASS in the series' history** (r9's first was (a2) VALIDATED recall)
- (d) SpecificationPoint resolution: **0.4607 / 0.7857 — UNCHANGED from r9, exactly** (66/84 gold points on 89 scored queries; the projection census pinned 210/209/164/181; `4CH1-PR-08` remains the single unbridged gold point). No new regression and no recovery: the S8D-RULING-REVIEW ledger's 9 displaced carriers sit BEYOND the per-arm-20 candidate pools (they were pushed out of both arms' top-20s by the wave's paper mass), and a post-fusion reranker structurally cannot reach evidence that is not in its pool. The raw −10.11pp/−13.10pp movement vs the r8 baseline therefore stands as recorded, pending the spec-owner ruling (compositionality reading); this run adds the mechanism finding: **(d) recovery is pool-side (per-arm depth / pool composition), not rerank-side**.
- (e) p95 latency: not evaluable from records (A0 p95 not recorded); this run records retrieval-only p50/p95 (305.2/322.7 ms served; r9: 301.5/315.0 ms) — the in-process rerank over ≤40 fused candidates adds microseconds, well inside any §8(e) reading; a deployed hybrid adds the production query-embedding round-trip.
- (f) Validation boundary: served view surfaced **0** non-VALIDATED hits — PASS (hard requirement per §5.1). The compliant view audited **0** by construction. The reranker cannot re-admit boundary-excluded candidates (identity-checked, fail-closed).
- (g) Per-class regression: **zero regressions vs r9** — every class improved or held (vague_learner recovered, why_wrong +23% recall@10 inside all allowances, no class regressed at all). Satisfied with no tradeoff notes required.
- **VERDICT: NOT PROMOTED** (promotion requires BOTH views to pass ALL six checks; (a)(b)(c) fail on the ALL view and (b2) fails on the VALIDATED view — even with two bars now passing).

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS (served view): 0. The compliant view's central pre-fusion gate audited ZERO violations across all 120 queries; the reranker seam is boundary-blind by construction (it sees only what the fabric produced).
- Zero-result queries (served): 0/120. Compliant-starved queries: 0.
- SpecificationPoint resolution (spec_resolution_hv): full-coverage 0.4607 · micro-average 0.7857 over 84 gold points on 89 scored queries (served ALL-denominator view; compliant view reported alongside — identical, the r9 finding unchanged). Projection census pinned (210 rows / 209 with refs / 164 distinct refs / 181 distinct codes).
- Determinism: PASS — scoring recomputed twice in-process (second full retrieval pass through the reranker), both views' aggregates byte-identical.

## Reading

- **The rank-quality lever works exactly where the diagnosis said it would.** Within a provably fixed top-20 set (89/89 permutation), pure re-ordering bought +40.3% recall@10, +107.6% recall@5, +33.7% MRR, +63.2% nDCG@10 — and the second §8.1 bar PASS in the series (VALIDATED nDCG@10). The (g) axis is now clean: zero per-class regressions; r9's vague_learner loss was itself a rank artifact and the reranker recovered it.
- **The (d) recovery is pool-side — the recorded next lever.** The displaced §8(d) carriers are outside the per-arm-20 pools; no post-fusion reranker can reach them. The pool composition (per-arm depth, the cosine floor's interaction with the newly-thick paper mass, arm D's ordering inside a deeper pool) is where the next tranche's design space lives — with the fusion-weights lever (charter tranche 3) still unmeasured.
- **What still separates the run from PROMOTED:** the ALL-view floors need +31.2% recall@10, +32.2% MRR, +27.5% nDCG@10 from here, and (b2) needs +26.5%. Two of six bars pass; four fail. The reranker narrowed (b2) by 42% of its gap width in one tranche.
- The fabric+reranker is production-shaped but NOT a serving default: nothing in production constructs a reranking fabric; arm promotion happens in the owning lane with its own verification discipline after the owner accepts a verdict.
- Instrument notes: this is the first run recorded through Run005C's env-gated arm-D mode (default path byte-identical by construction — the same orchestrator, no replay-only branch); the r9-era run_id hardcode is now env-driven (BENCH_RUN_ID) per the T-C40 bproxy env-identity lesson.
