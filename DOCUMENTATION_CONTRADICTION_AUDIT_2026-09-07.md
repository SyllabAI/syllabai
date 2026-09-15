> **HISTORICAL SNAPSHOT — annotated 2026-09-15.** This is a point-in-time record of 2026-09-07, preserved verbatim. Any statement here that "Cycle 1 = Edexcel IAL Chemistry" — and every scope statement derived from it — was superseded by **ADR-019 (2026-09-11)**: the Cycle-1 pilot subject is now **Edexcel International GCSE Chemistry (4CH1)**. Read as history, not as current scope; current scope lives in `MASTER_SPEC.md` section 39a and ADR-019.

# SyllabAI Documentation Contradiction Audit — 2026-09-07

**Audit date:** 2026-09-07
**Scope:** `MASTER_SPEC.md`, `AGENT.md`, `PROJECT_CONTEXT.md`, `DECISIONS.md`, `SUBJECT_ARCHITECTURE.md`, current backlog/addenda, and current T-029 product state.
**Purpose:** prevent AI/coding agents from following stale or conflicting project instructions after the subject-first and teacher/classroom discussions.

## Executive summary

The project documents are broadly aligned on the major principles:

- modular-monolith Java core
- subject-first student architecture
- Board → Qualification → Subject → CurriculumVersion identity
- learner state as an overlay rather than curriculum mutation
- Cycle 1 scope remains Edexcel IAL Chemistry
- T-029 is a minimal teacher surface, not the final LMS

However, the audit found several places where older Master Spec language is now incomplete or inconsistent with the newer canonical decisions. None requires changing the scientific research model. They are documentation/architecture synchronization issues.

## Finding 1 — Master Spec KG hierarchy is stale relative to ADR-014

**Severity:** HIGH
**Status:** KNOWN CONTRADICTION — requires controlled Master Spec revision

`MASTER_SPEC.md` section 7 currently describes the canonical educational hierarchy as:

```text
Subject
  └── Unit
       └── Topic
            └── SubTopic
                 ├── Misconception
                 ├── LearningObjective
                 ├── Question
                 └── Resource
```

and section 6.2 still lists `LearningObjective` rather than `SpecificationPoint` as the fine-grained curriculum entity.

Current canonical decision in ADR-014 and `SUBJECT_ARCHITECTURE.md` is:

```text
Board
  └── Qualification
       └── Subject
            └── CurriculumVersion / SpecificationVersion
                 └── Unit / Section
                      └── Topic / SubTopic
                           └── SpecificationPoint
```

**Required resolution:** In the next controlled `MASTER_SPEC.md` revision, make `SpecificationPoint` the canonical first-class curriculum object. `LearningObjective` may remain only as a compatibility/legacy term or be formally aliased if the existing implementation requires it; do not let both appear as competing canonical entities.

**Operational instruction until resolved:** Agents must follow `SUBJECT_ARCHITECTURE.md` and ADR-014 for specification-point work.

## Finding 2 — Master Spec question metadata is incomplete relative to specification-point architecture

**Severity:** MEDIUM
**Status:** INCOMPLETE, not a direct contradiction

The Master Spec's question-bank section currently emphasizes:

```text
primary_topic
secondary_topics[]
prerequisites[]
misconceptions[]
mark_points[]
```

The new subject architecture requires future first-class relationships from `QuestionVersion` / `QuestionPart` to one or more `SpecificationPoint` objects.

This extends existing multi-topic support; it does not invalidate it.

**Required resolution:** Update the Master Spec in its next controlled revision so `specification_points[]` or an explicit relational mapping is part of the canonical future question model, with mapping confidence, provenance, validation state, and support for multi-point coverage.

## Finding 3 — Master Spec system-architecture diagram still presents internal modules as if they were repositories

**Severity:** HIGH
**Status:** CONTRADICTION — requires controlled Master Spec revision

`MASTER_SPEC.md` section 4 includes diagram labels such as:

```text
syllabai-assessment
syllabai-learner-model
syllabai-ai
```

but ADR-012 explicitly moved those former repositories into strongly separated modules inside `syllabai-core`. The current actual repository set is:

```text
syllabai
syllabai-core
syllabai-web
syllabai-parser
Past-Papers
```

**Required resolution:** Replace the diagram's pseudo-repository labels with `syllabai-core` internal modules, or explicitly label them as bounded contexts/modules. Never describe them as deployable repositories.

## Finding 4 — ADR-012 title is now semantically awkward because the corpus repository is also part of the current repo set

**Severity:** LOW
**Status:** DOCUMENTATION DRIFT

The ADR title says **"Four repositories now; module repos deferred"**, while its body and current Master Spec recognize the public `Past-Papers` corpus repo as an additional repository in the project ecosystem.

This is not an architectural conflict if "application repositories" is intended, but the wording is ambiguous.

**Resolution:** Keep the historical decision ID, but clarify the title/body in a future revision as something like:

> **ADR-012: Four application repositories; public corpus repository tracked separately**

The corpus repository is not an application/runtime repo and does not change the modular-monolith decision.

## Finding 5 — Project Context repository table was previously incomplete

**Severity:** LOW
**Status:** RESOLVED

`PROJECT_CONTEXT.md` previously listed four repos while the current Master Spec recognized `Past-Papers`. It has now been synchronized to list all five project repositories and distinguishes the corpus repo from application code.

## Finding 6 — Teacher architecture existed conceptually, but the operational product model was under-specified

**Severity:** MEDIUM
**Status:** RESOLVED BY NEW CANONICAL DOC

The Master Spec already mentions teacher intelligence responsibilities such as class heatmaps, learner summaries, syllabus coverage, early warning, assignment/test creation, and Smart Mark review. The existing tracker also contains F-050, F-068–F-075.

What was missing was a coherent product model for:

- teacher subject-scoped workspaces
- classroom-enrolled student mode
- teaching-coverage overlay (`NOT_TAUGHT` versus low mastery)
- Test Builder as a richer SyllabAI-specific evidence-driven tool
- distinct Teacher AI Assistant versus Data Assistant
- evidence-explainable At-Risk Students
- class KG → individual student graph drill-down

`TEACHER_ARCHITECTURE.md` is now canonical for this layer, and ADR-015 records the decision.

## Finding 7 — Existing teacher tracker rows already cover several requested features

**Severity:** IMPORTANT RECONCILIATION
**Status:** RESOLVED BY EXTENSION, not duplication

The existing definitive tracker already contains:

- F-050 Test Builder (Teacher Tool)
- F-068 Class Creation & Management
- F-069 Class Roster View
- F-070 Assignment Creator
- F-071 Assignment Submissions View
- F-072 Class Knowledge Graph Heatmap
- F-073 Early Warning System (At-Risk Students)
- F-074 Teacher Dashboard (Summary)
- F-075 Announcements
- F-076 Teacher-only Question Bank

Therefore the new teacher architecture must **not** create duplicate feature IDs for these capabilities.

`backlog/teacher-lms-feature-addendum.tsv` uses TFA identifiers for genuinely new capabilities and explicitly labels F-050/F-072/F-073 extensions rather than replacements.

## Finding 8 — T-029 pilot roster shortcut must not be mistaken for the final Class model

**Severity:** HIGH for future implementation
**Status:** CLARIFIED

T-029 is merged and currently exposes an honest enabled-STUDENT cohort because Cycle 1 does not yet have a persistent Class entity.

The long-term teacher architecture requires an explicit class/membership model.

**Rule:** Do not keep stretching the T-029 cohort endpoint into the final LMS class system. Future Class Management must introduce the proper class/teaching-assignment/student-membership domain model with authorization boundaries.

## Finding 9 — Teacher and student Knowledge Graphs must share one curriculum graph

**Severity:** ARCHITECTURAL PRINCIPLE
**Status:** CLARIFIED

A student graph and a teacher graph are not two different knowledge graphs.

```text
Same subject curriculum / knowledge graph
            │
     ┌──────┴──────┐
     ▼             ▼
Student lens   Teacher lens
individual     teaching coverage +
learner state  class aggregation + drill-down
```

The teacher graph adds overlays/aggregates; it does not fork the curriculum.

## Finding 10 — `NOT_TAUGHT` is not a learner mastery state

**Severity:** HIGH for visualization semantics
**Status:** CLARIFIED

Teacher graph grey nodes mean that teaching coverage has not been recorded. They must not be interpreted as weak mastery.

A node can be:

- not taught / no coverage
- taught + strong
- taught + good
- taught + developing
- taught + weak
- taught + critical

The exact palette is a UI decision; the semantic distinction is architectural.

## Finding 11 — Teacher AI Assistant and Data Assistant are different systems at the product level

**Severity:** MEDIUM
**Status:** CLARIFIED

Do not merge these into one vague "teacher chatbot".

**Teacher AI Assistant:** grounded academic/content/teaching copilot.

**Data Assistant:** authorized structured analytics interface over class/student evidence.

The Data Assistant must not invent counts, marks, dates, risk labels, or trends. The Teacher AI Assistant must not fabricate specification requirements or present AI-generated questions as official exam content.

## Finding 12 — At-Risk Students must remain evidence-first and research-sensitive

**Severity:** HIGH
**Status:** CLARIFIED

Existing F-073 is the early-warning feature. The new architecture adds explicit explainability expectations.

Any risk label must expose contributing observations, time window, and the rule/model version where relevant. If thresholds become research constructs, the corresponding research paper sections and evaluation plan must be reviewed.

## Finding 13 — Cycle 1 scope remains protected

**Severity:** CRITICAL GOVERNANCE CHECK
**Status:** NO CONTRADICTION

The new teacher/LMS and IGCSE subject discussions are long-term architecture decisions. They do not change ADR-010.

Current Cycle 1 remains:

```text
Edexcel IAL Chemistry
~50 retake-path students
8 weeks
Tutor + Assessor agents
Predictions P1–P8
```

No document update in this change authorizes IGCSE bulk ingestion or a full LMS rollout during Cycle 1.

## Finding 14 — Save My Exams is a UX/workflow reference, not a content/runtime dependency

**Severity:** LOW
**Status:** ALIGNED

Current external research confirms useful teacher workflows around Test Builder: topic/difficulty filtering, teacher-only questions, reuse/edit, and print-ready PDFs. Save My Exams also presents subject-specific teacher resources.

The project's documents correctly treat Save My Exams as a **product/UX reference only**. SyllabAI must use its own validated content, its own question bank, its own graph/evidence layer, and its own architecture.

## Recommended controlled documentation sequence

The next Master Spec revision should synchronize three areas:

1. Replace `LearningObjective` as the canonical fine-grained graph entity with `SpecificationPoint` (or formally define a non-competing alias).
2. Correct the section-4 repository/module diagram so internal core modules are not shown as separate repos.
3. Add the teacher/classroom/LMS product layer at a level consistent with ADR-015 and `TEACHER_ARCHITECTURE.md`, while keeping those features outside Cycle 1 unless individually promoted by an explicit scope decision.

Until then, agent precedence is:

```text
Research papers
      ↓
MASTER_SPEC.md
      ↓
DECISIONS.md / ADR-014 + ADR-015
      ↓
SUBJECT_ARCHITECTURE.md
      ↓
TEACHER_ARCHITECTURE.md
      ↓
Tracker + living state
```

When a task touches the identified stale Master Spec sections, the agent must not silently follow the stale wording; it should record the contradiction and follow the current ADR/canonical addendum as instructed above.

## Current audit verdict

**Architecture is coherent after the new subject/teacher decisions, but `MASTER_SPEC.md` has three known synchronization issues that should be corrected in the next controlled version bump.** No scientific contradiction with Paper A or Paper B was identified by this documentation-only audit.
