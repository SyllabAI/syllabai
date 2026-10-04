# Run 005 — C hybrid arm, per-kind notes arm posture, rank-bounded horizon (the T-C77 rank-bound lever, RANK-CAP form)

**Status:** RECORDED — production hybrid arm on record (deterministic, offline replay, zero API calls; snapshot snap-007 (frozen snapshot)).
**Arm:** C hybrid — PRODUCTION retrieval fabric (com.syllabai.retrieval.RetrievalFabric: explicit arms [pgvector, bm25, notes-kind-arm], central BoundaryPolicy, shipped ReciprocalRankFusion k=60, rank-only, NoReranker) over arm A's production vector path and arm B's production lexical path with the per-kind EXTERNAL_NOTES arm K=15 as a THIRD fusion input, PRE-boundary (the T-C72 kind-arm lever, KIND-ARM form — pre-registered BEFORE this run) with the kind-arm's exclusive mass rank-bounded below the two-arm surface H=20 (the T-C77 rank-bound lever, RANK-CAP form — the fused pool re-partitioned post-fusion: two-arm contributions STRIPPED of the kind-arm's additive RRF term, kind-arm-only admissions ordered by kind-arm rank, chunk_ref ASC tiebreaks, pre-registered BEFORE this run); chunk+query vectors replayed from the frozen artifact embed-backfill-snap-007-preload, zero API calls at run time
**Executor:** production code over a real Flyway-migrated Postgres (PostgreSQL 17.11 + pgvector 0.8.0, version-exact with the T-C59 pin), corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served through the production EmbeddingProvider port; no PRODUCTION retrieval SQL changed, no fusion code written (the shipped ReciprocalRankFusion runs unchanged); the kind-arm horizon rank-bound (H=20) runs as a pure post-fusion served-order partition (deterministic, zero API calls, no boundary interaction; pre-registered in RANK-BOUNDED-KIND-ADMISSION-PREREGISTRATION.md BEFORE this run) — code `fa2dddbdf57af2c1f2906d3bc3cf0876f7970553` (PR syllabai-core#77, MERGED on the operator's explicit word, trace `1a1047dc0e4fedbd`).
**Date:** 2026-10-04 | **Gold:** gold-v5 (120 queries; frozen) | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Fabric provenance

- Orchestrator: `RetrievalFabric` composes the explicit arms [pgvector, bm25, notes-kind-arm], applies the serving boundary ONCE centrally pre-fusion, and fuses with the shipped `ReciprocalRankFusion` k=60 — no new fusion code, no PRODUCTION retrieval SQL changed. Per-arm candidate bound 40.
- Notes kind arm: per query, the top K=15 EXTERNAL_NOTES chunks by arm A's production candidate SQL (same distance operator, same embedding column, same embed_rev stamp, both T-C07 VALIDATED scope branches) + `AND kind = 'EXTERNAL_NOTES'` + `LIMIT 15` + a deterministic `document_id ASC, chunk_index ASC` final tiebreak; the SAME frozen query vector through the production EmbeddingProvider port. Under-fill 0 queries at the 350-note universe. The kind-arm admits exactly as recorded in run-005-h (its list, its SET contribution, the pool — all unchanged).
- Notes rank cap: H=20 applied POST-fusion to BOTH fabrics (the T-C77 rank-bound lever, RANK-CAP form — the two-arm horizon partition: every pool ref carrying an arm A/B contribution orders by its STRIPPED two-arm RRF score at the view's own filtered kind rank, kind-arm-only admissions serve below the entire two-arm surface ordered by kind-arm rank, chunk_ref ASC tiebreaks; set-preservation fail-closed on every call; dichotomy breach fail-closed; under-fill 0 query-views shorter than H; pre-registered in RANK-BOUNDED-KIND-ADMISSION-PREREGISTRATION.md BEFORE this run).
- Frozen artifact `embed-backfill-snap-007-preload`: model `gemini-embedding-001` @ 768 dims; verified fail-closed against this run's frozen inputs before anything ran; SHA-256 echo in results.json `embedding_artifact.sha256_echo` (chunks `1fd6a617…`, queries `bca55841…` — byte-verified in this workspace before the run as well).

## Overall (chunk axis, n=89 labeled queries)

- **C served (fabric over components as they stand, ALL denominator, 4510 embedded chunks):** recall@5 0.0616 · recall@10 0.1043 · recall@20 0.1612 · mrr 0.07 · ndcg@10 0.1095 · evidence_precision@10 0.0303 · false_positive_rate@10 0.9697
- **C compliant (central VALIDATED gate pre-fusion):** IDENTICAL to served — the prereg's §2 prediction holds (the compliant pool equals the served pool via the recorded subject-level document-validation branch; the partition applies identically to both fabrics).

## §8(d) — the ruled metric (§10 Ruling 7, gate reading = per-query full coverage)

- **(d) full 52/89 = 0.5843 · micro 79/84 = 0.9405 — BYTE-EXACT vs run-005-h.** The theorem-shaped prediction CONFIRMED on the production path: a pure served-order permutation of the h pool leaves (d) unchanged (reorder-only; held on all seven recorded runs). The recorded chain: r8 0.5618/0.9167 → r9 0.4607/0.7857 → f 0.5056/0.8571 → g 0.5169/0.8690 → h 0.5843/0.9405 → **i 0.5843/0.9405**. r8 remains a DIFFERENT-basis recorded reference (snap-006 + chunk vectors `1e22a202…`), not a target under the current basis.
- **SET-preservation (the primary endpoint): 89/89** — i's served pool SET == h's pool SET per query; superset vs f 89/89 (the standing findings rule).
- **The H=20 horizon assertion: 0 kind-arm-only refs at fused ranks 1..20 on all 89 queries**; the partition order (every two-arm ref precedes every kind-arm-only ref) clean on 89/89; **the demotion ledger: 797 kind-arm-only refs below the two-arm surface — the census prediction byte-exact** (min 0 / max 15 per query; 83 queries carry >0, the census's 83/89 shape).
- Non-regression total: f-full losses 0 (the lever removes nothing); all 5 f-lost flips (g2-011/016/056/059/112) stay ADMITTED+REVERTED; the h beyond-flip recoveries g2-061 and g2-109 hold their 2 covered points.

## Rank-slice ledger (the prereg's byte-stability predictions — all HELD)

- recall@5 **0.0616** · recall@10 **0.1043** · recall@20 **0.1612** · evidence_precision@10 **0.0303** — BYTE-EXACT vs the recorded pre-kind-arm values (the pins held through every recorded execution and now through the production partition path). **The recall@20 0.1612 pin holds a 6th run.**
- mrr **0.07** and nDCG@10 **0.1095** — inside the recorded f↔g re-execution band [0.0626, 0.07] / [0.1057, 0.1095], at the band's top edge (the simulation's central values, reproduced).
- Per-query movement vs f: recall@5/@10/@20 moved on 0 queries; mrr moved on 1; ndcg@10 moved on 1 — the served horizon IS the pre-kind-arm recorded shape, as pinned.
- **Top-20 identity vs f's recorded lists: set-identity 87/89, order-identity 86/89 — exactly the simulation's predicted shape**, with the grounding's three named queries (g2-024, g2-086 set diffs; g2-077 order-only) — the declared re-execution band; confirmation, not a finding.

## §8.1 v1.1 gate arithmetic (evaluated fresh, both views; ruling 1: ALL bars on the served view; UNCHANGED bars per Ruling 8)

- (a) ALL bars, served view — Recall@10: **0.1043** vs floor 0.1920 -> FAIL
- (b) ALL bars, served view — MRR: **0.07** vs floor 0.1237 -> FAIL
- (c) ALL bars, served view — nDCG@10: **0.1095** vs floor 0.2316 -> FAIL
- (a2) VALIDATED bars, compliant view — Recall@10: **0.1043** vs floor 0.0734 -> **PASS RESTORED** (h failed it at 0.0612; the partition removes the dilution the kind-arm's in-horizon admissions caused)
- (b2) VALIDATED bars, compliant view — MRR: **0.07** vs floor 0.1184 -> FAIL
- (c2) VALIDATED bars, compliant view — nDCG@10: **0.1095** vs floor 0.1683 -> FAIL
- Boundary: served violations **0**; compliant-starved 0; zero-result queries 0.
- **VERDICT: NOT PROMOTED** — the pinned expected outcome (the ALL-view bars sit 2–3x away and are the located binding constraint, Ruling 8 §3.4; this tranche does not address them).

## The SEPARABILITY answer (the tranche's pre-registered question)

- **YES — measured, not assumed.** run-005-i is the FIRST recorded posture where (d) beyond the r8 reference (0.5843/0.9405) AND (a2) PASS coexist: the (d) maximum of the kind-arm posture is kept IN FULL (the SET is h's SET, byte-identical coverage) while the served horizon reverts to the pre-kind-arm rank shape (the byte-stability pins) and the compliant view's gate restores. The recorded tension h left open — (d) above r8 while every §8.1 gate FAILs — is resolved by the partition: the SET gain and the ORDER cost were severable, and the seam severs them on the production path.
- The declared give-back, recorded honestly: the fresh notes' gold coverage stays covered (SET-invariant) but serves below the horizon. exam_question mrr moved f 0.494 → i 0.6607 (+33.7%, the one >15% per-class flag): the single mrr-moving query is **g2-077** — the same order-only top-20 diff §Rank-slice names — whose first tier-2 ref serves at rank 1 under the deterministic stripped-order surface vs f's rank 3 (per-query mrr 0.3333 → 1.0; class avg +0.1667 at n=4). A movement of the re-execution band shape, recorded under (g), not smoothed.
- (e) latency: retrieval-only p50 343.8 ms / p95 361.2 ms (served; compliant 305.8/322.0) — h's shape (p50 346.5 ms) with the partition's O(n) pass invisible; the NotesArmRetrieval memo keeps the post-hoc read O(1) with zero extra SQL. Below g's 1080.0 ms.

## Reading

- The fabric is production code but NOT a serving default: nothing in production constructs a RetrievalFabric; promotion happens in the owning lane with its own verification discipline after the owner accepts a verdict.
- The rank-bound is bench-scoped: nothing in production reads `BENCH_NOTES_RANK_CAP` (the five bench gates verified bench-scoped; serving's own candidate selection and fusion untouched).
- Determinism: no clocks in scoring (latency is an ops field, measured outside rankings); aggregates byte-identical across the double pass; the partition transform is a pure function of the three arm lists.
- Verdict honesty: NOT PROMOTED was pinned BEFORE the run (prereg §3.6); the tranche's deliverable is the separability answer above. Any promotion-shaped next step = new operator word + dated new prereg under the UNCHANGED bars (Ruling 8), with the binding constraint located at the served-surface ALL-view rank-slice quality.
