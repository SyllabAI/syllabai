# SyllabAI Master Technical Specification

**Document status:** Canonical project specification  
**Specification version:** 1.3.0 (Cycle-1 scope revision, 2026-09-11 — ADR-019: the Cycle-1 pilot subject moves from Edexcel IAL Chemistry to Edexcel International GCSE Chemistry (4CH1); §39a Subject bullet rewritten, all other architecture content unchanged from v1.2.1)  
**Research date:** 2026-09-02  
**Project:** SyllabAI  
**Academic context:** Advanced Object Oriented Programming (Java backend)  
**Primary domain:** IGCSE/IAL exam preparation in the Bangladesh English-medium context  

---

## 0. Purpose of this document

This is the **operational source of truth for SyllabAI engineering**. It consolidates the approved architectural direction from the SyllabAI system-design paper, the conceptual/diagnostic framework, the repository research, the feature backlog, and the technology decisions made for the project.

The two research papers remain authoritative for scientific claims, hypotheses, operational definitions, pre-registrations, and research-methodology details. This specification translates those ideas into an implementable software architecture. Agents should therefore read this document first and return to the papers whenever a task changes a research construct, measurement definition, scientific hypothesis, learner-model assumption, or evaluation protocol.

### Authoritative source hierarchy

1. **Current research papers** - authority for scientific framing, hypotheses, operational definitions, and research claims.
2. **This Master Technical Specification** - authority for the current software architecture and engineering decisions.
3. **Canonical architecture addenda** (`SUBJECT_ARCHITECTURE.md`, `TEACHER_ARCHITECTURE.md`, `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md`, `RECOMMENDATION_SYSTEM_ARCHITECTURE.md`, `MOCK_EXAM_GENERATOR_ARCHITECTURE.md`, with ADR-014–ADR-018 in `DECISIONS.md`) - authority for their named architecture layers. Where this spec and an addendum disagree, the addendum governs for its layer; record the discrepancy in `WORKLOG.md` and fold it back at the next controlled spec revision.
4. **Definitive project spreadsheet** - authority for feature inventory, dependencies, implementation status, priority, owner, and execution tracking.
5. **Repository Research Dossier** - implementation-reference knowledge about external/open-source projects.
6. **AGENT.md** - operating procedure for coding agents and maintenance rules.
7. **Worklog / Progress / TODO / Decisions** - living project state and history.

If these sources disagree, do not silently resolve the conflict. Record the discrepancy in `WORKLOG.md`, update `DECISIONS.md` if a decision is required, and escalate the relevant scientific question to the papers before changing research semantics.

---

# 1. Product definition

SyllabAI is a syllabus-grounded, adaptive learning and examination-preparation platform designed to model not only what a student knows, but also why the student struggles and what intervention is appropriate.

The system is not defined as a generic "chat with PDF" application. Its defining loop is:

```text
Official curriculum + assessment evidence
                ↓
        Structured knowledge
                ↓
     Prerequisite / concept graph
                ↓
         Learner state model
                ↓
    Diagnosis of weakness/struggle
                ↓
       Targeted intervention
                ↓
          Assessment again
                ↓
          Learner update
                ↓
        Next best learning step
```

Paper A defines the conceptual model as **Content Knowledge × Exam Literacy × Learning Strategy × Self-Regulation**, with six struggle types. Paper B operationalizes the framework through a syllabus knowledge graph, proficiency overlay, KA-RAG chatbot/Smart Mark, and learning log.

---

# 2. Non-negotiable design constraints

## 2.1 Backend

- **Java 25** target.
- **Spring Boot 4.1.x**.
- **Spring AI 2.0.x** as the AI application framework (chat/embedding abstraction, pgvector support, OpenAI-compatible endpoints).
- Maven build.
- Spring Security.
- JPA/Hibernate + explicit SQL/native queries where needed.
- Flyway database migrations.
- Modular monolith architecture.

Spring Boot 4.1.1 currently requires Java 17+ and supports through Java 26; Java 25 is therefore the selected baseline. Spring Boot 3.x reached end of life on 2026-06-30, and Spring AI 2.0 GA (2026-06-12) requires Spring Boot 4.x — do not start new code on Boot 3.x. Sources: https://docs.spring.io/spring-boot/system-requirements.html and https://spring.io/blog/2026/06/12/spring-ai-2-0-0-GA-available-now

## 2.2 Frontend

- **Next.js 16.x + React 19.x + TypeScript**.
- Hosted on **Vercel**.
- The Next.js application is the web experience, not the Java backend.
- Browser-to-backend communication uses HTTPS to the Spring Boot API.

## 2.3 Database

- **Neon PostgreSQL** as the default hosted relational database.
- PostgreSQL is the system of record.
- **pgvector** is the default vector-search layer.
- The knowledge graph is initially represented through PostgreSQL relational graph tables and recursive queries.
- Graph and vector implementations must be abstracted behind interfaces so Neo4j, HelixDB, Zvec, Weaviate, or another provider can be substituted later.

Neon's current free plan is $0 and advertises no credit-card requirement, with a bounded compute/storage allowance. Source: https://neon.com/pricing

## 2.4 Deployment

- **Vercel**: Next.js frontend.
- **Render** (Docker): Spring Boot backend while the project operates under the no-credit-card / free-tier constraint.
- No production-critical files are stored on the backend filesystem.
- External object storage is used for large binaries.

Render's current free web services support Docker, but free services spin down after 15 minutes of inactivity, have finite monthly instance hours, and have ephemeral filesystems. Treat this as an academic/free deployment tier, not the final always-on production SLA. Source: https://render.com/docs/free and https://render.com/docs/docker

## 2.5 Cost policy

The default deployment target is designed to operate at **$0 total cost** within free-tier limits and without requiring a credit card — **including LLM inference**. The default provider chain (section 26.1) runs on verified free tiers: Groq (primary) → Gemini 2.5 Flash (fallback) → OpenRouter free models (tertiary). Paid providers remain allowed behind `LlmProvider` for experiments that require them, but no Cycle-1 feature may hard-depend on a paid-only provider.

Never introduce a paid-only infrastructure dependency when an equivalent free/open-source path exists without documenting the tradeoff in `DECISIONS.md`.

---

# 3. Repository architecture

SyllabAI is a multi-repository project. Repositories are separated only where a component has an independent responsibility, lifecycle, runtime, language, test strategy, or deployment model.

```text
SyllabAI GitHub account (github.com/SyllabAI) — 8 repositories (ADR-012 amended 2026-09-03: the public `Past-Papers` corpus repo joins `syllabai` (control), `syllabai-core`, `syllabai-web`, `syllabai-parser`; amended 2026-09-13: the content-ops repositories `syllabai-pastpapers` + `syllabai-resources` complete the then-7-repo set; amended 2026-09-15: `syllabai-teacher-workbench` (teacher validation workbench: staged decision importer, evidence packs, release/verification tooling) joins as the 8th repository — the README repo map is the authoritative list)
│
├── syllabai  (this repo — the "main repo")
│   └── master project pack: spec, ADRs, backlog, research dossiers, papers
│
├── syllabai-web
│   └── Next.js 16 / React 19 / TypeScript frontend (Vercel)
│
├── syllabai-core
│   └── Java 25 / Spring Boot 4.1 / Spring AI 2.0 modular monolith
│       modules: identity, curriculum, knowledge, content, assessment,
│       smartmark, learner (BKT/BDT/decay), tutor (KA-RAG), diagnostic,
│       recommendation, teacher, research/telemetry, infrastructure
│
├── syllabai-parser
│   └── polyglot offline content pipeline: Java in-process
│       (opendataloader-pdf via Maven) + Python/Rust offline engines
│       (MinerU / Surya / anydoc / pdf-inspector)
│
├── syllabai-pastpapers  (public)
│   └── canonical exam-material corpus: manifests, SHA-256 provenance,
│       ledgers + Python ingestion tooling
│
├── syllabai-resources  (public)
│   └── RAG revision-note corpus + T-C09/T-C11 mapping/graph QA +
│       Python governance scripts
│
├── syllabai-teacher-workbench  (public)
│   └── teacher validation workbench: staged decision importer,
│       evidence packs, release/verification tooling
│
└── Past-Papers  (public, 689 MB)
    └── official content corpus: Edexcel IAL/IGCSE past papers +
        mark schemes (QP/MS PDFs) — ingestion source for T-010/T-011;
        licensing: pilot use under institution/own-use terms
        (ADR-013 posture; re-check before any redistribution)
```

The former `syllabai-knowledge` / `-assessment` / `-learner-model` / `-ai` / `-research` / `-infrastructure` repositories from spec v1.0 are **modules inside `syllabai-core`**. They graduate to separate repositories only when a genuine runtime/lifecycle boundary appears (ADR-012). Polyglot policy (ADR-011): languages other than Java are welcome where they are clearly better — OCR/ML parsing tooling (Python/Rust) and the web frontend (TypeScript) — but the domain core stays Java.

### Important boundary

`syllabai-core` remains a **modular monolith**, not a set of microservices. Internal modules are strongly separated but deployed together. The parser and specialist processing engines are separated because their runtime/ecosystem needs differ materially from the Java application.

---

# 4. System architecture

```text
                    ┌───────────────────────────┐
                    │        syllabai-web        │
                    │       Next.js / React      │
                    └─────────────┬─────────────┘
                                  │ HTTPS
                                  ▼
                    ┌───────────────────────────┐
                    │       syllabai-core        │
                    │ Java 25 / Spring Boot      │
                    │ Modular Monolith           │
                    └─────────────┬─────────────┘
                                  │
       ┌──────────────────────────┼──────────────────────────┐
       ▼                          ▼                          ▼
 Assessment module         Learner/Diagnosis           Tutor/AI modules
 (bounded context          modules (bounded             (bounded context
  inside core)              contexts inside core)        inside core)
       │                          │                          │
       └──────────────────────────┼──────────────────────────┘
                                  ▼
                       Knowledge / Data Layer
                                  │
              ┌───────────────────┼──────────────────┐
              ▼                   ▼                  ▼
         PostgreSQL             pgvector          Object Storage
           (Neon)                                    │
                                  │                  │
                                  └─────────┬────────┘
                                            ▼
                                   Content intelligence
                                            │
                              syllabai-parser / parsers
                                            │
                         MinerU / OpenDataLoader / Surya /
                               anydoc / pdf-inspector
```

The three labels above the data layer (`Assessment module`, `Learner/Diagnosis modules`, `Tutor/AI modules`) are **bounded-context modules inside `syllabai-core`**, not separate repositories — ADR-012 consolidated the former `syllabai-assessment` / `syllabai-learner-model` / `syllabai-ai` spec-v1.0 repositories as modules of the monolith. The current repository set is `syllabai`, `syllabai-core`, `syllabai-web`, `syllabai-parser`, the content-ops repositories `syllabai-pastpapers` and `syllabai-resources`, plus the public `Past-Papers` corpus repository (section 3). Never describe internal modules as deployable repositories.

---

All AI calls flow through `LlmProvider` / `EmbeddingProvider` ports; the default implementation is the free-tier chain Groq → Gemini 2.5 Flash → OpenRouter (section 26.1). Binary sources live in object storage (Cloudflare R2 free tier, no credit card), never on the Render filesystem.

# 5. Major architectural layers

## 5.1 Experience layer

Student, teacher, administrator, and later parent/school experiences.

Long-term product shape (ADR-014/015): a student starts with zero subjects and enrolls via `Board → Qualification → Subject → Curriculum/Specification Version`; each enrolled subject opens a self-contained workspace (dashboard, revision notes, exam questions, past papers, flashcards, Target Test, mock exams, Smart Lesson, tutor, knowledge graph — F-164/F-165). Class-enrolled students see Announcements/Assignments/My Results in the same workspace. Teachers get a subject-scoped workspace over the same substrate (section 6.10).

## 5.2 Application layer

Use-case orchestration, commands, queries, authorization, transactions.

## 5.3 Domain layer

Curriculum, knowledge, assessment, learner state, diagnostic inference, tutoring, recommendation, research concepts.

## 5.4 Infrastructure layer

PostgreSQL, pgvector, object storage, email, LLM providers, document parsers, external APIs, observability.

## 5.5 Research layer

Telemetry, experiment assignment, calibration, evaluation datasets, model/prompt version tracking, reproducibility metadata.

---

# 6. Core bounded contexts / modules

## 6.1 Identity and access

Entities:
- User
- StudentProfile
- TeacherProfile
- AdminProfile
- Organization/School
- Role
- Permission
- Session
- ConsentRecord

Responsibilities:
- registration/login
- verification
- password recovery
- MFA
- RBAC
- school/teacher/student membership
- session revocation
- consent and deletion/export workflows

## 6.2 Curriculum

Entities:
- Board
- Qualification
- Subject
- CurriculumVersion (SpecificationVersion)
- Unit / Section
- Topic
- SubTopic
- SpecificationPoint

The canonical hierarchy is `Board → Qualification → Subject → CurriculumVersion → Unit/Section → Topic/SubTopic → SpecificationPoint` (ADR-014). A `SpecificationPoint` is the first-class anchor for the official numbered learning objectives of a board specification (e.g. `1.1`, `1.2`): it preserves the official code, verbatim objective statement, ordering, curriculum version, source provenance, and applicability metadata; agents must never flatten points into generic tags or invent numbering. The v1.1 term `LearningObjective` is a **legacy alias** of `SpecificationPoint` — existing code and migrations may keep the older name, but both must never appear as competing canonical entities.

Relationships:
- PART_OF
- REQUIRES_PREREQUISITE
- RELATED_TO
- SUPERSEDES
- MAPS_TO_STANDARD

## 6.3 Knowledge

Entities:
- KnowledgeNode
- KnowledgeRelation
- Misconception
- Resource
- Evidence
- DocumentElement
- ConceptDefinition
- Example
- CounterExample

Responsibilities:
- graph traversal
- provenance
- concept linking
- misconception mapping
- resource linking

## 6.4 Content

Entities:
- Document
- DocumentVersion
- DocumentSource
- DocumentElement
- Page
- Section
- Table
- Figure
- Equation
- MediaResource

Responsibilities:
- ingestion
- versioning
- canonical document representation
- provenance
- parsing-status management

## 6.5 Assessment

Entities:
- Question
- QuestionVersion
- QuestionPart
- MarkScheme
- MarkPoint
- ExamPaper
- ExamSession
- Assessment
- Attempt
- Answer
- SmartMarkResult
- HumanMark

**Blueprint-driven mock-exam principle (ADR-018, 2026-09-07):** the Mock Exam Generator is a versioned exam-blueprint engine scoped by `Board → Qualification → Subject → CurriculumVersion → PaperCode → PaperType/Variant → BlueprintVersion`, not an LLM-writes-an-exam prompt. Blueprints keep official board rules and historical corpus patterns as separately provenance-bearing evidence classes (F-051, extended); paper assembly draws only validated Question/QuestionPart candidates and AssessmentBlock groupings where shared stems/data/diagrams create atomic semantics (F-171/F-172); hard validity constraints are enforced separately from soft optimization objectives and a scalar fidelity score can never hide a hard failure (F-173); Exam Simulation and Adaptive Diagnostic Mock are explicit policies in which blueprint validity stays a hard floor while learner evidence may guide valid item selection (F-174); AI-generated variants pass a gated source→generation→deterministic/domain validation→mark-scheme validation→review→servable pipeline and are never canonical board truth (F-175, Cycle 2+); mock attempts reuse the existing Learning Evidence subsystem with no parallel attempt ledger, and predicted grades remain research outputs until a validated model exists (F-176). Difficulty is contextual evidence; universal `marks × 1.5 minutes` timing is rejected. Canonical design: `MOCK_EXAM_GENERATOR_ARCHITECTURE.md`.

## 6.6 Learner model

Entities:
- LearnerState
- SkillState
- MisconceptionState
- ExamLiteracyState
- ProceduralFluencyState
- StrategyState
- SelfRegulationState
- ConfidenceObservation
- ReviewSchedule

## 6.7 Diagnosis

Entities:
- DiagnosticObservation
- StruggleInference
- DiagnosticEvidence
- InterventionRecommendation
- TeacherOverride

Six top-level struggle types:
1. Prerequisite gap
2. Surface engagement
3. Exam literacy
4. Metacognitive
5. Motivational
6. Instructional environment

Research-proposed subtypes:
- Type 3a exam-literacy knowledge/mark-scheme language
- Type 3b procedural fluency/timed performance
- Type 5a internal/self-efficacy
- Type 5b circumstantial/competing demands

Paper A explicitly treats Type 6 as an environment-side phenomenon that may be revised from a peer type into a moderator in later empirical cycles.

## 6.8 Tutor

Responsibilities:
- question understanding
- learner-state inspection
- diagnosis-aware intervention selection
- knowledge-grounded generation
- Socratic dialogue
- worked examples
- explanation
- verification
- transfer questions
- learning-loop completion

## 6.9 Recommendation

Candidate sources:
- prerequisites
- mastery
- misconceptions
- timed/untimed gap
- assessment history
- exam readiness
- learning-strategy state
- engagement signals
- content preferences
- population-level signals

The final system supports a layered recommender rather than a single algorithm.

**Learning-first principle (ADR-017, 2026-09-07):** recommendations maximize expected learning progress and appropriate syllabus coverage under subject/curriculum, validation, authorization, prerequisite and teacher constraints — never engagement. Rule-based candidates are the canonical baseline (F-087); content-based similarity only expands candidates (F-088); collaborative filtering is a later experiment that can never override hard pedagogical constraints (F-089); the long-term architecture is a hybrid cascade — hard constraints → rule candidates → content-based expansion → optional learned ranking → constrained exploration → explainable next-best action (F-090). Recommendations are actions, not just resources (F-092); every recommendation carries structured evidence-backed reason codes (F-093); LLMs never invent learner statistics or causal explanations. The old hard-coded 10% random epsilon-greedy exploration rule is rejected as a product rule; educational video discovery and watch telemetry are redesigns under the same decision (F-025/F-026). Canonical design: `RECOMMENDATION_SYSTEM_ARCHITECTURE.md`.

## 6.10 Teacher intelligence

Responsibilities:
- class heatmaps
- learner diagnostic summaries
- syllabus coverage
- early warning
- intervention recommendations
- assignment/test creation
- Smart Mark review
- teacher overrides
- professional development recommendations

**Teacher/classroom LMS layer (ADR-015, 2026-09-07):** the long-term product adds a role-specific teacher layer over the **same** subject graph, question bank, evidence and learner-model substrate used by students — never a second curriculum or parallel graph. Teachers are subject-scoped (teacher workspace per taught subject); class-enrolled students keep one identity/learner state and gain Announcements/Assignments/My Results inside the same subject workspace. The teacher KG is a different lens over one shared graph: a teaching-coverage overlay (`NOT_TAUGHT` is semantically distinct from `LOW_MASTERY` — grey nodes mean absent teaching coverage, not weak understanding) plus class-level aggregation with drill-down from class node → affected students → individual graph → evidence → action. The Teacher AI Assistant (grounded academic/content copilot) and the Data Assistant (authorized structured analytics that never invents counts, marks, dates, or risk labels) are separate systems. At-Risk Students is evidence-first: every flag exposes contributing evidence, time window, and rule/model version (F-073 + TFA-08). The existing F-050 Test Builder remains the canonical test-creation identity; the new requirement is an evidence-driven enhancement (TFA-06), not a duplicate feature. `T-029` is the current minimal teacher review surface — its Cycle-1 enabled-STUDENT cohort roster is a pilot shortcut, not the final Class domain model (future class management introduces the explicit class/membership model with authorization boundaries). Canonical blueprint: `TEACHER_ARCHITECTURE.md`; tracker rows: `backlog/teacher-lms-feature-addendum.tsv` (TFA-01…TFA-08, synced into the master workbook 2026-09-07). This layer is long-term architecture and does not expand Cycle 1.

## 6.11 Research

Responsibilities:
- event capture
- cohort assignment
- experiment registry
- model/prompt versioning
- ground-truth collection
- evaluation pipelines
- reproducible exports

---

# 7. Knowledge graph specification

The canonical educational hierarchy is (ADR-014):

```text
Board
  └── Qualification
       └── Subject
            └── CurriculumVersion / SpecificationVersion
                 └── Unit / Section
                      └── Topic
                           └── SubTopic
                                ├── SpecificationPoint
                                ├── Misconception
                                ├── Question
                                └── Resource
```

`SpecificationPoint` is the canonical fine-grained curriculum entity (the spec-v1.1 term `LearningObjective` is a legacy alias — keep at most one canonical entity in code and docs). Resources, questions, learner evidence and adaptive surfaces map to SpecificationPoints; learner state (mastery, misconceptions, confidence, fluency, review) is a separate time-aware **overlay** on this stable graph and never mutates official curriculum nodes. The subject-first student product (subject enrollment → subject workspace; F-164/F-165) and the teacher lens (section 6.10) are both built over this one shared graph.

Minimum edge types:

```text
PART_OF
REQUIRES_PREREQUISITE
RELATED_TO
TESTED_BY
MISCONCEPTION_OF
EXPLAINED_BY
REMEDIATED_BY
```

Every edge should have:
- source_node_id
- target_node_id
- relation_type
- strength/confidence where applicable
- provenance
- rationale
- created_by
- validation_status
- version

Prerequisite relationships suggested algorithmically must be distinguishable from SME-validated relationships.

---

# 8. Canonical document format

`syllabai-parser` must output a repository-independent normalized format.

```json
{
  "documentId": "uuid",
  "version": 1,
  "source": {
    "uri": "...",
    "checksum": "...",
    "mimeType": "application/pdf"
  },
  "pages": [],
  "sections": [],
  "textBlocks": [],
  "tables": [],
  "figures": [],
  "equations": [],
  "provenance": {}
}
```

Every extracted element should support:
- element_id
- page_number
- bounding_box if available
- text
- element_type
- reading_order
- confidence
- source_engine
- source_engine_version

This prevents SyllabAI from being coupled to MinerU, Surya, OpenDataLoader, anydoc, or another parser.

---

# 9. Content-processing architecture

```text
Source
  ↓
Ingestion API
  ↓
pdf-inspector / document classifier
  ↓
route
  ├── clean text → anydoc / OpenDataLoader
  ├── complex PDF → MinerU / OpenDataLoader hybrid
  ├── OCR/layout → Surya
  └── specialized long OCR → Unlimited-OCR
  ↓
Canonical Document Format
  ↓
semantic extraction
  ↓
knowledge graph / question bank / retrieval index
```

The parser must support provider adapters and keep original sources plus normalized output.

---

# 10. Question-bank specification

Questions must support multiple topic relationships.

Minimum metadata:

```text
board
qualification
subject
paper
session
question_number
part_number
marks
command_word
difficulty
primary_topic
secondary_topics[]
specification_points[]
prerequisites[]
misconceptions[]
mark_points[]
expected_time_seconds
question_type
provenance
version
```

The system must not force a multi-topic question into one topic. Secondary mappings are first-class.

**Specification-point mapping (ADR-014 / F-168):** `QuestionVersion` / `QuestionPart` may map to one or more `SpecificationPoint`s, preserving multi-point coverage, mapping confidence, provenance, and validation state — unreviewed/suggested mappings never become authoritative. Topic-level placement (above) remains valid and is extended, not replaced, by point-level mapping.

---

# 11. Learner state specification

Persisted learner state is not one score.

```text
Learner
│
├── Skill mastery (BKT)
├── Misconception probabilities (BDT)
├── Exam literacy
├── Procedural fluency
├── Learning strategy
├── Self-regulation
├── Confidence
├── Engagement
├── Intervention history
└── Review schedule
```

## BKT

The research design currently specifies:
- initial knowledge L0 = 0.1
- slip = 0.1 initial default
- guess = 0.25 initial default
- learning rate T = 0.1 initial default
- monthly parameter recalibration
- forgetting decay applied nightly
- tau 30/90/365 days by proficiency band

These are research-design parameters and should be configurable/versioned rather than hard-coded throughout application code.

## BDT

Tracks misconception-specific probabilities and is driven by diagnostic evidence such as question distractors, answer patterns, and observed errors.

---

# 12. Assessment-to-learner evidence contract

Assessment must emit evidence rather than mutating learner state directly.

```text
AssessmentAttempt
      ↓
AssessmentEvidence
      ├── correctness
      ├── score
      ├── marks lost
      ├── response time
      ├── confidence
      ├── misconception evidence
      ├── timed/untimed context
      └── provenance
      ↓
LearnerModel.update(evidence)
```

This keeps assessment, learner modeling, and research instrumentation decoupled.

**Question Attempt & Learning Evidence subsystem (ADR-016, 2026-09-07):** F-055 is promoted to a foundational evidence subsystem with the invariant

```text
Immutable assessment evidence  ≠  Mutable learner review state  ≠  Derived learner mastery
```

Canonical `Question`/`QuestionPart` identity is preserved across Past Papers, Target Tests, Test Builder, Mock Exams, teacher assignments and Smart Lessons; normal submissions and Smart Mark attempts auto-log as evidence (with AI execution metadata kept separate from human overrides); `awardedMarks`/`maximumMarks` are preserved, not only percentages; skipped/unattempted parts stay detectable even when a paper session is marked complete; problematic/doubt/self-doubt/resolved flags are mutable review state around immutable attempts — evidence, never deterministic mastery arithmetic (the old `flag → -0.02` / `resolve → +0.01` / "self-doubt halves mastery gain" rules are rejected). Review Hub, spaced review, recommendations, KG inference and teacher analytics all consume this one evidence substrate — no parallel tracking models. Full contract: `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md`.

---

# 13. KA-RAG specification

The current SyllabAI research architecture is knowledge-augmented retrieval rather than vector-only RAG.

```text
Student Query
    ↓
Intent / entity extraction
    ↓
Knowledge-graph query
    ↓
Prerequisite / concept context
    ↓
Vector + lexical retrieval
    ↓
Evidence fusion / reranking
    ↓
Grounded context
    ↓
Tutor generation
    ↓
Citation / provenance
```

Retrieval interfaces:

```java
public interface RetrievalStrategy {}
public interface VectorStore {}
public interface KnowledgeGraphRepository {}
public interface Reranker {}
```

Implementations remain replaceable.

---

# 14. Tutor policy

The tutor is learner-state-aware.

It should never treat every query as a generic answer-generation task.

Decision path:

```text
Question
  ↓
Learner state
  ↓
Question/context classification
  ↓
Relevant knowledge
  ↓
Potential struggle/misconception
  ↓
Intervention selection
  ↓
Response
  ↓
Understanding check
  ↓
Variation/transfer
```

Behavioral principles may be informed by SocraticLM and Scientific Learning Skills, while DeepTutor is an architectural reference rather than a mandatory dependency.

---

# 15. Smart Mark architecture

Smart Mark is an explainable assessment subsystem.

```text
Student Answer
  ↓
Answer normalization
  ↓
Question decomposition
  ↓
Mark-scheme decomposition
  ↓
Evidence-to-mark-point alignment
  ↓
Partial-credit evaluation
  ↓
Misconception detection
  ↓
Score + explanation + confidence
  ↓
Teacher review / override
```

Persist:
- AI mark
- human mark where available
- difference
- evidence
- mark points
- model/version
- prompt/version
- reviewer
- override reason

This supports the Smart Mark calibration dataset described in Paper B.

---

# 16. Timed vs untimed assessment

The system must support two comparable assessment conditions.

```text
Untimed performance
vs
Timed performance
```

Derived metric:

```text
procedural_fluency_gap = untimed_performance - timed_performance
```

The paper uses this comparison to separate Type 3a exam-literacy/knowledge issues from Type 3b procedural fluency. This is a research construct and must remain versioned/configurable.

---

# 17. Struggle inference engine

The system should evolve toward:

```text
Telemetry
  ↓
Feature extraction
  ↓
Diagnostic model
  ↓
Struggle probabilities
  ↓
Evidence explanation
  ↓
Recommended intervention
```

Every inference should store:
- inference_id
- learner_id
- type
- subtype
- probability/confidence
- supporting evidence
- model version
- generated timestamp
- expiry/reassessment policy
- teacher override if any

Avoid ungrounded black-box "at-risk" labels.

---

# 18. Research / telemetry architecture

The learning log is an intentional research instrument.

Minimum event families:

```text
session.started
session.ended
question.opened
question.started
question.submitted
confidence.submitted
markscheme.viewed
smartmark.completed
bkt.updated
bdt.updated
recommendation.generated
intervention.started
intervention.completed
chat.started
retrieval.completed
citation.emitted
teacher.override.created
```

Each event should support:
- event_id
- learner_id
- session_id
- timestamp
- topic_id
- question_id when relevant
- model_version when relevant
- prompt_version when relevant
- application_version
- source_version
- metadata

Raw telemetry should be append-only and transformed into analytics tables/views rather than overwritten.

---

# 19. Research reproducibility requirements

Every AI-mediated research outcome must be attributable to:

```text
model provider
model name/version
prompt version
retrieval version
KG version
question version
parser version
application version
experiment/cohort
```

Maintain:
- Experiment Registry
- Dataset Registry
- Model Registry
- Prompt Registry
- KG Version Registry
- Evaluation Runs

The project must not silently switch model versions for a registered experiment.

---

# 20. Security and privacy

Minimum requirements:

- TLS/HTTPS everywhere.
- Strong password hashing.
- Secure session management.
- RBAC on every protected operation.
- Server-side authorization; frontend role UI is not sufficient.
- Input validation and output encoding.
- CSRF/XSS protections where applicable.
- Rate limiting.
- Audit logging.
- Secrets only through environment/secret stores.
- No credentials in repositories.
- No source documents on ephemeral server filesystems.
- Account deletion and export workflows.
- Minor/guardian consent workflows before real pilot use.
- Research identifiers separated from direct PII where possible.
- Minimum-necessary telemetry.
- Retention policies.

The papers discuss data protection and explicitly position teacher augmentation rather than teacher replacement as the intended deployment posture.

---

# 21. Accessibility

Accessibility is a product and agent design requirement, not merely a CSS checklist.

Target baseline:
- WCAG 2.1 AA.
- Keyboard navigation.
- Screen-reader semantics.
- Sufficient non-color cues.
- Accessible charts/graphs.
- Reduced motion support.
- Readable equation rendering.
- Captions/transcripts for audio/video.
- Cognitive-load-sensitive interfaces.

A11Y.md is an implementation/reference resource for this layer.

---

# 22. API architecture

Base path:

```text
/api/v1
```

Domains should be organized by resource/use case rather than one giant controller.

Examples:

```text
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout

GET    /api/v1/curriculum/subjects
GET    /api/v1/curriculum/topics/{id}
GET    /api/v1/curriculum/topics/{id}/prerequisites

POST   /api/v1/documents
GET    /api/v1/documents/{id}
POST   /api/v1/documents/{id}/process

GET    /api/v1/questions
GET    /api/v1/questions/{id}
POST   /api/v1/assessments
POST   /api/v1/attempts
POST   /api/v1/attempts/{id}/submit

GET    /api/v1/learners/me/state
GET    /api/v1/learners/me/knowledge-graph
GET    /api/v1/learners/me/recommendations

POST   /api/v1/tutor/query
GET    /api/v1/tutor/sessions/{id}
GET    /api/v1/tutor/sessions/{id}/stream

POST   /api/v1/teacher/classes
GET    /api/v1/teacher/students/{id}/diagnostics
POST   /api/v1/teacher/interventions

POST   /api/v1/research/events
GET    /api/v1/research/experiments
```

Use DTOs at API boundaries. Do not expose JPA entities directly.

---

# 23. OOP architecture requirements

The Java implementation should visibly demonstrate sound object-oriented design.

Required patterns/concepts where appropriate:

- encapsulation
- abstraction
- inheritance only when domain semantics justify it
- composition over inheritance when possible
- interfaces and dependency inversion
- Repository Pattern
- Strategy Pattern
- Factory/Provider Pattern
- Specification Pattern where useful
- Adapter Pattern for external providers
- Observer/event patterns for telemetry
- Command/Query separation where beneficial

Examples:

```java
public interface LearnerModel {
    LearnerState update(Learner learner, Evidence evidence);
}

public interface AssessmentStrategy {
    AssessmentResult evaluate(AssessmentContext context);
}

public interface KnowledgeGraphRepository {
    List<KnowledgeNode> findPrerequisites(UUID nodeId);
}

public interface LlmProvider {
    LlmResponse generate(LlmRequest request);
}
```

Avoid creating classes solely to demonstrate textbook OOP. Classes should represent meaningful responsibilities.

---

# 24. Database design principles

PostgreSQL is the system of record.

Use:
- normalized relational tables for transactional data
- JSONB for bounded extensibility, not arbitrary database blobs
- foreign keys and check constraints
- optimistic locking where needed
- explicit indexes on query paths
- pgvector indexes for semantic retrieval
- database migrations through Flyway

Knowledge graph tables should be explicit and queryable.

Suggested core tables:

```text
users
roles
user_roles
schools
school_memberships
consents
sessions

curriculum_versions
subjects
units
topics
subtopics
knowledge_nodes
knowledge_edges
misconceptions

sources
documents
document_versions
document_pages
document_elements

questions
question_versions
question_topics
question_misconceptions
mark_schemes
mark_points
exam_papers
exam_sessions

assessments
assessment_items
attempts
answers
smart_mark_results
human_marks

learner_states
skill_states
misconception_states
confidence_observations
review_schedules
interventions
recommendations
struggle_inferences

telemetry_events
experiments
cohorts
model_versions
prompt_versions
evaluation_runs
teacher_overrides
```

---

# 25. Object storage

Large binary content must be external to PostgreSQL.

Use an `ObjectStorage` interface.

Possible implementations:
- Cloudflare R2
- Supabase Storage
- S3-compatible storage
- local development filesystem

Cloudflare R2 currently advertises a free monthly tier including 10 GB-month standard storage, 1 million Class A operations, 10 million Class B operations, and free egress. Source: https://developers.cloudflare.com/r2/pricing/

For academic deployment, use the simplest available storage and keep the adapter provider-neutral.

---

# 26. AI provider abstraction

Never place provider-specific API calls inside domain services.

```text
LlmProvider
EmbeddingProvider
Reranker
SpeechProvider
VisionProvider
```

Possible implementations:
- OpenAI
- Anthropic
- Google Gemini
- OpenRouter
- Ollama/local models

Research experiments must record provider/model/version.

## 26.1 Free-tier provider chain (default)

The default chain satisfies the $0 / no-credit-card constraint (verified 2026-09, details in `PLATFORM_RESEARCH.md`):

1. **Groq — `llama-3.3-70b-versatile` (primary).** Free tier, no credit card, OpenAI-compatible API. Verified 2026-09 limits: ~30 req/min, ~14,400 req/day, 30K tokens/min. Connect via Spring AI's OpenAI client pointed at the Groq base URL.
2. **Google Gemini 2.5 Flash (fallback).** Free tier (~10 RPM / ~250 RPD class; volatile — re-verify at build time). Native Spring AI Gemini client.
3. **OpenRouter free models (tertiary).** ~50 RPD on the no-card tier.

Failover is automatic on error/rate-limit, with health and rate-budget tracking per provider. **Per-experiment pinning:** a registered experiment records provider+model+version and must not silently drift between providers mid-experiment. **Embeddings:** Gemini embedding API free tier is the primary `EmbeddingProvider`; embedding dimension/model is recorded alongside vector rows.

At 50 students × ~20 tutor queries/day, the pilot fits comfortably inside Groq's free daily budget; Smart Mark batch runs are queued off-peak.

---

# 27. Document parser abstraction

```text
DocumentParser
 ├── MinerUParser
 ├── OpenDataLoaderParser
 ├── SuryaOcrParser
 ├── AnyDocParser
 ├── GlmOcrMarkdownParser
 └── PdfInspectorRouter
```

The parser repository may be Python/Rust/etc. The application contract remains language-neutral.

---

# 28. Final technology-to-function mapping

| Function | Preferred implementation/reference |
|---|---|
| Web UI | Next.js / React / TypeScript |
| Application backend | Java 25 / Spring Boot 4.1 |
| Relational DB | Neon PostgreSQL |
| Vector search | pgvector |
| Knowledge graph | PostgreSQL graph tables initially |
| Document parsing | MinerU / OpenDataLoader |
| OCR/layout | Surya |
| PDF routing | pdf-inspector |
| Office document conversion | anydoc |
| Knowledge extraction | Hyper-Extract patterns |
| Curriculum taxonomy | Marble taxonomy patterns |
| Semantic compression | Blockify patterns |
| Agent skill packaging | book-to-skill patterns |
| Socratic teaching | SocraticLM research patterns |
| Diagnostic teaching | Scientific Learning Skills patterns |
| Full tutor architecture reference | DeepTutor |
| Agent memory | Cognee reference |
| Live research | SurfSense |
| Local knowledge workspace reference | Open Notebook / OpenKnowledge |
| Accessibility | A11Y.md principles |
| LLM inference (default) | Free-tier chain: Groq llama-3.3-70b → Gemini 2.5 Flash → OpenRouter (section 26.1) |
| Embeddings (default) | Gemini embedding API free tier behind `EmbeddingProvider` |
| Java AI framework | Spring AI 2.0.x (requires Boot 4.x) |
| Object storage | Cloudflare R2 free tier — 10 GB, 1M/10M ops, free egress, no credit card |

These are references/adapters, not mandatory copied dependencies.

**License policy (ADR-013):** only permissively licensed code/data (MIT, Apache-2.0, ISC, ODbL with attribution) may be embedded in SyllabAI. BSL 1.1 (SurrealDB — struck from all tiers), AGPL (Leantime), GPL-3.0 (open-knowledge), source-available-with-conditions (Chat2DB) and custom/community licenses (PageLM, Blockify, SurfSense) are **reference-only**. Surya: code is Apache-2.0, model weights carry separate modified-OpenRAIL terms — do not redistribute weights. SocraticLM dataset is CC-BY-NC: use for prompt-pattern inspiration only, never redistribution.

---

# 29. Frontend architecture

```text
src/
├── app/
├── components/
│   ├── ui/
│   ├── knowledge-graph/
│   ├── assessment/
│   ├── tutor/
│   ├── dashboard/
│   └── teacher/
├── features/
│   ├── auth/
│   ├── curriculum/
│   ├── learner/
│   ├── assessment/
│   ├── tutor/
│   └── teacher/
├── lib/
├── hooks/
├── services/
├── types/
└── accessibility/
```

Use a typed API client generated from the canonical API schema where practical.

Do not duplicate business rules in the frontend.

---

# 30. Backend package architecture

Recommended Java structure:

```text
com.syllabai
├── auth
├── user
├── school
├── curriculum
├── content
├── knowledge
├── assessment
├── learner
├── diagnostic
├── tutor
├── recommendation
├── teacher
├── analytics
├── research
├── infrastructure
└── shared
```

Each domain module should own its application services, domain objects, ports, and persistence adapters as appropriate.

---

# 31. Background processing

Document parsing, embedding, bulk imports, exports, report generation, recalibration, and scheduled forgetting-curve updates should be asynchronous.

Primary design:
- Spring scheduled jobs for simple recurring tasks.
- A queue abstraction for durable async tasks.
- Redis only if operational need justifies it.
- Do not make Redis a mandatory dependency merely because it is common.

Job categories:

```text
DOCUMENT_PROCESS
EMBED_CONTENT
BUILD_KNOWLEDGE_GRAPH
RECALIBRATE_BKT
APPLY_FORGETTING_DECAY
GENERATE_REPORT
EXPORT_DATA
SEND_EMAIL
RUN_RESEARCH_EVALUATION
```

---

# 32. Observability

Required in production-oriented builds:
- structured logs
- trace/correlation IDs
- application metrics
- exception tracking
- health checks
- dependency health
- AI latency/cost metrics
- retrieval metrics
- queue/job metrics

Recommended tools are replaceable. The feature backlog includes Prometheus/Grafana/ELK/Sentry-style capabilities.

---

# 33. Testing strategy

## Unit tests

Every domain policy and algorithm should be unit tested.

## Integration tests

Use Testcontainers for PostgreSQL and infrastructure integrations where practical.

## Contract tests

Repositories communicate through canonical contracts.

## End-to-end tests

Critical journeys:
- registration/login
- content ingestion
- question attempt
- BKT update
- tutor query
- Smart Mark
- teacher dashboard
- data export/deletion

## Research tests

- BKT simulation
- Smart Mark agreement
- retrieval grounding/citation checks
- diagnostic inference validation
- metric reproducibility

---

# 34. CI/CD

GitHub Actions should run:

```text
format/lint
↓
unit tests
↓
integration tests
↓
build
↓
container build
↓
security/dependency checks
↓
artifact publication
↓
deployment
```

Public GitHub repositories can use standard GitHub-hosted runners without Actions charges; private repositories retain account-specific free allowances and can incur charges beyond the allowance. Source: https://docs.github.com/en/actions/concepts/billing-and-usage

---

# 35. Feature management

Feature flags may be used for staged rollout, experiments, and safe deployment.

Never let a feature flag silently alter research semantics inside an active preregistered experiment without recording the configuration.

---

# 36. Research experiment architecture

Each experiment should specify:

```text
experiment_id
hypothesis
population/cohort
intervention
control/comparison
eligibility
assignment rule
primary outcome
secondary outcomes
analysis plan
model versions
feature configuration
start/end
status
```

Research records are immutable after analysis lock except through explicit versioned corrections.

---

# 37. Final feature inventory governance

The definitive spreadsheet is not merely a wishlist. It is the project-management database for the product surface.

Every feature must have:
- stable feature ID
- epic
- architecture layer
- category
- description
- implementation repo
- priority
- build wave
- dependencies
- complexity
- status
- owner
- research linkage
- validation metric
- source
- notes

No feature is considered complete without updating its row.

---

# 38. Definition of Done

A feature is complete only when:

1. implementation exists in the correct repository/module;
2. tests cover the behavior;
3. security/access control is implemented where applicable;
4. telemetry exists when the feature affects learning/research state;
5. documentation is updated;
6. the spreadsheet status is updated;
7. relevant evidence/provenance exists;
8. deployment/build succeeds;
9. user-visible behavior is verified;
10. research semantics are preserved.

---

# 39. Build waves for the full system

This is an execution order, not a scope restriction.

## Wave 0 - Program foundations

Repositories, contracts, CI, environment management, architecture docs, security baseline.

## Wave 1 - Knowledge and content fabric

Curriculum, document normalization, parsing, provenance, graph, question bank, mark schemes.

## Wave 2 - Learner and assessment engine

Attempts, BKT, BDT, timed/untimed assessment, Smart Mark, learner state.

## Wave 3 - Tutor and diagnostic intelligence

KA-RAG, Socratic tutor, diagnosis, struggle inference, recommendations.

## Wave 4 - Teacher platform and analytics

Class management, dashboards, interventions, early warning, heatmaps, reporting.

## Wave 5 - Advanced multimodal intelligence

Handwriting, image inputs, richer graph reasoning, voice, advanced recommendation, visual explanations.

## Wave 6 - Platform, integration and commercialization

PWA/mobile, LTI, white-labeling, billing, community, support, enterprise integrations.

## Wave 7 - Research maturation

Calibration, longitudinal analyses, external replications, model comparisons, quasi-experimental evaluation, reproducible public datasets where permitted.

---

# 39a. Cycle-1 pilot scope (execution override)

The build waves in section 39 describe the full-system roadmap. The **authoritative execution scope for the course project** is the Cycle-1 pilot slice defined by Paper B:

- **Subject:** Edexcel International GCSE Chemistry (4CH1) — scope moved from Edexcel IAL Chemistry by operator decision (ADR-019, 2026-09-11, which amends the subject scope of ADR-010). The 4CH1 content corpus, spec-point registry (182 points) and mapping program (T-C05/T-C09/T-C10) already execute on this qualification; IAL remains a supported platform qualification (namespaced, coexistence per T-C07) but is Cycle-2+.
- **Population:** ~50 retake-path students, 8 weeks.
- **Agents in scope:** **Tutor + Assessor only** (Paper B Cycle 1). No coach/counselor agents.
- **Study:** pre-registered predictions P1–P8 evaluated against learning-log telemetry.
- **Feature cut:** the rows marked `Cycle 1` in the definitive backlog (34 rows; 12 of them are the critical-path spine: F-020 syllabus parser → F-032 KG → F-033 overlay → F-040 KA-RAG → F-041/F-043 tutor chat with citations → F-047 Smart Mark → F-055 attempt logging → F-137/F-138 learner model + BKT → F-148 LLM provider → F-160 learning log).
- **Everything else** (teacher analytics depth, DAT, gamification, mobile, community, multimodal, mock-exam blueprints) is Cycle 2+ and must not be pulled into Cycle 1. The 2026-09-07 architecture extensions — subject-first workspaces (F-164+), the teacher/classroom LMS layer (TFA-01…TFA-08), point-level question tagging (F-168), the learning-first recommender (ADR-017) and the blueprint-driven Mock Exam Generator (ADR-018, F-171…F-176) — are likewise Cycle 2+ unless individually promoted by an explicit scope decision.

**Cycle-1 exit criteria:** BKT updates live for all pilot topics; KA-RAG answers carry verbatim citations; Smart Mark released to students only after the κ ≥ 0.60 agreement gate (F-161) vs human double-marking; the learning log captures the Paper B §3.5 research fields (keystroke/dwell timing, self-doubt flag, response latency, IRT item parameters); the timed-vs-untimed fluency-gap construct (F-162) is computed for every pilot student.

# 40. Important technology tradeoffs

## Java vs Python

Java is the application/backend language because of the Advanced OOP requirement and the project's strong domain-model fit. Python/Rust/etc. remain valid for specialist parsing and research tooling behind adapters.

Java's main downside is lower convenience for ML/OCR experimentation; this is handled by external engines.

## Next.js vs React-only

Next.js is preferred because the project is a website deployed on Vercel and benefits from routing, rendering, server/client boundaries, and deployment ergonomics. The actual application backend remains Java.

## Neon vs managed alternatives

Neon is preferred because it is PostgreSQL-native, serverless-oriented, inexpensive, and currently offers a no-credit-card free plan. Supabase is a strong alternative, especially for integrated auth/storage, but Neon better preserves a clean Spring Boot/PostgreSQL separation.

## PostgreSQL graph vs Neo4j

PostgreSQL graph tables minimize infrastructure and keep the initial system simple. Neo4j/HelixDB remains an optional provider behind the graph abstraction if traversal complexity demands it.

## pgvector vs dedicated vector DB

pgvector reduces infrastructure and keeps transactional data and embeddings close together. A dedicated vector database remains a replaceable backend if scale/latency/feature requirements justify it.

## Render free backend

Suitable for academic/free deployment, but free services sleep and have finite resources. The architecture must therefore tolerate cold starts and should not depend on local state.

---

# 41. What the research papers do and do not establish

The papers are **design/proposal and preregistration work**, not completed empirical evidence of efficacy. Paper B explicitly says the system has not yet been deployed and describes a design proposal. Paper A similarly frames the conceptual model and predictions as hypotheses to be tested.

Therefore engineering documentation must distinguish:

```text
Established source evidence
vs
Research hypothesis
vs
System design choice
vs
Implementation fact
vs
Maintainer-reported external claim
```

Never present a research hypothesis as a validated outcome.

---

# 42. Paper-reading policy for agents

Agents should **not** reread both papers for every normal coding task.

They should:

1. read `AGENT.md`;
2. read this `MASTER_SPEC.md`;
3. inspect the spreadsheet row(s) they are changing;
4. read the relevant repository/module docs;
5. read the relevant paper section when changing a research-sensitive construct.

Mandatory paper re-read triggers include:
- changing struggle definitions;
- changing BKT/BDT assumptions;
- changing research telemetry fields;
- changing operationalization of predictions;
- changing Smart Mark evaluation;
- changing the conceptual model;
- changing experimental design;
- changing claims about student psychology or educational outcomes.

---

# 43. Project documentation set

The project should maintain:

- `MASTER_SPEC.md` - canonical engineering architecture.
- `AGENT.md` - instructions for coding/research agents.
- `WORKLOG.md` - chronological execution history.
- `PROGRESS.md` - current-state dashboard narrative.
- `TODO.md` - actionable work queue.
- `DECISIONS.md` - architectural decision records (ADR-001…ADR-020; ADR-020 also lives as the standalone `ADR-020-EDUCATIONAL_RETRIEVAL_ENGINE.md`).
- `REPOSITORY_RESEARCH.md` - researched external repository dossier.
- `README.md` - project entry point and navigation.
- `PROJECT_CONTEXT.md` - concise cross-document orientation for humans/agents.
- `ARCHITECTURE_DISCUSSION_SYNC_2026-09-07.md` - durable index of the 2026-09-07 architecture discussions (subject-first, teacher/LMS, learning evidence, recommendations, mock exams).
- `SUBJECT_ARCHITECTURE.md` - canonical subject-first / specification-point architecture (ADR-014).
- `TEACHER_ARCHITECTURE.md` - canonical teacher/classroom LMS blueprint (ADR-015).
- `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` - canonical evidence-subsystem contract (ADR-016).
- `RECOMMENDATION_SYSTEM_ARCHITECTURE.md` - canonical learning-first recommender design (ADR-017).
- `MOCK_EXAM_GENERATOR_ARCHITECTURE.md` - canonical blueprint-driven mock-exam architecture (ADR-018).
- `MOCK_EXAM_GENERATOR_AGENT_ADDENDUM.md` - mandatory implementation rules for F-051 and the mock feature family.
- `DECISION_018_MOCK_EXAM_GENERATOR.md` - dedicated ADR-018 decision record.
- `LEARNER_INTERACTION_MEMORY_ARCHITECTURE.md` - canonical learner-interaction-memory architecture (implemented V21/V23 runtime).
- `MASTER_SPEC_ADDENDUM_1.4_LEARNER_INTERACTION_MEMORY.md` - spec addendum for the learner-interaction-memory layer.
- `AGENT_LEARNER_INTERACTION_MEMORY_ADDENDUM.md` - mandatory implementation rules for all conversational-surface work.
- `CONTEXTUAL_LEARNING_ASSISTANT_ARCHITECTURE.md` - canonical Contextual Learning Assistant contract (ADR-022; PROPOSED, no runtime).
- `MASTER_SPEC_ADDENDUM_1.5_CONTEXTUAL_LEARNING_ASSISTANT.md` - spec addendum for the CLA contract primitives and leakage policy.
- `AGENT_CONTEXTUAL_LEARNING_ASSISTANT_ADDENDUM.md` - mandatory rules for any future CLA implementation work.
- `WORKBOOK_SYNC_2026-09-07.md` - record of the canonical workbook consolidation and cleanup.
- `backlog/*-feature-addendum.tsv` - detailed feature-tracker addenda feeding the definitive master workbook (folded: subject/teacher/learning-evidence/recommendation in session 17, mock-exam in session 18; the addenda remain detailed supplements, not competing inventories).

The research papers themselves should remain in the context pack and project source archive.

---

# 44. Final architectural principle

SyllabAI should own its domain model and contracts.

External projects should accelerate implementation, not define SyllabAI's architecture.

The system should be able to replace:

```text
LLM provider
Vector store
Graph store
Parser engine
OCR engine
Object storage
Deployment provider
```

without rewriting the core learning-domain logic.

The final system is therefore a **contract-driven, modular, research-instrumented adaptive learning platform** with a Java/Spring Boot core, Next.js/Vercel web experience, PostgreSQL/pgvector data foundation, and independently replaceable content/AI engines.
