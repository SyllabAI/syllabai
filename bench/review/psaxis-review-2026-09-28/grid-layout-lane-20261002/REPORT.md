# GRID-LAYOUT LANE — ENGINE-GRADE GRAMMAR v2 + 24-QV SCHEME FILL (2026-10-02)

**Authorization:** operator IM trace `1a0f8fb15fc9ea49` — "engine-grade grid-layout
lane" — the named Remaining-open item of the three-lane closeout (structural parse
residue ~26 qv, 2015–2019 mark-grid layouts) as sharpened by the bank-defect lane
closeout (3 echo-pinned qv). Task record: `.syllabai/tasks/T-C45.yaml` (claimed
first at master `9ee3b3b0c`, base `8a3c9eb48`).

## 0. Protocol ② finding — an unrecorded concurrent fill was verified, not duplicated

The live-DB state check caught drift vs `census_bundle_bankdefect_20261002.json`:
**+17 mark_schemes / +86 mark_points** (all SUGGESTED, method
`ms-print-gated-extraction-v2`, single timestamp 2026-10-01T20:25:20.505251Z — one
transaction) **and 3 marks repairs** (1CR-2016 Q9 1→13, Q11 1→15, 2CR-2016 Q6 1→8 —
exactly the echo-pinned trio) **with no records anywhere**: no evidence pack, no
TODO entry, no WORKLOG session, no task yaml, no parser-repo push (main was at
`55166afb2`, 2026-09-25; branch scan found no v2 grammar).

Per the fail-closed rule the fill was **verified first-hand, not re-executed**:

- **sha identity**: every source MS re-downloaded from `SyllabAI/Past-Papers` and
  sha256-matched to `documents.checksum` (24/24 PDFs OK — see `SHA256SUMS` inputs).
- **variant attribution**: the 17 schemes' `source_document_id`s resolve to the
  variant-correct MS docs (1CR-2016 → doc `b27f9358` = sha `cfe40a1b…` 28 pp;
  2CR-2016 → `9fcd9d72` = sha `95ede68d…`; reg qv → reg docs) — all 17 correct.
- **arithmetic**: 17/17 per-scheme point sums == qv.marks.
- **fidelity**: 75/86 point texts strict verbatim (normalized containment, wrap-
  tolerant) in the printed MS text; **11/86 row-boundary merge artifacts** — all
  11 with **zero fabrication** (every token present in the print; classification
  capture in the verify session), e.g. guidance-cell merges ('ionic Ignore
  electron transfer') and symbol verbalizations. All rows are SUGGESTED (never
  serve); the artifacts are recorded here for the teacher lane, not mutated.
- **marks repairs**: 3/3 == printed QP echo (`pdftotext -layout`,
  `Total for Question N = M marks`), re-derived first-hand.

The 17 fills covered the 2016 R-variant grids, 1C-2015 Q9, 1C-2017 Q1, 1C/1CR-2019
and 1CR-2022 Q11 — leaving **26 zero-scheme qv** as this lane's execution targets.

## 1. Engine work — pdflane parse_ms G2 grammar (syllabai-parser `5643689`)

Fresh `pdftotext -layout` re-extraction of the 12 affected MS papers (the lane
ground truth) showed the **v1 engine already closed 20/26 targets** on clean
pages (laneB's weaker results had used the ingested pages). The remaining gaps
were diagnosed line-by-line into three layout classes and fixed in
`tools/pdflane/parse_ms.py` (commit `5643689`, fixture tests `tests_g2_grid_layout.py`,
full pdflane suite **85/85 green**):

- **G2.4** — a bare M/A label row carrying its marks tail AND answer body on the
  SAME line is a complete row, never a split label. The pending machinery
  previously swallowed it and the next non-digit line silently discarded it
  (evidence: 2CR-2016 q1(a) 'A (the crystal dissolves) 1', q3(b) 'A (argon) 1';
  1C-2015 q7(a)/(b) '(addition)' / '(a molecule used to make a polymer)').
  Column-discipline rejection keeps the legacy pending path.
- **G2.5** — a bare column-0 part lead with content is grid content: short
  continuation pages holding ONLY such rows (no [MA] token, no total, no header)
  were furniture-skipped whole (evidence: 1C-2015 q11(c) 'c ∆H … 1' p29; 1CR-2016
  q10 p20). Empirical scan of the 12 lane papers: **exactly one page flips**.
- **G2.6** — regional-variant bold rendering duplicates the part letter in the
  label position ('bb'), normalized length-preservingly (evidence: 2CR-2016 q1(b)).

Post-G2 target table: **24/26 FILL-OK** (was 20), 1 NEW-DEFECT candidate, 1 residue.

## 2. The fill — one fail-closed tx, 24 schemes / 164 points

Targets: the 26 zero-scheme qv. Gates per entry (all 24 pass):
`v3 sum == printed QP echo == live qv.marks` (7 qv carry laneD-corrected marks —
the stale laneB bank values are NOT used), variant-pinned source doc, no existing
scheme, attribution check 24/24, plan pinned pre-write.

- Plan: `gridlane_plan.json` sha `aa38b698c47a7ff86bb292772987331ce8d4f486b678f05dc63ea05bcfe03868`
  (24 entries / 164 points / 233 marks; method `ms-print-gated-extraction-v3`,
  engine = pdflane G2 `5643689`).
- Pre-asserts (fresh conn): qsp 2637 · qt 1725 · schemes 1485 · mp 5738 ·
  audit 4048 · tve 0 — ALL OK; 24/24 qv marks + no-scheme checks OK.
- Apply (`gridlane_apply.py --commit`): one tx, uuid4 ids, in-tx per-entry sum
  checks, in-tx post-asserts — schemes **1509** (1360V + 149S), mp **5902**,
  SUGGESTED 149, qsp/qt/audit/tve unchanged. **[COMMITTED]**.
- Independent fresh-conn verify (`gridlane_verify_fill.py`): **24/24 entries
  clean** (counts, sums, verbatim byte-match, doc, state), residues untouched,
  census re-measured.
- Fidelity: **157/164** point texts strict verbatim in the printed MS; **7/164
  row-boundary merge artifacts, all zero-fabrication** (token-level assertion),
  recorded per-point in the plan (`containment` field). House shape: SUGGESTED,
  version_label '1', part links/acceptance NULL, confidence 1.0.

Sparse recount in the lane universe: **26 → 2** (`census_bundle_gridlayout_20261002.json`,
drift NONE).

## 3. Dispositions

- **NEW-DEFECT candidate (documented, NOT repaired)**: `q03-51fea326` — 4CH0/2C
  January 2013 Q3, bank **1** vs double-evidenced printed total **8** (v3 rows sum
  8 == QP echo 8). Task-66-TX-B class; the three-lane closeout reserved this
  class for its own operator mandate and no prior lane classified this ref —
  the marks repair is left to the operator.
- **Structural residue (1 qv)**: `q10-5273dfa3` — 4CH0/1CR June 2016 Q10, bank 15,
  v3 sum **13** (G2.5 recovered b/c rows, +3). The remaining 2 marks sit in
  a(ii)'s OR-route fraction block ('0.38(4) × 1000 / 50' stacked lines, M1/M2
  marks cells displaced) — documented with page evidence for the next grammar
  iteration.
- **Corpus-side honest note**: `review_schedules` grew 120 → 154 between census
  reads (app-side scheduling activity, not a lane surface); recorded in the census
  bundle. V57 remains deploy-held (knowledge_nodes 492 / ING 57 pre-deploy).

## 4. Files

`REPORT.md` (this file) · `VERIFY_OUTPUTS.md` (verbatim session captures) ·
`gridlane_plan.json` (24 classified entries with per-point provenance) ·
`census_bundle_gridlayout_20261002.json` · `SHA256SUMS`.
Scripts (session workspace): `gridlane_db.py`, `gridlane_census_probe.py`,
`gridlane_drift_probe.py`, `gridlane_marks_diff.py`, `gridlane_docs_bysha.py`,
`gridlane_fetch_pdfs.py`, `gridlane_dump_writes.py`, `gridlane_verify_writes.py`,
`gridlane_classify_miss.py`, `gridlane_baseline.py`, `gridlane_target_table.py`,
`gridlane_build_plan.py`, `gridlane_apply.py`, `gridlane_verify_fill.py`,
`gridlane_census_final.py` — SELECT-only except the one fail-closed apply tx.
Engine: syllabai-parser `5643689` (parse_ms G2 + `tests_g2_grid_layout.py`, 8 tests).

## 5. Remaining open

- New-defect marks repair for `q03-51fea326` (2C Jan 2013 Q3, 1 vs 8) — operator
  mandate; the double evidence is pinned in `gridlane_plan.json`.
- 1CR-2016 Q10 a(ii) OR-route fraction block (2 marks) — next grammar iteration.
- §C children VALIDATE_ALL; sibling supersession sign-offs; post-deploy census
  re-pin (V57 → kn 435); F-PROD-1 teacher review of the 25 REVIEW_REQUIRED papers.
- The 11+7 row-boundary merge artifacts across the v2/v3 fills are SUGGESTED-state;
  the teacher validation lane can refine their texts at review time.
