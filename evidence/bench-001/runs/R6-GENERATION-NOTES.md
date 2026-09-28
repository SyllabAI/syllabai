# R6 GENERATION NOTES — the r6 card-flip at-flip run (2026-09-28)

Operator-directed at-flip recorded run per `bench/AT_FLIP_RUNBOOK.md` trigger A
and `bench/r6-staging/R6_STAGING_STATE.md` ("executes the moment the wave
lands"). **The r6 gate — the operator/teacher card validation wave — LANDED
2026-09-28 ~08:03Z**: the operator (Nawaf Al Hussain Khondokar) completed the
298-card review sheet (sha256 `89c0714681ecd710…`, delivered via their own
GitHub upload) and the recorded decisions — **295 VALIDATE + 3 FLAG**
(#207/#278/#291, the no-spec-linkage cards, operator notes verbatim) — were
applied VERBATIM in one fail-closed transaction = `content_review_audit` run
`a5d13c0a-2503-4d06-bb14-9397e9a1cf37`, 298 operator-labeled rows, sheet
sha256-pinned in every detail (import trace `1a0e702ed9960375`; freeze trace
`1a0e71324fcdc119`). No agent-asserted validation anywhere: every decision
carries the operator's named declaration; the wave was the operator's own.

## The flip, verified first-hand before freezing

documents census (kind EXTERNAL_QUESTIONS) at freeze: **296 VALIDATED** (295
wave + the pre-existing 09-20-cohort 4CH1/1C card doc) / **3 FLAGGED**
(non-servable; serving gate untouched) / **80 SUGGESTED neighbors untouched**
(created ≠ 2026-09-26, verified unchanged). Chunks mirror the documents:
**295 up-flips + 3 flag decisions, 0 true regressions**. The
`teacher_validation_events` ledger stays 0 rows (its CHECK domain excludes
documents; the wave's ledger is content_review_audit — constraint contract
respected). A same-day app-side teacher wave on the papers/schemes axis
(pilot.teacher: 11 qv VALIDATE + 1 ep VALIDATE_ALL = +11 question_anchors,
purely additive, audit-evidenced) was captured as SNAP5-F6; zero interference
with the card wave.

## The freeze

`snap005_export.py` run FOR REAL after two narrowly-scoped, manifest-bound
exporter amendments (SNAP5-F5: SUGGESTED→FLAGGED card decisions are the
operator's own, not regressions — any other down-flip still aborts; SNAP5-F6:
question_anchors fidelity = multiset superset, growth recorded as a delta).
ALL VERIFICATIONS PASS: 4,181 chunks (3,831 carried identical + 350 notes
additive), drift gate 0 divergences (census 210/209/164/181 + 205/4/0/1),
spec_points/graph_edges/misconceptions/concept_attachments byte-identical to
snap-004, `chunk_spec_hv.json` BYTE-IDENTICAL (b5b20ffa…, SNAP5-H1 — §8(d)
flips NOT SCOREABLE → scoreable-with-coverage). Freeze committed:
`evidence/bench-001/snapshots/snap-005/` @ records `ab600e18f1`
(+ FREEZE_RECORD.md + amended exporter as provenance).

## Dispatches (all benchmark-only, workflow_dispatch, zero production writes)

| run | workflow | outcome |
|---|---|---|
| 36400373270 | ops-embed-backfill-r6 | SUCCESS — frozen artifact `embed-backfill-snap-005`: **4,181/4,181 chunk vectors from the production-derived preload — 0 chunk API calls** (the SNAP5-F4 notes chunks ARE embedded in production), 120 gold queries fresh (gemini-embedding-001@768, RETRIEVAL_QUERY); committed as the final `bench/inputs/embeddings/preload-r6` @ 821fb5ebb7 |
| 36401105223 | ops-run003b-r6 | SUCCESS — arm B lexical, recorded at `evidence/bench-001/runs/run-003-b-r6/` @ 5f409767a5 |
| 36401616124 | ops-run004a-r6 | SUCCESS — arm A semantic, recorded at `evidence/bench-001/runs/run-004-a-r6/` @ 34a96f5379 |
| 36402153529 | ops-run005c-r6 | SUCCESS — arm C hybrid fabric (the registered orchestrator gap CLOSED), recorded here |

Core pin for every run: `05f262169` = core main at the freeze (carries the
§8(d) substrate wiring c91372c+64c71ff+670423a+b45b5d6 + the census fail-closed
loader). No re-dispatches; the runbook ordering (commit prior runs before the
arm-C dispatch) was held.

## The numbers (verbatim from the run reports; chunk axis, n=89 labeled queries)

| arm | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| B lexical (VALIDATED-served) | 0.0247 | 0.0247 | 0.0247 | 0.0449 | 0.0449 | 0.0045 | 0.0112 |
| A semantic (served = VALIDATED-only gate) | 0.0627 | 0.0740 | 0.0852 | 0.0350 | 0.1166 | 0.0213 | 0.9787 |
| C hybrid RRF k=60 (fabric) | 0.0627 | 0.0740 | 0.0852 | 0.0640 | 0.1384 | 0.0213 | 0.9787 |

- 112/120 zero-result queries on B (the bare-word AND form starves natural-
  language questions — the known finding, unchanged); 0/120 zero-results on
  A/C but everything below the 0.15 cosine floor is scored as real zeros.
- fp@10 ≈ 0.98 on A/C is a denominator statement, not a defect: the served
  pool is 4,181 chunks of which 3,718 are SUGGESTED papers/notes/axes the
  compliant view filters — B's 0.0112 fp on its 612-chunk VALIDATED pool and
  A/C's 0.9787 on the ALL pool are the dual-denominator design working as
  recorded (ruling-1 gate arithmetic stays on the ALL denominator).

## §8(d) — SCORED for the first time; the honest reading

`spec_resolution_hv` is SCORED on all three arms (full-coverage **0.0** ·
micro-average **0.0** over 84 gold points on 89 scored queries, both views).
This is **honest production truth, not a harness failure**: the 210
HUMAN_VALIDATED chunk→SP mappings anchor on notes chunks, notes are SUGGESTED
in production truth, and the production serving gate (T-C05/T-C20
VALIDATED-only) therefore excludes exactly the chunks that carry the
mappings. The substrate (SNAP5-H1) makes (d) scoreable — the recording is the
deliverable; the number says the promotion step for the notes axis has not
happened, which is the operator's decision, not this lane's. **No promotion
claim on (d) at r6** (pinned rule).

## Interpretation pass (the pre-registration's two obligations, records 09a624728)

**1. Gold-query leakage — measured, no inflation signal.** Per query, the
normalized gold ask was compared against the normalized content of its top-1
and top-3 served chunks (difflib ratio ≥ 0.8 = near-duplicate; verbatim
containment also flagged). Max ratio across all arms: **0.4033** (A/C),
0.2794 (B) — far below the 0.8 near-duplicate threshold. Containment flags:
A 2/89 queries (both in top-3, not top-1), B 3/89, C 3/89 — all short-ask-
inside-long-chunk coincidences at ratios 0.15–0.27 (a short factual ask whose
exact phrasing appears somewhere in a multi-paragraph chunk), recorded here
as flagged-but-not-near-duplicates. **No served result this generation is a
near-duplicate of its gold ask; nothing in the numbers above is inflated by
memorization.** (Measurement script + full summary:
`r6_interpretation.py` / `interpretation_summary.json`, session artifacts.)

**2. Attribution risk — moot this generation, recorded for the pattern.**
The risk was "a high (d) beside weak (a)/(b)/(c) is a coverage signal, not a
retrieval-quality signal". (d) is 0.0 on every arm and both views, so there
is no high-(d) number to misread; the obligation resolves trivially. The
reading discipline stands for future generations: §8(d) alone must never be
cited as "retrieval works".

## The card-axis serving impact (r6's headline delta vs r5)

Across the 89 scored queries, arms A and C served **671
EXTERNAL_QUESTIONS refs — every one VALIDATED** (the operator wave's cards
entering the vector serving path for the first time; r5 served 0 card chunks).
Arm B served 0 — the lexical branch is paper-anchored by design (the pinned
asymmetry held exactly as the card-serving-boundary fixture proved).
The 3 FLAGGED cards never appear in any served set (their chunks are
FLAGGED; the gate excludes them) — the operator's review decisions are
visible end-to-end in serving behavior.

## Honest scope

- The runs replay the frozen snap-005 corpus through production serving code
  on disposable pgvector containers; zero production writes; zero production
  reads beyond the sanctioned SELECT-only freeze path.
- Arms A/B/C are benchmarkable capabilities, NOT serving defaults: nothing in
  production constructs a RetrievalFabric or a Bm25Retriever; promotion
  happens in the owning lane with its own verification discipline after the
  §8 gate arithmetic is ratified by its owner.
- The 3 FLAGGED cards need source verification (operator's own note); the 80
  neighbor SUGGESTED docs are out of this generation's scope by design.
- The r6 §8 verdict: (a)/(b)/(c) axes recorded per arm as in r5 (no threshold
  change, no promotion arithmetic run — the gate input is the ALL-denominator
  record above); (d) SCORED at 0.0 with the serving-gate explanation; the
  first §8(d)-scoreable baseline is now on record for every future generation
  to regress or improve against.
