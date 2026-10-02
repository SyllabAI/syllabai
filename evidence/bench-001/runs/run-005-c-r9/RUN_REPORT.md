# Run 005-c-r9 — C hybrid re-record (§8.1 v1.1 dual-view bars; the wave-2 generation, snap-007)

**Status:** RECORDED — production hybrid arm on record (deterministic, offline replay, zero API calls; snapshot snap-007 (frozen snapshot)).
**Arm:** C hybrid — PRODUCTION retrieval fabric (com.syllabai.retrieval.RetrievalFabric: explicit arms [pgvector, bm25], central BoundaryPolicy, shipped ReciprocalRankFusion k=60, rank-only, NoReranker) over arm A's production vector path and arm B's production lexical path; chunk+query vectors replayed from the frozen artifact embed-backfill-snap-007-preload, zero API calls at run time
**Executor:** production code over a real Flyway-migrated Postgres, corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served through the production EmbeddingProvider port; no retrieval SQL changed, no fusion code written (the shipped ReciprocalRankFusion runs unchanged) — code `c4b67e8` (core main; includes the T-C46 paired embed_rev re-stamp re-land, so this is the FIRST Run005C replay executed from main — no replay-only branch, by construction).
**Date:** 2026-10-02 | **Gold:** gold-v5 (120 queries; frozen; re-paired to snap-007, gold_check PASS) | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Why this run exists (the commission)

The wave alternation (WAVES.md): validate → re-freeze/re-record → read the bars → validate the next wave. Wave-1 (teacher surface, 2026-10-02) + wave-2 (governed SQL batch `14cb8ae4…`, 297 documents SUGGESTED→VALIDATED, 2026-10-02T08:31:44Z, T-C54) landed; the F-PROD-4 4CH1/2C REJECTED ingest shell was removed (07:34:18Z); the 09-28 20:18–20:24Z chemistry re-ingest generations joined the corpus. Operator directive (trace `1a0fbeaf2695af79`): **"Run005C re-record against the §8.1 VALIDATED bars"**. The snap-007 freeze (T-C57 lane, exporter adapted from the snap-006 exporter with all producer queries verbatim) captures that production truth: **4,510 chunks = 4,181 carried byte-identical + 329 re-ingest (145 MS + 184 QP across 20 documents, all created_at in the re-ingest window)**; **3,162 chunk up-flips to VALIDATED**; 30 MS + 34 QP chunks REJECTED with teacher audit rows re-verified; zero content/kind/spec-code drift on the carried set; HV projection drift gate 0 divergences (census 210/209/164/181, kinds 205/4/0/1 pinned); spec_points BYTE-IDENTICAL (194 — the gold pairing anchor). Curriculum-axis growth since snap-006 (the KG/teaching-coverage lanes' work) is recorded as manifest-bound deltas in the freeze manifest, never silently patched: graph_edges 152→270 (+130/−12, the 12 gone rows are the practicals' REQUIRES_PREREQUISITE→PART_OF re-model with successor edges recorded), misconceptions 19→30, question_anchors 731→988 (+448 added / 75 field-mutated / 115 unmatched rows consistent with the coverage lanes' delete-and-re-extract question lineage — full list in the freeze manifest), PART_OF serving pairs 117→211 with the ratified 117-row c19 record byte-identical.

## Fabric provenance

- Orchestrator: `RetrievalFabric` composes the explicit arms [pgvector, bm25] (never injection-implied, E-1 forward note), applies the serving boundary ONCE centrally pre-fusion, and fuses with the shipped `ReciprocalRankFusion` k=60 — no new fusion code, no retrieval SQL changed. Per-arm candidate bound 20. MIN_COSINE = 0.50 (the T-C42 calibrated floor, merged via PR #44) — unchanged since r8.
- Frozen artifact `embed-backfill-snap-007-preload`: model `gemini-embedding-001` @ 768 dims; 4,510 rows = 4,181 carried BYTE-IDENTICAL from the r7-lineage artifact (`embed-backfill-snap-006-preload-copy`) + 329 rows exported SELECT-only from production (the re-ingest chunks' embeddings were computed once in production; exporting is not re-computation — zero embedding API calls in this generation). **Bit-identity proof: every one of the 4,181 shared refs proven float32-bit-identical between live production and the frozen artifact** before the copy (the r7 doctrine, upgraded from sample to full coverage). 120 query vectors byte-copied (gold texts unchanged). Verified fail-closed against this run's frozen inputs before anything ran; SHA-256 echo in results.json `embedding_artifact.sha256_echo`.

## Overall (chunk axis, n=89 labeled queries)

- **C served (fabric over components as they stand, ALL denominator, 4510 embedded chunks):** recall@5 0.0616 · recall@10 0.1043 · recall@20 0.1612 · mrr 0.07 · ndcg@10 0.1113 · evidence_precision@10 0.0303 · false_positive_rate@10 0.9697
- **C compliant (central VALIDATED gate pre-fusion, 702 reachable chunks — the T-C05-closed configuration):** recall@5 0.0616 · recall@10 0.1043 · recall@20 0.1612 · mrr 0.07 · ndcg@10 0.1113 · evidence_precision@10 0.0303 · false_positive_rate@10 0.9697
- **A0 (run-002, zero-vector baseline):** evidence_precision@10 0.0 · false_positive_rate@10 0.0 · mrr 0.0 · ndcg@10 0.0 · recall@10 0.0 · recall@20 0.0 · recall@5 0.0
- **B (run-003, production lexical, VALIDATED-served):** evidence_precision@10 0.0045 · false_positive_rate@10 0.0112 · mrr 0.0449 · ndcg@10 0.0449 · recall@10 0.0247 · recall@20 0.0247 · recall@5 0.0247
- **A served (run-004, production vector, ALL denominator):** evidence_precision@10 0.0146 · false_positive_rate@10 0.9854 · mrr 0.0313 · ndcg@10 0.0684 · recall@10 0.0515 · recall@20 0.0717 · recall@5 0.0273
- **r8 (run-005-c-r8, snap-006, the immediate predecessor):** recall@5 0.0386 · recall@10 0.0515 · recall@20 0.0717 · mrr 0.0559 · ndcg@10 0.0871 · evidence_precision@10 0.0146
- **r8 → r9 (the wave unlock, measured):** recall@5 **+59.6%** · recall@10 **+102.5%** · recall@20 **+124.8%** · mrr **+25.2%** · ndcg@10 **+27.8%**. The dual view's metrics are identical because production's retrieval components gate serving-eligibility internally (the searchServingEligible replica at CURRENT_EMBED_REV=2 inside the arms) — the as-served stream IS the compliant configuration now; the dual-view arithmetic evaluates it twice, recorded as observed, never patched.

## Per class (C served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.085 | 0.085 | 0.085 | 0.25 | 0.25 | 0.0425 | 0.9575 |
| conceptual | 0.0256 | 0.1282 | 0.1949 | 0.0 | 0.0985 | 0.0197 | 0.9803 |
| exam_question | 0.75 | 1.0 | 1.0 | 0.6607 | 0.7929 | 0.1 | 0.9 |
| factual | 0.0727 | 0.1727 | 0.2273 | 0.0 | 0.0818 | 0.0205 | 0.9795 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 0.0 | 0.0 | 0.12 | 0.0 | 0.0 | 0.0 | 1.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0286 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.0 | 0.0 | 0.0833 | 0.0 | 0.0 | 0.0 | 1.0 |
| vague_learner | 0.0 | 0.0 | 0.25 | 0.0 | 0.0417 | 0.025 | 0.975 |
| why_wrong | 0.05 | 0.0867 | 0.1067 | 0.1091 | 0.2202 | 0.0533 | 0.9467 |

The wave unlock's showcase: exam_question recall@10 **0.50 → 1.00** (all 8 exam_question queries now retrieve their gold evidence inside the top-10 — the four wave papers' QP/MS surfaces were the binding constraint), factual recall@10 0.0364 → 0.1727, conceptual recall@10 0.0385 → 0.1282, calculation MRR 0.10 → 0.25, misconception recall@20 0.02 → 0.12. mark_scheme stays 0.0 (its gold queries' tier labels are substrate-absent/sparse — the recorded exclusion reason, unchanged from r8).

## Per class (C compliant view — T-C05-closed configuration)

Identical to the served view (same stream, see the dual-view note above).

## S8 gate arithmetic (§8 v1.1 re-index 2026-10-01, spec §8.1; ruling 1: ALL denominator = served view; VALIDATED bars on the compliant view; v1.0 reference retained)

- (a) ALL bars, served view — Recall@10: **0.1043** vs floor 0.192 -> FAIL
- (b) ALL bars, served view — MRR: **0.07** vs floor 0.1237 -> FAIL
- (c) ALL bars, served view — nDCG@10: **0.1113** vs floor 0.2316 -> FAIL
- (a2) VALIDATED bars, compliant view — Recall@10: **0.1043** vs floor 0.0734 -> PASS — **the first PASS of a §8.1 bar in the series' history** (r7: 0.0515, r8: 0.0515)
- (b2) VALIDATED bars, compliant view — MRR: **0.07** vs floor 0.1184 -> FAIL
- (c2) VALIDATED bars, compliant view — nDCG@10: **0.1113** vs floor 0.1683 -> FAIL
- (d) SpecificationPoint resolution: **SCORED, measured against the r8 baseline** (r8 set the chunk-arm baseline; this is the first run where the 1pp rule applies): full-coverage **0.5618 → 0.4607 (−10.11pp)** · micro-average **0.9167 → 0.7857 (−13.10pp)** — beyond the 1pp allowance as a raw delta. Read with the two pre-registered facts: (1) the r7 interpretation (records 09a624728) — a (d) movement beside weak (a)/(b)/(c) is a **coverage/competition signal, not a retrieval-quality signal**: the newly-validated QP/MS/EQ mass now outranks the 210 HV-mapped notes chunks on most queries, so per-query full coverage drops while the corpus wall falls; (2) the projection itself is UNCHANGED (the snap-007 HV drift gate re-verified all 210 mappings over the frozen bytes with 0 divergences; census 210/209/164/181 pinned). No promotion claim is made on (d); the owning lane owns the interpretation.
- (e) p95 latency: not evaluable from records (A0 p95 not recorded); this run records retrieval-only p50/p95 (301.5/315.0 ms served; r8: 309.7/322.7 ms); a deployed hybrid adds the production query-embedding round-trip.
- (f) Validation boundary: served view surfaced **0** non-VALIDATED hits — PASS (hard requirement per §5.1). The compliant view audited **0** by construction.
- (g) Per-class regression: satisfied vs the zero A0 baseline; honest tradeoff notes recorded — vague_learner recall@10 0.125 → 0.000 (the newly-served pool outranks its single r8 hit; recall@20 0.125 → 0.250 improved) and why_wrong recall@10 0.0983 → 0.0867 (−11.8%, inside the 15% allowance) — both pool-composition effects of the unlock, recorded per §8(g)'s note discipline.
- **VERDICT: NOT PROMOTED** (promotion requires BOTH views to pass ALL six checks; (a)(b)(c) fail on the ALL view and (b2)(c2) fail on the VALIDATED view).

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS (served view): 0. The T-C20 vector-surface gap remains closed in production; the compliant view's central pre-fusion gate audited ZERO violations across all 120 queries.
- Zero-result queries (served): 0/120.
- Compliant-starved queries: 0 (served non-empty but every eligible-rank hit sits on a non-VALIDATED paper).
- SpecificationPoint resolution (spec_resolution_hv): full-coverage 0.4607 · micro-average 0.7857 over 84 gold points on 89 scored queries (served ALL-denominator view; compliant view reported alongside in results.json). Projection census pinned (210 rows / 209 with refs / 164 distinct refs / 181 distinct codes); `4CH1-PR-08` remains the single unbridged gold point.

## Reading

- **The validation waves moved the needle — the corpus wall is softening, not broken.** The dual-view numbers doubled on recall@10 (0.0515 → 0.1043) exactly as the wave theory predicted: the binding constraint was validation throughput, and the 3,162-chunk unlock bought +102.5% recall@10, +124.8% recall@20, +25.2% MRR. The first §8.1 bar ever passed is the VALIDATED recall bar — the validation axis is now inside its own bar.
- **What still separates the run from PROMOTED:** the ALL-view floors (0.1920 / 0.1237 / 0.2316) need another +84% recall@10, +77% MRR, +108% nDCG@10 from here, and the VALIDATED MRR/nDCG floors need +69% / +52%. The remaining gap is rank QUALITY (the correct chunk is in the pool but not at the rank the bars price — MRR 0.07 with recall@20 0.1612 says the evidence is found at depth ~14 on the median hit), not pool coverage. The next levers are rank-side (arm D's reranker port; the fusion weights lane), not more validation volume alone.
- **(d) needs the owning lane's eye**, not a waiver: the raw −10.11pp / −13.10pp movement against the r8 baseline is exactly the pre-registered coverage/competition shape (the HV-mapped notes chunks are now ranked below the newly-served paper mass on most queries). If a promotion verdict ever hinges on (d), the ruling question is whether §8(d) means mapping fidelity (unchanged by construction here) or top-rank resolution compositionality (moved) — that is a spec-owner decision, recorded here as data, not resolved by this lane.
- The fabric is production code but NOT a serving default: nothing in production constructs a RetrievalFabric; promotion happens in the owning lane with its own verification discipline after the owner accepts a verdict.
- Determinism: no clocks in scoring (latency is an ops field, measured outside rankings); aggregates byte-identical across the double pass; the run executed in the records lane's sandbox on the user-space Postgres 17.11 + pgvector 0.8.0 disposable cluster (Debian-native debs, relocatable layout), Flyway V1→V59, the T-C46 paired rev stamp 4,510 → rev 2.
