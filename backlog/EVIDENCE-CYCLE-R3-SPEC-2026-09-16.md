# Evidence Cycle r3 — Post-Fix Verification Round Specification (2026-09-16, Session 76)

**Status: PREPARED — not executed.** Everything below is specified against
the existing, committed production workflows (`s2-evidence-cycle.yml` phases)
and the verified data state (Session 75 reconciliation). Nothing here has
been dispatched; r3 requires the Actions path back (its vehicle is a
GitHub Actions workflow) and will be marked VERIFIED only when actually run.
No synthetic learner evidence is created by this specification; the round
uses the same honestly-labeled controlled-remediation-input pattern as r2.

## What r3 must prove (the acceptance question)

After the `fe01b87` fix (evidence fires at the COMPLETING mark, once, with
the settled total) and the Session-75 data reconciliation, **does a live
multi-part remediation attempt get correctly credited through the deployed
app?** Specifically:

1. A structured attempt with full-mark parts, marked part-by-part, must fire
   exactly ONE evidence event — at the completing mark — carrying the
   settled total and `correct=true` (the r2 defect mis-fired at part-`a`
   partial totals with `correct=false`).
2. The learner's Smart Lesson on the topic must show the honest measured
   value consistent with the new evidence (no INSUFFICIENT_COVERAGE
   regression; LOW_MASTERY band is expected and legitimate — the ceiling is
   0.45 and one more correct round does not have to cross it).
3. The learner-state projection (`skill_states`) must advance consistently
   with the event (attempts+1, correct_count+1 if full-mark, BKT posterior
   from the current verified value `0.3135593220338984`), and the
   whole-projection audit must stay clean (zero mismatches) after the round.
4. The class aggregation must propagate the same evidence (mean moves only
   by the monitor's contribution).

## The vehicle (existing, unchanged)

The `s2-evidence-cycle` workflow (syllabai-web), exactly as r1/r2 ran:

```text
phase=after   → weakness re-read → targeted test preview → NEW attempts
                (monitor learner, answer-key inputs, honestly labeled) →
                smart-lesson before/after
phase=mark    → the teacher's r3 marks manifest applied through the
                marking contract (manifest committed + sha-pinned first)
phase=final   → smart-lesson response + class view after marked evidence
```

Plus the data-level audit (read-only, the Session-75 path or the new t0
capture): post-round projection audit + event-level inspection.

## r3 learner cohort

- **Actor:** the pilot monitor learner (the real enrolled TEST-classified
  account, `pilot.monitor@syllabai-test.dev`) — the same account r2 used,
  whose state is the verified `0.3135593220338984` on 4CH1-S2-f.
- **Class context:** the 8 measured learners on 4CH1-S2-f (unchanged by r3
  except the monitor's own row).
- **No other learner is touched.** The concurrent CLA lane's 2 PENDING
  attempts (`web-structured-v1` provenance) remain untouched per §12.

## r3 question set (selection, read-only)

The `after` phase selects deterministically: the learner's servable list on
the weakest targetable topic. Expected today on 4CH1-S2-f: the same 3
servable VALIDATED questions r2 used (`96ae4235…`, `ac5045d7…`, `ddf30066…`)
— re-attempting them is the loop's design (targeted remediation of the weak
topic). The phase re-reads weakness-options live, so if the target selection
changed since r2 the artifact records the new target with its reasons; the
specification does not hard-code the topic, only the selection rule
(most measured learners → weakest mean → code), which is the workflow's
existing deterministic order.

**Precondition check (read-only, at dispatch time):** the 3 questions remain
servable (active, VALIDATED current version, paper VALIDATED); the monitor
learner's state is still the verified baseline (version 3); no PENDING r2
answers remain on the account.

## r3 marks manifest (authored when the dump exists)

The `mark` phase requires a committed manifest (`scripts/ops/
s2_marks_manifest_r3.json`, sha passed to the workflow). It is authored
**after** the `after` phase's dump shows the new PENDING attempts, from the
teacher's honest judgment against the mark scheme — the r2 pattern (17
part-level decisions, per-point comments). The manifest is NOT pre-authored:
pre-writing marks for attempts that do not yet exist would be manufacturing
evidence. What is pre-specified here is only the manifest's shape and the
honesty rules: per-part decisions against the scheme points, zero-invented
marks, conflicts fail closed.

## r3 evidence verification (what gets checked, at the data level)

After `mark` completes — using the t0-capture instrument's sections as
read-only queries (or the Session-75 investigation script pattern):

1. **Event timing:** for each r3 structured attempt, exactly one BKT_UPDATED
   telemetry row exists, its `occurred_at` ≥ the completing part's mark
   timestamp (not the first part's), `payload.marksAwarded` = the settled
   total, `payload.correctness` = the full-marks rule result.
2. **Projection consistency:** the monitor's `skill_states` row advanced by
   exactly the r3 evidence (attempts 3→3+n, correct_count 2→2+k, mastery =
   BKT posterior of the verified value over the r3 correctness sequence,
   version +n).
3. **Whole-projection audit:** zero mismatches across all `skill_states`
   rows (the T0.7 query).
4. **Smart Lesson:** the `final` probe's action/reason carries the honest
   post-r3 measured value; same policy version (smart-lesson/v2).
5. **Class propagation:** mean of stored mastery moves only by the monitor's
   delta; learners_measured unchanged (8).

## Post-round audit (the r3 closing checklist)

- All checks above recorded in the cycle record with run ids + timestamps.
- The r3 artifact appended to `evidence/cycle-001/` (or a sibling cycle-002
  dir if the operator prefers a new round id) with the same structure as the
  r2 reconciliation artifacts.
- Statuses updated: fix chain PRODUCTION VERIFIED (app-level) — the last
  open gate of the pilot readiness checklist besides CI.
- **t0 captured** (per `EVIDENCE-ACCUMULATION-T0-PROCEDURE-2026-09-16.md`)
  after r3 closes, before any new pilot evidence event.

## Blocking dependencies (honest)

- **GitHub Actions quota** — the `s2-evidence-cycle` workflow must run
  (`CI = BLOCKED` until the monthly allowance resets; the quota sentinel on
  the public syllabai-ops repo detects restore automatically).
- **Teacher judgment** — the marks manifest requires the operator's honest
  marking pass (or an explicit delegation decision); it cannot be
  pre-authored.
- **The pilot monitor + teacher credentials** — Actions secrets, already in
  place from r1/r2.

## What r3 is NOT

- Not a new marking-path change (no code changes; the fix chain is frozen).
- Not a κ evaluation (the κ gate still waits for real mixed-award samples;
  r3's controlled inputs are not a legitimate κ basis — same stance as r2).
- Not the pilot itself (it is the last verification round before pilot
  entry; the pilot's own evidence accumulation starts at t0).
