# Evidence Accumulation t0 Measurement Procedure (2026-09-16, Session 76)

**Status: PREPARED — not yet executed.** The capture scripts are written,
schema-validated against the real Flyway V1..V26 schema, and execution-tested
against a local Postgres loaded with the real migrations plus representative
cycle-001-shaped data (including a negative control proving the integrity
audit detects injected contamination). Execution against production requires
the operator's Neon path (the same read-only access pattern Session 75 used)
and will be recorded as VERIFIED only when actually run.

## Why a procedure, not just a baseline document

The Session-73 baseline (`EVIDENCE-ACCUMULATION-BASELINE-2026-09-15.md`) is a
**record of what the cycle-001 data showed** — assembled from workflow
artifacts after the fact. That record is correct for its purpose, but it is a
reconstruction, not a measurement procedure. The repaired historical state
(`0.3135593220338984`, verified Session 75) must not become the pilot's t0
"merely because it is now corrected": t0 must be a **fresh, reproducible
capture at a defined moment**, so that t1 can be measured the same way and
the delta attributed to pilot evidence — not to measurement drift.

This document defines that procedure once, so t0 and t1 differ only in when
they run, never in how.

## The procedure

**Instrument:** `scripts/ops/t0_capture.sql` + `scripts/ops/t0_capture.py`
(syllabai-web repo, siblings of the existing s2 pilot ops scripts).

**Execution (operator, or a session holding the Neon path):**

```bash
cd scripts/ops
DATABASE_URL='<the read-only Neon DSN>' python3 t0_capture.py --out t0-artifact.json
```

**Contract:**

1. **Read-only by construction.** The SQL file is SELECT-only; the runner
   opens the session with `default_transaction_read_only = on` plus a 60s
   statement timeout and TLS. No credential is ever hardcoded or printed;
   the DSN comes from the environment and lives only in an untracked, 0600
   file (the Session-75 discipline).
2. **t0 is a moment, not a derivation.** The artifact records the capture
   timestamp, the repo lineages (application SHAs — core/web/parser/
   resources/tracker, with dirty-state flags), the server identity, and the
   Flyway head, so the artifact can always answer "what exactly was
   measured, when, on what".
3. **Integrity is audited AT CAPTURE, not later.** The Session-75
   whole-projection audit (stored `skill_states` vs evidence-derived values
   per learner×topic, replicating `EvidencePublisher.topicNodeIds()` —
   primary ∪ secondary), the settled-without-evidence check, and the
   duplicate-row check all run as part of t0. A non-empty invariant BLOCKS
   the pilot start (exit code 2); the artifact's `integrity.verdict` must
   read `CLEAN`.
4. **No PII beyond ids.** Learner/topic UUIDs are retained (the same
   population must be trackable at t1); emails are never selected.

## What t0 captures (the directive's checklist)

| Requirement | Section | How |
|---|---|---|
| timestamp | T0.1 | `now()` + capture timestamp + server identity |
| application SHA | artifact header | repo lineages recorded by the runner (the DB contributes the Flyway head; Render's deployed SHA remains unverifiable without the token — the lineage pins what was measured) |
| learner/topic population | T0.2 | enabled STUDENT count; knowledge_nodes by type × validation state |
| measured topics | T0.3 | per-topic aggregation over skill_states, replicating the ClassAnalyticsService read model (mean of STORED mastery, LOW/DEVELOPING/SECURE bands at 0.45/0.8) |
| weak topics | T0.3 | `weak = mean < 0.45` — the same ceiling weakness-options and Smart Lesson use |
| mastery distribution | T0.4 | full stats + 10-bucket histogram + the complete learner×topic matrix |
| attempts | T0.5 | by marking_state × evidence_emitted, by provenance; answer-level marking states |
| settled marks | T0.5 | settled attempt rows with totals + raw correctness (the ground truth) |
| evidence count | T0.6 | BKT_UPDATED telemetry aggregate + full event-level detail (ids, correctness, marks, topicNodeIds — the audit trail t1 compares against) |
| tutor signals | T0.8 | tutor_topic_engagements (structured, deterministic-matcher output only) |
| Smart Lesson state | T0.9 | the INPUTS the ladder reads (raw mastery, last_practiced_at, attempts) + the runner's replication of the production decay semantics (Ebbinghaus, τ=30/90/365 by band, floor 0.1) — labeled as replication; the live decision surface remains the app's |
| targeted-test state | T0.10 | intervention_run records + servable-question inventory per topic (the real ServableQuestionSpec rule in SQL: active AND (non-structured OR current version VALIDATED) AND paper not rejected) |
| (gate inputs) | T0.11 | smart-mark run counts + κ evaluation state |

## Validation performed (2026-09-16, local)

- **Schema validation:** every `table.column` reference cross-checked against
  a table→column map parsed from the real Flyway V1..V26 migrations —
  0 errors (the only warnings are CTE/lateral aliases, manually verified).
- **Execution validation (stronger):** a real embedded Postgres was loaded
  with the actual 26 Flyway migrations, seeded with representative
  cycle-001-shaped data (2 learners, 2 topics, a settled 6/6 multi-part
  attempt, an auto-graded MCQ, matching evidence events and skill_states, a
  tutor engagement, an intervention run, smart-mark + κ rows). All 25
  statements execute cleanly; the class-state aggregation, evidence counts,
  servable inventory, smart-mark counts, and the decay replication all
  assert to expected values.
- **Negative control:** deliberately corrupting `skill_states.correct_count`
  is DETECTED by the T0.7 audit — the invariant queries provably work, not
  merely run.
- **Defect found and fixed during validation:** the first draft of the
  projection audit joined only `question_topics` (secondary mappings),
  missing the primary-topic path — the local execution caught it as a false
  mismatch, and the query now replicates `topicNodeIds()` exactly
  (primary ∪ secondary, deduplicated). This is exactly why local
  execution validation was required before shipping the procedure.

## When t0 is executed

The gates before the pilot (already documented in the baseline): CI restored
and the fix chain verified, the live r3 round green. **t0 is captured after
r3 closes and before the pilot's first new evidence event** — the t0
population then includes r3's correctly-credited attempts, and t1 measures
the pilot's own accumulation from a clean, audited starting state. If the
operator prefers a t0 before r3 (to include r3 in the measured delta), that
is equally valid — the procedure is the same; the choice only changes what
t0–t1 attribute to the pilot versus to r3. The recommended default: capture
t0 immediately after r3 (r3 is verification of the fix, not pilot evidence).

## Relationship to the existing baseline document

`EVIDENCE-ACCUMULATION-BASELINE-2026-09-15.md` remains the authoritative
**narrative** baseline (what cycle-001 showed, with the contamination status
chain). This procedure is the **instrument**: when executed, its artifact
becomes the machine-readable t0 that t1 is measured against, and the
baseline document's t0 values are superseded by the captured ones where they
differ (they should not differ materially — the state has been repaired and
audited clean; but t0 will say so itself, freshly measured).
