# Evidence Cycle 001 — Round r3 (the post-fix verification round, 2026-09-17)

The FROZEN-protocol verification round proving the `fe01b87` evidence fix
(fire once, at the COMPLETING mark, with the settled total) through the
deployed app. Protocol: `backlog/EVIDENCE-CYCLE-R3-SPEC-2026-09-16.md`
(assertions A1–A9, invariants I1–I6, verdict rules P.5, frozen 2026-09-17).

**VERDICT: PASS** — every assertion and invariant holds; the fix chain is
app-level PRODUCTION VERIFIED. The phase artifacts came from the
`s2-evidence-cycle` workflow (runs listed below); the S0/S3/t0 captures were
produced by the t0 instrument over the operator's read-only Neon path (a
dedicated `t0_readonly` role, SELECT-only + DSN-level
`default_transaction_read_only=on` — zero app-data writes from the
measurement side).

| File | Boundary | Produced by | What it shows |
|---|---|---|---|
| `s0-baseline-t0-capture.json` | S0 | t0 instrument @ 23:03Z | the pre-round baseline: integrity CLEAN (0/0/0); 4CH1-S2-f = 8 measured, mean 0.1384718719; monitor row 3 attempts / 2 correct / 0.3135593220338984 / v3; Flyway V28 |
| `s0-preconditions.json` | S0 | spec's pre-registered check | the r2 trio servable + VALIDATED; monitor baseline intact; ZERO monitor PENDING answers; the 8-row class matrix pinned |
| `s1-after-leg.json` | S1 | run 35161163357 @ 23:11Z | target 4CH1-S2-f (deterministic); 3 STRUCTURED attempts accepted, all PENDING; Smart Lesson + class view correctly UNCHANGED pre-settlement (the r2 defect class does not recur) |
| `s1-marking-dump.json` | S1 | run 35161328200 @ 23:13Z | the marking working set: the monitor's 17 part answers (answer-key texts for 96ae4235/ac5045d7; empty for ddf30066) + the schemes |
| `s1-evidence-extract.json` | S1 | extraction | attempt/answer mapping + the settlement sequence (queue order) |
| `mark-r3.json` | S2 | run 35161655716 @ 23:17–18Z | manifest `evidence-cycle-001-r3` (web 012f88c, sha d995b9c77bc4d6e9…) applied 17/17, zero conflicts; completing marks 23:18:10.875 / 23:18:17.354 / 23:18:25.330 |
| `final-probe.json` | S3 | run 35161751482 @ 23:19Z | Smart Lesson ADVANCE_TOPIC/TOPIC_MASTERED (0.77 over 6 attempts, 6 evidence facts); the closed loop responded to marked evidence |
| `s3-poststate-t0-capture.json` | S3 | t0 instrument @ 23:20Z | post-round state: integrity CLEAN (0/0/0); monitor 6 attempts / 4 correct / 0.7735556016 / v6; class mean 0.1959714068 |
| `verdict.json` | verdict | frozen P.2/P.3 evaluation | A1–A9 + I1–I6 all HOLDS with evidence; BKT trace in true mark order = stored mastery to full precision (0.7735556015738249) |
| `t0-phase4-capture.json` | Phase 4 | t0 instrument @ 23:33Z | the pilot's t0: exit 0, integrity CLEAN, all 25 sections |
| `t0-phase4-verdict.json` | Phase 4 | expected-diff procedure | PASS — only W1 (capture identity) + W2 (decay replication) differences; zero unexplained; zero post-S3 telemetry |

## The acceptance question, answered

1. **Exactly ONE evidence event at the completing mark with the settled
   total and correct=true** — one BKT_UPDATED per topic node (3 for
   ddf30066's 3 nodes; 1 each for the single-node questions); payloads carry
   settled-total `correctness` (true for the two 6/6 attempts — unreachable
   from partial totals); events strictly after the (n−1)th part mark. The
   r2 defect (mis-fire at part-`a` partial totals) did NOT recur — confirmed
   both pre-settlement (Smart Lesson/class view unchanged after the after
   phase) and at settlement.
2. **Smart Lesson shows the honest measured value** — ADVANCE_TOPIC with
   decay-adjusted 0.77 over 6 attempts, evidence trace intact.
3. **The projection advanced consistently** — attempts 3→6, correct 2→4,
   mastery = the frozen BKT recursion over [incorrect, correct, correct]
   seeded with the S75-verified prior 0.3135593220338984 (zero DECAY_APPLIED
   in between); whole-projection audit CLEAN at both boundaries.
4. **The class aggregation propagated exactly** — mean moved by the
   monitor's contribution only (0.1384718719 → 0.1959714068 = +Δmonitor/8),
   measured stays 8, no other learner's row changed.

## Operational notes carried by the record

- One after-phase infrastructure retry (run 35160859448 → 35161163357):
  the first dispatch died on an unhandled health-check socket timeout
  (Render free-tier cold start) BEFORE any mutation — verified read-only
  (0 new rows anywhere) — so I6's no-re-run rule is not engaged (no outcome
  existed to re-run against).
- Dispatch-time gate: core rail RED at 57959ae with failure scope exactly
  1/721 (`ChunkLexicalSearchIT.rankingSanity`, the active T-C14 lane's own
  new test, never green); all pilot-named ITs green in the same run. Web
  rail (the vehicle) green at its head.
- P.6 Amendment #1 (A1's payload keys + intra-transaction ordering) is
  recorded in the spec with its non-weakening justification.
