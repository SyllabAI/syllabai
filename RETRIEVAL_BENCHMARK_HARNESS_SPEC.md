# Retrieval Benchmark Harness Spec (T-C13)

**Status:** PROPOSED — Draft v0.1, authored 2026-09-17 on the T-C13 registration lane (commit `91bd842`). Awaiting owner ratification of the §10 open questions before M0 build starts. Committed as a research artifact per the repo's proposed-contract precedent (cf. the InterventionRun prototype contract); nothing in this doc changes a production default.
**Sources (accepted):** `RAG_RETRIEVAL_RESEARCH.md` §6 (arms A–I, metrics, acceptance principle, rule 12 "benchmark before promotion") as extended by `GEMINI_FILE_SEARCH_AND_NOTEBOOK_ARCHITECTURE_RESEARCH.md` §16 (File Search arms E–G, provider tests 1–8, 12-class query set).
**Related tracker rows:** T-C13 (this spec — the gate), T-C14 (provider-neutral + lexical retrieval contracts — supplies arm B/C retrievers), T-C15 (Gemini File Search POC — supplies arms E/F/G), T-C07 (curriculum scoping — hard prerequisite for arm A and any embedding work), T-C06 (corpus converter — out of scope here).
**DB-verified preconditions (production Neon, read-only, 2026-09-17 reconciliation `15d8914`/`82b3a8c`):** 182/182 4CH1 spec-point nodes VALIDATED (SUBTOPIC-typed, namespaced codes); 112 VALIDATED `REQUIRES_PREREQUISITE` + 14 `REMEDIATED_BY` + 13 `WRONG_ANSWER_PATTERN` + 2 `COMMONLY_CONFUSED_WITH` edges (= the settled 153-HV store, verified in exact sync); 98 CONCEPT nodes (all SUGGESTED); 127 VALIDATED question versions over 94 papers (15 VALIDATED); 172 documents (91 QUESTION_PAPER + 81 MARK_SCHEME); 2,333 chunks with **zero embeddings** (gated by T-C07); Flyway V26.

---

## 1. Purpose and gate semantics

This harness exists to arbitrate exactly one decision: **whether a retrieval configuration may become a production default** for the KA-RAG tutor and the resource assistants. `RAG_RETRIEVAL_RESEARCH.md` §6 states the rule this harness enforces, and MASTER_SPEC rule 12 repeats it: no technique is adopted from README claims; it is adopted when the benchmark shows a meaningful improvement without unacceptable latency/cost/complexity and without any deterioration in educational precision. The harness is therefore a measurement instrument, not a feature: it must never itself change serving behavior, and its output must be auditable evidence, not a dashboard opinion.

Three properties make the measurement trustworthy in this repo's governance culture. First, **honesty**: every arm reports its true state — an arm whose prerequisites are unmet reports `UNAVAILABLE` and contributes nothing, never a silent zero (fail-closed, the same discipline as the deterministic refusal on empty evidence). Second, **determinism**: a run is fully described by a committed manifest (gold-set hash, corpus snapshot hash, arm configuration, provider/model versions, fusion/reranker parameters); re-running the same manifest must reproduce the same numbers, and where an LLM judge is involved the judge config is pinned and the raw-agreement between judges is reported rather than a fabricated κ. Third, **provenance**: gold labels cite their source (spec-point code, question version, document checksum + page), because an unattributed gold label is exactly the kind of un-evidenced claim this codebase refuses elsewhere.

The known failure mode this harness must guard against is named in the research doc: a retrieval system can produce fluent answers while resolving the wrong SpecificationPoint. The primary quality axis is therefore **SpecificationPoint resolution and evidence identity**, not answer fluency. Grounding metrics (§5.2) exist to catch grounding regressions, but fluency is explicitly out of scope (§9).

## 2. What is benchmarked: the arms registry

Arms are **configurations over the provider-neutral retrieval contract** (see the RetrievalProvider contract sketch, to be ratified by T-C14), not new code paths. Each arm is an ordered composition of providers + fusion + reranking + filters. The registry unifies `RAG_RETRIEVAL_RESEARCH.md` §6 arms A–I with `GEMINI_FILE_SEARCH_...` §16 arms E–G; ids follow the research docs so results stay comparable across both.

| Arm | Composition | Prerequisite rows | Status at t0 |
|---|---|---|---|
| **A0** | KG-only deterministic retrieval (`GraphKnowledgeRetriever` through `ReciprocalRankFusion` as the single active arm, `NoReranker`) — **the current production default** | none | **RUNNABLE NOW — the baseline to beat** |
| **A** | pgvector semantic retrieval (`ContentVectorRetriever`, `GeminiEmbeddingProvider`) | T-C07 + embedding backfill | UNAVAILABLE (0/2,333 embedded) |
| **B** | BM25 / lexical (Postgres FTS `tsvector` + GIN on `document_chunks.content`) | T-C14 (retriever + migration) | UNAVAILABLE |
| **B-proxy** | Harness-internal raw-SQL FTS probe over the frozen snapshot — early lexical signal, **explicitly not a production arm**, never cited for promotion | none (snapshot only) | runnable at M1 |
| **C** | Hybrid lexical + semantic (RRF k=60, the shipped `ReciprocalRankFusion`) | A + B | UNAVAILABLE |
| **D** | C + reranker behind the `EvidenceReranker` port (default remains `NoReranker` until this benchmark says otherwise) | C | UNAVAILABLE |
| **E** | Gemini File Search standalone | T-C15 | UNAVAILABLE |
| **F** | Hybrid + File Search | C + T-C15 | UNAVAILABLE |
| **G** | KG-aware hybrid + File Search | C + T-C15 | UNAVAILABLE |
| **H1** | Hierarchical curriculum filtering (subject → unit → topic → spec point) over C | T-C07 | UNAVAILABLE |
| **H2** | Contextual metadata/headers (CMC front matter injected into chunk text) | T-C06 chunking contract | UNAVAILABLE |
| **H3** | HyPE (hypothetical document embeddings) over A | A | UNAVAILABLE |
| **I** | Authoritative KG expansion + best-of (KG expansion feeding C/D; the §6 "I" combo) | C/D + KG expansion rules | UNAVAILABLE |

Two registry rules. **Baseline honesty:** A0 is the only legitimate baseline until A is runnable, because A0 is what serves today; all deltas are reported against A0. **No silent demotion:** when a prerequisite lands, the arm flips to runnable in the next recorded run — arms are never removed from the registry, only marked unavailable (a removed arm would silently erase the comparison the research docs demand).

## 3. Gold set construction (the dataset)

### 3.1 Size, classes, quotas

Initial frozen tranche: **120 queries**, inside the research doc's 100–200 band, stratified over the 12 classes of the Gemini §16 query list (which is a superset of the §6 list). Minimum quotas, chosen so every class supports a per-class metric read:

| # | Class | Quota | Primary gold anchor |
|---|---|---:|---|
| 1 | Direct factual questions | 15 | spec-point code + gold chunks |
| 2 | Conceptual explanations | 15 | spec points + concept codes |
| 3 | Calculations | 10 | VALIDATED question versions + MS points |
| 4 | Prerequisite questions | 12 | the 112 VALIDATED `REQUIRES_PREREQUISITE` edges |
| 5 | Misconception questions | 10 | `REMEDIATED_BY` / `WRONG_ANSWER_PATTERN` edges |
| 6 | "Why did I get this wrong?" | 10 | VALIDATED qversion + its mark scheme |
| 7 | Exam-question retrieval | 10 | qversion → chunk identity |
| 8 | Mark-scheme retrieval | 8 | MS document + page |
| 9 | Revision-note retrieval | 10 | note chunk identity |
| 10 | Vague learner-language queries | 8 | same as source class, colloquial phrasing |
| 11 | Multi-SpecificationPoint questions | 7 | union of 2–3 spec points |
| 12 | Diagram/figure-dependent questions | 5 | chunks carrying figure markers |
| | **Total** | **120** | |

### 3.2 Authoring rules

Queries are authored **from validated material only** (the standing honesty constraint: SUGGESTED never serves, so SUGGESTED material never authors a gold anchor). Class 1–2 queries derive from the 182 VALIDATED spec points' command words and titles; class 4 from the settled prerequisite edges (source → target concept, resolved to spec points); class 5–6 from the 127 VALIDATED question versions and their mark schemes; class 7–9 from chunk identities of VALIDATED papers and validated revision notes. Vague-language queries (class 10) are paraphrase sets over classes 1–3 authored in colloquial learner phrasing, and multi-SpecPoint queries (class 11) are composed from non-adjacent spec points to defeat trivial co-retrieval. Diagram-dependent queries (class 12) are capped at 5 because figure-marker coverage in the current corpus is thin; the class stays in the registry with an honest small quota rather than being dropped.

Two anti-corruption rules bind authoring. **No tuning on the test set:** queries are authored without executing any retrieval arm against them; the set is frozen and SHA-256-manifested before the first recorded run, and after freezing it is read-only — tuning iterations must author a separate dev split or wait for a versioned re-freeze (v2, v3, …), never mutate v1 in place. **Every label cites provenance:** a gold label without a cited source (spec-point code / qversion id / document checksum + page) fails the set validator, exactly as graph edges without evidence anchors fail `graph_check`.

### 3.3 Label shape

Each gold record carries: the query text; **gold SpecificationPoints** (required, ≥1); **gold evidence** where practical, as graded relevance tiers — `2` = directly answers the query, `1` = legitimate supporting evidence, `0` = not relevant (tiers are what make nDCG meaningful); **gold concepts/misconceptions** where applicable (from the settled graph, by code); and the provenance citations. Evidence identity is **portable**: chunks are identified by `(document checksum, chunk ordinal, content SHA-256)` — never by environment-local DB UUIDs — so the same frozen set scores identically against a Testcontainers rebuild, the classpath snapshots, or production (this is also what makes Gemini §16 provider test 2, document identity fidelity, scoreable).

### 3.4 Storage and freeze mechanics

The frozen set lives in-repo under `bench/gold/` as deterministic YAML/JSON (one file per class + a manifest), in the byte-verbatim, SHA-256-pinned style the graph store already uses (`graph/*.yaml` never hand-edited; generators + validators, no freehand). The manifest records set version, per-class counts, total, authoring source list, and the SHA-256 of every file. A `bench/gold_check.py`-style validator (deterministic, negative-tested) enforces: schema, quota table conformity, provenance presence, tier validity, spec-point code format (`^4CH1-[0-9]+\.`), and cross-file uniqueness of query text.

---

## 4. Corpus snapshot discipline

The harness never scores against live production. A one-time deterministic export per set version captures: every serving-eligible chunk (`(checksum, ordinal, content hash, document kind, page)`, 2,333 at t0), the VALIDATED spec-point table (182 codes + titles), the settled graph projection relevant to retrieval (112 + 14 + 13 + 2 VALIDATED edges with endpoint codes), and the four-tier spec-mapping rows with `HUMAN_VALIDATED` provenance flagged. The export is committed under `evidence/bench-001/snapshot/` with `SHA256SUMS`, in the same evidence-outlives-retention spirit as cycle-001. Production DB access (the operator's Neon read-only path) is used **only to build the snapshot**; scoring is fully offline. Any corpus change (T-C06 imports, re-chunking) invalidates the snapshot and requires a new set+snapshot version pair — recorded, never patched.

## 5. Metrics

### 5.1 Retrieval (deterministic, primary)

- **Recall@5 / @10 / @20** — fraction of the query's gold evidence (tier ≥1) present in the top-k of the fused ranking.
- **MRR** — 1/rank of the first tier-2 hit.
- **nDCG@10** — graded, using the 2/1/0 tiers.
- **SpecificationPoint resolution accuracy** — the flagship metric: does the arm surface evidence whose `HUMAN_VALIDATED` spec mapping covers the query's gold spec points (AI_SUGGESTED / RULE_DERIVED mappings never count as resolution, per the four-tier provenance contract)?
- **Evidence precision@10** — tier ≥1 fraction of the top-10.
- **False-positive rate** — tier-0 fraction of the top-10, reported per class (a fluent-but-wrong retrieval shows up here first).
- **Validation-boundary flag (hard)** — any arm surfacing a chunk or resource whose serving state is SUGGESTED-only is recorded as a `VALIDATION_BOUNDARY_VIOLATION`; per Gemini §16 test 5 this is not a metric to trade off, it is a fail condition for the run (score the run, print the violation, mark the arm's result `INVALID for promotion`).

Per-class breakdowns are mandatory in every report — an aggregate that hides a collapsed class (e.g., calculations) is treated as a misreport.

### 5.2 Grounding (M2, bounded-cost)

Measured over the existing grounded generation path (`GroundedTutorGenerator`, tutor-grounded/v2) with a **fixed, manifest-pinned generator config**, on a stratified 40-query subset of the frozen set (all 12 classes represented): evidence sufficiency (does the retrieved set contain the gold evidence needed for a complete answer), citation correctness (do the emitted citations resolve to retrieved evidence via `SimpleCitationResolver` semantics), claim-to-evidence alignment, and unsupported-claim rate. Where judging requires an LLM, the judge model/prompt/version are pinned in the run manifest and the judge's raw agreement across a double pass is reported (the C11 precedent: honest raw agreement, no fabricated κ). LLM judging budget is capped per run (§10) so the gate cannot become a cost leak.

### 5.3 Operations

p50/p95 latency per arm; embedding + retrieval + LLM cost per query (incl. File Search quota for E/F/G); LLM calls per query; storage overhead (pgvector bytes vs FS index); index build/rebuild time; failure/retry rate (FS arms); provider dependency surface (Gemini §16 operational list).

## 6. Harness architecture

Lives in `syllabai-core` under `src/test/java/com/syllabai/bench/` (JUnit tag `benchmark`, excluded from default CI runs) plus a `BenchmarkRunner` main for local/evidence runs, mirroring the existing split of unit tests vs `KaRagFlowIT`-style harnesses. Core pieces: `GoldSetLoader` (validates against the manifest before anything runs — fail-closed), `SnapshotStore` (loads the committed corpus snapshot), `ArmRegistry` (declarative arm configs over the `RetrievalProvider` port), `MetricsEngine` (pure, deterministic scoring), `RunManifest` + `RunReport` writers (JSON + human-readable md under `evidence/bench-001/runs/`, with `SHA256SUMS`). Determinism contract: no clocks in scoring paths, pinned provider versions recorded per run, fixed seeds, and the fusion parameters (RRF k=60) recorded explicitly — a run whose manifest cannot be reconstructed is discarded, not approximated.

Arms with unmet prerequisites return `UNAVAILABLE` with the named missing row (e.g., "A: requires T-C07 + embedding backfill") — the registry never fabricates numbers, and an empty result from a *runnable* arm is scored as a real zero (that is how the deterministic-refusal honesty propagates into measurement).

## 7. Phasing and exit conditions

- **M0 — gold set:** author + validate + freeze v1 (120 queries, 12 classes) and the corpus snapshot; validator green incl. negative tests. No code dependencies; startable immediately after ratification.
- **M1 — harness + baseline:** harness core + arm A0 + arm B-proxy; **Run 1 recorded** = the baseline numbers on record for every future delta. Fully offline, no keys, no spend.
- **M2 — semantic arms:** arm A after T-C07 + embedding backfill, then C, D, H1; grounding metrics with the pinned generator config; first hybrid-vs-baseline verdict.
- **M3 — File Search arms:** E/F/G via T-C15 plus provider tests 1–8 (metadata filtering accuracy, document identity fidelity, page/figure fidelity, corpus update behavior, validation boundary, isolation, scale, portability).
- **T-C13 exit condition:** registry A0/A/B/C/D runnable, frozen gold set v1, ≥1 full recorded run per arm with reports + manifests under `evidence/`, and the owner's written acceptance of the promotion verdict for the first technique (expected: hybrid lexical + semantic).

Ordering note (lanes stay distinct): T-C13 does not block on T-C14/T-C15 — M0/M1 proceed now; arms light up as their prerequisite rows land, in recorded runs, on the same frozen v1 set.

## 8. Proposed acceptance thresholds (owner-ratifiable)

The research docs state the acceptance **principle** qualitatively; the harness needs numeric lines to enforce. Proposed (v0.1, for ratification): a technique becomes a production default iff, on frozen set v1 vs A0 — (a) Recall@10 improves ≥10% relative; (b) MRR improves ≥0.05 absolute; (c) nDCG@10 improves ≥0.05 absolute; (d) SpecificationPoint resolution does not regress by more than 1 percentage point; (e) p95 latency increases by ≤300 ms; (f) zero validation-boundary violations; (g) no single class regresses by more than 15% relative without a written tradeoff note in the run report. Replacing pgvector with File Search wholesale (the Gemini decision matrix's "not yet; benchmark first") additionally requires provider tests 1–8 to pass and a recorded cost-parity or accepted-cost-premium note. Thresholds are versioned with the gold set; changing thresholds and re-judging an old run against new thresholds is forbidden — new thresholds mean new runs.

## 9. Non-goals

No answer-fluency evaluation (the named trap: fluent-but-wrong). No tuning loops against the frozen set. No changes to serving behavior, fusion defaults, or provider wiring inside the harness lane — the harness measures; promotion happens in the owning lane with its own verification discipline. No live-production scoring, no write access from harness code, and no new external dependencies beyond what the arms themselves require.

## 10. Open questions for owner ratification

1. **Thresholds** — accept §8 v0.1 numbers, or adjust before M0?
2. **Set size** — 120 now (expandable to 200 later as v2), or author the full 200 immediately?
3. **Labeling ownership** — operator reviews auto-derived labels (recommended: auto-derive from validated anchors, operator spot-checks 20% + all class-4/5/6), or full manual authoring?
4. **M2 judge budget** — cap LLM judging spend per run (proposed: a fixed small quota; double-pass agreement only on the 40 grounding-metric queries)?
5. **B-proxy legitimacy** — confirm the harness-internal FTS probe may publish early lexical signal (clearly marked non-production), or must arm B wait for T-C14's production retriever?
6. **Arm timing** — any appetite to pull H2 (contextual headers) forward via the T-C06 chunking contract, or keep it behind C/D verdicts as sequenced here?

---

**Provenance:** arms/metrics/acceptance principle — `RAG_RETRIEVAL_RESEARCH.md` §6 (last touched `59bf30c`, 2026-09-11); File Search arms + provider tests + 12-class set — `GEMINI_FILE_SEARCH_AND_NOTEBOOK_ARCHITECTURE_RESEARCH.md` §16 (2026-09-14). T-C13 row registered `91bd842` (2026-09-16). DB preconditions verified read-only 2026-09-17, reconciliation commits `15d8914`/`82b3a8c`. RetrievalProvider contract relationship per the uncommitted contract sketch (2026-09-17) — ratification tracked under T-C14.
