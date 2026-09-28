# DECISIONS.md - SyllabAI Architecture Decision Records

## ADR-001: Java is the core backend language

**Status:** Accepted  
**Date:** 2026-09-02

SyllabAI's application backend will be Java 25 + Spring Boot 4.1.x. This satisfies the Advanced Object Oriented Programming requirement and provides a strong domain-oriented architecture.

Specialist OCR/document/ML workloads may live in independent repos and runtimes behind stable contracts.

## ADR-002: Next.js for the web frontend

**Status:** Accepted

Use Next.js 16.x + React 19.x + TypeScript for the website. Deploy the frontend to Vercel. Do not move the Spring Boot backend into Vercel functions.

## ADR-003: Multi-repository architecture

**Status:** Accepted

Separate genuinely independent subsystems such as parsing, learner modeling, knowledge tooling, assessment, AI, research, and infrastructure. Keep the main application a modular monolith rather than premature microservices.

## ADR-004: Neon PostgreSQL + pgvector

**Status:** Accepted

Use Neon PostgreSQL as the default hosted system of record and pgvector as the default vector layer. This keeps the free architecture simple and avoids an unnecessary dedicated vector database.

## ADR-005: PostgreSQL-backed knowledge graph first

**Status:** Accepted

Represent the curriculum/knowledge graph using relational graph tables and recursive queries initially. Hide the graph behind an interface so Neo4j/HelixDB/etc. can be introduced without changing domain logic.

## ADR-006: Render for free Java backend hosting

**Status:** Accepted with constraint

Use a Dockerized Spring Boot service on Render's free tier under the no-credit-card requirement. Accept cold starts/ephemeral filesystem limitations. Design the application so no important state depends on the instance filesystem.

## ADR-007: Master Spec vs research papers

**Status:** Accepted

The Master Spec is the engineering source of truth. The papers remain authoritative for research claims, definitions, hypotheses, and evaluation design. Agents read the relevant paper section when scientific meaning changes.

## ADR-008: Spreadsheet as definitive feature tracker

**Status:** Accepted

The definitive workbook records feature IDs, status, priority, dependencies, implementation repo, validation metrics, and other execution metadata. Any newly discovered capability must be added there rather than left only in prose.

## ADR-009: Free-tier LLM provider chain ($0, no credit card)

**Status:** Accepted
**Date:** 2026-09-03

All AI inference for the Cycle-1 pilot runs on verified free tiers behind `LlmProvider`: Groq `llama-3.3-70b-versatile` (primary, ~14,400 req/day, OpenAI-compatible), Gemini 2.5 Flash (fallback), OpenRouter free models (tertiary). Embeddings: Gemini embedding API. Automatic failover with per-experiment provider pinning. Paid providers stay allowed for experiments that need them; no Cycle-1 feature may hard-depend on a paid model. Verified limits recorded in `PLATFORM_RESEARCH.md`. Re-verify limits at build time — free tiers drift.

## ADR-010: Cycle-1 pilot scope (execution override)

**Status:** Accepted
**Date:** 2026-09-03

The authoritative execution scope is Paper B's Cycle-1 pilot: Edexcel IAL Chemistry, ~50 retake-path students, 8 weeks, Tutor + Assessor agents only, predictions P1–P8. Backlog rows marked `Cycle 1` (34 rows; 12-spine critical path) define the cut. The build waves remain the full-system roadmap, but Cycle 2+ features must not be pulled into Cycle 1. Exit criteria in Master Spec §39a (κ ≥ 0.60 Smart Mark gate; Paper B §3.5 telemetry fields live).

## ADR-011: Polyglot policy — Java preferred, best language wins per component

**Status:** Accepted
**Date:** 2026-09-03

Java (25, Spring Boot 4.1, Spring AI 2.0) owns the domain core — the Advanced OOP course requirement and the strongest domain-model fit. Components where another ecosystem is clearly better may use that language: web frontend in TypeScript (Next.js), offline OCR/ML parsing in Python/Rust (MinerU/Surya) inside `syllabai-parser`. Where the choice is a tie, Java wins (e.g. opendataloader-pdf — Java + Apache-2.0, embeddable in-process via Maven, no extra runtime).

## ADR-012: Four application repositories now; module repos deferred (public corpus repository tracked separately)

**Status:** Accepted
**Date:** 2026-09-03 (title clarified 2026-09-07 per the documentation contradiction audit — the historical decision is unchanged)

Repositories are `syllabai`, `syllabai-core`, `syllabai-web`, `syllabai-parser`, plus the public `Past-Papers` corpus repository described in the current Master Spec and Project Context. The former syllabai-knowledge/-assessment/-learner-model/-ai/-research/-infrastructure repos become strongly-separated modules inside the `syllabai-core` monolith. They graduate to repositories only when a genuine runtime/lifecycle boundary appears. Rationale: solo + AI-agent development; many repos of mostly-empty stubs create process overhead at pilot scale.

## ADR-013: License wall for external code and data

**Status:** Accepted
**Date:** 2026-09-03

Only permissively licensed code/data (MIT, Apache-2.0, ISC, ODbL with attribution) may be embedded in SyllabAI. BSL 1.1, AGPL, GPL, source-available, and custom/community licenses are reference-only. **SurrealDB is reference-only** (BSL 1.1). Also reference-only: Chat2DB, PageLM, Blockify, SurfSense, open-knowledge, Leantime. Surya model weights and the SocraticLM dataset carry separate non-permissive terms.

## ADR-014: Subject-first student experience and first-class specification points

**Status:** Accepted
**Date:** 2026-09-07

SyllabAI's long-term student product is organized around **subject enrollments**, not a single mixed-subject dashboard. A student can begin with zero subjects, then add courses through `Board → Qualification → Subject → Curriculum/Specification Version`. Each enrolled subject becomes a self-contained workspace containing its academic resources, assessment tools, tutor context, learner state, and subject knowledge graph.

The curriculum model is extended from `Subject → Unit → Topic → SubTopic` to:

```text
Board → Qualification → Subject → CurriculumVersion
  → Unit/Section → Topic/SubTopic → SpecificationPoint
```

A `SpecificationPoint` is a first-class curriculum/knowledge anchor for the official numbered learning objectives found in detailed board specifications. It preserves official code, verbatim objective statement, ordering, curriculum version, source provenance, and applicability metadata. Agents must not flatten these objectives into generic tags or invent numbering.

Resources such as Revision Notes, Flashcards, and Smart Lesson steps should map to specification points. Future QuestionVersion/QuestionPart tagging may map one question to multiple specification points and must preserve uncertainty/review state. This extends F-152 rather than replacing it.

The stable curriculum graph and mutable learner state remain separate. Mastery, misconception, confidence, procedural fluency, evidence, and review state are overlays keyed to the relevant subject/curriculum graph nodes; they never mutate official curriculum content.

The detailed decision and implementation blueprint is canonical in `SUBJECT_ARCHITECTURE.md`.

**Scope guard:** this ADR changes the product architecture, not the active pilot scope. Cycle 1 remains Edexcel IAL Chemistry under ADR-010. IGCSE Chemistry is a supported target architecture/example, not authorization to begin IGCSE bulk ingestion.

## ADR-015: Role-aware teacher/classroom LMS layer over the shared subject graph

**Status:** Accepted
**Date:** 2026-09-07

SyllabAI's long-term product includes a role-specific **Teacher/Classroom/LMS layer** built over the same Board → Qualification → Subject → CurriculumVersion → SpecificationPoint graph, question bank, content system, assessment evidence, and learner-model substrate used by students.

Teachers are subject-scoped. Clicking a taught subject opens a teacher workspace containing subject resources plus teacher workflows such as Classes, Assignments, Test Builder, Mock Exams, Announcements, Knowledge Graph, At-Risk Students, reports, Teacher AI Assistant, and Data Assistant. Smart Lesson remains primarily a student-facing adaptive workflow unless a later decision adds a teacher-specific variant.

There are two student interface modes over one identity and learner model:

```text
Independent student
  └── subject workspace

Classroom-enrolled student
  └── same subject workspace
       └── Announcements + Assignments + My Results/Feedback
```

Class enrollment is an additional capability/authorization relationship, not a second account or second learner model.

The teacher Knowledge Graph is a **different lens over the same graph**, not a separate curriculum graph. It adds a teaching-coverage overlay and class-level aggregation of learner state. `NOT_TAUGHT` is semantically distinct from `LOW_MASTERY`; grey nodes may indicate absent teaching coverage, while taught nodes may be colored by class understanding. Class aggregates should preserve distributions, evidence counts, and misconception prevalence rather than relying on mean mastery alone. Teachers must be able to drill down from class node → affected students → individual student graph → evidence → teacher action.

The Teacher AI Assistant and Data Assistant are separate capabilities:
- Teacher AI Assistant: grounded academic/content/teaching copilot.
- Data Assistant: authorized structured analytics assistant that summarizes class/student evidence and never invents marks, counts, dates, or risk labels.

At-Risk Students is evidence-first. Every flag must be inspectable and should expose contributing evidence plus the relevant rule/model version. Teacher-facing AI-generated questions/resources remain drafts until they satisfy the project's validation/content-serving policy.

The existing F-050 Test Builder remains the canonical feature identity for teacher test creation. The new requirement is an **evidence-driven enhancement**, not a duplicate feature: specification-point, skill, misconception, class-weakness and teaching-coverage targeting may augment the existing builder while retaining manual question selection, reuse/edit behavior and PDF export.

`T-029` is a minimal current teacher review surface, not the complete teacher product. Its Cycle-1-era roster implementation intentionally uses the enabled STUDENT cohort because a persistent Class domain entity is not yet part of the pilot. Future Class Management must introduce the explicit class/membership model rather than treating the pilot shortcut as final architecture.

The complete teacher/classroom/LMS blueprint is canonical in `TEACHER_ARCHITECTURE.md`.

**Scope guard:** ADR-015 defines the long-term product architecture and does not expand Cycle 1. Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010.

## ADR-016: Question Attempt & Learning Evidence as a first-class subsystem

**Status:** Accepted
**Date:** 2026-09-07

SyllabAI will treat question-level learner interaction as a first-class **Question Attempt & Learning Evidence** subsystem, also called the **Learning Log** in Paper B.

The subsystem is the canonical bridge between the assessment/question domain and learner modeling, diagnostic inference, Knowledge Graph learner overlays, recommendation/intervention, spaced review, the student Review Hub, teacher/class evidence analytics, and research telemetry.

### Semantic separation

```text
Immutable assessment evidence
        ≠
Mutable learner review state
        ≠
Derived learner mastery
```

A QuestionAttempt records what happened. A review state records how the learner currently relates to the question (problematic, doubtful, resolved, etc.). Mastery is inferred by the learner model from evidence and must not be directly mutated by UI actions.

### Canonical question identity

The same Question/QuestionPart may appear in Past Papers, Target Tests, Test Builder quizzes, Mock Exams, Teacher Assignments, Smart Lessons, and future generated/variant sessions. A source session is provenance/context, not a new academic question identity.

### Granularity and evidence

Evidence should use QuestionPart granularity whenever feasible because marking and SpecificationPoint coverage may be part-specific. Raw assessment evidence must preserve `awardedMarks` and `maximumMarks`; a normalized percentage may be derived but is not sufficient as the canonical record.

QuestionPart → SpecificationPoint is many-to-many. Multi-specification coverage must never be collapsed to one topic purely for storage convenience.

### Learner self-report

Confidence, self-doubt, problem flags and resolution are legitimate learner signals, especially for metacognition research, but are not assessor truth. The following older brainstorm rules are explicitly rejected as deterministic learner-model arithmetic:

```text
flag → mastery -0.02
resolve → mastery +0.01
self-doubt → halve mastery gain
```

Such signals may be weighted by the learner model, but UI clicks do not directly change mastery.

### Previously attempted / skipped work

A previously-attempted indicator must query canonical question identity across sources. A “paper completed” state must never imply that all questions were attempted. Skipped/unattempted parts must remain detectable and resurfaced when the learner encounters the material again.

### Integrations

Smart Mark and normal test submission are automatic producers of attempt evidence. The same evidence substrate feeds the learner model, KG overlay, recommendations, Review Hub, spaced review, and teacher analytics. No parallel tracking model should be created for any of those features.

Research-only telemetry such as IRT parameters or keystroke timing must be versioned, privacy-aware, and explicitly justified by the research protocol before it becomes product-critical.

### Research basis

Paper B §3.5 explicitly defines the Learning Log and explains the 80%-of-a-paper / skipped-hard-questions failure mode. Paper B §3.13 maps richer telemetry to the project's struggle types. Changes that alter these semantics are research-sensitive and must be checked against the relevant paper section.

The full implementation contract is canonical in `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md`; agent-specific rules are in `LEARNING_EVIDENCE_AGENT_ADDENDUM.md`.

**Scope guard:** ADR-016 defines long-term product and research architecture and does not expand Cycle 1. Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010.

## ADR-017: Learning-first recommendation system

**Status:** Accepted
**Date:** 2026-09-07

SyllabAI implements recommendations as a **learning-first adaptive action-selection system**, not an engagement-maximizing feed. The objective is expected learning progress and appropriate syllabus coverage under subject/curriculum, validation, authorization, prerequisite and teacher constraints. The canonical model is a cascade: learner evidence/state + subject/specification graph → constrained candidate generation → content-based expansion → optional learned ranking → constrained exploration → explainable next-best learning action → new learner evidence.

Rules: rule-based recommendations are the canonical baseline (F-087); content-based similarity is candidate expansion, not the objective (F-088); collaborative filtering is a later experiment that can never override hard pedagogical/curriculum constraints (F-089); the hybrid cascade is the canonical long-term architecture (F-090); the old hard-coded 10% random epsilon-greedy exploration proposal is rejected as a product rule and the old 0–5/5–20/20+ interaction thresholds are heuristic examples, not scientific constants (F-091); personalized next steps are the primary learner-facing orchestration — recommendations are actions, not just resources (F-092); reasons derive from structured evidence and reason codes, never invented statistics (F-093); recommendation quality is ultimately evaluated with learning outcomes, not CTR/watch time (F-154); educational video discovery is subject-scoped and validated, with generic YouTube recommendation feeds explicitly rejected as SyllabAI's learning policy and watch time treated as telemetry, never mastery (F-025/F-026). No recommendation microservice is needed under the modular-monolith architecture. The decision extends the existing tracker rows rather than duplicating them; the recommendation engine consumes the ADR-016 evidence subsystem.

The full design is canonical in `RECOMMENDATION_SYSTEM_ARCHITECTURE.md`; agent rules are in `RECOMMENDATION_SYSTEM_AGENT_ADDENDUM.md`; the decision record is also mirrored in `ADR_017_LEARNING_FIRST_RECOMMENDATION_SYSTEM.md`.

**Scope guard:** ADR-017 defines long-term product architecture and does not expand Cycle 1. Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010.

## ADR-018: Blueprint-driven Mock Exam Generator

**Status:** Accepted
**Date:** 2026-09-07

SyllabAI will treat the Mock Exam Generator as a **versioned exam-blueprint-driven assessment system** rather than an LLM-only text-generation feature. It shares the canonical question bank and assessment substrate with F-050 Test Builder, F-049 Target Test, F-053 Timed Exam Mode, F-047 Smart Mark and the F-055+ Question Attempt/Learning Evidence subsystem, while remaining a distinct product policy.

The blueprint is scoped and versioned by `Board → Qualification → Subject → CurriculumVersion → PaperCode → PaperVariant/PaperType → BlueprintVersion`. Official board rules and historical corpus-derived patterns must remain separately identified and provenance-bearing; historical frequency must not silently become board truth.

Paper assembly uses validated Question/QuestionPart candidates and AssessmentBlock/QuestionGroup groupings where shared stimulus/data/context creates atomic assessment semantics. Hard validity constraints are distinct from soft optimization objectives. The solver implementation is replaceable; knapsack/CP-SAT/integer programming/dynamic programming are implementation options, not architectural commitments. Unsatisfiable hard constraints fail explicitly.

Difficulty is contextual evidence rather than a universal immutable 1–5 fact; Bloom is optional annotation; universal `marks × 1.5 minutes` timing is rejected. Exam Simulation and Adaptive Diagnostic Mock are explicit policies: personalization may affect valid item selection in the latter, but blueprint validity remains a hard floor.

AI-generated or AI-modified variants are later and higher-risk. They must pass deterministic structural checks, numerical/domain/unit validation, answer/mark-scheme alignment and provenance/AI-execution metadata, plus human review where required, before being learner-served. Generated questions never become canonical board truth merely because they are plausible.

Mock attempts use the existing immutable-evidence / review-state / derived-mastery separation. Paper completion never implies every question was attempted. Predicted grades/readiness values remain future research/evaluation outputs until a validated model exists; no fabricated prediction UI is permitted.

The complete implementation blueprint is canonical in `MOCK_EXAM_GENERATOR_ARCHITECTURE.md`, with agent rules in `MOCK_EXAM_GENERATOR_AGENT_ADDENDUM.md` and the dedicated decision record in `DECISION_018_MOCK_EXAM_GENERATOR.md`.

**Scope guard:** ADR-018 defines long-term product architecture and does not expand Cycle 1. Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010.

## ADR-019: Cycle-1 pilot qualification pivot — Edexcel IAL Chemistry → Edexcel IGCSE Chemistry (4CH1)

**Status:** Accepted (operator decision)
**Date:** 2026-09-11

The Cycle-1 course-project pilot runs on **Edexcel International GCSE Chemistry (4CH1)** instead of Edexcel IAL Chemistry. This amends the subject scope of ADR-010 and supersedes every earlier "Cycle 1 remains Edexcel IAL Chemistry" statement (the ADR-017/ADR-018 scope guards, the §39a v1.2.1 text, and similar lines in historical logs). Those records are preserved verbatim per the source hierarchy; this ADR is the superseding authority.

Rationale: the operator's teaching context is IGCSE, and the entire content program already executes on 4CH1 — the 2017 4CH1 specification with its 182-point registry (S1:60 / S2:50 / S3:22 / S4:50, 28 subtopics), the CMC v1.0 content corpus and provenance machinery (T-C05), the 112-note spec-point mapping with ratification gates (T-C09/T-C10), and the past-paper QP/MS ingestion (41 sessions complete, Papers 1–2). The only IAL artifact is the core DB's T-010 curriculum seed (Pearson 2018 IAL spec: 6 units / 20 topics / 15 subtopics), which remains valid, namespaced platform content awaiting T-C06 wiring.

Unchanged by this decision: the pilot population (~50 retake-path students, 8 weeks), the agents in scope (Tutor + Assessor only), the pre-registered predictions P1–P8, the 34-row Cycle-1 backlog cut with its 12-spine critical path, and the qualification coexistence rules — KG node codes stay namespaced per qualification (`4CH1-*`, `WCH*`), and the T-C07 curriculum-scoping gap in retrieval must close before corpus embeddings are enabled. IAL support remains a Cycle-2+ platform capability, not a Cycle-1 subject.

Follow-ups already registered stay valid: 4CH1 curriculum ingestion into core rides T-C06's CurriculumDraftDto path; T-C11 zero-coverage corpus-gap work (annotated 4CH1-4.15 gap) continues unchanged.

**Scope guard:** ADR-019 IS the explicit scope change that SUBJECT_ARCHITECTURE §0/§15 and Master Spec §39a anticipated. It changes only the Cycle-1 subject qualification; it does not authorize bulk ingestion of any further qualification, subject, or course.

## ADR-020: SyllabAI-native Educational Retrieval Engine

**Status:** Accepted architecture direction; implementation promotion gated by benchmark evidence
**Date:** 2026-09-12

SyllabAI builds a provider-neutral **Educational Retrieval Engine** inside the existing modular architecture instead of adopting a generic RAG framework. Research into `NirDiamant/RAG_Techniques`, `HKUDS/LightRAG`, `HKUDS/RAG-Anything` and `infiniflow/ragflow` identified the borrowable techniques (hybrid recall, reranking, hierarchical/contextual retrieval, graph-aware expansion, evidence selection, stronger citation/evaluation practice), but adopting a generic platform would create a competing source of truth beside the authoritative curriculum graph, SpecificationPoints, validated resource mappings, learner state and immutable learning evidence, and would weaken provenance. Trade-off accepted: SyllabAI implements and maintains more retrieval logic itself, and a benchmark/evaluation corpus is required before aggressive optimization.

The complete decision record is canonical in `ADR-020-EDUCATIONAL_RETRIEVAL_ENGINE.md`, with the research dossier in `RAG_RETRIEVAL_RESEARCH.md`. (Ledger entry registered 2026-09-13 to restore the standalone-file ↔ ledger mirror pattern; the standalone file remains the authority.)

**Scope guard:** this ADR does not authorize bulk ingestion of new subjects or expansion of Cycle 1 — the pilot corpus remains Pearson Edexcel International GCSE Chemistry 4CH1 — and retrieval work must not become an excuse to indefinitely delay the pilot.

## ADR-021: Content Compiler and Portable Content Package

**Status:** Proposed  
**Date:** 2026-09-15

Markdown is a first-class durable content/interchange representation for Revision Notes and parser/OCR-derived QP/MS artifacts; PostgreSQL remains the canonical operational/domain representation; a SyllabAI-specific SQLite Content Package is designed as a derived portable/reproducible corpus, QA, research and distribution format. SQLite packages are not authoritative learner state, curriculum truth, KG truth, or production multi-user storage. Generic MarkdownDB is not adopted as a core dependency. No package or Markdown artifact bypasses existing validation, authorization or learner-serving gates.

The complete decision record is canonical in `ADR_021_CONTENT_COMPILER_AND_PORTABLE_CONTENT_PACKAGE.md`, with the architecture in `CONTENT_COMPILER_AND_PACKAGE_ARCHITECTURE.md` and the initial package contract in `CONTENT_PACKAGE_V0_1.md`. (Ledger entry registered 2026-09-15 by the documentation audit reconciliation to close the 020→022 numbering gap; the standalone file remains the authority. Promotion from PROPOSED requires implementation evidence and bounded reproducibility tests.)

**Scope guard:** this ADR does not change Cycle-1 product scope and does not authorize bulk ingestion, learner-serving changes, or a production database migration.

## ADR-022: Contextual Learning Assistant — contract-first, platform-owned context

**Status:** Accepted as contract direction; runtime PROPOSED and separately gated
**Date:** 2026-09-15

The next conversational surface after the Grounded Tutor is the **Contextual Learning Assistant (CLA)**: a grounded assistant that operates in the resolved context of the resource the learner is viewing (spec point, KG topic, note section, question part, Smart Lesson topic). The operator registered the contract task on the core tracker (syllabai-core#17, with the Learner Interaction Memory binding rules in syllabai-core#16); this ADR accepts the contract direction and fixes its non-negotiables.

Decision: the CLA **composes** the verified subsystems — Educational Retrieval Engine (ADR-020) for context-anchored evidence acquisition, the Grounded Tutor (KA-RAG) for grounded generation with deterministic refusal and claim/citation validation, Learner Interaction Memory (Master Spec Addendum 1.4; core contract `syllabai-core/docs/LEARNER_INTERACTION_MEMORY_IMPLEMENTATION.md`) for evidence capture, and the governed learner-state/NBA layers for consumption — and it introduces no new generative stack. Context resolution, response modes, tool registry, budgets and leakage control are **platform-owned application code**; provider-side memory, session, tools or context are rejected (provider infrastructure must not become canonical SyllabAI state).

The defining safety property is the **exam-question answer-leakage policy**: answer-protection for content with pending attempts or in timed/mock/assignment contexts is deterministic application logic (HINT scaffolds, never reveals; full feedback unlocks only post-attempt, proven from attempt evidence), enforced in code and CI-tested with a mandatory negative leakage suite — never delegated to the model or to prompts.

Canonical artifacts: `CONTEXTUAL_LEARNING_ASSISTANT_ARCHITECTURE.md`, `MASTER_SPEC_ADDENDUM_1.5_CONTEXTUAL_LEARNING_ASSISTANT.md`, `AGENT_CONTEXTUAL_LEARNING_ASSISTANT_ADDENDUM.md`, and the core implementation contract `syllabai-core/docs/CONTEXTUAL_LEARNING_ASSISTANT_IMPLEMENTATION.md`.

**Scope guard:** this ADR authorizes contract and evaluation design only — no runtime implementation, no Cycle-1 scope expansion (pilot remains 4CH1, Tutor + Assessor agents under ADR-019), and it must not delay the pilot. Runtime work proceeds only as separately planned, separately verified tranches under the core contract's sequencing and the ADR-020 evaluation discipline.

## ADR-023: LLM provider pool hardening — extend FailoverLlmChain, structured failures, local daily budget, fail-closed modes

**Status:** Accepted (slices B/C/D/E + benchmark harness; evidence on main)
**Date:** 2026-09-17

The LLM Provider Pool work extends the EXISTING provider architecture instead of rewriting it: `LlmProvider` + `FailoverLlmChain` remain the only routing abstraction (ADR-009 chain order unchanged). Failures are classified ONCE at the provider/adapter boundary into `LlmFailureClass` from SDK exception types and HTTP status codes — never message string-matching; dead-key / retired-model configuration failures suppress that provider until the end of the UTC day while transient classes keep threshold/cooldown semantics. `daily-budget-per-provider` is enforced as a configured LOCAL routing guard (requestsToday >= budget ⇒ ineligible until UTC-day rollover; chain fails over; pinned experiments fail closed — pins never silently drift). `syllabai.llm.mode` = production|test|live makes test boots FAIL CLOSED (real adapters are never constructed in test mode; keys are ignored with a warning) and gates live-provider tests behind `LIVE_LLM_TESTS=explicit`. One reusable deterministic `FakeLlmProvider` test fixture replaces duplicated hand-written fakes and records invocation metadata (never prompt text). Admin chain-health snapshots gain additive routing fields (enabled/configured/healthy/coolingDown/requestsToday/dailyBudget/remainingLocalBudget/lastFailureClass/effectiveModel).

FreeLLMAPI (self-hosted OpenAI-compatible free-tier aggregator) is researched against primary sources in `PLATFORM_RESEARCH.md` and stays **PROPOSED / EXPERIMENTAL** — no production integration; if ever promoted it enters as an optional, experiment-pinnable member through the existing `SpringAiChatModelAdapter`, never as the canonical layer. Quota circumvention (multi-account pools, credential rotation) is rejected outright.

The complete decision record is canonical in `ADR-023-LLM_PROVIDER_POOL_HARDENING.md` (standalone file remains the authority). Implementation evidence: syllabai-core `b8ce0f4`/`f669330`/`bdc2540`/`8e1d27b`; regression 582 tests green (0 failures, 1 live-gated skip).

**Scope guard:** provider-routing mechanics only — no retrieval, KG, learner-state, evidence, InterventionRun or CLA pedagogy semantics change; benchmark execution remains operator-gated behind live credentials.

## ADR-024: InterventionRun (E2) promoted to ACCEPTED production architecture

**Status:** Accepted
**Date:** 2026-09-17

The bounded InterventionRun orchestration boundary (contract `docs/research/INTERVENTION_RUN_PROTOTYPE.md`, core issue #19) is promoted PROPOSED → ACCEPTED under the contract's own §14 decision gate, with every precondition executed and verified rather than reported: acceptance criteria 1–10 demonstrated claim-by-claim (unit suite green; live verification 10/10 PASS on production at core `02643ed`, evidence committed in the central repo); persistence/query cost understood (`syllabai-core/docs/INTERVENTION_RUN_PERSISTENCE_QUERY_COST.md` — run-PK-scoped index-covered queries, ≈0.75 MB/month worst-case growth, normalization trigger not fired, so the §14 fallback clause does not apply); `InterventionRunFlowIT` 2/2 GREEN in real Docker core-ci (run `35139255878` at `7eb621a`, the fixture-fix `ef69d8d` lineage); and the deployed runtime verified via the Render API — the LIVE deploy is exactly `7eb621a`, with intervention product code byte-identical since `02643ed`, making the production 10/10 apply verbatim to the deployed build. The operator's conditional promotion directive was given and executed the same day.

**Scope guard:** the run records bounded execution and NEVER mutates learner state (the governed evidence path remains the sole authority — DB-level bit-identical proof stands); no generic workflow engine, no autonomous LLM-defined steps, no curriculum/KG mutation, terminal history append-only. Any future scope growth re-opens the contract, not this record.

## ADR-025: Smart Mark product contract — bounded per-part marker inside Exam Questions, no chatbox

**Status:** Accepted (operator decision)
**Date:** 2026-09-18

Smart Mark's product placement is fixed by operator clarification (session 101): it is the in-page marking widget on Exam Questions pages and the **single marking authority** — the tutor/CLA explain, Smart Mark marks, and Smart Mark has no chatbox. The marking unit **remains per-part** (one `Answer` per `QuestionPart`, scheme points scoped to that part); the whole-question single-context marking proposal is **rejected** to preserve per-point κ calibration (F-161), the bounds/mark-sum/coverage validator scoping, and skipped-part detection — full-question/full-scheme rendering is presentation context only, and answers persist per-part regardless of input presentation. Bounded post-mark actions ("Explain my feedback" / "Improve my answer") are single-purpose governed generation over the learner's answer and the question's own validated scheme points under the post-attempt leakage rules; resubmission re-marks with append-only result history; self-mark stays a first-class alternative. Question-level topic/spec categorization powers the Exam Questions repo, Test Builder (F-050) and Target Test; the filter/difficulty/type substrate is owned by T-C18. Canonical record: `ADR-025-SMART_MARK_PRODUCT_CONTRACT.md` (standalone file remains the authority); Master Spec §15.1; build lane T-C21.

**Scope guard:** product placement/UX contract only — no pipeline, validator, κ-gate, evidence-contract or CLA-leakage semantics change; build execution separately tracked (T-C21).

## ADR-026: SME question-bank import surface (igcse-chemistry-19) — corpus replace, evidence-safe deactivation, κ-excluded self-marking

**Status:** ACCEPTED (production, deployed 2026-09-18)
**Date:** 2026-09-18 (s104 branch built + tested; session 105 reconstructed the lost artifacts, renumbered V29→V30, extended the surface, merged, deployed)
**Build lane:** T-C22

The operator's directive (2026-09-17/18): validate the SME→4CH1 mapping, then replace the live question bank with the SME exam-question corpus and the live revision notes with the SME re-scrape (igcse-chemistry-19 only — ADR-014 Cycle-1 scope guard). The import rides a versioned ZIP package (`sme-question-package/1.0` + `assets/`), built by deterministic zero-LLM scripts (`scripts/s104_*.py`, syllabai-resources@sme-import-session-104), validated fail-closed at the endpoint (wrong version / duplicate refs / unresolvable KG codes / MCQ without exactly-one-correct / part-marks mismatch / dangling asset refs reject the whole package, single transaction, live bank untouched).

Key decisions:

1. **Replace semantics, evidence-safe:** one transaction deactivates every active question (rows survive — attempts, the pending κ marking queue, BKT evidence and FK chains untouched) and inserts the SME set as VALIDATED v1 (PAST_PAPER provenance, difficulty_source=SME, easy/medium/hard → 2/3/4). Old bank recovery = re-ingest any prior package; nothing is ever deleted.
2. **Question→spec-point mappings are first-class** (T-C18's ratified design): `question_spec_points` (role PRIMARY/SECONDARY, provenance + validation_state, AI_VALIDATED under the operator's 2026-09-17 delegation, upgradable to HUMAN_VALIDATED by review without re-import). Codes resolve against the official 182-point 4CH1 registry — 1,404/1,404 corpus parts coded, all in-registry (verified A-gate).
3. **Learner self-marking is first-class but κ-excluded** (complements ADR-025's "self-mark stays first-class"): the SME reveal-and-self-mark flow settles the caller's own structured attempt and fires the once-only evidence exactly like the teacher human-mark path (attempt-row lock, per-part bounds, conservative full-marks-equals-correct), but records in `learner_self_marks` — never `HumanMark` — so the F-161 κ agreement sample stays teacher-only by construction. Single-shot: settled attempts reject self-marks (409); the teacher override path remains authoritative.
4. **Serving posture:** SME questions are born VALIDATED (operator delegation; the mapping cross-check 161/162 vs the human c10/c12 notes mappings is recorded in the corpus VALIDATION.md); the V20 paper gate and servability rules apply unchanged. `solutionMd` is SME's worked solution feeding the reveal/self-mark flows — NOT the official Pearson scheme; κ-grade marking still runs on teacher judgment (F-161 unchanged).
5. **Migration numbering:** the surface lands as V30 — T-C06's V29__content_corpus_kinds landed on main after the branch was cut; two V29s cannot coexist under Flyway (the renumber is recorded in the migration header).

Propagation obligations: the corpus packages are sha256-pinned (web release `sme-corpus-2026-09-18` + operator runbook download/s104-sme-import/); re-ingestion is idempotent-by-replace (re-runs deactivate+insert, same corpus version = same content). The revision-notes corpus (v2 package, union spec-map: c10 HUMAN_VALIDATED ∪ SME resolution) shares the full-replace semantics of the existing V27 surface — T-C06's IAL canonical-documents track is a separate path (documents/chunks, born-SUGGESTED) and is unaffected.

**Scope guard:** igcse-chemistry-19 only; flashcards, IAL and the other 37 courses remain Cycle 2+ (ADR-014). The upload itself requires ADMIN (operator credential boundary — run 35348458620 verdict OPERATOR_BOUNDARY; no ADMIN secret exists in any repo).

> [Session-112 reconciliation note] Originally recorded as ADR-025 on this lane's branch; renumbered ADR-027 at the merge because the canonical ADR-025 was independently taken by the operator's Smart Mark product-contract decision (`1304eaa`). No semantic change; references in the classroom lane's copy of the original ADR-025 file resolve to this ADR-027.
## ADR-027: Teacher-marking-surface scoping — classroom-authorization visibility; independent learners teacher-invisible

**Status:** Accepted
**Date:** 2026-09-20

The teacher marking surface (T-029 queue, throughput metrics, Run-Smart-Mark batch, override/κ views) is AUTHORIZATION-SCOPED: it shows only answers from learners enrolled in classes assigned to the requesting teacher. Independent learners (no class enrollment) never appear on any teacher surface — closing TEACHER_ARCHITECTURE §8 ("a teacher must only be able to access classes and students covered by their authorization scope") at the marking boundary. Today's global `findByMarkingState` read survives only as the ADR-015 pilot shortcut (no Class entity yet; pilot-staff authorization covers every pilot learner), is time-boxed here, and becomes a defect — not a cleanup item — the moment the classroom lane introduces the Class/membership model.

Teacher marking is NEVER a blocking step for an independent learner: their flow is self-mark (View Answer mark-scheme reveal) or Smart Mark, with evidence semantics unchanged and fail-closed (κ-gated, F-161); an answer remaining SMART_MARKED indefinitely is a correct terminal state, not a stuck one. Paired κ calibration decisions originate exclusively where a human marker holds authorization (classroom scope; today the pilot-staff runbook) — independent answers are never sampled for calibration and never need to be. Visibility is computed live from current enrollment + teacher class assignments (no snapshots): enrollment grants prospective visibility, un-enrollment revokes it, and append-only HumanMark history is never erased (honesty rule). Marking states, evidence contract, gate math, and T-029 acceptance criteria are all unchanged — this is a scoping decision, not a semantics change.

The complete decision record is canonical in `ADR-027-TEACHER_MARKING_QUEUE_SCOPING.md` (standalone file remains the authority).

**Scope guard:** decides WHO sees learner answers on teacher surfaces and WHEN teacher marking is required (classroom scope only, never for independent learners); does not design the Class entity, change marking states/gate math/evidence semantics, or expand Cycle-1. Conflicts re-open this ADR, not the implementation.

## ADR-028: Learning Hub import into syllabai-web — 39-course read-only resource hubs under the ADR-019 waiver

**Status:** Accepted (operator decision, trace 1a0e721469ee8ef5)
**Date:** 2026-09-28

The Learning Hub frontend (built in `syllabai-demo`) is imported into the production frontend `syllabai-web` (web `f041237`): all 39 course bundles serve as read-only resource hubs (revision notes, exam questions with self-marking, flashcards, past-papers viewer, practice papers, specification reader, strengths & weaknesses) under `/courses/*` + `/dashboard`, alongside the demo's dual-theme design system (SME default + Quiet Green, each light/dark) adopted as web's global design system. The operator's three decisions on the record: (1) the ADR-019 scope guard is waived "for now" for these read-only hub resources — all 39 courses serve, the pilot remains 4CH1 Chemistry (course `igcse-chemistry-19`, official Pearson tree, 182 spec points); (2) SME corpus licensing is operator-attested ("we have permission from SME", 2026-09-28; contract available from the operator on request — archive it with ADR-013's record when convenient); (3) both demo themes with their dark modes are the adopted design system.

**What this decision does NOT change — the boundary that keeps it a waiver, not an expansion:** core's Cycle-1 scope is untouched. Nothing was ingested into core — no new subject, paper, document, chunk, or KG node; the 38 non-pilot courses exist only as web-served committed content bundles that never touch the retrieval corpus, the KG, learner state, or evidence. The pilot's learner model, serving gates (VALIDATED-only), bench artifacts, and r6 substrate are byte-unaffected. Learner progress on hub surfaces is localStorage-SIMULATED and labelled as such until the 4CH1 bridge tranche wires the hub overlay to core's real BKT/decay state and core serves the needed contracts. AI on hub surfaces flows exclusively through core: the demo's self-hosted `/api/ai/*` endpoints and their frontend-held keys were NOT imported; the note-anchored CLA mirrors the workbench's `api.claAsk` NOTE_SECTION contract (fail-closed until core serves that kind at runtime); AI marking on bundle questions is explicitly off (core Smart Mark requires core question IDs) — self-mark (reveal + award) is the hub marking path.

Hardening closed at the import seam (demo gaps the promotion plan flagged): every corpus HTML render passes a `rehype-sanitize` allow-list (the demo carried unsanitized `rehype-raw`); the demo's upstream `rehype-katex` is replaced by web's local `rehypeKatexMhchem` (s142) so `\ce{}` chemistry renders on one shared katex instance; the Neon direct provider is not ported (frontends never bypass the core domain layer). Verified: tsc + eslint clean, production build green (25 routes), browser-verified (courses directory, pilot hub, note reader KaTeX, flashcards, past papers, both themes + dark, workbench regression-clean). NOT imported (later tranches, tracked in TODO): teacher surfaces (need core-RBAC re-gating), KG/graph-explorer/experiments visualizers, streamed tutor (core has no SSE), flashcard evidence class, ADR-021 content packages for the 80 MB bundle payload.

**Scope guard:** this ADR authorizes web-served read-only resource hubs on committed bundles under the operator's explicit waiver. It does not authorize bulk ingestion into core for any non-4CH1 subject, does not change the pilot population or its agents, and does not by itself wire the hub to the learner model — the 4CH1 bridge and every core-contract addition remain separately-scoped tranches.

## ADR-029: syllabai-demo promoted to the product frontend as the new repo SyllabAI/syllabai-hub; syllabai-web demoted to the internal teacher/ops console

**Status:** Accepted (operator decision, trace 1a0e747677812df5)
**Date:** 2026-09-28

After the ADR-028 import landed (web `f041237`), the operator judged the adapted result ("You did not implement syllabai-demo's UX flow") and reversed direction: promote the demo itself rather than keep porting its surfaces into web. The promotion assessment (same trace) confirmed the reverse graft is the cheaper direction — the expensive asset (the full 14-route-group UX flow: landing, student/teacher login split, learner workspace, tutor center, teacher workspace, KG labs) stays intact by construction, and what gets grafted is ~3.7K lines of mechanical, testable plumbing behind existing seams (the data-provider ladder, the 3-file fs coupling, the AIProvider boundary). The demo's own `docs/FRONTEND_PROMOTION_PLAN.md` (2026-09-18, PROPOSED) anticipated exactly this move and its gap analysis + Phase 0–3 skeleton was adopted as the execution plan.

**The decision (operator, verbatim intent):** create a new repo `SyllabAI/syllabai-hub` by cloning `syllabai-demo` at `a8f8fba` (full history preserved; `syllabai-demo` frozen as the prototype playground), and promote the clone as the main product frontend connected to core. Commits authored as `nawaf-al-hussain`. **Repo identity (the promotion plan's Phase-0 Q1) resolves as:** hub = the product frontend (students + teachers live here; the 4CH1 pilot runs here); syllabai-web = the internal teacher/ops console (Smart Mark, marking queue, decay ledger, class intelligence — already core-wired; product-surface development there is frozen; its ADR-028 import stands as the console's resource-hub view); Neon-direct mode is deprecated in hub (data ladder: `mock | core-api` only).

**What the promotion landed (hub `a8f8fba..700c881`, 4 commits, CI green):** (1) rebrand to SyllabAI Hub + removal of the local AI and DB stacks — `z-ai-web-dev-sdk`, Prisma, drizzle, Neon provider, `next-auth` dep, `db.ts` all deleted; zero LLM keys in the repo or its env (R3). (2) The math pipeline swapped to web's s142-hardened set: katex 0.16.23 + local `rehypeKatexMhchem` + a `rehype-sanitize` allow-list after `rehype-raw` (the demo's stored-XSS surface closed). (3) Real core auth: web's 71-method api client + session store ported; the mock TEACHER-1 persona replaced by a session-backed identity (core `UserView.roles`, TEACHER/ADMIN → teacher workspace); login/register hit core's AuthController with Render-wake on mount; `RequireAuth` UX gates on `/tutor`, `/assistant`, `/learner` and a teacher-layout RBAC gate on `/teacher/*` (core enforces authorization server-side on every call). (4) All AI through core proxies: `/api/ai/chat` forwards the learner JWT to core `POST /api/v1/tutor/ask` and adapts the answer into the SSE reader contract (citations mapped, history `{content}`→`{text}`); `/api/ai/cla` maps note→NOTE_SECTION (forwarded, lights up when the serving lane lands), topic→KG_TOPIC (topicNodeId resolved through core's knowledge tree by code, rootId via `subjects()`), question→honest fail-closed guidance (SME question IDs don't map to core questions yet); `/api/ai/mark` reports unavailable (self-mark is the path — f041237 precedent). (5) CI (`hub-ci`: bun frozen-lockfile → lint → corpus-gated type-checked build), eslint toolchain pinned to web's exact versions, fresh `bun.lock`.

**Verified end-to-end (production build on :3100 against live core):** landing/courses/notes (KaTeX 20 rendered, 0 errors, mhchem live), flashcards, exam questions, past papers; **real core register + login** (fresh verification account `hub.promotion.verify@syllabai-test.dev`, roles STUDENT); **tutor through core** — a 4CH1 states-of-matter answer streamed with numbered citations and the core provider badge (groq — proof the generation ran in core's LlmProvider chain, not locally); **topic CLA through core** — the KG_TOPIC anchor resolved and core's honest anchored-refusal rendered; teacher route correctly gated for a student account; signed-out tutor shows the sign-in prompt; both themes + dark modes verified; zero console/page errors throughout.

**Boundary (carried from ADR-028 unchanged):** core's Cycle-1 scope is untouched — nothing ingested, the 38 non-pilot courses remain bundle-served read-only resources, hub learner progress stays the labelled SIMULATED overlay until the 4CH1 bridge, and the pilot's gates/bench/r6 substrate are byte-unaffected. **Deployment prerequisites (operator actions):** create the Vercel project for `SyllabAI/syllabai-hub` (env: `NEXT_PUBLIC_API_BASE_URL`, `SYLLABAI_CORE_BASE_URL`, `HUB_DATA_MODE=mock`) and add the hub's production origin to core's `SYLLABAI_CORS_ORIGINS` on Render (browser→core calls are direct, as in web).

**Follow-up tranches (re-scoped from ADR-028's list, tracked in TODO):** the 4CH1 real-learner-model bridge (attempts → core evidence, overlay → core BKT/decay, spec-code↔KG-node mapping + question-ID bridge); core contracts still missing (tutor SSE streaming, NOTE_SECTION serving, flashcard ratings evidence, note helpfulness votes, assignments, Ebbinghaus review queue, course-stats); teacher workspace surfaces onto core RBAC data; ADR-021 content packages for the 80 MB bundle payload + perf pass; a11y audit + E2E suite (promotion-plan Phase-1 remainder); repo-map/PROJECT_CONTEXT registration of the new repo in the master pack.

**Scope guard:** this ADR records the frontend repo-identity pivot and the promotion hardening already landed. It does not change core's Cycle-1 scope, does not ingest anything, does not by itself wire the hub to the learner model, and does not retire syllabai-web (it remains the internal console and the Smart Mark/marking home). Every core-contract addition and the 4CH1 bridge remain separately-scoped tranches.

**Tranche 4 landed (2026-09-28, same trace — the 4CH1 real-learner-model bridge + production deployment):** hub `700c881..e471e08` (hub-ci green). (1) **Question identity bridge** — `GET /api/core/questions` joins every pilot corpus question to core's SME question-bank rows server-side (verified 1:1 against production: 28 topics, 524 questions; family `sme-eq-<topicSlug>-q<order>` ↔ core's `external_ref`/`QuestionFamilyView`, MCQ parts ↔ member rows by order + marks, structured parts ↔ the structured member's lettered parts by order + marks, option labels A–D ↔ option UUIDs). Any question the join cannot verify stays local-only — never fabricated evidence. (2) **Real attempts** — MCQ submits fire `POST /api/v1/attempts` (fire-and-observe beside the local instant mark; response-time telemetry from mount to submit); structured questions get the full core loop: Submit answers (`/attempts/structured`, typed answers saved synchronously so a fast submit can never send stale text) → Smart Mark (`/learners/me/attempts/{id}/smart-mark`, κ-gate honesty shown as authoritative/indicative) → per-part mark-point breakdowns → Explain my feedback / Improve my answer coaching buttons. (3) **Learner model reads** — the knowledge-graph overlay and the My State / History drawer derive from core's read models (`/learners/me/state`, `/knowledge-graph?rootId`, `/attempts`) when signed in on the pilot: same overlay contract + drawer shapes, provenance labelled `CORE_MEASURED` (new badge tier) vs `SIMULATED`; a topic-mastery section surfaces core's topic-granular evidence honestly (core's assessment evidence fires at topic nodes, so per-spec-point painting stays "Not measured" until point-granular evidence exists — no fabricated precision). (4) **Note views** on the pilot report to core's revision-notes progress. (5) Everything degrades honestly: signed-out pilot shows the sign-in prompt; non-pilot courses are silently local-only (the ADR-028 boundary); core down falls back to the simulated derivation labelled as such.

**Two bugs found and fixed on the way:** (a) core `2a1676a` — `TelemetryEvent`'s constructor used `Map.copyOf`, which rejects null VALUES; the attempt contract makes `confidence` optional, so every confidence-absent submission 500'd AFTER the attempt row was saved (found live from the bridge; regression test added, TelemetryServiceTest 12/12). (b) hub `e471e08` — the tutor composer passed `onSend={send}` and the button called `onSend(clickEvent)`, making the click event the `override` question → `.trim()` TypeError on every Send-button click (pre-existing since the promotion; Enter-to-send had masked it in verification).

**Deployment (the operator prerequisites above are now executed and retired):** Vercel project `syllabai-hub` created (team workspace, linked to `SyllabAI/syllabai-hub` main, env: `NEXT_PUBLIC_API_BASE_URL` + `SYLLABAI_CORE_BASE_URL` = `https://syllabai-core.onrender.com`, `HUB_DATA_MODE=mock`) — **the product frontend is live at `https://syllabai-hub.vercel.app`**; core's `SYLLABAI_CORS_ORIGINS` on Render now carries `https://syllabai-hub.vercel.app` alongside web + localhost (dev :3000 and :3100). **Verified live on production:** register + login through core, pilot bridge banner, MCQ recorded to the real learner model, structured submit + Smart Mark (authoritative per-part decisions through core's LLM chain), feedback explanations rendered, KG My State drawer (`CORE_MEASURED`, topic mastery from real attempts, History listing the session's attempts with timestamps), tutor cited answer (groq badge), CLA anchored + cited, non-pilot course silent local-only, signed-out honest prompt, zero console errors. Local verification (dev :3100 against live core) covered the same matrix plus the theme system.

**Tranche 4.1 landed (2026-09-28, operator trace 1a0e8568eb6bb545 — KG course scoping + real-model My Progress):** hub `e471e08..d2681aa` (hub-ci green). Operator direction: the knowledge graph must show only the subject it was opened for (no browsing other courses' graphs from there), and the learner-model surfaces must never display fabricated numbers. (1) **KG single-course scoping** — the all-courses switcher (51 courses) is removed; the graph renders exactly the course it was opened for (`?course=` deep link, validated against the registry, pilot default), course pages link "View parsed spec" with their own slug, and the course is derived from the URL (not component state) so deep links stay reactive. The graph is a property of the selected subject, not a browsing surface. (2) **Renderer honesty hardening** (`public/kg/openhuman-course-explorer.html`) — in loader mode (any `?course=` open) the embedded OpenHuman sample map is dead on arrival: `LIVE_LEARNER` defaults to `{}`, so no fabricated mastery can ever paint — including the previously-uncovered window where the host's derivation fails or the file is opened standalone (verified: `learner({pointId:'1.1'})` returns null where the sample carries mastery 86%). The legend and node-peek texts are provenance-aware (`core` = "Measured from your SyllabAI account — real attempt evidence." / `simulated` = browser-local overlay / `unavailable` = nothing painted) instead of the unconditional "Demo overlay only". The byte-faithful inline mode (no query) is untouched. (3) **Host always posts** — `syllabai-kg:learner` is posted once the derivation resolves, including the bridge-error case (empty overlay + `provenance:"unavailable"`), so the graph, drawer and page can never disagree and the sample map can never resurface. (4) **My Progress rewired** (`/learner`) — the old simulated skill-state viewer (fabricated BKT percentages, fake T-C11 probabilities) is retired; the page now renders the SAME derivation as the KG (stat tiles, topic mastery, review queue, spec-point mastery table, history — reusing the drawer's exported tab components, one derivation and one UI) with `CORE_MEASURED`/`SIMULATED` provenance, an honest unavailable panel on bridge failure, and the "Demo model — simulated parameters" footer shown only on the simulated path. `PILOT_COURSE_SLUG` exported from attempt-bridge as the single learner-model scope until more courses get a real join. Verified on a production build against live core: KG deep links (pilot + IAL Biology), no switcher, provenance legend, standalone explorer honest default, signed-out gate, fresh account `CORE_MEASURED` honest zero-state, one real MCQ attempt → core (total 1) → My Progress topic mastery "States of matter 11% → 11% · low · 1 attempt" + History event ("not correct · 0/1") + KG chip "live · my state" + drawer `CORE_MEASURED`; tsc/eslint/build clean, zero console errors.

**Tranche 4.2 landed (2026-09-28 — the teacher console port; the last web-only capability moves to the hub):** hub `d2681aa..e83dfd7` (hub-ci green, Vercel deployed). With this tranche every teacher capability the demoted web console served is reproducible on the hub; web's product role ends (it remains the frozen internal ops console). (1) **Marking review** (`/teacher/marking`, ported from web's T-029 `TeacherReviewView` with its honesty rules intact) — class list, the paper-grouped queue-v2 with backend-owned pagination (G-5), answer detail with Run Smart Mark, bounded batch smart-mark per paper group (partial success reported), human-mark overrides with per-point κ-pairing decisions seeded from the smart breakdown, Record & next along the deterministic queue chain, the κ gate with real ALL/paper scope (honest 404 "none recorded" / 409 "no paired decisions" / 500-surface-the-reason trichotomy) and marking throughput. (2) **Class intelligence** (`/teacher/class`, ported from web's sprint-2 §2–§5 `ClassIntelligenceView`) — subject selector over core subjects (hub loads them itself; defaults to the first with a KG root — production: 4CH1 + CHM), overview stats, weak-prerequisite areas, topic heatmap (curriculum / weakest-first ordering), §5 drill-down (prerequisite chain, affected learners, representative evidence, remediation assembly through the validated-question serving boundary), the learner attention table, and the v75 class graph — the kg-explorer engine ported verbatim (5 self-contained files) with `classGraphHost` trimmed to the one host this surface needs, rendering REAL aggregates (class mastery bands, misconception signals, reviews due, engagement) with drill-down actions wired back into the tables. Evidence-semantics banner preserved verbatim: mastery = graded BKT evidence, misconceptions = BDT estimates, tutor asks are engagement never weakness, unmeasured reads unmeasured. (3) **SAMPLE class graph retired** — the demo's simulated class lens is superseded; `/teacher/class-graph` is a URL-level 308 to `/teacher/class` (next.config redirects, fires before the auth layout so it works signed-out; the in-page `permanentRedirect` alternative was rejected because the teacher layout's client-side RBAC gate swallowed it for non-teachers). The overview's SAMPLE cohort snapshot is retired (its "real analytics need accounts + server-side progress" caption became false the moment this tranche landed) and replaced by LIVE console cards; corpus tools (Test Builder / assignments / validation) stay honestly labeled local-demo. Verified against live core: fresh-STUDENT role gate on every `/teacher` route, signed-out sign-in gate, 308 redirect, zero console errors; API-level RBAC proof (student token 403 on all teacher endpoints, anonymous 401, subjects 200); positive data path proven by the re-dispatched production probes with pilot-teacher credentials — s2-class-probe ALL OK (enrolled=223, 107 with evidence, 26/329 topics measured, drill-down affected=5 evidence=20 servable=35) and s2-marking-probe ALL OK (queue-v2 82 pending over 5 contiguous oldest-first paper groups, throughput states match, unknown-id batch guard fails closed); tsc/eslint/build clean. The teacher-eye browser E2E (marking a real answer, recording a human mark, drill-down navigation) is packaged for the operator — teacher credentials are operator-held by design.

**Tranche 4.3 landed (2026-09-28, operator trace 1a0e8814f9ce8fbd — tutor SSE streaming, parallel lane; recorded in TODO):** core `1357408` + `6a4931d` (core-ci green, Render live) and hub `e784c1c..9d48a12` (hub-ci green, Vercel live) — the first missing core contract. True token streaming end-to-end (`POST /api/v1/tutor/ask/stream` through Spring AI StreamingChatModel; retrieval extracted into `KaRagService.prepare()` shared with the blocking `/ask` so the two modes cannot drift; StreamSanitizer holdback pins streamed hygiene to the blocking path; citations stream before generation; the free-chain failover contract preserved up to the first token; `/ask/stream` joins the R8 LLM tier; the blocking `/ask` byte-identical). The hub's `/api/ai/chat` pipes core's SSE verbatim with a 3-line spec-compliant field parse (Spring's SseEmitter writes `event:name` with no space), 15s heartbeats, client-cancel release, and a blocking-`/ask` fallback on legacy responses. Prod-verified: 135-event served stream, 4-event deterministic refusal, full-chain E2E through Vercel; +27 core tests, suite 1002/1002.

**Tranche 4.4 landed (2026-09-28, operator chat bb263437 — the demo frontend-fix wave):** hub `9d48a12..8cc598a` (hub-ci green, Vercel deployed). The syllabai-demo UI-fix wave (P1 `501782b` + P2 `648e2ae` + scope decision `c6251ff` + blueprints regen `8c2c38c`) is assessed file-by-file and ported: (1) **P1 mobile honesty** — the course drawer closes only on real navigation (expand-caret taps used to unmount it and reset TopicTree state, leaving no topic beyond the auto-expanded one reachable on phones); note pagination truncates at 48% per button with real ellipsis (two nowrap titles measured 402-426px in the 343px article column); `.katex-display`/`.prose-sm pre` scroll in place; signed-out phones get a Sign-in item in the study-tools menu (the header button is `hidden sm:inline-flex`). (2) **P2 teacher honesty** — swallowed fetch errors surface as destructive Alerts with retry guidance (dead `error: boolean` flags retired) on the workspace, assignments and validation surfaces; the validation queue's comment drafts are per-item `Record<resourceId,string>` (a single shared string leaked one row's text into every pending input and into whatever verdict was committed next). (3) **P2 touch/dvh** — dialog/sheet built-in closes 36px hit area, PDF toolbar/find 36px, MCQ letters 44px, test-builder floating pill wraps below ~510px with icon-only undo, paper-viewer Split tab gating unified on lg (was a silent no-op in the 640-1023px band), dvh cascade on viewers/dialogs. (4) **Past-papers scope purity (demo `c6251ff`)** — 4CH0 `legacySpecs` promoted onto double-award chemistry (its Paper 1 IS 4CH0 Paper 1, covers-print-both-codes evidence; unlocks the Jan 2013 1C recon); single-award 2-series papers stay OUT of Double Award Mode 1 on purpose (the qualification assesses Paper 1 only) and unmatched recons carry the derived "Single-award paper" chip instead of an unexplained absence — scope purity beats interactive counts; blueprints regenerated against the shared corpus tree `029c6ec9` (the hub had been one regen behind the same tree: +1 paper, 5 refined). (5) **One-way app-shell adaptation** — the demo mirrors Sign-in AND Sign-out below sm; the hub's identity dropdown renders at every width, so only the signed-out Sign-in mirror was ported (no duplicate Sign-out). (6) **Three hub-specific 375px defects the wave's probe method exposed** (invisible to the demo — its header shows no identity on mobile): the app header now fits signed-in phones (wordmark " Hub" suffix and icon-only study-tools trigger below sm, name `max-w-16`); the teacher identity card shrinks (`min-w-0` — its nowrap min-content ran 130px past the viewport); the workspace status badge wraps. Verified on the prod build: tsc/eslint/build clean; runtime probes at 375px/1440px — drawer survives expand taps and closes on leaf links, pagination ellipsizes po=0, served-CSS KaTeX scroll-in-place, signed-out mobile Sign-in item, per-item drafts don't leak (row1 typed, row2 empty), destructive Alerts on aborted fetches across all three teacher surfaces, 4CH0 papers + 24 scope chips + 40 legacy badges in production SSR, the drawer close-on-link guard confirmed in the production JS bundle, po=0 across 12 probed pages, zero console errors. The first hub-ci run on `8cc598a` failed on a transient npm-registry 404 (`typescript-eslint-8.71.0.tgz`, metadata live/tarball absent — no dependency was touched by this tranche); the re-run is green. Out of scope, flagged: the demo's next-best-actions card + cascading add-course overlay (`8bfcdb7`, +1147 lines — a feature wave, not fixes).

**Tranche 4.6 landed (2026-09-28, operator chat bb263437 "Add the NBA card + add-course overlay"; the hub commit message self-labels 4.5 — renumbered here to keep the ledger linear after the parallel flashcards lane's TODO-only 4.5 row landed first):** hub `e225a33..2b06683` (hub-ci green, Vercel deployed and probe-verified). The demo's feature wave `8bfcdb7` (flagged out of scope in 4.4) is ported: (1) **Next-best-actions card** (web T-033 / F-092 / ADR-017 parity, client-derived) — five ranked action tiers from the learner's own browser-local evidence chain (progress store × kg-learner-bridge × buildOverlay × forgetting-decay): misconception remediation (active sim states, SIMULATED-labelled), review-due topics, problem-question retry (<50% marked), low-mastery practise, note coverage; ranked across all my subjects, deep-linked to notes/topic player/tutor, honest empty states, deterministic policy footer with reason codes. (2) **Cascading add-course overlay** (board → level → subject, registry-shaped: Edexcel lane + IGCSE 36 / IAL 13 census chips + filterable lane rows with exam codes) replaces the dashboard's full-registry "Add a subject" catalogue; the dashboard lists ONLY added subjects; header button, "Got another course?" slot and empty-state CTA all open the overlay. (3) **Bridge API** grows `pointTexts` (182 spec-point statements) + `noteTitles` (112) — union-merged with the parallel flashcards lane's `pointSubtopics` anchor join (one conflict hunk, resolved as the union; their 909 anchored `flashcardCodes` and my fields coexist in one payload). (4) **Port discipline** — `progress.ts` keeps the `syllabai-hub:progress:*` localStorage key (porting the demo key verbatim would have wiped every prod user's saved progress); user-visible "The demo registry covers…" copy adapted to "The registry covers…" (comment-level demo references kept per the 45-file house convention); the 32-pass harness ports with hub keys + one hardening (pre-click scrollIntoView — the Chemistry 4CH1 row sits below the 42dvh fold at small viewports, and a coordinate click that misses lands on the dialog backdrop, closing the overlay and starving every downstream check). (5) **Latent mobile defect found and fixed (inherited from the demo, invisible to the demo's own harness)**: `DialogContent`'s `grid` track sizes to grid-item min-content, and the overlay's nowrap `truncate` lane labels ("Science (Double Award) — Modular 2024, Chemistry Unit 2" = 392px) drove the track to 503px — at viewports below ~560px the dialog renders full-bleed with the right-hand Add buttons genuinely OFF-VIEWPORT (users cannot tap them), while `overflow-x:auto` on the lane list plus fixed-position dialog metrics (which don't contribute to `documentElement.scrollWidth`) kept every po probe green. Fixed at the component level — `[grid-template-columns:minmax(0,1fr)]` on `ui/dialog.tsx` (rendering-neutral at ≥sm where the track equals the max-width either way; protects every dialog consumer from the same blowout class) — plus the overlay drops its unconditional `max-w-lg` override for the base's `max-w-[calc(100%-2rem)]` mobile margin cap (house convention: consumers override with `sm:max-w-*`). Post-fix geometry: 375px dialog 343 wide with 16px margins, lane list 293 = scrollWidth (no hidden overflow), Add button in-viewport; 1440px dialog 512, unchanged. (6) **Verification** — tsc/eslint/build clean; harness 32/32 ×3 runs; s132 probe 18/18 (po=0 at 375px/1440px, lane list scrolls in place, roster persistence, seeded-evidence NBA rows with SIMULATED labels, no console errors); dialog-consumer regression check (question-player "View answer" dialog fits at 375px, no errors). Vercel verified live: bridge serves pointTexts/noteTitles on prod, NBA card in dashboard SSR, old catalogue heading gone, overlay copy + dialog grid fix both present in the deployed JS chunks. **Parallel-lane note:** the flashcards lane's hub commit (`ed28c72`, "ratings record to the learner model") self-labels "tranche 4.4", its ledger TODO row records 4.5 (TODO-only — no DECISIONS paragraph), and this ledger's 4.4 is the demo fix-wave port; its work is fully preserved in the 4.6 rebase union and its numbering drift is recorded here rather than rewritten. Polish-list additions from this tranche's probes: unknown exam-question topic slugs serve HTTP 200 with a 404 UI (pre-existing soft-404 on both repos — the demo harness's fake seed slug `1-1-states-of-matter` exploits it; real recorded attempts use the `--exam-questions`-suffixed slugs); question-player po=36 at 375px (pre-existing — no dialog in DOM, cannot be the dialog change; likely the Q3/Q22 tables).

**Tranche 4.8 landed (2026-09-28, operator trace 1a0e947969e75df1 "Start with 1 (Ebbinghaus queue)"; hub `2cd4a28` self-labels 4.6 — renumbered per the 2fa35a8 precedent, see the TODO row):** hub `ed28c72..2cd4a28` (hub-ci green, Vercel live) — the Ebbinghaus flashcard review queue, the consumer the tranche-4.5 rating trail was explicitly wired for. Design ruling: the queue is derived from the DEVICE-LOCAL overlay trail, not the core `flashcardRatings` view — the local store holds every rating this browser ever made (complete per-device history), while core serves only the latest 50 events for the learner model; core stays untouched this tranche (no deploy, no migration), and a future cross-device scheduling tranche can merge the core trail on top without shape changes. The schedule is an expanding ladder on the binary self-report (still-learning → due now; know-streak n → 1·2·4·8·16d, 32d cap; re-rate resets; legacy trail-less records = conservative streak 1) — deliberately NOT the forgetting.ts decay arithmetic, which stays anchored to measured attempts: two evidence classes, two arithmetics, one UI keeps them visually distinct ("Flashcards due" section sits beside the mastery review queue, footer states the timing-only rule). The trail is append-only and bounded (10) — bounded because the interval caps at streak 6, so a capped trail can never understate a due date. Surfacing is three-level (drawer per-deck summary + deck-player due-first run + index per-deck chips) so the queue is actionable at every altitude, and `cardReviews` is stamped at the single `useLearnerState` convergence so the core/sim drawer paths cannot disagree. Verification: 27-pin bun harness ALL GREEN + eslint + type-checked build on the merged base (the concurrent e225a33..b3b76e7 wave was fast-forwarded and stash-popped mid-flight; union verified hunk-by-hunk on the shared progress.ts); Vercel probe confirmed the new copy and scheduler markers in the served chunks.
