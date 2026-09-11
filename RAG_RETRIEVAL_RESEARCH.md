# SyllabAI RAG & Retrieval Research — Definitive Integration Guidance

**Status:** Accepted research/architecture guidance; implementation requires benchmark evidence before promotion to production defaults.
**Research date:** 2026-09-12
**Scope:** `NirDiamant/RAG_Techniques`, `HKUDS/LightRAG`, `HKUDS/RAG-Anything`, `infiniflow/ragflow` and their implications for SyllabAI.
**Primary SyllabAI constraint:** These projects are implementation references. SyllabAI remains the authoritative educational system and must not become a generic RAG platform.

---

## 1. Executive decision

These repositories are genuinely useful to SyllabAI, but **not as wholesale dependencies or replacements for the SyllabAI architecture**.

The strongest conclusion is:

> Build a SyllabAI-native Educational Retrieval Engine and selectively borrow proven retrieval/document-processing techniques from these projects.

The engine should sit underneath the Tutor and other grounded AI features:

```text
Official curriculum + validated resources
                ↓
        SyllabAI Curriculum KG
                ↓
 SpecificationPoints / Concept KG / Prerequisite KG
                ↓
          Learner KG / State
                ↓
         Query Understanding
                ↓
 Curriculum + learner + concept resolution
                ↓
        Candidate generation
     ┌──────────┼───────────┐
     ↓          ↓           ↓
  lexical    semantic      KG
     ↓          ↓           ↓
     └──────────┼───────────┘
                ↓
              Fusion
                ↓
       SyllabAI-aware reranking
                ↓
        Evidence selection
                ↓
       Evidence sufficiency
                ↓
            Tutor LLM
                ↓
       Claim/citation check
                ↓
       Grounded Tutor answer
```

Do **not** replace the authoritative SyllabAI graph with a framework-generated graph, and do not let embeddings become educational truth.

---

## 2. Why generic RAG is insufficient

SyllabAI is not a `PDF → chunks → embeddings → vector DB → LLM` product.

The long-term substrate is:

```text
Board → Qualification → Subject → CurriculumVersion
  → Section → Topic/SubTopic → SpecificationPoint
```

with:

- validated resources and evidence;
- many-to-many resource → SpecificationPoint mappings;
- concept/prerequisite/misconception relationships;
- immutable assessment evidence;
- mutable learner review state;
- derived mastery, misconception, confidence and procedural-fluency state;
- recommendation/next-best-action logic.

Therefore retrieval must answer more than "what text is similar?" It must answer:

1. What subject/curriculum version is this about?
2. Which SpecificationPoint(s) are implicated?
3. Which concepts and prerequisites are relevant?
4. What does this learner currently know or misunderstand?
5. Which validated resources are appropriate?
6. Which exact evidence segments support the intended answer?
7. Is the evidence sufficient for the claim the Tutor wants to make?

---

# 3. Repository-by-repository assessment

## 3.1 NirDiamant/RAG_Techniques

**Official repository:** https://github.com/NirDiamant/RAG_Techniques

**Role:** Research/reference toolbox. Do not treat it as a framework dependency.

The repository contains many runnable implementations of individual retrieval techniques, including hybrid/fusion retrieval, reranking, contextual enrichment, HyPE, relevant segment extraction, semantic chunking, query transformations, hierarchical retrieval, graph RAG, explainable retrieval, CRAG, Self-RAG, RAPTOR and agentic approaches.

### SyllabAI value

**Very high as a technique-selection and benchmarking source.** It lets SyllabAI test individual techniques against its actual Chemistry corpus rather than adopting a generic platform.

### Highest-value techniques

#### Hybrid/Fusion Retrieval — priority: P0

Combine lexical and semantic retrieval rather than relying on one signal.

Useful signals:

- BM25/exact lexical match;
- pgvector semantic similarity;
- specification code match;
- subject/curriculum metadata;
- resource type;
- concept match;
- learner-state relevance.

#### Reranking — priority: P0

Initial retrieval should be broad; a second-stage reranker should select the most educationally relevant candidates.

The SyllabAI reranker should eventually consider:

```text
semantic relevance
+ lexical relevance
+ SpecificationPoint match
+ concept match
+ prerequisite relevance
+ misconception relevance
+ learner-state relevance
+ resource suitability
+ exam relevance
+ evidence quality
```

Do not assume a generic cross-encoder is automatically the final answer. Benchmark it first, then add SyllabAI-specific features.

#### Contextual headers / contextual enrichment — priority: P0

Retrieved evidence should carry structured context such as:

```text
Subject: International GCSE Chemistry
Qualification: Pearson Edexcel International GCSE
Specification: 4CH1 2017 linear
Section: Principles of Chemistry
Topic: Chemical Formulae, Equations and Calculations
SpecificationPoint: 1.28
ResourceType: Revision Note
```

This improves retrieval without flattening the canonical curriculum hierarchy.

#### Hierarchical retrieval — priority: P0

Use SyllabAI's existing hierarchy as a retrieval constraint/expansion mechanism. Do not invent a second synthetic hierarchy merely because a RAG technique supports one.

#### Relevant Segment Extraction — priority: P1

After retrieval/reranking, reconstruct contiguous local evidence where educational meaning depends on surrounding material. Particularly useful for worked calculations, multi-step explanations, practical procedures, tables and diagram-adjacent prose.

#### HyPE — priority: P1 experimental

Generate hypothetical learner questions during indexing and use them as retrieval aliases/proxies. This is promising because educational language has a strong document-language vs learner-language mismatch.

HyPE output is **retrieval metadata, never educational truth**.

Recommended structure:

```text
Validated resource
  ↓
SpecificationPoint mappings
  ↓
Concepts
  ↓
Candidate hypothetical learner questions
  ↓
validation/deduplication
  ↓
retrieval aliases
```

#### Query transformation — priority: P1

Use structured query understanding rather than simple paraphrase generation. A learner query such as "Why did I get this wrong?" should resolve intent, question identity, SpecificationPoint, misconception and prerequisite context before retrieval.

#### Explainable retrieval — priority: P0

Every grounded Tutor answer should be able to explain why evidence was selected.

### Lower-priority / generally unsuitable techniques

- Generic GraphRAG: useful as a retrieval idea, not as SyllabAI's authoritative graph.
- RAPTOR: probably redundant while SyllabAI already has explicit curriculum hierarchy.
- Generic semantic chunking: must not cross meaningful SpecificationPoint/resource boundaries merely because embeddings suggest similarity.
- Generic Agentic RAG: defer until deterministic retrieval is benchmarked and shown insufficient.
- Self-RAG: interesting research, not a current priority because SyllabAI can implement explicit evidence-sufficiency and claim-checking gates.
- CRAG: potentially useful later as a retrieval-quality fallback.

### License

Treat the repository as a research/reference source. Check the current repository license before copying code into SyllabAI. Do not assume a notebook implementation is automatically safe to embed.

---

## 3.2 HKUDS/LightRAG

**Official repository:** https://github.com/HKUDS/LightRAG

**Assessment:** ~9/10 as architecture/research reference; substantially lower as a direct dependency.

LightRAG is valuable because it combines graph-aware retrieval, multiple retrieval/query modes, vector/keyword retrieval, reranking, citation/source handling, evaluation/tracing integrations, PostgreSQL-compatible storage options and multimodal integration.

### What SyllabAI should borrow

- graph-aware retrieval;
- local/global retrieval modes;
- graph expansion around relevant entities;
- candidate fusion;
- reranking;
- citation/evidence tracking;
- retrieval observability/evaluation.

### What SyllabAI must not borrow as-is

LightRAG's retrieval graph and SyllabAI's educational knowledge graph have different semantics.

**LightRAG-style graph:** useful for retrieving information.

**SyllabAI graph:** represents educational truth and validated relationships.

Never promote an automatically inferred LightRAG-style edge into an authoritative `REQUIRES_PREREQUISITE`, `MISCONCEPTION_OF`, `EXPLAINED_BY` or similar SyllabAI educational relation without the existing provenance/validation gates.

This is especially important after T-C11, where one candidate prerequisite was rejected and another held because evidence did not support the proposed relation. Co-occurrence or semantic similarity is not evidence of pedagogical dependency.

### Recommended architecture

Keep the authoritative graph in PostgreSQL using the existing SyllabAI graph contracts. Use LightRAG-style traversal as a **retrieval strategy over that graph**.

Do not introduce Neo4j or another graph database solely to imitate LightRAG.

### Citation chain

SyllabAI should go deeper than a generic chunk citation:

```text
Tutor claim
  ↓
Evidence segment
  ↓
Validated resource
  ↓
SpecificationPoint
  ↓
SpecificationVersion
  ↓
Official source/provenance
```

---

## 3.3 HKUDS/RAG-Anything

**Official repository:** https://github.com/HKUDS/RAG-Anything

**Assessment:** ~9/10 as a multimodal ingestion/reference layer; ~4/10 as a complete SyllabAI architecture.

RAG-Anything is especially relevant because educational chemistry resources are not text-only. PDFs may contain:

- tables;
- equations;
- chemical notation;
- diagrams;
- apparatus illustrations;
- question layouts;
- mark-scheme structures;
- scanned pages.

### Best role

Use it as a **candidate multimodal extraction pipeline** in `syllabai-parser` research/ingestion work.

```text
PDF / DOCX / image / scan
          ↓
multimodal parser / VLM
          ↓
candidate structured representation
          ↓
provenance + deterministic validation
          ↓
human/validation gate where required
          ↓
authoritative SyllabAI content objects
```

### Critical rule

VLM/parser output is not authoritative truth.

A parser can misread an equation, table cell, diagram label or chemical symbol. Extraction must preserve uncertainty and source location, and authoritative SpecificationPoints remain governed by the curriculum pipeline.

### Strong future use

Represent document evidence as typed elements:

```text
Document
 ├── TextSegment
 ├── Table
 ├── Equation
 ├── Figure
 ├── Question
 ├── Answer/MarkPoint
 └── Page/BoundingBox provenance
```

Those evidence objects can then be retrieved by the SyllabAI retrieval engine.

---

## 3.4 infiniflow/ragflow

**Official repository:** https://github.com/infiniflow/ragflow

**Assessment:** ~9/10 engineering/reference value; ~3/10 as a direct SyllabAI dependency.

RAGFlow is particularly valuable for studying production-oriented document ingestion, chunking, multiple recall, fused reranking, grounded citations, metadata filtering and operational controls.

### Strong lessons

1. Treat document ingestion as a real pipeline, not a naive fixed-token splitter.
2. Preserve document structure and metadata.
3. Combine multiple retrieval methods.
4. Rerank after broad recall.
5. Make citations/evidence first-class.
6. Expose retrieval configuration and observability.
7. Evaluate retrieval independently from generation.

### Why not embed RAGFlow

RAGFlow is a complete RAG platform and would introduce a competing abstraction around documents, chunks, datasets, retrieval and orchestration.

SyllabAI already owns:

- curriculum;
- SpecificationPoints;
- resources;
- knowledge graph;
- assessment;
- learner state;
- tutoring;
- provenance;
- evidence.

Adding RAGFlow wholesale risks creating two sources of truth and an unnecessary operational stack.

Use its ideas behind SyllabAI contracts instead.

---

# 4. Authoritative SyllabAI architecture decision

## Two graph layers, not one

SyllabAI should conceptually distinguish:

### Authoritative Educational KG

Contains validated educational relations:

```text
SpecificationPoint
Concept
Prerequisite
Misconception
Resource relationship
```

Governed by provenance, confidence, validation and the T-C11 promotion rules.

### Retrieval Graph / Retrieval View

Can contain derived, non-authoritative retrieval relations:

```text
retrieves
similar_to
co-occurs_with
supports
adjacent_to
shares_context
```

These may be generated automatically because their purpose is retrieval, but they must never silently become educational truth.

This distinction is mandatory.

---

# 5. Recommended SyllabAI Educational Retrieval Engine

```text
Learner request
      ↓
Intent + query understanding
      ↓
Curriculum resolution
      ↓
Concept / misconception resolution
      ↓
Learner-state resolution
      ↓
Candidate generation
 ┌────┼─────┬──────┐
 ↓    ↓     ↓      ↓
BM25 semantic metadata KG expansion
 └────┴─────┴──────┘
      ↓
Fusion / deduplication
      ↓
SyllabAI-aware reranker
      ↓
Evidence selection / relevant-segment reconstruction
      ↓
Evidence sufficiency gate
      ↓
Tutor / downstream AI
      ↓
Claim verification + citation chain
```

### Retrieval candidate metadata

At minimum, candidates should carry:

- subject ID;
- qualification ID;
- curriculum/specification version;
- section/topic/subtopic;
- SpecificationPoint IDs;
- concept IDs;
- resource ID/version;
- evidence segment ID;
- resource type;
- provenance;
- validation status;
- embedding/model metadata;
- optional HyPE/query aliases;
- retrieval source(s) and scores.

### Learner-aware ranking

The same learner query can legitimately retrieve different evidence for different learners.

Example:

```text
Learner A:
  mole mastery high
  percentage-yield mastery low
  misconception: moles ↔ grams confusion high

Learner B:
  mole mastery low
  reacting-mass mastery low
  no established percentage-yield misconception
```

A generic semantic retriever may return the same note. A SyllabAI-aware engine should be able to prioritize different prerequisite/remediation evidence.

Learner state is therefore a **ranking/context signal**, not a replacement for curriculum truth.

---

# 6. Retrieval benchmark before implementation promotion

Do not adopt these techniques based on README claims alone.

Construct a real SyllabAI benchmark over the current IGCSE Chemistry 4CH1 corpus. The benchmark should include roughly 100–200 representative Tutor queries covering:

- direct factual questions;
- conceptual questions;
- calculation questions;
- prerequisite questions;
- misconception questions;
- "why did I get this wrong?" requests;
- exam-question requests;
- revision requests;
- vague natural-language learner queries;
- multi-SpecificationPoint questions.

The benchmark should include known gold SpecificationPoints and gold evidence where practical.

### Compare at least

```text
A  baseline semantic retrieval
B  BM25 / lexical
C  hybrid lexical + semantic
D  hybrid + reranking
E  hierarchical filtering + hybrid + reranking
F  contextual headers + E
G  HyPE + E
H  authoritative KG expansion + E
I  KG + HyPE + reranking + evidence selection
```

### Metrics

Retrieval:

- Recall@5
- Recall@10
- Recall@20
- MRR
- nDCG
- SpecificationPoint resolution accuracy
- evidence precision
- false-positive rate

Grounding:

- evidence sufficiency;
- citation correctness;
- claim-to-evidence alignment;
- unsupported-claim rate.

Operations:

- p50/p95 latency;
- embedding/retrieval cost;
- LLM calls per query;
- storage overhead;
- index build time.

### Acceptance principle

A technique should become a default only if it produces a meaningful improvement on the benchmark without unacceptable latency/cost/complexity or a deterioration in educational precision.

Do not optimize only generic answer quality. A retrieval system can produce fluent answers while retrieving the wrong SpecificationPoint.

---

# 7. Priority table

| Technique | Priority | Decision |
|---|---:|---|
| Hybrid lexical + semantic retrieval | P0 | Benchmark and likely adopt |
| SyllabAI-aware reranking | P0 | Benchmark and likely adopt |
| Hierarchical curriculum retrieval | P0 | Adopt as architecture |
| Contextual metadata/headers | P0 | Benchmark and likely adopt |
| Explainable retrieval/citation chain | P0 | Required design principle |
| Relevant Segment Extraction | P1 | Benchmark |
| Authoritative KG-aware retrieval | P1 | Benchmark |
| HyPE | P1 | Serious experiment |
| Query transformation | P1 | Implement as structured query understanding |
| Multimodal extraction | P1 | Investigate in parser pipeline |
| Contextual compression | P2 | Later |
| CRAG | P2 | Later experiment |
| Self-RAG | P2 | Research only initially |
| Agentic RAG | P2 | Later |
| RAPTOR | P3 | Low priority |
| Generic GraphRAG | P3 | Retrieval ideas only |
| Generic semantic chunking | P3 | Use only where structure permits |
| RAGFlow wholesale | P3 | Do not adopt |
| LightRAG wholesale | P3 | Do not adopt |
| RAG-Anything wholesale | P3 | Do not adopt |

---

# 8. Integration rules for agents

1. **Do not install a RAG framework merely because it supports a desired technique.** Reimplement the smallest necessary behavior behind SyllabAI interfaces when that is simpler.
2. **Do not replace PostgreSQL/pgvector by default.** The current architecture already supports the needed relational graph + vector substrate.
3. **Do not create Neo4j solely for GraphRAG.** The authoritative graph remains PostgreSQL-backed.
4. **Do not let embeddings define educational truth.** Embeddings are retrieval signals.
5. **Do not let automatically generated graph edges become authoritative educational relations.** They require the existing evidence/provenance/validation gates.
6. **Do not flatten SpecificationPoints into arbitrary chunks.** Curriculum hierarchy is retrieval context.
7. **Do not cite only a vector chunk when a richer provenance chain exists.** Prefer claim → evidence segment → resource → SpecificationPoint → specification source.
8. **Do not use HyPE-generated questions as curriculum or assessment truth.** They are retrieval aliases only.
9. **Do not introduce a second learner model inside retrieval.** Retrieval consumes the canonical learner state/evidence subsystem.
10. **Keep retrieval provider-neutral.** `VectorStore`, graph repository, retrieval, reranking and evidence-selection contracts must not expose a vendor-specific domain model.
11. **Keep external repository code behind the license wall.** Check license at the exact commit before copying code/data.
12. **Benchmark before promotion.** Record dataset, corpus version, query set, model/provider, configuration, metrics and failure cases.
13. **Preserve free-tier constraints.** Retrieval improvements must not silently introduce paid-only infrastructure or model requirements.
14. **Do not allow retrieval work to block the pilot indefinitely.** Build the minimum useful Tutor retrieval path, benchmark it, then iterate.

---

# 9. Corpus-specific guidance for the current 4CH1 pilot

The current Cycle-1 subject scope is Pearson Edexcel International GCSE Chemistry 4CH1 (2017 linear).

Current validated substrate includes:

- 182 SpecificationPoints;
- 112 SME revision notes;
- 209 final HUMAN_VALIDATED note → SpecificationPoint mappings;
- T-C09 deterministic specification graph;
- T-C11 concept/prerequisite/misconception pilot with explicit promotion gates;
- 4.15 intentionally uncovered in T-C10 after semantic review;
- 1.17 rejected mapping;
- T-C11 held/rejected candidate edges must not be silently promoted.

Retrieval experiments must respect these facts. In particular:

- uncovered `4CH1-4.15` must not acquire manufactured resource coverage through retrieval aliases or generated graph edges;
- rejected/held T-C11 edges are not valid expansion paths;
- retrieval can discover candidate evidence but cannot rewrite curriculum coverage;
- note mappings are many-to-many and exact resource identity matters;
- official specification provenance outranks resource-derived claims.

---

# 10. Recommended implementation sequence

### Phase A — Retrieval contracts

Define provider-neutral contracts for:

- lexical retrieval;
- semantic retrieval;
- candidate fusion;
- reranking;
- curriculum filtering;
- graph expansion;
- evidence segment selection;
- evidence sufficiency;
- citation construction.

### Phase B — Baseline

Implement/measure:

```text
pgvector + lexical search
        ↓
metadata filtering
        ↓
basic fusion
        ↓
existing validated evidence
```

### Phase C — Reranking

Add cross-encoder or equivalent reranking behind an interface and measure gains.

### Phase D — Curriculum-aware retrieval

Add SpecificationPoint/topic/concept filtering and authoritative KG expansion.

### Phase E — Context enrichment

Add structured contextual headers/metadata to retrieval representations.

### Phase F — HyPE + segment reconstruction

Benchmark both independently and together.

### Phase G — Learner-aware retrieval

Use learner evidence/state to rank interventions without changing curriculum truth.

### Phase H — Tutor grounding

Add evidence sufficiency and claim/citation validation.

---

# 11. Non-goals

This research does not authorize:

- replacing the SyllabAI curriculum KG;
- creating a second graph database;
- replacing Postgres/pgvector;
- moving the Tutor to an external RAG platform;
- bulk ingestion of other subjects;
- turning Cycle 1 into a generic RAG research project;
- treating automatically extracted or generated relationships as validated educational truth;
- importing code/data from repositories whose licenses fail ADR-013.

---

# 12. Bottom line

The external repositories have exposed a strong set of techniques, but SyllabAI's competitive architecture should remain its own.

The likely winning combination is:

> **SyllabAI authoritative curriculum/knowledge graph + learner state + hybrid retrieval + SyllabAI-aware reranking + hierarchical/contextual retrieval + evidence-level citations + selective HyPE/segment reconstruction + multimodal ingestion.**

The repositories should be treated as a research toolbox and engineering reference library. The benchmark decides which techniques graduate into production defaults.
