# SNAP-004 at-flip freeze record (2026-09-27) — T-C13 corpus snapshot discipline

Task: T-C27 trigger-A re-run substrate — operator directive "re-run trigger A"
(delivered in-chat, trace 1a0e23212e7b3cf5, session web-23eb7684). This is the
freeze the trigger-A path of bench/AT_FLIP_RUNBOOK.md names, executed by the
session holding the sanctioned production read per the coordination handoff
recorded at a61bdb008/db3573a6b (the claiming session is env-gated away from
production; this session verified the flip first-hand and froze it).

## What this is

The fourth versioned freeze in the snap-N series (snap-001 2026-09-17 →
snap-002 2026-09-25 → snap-003 2026-09-26 → snap-004 2026-09-27): a fresh
read-only capture of the serving database under the same evidence discipline,
taken AT the serving flip. The gold re-pair (gold-v3) rides this freeze per
the set+snapshot pair discipline (spec §3/§4): gold-v3's 12 class files are
BYTE-IDENTICAL to gold-v2 (anti-tuning — no query re-selected, re-worded or
re-labeled); only the manifest's snapshot pairing pins move to snap-004.

## The flip, verified first-hand before freezing

- 13 exam_papers rows VALIDATED (11 glmocr-era 09-14 rows + 4CH1/2C June-2019
  and 4CH1/1C January-2022 from the 09-25 bank wave — the count moved
  11 → 13 after the paper-axis repairs f96b0d57, 2026-09-26T21:18Z).
- Their 13 QP + 13 MS documents are VALIDATED at doc level (documents were
  uniformly SUGGESTED at the snap-003 freeze; core 02664958a then recorded
  paper-VALIDATED + doc-SUGGESTED as production reality).
- 317 chunks flip SUGGESTED → VALIDATED: 145 QP + 161 MS + 11 EXTERNAL_
  QUESTIONS (the pre-existing 09-20-cohort 4CH1/1C card document, promoted in
  the same wave).
- The 298 T-C27 cards (2026-09-26) are ALL still SUGGESTED — the card
  validation wave has NOT landed; the card-flip run (r6) stays available.
- No corpus evolution: bank census unchanged (999 documents / 4,343 chunks /
  1,533 questions / 1,533 question_versions); the chunk_ref set, contents,
  kinds and spec_codes are IDENTICAL to snap-003 (verified programmatically,
  per-field).

## Method

- Read path: the sanctioned session-env production connection (the same read
  path the ops-lane state probes use), opened READ-ONLY —
  `set_session(readonly=True)`, SELECT-only statements, rolled back and closed
  at export end. Zero production writes. Method unchanged (SNAP4-M1 = SNAP3-M1).
- Exporter: `snap004_export.py` (carried here as export provenance), adapted
  from the frozen `snap003_export.py`. The t0 predicates are preserved
  verbatim; no predicate extension this generation.
- Determinism: gzip mtime=0; ORDER BY d.checksum, c.chunk_index unchanged.

## Fidelity anchors (all PASS)

Five of seven artifacts are BYTE-IDENTICAL to snap-003 — the non-chunk
substrate remains frozen-stable across all four snapshots:

| file | status vs snap-003 |
|---|---|
| `spec_points.json` | BYTE-IDENTICAL (194 rows; sha b95361eff3ac5a70…, the snap-001→002→003 value) |
| `graph_edges.json` | BYTE-IDENTICAL (152 VALIDATED semantic edges; sha f4dc1ddd10df2fa8…) |
| `misconceptions.json` | BYTE-IDENTICAL (19 rows; sha c659dbdc685a03a2…) |
| `question_anchors.json` | BYTE-IDENTICAL (720 VALIDATED anchors; sha 11a53c11e6e35cec…) |
| `concept_attachments.json` | BYTE-IDENTICAL (117 HUMAN_VALIDATED rows; sha bff866bc4d28edba…); DB SUGGESTED PART_OF pair set still 1:1 with the ratified set |
| `graph_code.json` | rows SET-EQUAL (pinned store @1245df0 unchanged since snap-002; only `source.date` differs by construction) |
| `chunks.jsonl.gz` | same rows, two value deltas + one additive projection — see findings |

## Findings (recorded, none silent)

1. **SNAP4-F1 — the validation wave (the headline)**: 317 chunk rows flip
   SUGGESTED → VALIDATED at doc level (per-doc paper_state), the at-flip
   substrate the harness VALIDATED-only gate reads. Zero regressions. The
   paper axis enters the served view; the card axis stays inert except the
   one promoted 09-20 card document. Full per-kind/per-paper breakdown in
   the manifest deltas.
2. **SNAP4-F2 — chunk paper_code stamps**: 246 chunk rows gained a paper_code
   value (null in snap-003) — the mirror stamping that accompanied the
   post-freeze repair/validation lane. Metadata-only; retrieval identity is
   content-addressed and unaffected.
3. **SNAP4-F3 — chunk subject_id projection**: chunk rows project
   `document_chunks.subject_id` per the at-flip generation enabler
   (syllabai-core e728b7d, core-ci 36310569728 SUCCESS): the optional field
   is parsed as verification/census evidence, never a container gate input
   (the container stamps chunks with the bench scope's subject, single-subject
   topology). snap-001..003 carry no such field; missing/JSON-null fold to
   null (BenchSnapshotSubjectIdTest pins the fold). Census: rows with
   subject_id vs without recorded in the manifest.
4. **Loader contract**: Run003B.loadSnapshot (at the pinned enabler sha) now
   inserts documents.validation_state from the same per-document paper_state,
   so the post-flip freeze serves through BOTH searchServingEligible branches
   exactly as production does. Backward-compatibility for the recorded
   r3/r4 generations is by construction (uniform SUGGESTED + V29 default =
   value-identical insert; sha-pinned dispatches untouched).

## Pairing (the set+snapshot pair discipline, recorded)

- **gold-v3** (`bench/gold-v3/`, staged as `bench/inputs/gold-r5/`): the 12
  class files are BYTE-IDENTICAL to gold-v2 (hashes re-verified at build
  time against the v2 manifest pins). ONLY the manifest's snapshot pairing
  pins move (snap-003 → snap-004) — the designed mechanism for a new
  generation, enforced by gold_check.py's own snapshot-pin gate (the
  validator FAILs a v2-manifest against snap-004: "snapshot hash drift",
  observed and honored). No query/label/evidence change; anti-tuning
  preserved. `gold_check.py (snap-004, gold-v3)` → PASS: 120 records,
  quotas ok, all anchors resolve; selftest 6/6 corruption classes detected.
- gold-v1, gold-v2: byte-untouched. The r3/r4 lineages: untouched.
- The r4 record (trigger B, pre-flip) stands as recorded; its artifacts are
  never rewritten.

## Boundaries respected

- No recorded run in this freeze — the run chain (stage → dispatch → record)
  follows as separate commits with its own RUN_REPORT + SHA discipline.
- No agent-asserted content validation anywhere: the wave was performed by
  the operator/teacher before this directive (verified first-hand, recorded
  above); this lane only freezes the state it found.
- Production: read-only via the sanctioned connection; zero writes.

## Artifacts

| file | sha256 | bytes (uncompressed) |
|---|---|---|
| `chunks.jsonl.gz` | `f1dfaaa5696070cdc1be0d212aecca40ca07600bde8abc97b64a24a32d67fcfc` | 4307323 |
| `concept_attachments.json` | `bff866bc4d28edbaa1765af1a748d1aeebe47dab1ed97c354b329030467acd1b` | 10947 |
| `graph_code.json` | `d2a6c4e547331da4a7f2033a0dec9ba488779c4db451182e6db7f6fd41ad5f07` | 31525 |
| `graph_edges.json` | `f4dc1ddd10df2fa8fe87d5f57e52fc7c3abc2cf44951ad22cd7b7854aadffa5a` | 15686 |
| `misconceptions.json` | `c659dbdc685a03a2c7ed4ac3cb6c00dc3d695a18046044a100219c661ba830c1` | 2264 |
| `question_anchors.json` | `11a53c11e6e35cec6f7bc436a0765a63a321a671f5c9e54be92a41e8571fc78f` | 154953 |
| `spec_points.json` | `b95361eff3ac5a70040e0bc79af7b5f5666704db350505830ca409ead607d6fb` | 39379 |

Manifest: `manifest.json` (counts incl. per-kind paper_state distribution,
predicates, deltas, pairing, serialization notes). SHA256SUMS covers the
seven artifacts (t0 convention). Count summary: 3,831 chunks (1,281 QP +
1,494 MS + 1,056 cards) across 575 documents · 317 serving-eligible flips ·
194 spec points · 152 edges · 19 misconceptions · 720 anchors · 117
attachments.
