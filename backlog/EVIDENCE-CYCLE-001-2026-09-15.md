# Production Evidence Cycle 001 — 2026-09-15

**The first full teacher–learner loop run as PRODUCTION WORK, not a test.**
Every step below was executed against the live system (Render API / Neon DB /
Vercel frontend) by the operator-directed teacher workflow, with workflow run
IDs, timestamps and honest states. Nothing here is a fixture, a mock, or a
CI-only assertion.

## The chain, as it happened

| Stage | What happened | When (UTC) | Evidence |
|---|---|---|---|
| **PENDING** | 255 structured answers across 15 real Edexcel past papers sat PENDING; class mastery 0/325 topics measured; weakness lane: 0 weak / 8 coverage gaps | 11:51–11:54 | pilot-monitor run 34965596626 (18/18 green incl. web-bundle); s2-evidence-cycle dump run 34965972456 |
| **MARKED** | Teacher review of every pending answer against its part prompt + mark scheme points (all probe/E2E placeholders — honest mark 0, per-class comments). Smart Mark assist first: per-group batches, 105 provisional / 150 honest FAILED (NO_SCHEME_POINTS / missing scheme). Then 255/255 human marks applied through the marking contract — zero conflicts, queue cleared | 12:16–12:33 | smartmark run 34967933402; mark run 34968747628 (manifest sha 269f13b5…, committed) |
| **LEARNER EVIDENCE** | First authoritative mark per attempt fired the evidence contract: 52 evidence events over 8 curriculum topics; BKT mastery ~0.113 (all-incorrect observations, prior 0.1) | 12:33–12:35 | precheck run 34969674690: 29 learners with evidence |
| **CLASS EVIDENCE** | Class analytics populated: 8 topics measured, LOW mastery across the marked set | 12:34–12:35 | weakness options run: 8 weak topics, all LOW_MEAN_MASTERY |
| **WEAKNESS IDENTIFIED** | Weakness options: 8 weak topics with explicit reasons (LOW_MEAN_MASTERY), raw aggregates, no synthetic score. Target selected: **4CH1-S2-f (Acids, alkalis & titrations)** — most class evidence (7 measured learners) AND targetable (3 servable VALIDATED questions) | 12:40 | after-leg run 34970283178 |
| **TARGETED TEST** | Test Builder preview on the weak topic: 3 questions / 30 marks / 8 answer-key entries, VALIDATED-only, deterministic | 12:40–12:42 | same run |
| **NEW ATTEMPTS** | The pilot monitor learner (a real enrolled learner account) worked the targeted questions — 3/3 structured submissions accepted (answer-key texts as a controlled remediation input, honestly labeled), returning to PENDING for the next marking round | 12:41–12:42 | same run |
| **MARKED (round 2)** | The loop fed itself: teacher marked the 3 new attempts honestly — Q1 6/6 (apparatus + both litmus colours), Q2 6/6 (neutralisation + complete table + all three reasons), Q3 0/18 (empty submissions) — 17/17 part marks applied | 12:47 | mark run 34970915089 (manifest r2 sha ad99c75b…) |
| **SMART LESSON RESPONSE** | The learner's Smart Lesson on the targeted topic changed **for the right reason**: `INSUFFICIENT_COVERAGE` ("No attempt evidence on 4CH1-S2-f yet") → **`LOW_MASTERY`** ("Measured mastery 0.12 over 3 attempts is below the weak ceiling (0.45) — keep practising 4CH1-S2-f"), evidence trace now carrying attempts=3, mastery raw/decay-adjusted, topic status ESTABLISHED. Class view after: S2-f 8 measured learners, mean 0.1137, 14 evidence-backed attempts | 12:52 | final probe run 34971418531 |

## Defect found BY the cycle, fixed the same day

**Multi-part attempts fired evidence at the first part's mark with a PARTIAL
total.** The monitor's two 6/6 attempts fired as INCORRECT (4/6 and 1/6 at the
instant of their first parts' marks), so full-mark remediation never credited
mastery — measured 0.12 where ~0.31 was earned. The settled attempt row
(`correct=true`, 6/6) and the evidence event (`correct=false`) disagreed,
which is exactly what `Attempt.recordTotalMarks`' contract forbids ("raw-column
consumers agree with the evidence event").

**Fix (core `fe01b87`)**: the evidence event now waits until the attempt has no
PENDING answer rows, then fires ONCE with the settled full total — same
once-only guard, same fail-closed stance; single-part attempts behave exactly
as before; the κ-released Smart Mark path gets the same completion rule. New
multi-part regression test pins it (part-a mark → no evidence; completing mark
→ one event, full total, correctness true). Local unit suite 495 green.

Already-fired events are immutable by design; the three mis-observed events
remain as historical data. Post-fix attempts observe correctly.

## Post-fix verification (2026-09-15, same day — statuses updated)

- **`fe01b87` — IMPLEMENTED / LOCALLY VERIFIED (strengthened) / CI
  VERIFICATION BLOCKED — ACTIONS QUOTA.** Local unit suite on main `95093d7`
  (contains `fe01b87` untouched): **510 green** (1 pre-existing skip), up from
  495 — the post-fix round added the same invariant proof for the SECOND
  marking path and for the shared guard (core `2d613d5`): the κ-released
  Smart Mark multi-part regression (part-a authoritative mark with part b
  PENDING → NO evidence; completing mark → publishGraded exactly once, full
  settled total) and `EvidencePublisherTest` (the once-only CAS pinned
  directly: repeated `publishGraded` after firing is a no-op emitting
  nothing; settled-total + conservative-correctness payload; `publishMcq`
  fails closed on duplicate submit). ITs unchanged and awaiting CI (no local
  Docker).
- **Contamination reconciled deterministically**
  (`evidence/cycle-001/reconciliation.json`, generator
  `scripts/ops/s2_reconcile_evidence.py` in web): replaying the defective
  sequence [F,F,F] reproduces the production value `0.11533544411262374`
  EXACTLY — the replay model is validated to the last digit. Corrected
  replay [T,T,F] (what the settled attempts earned): **mastery 0.3135593,
  attempts=3, correct=2; class mean 0.1137 → 0.1385** (still LOW — S2-f
  legitimately remains a weak topic). Decision: **deterministic
  RECOMPUTATION, not reset** — the settled attempt rows are the ground
  truth, `skill_states` is a rebuildable projection, the evidence events
  stay immutable (audit + κ pairing). The guarded repair SQL + rollback are
  prepared in the reconciliation artifact; execution BLOCKED on an operator
  path to the production DB (no Neon DSN / Render token available to the
  agent; Actions secrets are write-only). The old 0.12/0.1137 values are
  REPORTED → INVALIDATED BY ROOT-CAUSE ANALYSIS → CORRECTED; VERIFIED only
  after the recomputation lands and the post-fix round confirms.
- **The deferred `correct: null` gap — now FIXED** (core `04d621a`):
  classified by contract inspection as a semantic API defect, not intentional
  representation — the `AttemptHistoryView` DTO documents `correct` as null
  "UNTIL an authoritative mark exists" (a temporary state) but the
  implementation never populated it for structured attempts. Smallest fix:
  once every part is authoritatively marked the item carries the settled
  row's own classification (the same conservative full-marks rule the
  evidence event used); pending stays null. Unit regression added (settled
  full marks → true; partial → false with the summed total); the flow IT
  strengthened (correct=true after the human full-mark). Full suite **511
  green** locally. Web `HistoryView` comment updated (no logic change).
- **Frontend re-verified anonymously post-cycle:** §8–§10 markers still
  present in the live Vercel bundle ("Target class weaknesses",
  ACTIVE_MISCONCEPTION_PRESENT, weakness-options client fn); backend
  `/actuator/health` UP.

## Honest states (§20)

- **VERIFIED**: the full chain above (production runs, artifacts downloadable);
  Vercel block resolved (PAT deployment `dpl_J93ocENkMuxXX4UYih5XfMjdWBrr` of
  main `8a63f5d` READY; deployed bundle carries all §8–§10 markers; official
  pilot-monitor 18/18 green including web-bundle for the first time since
  session-69).
- **PARTIAL**: core `fe01b87` (the evidence-timing fix) — unit-tested locally
  (511 green after the same-day post-fix round: the both-path invariant tests
  `2d613d5` and the settled-classification fix `04d621a`) but **CI BLOCKED**:
  the org's GitHub Actions began failing every
  workflow instantly (even a one-step echo) at ~13:02 UTC while the platform
  status is operational — consistent with Actions minutes/spending-limit
  exhaustion. The concurrent CLA lane's pushes are equally blocked. Render
  auto-deploy is webhook-driven and presumed applied; not independently
  verifiable without the Render token.
- **BLOCKED (operator actions)**: (1) restore GitHub Actions (billing/minutes)
  so CI can verify `fe01b87` and the evidence-cycle workflows can run again;
  (2) the post-fix production verification round (re-attempt → mark → observe
  correctly-credited mastery rise) is designed and ready
  (`s2-evidence-cycle.yml` phases `after`/`mark`/`final`) but needs the
  Actions path back.
- **FOUND, FIXED same day**: `AttemptHistoryView.correct` stayed null for
  structured attempts after marking settled — classified by DTO-contract
  inspection as a semantic API defect (the contract documents null "UNTIL an
  authoritative mark exists"); fixed in core `04d621a` with unit + IT
  regressions (511 local green).
- **Left for its lane**: 10 new PENDING answers from the concurrent CLA eval
  bundle (created 12:43–12:47) — untouched per the concurrent-lane protocol.
- **Deliberately NOT done**: κ/evaluate. All 255 round-1 answers plus the
  round-2 set carry paired per-point decisions (κ pairing data exists now),
  but the sample is placeholder-degenerate (all-zero human awards); releasing
  Smart Mark authority on it would be manufacturing a gate pass. κ waits for
  real mixed-award answers from the pilot.

## Vercel resolution (the session-69 operator block)

- Team invite is IMPOSSIBLE on the Hobby plan (`invites_not_allowed`) — the
  dashboard path is closed without a plan upgrade.
- The documented PAT path works: `POST /v13/deployments` (gitSource ref=main)
  deploys without touching the commit identity. Executed: deployment
  `dpl_J93ocENkMuxXX4UYih5XfMjdWBrr` READY in ~15 s; aliases live; bundle
  verified (7/7 markers incl. "Target class weaknesses" and the
  ACTIVE_MISCONCEPTION_PRESENT reason badges); API base + §8–§10 client
  functions inlined.
- Residual: pushes to web main still create BLOCKED git deployments
  (TEAM_ACCESS_REQUIRED for the nawaf-al-hussain author). PAT-deploy on
  demand remains the workaround; the deployed bundle (`8a63f5d`) contains
  all §8–§10 UI — later commits are ops-scripts only.

## Artifacts

- Workflow runs (SyllabAI/syllabai-web, `s2-evidence-cycle`): dump
  34965972456 / 34966559211 (topic pass) / 34971171486 (round-2 dump),
  smartmark 34967933402, mark 34968747628 (r1) / 34970915089 (r2), precheck
  34967504208 / 34969674690, after 34970283178, final 34971418531.
- Marks manifests (committed, sha-pinned): `scripts/ops/s2_marks_manifest.json`
  (255 decisions, sha 269f13b5…) and `scripts/ops/s2_marks_manifest_r2.json`
  (17 decisions, sha ad99c75b…).
- Monitor: pilot-monitor run 34965596626 — 18/18 green, web-bundle green.

## Reconciliation EXECUTED (2026-09-15 18:00:34 UTC — Session 75 amendment)

The operator provided a Neon API key (org-scoped) for this session; the
prepared recomputation was then executed EXACTLY as documented above — no
second repair mechanism was introduced.

- **Access path (non-destructive):** Neon API v2 → the SyllabAI org's single
  production project → branch `production` → database `neondb`, PG 18.6,
  Flyway V26 — matching the deployed schema (exact resource ids deliberately
  not recorded in tracked files; they live in the operator's Neon console
  and the local session artifacts). The role password was retrieved via the
  API's read-only `reveal_password` endpoint (`neondb_owner` — NO password
  reset, NO rotation, NO app-visible change; the Render service's
  connections were never disturbed). No credentials are stored in any
  tracked file.
- **Read-only investigation first** (`evidence/cycle-001/reconciliation-investigation.json`):
  the affected row matched the prepared guard shape BIT-EXACTLY
  (mastery `0.11533544411262374`, attempts=3, correct_count=0, version=2;
  the nightly decay job had NOT touched it — last practice was within the
  2-day idle grace). The 3-attempt chain matched the reconciliation record
  exactly (settled 6/6, 6/6, 0/18; question ids `96ae4235…`, `ac5045d7…`,
  `ddf30066…`; per-part marks show evidence fired at part-`a` partials).
  A WHOLE-PROJECTION audit — stored (attempts, correct_count) vs
  derived-from-settled-attempts over primary+secondary topics, order-independent
  — found **exactly ONE mismatch among all 47 `skill_states` rows: the known
  row**. Zero settled attempts without evidence; zero duplicate rows. This
  independently confirms the session-73 scope analysis (r1's 0-mark
  placeholders could not change correctness; the contamination is exactly
  the two r2 mis-fires + one derived row).
- **The guarded repair, one transaction** (`evidence/cycle-001/reconciliation-execution.json`):
  `BEGIN` → `SELECT … FOR UPDATE` (shape re-verified under lock) → the
  prepared `UPDATE` (with an additive `RETURNING` for the rowcount guard;
  WHERE/SET semantics identical to the prepared SQL) → rowcount **1** →
  in-transaction after-read → `COMMIT`, at 2026-09-15 18:00:34 UTC.
  Result: mastery `0.11533544411262374` → **`0.3135593220338984`**
  (bit-exact corrected value), correct_count 0 → 2, version 2 → 3
  (optimistic-lock discipline preserved); `last_practiced_at` untouched.
  **Zero unintended changes, proven at row granularity: exactly ONE of the
  47 rows changed, row count unchanged, post-repair whole-projection audit
  0 mismatches.** The prepared rollback SQL and the full before-snapshot
  are preserved in the execution audit artifact.
- **Post-fix verification** (`evidence/cycle-001/postfix-verification.json`):
  corrected learner state confirmed (0.3135593220338984, 2/3 correct,
  version 3); Smart Lesson decision replicated with the production code
  semantics (raw 0.3136, decay-adjusted ≈0.311, weak ceiling 0.45 →
  **LOW_MASTERY — same code, honest value**); class analytics propagation
  (8 measured, mean of stored mastery `0.11369388714241949` →
  **`0.1384718718825788`**, LOW band — S2-f legitimately remains weak;
  weakness options and the targeted Test Builder read the same live
  aggregation); the 2 remaining PENDING attempts are the concurrent CLA
  lane's (`web-structured-v1`), untouched.
- **Correction to the earlier estimate (honest nuance):** session 73's
  corrected class mean 0.13847798474015932 was computed from the ROUNDED
  t0 mean (0.1137). The exact live recomputation is **0.1384718718825788**.
  The difference (≈5.4e-06) is rounding in the estimate, not a data change;
  both values are recorded for transparency.
- **Status chain closed:** the 0.1153/0.1137 cycle figures are now
  REPORTED → INVALIDATED BY ROOT-CAUSE ANALYSIS → CORRECTED →
  **VERIFIED (production recomputation executed + post-fix data-level
  verification)**. The live r3 round (re-attempt → mark → mastery trajectory
  through the deployed app) still waits for the Actions quota — it is the
  remaining app-level confirmation, riding the §9 recovery plan.
