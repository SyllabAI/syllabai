# G1.3 Round 4 — Evidence Cards for the 49 SIGNATURE-REVIEWED + Jun-2025 Residuals

- **Date**: 2026-09-25
- **Lane**: mark-closure / round-4 evidence (Session 126)
- **Parser**: syllabai-parser branch `bench/g13-r3-letter-review` (`f4ec81f`) — round-3 grammar, unmerged main; NO grammar changes this session (evidence-only round)
- **Trigger**: user instruction "Finalize this paper, round-4 evidence cards" — the session-125 NEXT item 2: "round-4 evidence-cards for the 49 SIGNATURE-REVIEWED + the two Jun-2025 residuals"
- **Iron rule**: every number re-derived from first-hand sources (fresh records clone @71bcb4e, Past-Papers blob downloads byte-checked against the Task-40 regate sizes, local pdflane runs at the r3 grammar, per-card printed pdftotext blocks read in full); the pre-session summary was again stale (local worklog ended at Task 41; workspace re-provisioned).

## 1. Queue derivation and repro

Queue = `g15_classification.json` SIGNATURE-REVIEWED items (49) + the two Jun-2025 ESCALATED residuals from the session-125 doc-lane regate (`4ch1-1c-202506:q6`, `4ch1-1cr-202506:q10`) = **51 questions across 29 papers**. Note: the SIGNATURE-REVIEWED entry `4ch0-2c-201601:q3` is the **2C** January-2016 paper (content-consistent per the round-3 session-label sweep) — distinct from `4ch0-1c-201601`, whose 12 SOURCE-PAIR-MISMATCH questions were resolved by the doc-lane re-fetch (session 125) and are correctly absent here.

Repro: all 29 papers' QP+MS downloaded from SyllabAI/Past-Papers (0 failures; regional-ambiguous June 2013/2014/2017 4ch0 papers downloaded in BOTH variants and selected by committed questionCount/totalMarks) and re-parsed locally at `f4ec81f`. **29/29 match the committed gate reports**; all 51 queue questions reproduce their flags (`g16_repro_parse_results.json`). Jun-2025 byte-sizes match the session-125 regate exactly (1c: 366,795/212,687; 1cr: 429,212/244,273) — download-path integrity cross-check.

## 2. Method

For every card: (a) emit_atoms-faithful letter arithmetic (leaf marks, pool caps mirrored from emit_atoms.py) — letter_cmp + sub_div; (b) the **printed pdftotext question block** from the MS layout pages (every card's block read in full during classification); (c) parsed MS points dump cross-check. Cards carry the full printed block (`g16_cards_raw.json`), so each mechanism claim is auditable against the print without re-downloading anything.

## 3. Seven mechanisms (g16_classification.json)

| code | count | meaning |
|---|---|---|
| R4-LOSS | 15 | whole-letter / whole-question / whole-row loss at layout boundaries: page breaks + grid-header re-prints, PMT footers, split header artifacts (`Mar/ks`), figure-label margin fragments interleaving rows (`8 all clip with graph`, 1cr-202201 q8), flipped-paren rows (`b) i)`, 1cr-202006 q3), and 3 QMISS all-MCQ questions (201706 q1, 201806 q9, 2c-201306 q2) |
| R4-GRID | 13 | marks-cell vertical displacement / cross-letter bleed: next-letter opener-attached cells bled into the previous letter (202406 q3 `4`→b, q4 `5`→b.ii, q8 d/e; 2cr-202101 q7; 2c-201401 q5), cells printed on the line ABOVE their row attached to the previous letter (2c-202001 q2, 202506 q6), lone-cell back-fill under/over-reach (2c-201306 q7, 201406 q15, 201401 q11) |
| R4-MCQ | 9 | 2017+ MCQ answer rows `X (gloss) 1` and `X is correct because... 1` — cell/row lost after header re-prints or consumed as openers (201701 q1, 201706 q2/q4/q10, 2c-201301 q2, 2c-201601 q3, 1cr-202201 q1, 202506 q6c); **QP-side**: MCQ sub-romans (i)(ii)(iii) parsed as letter-`i` parts (202111 q1, 1cr-202006 q1 — both carry UNKNOWN-PART) |
| R4-SUB | 6 | sub-lead / label-token rows: `6 (b) i` bare-roman-after-paren-part openers (201306 q6), bare-roman continuation rows consumed as point mds (`ii`, 201306 q11), solo `(v)` at page bottom (201701 q5), `M1`-rows-after-bare-`(ii)`-opener (201401 q12), label token `b(iv)` as 2-mark point md (1cr-201906 q4), phantom letter `g` from a misparsed `(b)(iv)` row (2c-202201 q3) |
| R4-PHANTOM | 3 | phantom points from continuation fragments + stray cells: `and (iii)` 2-mark (201106 q8), accept-continuation fragment (201406 q9), guidance-row cell + numeric-md point (201501 q7) |
| R4-TBL | 3 | answer-value/state-symbol tables: state-symbol rows `s l aq g` spawning points (201401 q8), two 5-mark table rows with part=None doubling the printed 5 (2c-201501 q8), arithmetic fraction fragment `) 3` interleaving (2c-202106 q7) |
| R4-ORGROUP | 2 | OR-alternative M1/M2 groups summed raw with no capped pool formed (201206 q1 b=3 vs printed 2) or cells lost inside OR blocks (201206 q11) |

Direction split (per card): 23 pure under-capture (MS<QP), 23 mixed-direction (over- and under-capture on different letters of the same question — e.g. 202406 q3 b 2→6 AND d 1→0), 2 pure over-capture, 3 whole-question zero — i.e. the residual is NOT a single-sign monotone error; per-mechanism grammar is required (a global bias fix would regress the 23 corpus-VERIFIED papers).

## 4. What this pins for round 5 (grammar queue, in expected-yield order)

1. **R4-GRID cell attribution** (13 cards, concentrated in 2019+ sessions but present since 2013): opener-attached / above-row cells must attribute to the FOLLOWING letter, not the previous open point — the biggest single lever on the modern papers (202406×3, 202506×2, 2cr-202101, 2c-202001…).
2. **R4-LOSS boundary recovery** (15 cards): page-break + header-re-print row re-anchoring, QMISS all-MCQ question capture, figure-margin fragment suppression, `b)` flipped-paren tolerance.
3. **R4-MCQ QP-side sub-romans** (2 cards, both flagging UNKNOWN-PART): QP parse of MCQ `(i)/(ii)/(iii)` sub-parts — small fix, clears 2 UNKNOWN-PART instances.
4. R4-SUB label tokens (6), R4-TBL (3), R4-ORGROUP pool formation (2), R4-PHANTOM guards (3) — each 1-2 fixture-sized mechanisms.

All cards carry the printed evidence needed to write fixture tests directly from `g16_cards_raw.json`.

## 5. Session disclosures

- No parser grammar changes, no re-gate, no bank drive this session (evidence-only round per the session-125 NEXT item; drive is only sanctioned after a grammar round re-verifies).
- The 29-paper PDF set was downloaded to the local workspace for the repro; corpus (Past-Papers repo) unchanged.
- The two teacher-VALIDATED bank papers and all bank rows are untouched.

## 6. Artifacts

- `g16_classification.json` — 51 cards: flags, arithmetic, letter_cmp, sub_div, mechanism + note, ms_pages, full printed question block
- `g16_cards_raw.json` — raw card dump (letter excerpts + question blocks, pre-classification)
- `g16_repro_parse_results.json` / `g16_committed_counts.json` / `g16_queue.json` — repro basis and queue derivation
- SHA256SUMS covers all files
