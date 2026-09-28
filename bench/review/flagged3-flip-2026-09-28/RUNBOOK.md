# RUNBOOK — flagged3 flip execution

**INTEGRATION-TESTED 2026-09-28: 23/23 checks green** on a scratch PostgreSQL 17.2
(self-signed SSL, `content_review_audit` DDL verbatim from core V22 incl. CHECKs,
seeded to the exact 306V/747S/3F census): dry-run OK + zero writes; census-drift
abort; per-card pre-state abort; foreign-batch abort; real apply (APPLIED,
309V/747S/0F, 3 audit rows with the exact vocabulary + provenance detail);
idempotent re-run (ALREADY_APPLIED, no double-apply); post-apply external drift
(INCONSISTENT, manual review). The harness also caught one real bug pre-production
(zero-count census states vanish from GROUP BY — census now normalizes explicit
zeros; the recorded census vocabulary includes REJECTED: 0 so any rejected EQ doc
triggers drift-abort).

The decision is RECORDED (operator trace `1a0e7865c3b35715`); execution needs a session
holding the sanctioned production connection material (the per-session handoff, or
`scripts/.render_env.json` — the snap005 path). Any session with either can finish this
in one command. The agent that prepared this kit holds neither, by its own honest census.

## 1. (optional, recommended) dry run — zero writes

```bash
cd <records repo>/bench/review/flagged3-flip-2026-09-28
SYLLABAI_DATABASE_URL='...' FLIP_DRY_RUN=1 python3 apply_flip.py
```

Expected: `"status": "DRY_RUN_OK"`, census_before exactly
`{VALIDATED: 306, SUGGESTED: 747, FLAGGED: 3}`, all 3 cards reported pre_state FLAGGED.
Anything else → STOP, do not force; re-verify against the freeze.

## 2. apply (single transaction, fail-closed)

```bash
SYLLABAI_DATABASE_URL='...' python3 apply_flip.py
```

Expected: `"status": "APPLIED"`, census_after `{VALIDATED: 309, SUGGESTED: 747,
FLAGGED: 0}`, final_states all VALIDATED, audit_rows_committed 3. Re-running prints
`"status": "ALREADY_APPLIED"` (idempotent by batch id, no double-apply possible).

## 3. record the execution (records lane)

- Save the stdout JSON as `evidence/bench-001/flagged3-flip-2026-09-28/run_report.json`.
- Append the outcome (batch_run_id + census_after + final_states) to T-C27.yaml's
  `flagged3_flip_2026-09-28` block and TODO.md's open-items line; commit records.

## Guarantees (what the script will and will not do)

- WILL: move exactly the 3 pinned documents FLAGGED → VALIDATED; write exactly 3
  `content_review_audit` rows (`target_type='question'`, the wave-import vocabulary);
  abort on census drift, pre-state mismatch, foreign prior VALIDATE rows, or any assert
  failure — rolling back everything; never print or persist connection material.
- WILL NOT: touch any other document, any chunk row, any embedding, any bank row;
  fabricate spec linkage (the honest skips stand); re-apply when already applied.

## Standing boundary note

The flip decision is the operator's own (named instruction, recorded verbatim in
`flip_decisions.json`). The executing agent asserts no validation of its own — the audit
detail says exactly that. After the flip the 3 cards satisfy the VALIDATED-only serving
gate; whether the live read filter serves them (embed_rev question, TODO) is a separate,
already-recorded probe — not assumed here.
