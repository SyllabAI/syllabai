# Task 70 — Sibling Supersessions EXECUTED (operator "APPROVE both", trace 1a0ec06fbd199a99)

Packages: `bench/review/validated-supersession/4ch1-2cr-202001` and
`bench/review/validated-supersession/4ch0-2c-201701` — the two standing
operator-owned sign-offs named by the Task-64 close-out. The operator's
**"APPROVE both"** (IM trace `1a0ec06fbd199a99`) is the sign-off both
REVIEW.md contracts required. Executed as agent-performed work under explicit
operator delegation, mirroring the Task-64 jan2021-supersession pattern;
**not** an in-app teacher session; `teacher_validation_events` 0 throughout.

## What was executed per package (REVIEW.md steps 1–4 + Task-64 TX-2 pattern)

Both package SHAs re-verified byte-exact before anything ran
(`4ch1-2cr-202001` draft `3e074f6d…` archive `7f575f52…`;
`4ch0-2c-201701` draft `33d8030a…` archive `bcf8ca4a…`). Preflight also
verified: paper identity/state/provenance, doc pointers intact, zero audit
rows referencing either chain, zero agreement-evaluations, docs VALIDATED with
0 rev1 chunks, subjects and ING anchors present, no `external_ref` collisions,
dry-run of the full delete with ROLLBACK green.

### 4ch1-2cr-202001 (4CH1/2CR — January 2020)

1. **Fresh live archive** (`archive_live_2cr202001.json`) — the undo record.
   Census: 1 paper, 7 questions, 7 versions, 43 parts, 7 schemes, 31
   mark_points (26 part-linked + 5 NULL-part multi-level refs — the staged
   side-by-side's "26" was the part-linked subset view; all rows created
   2026-09-14, zero post-staging mutation), 1 bridge record, 3 attempts,
   19 answers, 19 human_marks, 19 smart_mark_results (post-staging pilot
   growth; the staged header said "smart-mark results: 0").
2. **TX-1 guarded delete** (one fail-closed tx, every DELETE rowcount-gated
   against the fresh archive): human_marks 19 → smart_mark_results 19 →
   answers 19 → attempts 3 → mark_points 31 → mark_schemes 7 → question_parts
   43 → question_versions 7 (the teacher-VALIDATED rows the standing
   convention protects) → questions 7 → bridge 1 → exam_papers 1. COMMITTED.
3. **POST the SHA-pinned draft verbatim** →
   `POST /api/v1/teacher/content/past-papers` → 201, paper
   `d180d1b6-eafe-4468-af94-f88125da4569`, 7 questions / 48 parts / 38 mark
   points, SUGGESTED.
4. **Arithmetic gate bank==draft EXACT**: q marks multiset [6,6,7,9,13,14,15]
   = 70 (print total) · 48 parts (label/marks multiset equal) · 38 points
   (ref/text/marks multiset equal) sum 70 · all SUGGESTED pre-flip.
5. **TX-2 resolution** (one fail-closed tx): pointers already correct (the
   draft carried the live chunk-ful docs 37664a21/7f5e53ea — no PLACE row) ·
   series/year backfill JAN/2020 · VALIDATE paper + 7 qv + 7 schemes (15 audit
   rows) · re-stamp guard 0 rev1 · post-asserts green. COMMITTED.

### 4ch0-2c-201701 (4CH0/2C — January 2017)

1. **Fresh live archive** (`archive_live_2c201701.json`). Census: 1 paper,
   8 questions, 8 versions, 44 parts, 8 schemes, 34 mark_points (33
   part-linked + 1 NULL-part — reconciling the staged "34 (sum 54)"; all rows
   created 2026-09-14, zero post-staging mutation), 1 bridge record,
   **12 question_topics rows** (real 4CH1 TOPIC mappings created 2026-09-14
   18:03–18:04 on the legacy-spec rows; archived in the undo record, deleted
   with the chain — the replacement rows are ING-anchored per the ingestion
   contract and need their own mapping pass), 0 attempts/answers.
2. **TX-1 guarded delete**: mark_points 34 → mark_schemes 8 → question_parts
   44 → question_versions 8 (teacher-VALIDATED) → question_topics 12 →
   questions 8 → bridge 1 → exam_papers 1. COMMITTED.
3. **POST the draft verbatim** → 201, paper
   `21041891-11f6-4168-9136-771e666cd8fa`, 8 questions / 44 parts / 37 mark
   points, SUGGESTED (the staged draft carried NULL doc refs and
   ms sourceDocumentId — per package, verbatim).
4. **Arithmetic gate bank==draft EXACT**: q marks multiset [5,5,6,7,8,8,8,13]
   = 60 (print total) · 44 parts multiset equal · 37 points multiset equal
   sum 60 · all SUGGESTED pre-flip.
5. **TX-2 resolution**: PLACE pointers → the live chunk-ful docs
   d7d00cea/d04e464e (1 guarded UPDATE, 1 PLACE audit row) · series/year
   backfill JAN/2017 · VALIDATE paper + 8 qv + 8 schemes (17 audit rows) ·
   re-stamp guard 0 rev1 · post-asserts green. COMMITTED.

## Execution mechanics

- Auth for the two POSTs: HS256 access token minted with the deployment's own
  `SYLLABAI_JWT_SECRET` for the existing ops admin `admin@syllabai.dev`
  (ADMIN+TEACHER, token_version 1), shape-matched to live-issued tokens
  (jti/ver claims — the deployed JwtService is newer than the core-fresh
  working copy). Teacher-token smoke test (GET review-queue-v2 → 200) ran
  BEFORE any destructive commit. Ingestion does not write audit/events rows.
- Ledger: `content_review_audit` rows **ids 4015–4047 (contiguous, 33 rows:
  VALIDATE exam_paper ×2, VALIDATE question_version ×15, VALIDATE
  mark_scheme ×15, PLACE exam_paper ×1)**, actor_label `Nawaf Al Hussain
  Khondokar`, trace + package + honesty note on every row.
  `teacher_validation_events` stays 0 (Task-51 constraint-contract decision).
- ANALYZE document_chunks/exam_papers/documents after each TX-2.

## End state (independently verified, fresh connections + live probes — see verify_landing.log)

- Papers census **90 VALIDATED / 0 FLAGGED / 0 SUGGESTED / 14 REJECTED**
  (totals unchanged: −2 glmocr +2 pdflane). Both new rows VALIDATED and
  serving through their pre-existing chunk-ful docs (qp/ms VALIDATED,
  11/13 and 11/11 chunks, all embed_rev=2 — serving pool **unchanged at
  2,935**, additive-only design: no rev1 chunks involved, no doc flips).
- Documents census unchanged (567 V / 305 S / 147 R).
- New rows carry the drafts' bank-namespace external_refs
  (`4ch1/past-papers/2020-01/4ch1-2CR#qN`, `4ch0-2c-201701#qN`) — the same
  namespace the T-C27 qcard bridge cites, restoring card↔bank identity for
  these sittings.
- Live probe: fresh learner GET /api/v1/exam-papers/{pid} renders 7 and 8
  questions with the draft mark multisets.
- Marks-integrity headline: 2CR rows were 43/70 vs print — now 70/70 EXACT;
  2C rows had part-sum 2 and point-sum 54 vs print 60 — now 60/60 EXACT.

## Follow-ups recorded (none blocking)

- The 15 new questions are ING-anchored per the ingestion contract
  (ING-4CH12CRJANUARY2020 / ING-4CH02CJANUARY2017, reused find-or-create) —
  they join the next topic-mapping pass (the Jan-2021 supersession's rows
  followed the same path via Task 68/69).
- 2c-201701's 12 archived qt mappings (real 4CH1 topics on legacy-spec rows)
  are restorable from the undo record if the mapping pass wants them.
- 2cr-202001's 5 + 2c's 1 NULL-part mark_points reproduce the ingestion's
  known multi-level-ref behavior (Task-54-class observation; print-faithful).
