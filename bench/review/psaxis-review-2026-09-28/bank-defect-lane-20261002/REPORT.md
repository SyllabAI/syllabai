# BANK-DEFECT REPAIR LANE — 19-qv PRINTED-EVIDENCE RE-CLASSIFICATION + 4 MARKS REPAIRS (2026-10-02)

**Authorization:** operator IM trace `1a0f8d54ffe8d93d` — "mandate the new bank-defect
repair lane" — the operator mandate requested by the three-lane closeout
(`three-lane-20261002/REPORT.md` §Remaining-open item 1). Scope: the 19 unique qv
flagged by laneB's `new_defects` classification (22 evidence lines; the four
best-evidenced candidates plus the 1CR/2CR-2016 "version-misalignment" cluster and
1C-2016 Q10). The ~26 structural parse failures remain out of scope (engine-grade
work, separate lane).

## Method — variant-pinned, printed-evidence, fail-closed

laneB's defect flags compared bank `qv.marks` against **whatever MS doc was tried
first** — for the 1CR/2CR sittings that was frequently the wrong regional variant
(e.g. the 2C MS for 2CR-2016 questions; the 1C MS for 1CR-2016 Q2–Q12). This lane
rebuilds every judgment on variant-pinned evidence:

1. **Bank resolution** — external_ref + paper_code + session_label (1 row asserted;
   qv id re-asserted against the laneA/laneB ref map).
2. **Content attribution** — normalized stem tokens (q.stem + qv.stem + part
   prompts) scored against each printed-variant QP doc's ingested chunk text;
   best variant must be the qv's own paper variant at ≥0.90 with ≥0.02 margin
   (Lane A's attribution standard, plus an ambiguity guard).
3. **Printed evidence per variant** (checksum-pinned bytes, sha256-matched to
   `documents.checksum`):
   - **QP echo** — `(Total for Question N = M marks)` from `pdftotext -layout`
     over the local QP PDF (Lane A G2 machinery);
   - **MS corroboration** — per-question total via TOT lines and/or complete
     mark-row sums, from the local printed MS PDF and from the ingested MS chunks
     (v2-gated segment parse; both recorded).
4. **Classification** —
   - **REPAIR**: attribution to own variant + echo == MS corroboration (double)
     + bank differs → `qv.marks + q.marks := own-variant printed total`.
   - **NO-DEFECT**: attribution to own variant + bank == own-variant echo →
     laneB flag was variant misattribution; bank already matches the print.
   - **UNRESOLVED**: own echo exists but MS-side corroboration incomplete
     (2016 grid-parse gaps) → no write; joins the engine-grade residue.
   - **MISALIGNED-CONTENT**: attribution strongly to the *other* variant (none
     occurred — see Findings).

Doc identities were resolved by byte-identity, not by folder names: `4aa18ec4`
(28 pp, doc_id `b27f9358`) = **1CR June 2016 MS**; `01d95abf` (22 pp, doc_id
`c224dfa3`) = **1C June 2016 MS**; `11a85cd3` (doc_id `9fcd9d72`) = **2CR June
2016 MS**; `cf456ceb` = 2C June 2016 MS. laneB had used `cf456ceb` (2C) as the
only MS evidence for the whole 2CR-2016 cluster and `01d95abf` (1C) for
1CR-2016 Q2–Q12.

## Result — 4 REPAIRS committed; 12 NO-DEFECT; 3 UNRESOLVED; 0 misaligned

| ref | paper / session | QN | bank | own | echo | MS corroboration | class |
|---|---|---|---|---|---|---|---|
| q09-57202de4 | 4CH0/1CR June 2013 | 9 | 1 | R | 9 | chunk TOT 9, rows 7/7 | **REPAIR 1→9** |
| q11-22184324 | 4CH1/1CR June 2022 | 11 | 1 | R | 10 | chunk TOT 10, rows 10/5 | **REPAIR 1→10** |
| q01-5273dfa3 | 4CH0/1CR June 2016 | 1 | 1 | R | 7 | rows 7/7 | **REPAIR 1→7** |
| q10-2701ad3c | 4CH0/1C June 2016 | 10 | 1 | reg | 6 | rows 6/3 | **REPAIR 1→6** |
| q08-57202de4 | 4CH0/1CR June 2013 | 8 | 8 | R | 8 | chunk TOT 8 (rows 6/6) | NO-DEFECT |
| q03-d5815b70 | 4CH0/2CR June 2014 | 3 | 5 | R | 5 | chunk TOT 5 | NO-DEFECT |
| q02-5273dfa3 | 4CH0/1CR June 2016 | 2 | 6 | R | 6 | rows 2/4 (incomplete) | NO-DEFECT |
| q03-5273dfa3 | 4CH0/1CR June 2016 | 3 | 4 | R | 4 | rows 3/3 | NO-DEFECT |
| q04-5273dfa3 | 4CH0/1CR June 2016 | 4 | 8 | R | 8 | rows 4/4 | NO-DEFECT |
| q05-5273dfa3 | 4CH0/1CR June 2016 | 5 | 9 | R | 9 | rows 4/5 (incomplete) | NO-DEFECT |
| q08-5273dfa3 | 4CH0/1CR June 2016 | 8 | 8 | R | 8 | rows 3/3 | NO-DEFECT |
| q10-5273dfa3 | 4CH0/1CR June 2016 | 10 | 15 | R | 15 | rows 1/3 (incomplete) | NO-DEFECT |
| q12-5273dfa3 | 4CH0/1CR June 2016 | 12 | 13 | R | 13 | rows 4/6 (incomplete) | NO-DEFECT |
| q01-6ab313e4 | 4CH0/2CR June 2016 | 1 | 4 | R | 4 | rows 2/2 | NO-DEFECT |
| q02-6ab313e4 | 4CH0/2CR June 2016 | 2 | 8 | R | 8 | rows 4/4 | NO-DEFECT |
| q04-6ab313e4 | 4CH0/2CR June 2016 | 4 | 6 | R | 6 | rows 5/5 | NO-DEFECT |
| q09-5273dfa3 | 4CH0/1CR June 2016 | 9 | 1 | R | 13 | rows 6/2 only | UNRESOLVED |
| q11-5273dfa3 | 4CH0/1CR June 2016 | 11 | 1 | R | 15 | rows 11/6 only | UNRESOLVED |
| q06-6ab313e4 | 4CH0/2CR June 2016 | 6 | 1 | R | 8 | rows 6/2 only | UNRESOLVED |

Attribution scores (bank content): 18/19 attribute to the **R variant** at
0.90–1.00 (margins 0.08–0.60); 1C-2016 Q10 attributes to reg at 1.00 (its own
variant). **No qv attributed to a foreign variant** — the REPORT's
"version-misalignment" suspicion is refuted at content level.

## Findings

1. **The 1CR/2CR-2016 "misalignment cluster" was mostly a laneB artifact.** The
   bank's marks match the R-variant printed QP echo for 9 of the 11 R-attributed
   2016 qv (12 NO-DEFECT overall including 2013/2014/2022). laneB's "NEW-DEFECT?"
   lines were computed against the wrong variant's MS totals and must be read as
   void for these 12 refs.
2. **4 genuine bank-defects repaired** (all banked as 1): the printed-QP echo and
   the MS side agree per variant (double evidence), attribution to own variant,
   byte-level stem guards in-tx. Mechanics precedent: Task-66-TX-B
   marks-arithmetic; no state flips; no audit rows; parts untouched.
3. **3 qv move to the engine-grade structural residue with sharpened evidence**:
   1CR-2016 Q9 (echo 13), Q11 (echo 15), 2CR-2016 Q6 (echo 8) vs bank 1 — the
   printed totals are unambiguous, but the R MS chunk row-parses are incomplete
   (2–6 rows recovered), so no double-evidenced write under this lane's standard.
   Sparse recount stays 43.
4. **Corpus folder-mislabel finding:** the local PDF `202206_1cr_qp_R.pdf`
   (sha `f21e970f…`) is content-verified as the **4CH1/1CR** June 2022 QP
   (page-1 paper reference) but its bytes are the corpus doc filed under
   `4CH1-1C-202206/qp.pdf` (doc `a7a0e028`); the `4CH1-1CR-202206/qp.pdf` doc
   (`34bf2c02`, sha `f1d98b59…`) has no local bytes. Echo evidence for
   1CR-2022 Q11 used the content-verified file (recorded as
   `echo_src=202206_1cr_qp_R (content-verified override)` in the plan).
   The docmap also mislinks 2CR June 2014 to the paper-1 R MS. Folder names in
   the corpus are unreliable; checksums + page-1 content are the identity.
5. **audit tail 4047 → 4048 between sessions**: a benign no-op
   `VALIDATE_ALL` by `pilot.teacher@syllabai-test.dev` on 4CH1/1C Specimen 2017
   (0 versions + 0 schemes, VALIDATED→VALIDATED) landed 2026-10-01T19:16:19Z,
   after the three-lane census read. Verified read-only; this lane re-pinned
   audit_max = 4048 and writes no audit rows.

## Execution record

- Plan pinned pre-write: `laneD_plan.json` sha `51a7480544014c02f9d091818349e4a53147d8f9c5e3b806001d81c51b44a835`
  (builder `laneD_build_plan.py`, SELECT-only).
- Apply (`laneD_apply.py`): first dry-run **tripped fail-closed** on the audit
  pin (4048 ≠ 4047) — investigated read-only (Finding 5), re-pinned with the
  explanation inlined in the script; second dry-run green; `--commit` — one
  fail-closed tx, 4 double-condition-guarded updates ×2 tables, in-tx
  post-asserts (qsp 2637, qt 1725, schemes 1468, mp 5652, audit 4048, tve 0).
- Independent fresh-connection verify (`laneD_verify.py`): **ALL PASS** —
  after-values ×4, 15 non-repairs untouched, per-paper banked-sum deltas exact
  (+8 / +9 / +6 / +5 / +0 / +0), census pins (sparse 43, kn 492 pre-deploy,
  edges 730, audit 4048, tve 0).
- Post-lane census: `census_bundle_bankdefect_20261002.json` — drift NONE.

## Files

`REPORT.md` (this file) · `VERIFY_OUTPUTS.md` (verbatim session captures) ·
`laneD_plan.json` (19 classified entries, frozen evidence + before/after images) ·
`laneD_matrix.csv` (one-row-per-qv matrix) ·
`census_bundle_bankdefect_20261002.json` · `SHA256SUMS`.
Scripts (session workspace): `laneD_probe.py`, `laneD_probe2.py`,
`laneD_probe3.py`, `laneD_build_plan.py`, `laneD_apply.py`, `laneD_verify.py`,
`census_bankdefect_20261002.py` — SELECT-only except the one fail-closed apply tx.

## Remaining open (updated)

- **Engine-grade grid-layout work** (2015–2019 mark grids): the ~26 structural
  residue now including 1CR-2016 Q9/Q11 and 2CR-2016 Q6 with printed echo
  targets 13/15/8 already pinned by this lane's evidence.
- §C children VALIDATE_ALL; sibling supersession sign-offs — unchanged.
- V57 executes at next core deploy; post-deploy census re-pin (kn 435).
- Corpus hygiene follow-up (non-urgent): doc-folder mislabels from Finding 4 —
  folder/source_uri naming vs byte identity should be audited before the next
  ingestion wave trusts folder names.
