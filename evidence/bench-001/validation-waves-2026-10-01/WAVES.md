# Validation waves — wave 1 kit (T-C41, 2026-10-01, snapshot snap-006)

**Status:** READY FOR OPERATOR EXECUTION — composed deterministically from the committed
T-C40 worklist; every number traceable to snapshot bytes. **No validation is asserted here**
(AGENT.md core rule 6): the validate-all calls are teacher-surface actions (pilot-teacher
credential, operator-held per T-C38).

## Wave 1 units (top 4 by gold unlock, QP+MS merged — one validate-all per paper)

1. **4CH1/2C** — QUESTION_PAPER chunks 207 (SUGGESTED 164); MARK_SCHEME chunks 232 (SUGGESTED 186); EXTERNAL_QUESTIONS chunks 168 (SUGGESTED 87). Wave unlock: **60 tier-1** + **4 tier-2** gold queries across 10 classes (calculation, conceptual, exam_question, factual, mark_scheme, misconception, multi_spec_point, prerequisite, vague_learner, why_wrong).
2. **4CH0/2C** — QUESTION_PAPER chunks 218 (SUGGESTED 178); MARK_SCHEME chunks 218 (SUGGESTED 176); EXTERNAL_QUESTIONS chunks 143 (SUGGESTED 117). Wave unlock: **34 tier-1** + **4 tier-2** gold queries across 10 classes (calculation, conceptual, exam_question, factual, mark_scheme, misconception, multi_spec_point, prerequisite, vague_learner, why_wrong).
3. **4CH1/2CR** — QUESTION_PAPER chunks 123 (SUGGESTED 103); MARK_SCHEME chunks 176 (SUGGESTED 152); EXTERNAL_QUESTIONS chunks 90 (SUGGESTED 65). Wave unlock: **42 tier-1** + **2 tier-2** gold queries across 9 classes (calculation, conceptual, exam_question, factual, mark_scheme, misconception, multi_spec_point, prerequisite, why_wrong).
4. **4CH1/1C** — QUESTION_PAPER chunks 259 (SUGGESTED 231); MARK_SCHEME chunks 307 (SUGGESTED 274); EXTERNAL_QUESTIONS chunks 212 (SUGGESTED 120). Wave unlock: **52 tier-1** + **1 tier-2** gold queries across 7 classes (calculation, conceptual, factual, misconception, multi_spec_point, prerequisite, why_wrong).

Combined wave-1 reach: **188 tier-1 + 11 tier-2 gold queries** become
potentially reachable — the precondition for any recall movement the next §8.1-governed run can measure.

## Execution order per unit (binding)

1. **Prestate probe** (`prestate.sql`, read-only): record paper_id, paper/doc validation states,
   chunk/embed/rev census, bridge reconciliation status. If `bridge_status = REVIEW_REQUIRED`:
   STOP — review findings item-by-item via the workbench; only `force=true` overrides, and that
   is an operator judgment, never a default.
2. **validate-all** (teacher auth; `validate_calls`): `POST /api/v1/teacher/content/exam-papers/{id}/validate-all`.
   Fail-closed on FLAGGED/REJECTED papers or REJECTED/FLAGGED versions — resolve first.
3. **Paired rev re-stamp** (`restamp.sql`, guarded write): re-stamps ONLY this paper's
   `embed_rev = 1` embedded chunks to `embed_rev = 2`, and only when the paper row is now
   VALIDATED. Skip silently-degenerates: if prestate `at_rev1 = 0`, no re-stamp is needed
   (rev2-born corpus serves immediately). AGENT.md rule 2: `scripts/campaign_db_preflight.py`
   runs before any write.
4. **Serving postcheck** (`poststate.sql`, read-only): `reachable_at_rev2` MUST increase by the
   unit's expected chunk count (prestate SUGGESTED ∩ embedded). A zero delta = the T-C23
   empty-funnel trap — stop, diagnose via `X-Search-Empty-Cause`/`diagnoseEmpty` before the
   next unit.
5. **Evidence pack** per wave: `prestate.json`, `validate-<paperId>.json` (the API's BatchResult),
   restamp rowcount, `poststate.json`, `SHA256SUMS` — under
   `evidence/bench-001/validation-wave-1-<date>/` (house pattern).

## Why this exact order (the two recorded traps)

- **The rev1 trap:** CURRENT_EMBED_REV = 2 (core `ChunkVectorRepository`); the 09-28 cut-over
  re-stamped only the 965 already-VALIDATED chunks. A validate-all WITHOUT the paired re-stamp
  validates the paper but serves nothing — the empty funnel returns with a new cause.
- **The REVIEW_REQUIRED trap:** bridge records with reconciliation findings block validate-all
  unless forced; forcing past unreviewed findings is how mis-validated content enters the
  serving pool. First pass never forces.

## After wave 1

- Re-run `bench/validation_worklist.py` against a FRESH snapshot re-freeze (the worklist's
  SUGGESTED counts are snapshot bytes, not live DB) OR rely on the live poststate probes;
  then the **Run005C re-record** (run-005-c-r8) measures the reachable-pool delta against the
  §8.1 v1.1 VALIDATED bars. Waves and re-records alternate: validate → re-freeze/re-record →
  read the bars → validate the next wave.
