# Wave-2 prep — F-PROD-2/3/4 executed on production (2026-10-02)

**Status: EXECUTED under the operator directive "Wave-2 prep (F-PROD-2/3/4)"**
(trace 1a0fb74e4c5d4419), continuing the wave-1 PRODUCTION run of the same
date. DB access re-established via the sanctioned session-env read path
(Render env-vars API → `SYLLABAI_DATABASE_URL`, the snap-006 lineage) after
the morning run's session-scoped Neon API key aged out of the sandbox. Every
script runs the fail-closed DB identity gate first (`current_database()` =
`neondb` AND `campaign_db_identity` row `T-C04-CAMPAIGN`/`neondb`, AGENT.md
rule 2 pattern). Read probes are SELECT-only; the one write (F-PROD-4) is a
single guarded transaction, archived before execution, verified after.

## Headline results

| item | disposition |
|---|---|
| **F-PROD-2** (kit poststate resolves ARCHIVED scope) | **CLOSED — joint with the concurrent T-C48 lane.** T-C48 (b507039) landed the poststate fix (ACTIVE-pinned subselects + inline fail-closed DO-block census guard, pack poststate.sql synced, production-verified 2935/2935); this lane's rebase adopts that version (its own separate-gate variant dropped as redundant) and completes T-C48's disclosed staleness: prestate/restamp joined `documents.id` instead of the `document_id` VARCHAR business key and used `:paper_code` instead of `:'paper_code'`. After the fix the kit re-emits the production-proven pack byte-identically for ALL FIVE artifacts. Defect demonstrated live: old predicate 0/0, corrected 2935/2935. |
| **F-PROD-3** (worklist stale; fresh composition needed) | **DONE** — live chunk census exported (4,672 chunks, `live_census_chunks.json.gz`, chunk_ref contract identical to snap-006) and wave-2 composed by the new `bench/validation_worklist_v2.py`: **297 actionable documents / 1,673 SUGGESTED chunks**, ALL on the subject-branch surface. Zero paper-axis SUGGESTED mass remains. |
| **F-PROD-4** (4CH1/2C REJECTED shell) | **REMOVED** — governed single-transaction deletion of the 111-row closure (1 paper + 2 REJECTED empty docs + 7 never-validated questions + 7 versions + 7 schemes + 8 topics + 0 options + 44 parts + 35 mark_points), zero downstream references verified twice (dry-run + in-tx), full row archive retained (`wave2_shell_archive.json`), teacher decision audit trail untouched, lane audit row appended, serving funnel unchanged 2935/2935. |

## The wave-2 surface (probe-verified, sharper than the finding)

The wave-1 finding read "QP/MS documents of unplaced ingest-era papers
(QP 369 + MS 395, subjects NULL/DRAFT curriculum versions)". The live probe
refines it: those 55 QP/MS documents have **no owning exam_papers row at
all** (ingest-era partial imports — the paper rows never existed), and their
chunks carry the **ACTIVE curriculum's subject identity** in the V33
denormalized `document_chunks.subject_id` (D4 probe). Consequences:

- No placement or ingestion repair is needed for wave-2 — the subject-branch
  serving gate (`subjects s2 … s2.id = c.subject_id and
  d.validation_state = 'VALIDATED'`) serves every one of the 1,673 chunks
  the moment its DOCUMENT flips SUGGESTED → VALIDATED.
- The same gate covers the two corpus blocks: EXTERNAL_QUESTIONS 747 chunks /
  80 docs and SYLLABUS 162 chunks / 162 docs, both fully in ACTIVE scope.
- The 64 REJECTED chunks (30 MS + 34 QP on REJECTED docs) are dead by teacher
  decision and excluded from wave-2 by construction.

## The instrument gap — operator decision required before wave-2 execution

No write path flips `documents.validation_state` on core main (audited
2026-10-02): `ContentController` validates papers/paper-versions/mark-schemes
only; `ContentDocumentController` ingests/embeds/searches but never validates;
no SQL migration flips it. Corpus documents are born SUGGESTED (V29) and stay
that way. Two execution options for the 297 document-validate acts:

1. **Governed SQL batch** — the notes-axis promotion precedent
   (112 EXTERNAL_NOTES docs, 09-28, operator trace 1a0e88af08e12df5, batch
   records `9ea54e1`): operator authorizes, batch_run_id recorded, fail-closed
   prestate/poststate, vectors and chunks untouched.
2. **New teacher endpoint** (`POST /api/v1/teacher/content/documents/{id}/validate`
   + content_review_audit row) — the durable instrument; product work on core
   before wave-2 runs. Recommended if more corpus axes are coming.

## F-PROD-4 removal detail

Prestate (dry run, all asserted): paper `7d40476f…` 4CH1/2C June 2020
REJECTED; docs `41bc5a1a…` (QP) / `1cf11a41…` (MS) both REJECTED, 0 chunks;
7 questions `4ch1/past-papers/2020-06/4ch1-2C#q1..q7` (active, never
validated); 7 question_versions v=1 SUGGESTED; 7 mark_schemes SUGGESTED;
8 question_topics; 44 question_parts; 35 mark_points.

Blocking sweep — all zero (dry-run AND re-verified inside the transaction):
attempts, question_attempts, smart_mark_results (by scheme), smart_mark_
agreement_evaluations (by paper), glm_ocr_bridge_records, marking_queue_items,
document_chunks, foreign exam_papers doc pointers.

Run history: execute attempt 1 aborted fail-closed (psycopg2 session-state
bug in the runner — ROLLBACK, zero rows touched); attempt 2 COMMITTED
(2026-10-02 07:34:18Z); attempt 3's prestate assert refuses with "paper rows
= 0" — the idempotence proof (`shell_removal_idempotence_proof.txt`).
Poststate independently verified (`shell_poststate_verification.txt`): all
shell counts 0; `content_review_audit` = 2 historical teacher rows (FLAG
19:09Z, REJECT 21:19Z, 09-28, Nawaf Al Hussain Khondokar) + 1 lane row
documenting the removal; serving funnel 2935/2935 unchanged. By-code census:
4CH1/2C now 16 rows (4 ACTIVE-scope VALIDATED + 12 DRAFT-scope VALIDATED),
one fewer than the 17 before the removal — the shell no longer conflates
sessions per code.

## Kit regression check (F-PROD-2 verification method)

`bench/validation_wave_kit.py` re-run against the committed snap-006 +
worklist bytes with `BENCH_OUT` pointed at a scratch directory: ALL FIVE
artifacts (WAVES.md, prestate.sql, validate_calls.sh, restamp.sql,
poststate.sql) emit **byte-identical** to the production-proven
`evidence/bench-001/validation-waves-2026-10-01/` pack — poststate.sql via
T-C48's synced correction (inline DO-block census guard refusing on
`active_versions <> 1`, the `singleOwnerScope` mirror materialized inside
the generated SQL so any driver refuses), prestate/restamp via this lane's
document_id/psql-param completion of T-C48's disclosed staleness.

## Contents

| file | what it is |
|---|---|
| `probe_output.txt` / `probe_result.json` | the read-only reconnaissance (identity, scope, funnel both predicates, D1–D4 surface census, shell sweep) — runner `wave2_prep_probe.py` |
| `live_census_chunks.json.gz` + `live_census_manifest.json` | the F-PROD-3 composition input (4,672 chunks; snap-006 chunk_ref contract) — runner `wave2_census_export.py` |
| `worklist2.json` + `WORKLIST2_REPORT.md` | the wave-2 worklist (297 actionable documents, gold-unlock priorities) — generator `bench/validation_worklist_v2.py` in the syllabai repo |
| `wave2_shell_archive.json` | full row images of the 111 removed rows (reversible-by-record) |
| `shell_removal_idempotence_proof.txt` | attempt 3: prestate assert refuses (paper already gone) |
| `shell_poststate_verification.txt` | independent poststate verification incl. funnel + audit trail |
| `wave2_prep_probe.py`, `wave2_census_export.py`, `wave2_shell_removal.py`, `wave2_shell_poststate.py` | the runners (all identity-gated, fail-closed) |

## Remaining for the operator

- **Choose the wave-2 execution instrument** (governed SQL batch vs new
  teacher endpoint) — then wave-2 executes the 297 document-validate acts in
  priority order per `worklist2.json`, followed by the Run005C re-record
  against the §8.1 VALIDATED bars.
- Standing items unchanged: post-deploy tutor refusal-rate watch at the 0.50
  floor (T-C42); F-PROD-1 teacher review of the 25 REVIEW_REQUIRED papers.
