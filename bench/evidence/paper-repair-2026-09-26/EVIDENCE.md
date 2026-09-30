# Paper-axis repair evidence — series/year backfill + Jun-2024 CR relink (2026-09-26)

Operator directive: "Ok, start executing" (the paper-axis repair queue logged in the
verification session). Two repairs executed against the live DB following the
bank-wave/rw-9b discipline (archive-first, inline guards, FK-safe deletes, API
ingestion, post-gates). All facts first-hand probed (psycopg2, sslmode=require,
read-only probes for every pre-state; guarded transactional writes for changes).

## Context corrections recorded (worklog Tasks 40-41 vs truth)

- 4CH1 2C/2CR June-2022 "twin bank-merge": ALREADY EXECUTED by the bank-wave lane
  (bw-bank-wave-2026-09-26 EVIDENCE.md: MERGE x2 of the Summer-2022 duplicate-sitting
  rows, exam_papers 105 -> 104). The June-2022 rows are the canonical same-sitting
  registrations, not unresolved twins. Verification-lane mislabel corrected.
- HOLD-NO-DOC premise ("QP docs absent"): FALSE — the 4CH1-1CR/2CR June-2024 QP
  documents existed all along (ingested by the G1 corpus landing, 09-21/22) but were
  invisible to uri-pattern probes because their source_uri (`4CH1-1CR/qp.pdf`) carries
  no year token. Identity PROVEN first-hand: the converter's uuid5(checksum+engine)
  derivation over the sha-pinned corpus bytes reproduces the live documentIds exactly
  (QP afa9a7e7 / 82d5aeca; MS 4c3c9759 / 123e0bf0).

## Repair B — exam_papers.series/year backfill (12 bank-wave rows)

- Defect: the past-paper draft-ingest path (PastPaperDraftDto) never sets series/year;
  the 12 ep rows created 2026-09-25 16:56-17:01Z carried NULL/NULL, breaking
  series/year-based resolution (matches the core lane's 09-26 live-probe complaint).
- Fix: guarded UPDATE deriving JAN/JUN/NOV + year from session_label (single
  transaction, belt-and-braces WHERE id IN + series IS NULL AND year IS NULL,
  rowcount==1 asserted per row). Pre-state archived (repair_b_prestate.json).
- Deliberately NOT touched: the two glmocr 'Specimen 2017' rows (no series exists for
  specimen sittings — honest NULL) and the 3 sprint-acceptance REJECTED audit rows.
- Post: 0 non-specimen NULL series remain across all 37 pdflane rows.

## Repair A+HOLD — 4CH1/1CR + 4CH1/2CR June 2024 REPLACE drive

- Defect: glmocr-era ep rows (09-14) cross-spec mislinked — paper_code says 4CH1/1CR
  and 4CH1/2CR (new spec) but QP+MS pointers targeted 4CH0 old-spec regional documents
  (corpus/igcse-chemistry-4ch0-1c-2024junr / 4ch0-2c-2024junr), and the 19 bank
  questions were 4CH0 content (all active=FALSE, serving-inert). The genuine 4CH1
  202406 docs sat orphaned from any ep row.
- Fresh parse first (parser main 55166af, g1.7 closure grammar + G6 identity gate):
  4ch1-1cr-202406 = 12q/110 marks marksVerified=true PASS (one expected
  IDENTITY-SESSION-DRIFT flag: printed date 2024-05-17 vs claimed June 2024 — the
  Pearson coded-date convention, pairing confirmed in the corpus manifest ops_log);
  4ch1-2cr-202406 = 7q/70 marks marksVerified=true PASS, zero flags. Corpus bytes
  sha-verified against manifests (aacf1223/446ef673/c6edac24/cbeeacd0).
- Drive (hold_drive.py, fail-closed):
  1. Guards: attempts=0 answers=0 human_marks=0 smart_mark_results=0
     agreement_evals=0 on all 19 questions/111 parts (FK NO ACTION backstop).
  2. Archive: 19 q + 19 qv + 111 parts + 57 mp + 17 ms + 2 glmocr bridge records +
     the 2 ep rows -> hold_drive_prestate_archive.json (full recovery).
  3. Delete FK-safe single transaction: mark_points(57) -> spec_points/topics/options(0)
     -> bridges(2) -> questions(19, cascade qv/parts/schemes) -> exam_papers(2).
  4. POST /api/v1/teacher/content/past-papers (201, minted 10-min admin JWT):
     4CH1/1CR -> paperId 29bba2da (12 q / 70 parts / 57 mp, SUGGESTED);
     4CH1/2CR -> paperId 0f903acf (7 q / 48 parts / 38 mp, SUGGESTED).
     Drafts built by the audited converter (atoms_to_draft, identity pinned to the
     EXISTING genuine documents — QP afa9a7e7/82d5aeca, MS 4c3c9759/123e0bf0).
  5. series/year backfill JUN/2024 on the 2 new rows (same draft-path gap as Repair B).
- Post-gates (verify_final.json, ALL PASS):
  - ep pointers resolve to the correct genuine docs; extraction_method
    pdflane-atoms-draft-v1; validation SUGGESTED; series/year JUN/2024.
  - Bank: 12q/110 marks and 7q/70 marks — equal to the closure-verified atoms totals.
  - 4CH0 mislinks on 4CH1 rows: 0. Old row ids absent.
  - Serving: all 4 referenced docs fully embedded (51/51 chunks), chunk mirrors exact
    (paper_code 4CH1/1CR|4CH1/2CR, series JUN, year 2024, embed_rev=2 = current rev).
- Global census after both repairs: exam_papers 104 (80 SUGGESTED / 13 REJECTED /
  11 VALIDATED — unchanged totals); documents 999; chunks 4,343; questions +0 net
  (19 wrong removed, 19 correct created); mark_schemes +2 net (19 fresh schemes for
  17 archived: one scheme per question).

## Files

- `repair_b_prestate.json` — the 12 rows before the series/year backfill
- `hold_drive_prestate_archive.json` — full JSON archive of every deleted row
- `draft_4ch1-1cr-202406.json` / `draft_4ch1-2cr-202406.json` — the POSTed drafts
- `post_results.json` — API ingestion summaries (paperIds, counts)
- `verify_final.json` — post-gate verification (read-only probe output)
- `SHA256SUMS` — integrity manifest of this pack

## Standing items unchanged

PAT/credential rotation; ENU-STRUCT-1.32 exogenous drift; R4 active-policy; the
SKIP-flagged 4CH1/2C January 2021 supersession (teacher-VALIDATED rows + learner
activity — operator decision owed, version-bump path or re-validation flow).
