# G1.2 grammar pack + the-77 re-gate + first bank backfill drive (2026-09-24)

Lane: mark-closure (Task 38's "G1.2 grammar pack" next-step, executed as
Session 118). Operator directive: "proceed with implement the G1.2 grammar pack
(RC-A…RC-F + fixture tests), then re-gate the 77 and drive the bank backfill".
Iron rule honored: every number re-derived from first-hand sources (parser repo
@7208118 local build, Past-Papers git tree + blob-verified downloads, fresh
prod DB probes, records gate report @67c8beb as baseline).

## 1. Parser: G1.2 grammar pack (7208118, pushed to parser main)

Six rules, each pinned to corpus evidence from the Task-38 taxonomy
(`mc_taxonomy.json`, 6-paper stratified sample, all shapes reproduced from
pdftotext -layout text):

- **RC-A (2012+ table grids):** `is_grid_page` recognizes the
  `Expected Answer / Accept / Reject / Marks` header family — pages that were
  skipped whole as furniture (4CH0 2C Jan 2012 q1 captured 1/10 marks; 201401
  q3/q10 zero capture) now parse. Opener-only rows (`1 (a)`) open part blocks;
  lone marks cells fill aggregate openers (backward), defer to the next opener
  row (forward, 4CH1 2C Jun 2021 q3 `2` above `(iii)`), or open deferred
  points above plain answer rows (201201 q1 (c) `1` above `= 79.99`).
- **RC-B (guidance-vs-point):** marks-column discipline — a trailing digit far
  left of the established marks column is table data, never marks (kills the
  fraction-row `1 1 3` +3 phantom; 201106 q5 12→10, now fully closes). Zero
  value tails (`400 000`) rejected. Note-led point text (answer column empty at
  the marks row, note text supplied the "text") moves to notes.
- **RC-C (QP sub-part segmentation):** standalone `(ii)`/`(iii)` sub openers
  (empty rest) parse — 4CH0 1C Jun 2011 q2 parts 4→6 matching MS 6/6; part
  opener text printed BEFORE the question-number block (PyMuPDF column order)
  is buffered same-page and routed into the new atom (201201 q1 part (a)
  recovered).
- **RC-D (label truncation):** `(v)`/`(i)`/`(x)` roman tokens no longer claimed
  as part letters (4CH1 1C Jun 2024 q2 (a)(v) UNKNOWN-PART).
- **RC-E (point-row loss):** displaced merged cells above openers fill them;
  tail-less M/A rows under a deferred-cell opener absorb as marking STEPS
  (202106 q3 (iii) closes 10/10).
- **RC-F (total-row crash):** `build_qp_atoms` mirrors `parse_qp`'s orphan-total
  tolerance — no hard abort on rasterized opener pages (4CH1 1C Jun 2019 p1/2/4/
  12/16/18/20/26 carry no text layer; blob-verified against the current
  Past-Papers HEAD). Orphan stubs surface as `QP-OPENER-UNSEEN` review rows and
  are excluded from the product; crosscheck parity via `orphan_events`.

Fixture tests: `tests_g12_grammar_pack.py` (13 evidence-cited fixtures).
Suite: **127 passed, 1 skipped** (114 legacy + 13 new; legacy G1 phantom-point
guard still green).

## 2. Sample validation (6 papers, before→after vs the A1 gate report)

- 4ch0-1c-201106: 4 flagged questions → 1 (q8 letter-level only; sum 17→18).
- 4ch0-2c-201201: 5 → 1; q1 sum 9→10 with parts recovered; MS-PART-NO-POINTS
  cleared; no gained flags after the part-opener buffer.
- 4ch0-1c-201401: MS-QUESTION-MISSING + MS-POINT-UNKNOWN-PART cleared.
- 4ch1-1c-201906: RUN-FAILED (EmitError) → parses (8 real atoms + 6 disclosed
  orphan stubs; the sandbox's earlier 10-q/110-mk product is not reproducible —
  the source PDF's raster pages are a source defect, not a grammar one).
- 4ch1-2c-202106: q3/q5 now close; q6/q7 retain ±1–2 residuals (disclosed).
- 4ch1-1c-202406: VERIFIED (flags cleared + marksVerified=true).

## 3. Re-gate of THE 77 (67 parsed / 10 unmappable)

`g12_gate_report.json`: blob-verified QP+MS downloads from the Past-Papers
repo (git blob SHA check on every file), per-paper run + flags.

- **67/77 parsed, 0 RUN-FAILED** (the RC-F crash fix holds corpus-wide).
- **2 VERIFIED** (marksVerified=true, zero flags): `4ch1-2c-202406`,
  `4ch1-2cr-202006` — the bank-backfill-eligible set.
- **65 ESCALATED** (flags remain — honest HOLD; glmocr rows stay).
- **10 PDF-MAPPING-AMBIGUOUS**: Nov 2020 1C + Nov 2023/2024 + 2025 sessions —
  these papers' PDFs are NOT in the Past-Papers repo under any matching name
  (verified against the full tree listing); they exist only in the A1 sandbox's
  corpus store, which is not accessible from this environment. HOLD, disclosed.
- Flag-type deltas over the 67 (old→new): MS-POINT-UNKNOWN-PART 34→10,
  MS-QUESTION-MISSING 17→6, PRINTED-TOTAL-DISCREPANCY-QP-VS-MS 16→2,
  MS-PART-NO-POINTS 58→44, MS-POINTS-DONT-CLOSE 43→38, PART-MARKS-MISMATCH
  65→60. 41/67 papers had at least one flag type cleared. Residual long tail =
  per-letter PART-MARKS-MISMATCH (RC-C QP-side sub-part arithmetic) + the
  2021-style step-block shapes (202106 q6/q7 ±1–2) — next iteration's scope.

## 4. Bank backfill drive (2 VERIFIED papers, sanctioned A1 pattern)

`g12_drive_report.json`. Pattern: archive → guarded delete → POST
`/api/v1/teacher/content/past-papers` (201). Auth: 10-min ADMIN/TEACHER JWT
from the LIVE Render env SYLLABAI_JWT_SECRET (render_token path). Prestate
asserts on both papers: attempts=0, smart_mark_results=0,
smart_mark_agreement_evaluations=0, validated_versions=0 — **zero
teacher-validated rows destroyed**.

| slug | action | old rows (archived) | POST | new paper | counts_match_draft |
|---|---|---|---|---|---|
| 4ch1-2c-202406 | REPLACE | 1 ep / 7 q / 45 parts / 30 mp / 1 bridge | 201 | 9a462279, SUGGESTED, 7 q / 37 mp | true |
| 4ch1-2cr-202006 | REPLACE | 1 ep / 7 q / 29 parts / 15 mp / 1 bridge | 201 | d3d7e0f2, SUGGESTED, 7 q / 35 mp | true |

- Per-question mark arithmetic vs atoms: EXACT for both (bank [5,7,10,10,11,13,
  14]=70 and [5,7,8,10,11,13,16]=70, byte-equal to the verified atoms).
- `extraction_method = pdflane-atoms-draft-v1` on all 14 versions; all rows
  SUGGESTED (reviewRequired=true by construction).
- Doc pointers carried over from the archived rows (9ab00b14/1beecbbf,
  2ad68057/d110adef). **These pointers are DEAD in `documents` (0 rows) —
  pre-existing hygiene from the 2026-09-14 glmocr rows, preserved as-is; the
  docs themselves were never touched by this lane.** The A1 lane's "13
  pre-existing dead MS pointers" note covers this class of defect.
- Archives: `g12_bank_archive/<slug>/archive.json` + SHA256SUMS (full row
  export incl. glm_ocr_bridge_records; drafts alongside as
  `past-paper-draft.json`).
- 202406 drive note: the first invocation committed archive+delete then crashed
  on a fetch-after-delete bug; the second invocation resumed via the archive
  (doc ids recovered from the archive) and POSTed — the delete and POST of the
  SAME paper were verified end-state-clean (poststate 0 rows, then exactly the
  draft's rows).
- mp count nuance (2cr): POST body reported markPoints 36 (draft points), bank
  holds 35 scoped rows — the converter's marks=0-alternative merge rule makes
  the draft point count an upper bound of stored rows; counts_match_draft is
  asserted on QUESTIONS (7=7), the A1 gate convention.
- Bank totals: 1454 q / 4466 mp / 95 ep (net: 2×REPLACE, no NEW papers).

## 5. Not done / honest limits

- The other 63 ESCALATED papers keep their glmocr rows (marksVerified=false
  state unchanged) — closure work continues (RC-C letter-level arithmetic is
  the dominant residual).
- The 10 unmappable slugs need the corpus-store PDFs (or a Past-Papers repo
  upload) before they can re-gate.
- 4ch1-1c-201706 GAINED an MS-QUESTION-MISSING flag — a previously-silent loss
  now disclosed by the stricter walk; treated as honest, not a regression to
  suppress.
- Serving soak / embedding refresh for the 2 papers not run this session (the
  bank questions are fully self-contained for serving; embed runs are the
  embed-lane's cadence, as in G1/A1).
