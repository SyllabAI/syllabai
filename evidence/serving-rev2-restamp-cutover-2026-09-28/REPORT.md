# Standing-menu item (2) EXECUTED — the eval-gated embed_rev re-stamp + CURRENT_EMBED_REV cut-over — 2026-09-28

**Commission + provenance.** The operator's "Proceed with (2) (eval-gated rev1→2
re-stamp/cut-over) now has its gate input" (IM trace `1a0e8efc1773852d`) discharged
the operator gate on item (2) of the corrected standing menu
(`evidence/serving-rev2-flipback-refutation-2026-09-28/REPORT.md`). The eval gate
input existed: the r7 serving-set generation (traces `1a0e88bb060ed3b5` /
`1a0e8a8180a3f8cd`; `evidence/bench-001/runs/R7-GENERATION-NOTES.md`) had measured
today's serving corpus — snap-006 frozen, arms A/B/C recorded, §8(d) 0.5618
full / 0.9167 micro through the promoted notes substrate — and handed item (2) its
eval input verbatim: "a re-stamp changes which rows serve under rev2 semantics but
not this quality picture (same model, same content)".

**What executed (the pair, in order).**

1. **Core leg** — commit `665d7aa8` (syllabai-core main, fast-forward on `838203e`):
   `ChunkVectorRepository.CURRENT_EMBED_REV` 1→2 with an honest javadoc recording the
   paired mechanism, the refuted d523f57 revert condition, and the rollback pair.
   Render auto-deploy `dep-data1im7bikc73b1jcq0` built and went **live 17:20:03Z**.
2. **DB leg** — a single fail-closed transaction fired at deploy-live
   (`scripts/restamp_kit/restamp_cutover_20260928.py`, kit committed with the
   evidence): the guarded re-stamp of **exactly the 965 gate-eligible rev1 chunks**
   (the `searchServingEligible` replica at rev=1 — EQ 309 + QP 145 + MS 161 + EN 350)
   `embed_rev 1→2`; rowcount asserted == 965; **COMMITTED 17:20:12Z**.

**Serving identity — the guarantee this cut-over was built around.** Pre-flight
(read-only, `preflight_exact_gate.json`) verified: exact-gate replica rev1 = 965
(965 embedded, single model gemini-embedding-001), rev2 = 0 (the flip is additive
on the serving surface — nothing new becomes servable, the VALIDATED-only gate is
untouched), documents census EQ 299V/80S + EN 112V + QP 13V/164S + MS 13V/156S +
SYLLABUS 162S, `teacher_validation_events` = 0, and the audit tail showed no
concurrent production writes after the notes promotion (15:22Z). The served-set
chunk-id list (965 ids) was snapshotted before the flip and re-asserted INSIDE the
cut-over transaction pre- and post-UPDATE: **identical — the served set is
provably the same 965 rows across the boundary** (same vectors, same model, both
revs gemini-embedding-001 @ 768-d; only the stamp moved).

**The 0-hit window, measured.** Between the new app going live (reads rev=2) and
the re-stamp committing, the served set is empty — searches fail closed (empty
result, no crash). **Measured window: 8.9 seconds** (17:20:03.5 → 17:20:12.4Z),
pilot-scale traffic, deterministic refusal semantics throughout. Rollback is the
same pair in reverse (re-stamp 965 2→1 + flip the constant back) and is recorded
in the kit + javadoc.

## The live-serving incident found by post-verification, and its fix

Post-cut-over the live probe (5 chemistry queries through the production search
endpoint) returned 46/50 hits — query 5 lost its ranks 7–10 while its top-1 score
stayed **bit-identical** to the pre-cut-over baseline, and the DB-side served set
was proven identical. Diagnosis (all read-only):

- The serving SQL is served by the **HNSW index** `ix_document_chunks_embedding`
  (V11) with `hnsw.iterative_scan = off` and `ef_search = 40`. The filter
  (`embed_rev` + VALIDATED/scope branches) is applied **after** the ANN traversal;
  candidates it rejects are not replaced.
- The corpus contains 3,378 SUGGESTED rev2-stamped chunks (the bridge corpus). A
  query whose nearest-40 neighborhood is SUGGESTED-dense exhausts the candidate
  budget on rejected rows and returns FEWER than 10 rows — reproduced at the
  extreme with a SUGGESTED-dense probe vector: **0 rows** through a prepared
  statement (the JDBC generic plan) vs 10 exact. This defect is **pre-existing**
  (it exists whenever SUGGESTED rows dominate the scanned neighborhood — the same
  structure was true pre-cut-over with the rev filter reversed), but the 965-row
  re-stamp changed the graph topology (new tuple versions = new index nodes) and
  made a previously-lucky query unlucky (10 → 6 → 5 across graph states).

**Remedy (the pgvector-documented one).** `REINDEX INDEX ix_document_chunks_embedding`
(3.43 s, 4,343 rows / 17 MB) to rebuild a clean graph, then
`ALTER DATABASE neondb SET hnsw.iterative_scan = 'strict_order'` so filtered index
scans keep traversing until the true top-k PASS the filter (correctness guaranteed
by pgvector strict_order semantics), plus one idle pooled JDBC backend terminated
so the app's pool re-connected with the new default. Result — **final live probe
50/50 hits, every top-1 score bit-identical to the pre-cut-over baseline**
(`probe_final.json`), and the worst-case DB probe now delivers 10/10 where it
delivered 0. The GUC is additive and reversible (`ALTER DATABASE neondb RESET
hnsw.iterative_scan`); the reindex is transparent to correctness.

## Ledger discipline

Zero rows in `content_review_audit` and `teacher_validation_events` from this
operation (the re-stamp is a serving-infrastructure mutation, not a content
review — the audit ledger's CHECK domain does not cover chunk stamps and no
content decision was made). The ledger for THIS action is this evidence pack +
the core commit `665d7aa8` + the worklog. Post-state censuses: documents census
unchanged (asserted in-tx), `teacher_validation_events` 0 (asserted in-tx).

## Follow-ups handed forward

- **Future validation waves on existing rev1-stamped SUGGESTED docs** (the 80
  sme-bank cards, 129 QP + 160 MS SUGGESTED rev1 chunks) must carry a paired
  rev re-stamp step — under the flipped constant a VALIDATED rev1 row would not
  serve until re-stamped (the wave kit should do it in the same transaction).
- CI note: core-ci on main is red at `f9d9069` on `FlashcardRatingFlowIT`
  (expected "fl_testCard2") — the flashcard-ratings lane's in-flight tranche 4.4,
  not the cut-over (all 120 corpus/serving tests passed on that run; the lane's
  own fix commit for it had already landed mid-verification).
- rev1 retirement (deletion) stays gated at R5, per the constant's javadoc.

## Artifacts

| file | what |
|---|---|
| `preflight_exact_gate.json` | read-only pre-flight: supply matrix, exact-gate 965/0, censuses, audit tail |
| `served_set_pre.json` | the 965 served chunk ids captured pre-flip (re-asserted in-tx pre/post) |
| `probe_pre.json` / `probe_post.json` / `probe_post_reindex.json` / `probe_final.json` | live 5-query serving probes: baseline 50/50 → incident 46/50 → 45/50 → final 50/50 with bit-identical top scores |
| `SHA256SUMS` | checksums for this pack |
