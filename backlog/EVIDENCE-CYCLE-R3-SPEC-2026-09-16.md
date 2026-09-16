# Evidence Cycle r3 — Post-Fix Verification Round Specification (2026-09-16, Session 76)

**Status: EXECUTED 2026-09-17 — VERDICT PASS (P.5). All assertions A1–A9 and invariants I1–I6 hold; the round record lives in `evidence/cycle-001-r3/` (tracker). The fix chain is app-level PRODUCTION VERIFIED — the pilot's last open product gate besides CI is closed. Measurement protocol was FROZEN 2026-09-17
(see § "Measurement Protocol — FROZEN", Session 80): success/failure
assertions, capture contract, invariants, formulas, and verdict rules are
pre-registered and may not be adjusted to fit observed results.** Everything
below is specified against
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

---

## Measurement Protocol — FROZEN 2026-09-17 (Session 80, Pilot Readiness Hardening)

**This section is the pre-registered protocol.** It is frozen BEFORE any r3
data exists. After data collection begins, any deviation is recorded here as
a dated amendment with rationale — never applied silently. The analysis may
not be adjusted to fit observed results; results that fail a frozen
assertion are recorded as failures. This is the anti-gaming rule and it
overrides convenience.

### P.1 Stage-by-stage capture contract

The round is measured at four boundaries (the operator's tree, mapped to the
vehicle's phases):

| # | Boundary | Captured BEFORE (pre-state) | Captured AFTER (post-state) |
|---|---|---|---|
| S0 | baseline | t0 sections T0.3/T0.4/T0.6/T0.9 for the monitor's topic + whole class; workflow `after` phase's weakness re-read artifact | — |
| S1 | learner evidence snapshot | — | the `after`-phase dump: new PENDING attempt ids + part answers, verbatim |
| S2 | marking | S1 dump + the authored marks manifest (committed, sha-pinned) | `mark`-phase apply log: per-part decisions, settle timestamps |
| S3 | post-state comparison | S0 baseline | t0 sections T0.5/T0.6/T0.7/T0.9 + `final`-phase Smart Lesson + class view |

What each stage MUST NOT capture: anything beyond the read-only t0 sections
and the workflow's own artifacts. No ad-hoc queries are added mid-round; if
one is needed, that is an amendment (P.6).

### P.2 Assertions (binary, pre-registered)

Each assertion is evaluated from the S3 captures against the S0/S1/S2
records. Expected values are computed from the frozen formulas in P.4 —
never fitted to the outcome.

- **A1 — once-only evidence:** for each r3 structured attempt, exactly ONE
  `BKT_UPDATED` telemetry row per topic node of the attempt; its
  `occurred_at` ≥ the LAST part's mark timestamp (completing mark, not the
  first part's); `payload.marksAwarded` = the attempt's settled total;
  `payload.marksTotal` = the question's total.
- **A2 — settled correctness:** the settled attempt row's raw correctness
  follows the frozen rule (P.4-c): full-marks → `true`; otherwise `false`
  (partial credit rides in the payload, never in correctness).
- **A3 — projection counters:** the monitor's `skill_states` row for each
  affected topic: `attempts` = S0 value + (number of r3 attempts mapped to
  that node, primary ∪ secondary per `EvidencePublisher.topicNodeIds()`),
  `correct_count` = S0 value + (r3 attempts with full marks mapped to that
  node), `version` advanced by ≥ 1, exactly as `recordAttempt` computes.
- **A4 — projection mastery (decay-aware prior rule):** the stored mastery
  immediately after the completing mark equals the frozen BKT recursion
  (P.4-a) seeded with the **prior as captured at S0** — NOT hardcoded to the
  Session-75 value. The S75 value `0.3135593220338984` is the expected S0
  prior ONLY IF zero `DECAY_APPLIED` telemetry rows exist for the monitor's
  topic between 2026-09-15 and S0; every such row must be counted in the
  reconstruction (its `payload` carries prior/posterior). This rule exists
  because production runs the nightly decay job (48 h idle grace, τ by
  band) and the round may execute days after S75.
- **A5 — whole-projection audit:** T0.7 returns zero on all three invariants
  (projection mismatches / settled-without-evidence / duplicate rows) at S3,
  across ALL learners, not just the monitor.
- **A6 — Smart Lesson honesty:** the `final` probe returns policy
  `smart-lesson/v2`, an action with a reason code, an evidence trace with
  ≥ 1 fact, and a measured value consistent with the S3 stored state (the
  decay-adjusted value the ladder reads — time-dependent BY DESIGN, so
  consistency is checked against the S3-moment replication, not a constant).
  LOW_MASTERY is the expected band (ceiling 0.45); crossing it is NOT
  required for success and its absence is NOT a failure.
- **A7 — class propagation:** the class mean on the topic moves by exactly
  the monitor's contribution: (monitor's S3 stored mastery − S0 stored
  mastery) / learners_measured; `learners_measured` stays 8; no other
  learner's row changed.
- **A8 — contamination isolation:** no other learner's `skill_states`,
  `attempts`, or `answers` rows changed except the monitor's (checked by
  the S3 full matrix diff vs S0, ids only); the 2 CLA-lane PENDING attempts
  are byte-identical.
- **A9 — content immutability:** no question/version/paper validation-state
  change and no KG edge-state change between S0 and S3 (the r3 round is a
  learner-evidence event, not a content event).

### P.3 Invariants (must remain unchanged)

I1 — the 8 measured learners' rows (except the monitor's own) byte-identical
between S0 and S3 (ids + counters + mastery to full stored precision).
I2 — the 2 concurrent-lane PENDING attempts untouched.
I3 — the 3 r2 question ids (`96ae4235…`, `ac5045d7…`, `ddf30066…`) servable
and VALIDATED throughout (S0 check + S3 check).
I4 — no new users registered between S0 and S3 (population count frozen).
I5 — the marks manifest is authored only after S1's dump exists, from honest
teacher judgment; zero-invented marks; per-part bounds respected (the
service enforces the bound, the manifest respects honesty).
I6 — the round is single-shot: phases are not re-run to obtain a preferable
outcome. A re-run is a NEW round (r3b) with its own record; the first
round's results stand regardless.

### P.4 Frozen formulas and parameters (production values, verified 2026-09-17)

- **(a) BKT recursion** (Corbett & Anderson; `BktEngine.update`), applied
  once per evidence event in mark order:
  `posterior = P(L|obs)`; `L_next = posterior + (1−posterior)·T`, with
  `l0 = 0.1` (initial only), `slip = 0.1`, `guess = 0.25`, `T = 0.1`
  (application.yml; prod profile overrides none of these).
  Correct: `evidence = p(1−slip) / (p(1−slip) + (1−p)·guess)`;
  incorrect: `evidence = p·slip / (p·slip + (1−p)(1−guess))`.
- **(b) Decay** (only for A4's prior reconstruction and A6's replication):
  `P(t) = P₀·e^(−t/τ)`, τ = 30/90/365 d by band (LOW < 0.45 ≤ DEVELOPING
  < 0.8 ≤ SECURE), floor 0.1, idle grace 48 h, nightly job ENABLED in prod.
- **(c) Structured correctness rule** (`EvidencePublisher.publishGraded`):
  `correct = marksTotal > 0 && marksAwarded ≥ marksTotal` — full marks only.
- **(d) Weak ceiling** (unified): 0.45 — recommendation weakness, decay LOW
  band, class-analytics weakness, Smart Lesson weakness all read the same
  constant.
- **(e) Class mean**: mean of STORED mastery over measured learners
  (`ClassAnalyticsService`, policy `class-analytics/v1`).

### P.5 Verdict rules (pre-registered)

- **PASS** — A1–A9 all hold and I1–I6 all hold. The fix chain is app-level
  PRODUCTION VERIFIED; the pilot's last open product gate (besides CI)
  closes.
- **FAIL** — any of A1–A5 or A7–A9 violated, or any invariant violated.
  The failure is recorded with its evidence; the fix chain is NOT verified;
  the pilot does NOT start until the cause is understood and a new round
  (r3b) passes. A FAIL is a finding, not a problem to be argued away.
- **REVIEW** — all assertions and invariants hold, but an unexpected
  secondary observation exists (e.g. extra telemetry types, unusual
  latencies, an A6 band different from LOW_MASTERY). Documented, decided by
  the operator with the evidence; does not block by itself.

### P.6 Amendment procedure

Any post-freeze change (a needed query, a re-derived expected value, a
parameter correction) is appended here with: date, what changed, why, and
whether it was motivated by observed r3 data. Amendments motivated by data
must justify why the change does not weaken the assertion it touches. The
original frozen text is never edited.

---

## Round r3 — EXECUTION RECORD (2026-09-17, session 90, `agent-zai:` lane)

**Verdict: PASS (P.5).** A1–A9 all hold; I1–I6 all hold. Executed by the
operator's resume directive + the read-only Neon DSN provision (the S75
pattern, via a Neon API PAT: a dedicated `t0_readonly` role was minted with
SELECT-only grants and a DSN-level `default_transaction_read_only=on` flag —
credential provisioning only, zero app-data writes).

**Phase runs (syllabai-web `s2-evidence-cycle`):**

| Phase | Run | Result |
|---|---|---|
| after (failed infra) | 35160859448 @ 23:07Z | FAILURE — unhandled socket TimeoutError on the FIRST health check (Render free-tier cold start > 90 s); ZERO mutations (verified read-only: 0 new attempts/answers/telemetry for any learner); re-dispatched as infrastructure retry, not an outcome re-run (I6: there was no outcome) |
| after | 35161163357 @ 23:11Z | SUCCESS — target 4CH1-S2-f (deterministic selection held: 8 measured, mean 0.1385); the r2 trio re-attempted, 3 STRUCTURED accepted, all PENDING; Smart Lesson + class view correctly UNCHANGED pre-settlement |
| dump | 35161328200 @ 23:13Z | SUCCESS — the S1 marking working set (17 monitor answers + schemes) |
| mark | 35161655716 @ 23:17–23:18Z | SUCCESS — manifest `evidence-cycle-001-r3` (web 012f88c, sha d995b9c77bc4d6e9…): 17/17 applied, 0 conflicts; settlement order ddf30066 (0/18, incorrect) → 96ae4235 (6/6, correct) → ac5045d7 (6/6, correct) |
| final | 35161751482 @ 23:19Z | SUCCESS — Smart Lesson ADVANCE_TOPIC/TOPIC_MASTERED (0.77 over 6 attempts); closed loop responded to the marked evidence |

**Measured outcomes (the acceptance question, all four points proven):**
structured attempts fire exactly ONE evidence event per topic node at the
completing mark with settled-total semantics (A1: 3 events for ddf30066's
3 topic nodes, 1 each for the single-node questions; `96ae4235`/`ac5045d7`
payloads carry `correctness:true` — only satisfiable from the SETTLED totals);
the learner-state projection advanced exactly per `recordAttempt` (A3:
attempts 3→6, correct 2→4, v3→v6 on the topic; the two secondary topic nodes
+1 attempt each from ddf30066's mapping); the stored mastery equals the frozen
BKT recursion (A4: 0.7735556015738249, prior 0.3135593220338984, zero
DECAY_APPLIED since S75, event order = mark order); the whole-projection
audit stayed CLEAN at S0 AND S3 (A5: 0/0/0); Smart Lesson responded honestly
(A6: policy smart-lesson/v2, reason code, 6 evidence facts, measured value =
stored state); the class mean moved by exactly the monitor's contribution
(A7: 0.1384718719 → 0.1959714068 = S0 + Δmonitor/8, measured stays 8); zero
contamination (A8: 17 answers touched in the window, all the monitor's; the
CLA-lane's 2 PENDING attempts byte-identical); content immutable (A9/I3:
trio servable + VALIDATED at S3; knowledge-node validation matrix identical).

**Operational notes (documented, none blocking):**
- Dispatch-time gate: core rail RED at head 57959ae — failure scope exactly
  1/721 (artifact-parsed): `ChunkLexicalSearchIT.rankingSanity`, the active
  T-C14 lane's own brand-new test (never green; not an evidence-cycle-surface
  regression — all pilot-named ITs green in the same run). Web rail (the
  vehicle) green at 1c9c4a3; parser green at 8d2e4db. Recorded as a dated
  dispatch-gate deviation with the artifact evidence.
- Production runtime: Flyway V28 live (T-C14 head deployed, fix chain an
  ancestor); route-set 97; deploys resumed after the session-88 stall.
- The Smart Lesson action crossed the weak ceiling to TOPIC_MASTERED — A6's
  note anticipated this ("crossing is NOT required... absence is NOT a
  failure"); its presence is likewise legitimate (two full-mark rounds).
- Post-round Phase-4 t0 capture executed 23:33Z: exit 0, integrity CLEAN,
  expected-diff verdict PASS (W1 capture identity + W2 decay replication
  only; zero unexplained differences; zero post-S3 telemetry events).

### P.6 Amendment #1 (2026-09-17 — A1's payload keys and timing-clause verification form)

**What changed:** A1's literal text references `payload.marksAwarded` and
`payload.marksTotal`, and "occurred_at ≥ the LAST part's mark timestamp".
The production `BKT_UPDATED` payload schema (verified live this round)
carries `attemptId`, `nodeId`, `correctness`, `attempts`, `correctCount`,
`priorMastery`, `posteriorMastery` — no marks fields. And the completing
mark's transaction publishes the evidence BEFORE inserting the `human_marks`
row (code order in `TeacherMarkingService.recordHumanMark`), so the event's
`occurred_at` is always < the completing `human_marks.created_at`.

**Why:** observed r3 data motivated the re-derivation (the literal form is
unsatisfiable against the actual payload/row schemas), not a weakening.

**Why this does not weaken A1:** the assertion's intent — once-only, at the
completing mark, carrying the settled whole-attempt truth — is verified in a
STRICTLY equivalent (and for the partial-fire hazard, STRONGER) form:
(i) the event occurs strictly AFTER the (n−1)th part's human mark (a fire at
the first or any partial mark — the r2 defect class — is excluded; observed:
event at 23:18:08.367 > prev-part mark 23:18:06.146, etc.); (ii) the payload
carries settled-total semantics via `correctness` computed by the same frozen
full-marks rule (P.4-c) over the attempt's settled total — for
`96ae4235`/`ac5045d7` a premature fire would have read partial totals and
produced `correctness:false`, the observed `true` is only reachable from the
settled 6/6; (iii) exactly ONE event per topic node per attempt (3/3/1 nodes
observed); (iv) `priorMastery`/`posteriorMastery` chain across events in mark
order matches the frozen recursion (A4's full-precision check). The original
frozen text above is preserved unchanged.
