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
6. `DATA_MODEL_ERD.md` for database/schema/entity-relationship work. **Treat its Current ERD as implementation evidence and its Target EERD as architecture; never silently present target-only entities as implemented.**
7. `TEACHER_ARCHITECTURE.md` for teacher/class/LMS/Test Builder/assignments/teacher analytics/teacher AI/class-KG work.
8. `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` and `LEARNING_EVIDENCE_AGENT_ADDENDUM.md` for question/attempt/assessment evidence/Smart Mark/review/recommendation/telemetry work.
9. `RAG_RETRIEVAL_RESEARCH.md` for retrieval, Tutor grounding, embeddings, reranking, graph retrieval, HyPE, evidence selection or multimodal-RAG work.
10. `RAG_RETRIEVAL_CORPUS_GUIDANCE.md` in `syllabai-resources` for corpus-side retrieval preparation.
11. Relevant research-paper sections whenever scientific constructs, hypotheses, operational definitions, metrics or learner-model semantics change.

The Master Spec is the engineering source of truth. Research papers remain authoritative for scientific claims. Named architecture addenda govern their specific layers. Do not silently resolve conflicts; record them and make/update the appropriate decision.

---

## Source hierarchy

1. Research papers — scientific claims, hypotheses, operational definitions and evaluation design.
2. `MASTER_SPEC.md` — engineering architecture and technology decisions.
3. Canonical architecture addenda — named architecture layers.
4. `DATA_MODEL_ERD.md` — current physical/logical data model versus canonical target EERD, for schema/entity decisions.
5. Definitive project spreadsheet — feature inventory and execution state.
6. `RAG_RETRIEVAL_RESEARCH.md` — canonical RAG/retrieval research and integration guidance.
7. `REPOSITORY_RESEARCH.md` — external implementation references and license decisions.
8. `DECISIONS.md` and ADR files — explicit architecture decisions.
9. `SUBJECT_ARCHITECTURE.md` — subject/specification-point architecture.
10. `TEACHER_ARCHITECTURE.md` — teacher/classroom architecture.
11. `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` and addendum — assessment evidence architecture.
12. `WORKLOG.md`, `PROGRESS.md`, `TODO.md` — living execution state/history.

---

## Project repositories

```text
syllabai                 main repo: spec, ADRs, backlog, research dossiers, papers
syllabai-web             Next.js 16 / React 19 / TypeScript frontend
syllabai-core            Java 25 / Spring Boot 4.1 / Spring AI 2.0 modular monolith
syllabai-parser          polyglot offline content pipeline
syllabai-pastpapers      canonical exam corpus: manifests, provenance, ledgers
Past-Papers              official QP/MS corpus source repository
syllabai-resources       validated revision/content corpus and corpus QA
syllabai-teacher-workbench teacher validation workbench / staged decision importer
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
