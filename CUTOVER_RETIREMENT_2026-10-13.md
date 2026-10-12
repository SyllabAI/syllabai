# CUTOVER + RETIREMENT OF RECORD — 2026-10-13 (Render, syllabai-core, syllabai-hub)

> Status: **EFFECTIVE.** Filed by lane r0 (Super Z, session `web-df0238cc-641e-4e8e-ae60-bc44c2aeec2e`)
> under the operator's direct order (trace `1a131d02c805602d`): *"Dont have to wait 48 hours.
> If we have already 100% migrated to v2 without a single issue, then retire Render,
> syllabai-core, and syllabai-hub. Update the master doc repo, so all agents know about it."*
> The 48-hour watch (cutover runbook §4) is **WAIVED of record** by the same order.

## 1. What is retired, effective 2026-10-13

| Asset | Disposition | Evidence of record |
|---|---|---|
| **`SyllabAI/syllabai-core`** (Java 25 / Spring Boot, hosted on Render) | **RETIRED** — GitHub repo **ARCHIVED read-only** at head `6cad6ef` (2026-10-04). Never deleted: issues, receipts, blame stay resolvable. The Render service disable is the one remaining operator console act (no Render credential is held lane-side). | PATCH `/repos/SyllabAI/syllabai-core` → HTTP 200, `archived=true` verified first-hand |
| **`SyllabAI/syllabai-hub`** (legacy v1 hub, head `93226a43`) | **RETIRED** — GitHub repo **ARCHIVED read-only** at head `93226a43` (2026-10-04). Never deleted. | PATCH `/repos/SyllabAI/syllabai-hub` → HTTP 200, `archived=true` verified first-hand |
| **Render (the Java core hosting)** | **RETIREMENT ORDERED** — traffic has been off Render since the cutover; the service-disable console act (runbook §6.2: disable, **never delete**) is the enumerated operator residual. Nothing on Render serves any traffic of record. | the §Z census LIVE=0 + the bake battery below |
| **The 48h soak** | **WAIVED** by the operator order (trace `1a131d02c805602d`). The census gate + the baked-census battery + the fresh replay seal stand as the replacement evidence. | this file §2–§3 |

## 2. Why the retirement condition is MET (100% migrated, zero open migration issues)

- **The last live family flipped and baked**: band B6 (answer-input/transcribe) landed at
  `0bdc594` under operator rulings (b) `08557d3` + B7 `7a6868a`, and the serialized hub
  redeploy baked it LIVE: deployment `dpl_AfZZb5bBSY3qsQRSwZUfaHTnKGYo` READY with both
  production aliases attached (`syllabai-hub-v2.vercel.app`, `syllabai-hub-v2-syllab-ai.vercel.app`).
- **The §Z zero-core census gate: GREEN, LIVE=0** (`zero-core-census-2026-10-13-b6-baked-r0.json`)
  — pins=7, rides-v2=2, rollback-fallback=1, dormant=5 (B7-ruled), unmapped=0, stale=0, unknown=0.
- **The gate is now ENFORCED in CI**: `ci.yml` runs `python3 scripts/preflight_zero_core_census.py --gate`
  in the verify job (commit `32272d2`) — any regression that re-introduces a LIVE core call fails CI.
- **Baked-census + wire battery 9/9 GREEN** on the live production alias (receipt
  `T-MIG-121/run-004-b6-bake-redeploy-r0.json` in syllabai-v2): the B6 transcribe needle present in the
  served bundle, B1/B2/B5 rows stable, hub health `core-api` 200, chat 400/401 laws live, bridge 200,
  actuator UP, the ruling-(b) deterministic 401 law-capture live on the api-of-record.
- **Fresh union golden replay at the final tip `32272d2`: 223/223 PASS** (seed 208/208 + prod 15/15,
  10 via the declared T-MIG-071 R3-C disposition) — run `38307013191`, SUCCESS, artifact 11773107960.
- **CI 2/2 SUCCESS** (verify + hub) at both `0bdc594` and the wiring tip `32272d2` (check-runs API).
- **Open-issue census**: exactly one open issue (`#147`) = the zombie Vercel project `prj_D7vf`
  decommission lever — a decommission-cleanup item, **not** a migration defect.

## 3. What ALL agents must now do differently

1. **`SyllabAI/syllabai-core` and `SyllabAI/syllabai-hub` are READ-ONLY of record** (archived).
   Any task that would write to them is void — reference them read-only (C1 law unchanged, now physical).
2. **The only system of record is `SyllabAI/syllabai-v2`** (api-of-record `syllabai-v2.vercel.app`,
   hub-of-record `syllabai-hub-v2.vercel.app`). All new work, receipts, and law live there
   (`.syllabai` channel law unchanged).
3. **No lane may attempt to un-retire or re-point any family at the frozen core.** The CI census
   gate will fail such regressions; the rollback lever (runbook §5) remains documented but is
   superseded by this retirement record — re-activation requires a new operator order.
4. **The Render console disable** (disable, never delete — runbook §6.2) and the zombie `prj_D7vf`
   decommission (Issue #147) remain the operator's standing console residuals.
5. The standing law survives retirement unchanged: append-only worklog, receipts-or-it-didn't-happen,
   no force pushes, authors-never-self-merge — the repo is the audit trail.

## 4. Where the full law lives

- `syllabai-v2 @ 32272d2`: `docs/MIGRATION_REPORT.md` (§7/§8 post-cutover record),
  `docs/CUTOVER_RUNBOOK.md` (the executed procedure), `.syllabai/receipts/W7-CUTOVER/*`,
  `.syllabai/receipts/T-MIG-121/run-004-b6-bake-redeploy-r0.json`, and the append-only
  `.syllabai/worklog.md` entry of this act.
- The plan/§Z/§6.2 law: `syllabai-v2/docs/MIGRATION_PLAN.md` + the DECOMMISSION-BANDS-PLAN band table.
