# CI Optimization Execution — 2026-09-16 (Session 77)

**Mandate:** the operator directive for Session 77 — the operator cannot
purchase additional GitHub Actions capacity; do NOT redesign CI; do NOT weaken
tests or verification gates; reduce unnecessary Actions consumption while
preserving the architecture and all educational-correctness/integrity gates.
Treat the Session 76 audit (`CI_COST_AUDIT_2026-09-16.md`) as the optimization
baseline; audit the largest remaining consumers; verify (not assume) that the
dashboard migration actually reduced consumption; investigate the Pilot
Monitor migration; modify a workflow only after the six-step proof
(consumption → purpose → no-gate-weakening → savings → documented decision →
smallest change).

**Method:** read-only GitHub REST API re-audit of all nine SyllabAI repos
(run inventory since 2026-09-10, per-job timing samples, job-log downloads for
the mirror and the monitor) + workflow-source inspection at the current
lineages + one real workflow dispatch on the public ops repo to verify the
migrated monitor's wiring. One workflow file was ADDED (public repo), one
RETIRED (the migrated source) — the first workflow changes since the
concurrent lane's minutes-cut, each following the six-step procedure below.

## 1. Verification of the Session 76 audit's claims (the directive's §2)

The dashboard migration was **verified as actually working, not assumed**:

- **Private `syllabai` Google Sheet Dashboard: STOPPED.** Last run
  2026-09-15T15:28Z (a quota-blocked failure); last successful run
  2026-09-15T12:51Z (~10 min billed). Zero runs since.
- **Public `syllabai-ops` dashboard: RUNNING.** Dispatch 2026-09-15T17:36Z
  (success, 10.2 min wall — same work, now free) + the daily 02:43 UTC
  schedule firing (2026-09-16T07:54Z observed). The ~717 min/mo historical
  dashboard consumption is now $0 and quota-immune.
- **Discord-merge verified behaviorally:** post-merge pushes (e.g. parser
  2026-09-15T16:43/19:32/19:50, syllabai 2026-09-15T19:24→2026-09-16T07:00)
  triggered the merged sync workflow and CI but **no separate Discord Commit
  Notify runs** — the standalone notify workflow's last runs predate the merge
  commits.
- **Central Repo Mirror failover verified from real job logs:** the scheduled
  light lane (2026-09-16T02:44Z) auto-skipped every repo that still self-syncs
  (`syllabai`, `syllabai-web`, `syllabai-parser`, `syllabai-pastpapers`,
  `Past-Papers`, `syllabai-teacher-workbench`) plus the skip-list entries
  (`syllabai-ops`, `syllabai-resources`), and **mirrored `syllabai-core`**
  (the repo whose own sync was retired): `[OK] SyllabAI/syllabai-core (1.6 MB,
  1.1 min) — synced`. The `own_sync_active` auto-pickup works as designed.
- **Quota wall confirmed still in force:** every private-repo run since
  2026-09-15T13:02Z fails with jobs never started (1–3 s, zero minutes
  billed); the `actions-health` canary dispatched 2026-09-16T07:51Z failed the
  same way. `CI = BLOCKED` remains factually correct; the sentinel (hourly,
  free) date-guards itself to the 2026-09-27 probe window.

## 2. Corrections to the Session 76 model (measured, this session)

1. **`syllabai-resources` is PUBLIC — its Actions minutes are free.** Decisive
   evidence: its Google Drive Sync SUCCEEDED at 2026-09-15T16:43Z (2.8 min
   wall) *after* the org-wide quota wall blocked every private repo. The S76
   steady-state model counted the resources sync (~102 min/mo) and
   scripts-tests (~4 min/mo) as private-billed. **Corrected steady state:
   ~1,086 min/mo** (S76 published ~1,190). Candidate #3 from the S76 audit
   (resources sync retirement) is **moot** — there is nothing to save; its
   per-push sync is free and fresher than the central mirror, exactly what the
   mirror's skip-list design intends.
2. **Full org inventory:** nine repos, of which only four are private
   (`syllabai`, `syllabai-core`, `syllabai-web`, `syllabai-parser`); five are
   public (`syllabai-ops`, `syllabai-resources`, `syllabai-teacher-workbench`,
   `Past-Papers`, `syllabai-pastpapers`) — all their workflows run free.
3. **Pilot Monitor real cost band:** five real (non-quota-blocked) runs
   measured 2026-09-15: 141–309 s wall → 2–6 min billed, median 3 min. At the
   full schedule (4×/day + weekly = ~126 runs/mo) that is **~380–500 min/mo**
   (S76's ~496 stands as the conservative upper bound). Confirmed as the
   largest remaining private-billed consumer (~42% of the corrected steady
   state).

## 3. Pilot Monitor migration (the directive's §3) — INVESTIGATED, then EXECUTED

**Investigation findings:**

- *Which jobs consume the minutes:* one `probe` job per run on `syllabai-web`
  (private), scheduled `17 */6 * * *` + Sun `33 9 * * 0` + dispatch.
- *Why they run:* minimum operational monitoring for the controlled pilot
  (DEPLOYMENT.md §4) — 19 read-only checks over real HTTP: backend health
  (cold-start tolerant), CORS preflight, auth-401 failure mode, teacher-route
  guard, deployed Vercel bundle markers, the monitor-learner loop (subjects,
  practice list, recommendations policy, Smart Lesson v2 shape), subject
  scoping 404, missing-param 400, cross-subject contamination, teacher
  concept-graph, class-analytics honesty, marking lane, weakness targeting,
  tutor LLM chain, weekly teacher-activation idempotency + the operator
  checklist; Discord report on every run; exit 1 when any check fails.
- *Whether it can run without a hosted runner:* it needs A runner (stdlib-only
  Python doing outbound HTTP — no serverless substitute exists without new
  infrastructure), but it does NOT need a PRIVATE runner: nothing it touches
  requires private-repo access. The public ops repo is a complete substitute.
- *Whether the concurrent lane had already migrated it:* **NO.** The ops repo
  (through `355a23a`) contained sentinel/mirror/dashboard/digest/keepalive
  only; the web repo still carried the workflow. The S76 audit's candidate #1
  was proposed-only and remained unimplemented.
- *Failure semantics (verified from real logs):* the 2026-09-15 pre-quota
  failures were **correct detections** — the monitor flagged a genuinely
  stale Vercel bundle (`web-bundle: stale bundle — missing: teacher class
  intelligence (c3fb24d)`), went red with a Discord report, and returned to
  19/19 green after the redeploy at 11:51Z. The alerting works and must be
  preserved.

**The six-step proof (the directive's §6), then the smallest change:**

1. *Consumption identified:* ~126 runs/mo × 2–6 min billed (median 3) ≈
   **~380–500 min/mo**, ~42% of the corrected steady state.
2. *Purpose understood:* operational monitoring (above) — **not a CI gate**
   (reconfirmed against the S76 audit's classification by reading every check:
   all read-only HTTP probes + reporting).
3. *No gate weakened:* the probe script is copied **byte-identical** (sha256
   `93379eaf…db8157`, verified both sides); the crons are identical (the
   weekly operator checklist keys off the exact `33 9 * * 0` string); the env
   plumbing, concurrency group, 15-min timeout, and fail-loud exit-1 semantics
   are identical. No test, IT, or verification workflow was touched.
4. *Savings estimated:* ~380–500 min/mo of private billing → free public
   minutes.
5. *Decision documented:* this document + the ops repo README ("Pilot Monitor
   cutover") + both commit messages + the tracker WORKLOG.
6. *Smallest change made:*
   - **ADDED** to public `syllabai-ops` (`7d6622a`):
     `scripts/pilot_monitor/pilot_probe.py` (verbatim) +
     `.github/workflows/pilot-monitor.yml` (same crons/env/concurrency; plus a
     **fail-closed secrets preflight** that exits 1 with an actionable message
     until the operator adds the monitor-account secrets — monitoring is
     visibly DOWN, never silently green) + README cutover runbook.
   - **RETIRED** from private `syllabai-web` (`022d9ba`): the single workflow
     file `.github/workflows/pilot-monitor.yml` (script retained for
     provenance; ops copy is now canonical; restore path = revert).

**Migration status: WIRED AND VERIFIED to the maximum extent possible without
the operator's secrets.** A real dispatch on the ops repo (run
`35072946448`, 2026-09-16T08:17Z, public = free) executed the preflight and
failed closed with exactly the intended actionable message — trigger, wiring,
and fail-closed behavior proven. **The end-to-end probe (19/19 checks green +
Discord report) is NOT CLAIMED until it happens** — it requires the one step
nobody but the operator can perform (Actions secrets are write-only; they
cannot be copied via the API): add `PILOT_MONITOR_EMAIL`,
`PILOT_MONITOR_PASSWORD` (and optionally `PILOT_TEACHER_EMAIL` /
`PILOT_TEACHER_PASSWORD`) to `SyllabAI/syllabai-ops` → Settings → Secrets and
variables → Actions. The next 6-hourly run then reports to Discord
automatically.

**Operational side-effect (positive):** the private-repo monitor had been
quota-dead since 2026-09-15T13:02Z (its schedule fired but jobs never
started — the pilot has had NO scheduled monitoring during the blackout). The
public-repo copy can run NOW, so the migration also restores monitoring
during the blackout rather than only saving money after it. The double-alert
risk is structurally eliminated (the private workflow is already retired; the
public one is the only monitor).

## 4. Before/after estimate (the directive's §3 format)

```text
Current (S76 published steady state):            ~1,190 min/mo
Corrected (resources is public — S77 finding):   ~1,086 min/mo
After existing migration (Pilot Monitor → ops):  ~590 min/mo
   core-ci 120 · parser-ci 129 · web-ci 75 · syncs 244 · ocr 2 · on-demand 20
Expected saving:                                  ~500-600 min/mo total
                                                  (~380-500 from the monitor
                                                   + ~106 model correction)
Verification impact: NONE
   — the probe script is byte-identical, every check preserved, crons
     unchanged; the monitor is operational reporting, not a verification
     gate; no test/IT/coverage change anywhere.
```

**Steady state is now ~590 min/mo against the 2,000 min/mo allowance (~70%
headroom)** — comfortably sufficient for pilot activity, with no architecture
change and no gate weakened.

## 5. Remaining candidates (documented, NOT implemented — operator decisions)

| # | Candidate | Saving | Why not executed this session |
|---|---|---|---|
| 2 | Retire the per-repo Drive syncs in `syllabai`/`syllabai-web`/`syllabai-parser` (the central mirror auto-picks-up) | ~244 min/mo | **New caveat found this session:** the Discord commit-notify was merged INTO the sync jobs — retiring them also retires per-push commit notifications, and Drive freshness drops from per-push to ≤30 min. A real observability/freshness trade-off, not a free win; the quota no longer requires it (590 ≪ 2,000). Operator decision. |
| 4 | parser-ci path filters | ~10–30 min/mo | Fail-open edge (an incomplete filter silently skips verification); tiny saving; operator decision. |
| 5 | web-ci path filters | ~10–30 min/mo | Same shape as #4. |
| 6 | web-ci bun dependency caching | ~30 min/mo | CI-workflow change for a small saving; operator decision. |
| 7 | parser-ci conformance job dedup | ~1 min/run | Job-boundary change; operator decision. |
| — | Test sharding / Testcontainers reduction | — | **Rejected again on the numbers** (unchanged from S76): the full `mvn verify` is ~3 min; the 18-class IT suite ~115 s. Would weaken gates for ~zero saving. |

## 6. Verification-gate impact statement (the red line)

No test was skipped, no IT disabled, no coverage reduced, no CI workflow
semantics changed. `core-ci`, `web-ci`, `parser-ci`, the 18 Testcontainers IT
classes, the s2-evidence-cycle vehicle, and every educational-correctness
gate are untouched. The only workflow changes are the operational monitor's
relocation (byte-identical script, identical schedule, fail-closed until the
operator's secrets land) — and its private-repo source was already dead
(quota-blocked) at the moment of retirement, so nothing observable was lost.
**The educational correctness gates are more important than runner minutes,
and this session did not have to choose.**

## 7. Local verification this session (the directive's §7 — changed code only)

The concurrent lane shipped SMART_LESSON after Session 76's `6c8b582` (core
`50dfa59`→`9c0cad0`, web `4c3326a`). Because product code changed, the unit
suite was re-run at the new lineage rather than assumed: **535 tests / 0
failures / 0 errors / 1 known skip** (`DatabaseIsolationGuardTest` — the
documented no-test-DB skip) — BUILD SUCCESS at core `9c0cad0`, with the named
invariants confirmed green per-class (TeacherMarkingServiceTest 6/6,
SmartMarkServiceTest 4/4, EvidencePublisherTest 4/4, plus the SMART_LESSON
classes 22/22 + 11/11 + 20/20). This independently confirms the concurrent
lane's 535-green claim at the unit level. The r3 spec and t0 instrument are
**unchanged** (verified: empty diff at web `4c3326a` vs `d0fc4d9` for
`scripts/ops/t0_capture.{sql,py}`; the r3 spec untouched in this tracker) —
per the directive, they were not recreated.

## 8. Status

```text
LOCAL VERIFIED        = YES   (535 unit green at core 9c0cad0, new lineage)
PRODUCTION VERIFIED   = YES   (read-only checks green, S75 state stands)
CI VERIFIED           = NO    (BLOCKED — quota exhausted; sentinel-automated)
PILOT READY           = NO    (4/5 gates; CI + live r3 remain)

Pilot Monitor migration = COMPLETE (ops 7d6622a→04d7d68 + web 022d9ba);
                          credentials re-provisioned after loss
                          (pilot.monitor2@syllabai-test.dev); end-to-end
                          VERIFIED by real dispatch 35080761751:
                          preflight passed, 15/15 checks green,
                          Discord report posted (see §9).
Steady state             = ~590 min/mo private-billed (was ~1,190 published)
Money spent              = zero
Gates weakened           = none
```

## 9. Amendment (2026-09-16, later same day): operator reported the passwords LOST — credentials re-provisioned, secrets set, cutover COMPLETED end-to-end

The operator's follow-up ("I dont have the passwords" / "Yes, pasted") closed
the one pending step, with a recovery in between:

- **Credential loss confirmed unrecoverable by design.** The session-58
  password was sealed into write-only GitHub secrets and delivered only in
  the session-59 report, which was wiped by the sandbox reset (verified: only
  t-c03/t-c11/t036 artifacts persist in `download/`); no forgot-password
  endpoint exists (AuthController: register/login/me/password-change-needs-
  current); no credentials were ever committed (session-60 leak-scan stands).
- **Recovery = the sanctioned provisioning path, session-58 precedent:** a
  fresh TEST monitor learner via the PUBLIC register API —
  `pilot.monitor2@syllabai-test.dev` (STUDENT, verified via /auth/me; TEST
  classification = the `@syllabai-test.dev` email-domain convention, applied
  analytically; the users table has no classification column and the evidence
  export excludes test accounts at analysis time). The probe is designed for
  a FRESH learner (its smart-lesson check expects the cold-start
  INSUFFICIENT_COVERAGE action), so no account state needed migration; the
  dormant old account is a harmless TEST STUDENT row. One production write:
  a single users+user_roles row — the same write session-58 made.
  **Pre-handover local verification with the real probe script (byte-identical
  ops copy): 15/15 checks green, exit 0.**
- **Operator pasted the new pair** (verified present by name via the API:
  `PILOT_MONITOR_EMAIL` + `PILOT_MONITOR_PASSWORD` now in syllabai-ops).
- **End-to-end dispatch VERIFIED (run `35080761751`, 2026-09-16T09:40Z,
  public = free, 22 s):** preflight → "monitor-account secrets present" →
  full probe → `SUMMARY: 15/15 checks green (0 failing, 2 advisory)` →
  "discord report posted" → conclusion success. The 2 advisories: teacher
  creds not set + kappa N/A until T-C04 — both known, both non-blocking.
  (The earlier "19/19" phrasing was the with-teacher-creds estimate; the
  observed 6-hourly probe summary line is 15/15 with teacher advisory-skip.)
- **Cutover status: COMPLETE.** Pilot monitoring is RESTORED during the
  blackout (the private monitor had been quota-dead since 2026-09-15T13:02Z);
  the next 6-hourly schedule (17 */6 * * *) now reports to Discord
  automatically. Steady state stands at ~590 private min/mo. Teacher secrets
  remain optional/unset: recovery requires the operator's Neon path (bcrypt
  reset) or their local copy of the session-59 report (`recovery-2026-09-13-*`);
  the register API cannot recreate the TEACHER role (always STUDENTs,
  Master Spec §6.1); the monitor degrades gracefully without them.
- Docs updated truthfully: ops `04d7d68` (README cutover runbook + workflow
  comment name the new account + re-provisioning provenance; NO password in
  any repo file). Core `DEPLOYMENT.md` §4 pre-existing drift (still says
  "web repo secrets" + the old email — stale since the migration itself)
  noted, not fixed here (scope discipline; standalone doc follow-up).
