# SNAP-003 re-freeze record (2026-09-26) — T-C13 corpus snapshot discipline

Task: T-C13 / bench lane — operator directive "Proceed with retrieval bench
(snap-003 re-freeze + gold-v2)" (delivered in-chat, session web-23eb7684).
This is the freeze the T-C27 blocked item names ("recorded T-C13 bench
(snap-003 re-freeze + gold-v2) — operator-held per the snap-002
FREEZE_RECORD; owed at the serving flip"); the operator directive lifts the
hold on the SUBSTRATE (this snapshot + gold-v2). The recorded serving-flip
run itself remains owed at the flip.

## What this is

The third versioned freeze in the snap-N series (snap-001 2026-09-17 →
snap-002 2026-09-25 → snap-003 2026-09-26): a fresh read-only capture of the
serving database under the same evidence discipline. Gold-v2 is generated
from this snapshot in the same freeze per the set+snapshot pair discipline
(spec §3/§4); gold-v1 stays byte-untouched and SHA-paired with snap-001.

## Method

- Read path: the sanctioned session-env production connection (the same read
  path the ops-lane state probes use), opened READ-ONLY —
  `set_session(readonly=True)`, SELECT-only statements, rolled back and closed
  at export end. Zero production writes; zero roles created.
- SNAP3-M1 (method delta, recorded): snap-002 froze via an isolated Neon
  branch + dedicated role created with the management credential; that
  credential is not present in this session, so the freeze uses the direct
  read-only connection instead. Every query is a SELECT; the discipline
  boundary (no production mutation) is unchanged.
- Exporter: `snap003_export.py` (carried here as export provenance), adapted
  from the frozen `snap002_export.py`. The t0 predicates are preserved
  verbatim except one named extension (SNAP3-F1).
- Determinism: gzip mtime=0; re-gzip of the staged chunks artifact verified
  byte-identical at freeze time.

## Fidelity anchors (all PASS)

Five of seven artifacts are BYTE-IDENTICAL to snap-002, which was itself
byte-identical to snap-001 on these files — the entire non-chunk substrate is
frozen-stable across all three snapshots:

| file | status vs snap-002 |
|---|---|
| `spec_points.json` | BYTE-IDENTICAL (194 rows; sha b95361eff3ac5a70…, the snap-001→002 value) |
| `graph_edges.json` | BYTE-IDENTICAL (152 VALIDATED semantic edges; sha f4dc1ddd10df2fa8…, the snap-001 chain value) |
| `misconceptions.json` | BYTE-IDENTICAL (19 rows; sha c659dbdc685a03a2…) |
| `question_anchors.json` | BYTE-IDENTICAL (720 VALIDATED anchors; sha 11a53c11e6e35cec…) |
| `concept_attachments.json` | BYTE-IDENTICAL (117 HUMAN_VALIDATED rows; sha bff866bc4d28edba…); DB SUGGESTED PART_OF pair set still 1:1 with the ratified set (status lag preserved, all CONCEPT→SUBTOPIC) |
| `graph_code.json` | rows SET-EQUAL (pinned store @1245df0 unchanged since snap-002; only `source.date` differs by construction) |
| `chunks.jsonl.gz` | the live corpus — see findings |

## Findings (recorded, none silent)

1. **SNAP3-F1 — predicate extension (the headline)**: `chunks.jsonl.gz` now
   includes `documents.kind='EXTERNAL_QUESTIONS'` — the T-C27 question cards
   (298 ingested 2026-09-26 + 81 pre-existing 2026-09-20), 1,056 chunks
   across 379 documents, all SUGGESTED and serving-inert at freeze time. The
   extension is what makes this pair usable for the serving-flip recorded
   run the T-C27 debt names: when cards enter the serving set, the run can
   consume snap-003 + gold-v2 without a further freeze. The dual-denominator
   discipline (ALL vs VALIDATED-only) already handles non-served chunks —
   snap-001's corpus was 86% non-served papers. `EXTERNAL_NOTES` (350
   chunks) and `SYLLABUS` (162) stay EXCLUDED (T-C06/C13 lane governance;
   counts recorded in the manifest).
2. **SNAP3-F2 — QP/MS corpus evolution since snap-002**: 2,517 → 2,775
   QP/MS chunks (rw-9b v2 supersession of the 13 clear pairs, bank-wave
   repoint, T-C23 guarded repair); the card axis is purely additive
   (+1,056). QP/MS→QP/MS survival arithmetic is in the manifest deltas.
3. **SNAP3-F3 — chunk rows carry `spec_codes`** (the V33 GIN column, landed
   by T-C27's deterministic join): projected jsonb → sorted unique code
   strings on every chunk row. Loader-safe: `BenchSnapshot` reads known
   fields via path accessors and ignores unknown ones. Rows-with-codes by
   kind: QP 174/1,281, MS 237/1,494, cards 295/1,056 (these reconcile
   T-C27's "512 → 923" exactly: 350 notes + 162 syllabus pre-existing = 512;
   +411 QP/MS = 923; the 295 card rows arrived with the card ingest).
4. **paper_state semantics unchanged**: `documents.validation_state` is
   uniformly SUGGESTED in snap-002 AND snap-003 (doc-level state; paper-level
   VALIDATED lives on exam_papers — 11 VALIDATED — and question_versions
   axes). Recorded to preempt the misreading that a state reset occurred.
5. **Docs-census precision note**: the snap-002 FREEZE_RECORD's "345
   documents" prose counted documents-table rows (including archive rows
   whose chunks had been deleted by the re-ingestion waves); the frozen
   artifact itself carries 173 distinct documents. snap-003 records both
   numbers: 575 documents with chunks under the snap-003 predicate (196 QP/MS
   + 379 cards), against 346 QP/MS documents-table rows (150 archive rows
   carry no chunks — the chunk JOIN excludes them, t0 behavior unchanged).

## Boundaries respected

- gold-v1: byte-untouched (validator selftest re-run green in this freeze —
  see gold-v2 record).
- No recorded run, no serving re-projection, no core sync, no policy change —
  none commissioned; the serving-flip recorded run remains operator-owed.
- Production: read-only via the sanctioned connection; zero writes.

## Artifacts

| file | sha256 | bytes (uncompressed) |
|---|---|---|
| `chunks.jsonl.gz` | `671a4d8cbc6596c10a50b04a6f952f216b182f475f7879180d86f154875a3a92` | 4106837 |
| `concept_attachments.json` | `bff866bc4d28edbaa1765af1a748d1aeebe47dab1ed97c354b329030467acd1b` | 10947 |
| `graph_code.json` | `2f0ed04bb60d7a664f124a4af61e4c6b27b1a85cc752d18036459b97a5debca3` | 31525 |
| `graph_edges.json` | `f4dc1ddd10df2fa8fe87d5f57e52fc7c3abc2cf44951ad22cd7b7854aadffa5a` | 15686 |
| `misconceptions.json` | `c659dbdc685a03a2c7ed4ac3cb6c00dc3d695a18046044a100219c661ba830c1` | 2264 |
| `question_anchors.json` | `11a53c11e6e35cec6f7bc436a0765a63a321a671f5c9e54be92a41e8571fc78f` | 154953 |
| `spec_points.json` | `b95361eff3ac5a70040e0bc79af7b5f5666704db350505830ca409ead607d6fb` | 39379 |

Manifest: `manifest.json` (counts, predicates, deltas, pairing, serialization
notes). SHA256SUMS covers the seven artifacts (t0 convention). Count summary:
3,831 chunks (1,281 QP + 1,494 MS + 1,056 cards) across 575 documents · 194
spec points · 152 edges · 19 misconceptions · 720 anchors · 117 attachments.
