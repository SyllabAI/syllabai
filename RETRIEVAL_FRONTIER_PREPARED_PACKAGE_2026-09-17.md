# Retrieval Frontier Prepared Package — T-C07 / Embeddings / T-C14 / T-C06

**Status:** PREPARED (2026-09-17, execution lane following the operator's "proceed 1–5" directive). Everything here is a build-ready contract or draft — **nothing in this package changes serving behavior, and no Java artifact in it has been compiled or tested** (the authoring environment lacks Java 25 / Maven / Docker; per AGENT.md state honesty these artifacts are UNVERIFIED until a Maven-equipped lane runs them). **Addendum 2026-09-17 late:** the toolchain blocker is lifted — Temurin JDK 25.0.4 LTS + Maven 3.9.11 bootstrapped user-space (no root) in the agent workspace; `syllabai-core` @ `7eb621a` compiles main+test green (`mvn test-compile` EXIT=0) and executes unit tests (ReciprocalRankFusionTest 4/4). Docker/Testcontainers remain absent in the sandbox, so Docker-ITs still need a Docker-equipped lane (the CI workflow_dispatch route per the CI-recovery runbook is the intended path). Artifacts in this package remain unimplemented contracts until written and merged through their owning lanes. The verified deliverables of the same directive live in `bench/` (gold set v1, gold_check) and `evidence/bench-001/` (snapshot snap-001 + run-001-bproxy) — see `RETRIEVAL_BENCHMARK_HARNESS_SPEC.md` (T-C13).
**DB-verified inputs (2026-09-17, read-only):** 2,333 chunks / 0 embedded; 94 papers (15 VALIDATED); 172 documents (91 QP + 81 MS); `documents.kind` ∈ {QUESTION_PAPER, MARK_SCHEME}; `questions.provenance` ∈ {PAST_PAPER, SEED_DEMO}; `questions.command_word` NULL 119/119; 85/119 VALIDATED question anchors point at ING-* nodes (audit finding AF-1); Flyway V26.

## 1. T-C07 — curriculum-scoped retrieval (pre-embedding prerequisite)

**Facts established from production schema:** `exam_papers(subject_id, paper_code, validation_state, question_paper_document_id, mark_scheme_document_id)`; `documents(id, document_id, kind, checksum)`; `document_chunks(document_row_id → documents.id, chunk_index, content, embedding)`. There is **no curriculum column on chunks or documents** — scope must be derived by join: `document_chunks → documents → exam_papers (via the two document FKs) → subject/curriculum`.

**Contract (to implement in `syllabai-core`):**
1. Resolve the learner's active `CurriculumVersion` → its subject and code (the join path `curriculum_versions ↔ subjects` is the one schema point this package could not verify read-only — verify first in the implementation session).
2. **Index-time AND query-time scoping** per the TODO row: every chunk-serving path (`ContentRetrievalService`, `ContentVectorRetriever`) gains a mandatory curriculum predicate built on that join; absent/unresolvable curriculum ⇒ **fail-closed empty result** (never serve unscoped).
3. KG side is namespaced already (`4CH1-*` codes), but AF-1 shows question→KG anchors leak to ING-* nodes — the same predicate must gate anchor resolution so tutor evidence never resolves through foreign-curriculum scrape nodes.
4. Tests (required before merge): unit — predicate correctness incl. null-curriculum fail-closed; IT — a 4CH0 chunk is never served to a 4CH1 learner (negative control), SUGGESTED-paper chunks behave per the T-C05 validation gate.

## 2. Embedding backfill runbook (the "fuel") — execute only after T-C07 merges

1. Preconditions: T-C07 merged with ITs green; operator-provided Gemini key present in secrets; quota window confirmed.
2. Job: idempotent batch backfill (`embedded_at IS NULL`) over all `document_chunks`, batch 100, `GeminiEmbeddingProvider` (text-embedding-004), exponential backoff, resumable; every batch logged (count, model, latency).
3. Scope discipline: embed the **serving-eligible projection only** (chunks whose paper passes the validation gate) + the rest flagged `ELIGIBLE_FOR_BACKFILL_LATER` — embeddings on unservable chunks are wasted spend under the boundary quantified by run-001.
4. Verification: `count(embedding IS NOT NULL)` vs plan; 2 spot cosine-sanity checks per kind; monitor green; record run under `evidence/` with the batch log.
5. Cost honesty: 2,333 embeddings is trivial compute but **operator-gated spend** — do not run without the key/quota confirmation (AGENT.md: no paid-only infrastructure by convenience).

## 3. T-C14 — lexical retrieval (P0) + provider contract ratification

**Migration draft V27 (additive, reversible):**
```sql
ALTER TABLE document_chunks
  ADD COLUMN content_tsv tsvector
  GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
CREATE INDEX idx_document_chunks_content_tsv ON document_chunks USING GIN (content_tsv);
```
**Retriever contract:** `Bm25Retriever implements RetrievalProvider` (per the ratified-on-merge contract sketch): `websearch_to_tsquery('english', :normalizedQuery)`, ordering `ts_rank_cd(content_tsv, query)`, curriculum predicate from T-C07 mandatory, limit from `StructuredRetrievalQuery`, empty/blank query ⇒ fail-closed empty. Fused via the existing `ReciprocalRankFusion` (k=60) as arm C — no new fusion code.
**Ratification checklist (T-C14 scope):** port + candidate records as sketched 2026-09-17 (`RetrievalProvider_contract_sketch.md`), Google types never leak past the port, `GeminiFileSearchRetriever` stub behind `available()=false` until T-C15.
**Tests:** ranking sanity (stem-verbatim query ranks its QP chunk top-5 — cross-checked against run-001 R1 population), empty query, curriculum negative control, boundary scope identical to §2 of the runbook.

## 4. T-C06 — CMC→canonical converter (unparked; contract only here)

1. **Enum migration draft V28 (additive):** `documents.kind` += `TEXTBOOK`, `EXTERNAL_NOTES`, `EXTERNAL_QUESTIONS`; `questions.provenance` += `EXTERNAL_BANK`; `SPEC_POINT` node type registered in the knowledge node-type constraint (production currently carries the 182 spec points as SUBTOPIC-typed nodes — the migration must include a recorded backfill decision: retype in place vs dual-type window; **retype-in-place is proposed**, with the retriever's type filter updated in the same change).
2. Converter shape: syllabai-parser adapter `CmcCanonicalConverter` (CMC front matter → canonical schema 1.0 DTOs) + core ingestion endpoint writing SUGGESTED-only; corpus lint runs pre-ingestion (CMC v1.0 rules: front-matter schema, heading grammar, chemistry notation, marks/MS conventions, asset/figure-missing markers).
3. F-168 mapping-provenance columns land on the question mapping table in the same migration family as V28 (four-tier provenance enum per T-C05).
4. Sequencing: converter work may start after T-C07 (shared scoping joins) and before/parallel with M2 arms; it feeds arms H2/contextual headers and the notes_mirror substrate (gold classes 9/12 currently N/A for that exact reason).

## 5. Audit findings carried by this package (durable knowledge)

- **AF-1 — ING-* anchors are load-bearing:** 85/119 VALIDATED question anchors resolve `primary_topic_node_id` to ING-* paper-scrape nodes, not 4CH1 spec points. The "cruft" cannot simply be deleted; remapping is T-C06/T-C07 work. Gold set quarantines these anchors (recorded per-record as `provenance.anchor_code_non_spec`).
- **AF-2 — validation boundary halves lexical retrieval:** run-001-bproxy, identical BM25 scorer: ALL-chunks Recall@10 0.2954 vs VALIDATED-paper-only 0.1449 (MRR 0.2464 → 0.2330; nDCG@10 0.4299 → 0.3237). The 79 SUGGESTED papers hold most machine-usable evidence; T-C04-family validation throughput is therefore on the retrieval critical path, not just a governance nicety.
- **AF-3 — `questions.command_word` is unpopulated** (119/119 NULL), which broke the planned calculation/marks query selectors and forced the recorded quota amendment in gold-v1; fixing it is cheap and improves future gold set v2 authoring.

## 6. What remains to reach Run 2

A0 baseline + B/C arms in the Java lane (Maven + Docker present), per `RETRIEVAL_BENCHMARK_HARNESS_SPEC.md` §7; then the §8 thresholds produce the first promotion verdict (expected candidate: hybrid lexical + semantic).
