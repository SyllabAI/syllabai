# CORRECTION — embed-bridge-v2 artifact vs production vectors (2026-09-20)

The manifest.json in this artifact states: "rev2 re-verified post-ingest by
DB-vs-artifact vector diff". That verification was performed and it FAILED
identity — this note is the honest record of what was found and what was done.

## Finding

The CI embeddings (this artifact; single `embedContent` REST calls,
RETRIEVAL_DOCUMENT, outputDimensionality=768) are NOT byte-identical to the
vectors production's Spring AI `GoogleGenAiTextEmbeddingModel` provider wrote
at `POST /{id}/embed` (batched transport, same model/taskType/dimensions),
despite the chunk CONTENT being byte-identical (300/300 SHA-verified,
see eval_report_dbvectors.json / verify_ingest_v2.py V3):

- max abs component diff: 8.91e-02 (float4 storage both sides)
- per-chunk cosine artifact-vs-DB: min 0.8619 / mean 0.9083 / max 0.9467
- top-10 neighbor rank agreement between the two spaces: 0.7907

For rev1 the equivalent G2 gate held float4 identity because the preload
vectors were produced through the SAME provider path as production. For rev2
the CI shortcut (raw REST, single-call transport) produced a DIFFERENT vector
space at the component level. Transport is not value-transparent here.

## Consequence

- The CANONICAL rev2 eval substrate is the PRODUCTION vector set (read back
  from document_chunks, embed_rev=2) — eval_report_dbvectors.json. The CI
  artifact vectors (eval_report.json) overstate paired-gate results
  (9/9 vs the canonical 6/9) because both sides of that comparison shared the
  single-call transport shape.
- The frozen gold QUERY vectors (embed-backfill-snap-001) remain canonical
  (G4: production semantics, reconciled against CI run-004-a-r3).

## Canonical gate result (production vectors)

- Paired covered-subset: rev2 6/9 hit@10 vs rev1 1/9 (only enumerate_paper
  ENU-037 hit on rev1; FETCH 0/40 on rev1 per CI run-004-a-r3)
- Topical probes: 10/10 keyword-matched in top-10
- The 3 rev2 FETCH near-misses are same-paper-code/wrong-year confusions
  ("question 6 summer 2011" surfacing 2012/2021 q6 MS chunks) — precisely the
  metadata-intent class the plan assigns to the R4 deterministic Fetch path
  over the V33 columns (series/year/paper_code/atom_number), which the rev2
  ingest now populates on every chunk.

This artifact is retained unmodified (SHAs pin it) as the record of the
CI-computed space; treat it as a transport-variant reference, not the serving
truth.
