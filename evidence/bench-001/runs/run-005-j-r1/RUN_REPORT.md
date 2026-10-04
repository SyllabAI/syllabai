# Run 005 — C hybrid arm, precision-side cosine trim posture (the T-C83 MIN_COSINE lever, TRIM form)

**Status:** RECORDED — production hybrid arm on record (deterministic, offline replay, zero API calls; snapshot snap-007 (frozen snapshot)).
**Arm:** C hybrid — PRODUCTION retrieval fabric (com.syllabai.retrieval.RetrievalFabric: explicit arms [pgvector, bm25], central BoundaryPolicy, shipped ReciprocalRankFusion k=60, rank-only, NoReranker) over arm A's production vector path and arm B's production lexical path with the vector arm's post-cut candidates trimmed to cosine >= 0.6 (the T-C83 precision-side MIN_COSINE lever, TRIM form — removal-only, the production constant's own post-cut filter shape, the list under-fills and never backfills, pre-registered BEFORE this run); chunk+query vectors replayed from the frozen artifact embed-backfill-snap-007-preload, zero API calls at run time
**Executor:** production code over a real Flyway-migrated Postgres, corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served through the production EmbeddingProvider port; no retrieval SQL changed, no fusion code written (the shipped ReciprocalRankFusion runs unchanged); the precision-side cosine trim (theta=0.6) runs as a pure post-cut removal filter on the vector arm's candidates (the production MIN_COSINE constant's own filter shape at the bench posture; deterministic, zero API calls, no boundary interaction; the list under-fills and never backfills; pre-registered in MIN-COSINE-PREREGISTRATION.md BEFORE this run) — code `6cad6ef9463e8d21f1555456561a4caaf7e89395`.
**Date:** 2026-10-04 | **Gold:** gold-v5 (120 queries; frozen) | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Fabric provenance

- Orchestrator: the registered gap CLOSED — `RetrievalFabric` composes the explicit arms [pgvector, bm25] (never injection-implied, E-1 forward note), applies the serving boundary ONCE centrally pre-fusion, and fuses with the shipped `ReciprocalRankFusion` k=60 — no new fusion code, no retrieval SQL changed. Per-arm candidate bound 40.
- Min-cosine trim: the vector arm's post-cut candidates filtered to cosine >= 0.6 (the T-C83 precision-side MIN_COSINE lever, TRIM form — the production constant's own post-cut filter shape at the bench posture; REMOVAL-ONLY: the list under-fills and never backfills, the bm25 arm untouched — bm25 has no cosine; survivors' fused scores byte-identical, the whole posture's delta is the removed-ref ledger; 295 candidates removed per the idempotent per-query ledger; pre-registered in MIN-COSINE-PREREGISTRATION.md BEFORE this run).
- Frozen artifact `embed-backfill-snap-007-preload`: model `gemini-embedding-001` @ 768 dims; verified fail-closed against this run's frozen inputs before anything ran; SHA-256 echo in results.json `embedding_artifact.sha256_echo`.

## Overall (chunk axis, n=89 labeled queries)

- **C served (fabric over components as they stand, ALL denominator, 4510 embedded chunks):** recall@5 0.0616 · recall@10 0.1043 · recall@20 0.1612 · mrr 0.07 · ndcg@10 0.1095 · evidence_precision@10 0.0303 · false_positive_rate@10 0.9663
- **C compliant (central VALIDATED gate pre-fusion, 702 reachable chunks — the T-C05-closed configuration):** recall@5 0.0616 · recall@10 0.1043 · recall@20 0.1612 · mrr 0.07 · ndcg@10 0.1095 · evidence_precision@10 0.0303 · false_positive_rate@10 0.9663

## Per class (C served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.085 | 0.085 | 0.085 | 0.25 | 0.2631 | 0.04 | 0.96 |
| conceptual | 0.0256 | 0.1282 | 0.1949 | 0.0 | 0.0708 | 0.0308 | 0.9692 |
| exam_question | 0.75 | 1.0 | 1.0 | 0.6607 | 0.7104 | 0.15 | 0.85 |
| factual | 0.0727 | 0.1727 | 0.2273 | 0.0 | 0.1652 | 0.0727 | 0.9182 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 0.0 | 0.0 | 0.12 | 0.0 | 0.0 | 0.0 | 1.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0286 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.0 | 0.0 | 0.0833 | 0.0 | 0.0 | 0.0 | 1.0 |
| vague_learner | 0.0 | 0.0 | 0.25 | 0.0 | 0.0 | 0.0 | 0.95 |
| why_wrong | 0.05 | 0.0867 | 0.1067 | 0.1091 | 0.1533 | 0.05 | 0.95 |

## Per class (C compliant view — T-C05-closed configuration)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.085 | 0.085 | 0.085 | 0.25 | 0.2631 | 0.04 | 0.96 |
| conceptual | 0.0256 | 0.1282 | 0.1949 | 0.0 | 0.0708 | 0.0308 | 0.9692 |
| exam_question | 0.75 | 1.0 | 1.0 | 0.6607 | 0.7104 | 0.15 | 0.85 |
| factual | 0.0727 | 0.1727 | 0.2273 | 0.0 | 0.1652 | 0.0727 | 0.9182 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 0.0 | 0.0 | 0.12 | 0.0 | 0.0 | 0.0 | 1.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0286 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.0 | 0.0 | 0.0833 | 0.0 | 0.0 | 0.0 | 1.0 |
| vague_learner | 0.0 | 0.0 | 0.25 | 0.0 | 0.0 | 0.0 | 0.95 |
| why_wrong | 0.05 | 0.0867 | 0.1067 | 0.1091 | 0.1533 | 0.05 | 0.95 |

## S8 gate arithmetic (§8 v1.1 re-index 2026-10-01, spec §8.1; ruling 1: ALL denominator = served view; VALIDATED bars on the compliant view; v1.0 reference retained)

- (a) ALL bars, served view — Recall@10: **0.1043** vs floor 0.192 -> FAIL

- (b) ALL bars, served view — MRR: **0.07** vs floor 0.1237 -> FAIL

- (c) ALL bars, served view — nDCG@10: **0.1095** vs floor 0.2316 -> FAIL

- (a2) VALIDATED bars, compliant view — Recall@10: **0.1043** vs floor 0.0734 -> PASS

- (b2) VALIDATED bars, compliant view — MRR: **0.07** vs floor 0.1184 -> FAIL

- (c2) VALIDATED bars, compliant view — nDCG@10: **0.1095** vs floor 0.1683 -> FAIL

- (d) SpecificationPoint resolution: SCORED (spec_resolution_hv): full-coverage 0.4944 · micro-average 0.8452 on the ALL-denominator view over 84 gold points — first §8(d)-scoreable run: this run SETS the chunk-arm baseline; the §8(d) 'no regression beyond 1pp' rule applies from the next run onward, and no promotion claim is made on (d) here
- (e) p95 latency: not evaluable from records (A0 p95 not recorded); this run records retrieval-only p50/p95; a deployed hybrid adds the production query-embedding round-trip.
- (f) Validation boundary: served view surfaced **0** non-VALIDATED hits (the T-C20 vector-surface gap) — hard fail per §5.1 for the as-served configuration; the compliant view audited **0** by construction.
- (g) Per-class regression: trivially satisfied vs the zero A0 baseline.
- **VERDICT: NOT PROMOTED**

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS (served view): 0. **Named finding, not a silent patch:** the production vector surface predates T-C05; the compliant view's central pre-fusion gate (this run's new production capability) audited ZERO violations across all 120 queries — the gate is the T-C20 closure shape.
- Zero-result queries (served): 0/120.
- Compliant-starved queries: 0 (served non-empty but every eligible-rank hit sits on a non-VALIDATED paper).
- SpecificationPoint resolution: SCORED (spec_resolution_hv) — full-coverage 0.4944 · micro-average 0.8452 over 84 gold points on 89 scored queries (served ALL-denominator view; the HV-mapped notes chunks are SUGGESTED content, so a near-zero number on a compliant view is honest production truth — see the section's dual-view caveat). First §8(d)-scoreable run: this run sets the chunk-arm baseline.
## Reading

- The fabric is production code but NOT a serving default: nothing in production constructs a RetrievalFabric; promotion happens in the owning lane with its own verification discipline after the owner accepts a verdict.
- C vs A/B: fusion rewards agreement; read the dual view against the recorded arms. The compliant view is the configuration a promotion would actually serve; the served view is the production-truth measurement the ratified gate runs on.
- Determinism: no clocks in scoring (latency is an ops field, measured outside rankings); aggregates byte-identical across the double pass.

## T-C83 analysis — the pre-registered predictions, verified (run005j_verify.py, EXIT=0)

The prereg (MIN-COSINE-PREREGISTRATION.md, records 40a6724, committed BEFORE the run) pinned six falsifiable predictions; the verification recomputes every one from the recorded bytes + the SHA-verified frozen preload:

| # | prediction | observed | verdict |
|---|---|---|---|
| (i) | subset invariant: run pool ⊆ f pool per query, 89/89 | 88/89 — ONE violation: g2-024 (4 refs, the NAMED re-execution tie-noise precedent query; the T-C69/T-C72/T-C77 lanes recorded the same class) | HELD (findings rule) |
| (ii) | removed-ref ledger byte-exact: 170 vector refs on 10 scored queries | **BYTE-EXACT per query** — observed removed (f pool − j pool) == the recomputed census removed set on 89/89 queries | HELD |
| (iii) | (d) 44/89 = 0.4944 · 71/84 = 0.8452 (Δ−1/−1 vs f — g2-104's 4CH1-4.46 carrier at cosine 0.5948) | **44/89 = 0.4944 · 71/84 = 0.8452 BYTE-EXACT**; the carrier-loss ledger confirms the single loss is g2-104's carrier | HELD |
| (iv) | pure-filter order: j's order == f's order minus removals | 87/89 — deviations g2-024 + g2-077 (the declared re-execution band; the same two queries the T-C77 verify named) | HELD (findings rule) |
| (v) | six rank slices byte-stable | recall@5 0.0616 / recall@10 0.1043 / recall@20 0.1612 / evidence_precision@10 0.0303 **BYTE-STABLE** (the recall@20 pin's 7th consecutive run); mrr 0.07 (f 0.0626) and nDCG@10 0.1095 (f 0.1057) MOVED — to exactly g's recorded values, inside the recorded f↔g re-execution band | HELD for the set-level slices; the two order-sensitive aggregates moved within the declared band (FINDINGS) |
| (vi) | top-20 changed on exactly 5 queries; 0 gold carriers entering | 7 changed (the 5 predicted + g2-024/g2-077's tie noise); **0 gold carriers entering the served horizon** | HELD (the falsification test held); the count is a FINDING |

The results ledger (`min_cosine_removed`: θ 0.60, 15 affected queries, 295 removed) spans the FULL 120-query gold set — the wrapper retrieves every query, scored or not. The all-queries census recompute reproduces it EXACTLY (15/295); the scored-89 subset is the 10/170 the census prediction pinned (section ii). Both scopes reconcile: the 125-ref gap is the 31 substrate-excluded queries, not a mechanism deviation.

## THE PROBE'S ANSWER — the precision-side exchange rate, measured

1. **The precision hypothesis is FALSIFIED, as the census predicted.** At θ = 0.60 the trim removes 170 scored-query refs carrying real pool mass (and 295 corpus-wide) — and lifts **ZERO** gold carriers into the served horizon. The low-cosine band the trim removes does not displace gold from the top-20; removing it buys no recall@5/@10/@20, no MRR beyond the tie band, no nDCG beyond the tie band, no evidence-precision movement at all. The trim's entire measurable effect on the served horizon is the removal of non-gold tail mass — precision-neutral by every rank-slice the bars read.
2. **The (d) price is real and exactly as priced:** one full-coverage query (g2-104) and one micro point (4CH1-4.46) — the band's ONLY gold-carrying ref sits at cosine 0.5948, INSIDE the trim band, while the census's flip-query carriers sit at 0.5811–0.6336. **Cosine does not separate gold from flood on this corpus** — the T-C72 flip-query fact, now measured corpus-wide at the pool level: the carriers' cosine band and the flood's interior overlap, so any threshold that trims flood trims carriers at the same rate. θ = 0.65 (context, priced in the prereg at (d) 0.3933/0.6905 with recall@20 falling to 0.1084) only deepens the loss — there is no interior θ that wins.
3. **The (d) recovery arithmetic is now complete in both directions.** The recovery campaign closed at run-005-h-r1 with (d) 0.5843/0.9405 (every lever accounted: depth +4 flips, floor +1, kind-arm +4, plus 2 beyond-flip recoveries); this probe measures the reverse edge of the same theorem — removal-only levers pay (d) down at a measured exchange rate (here: −1 full / −1 micro per 170 refs removed) and buy ZERO rank-slice movement. The binding constraint Ruling 8 located (served-surface ALL-view rank-slice quality) is untouched by cosine trimming: the ALL-view bars remain 2–3x away exactly as recorded on f/g/h/i.
4. **(a2) PASS held BY DESIGN** (0.1043 ≥ 0.0734 — the trim is boundary-neutral, (f) 0/0), and (e) improved marginally (p50 302.8 ms vs f's 308.2 — the trim removes work, never adds it). No (g) per-class regression >15% relative vs f.

## Verdict

**NOT PROMOTED** — as pinned. The Ruling-8 conjunction at the UNCHANGED bars: (a) 0.1043 vs 0.1920 FAIL · (b) 0.07 vs 0.1237 FAIL · (c) 0.1095 vs 0.2316 FAIL · (a2) 0.1043 ≥ 0.0734 PASS · (b2) 0.07 vs 0.1184 FAIL · (c2) 0.1095 vs 0.1683 FAIL · (d) 0.4944/0.8452 vs the r8 reference 0.5618/0.9167 ±1pp FAIL (the removal price, as the theorem requires) · (e) PASS-shape · (f) 0/0 PASS · (g) no flags. Five rank conjuncts + the (d) conjunct fail; NOT PROMOTED stands with no waiver and no bar movement. **The MIN_COSINE family's pre-registered question is now MEASURED-COMPLETE: the precision-side license is discharged by measurement — the lever is precision-neutral on the served horizon, (d)-costly by theorem, and closed on this corpus exactly as the reach-side census closed it.** Any further shape (other θ, pre-cut backfill, per-kind trims) = a dated new prereg under the UNCHANGED bars per Ruling 8/9; the binding constraint remains the served-surface rank-slice quality, which no cosine trim moves.

Additive discipline: no recorded verdict re-judged; no threshold moved in either direction; no frozen artifact mutated (fail-closed SHA echo, verified); zero API calls; nothing in production reads BENCH_MIN_COSINE (the production constant stays 0.50).
