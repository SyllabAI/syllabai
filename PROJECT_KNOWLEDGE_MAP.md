# SyllabAI Project Knowledge Map

**Status:** Canonical navigation/index document  
**Purpose:** Locate durable project knowledge without relying on conversation memory.  
**Last reviewed:** 2026-09-15

## 1. Purpose

This file is an **index, not a second source of truth**. It answers one question:

> If an agent, developer, or future conversation needs to understand an important part of SyllabAI, where is the authoritative information?

The referenced artifact remains authoritative for its subject. Do not copy large bodies of those documents into this map merely for convenience.

SyllabAI conversations, agent sessions, PR discussions and temporary workspaces are working interfaces. They are **not** canonical project memory. Important knowledge becomes durable only when it is persisted to an appropriate repository artifact.

## 2. Source-of-truth hierarchy

When sources overlap, use the project's existing hierarchy and claim-status rules:

1. Research papers — scientific claims, hypotheses, operational definitions and evaluation design.
2. `MASTER_SPEC.md` — engineering architecture and product/technology source of truth.
3. Canonical architecture documents and addenda — detailed contracts for their named subsystem.
4. `DATA_MODEL_ERD.md` — current implementation evidence versus target architecture for data-model questions.
5. Definitive feature tracker — feature inventory and execution state.
6. Accepted research dossiers — external research and integration guidance, subject to their stated status.
7. `DECISIONS.md` / ADRs — explicit architecture decisions and scope constraints.
8. Agent addenda / implementation contracts — binding implementation rules for the relevant subsystem.
9. `PROJECT_CONTEXT.md` — cross-document orientation and current project map.
10. `WORKLOG.md`, `PROGRESS.md`, `TODO.md` and release/evidence artifacts — living execution state and historical evidence.
11. Chat/agent conversation — working context only; not durable truth unless explicitly persisted.

If two canonical artifacts conflict, **do not silently choose one**. Record the conflict and update the appropriate decision/architecture artifact.

## 3. Canonical project orientation

| Area | Canonical artifact(s) | Role |
|---|---|---|
| Overall engineering architecture | `MASTER_SPEC.md` | Engineering source of truth |
| Agent operating rules | `AGENT.md` | Binding implementation workflow and invariants |
| Architecture decisions | `DECISIONS.md`, `ADR-*.md`, named decision records | Accepted/rejected decisions |
| Cross-project orientation | `PROJECT_CONTEXT.md` | Durable context map |
| Feature inventory | `backlog/syllabai-master-project.xlsx` + TSV/addenda | Definitive feature tracker |
| Execution history | `WORKLOG.md` | Historical project record |
| Current execution state | `PROGRESS.md`, `TODO.md` | Living state/work queue |
| Repository research | `REPOSITORY_RESEARCH.md` | External implementation/license research |
| Platform/provider research | `PLATFORM_RESEARCH.md`, current AI runtime/provider report | Provider and platform evidence |
| Content representation/package | `CONTENT_COMPILER_AND_PACKAGE_ARCHITECTURE.md`, `CONTENT_PACKAGE_V0_1.md`, ADR-021 | Markdown artifacts, PostgreSQL boundary and portable SQLite package direction |

## 4. Curriculum, subject and knowledge graph

| Area | Canonical artifact(s) |
|---|---|
| Subject-first product architecture | `SUBJECT_ARCHITECTURE.md` |
| SpecificationPoint model | `SUBJECT_ARCHITECTURE.md`, `MASTER_SPEC.md`, ADR-014 |
| Teacher/classroom lens over shared graph | `TEACHER_ARCHITECTURE.md`, ADR-015 |
| Knowledge graph build/context | `KNOWLEDGE_GRAPH_BUILD_PLAN.md`, `KNOWLEDGE_GRAPH_CONTEXT.md`, relevant KG evidence/releases |
| Current corpus/resource mappings | `syllabai-resources` canonical corpus and its QA/graph artifacts |
| Learner KG/state overlay | `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md`, learner/KG implementation contracts |

**Invariant:** authoritative educational KG semantics are distinct from retrieval-derived relationships. Learner state is an overlay and does not mutate canonical curriculum content.

## 5. Learning evidence and learner model

| Area | Canonical artifact(s) |
|---|---|
| Question Attempt / Learning Log | `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` |
| Agent implementation rules | `LEARNING_EVIDENCE_AGENT_ADDENDUM.md` |
| Recommendation system | `RECOMMENDATION_SYSTEM_ARCHITECTURE.md`, `RECOMMENDATION_SYSTEM_AGENT_ADDENDUM.md`, ADR-017 |
| Learner Interaction Memory | `LEARNER_INTERACTION_MEMORY_ARCHITECTURE.md`, `MASTER_SPEC_ADDENDUM_1.4_LEARNER_INTERACTION_MEMORY.md`, `AGENT_LEARNER_INTERACTION_MEMORY_ADDENDUM.md` |
| Learner interaction implementation | `syllabai-core/docs/LEARNER_INTERACTION_MEMORY_IMPLEMENTATION.md` and core agent rules |

**Invariant:** raw conversation is history/audit data; extracted interaction evidence is a candidate signal with provenance; learner patterns and mastery are derived through governed learner-model logic. Chat output does not directly mutate canonical KG or mastery.

## 6. Assessment, Smart Mark and exams

| Area | Canonical artifact(s) |
|---|---|
| Question identity/evidence | `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` |
| Smart Mark | relevant Master Spec feature contract + learning-evidence architecture + Smart Mark implementation in `syllabai-core` |
| Mock Exam Generator | `MOCK_EXAM_GENERATOR_ARCHITECTURE.md`, `MOCK_EXAM_GENERATOR_AGENT_ADDENDUM.md`, `DECISION_018_MOCK_EXAM_GENERATOR.md` |
| Past Papers | `syllabai-pastpapers` charter/data contracts + `Past-Papers` source corpus + ingestion/release evidence |
| Teacher Test Builder | `TEACHER_ARCHITECTURE.md` and canonical F-050 feature identity |

## 7. Retrieval, RAG and AI

| Area | Canonical artifact(s) | Status/role |
|---|---|---|
| RAG/retrieval research | `RAG_RETRIEVAL_RESEARCH.md` | Accepted research/architecture guidance; promotion requires benchmark evidence |
| Retrieval benchmark harness | `RETRIEVAL_BENCHMARK_HARNESS_SPEC.md` + `bench/` + `evidence/bench-001/` | T-C13 gate spec (PROPOSED v0.1); frozen gold-v1 set, snapshot snap-001, run records |
| Retrieval frontier prepared contracts | `RETRIEVAL_FRONTIER_PREPARED_PACKAGE_2026-09-17.md` | PREPARED (UNVERIFIED) contracts: T-C07 scoping, embedding runbook, T-C14 lexical (V27), T-C06 converter (V28); audit findings AF-1..AF-3 |
| Gemini File Search / Gemini Notebook architecture research | `GEMINI_FILE_SEARCH_AND_NOTEBOOK_ARCHITECTURE_RESEARCH.md` | Accepted research investigation; benchmark required; no production default yet |
| Educational Retrieval Engine | `ADR-020-EDUCATIONAL_RETRIEVAL_ENGINE.md` | Accepted architecture direction |
| Retrieval agent rules | `AGENT.md` RAG section and relevant core implementation contracts | Binding |
| Contextual Learning Assistant | `CONTEXTUAL_LEARNING_ASSISTANT_ARCHITECTURE.md`, `MASTER_SPEC_ADDENDUM_1.5_CONTEXTUAL_LEARNING_ASSISTANT.md`, `AGENT_CONTEXTUAL_LEARNING_ASSISTANT_ADDENDUM.md`, `syllabai-core/docs/CONTEXTUAL_LEARNING_ASSISTANT_IMPLEMENTATION.md`, `syllabai-core/docs/CLA_STEP1_RUNTIME_ACCEPTANCE.md`, ADR-022 | Steps 1–2 IMPLEMENTED/VERIFIED + §10.4 VERIFIED on both lineages (baseline `6092650` 44/44; final-lineage closure 29/29 after the groq-quota-blocked 4CH1-S1-e S-B check was closed by the sliced harness run) and extended to **37/37 VERIFIED with the QUESTION_PART gate (S-G 7/7) at core `d0dc00a`** — FOUR context kinds live (KG_TOPIC + PAST_PAPER_QUESTION + SPECIFICATION_POINT + QUESTION_PART: part-level anchor through canonical assessment FKs with a current-version relationship gate, part-scoped marking evidence, LEARNER_WORK evidence so CHECK can review the learner's own submitted work; live verification 9/9; three live-found product defects fixed honestly — lazy-proxy init, boot-killing JPQL, missing learner work), EXPLAIN/SUMMARIZE/HINT/CHECK, read-only tools, §7 deterministic leakage gate + CI-mandatory negative suite, LIM evidence, web Assistant panel with question+part selectors (`1f22113`); FIFTH context kind live: SMART_LESSON (core `50dfa59`, live verification 15/15, S-H evaluation 33/33 GREEN — VERIFIED; web panel smart-lesson selector `4c3326a`, **in-browser VERIFIED 2026-09-16** on the main-lineage build × production backend — **production Vercel deployment REDEPLOYED and VERIFIED 2026-09-17** (deployed panel chunk `cf73528213c5da17.js` = the exact `4c3326a` main-lineage content hash; re-confirmed in-browser on the deployed build: selector + anchored label + live grounded EXPLAIN, `cla_smartlesson_deployment_verification_20260917.log`); Actions quota RECOVERED 2026-09-16 ~08:47Z and the first real Docker-backed core-ci since the blackout ran on the E2 lineage (unit 540 green confirmed in CI; `SmartLessonFlowIT` 5/5 green) with 4 ClaFlowIT first-execution fixture defects recorded (HARNESS class, zero product defects — core-ci RED until fixed)) — the lesson anchor IS the resolved topic (the Smart Lesson surface is a deterministic smart-lesson/v2 projection, not an entity), with the learner's OWN deterministic lesson action on the context as framing state only; further context kinds remain contract-governed: NOTE_SECTION = SUBSTRATE-BLOCKED / architecture decision required (no note-content substrate exists) |
| E2 InterventionRun boundary | `docs/research/INTERVENTION_RUN_PROTOTYPE.md`, `syllabai-core/docs/INTERVENTION_RUN_ACCEPTANCE.md`, ADR: none (research prototype), core issue #19 | PROTOTYPE IMPLEMENTED / VERIFIED (unit 540 green + live 10/10 on production at core `02643ed`): recommendation-backed creation from the deterministic NBA PRACTICE action, learner API surface, ordered steps, evidence BY REFERENCE, append-only terminal history, DB-level mutation-boundary proof (run ops never touch learner state); two live-found product defects fixed (jsonb varchar write → `SqlTypes.JSON`; named resume-mismatch 409 swallowed) — the §14 promotion gate (PROTOTYPE → ACCEPTED) is the operator's decision, NOT claimed. **2026-09-17 reconciliation updates:** the first real Docker-backed CI execution (runs `35075687695`/`35077858230`/`35078454055`, 2026-09-16 — Actions quota recovered mid-day) ran `InterventionRunFlowIT` for the FIRST time: 2/2 flows RED, both classified HARNESS (fixture) defects with ZERO product defects — the deterministic NBA's first-rank action for the fixture's fresh two-zero-attempt state is `RETRY_PROBLEM_QUESTION` (the policy behaving deterministically; the fixture expected `PRACTISE_QUESTIONS`/`LOW_MASTERY`), and the paper-ingestion path creates the draft's Subject row WITHOUT a KG root so `createFromRecommendation` fail-closes 404 on the standalone anchor (correct product behavior; the fixture assumed the anchor is a subject root); unit 540 green CONFIRMED in CI; live 10/10 stands; core-ci is RED until the two fixtures are fixed (which also gates the CI-recovery runbook's "real-failure = stop" r3 pipeline). §14 audit: criteria 1–10 demonstrated, but the persistence/query-cost analysis precondition has NO artifact yet → **E2 NOT ready for ACCEPTED promotion; NOT claimed** |
| AI runtime/provider choices | `PLATFORM_RESEARCH.md` + ADR-009 (free-tier LLM chain) + `ADR-020-EDUCATIONAL_RETRIEVAL_ENGINE.md` (retrieval runtime direction) | Time-sensitive operational/research evidence |
| External RAG references | `RAG_RETRIEVAL_RESEARCH.md`, `REPOSITORY_RESEARCH.md`, `GEMINI_FILE_SEARCH_AND_NOTEBOOK_ARCHITECTURE_RESEARCH.md` | Reference only unless explicitly adopted |

### RAG invariant

The intended retrieval flow is:

```text
Learner query
  → intent/query understanding
  → curriculum + concept + learner resolution
  → lexical + semantic + metadata + authoritative-KG candidates
  → fusion/deduplication
  → SyllabAI-aware reranking
  → evidence/segment selection
  → evidence sufficiency
  → grounded downstream AI
  → claim/citation validation
```

Do not reduce SyllabAI to generic `PDF → chunks → embeddings → vector DB → LLM`.

## 8. Teacher and production systems

| Area | Canonical artifact(s) |
|---|---|
| Teacher product architecture | `TEACHER_ARCHITECTURE.md` |
| Teacher validation | teacher-workbench repo contracts, release/evidence packs, relevant core validation contracts |
| V20 production reconciliation | `V20_PRODUCTION_RECONCILIATION_2026-09-15.md` — cross-repository reconciliation of core fixes, teacher verification battery, workbench deployment repair, and remaining evidence gaps |
| Production/project coordination | `.syllabai/project-state.yaml`, `.syllabai/agent-registry.yaml`, `.syllabai/locks.yaml`, `.syllabai/tasks/`, `.syllabai/contracts/`, `.syllabai/evidence/` |
| Deployment state | release records, deployment evidence, `PROGRESS.md`, current project state |
| Operational verification | `.syllabai/evidence/` and release-specific evidence artifacts |

Operational evidence must not be confused with architectural intent. A feature can be designed but not implemented, implemented but not deployed, or deployed but not fully verified.

## 9. Repository ownership map

| Repository | Durable knowledge owned there |
|---|---|
| `SyllabAI/syllabai` | Master architecture, ADRs, research, backlog, cross-project contracts and project knowledge map |
| `SyllabAI/syllabai-core` | Backend implementation, domain contracts, migrations, AI/tutor/learner/assessment implementation evidence |
| `SyllabAI/syllabai-web` | Frontend implementation and UI contracts |
| `SyllabAI/syllabai-parser` | Offline parsing/OCR/document-processing implementation and evidence |
| `SyllabAI/syllabai-resources` | Validated content corpus, specification/resource mappings and corpus QA |
| `SyllabAI/syllabai-pastpapers` | Normalized past-paper data, manifests, provenance, quarantine and ingestion evidence |
| `SyllabAI/Past-Papers` | Official source corpus and source provenance; no application architecture |
| `SyllabAI/syllabai-teacher-workbench` | Teacher validation workbench implementation, staging contracts and workbench production evidence |

Cross-repository architecture belongs in the central `syllabai` repository. Repository-local implementation knowledge belongs with the implementation repo and should be linked from the central map when it is important to the whole system.

## 10. Durable knowledge test

Persist a discovery when it can reasonably change a future implementation, research interpretation, product behavior, data meaning, safety boundary, deployment operation, or project decision.

Typical durable discoveries include:

- architecture decisions or constraints;
- accepted/rejected research conclusions;
- non-obvious invariants;
- important root causes and their evidence status;
- schema/data/provenance semantics;
- model/provider decisions and compatibility findings;
- retrieval/learner/KG semantics;
- security, privacy, validation or serving boundaries;
- major operational/deployment discoveries;
- scope changes;
- benchmark definitions and acceptance criteria.

Do **not** document every ordinary implementation thought. Temporary debugging, discarded alternatives and routine code discussion remain ephemeral unless they reveal a durable rule or lesson.

## 11. Conversation durability rule

A conversation may discover important knowledge, but the knowledge is not considered retained project knowledge until it is persisted.

Therefore:

```text
Conversation / research session
        ↓
Durability test
        ↓
Existing canonical artifact?
   ↙              ↘
 yes              no
  ↓                ↓
update it      create the smallest
               appropriate artifact
   ↘              ↙
      update this map if needed
              ↓
          commit / PR
```

Prefer updating an existing canonical artifact over creating a duplicate summary.

## 12. Claim/status discipline

Durable artifacts should distinguish at least the following where relevant:

- `PROPOSED` — idea under discussion;
- `ACCEPTED` — deliberate architecture/research decision;
- `IMPLEMENTED` — code/data exists;
- `VERIFIED` — evidence proves the stated claim;
- `INFERRED` — supported interpretation but not directly proven;
- `REPORTED` — reported by an agent/operator without independent verification;
- `UNVERIFIED` — known gap requiring evidence;
- `REJECTED` — explicitly not adopted.

Historical text must not be silently promoted to current truth.

## 13. Maintenance rule

When adding a new canonical cross-project artifact:

1. Give it a clear status and scope.
2. Link it from `PROJECT_CONTEXT.md` when it is part of normal project orientation.
3. Add it to this map when future agents need it to locate durable knowledge.
4. Link related ADRs/architecture contracts rather than duplicating their content.
5. If implementation behavior changes, update the relevant agent contract.
6. If the change affects the feature inventory, update the definitive tracker.
7. Preserve evidence/provenance and distinguish verified facts from inference.

This maintenance is part of the definition of done for durable architectural knowledge; it is not a requirement for routine code-only changes.
