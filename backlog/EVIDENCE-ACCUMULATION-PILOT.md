# Milestone — Evidence Accumulation / Closed-Loop Pilot

**Commissioned 2026-09-15 (session-72), on the operator's direction.**

> The next meaningful product question is no longer "can SyllabAI generate an
> adaptive recommendation?" It is: **does the adaptive loop improve when real
> evidence accumulates?** — measured with real teacher marking and real student
> attempts, not probes.

Evidence Cycle 001 (2026-09-15, `backlog/EVIDENCE-CYCLE-001-2026-09-15.md`)
proved the loop EXECUTES end-to-end in production: PENDING → MARKED → LEARNER
EVIDENCE → CLASS EVIDENCE → WEAKNESS IDENTIFIED → TARGETED TEST → NEW ATTEMPTS
→ SMART LESSON RESPONSE. It also caught a real defect (multi-part attempts
fired evidence on partial totals — fixed in core `fe01b87`) — which is itself
the argument for this milestone: only accumulated real evidence exercises
these paths.

## The question this pilot answers

For each learner and each class: **as evidence accumulates, do the
recommendations actually get better?** Operationally:

1. **Direction** — after a targeted intervention (weakness → targeted test →
   attempts → marking), does measured mastery on the targeted topic MOVE in
   the right direction, and does the next Smart Lesson / NBA action reflect
   the movement (§8's closed loop, at class scale)?
2. **Calibration** — do BKT mastery estimates track the marks teachers
   actually award (rank correlation per topic), or is the conservative
   Cycle-1 parameterization (L0=0.1, slip=0.1, guess=0.25, T=0.1) too slow to
   credit real learning? Cycle 001 already hints at this: mastery 0.12 after
   evidence a human would read as "two solid answers out of three".
3. **κ release readiness** — Smart Mark's agreement gate has paired data the
   moment human marks carry per-point decisions. The pilot's mixed-award real
   answers are the first legitimate κ sample (the placeholder sample was
   deliberately NOT evaluated — degenerate all-zero agreement would have
   manufactured a gate pass).
4. **Weakness lane precision** — as the heatmap fills: are the flagged weak
   topics the ones the teacher also judges weak (reasons + drill-down
   evidence reviewed case by case)?

## Entry criteria (all currently BLOCKED on operator actions)

- [ ] **GitHub Actions restored** (minutes/spending limit — every workflow in
  the org fails instantly since ~13:02 UTC 2026-09-15, while the platform is
  operational; even a one-step echo fails). Blocks: CI for core `fe01b87`,
  the s2-evidence-cycle verification phases, the pilot monitor cron.
- [ ] **CI green on `fe01b87`** (evidence-timing fix; local unit suite 495
  green, ITs unverified without CI) + Render deploy confirmed current.
- [ ] **Post-fix verification round** (ready to dispatch: `s2-evidence-cycle`
  phases `after` → `mark` (r3 manifest from the fresh dump) → `final`):
  re-attempt the targeted questions → mark → the mastery trajectory must show
  correctly-credited full-mark attempts (the fix working live).
- [ ] Teacher marking rhythm agreed (the marking queue is the loop's clock).

## Pilot shape (minimal, §21-bounded — no new architecture)

- **Cohort:** the existing pilot learners + the teacher account already in
  production. No new surfaces.
- **Cadence:** students practice (Smart Lesson / NBA driven) → structured
  answers land PENDING → the teacher works the queue (queue-v2 order, Smart
  Mark assist, per-point decisions for κ) → class evidence updates → weakness
  options refresh → the teacher issues targeted tests → students re-attempt.
- **Instrumentation (already shipped, read-only):** class-analytics overview
  + drill-down, weakness-options with reasons, marking throughput, the
  s2-evidence-cycle artifacts, pilot-monitor. The measurement IS the product
  surface — no analytics side-build.
- **Success signals:** mastery trajectories move with marked performance;
  Smart Lesson actions track the evidence (INSUFFICIENT_COVERAGE → measured
  low → measured adequate → advance/review); weakness flags concur with
  teacher judgment; κ over real mixed-award marking approaches the 0.60 gate
  on enough paired points to make the release decision a real one.

## Explicitly out of scope (§21 discipline)

No ML recommendation, no BDT recalibration, no full blueprint engine, no
BKT parameter refit during the pilot (calibration is MEASURED first; any
parameter change is a separate, evidence-backed decision), no class-entity
management, no new teacher analytics beyond the shipped drill-down.
