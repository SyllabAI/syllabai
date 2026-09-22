# CORRECTIONS to the G-4 round record — session 116 re-audit, 2026-09-22

Found while preparing the human-round handover. The frozen data files in this
directory are NOT modified (SHA256SUMS stands); this document corrects the
PROSE claims made about them. Additive, in the project's explicit-reconciliation
pattern. Three corrections, in descending severity.

## Correction 1 (significant) — the `authoritative` flag was TRUE on every part; the round prose claimed FALSE

**Claimed (README §4, `release_state_per_part.json` note, PROGRESS/WORKLOG
session 115):** "per-part `authoritative=false` pre-gate (honest gated state
verified end-to-end)" and "the release gate honestly unchanged".

**Captured data:** every one of the 26 captured parts in `smart_results.json`
and `release_state_per_part.json` records `"authoritative": true` — including
the refused part. The "false everywhere" note is hardcoded prose in the
packaging script, contradicted by the verbatim responses sitting next to it.
The data is the ground truth of what production returned.

**Code facts (unchanged across `14b5e3d` → `ad44cee` → `e7a55fe`; file created
at `a86c30d` and never touched since):** the student surface computes
`authoritative = smartMarkService.kappaGatePassed(question.examPaperId())`
once per attempt (`StudentSmartMarkService`); `kappaGatePassed` is fail-closed
— absence of any evaluation row yields `false`, and `true` requires the
NEWEST κ evaluation row for scope ALL (or the paper) to have
`passed = kappa ≥ 0.60`.

**Security facts:** `/api/v1/teacher/**` requires `TEACHER|ADMIN`
(`SecurityConfig`); this round held only a STUDENT token (public-register
learner, verified) and made zero teacher-endpoint calls. The round did not —
and could not — have written an evaluation row.

**Timeline:** the 2026-09-16 production captures (`evidence/cycle-001-r3/`,
`s0/s3/t0-phase4` files) show `max_kappa: null` — no evaluation rows existed
then.

**Conclusion:** production returned `authoritative=true` only if a **passed κ
evaluation row existed in the production database at execution time** (scope
ALL, or the 4CH1 paper), created by operator-side teacher/admin activity
between 2026-09-16 and 2026-09-22. Provenance is not determinable from the
sandbox. The residual alternative — a deployed build diverging from canonical
main in these exact files — has no supporting evidence: the observed response
shape (`pointLabel`, per-point partial `marksAwarded`) matches the 1.2.0 line
byte-for-byte, and the endpoint's existence constrains deployed ≥ `a86c30d`,
where the wiring is already current.

**Consequences:**

1. The release gate was **OPEN** during the round. Session 115's "release
   gate honestly unchanged / remains CLOSED" is RETRACTED.
2. The round's accepted marks carried `authoritative=true` at the student
   surface, and the completing attempts fired BKT evidence for the TEST
   learner under the open gate (research-side effect limited to
   simulated-learner test data; no student-facing harm — the learner was the
   round's own test account).
3. The κ numbers themselves are UNAFFECTED (computed offline from frozen
   artifacts; the pairing code is byte-unchanged on the current line).

**Remediation = the sanctioned human round itself:** `kappaGatePassed` reads
the NEWEST row per scope (`OrderByComputedAtDesc`), so the operator's Step 3
evaluation supersedes whatever row exists; a failing human round re-closes the
gate (fail-closed restored). The human-round package therefore adds a
**Step 0 preflight**: `GET /api/v1/teacher/marking/kappa/latest` (ALL and
paper scope) and RECORD kappa / sampleSize / computedBy / computedAt before
any marking — if a passed row of unknown provenance exists, halt and decide
(keep-and-document or supersede) BEFORE the round.

## Correction 2 — the round ran against pipeline 1.2.0, not 1.1.0

The runbook (Step 2 contract facts) and the round prose say "pipeline version
1.1.0". In reality canonical core main advanced on 2026-09-21
(`14b5e3d → ad44cee`, concurrent lane, sessions 112–116) — including
`fa59342` **"partial marks within compound points — pipeline 1.2.0"** and the
feedback-transaction fixes — and Render auto-deployed it before the round.

**Proof from the captured responses themselves:** the breakdown entries carry
`pointLabel` (compact label, no-reveal flow) and per-point partial
`marksAwarded` (3/4, 1/3, 1/2 …) — a shape that exists ONLY in the 1.2.0
line (`git log -S pointLabel` finds nothing before it).

**Materiality:** `KappaAgreementService` and
`TeacherMarkingService.evaluateAgreement` are byte-unchanged
(`14b5e3d → ad44cee → e7a55fe`), so the offline κ port remains an exact mirror
of production pairing — **the κ numbers stand unmodified**. The convention pin
(any credit = 1) is unchanged and becomes MORE gate-critical: with 1.2.0
partial marks, "any credit" vs "fully earned" divergences are routine (a 1/4
point pairs as 1). The model, G-2 VALIDATED-only selection, and validator
behavior claims are unaffected.

## Correction 3 — "longest part" imprecision

The refused part (`q7|b`) is the **only 5-mark part** and carries the largest
single scheme-point text (1,512 chars), but ranks 3/26 by total input
(`q10|b` 2,153 and `q5|a` 1,885 chars were larger and passed). The precise
statement: the reasoning-heaviest compound point failed, not the longest
input. Full analysis:
`UNPARSEABLE_OUTPUT_INVESTIGATION.md` in this directory.

## What this does NOT change

- The frozen blind discipline (decisions sha256 `255265d7…` frozen before any
  smart call) — verified intact.
- The κ computations and both convention readings (n=25) — the pairing code
  they mirror is unchanged on the canonical line.
- The provenance law: every decision in this round is `AGENT_MARKING`; nothing
  here is teacher/human evidence; the gate requires the operator's genuine
  human reference round (ADR-025/ADR-027), which remains the single remaining
  action — now with a κ-row preflight added.
