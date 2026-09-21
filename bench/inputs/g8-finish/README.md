# g8-finish inputs

Frozen 2026-09-21T15:00:42.499908+00:00 from production (G8 backfill lane).

- pending_docs.jsonl: 59 documents whose rev2 chunks are still pending
  embedding. This is the G8 backfill queue: 66 papers ingested 2026-09-21 whose
  embed run was cut twice by daily key quota (serving keys sha256:91fdfb06ac then
  sha256:797b77a879 both exhausted), plus the final 8 papers posted after the
  parser fix (4CH0-1C-201601, 5x 4CH1-2CR, 2x specimen).
- identity.json: admin JWT identity for POST /{id}/embed auth.

Transport contract: vectors MUST be produced by the production app itself
(POST /{id}/embed, Spring AI batched transport) — CI single-call REST vectors
are a different vector space (evidence/bench-001/embed-bridge-v2/CORRECTION.md,
top-10 rank agreement 0.79 cross-space). The finish pipeline rotates the Render
embedding key to a remaining key and drives the app's own endpoint.
The G8 default key order is 3,0,1,2 (indices 1 and 2 are the two keys already
exhausted today; 3 and 0 are untouched).
