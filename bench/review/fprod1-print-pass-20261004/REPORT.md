# F-PROD-1 print pass — the 62 print-dependent rows adjudicated against the corpus PDFs (2026-10-04)

**Status:** EXECUTED — all 62 print-dependent rows carry verdicts with print-level evidence; the worksheet is complete (v3, 176/176 verdicts, 0 blank).
**Authority:** operator trace `1a103290c88606f9` ("62-row print pass"); REPORT protocol item 4b — verdicts are made against the **corpus's checksum-verified PDFs**, never against either import lineage. The act is the operator's, delegated in-session (the rulings 1–8 form); every verdict carries its printed evidence so any human can re-verify it in minutes.
**Print substrate:** `SyllabAI/syllabai-pastpapers` @ `1f7e8355`, chemistry subtree (sparse-checkout expanded locally, read-only). **All 25 papers' manifest sha256 pins verified OK** (G6 discipline). Page-1 identity prints read on every paper (codes + series) — the folder-mislabel audit's lesson applied.

## The 2020-11 mapping (resolved first, before any verdict)

The roster's "4CH1/1C + 1CR June 2020" map to the corpus's `2020-11` dirs (June 2020 series cancelled; these are the printed June-series papers). Identity verified from the prints: the QP cover prints **"Thursday 14 May 2020", Paper Reference 4CH1/1C** — a June-2020-series paper; the MS cover prints "November 2020" (the marking session). Exactly the T-C71 4PH1 precedent (DAM November-2020 files printing the June-2020 timetable). Usable as the authoritative prints for the "June 2020" roster entries.

## P1 — the 7 mismatch rows: ZERO genuine print conflicts

**Headline: every one of the 7 "QP vs MS mismatches" dissolved under the print pass.** None is a print conflict; all 7 are **bridge parser cross-format misalignments** — the bridge read the wrong question's block total from the MS grid (whose block structure differs per era), or a cumulative block total as a single-question total. The prints themselves agree everywhere they both speak.

| row | bridge claimed | print verdict | evidence |
|---|---|---|---|
| 4CH0/1C Jan 2013 Q2 | QP 6 vs MS 15 | **qp-print-authoritative(6)** | QP prints "= 6 marks"; the MS prints NO separate Q2 total — Q1's block total is itself unprinted and the Q2 block's "Total 15" is cumulative (9+6); QP questions sum to 120 = printed paper total |
| 4CH0/1CR Jun 2013 Q5 | QP 11 vs MS 16 | **both-prints-agree(11)** | QP "= 11 marks"; MS Q5 block prints 11 (bridge read Q6's) |
| 4CH0/1CR Jun 2013 Q7 | QP 16 vs MS 9 | **both-prints-agree(16)** | QP 16; MS Q7 block 16 (bridge read Q9's) |
| 4CH0/2C Jan 2013 Q1 | QP 4 vs MS 8 | **both-prints-agree(4)** | QP 4; MS Q1 block 4 (bridge read Q3's) |
| 4CH0/2CR Jun 2017 Q4 | QP 9 vs MS 6 | **both-prints-agree(9)** | QP 9; MS Q4 block 9 |
| 4CH1/1C Jun 2019 Q1 | QP 4 vs MS 9 | **both-prints-agree(4)** | QP 4; MS Q1 block 4 (bridge read Q11/Q12's) |
| 4CH1/1C Jun 2019 Q13 | QP 12 vs MS 9, bank 12 | **both-prints-agree(12) + bank-total-verified** | QP 12; MS Q13 block 12; bank 12 — all three agree (bridge read Q15's) |

## P3 — the 32 banked parse-side rows: 28 verified, 4 real defects

- **28 `bank-total-verified`** — the bank's served total equals the authoritative print (25 qp-only rows: bank == QP printed per-question total, every one; 3 gap rows resolved via the QP print: 1C 2016-06 Q10 = 6, 1CR 2016-06 Q11 = 15, 1C 2019 Q10 = 7 — the last also cross-checked against the MS's printed Q10 block total 7).
- **4 `defect(bank-repair lane)`** — all four are the ms-only rows where the bank serves a **1-mark partial entry** while the print carries 9–13 marks: 4CH0/1C Jun 2013 Q10 (bank 1, print 13 — QP and MS prints agree), 4CH0/1C Jun 2017 Q11 (bank 1, print 11), 4CH0/1C Jun 2018 Q12 (bank 1, print 11), 4CH0/1CR Jun 2017 Q11 (bank 1, print 9). These rows' `bank_state=VALIDATED` with a 1-mark total is the defect the bank-repair lane's next pass should repair.

## P2 — the 23 identity rows: 20 verified, 3 narrowed by a print-format fact

The MS docs print paper totals in four different formats across the eras ("Total for paper N" / "PAPER TOTAL: N MARKS" / "Total marks N" / per-question block markers in three phrasings). Verdict tiers:

- **6 `paper-totals-verified`** — both paper totals PRINTED and equal: 1C 2012-06 (120), 1C 2013-06 (120), 2C 2013-06 (60), 2CR 2013-06 (60), 1CR 2019-06 (110), 2CR 2019-06 (70).
- **14 `ms-total-derived-agrees`** — the MS prints no paper total, but its printed per-question block totals sum exactly to the QP's printed paper total (e.g. 1C 2015-06: 120; 1CR 2013-06: 120; 2C 2017-06: 60; 1C 2024-06: 110; 1CR 2020-11: 110; 2CR 2023-06: 70; 1C 2019-06: QP prints "TOTAL FOR PAPER = 110 MARKS" on the end page, MS blocks sum 110). Four of the 14 involve partially-printed MS block sets (1CR 2017-06: 14/15 printed, the unprinted Q14 block covered by its QP print 10; 2C 2015-06: 5/6 + QP 14; 1C 2020-11: 6/10 + QP prints 12/14/14/12) — every derivation recorded in the worksheet notes; no conflict anywhere both prints speak.
- **3 `qp-total-printed-ms-total-unprinted`** — the 2016-family MS docs (1C/1CR/2CR June 2016) print NO totals at all: no paper total, no per-question block totals (verified pdftotext + PyMuPDF + OCR probe). The QP totals are printed (120/120/60) and the MS pairing is confirmed by its cover codes ("Chemistry (4CH0) Paper 1C", Summer 2016), but the totals-agreement check is structurally uncompletable against those MS prints. Narrowed open — a print-format fact, not a serving risk (the papers serve from the VALIDATED lineage).

## Net outcome

| class | rows | outcome |
|---|---:|---|
| P1 mismatch | 7 | closed: 6 both-prints-agree + 1 qp-print-authoritative — **zero genuine print conflicts** |
| P3 banked parse-side | 32 | 28 bank-total-verified + 4 defects → bank-repair lane |
| P2 identity | 23 | 20 verified (6 printed + 14 derived) + 3 narrowed (MS prints no totals) |
| **Total** | **62** | **55 closed + 4 defects referred out + 3 narrowed open** |

With the 114 `gap-accepted` rows from the operator disposition, **the worksheet stands at 173 closed / 4 defects referred / 3 narrowed** — F-PROD-1's review debt is discharged to the print-evidence boundary.

**The parser finding (for the ingestion lane):** the bridge's cross-format MS-total alignment was the single largest defect source — 7 misparses on these papers alone, all from reading the wrong question's block total across MS format eras. Any future bridge rebuild (the F-PROD-1b ruling's future-re-ingest clause) should align MS blocks by question number where the format prints it, and treat unmarked/cumulative block totals as spanning until proven single-question.

## Artifacts

- `fprod1_review_worksheet_v3_print_pass.csv` (in the packet dir; sha256 `419521e6c51f961f…`) — 176 rows, verdicts + per-row print evidence in the notes.
- This dir: the five phase scripts + four evidence JSONs (inventory, P1, P3/P2, P2).
- Upstream records: packet `762896b` · disposition `1835fd5` · ruling `d2befa9` · status lane `e3a566d`.
