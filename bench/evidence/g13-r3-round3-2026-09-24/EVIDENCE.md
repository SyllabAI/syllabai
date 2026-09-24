# G1.3 Round 3 — Per-Letter Review of the Remaining 39 ESCALATED Papers

- **Date**: 2026-09-24/25
- **Lane**: mark-closure (Session 124)
- **Parser**: syllabai-parser branch `bench/g13-r3-letter-review` (`a7f481f`, on top of main `613c147`)
- **Trigger**: user instruction "Conduct a third round of review on the remaining 39 papers" — the session-123 NEXT item: "39 papers still carry PART-MARKS-MISMATCH (residual split: sub-level attribution nuances vs genuine printed QP/MS discrepancies — needs the per-letter layout-evidence round 3)".
- **Iron rule**: every number re-derived from first-hand sources (local parser build, downloaded corpus PDFs, local pdflane runs, fresh prod DB probes); the pre-session summary was again stale (local worklog ended at Task 38; g14/g15 state lived only in the records repo).

## 1. Repro basis

39/39 ESCALATED papers (g14) downloaded from SyllabAI/Past-Papers (78 PDFs, 0 missing) and re-parsed locally at `613c147`: **39/39 repro MATCH** vs the committed g14 report (questionCount/totalMarks/marksVerified). The drill (r3_drill.json, emit_atoms-faithful leaf semantics — parents excluded, pool caps honored) scoped **97 flagged questions across 39 papers**, letter-level diffs + direction stats.

## 2. Five new parser mechanisms found and fixed (parse_ms.py, +141/−4)

Every mechanism pinned to printed-layout evidence:

1. **Column-0 bare part openers** (`PART_BARE_COL0_RE`): pdftotext puts the part letter at the LEFT MARGIN when the qn column is empty — banner rows (`f   In part (f):`, 4CH0 1C Jun 2015 q8 p21) and scored rows (`d   i   silica ... 1`). `PART_BARE_RE` requires 1-8 leading spaces, so the whole f block scored under e (signature ms e3->8 / qp f5->None). Banner rows are structural openers; scored rows create points.
2. **Bare part letter ALONE** (`PART_BARE_SOLO_RE` + col-0 variant) and **paren part solo without qn** (`PART_PAREN_SOLO_QNLESS_RE`, `   (c)`, 4CH0 1C Jan 2018 q12 p18): both fell through and the following block inherited the PREVIOUS letter. Now open aggregates (QPART_*_SOLO semantics; end-of-parse resolution fills or demotes). Sequential guard: next/same letter of the open question, question must be open.
3. **qn + bare roman sub lead** (`QPART_BARE_SUB_RE`: `5   iv   oxygen / O2   1`, 4CH0 1C Jun 2013 q5 p10): qn+sub with an EMPTY part column matched nothing; the whole sub-block dropped. Same-question continuation only.
4. **Compact part+sub opener** (`PART_PAREN_COMPACT_RE`: `(c)(i) (Iron (III) oxide) loses oxygen   1`, 4CH1 1CR Jan 2020 q11 p18): `PART_PAREN_RE` demands `\s+` after the part letter — the whole (c) letter merged into (b) (ms b13 vs qp b5, c none).
5. **Arabic option leads** (`SUB_PAREN_NUM_RE`: `(2)`-`(5)` rows, 4CH0 1C Jun 2013 q8(b)): scored under the open part with sub=None (the atoms schema types sub as roman only — V1 schema error otherwise).
6. **Lone-cell backward fill relaxed**: the second marks cell under a tail-less M2 row (`M2 - 0.006` + lone `1`, 4CH0 2C Jan 2013 q7(a)(i)) now fills the text-bearing open point; previously the cell routed forward as pending and was WIPED by the next opener's own cell.

**Rejected experiment (kept out by fixtures)**: raising the unlocked marks-column threshold 48->73 broke 11 fixtures + 8 repro papers (real marks columns in 48-73 exist) — reverted byte-exact.

Tests: `tests_rcc_residual.py` +8 fixtures (suite **140 / 1 skip / 0 failures**). Branch pushed (`bench/g13-r3-letter-review`); parser-ci lanes unaffected; pdflane suite local-verified as in prior rounds.

## 3. Re-gate (g15_gate_report.json)

42 papers re-gated (the 39 + the 3 carried VERIFIED): **8 VERIFIED / 34 ESCALATED**. Newly VERIFIED (flags fully cleared, marksVerified=true): 4ch0-1c-201801, 4ch0-2c-201701*, 4ch1-1cr-202001, 4ch1-1cr-202101, 4ch1-2c-201906. (*2c-201701's bank rows are teacher-VALIDATED — see §5.) Corpus-wide VERIFIED (of the original 77): 16 -> **21**.

Flag deltas (papers): PART-MARKS-MISMATCH 39 -> 34; flagged questions 97 -> 78 (19 cleared).

## 4. Classification of the remaining 78 flagged questions (g15_classification.json)

| class | count | meaning |
|---|---|---|
| SIGNATURE-REVIEWED | 49 | shape-bucket level (r3_drill.json signatures: 1-2 mark shorts, phantom over-captures, option-row losses) — next round's evidence-card queue |
| SOURCE-PAIR-MISMATCH | 12 | **4ch0-1c-201601 wholesale**: the repo's "January 2016 QP" carries Jan-2015 content (cover printed "Monday 12 January 2015"; byte-distinct from the real Jan-2015 QP) while its MS is genuine Jan-2016 — every mismatch is a cross-session pairing. Doc-lane corpus fix (fetch the real Jan-2016 QP), NOT parser work. |
| RESIDUAL-PARSER | 10 | evidence-carded mechanisms for future rounds: 2012+ table-grid interleaving (notes-column fragments spawn points under "Any two from"), merged-cell arithmetic over-captures |
| DEGENERATE-LAYOUT | 5 | inherently ambiguous print: matching block with ONE cell covering rows (i)-(vi) (201606 q4), inline marks (`M2 2 2`, 201506 q3), detached grid cells (201701 q10), answer-value tables (2CR 2019 q2) |
| PRINTED-DISCREPANCY | 2 | genuine QP-vs-MS printed total disagreements on the paper (201301 q2, 2C 201401 q3) — source truth, disclosed |

Session-label sweep (r3i): all 39 pairs checked; only 201601 mismatches. (1CR-202006's MS printing "November 2020" is the COVID renaming of the June-2020 regional sitting — content-consistent.)

## 5. Bank drive (g15_drive_report.json + g15_cgate_report.json)

Sanctioned supersession pattern; idempotency-probe recovery executed once (first 201801 POST timed out on a Render cold start; the probe confirmed it landed late, the landed row was archived and the drive completed cleanly — never a blind re-POST):

- **4 REPLACE** (archive -> guarded delete with prestate asserts attempts=0/smart_mark=0/agreement=0/validated=0 -> POST 201): 4ch0-1c-201801 (16q/120), 4ch1-1cr-202001 (11q/110), 4ch1-1cr-202101 (10q/110), 4ch1-2c-201906 (8q/70). Arithmetic bank=draft=atoms EXACT 4/4.
- **1 SKIP fail-closed**: 4ch0-2c-201701 carries 8 teacher-VALIDATED glmocr versions — routed to the review-package flow: `bench/review/validated-supersession/4ch0-2c-201701/` (REVIEW.md + SHA-pinned archive + proposed draft). The package surfaces the same material finding as the first two: the VALIDATED rows are grossly incomplete vs the print (**2 marks** of part-marks vs printed 60; proposed pdflane product 60/60 VERIFIED, 0 attempts).

C-gates: zero-teacher-validated-rows-destroyed (0 in all archives); the three bank-VALIDATED papers verified untouched (4ch1-2c-202101, 4ch1-2cr-202001, 4ch0-2c-201701 — all still VALIDATED + glmocr provenance).

Bank totals: 1,468 questions / **4,796 mark points** / 97 exam_papers; pdflane-atoms-draft-v1 provenance 149 -> **194 versions**. (glmocr versions 715 -> 670.)

Disclosures: (a) embed refresh for the newly landed papers NOT run this session (embed-lane cadence); (b) serving soak not run; (c) the 201601 source-pair defect means its currently-landed bank rows (driven in earlier rounds) pair a Jan-2015 QP with a Jan-2016 MS — flagged to the doc lane.

## 6. NEXT (round 4 candidates)

1. Evidence-card the 49 SIGNATURE-REVIEWED questions (biggest bucket) — expect 1-2 more mechanisms (grid interleaving + merged-cell arithmetic).
2. Doc-lane: re-fetch the real Jan-2016 QP for 4ch0-1c-201601; re-expose the 10 PDF-MAPPING-AMBIGUOUS slugs.
3. Teacher sign-off on the THREE validated-supersession packages (4ch1-2c-202101, 4ch1-2cr-202001, 4ch0-2c-201701).
4. Embed refresh + serving soak for the 16 landed papers (embed-lane).

## 7. Artifacts

- `g15_gate_report.json` — 42-paper re-gate (8 VERIFIED / 34 ESCALATED)
- `r3_drill.json` — 97-question letter-level drill + shape buckets
- `g15_classification.json` — the 5-way classification of the 78 residuals
- `g15_drive_report.json` / `g15_cgate_report.json` — 4 drives + gates
- `g15_bank_prestate.json` — prestate probes for the 5 candidates
- `drafts/` — the 4 past-paper drafts (SHA256SUMS covers all files)
- Parser: `bench/g13-r3-letter-review` a7f481f (pushed); parse_ms.py +141/−4; tests_rcc_residual.py +8 fixtures
