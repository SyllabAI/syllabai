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

## Honest states (§20)

- **VERIFIED**: the full chain above (production runs, artifacts downloadable);
  Vercel block resolved (PAT deployment `dpl_J93ocENkMuxXX4UYih5XfMjdWBrr` of
  main `8a63f5d` READY; deployed bundle carries all §8–§10 markers; official
  pilot-monitor 18/18 green including web-bundle for the first time since
  session-69).
- **PARTIAL**: core `fe01b87` (the evidence-timing fix) — unit-tested locally
  (495 green) but **CI BLOCKED**: the org's GitHub Actions began failing every
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
- **FOUND, deferred**: `AttemptHistoryView.correct` stays null for structured
  attempts after marking settles (display-level gap, ~3-line fix in
  `AttemptHistoryService`); deferred to avoid stacking unverified changes
  while CI is blocked.
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
