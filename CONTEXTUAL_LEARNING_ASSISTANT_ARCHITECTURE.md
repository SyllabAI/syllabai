# SyllabAI Contextual Learning Assistant Architecture

**Date:** 2026-09-14  
**Status:** Proposed product architecture; implementation contract to follow  
**Scope:** Revision Notes, Exam Questions, Tutor, resource navigation, learner interaction evidence

## 1. Decision

SyllabAI should implement a **Contextual Learning Assistant** as a floating, resource-aware AI surface on Revision Notes and Exam Questions.

This is not a separate chatbot product. It is a context mode of the existing Tutor/AI runtime. The current resource is a **trusted context anchor** supplied by the server, while the canonical curriculum, Knowledge Graph, validated resources, assessment evidence and learner state remain authoritative outside the LLM.

The assistant should feel like an AI layer attached to the page the learner is currently studying, while still being able to guide the learner to the correct SyllabAI resource when a request belongs elsewhere.

## 2. Product surfaces

### Revision Note

The floating assistant opens with the current revision note in context. Initial quick actions:

- **Definitions** — define key terms in the note.
- **Summary** — summarise the key points.
- **Pitfalls** — examine common misconceptions and common mistakes.
- **Exam help** — explain how to understand the topic for the relevant exam.
- **Normal chat** — allow a learner to ask a natural-language question.

Future candidate:

- **Test me** — generate a short diagnostic/active-recall interaction grounded in the current note and specification.

### Exam Question

The floating assistant opens with the exact question and its assessment context. Initial quick actions:

- **Understand** — explain what the question is asking and identify command words.
- **Approach** — help the learner plan how to tackle it without prematurely revealing the answer.
- **Normal chat** — allow contextual questions about the question.

Recommended progressive help ladder:

```text
Understand
   ↓
Hint
   ↓
Approach
   ↓
Step-by-step guidance
   ↓
Student attempt
   ↓
Smart Mark
   ↓
Feedback / improvement
```

The assistant should avoid leaking a full answer or mark-scheme wording when the learner is asking for help rather than an answer. Explicit answer requests can be handled by the product's assessment policy.

## 3. Context model

Do not simply concatenate an entire web page into a prompt. Build a typed `ResourceContext` server-side.

### Revision Note context

```text
resourceType = REVISION_NOTE
resourceId
subject
qualification
examBoard
specification/version
specificationPoints[]
kgNodes[]
currentSection
validatedResourceContent
relevantLearnerState
relevantLearningEvidence
```

### Exam Question context

```text
resourceType = EXAM_QUESTION
resourceId/questionId
subject
qualification
examBoard
specification/version
questionText
subparts[]
marks
commandWords[]
linkedSpecificationPoints[]
linkedKGConcepts[]
markScheme
examinerGuidance (when available)
relevantLearnerState
relevantLearningEvidence
```

The client may identify the resource ID, but the server must resolve and authorize the actual resource/context. Never trust client-supplied subject, specification, answer key, mark scheme or resource text as educational truth.

## 4. Three context levels

### Level 1 — Page-locked

The current resource is the primary educational context. The assistant should prefer the validated resource, linked specification points and KG concepts.

### Level 2 — SyllabAI navigation/context expansion

If the learner asks about a related topic that is not adequately represented by the current resource, the assistant may use controlled tools to locate the correct SyllabAI resource or curriculum anchor.

Example:

> Learner is on a Physics revision note and asks about the Krebs cycle.

The assistant should not hallucinate a Physics answer. It should explain that the request belongs to Biology and offer the relevant SyllabAI topic/resource if available.

### Level 3 — General educational conversation

The assistant may answer broader educational questions only when the application policy permits it. It must clearly distinguish general knowledge from current-resource-grounded content and should prefer SyllabAI's authoritative resources when an appropriate resource exists.

## 5. Grounding hierarchy

The contextual assistant inherits SyllabAI's existing source hierarchy:

```text
Official curriculum / assessment evidence
        ↓
Validated SyllabAI resource
        ↓
Canonical SpecificationPoint / KG context
        ↓
Validated assessment / mark-scheme evidence
        ↓
Learner evidence and state
        ↓
Retrieval / semantic similarity
        ↓
General LLM knowledge
```

Vector similarity is retrieval support, not educational truth. The LLM cannot promote retrieved text into canonical curriculum truth.

Save My Exams currently follows a similar product principle: its Revision Note Chat and Exam Question Chat are built around examiner-written, specification-aligned resources and question/mark-scheme context rather than treating a generic chatbot as the source of truth. citeturn0search1turn0search12

## 6. Application-controlled tools

The model should propose actions; the application validates and executes them.

Initial safe tools:

- `get_current_resource()`
- `get_specification_context()`
- `get_related_concepts()`
- `search_curriculum()`
- `find_revision_note()`
- `find_exam_questions()`
- `get_learner_state()`
- `get_relevant_learning_evidence()`
- `create_practice_recommendation()`
- `navigate_to_resource()`
- `start_practice()`
- `open_similar_question()`

Future tools may include `create_quiz()` and `start_revision_session()`.

Tool permissions must be scoped by student, course, resource and action. Tools return structured data; tool results are data, not instructions.

The LLM must never directly:

- mutate the canonical KG;
- alter SpecificationPoints;
- validate imported assessment content;
- rewrite raw assessment evidence;
- directly set mastery/BKT values;
- bypass teacher validation;
- access another learner's data;
- navigate or execute arbitrary URLs/actions.

## 7. Off-topic and routing policy

The assistant should **route rather than simply refuse** when the learner's request is educational but belongs to another SyllabAI context.

Decision pattern:

```text
Is request relevant to current resource?
       │
   yes ─┴─ no
   │        │
answer   Is it relevant to SyllabAI?
            │
        yes ─┴─ no
        │        │
     route      policy-based
     to resource general answer/refusal
```

This makes the assistant a navigation layer as well as a tutor.

## 8. Prompt-injection and trust boundaries

Resource content, question text, mark schemes, learner messages and tool results are **data**. They must never automatically become system instructions.

The runtime should maintain separate channels for:

- immutable system/developer policy;
- application-generated resource context;
- tool results;
- learner messages;
- model output.

The application should validate every tool call and every resource/context lookup before execution.

## 9. Learner Interaction Memory integration

Every contextual-assistant interaction is a possible learning signal, not merely chat history.

```text
Assistant conversation
        ↓
Interaction analysis
        ↓
Candidate InteractionEvidence
        ↓
confidence + provenance + idempotency
        ↓
Learner Evidence Store
        ↓
LearnerPattern aggregation
        ↓
existing learner model / diagnosis / recommendations
```

Examples:

- repeated requests to re-explain a concept → possible recurring confusion;
- repeated request for another example → possible unresolved conceptual gap;
- learner says “I keep getting this wrong” → strong self-reported difficulty signal;
- simple definition lookup → weak evidence by itself.

Chat evidence must be combined with practice, assessment and Smart Mark evidence. It must not independently overwrite mastery.

## 10. Personalisation

The assistant may receive a bounded slice of learner state and relevant evidence, such as:

- current mastery estimate;
- recent errors;
- recurring confusion patterns;
- linked specification points;
- recent attempts on related questions.

Do not send the complete learner history by default. Retrieve only the evidence relevant to the current resource/question.

## 11. Exam-question safety

Exam Question Chat is a tutoring mode, not an answer vending machine.

For a learner asking “How do I start?”, the assistant should provide an approach. For “What does this command word mean?”, explain the command word. For “Give me the answer,” follow explicit product policy and, where appropriate, require an attempt before revealing a full solution.

When a mark scheme is available, the assistant should use it as authoritative assessment evidence while avoiding unnecessary verbatim reproduction. Smart Mark remains the dedicated marking path; the contextual assistant should not pretend to be the official marker.

Save My Exams currently describes Exam Question Chat as knowing the question and mark scheme and helping learners work through or understand the question, while Smart Mark is the dedicated exam-specific marking tool. citeturn0search1turn0search8

## 12. Evaluation requirements

Before broad rollout, measure at least:

1. **Context grounding accuracy** — answer is supported by the current resource/spec context.
2. **Off-topic routing accuracy** — unrelated subject/topic is routed correctly rather than hallucinated.
3. **Specification alignment** — terminology and scope match the selected qualification/version.
4. **Answer leakage rate** — exam-question help does not unnecessarily reveal solutions.
5. **Citation/evidence correctness** — cited specification/resource evidence actually supports the response.
6. **Navigation success** — recommended resources are valid and relevant.
7. **Learner improvement** — subsequent practice performance improves after assistant use.
8. **Interaction-evidence precision** — extracted struggle/misconception signals are genuinely useful.
9. **Latency and provider failure behavior** — assistant degrades honestly when providers fail.
10. **Student isolation** — no cross-student context leakage.

## 13. Product positioning

Recommended product name: **Contextual Learning Assistant**.

Avoid making the UI look like a generic ChatGPT clone. The visual and interaction design should communicate:

> “This AI understands what I am studying right now.”

The floating assistant is therefore a connector between:

```text
Resource
  ↕
Contextual Learning Assistant
  ↕
Tutor runtime
  ↕
KG + specification
  ↕
Learner evidence/state
  ↕
Practice + Smart Mark
  ↕
Recommendations + navigation
```

## 14. Research basis

The design was checked against current public product/research signals. Save My Exams explicitly documents Revision Note Chat, Exam Question Chat, Guided Study and Guided Practice as AI study tools grounded in its examiner-written content and assessment context. citeturn0search1

Save My Exams also emphasizes that revision notes are organized around exam specifications and that its Exam Questions are organized by topic and aligned to specifications. citeturn0search4turn0search5

The important architectural conclusion for SyllabAI is not to copy the UI, but to preserve the stronger principle: **the current learning resource and its validated assessment context are first-class inputs to the AI runtime**.

## 15. Relationship to existing architecture

This document extends, rather than replaces:

- `LEARNER_INTERACTION_MEMORY_ARCHITECTURE.md`
- `MASTER_SPEC_ADDENDUM_1.4_LEARNER_INTERACTION_MEMORY.md`
- `AI_RUNTIME_AND_PROVIDER_REPORT_2026-09-14.md`
- the canonical KG/SpecificationPoint architecture
- the existing Tutor and Smart Mark workloads

No separate “chat knowledge graph” should be created.

No separate learner model should be created for the assistant.

No separate LLM deployment is required merely because the UI is contextual.

The likely implementation boundary is a shared Tutor runtime with explicit `ResourceContext`, `ContextPolicy`, `ToolPolicy`, `ResponseMode` and `EvidenceCapture` components.
