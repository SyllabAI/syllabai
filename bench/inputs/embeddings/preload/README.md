# Preload checkpoint for `ops-embed-backfill`

The latest INCOMPLETE `embed-backfill-snap-001` artifact (checkpoint-resume
state — CI runner DBs are ephemeral, this frozen artifact IS the resume
state). The workflow passes this directory as `BENCH_PRELOAD_ARTIFACT`; the
runner verifies it fail-closed (SHA256SUMS + model match + chunk-id identity)
before applying, then embeds only the remaining pending chunks. Replaced each
time a newer checkpoint lands; the COMPLETE artifact graduates to
`bench/inputs/embeddings/snap-001/`. Provenance: `manifest.json`.
