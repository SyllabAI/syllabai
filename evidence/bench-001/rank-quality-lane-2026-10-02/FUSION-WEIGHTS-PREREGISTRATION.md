# Fusion-weights replay — pre-registration (charter tranche 3, T-C65)

**Status:** PRE-REGISTERED — committed to the records repo BEFORE any weighted run executes
(spec §9: no retrieval change ships without the eval harness; r3 anti-gaming doctrine: no
tuning against the frozen set; new parameters mean new runs).
**Lane:** rank-quality-lane-2026-10-02 (T-C63 charter, "The two levers", item 2; the T-C63
yaml's tranche-3 next_safe_action). Arm D's verdict is recorded (run-005-d-r1, NOT PROMOTED,
core 60bdd64) — the charter's precondition for opening this tranche is met.
**Authority:** operator IM trace `1a0fc8c1e8b73939` ("commission the rank-quality lane"),
tranche 3 of the commissioned lane.

## 1. The lever, exactly (shipped code, zero new fusion code)

The replay runs the bench through the **shipped 4-arg `RetrievalFabric` constructor** with
the **shipped `ReciprocalRankFusion.PLAN_V2_WEIGHTS` map** (plan §7 v2 routing stance,
canonical home `ReciprocalRankFusion.PLAN_V2_WEIGHTS`, aliased as
`RetrievalFabric.PLAN_V2_WEIGHTS`; the serving fusion consumes the same map via
`fuseWithPlanWeights` — one source of truth):

| EvidenceSource | weight | corpus document_kind (fabric `chunkSource`) |
|---|---|---|
| NOTE | 1.0 | EXTERNAL_NOTES |
| SYLLABUS | 0.9 | SYLLABUS |
| QUESTION_PAPER | 0.8 | QUESTION_PAPER |
| TEXTBOOK | 0.7 | TEXTBOOK |
| MARK_SCHEME | 0.6 | MARK_SCHEME |
| CARD | 0.3 | EXTERNAL_QUESTIONS |
| (absent: KNOWLEDGE_NODE, LEARNER_WORK, OTHER) | 1.0 | — |

Weighted contribution = `weight(source) / (k + rank + 1)`, k=60 unchanged; within-arm rank
order untouched; only cross-source influence scales. These constants are SHIPPED — this run
measures the shipped serving posture on the bench; **no parameter search, no tuning loop,
no post-hoc weight change** (any future weight change = dated new pre-registration + new run,
plan §9).

Bench seam (the only code change): `BENCH_FUSION_WEIGHTS=plan_v2` env-gates the 4-arg ctor in
`Run005C` (both views' fabrics identically); the default (absent) path stays the 3-arg ctor —
byte-identical by construction (the S8D absent-path precedent, r9 basis). Unknown spec values
fail closed. `BENCH_FUSION_WEIGHTS` and `BENCH_ARM_D_RERANKER` are **mutually exclusive
(fail-closed)**: one lever at a time — attribution honesty (this run measures weights ALONE
against the unweighted r9 basis, not the arm-D stack).

## 2. Mechanism — what weights can and cannot do (stated BEFORE the run)

- **Weights cannot change pool membership.** Providers are weight-blind: both arms'
  per-arm-20 candidate lists are exactly r9's (same frozen vectors, same cosine floor
  MIN_COSINE=0.50, same lexical index, same per-arm bound). Weights apply only inside fusion,
  over the union pool. Therefore the fused output — which is the ENTIRE deduped union pool
  (the fabric does not truncate; recorded `ranked_refs` are 20–40 refs) — is a REORDERING of
  r9's pool, never a re-pooling.
- **Weights therefore cannot recover the 9 displaced §8(d) carriers** (run-005-d-r1's
  mechanism finding: they sit beyond both arms' top-20s, absent from the pool entirely).
  The (d) scorer (`ChunkSpecHvResolution.scoreQuery`) covers the FULL served ref list, and
  coverage is a SET property of that list — order-free. Hence:

> **Pre-registered invariant 1 (pool set identity):** per query, the weighted run's
> `ranked_refs` as a SET equals run-005-c-r9's `ranked_refs` as a SET — expected 89/89
> labeled queries (verified from recorded bytes post-run). Any mismatch = harness defect:
> abort, investigate, NO verdict recorded from a defective run.

> **Pre-registered invariant 2 (§8(d) exact invariance):** (d) full-coverage 0.4607 /
> micro 0.7857 on both views, EXACTLY as r9 and d-r1 recorded. This follows from
> invariant 1 plus the scorer's set semantics. A second, independent lever (after the
> reranker) landing on the same unchanged (d) CONFIRMS the pool-side mechanism finding;
> any movement would REFUTE it and stall the run for investigation.

## 3. Pre-registered expectations (directions; magnitudes unknowable without forbidden tuning)

1. **Chunk axis, served view (vs r9's 0.0616/0.1043/0.1612, MRR 0.0700, nDCG@10 0.1113):**
   MRR, nDCG@10 and recall@10 are expected to RISE — the gold-bearing notes carriers
   (NOTE 1.0) hold their full influence while the wave's QP/MS/EQ mass that displaced them
   demotes to 0.8/0.6/0.3; deep in-pool notes rise over agreed paper mass (e.g. a
   rank-20 note at 1/81 now outscores a double-agreed rank-1 EQ at 2×0.3/61).
2. **recall@20 is NOT set-invariant this time** (unlike d-r1's permutation theorem): the
   first-20 SET can change (r9's ranks 21–40 can enter; r9's top-20 can fall out).
   Direction not pre-judged; a material DROP would itself be a finding (the cost of
   demotion when gold itself is paper-kind).
3. **Per-class (g) watch, declared now:** `exam_question` (gold anchored on QP chunks,
   demoted 1.0→0.8) and `mark_scheme` (MS 1.0→0.6) are the classes the plan-§7 posture
   trades away from; regression there is the expected cost, and any per-class regression
   >15% relative gets its written tradeoff note. r9's vague_learner/conceptual/
   misconception rank losses are the expected BENEFICIARIES.
4. **Compliant view:** same weights, smaller (VALIDATED-only) pool — same reordering
   logic. (a2) holds large headroom (floor 0.0734 vs 0.1463 recorded); **(c2) is the
   at-risk PASS** (floor 0.1683 vs 0.1816 recorded, +7.9% relative margin) — the weighted
   posture may flip it either way; this run's own bars are evaluated fresh, honestly
   (no recorded verdict is re-judged; d-r1's verdicts stand).
5. **(f)** structurally 0/0 (weights live inside fusion, downstream of the ONE central
   pre-fusion boundary; the reranker cannot re-admit boundary-excluded candidates and
   neither can weights — nothing enters the pool that the arms did not emit).
6. **(e)** latency posture unchanged (weights are O(1) per fused candidate).
7. **§8.1 v1.1 dual-view bars** are the success criteria, evaluated per the ratified
   arithmetic; verdict recorded honestly — NOT PROMOTED is a finding, not an argument.

## 4. Evaluation protocol

- `BENCH_RUN_ID=run-005-e BENCH_FUSION_WEIGHTS=plan_v2` (reranker spec absent) over the
  SAME frozen inputs as r9/d-r1 — **snap-007 × gold-r9 × preload-r9, no re-freeze**: the
  comparison basis is the recorded r9 fabric (the same-basis discipline both prior tranches
  used). Output pack `evidence/bench-001/runs/run-005-e-r1/`.
- Environment: the T-C59 recipe (user-space PostgreSQL 17.11 + pgvector 0.8.0 Debian-native
  debs; JDK 25.0.4.1 + Maven 3.9.9; disposable cluster :5433; Flyway V1→V59; corpus 4,510
  embedded chunks at rev 2 re-verified by the run's fail-closed checks).
- Determinism: the double-pass contract covers the weighted path (pure function ⇒
  byte-identical second pass or abort). §8.1 v1.1 dual-view gate + (d)(e)(f)(g).
- Post-run verification (from recorded bytes): invariant 1 (89/89 set identity), invariant 2
  ((d) recompute via the s8d_ruling_review.py tool against the recorded lists), per-query
  first-20 entry/exit ledger, per-class deltas vs r9 AND vs d-r1 (read-only context).

## 5. Guardrails (restated from the charter)

No production serving change — nothing in production constructs a weighted bench fabric;
the SERVING side's `fuseWithPlanWeights` posture question stays with the owning lane and
the owner's acceptance after a §8-passing verdict (harness spec §9). No frozen artifact is
mutated. No tuning against the frozen set: the weights are the shipped constants, measured
once. No recorded verdict is re-judged. One lever at a time.
