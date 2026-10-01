# Card-axis serving boundary — pinned 2026-09-28 (bench/card-serving-boundary)

Operator directive (trace `1a0e67315a95fc09`): "Continue development. Do not wait for
teacher validation. Do not alter validation state or create validation events. Treat the
298 cards as SUGGESTED and non-servable. Build and test against them as non-servable
fixtures, while preserving the serving-validation gate."

## Deliverable (core `b697492` = main, 4 commits on e5cc266)

- **`CardServingBoundaryIT`** (new, Testcontainers, CI lane): row-level proof on real
  Postgres that the T-C27 card shape (EXTERNAL_QUESTIONS, SUGGESTED, subject-linked, no
  exam-paper row) is NON-SERVABLE on both serving surfaces:
  - **vector branch 2** (V33 subject branch): a SUGGESTED card chunk never serves — the
    `d.validation_state = 'VALIDATED'` gate had SQL-text coverage only (T-C20); it now
    has row-level proof.
  - **lexical**: paper-anchored by design (no subject branch — V33); cards structurally
    unreachable at ANY validation state, including on the neutral ALL view (asymmetry
    PINNED: a future lexical widening must be a deliberate reviewed act).
  - **boundary invariant**: zero non-VALIDATED hits across both serving surfaces — the
    arm-B VALIDATION_BOUNDARY_VIOLATION hard fail, encoded as a permanent fixture test.
  - **dual-view design pinned**: neutral surfaces still return SUGGESTED rows (vector:
    papers + cards; lexical: papers only) — guarded against over-tightening.
  - **flip contract**: card serves ONLY when its own document turns VALIDATED (inside
    the throwaway container) — proves exclusion is state-driven, not kind-driven; this
    is exactly the mechanism the operator's card wave relies on when it lands. No
    production write, no agent-asserted validation.
- **`ChunkLexicalRepositoryTest` +4**: serving-eligible null-scope rejection, blank-query
  fail-closed, T-C05 VALIDATED-gate SQL (paper branch only, single-occurrence asserted,
  subject-branch absence asserted), bind order. Mirrors the vector T-C20 coverage.

## Evidence

- Branch CI run `36384982647` SUCCESS (rebased on e5cc266, head b697492): full build +
  surefire (894 unit incl. 9 lexical-repo tests) + failsafe (112 ITs incl. 7 card-boundary).
- Main ff-merge: `b697492` verified on origin/main.
- Production probed read-only before/after (SELECT-only): EQ docs 378 SUGGESTED + 1
  VALIDATED unchanged; `teacher_validation_events` = 0 rows; no production write of any kind.
- Self-diagnosing seed sanity (runs live in the IT): any future premise break (fixture
  drift, migration drift, gate change) fails with the exact counts needed to localize it.

## Fixture bugs caught by the IT itself (both fixed, recorded as design facts)

1. `exam_papers.question_paper_document_id` holds the documents.**document_id STRING**
   (production semantics probed: 90 papers match string-wise, 0 match row-UUID-wise) —
   the IT failed closed until the fixture used the production shape.
2. `websearch_to_tsquery` is AND-semantics — the lexical view only matches content that
   carries the full query vocabulary. Fixture content aligned; the constraint is now
   documented by the seed sanity expectations (vector 6 / lexical 4).

## Cross-lane note (attribution, not my lane)

Main-HEAD CI run `36385458606` FAILED after identity lane commit `2f117073a`
(rate limiting at the security-chain boundary): `RateLimitFilter` fails to instantiate in
the IT Spring context ("No default constructor found"), breaking ApplicationContext load
for ALL @SpringBootTest ITs — including pre-existing ones (EmbedBackfillReplayIT,
ArmAReplayIT, InterventionRunFlowIT) and this lane's. The identical content ran GREEN on
the branch run pre-2f117073a. Attribution: identity lane; card-boundary lane clean.
