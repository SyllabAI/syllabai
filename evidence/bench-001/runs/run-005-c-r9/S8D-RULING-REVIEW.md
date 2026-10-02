# §8(d) ruling-question review — run-005-c-r9 (d) section, evidence pack for the spec owner

**Status:** REVIEW RECORDED — evidence and analysis assembled for the spec-owner ruling; this lane does not rule (r9 RUN_REPORT line 73: "recorded here as data, not resolved by this lane").
**Date:** 2026-10-02 | **Inputs:** run-005-c-r8/r9 `results.json` (recorded bytes) · `bench/evidence/chunk-sp-substrate-2026-09-27/chunk_spec_hv_projection.json` (frozen) · gold-v5 (frozen) · snap-006/snap-007 chunk tables · `RETRIEVAL_BENCHMARK_HARNESS_SPEC.md` §1/§5/§8/§8.1 · `bench/S8D_SCORING_HANDOFF_2026-09-28.md`.
**Tool:** recompute script persisted at `scripts/s8d_ruling_review.py` (records-repo lane workspace); every claim below is derived from recorded bytes, and the recompute is self-checked against both runs' recorded aggregates (9/9 exact).

## 1. The ruling question, verbatim

r9 RUN_REPORT, §8.1 gate item (d): full-coverage **0.5618 → 0.4607 (−10.11pp)** · micro-average **0.9167 → 0.7857 (−13.10pp)** vs the r8 baseline — beyond the 1pp allowance as a raw delta, with the pre-registered coverage/competition interpretation attached and no promotion claim made on (d). The Reading section states the open question:

> "the ruling question is whether §8(d) means **mapping fidelity** (unchanged by construction here) or **top-rank resolution compositionality** (moved) — that is a spec-owner decision, recorded here as data, not resolved by this lane."

Reading (i) — *mapping fidelity*: (d) measures the correctness/stability of the HUMAN_VALIDATED chunk→SpecificationPoint projection itself. Reading (ii) — *top-rank resolution compositionality*: (d) measures whether the arm's served top-ranked evidence composes to cover the query's gold spec points.

## 2. What the spec text says (the textual reading)

- **§1 (purpose):** the guarded failure mode is "a retrieval system can produce fluent answers while resolving the wrong SpecificationPoint. The primary quality axis is therefore **SpecificationPoint resolution and evidence identity**, not answer fluency."
- **§5 (metrics):** the flagship metric is defined over the serving surface: "**does the arm surface** evidence whose `HUMAN_VALIDATED` spec mapping covers the query's gold spec points".
- **§8 v1.0(d):** "SpecificationPoint resolution does not regress by more than 1 percentage point" — a *regression* rule, which presupposes a metric that moves when serving moves. §8.1 v1.1 re-indexed only the (a)(b)(c) bars; (d)'s definition was never touched.
- **The scoring handoff (§5)** quotes the §5 definition verbatim and specifies the implemented scorer: covered set = union of HV codes **over the arm's served (ranked) evidence refs**. `ChunkSpecHvResolution.scoreQuery` (core `c4b67e8`) does exactly that; `Run005C` feeds it the full served top-20 fused candidate list, per view.

Textually, the metric's object is the **served surface**, not the projection's internal fidelity. A fidelity instrument already exists separately and is reported every run: the HV drift gate (re-verification of all 210 mappings against the frozen bytes), the projection census (210/209/164/181), and the substrate bridge's anchor-kind audit (205 CLEAN / 4 MULTI / 1 MISS).

## 3. The recompute: every basis point of the r8→r9 (d) delta is accounted for

Per-query (d) recomputed for both runs from recorded bytes (projection ref→codes; gold-v5 gold points; each run's recorded served `ranked_refs`). Self-check — the recompute reproduces the recorded aggregates exactly:

| | recomputed | recorded |
|---|---|---|
| r8 full-coverage | 50/89 = 0.5618 | 0.5618 |
| r8 micro | 77/84 = 0.9167 | 0.9167 |
| r9 full-coverage | 41/89 = 0.4607 | 0.4607 |
| r9 micro | 66/84 = 0.7857 | 0.7857 |

**The complete movement ledger r8→r9:**

- Full-coverage flips 1→0: **9 queries** (50→41). Flips 0→1: **0**. The −10.11pp is exactly these 9 losses; nothing else moves the number.
- Query-point losses: **11** (77→66), gains **0**. Ten losses sit on the 9 flip queries; one is a partial-coverage loss (g2-061, misconception, gold {1.26, 1.28}: r8 covered {1.26} → r9 covered {} — already non-full in r8, zero in r9).
- Lost codes (query-point counts): 4CH1-1.3 ×2 (g2-056, g2-112) · 4CH1-1.28, 4CH1-4.5, 4CH1-3.21C, 4CH1-1.17, 4CH1-1.58C, 4CH1-1.44, 4CH1-1.45, 4CH1-1.10, 4CH1-1.26 ×1 each.
- **Corpus check: CLEAN.** Every lost point's carrier refs are still present in snap-007 — no carrier chunk vanished, no mapping changed. Every single loss is a carrier ref falling **out of the served top-20** on its query.
- **r8 carrier ranks before the drop: 7, 8, 12, 13, 14, 15, 16, 16, 20** (plus carriers that already covered from other chunks) — deep ranks, never top-5. The r8 baseline's (d)=0.5618 was already living at the edge of the scoring horizon.
- **What displaced them (r9 top-20 newcomers, by kind):** overwhelmingly paper mass — e.g. g2-016: 12 MARK_SCHEME + 3 QUESTION_PAPER; g2-011: 8 MS + 5 QP + 3 EXTERNAL_QUESTIONS; g2-048: 5 MS + 3 QP + 3 EQ; incl. re-ingest chunks (snap-007-only refs). Crucially, the newcomers are **not the queries' own tier-1 gold chunks**: on these 9 queries the gold_evidence chunk labels were mostly unsurfaced in *both* generations (exceptions: g2-011 tier-1 at r8 rank 12; g2-056 tier-1 entering at r9 rank 16). This is volume competition from query-adjacent same-paper mass, not better evidence displacing worse.
- Flip classes: misconception ×3, prerequisite ×3, conceptual ×1, factual ×1, multi_spec_point ×1. Six of the nine lost exactly one point of several (kept the rest) — full-coverage accounting is brittle to single-point loss on multi-point queries; the micro reading weighs the same 11 losses across all 84 points. Both readings fail the 1pp rule in the same direction.

## 4. Findings

- **F1 — The mapping-fidelity input did not move, by construction.** spec_points byte-identical across the freeze, HV drift gate 0 divergences, census pinned 210/209/164/181 in both runs' results.json. Under reading (i), r9's (d) would be *unmoved* — and no recorded number could ever catch what actually happened to the served surface.
- **F2 — The served-surface input moved, measurably and completely.** The recompute decomposes 100% of the delta into 9 full-coverage flips + 1 partial loss, each a carrier ref crossing the top-20 horizon. Nothing unexplained remains.
- **F3 — The mechanism is the pre-registered coverage/competition shape, now with named rows.** The newly-served QP/MS/EQ mass (wave-unlocked, 3,162 up-flips + 329 re-ingest chunks) outranks the HV-mapped notes carriers under RRF fusion on those queries. The carriers were at deep ranks already (median ~14 of 20).
- **F4 — (d) as implemented IS the compositionality reading.** The scorer's definition, the handoff, and the recorded-generation behavior all measure "does the served top-20 compose to cover the gold points" — horizon-sensitive by construction (a carrier at rank 21 is an uncovered point).
- **F5 — Reading (i) would make (d) uninformative in exactly the scenario the spec built it for.** §1 names fluent-but-wrong serving as the guarded failure; a fidelity-only (d) cannot see serving regress, and would have blessed this run's (d) while the learner-facing surface lost 11 gold-point resolutions in top ranks.
- **F6 — Verdict-irrelevant here, blocker-relevant forward.** r9 is NOT PROMOTED on (a)(b)(c)(b2)(c2) regardless of (d). Under reading (ii), (d) additionally stands as a genuine beyond-1pp regression on record — a fourth failing axis that the rank-side levers (arm D reranker port, fusion weights) must recover before any promotion claim; under reading (i), the same rank-side recovery would be tracked only by (a)-(c), and (d) would be silent.

## 5. Consequences of each ruling

- **Rule (ii) — compositionality (the spec-text reading):** r9's (d) stands as recorded: a real −10.11pp/−13.10pp movement, honestly beyond the 1pp allowance, mechanism fully explained, no waiver needed or taken. The 1pp rule does its intended job: it blocks promotion until rank quality recovers compositionality — consistent with the recorded NOT PROMOTED verdict and the named levers. No spec change required; optionally codify the horizon (scored over served top-20) and the granularity choice (both reported; full-coverage recommended) in the same §10 ratification the handoff already flags.
- **Rule (i) — fidelity:** (d) as scored since r8 would be redefined mid-series; the serving-side coverage metric the runs have actually been producing would need a new home (a new letter or the (a)-(c) family) via a dated §8.x amendment per the spec's own versioning rule ("changing thresholds and re-judging an old run against new thresholds is forbidden"). The r9 (d) row would need a corrective note, and the lane would still have to build a separate fidelity instrument — which the drift gate already provides every run.

## 6. Review conclusion (input to the ruling, not the ruling)

The evidence supports reading (ii): the spec's own definition, the implemented scorer, and the recorded runs all measure top-rank resolution compositionality, and the r9 (d) movement is fully, byte-level explained as a serving-surface event (9 flips + 1 partial loss; carriers intact; paper-mass competition; deep pre-drop ranks) with zero mapping-layer contribution. Ruling (ii) keeps the recorded series coherent, keeps (d) falsifiable, and prices exactly the rank-quality problem the run identified (evidence found at median depth ~14; MRR 0.0700). The lane records this as the review's recommendation and defers the ruling to the spec owner.
