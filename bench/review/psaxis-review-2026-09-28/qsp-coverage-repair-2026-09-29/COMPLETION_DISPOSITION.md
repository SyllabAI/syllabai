# QSP coverage repair — the 9 unmapped pilot-cohort questions (2026-09-29)

Trace: `1a0ea81eb466e08d` · operator ask: "bump the mapped-question coverage for
the 9 unmapped pilot questions" · mechanics: Task-66 class (fail-closed SQL on
prod Neon, dry-run first, no content mutation).

## Cohort identification

Tranche 4.15 recon measured `question_spec_points` at 621/630. The 630 = the
2026-09-19 SME pilot landing (593 `sme-eq-*` questions) + the 2026-09-22 paper
batch (37 questions). The 2026-09-26 mapping wave (+634 rows) went to the
09-24/09-25 batches and did NOT touch these. Bank has since grown to 946
active / 2389 mapping rows; within the recon cohort the 9 unmapped are exactly
where the recon left them (measured, not guessed — scripts
`qsp_unmapped_probe.py` / `qsp_cohort_segment.py` / `qsp_nine_identity.py`).

## The 9 and their derivations (all grounded in part content vs the live 194-node
4CH1 SUBTOPIC vocabulary; style copied from same-paper mapped siblings)

| # | Question | Content basis | Mapping (PRIMARY first) |
|---|----------|---------------|--------------------------|
| 1 | 4ch0/2012-01/1C#q2 (8m) | rust conditions, galvanising, oxidation MCQ | 2.18 P; 2.19 S; 2.20 S |
| 2 | 4ch0/2012-01/1C#q3 (13m) | NH4+/Cl− tests, ⇌ symbol, hazard | 2.47 P; 2.48 S; 3.17 S; 1.38 S |
| 3 | 4ch0/2012-01/1C#q5 (11m) | hydrocarbons, bromine water, alkane general formula, isomers | 4.1 P; 4.3 S; 4.19 S; 4.28 S |
| 4 | 4ch0/2012-01/1C#q7 (9m) | halogen colours/states, HCl equation, acidity only in water | 2.5 P; 2.31 S; 1.25 S |
| 5 | 4ch1/2023-01/2CR#q1 (4m) | pH values, Group 0, elements in glucose | 2.29 P; 1.24 S; 1.8 S |
| 6 | 4ch1/2023-01/2CR#q4 (9m) | formula types, homologous series, alcohols, polyesters | 4.3 P; 4.2 S; 4.29C S; 4.48C S; 4.49C S |
| 7 | 4ch1/2023-06/1CR#q3 (8m) | atom structure, isotopes, Ar from abundances | 1.16 P; 1.15 S; 1.17 S; 1.37 S |
| 8 | sme-eq-2-7-…-q3-p1 (MCQ 1m) | measure the volume of a liquid | 2.33C P; 2.40C S |
| 9 | sme-eq-2-7-…-q3-s (4m) | name the apparatus table | 2.33C P; 2.40C S |

Sibling precedent used: 2012-1C q1 → 1.10P+1.8S+1.9S, q9 → 2.22C+2.23C;
2023-01 2CR q2 → 1.4+1.5C, q8 → 2.11+2.12+2.44 — 4CH0→4CH1 cross-spec mapping
is established house practice. Twin SME questions (p1/s) carry identical
mappings (package pattern: q4-p1/p2/s and q7-p1/s identical; q15-p1 == q15-s).

## Execution

`scripts/qsp_repair_execute.py` (sandbox copy) — single transaction,
every insert guarded by NOT-EXISTS, in-tx asserts (9 refs mapped, exactly one
PRIMARY each, cohort 630/630, all new nodes 4CH1 SUBTOPIC), dry-run ROLLBACK
then COMMIT. Rows: 30 (table 2359 → 2389), provenance/validation_state
AI_VALIDATED (the table's only existing values, 2359/2359).

## Verification (all green)

1. DB post-commit: table 2389; cohort 630/630 mapped; bank-wide active
   unmapped 60 → 51 (remaining 51 = later batches with ING-* synthetic
   primary topics — OUT of the pilot cohort, recorded as a named open item).
2. Serve path (prod API, fresh probe learner): `GET /exam-papers/{id}`
   exposes the new `specPoints` on all repaired paper questions — 2CR-Jan23
   q1/q4, 1CR-Jun23 q3, 4CH0-Jan12 q2 — indistinguishable from house-mapped
   siblings. `scripts/qsp_api_verify.py` → ALL PASS.
3. Evidence path (prod, end-to-end): fresh learner → structured attempt +
   full self-mark on the repaired 2CR-Jan23 q1 → evidenceFired=True →
   `/learners/me/state` carries 4 skillStates: the ING topic anchor +
   SUBTOPIC 4CH1-2.29 / 4CH1-1.24 / 4CH1-1.8 at mastery 0.357.
   `scripts/qsp_e2e_evidence_probe.py`. Before the repair this question could
   only fire topic-level evidence.

## Observations recorded (no action taken)

- sme-eq-2-7-…-q3-p1: MCQ options are empty strings (4 options, C correct) —
  image-option ingestion loss, same disposition class as the recorded
  empty-stem bank shape; mapping unaffected (stem is fully readable).
- The 51 remaining unmapped questions all carry synthetic `ING-*` primary
  topic nodes (per-paper ingestion anchors, TOPIC type). Naming open item:
  **T-QSP2** — later-batch questions (09-24/25/26/28 landings) need both
  real primary-topic assignment and spec-point mapping before their evidence
  can paint anywhere meaningful.
