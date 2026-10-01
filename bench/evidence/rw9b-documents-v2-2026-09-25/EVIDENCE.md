# rw-9b — documents-v2 supersession of the 13 clear 4CH1 pairs (2026-09-25)

**Lane:** corpus identity → F10 repair → rw-11 re-parse → g1.7 G1-closure → **rw-9b** (this wave)
**Scope:** the 13 closure-verified corrected pairs (`reparse_g17_report.json` G1-PASS set)
**Actor:** ops session, Task 43. Prod API (syllabai-core.onrender.com) for ingests/embeds;
direct guarded DB writes (psycopg2, sslmode=require) for pointer updates and retirements.

## What the wave did

For each of the 13 clear pairs:

1. **QP v2 ingested** — canonical draft built by the audited converter
   (`pdflane.atoms_to_canonical`, parser main `2e4ba19`, engine `pdflane-atoms/1.2.0`)
   from the g17 re-parse atoms + corrected genuine-C QP bytes pinned at corpus HEAD.
   New checksum → new `documentId` (uuid5 of checksum+engine+engine_version) → no
   dedup conflict. Draft `version` set to 2 (wave marker; identity derivation excludes it).
2. **MS v2 swapped** — the MS bytes were never poisoned, so the v1 pdflane row
   (engine 1.2.0, same checksum) blocks re-ingest via the core's checksum dedup.
   Flow per Task-37-landing precedent: archive v1 canonical_json + chunks
   (`ms_v1_archive/<slug>.json`) → guarded delete (chunks then row, assertions on
   doc_version/checksum) → POST g17 MS draft as v2 (same documentId, doc_version=2).
   Rationale: 8 of the 13 v1 MS canonical_json carried the known pre-g17 marks-layout
   defects (rw-11 G1 families); the bank only ingests closure-verified atoms.
3. **Embedded** — `POST /documents/{row-uuid}/embed` per v2 doc; 349/349 chunks
   embedded, retrieval-identity mirror verified (paper_code/series/year/subject_id).
4. **exam_papers repointed** (12 rows) — pointers set to the v2 `document_id` strings,
   the form the app reads (`findTopByDocumentIdOrderByDocVersionDesc`); this also fixes
   `4CH1/2C June 2022`, whose pointers were uuid-PK-form and therefore app-invisible.
5. **Gen-B QP retired** (12 rows, R-content) — guarded delete after repoint
   (zero ep/bank/bridge references re-verified inline at delete time).

## Pre-write verification chain (all fail-closed)

- 13 manifests fetched from corpus HEAD; all 26 material sha256 pins == reparse input pins.
- Converter checksums == HEAD pins (26/26); MS draft documentIds == the live v1 rows
  (13/13 identity match); QP documentIds absent from prod (13/13).
- Reference guards: 24/26 Gen-B rows fully unreferenced. The `2c-202206` pair carried
  uuid-PK-form refs from the 09-24 grammar-pack drive (7 question_versions + 7
  mark_schemes + the ep row); normalized onto the v2 document_ids **before** the MS delete
  so nothing dangled.

## Counts (prestate → poststate)

| table | before | after | delta |
|---|---|---|---|
| documents | 700 | 701 | +26 v2 −13 MS v1 −12 QP v1 |
| document_chunks | 3,787 | 3,799 | +349 v2 −191 MS v1 −146 QP v1 |
| questions / parts / mark_points / exam_papers / attempts | 1,540 / 7,253 / 5,197 / 105 / 166 | unchanged | **0** (rw-9b is documents-axis only) |

## Verified end-state (rw9b_verify.py, all green)

- 26 v2 rows: checksums pinned, chunk counts == converter preview, 100% embedded,
  validation_state SUGGESTED, retrieval mirror exact (JAN/JUN/NOV + year + paper code).
- 12 ep rows resolve to v2 ids; `2c-202011` has no exam_papers row (flagged for the
  bank wave — its QP v2 doc `6087c43e…` is ready to be referenced by a future draft).
- 25 retired rows absent; uuid-form bank refs confined to the out-of-scope
  `4CH1/2CR June 2022` twin (duplicate-sitting bank-merge wave item).
- Content smoke: `4ch1-1c-202001` QP v2 chunk 0 prints `4CH1/1C`, no `4CH1/1CR`;
  all 13 QP v2 corpora carry base-C references (the F10 poisoning is out of the served corpus).

## Deviations / decisions recorded

- v2 `source.uri` uses the pdflane slug convention (`4ch1-1c-202001/qp.pdf`) vs the v1
  staging-path style (`4CH1-1C-202001/qp.pdf`). Identity is the checksum (§8); uri is
  informational. Kept (re-ingesting 26 embedded rows for casing buys nothing).
- Gen-B QP canonical_json was not archived before retirement: the R bytes remain in
  corpus git history and the parse is deterministic (regenerable); the pre-g17 MS
  canonical IS archived (it parsed never-poisoned bytes and is not trivially regenerable
  without the exact pre-g17 grammar).
- The `2c-202206` bank rows (7 questions) were driven on 09-24 from the then-poisoned
  R QP bytes; their provenance pointer now targets the corrected C QP document, but the
  question CONTENT still needs the bank supersession wave (g8-style drive) — recorded
  as a bank-wave item, deliberately not touched here (documents-axis discipline).

## Files

- `drive_state.json` — resumable phase state incl. every row id touched/deleted
- `guards_report.json` — prestate counts + reference-guard evidence
- `draft_summary.json` / `manifest_pins_check.json` — draft identities + pin chain
- `ms_v1_archive/<slug>.json` — the 13 archived v1 MS canonical_json + chunks (recovery)
- `SHA256SUMS` — integrity manifest of this pack
