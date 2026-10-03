# F-PROD-1b IDENTITY RULING (2026-10-04) — the drifted bridge records are SUPERSEDED-BY-REINGEST

**Status:** RULED — the identity semantics for the drifted bridge records are **superseded-by-reingest** (option (b) of the three options the packet recorded). This ruling decides **semantics only**: zero production writes in this record. With semantics decided, the status-clearing lane moves from NO-GO (the operator disposition's blocker) to **DESIGNED and operator-gated for execution** — the seam/run two-word pattern: this ruling is the design; the flip executes only on the operator's explicit word.
**Authority:** operator trace `1a102e2dfe703779` ("F-PROD-1b call") — in-session owner delegation, the same form as §10 rulings 1–8. The packet's question being discharged (REPORT, F-PROD-1b consequence (c)): "any future status-clearing lane must FIRST decide the identity semantics (re-point bridge records to serving docs vs mark them superseded vs rebuild bridges on the serving lineage)".
**Record class:** this is a **production-data governance decision**, NOT a §10 spec ruling — no spec paragraph is amended, no bench instrument is touched, no run is re-judged (the §10 ruling namespace is untouched; Ruling 8's conjunction rule and closed rank-quality campaign are unaffected and unrelated).

## The ruling

1. **The 49 drifted bridge records are superseded-by-reingest.** Scope: ALL 49 records whose anchored document ids differ from their paper's serving canonical ids — the 25 `REVIEW_REQUIRED` **and** the 24 drifted `OK` records (the defect is one identity defect, not two). The 10 undrifted `OK` records (still attached to their serving docs) are untouched.
2. **Their `review_findings` payloads are preserved byte-for-byte** on the rows as historical data — superseded means the records stop GATING, not that they stop EXISTING. The findings' afterlife is the records repo: the packet (pin `762896b`), the operator disposition (`1835fd5`), and worksheet v2 are the canonical review surface.
3. **The REVIEW_REQUIRED gate's blocking effect on the 25 papers ends only through the governed execution lane** below — operator-gated, with preflight, guards, and post-flight census. Nothing flips as a side effect of this ruling.
4. **Fresh bridges compute only on future re-ingests**, against the then-current lineage, under whatever bridge policy governs that wave. Superseding forecloses nothing: it is the clean slate that makes a future bridge honest.

## The basis (three legs, all from already-recorded evidence)

1. **Truthfulness — this kills re-point (option (a)).** The findings and the qp/ms marks were DERIVED FROM the campaign-era GLM-OCR import's drafts. Re-pointing the records to the serving document ids would attach old derivations to documents they were never computed from — fabricated provenance on the lineage that actually serves. A bridge's entire value is its derivation honesty; re-pointing would preserve the gate and destroy the truth it was supposed to carry.
2. **No live surface loses a guard — this answers the safety objection to superseding.** The bridge-linked documents are REJECTED with 0 chunks: nothing serves from them. The serving lineage's protection is its own, independent trail — all 25 papers' serving documents VALIDATED, every chunk at rev2, 0 anomalies (production-verified 2026-10-03, Session 169). Today the REVIEW_REQUIRED gate blocks validate-all on the 25 SERVING papers while guarding an import that serves nothing — "the gate is attached to the wrong lineage" (the packet's own words). Superseding re-homes the protection where it already lives (the serving lineage's own gates and validation trail) and ends the false block.
3. **Non-duplication — this kills rebuild (option (c)).** The serving lineage already carries governed validation evidence (rev2-completeness, 0 anomalies, the validation-wave and bank-defect lanes' receipts). Rebuilding campaign-form bridges on it would re-derive findings that lineage's path never needed and mint a FRESH REVIEW_REQUIRED batch requiring a second teacher pass — duplicating the 62 print-dependent rows already owed and confusing two review debts into one surface. If a future re-ingest touches these papers, a new bridge computes then, honestly, against the then-current import.

## Consequences

1. **The 62 print-dependent review rows REMAIN OWED — unchanged.** The review debt lives in the records repo (packet + worksheet v2 + TODO) and never depended on the DB gate; superseding the gate neither discharges nor enlarges it. P1 (7 mismatch) → P2 (23 identity) → P3 (32 banked parse-side) against the prints, per the REPORT protocol.
2. **The F-PROD-1b open design item is CLOSED as ruled;** the open item that replaces it is the execution lane's operator word (below).
3. **No §10/§8/§8.1 surface changes.** Additive records only: this file, TODO, WORKLOG.
4. **The workbench read-model refresh** (campaign-era `data/review` dataset) remains the separate follow-up lane it was; this ruling does not touch it.

## The execution lane (DRAFT DESIGN — PROPOSED, NOT EXECUTED)

Preconditions and shape, following the lane's established patterns (Session 169's copy-on-write preflight; the wave-kit/bank-defect-tx governed-SQL pattern; core Flyway for schema-touching changes):

- **Preflight (read-only):** recreate the copy-on-write review branch (Session 169 recipe), re-run the drift census, and confirm the predicate below still selects **exactly 49** rows (25 REVIEW_REQUIRED + 24 OK) — any other count aborts the lane and re-opens the question. Also confirm whether `reconciliation_status` is free varchar or enum/CHECK-constrained.
- **The drift predicate (as recorded by Session 169's probes):**
  ```sql
  select b.id, b.reconciliation_status
  from glm_ocr_bridge_records b
  join exam_papers p on p.id = b.paper_id
  where b.qp_document_id is distinct from p.question_paper_document_id
     or b.ms_document_id is distinct from p.mark_scheme_document_id;
  ```
- **The flip:** if the column is free — a single governed `UPDATE glm_ocr_bridge_records SET reconciliation_status = 'SUPERSEDED' WHERE id = ANY(<the 49 ids, pinned by the preflight>)` with `review_findings`, `qp/ms_document_id` untouched; if the column is constrained — a core Flyway migration first (extend the status domain or add the superseded value), then the same governed update, deployed by the operator-gated deploy path.
- **Post-flight:** re-census by status (expect 0 REVIEW_REQUIRED remaining among the 25, 10 untouched OK, 49 SUPERSEDED), record receipts in the records repo, and only then is validate-all unblocked on the 25 serving papers.
- **Guards:** row-count pin (49), id pin (the preflight's explicit list, not a re-derivation at write time), backup note in the receipts, session-only credentials, zero other columns touched.

## Delegation-honesty

The operator's trace `1a102e2dfe703779` ("F-PROD-1b call") is the in-session owner delegation. Honesty notes: (a) unlike §10 Ruling 7, the decision direction was **not** pre-recorded in an earlier pack — this record is the first articulation; its basis is drawn entirely from already-pushed records (the packet `762896b`, the disposition `1835fd5`, Session 169's production verification), all visible to the operator before the directive; (b) no new production data was gathered between the directive and this record; (c) the operator can overturn the option choice by word at any time before the execution lane runs — the production surface is untouched until then.
