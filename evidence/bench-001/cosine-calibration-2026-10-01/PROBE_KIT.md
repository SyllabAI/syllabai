# Production probe kit — MIN_COSINE 0.50 flip gate (T-C42, 2026-10-01)

**Gate context:** the calibration pack (`REPORT.md` in this directory) makes the
0.50 flip binding on two gates. Gate 1 (Run005C re-record, `run-005-c-r8`) is
**PASS**. Gate 2 — this probe — is **PENDING, operator-run**. The staged flip
sits on `syllabai-core` branch `tc40-min-cosine-050` @ `06297f2` (no PR by
design) and lands only after this probe is recorded.

**What the probe measures:** the distribution of query-vs-pool cosine over the
**VALIDATED serving pool** at `embed_rev = 2`, for one canonical query vector
embedded in the **production transport** (Spring AI Google GenAI, model
`gemini-embedding-001`, `taskType RETRIEVAL_QUERY`, `outputDimensionality 768`).
The pack's binding rule: the flip lands only if the pool's relevance-bearing
mass sits **above 0.50**.

**Canonical query (PRB-01, first topical probe of the pack, self-verified):**

> explain what happens during the electrolysis of aluminium oxide

Quota cost: **one** `embedContent` call. The SQL is **read-only** (two SELECTs).

---

## Path A — one command (needs `psql` + `jq` locally)

```bash
export GEMINI_API_KEY=...     # the operator-held Gemini key (the Render
                              # SYLLABAI_EMBEDDING_API_KEY value)
export DATABASE_URL=...       # the Neon postgresql:// URL (operator-held)
bash run_production_probe.sh
```

The script prints: the vector dimension check (must be `768`), the pack's
histogram query verbatim, and a derived above-0.50 summary row.

## Path B — manual (Neon web SQL editor)

**Step 1 — get the query vector** (run locally, key never leaves your machine):

```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key=$GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"models/gemini-embedding-001","content":{"parts":[{"text":"explain what happens during the electrolysis of aluminium oxide"}]},"taskType":"RETRIEVAL_QUERY","outputDimensionality":768}' \
  | jq -r '.embedding.values | "[" + (map(tostring) | join(",")) + "]"'
```

Check the output starts with `[` and has 768 comma-separated numbers.

**Step 2 — paste into the Neon SQL editor** with `:qv` replaced by the literal
from step 1 (keep the single quotes):

```sql
-- Pack gate-2 query (byte-identical to REPORT.md, :qv bound)
select width_bucket(1 - (c.embedding <=> ':qv'::vector), 0, 1, 20) as bucket,
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

**Step 3 (same editor session) — derived summary:**

```sql
select count(*) as total,
       count(*) filter (where 1 - (c.embedding <=> ':qv'::vector) > 0.50) as above_050,
       round(100.0 * count(*) filter (where 1 - (c.embedding <=> ':qv'::vector) > 0.50)
             / count(*), 1) as pct_above_050
from document_chunks c
join documents d on d.id = c.document_row_id
where c.embedding is not null
  and c.embed_rev = 2
  and (exists (select 1 from exam_papers p join subjects s on s.id = p.subject_id
               where p.validation_state = 'VALIDATED'
                 and (p.question_paper_document_id = d.document_id
                   or p.mark_scheme_document_id = d.document_id))
    or exists (select 1 from subjects s2 where s2.id = c.subject_id
               and d.validation_state = 'VALIDATED'));
```

---

## Reading the result (decision rule)

- `bucket` b covers cosine `[(b-1)/20, b/20)`; buckets **11–20 = cosine ≥ 0.50**.
- The flip passes when the **dominant share of the VALIDATED pool sits above
  0.50** (`pct_above_050` comfortably over half). Benchmark: the artifact-space
  sweep put **89.9%** of the corpus above 0.50; production sits lower by the
  measured 0.024–0.057 transport downshift, so expect somewhat less — the gate
  asks for the mass, not for 89.9%.
- Paste both result tables back into this chat; the output gets recorded in a
  dated addendum here together with the flip decision.

## Honesty boundaries (inherited from the pack)

- Small-n: one canonical query. The r8 re-record already proved zero gold-loss
  at 120 eval points; this probe guards the pool-mass side only.
- If `pct_above_050` comes back below ~50%, the gate fails: hold the flip,
  record the histogram, and the floor question returns to the worklist.
