# T-C60 prep pack — papers-axis completion (2026-10-02)

Authority: operator message (zai-web, trace 1a0fc2a56bfb1a31) naming the
papers-axis gaps. Claim-first: T-C60 registered at c7fa75e7fdc3 (T-C57/58/59
taken by concurrent lanes; ID re-asked at the claim parent).

## Status

- Corpus gate for the 5 ingest-target papers: **PASSED** (10/10 sha-vs-pin,
  see corpus-verification.json). All 5 dirs are complete QP+MS pairs with
  print-verified manifests (confidence_rank 0, pdf_text).
- Heal targets for the 11 half-linked VALIDATED ep rows: pinned per identity
  (heal-targets.json). NOTE refined vs the probe report: the 11 rows are
  missing BOTH doc links (ep row exists, no QP/MS documents linked at all).
  10 of 11 identities' correct bytes are pinned in current corpus manifests;
  2025-06/4CH1-2C is one of the 5 ingest-target papers (overlap with item 2).
- 64-chunk promotion (8 SUGGESTED docs): itemization requires the live DB —
  the census counts (8S docs, 64 chunks) come from T-C54/T-C56; the probe's
  P1 itemizes them at execution time.
- Embed-state recheck (09-28 repaired generations): P3 staged; VERIFIED-live
  is the acceptance bar, nothing carried from T-C54.

## Execution instrument (the single open decision)

Write phases run on the T-C54 wave-2 instrument: operator-supplied Neon
credential, env-only, governed batches with batch_run_id + audit rows
recording the operator as the deciding actor, fail-closed pre/post gate
replicas. Read-only probes are staged in scripts (tc60_probe.py, P1-P5,
SELECT-only) and run the moment the credential lands; ingestion of the 5
papers runs through the parser pair pipeline (ParserCli QP/MS -> canonical
bundle -> ingestion persists SUGGESTED -> governed validation batch applies
the operator's named instruction).

## Probe set (scripts/tc60_probe.py, all SELECT-only)

P1 census + SUGGESTED itemization | P2 heal-target checksum join + ep link
state | P3 embed_rev/embedded_at recheck per ep-linked doc | P4 exact
searchServingEligible gate replica (per curriculum) | P5 pre-ingest absence
check for the 10 target checksums.

## Gate expectations (fail-closed deltas)

- Pre: gate replica == 4,608 serving-eligible at rev2; chunks 4,672/4,672
  embedded rev2 (T-C54 pin; INFERRED current until P3/P4 re-run).
- Post (after 5-paper ingest + 11-link heal + 8-doc promotion): +10 docs
  (QP+MS x5) with chunks embedded rev2; links healed; gate = 4,608 + 64
  (promotion) + the 5 papers' new chunks (exact delta asserted from the
  batch audit rows, never assumed).
