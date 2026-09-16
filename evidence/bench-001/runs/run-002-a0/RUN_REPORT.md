# Run 002  -  A0 KG-only baseline (T-C13 M1)

**Status:** RECORDED  -  production baseline on record (LOCAL VERIFIED; deterministic, offline, snapshot snap-001).
**Arm:** A0 KG-only  -  production GraphKnowledgeRetriever (unmodified) over frozen snapshot: title-token specificity matching over VALIDATED structure nodes, maxTopics=5, single-token floor 0.50; single-list RRF k=60; NoReranker  -  RUNNABLE  -  current production serving default; the baseline to beat.
**Code:** production `GraphKnowledgeRetriever` + `ReciprocalRankFusion` unmodified over snapshot-backed repo stubs; core version `9690c00`.
**Date:** 2026-09-17 | **Gold:** gold-v1 frozen | **Determinism:** double in-process run byte-identical.

## Evaluation contract

- SpecPoint resolution (flagship, A0's native axis): coverage of gold spec points by the fused ranked topics (top-5).
- Chunk axis: A0 emits no chunk evidence (production truth at 0/2,333 embedded) -> REAL ZEROS per ratified spec section 6, not exclusions. Zero boundary violations.

## SpecPoint resolution (overall, n=120)

- coverage_mean=0.5569, exact_hit_rate=0.5083, matched_ratio=0.6, precision_mean_over_matched=0.2944, gold_points_mean=0.8667

### Per class

| class | coverage_mean | exact_hit_rate | matched_ratio | precision(over matched) |
|---|---:|---:|---:|---:|
| calculation | 0.0 | 0.0 | 0.0 | 0.0 |
| conceptual | 1.0 | 1.0 | 1.0 | 0.23 |
| diagram_dependent | 0.0 | 0.0 | 0.0 | 0.0 |
| exam_question | 0.0 | 0.0 | 0.0 | 0.0 |
| factual | 1.0 | 1.0 | 1.0 | 0.2322 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 |
| misconception | 0.65 | 0.5 | 0.8 | 0.4104 |
| multi_spec_point | 0.5714 | 0.4286 | 0.7143 | 0.32 |
| prerequisite | 0.6944 | 0.4167 | 0.9167 | 0.3545 |
| revision_note | 1.0 | 1.0 | 1.0 | 0.315 |
| vague_learner | 1.0 | 1.0 | 1.0 | 0.2917 |
| why_wrong | 0.0 | 0.0 | 0.0 | 0.0 |

## Chunk axis (A0 real zeros  -  the engine-without-fuel state on record)

- ALL-chunks (2333) and VALIDATED-only scopes: all chunk metrics 0.0 over 98 labeled queries (22 excluded  -  no chunk labels, same rule as run-001).
- This is the baseline the section 8 thresholds will be evaluated against once arms A/B/C light up: any chunk-producing arm beats it by construction, which is why the resolution axis and run-001's B-proxy numbers carry the real comparison weight until then.

## Signals

- Queries with zero matched topics: 3/120 (production: fail-closed refusal path).
- Prerequisite signals: 0 across 0 queries; misconception signals: 0 across 0 queries (recorded, unscored).

## Arms unavailable at this run

- A: T-C07 + embedding backfill (0/2,333 embedded)
- B: T-C14 Bm25Retriever + tsvector migration
- C/D: require A + B
- E/F/G: require T-C15

## Reading

- A0's chunk-axis zeros are the quantified 'engine built, fuel not loaded' state: the tutor's evidence chain carries no document chunks today.
- Prerequisite and misconception signals are ZERO across all 492 matched topics - not a stub artifact: the settled pedagogy edges (112 REQUIRES_PREREQUISITE + misconception family) live on 4CH1-CON-* concept nodes, which are all SUGGESTED (invisible to the production matcher) and carry no VALIDATED attachment rows bridging them to spec points (snapshot concept_attachments = 0). A0 in production therefore never emits pedagogy context; surfacing it is arm I / KG-expansion work.
- Comparator caveat: factual/conceptual (and their vague paraphrases) score coverage 1.0 partly by construction - rule R2 authors those queries from spec-point titles, the same surface A0 matches on. The informative classes for arm comparisons are the stem-derived ones (exam_question, why_wrong, calculation, mark_scheme, diagram_dependent) where A0 scores 0.0.
- The resolution profile splits exactly along the documented v0 limitation (title-token matching, no stemming/synonymy): formal spec-title vocabulary matches; colloquial learner phrasing does not  -  semantic/lexical arms exist to close precisely this gap.
- Numbers are comparable line-for-line with run-001 (same metric formulas, same exclusion rule, same denominators).
- Comparator honesty: A0 here runs the production retriever over the frozen snapshot  -  matching semantics are the production code, not a port; the only modeling deltas (structure nodes = the 182 snapshot spec points; misconception family interpretation) are recorded in results.json.
