# run-006-bproxy — B-proxy probe (T-C13 harness-internal lexical arm)

**Status:** RECORDED — harness-internal probe, LOCAL VERIFIED (deterministic, offline, snapshot snap-006).
**Arm:** B-proxy (harness-internal Okapi BM25 k1=1.2 b=0.75) — PROXY — NOT a production arm; never citable for promotion decisions.
**Queries:** 89/120 scored (31 excluded — no chunk labels: substrate-absent classes / sparse auto-labels, excluded not zeroed).

## Overall (Recall@5/10/20 · MRR · nDCG@10 · precision@10 · FP@10)

- **ALL chunks (4181):** recall@5 0.1292 | recall@10 0.1745 | recall@20 0.2564 | mrr 0.0737 | ndcg@10 0.1816 | evidence_precision@10 0.0528 | false_positive_rate@10 0.9472
- **VALIDATED-paper chunks only (965):** recall@5 0.0566 | recall@10 0.0667 | recall@20 0.0861 | mrr 0.0684 | ndcg@10 0.1183 | evidence_precision@10 0.018 | false_positive_rate@10 0.982

## Per class (ALL-chunks scope)

| class | n | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| calculation | 10/10 | 0.105 | 0.105 | 0.105 | 0.15 | 0.2018 | 0.05 | 0.95 |
| conceptual | 13/15 | 0.1179 | 0.1821 | 0.2462 | 0.0 | 0.1462 | 0.0462 | 0.9538 |
| exam_question | 4/10 | 1.0 | 1.0 | 1.0 | 0.625 | 0.7188 | 0.15 | 0.85 |
| factual | 11/15 | 0.2 | 0.4 | 0.5818 | 0.0 | 0.3107 | 0.1364 | 0.8636 |
| mark_scheme | 8/8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 10/10 | 0.12 | 0.18 | 0.4 | 0.0 | 0.216 | 0.05 | 0.95 |
| multi_spec_point | 7/7 | 0.0 | 0.0 | 0.0857 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 12/12 | 0.0333 | 0.0667 | 0.1667 | 0.0 | 0.0654 | 0.0333 | 0.9667 |
| vague_learner | 4/8 | 0.0625 | 0.0625 | 0.125 | 0.0 | 0.0967 | 0.025 | 0.975 |
| why_wrong | 10/10 | 0.0867 | 0.0867 | 0.1067 | 0.2559 | 0.2624 | 0.05 | 0.95 |

## Arms unavailable at this run

- **A0:** requires syllabai-core Java lane — PREPARED, not RUNNABLE in this authoring env
- **A:** requires T-C07 + embedding backfill (embedding state not probed here; snapshot carries 4181 chunks)
- **B:** requires T-C14 Bm25Retriever + tsvector migration
- **C/D:** require A + B
- **E/F/G:** require T-C15

## Reading

- The ALL-vs-VALIDATED scope gap is the **quantified cost of the validation boundary**: gold evidence anchored on SUGGESTED papers is unreachable by a compliant serving scope.
- BM25 over exam corpus rewards verbatim stem overlaps (exam_question / why_wrong classes) and penalizes formal spec-title vocabulary (factual / conceptual) — the expected lexical profile; semantic arms (A/C) exist to close exactly this gap.
- These numbers are baselines-on-record for the B-proxy lane only; the production baseline (A0 KG-only) records in the Java lane per the spec (§7 M1).
