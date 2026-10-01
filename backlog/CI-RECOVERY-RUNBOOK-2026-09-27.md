# CI Recovery Runbook — the 2026-09-27 quota window (prepared 2026-09-17, Session 80)

**Purpose:** when the Actions quota returns, restoration is a mechanical
execution of this sequence — not an improvisation. Everything before r3 is
automated or one-command; everything after is a frozen protocol.

**Zero-cost posture until then:** the sentinel on the PUBLIC ops repo probes
hourly but only AFTER `2026-09-27T06:00Z` (billing anchor = day 27); while
blocked, its canary's jobs never start, so probing costs zero minutes. Do
NOT manually dispatch private-repo workflows before the window — a failed
dispatch is noise, and the S77 record already proved the wall with run
`35070697220` (zero-step failure).

## Phase 0 — automatic (no action required)

The **CI Quota Sentinel** (`ci-quota-sentinel.yml`, public ops repo, hourly
at :17) does this unattended once the window opens:

1. Status pass — exits if all three pilot CI workflows are already green.
2. Canary — reruns parser-ci's latest non-green run; if jobs actually
   start (no billing annotation) → quota is back.
3. Unlock — reruns core-ci and web-ci too, and pings Discord:
   "Quota back — pilot CI reruns fired".

**Operator signal = the Discord ping.** If it fires, start Phase 1.

## Phase 1 — confirm the three CI rails (manual, read-only)

For each repo, the latest run on main must be `completed/success`:

```bash
gh api repos/SyllabAI/syllabai-core/actions/workflows/ci.yml/runs?per_page=1 \
  --jq '.workflow_runs[0] | {run_number, status, conclusion, head_sha}'
# repeat for syllabai-web and syllabai-parser (same path)
```

Notes:
- core-ci runs `mvn -B -ntp verify` — **the 18 ITs run inside it**
  (Failsafe + Testcontainers). A green core-ci IS the "18 ITs" gate; no
  separate dispatch exists or is needed.
- Expected durations (S76-measured): core-ci ≈ 3 min wall (IT suite
  ≈ 115 s), parser-ci / web-ci similar order.
- If a rerun was not fired (e.g. sentinel raced a new push), rerun manually:
  `gh api -X POST repos/SyllabAI/<repo>/actions/runs/<run_id>/rerun`.
- If a run FAILS on real (non-quota) grounds: stop, read the artifact
  (`test-reports`), treat as a product regression — do NOT proceed to r3.

**Head-SHA check:** the green runs must cover the current main heads
(core `efea4e5`-or-later, web `022d9ba`-or-later, parser `8142574`).
If main advanced past the green run (docs-only commits included for
web/parser which trigger on every push), let the newer run finish — the
r3 vehicle runs from the web repo, so web-ci must be green at its head.

## Phase 2 — critical-regression spot checks (read-only)

The suites are green, so this is a 5-minute eyeball of the artifacts that
gate the pilot's named invariants (all already covered by the suites; this
is belt-and-braces confirmation, not a re-run):

- core `target/surefire-reports`: `TeacherMarkingServiceTest`,
  `SmartMarkServiceTest`, `EvidencePublisherTest`, the multi-part evidence
  regression, `correct:null` regression, QUESTION_PART fail-closed set —
  0 failures each.
- failsafe-reports: `MultipartMarkingFlowIT`, `SmartLessonFlowIT`,
  `NextBestActionFlowIT`, `ClassAnalyticsFlowIT`,
  `WeaknessTargetingFlowIT` — 0 failures each.

## Phase 3 — live r3 round (the FROZEN protocol)

Vehicle: `s2-evidence-cycle.yml` (syllabai-web, workflow_dispatch), per
`backlog/EVIDENCE-CYCLE-R3-SPEC-2026-09-16.md` § Measurement Protocol
(FROZEN 2026-09-17). Sequence:

```bash
# S0/S1 — after phase: baseline capture + new attempts (monitor learner)
gh workflow run s2-evidence-cycle.yml -R SyllabAI/syllabai-web \
  -f phase=after
# THEN author the marks manifest from the dump (operator judgment,
# never pre-authored), commit it, and:
gh workflow run s2-evidence-cycle.yml -R SyllabAI/syllabai-web \
  -f phase=mark -f manifest_path=scripts/ops/s2_marks_manifest_r3.json \
  -f manifest_sha=$(sha256sum scripts/ops/s2_marks_manifest_r3.json | cut -d' ' -f1)
# S3 — final phase: Smart Lesson + class view after marked evidence
gh workflow run s2-evidence-cycle.yml -R SyllabAI/syllabai-web \
  -f phase=final
```

Evaluate assertions A1–A9 + invariants I1–I6 exactly as frozen. Verdict
rules P.5: PASS / FAIL / REVIEW — a FAIL is recorded, not argued away.

## Phase 4 — t0 capture (the objective gate)

Per `backlog/EVIDENCE-ACCUMULATION-T0-PROCEDURE-2026-09-16.md` §
Expected-diff policy (2026-09-17):

```bash
cd scripts/ops   # syllabai-web
DATABASE_URL='<read-only Neon DSN>' python3 t0_capture.py --out t0-artifact.json
echo $?   # 0 = CLEAN, 2 = BLOCKED ( FAIL immediately, understand first )
```

Then run the verdict procedure (diff vs r3 S3 + declared transients W1–W5;
hard-fail classes F1–F6). Record the verdict beside the artifact.

## Phase 5 — pilot readiness review (T-032)

Only after: three CI rails green at head + r3 PASS (or PASS-WITH-NOTES) +
t0 PASS. Then the §14 five-gate review collapses CI=NO → YES and the
PILOT READY decision is made on the record — not before.

## What NOT to do

- Do not bulk-rerun old failed runs from before the blackout (stale heads;
  the sentinel only reruns the LATEST per workflow — keep it that way).
- Do not dispatch r3 phases concurrently (the workflow has a concurrency
  group; phases are strictly sequential by design).
- Do not re-run an r3 phase to improve an outcome — the protocol's I6: a
  re-run is a new round (r3b), the first result stands.
- Do not pre-author the marks manifest (I5) or adjust the protocol after
  seeing data (P.6 amendment procedure instead).
- Do not probe private Actions before 2026-09-27T06:00Z (zero-noise rule).

---

## Addendum (2026-09-17, CI-recovery lane) — the tree is PREPARED for the window

- **core main = `ef69d8d`** carries the fix for the six first-execution IT fixture
  defects (test-only) + `workflow_dispatch` on `ci.yml` (build job unchanged) +
  the E2 §14 persistence/query-cost artifact. Pushed with `[skip ci]` — zero
  minutes consumed; no run exists for `ef69d8d` yet.
- **The ONE authoritative run when minutes are available** (replaces the
  sentinel's old-SHA rerun for core, whose latest non-green run predates the
  fix):
  ```bash
  gh api -X POST repos/SyllabAI/syllabai-core/actions/workflows/ci.yml/dispatches -f ref=main
  ```
- **Honest expectation for that run:** unit 582 green (already proven locally on
  JDK 25 and in CI on `78c8afc`); the six fixture REDs are gone. TWO residual
  lane-owned REDs may still fail the run: `RevisionNoteFlowIT`
  (`revision_note_asset.bytes` bytea/bigint binding — revision-notes lane) and
  `EvidenceStateConcurrencyIT.sameAnswerConcurrentMarks…` (their DB-backed
  harness demonstrating the 630b269 double-emission gap: evidence=2, expected 1,
  6/6 rounds — a REAL product defect their lane is addressing). A RED on those
  two is NOT a fixture regression; do not re-classify the six fixed defects.
- Empirical quota note: real (non-zero-step) CI builds executed 2026-09-16
  18:27–18:49Z (`35135082818`, `35136279108`, `35136630860` — all failure /
  failure / failure), so the "2026-09-27 window" premise is soft; the
  operator's standing directive (minutes exhausted) governs dispatch timing.
