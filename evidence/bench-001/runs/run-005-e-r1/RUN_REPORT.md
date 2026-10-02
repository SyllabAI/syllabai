# Run 005-e-r1 — C hybrid, plan-v2 weighted fusion posture (the shipped PLAN_V2_WEIGHTS lever; rank-quality lane tranche 3)

**Status:** RECORDED — deterministic, offline replay, zero API calls; snapshot snap-007 (frozen snapshot); the same frozen basis as r9 and run-005-d-r1 (no re-freeze).
**Arm:** C hybrid, plan-v2 weighted fusion — the PRODUCTION retrieval fabric (com.syllabai.retrieval.RetrievalFabric: explicit arms [pgvector, bm25], central BoundaryPolicy) with the shipped ReciprocalRankFusion k=60 running the shipped PLAN_V2_WEIGHTS per-kind serving posture (plan §7: NOTE 1.0 / SYLLABUS 0.9 / QUESTION_PAPER 0.8 / TEXTBOOK 0.7 / MARK_SCHEME 0.6 / CARD 0.3; sources absent from the map weigh 1.0; within-arm ranks untouched, only cross-source influence scales) over arm A's production vector path and arm B's production lexical path; chunk+query vectors replayed from the frozen artifact embed-backfill-snap-007-preload, zero API calls at run time.
**Executor:** production code over a real Flyway-migrated Postgres, corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served through the production EmbeddingProvider port; no retrieval SQL changed, no fusion code written (the shipped ReciprocalRankFusion runs unchanged; the fusion runs the shipped PLAN_V2_WEIGHTS per-kind posture — the 4-arg fabric ctor, the shipped serving map) — code `3d69a293d6e38517d8be0eaa464706e431f2907f` (branch feat/t-c65-fusion-weights, PR syllabai-core#67, CI build SUCCESS; suite 1212 green offline JDK25; based on core main 422ed7e; the same Run005C orchestrator in its env-gated weighted mode — BENCH_RUN_ID=run-005-e BENCH_FUSION_WEIGHTS=plan_v2 — default path byte-identical by construction).
**Date:** 2026-10-02 | **Gold:** gold-v5 (120 queries; frozen) | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Why this run exists (the pre-registration, committed BEFORE the run)

The rank-quality lane's tranche 3 (T-C65; charter `rank-quality-lane-2026-10-02`, "The two levers" item 2; operator commission trace `1a0fc8c1e8b73939`): the shipped 4-arg `RetrievalFabric` ctor accepts per-kind `sourceWeights` — the plan §7 v2 routing stance the serving fusion already ships (`fuseWithPlanWeights`) — while the bench replay ran the unweighted 3-arg ctor through r9 and run-005-d-r1. `FUSION-WEIGHTS-PREREGISTRATION.md` (records `3880dd5`, committed and pushed BEFORE any weighted run, spec §9 anti-gaming) registered the lever, the mechanism analysis, two hard invariants, and the direction expectations. The weights are the SHIPPED constants — no parameter search, no tuning loop; the run measures the shipped serving posture once, honestly.

## Pre-registered invariants — both HOLD (verified from recorded bytes, `run005e_verify.py`)

1. **Pool set identity: 89/89.** Per query, run-005-e's recorded `ranked_refs` as a SET equals r9's EXACTLY (the full recorded fused pool, 20–40 refs). Weights reorder a fixed union pool — never re-pool it — exactly as pre-registered: the providers are weight-blind, so both arms' per-arm-20 lists are r9's, and the fabric's untruncated fused output is the same deduped candidate set.
2. **§8(d) exact invariance: 0.4607 / 0.7857 — three-way agreement.** r9's recorded aggregate == run-005-e's recorded aggregate == the recompute from the frozen HV projection × gold-v5 × run-005-e's recorded lists (41/89 full-coverage queries, 66/84 gold points). Coverage is a SET property of the pool, and the pool is set-invariant — the second independent lever (after d-r1's reranker) to land on an EXACTLY unchanged (d). The pool-side mechanism finding is now confirmed by two levers: **no post-arm lever (rerank or reweight) can recover the 9 displaced carriers — they are not in the pool.**

## Overall (chunk axis, n=89 labeled queries)

- **C-W2 served (weighted fabric, ALL denominator, 4510 embedded chunks):** recall@5 0.0346 · recall@10 0.0927 · recall@20 0.1612 · mrr 0.0563 · ndcg@10 0.0953 · evidence_precision@10 0.0270 · false_positive_rate@10 0.9730
- **C-W2 compliant (central VALIDATED gate pre-fusion, 702 reachable chunks):** identical to served (production arms gate internally at rev2 — the as-served stream IS the compliant configuration, the r9 finding unchanged).
- **r9 → e1 (the shipped weighted posture, measured):** recall@5 **0.0616 → 0.0346 (−43.8%)** · recall@10 **0.1043 → 0.0927 (−11.1%)** · recall@20 **0.1612 → 0.1612 (±0.0%)** · MRR **0.0700 → 0.0563 (−19.6%)** · nDCG@10 **0.1113 → 0.0953 (−14.4%)**.
- **The pre-registered direction expectation is REFUTED by the data.** The pre-registration expected MRR/nDCG@10/recall@10 to RISE (notes hold weight 1.0 while the displacing QP/MS/EQ mass demotes to 0.8/0.6/0.3). The recorded data says the opposite: every rank-quality axis regressed. The refutation is clean and the mechanism is legible (below) — recorded here as the finding it is.
- **d-r1 context (read-only, no verdict re-judged):** the reranker lever sits at recall@5 0.1279 / recall@10 0.1463 / MRR 0.0936 / nDCG@10 0.1816 on this same basis. The e1 regression is therefore lever-specific, not basis drift: the same frozen inputs that gave d-r1 +63% nDCG give the weighted posture −14%.
- **recall@20: 0.1612 for the THIRD consecutive run** (r9, d-r1, e1) — a 16/16 tier-2-in-first-20 count (set-level), with only 3/89 first-20 SETS changing at all.

## Mechanism — why the weights hurt (the recorded movement ledger)

- Order moved on 88/89 queries (the weighted posture is a real reorder), but the first-20 SET changed on only 3/89 (double-agreement dominates RRF at k=60): entries EXTERNAL_QUESTIONS 7 / QUESTION_PAPER 3 / EXTERNAL_NOTES 2, exits MARK_SCHEME 7 / QUESTION_PAPER 5.
- The damage is INTRA-top-20 ordering, concentrated exactly where the gold is: the bench's tier-2 gold is heavily paper-kind (exam_question's QP/EQ gold made it r9's best class — recall@10 1.00). Demoting QUESTION_PAPER→0.8 / MARK_SCHEME→0.6 / CARD(EXTERNAL_QUESTIONS)→0.3 demotes the gold itself: among the 11 queries whose tier-2 gold is in the pool at all, the first tier-2 hit WORSENED on 6 and improved on 0 (conditional median first-hit depth 2 → 6).
- The pre-registration's declared (g) tradeoff classes were exactly the ones hit — the plan §7 stance ("knowledge-layer evidence leads, question evidence is verbatim context") prices paper-kind evidence at 0.3–0.8, but the bench's paper-anchored classes price their gold AT the paper. Meanwhile the notes carriers the posture is designed to protect are BEYOND the pool (invariant 2), so the posture's benefit side had nothing to lift.

## Per class (C-W2 served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.065 | 0.085 | 0.085 | 0.2125 | 0.2315 | 0.04 | 0.96 |
| conceptual | 0.0 | 0.1179 | 0.1949 | 0.0 | 0.0816 | 0.0308 | 0.9692 |
| exam_question | 0.375 | 0.875 | 1.0 | 0.5607 | 0.5589 | 0.125 | 0.875 |
| factual | 0.0545 | 0.1364 | 0.2273 | 0.0 | 0.1455 | 0.0545 | 0.9455 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 0.0 | 0.0 | 0.12 | 0.0 | 0.0 | 0.0 | 1.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0286 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.0 | 0.0 | 0.0833 | 0.0 | 0.0 | 0.0 | 1.0 |
| vague_learner | 0.0 | 0.0 | 0.25 | 0.0 | 0.0 | 0.0 | 1.0 |
| why_wrong | 0.0333 | 0.0867 | 0.1067 | 0.0646 | 0.1269 | 0.05 | 0.95 |

**(g) tradeoff notes (>15% relative regressions vs r9, per the pre-registration's declared watch):** exam_question recall@5 0.75→0.375 (−50.0%), nDCG@10 0.7104→0.5589 (−21.3%), MRR 0.6607→0.5607 (−15.1%); why_wrong MRR 0.1091→0.0646 (−40.8%), recall@5 0.05→0.0333 (−33.4%), nDCG@10 −17.2%; factual recall@5 −25.0%, recall@10 −21.0%, nDCG@10 −19.1%; calculation recall@5 −23.5%, MRR −15.0%; conceptual recall@5 0.0256→0.0 (one top-5 hit lost). The tradeoff the plan §7 posture makes is explicit and recorded: it trades paper-anchored classes down to buy nothing for the notes-anchored ones on this basis (their carriers are out-of-pool). mark_scheme and multi_spec_point stay at their recorded substrate-absent/sparse floors (exclusion reason unchanged since r8).

## S8 gate arithmetic (§8 v1.1 re-index 2026-10-01, spec §8.1; ruling 1: ALL denominator = served view; VALIDATED bars on the compliant view; v1.0 reference retained)

- (a) ALL bars, served view — Recall@10: **0.0927** vs floor 0.192 -> FAIL
- (b) ALL bars, served view — MRR: **0.0563** vs floor 0.1237 -> FAIL
- (c) ALL bars, served view — nDCG@10: **0.0953** vs floor 0.2316 -> FAIL
- (a2) VALIDATED bars, compliant view — Recall@10: **0.0927** vs floor 0.0734 -> PASS (holds from r9/d-r1)
- (b2) VALIDATED bars, compliant view — MRR: **0.0563** vs floor 0.1184 -> FAIL
- (c2) VALIDATED bars, compliant view — nDCG@10: **0.0953** vs floor 0.1683 -> FAIL — **d-r1's PASS flips back to FAIL under the weighted posture** (each run's own bars evaluated fresh; d-r1's recorded verdict stands).
- (d) SpecificationPoint resolution: **0.4607 / 0.7857 — EXACTLY unchanged from r9 and d-r1** (three-way agreement, recomputed from recorded bytes; 41/89 full, 66/84 points; the projection census pinned 210/209/164/181; `4CH1-PR-08` remains the single unbridged gold point). No new regression and no recovery — as pre-registered: the covered set is a property of the pool, and the pool is set-identical. The raw −10.11pp/−13.10pp movement vs the r8 baseline stands as recorded, pending the spec-owner ruling (compositionality reading); the pool-side mechanism finding is now two-lever-confirmed.
- (e) p95 latency: not evaluable from records (A0 p95 not recorded); this run records retrieval-only p50/p95 (306.9/323.5 ms served; r9: 301.5/315.0, d-r1: 305.2/322.7) — the weighting is O(1) per fused candidate, well inside any §8(e) reading; a deployed hybrid adds the production query-embedding round-trip.
- (f) Validation boundary: served view surfaced **0** non-VALIDATED hits — PASS (hard requirement per §5.1). The compliant view audited **0** by construction. Weights live inside fusion, downstream of the ONE central pre-fusion boundary — nothing enters the pool that the arms did not emit.
- (g) Per-class regression: **five classes regress >15% relative** (exam_question, why_wrong, factual, calculation, conceptual) — tradeoff notes above; the pre-registration declared the paper-anchored classes as the posture's expected cost, and the recorded cost landed there.
- **VERDICT: NOT PROMOTED** (promotion requires BOTH views to pass ALL six checks; (a)(b)(c)(b2)(c2) fail; (g) carries tradeoff notes).

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS (served view): 0. The compliant view's central pre-fusion gate audited ZERO violations across all 120 queries; the weighting seam is boundary-blind by construction (it scales what fusion produced; it cannot re-admit boundary-excluded candidates).
- Zero-result queries (served): 0/120. Compliant-starved queries: 0.
- SpecificationPoint resolution (spec_resolution_hv): full-coverage 0.4607 · micro-average 0.7857 over 84 gold points on 89 scored queries (served ALL-denominator view; compliant view identical, the r9 finding unchanged). Projection census pinned (210 rows / 209 with refs / 164 distinct refs / 181 distinct codes).
- Determinism: PASS — scoring recomputed twice in-process (second full retrieval pass through the weighted fabric), both views' aggregates byte-identical.

## Reading

- **The shipped serving posture, measured on the bench, is a regression.** The plan §7 weights are anti-correlated with the bench's gold composition on this corpus basis: the gold they would protect (notes carriers) is out-of-pool, and the gold they demote (QP/MS/EQ) is the bench's best-performing class evidence. The pre-registered invariants held exactly; the pre-registered directions did not — that is what an honest run is for.
- **The lane's design space narrows with data.** Post-arm levers are exhausted as (d) recovery candidates (two-lever-confirmed pool-side mechanism); the fusion-weights lever is now measured and REFUTED on this basis (as shipped constants — no tuning was done and none is licensed post-hoc; any new weights = dated new pre-registration + new run). The recorded remaining lever family is POOL-side: per-arm depth and pool composition (tranche 4's pre-registration task), where the 9 displaced carriers actually live.
- **Owning-lane decision input (recorded, not decided):** nothing in production constructs a weighted bench fabric; this datapoint says that enabling the serving-side `fuseWithPlanWeights` posture on this corpus shape would regress the §8.1 bars — the posture question stays with the owning lane and the owner's acceptance per harness spec §9.
- The comparison basis is the recorded r9 fabric (snap-007 × gold-r9 × preload-r9, no re-freeze — the same-basis discipline of every tranche); d-r1's and r9's recorded verdicts stand unchanged; each run's own bars are evaluated fresh.
- Instrument notes: first run recorded through Run005C's env-gated weighted mode (default path byte-identical by construction — the same orchestrator, no replay-only branch); BENCH_ARM_D_RERANKER × BENCH_FUSION_WEIGHTS fail-closed mutual exclusion kept the attribution clean (one lever at a time).
