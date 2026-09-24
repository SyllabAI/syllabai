# G1.3 — RC-C Letter-Level Residual: Grammar Fixes, Re-Gate, Bank Backfill

- **Date**: 2026-09-24
- **Lane**: mark-closure (Session 121)
- **Parser**: syllabai-parser main `ae8aee0` (on top of G1.2 `7208118`)
- **Trigger**: user instruction "proceed with RC-C" — the Task-39 NEXT item:
  "RC-C letter-level residual (PART-MARKS-MISMATCH 60 papers — QP sub-part
  mark arithmetic vs MS letter sums)"
- **Iron rule**: every number below re-derived from first-hand sources (local
  parser build, cached corpus layouts, fresh prod DB probes); no summary
  trusted.

## 1. Diagnosis (rcc1_drill.json)

Re-derived the emit_atoms letter-level comparison (PART-MARKS-MISMATCH sites,
emit_atoms.py:766-824/857-863) from the G1.2 re-gate cache over the 60
ESCALATED papers carrying the flag: **154 flagged questions**, classified:

| shape | count | meaning |
|---|---|---|
| QP-EXTRA-SUB | 83 | MS letter owns fewer sub-parts than the QP prints |
| LETTER-SUM-DIFF | 51 | same sub structure, letter sums disagree |
| SUB-MARKS-DIFF | 31 | common letter+sub, marks disagree |
| QP-MISSING-SUB | 24 | MS letter owns sub-parts the QP lacks |
| QP-INTERNAL | 3 | QP leaf sum != printed total while MS closes |

Ground truth was pinned on raw pdftotext layouts (not product shapes):

1. **4ch0-1c-201206 q6(c)(i)** — M2's marks cell is the accept-column text
   `12` ("carbon-12 has a mass of / 12 / which is 12"); the real `1` is a
   merged cell printed on the `mass of isotopes` continuation line.
   G1.2 produced phantom P2 ("on a scale where", 1 mark) + M2=12.
   Geometry: true marks column 117-118; bleed at col 65.
2. **4ch1-1c-202001 q4** — sub-part openers `4 (a) (i)   3` and `(ii)   3`
   (marks on the opener line, empty answer body, table/step rows below)
   matched NO regex: whole sub-parts lost (MS sum 3 vs printed 9).
3. **4ch1-1c-202001 q5(e)(i)** — `19` in the example-calculation table
   (fluorine's relative atomic mass) read as a marks cell (M1=19; MS sum 34
   vs printed 14).
4. **4ch1-1c-202106 q7(b)(ii)** — `7   (ii)   • content   2` (question number
   + solo sub-part + content + marks) matched nothing.
5. **4ch1-1c-202106 q6(b)(ii)** — page 13 carries ONLY the MCQ answer row
   `(ii)   D yellow   1` + incorrect-option notes: no [MA] token, no total
   row, no grid header → G1 furniture-page skip dropped the whole page.

## 2. Parser fix (ae8aee0, +147/−4 in parse_ms.py, +8 fixtures)

- **OPENER_MARKS_*_RE (4 regexes)**: empty-body opener rows whose only
  content is the marks cell → aggregate point with the column-disciplined
  tail as marks; `_from_deferred` step absorption; solo-sub shapes require
  an open part context (RC-D `(v)` legacy fallback preserved — guarded by
  the pre-existing `test_paren_v_without_part_context_stays_part`).
- **Bug A**: legacy unguarded wrapped-marks recovery (line ~880) now applies
  the same MARKS_CELL_MAX cap + marks-column discipline as the G1.2
  disciplined copy — accept-text digits can no longer poison tail-less
  M-rows.
- **Bug B**: deferred merged-cell spawn redirects to `pending_marks_next`
  when a complete M/A-labeled row starts within the 3-line lookahead window
  (`_labeled_row_ahead`); note-wrap-only chains (Jan 2012 q1(b)(ii)
  "proton number 1") keep the legacy deferred-point spawn.
- **Question-boundary pending expiry**: `pending_marks_next` expires in
  `ensure_question` — q5's displaced cell (intended row absorbed as prose)
  no longer leaks into q6's first provisional (latent G1.2 defect EXPOSED by
  this iteration's OM recovery on 4ch1-1c-202006; root-caused via bisect +
  traced G1.2 replay before fixing).
- **is_grid_page**: a page with an opener-shaped row carrying a trailing
  marks digit is grid content (MCQ continuation pages no longer skipped).

Tests: `tests_rcc_residual.py` 8 fixtures, every one replicating a corpus
evidence shape. Suite: **129 tests / 1 pre-existing skip / 0 failures**.
6-paper sample re-run: no flag regressions; 4ch0-2c-201201 fully CLEARED.

## 3. Re-gate the 60 (g13_gate_report.json)

60/60 parsed, **0 regressions** (no new flag types on any paper):

- **11 newly VERIFIED** (all flags cleared): 4ch0-2c-201201,
  4ch0-2c-201606, 4ch1-1c-202201, 4ch1-1c-202306, 4ch1-1cr-202301,
  4ch1-2c-202006, 4ch1-2c-202101*, 4ch1-2c-202206, 4ch1-2c-202306,
  4ch1-2cr-202001*, 4ch1-2cr-202206  (*the two asterisked are
  teacher-VALIDATED in the bank — see §4)
- 16 improved-not-cleared, 33 unchanged
- flag deltas (papers): PART-MARKS-MISMATCH 60→42, MS-PART-NO-POINTS 40→31,
  MS-POINTS-DONT-CLOSE 36→25, MS-POINT-UNKNOWN-PART 9→7, MS-QUESTION-MISSING 5→4

Corpus-wide VERIFIED count (of the original 77): 2 (Task 39) + 11 = 13.

## 4. Bank backfill (g13_drive_report.json, g13_cgate_report.json)

Sanctioned A1/G7/G1.2 supersession pattern; idempotency probe added after
the first invocation's POST landed server-side while its response timed out
(crash pattern previously seen at Task 39 — probe, never blind re-POST).

- **7 REPLACE** (archive → guarded delete with prestate asserts
  attempts=0/smart_mark=0/agreement=0/validated=0 → POST 201):
  4ch0-2c-201201, 4ch0-2c-201606, 4ch1-1c-202201, 4ch1-1c-202306,
  4ch1-1cr-202301, 4ch1-2c-202006, 4ch1-2c-202306
- **2 NEW** (no exam_papers row; live doc ids resolved from documents by
  source_uri `<SLUG>/qp.pdf|ms.pdf`): 4ch1-2c-202206, 4ch1-2cr-202206
- **2 SKIPPED fail-closed**: 4ch1-2c-202101 (January 2021) and
  4ch1-2cr-202001 (January 2020) carry teacher-VALIDATED glmocr rows — the
  zero-teacher-validated-rows-destroyed convention excludes them from
  supersession until a review flow exists.
- All 9 ingests: `counts_match_draft=true`, version states all SUGGESTED,
  extraction_method=pdflane-atoms-draft-v1.

C-gates: 9/9 per-paper mark arithmetic **bank=draft=atoms multiset EXACT**
(60/60/110/110/110/70/70/70/70); validated rows across all archives = 0;
the 2 VALIDATED papers verified untouched (VALIDATED + glmocr provenance).

Bank totals: 1,454 → **1,468 questions** / 4,466 → **4,635 mark points** /
95 → **97 exam_papers**; pdflane-atoms-draft-v1 provenance now 126 versions
(was 112 after Task 39).

Disclosures: (a) archived exam_papers doc pointers remain DEAD in documents
for the 7 REPLACE papers (pre-existing glmocr-era hygiene, disclosed at Task
39; the 2 NEW papers carry LIVE pointers); (b) mp nuance from the
marks=0-merge converter rule persists (e.g. POST said N, bank N-1 on some
papers — counts_match_draft asserted on questions per A1 convention);
(c) embed refresh for the 9 landed papers NOT run this session (embed-lane
cadence); (d) serving soak not run this session.

## 5. Artifacts

- `g13_gate_report.json` — 60-paper re-gate vs G1.2 baseline
- `rcc1_drill.json` — 154-question diagnosis + classification
- `g13_drive_report.json` — 9 drives with prestate/poststate + 2 disclosures
- `g13_cgate_report.json` — arithmetic/provenance/untouched gates
- `drafts/` — the 9 past-paper drafts (SHA256SUMS covers all files)
- Parser: `ae8aee0` (pushed, main); tests `tests_rcc_residual.py`
