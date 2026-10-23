# ADR-036: Research endpoint k-anonymity on the wire (the C7 resolution)

**Status: Accepted** (ACCEPT recorded 2026-10-23 by the operator's ACCEPT word, chat
trace 1a169835f503b151; drafted 2026-10-04 under T-COORD-3 R-D, operator directive
trace 4acec4babbc5db5c842fa4bce379e604). The operator's ACCEPT flip was the
ratification step; this ADR does not self-accept. See "ACCEPT of record" below.

## Context

ADR-033 (BKT emission is format-aware) carried one open follow-up that is not
gated on data:

> "The research endpoint spans all learners and is nodeId-filterable; an n<5 band
> could be cross-read against class surfaces to infer an individual. Decide:
> ADMIN-only, class-scoping, or n<k suppression."

The C4 protocol §4.2 borrowed the n<5 row floor as "a floor, not the answer".
An implementation now exists as **syllabai-core PR #62** (head `b3e53f6`, base
`c4b67e8`, core-ci SUCCESS 2026-10-02, open, unmerged, base-stale — moved-base
protocol due at its merge word per the fleet census in `TODO.md`).

## The decision implemented in PR #62 (authored by the owning lane)

**k-anonymity on the wire, the unit is the learner** — calibration cells under
5 distinct learners hide their outcomes but keep their counts.

- **ADMIN-only — rejected** (per the PR's own argument): authorization is not
  disclosure control. An admin holds every class surface (the strongest
  cross-read position) and is exactly the §2 nodeId-slice drift-forensics user
  the instrument serves; narrowing the audience loses the teacher audience the
  gate exists for.
- **Class-scoping — rejected**: calibration is a property of the population
  served, not of a class roster; scoping re-opens the inference vector it
  claims to close.
- **n<5 suppression on the wire — chosen**: enforced by the API itself
  (`k = 5`, unit = distinct learners), so no surface — teacher, admin, or
  research — can observe a sub-k cell's outcomes regardless of authorization.

## Consequences

- The research endpoint becomes self-defending: the invariant lives in the
  response, not in caller discipline.
- Teachers keep count visibility (counts are not suppressed, outcomes are).
- Any future k change is an ADR-level decision (privacy parameter, not a tuneable).
- ADR-033's open follow-up closes; the C4 §4.2 "floor, not the answer" note is
  resolved by this answer.

## Verification gate (before ACCEPT)

1. The operator reviews PR #62's implementation of the learner-unit rule
   (distinct-learner counting, not row counting) against this ADR.
2. Moved-base protocol: rebase/merge onto current core main, core-ci green.
3. Operator merge word on PR #62 with this ADR's ACCEPT recorded in the same
   session (the T-C72/T-C76 pattern: decision, merge, and receipt in one trace).

## ACCEPT of record (2026-10-23)

The operator's ACCEPT word is chat trace `1a169835f503b151` (2026-10-23). The
T-C72/T-C76 pattern — decision, merge, and receipt in one session — completes here:
the decision is this banner + section, the merge of record is **syllabai-core PR #62**
(merge `bbc438e86ec4739709f40c0f393bc9ee3ee18153`, 2026-10-04), and the receipt is the
verification-gate evidence below.

Verification gate, leg by leg:

1. **Implementation review — PASS.** The merged learner-unit rule on core main
   (`LearnerModelCalibrationService.java`) counts DISTINCT learners, not rows: per-cell
   `Set<UUID> learners` and per-bin `Set<UUID> binLearners` accumulators gate every wire
   statistic on `MIN_REPORTABLE_LEARNERS`. `k = 5` is a code constant, deliberately not
   configuration (a privacy floor, not a tuneable). Sub-k cells render all outcome
   statistics `null` with `suppressed: true` while counts stay visible (sampleCount,
   learnerCount, bin counts, skippedRows); empty segments render honest zeros with
   `suppressed: false` (no evidence, never hidden evidence); suppressed bins still
   contribute to segment aggregates (excluding them would select-bias the statistic).
   Wire surface: `GET /api/v1/research/learner-model/calibration`. Tests: the PR's
   +365/−122 battery on `LearnerModelCalibrationServiceTest`.
2. **Moved-base protocol — SATISFIED.** PR #62 merged onto core main 2026-10-04, and
   core-ci is green on the current core main head carrying the merged code
   (`6cad6ef9463e`, run 37204223285 success).
3. **Operator merge word + ACCEPT in one session — THIS SESSION.** The merge word is
   the ACCEPT trace itself; the merge of record predates it (2026-10-04, owning lane)
   and is ratified here.

Consequences now of record: ADR-033's open follow-up is closed; the C4 §4.2 "floor,
not the answer" note is resolved. The F-186 battle wave's matchmaking/brackets gate
(operator ruling trace `1a1693693b033a2d`) cites an ACCEPTED ADR on its ADR-036 arm;
its realtime-infra arm is unchanged.
