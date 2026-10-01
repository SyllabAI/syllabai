# pending-v2 finish inputs

Frozen 2026-09-21T09:38:02.641056+00:00 from production.

- pending_docs.jsonl: 61 documents whose embed_rev=2 chunks are pending
  (584 chunks, all kind=EXTERNAL_QUESTIONS — the question-card leg that the
  2026-09-20 ingest auto-embed stalled on at 20:00:25 UTC, daily quota of the
  then-serving key fingerprint sha256:797b77a879).
- identity.json: admin JWT identity for POST /{id}/embed auth.

Transport contract: vectors MUST be produced by the production app itself
(POST /{id}/embed, Spring AI batched transport) — CI single-call REST vectors
are a different vector space (see evidence/bench-001/embed-bridge-v2/CORRECTION.md,
top-10 rank agreement 0.79 cross-space). The finish pipeline rotates the Render
embedding key to a remaining key and drives the app's own endpoint.
