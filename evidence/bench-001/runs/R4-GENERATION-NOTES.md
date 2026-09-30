# R4 GENERATION NOTES — the recorded serving-flip-runbook run (2026-09-27)

Operator-commissioned pre-flip recorded run per `bench/AT_FLIP_RUNBOOK.md` trigger B
(directive trace `1a0e07674d2b1e19` recorded in `.syllabai/tasks/T-C27.yaml`). This file
is the interpretive addendum to the runner-generated artifacts; the artifacts themselves
are recorded verbatim and never rewritten.

## Dispatches (all benchmark-only, workflow_dispatch, zero production writes)

| run | workflow | head | outcome |
|---|---|---|---|
| 36286617830 | ops-embed-backfill-r4 | aa6af0005 | SUCCESS — frozen artifact `embed-backfill-snap-001-r4`: 3,831/3,831 chunk vectors preloaded from the production-derived preload (0 chunk API calls), 120 gold queries fresh (key sha256:01ac5264a3; per-key counters in manifest); SHA256SUMS all OK; committed as `bench/inputs/embeddings/preload-r4` @ c704591f5 |
| 36286954444 | ops-run003-b-r4 | c704591f5 | SUCCESS — arm B lexical, recorded at `evidence/bench-001/runs/run-003-b-r4/` @ 573fa2777 |
| 36287130564 | ops-run004-a-r4 | 573fa2777 | SUCCESS — arm A semantic, recorded at `evidence/bench-001/runs/run-004-a-r4/` @ 22b98687 |
| 36287567921 | ops-run005-c-r4 | 573fa2777 | SUCCESS but SUPERSEDED (ordering slip: dispatched before run-004-a was committed; prior-arm context honestly UNAVAILABLE; artifacts not committed) |
| 36287897846 | ops-run005-c-r4 | 22b98687 | SUCCESS — arm C hybrid, RECORDED at `evidence/bench-001/runs/run-005-c-r4/`; full prior-arm context (A served + compliant loaded; A0 honestly UNAVAILABLE — run-002-a0 dir is absent from the r4 repo state) |

Deviations, disclosed: (1) embed-backfill was double-dispatched at 01:47Z (the first
POST returned an unparseable 204 and was re-issued); the duplicate was cancelled and a
single run is recorded. (2) The first arm C dispatch slipped the runbook's "commit prior
runs before the arm-C dispatch" ordering; it completed with honest UNAVAILABLE context
and is superseded by the recorded re-dispatch. Both slips are benchmark-only, no side
effects; deterministic re-runs.

## Why every served number is 0.0 — and why that is the gate working, not a retrieval failure

- **The mechanism is the T-C05/T-C20 VALIDATED-only serving gate on core main
  `45f6774d7`.** The production vector/lexical surfaces (`searchServingEligible`) serve
  VALIDATED-only; snap-003's chunk `paper_state` is uniformly SUGGESTED at doc level (the
  known re-ingestion state lag — snap-003 FREEZE_RECORD finding 4). The served corpus is
  therefore EMPTY: 120/120 zero-result queries on every arm, served and compliant views
  agree, `VALIDATION_BOUNDARY_VIOLATIONS = 0` — zero is the contract post-T-C20; the
  gate held under the real run on all three arms.
- **The vector space is healthy — the zeros are NOT a floor artifact and NOT a preload
  corruption.** Local diagnostic over the frozen artifact: best query→chunk cosine
  0.54–0.69 across 12 gold queries (200-chunk window), inter-chunk cosine 0.70–0.76,
  vector norms ≈ 0.59 (the normal truncated gemini-embedding-001 space). The production-
  mirrored chunk vectors and the fresh RETRIEVAL_QUERY query vectors live in one
  consistent space; the preload's corpus identity was proven by `content_sha256`
  (3,831/3,831 exact) before any of this ran.
- **Caveat on runner text:** the arm A report's "Zero-result queries: 120/120 (all
  top-20 hits below the production cosine floor 0.15 …)" line is STATIC runner template
  text (Run004A report builder); the operative mechanism for this generation is the
  serving gate, not the floor. `results.json` `evaluation_contract` states the true
  semantics ("empty result lists are honest zeros"). The template line is flagged here
  rather than edited — runner output is recorded verbatim.
- **r3 vs r4 cross-generation comparison is invalid by design:** r3's non-zero served
  numbers ran core `c05efb98` (pre-T-C05/T-C20 — the served view was then ALL-scoped,
  which is exactly why r3 surfaced the fp@10 0.99 boundary findings that T-C20 closed).
  r4 runs main post-gate. The r4 record is the FIRST recorded run of the post-T-C20
  production surface.

## What the recorded run establishes (and what it cannot)

- Establishes: the fail-closed chain end-to-end on the r4 pair (staging SHAs, artifact
  checksums, deterministic ids, dual-pass determinism PASS on all arms, zero
  validation-boundary violations across 120 queries × 3 arms); the preload discipline
  (production-derived chunk vectors mirrored SELECT-only, 0 chunk API calls at freeze);
  the §8 arithmetic machinery consuming the r4 inputs cleanly.
- §8 verdict recorded verbatim: **NOT PROMOTED** (a Recall@10 0.0 vs floor 0.3249 FAIL;
  b MRR 0.0 vs 0.2964 FAIL; c nDCG@10 0.0 vs 0.4799 FAIL; d NOT SCOREABLE — zero
  HUMAN_VALIDATED chunk→SP rows; e not evaluable from records; f 0 violations = pass).
- Cannot establish: any retrieval-quality number. The snapshot's starved validation
  state zeroes every served metric; the ALL-denominator axis of the ratified gate has no
  post-T-C20 production surface to measure until the flip (trigger A — the operator/
  teacher validation wave promotes papers/cards). The meaningful at-flip re-run is the
  trigger-A path recorded in the runbook; it stays operator-held.
- For the operator's attention (no work registered): if an ALL-denominator measurement
  is wanted before the flip, it needs an explicitly authorized ungated diagnostic arm —
  not a serving change.
