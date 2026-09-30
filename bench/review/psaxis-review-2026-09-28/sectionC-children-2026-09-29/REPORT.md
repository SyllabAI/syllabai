# Task 67 — §C CHILDREN REVIEW: VALIDATE_ALL EXECUTED (2026-09-29)

**Authorization:** operator IM trace `1a0ea8242c254e35` — "Proceed with next"
(extends the Task-58→66 delegation chain; honest provenance on every audit row:
agent-performed, operator-delegated, NOT an in-app teacher session;
teacher_validation_events 0 throughout).

The "next" open item per the Task-66 close was the **§C children review**
(T-PS1 §C rows 1-2, named in Task 66 as a NEW open item): the children of two
already-VALIDATED papers, all SUGGESTED, **zero audit rows**, never covered by
any lane. The sheet's decision menu for both rows: *"run VALIDATE_ALL on the
children, or re-flag the paper if the extraction is suspect."*

## A. Probe findings (read-only, evidence-frozen)

1. **Identity (paper_code-based; (series, year) alone is ambiguous — 1CR/2CR
   rows exist alongside):**
   - `4CH1/1C January 2022` = paper `566c24ca-1049-4c64-9419-b52ae3ed2213`,
     extraction `pdflane-atoms-draft-v1`, subject `4CH1` (legacy cohort).
   - `4CH1/2C June 2019` = paper `37f7f180-6643-4635-9921-88ee8bc6aad1`,
     extraction `pdflane-atoms-draft-v1`, subject `4CH1`.
2. **Child trees:** 11 q + 11 qv + 11 schemes (Jan-2022, banked 110) and
   8 q + 8 qv + 8 schemes (Jun-2019, banked 70); every qv single-version,
   confidence 1.0, mirror invariant (qv stem/marks == question row) intact;
   all questions active/STRUCTURED.
3. **Zero audit rows** on every child AND on both paper rows themselves — the
   papers were validated in the corpus-wave era before per-paper audit
   discipline; the children were never reviewed. Exactly the §C pattern.
4. **Printed evidence = the papers' linked VALIDATED QP/MS docs** (serving
   chunks, rev2): `4ch1-1c-202201/qp.pdf` 16 chunks, `ms.pdf` 18 chunks;
   `4ch1-2c-201906/qp.pdf` 11 chunks, `ms.pdf` 15 chunks — all texts frozen
   under `evidence/`. The QP chunks carry no mark tokens (chunker furniture
   filter); the **MS chunks carry per-question "printed total" lines and
   per-point "(M marks)" tokens** — the authoritative printed arithmetic.
5. Bank shape notes (both accepted shapes, cf. Task-66 dispositions): pure
   context container rows (e.g. part `a`) may be absent while their subparts
   are present; prompts carry "DO NOT WRITE IN THIS AREA" answer-booklet
   furniture that the printed chunk text filters out; some scheme points merge
   printed guidance notes into the point text.

## B. Content review — ALL RECONCILIATION CHECKS PASS (both papers)

Against the sha-frozen chunk evidence (`review_task67.json`):

- **R1 question census:** bank question count == printed QP chunk headers ==
  printed MS question sections (11 and 8). PASS.
- **R2 per-question totals:** every qv.marks equals the printed MS "Question N
  printed total" — 19/19. PASS.
- **R3a scheme points:** bank point marks multisets == printed MS point marks
  per question, 19/19. PASS.
- **R3b point text attribution:** every ';'-fragment of every banked point
  (including merged-guidance points) attributes token-wise into the printed MS
  text of its question. PASS.
- **R4 prompt attribution:** every banked part prompt (minus answer-booklet
  furniture) attributes token-wise into the printed QP text of its question
  (interleaving-tolerant token-multiset containment). PASS.
- **R5 effective-marks arithmetic:** containers with subparts equal their
  subpart sums; container-less subpart chains count directly; effective totals
  equal qv.marks 19/19 (Jan-2022 Q4: 3+5=8, Q8: 5+2+5+3=15, Q11: 4+5+3=12;
  Jun-2019 Q6: 4+3+2+5=14, Q8: 2+5=7). PASS.
- **Paper totals:** banked 110 == printed per-question totals sum 110; banked
  70 == printed 70. PASS.

**Verdict: the extraction is NOT suspect → VALIDATE_ALL per the sheet's
recommended option.** No marks or content were mutated; this is a states-only
landing (no Q10-style repair needed — the arithmetic is already exact).

## C. Apply — single fail-closed tx (dry-run first), COMMITTED

Pre-asserts: censuses (papers 90V/14R, docs 567V/305S/147R), pool 2,935,
rev1 0, events 0, audit tail 3,976, zero audit rows on targets, banked sums
110/70, all 38 targets SUGGESTED (per-target gates). Guarded UPDATEs
(`... AND validation_state='SUGGESTED' RETURNING id::text`, returning-set
equality gates): 19 qv + 19 schemes → VALIDATED. **38 audit rows
(ids 3977-4014)**, one per target, each stating the §C decision, the review
evidence, the operator delegation trace, and the no-teacher-events fact.
Post-asserts: per-paper child matrices {VALIDATED: 11}/{VALIDATED: 11} and
{VALIDATED: 8}/{VALIDATED: 8}, tail 4,014, events 0, banked sums and pool
unchanged. COMMITTED.

## D. Independent verify (fresh connection): 22/22 PASS

Censuses / pool / rev1 / events unchanged; full per-paper matrices VALIDATED;
audit rows 3977-4014 contiguous with exact verbs/actor/trace/target set; the
global ledger-vs-live reconciliation still shows **exactly 10 mismatches, all
pre-2026-09-15 demo-era ids** (no new mismatches); stems/marks byte-equal to
the frozen before-images; bank-wide mirror invariant intact; **19 questions
now servable** (active + VALIDATED current version). L1 live serving probe
5/5 queries × 10 hits, gemini-embedding-001.

## Honesty notes

1. Review-method false starts, all fixed before any write: (a) a probe join
   bug (papers reference `documents.document_id`, the canonical content-derived
   id, not the row uuid `documents.id` — briefly looked like missing docs;
   disproved within minutes, nothing written); (b) tokenization of normalized
   (space-stripped) strings glued words together and failed attribution;
   (c) R4 needed answer-booklet furniture stripping, R5 needed the
   effective-marks rule — both documented bank shapes, not defects.
2. One verify-side bug (credential-less DSN) aborted the first verify run
   before any read; fixed and re-run. A second run timed out on Render cold
   start and was re-run successfully — all reads are fresh-connection
   read-only; no writes outside the apply tx.
3. Serving context (report-only): the 19 questions carry **zero topic
   mappings** — they serve on the unscoped surface now, by-topic serving needs
   the separate mapping lane. Both papers sit under the legacy `4CH1` subject
   despite pdflane extraction (the subject fork recorded in Task 64).

## Files

`probe_task67.json` (incl. full chunk-text dump) · `review_task67.json` ·
`preflight_task67.json` · `archive_task67.json` (before-images) ·
`apply_task67_report.json` · `verify_task67.json` ·
`evidence/chunks_*.txt` (frozen printed QP/MS evidence, 4 files) · `SHA256SUMS`

## Remaining open (updated)

- Sibling supersession sign-offs 4ch1-2cr-202001 / 4ch0-2c-201701
  (operator per-package APPROVE; destroy teacher-VALIDATED rows).
- Sheet-generator regex fallback fix (code lane).
- Stale-citation re-point (cosmetic).
- Bank-scheme sparsity (91 qv without scheme rows on VALIDATED papers) —
  accepted gap; only evidence-clean MS extractions could fill it.
- By-topic serving for the 19 newly-VALIDATED questions (topic mapping lane).
