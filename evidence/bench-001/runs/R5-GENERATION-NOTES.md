# R5 GENERATION NOTES — the at-flip trigger-A re-run (2026-09-27)

Operator-directed at-flip recorded run per `bench/AT_FLIP_RUNBOOK.md` trigger A
(directive traces `1a0e23212e7b3cf5` — this lane, the owner session with the
sanctioned production read — and `1a0e2220d22a90b1` — the claim-first lane whose
core enabler this generation consumes; coordination handoff recorded in
`.syllabai/tasks/T-C27.yaml` at db3573a6b / a61bdb008). This file is the
interpretive addendum to the runner-generated artifacts; the artifacts
themselves are recorded verbatim and never rewritten.

## What trigger A means here — and the honest scope

The runbook's trigger A = "the flip, then the run". The flip was **verified
first-hand** from the production read before anything froze: the
operator/teacher validation wave promoted **13 exam_papers rows** (11
glmocr-era + 4CH1/2C June-2019 + 4CH1/1C January-2022) with their **13 QP + 13
MS documents VALIDATED at doc level**, plus the pre-existing 09-20-cohort
4CH1/1C card document — **317 chunks flip SUGGESTED → VALIDATED** (145 QP +
161 MS + 11 EQ). The 298 T-C27 cards (2026-09-26) are **all still SUGGESTED**:
the card validation wave has NOT landed. The r5 run is therefore the at-flip
bench **on the paper axis, honestly scoped** — the card axis enters serving
only through the one promoted card doc. The card-flip run (r6) stays available
when the card wave lands. No agent-asserted content validation anywhere: the
wave was performed by the operator/teacher before the directive; this lane
only froze the state it found (read-only, zero production writes).

## Dispatches (all benchmark-only, workflow_dispatch, zero production writes)

| run | workflow | head | outcome |
|---|---|---|---|
| 36311624648 | ops-embed-backfill-r5 | f04451930 | SUCCESS — frozen artifact `embed-backfill-snap-004`: 3,831/3,831 chunk vectors applied from the production-derived preload (**0 chunk API calls**, `chunks_embedded_this_run=0`, `pending_after=0`), 120 gold queries fresh (gemini-embedding-001@768, task RETRIEVAL_QUERY); SHA256SUMS all OK; committed as the complete `bench/inputs/embeddings/preload-r5` @ 5770133f2 |
| 36311973564 | ops-run003-b-r5 | 5770133f2 | SUCCESS — arm B lexical, recorded at `evidence/bench-001/runs/run-003-b-r5/` @ d003a45e0 |
| 36312145176 | ops-run004-a-r5 | d003a45e0 | SUCCESS — arm A semantic, recorded at `evidence/bench-001/runs/run-004-a-r5/` @ 7723d90d8 |
| 36312444139 | ops-run005-c-r5 | 7723d90d8 | SUCCESS — arm C hybrid, recorded at `evidence/bench-001/runs/run-005-c-r5/`; full prior-arm context (A + B results; A0 honestly UNAVAILABLE — carried from r3/r4) |

No deviations: the runbook ordering (commit prior runs before the arm-C
dispatch) was held; every dispatch landed on the commit its artifacts were
recorded from; no re-dispatches were needed.

## The substrate (recorded in the snap-004 FREEZE_RECORD; summarized)

- **snap-004** (at-flip freeze): chunk_ref set, contents, kinds, spec_codes
  IDENTICAL to snap-003 (programmatic per-field diff); 5/7 artifacts
  BYTE-IDENTICAL; graph_code set-equal. Named deltas: SNAP4-F1 (the 317
  validation-wave flips), SNAP4-F2 (246 paper_code stamps), SNAP4-F3 (the
  chunk subject_id projection per the enabler), SNAP4-M1 (method, unchanged).
- **gold-v3** (re-pair): 12 class files BYTE-IDENTICAL to gold-v2 (anti-tuning
  — no query re-selected, re-worded or re-labeled); only the manifest's
  snapshot pins move to snap-004 — the validator's own designed mechanism
  (`gold_check.py` FAILed the v2 pins against snap-004: "snapshot hash drift",
  observed and honored, never bypassed). gold_check PASS (120 records, quotas
  ok, all anchors resolve) + selftest 6/6.
- **preload-r5**: production-derived chunk-vector mirror, SELECT-only over the
  sanctioned session-env read path (3,831/3,831 refs, per-row content_sha256
  verified — the mixed-corpus guard; zero writes).
- **core enabler** (web-98866c45 lane, consumed not re-derived):
  `e728b7deaf6a3c21acb78d420c93904c9213e13e` — Run003B.loadSnapshot carries
  documents.validation_state from the per-document paper_state and stamps the
  bench scope's subject, so BOTH searchServingEligible branches are
  production-faithful in the container; core-ci 36310569728 SUCCESS.

## What the numbers say — the r4 → r5 differential IS the flip

The r4 pre-flip record (trigger B) measured **all-served-metrics 0.0** on a
uniformly-SUGGESTED snapshot. The r5 at-flip record measures the SAME
frozen-set discipline against the SAME 120 queries with 317 chunks newly
serving-eligible:

| arm | served scope | recall@10 | MRR | nDCG@10 | violations |
|---|---|---:|---:|---:|---:|
| B lexical (r5) | 317 VALIDATED chunks | 0.0247 | 0.0449 | 0.0449 | 0 |
| A semantic (r5) | VALIDATED-only gate, 27 reachable | 0.0762 | 0.0543 | 0.1376 | 0 |
| C hybrid (r5) | compliant pre-fusion gate, 27 reachable | 0.0762 | 0.0674 | 0.1473 | 0 |

- The zeros are gone: the at-flip served view is non-empty and measurable —
  the differential the trigger-A path was designed to capture.
- Fusion (C) improves ranking over A (MRR 0.0543 → 0.0674, nDCG@10 0.1376 →
  0.1473) at identical recall — RRF rewards cross-arm agreement.
- exam_question is the standout class on both arms (A recall@10 0.5, MRR
  0.5833; B 0.5/0.75) — the card-anchored gold records now reach serving-
  eligible paper/card chunks.
- Boundary: 0 violations on every arm across 120 queries — the T-C20
  VALIDATED-only gate held under the real post-flip load ("zero is the
  contract").
- Determinism: double-pass byte-identical aggregates on all three arms.

## §8 verdict recorded verbatim: NOT PROMOTED

(a) Recall@10 0.0762 vs floor 0.3249 FAIL · (b) MRR 0.0674 vs 0.2964 FAIL ·
(c) nDCG@10 0.1473 vs 0.4799 FAIL · (d) NOT SCOREABLE (zero HUMAN_VALIDATED
chunk→SP rows — named data gap) · (e) NOT EVALUABLE from records · (f)
boundary 0 violations PASS (results.json `f_boundary.pass=true`) · (g) PASS
trivially vs the zero A0 baseline.

**Caveat on runner text:** the arm C report's static "(f) … hard fail per
§5.1 for the as-served configuration" line is template prose carried from the
r3 generation (where the vector surface predated the gate); the operative
semantics for this generation are results.json's `f_boundary` (0 violations,
pass=true) and the arm A report's explicit "zero is the contract". The
template line is flagged here rather than edited — runner output is recorded
verbatim. Same class of caveat as the r4 notes.

## Honest limits

- The compliant served corpus is 317 chunks across 14 documents (13 papers +
  1 card doc) — small against a 3,831-chunk snapshot; recall floors calibrated
  on the r1-era ALL-served corpus are not met by a 317-chunk served view, and
  that is the honest finding: the paper-axis wave alone does not clear the
  promotion gate. The card wave (298 T-C27 cards) is the next denominator
  change; r6 measures it when the operator/teacher lands it.
- fp@10 ≈ 0.98 on arms A/C: with 89 labeled queries against 317 served chunks,
  most retrieved chunks carry no gold-evidence label — the label sparsity is a
  property of the frozen gold set, not new noise.
- r5 vs r3 comparisons remain invalid by design (different served corpora,
  different gates); the valid differential is r4 (pre-flip) vs r5 (at-flip) —
  same set+snapshot discipline, same 120 queries, 317-chunk flip in between.

## What this closes (and what stays open)

- Closes: the T-C27 trigger-A at-flip re-run, operator-held since 5a18253d —
  now recorded on all three arms with the r4→r5 differential on file.
- Stays open: the card validation wave (operator/teacher action) + the r6
  card-flip run; §8 promotion (fails on quality floors until the corpus/labels
  grow); the T-C06/F-168 HUMAN_VALIDATED chunk→SP substrate (spec axis
  NOT SCOREABLE); runner §8 template-text fix (cosmetic, registered here).
