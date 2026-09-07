# SyllabAI — Learning-First Recommendation System Architecture

**Status:** Accepted architecture direction  
**Date:** 2026-09-07  
**Canonical feature family:** F-087–F-093  
**Related features:** F-025, F-026, F-033, F-054, F-055, F-056, F-058, F-059, F-091, F-092, F-093, F-098, F-153, F-154, F-166, F-167  
**Research authority:** `papers/paper_a_conceptual_model.pdf`, `papers/paper_b_system_design.pdf`

## 1. Executive decision

The old brainstorming document proposed a “YouTube/Instagram-style recommendation system.” The product idea is retained, but the objective function and architecture are explicitly changed.

SyllabAI must **not** become an engagement-maximizing recommendation feed. The recommender is a learning-orchestration subsystem whose primary purpose is to select the next useful learning action for the learner's enrolled subject.

The canonical objective is:

> **Maximize expected learning progress and appropriate syllabus coverage subject to pedagogical, curriculum, authorization, content-validation, and learner-safety constraints.**

Clicks, impressions, session duration, watch time and raw engagement may be telemetry signals, but they are not the primary optimization target.

## 2. Why the old idea matters

The old document correctly identified several important product problems:

- cold-start learners have no behavioral history;
- interaction data is sparse at first;
- pure personalization can create an echo chamber;
- a sophisticated ML recommender needs more data and engineering effort than a small team initially has;
- recommendation quality is constrained by the quality and breadth of available educational content;
- recommendation should be connected to the Knowledge Graph rather than treating resources as an undifferentiated catalog.

Those observations remain useful. The implementation should, however, be grounded in the later SyllabAI research architecture and the subject/specification-point model.

## 3. Canonical architecture

```text
                    Learner / Subject Context
                              │
                              ▼
              ┌──────────────────────────────┐
              │ Learner Evidence & State     │
              │                              │
              │ • Question attempts         │
              │ • marks / confidence        │
              │ • misconceptions            │
              │ • timed-vs-untimed fluency  │
              │ • review state               │
              │ • subject goals / exam date │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Knowledge / Curriculum Graph │
              │                              │
              │ SpecPoints + prerequisites   │
              │ + resource/question links    │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Candidate Generation         │
              │                              │
              │ weak / due / prerequisite    │
              │ unresolved / untouched /     │
              │ teacher-assigned / goals     │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Content Retrieval            │
              │                              │
              │ metadata + topic + embeddings│
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Hybrid / Cascade Ranking     │
              │                              │
              │ rules → content → ML later  │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Next Best Learning Action    │
              │                              │
              │ explainable + evidence-backed│
              └──────────────┬───────────────┘
                             │
                             ▼
                    Learner interaction
                             │
                             ▼
                    Learning evidence
                             │
                             └──────────► recommender evaluation
```

## 4. Hard constraints before ranking

A candidate must first pass hard constraints. A learned relevance score can never override them.

### 4.1 Subject and curriculum isolation

Recommendations are evaluated inside the learner's explicit:

```text
Board → Qualification → Subject → CurriculumVersion
```

Do not recommend content merely because its title or embedding is similar if it belongs to another subject, board, qualification, or incompatible syllabus version.

### 4.2 Content validity

Only content that is currently servable under the content validation lifecycle may be recommended to learners.

Suggested/draft/unvalidated educational content is not learner-facing merely because it has a high semantic score.

### 4.3 Authorization

Teacher-assigned material, class content, and student-specific analytics must respect class membership and teacher authorization.

### 4.4 Pedagogical safety

If a graph diagnosis indicates a prerequisite problem, downstream content should not automatically outrank prerequisite remediation merely because it has higher historical engagement.

### 4.5 Teacher constraints

A teacher-assigned or teacher-pinned item may be mandatory within the authorized classroom context. The recommender may organize surrounding support, but must not silently ignore teacher intent.

## 5. Objective function

The old brainstorming document explicitly proposed a learning-first objective. That principle is retained and formalized.

The primary outcome is not:

```text
click-through rate
watch time
session length
number of recommendations consumed
```

Instead, recommendation quality should eventually be assessed through outcomes such as:

```text
subsequent assessment performance
learning gain
prerequisite-gap correction
retention / delayed retrieval
syllabus coverage
appropriate difficulty progression
metacognitive calibration
```

Engagement signals remain useful as secondary evidence because a learner cannot benefit from a resource they never meaningfully use, but engagement should not become a proxy for learning.

## 6. Candidate generation

F-087 is the MVP candidate-generation layer.

Candidates may come from:

1. **Weak evidence** — specification points/concepts where recent or accumulated evidence is weak.
2. **Prerequisite gaps** — prerequisites of currently weak advanced topics.
3. **Unresolved problems** — question review states still marked problematic or doubtful.
4. **Due reviews** — items or concepts whose review state says retrieval is due.
5. **Untouched curriculum** — specification points with insufficient exposure.
6. **Goal/exam pacing** — curriculum work that is behind the learner's intended exam-date pace.
7. **Teacher assignment/pin** — authorized classroom requirements.
8. **Related resources** — content-connected material around a diagnosed learning need.
9. **Cross-topic synthesis** — later-stage questions or resources that intentionally combine related concepts for transfer.

Candidate generation is a constraint-and-evidence stage, not a free-form LLM stage.

## 7. Cold start

The old document proposed a diagnostic quiz, subject goals, default syllabus order and peer popularity. Keep the idea, but apply it conservatively.

### New learner hierarchy

```text
1. Explicit subject/curriculum selection
2. Goal/exam-date information when available
3. Default curriculum/prerequisite path
4. Brief diagnostic evidence where appropriate
5. Validated content metadata
6. Only then behavioral similarity
```

A learner should never see an empty recommendation surface merely because there is no history.

The recommender may initialize with syllabus structure and prerequisite logic. A diagnostic assessment may provide evidence, but self-reported confidence should not be treated as equivalent to observed assessment evidence.

## 8. Data-sparsity cascade

The old brainstorm proposed:

```text
0–5 interactions     → rules
5–20 interactions    → content-based filtering
20+ interactions     → collaborative filtering
```

The thresholds are **not canonical**. They are an intuitive illustration, not validated constants.

The canonical architecture is maturity-based:

```text
Sparse / cold
   → deterministic learning-first rules

Some history
   → rules + content similarity

Sufficient validated data
   → rules + content + experimental learned ranking
```

The system should decide whether learned signals are eligible based on data sufficiency and evaluation quality, not a fixed global interaction-count threshold.

## 9. Content-based retrieval

F-088 should use the existing content/retrieval substrate rather than introducing a dedicated recommendation database.

Candidate similarity may use:

- SpecificationPoint overlap;
- concept/skill overlap;
- question type;
- difficulty;
- resource type;
- embedding similarity via pgvector;
- prerequisite distance;
- learner-state compatibility.

Embedding similarity is a **candidate-generation signal**, not the final objective.

A resource that is semantically similar to a learner's last click can still be pedagogically wrong if the learner actually needs a prerequisite, review, or harder transfer task.

## 10. Collaborative filtering

F-089 remains a valid future experiment, not the foundation.

Collaborative filtering can learn patterns such as:

> Learners with a similar evidence profile improved after using resource X.

But a popularity signal is not automatically a learning-value signal.

Before using collaborative models for learner-facing decisions, SyllabAI should have:

- enough interaction volume;
- stable item identity;
- sufficiently dense subject-level coverage;
- offline evaluation;
- leakage controls;
- cold-start fallback;
- learning-outcome evaluation rather than engagement-only metrics.

A learned model must not override explicit prerequisite or syllabus constraints.

## 11. Hybrid / cascade model

F-090 is the long-term architecture.

The preferred sequence is:

```text
Hard constraints
      ↓
Rule-based learning candidates
      ↓
Content-based expansion
      ↓
Optional learned ranking
      ↓
Exploration / diversification
      ↓
Next-best-action policy
```

This is preferable to an opaque single model because each layer has a clear role and can fail safely.

The recommender should be able to operate entirely on rule/content signals when ML is unavailable, poorly calibrated, or inappropriate for the learner/data regime.

## 12. Exploration without random waste

The old brainstorm proposed 10% epsilon-greedy random recommendations. That exact rule is rejected.

Randomness is not inherently pedagogical.

F-091 should instead implement **constrained exploration**:

```text
Untouched SpecificationPoint
        OR
High uncertainty
        OR
Exam pacing gap
        OR
Teacher-priority content
        OR
Cross-topic transfer opportunity
```

subject to all normal curriculum, validity, authorization and prerequisite constraints.

Epsilon-greedy, UCB and similar methods may be used as research experiments later. They are not product requirements and their parameters must not be hard-coded as scientific facts.

## 13. Recommendation orchestration / Next Best Action

F-092 is the primary student-facing orchestration feature.

It should answer:

> **What is the most useful next learning action for this learner, in this subject, right now?**

The answer may be:

```text
Read a revision note
Watch a validated educational video
Practice a similar question
Review a prerequisite
Ask Tutor
Complete a Target Test
Review a flagged problem
Complete a due retrieval
Attempt a teacher assignment
```

This is intentionally broader than “recommend a resource.” SyllabAI recommends **learning actions**.

## 14. Recommendation reasons

F-093 should make every learner-facing recommendation inspectable.

Examples:

```text
Because you have repeated low-mark evidence on Mole Calculations.
Because Differentiation depends on a prerequisite you are currently weak on.
Because this review is due.
Because you have not yet demonstrated coverage of SpecificationPoint 3.2.
Because your teacher assigned this for the current class.
```

Reasons must come from structured facts and evidence references. Do not allow an LLM to invent recommendation reasons.

A reason is not a causal claim. “Recommended because…” means the system used the listed evidence/rule, not that the resource has been proven to cause the learner's improvement.

## 15. Syllabus completion and exam-date planning

The old document's completion mandate should be retained, but not as a simplistic “force every topic” algorithm.

The recommender should account for:

- curriculum coverage;
- demonstrated mastery;
- prerequisite gaps;
- review/retention needs;
- intended exam date;
- available study time when provided;
- teacher assignments;
- required assessments.

A learner should be able to progress toward full syllabus coverage without the recommender trapping them inside a narrow set of comfortable topics.

A “complete” specification point should eventually require evidence appropriate to the subject rather than only exposure or viewing a resource.

## 16. Avoiding the echo chamber

Diversification is required, but it must be educationally meaningful.

Use a portfolio such as:

```text
weak-topic remediation
+ prerequisite support
+ due retrieval
+ untouched syllabus coverage
+ transfer / cross-topic synthesis
+ teacher-required work
```

Do not treat all six categories as equal on every request. The ranking policy should respond to learner state and context.

## 17. Diminishing returns and content breadth

The old document correctly observed a strategic constraint: recommendation sophistication cannot compensate for a weak content library.

SyllabAI should therefore invest in:

- broad SpecificationPoint coverage;
- multiple resource types;
- varied question difficulty;
- multiple past-paper instances;
- validated videos/learning resources;
- generated question variants where allowed and validated;
- transfer and mixed-topic assessments.

The goal is not an endless feed. The goal is an adequately rich set of **useful learning actions**.

## 18. Educational YouTube / video recommendation

F-025 is retained but explicitly redesigned as an **education-scoped video library**, not generic YouTube browsing.

### Required behavior

```text
Student subject
      ↓
SpecificationPoint / learning need
      ↓
Approved / validated video candidates
      ↓
Learning-first ranking
      ↓
Video shown in SyllabAI context
```

The system should support approved-channel/source policies and preserve video provenance.

The product should not simply embed YouTube's home/recommended feed because its optimization objective is outside SyllabAI's learning policy.

A video may be recommended because it addresses a diagnosed need, not merely because similar users watched it.

## 19. Video watch telemetry

F-026 is retained, but viewing behavior is treated as learning evidence/telemetry rather than mastery itself.

Record useful events such as:

- impression;
- start;
- meaningful progress;
- completion;
- repeat viewing;
- resource exit;
- downstream question attempt.

Do not implement:

```text
10 minutes watched → +0.10 mastery
```

The relationship between video exposure and subsequent learning should be evaluated empirically.

Paper B's system design explicitly calls for videos to be tagged to Knowledge Graph nodes using the same metadata framework as questions, so video content belongs to the same subject/specification graph rather than a separate unstructured silo.

## 20. Learning Log integration

The Question Attempt / Learning Evidence subsystem is a key recommender feedback source.

```text
Recommendation exposed
       ↓
Learner interacts
       ↓
Question/lesson/video evidence
       ↓
Learning Log / telemetry
       ↓
Later assessment outcome
       ↓
Recommendation evaluation
```

The recommender must not train directly on raw clicks as if they were learning labels.

## 21. Recommendation evaluation

Recommendation evaluation should have at least two layers.

### Immediate utility

- recommendation opened;
- action started;
- action completed;
- student dismissed/ignored;
- student explicitly rated useful/not useful where available.

### Learning outcome

- subsequent assessment improvement;
- prerequisite-gap correction;
- retention after delay;
- confidence calibration;
- successful transfer to similar or cross-topic questions;
- syllabus coverage progression.

CTR or watch time alone is insufficient to claim educational benefit.

## 22. Research and experimentation

Learned recommendation policies should be introduced through registered experiments rather than silently replacing the baseline.

At minimum, experiments should identify:

```text
policy/version
candidate-generation policy
ranking policy
eligible population
subject/curriculum scope
outcome metrics
observation window
```

The project should preserve the deterministic baseline so future models can be compared against it.

## 23. Architecture and implementation boundaries

Recommendation code belongs in the `recommendation` module inside `syllabai-core` under the current modular-monolith policy.

Use interfaces for replaceable strategies, for example:

```java
CandidateGenerator
ContentSimilarityStrategy
CollaborativeRankingStrategy
ExplorationStrategy
RecommendationPolicy
RecommendationExplanationProvider
RecommendationEvaluationSink
```

No dedicated recommendation microservice is required at the current stage.

Python/ML jobs are permitted later when they solve a real offline modeling problem, but the application contract remains language-neutral and owned by the Java domain core.

pgvector remains the default content-similarity substrate under the current architecture.

## 24. Data model concepts

The physical schema is an implementation decision, but the semantic objects should include:

```text
RecommendationRequest
RecommendationCandidate
RecommendationDecision
RecommendationReason
RecommendationExposure
RecommendationOutcome
RecommendationExperiment
```

`RecommendationExposure` should reference the policy/version that produced it.

Where an outcome can be linked to question-level evidence, retain that relationship for research/evaluation.

## 25. Agent non-negotiables

1. Do not optimize the recommender for watch time, clicks or session duration as the primary objective.
2. Do not let collaborative popularity override curriculum/prerequisite/teacher constraints.
3. Do not recommend unvalidated educational content to learners.
4. Do not use generic YouTube recommendations as the SyllabAI learning policy.
5. Do not invent learner facts or recommendation reasons with an LLM.
6. Do not treat video watch time as mastery.
7. Do not hard-code “10% random exploration” as a product rule.
8. Do not treat the old 0–5 / 5–20 / 20+ interaction thresholds as validated scientific boundaries.
9. Do not create a recommendation microservice without a separately justified runtime/lifecycle boundary.
10. Keep recommendations distinct from measured learner state.
11. Use the Learning Log as the canonical question-level evidence feedback loop.
12. Preserve subject, qualification, curriculum-version and specification-point isolation.
13. Keep the deterministic baseline available when learned ranking is unavailable or untrustworthy.

## 26. Relationship to the old brainstorming proposal

| Old proposal | Current verdict |
|---|---|
| YouTube-style personalized discovery | **KEEP, redesign around learning** |
| Rule-based MVP | **KEEP; canonical baseline** |
| Content-based filtering | **KEEP; candidate expansion** |
| Collaborative filtering | **FUTURE EXPERIMENT** |
| Hybrid/cascade | **KEEP; canonical long-term architecture** |
| 10% epsilon-greedy random topic | **REJECT exact rule; replace with constrained exploration** |
| Knowledge-graph-integrated recommendations | **CORE** |
| “Next Steps” | **CORE; F-092** |
| Recommendation explanations | **CORE trust/evaluation feature** |
| Syllabus completion mandate | **KEEP, contextualize** |
| Exam-date pacing | **KEEP as goal-aware scheduling input** |
| Diagnostic warm start | **KEEP, subject to assessment design** |
| Popular-among-peers | **SECONDARY signal only** |
| Watch time as a ranking target | **REJECT** |
| Dynamic content replenishment | **KEEP as future content strategy, not a recommender requirement** |
| AI-generated variants | **KEEP only with content validation** |
| Student-generated content | **FUTURE; separate moderation/content policy** |

## 27. Scope

This is the long-term recommendation architecture. It does not expand Cycle 1.

Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010. The recommendation subsystem may be designed now so that its contracts are compatible with the pilot, but broad recommendation product work remains governed by the active execution scope.
