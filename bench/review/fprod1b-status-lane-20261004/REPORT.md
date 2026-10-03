# F-PROD-1b status lane — EXECUTION RECEIPT (2026-10-04)

**Status:** EXECUTED — the 49 drifted `glm_ocr_bridge_records` are **SUPERSEDED** on production. The F-PROD-1b governance blocker is discharged end-to-end.
**Authority chain:** ruling `FPROD1B-IDENTITY-RULING-2026-10-04.md` (operator trace `1a102e2dfe703779` "F-PROD-1b call") → execution word (operator trace `1a1030b602705911` **"run the status lane"**). Zero writes outside the designed lane's shape.
**Production branch:** `br-muddy-bar-a5huwldd` (project `billowing-cherry-15418366`, org `org-withered-mud-59985156`). Note: the F-PROD-1 REPORT's `br-purple-sun-a5huwldd` id was stale — WORKLOG's `br-muddy-bar-a5huwldd` + live API agree.

## 1. Preflight — copy-on-write dress rehearsal (read-only for production)

Script: `fprod1b_status_lane_preflight.py` · artifacts: `fprod1b_preflight_result.json` / `fprod1b_preflight_output.txt`. Rehearsal branch `br-noisy-sky-a5xlg7q8` (child of production, throwaway password, deleted after — the credential died with it). Three earlier rehearsal branches from aborted attempts (one 423-conflict abort, one constraint-shape abort, one retry of the same) were also deleted; final branch list clean.

| gate | result |
|---|---|
| identity (`neondb` / `campaign_db_identity` T-C04-CAMPAIGN) | PASS |
| bridge census | 25 REVIEW_REQUIRED + 34 OK (59) — unchanged since Session 169 |
| drift predicate count | **49 exactly** (25 RR + 24 OK) — the ruling's hard pin |
| undrifted records | 10 (stay OK, untouched) |
| `reconciliation_status` domain | varchar + CHECK `ck_glm_ocr_reconciliation_status` = `ANY(ARRAY['OK','REVIEW_REQUIRED'])` — 'SUPERSEDED' NOT allowed → migration must extend the domain first (the ruling's anticipated branch) |
| dress rehearsal (constraint-extend + flip on the branch) | 49 rows updated → **0 RR / 49 SUPERSEDED / 10 OK**; zero collateral status changes; `review_findings`/doc-id payloads byte-intact (md5-verified before/after) |

## 2. The migration — core V60

`V60__fprod1b_bridge_superseded.sql` (branch `fprod1b-status-lane` @ `49072b2` → **PR syllabai-core#75** → merged as **`43bc14d0`**, merge-commit method; head CI build SUCCESS; post-merge main CI build SUCCESS).

Shape: (1) `ALTER TABLE … DROP CONSTRAINT ck_glm_ocr_reconciliation_status` + re-ADD extended to `IN ('OK','REVIEW_REQUIRED','SUPERSEDED')`; (2) a census-gated `DO` block — aborts the deploy (RAISE ⇒ full migration rollback) unless the drift predicate selects exactly 49 on a non-empty table, then supersedes by PREDICATE (the id list is pinned in the preflight receipts, not re-derived at write time). Fresh-DB safe: empty table ⇒ skip + no-op flip. `review_findings`, `qp/ms_document_id`, all other columns untouched.

Behavioral delta (designed, the ruling's point): `ContentReviewService`'s validate-all gate (`"REVIEW_REQUIRED".equals(…)`) stops blocking the 25 serving papers; the entity field is a plain String (no enum); `OK`-equality priority checks treat SUPERSEDED as non-OK (benign ordering). Serving chunk layer untouched — no chunk/document rows changed, only `reconciliation_status` on 49 bridge rows.

## 3. Deploy + post-flight (fresh COW poll)

Script: `fprod1b_postflight_poll.py` · artifacts: `fprod1b_postflight_result.json` / `fprod1b_postflight_output.txt`. Poll branch `br-aged-dust-a51nbu69` created from production, SELECT-only checks, deleted after.

| gate | result |
|---|---|
| `flyway_schema_history` V60 | **applied, success=true, 2026-10-03T18:56:25.633295Z** |
| bridge census | **0 REVIEW_REQUIRED / 49 SUPERSEDED / 10 OK** |
| drift set identity | 49 drifted, **all 49 SUPERSEDED** (split informational: qp-drifted 39, ms-drifted 49 — the OR predicate) |
| REVIEW_REQUIRED residual | 0 |
| live constraint | includes `'SUPERSEDED'` in the domain |
| poll branches | deleted (credentials dead) |

## 4. Consequences

1. **validate-all is unblocked on the 25 F-PROD-1 serving papers** — the gate no longer guards a dead import. The 62 print-dependent review rows REMAIN OWED in the records repo (worksheet v2; P1 7 mismatch → P2 23 identity → P3 32 banked parse-side) — the review debt never depended on the DB gate.
2. **The findings survive as data**: `review_findings` payloads byte-intact on the rows; the packet (`762896b`), disposition (`1835fd5`), ruling (`d2befa9`) are the canonical review surface.
3. **Fresh bridges compute only on future re-ingests**, against the then-current lineage.
4. Secrets discipline: the Neon key lived in a session-only env file outside every repo, is in no committed artifact (pack scanned clean), and the env file is purged post-lane; the standing rotation reminder applies to it as before.
