# Run 001 — B-proxy baseline (T-C13 M1, partial)

**Status:** RECORDED — harness-internal probe, LOCAL VERIFIED (deterministic, offline, snapshot snap-001).
**Arm:** B-proxy (harness-internal Okapi BM25 k1=1.2 b=0.75) — PROXY — NOT a production arm; never citable for promotion decisions.
**Queries:** 98/120 scored (22 excluded — no chunk labels: substrate-absent classes / sparse auto-labels, excluded not zeroed).

## Overall (Recall@5/10/20 · MRR · nDCG@10 · precision@10 · FP@10)

- **ALL chunks (2333):** recall@5 0.2679 | recall@10 0.2954 | recall@20 0.3638 | mrr 0.2464 | ndcg@10 0.4299 | evidence_precision@10 0.0827 | false_positive_rate@10 0.9173
- **VALIDATED-paper chunks only (296):** recall@5 0.1388 | recall@10 0.1449 | recall@20 0.1658 | mrr 0.233 | ndcg@10 0.3237 | evidence_precision@10 0.0439 | false_positive_rate@10 0.9561

## Per class (ALL-chunks scope)

| class | n | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| calculation | 10/10 | 0.375 | 0.375 | 0.375 | 0.9 | 0.9 | 0.11 | 0.89 |
| conceptual | 13/15 | 0.2846 | 0.3231 | 0.3385 | 0.0 | 0.2716 | 0.0692 | 0.9308 |
| exam_question | 8/10 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.1375 | 0.8625 |
| factual | 12/15 | 0.2167 | 0.3167 | 0.4833 | 0.0 | 0.3374 | 0.1333 | 0.8667 |
| mark_scheme | 8/8 | 0.0 | 0.025 | 0.05 | 0.0 | 0.0222 | 0.0125 | 0.9875 |
| misconception | 10/10 | 0.3 | 0.32 | 0.47 | 0.0 | 0.4276 | 0.1 | 0.9 |
| multi_spec_point | 7/7 | 0.0571 | 0.0857 | 0.2571 | 0.0 | 0.124 | 0.0429 | 0.9571 |
| prerequisite | 12/12 | 0.1167 | 0.15 | 0.2333 | 0.0 | 0.3309 | 0.075 | 0.925 |
| vague_learner | 8/8 | 0.125 | 0.125 | 0.15 | 0.0 | 0.125 | 0.025 | 0.975 |
| why_wrong | 10/10 | 0.24 | 0.24 | 0.28 | 0.7144 | 0.7262 | 0.09 | 0.91 |

## Arms unavailable at this run

- **A0:** requires syllabai-core Java lane (Java 25 + Maven unavailable in authoring env) — PREPARED, not RUNNABLE here
- **A:** requires T-C07 + embedding backfill (0/2,333 chunks embedded)
- **B:** requires T-C14 Bm25Retriever + tsvector migration
- **C/D:** require A + B
- **E/F/G:** require T-C15

## Reading

- The ALL-vs-VALIDATED scope gap is the **quantified cost of the validation boundary**: gold evidence anchored on SUGGESTED papers is unreachable by a compliant serving scope.
- BM25 over exam corpus rewards verbatim stem overlaps (exam_question / why_wrong classes) and penalizes formal spec-title vocabulary (factual / conceptual) — the expected lexical profile; semantic arms (A/C) exist to close exactly this gap.
- These numbers are baselines-on-record for the B-proxy lane only; the production baseline (A0 KG-only) records in the Java lane per the spec (§7 M1).
