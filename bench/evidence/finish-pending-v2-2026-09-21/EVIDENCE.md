# finish-pending-v2 — corpus-v2 card-leg embed COMPLETED (2026-09-21)

Task 33 (retrieval lane). Completes the rev2 ingest the 2026-09-20 auto-embed
stalled at 986/1570 (20:00:25 UTC, daily quota of serving key sha256:797b77a879).

## Run (ops-finish-pending-v2 #4, run 35585223465, SUCCESS)

- transport: the PRODUCTION app's own POST /api/v1/teacher/content/documents/{id}/embed
  (Spring AI batched transport — CI single-call REST vectors are a different
  vector space per evidence/bench-001/embed-bridge-v2/CORRECTION.md)
- key rotation: REMAINING keys only, order [1,3,0]; the stalled serving key
  index 2 (sha256:797b77a879) deliberately excluded
- round 1: key[1] sha256:91fdfb06ac, deploy dep-daofqbrtqb8s73f62kr0 (197s),
  61/61 docs POSTed, embedded=584, skipped=0, failures=0 — COMPLETE in one round
- serving key on Render is now sha256:91fdfb06ac (old key preserved for the
  operator's records; rotate all 4 keys remains a standing security action)

## Post-verify (independent, from operator sandbox + prod DB)

- document_chunks: rev1 2333/2333 (0 pending, UNTOUCHED), rev2 1570/1570 (0 pending)
- rev2 by kind complete: EXTERNAL_NOTES 350/350, EXTERNAL_QUESTIONS 758/758
  (was 174/758), MARK_SCHEME 160/160, QUESTION_PAPER 140/140, SYLLABUS 162/162
- single model gemini-embedding-001, all vectors 768d (0 vectors with dims<>768)
- LIVE E2E PASS (4/4 searches, 4.1-5.2s): knowledge queries hit EXTERNAL_NOTES
  (spec-coded headers) + QP chunks; card queries return the NEWLY EMBEDDED
  EXTERNAL_QUESTIONS cards (scores 0.62-0.80) — the finished leg SERVES

## Corpus-v2 status after this run

INGEST COMPLETE: all rev2 legs embedded (bridge papers + spec + notes + cards).
Serving runs embed_rev=CURRENT_EMBED_REV=2 on the R4 routing build (core 57e0763:
deterministic Fetch/Enumerate + per-kind RRF weights, gates FETCH 40/40,
ENUMERATE 1.0/1.0 recorded by the R4 lane in bench/evidence/r4-routing-2026-09-20/).
