# ADR-036: Research endpoint k-anonymity on the wire (the C7 resolution)

**Status: Proposed** (drafted 2026-10-04 under T-COORD-3 R-D, operator directive
trace 4acec4babbc5db5c842fa4bce379e604). The operator's ACCEPT flip is the
ratification step; this ADR does not self-accept.

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
