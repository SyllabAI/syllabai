# REPORT — T-C55: G3 grammar (col-0 scored leads + cell-less block residual) + the 2 sparse-qv scheme fills (2026-10-02)

**Authorization:** operator IM trace `1a0fb848d5b29681` — "Proceed with Remaining
opens: 1CR-2016 Q10 a(ii) (2 marks), scheme-fill mandates for the 2 sparse qv" —
the last two named Remaining-open items of the grid-layout lane (T-C45) /
ruling-v57 closeout (T-C49): the `q10-5273dfa3` structural residue ("needs an
engine-level fix or an operator ruling") and the explicit scheme-fill mandates
for `q03-51fea326` + `q10-5273dfa3` (the 2 sparse qv of the 26-qv grid lane
universe). Task record: `.syllabai/tasks/T-C55.yaml`.

## 0. The defect, root-caused first-hand (not "displaced" — ABSENT)

The T-C45 residue note said "M1/M2 marks cells displaced". Coordinate-level
re-verification (pymupdf words, x>700 = the marks column of `201606_ms_R.pdf`
sha `cfe40a1b…` == `documents b27f9358-bd57-5545-8c69-aeeb5cdbd476`) proves
something stronger: **the printed MS itself never prints the a(ii) marks
cell(s)** — page 19's marks column contains exactly ONE digit (a(i)'s `3` at
y=128.5); the whole a(ii) block (M1, M2, OR, M1, M2 rows) has none. The
2-mark value is nevertheless fully determined by printed evidence:

1. printed QP echo `(Total for Question 10 = 15 marks)` (sha `d5d0f929…`);
2. the seven sibling blocks' printed cells sum 13 (3+1+1+1+2+2+3);
3. residual 15 − 13 = **2** == the a(ii) main route's M1+M2 row count (the
   bare `OR` divider starts an ALTERNATIVE route for the same marks — its
   M1/M2 rows are never additional).

The operator's mandate states the same value: "1CR-2016 Q10 a(ii) (2 marks)".

## 1. Protocol ② — live-DB check caught real drift again (F-PROD-4, not corruption)

The T-C49 census pins had moved: qv_pool 1533→1526, schemes 1509→1502,
mark_points 5902→5867, qsp 2637→2620, qt 1725→1717, questions_active 961→954,
papers_rejected 14→13, audit_max 4048→4049. Root-caused from the audit trail:
**row 4049 — `wave2-prep-agent(Super Z)`, 2026-10-02T07:34:18Z, "F-PROD-4
governed removal: ingest-era shell (1 paper + 2 REJECTED docs + 7-question
SUGGESTED skeleton) removed under the operator wave-2-prep directive; full row
archive retained"** — deltas match exactly (−7 qv / −7 schemes / −35 points /
−17 qsp / −8 qt / −1 REJECTED paper), 0 orphan schemes (clean cascade). Both
lane targets untouched (q03-51fea326 8/8 VALIDATED 0 schemes; q10-5273dfa3
15/15 VALIDATED 0 schemes). The lane re-based every pin to the post-F-PROD-4
baseline and proceeded; nobody else's work was re-executed or undone.

## 2. Engine — pdflane parse_ms G3 grammar (syllabai-parser main `0fc5c32`)

A line-by-line trace of the G2 parse (debug harness over pages 19–20) pinned
the failure chain: (a) q10(b)'s column-0 lead `b   as the (hydrochloric)
acid/HCl is added` took the G1.3-r3 BANNER branch (no same-line cell) and
never became a point, so (b) its lone `1` cell BACKWARD-FILLED the previous
part's unresolved a(ii) OR-M2 row (b's mark stolen — the spurious 1), and (c)
q10(c)(i)'s lone cell spawned a deferred point inheriting **(a, ii)** instead
of (c, i) (the mislabel). Two mechanisms fix the class:

- **G3.1 — column-0 scored leads:** a col-0 bare part lead carrying answer
  content whose marks cell prints as a LONE line below it (before any labeled
  row; column-disciplined, value-capped, `_lone_cell_ahead` scan) now opens a
  provisional point so the backward fill assigns the cell to IT. Prose
  banners (`f   In part (f):`) keep the structural branch.
- **G3.3 — cell-less block residual recovery:** the end-of-parse merged-cell
  recovery generalized from one unresolved POINT to one cell-less BLOCK — a
  block with NO resolved row anywhere recovers `total − resolved_sum` on its
  opener when exactly one such block exists and the residual equals the
  block's MAIN-route row count (an M/A label-number restart inside the block
  — M1 after M2 — is the OR-route alternative signature; alternatives never
  add marks). Any gate failure keeps the legacy demotion (fail-closed).

**Verification:** `tests_g3_grid_layout.py` 6/6 (page-provenance cited);
full pdflane suite **196 OK** (190 pre-existing + 6 new); CI on `0fc5c32`
content-package-proof / conformance / build ALL success. **12-paper corpus
regression (24 baseline extractions × no-qp / with-qp), G2 vs G3 per-question
output diff: 13 diff sites, ALL individually justified** — 1CR-2016 Q10
(13→15 with-qp; the mandate; b/c(i) correctly attributed in both conditions),
1C Jan 2017 Q5 (16→17 with-qp — G3.3 recovered the unprinted `b(v) OH— /
HO—` cell; **QP echo 17 confirms G3 and convicts G2's 16**), and two
SUM-INVARIANT attribution improvements (1CR-2016 Q5 `c:'CQ on M1'`→`d:(real
answer)`; 4CH1 1CR-2019 Q4 `b(ii):'in either order'`→`c`-block). Zero
unexplained diffs; no q-by-q sum change anywhere else.

## 3. The fills — one fail-closed tx, 2 schemes / 16 points / 23 marks

Plan `g3_fill_plan.json` (file sha `2b7f433f39254934ad91b32d5611a8723d6d3c580b1a793702a0ff0effadb4ea`,
pinned pre-write): both entries gate `engine sum == printed QP echo == live
qv.marks` and carry **0 containment artifacts** (16/16 strict verbatim).

- `q03-51fea326` (4CH0/2C January 2013 Q3): 8 points × 1 mark (a(i) ×2, a(ii),
  b(i) ×2, b(ii), c(i), c(ii)) — sum 8 == echo 8 == the T-C49-repaired
  qv.marks 8. G2-equivalent parse (no G3 code path exercised; noted).
- `q10-5273dfa3` (4CH0/1CR June 2016 Q10): 8 points (a(i) 3, **a(ii) 2 — the
  recovered residual**, b 1, c(i) 1, c(ii) 1, d(i) 2, d(ii) 2, e 3) — sum 15
  == echo 15 == qv.marks 15, via `qp_totals`-gated G3.3.

Apply (`g3_apply_fill.py --commit`, one tx): pre-asserts re-based and ALL OK
(qsp 2620, qt 1717, schemes 1502, mp 5867, audit 4049, tve 0, qv_pool 1526,
questions_active 954); document resolution 2/2 MARK_SCHEME; per-entry qv
marks + no-scheme checks OK; in-tx per-entry sum checks 8/8 and 15/15;
in-tx post-asserts (schemes 1504, mp 5883, SUGGESTED 144, qsp/qt/audit/tve
unchanged) — **[COMMITTED]**. Fresh-connection verify: 2/2 schemes clean,
16/16 points byte-match + verbatim, doc shas `1e9c53b5…` / `cfe40a1b…`.
**Lane-universe sparse recount: 2 → 0.**

## 4. Census re-pin (census-last)

`census_bundle_g3_20261002.json` — 18 pins, **drift NONE**: qsp 2620, qt 1717,
schemes 1504 (1360V/144S), mp 5883, audit 4049, tve 0, qv_pool 1526,
questions_active 954, questions_total 1526, papers 90V/13R, docs
567V/305S/145R (the F-PROD-4 removals reflected), kn 435, edges 730, ING 0.
Closes the sparse-universe item; supersedes the T-C49-era "2 sparse qv" line.

## 5. Remaining open (updated)

- Secrets revocation: the operator-provided GH_PAT and RENDER_KEY were used
  env-only this session; revoke after reading the records.
- Corpus hygiene follow-up (non-urgent, laneD Finding 4): doc-folder
  mislabels vs byte identity, before the next ingestion wave trusts folder names.
- Teacher-lane note: the a(ii) scheme point carries the main-route text; the
  OR alternative + step rows live in the parse's demoted-notes (house shape,
  as in the 24 T-C45 fills). The 1CR-2016 Q5 / 1CR-2019 Q4 attribution
  improvements are recorded for any future re-parse of ALREADY-applied
  schemes; no applied row was mutated.

## Files

`REPORT.md` (this file) · `VERIFY_OUTPUTS.md` (verbatim session captures) ·
`g3_fill_plan.json` (2 entries, per-point provenance + containment) ·
`census_bundle_g3_20261002.json` · `SHA256SUMS`.
Scripts (session workspace, SELECT-only except the one fail-closed apply tx):
`g3_probe_20261002.py`, `g3_drift_investigate.py`, `g3_corpus_regression.py`,
`g3_build_fill_plan.py`, `g3_apply_fill.py`, `g3_verify_and_census.py`.
Engine: syllabai-parser `0fc5c32` (parse_ms G3.1 + G3.3 +
`tests_g3_grid_layout.py`, 6 tests).
