# Evidence Cycle 001 — durable snapshots

Raw JSON snapshots from the production evidence cycle of 2026-09-15
(record: `backlog/EVIDENCE-CYCLE-001-2026-09-15.md`). Copied from the GitHub
Actions artifacts so the evidence outlives artifact retention. Each file was
produced by the `s2-evidence-cycle` workflow against production
(https://syllabai-core.onrender.com) with the sanctioned PILOT_TEACHER_* /
PILOT_MONITOR_* credentials — EXCEPT the three Session-75 files (bottom of the
table), which were produced by direct read-only/reconciling SQL against the
production Neon database via the operator-provided Neon API path (no app
credentials involved; see `backlog/EVIDENCE-CYCLE-001-2026-09-15.md` §
"Reconciliation EXECUTED").

| File | Phase | Workflow run | What it shows |
|---|---|---|---|
| `precheck-before-marking.json` | precheck | 34967504208 @ 12:12 UTC | BEFORE: 0 weak topics / 9 coverage gaps / 34 serving questions — the honest empty weakness lane |
| `smartmark-assist.json` | smartmark | 34967933402 @ 12:16–12:24 | Smart Mark assist: 105 provisional / 150 honest FAILED (NO_SCHEME_POINTS, missing schemes) across 15 paper groups |
| `mark-r1.json` | mark (r1) | 34968747628 @ 12:25–12:33 | 255/255 human marks applied (manifest sha 269f13b5…); queue cleared: PENDING 0, HUMAN_MARKED 52, OVERRIDDEN 203 |
| `precheck-after-marking.json` | precheck | 34969674690 @ 12:34–12:35 | AFTER: 8 weak topics (LOW_MEAN_MASTERY), the class evidence populated |
| `after-leg.json` | after | 34970283178 @ 12:40–12:42 | Weakness → targeted test (S2-f, 3 q / 30 marks) → monitor learner's 3 new attempts (PENDING) |
| `mark-r2.json` | mark (r2) | 34970915089 @ 12:47 | Round-2 marking 17/17 (manifest sha ad99c75b…); the loop feeding itself |
| `final-probe.json` | final | 34971418531 @ 12:52 | Smart Lesson response: LOW_MASTERY with the measured evidence trace (attempts=3, mastery 0.12); S2-f class view: 8 measured, mean 0.1137, 14 evidence-backed attempts |
| `reconciliation.json` | prepared | session 73 (2026-09-15) | the PREPARED deterministic recomputation: validated replays (contaminated [F,F,F] → 0.11533544411262374 exact; corrected [T,T,F] → 0.3135593220338984), guarded repair SQL + rollback, RECOMPUTATION-not-reset rationale |
| `reconciliation-investigation.json` | investigate | session 75 @ 2026-09-15 ~17:5x UTC | READ-ONLY production investigation: the affected-row before-snapshot (bit-exact guard match, no decay intervention), the full 3-attempt chain with per-part marks, and the WHOLE-PROJECTION audit — 47 skill_states rows, exactly ONE mismatch (the known contaminated row), zero settled-without-evidence, zero duplicates |
| `reconciliation-execution.json` | repair | session 75 @ 2026-09-15 18:00:34 UTC | EXECUTION AUDIT of the prepared guarded UPDATE in one transaction (FOR UPDATE shape re-verify → UPDATE → rowcount 1 → COMMIT): before/after snapshots, exactly ONE of 47 rows changed, row count unchanged, whole-projection audit 0 mismatches post-repair, prepared rollback preserved |
| `postfix-verification.json` | verify | session 75 @ 2026-09-15 ~18:0x UTC | POST-FIX VERIFICATION: corrected learner state (0.3135593220338984, correct 2/3, version 3), Smart Lesson decision replication (LOW_MASTERY, raw 0.3136 / decay-adjusted ≈0.311 — same code, honest value), class propagation (8 measured, mean 0.1384718718825788, legitimately still weak), integrity invariants all 0 |

Note on `mark-r2.json`'s PENDING=10: answers created by the concurrent CLA
eval lane between the dump and the marking — left untouched for that lane,
documented in the cycle record.
