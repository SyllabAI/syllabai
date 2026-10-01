# MIN_COSINE calibration — frozen score distributions (T-C40 ④, 2026-10-01)

**Status:** RECORDED — deterministic, offline, zero API spend; vectors read from the frozen
embed-bridge-v2 artifact; every recorded top-3 RE-VERIFIED from raw vectors (PASS, 10/10 probes).
**Inputs:** 300 chunk vectors × 10 topical probes (self-consistent CI-transport space) + paired
FETCH evals in artifact AND production-vector space + the artifact↔DB drift record (CORRECTION.md).

## Headline finding

**At the current MIN_COSINE = 0.15 the floor is a no-op on this corpus: 100.0% of chunks clear it
for every probe** (mean over probes). Whatever the floor was meant to exclude, it excludes nothing
— the candidate-hygiene problem the review named (R4) is not theoretical, it is total on the
measured space.

## Measured separation (recomputed from raw frozen vectors)

- Probe top-3 (relevant) hits: worst cosine **0.6069**
- Non-hit bulk: max **0.6978**, p95 **0.6412**
- The distributions OVERLAP at the top (a non-hit reaches 0.6978) — no floor
  can fully separate relevant from junk; a floor can only cut the low tail that today competes for
  evidence slots on flat/vague queries where the top-12 reaches deeper into the bulk.
- Paired FETCH queries: worst hit cosine **0.6875** (artifact space) vs
  **0.6309** (production-vector space) — the observed transport downshift is
  **-0.024** (artifact↔DB mean pairwise cosine 0.9083, top-10 agreement 0.79).

## Floor sweep (30/30 = all probe top-3 hits retained)

| floor | hits retained | noise above floor per probe | corpus fraction above floor |
|---|---|---:|---:|
| 0.15 | 30/30 | 297.0 | 1.000 |

| 0.20 | 30/30 | 297.0 | 1.000 |

| 0.25 | 30/30 | 297.0 | 1.000 |

| 0.30 | 30/30 | 297.0 | 1.000 |

| 0.35 | 30/30 | 297.0 | 1.000 |

| 0.40 | 30/30 | 297.0 | 1.000 |

| 0.45 | 30/30 | 296.9 | 1.000 |

| 0.50 | 30/30 | 266.6 | 0.899 |

| 0.55 | 30/30 | 125.8 | 0.429 |

| 0.60 | 30/30 | 22.5 | 0.085 |

| 0.65 | 20/30 | 2.3 | 0.014 |

| 0.70 | 5/30 | 0.0 | 0.002 |

## Recommendation

**MIN_COSINE = 0.5** (rule: worst hit cosine 0.6069 − observed artifact→DB downshift
-0.024 = 0.5829, rounded DOWN to the 0.05 grid, minus one further grid step as
explicit transfer-safety margin). In production space this keeps every observed relevant hit with
margin while cutting a real share of the bulk. **0.55 is the
evidence-maximal alternative in artifact space but sits ~0.0002 above the worst
production-transferred hit — rejected unless the re-record and production probe both agree.

## Flip gate (binding)

The constant change lands ONLY together with:
1. the **Run005C re-record** over snap-006 × gold-v5 with the new floor (the "new floors mean
   re-verified serving" rule; vector axis replays from the frozen preload artifact — no API spend);
2. the **production-space probe** below, which must show the VALIDATED pool's relevance-bearing
   mass above the new floor.

```sql
-- Production-space confirmation (read-only): distribution of query-vs-pool cosine
-- for one canonical query vector, over the VALIDATED serving pool at CURRENT_EMBED_REV.
-- Bind :qv to the production (Spring AI, RETRIEVAL_QUERY) embedding of the query text.
select width_bucket(1 - (c.embedding <=> :qv::vector), 0, 1, 20) as bucket,
       count(*)
from document_chunks c
join documents d on d.id = c.document_row_id
where c.embedding is not null
  and c.embed_rev = 2
  and (exists (select 1 from exam_papers p join subjects s on s.id = p.subject_id
               where p.validation_state = 'VALIDATED'
                 and (p.question_paper_document_id = d.document_id
                   or p.mark_scheme_document_id = d.document_id))
    or exists (select 1 from subjects s2 where s2.id = c.subject_id
               and d.validation_state = 'VALIDATED'))
group by 1 order by 1;
```

## Honesty boundaries

- The frozen vectors are the CI transport variant; production vectors come from the Spring AI
  batched transport (mean pairwise cosine artifact↔DB 0.9083). The SEPARATION STRUCTURE
  transfers; exact cutoffs are confirmed by the flip gate above, not assumed.
- 10 topical probes + 9 FETCH pairs is a small n; the sweep's shape (cliff between 0.55 and 0.65)
  is the robust part, the exact cliff edge is not.
