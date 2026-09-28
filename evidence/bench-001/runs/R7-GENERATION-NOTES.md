# R7 GENERATION NOTES — the serving-set eval generation (2026-09-28)

**Commission.** Operator directive **"Proceed with (1) eval"** (IM trace
`1a0e88bb060ed3b5`) = item (1) of the corrected standing menu
(`evidence/serving-rev2-flipback-refutation-2026-09-28/REPORT.md`): run the
bench harness (run-004-a pattern) against **today's serving set**, zero
production writes. Claim-first registration: `bb56d5b` → rebased → `ba829c1`.
Staging commit: `6db6bdd` (snap-006 frozen ALL-VERIFICATIONS-PASS; gold-v5
re-pair; preload-r7; r7 workflows). Core pin: `d9cb3ddcf2` (main at staging;
the `05f262169..d9cb3dd` delta is the c37582d hygiene tranche — verified
SQL-emission-identical for every Document.Kind on the serving surface).

**Dispatches (benchmark-only, workflow_dispatch, zero production writes,
zero API calls).**

| run | workflow | outcome |
|---|---|---|
| 36446065734 | ops-run003-b-r7 | SUCCESS — arm B lexical, recorded `evidence/bench-001/runs/run-003-b-r7/` |
| 36446512908 | ops-run004a-r7 | SUCCESS — arm A semantic, recorded `evidence/bench-001/runs/run-004-a-r7/` |

Arm C was NOT dispatched: the commission named the run-004-a pattern; C is a
separate generation (its r6 record stands).

## What this generation measures (and the reconciliation, stated plainly)

The serving set being scored is **snap-006 production truth**: the VALIDATED
pool is **965 chunks** (EQ 309 + QP 145 + MS 161 + EN 350) — i.e. the r6 pool
(612) **plus the operator's two same-day decisions**: the flagged3 flip (3 EQ
cards, batch `0d5e4c4a`, trace `1a0e7865c3b35715`) and the notes-axis
promotion (350 EN chunks + 112 docs, batch `ef4c1fe4`, trace
`1a0e88af08e12df5`).

Correction carried from the staging state: the refutation report's "the
09-25/26 VALIDATED corpus has NEVER been eval'd" was imprecise — r6 already
served the post-card-wave VALIDATED corpus (671 EQ refs, all VALIDATED). What
r6 could not measure is exactly what r7 does: **both operator decisions now
live in the served set**, and the HV-mapped notes substrate is reachable. The
numbers below are the first record of that state.

## The numbers (chunk axis, n=89 labeled queries, frozen gold-v5)

| arm / view | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 |
|---|---:|---:|---:|---:|---:|---:|
| B lexical (965-chunk VALIDATED pool) | 0.0247 | 0.0247 | 0.0247 | 0.0449 | 0.0449 | 0.0045 |
| A semantic (served = production gate) | 0.0273 | 0.0515 | 0.0717 | 0.0313 | 0.0684 | 0.0146 |
| A semantic — **r6 for comparison** | 0.0627 | 0.0740 | 0.0852 | 0.0350 | 0.1166 | 0.0213 |

- VALIDATION_BOUNDARY_VIOLATIONS: **0 on both arms** (the T-C05/T-C20 gate held
  under the 965-chunk pool; non-zero would have been a regression).
- Zero-result queries: B 112/120 (the known bare-word AND-form starvation,
  unchanged); A 0/120 (all hits honest, cosine floor 0.15).
- Compliant-starved: 0; served == compliant on A (gate cross-check agrees).

## §8(d) — the headline delta: 0.0 → 0.9167 micro / 0.5618 full-coverage

`spec_resolution_hv` (84 gold points, 89 scored queries, both views identical):
**gold_points_covered 77/84 · full-coverage 0.5618 · micro-average 0.9167**.
r6 recorded 0.0/0.0 with the explanation that the HV-mapped notes chunks were
SUGGESTED and therefore excluded by the serving gate — "the promotion step for
the notes axis has not happened, which is the operator's decision". The
operator then made that decision (`pursue (a)`); r7 measures the consequence:
**the notes substrate now serves, and the vector surface resolves spec points
through it at 0.9167 micro** (unbridged gold point unchanged: 4CH1-PR-08;
projection census 210/209/164/181 byte-stable).

**Attribution discipline (the r6 warning MATERIALIZED — read this before
citing (d)):** r6 pinned the rule "§8(d) alone must never be cited as
'retrieval works'". r7 is exactly the predicted case: a high (d) beside a
WEAK chunk axis. The (d) number is a **coverage signal of the promoted notes
axis** (the mappings' anchor chunks entered the served set) — it is NOT
evidence that chunk retrieval quality improved. The chunk-axis numbers stand
on their own and declined (below).

## The chunk-axis decline is MEASURED displacement, not drift

Per-query top-10 kind composition across all scored queries (snap-006 chunk
kinds joined over the served refs):

| generation | QP | MS | EQ | EN |
|---|---:|---:|---:|---:|
| r6 top-10 slots | 266 | 272 | 352 | 0 |
| r7 top-10 slots | 120 | 136 | 186 | **448** |

The 350 newly-servable notes chunks took **448/890 top-10 slots**, displacing
paper-anchored chunks. The frozen gold labels paper-anchored evidence for
every class except revision_note, so displacement converts directly into
recall/precision declines — concentrated where gold evidence is
paper-anchored (factual 0.1455→0.0364, prerequisite 0.05→0, misconception
0.02→0) and absent where the anchor basis is unchanged (calculation,
conceptual, exam_question 0.5, vague_learner, why_wrong: byte-identical
values). Drill-down: 2 factual queries lost their top-10 gold hits; in both,
notes chunks replaced them (e.g. g2-009's top-5 went MS 3 + EQ 2 → EN 5).

**Honest label-coverage caveat (recorded, not tuned on):** a notes chunk that
genuinely helps a factual query still scores as a miss — the frozen set has no
notes labels for non-revision_note classes. Re-authoring gold against observed
retrievals would violate the anti-tuning rule; the registered route for that
question is a dev split / versioned re-freeze (§3.2).

## Pre-registered leakage check (same instrument as r6)

Per query, the normalized gold ask vs its top-3 served chunk contents
(difflib ratio; ≥0.8 = near-duplicate): **max ratio 0.4033** — far below
threshold; 2/89 verbatim-containment flags, both at top-3 (not top-1),
short-ask-inside-long-chunk coincidences. **No served result is a
near-duplicate of its gold ask; nothing above is inflated by memorization.**

## The menu question, answered

**"Does what serves today score bridge-quality?"** — **Not on the chunk
axis** (recall@10 0.0515, prec@10 0.0146 — and r7 additionally shows the
promoted notes axis displacing paper evidence on the frozen labels).
**The corpus question therefore does NOT dissolve**, and menu item (2) (the
eval-gated re-stamp of the 615 VALIDATED chunks 1→2) gains its eval input: a
re-stamp changes which rows serve under rev2 semantics but not this quality
picture (same model, same content — the refutation already established the
rev stamp is a content-generation marker, not a model marker). The strong
signal on record is §8(d) resolution through the notes/KG substrate — a
coverage capability the serving path can exploit at the retrieval-policy
level (per-kind weights, the registered T-C26/RFC surface), which is a
different decision than the re-stamp. Both remain operator-gated.

## Honest scope + staleness notes

- The run reports' report() template prose is r6-era in two places (the §8(d)
  dual-view caveat still calls the notes chunks SUGGESTED; B's report carries
  the r6-class "first scoreable run" framing). The pinned harness text is
  preserved unchanged — **the results.json numbers + this generation record
  govern**.
- preload-r7 carried the BYTE-IDENTICAL frozen r6 vector rows (production
  embeddings unchanged — the two promotions touched states/stamps only); all
  row guards re-verified (4,181/4,181 coverage, deterministic chunk ids, qid
  set 120/120, single model, 768 dims). Zero embedding API calls in this
  generation.
- gold-v5: set byte-identical to gold-v4/v3 (validator mechanism); pairing
  pins re-issued to snap-006; `gold_check` PASS (120 records, all anchors
  resolve).
- Zero production writes anywhere in this generation; the only production
  reads were the snap-006 exporter's SELECT-only freeze path (readonly
  session, rolled back).
