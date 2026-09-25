# Serving restoration COMPLETE — 2026-09-25 (session 130, operator PAT)

Operator handed the Render PAT ("do it yourself") — the last operator-gated
action was executed end-to-end by the agent with fail-closed guards.

## The real root cause (deeper than the 0-hit dig concluded)

R5 cut-over (09-21) DELETED all 2,333 embed_rev=1 chunk rows
(delete_result.json: deleted_rows=2333, rev1_remaining=0) while RETAINING
the 172 legacy document rows. The T-C23 Option B pre-flight ("rev1 corpus
intact + embedded") was FALSE — the documents census had counted the
STALE denormalized `documents.chunk_count` column, not real
`document_chunks` rows (an embed probe on a VALIDATED-paper QP doc
returned totalChunks=0 while the row claimed chunk_count=12). Flipping
CURRENT_EMBED_REV to 1 therefore served an EMPTY generation: 0 hits at
every probe regardless of deploy state. Render deploys were never the
blocker — 7803102 went LIVE at 16:20Z (Render API, deploy
dep-dar9uj9k55hc73fh); the 349 rev1 chunks that DO exist all belong to
SUGGESTED papers (blocked by the T-C20 gate), and the 11 VALIDATED
papers' docs had zero chunks.

## The repair (identity-faithful, app-mediated, guarded)

Phase 0 (read-only guards, ALL PASS): chunk-state truth via direct SQL
(Render env DB URL, the R5-precedent access class); 22 VALIDATED-paper
doc pointers = 22 distinct doc rows, ALL with 0 real chunks; NO FK
references documents (string pointers by design); canonical_json
retrievable for all 22 with CHECKSUM MATCH (byte-identity proof).

Phase 1-3 (per doc, 22/22, 0 errors — restore_execute.json): guarded
DELETE (exact id + exact checksum + zero-chunks guard) -> re-INGEST the
same canonical through the app (live build 7803102: chunker + V33
metadata mirror + embed_rev=1 stamp) -> idempotent EMBED
(gemini-embedding-001 = the query-time model, so cosine is meaningful —
materially better posture than the deleted rev1 vectors measured 0/9 in
the old eval). ~243 chunks recreated/embedded.

## Result

verify_serving_restore.py: **SERVING RESTORED** — all 5 IGCSE-chemistry
queries return 5/5 hits, scores 0.60-0.73, semantically precise (QP +
MS kinds). Tutor/CLA probe 11/11 PASS; EXPLAIN now carries 6 citations
(corpus chunks fused through the new per-kind weighted RRF — T-C26 live
in the same build).

## Posture notes

- CURRENT_EMBED_REV stays 1 (the operator's Option B stance): the rev2
  corpus is real and embedded but born SUGGESTED — it serves the moment
  rev2-era papers are teacher-validated (T-C23 menu Option A), then the
  constant flips back to 2.
- New doc rows land validation_state=SUGGESTED (corpus law); serving is
  gated on the PAPERS' pre-existing teacher VALIDATED state — no
  agent-asserted validation anywhere; checksums prove byte-identity.
- Docs created by the re-ingest are new rows (old row ids archived in
  restore_execute.json); exam_papers string pointers resolved unchanged.
- Credential hygiene: the Render PAT arrived in chat — rotation at
  engagement end is standing advice (alongside .g4_creds/.g4_token).
