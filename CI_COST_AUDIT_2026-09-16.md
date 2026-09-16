# CI Cost & Architecture Audit — 2026-09-16 (Session 76, read-only)

**Mandate:** the operator directive for Session 76 — GitHub Actions hosted
minutes are exhausted; perform a READ-ONLY cost/architecture audit; do NOT
modify workflows; do not let the quota distort architecture; first establish
whether the normal monthly quota is even sufficient for SyllabAI.

**Method (all read-only):** the GitHub REST API was queried for the complete
run inventory of the five SyllabAI repos (1,167 runs inventoried, 30-day
window 2026-08-17 → 2026-09-16), per-job wall-clock durations were sampled
from real successful runs (225 timed samples), and billed minutes were
estimated using GitHub's per-job round-up rule on Linux runners. One
test-report artifact from a successful core-ci run was downloaded to
establish what the CI minutes actually buy (498 unit tests + 59 IT tests
in one `mvn verify`). **No workflow file was modified. No quota-failed job
was re-dispatched.**

**Status context:** `CI = BLOCKED — GitHub Actions hosted-runner quota
exhausted` (org-wide since ~2026-09-15 13:02 UTC). The public
`SyllabAI/syllabai-ops` repo's **CI Quota Sentinel** (hourly, free on the
public repo) detects restore automatically — billing anchor is day 27, so
the probe window opens **2026-09-27** (bypassable with `force=true` after a
billing change). Local verification meanwhile stands at **523 unit green /
1 known skip** at core `6c8b582` (Session 76, this session).

## 1. Current estimated CI cost

**Historical 30 days (what exhausted the quota): ≈ 2,000+ billed minutes**
(the free-plan private-repo allowance is 2,000 min/month):

| Rank | Consumer | Runs (30d) | ~Min/run | Est. minutes | Share |
|---|---|---|---|---|---|
| 1 | Google Sheet Dashboard (syllabai) | 92 (65 ok) | ~10 | **~717** | 35% |
| 2 | core-ci (tests, real) | 188 (107 ok) | ~3 | ~381 | 19% |
| 3 | Google Drive Syncs (all 5 repos) | 417 | 1–3 | ~398 | 20% |
| 4 | Discord Commit Notify (5 repos, standalone) | 270 | ~1 | ~252 | 12% |
| 5 | parser-ci (3 jobs) | 52 | ~3 | ~135 | 7% |
| 6 | web-ci | 84 | ~1 | ~76 | 4% |
| 7 | Pilot Monitor (web) | 19* | ~4 | ~43 | 2% |
| 8 | everything else (S2/V20/ops one-offs) | ~40 | 1–3 | ~35 | 1% |

\* only ~19 runs exist because the quota blocked the schedule mid-month;
the full `*/6h` + weekly schedule is ~124 runs/month.

**The key finding: actual test CI was only ~29% of consumption.** The
quota was consumed predominantly by *operational* workflows — a Google Sheet
dashboard (35%), per-push Drive mirrors (20%), and Discord notifications
(12%).

**Steady state at the CURRENT configuration (post-migration): ≈ 1,190
minutes/month** — the concurrent lane already moved the largest consumers
off private-runner billing (see §2).

## 2. What already happened (context the audit must credit)

Between Session 75 and this session, the concurrent ops lane executed a
minutes-cut that this audit validates rather than duplicates:

- **`38579e9` (syllabai):** Google Sheet Dashboard + Discord Daily Pulse
  moved to the **public** `SyllabAI/syllabai-ops` repo — public repos get
  free, unlimited standard-runner minutes. Saves ~720 min/mo.
- **`cff5d2f` (core) / `0d70953` (web) + parser/resources equivalents:**
  Discord Commit Notify merged into each repo's Drive-sync job (one job per
  push instead of two). Saves ~250 min/mo.
- **`c3fb497` (core):** the per-repo Drive sync retired — mirrored
  centrally by `syllabai-ops` Repo Mirror (every 30 min light lane + weekly
  heavy lane, public = free). Saves ~110 min/mo.
- **`31ee896` (core):** core-ci got path filters (`src/**`, `pom.xml`,
  `mvnw`, workflow), concurrency cancel-in-progress, and a 30-minute
  timeout.
- **`syllabai-ops` (new public repo):** CI Quota Sentinel (hourly restore
  detection, canary re-run design), Repo Mirror, dashboard, digest,
  keepalive — all free.
- **Self-hosted runner probe (core `958110a` → `7478262`, reverted):**
  executed run `35012221720` on the QUESTION_PART lineage — 523 unit GREEN
  (real executed run, artifact-verified: 72 classes, 522 tests + 1 skip);
  ITs skipped (no Docker on that runner either). `runs-on` restored to
  `ubuntu-latest` immediately after; the sandbox runner was deregistered.

## 3. Largest sources of minutes — measured, not assumed

- **Google Sheet Dashboard: ~10 min per run** (measured median 9.48, range
  5.1–11.6), 92 runs in 30d — the single largest consumer, and it fired on
  **every push** (75 of the 92) plus daily schedule. *Now on the public ops
  repo — resolved.*
- **Per-repo Google Drive Sync on every push to every branch** (`branches:
  ["**"]`): 417 runs/30d across the five repos. Core's is retired; four
  remain (syllabai ~130, web ~67, parser ~47, resources ~34 runs/mo;
  resources is the expensive one at ~2.7 min/run — the repo carries the OCR
  corpus).
- **core-ci: ~3 min per successful run, total** — the surprising result.
  The full `mvn verify` (498–523 unit tests + 59 ITs across 18 Testcontainers
  classes) completes in ~2.5–3.0 minutes wall-clock: the unit suite sums to
  ~15 s of class time, and the entire IT suite to ~115 s — the Testcontainers
  overhead is **not** a significant cost driver because the containers are
  shared/cached effectively on the hosted runner. **Any proposal to shard
  the test suite or remove Testcontainers to save minutes would save almost
  nothing while weakening the educational gates — rejected on the numbers.**
- **Pilot Monitor: ~4 min per run at ~124 runs/mo ≈ 496 min/mo** — now the
  largest REMAINING private-billed consumer (42% of the steady state).
- **parser-ci: ~3–4 min per run** (3 jobs: build ~1.5, conformance ~1,
  content-package-proof ~0.2; billed as per-job round-ups). Runs on every
  push with no path filter.
- **web-ci: ~1 min per run**, every push, no path filter.

## 4. Safe optimization candidates (PROPOSED ONLY — nothing modified this session)

| # | Candidate | Expected reduction | Risk | Verification impact |
|---|---|---|---|---|
| 1 | **Pilot Monitor → public syllabai-ops** (same migration pattern as the dashboard: outbound HTTP probes + Discord webhook need no private-repo access; move the monitor credentials to ops-repo secrets) | **~496 min/mo** (steady state 1,192 → ~696) | LOW — the exact pattern already proven by the dashboard/digest/mirror migrations; the probe script is checkout-independent | NONE — it is operational monitoring, not a CI gate |
| 2 | **Retire per-repo Drive syncs in syllabai / web / parser** (the central Repo Mirror's `own_sync_active` logic auto-picks-up any repo whose own sync is retired — designed for exactly this) | **~244 min/mo** (→ ~452 total with #1) | LOW — Drive mirror freshness changes from per-push to ≤30 min; destinations unchanged | NONE — Drive is a backup mirror, not a gate |
| 3 | **resources Drive sync** (~102 min/mo): the mirror's default skip-list currently names `syllabai-resources` (size-tier related). Retiring its sync requires a deliberate ops-repo decision (remove from skip list or keep self-sync) | ~102 min/mo | MEDIUM — the skip-list entry exists for a reason that should be re-confirmed (repo size vs the light lane's 500 MB threshold) before acting | NONE |
| 4 | **parser-ci path filters** (mirror core's pattern; must cover `src/**`, `pom.xml`, `tools/glmocr/**`, `tools/content-package-v0.1/**`, workflow file — all three jobs' inputs) | ~10–30 min/mo (docs-only pushes skipped) | LOW, with one sharp edge: an incomplete filter list silently SKIPS verification — the filter set must be enumerated from each job's actual inputs | NONE if complete; a missed path = a skipped gate (fail-open) — needs the enumeration done carefully |
| 5 | **web-ci path filters** (src/**, configs, package files, workflow) | ~10–30 min/mo | Same shape as #4 | Same |
| 6 | **web-ci dependency caching** (no `cache:` on setup-node/bun today; `bun install` re-downloads each run) | ~20–30 s/run (~30 min/mo at current rates) | LOW | NONE |
| 7 | **parser-ci conformance job**: re-runs `mvn compile dependency:build-classpath` (~40 s) already done by the build job; could share via artifact or merge jobs | ~1 min/run | LOW-MEDIUM (job-boundary change) | NONE |
| — | **Rejected: test sharding** — the whole suite is ~3 min; sharding adds orchestration complexity for zero meaningful saving | — | — | Would not weaken gates, but saves nothing measurable |
| — | **Rejected: removing/reducing Testcontainers ITs** — the entire 18-class IT suite costs ~2 min inside core-ci; the hosted integration infrastructure is precisely what cannot be replaced locally (no Docker in the sandbox) | — | — | **Would weaken the educational correctness gates — forbidden** |

## 5. Is the normal monthly quota sufficient? (the directive's §8 question)

**Yes — with the migrations already done, no architecture change is
required.** Steady state at the current configuration is **~1,190 min/mo**
against a 2,000 min/mo free-plan allowance (~800 min headroom) at observed
push rates, with the two largest historical abuses (dashboard on every
push; standalone Discord jobs) already eliminated. If candidates #1–#2 are
adopted, steady state drops to **~450–700 min/mo** — comfortable headroom
for increased pilot activity.

What genuinely requires hosted integration infrastructure: the **18
Testcontainers IT classes** (real Postgres, real Spring context, ~2 min
total per run) and the **pilot/evidence workflows** (s2-evidence-cycle,
pilot-monitor, V20-verify — they hold the Actions-only secrets). None of
these have a cheaper correct substitute; none is a cost problem at ~3
min/run. **The educational correctness gates are more important than
runner minutes, and the numbers show we do not have to choose.**

## 6. Verification-impact statement (the audit's red line)

Every candidate above preserves all existing verification gates: no test is
skipped, no IT disabled, no coverage reduced, no workflow semantics
changed. Candidates #4/#5 (path filters) are the only ones that can *skip*
verification runs, and only for pushes that provably touch none of the
verified inputs — the same trade core already made in `31ee896`. Per the
directive, no optimization is implemented this session; each candidate
requires an explicit operator decision, and the CI boundary stays:

```text
CI = BLOCKED — GitHub Actions hosted-runner quota exhausted
```

until the monthly allowance genuinely resets (sentinel window opens
2026-09-27) or the operator changes billing. At restore, the existing
§9 recovery lineage runs unchanged: `actions-health` canary → core-ci →
web-ci → parser-ci (the sentinel automates the canary + re-runs).

## 7. Data artifacts

- Run inventory + timing samples: `tool-results/s76_ci_usage.json` (local
  session artifact; 1,167 runs, 225 timed samples)
- Real per-job durations of successful runs:
  `tool-results/s76_ci_real_durations.json` (local session artifact)
- Downloaded test-report artifact (core-ci run `34971124081` @ `6092650`):
  498 unit + 59 IT green in one `mvn verify` — the ground truth for the
  "what do CI minutes buy" measurement
- Generator scripts: `scripts/s76_ci_usage_audit.py`,
  `s76_ci_cost_analysis.py`, `s76_ci_real_durations.py`,
  `s76_ci_final_numbers.py` (local session artifacts)
