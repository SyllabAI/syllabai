# RUNBOOK — wave-2 validation batch (`wave2-validation-2026-10-02`)

## What this is
The operator's named decision (IM trace `1a0fb9dd09110041`, verbatim
"Proceed. Here is neon api if you need it."), answering the wave-2 prep
REPORT's single open instrument decision: how to execute the 297
document-validate acts composed by F-PROD-3
(`evidence/bench-001/wave2-prep-2026-10-02/worklist2.json`,
sha256 `74f02916…`). The in-session provision of a Neon API key sanctions
the **governed SQL batch** instrument (notes-axis precedent `9ea54e1`,
batch `notes-axis-promotion-2026-09-28`) over the teacher-endpoint product
route — the endpoint remains the durable follow-up if more corpus axes are
coming. Task record: `.syllabai/tasks/T-C54.yaml` (claimed T-C53, honestly
renumbered T-C53→T-C54 after an ID race with the flashcard-scheduling lane).

## Status
- **APPLIED 2026-10-02T08:31:44Z** (batch_run_id
  `14cb8ae4-beca-4b25-8568-2e99249e7fb4`): **297 documents
  SUGGESTED→VALIDATED** + **297 content_review_audit rows** (action
  VALIDATE, target_type 'document', actor = the operator, decision_text
  verbatim) — in ONE transaction, committed only after every assert passed.
- **Serving gate (exact `searchServingEligible` replica,
  `CURRENT_EMBED_REV = 2`): 2,935 → 4,608** (+1,673 exactly) — the wave-2
  subject-branch surface entered the pool: EXTERNAL_QUESTIONS 747,
  SYLLABUS 162, QUESTION_PAPER (orphaned) 369, MARK_SCHEME (orphaned) 395.
- **Zero chunk writes**: no re-stamp was required — the dry-run proved all
  1,673 actionable chunks were already embedded and rev2-stamped
  (chunks snapshot: 4,672 chunks, 4,672 embedded, all rev2 — unchanged
  pre/post). `teacher_validation_events` 0 before/after (delta 0 enforced
  in-transaction). No DDL: `ck_cra_target_type` was pre-verified to already
  include 'document' (widened additively by the 09-28 batch); the runner
  ABORTS if absent rather than re-widening.
- The agent asserts **no validation of its own** — it applied the
  operator's named instruction; every audit row records the operator as
  the deciding actor.

## Fail-closed chain (what had to pass, in order)
1. DB identity gate (`neondb` + `campaign_db_identity` T-C04-CAMPAIGN row).
2. Idempotence probe (no prior rows for this batch).
3. Scope resolution with the F-PROD-2 fail-closed census guard: exactly one
   ACTIVE curriculum_version, pinned `356840e6…` (4CH1-2017).
4. Live drift rule: the live SUGGESTED surface across the four kinds equals
   the worklist exactly (297 docs / 1,673 chunks) — nothing moved since the
   07:38Z census.
5. Per-doc fidelity 297/297: kind, state, chunk count, embedded, every
   chunk subject-resolved into the ACTIVE cv.
6. Non-interference: EXTERNAL_NOTES 112V/0S; full state×kind documents
   census snapshot compared pre/post with only the 297 flips allowed;
   chunk-table snapshot byte-equal; audit delta exactly +297; events delta 0.
7. Gate replica: pre 2,935 (asserted) and post 4,608 (asserted in-tx) —
   the +1,673 proving every flipped document's chunks actually serve.

Dry-run discipline: **DRY_RUN_OK first** (all asserts, rollback). The dry
runs caught two real runner bugs (an audit rowcount mis-assert; a census
compare that kept zero-valued phantom keys) — both fixed, zero production
effect (the transaction rolled back both times). The executed run then
passed every assert first try.

## Independent verification (fresh READONLY connection, driver-enforced)
`post_verify_independent.json`: census re-read (all five kinds as expected;
the 4 QP + 4 MS SUGGESTED survivors are chunkless docs outside the named
297 — see disclosure below); gate replica 4,608; the wave-2 delta re-derived
**from the audit trail** (batch_run_id → documents → embedded rev2 chunks
subject-resolved): 747 + 162 + 369 + 395 = 1,673; 297 audit rows in the
batch window; `teacher_validation_events` 0; chunks 4,672/4,672/rev2.
Idempotence re-run: **ALREADY_APPLIED** (exit 0, no-op).

## Disclosure: the 8 chunkless SUGGESTED documents
The post census keeps `SUGGESTED|QUESTION_PAPER = 4` and
`SUGGESTED|MARK_SCHEME = 4`: eight ingest-era documents with **zero
chunks**, never in the worklist (its census counts chunks), invisible to
the serving gate either way. Untouched by this batch; listed here because
the honest post state is not a flat zero across the four kinds.

## Re-running / reverting
- Re-run: `python3.13 apply_wave2_validation.py` → no-ops with
  ALREADY_APPLIED.
- Dry-run: `FLIP_DRY_RUN=1 python3.13 apply_wave2_validation.py` → all
  asserts, rollback.
- Revert: single transaction — flip the 297 documents VALIDATED→SUGGESTED
  (documents joinable from the batch's audit rows via batch_run_id), delete
  the 297 audit rows by batch_run_id. Requires a fresh operator naming
  (this batch's authority does not extend to a revert).

## Connection material handling
The Neon API key provided in-session is stored 0600 at
`/home/z/my-project/scripts/.neon_api_key.txt` (outside every git tree);
the pooled production connection URI it resolves (Neon API
`GET /v2/projects/{id}/connection_uri?branch_id=…`, org-scoped listing via
`/users/me/organizations`) is stored 0600 at
`/home/z/my-project/scripts/.syllabai_db_url.json`. Neither is printed in
full anywhere, persisted in the repo, or embedded in this pack. Both are
DB-credential-equivalent: the T-C52 credential-rotation residue item
remains operator-held (this key being fresh does not change the
discipline — rotate whenever exposure is suspected, and note the API key
can reveal the DB URI by design).

## Effect on measurement
Document validation moved the **REACHABLE pool (2,935 → 4,608)**; it does
not move vector quality. The next measurement step is the **Run005C
re-record against the §8.1 VALIDATED bars** (the first bars a
validated-corpus generation can legitimately clear) — which needs a fresh
corpus freeze (snap-007 from post-wave production) and a maven-capable
environment (this sandbox has none); it is the next lane's work, not
asserted here. Standing operator items unchanged: post-deploy refusal-rate
watch at the 0.50 floor (T-C52 gates: ≥50 post-flip asks or 72 h) and
F-PROD-1 teacher review of the 25 REVIEW_REQUIRED papers.
