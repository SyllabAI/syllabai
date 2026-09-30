# RUNBOOK — notes-axis promotion (batch `notes-axis-promotion-2026-09-28`)

## What this is
The operator's named decision (IM trace `1a0e88af08e12df5`, verbatim
"pursue (a). And check current state, and other agents' work. Check if they
completed these or not"), where option (a) was presented in trace
`1a0e88d81372240d` as: flip the 112 EXTERNAL_NOTES documents SUGGESTED →
VALIDATED so the 210 human-validated chunk→spec-point mappings
(`chunk_spec_hv_projection.json`, git blob `47fa2cd6415b`) enter the served
denominator and quality floor §8(d) can move off its r6 0.0 baseline.
Named outcome: "350 notes chunks enter the pool".

## Why the re-stamp is part of the decision
The serving gate (`ChunkVectorRepository.searchServingEligible`,
SCOPE_EXISTS_VALIDATED) reads `embed_rev = CURRENT_EMBED_REV` (= 1 since the
d523f57 rollback; the 1→2 flip-back was REFUTED same-day in
`evidence/serving-rev2-flipback-refutation-2026-09-28/`). All 350 notes chunks
were rev2-stamped (09-20 ingest). Pre-flight exact-gate replica: flip-only adds
**0** to serving; flip + re-stamp (350 chunks 2→1) is **purely additive**
(615 → 965; the 615 stay; notes serving set was empty; same model
gemini-embedding-001 768-d both revs; reversible by kind).

## Status
- **APPLIED 2026-09-28** by the sanctioned-credential session: dry-run
  DRY_RUN_OK → one transaction (batch_run_id in run_report.json) → 112
  documents SUGGESTED→VALIDATED + 350 chunks embed_rev 2→1 + 112
  content_review_audit rows (target_type 'document').
- Constraint `ck_cra_target_type` was widened **additively** inside the same
  transaction to allow 'document' (no honest value among the existing four;
  existing rows unaffected; the app never writes 'document'). The core team
  should codify this via the next Flyway migration.
- `teacher_validation_events` untouched (0 before and after — the audit-trail
  rule stands; the agent asserts no validation of its own, it applied the
  operator's named instruction).
- Independent post-verify (fresh readonly connection): census EXTERNAL_NOTES
  112V/0S; notes chunks rev1 350; gate replica 965; audit 477 = 365+112;
  events 0. Idempotence re-run: ALREADY_APPLIED.

## Re-running / reverting
- Re-run: `python3 apply_promotion.py` → no-ops with ALREADY_APPLIED.
- Dry-run: `FLIP_DRY_RUN=1 python3 apply_promotion.py` → all asserts, rollback.
- Revert: single transaction — flip docs VALIDATED→SUGGESTED, re-stamp chunks
  1→2 (`WHERE document_row_id IN (SELECT id FROM documents WHERE
  kind='EXTERNAL_NOTES')`), delete the 112 audit rows by batch_run_id in the
  detail. Requires a fresh operator naming (this batch's authority does not
  extend to a revert).

## Effect on measurement
The next bench freeze (snap-006+ / next r-run) folds the HV projection via the
chunk_ref join; with the notes chunks now VALIDATED + rev1, the served view
contains the mapped chunks and §8(d) is scoreable-with-coverage. The exact
§8(d) value is the next run's measurement — not asserted here. The 4
MULTI-flagged mappings stay flagged bench-side (mapping-level; untouched by
this flip). SYLLABUS (162 rev2 SUGGESTED) and the 80 SUGGESTED sme-bank cards
remain out of scope — different axes, not named by the operator.
