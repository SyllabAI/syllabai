# G8 Backfill — Coverage Report v1

Lane: G8 paper-axis chunk backfill · Date: 2026-09-21 · Status: **COMPLETE**
Scope: plan §11 "backfill remaining papers as atoms land" — QP/MS atomization of the
unparsed past-paper corpus, rev2 chunk ingest + embedding, and the paper-coverage
matrix. Bank tables were deliberately NOT modified (see §5).

---

## 1. Headline

| Metric | Value |
|---|---|
| Repo paper universe (Edexcel IGCSE chemistry, `syllabai-pastpapers`) | **86 dirs** |
| — session papers with qp.pdf + ms.pdf | 81 |
| — specimen papers with qp.pdf + ms.pdf | 2 |
| — MS-only dirs (2020-11 COVID session; no qp.pdf in repo) | 3 |
| Papers with rev2 QP+MS chunk docs in production | **83 / 83 = 100%** of the qp+ms-bearing universe |
| Gaps | 3 MS-only papers (QP structurally required by the parser contract) |
| Paper-axis rev2 chunks (QUESTION_PAPER + MARK_SCHEME) | **2,422** (QP 1,153 + MS 1,269) |
| Total rev2 corpus after G8 | **3,692 chunks / 0 pending** / single model gemini-embedding-001 / 0 bad dims |
| Serving verification post-G8 | probes PASS (§6) |

The "~83 unparsed papers" planning figure is now exactly explained: 86 repo dirs
− 11 already-parsed bridge papers (Task 32) − 3 MS-only (unparseable) − 2 specimen
(counted separately in planning) = 70 session papers + 2 specimen actually backfilled
by G8; 83 = 81 session + 2 specimen covered papers.

## 2. Coverage matrix (papers → chunk substrate)

| Source lane | Papers | Docs | Chunks | Notes |
|---|---|---|---|---|
| Bridge v1.2.0 (Task 32, Sep-20) | 11 (4CH0 2011-2014, 4CH1 2019-2025) | 22 | 300 | gates green, marks-verified |
| G8 pdflane batch (Sep-21) | 70 session + 2 specimen | 144 | 2,122 | review-flagged products (§5) |
| **Total paper-axis** | **83** | **166** | **2,422** | all rev2, embedded |
| MS-only 2020-11 (1CR/2C/2CR) | 3 | 0 | 0 | repo lacks qp.pdf; `pdflane.run_paper` requires it for atom identity — recorded gap, not a defect |

Per-paper identity: canonical `retrieval` (paperCode+series+year) joins the repo
slug space 1:1 — every repo paper with both PDFs has exactly one rev2 QP doc and one
rev2 MS doc (checksum-deduplicated, deterministic documentIds).

## 3. Defects found and fixed during execution

1. **kind=OTHER ingest defect (metadata-only, fixed in place).** The prior session's
   `g8_ingest.py` posted canonical docs without `?kind=`; `ContentDocumentController`
   defaults the query param to `OTHER`, so 132 docs / 1,916 chunks landed mis-stamped.
   Chunk text and headers are kind-independent for these docs (the only kind-dependent
   header segment, the `MS ` prefix, is suppressed when `retrieval.label` is present —
   verified in `ChunkHeaderBuilder` + live chunk content), so a guarded single-transaction
   UPDATE corrected `documents.kind` (66 QP + 66 MS) and `document_chunks.kind` (1,916)
   with no re-embedding. Pre-state archived: `download/g8_kind_fix_archive.json`; every
   doc matched by `checksum == canonical.source.checksum`. The ingest script now passes
   `?kind=` explicitly.
2. **Parser crash on 4CH0-1C-201601 (fixed upstream, `syllabai-parser` f59a612).**
   Old-spec layouts print `(Total for Question N = X marks)` inside the page-footer
   band (y0 792-801 ≥ FOOTER_Y_MIN 780); both walks skipped it as page furniture, the
   atom never sealed and `emit_atoms` raised `EmitError`. Fix: a total row is QUESTION
   furniture, never PAGE furniture — exempt `TOTAL_FOR_Q_RE` matches from the footer
   skip in `parse_qp.parse_blocks` and `emit_atoms.build_qp_atoms` (identical change,
   `crosscheck_qp` stays consistent). Regression-pinned by `tests_footer_total_rows.py`
   (4 cases); full parser suite 78 passed / 1 skipped; 4-paper determinism spot-check
   byte-identical products pre/post patch. Paper re-parsed (Q=15, 120 marks) and included.
3. **Daily key quota exhausted twice (recurring stall, finished via CI rotation).**
   Timeline: batch embed ran on key[2] 797b77a879, stalled 13:27 UTC (~1,378 chunks in);
   the prior session's key-swap + resume push (13:55-14:09, ~950 chunks) re-exhausted the
   same key before the session died; probes 14:37-14:56 confirmed provider-wide 500s.
   Resolution: `ops-g8-finish` workflow (Task-33 pattern) read the 4-key secret, rotated
   the Render serving key to key[3] 3687872106, redeployed (dep-daokflv40ujc73flr0ig,
   197s) and drove `POST /{id}/embed` for the frozen 59-doc / 744-chunk queue —
   **COMPLETE in one round, 0 failures** (run 35616602846, report SHA-pinned in evidence).
   Raw key values never left the GH secret (fingerprints only).

## 4. Corpus end-state (production)

| kind | docs | chunks | pending |
|---|---|---|---|
| QUESTION_PAPER | 176 (91 legacy + 11 bridge + 74 G8) | 1,153 | 0 |
| MARK_SCHEME | 166 (81 legacy + 11 bridge + 74 G8) | 1,269 | 0 |
| EXTERNAL_NOTES | 112 | 350 | 0 |
| EXTERNAL_QUESTIONS | 81 | 758 | 0 |
| SYLLABUS | 162 | 162 | 0 |
| **Total** | **697 documents** (172 legacy rows retained as superseded pointer/provenance substrate) | **3,692** | **0** |

rev1 rows: 0 (R5 cut-over). Model: gemini-embedding-001 only, 768d, 0 bad vectors.
Embed timeline (Sep-21 UTC): 09h 584 (Task 33) · 13:07-13:27 + 13:55-14:09 ≈ 2,320 (G8
direct, two keys) · 15:0x 744 (g8-finish CI, key[3]).

## 5. Parse-quality disclosure (drives the bank decision)

Aggregated over the 72 G8 pdflane products (escalations + review queues):

| Signal | Count | Meaning |
|---|---|---|
| G1 gate fail | 72/72 papers | marks arithmetic not verified — `marksVerified=false` for every G8 paper |
| G3 gate fail | 22 papers | printed QP↔MS total discrepancies (48 rows) |
| G5 gate fail | 4 papers | content-accounting (16 unaccounted MS rows) |
| MS-UNCLASSIFIED-ROW | 2,610 | old-spec mark-scheme row layouts the classifier does not know |
| FRONT-MATTER-ASSET-PRUNED | 2,340 | instruction-page assets pruned (expected) |
| QP-IMAGE-FURNITURE-DROPPED | 2,008 | footer/banner images excluded from atoms |

**Decision — bank tables untouched.** The plan's bank-backfill-from-atoms requires
bank-grade marks arithmetic; G8 products fail the G1 verification gate (unlike the 11
Task-32 bridge papers, which are marks-verified). Backfilling the bank with unverified
totals would degrade deterministic Fetch/Enumerate quality, so: the deterministic bank
path continues to serve from the existing bank rows (1,447 questions, FETCH 40/40,
ENUMERATE 1.0/1.0 unchanged — re-probed §6); the G8 corpus serves as the paper-axis
**search substrate** (vector + lexical lanes). Upgrading the old-spec MS classifier so
these papers pass G1 remains parser-lane work, after which a bank backfill can be
reconsidered per-paper.

## 6. Serving verification (post-G8 probes, live app)

- 8/8 search probes serve; kind lanes now include QUESTION_PAPER and MARK_SCHEME hits
  from the G8 corpus (e.g. M1 mark-scheme probe → MS+QP).
- Rev-leakage: 40/40 unique hits resolve to embed_rev=2 (0 leaks, 0 unresolved).
- Deterministic Fetch: FET-002 (summer 2011 q6 MS) 2 papers / 7 points; FET-003
  (4CH1/2CR 2022 q2) 2 papers / 9 points — unchanged from R5 soak.
- Enumerate: ENU-002 + structured spec axis resolved — unchanged.
- Determinism double-pass: PASS. Latency 3.9-5.7s.
- Raw probe JSON: `g8_post_probes.json` (this evidence dir) + `download/` copy.

## 7. Bank hygiene (pre-existing, unchanged, for the record)

- 10 exam_papers rows with `paper_code=NULL` (known R4 §8.2 item) — not joinable to
  repo slugs by code; their sessions duplicate covered papers.
- 3 AUDIT E2E dummy papers (`AUDIT-*`) — test artifacts, no materials.
- 2 specimen bank rows ("Specimen 2017") — covered by the 2 specimen docs.
- `exam_papers.*_document_id` pointers still resolve to the 172 legacy doc rows
  (superseded substrate, per R5 decision); 3 QP / 13 MS pointers pre-existing dangling.

## 8. Quota ledger (Gemini keys, since 2026-09-21 00:00 Pacific)

| key | fingerprint | consumed today | state |
|---|---|---|---|
| [0] | 01ac5264a3 | 0 | untouched |
| [1] | 91fdfb06ac | 584 (Task 33) + queries | RPD-exhausted |
| [2] | 797b77a879 | ≈2,320 (G8 direct) | RPD-exhausted |
| [3] | 3687872106 | 744 (g8-finish CI) | now the Render serving key |

Standing security action unchanged: rotate all 4 Gemini keys + both PATs.

## 9. Next steps (per plan §11)

1. Textbook tier (next corpus tier, unstarted).
2. Authoritative retrieval doc + supersede banners on superseded docs.
3. Parser lane: old-spec MS classifier upgrade (G1) → re-verify → optional bank backfill.
4. MS-only 2020-11 papers: obtain qp.pdf or extend the parser contract for MS-only mode.
5. STANDING: key/PAT rotation.
