# Task 64 — Jan-2021 Supersession EXECUTED (operator APPROVE, trace 1a0ea189623183e5)

Package: `bench/review/validated-supersession/4ch1-2c-202101` — the standing
operator-owned open item since Task 55. The operator's **APPROVE** (IM trace
`1a0ea189623183e5`) is the sign-off the REVIEW.md contract required. Executed
as agent-performed work under explicit operator delegation; **not** an in-app
teacher session; `teacher_validation_events` 0 throughout.

## What was executed (REVIEW.md steps 1–4 + Task-55 follow-up (a))

1. **Archive re-verified** — package SHAs byte-exact (`SHA256SUMS` in this
   pack). The staged `current-rows-archive.json` proved to MISS 6 mark_points
   (28 vs live 34): all 6 carry the chain's own creation timestamp
   (2026-09-14 12:03:04.87–.88) and the per-scheme sums reconcile exactly
   (+8 = 63 live), i.e. a staging-time **export artifact**, not post-staging
   mutation. A fresh complete live archive (`archive_live_task64.json`,
   incl. 3 attempts + 14 answers the package archive lacked) is the undo
   record.
2. **Guarded delete** of the glmocr bank chain — one fail-closed tx
   (TX-1): answers 14 → attempts 3 → mark_points 34 → mark_schemes 7 →
   question_parts 48 → question_versions 7 (the teacher-VALIDATED rows the
   standing convention protects) → questions 7 → bridge 1 → exam_papers 1,
   every DELETE rowcount-gated, post-asserts green, COMMITTED.
   First execute attempt aborted CLEAN (census-compare bug, zero partial
   writes — server-side rollback verified before re-run).
3. **POST the SHA-pinned draft verbatim** →
   `POST /api/v1/teacher/content/past-papers` → 201, paper
   `890f8634-700a-4e16-a02f-f67b1bf1f625`, 7 questions / 48 parts / 39 mark
   points, lands SUGGESTED per the ingestion contract.
4. **Arithmetic gate bank==draft EXACT**: q marks multiset [5,5,8,9,14,14,15]
   = 70 · 48 parts (multiset equal) · 39 points sum 70 · mark-point TEXT
   multiset equal · all SUGGESTED.

**Resolution tx (TX-2, fail-closed):** PLACE pointers to the corpus-wave
chunk-ful docs (the staged draft still referenced the pre-wave glmocr shells
0751cabc/f2237b67 — the live pointers had already been moved by the 09-25
corpus wave; restored, R6 per-paper PLACE pattern) · series/year backfill
JAN/2021 (Repair-B pattern; ingestion leaves them NULL) · VALIDATE paper +
7 qv + 7 schemes + 2 docs · REJECT the 2 empty shells (rows retained,
queryable; their display-only `source_document_id` citations remain
resolvable per Task-63 code check) · **in-tx paired re-stamp of the 22
parked rev1 chunks → rev2** (Task-55 follow-up (a); stamp precedent: no
audit rows, ck_cra_action admits review verbs only) · 20 audit rows
**ids 3871–3890** (PLACE 1 · VALIDATE 17 · REJECT 2), actor Nawaf Al
Hussain Khondokar, trace + honesty note on every row. COMMITTED, then
ANALYZE document_chunks/exam_papers/documents.

## Discoveries recorded (none blocking)

- **Doc topology**: the paper's live pointers were already the chunk-ful
  corpus-wave docs (a4a8a5e1 qp / d74802bc ms, 11+11 chunks, G6-true);
  the package's shell refs were staged pre-wave. Shells are now REJECTED
  inert rows (0 chunks, metadata had claimed 10).
- **Subject fork (pre-existing)**: the draft resolves subject code
  `4CH1CHEMISTRY` (0f3cc8ba — the pdflane-era cohort, 27 papers / 25
  VALIDATED); the legacy glmocr subject `4CH1` (e56dc9ee) keeps its 66
  remaining papers. Fork predates this task; recorded, not fought.
- **Audit id gap 3831–3870**: 40 sequence values burned by the two
  rolled-back INSERT attempts during apply debugging (NEXTVAL is not
  transactional; Task 62's id-3734 precedent). Zero live rows in the gap;
  the committed rows are exactly ids 3871–3890.

## End state (independently verified, fresh connections, 20/20 + live probe 5/5)

- Papers census **90 VALIDATED / 0 FLAGGED / 0 SUGGESTED / 14 REJECTED** —
  the corpus has **no SUGGESTED paper left**; the Jan-2021 row is the
  pdflane 7q/70 VERIFIED content, VALIDATED and serving.
- Documents census **567 V / 354 S / 98 R** (+2 chunk-ful VALIDATED,
  −2 shells REJECTED, all rows retained).
- The 22 chunks: rev2 · gemini-embedding-001 · on VALIDATED docs →
  serving pool **2,913 → 2,935** (+22, additive-only).
- Live probe: 5/5 queries × 10 hits, single model gemini-embedding-001.
- `content_review_audit` is the only ledger written;
  `teacher_validation_events` 0; provenance = this pack + records commit +
  worklog.

## Remaining open (unchanged by this task)

§D1 leftovers pass (59 zero-chunk SUGGESTED docs, minus the 2 shells retired
here → 57) · bank-repair queue (Q10 b–d 6 marks, 2 scheme rows, empty-stem
rows) · sheet-generator regex fallback fix · stale-citation re-point
(cosmetic) · sibling supersession packages `4ch1-2cr-202001` and
`4ch0-2c-201701` still await their own sign-offs (their papers are already
VALIDATED; rows incomplete vs print 43/60 → 70/60).
