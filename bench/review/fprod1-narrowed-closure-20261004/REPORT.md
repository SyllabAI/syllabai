# F-PROD-1 narrowed-row closure + engine-grade grid-layout lane completion (2026-10-04)

**Status:** EXECUTED — the 3 narrowed P2 rows are CLOSED on engine-derived print
evidence; the grid-layout lane's two documented residues are resolved (one by
first-hand verification of found writes, one by the G4 grammar round). Zero
production writes this lane; production verified at the exact post-V61 census
state.
**Authority:** operator trace `1a10622b96c017d5` — names the Session 188
Remaining list verbatim minus the standing operator item: "the 3 narrowed
2016-family rows (MS prints no totals), the engine-grade grid-layout lane,".
Records: T-C80 (claim `dd60112`, Session 189). For `q03-51fea326` this word
supplies the mandate T-C45's disposition required.
**Print substrate:** `SyllabAI/syllabai-pastpapers` @ `1f7e8355`, chemistry
subtree. All 8 target PDFs' manifest sha256 pins verified OK (G6 discipline);
page-1 identity gates pass inside the parse runs (G6 identity gate).
**Access note (honesty):** no Neon session key exists in this sandbox (purged
post-lane per the V60 discipline). Production probes are SELECT-ONLY via the
M6-era Render-PAT direct recipe (service env-vars → pg8000; the
`m6_prod_verify.py` precedent). Zero writes outside Flyway — and this lane
needed none.

## Lane A — the 3 narrowed rows CLOSED (`qp-total-printed-ms-total-unprinted` → `ms-total-derived-agrees`)

The print pass narrowed 3 P2 identity rows because the June-2016 4CH0 MS docs
print NO totals at all (verified there by pdftotext + PyMuPDF + OCR; the G4
parse re-confirms: every question's `markScheme.totals.printed == null`). The
QP prints carry per-question totals and paper totals (120/120/60). This lane
completes the totals-agreement check by deriving the MS-side totals from the
printed mark cells with the engine-grade grid-layout parser (parse_ms @ G4,
`9c538ad`), then closing:

| row (bridge_id, question=paper) | verdict before | verdict after | evidence |
|---|---|---|---|
| 4CH0/1C June 2016 (`01097b1d`) | narrowed | **CLOSED `ms-total-derived-agrees`** | 16/16 questions: MS-derived sum == QP print; derived paper sum **120 == QP 120** |
| 4CH0/1CR June 2016 (`476be1f7`) | narrowed | **CLOSED `ms-total-derived-agrees`** | 12/12 questions verified (Q7 12 after the G4 fix); derived paper sum **120 == QP 120** |
| 4CH0/2CR June 2016 (`f3984d0a`) | narrowed | **CLOSED `ms-total-derived-agrees`** | 7/7 questions verified; derived paper sum **60 == QP 60** |

Honest tier naming: this is **weaker evidence than the printed-block-totals
tier** the print pass used for 14 P2 rows — the 2016 format prints no block
totals, so the sums derive from the per-point marks cells (each cell printed
on the page; the parse deterministic with page-provenance fixtures; any human
can re-verify a question in minutes). Every per-question derivation is in
`ms_derived_totals_g4.json`.

Corroboration beyond the parse: the serving-lineage checksums for all 6
June-2016 QP/MS docs EQUAL the corpus print pins (production probe D) — the
print evidence and the serving lineage are byte-identical; and all 35 banked
rows on the three papers read marks == QP printed per-question totals
(probe E; zero mismatches — the P3 print-pass result re-confirmed against
today's production).

With these 3 closures: **the 62 print-dependent rows stand at 55 print-closed
+ 4 repaired (V61) + 3 closed here = 62 — F-PROD-1's print debt is fully
discharged.** Worksheet v3 stays byte-frozen; this pack is the closure
receipt.

## Lane B — the engine-grade grid-layout lane

### B1 — the two T-C45 residues were already repaired by an unrecorded writer; verified first-hand, records completed (never re-executed)

Probe C found BOTH refs resolved in production, contradicting the recorded
T-C45 dispositions:

- `q03-51fea326` (4CH0/2C Jan 2013 Q3): bank **8** (T-C45 recorded bank 1),
  1 scheme / 8 points / sum 8.
- `q10-5273dfa3` (4CH0/1CR Jun 2016 Q10): bank **15**, 1 scheme / 8 points /
  sum 15 (the G3.3 fraction-stack recovery value).

Probe G forensics: both schemes carry `ms-print-gated-extraction-v4`,
`created_at = 2026-10-02T08:13:23.372489Z` (between the 10-01 20:25Z v2 drift
and T-C45's own fill census — the same anonymous-writer pattern Session 140
documented; the census arithmetic shows they landed inside the pre-state
T-C45 measured, which is why T-C45 still recorded them as sparse). Source
documents = the SERVING lineage docs, checksums equal to the corpus prints.
Verification (T-C45 standard): every point text matched against the G4 parse
of the same checksum-pinned prints (normalized containment, marks exact) —
**8/8 and 8/8 VERIFIED, sums == QP echo == qv.marks (8, 15)** —
`scheme_verify.json`. The production census equaled Session 188's post-V61
pins exactly at this lane's probe time (papers 91V/13R · qv 1526 =
1465V/59S/2R · schemes 1504 = 1360V/144S · mp 5883 · marks sums 11713 ·
bridge 10 OK + 49 SUPERSEDED) — no drift, nothing to re-execute (the
concurrent T-C75 W2 wave landed afterwards on a disjoint surface:
docs/chunks/exam_papers for the 2025-2026 papers, zero bank writes), and T-C45's two dispositions are now
closed as verified-found-writes with these records completing the missing
documentation.

### B2 — the G4 grammar round (the lane's engine deliverable)

The 1CR-2016 Q7 block exposed two composed layout artifacts, both fixed in
`parse_ms` (syllabai-parser main `9c538ad`):

- **G4.1** — a captured tail that completes a colon-chain of >=2 pairs
  (`2 : 4 : 1`) is ratio/table data, never a marks cell. The Q7 ratio's
  trailing `1` sat in the marks column and minted a phantom 1-mark point.
- **G4.2** — the printed words `allow alternative method` are an OR-route
  boundary: a lone marks cell PENDING at the boundary is assigned BACKWARD
  to the main route's last cell-less point, never to the alternative
  route's M1-restart rows (the pending `3` used to cross onto the
  alternative's M1).

Fixtures: `tests_g4_grid_layout.py` (5 tests) built from the VERBATIM
1CR-2016 q7 pages 12-13. Full pdflane suite **201 OK** (196 prior + 5).
16-session 4CH0 corpus regression vs G3 head `0fc5c32`: the ONLY diff is
1CR-2016 Q7 (13 → 12, the mandate — QP prints 12; the block prints
2+1+1+2+1+3+2 with f(i)'s single cell `3` for the main route).

### Lane finding recorded, NOT fixed (out of mandate): the route-hint class

The regression initially flagged two further diffs (both from an early,
broader G4.1 guard — narrowed after the prints adjudicated them):

- 4CH0/2C Jan 2017 Q6(b): `Route 1:   4` prints the BLOCK's cell (no Total
  row in the block; QP 13 = 4 + 9) — a broad guard broke a correct parse.
- 4CH0/2C June 2017 Q5(c): `Route 1:   4` is a route-scoring HINT (the block
  also prints `Total 15`; QP 15) — G3 head sums **19 vs QP 15**, a real
  G3-era artifact. Rejecting the hint happens to produce 15, but for the
  wrong reason; distinguishing hint-vs-cell needs the Total-row-conflict
  rule — its own designed change with its own fixtures. Recorded here for
  that lane; the early guard was narrowed so both papers parse exactly as
  G3 did.

## Artifacts

- This dir: REPORT.md, evidence JSONs (`substrate_pins.json`,
  `preflight_result.json`, `ms_derived_totals.json` (G3, kept for the
  fail-closed trail), `ms_derived_totals_g4.json`, `scheme_verify.json`,
  `regression_diffs.json`), scripts (`tc80_preflight.py`,
  `tc80_ms_totals.py`, `tc80_ms_debug.py`, `tc80_regression.py`,
  `tc80_scheme_verify.py`), SHA256SUMS.
- syllabai-parser main `9c538ad` (G4 grammar + fixtures).
- Upstream records: packet `762896b` · disposition `1835fd5` · ruling
  `d2befa9` · status lane `e3a566d` · print pass `2ffbbb3` · bank repair
  (V61, PR #79) · T-C80 claim `dd60112`.
