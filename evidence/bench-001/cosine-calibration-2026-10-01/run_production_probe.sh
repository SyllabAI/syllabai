#!/usr/bin/env bash
# Production probe — MIN_COSINE 0.50 flip gate (T-C42, 2026-10-01).
# Read-only: ONE Gemini embedContent call + two SELECTs against the Neon DB.
# Needs: curl, jq, psql. Creds stay in your env (GEMINI_API_KEY, DATABASE_URL).
set -euo pipefail

: "${GEMINI_API_KEY:?export GEMINI_API_KEY first}"
: "${DATABASE_URL:?export DATABASE_URL (Neon postgresql://) first}"

Q='explain what happens during the electrolysis of aluminium oxide'

echo "== step 1: production-space query embedding (gemini-embedding-001, RETRIEVAL_QUERY, 768) =="
RESP=$(curl -sf "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key=${GEMINI_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d "$(jq -n --arg q "$Q" '{model:"models/gemini-embedding-001",content:{parts:[{text:$q}]},taskType:"RETRIEVAL_QUERY",outputDimensionality:768}')")

DIMS=$(printf '%s' "$RESP" | jq '.embedding.values | length')
if [ "$DIMS" != "768" ]; then
  echo "FATAL: embedding dimension is $DIMS, expected 768 — transport mismatch, ABORT" >&2
  exit 1
fi
QV=$(printf '%s' "$RESP" | jq -r '.embedding.values | "[" + (map(tostring) | join(",")) + "]"')
echo "vector OK (768 dims)"

POOL_FILTER="
from document_chunks c
join documents d on d.id = c.document_row_id
where c.embedding is not null
  and c.embed_rev = 2
  and (exists (select 1 from exam_papers p join subjects s on s.id = p.subject_id
               where p.validation_state = 'VALIDATED'
                 and (p.question_paper_document_id = d.document_id
                   or p.mark_scheme_document_id = d.document_id))
    or exists (select 1 from subjects s2 where s2.id = c.subject_id
               and d.validation_state = 'VALIDATED'))"

echo "== step 2: pack gate-2 histogram (byte-identical query, :qv bound) =="
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "
select width_bucket(1 - (c.embedding <=> '${QV}'::vector), 0, 1, 20) as bucket,
       count(*)
${POOL_FILTER}
group by 1 order by 1;"

echo "== step 3: derived above-0.50 summary =="
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "
select count(*) as total,
       count(*) filter (where 1 - (c.embedding <=> '${QV}'::vector) > 0.50) as above_050,
       round(100.0 * count(*) filter (where 1 - (c.embedding <=> '${QV}'::vector) > 0.50)
             / count(*), 1) as pct_above_050
${POOL_FILTER};"

echo "== done: paste both tables back into the chat for the record =="
