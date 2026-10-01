# ADR-020: SyllabAI-native Educational Retrieval Engine

**Status:** Accepted architecture direction; implementation promotion gated by benchmark evidence  
**Date:** 2026-09-12  
**Related research:** `RAG_RETRIEVAL_RESEARCH.md`  
**Related architecture:** `MASTER_SPEC.md`, `SUBJECT_ARCHITECTURE.md`, `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md`

## Context

Research into `NirDiamant/RAG_Techniques`, `HKUDS/LightRAG`, `HKUDS/RAG-Anything`, and `infiniflow/ragflow` shows that SyllabAI can materially improve retrieval through hybrid recall, reranking, hierarchical/contextual retrieval, graph-aware expansion, evidence selection, multimodal extraction and stronger citation/evaluation practices.

However, these projects solve a broader generic RAG problem. SyllabAI already has an authoritative curriculum graph, SpecificationPoints, validated resource mappings, learner state and immutable learning evidence. Replacing those with a generic RAG framework would create competing sources of truth and weaken provenance.

## Decision

SyllabAI will build a provider-neutral **Educational Retrieval Engine** inside the existing modular architecture.

The canonical flow is:

```text
Learner query
  ↓
Intent/query understanding
  ↓
Curriculum + concept + learner resolution
  ↓
Lexical + semantic + metadata + authoritative-KG candidate generation
  ↓
Fusion/deduplication
  ↓
SyllabAI-aware reranking
  ↓
Evidence/segment selection
  ↓
Evidence sufficiency
  ↓
Grounded downstream AI
  ↓
Claim/citation validation
```

### Authoritative graph vs retrieval graph

The existing SyllabAI educational KG remains authoritative. External GraphRAG/LightRAG-style techniques may be used to traverse or retrieve from it, but automatically generated retrieval relationships must not become authoritative educational relations.

Retrieval-only relations may include `similar_to`, `co-occurs_with`, `supports`, or `adjacent_to`. Educational relations such as `REQUIRES_PREREQUISITE`, `MISCONCEPTION_OF`, `EXPLAINED_BY`, and `REMEDIATED_BY` remain governed by the existing provenance/validation/promotion process.

### Technology boundary

- PostgreSQL remains the system of record.
- pgvector remains the default vector layer.
- No Neo4j/RAGFlow/LightRAG deployment is required by this ADR.
- RAGFlow, LightRAG and RAG-Anything are reference/inspiration unless a later ADR proves a specific isolated component is justified.
- RAG-Anything-style multimodal parsing belongs primarily in the offline parser/content pipeline.
- Retrieval providers remain behind interfaces.

## Initial priorities

**P0:** hybrid lexical+semantic retrieval, hierarchical curriculum filtering, contextual metadata, reranking, explainable citation/evidence chain.

**P1:** relevant-segment reconstruction, authoritative KG-aware expansion, HyPE, structured query transformation, multimodal evidence extraction.

**P2:** contextual compression, CRAG, Self-RAG, agentic retrieval.

**P3:** RAPTOR, generic GraphRAG, wholesale RAGFlow/LightRAG/RAG-Anything adoption.

## Benchmark gate

No technique becomes a production default solely from external repository claims. The current 4CH1 corpus should be used to benchmark representative Tutor queries with Recall@K, MRR, nDCG, SpecificationPoint resolution accuracy, evidence precision, false-positive rate, citation correctness, unsupported-claim rate, latency and cost.

A technique must demonstrate meaningful educational retrieval improvement without unacceptable operational or provenance regressions.

## Consequences

### Positive

- Preserves SyllabAI's educational authority and existing KG investment.
- Allows adoption of the best proven retrieval techniques independently.
- Keeps Postgres/pgvector architecture simple and free-tier compatible.
- Makes retrieval quality measurable independently from generation quality.
- Creates a path to learner-aware retrieval that generic RAG platforms do not provide.

### Negative

- SyllabAI must implement and maintain more retrieval logic itself.
- A benchmark/evaluation corpus is required before aggressive optimization.
- Some generic framework features will not be adopted even if they are technically mature because their abstractions do not match SyllabAI's semantics.

## Scope guard

This ADR does not authorize bulk ingestion of new subjects or expansion of Cycle 1. Current pilot corpus remains Pearson Edexcel International GCSE Chemistry 4CH1. Retrieval work must not become an excuse to indefinitely delay the pilot.
