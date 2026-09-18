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
