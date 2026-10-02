# T-C60 EXECUTION REPORT — papers-axis completion, governed batch (2026-10-02)

**Batch:** `tc60-papers-axis-completion-20261002` · **Status: APPLIED** (single
transaction, dry-run-verified) · **Instrument:** T-C54 wave-2 (operator-supplied
Neon credential, `neondb_owner`, batch_run_id + append-only audit rows, fail-closed
pre/post gate replicas) · **Operator:** Nawaf Al Hussain Khondokar — scope named in
IM trace `1a0fc2a56bfb1a31` (items 2/3/4 verbatim), instrument go "Proceed" IM
trace `1a0fc9695d27fdb5`. The agent asserts no validation of its own.

## 0. Live re-scope (execution-time probes, `tc60_probe_live.json`)

The prep pack (`f146d8f48273`) composed its worklists before any live probe could
run. Execution-time re-derivation (SELECT-only, `t0_readonly`) re-scoped all three
items — every verdict below is mechanically pinned to probe rows:

1. **Gap-4 adjudication — CLOSED AS BY-DESIGN (zero promotions).** All 5
   chunk-bearing REJECTED docs carry explicit 2026-09-28 §D1 retire verdicts
   ("retired candidate superseded by better-proven content in the OCR lane",
   operator "Proceed with next" delegation, trace `1a0ea3c208e16699`), and each
   doc's supersedor is verified live: `4CH1-1C-201906` QP parses (13+10) →
   VALIDATED QP linked at ep `0924a1fe` (June 2019); `4CH1-1C-202006` MS (19) →
   VALIDATED MS at ep `060f40c2` (June 2020); `4CH1-2C-202006` QP+MS (11+11) →
   the 2020-06↔2020-11 label drift, resolved by the ver2 re-ingest linked at ep
   `e6c96a2e` (November 2020). The 64 embedded chunks are dark **intentionally**;
   no duplicate content was promoted. The prep acceptance line "gate 4,608 →
   4,672" is retired — it was based on the pack's mis-attribution of the 64
   chunks to the 8 SUGGESTED docs.
2. **Gap-3 heals — all 11 BLOCKED on ingest.** None of the pinned heal-target
   checksums exists as a document. The 8 SUGGESTED docs are `.md` parses of
   `corpus/igcse-chemistry-4ch0-1c-<session>/` paths that no longer exist at
   corpus `029c6ec92` — identity-consistent by `source_uri` only, NOT
   current-corpus-matched by checksum, below the acceptance bar. 2 of the 8
   (specimen2017 pair) are already linked at ep `fd1bf331`. Per-row verdicts in
   §3; heals execute in the ingest wave.
3. **Gap-2 ep-row backfill — 1 of 6 executable now.** Prep drift: P5's "expect
   absent" assumption was wrong for `4CH1-1CR-202506` (QP+MS ingested 2026-09-21/22,
   VALIDATED, checksums == ingest pins `e366b168`/`54a0a9f6`, unlinked). Converted
   into the executed ep-row INSERT. The other 4 papers' docs are un-ingested;
   docless rows would replicate gap-3, so they defer to the ingest wave.

## 1. Acts applied (exactly; audit rows carry the full authority chain)

| # | Act | Detail |
|---|-----|--------|
| 1 | 8 documents SUGGESTED → VALIDATED | the operator-named 8-doc set (`4ch0-1c-2018jan`, `2020janr`, `2021janr`, `specimen2017` × QP+MS); 0 chunks each; per-doc fidelity asserted (id, document_id, kind, checksum, doc_version, chunk count) |
| 2 | 1 exam_papers INSERT | `4CH1/1CR June 2025` (id `80263901-10ce-4bf2-9346-0c1613c9f5b5`), VALIDATED, QP `d218677f…` + MS `bb59e1af…` (both VALIDATED, ver 1, checksums == pins) |
| 3 | 9 content_review_audit rows | 8 × VALIDATE/document + 1 × VALIDATE/exam_paper, actor_label + detail JSON (batch, batch_run_id, operator, traces, decision_text) |

**Gate replica: 4,608 → 4,608 (delta 0 — asserted both in-transaction and
independently).** Zero document_chunks writes; zero ep UPDATEs (no heals);
REJECTED census unchanged (67 MS / 78 QP); teacher_validation_events unchanged (0
throughout); no DDL.

## 2. Fail-closed chain (all PASS, `tc60_apply_report.json`)

Identity gate (db `neondb` + role `neondb_owner` + campaign identity row
`T-C04-CAMPAIGN`) · exactly-one-ACTIVE cv `356840e6…` (`4CH1-2017`) · census pre ==
decisions (zero drift since probe) · ep census 90V/13R pre · chunks snapshot
immutable · audit-constraint pre-check (`document` + `VALIDATE` allowed, no DDL) ·
8/8 flip fidelity · ep-link docs VALIDATED + checksum-pinned + unlinked ·
WHERE-NOT-EXISTS insert guard · post-census shifted exactly by the 8 flips ·
ep 91V/13R post · audit delta 9 · unlinked chem VALIDATED ep rows 11 → 11 ·
gate delta 0 · **DRY_RUN_OK** (run 1, then rollback) → **APPLIED** →
**ALREADY_APPLIED** idempotence proven (re-run no-ops cleanly) → independent
read-only post-verification (`tc60_post_verify.json`): SUGGESTED surface = 0.

## 3. Remaining lane scope (IN_PROGRESS) — the ingest wave

| Item | Rows | Blocker (exact) |
|------|------|-----------------|
| 4 ep rows (2025-06 1C; 2026-06 1C/2C/2CR) | 4 | parser ingest of the corpus dirs (docs must exist first) |
| 11 ep-link heals | 11 | same ingest (pinned PDFs); the 3 JAN identities additionally need the old `.md` inputs re-OCR'd or re-pinned from the current corpus |
| 8-doc completion (chunk → embed) | 8 | ChunkingService + GeminiEmbeddingProvider run |
| 5-paper corpus ingest (prep-pack target set) | 5 dirs | no GLM-OCR markdown in the dirs (PDFs + manifests only, verified live); no Maven/JDK-25 toolchain in sandbox; no JWT secret (CAMPAIGN_JWT/SYLLABAI_JWT_SECRET); no Gemini embedding key |

Environment prerequisites for the ingest wave (operator decision needed): OCR
markdown production for the 5 target dirs (manual ocr.z.ai workflow or
`tools/ocr_batch/`), JDK 25 + Maven + parser/core JAR builds, JWT secret,
Gemini embedding key. None of these exist in the current sandbox; the DB-side
governance work that could proceed without them is now complete and audited.

## 4. Machine evidence (this directory)

`tc60_probe_live.json` (execution-time probe pack, SELECT-only) ·
`tc60_decisions.json` (pinned worklist + verdicts + scope guards) ·
`tc60_apply_report.json` (APPLIED run report, batch_run_id inside) ·
`tc60_idempotence_report.json` (ALREADY_APPLIED proof) · `tc60_post_verify.json`
(independent post-verification). Secrets: none committed — credentials live in
0600 files under `.secrets/` and are never printed.
