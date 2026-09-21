# R5 cut-over — rev1 retired from the production retrieval corpus (2026-09-21)

Operator instruction: "proceed with soak rev2 briefly, then decide the R5 cut-over (retire/supersede rev1)".

## Decision

**RETIRE (delete) all `embed_rev=1` chunk rows from production. SUPERSEDE (retain) the 172 legacy document rows.**

Grounds, each verified live on 2026-09-21 before acting:

1. **Plan §6/§7/P4 semantics.** "rev1 rows are untouched until the eval gate passes, then
   deleted/superseded — including the 172 legacy docs — so RRF never sees both"; P4
   acceptance = "no rev1 rows". The eval-gate precondition was already met (Task 32:
   offline gates + canonical prod-vector eval 6/9 rev2 vs 1/9 rev1, probes 10/10; R4:
   FETCH 40/40, ENUMERATE 1.0/1.0; Task 33: finish run + live E2E 4/4).
2. **Serving-neutrality, proven both ways.** The live core (f47cbc3) binds
   `c.embed_rev = ChunkVectorRepository.CURRENT_EMBED_REV` (= 2) in BOTH retrieval
   paths (ChunkVectorRepository lines 96/114; ChunkLexicalRepository lines 86/99/139/153).
   An exhaustive grep of `document_chunks` readers in main source shows every remaining
   reader is either embed_rev-filtered (vector + lexical), bank-based (FetchService reads
   questions/question_parts/mark_points; EnumerateService reads exam_papers/questions/
   knowledge_nodes), KG-lane (knowledge_nodes), or bench-only (RetrievalFabric, CI).
   Empirically: the pre-cut-over soak resolved 40/40 served hits to rev2 — zero rev1
   leakage on the live app.
3. **Why chunks yes / docs no.** Deleting the 2,333 rev1 CHUNK rows changes nothing
   served and satisfies the plan's "no rev1 rows" acceptance. The 172 legacy DOC rows,
   however, are the target of 172 currently-resolvable string pointers:
   `exam_papers.question_paper_document_id` (91 resolve) and
   `mark_scheme_document_id` (81 resolve; 3 QP / 13 MS were ALREADY dangling before
   this cut-over — pre-existing, unchanged). Zero exam_papers rows point at rev2 bridge
   docs. Deleting the doc rows would dangle all 172 references to save ~1.3 MB — a bad
   trade; the docs are instead SUPERSEDED by this evidence record (project pattern:
   supersede banners in evidence, not DB state mutations). The 22 rev2 bridge doc rows
   already carry the re-parsed papers; G8 backfill re-parses the remaining ones.

## Soak (brief, decision-grade) — pre-cut-over, 2026-09-21

- health UP; 8 search probes served all FIVE rev2 substrate kinds
  (EXTERNAL_NOTES, EXTERNAL_QUESTIONS, SYLLABUS, QUESTION_PAPER, MARK_SCHEME all observed)
- rev-leakage assertion: 40 unique hits -> 40 rev2, 0 leaks, 0 unresolved
- Fetch (gold semantics): FET-002 "question 6 summer 2011 mark scheme" -> 2 papers,
  2 questions, 7 mark points; FET-003 (explicit code 4CH1/2CR 2022 q2) -> 2 papers,
  9 points; no parse defects
- Enumerate: ENU-002 "list all questions about metallic bonding" -> resolved;
  structured spec axis 4CH1-1.32 -> resolved
- determinism double-pass: byte-identical normalized JSON, PASS
- latency 4.1-8.3 s (first probe pays Render cold start; warm ~4.2-4.9 s)

Raw: soak_probes.json (this directory).

## Safety rails executed BEFORE deletion

- **Full row archive**: rev1_chunks.jsonl.gz — 2,333 rows, complete row state
  (content, metadata, embedding as float32-LE base64; content_tsv excluded as
  regenerable). SHA-256 pinned in SHA256SUMS. Operator copy:
  `download/rev1-retire-archive/`.
- **Vector identity re-verified at cut-over time**: all 2,333 production rev1 vectors
  are float4-IDENTICAL (bit-exact after float32 quantization on both sides) to the
  repo-frozen preload-r3 artifact (`bench/inputs/embeddings/preload-r3/
  embeddings_chunks.jsonl`). Restore therefore needs ZERO embedding API calls.

## Deletion

- Single transaction `DELETE FROM document_chunks WHERE embed_rev = 1` — 2,333 rows
  in 0.74 s, then `ANALYZE document_chunks`.
- Post-state: rev1 = 0 ("no rev1 rows" acceptance MET); rev2 = 1,570 embedded /
  0 pending / 0 bad dims with the exact expected kind mix (EXTERNAL_NOTES 350,
  EXTERNAL_QUESTIONS 758, MARK_SCHEME 160, QUESTION_PAPER 140, SYLLABUS 162);
  documents 549 -> 549 unchanged.

## Post-cut-over re-probe — serving unchanged

- 8/8 probes, identical kind mixes; 40/40 hits rev2-only; Fetch/Enumerate identical
  resolutions; determinism PASS; latency 3.8-5.0 s. The cut-over is serving-neutral,
  empirically confirmed. Raw: post_cutover_probes.json.

## Rollback runbook

1. **Deterministic re-seed (preferred)**: seed text+rows from snapshot-r3
   (bench/inputs/snapshot-r3), apply vectors from preload-r3 — float4-identical,
   zero API calls, reproducible in CI.
2. **Byte-exact restore**: gunzip rev1_chunks.jsonl.gz and COPY rows back
   (embedding_f32_b64 -> '[...]':vector); rebuild content_tsv (V28 semantics).

## Accepted interim gap (per plan, queued)

Paper-axis CHUNK content exists in the vector corpus only for the 11 re-parsed papers
(22 bridge doc rows); the remaining ~80 papers' QP/MS chunk substrate was rev1-only and
is now retired. This is exactly the plan's G8 backfill queue ("backfill remaining papers
as atoms land", ~83 unparsed papers). Interim paper-axis coverage is served
deterministically from the bank (FETCH 40/40, ENUMERATE 1.0/1.0) — that is the R4 design
working as intended.

## Artifacts in this directory

- soak_probes.json — pre-cut-over soak (live app + DB assertions)
- post_cutover_probes.json — post-cut-over re-probe
- retire_manifest.json — archive + vector-identity verification record
- delete_result.json — guarded deletion + post-state counts
- SHA256SUMS — SHA-256 over all of the above
