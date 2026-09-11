# AGENT.md - SyllabAI Agent Operating Manual

## Mission

You are working on **SyllabAI**, a research-informed, syllabus-grounded adaptive learning and examination-preparation platform. The application backend is Java/Spring Boot; the web frontend is Next.js/React. Your job is not merely to make code compile. Preserve architecture, research meaning, evidence traceability, provenance, validation state and project state while making measurable progress.

SyllabAI is **not a generic RAG chatbot**. Its defining loop is:

```text
Official curriculum + assessment evidence
        ↓
Structured knowledge
        ↓
Prerequisite / concept graph
        ↓
Learner state
        ↓
Diagnosis
        ↓
Targeted intervention
        ↓
Assessment again
        ↓
Learner update
        ↓
Next best learning step
```

---

## Mandatory reading order

Before substantial changes:

1. `MASTER_SPEC.md`.
2. Relevant rows in `backlog/syllabai-master-project.xlsx` and TSV export.
3. Relevant repository/module documentation.
4. `PROJECT_CONTEXT.md` for cross-cutting or unclear work.
5. `SUBJECT_ARCHITECTURE.md` for subject/curriculum/content-linking/assessment-tagging/knowledge-graph/student subject workspace work.
6. `TEACHER_ARCHITECTURE.md` for teacher/class/LMS/Test Builder/assignments/teacher analytics/teacher AI/class-KG work.
7. `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` and `LEARNING_EVIDENCE_AGENT_ADDENDUM.md` for question/attempt/assessment evidence/Smart Mark/review/recommendation/telemetry work.
8. `RAG_RETRIEVAL_RESEARCH.md` for retrieval, Tutor grounding, embeddings, reranking, graph retrieval, HyPE, evidence selection or multimodal-RAG work.
9. `RAG_RETRIEVAL_CORPUS_GUIDANCE.md` in `syllabai-resources` for corpus-side retrieval preparation.
10. Relevant research-paper sections whenever scientific constructs, hypotheses, operational definitions, metrics or learner-model semantics change.

The Master Spec is the engineering source of truth. Research papers remain authoritative for scientific claims. Named architecture addenda govern their specific layers. Do not silently resolve conflicts; record them and make/update the appropriate decision.

## Source hierarchy

1. Research papers — scientific claims, hypotheses, operational definitions and evaluation design.
2. `MASTER_SPEC.md` — engineering architecture and technology decisions.
3. Canonical architecture addenda — named architecture layers.
4. Definitive project spreadsheet — feature inventory and execution state.
5. `RAG_RETRIEVAL_RESEARCH.md` — canonical RAG/retrieval research and integration guidance.
6. `REPOSITORY_RESEARCH.md` — external implementation references and license decisions.
7. `DECISIONS.md` and ADR files — explicit architecture decisions.
8. `SUBJECT_ARCHITECTURE.md` — subject/specification-point architecture.
9. `TEACHER_ARCHITECTURE.md` — teacher/classroom architecture.
10. `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` and addendum — assessment evidence architecture.
11. `WORKLOG.md`, `PROGRESS.md`, `TODO.md` — living execution state/history.

---

## Project repositories

```text
syllabai           main repo: spec, ADRs, backlog, research dossiers, papers
syllabai-web       Next.js 16 / React 19 / TypeScript frontend
syllabai-core      Java 25 / Spring Boot 4.1 / Spring AI 2.0 modular monolith
syllabai-parser    polyglot offline content pipeline
Past-Papers        official QP/MS corpus source repository
syllabai-resources validated revision/content corpus and corpus QA
```

All domain modules (identity, curriculum, knowledge, content, assessment, smartmark, learner, tutor, diagnostic, recommendation, teacher, research/telemetry, infrastructure) live inside `syllabai-core` unless a real runtime/lifecycle boundary justifies separation.

## Technology constraints

- Java 25.
- Spring Boot 4.1.x + Spring AI 2.0.x.
- Maven.
- Next.js 16.x / React 19.x / TypeScript.
- Vercel frontend.
- Neon PostgreSQL + pgvector by default.
- Render/Docker for free-tier Java deployment.
- Cloudflare R2 for object storage.
- Default free LLM chain: Groq → Gemini 2.5 Flash → OpenRouter free models.
- Provider-neutral interfaces for LLM, embeddings, vector, graph, parser and object storage.

Do not add paid-only infrastructure merely for convenience. Do not embed code/data from non-permissive licenses. Check ADR-013 and the exact current license before copying external code or datasets.

---

# Subject-first architecture

The canonical curriculum hierarchy is:

```text
Board → Qualification → Subject → CurriculumVersion
  → Unit/Section → Topic/SubTopic → SpecificationPoint
```

`SpecificationPoint` is a first-class canonical curriculum/knowledge anchor. Preserve official code, wording, ordering, curriculum version, provenance and applicability. Never flatten official numbered objectives into generic topic tags.

Resources map many-to-many to SpecificationPoints. Questions may map at QuestionPart level to multiple SpecificationPoints. Uncertainty and review state remain explicit.

Learner state is a separate time-aware overlay: mastery, misconception, confidence, procedural fluency, exposure/evidence and review/decay. Never mutate official curriculum nodes with learner-specific state.

**Current Cycle 1 scope:** Pearson Edexcel International GCSE Chemistry 4CH1 (2017 linear), under the current scope decision. This does not authorize bulk ingestion of additional qualifications or subjects.

---

# Question / Learning Evidence rules

The invariant is:

```text
Immutable assessment evidence
        ≠
Mutable learner review state
        ≠
Derived learner mastery
```

Preserve canonical Question/QuestionPart identity across all assessment surfaces; preserve raw awarded/max marks, source/session provenance, attempt number, timing, confidence and AI execution metadata as applicable. Do not let UI clicks directly mutate mastery. Keep skipped/unattempted questions detectable. Review Hub, recommendations, learner KG state and teacher analytics consume the same evidence substrate.

Never implement the rejected brainstorming rules `flag → mastery -0.02`, `resolve → mastery +0.01`, or `self-doubt halves mastery gain` as deterministic learner arithmetic.

---

# RAG / Educational Retrieval rules

`RAG_RETRIEVAL_RESEARCH.md` is canonical for RAG/retrieval research. `ADR-020-EDUCATIONAL_RETRIEVAL_ENGINE.md` records the architecture direction.

## Core principle

SyllabAI must **not** become:

```text
PDF → arbitrary chunks → embeddings → vector DB → LLM
```

The retrieval layer must remain subordinate to the authoritative curriculum, educational KG, validated resources and learner evidence.

## Educational Retrieval Engine

The intended flow is:

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

### P0 — highest priority

- Hybrid lexical + semantic retrieval.
- Hierarchical curriculum-aware retrieval.
- Contextual metadata/headers.
- Reranking.
- Explainable evidence/citation chain.

### P1 — serious experiments

- Relevant Segment Extraction / local context reconstruction.
- Authoritative SyllabAI KG-aware retrieval.
- HyPE hypothetical learner-question aliases.
- Structured query transformation.
- Multimodal evidence extraction.

### P2 — later

- Contextual compression.
- CRAG.
- Self-RAG.
- Agentic retrieval.

### P3 — low priority / reference only

- RAPTOR.
- Generic GraphRAG as the knowledge architecture.
- Generic semantic chunking where it conflicts with curriculum structure.
- Wholesale RAGFlow/LightRAG/RAG-Anything adoption.

## Reranking rule

Do not stop at vector similarity. The long-term SyllabAI-aware rank should be able to consider:

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

Benchmark generic rerankers before adding model-specific complexity.

## Two graph layers

There are conceptually two different graph purposes:

**Authoritative Educational KG:** validated SpecificationPoints, concepts, prerequisites, misconceptions and educational relations. Governed by provenance/validation/promotion rules.

**Retrieval graph/view:** derived retrieval relationships such as `similar_to`, `co-occurs_with`, `supports`, `adjacent_to` and `retrieves`. These can be automatically generated, but they are **not educational truth**.

LightRAG/GraphRAG-style retrieval may traverse the authoritative SyllabAI graph, but it must not automatically create authoritative prerequisite or misconception edges.

This is especially important after T-C11: semantic similarity/co-occurrence is not evidence of pedagogical dependency. Held/rejected edges stay held/rejected unless explicitly promoted through the existing gate.

## HyPE rule

Hypothetical learner questions are retrieval aliases only. They must never become curriculum truth, assessment truth, or evidence. Generate them from validated resource/SpecificationPoint context, validate/deduplicate where practical, and retain model/version metadata.

## Citation rule

Prefer this provenance chain:

```text
Tutor claim
 → evidence segment
 → validated resource/version
 → SpecificationPoint
 → curriculum/specification source
```

Do not reduce a strong provenance chain to a generic vector-chunk citation.

## Learner-aware retrieval rule

Learner state is a retrieval/ranking signal, not a replacement for curriculum truth. Different learners may correctly receive different evidence for the same natural-language question because their prerequisite mastery or misconception state differs.

Do not create a second learner model inside RAG.

## Multimodal ingestion rule

RAG-Anything/MinerU/VLM/OCR-style extraction may be used as candidate document processing. Extracted text, equations, tables, diagrams and relationships remain candidate representations until the existing provenance/validation gates accept them.

## Infrastructure rule

PostgreSQL remains the system of record and pgvector remains the default vector layer. Do not add Neo4j, a separate vector database, RAGFlow or LightRAG solely to obtain a RAG feature that can be implemented behind existing contracts.

---

# External RAG repository guidance

### `NirDiamant/RAG_Techniques`

Use as a technique toolbox and benchmark source. Highest-value areas: hybrid/fusion retrieval, reranking, contextual enrichment, hierarchical retrieval, HyPE, relevant-segment extraction, query transformation and explainable retrieval. Do not blindly copy notebook architecture.

### `HKUDS/LightRAG`

Use for graph-aware retrieval, local/global retrieval ideas, candidate fusion, reranking and citation patterns. Do not use its retrieval graph as SyllabAI's authoritative educational KG.

### `HKUDS/RAG-Anything`

Use primarily as a multimodal ingestion/reference pattern for PDFs, tables, equations, figures, scans and heterogeneous educational documents. Parser/VLM output is not truth.

### `infiniflow/ragflow`

Use as an engineering reference for deep document understanding, multiple recall, fused reranking, metadata filtering, citation UX and retrieval operations. Do not make it the SyllabAI runtime or source of truth.

---

# Corpus-specific rules

The current 4CH1 validated corpus includes the T-C09/T-C10/T-C11 substrate. Important current facts:

- 182 SpecificationPoints.
- 112 revision notes.
- 209 final HUMAN_VALIDATED note → SpecificationPoint mappings.
- `4CH1-4.15` intentionally uncovered after semantic review.
- `4CH1-1.17` mapping rejected.
- T-C11 held/rejected candidates must not become retrieval expansion paths without explicit promotion.

Retrieval experiments must not manufacture coverage for an uncovered point through semantic similarity, generated HyPE aliases or inferred graph edges.

For corpus-side guidance see `syllabai-resources/RAG_RETRIEVAL_CORPUS_GUIDANCE.md`.

---

# Retrieval benchmark rule

Do not adopt RAG techniques based only on external README claims.

Use the real 4CH1 corpus and roughly 100–200 representative Tutor queries covering factual, conceptual, calculation, prerequisite, misconception, "why did I get this wrong?", exam, revision, vague-language and multi-SpecificationPoint requests.

Benchmark at minimum:

```text
semantic baseline
BM25
hybrid
hybrid + reranking
hierarchical + hybrid + reranking
context enrichment
HyPE
KG expansion
KG + HyPE + reranking + evidence selection
```

Measure:

- Recall@5/10/20;
- MRR;
- nDCG;
- SpecificationPoint resolution accuracy;
- evidence precision;
- false-positive rate;
- evidence sufficiency;
- citation correctness;
- unsupported-claim rate;
- p50/p95 latency;
- retrieval/indexing cost;
- LLM calls per query;
- storage overhead.

A technique becomes a default only after meaningful improvement without unacceptable latency, cost, complexity or educational-precision regression.

---

# Engineering rules

1. Preserve domain boundaries. UI does not own business rules; controllers do not own domain logic.
2. Prefer provider-neutral contracts: `KnowledgeGraphRepository`, `VectorStore`, `DocumentParser`, `ObjectStorage`, `LlmProvider`, `EmbeddingProvider`, `LearnerModel`, retrieval/reranking/evidence contracts.
3. Preserve provenance for every generated educational claim and AI-derived relation.
4. Record model/provider/prompt/version metadata wherever AI output matters.
5. Do not silently change scientific semantics. Consult the relevant research paper and decision record.
6. Do not introduce paid-only infrastructure under the free-tier constraint without an explicit decision.
7. Do not introduce microservices without a real runtime/lifecycle boundary.
8. Do not couple domain logic to OpenAI, Pinecone, Neo4j, MinerU, LightRAG, RAGFlow or another external implementation.
9. Do not copy external code/data across the license wall.
10. Treat external repositories as references behind SyllabAI contracts.
11. Retrieval work must not indefinitely block the pilot.

---

# Worklog / progress / TODO protocol

`WORKLOG.md` is chronological and append-only. Repeat important findings, mistakes and breakthroughs.

`PROGRESS.md` describes current state: repository status, subsystem state, architecture, latest findings, risks and next highest-value work.

`TODO.md` contains actionable tasks with IDs where useful, repository, priority, dependencies, status and acceptance criteria. Do not leave stale completed work.

The definitive spreadsheet remains the execution index. New capabilities must be represented there rather than only in prose.

---

# Coding workflow

```text
Understand task
  ↓
Locate feature in spreadsheet
  ↓
Read Master Spec / relevant architecture addenda
  ↓
Read RAG_RETRIEVAL_RESEARCH.md for retrieval/Tutor/content-intelligence work
  ↓
Read relevant research-paper section when scientific meaning changes
  ↓
Inspect existing code/tests
  ↓
Implement smallest coherent change behind existing contracts
  ↓
Run tests/static checks
  ↓
Verify behavior
  ↓
Update relevant docs/decisions
  ↓
Update WORKLOG
  ↓
Update PROGRESS
  ↓
Update TODO/spreadsheet state
```

Before finishing, ask:

- Did I preserve architecture and source-of-truth boundaries?
- Did I add/adjust tests?
- Did I preserve provenance?
- Did I introduce a new assumption requiring a research-paper check?
- If subject-scoped, did I preserve Board/Qualification/Subject/CurriculumVersion isolation?
- If curriculum-scoped, did I preserve official SpecificationPoint numbering and provenance?
- If question/evidence-scoped, did I preserve immutable evidence and canonical QuestionPart identity?
- If retrieval-scoped, did I avoid making embeddings or automatically inferred graph relations authoritative?
- If retrieval-scoped, did I record the benchmark configuration and failure cases?
- Did I update project-management state and documentation?

---

# Common mistakes to avoid

- Turning SyllabAI into a generic RAG chatbot.
- Letting vector similarity define educational truth.
- Letting GraphRAG/LightRAG-generated edges become authoritative prerequisites or misconceptions.
- Replacing the SyllabAI KG with a generic RAG graph.
- Adding Neo4j or another database solely for GraphRAG.
- Flattening SpecificationPoints into arbitrary chunks.
- Treating HyPE-generated questions as evidence or curriculum truth.
- Treating VLM/OCR/parser output as authoritative without validation.
- Creating a second learner model inside retrieval.
- Copying code from non-permissive reference repositories.
- Pulling Cycle-2+ features into Cycle 1.
- Coupling domain logic to external providers/frameworks.
- Putting important state on ephemeral Render storage.
- Exposing JPA entities directly through APIs.
- Treating frontend checks as authorization.
- Updating learner mastery directly from UI actions.
- Using one topic for multi-topic questions.
- Treating BKT as the complete learner model.
- Labeling students at risk without inspectable evidence.
- Presenting research hypotheses as validated facts.
- Introducing microservices without a genuine boundary.
- Adding paid infrastructure without an explicit decision.
- Updating code without updating project state and documentation.
- Letting retrieval research indefinitely postpone pilot delivery.
