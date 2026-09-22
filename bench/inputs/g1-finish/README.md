# g1-finish inputs

Frozen 2026-09-22 from production (G1 MS-classifier landing lane).

- pending_docs.jsonl: 86 documents whose rev2 MARK_SCHEME chunks are pending
  embedding: 83 G1-upgraded replacements (the old-spec MS row grammar upgrade,
  parser commit 9f38dda — marks arithmetic now verified against BOTH printed
  sources; canonical content changed for 83 of the 85 paper-axis MS docs) plus
  the first 3 MS-only papers (Nov 2020 COVID session: 4CH1-1CR/2C/2CR, parser
  commit dffeb1d --ms-only mode), 1,344 chunks total.
  The 83 replaced docs' old rows were archived to
  download/g1_ms_replace_archive/ (canonical_json + chunks incl. f32-LE b64
  embeddings) and deleted in a guarded single transaction AFTER the archive;
  the new docs were POSTed through the app's own ingest (kind=MARK_SCHEME).
- identity.json: admin JWT identity for POST /{id}/embed auth.

Transport contract: vectors MUST be produced by the production app itself
(POST /{id}/embed, Spring AI batched transport) — CI single-call REST vectors
are a different vector space (evidence/bench-001/embed-bridge-v2/CORRECTION.md,
top-10 rank agreement 0.79 cross-space). The finish pipeline rotates the Render
embedding key to a remaining key and drives the app's own endpoint.
The G1 default key order is 1,2,0,3 — as of 2026-09-22 all four keys recovered
after the Pacific-midnight reset; index 3 is the current serving key and is
tried last so a single-round completion leaves a fresh key serving.
