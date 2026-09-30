# G1.5 round-5 grammar — R4-GRID cell attribution + R4-MCQ QP sub-romans (2026-09-25)

Task: session-126 NEXT item — "round-5 grammar: R4-GRID cell attribution (13
cards) + R4-MCQ QP sub-romans (clears 2 UNKNOWN-PART); fixtures from
g16_cards_raw.json; merge bench/g13-r3-letter-review to parser main. And
4ch1-1c-202011 look in PMT."

## 1. Parser lane

Commits (SyllabAI/syllabai-parser main):

- `f4ec81f` — bench/g13-r3-letter-review fast-forward-merged to main
  (613c147..f4ec81f) BEFORE round-5 work, per instruction.
- `d921891` — feat(g1.5-r5): R4-GRID cell attribution + R4-MCQ QP sub-roman
  re-anchor (+10 fixture tests, `tools/pdflane/tests_g16_round5.py`).
- `b0907a0` — fix(g1.5-r5): step-with-captured-cell guard on the lone-cell
  forward (re-gate-exposed 1CR Jun-2019 q2 regression, then zero regressions).

Suite: 150 tests OK (1 skipped) at `b0907a0` — 140 baseline + 10 new.

### Grammar changes (parse_ms.py unless noted)

1. **Lone-cell forward precedence with opener-block own-cell scan**
   (`_opener_ahead_with_cell`): a lone marks cell with a block opener within
   4 content lines belongs to that opener's block when the block carries no
   other marks cell (shallow rows AND the opener row's own tail checked;
   deep note-column tails excluded — they are the NEXT block's displaced
   cell). Evidence: 4ch1-1c-202406 q3 '4' / q4 '5' above solo '(c)'; 2C
   Nov-2021 q7 '1' above '(d)'; 2C Jun-2020 q2 '1' above '(b)' past an
   IGNORE note.
2. **Solo opener forms** (PART_PAREN_SOLO_QNLESS_RE, PART_BARE_SOLO_RE,
   PART_BARE_SOLO_COL0_RE, PART_PAREN_COMPACT_RE, PART_BARE_COL0_RE,
   QPART_BARE_SUB_RE) added to `_is_opener_shaped` + both block-boundary
   sets — the G1.3-r3 forms were invisible to every lookahead.
3. **Redirected-cell step materialization**: a tail-less M/A row the G1.3
   redirect targeted materializes the pending cell as its own deferred point
   instead of absorbing as an unscored step (4ch0-1c-201401 q11(d) M3 — the
   expiry then let the end-of-parse merged-cell recovery poison b 2->3).
4. **Continuation-branch opener redirect**: deep-note cell above the next
   opener hands off via pending (202406 q3 (d) '1' on 'ALLOW Mg  1').
5. **Bare-digit question total**: 2019+ black-box totals print as a lone
   right-column digit; when it equals the open question's running point sum
   and the next content opens a QUESTION (or page ends), it is the total row,
   never a marks point (4ch1-1c-202111 q1 '5', b 2->7).
6. **Carry-guidance scored-row escape**: a guidance continuation carrying its
   own disciplined marks cell scores under the open block (4ch0-1c-201501
   q8(f)(i) 'by bacteria ... 1' after 'M2 can be awarded').
7. **emit_atoms.py question-number re-print re-anchor**: periodic-table
   inside-cover digits (y~755, below the footer band) open the atom
   prematurely; the true '1 (a) ...' re-print re-anchors (fresh container) so
   '(a)' opens and MCQ sub-romans (i)/(ii)/(iii) segment under (a) — phantom
   letter 'i' gone (4ch1-1cr-202006 q1, 4ch1-1c-202111 q1).

### Round-4 card coverage (harness: scripts/g16_grid_harness.py, real
full-MS parses at b0907a0)

Letter-exact after round-5 (9/13 GRID): 201401:11, 201406:15, 201501:8,
201306:7(letter-level), 202406:3, 202406:4, 202406:8, 202001:2, 2cr-202101:7.
Remaining GRID residuals (round-6 queue, shapes documented in
g16_cards_raw.json): 4ch0-2c-201401:5 (capped-pool '4' block cell), 
4ch0-2c-201501:9 (cell displaced two blocks up), 4ch1-1c-202506:6 +
4ch1-1cr-202506:10 (extra-point MCQ-adjacent shapes). R4-MCQ QP sub-romans:
2/2 fixed.

## 2. Re-gate (29 round-4 papers, blob-verified local PDFs, run_paper at
b0907a0; diff basis r4_parse_results.json @ f4ec81f)

Artifacts: r5_regate_diff.json (per-slug raw), r5_regate_summary.json.

- Papers improved: 10 — zero regressions.
- Newly marksVerified: 5 — 4ch0-1c-201206, 4ch0-1c-201406, 4ch0-1c-201501,
  4ch1-1c-202111, 4ch1-2c-202001.
- Questions clearing flags (improved papers): 17, incl. all round-4 targets
  202406 q3/q4/q8 (2024 1C now fully flag-free), 202111 q1/q2, 202001 q2,
  201401 q8/q11, 201406 q15, 201501 q8, 201306 q6/q7, 202006 q1,
  2cr-202101 q7.
- Fully flag-free among the 29: 4ch0-1c-201206, 4ch1-1c-202111, 
  4ch1-1c-202406, 4ch1-2c-202001, 4ch1-2cr-202101.

## 3. Doc-lane: 4ch1-1c-202011 (Nov-2020 1C) PMT probe — NEGATIVE

PMT (PhysicsAndMathsTutor) probed first-hand 2026-09-25:

- Main site Cloudflare-gated for curl AND headless Chromium (challenge loop);
  NOT authoritative.
- Download subdomain `pmt.physicsandmathstutor.com` is OPEN (404s, no
  challenge) — probes there are authoritative. Real structure discovered via
  search-index leak:
  `/download/Chemistry/GCSE/Past-Papers/Edexcel-IGCSE/New-Spec-Paper-{1,2}/{QP,MS}/<Session> <kind>.pdf`.
- Paper 1 sessions present: November 2021, June 2022, January 2023,
  June 2023 ONLY (17 session probes). Paper 2 additionally hosts
  "June 2020 QP/MS" — cover-verified as the CANCELLED June sitting
  ("Wednesday 10 June 2020", Paper Reference 4CH1/2C), not November.
- No November-2020 1C under 20+ naming/structure variants ((R) suffixes,
  v1/v2, "1C/1CH" prefixes, 4CH1 prefixes, Science Double-Award and Old-Spec
  parents, October-November spellings).
- Verdict: PMT does not host the Nov-2020 4CH1/1C pair. 4ch1-1c-202011
  remains operator-gated (Pearson Exam Officer / passworded dynamicpapers /
  manual upload). Local copies of the PMT probes: pmt_dl/ in the session
  workspace.

## 4. Disclosures

- No bank drive this session (not requested): the 5 newly marksVerified
  papers are drive-eligible (supersession / fresh ingest per existing gates)
  as the next mark-closure step.
- Parser-lane commit chain is verified reproducible: 150/150 fixture tests,
  29/29 paper re-parse, harness 9/13 letter-exact with the 4 residuals
  pinned to their card evidence for round-6.
