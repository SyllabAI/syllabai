# Run 005-f — pool-side (d) recovery, per-arm depth 20 → 40 (rank-quality lane tranche 4, T-C67)

**Status:** RECORDED — one measured datapoint for the pool-DEPTH lever on the r9 frozen basis; verdict NOT PROMOTED, the §8(d) recovery number is the tranche's headline and is recorded independently of promotion (pre-registration: `evidence/bench-001/rank-quality-lane-2026-10-02/POOL-RECOVERY-PREREGISTRATION.md`, records `d34e038`, committed BEFORE the run; verify script `run005f_verify.py` ships in this pack, zero failures, three findings).
**Lever (single):** per-arm candidate bound `StructuredRetrievalQuery.limit` 20 → 40 via the pre-existing `BENCH_PER_ARM_LIMIT` gate — ZERO syllabai-core diff; `BENCH_ARM_D_RERANKER` and `BENCH_FUSION_WEIGHTS` ABSENT (one lever at a time; the d-r1/e-r1 levers are not stacked here).
**Arm:** C hybrid — the production `RetrievalFabric` (explicit arms [pgvector, bm25], central BoundaryPolicy pre-fusion, shipped `ReciprocalRankFusion` k=60, rank-only, NoReranker) unchanged from r9; only each arm's SQL LIMIT doubled. Per-query served pool: **40–79 refs (r9: 20–40)** — the union grew on every one of the 120 queries.
**Executor:** production code over a real Flyway-migrated Postgres, corpus from the frozen snapshot, chunk vectors from the checksummed compute-once-freeze-forever artifact, query vectors through the production port, zero API calls at run time — code `e657b9a4a784d4ed394370051526b550e38cd306` (core main, the T-C65 merge; the bench ran on the recorded main, no local diff).
**Date:** 2026-10-02 | **Basis:** snap-007 × gold-r9 × preload-r9, NO re-freeze | **Gold:** gold-v5 (120 queries; 89 scored; 84 gold points; frozen) | **Determinism:** double retrieval pass, byte-identical aggregates both views — PASS.

## Headline: the §8(d) recovery (the tranche's purpose)

- **(d) full-coverage 0.4607 → 0.5056 (+4.49pp) · micro-average 0.7857 → 0.8571 (+7.14pp)** — 45/89 queries at full coverage, 72/84 gold points covered.
- The recompute from the frozen HV projection × gold-v5 × f's recorded ranked_refs equals the recorded aggregate EXACTLY (0.5056/0.8571); the same recompute reproduces r9's (0.4607/0.7857) and r8's (0.5618/0.9167) recorded aggregates byte-exactly — machinery self-check OK.
- **The pre-registered conditional theorem CONFIRMED** on the invariant-held subset (88 queries; see finding 1): (d) is a SET property of the served pool, and per-arm deepening is the first lever in the series that changes the set — both post-arm levers (rerank d-r1, reweight e-r1) left (d) EXACTLY unchanged because they reorder a fixed set.
- **PARTIAL recovery:** f stays below the r8 ruling baseline 0.5618/0.9167 (the ceiling preregistered in §3.1). Depth 40 recovered 4 of the 9 lost flips plus the partial loss — not all of them.
- The recovery reached (d) WITHOUT touching the served top-20: every recall axis is byte-identical to r9 (see below). The re-admitted carriers live at fused ranks 21–40.

## Per-flip recovery ledger (derived MECHANICALLY from recorded bytes — no hand-maintained list)

The 9 r9-lost flips (r8 full → r9 not-full), derived by comparing r8 vs r9 recorded per-query full-coverage booleans: `g2-011, g2-016, g2-042, g2-048, g2-050, g2-053, g2-056, g2-059, g2-112`.

| query | outcome at depth 40 | covered points (r8 → r9 → f) |
|---|---|---|
| g2-042 | **REVERTED** (full 0→1) | 1/2 → 1/2 → 2/2 |
| g2-048 | **REVERTED** (full 0→1) | 1/3 → 1/3 → 3/3 |
| g2-050 | **REVERTED** (full 0→1) | 0/1 → 0/1 → 1/1 |
| g2-053 | **REVERTED** (full 0→1) | 1/2 → 1/2 → 2/2 |
| g2-011 | MISS | 0/1 → 0/1 → 0/1 |
| g2-016 | MISS | 0/1 → 0/1 → 0/1 |
| g2-056 | MISS | 1/2 → 1/2 → 1/2 |
| g2-059 | MISS | 1/2 → 1/2 → 1/2 |
| g2-112 | MISS | 1/2 → 1/2 → 1/2 |

- All 4 reverted flips' re-entered carriers are **EXTERNAL_NOTES** chunks — the spec-mapped notes carriers the wave displaced, re-admitted from per-arm ranks 21–40 into the union pool.
- **5 of 9 flips STILL MISSED at depth 40** — the carriers are not in either arm's top-40 at all. This is the preregistered signal (§3.3): for these queries a pool-COMPOSITION lever (per-kind quotas, boundary-adjacent reordering of the arm inputs), not more depth, is what remains. Deeper cuts (60/80) were pre-rejected in the prereg §1 as compounding dilution without recorded evidence of need; that rejection stands — the miss is recorded, not chased.
- **Partial-loss cross-check:** g2-061 (named in the prereg §3.3) went r8 1 → r9 0 → **f 1 — RECOVERED** by depth.

## Pre-registered invariants — PASS/FAIL recorded honestly (run005f_verify.py)

1. **Superset invariant: 88/89 — FINDING (declared risk fired once).** g2-024's f-pool is missing 4 refs that r9's pool held (`…f81e62:9`, `…4cb3dc:15`, `…1a943:5`, `…733:5` — full SHA256s in the verify output). This is the preregistered per-arm prefix instability under LIMIT growth (HNSW approximation participates in the scan; ORDER BY ties have no deterministic order). **(d)-harmless in fact:** the 4 dropped refs cover no gold points — g2-024's coverage is 1/1 full in BOTH runs — so the (d) monotonicity claim is made over the 88-query held subset, and the one violated query is (d)-unchanged.
2. **(d) recompute + monotonicity: PASS.** Recomputed == recorded (0.5056/0.8571); monotone non-decreasing vs r9 on the held subset; per-query covered-point monotonicity on the held subset: 0 drops.
3. **(a)–(c) no-direction zone: recall axes BYTE-IDENTICAL (recall@5 0.0616, recall@10 0.1043, recall@20 0.1612 — the recall@20 pin HELDS for the 4th consecutive run at exactly 0.1612), evidence_precision@10 0.0303 and fp@10 0.9697 unchanged. MRR 0.0700 → 0.0626 (−10.6%) and nDCG@10 0.1113 → 0.1057 (−5.0%)** — the declared dilution cost materialized on the rank-quality axes only, and modestly: the added deep candidates changed within-top-10 ordering slightly without changing any served-set recall.
4. **(f) boundary 0/0: PASS** (served violations 0; the central pre-fusion gate audited clean at depth 40 exactly as at depth 20).
5. **(e) latency:** retrieval-only p50 308.0 ms / p95 322.0 ms (r9: 301.5/313.6) — depth 40 cost ≈ +2–3% scan work; frozen replay, zero API calls.
6. **Determinism: PASS** (double retrieval pass, byte-identical aggregates both views).

## §8.1 v1.1 gate arithmetic (fresh evaluation; no recorded verdict re-judged)

- (a) ALL served Recall@10: **0.1043** vs floor 0.1920 -> FAIL
- (b) ALL served MRR: **0.0626** vs floor 0.1237 -> FAIL
- (c) ALL served nDCG@10: **0.1057** vs floor 0.2316 -> FAIL
- (a2) VALIDATED compliant Recall@10: **0.1043** vs floor 0.0734 -> PASS (held)
- (b2) VALIDATED compliant MRR: **0.0626** vs floor 0.1184 -> FAIL
- (c2) VALIDATED compliant nDCG@10: **0.1057** vs floor 0.1683 -> FAIL
- (d) SCORED — full 0.5056 / micro 0.8571 (the recovery headline above)
- **VERDICT: NOT PROMOTED** (per §8.1 v1.1 — a finding, not an argument; promotion stays with the owning lane + owner acceptance per harness spec §9)

## (g) per-class tradeoff notes (vs r9; >15% relative flagged both directions)

- **exam_question MRR 0.6607 → 0.494 (−25.2%), nDCG@10 0.7104 → 0.627 (−11.7%) — written tradeoff note:** the prereg's dilution watch named this class before the run ("its QP/EQ gold now shares the pool with more of the same mass"). The RRF arithmetic admits same-kind paper mass from the deepened arm lists into the served top-10, pushing exam_question's first gold hit deeper. Recall is UNCHANGED (0.75/1.0/1.0 — the gold is still served); this is a rank-quality cost on the paper-anchored class, accepted as the price of the notes-carrier recovery that (d) records. No notes-anchored class regressed on any axis.
- factual nDCG@10 0.1798 → 0.1652 (−8.1%): under the flag, recorded for completeness.
- All other classes: byte-identical to r9 on every axis.

## What depth 40 added (composition of the growth)

- Added refs beyond r9's pools, summed over the 89 scored queries: **MARK_SCHEME 683 · QUESTION_PAPER 592 · EXTERNAL_QUESTIONS 340 · EXTERNAL_NOTES 182** (≈20.2 new refs/query).
- By fused rank band: **1759 at ranks 21–40, only 38 at ranks 41–80** — RRF concentrates the deepened arms' new mass in the union's 21–40 band; the pool grew, the top-20 barely moved (which is why the recall axes held and the (d) recovery was pool-deep).

## Manifest posture note

f's fabric block records `fusion_weights: "unweighted (null map — the recorded r9/d-r1 posture; the 3-arg ctor)"`; r9's manifest predates the T-C65 schema field and carries no such key. Postures are identical (both runs: 3-arg ctor, unweighted RRF k=60, NoReranker); the difference is manifest schema vintage, not lever state — recorded so the textual delta is not mistaken for a posture delta.

## Reading / next_safe_action

- The (d) mechanism ledger is now THREE-lever complete: rerank (reorder, (d) frozen), reweight (reorder, (d) frozen), **depth (set growth, (d) recovers)** — confirming the prereg's set-property analysis end-to-end. Depth recovered 4/9 flips + the partial loss at ≈+2–3% latency and zero recall cost; the remaining 5 misses are out-of-pool at either arm's top-40 and are a COMPOSITION problem, not a depth problem.
- **Next lever family (each its own dated pre-registration + run, one lever at a time): pool composition** — per-kind quotas inside an arm's list are the first candidate (the 5 misses' carriers are notes-kind chunks being outranked within their arm by paper mass), then MIN_COSINE floor moves, re-ingest dedup, arm-composition changes.
- No production serving change: nothing in production reads `BENCH_PER_ARM_LIMIT`; serving's own candidate bound is untouched; arm promotion happens in the owning lane after the owner accepts a §8-passing verdict (harness spec §9). No frozen artifact was mutated. No recorded verdict was re-judged; new depths or composition parameters mean dated new pre-registrations and new runs.
