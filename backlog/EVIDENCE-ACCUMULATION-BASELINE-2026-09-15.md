# Evidence Accumulation Baseline — t0 (2026-09-15)

**The measured starting state of the Evidence Accumulation / Closed-Loop Pilot.**
Measured from production evidence-cycle 001 (real teacher marking, real learner
attempts — `EVIDENCE-CYCLE-001-2026-09-15.md`, durable snapshots under
`evidence/cycle-001/`). This is a BASELINE, not a dashboard: every number below
exists to make the pilot's one question measurable — *does new learning evidence
cause the learner/class state and the next action to change correctly?*

**Contamination notice (§8 honesty):** the round-2 mastery figures reported by
cycle 001 carry the pre-`fe01b87` partial-total evidence defect. Status chain:

```text
REPORTED (cycle 001)                mastery 0.1153, class mean 0.1137
  → INVALIDATED BY ROOT-CAUSE ANALYSIS  (evidence fired at first-part partial totals)
  → CORRECTED (deterministic replay)    mastery 0.3136, class mean 0.1385
  → VERIFIED (Session 75, 2026-09-15)   recomputation EXECUTED 18:00:34 UTC on
                                        production (one guarded row repair, zero
                                        unintended changes) + post-fix data-level
                                        verification; live r3 round waits for Actions
```

The replay model is validated to the last digit: replaying the defective
sequence [F,F,F] reproduces the production `skill_states` value
`0.11533544411262374` EXACTLY (all 17 significant digits,
`evidence/cycle-001/reconciliation.json`). The corrected sequence [T,T,F] is
what the settled attempts earned (6/6, 6/6, 0/18 → full-marks rule).

## Learner baseline

| Metric | t0 value | Notes |
|---|---|---|
| Structured answers sat (cycle) | 255 + 3 targeted | 255 backlog (r1, all probe/E2E placeholders, honest 0) + 3 targeted (r2, controlled remediation input, honestly labeled) |
| Marked attempts | 255/255 (r1) + 3/3 (r2) | 272 part-marks total (255 + 17), all through the marking contract, zero conflicts |
| Evidence events | 55 | 52 after r1 + 3 after r2; 3 fired at partial totals (the defect); 2 of those carry wrong correctness (Q1 4/6→F vs settled 6/6→T; Q2 1/6→F vs 6/6→T); Q3 0/18 was correct as fired |
| Learners with evidence | 29 | across 8 curriculum topics after r1 |
| Cohort mastery (r1 topics) | ~0.113 | all-incorrect observations from the placeholder backlog; prior L0=0.1 |
| Monitor learner, 4CH1-S2-f | 0.1153 REPORTED → 0.3136 CORRECTED → **VERIFIED** | attempts=3, correct=2 (was 0); BKT params L0=0.1/slip=0.1/guess=0.25/T=0.1; row repaired 2026-09-15 18:00:34 UTC, version 2→3 |
| Misconception signals | 0 | structured evidence carries no misconception ids (MCQ-only path); none manufactured |
| Smart Lesson decisions | 1 documented change | monitor learner on 4CH1-S2-f: INSUFFICIENT_COVERAGE → LOW_MASTERY — the CODE changed for the right reason (coverage established); the measured VALUE in the reason was contaminated (0.12; corrected 0.31) |
| Recommendation changes | 1 | same event; smart-lesson/v2 deterministic ladder, evidence trace carried attempts + raw/decay-adjusted mastery |

## Class baseline

| Metric | t0 value | Notes |
|---|---|---|
| Measured learners (4CH1-S2-f) | 8 | 7 after r1 + the monitor after r2 |
| Measured topics | 8 (of 325) | measured = real evidence only; 317 remain honestly unmeasured |
| Weak topics | 8 → 10 | 8 after r1 (all LOW_MEAN_MASTERY with explicit reasons); 10 after r2's additional evidence |
| Coverage gaps (pre-marking) | 8→10 listed separately | weakness is NEVER inferred from absence of measurement — gaps and weak topics are distinct lanes |
| Evidence volume (4CH1-S2-f) | 14 evidence-backed attempts | at final probe |
| Class mean (4CH1-S2-f) | 0.1137 REPORTED → 0.1385 CORRECTED → **VERIFIED** | correction replaced the monitor's contaminated row only (exact live value 0.1384718718825788); still LOW — the topic legitimately remains weak |
| Targeted interventions | 1 | 4CH1-S2-f selected: most class evidence (7 measured) AND targetable (3 servable VALIDATED questions) |
| Post-intervention change | see learner rows | monitor: 0 (unknown) → 0.1153 REPORTED / 0.3136 CORRECTED; lesson INSUFFICIENT_COVERAGE → LOW_MASTERY |

## Teacher baseline

| Metric | t0 value | Notes |
|---|---|---|
| Marking throughput (r1) | 255 answers / ~17 min | ≈15 answers/min with Smart Mark assist first (queue-v2 order, per-paper grouping) |
| Marking throughput (r2) | 17 part-marks / ~35 s | the targeted-test round |
| Queue age | backlog cleared 255→0 | was ~249-255 pending since session-70; 10 CLA-lane answers remain for their own lane |
| Smart Mark assist | 105 provisional / 150 FAILED | honest failures: NO_SCHEME_POINTS / missing mark-scheme rows — fail-closed, no invented marks |
| κ evaluation | deliberately NOT run | placeholder-degenerate sample (all-zero awards) would manufacture κ≈1.0 and release Smart Mark authority on untested evidence |
| Targeted test creation | 1 | 4CH1-S2-f: 3 questions / 30 marks / 8 answer-key entries, VALIDATED-only, deterministic |
| Intervention targets | 1 topic / 8 learners | weakness → Test Builder → assigned through the existing surface |

## System baseline

| Metric | t0 value | Notes |
|---|---|---|
| Evidence-event correctness | **DEFECT FOUND** | 2 of 55 events carry wrong correctness (multi-part partial-total mis-fire); root cause: evidence fired at the first part's authoritative mark with the partial total; fixed core `fe01b87` (fires at the COMPLETING mark, once, with the settled total) |
| Regression invariant | PINNED both paths | human path (`TeacherMarkingServiceTest`) + κ-gated Smart Mark path (`SmartMarkServiceTest`, added 2d613d5) + the shared once-only CAS (`EvidencePublisherTest`, added 2d613d5): partial mark → no evidence; completing mark → ONE event with the full settled total; repeated processing → no duplicate |
| Duplicate-event rate | 0 | across 272 mark operations the once-only guard held — no duplicate evidence events |
| Settlement correctness | attempt rows correct | settled rows (6/6, 6/6, 0/18) always matched the part marks; the defect was event-vs-row DISAGREEMENT (timing), now pinned by regression |
| Recommendation determinism | held | smart-lesson/v2 versioned ladder; same state → same decision; the round-2 decision changed only because the evidence changed |
| API latency | no regression signal | cycle runs within normal bounds; monitor 18/18 green at 11:51 (pre-block) |
| N+1/query regressions | none introduced | `fe01b87` reuses the existing batched `findByAttemptIdOrderByQuestionPartId` per mark; no per-row loops added |

## Integrity boundary audit (all held at t0)

- PENDING never became learner evidence (255 r1 answers waited for marks).
- Partial marking became settled evidence **only via the defect** — fixed, both
  paths regression-pinned; post-fix production verification DONE at the data
  level (Session 75: whole-projection audit clean, corrected state verified;
  artifacts under `evidence/cycle-001/`).
- Smart Mark did not bypass the κ/human gates (never released; 105 provisional
  marks carried zero evidence).
- A single Tutor utterance changed no mastery (tutor signals feed priority, not
  mastery — no tutor-signal mastery writes exist).
- SUGGESTED/FLAGGED/REJECTED content never served (34 servable questions, all
  VALIDATED-only).
- Unknown evidence stayed unknown (317/325 topics unmeasured, never inferred).
- Class weakness was never inferred from absence (gaps and weak topics are
  distinct lanes with distinct reasons).
- No synthetic pilot activity was introduced to improve any metric above (the
  r2 attempts were honestly-labeled controlled remediation inputs; κ was
  deliberately left unevaluated).

## What must happen before t1 measurement

1. **Production recomputation of the contaminated row** — **DONE (Session 75,
   2026-09-15 18:00:34 UTC).** Executed exactly as prepared
   (`evidence/cycle-001/reconciliation.json`) via the operator-provided Neon
   API path: read-only investigation (whole-projection audit: exactly ONE
   mismatch — the known row), one guarded transaction (rowcount 1, exactly one
   of 47 rows changed), post-fix verification (audit clean; Smart Lesson
   LOW_MASTERY with the honest 0.31 value; class mean 0.1384718718825788).
   Artifacts: `evidence/cycle-001/reconciliation-investigation.json` +
   `reconciliation-execution.json` + `postfix-verification.json`.
2. **GitHub Actions restored** → CI verifies `fe01b87` + `2d613d5` +
   `04d621a` (511 local unit green; ITs need CI — no local Docker).
3. **Post-fix verification round** (`s2-evidence-cycle` phases after → mark
   r3 → final): re-attempt → mark → mastery trajectory must show
   correctly-credited full-mark attempts live. (The data-level half is DONE —
   Session 75; this gate is the LIVE app-level round, needs Actions.)
4. Teacher marking rhythm begins (the queue is the loop's clock).
