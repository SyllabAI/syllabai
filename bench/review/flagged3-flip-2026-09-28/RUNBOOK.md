# RUNBOOK — flagged3 flip execution

**EXECUTED 2026-09-28T11:32Z — APPLIED.** batch_run_id `0d5e4c4a-cacc-454c-9dfe-5983e1f11661`:
dry-run DRY_RUN_OK -> single transaction -> census 296V/80S/3F -> 299V/80S/0F; idempotent
re-run ALREADY_APPLIED; independent 8-point landing verification PASS (3 docs VALIDATED,
audit 365 = 362+3, 80 neighbors untouched, teacher_validation_events 0). Two
production-blocking defects fixed pre-apply, both caught fail-closed with zero writes:
(1) derived-not-probed census gate (corrected in db17167912); (2) the kit keyed documents
by documents.id while the decisions carry document_id varchar (row uuids
bf07304e/d84be99c/bccdacb2), assumed a flat render-env format (the sanctioned file is
{"env":[{key,value},...]}) — and the audit rows needed the proven wave vocabulary
(target_id = row uuid, varchar in detail). All fixed in the executed apply_flip.py.
Run report: evidence/bench-001/flagged3-flip-2026-09-28/.

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

**CENSUS CORRECTION 2026-09-28 (pre-execution, this session):** the kit author held no
production credentials and recorded a derived (not probed) census — 306V/747S/3F, whose
total 1,056 equals the snap-003 EQ *chunk* count, not the EQ *document* census. Live
probed twice (sanctioned scripts/.render_env.json, SELECT-only): documents total 999;
EXTERNAL_QUESTIONS **296 VALIDATED / 80 SUGGESTED / 3 FLAGGED / 0 REJECTED**. All
census figures in this RUNBOOK, SHEET.md and flip_decisions.json are amended to the
probed values; the decision and the +3/−3 delta are unchanged. The integration test
remains valid — it exercised the tool's paths, and its scratch was seeded to the then-
recorded (wrong) numbers; the production gate now compares against the probed truth.

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
`{VALIDATED: 296, SUGGESTED: 80, FLAGGED: 3, REJECTED: 0}`, all 3 cards reported pre_state FLAGGED.
Anything else → STOP, do not force; re-verify against the freeze.

## 2. apply (single transaction, fail-closed)

```bash
SYLLABAI_DATABASE_URL='...' python3 apply_flip.py
```

Expected: `"status": "APPLIED"`, census_after `{VALIDATED: 299, SUGGESTED: 80,
FLAGGED: 0, REJECTED: 0}`, final_states all VALIDATED, audit_rows_committed 3. Re-running prints
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

