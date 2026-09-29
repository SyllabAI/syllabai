# Task 66 — BANK-REPAIR LANE + O6 CHILDREN LANDING REMEDIATION (2026-09-29)

**Authorization:** operator IM trace `1a0ea5a6dbc30c79` — "Proceed with next"
(extends the Task-58→65 delegation chain; honest provenance on every audit row:
agent-performed, operator-delegated, NOT an in-app teacher session;
teacher_validation_events 0 throughout).

The "next" open item per the Task-65 close was the **bank-repair queue**
(Q10 b–d 6 marks, 2 scheme rows, empty-stem rows). The probe phase found a
**live-DB integrity defect from Task 61** that outranked it and is remediated
here as TX-A; the bank repair itself executed as TX-B.

## A. Probe findings (read-only, evidence-frozen)

1. **O6 children never landed (critical defect, Task-61 O6 commit 21:19:52Z).**
   The global ledger-vs-live reconciliation (1,408 audit rows on
   question_version/mark_scheme targets vs live states) found **37 mismatches,
   all from audit ids 3680–3696 + 3703–3722**: the O6 apply wrote VALIDATE
   audit rows for 25 qv + 12 schemes (4CH1/1C June 2019: 15+2; 4CH1/1C June
   2020: 10+10) but the script contains **no UPDATE statement for either
   table** (grep-proven). In-tx post-asserts checked only paper censuses /
   doc links / the 2C-children exclusion — child states were never asserted —
   and the O7 independent verify did not check them either. This is the same
   defect class as O6b (which fixed the document batch of the same commit);
   the child batch was missed.
2. **The OCR report's Q10 reading was wrong.** Printed QP p15 (text layer,
   sha-frozen in `evidence/qp_p15_text.txt`): Q10 = (a)(i) *State what is
   meant by the term isomers* **(2)**, (a)(ii) *Draw the displayed formula
   for another isomer of C5H12* **(2)**, (b)(i) *Complete the equation* **(2)**,
   (b)(ii) *Give the name of this type of reaction* **(1)** — total 7. The
   bank's Q10 row holds part (a) in the stem **and part (b) as 3 part rows**
   (b / b-i / b-ii) — the content was already banked; the defect is **marks
   arithmetic**: qv.marks = 1 (mirror questions.marks = 1), part marks all 0.
   The "parts (b)–(d) never banked" claim looked only at stems.
3. **"2 missing scheme rows"** = a condensation of "only 2/15 qv carry scheme
   rows" (T-PS1 sheet row 36: "scheme-extraction gap: 13 of 15 qv have no mark
   scheme"). No scheme rows were fabricated: the MS source chunk for Q10
   (`evidence/ms_q10_chunk.txt`) shows the corpus md's own table flattening is
   lossy (its Q10 rows sum 2+2+1 = 5 vs printed 7 — "verification FAILED" is
   baked into the chunk text; the (a)(ii) scheme exists only as bleed-through
   notes). Building rows from it would invent structure. Gap documented
   bank-wide (91 qv on VALIDATED papers lack schemes — sheet-documented
   glmocr-lane property; MS content serves via RAG chunks regardless).
4. **Empty-stem rows (30 qv on VALIDATED papers):** every one carries complete
   parts (prompts non-empty). These are pdflane-atoms-draft-v1 papers whose
   drafts had no question-level stems; the content lives in
   `question_parts.prompt`. Filling stems would write summaries not printed
   on any paper = fabrication → accepted bank shape, documented, closed.
   (The 2C-2020 empty-stem 10-mark row is on a REJECTED phantom paper — moot.)
5. **§C leftovers discovered untracked** (T-PS1 §C rows 1–2): 4CH1/1C Jan-2022
   (11 qv + 11 schemes) and 4CH1/2C Jun-2019 (8 qv + 8 schemes) are ALL
   SUGGESTED under VALIDATED papers with **zero audit rows** — never covered
   by any lane (the lanes targeted FLAGGED papers). Flipping them = new review
   decisions on unreviewed content → NOT done; left as a named open item.
6. Ten further ledger-vs-live mismatches date from 2026-09-14 (demo-era rows
   predating the review lanes) — outside this chain's provenance; untouched.

## B. TX-A — O6 children landing remediation (COMMITTED)

Fail-closed, dry-run first. Pre-asserts: censuses (papers 90V/14R, docs
567V/305S/147R), pool 2,935, rev1 0, events 0, audit tail 3,939, all 37
targets SUGGESTED, flip set == the two papers' **full** child sets (nothing
else exists under them), §C papers' children carry zero audit rows.
Guarded UPDATEs (`... AND validation_state='SUGGESTED' RETURNING id`,
returning-set equality gates): 25 qv + 12 schemes → VALIDATED. **37 corrective
audit rows (ids 3940–3976)**, one per target, each cross-referencing its
original O6 audit row id and stating the defect mechanism (O6b precedent:
append-only, originals retained). Post-asserts: per-paper child matrices
{VALIDATED: 15}/{VALIDATED: 2} and {VALIDATED: 10}/{VALIDATED: 10}, tail
3,976, events 0. COMMITTED.

## C. TX-B — Q10 marks repair (COMMITTED)

Printed-evidence-grounded, arithmetic only, **no content mutation** (stems
byte-equal to the frozen before/after archive; no new rows):
- question_versions.marks 1 → **7** (printed Total for Question 10)
- questions.marks 1 → **7** (bank-wide mirror invariant 1,533/1,533 preserved)
- question_parts b-i 0 → **2**, b-ii 0 → **1** (printed (2)/(1) tokens);
  context part 'b' stays 0
- paper banked sum 104 → **110 = printed cover total 110** (the Task-61
  marks reconciliation gap is now closed at the source)
- NO audit rows: marks mechanics are not review actions (Task-55/62 stamp
  precedent); provenance = this pack + the worklog + the sha-frozen printed
  evidence.

## D. Independent verify (fresh connection): 28/28 PASS

Censuses / pool / rev1 / events / tail unchanged as asserted; the 37 VALIDATED
with per-paper matrices clean; corrective rows 3940–3976 all traced; global
ledger-vs-live reconciliation now shows exactly 10 mismatches, all pre-2026-09-15
(demo era, documented); §C papers untouched (still zero audit rows on their
children); Q10 end state exact; mirror invariant intact; before-images intact.
L1 live serving probe 5/5 queries × 10 hits, gemini-embedding-001.

## Files

`probe_task66.json` · `probe2_task66.json` (ledger-vs-live full sweep) ·
`preflight_task66.json` · `archive_task66.json` (before-images) ·
`apply_task66_report.json` · `verify_task66.json` · `evidence/qp_p15_text.txt`
(printed Q10, sha-frozen) · `evidence/ms_q10_chunk.txt` (MS Q10 chunk) ·
`SHA256SUMS`

## Remaining open (updated)

- **§C children VALIDATE_ALL** (NEW named item): 4CH1/1C Jan-2022 11+11,
  4CH1/2C Jun-2019 8+8 — unreviewed content, needs its own review evidence /
  delegation (T-PS1 §C recommended the children decision explicitly).
- Sibling supersession sign-offs 4ch1-2cr-202001 / 4ch0-2c-201701
  (operator per-package APPROVE; destroy teacher-VALIDATED rows).
- Sheet-generator regex fallback fix (code lane).
- Stale-citation re-point (cosmetic).
- Bank-scheme sparsity (91 qv without scheme rows on VALIDATED papers) —
  accepted gap; only evidence-clean MS extractions could fill it.
