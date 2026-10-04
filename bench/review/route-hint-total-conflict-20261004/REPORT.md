# Route-hint lane — the Total-row-conflict rule (2026-10-04)

**Status:** EXECUTED — the T-C80 Lane-B recorded-NOT-fixed finding is resolved
at engine grade: parser main `c507ff1` (G5), suite 210 OK, 16-session 4CH0
corpus regression single-diff = the mandate (June-2017 2C q5 19 → 15). Zero
production writes; the bank-impact probe proves the artifact never reached the
bank (0 rows read 19; census == the post-V61 pins exactly).
**Authority:** operator trace `1a106bb9581f530d` ("Proceed with new route-hint
finding") — the finding T-C80 recorded NOT fixed (REPORT.md of
`fprod1-narrowed-closure-20261004` §"Lane finding recorded, NOT fixed (out of
mandate): the route-hint class"; claim `dd60112`, DONE `ab0670f`): "rejecting
the hint happens to produce 15, but for the wrong reason; distinguishing
hint-vs-cell needs the Total-row-conflict rule — its own designed change with
its own fixtures. Recorded here for that lane."
Records: T-C82 (claim `46d60f1`, Session 195).

## Print archaeology FIRST — the T-C80 framing re-adjudicated

The T-C80 report worked from regression diffs and framed the June-2017 `Route
1:   4` line as a "route-scoring HINT". This lane read the verbatim prints
first (fail-closed doctrine: classify from the prints, never from the diff):

- **4CH0/2C June 2017 q5(c)** (print `6204523f…`, page 18): `Route 1:` with
  the block's merged cell `4`, M1/M2 (route 1), `Route 2:`, M1/M2
  (alternative), M3, M4, then the block footer `Total    15`. The QP prints
  `(Total for Question 5 = 15 marks)`. **The `4` is a REAL cell** — 5(c) is
  worth 4 marks (M1+M2 via either route, M3, M4).
- **4CH0/2C Jan 2017 q6(b)** (print `d4690be6…`, page 11): `Route 1:` with the
  block's cell `4`, no Total row in the block (q6's footer `Total 13` prints
  after 6(c); QP 13 = 4 + 9). Same shape, same real-cell semantics.
- **The actual mint** (page 16 of the June MS): a standalone
  `Alternative Method` line opens a full-page OR-route REPRINT of q5(b)(ii) —
  the same part, the same M1–M4 structure, the SAME printed cell `4`. The
  G3/G4 parser counted it as an additional 4-mark point → q5 raw sum
  2+1+2+4+**4**+2+4 = **19** vs printed Total 15 / QP 15.
- "Rejecting the hint happens to produce 15, but for the wrong reason"
  (T-C80) is now print-explained: rejecting 5(c)'s REAL cell lands 11 + 4
  (the reprint still double-counted b(ii)) — the right total, wrong
  semantics: 5(c) marked 0 and the duplicate kept.

## The G5 grammar round (parser main `c507ff1`)

Two composed mechanisms, fail-closed at every gate:

1. **`Alternative Method` page divider** (`ALT_METHOD_PAGE_RE`, full-line
   title-case form only — the observed print): points minted from the divider
   line to the page end carry `_alt_method_reprint`. The tag alone is inert.
   The divider line is recorded in the unclassified trail with its own reason
   (`alternative-method-page-divider`) — the accounting trail is preserved.
2. **Total-row-conflict reconciliation** (fires at the single site where a
   question's printed total row is set): demote the tagged points ONLY when
   (a) the over-sum EXACTLY equals the tagged points' marks sum, (b) each
   tagged point has EXACTLY ONE earlier untagged twin in the same question
   with identical (part, sub) AND marks, (c) twins are pairwise distinct and
   no tagged point is a capped-group member. Any gate failure keeps the
   legacy fail-closed behavior (the arithmetic disagreement stays disclosed
   via `arithmetic_ok`). Demoted rows' text is preserved verbatim as question
   guidance and the receipt is recorded in the question dict
   (`_total_row_conflict`: total_row, raw_sum, demoted[], page).

## Fixtures and verification

- `tools/pdflane/tests_g5_route_hint.py` — 9 tests from the VERBATIM pages:
  the June-2017 q5 pages 14–18 (incl. the divider page) with the receipt
  asserted field-by-field; zero-loss guidance preservation; the divider's
  accounting trail; the no-divider baseline (sums exactly 15 — the artifact
  NEEDS the reprint); the Jan-2017 6(b) negative case (route cell REAL,
  q6 closes 13); three gate-abort cases (over-sum not explained / no twin /
  twin marks mismatch — all inert).
- **Full pdflane suite: 210 tests (201 prior + 9), all green.** The suite's
  one pre-existing failure (`CorpusSmoke` ≥10 parsed products) fails
  IDENTICALLY on the G4 base `9c538ad` in this sandbox — it is a
  materialization artifact of the sparse corpus checkout (4 products on
  disk), not a code regression (base and G5 both: 1 failure).
- **16-session 4CH0 corpus regression** (40 variants, G4 `9c538ad` vs G5
  `c507ff1`, print substrate `7e027cad` — the 4CH0 chemistry subtree is
  byte-identical to the T-C80 substrate `1f7e8355`; `git diff` on that path
  is empty): **the ONLY diff is 2017-06/4CH0-2C q5: 19 → 15** — exactly the
  mandate. Jan-2017 q6 = 13 unchanged. The June-2017 paper now closes
  4/11/11/19/15 = **60 == `TOTAL FOR PAPER = 60 MARKS`** with every question
  == its QP print (`g5_receipt.json`).

## Bank impact (SELECT-ONLY probe, Render-PAT direct recipe)

- Serving lineage: all four 2017 2C QP/MS docs (June + January) checksum ==
  the corpus print pins (byte-identity, `bank_impact.json`).
- The June-2017 2C ep row (`0a94f411…`, subject 4CH1, paper_code 4CH0/2C)
  carries 5 INACTIVE questions from the legacy glm-ocr segmentation with
  schemes summing 10/11/12/10/12 — a different (older) pipeline; **no bank
  row reads 19 anywhere and no duplicate-(b)(ii) scheme exists**. The Jan-2017
  2C ep row (`21041891…`, subject 4CH0CHEMISTRY) reads q6 = 13 — correct.
- Census pins: exam_papers 108 · questions 1526 · question_versions 1526 ·
  mark_schemes 1504 · mark_points 5883 — the post-V61 baseline exactly; the
  flyway head at probe time = V61 (the T-C79 lane's V63 Pearson seed is not
  yet on the production migration head — disjoint from this lane's rows).
- **Verdict: the artifact is engine-level only; zero bank repair needed and
  zero production writes performed.** The G5 parse products are what future
  ingests of the print lineage will carry.

## Artifacts

- This dir: REPORT.md, `substrate_pins.json` (G6: computed == manifest sha256
  for all four prints), `g5_receipt.json` (q5 before/after + the conflict
  receipt + the paper closure), `regression_diffs.json`, `bank_impact.json`,
  scripts (`tc82_regression.py`, `tc82_bank_impact.py`, `tc82_evidence.py`),
  SHA256SUMS.
- syllabai-parser main `c507ff1` (G5 grammar + fixtures; commit history on
  branch feat/g5-total-row-conflict, fast-forwarded to main).
- Upstream records: T-C80 pack `fprod1-narrowed-closure-20261004/` (the
  recorded finding), T-C82 claim `46d60f1`.
