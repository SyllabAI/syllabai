# Learner Interaction Memory Architecture

**Status:** Canonical architecture addendum  
**Date:** 2026-09-14  
**Scope:** Student Tutor conversations, interaction evidence, longitudinal learner patterns, recommendations and learner-KG integration  
**Primary implementation repository:** `SyllabAI/syllabai-core`  
**Related architecture:** `MASTER_SPEC.md`, `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md`, `RECOMMENDATION_SYSTEM_ARCHITECTURE.md`, `KNOWLEDGE_GRAPH_CONTEXT.md`, `RAG_RETRIEVAL_RESEARCH.md`

## 1. Decision

SyllabAI will implement **Learner Interaction Memory** as a learning-evidence subsystem, not as a generic chatbot-memory product.

The system must remember conversations for two different reasons:

1. **Conversation continuity:** allow the Tutor to understand the current and previous turns of a student's conversation.
2. **Longitudinal learning intelligence:** extract useful, provenance-bearing evidence from conversations so recurring confusion, misconceptions, requests for explanation, confidence signals and other learning patterns can inform diagnosis, learner state, recommendations and Tutor context.

The second purpose is the strategically important one. Raw chat history is not learner truth. A conversation becomes useful to the adaptive system only after it is transformed into structured evidence with provenance, confidence, scope and an explicit relationship to the curriculum/knowledge graph where possible.

## 2. Why this belongs in SyllabAI

SyllabAI already treats learner state as a time-aware overlay over an authoritative curriculum and knowledge graph. It already has question-attempt evidence, Smart Mark, Tutor, diagnosis and Next Best Learning Action recommendations. Tutor dialogue is therefore another evidence channel that can reveal signals that ordinary assessment cannot always capture.

Examples:

- A student repeatedly asks why mole ratios work even after answering numerical questions correctly.
- A student explicitly says that they keep confusing oxidation and reduction.
- A student asks for three different explanations of the same specification point.
- A student demonstrates a misconception in free-form reasoning before later correcting it.
- A student asks for an easier example after failing to understand an explanation.

These are not automatically proof of low mastery. They are observations that should become candidate learning evidence and be combined with assessment evidence, Smart Mark evidence and existing learner-state estimates.

The system must therefore answer:

> **What did the student reveal through interaction, what concept does it relate to, how strong is the evidence, and does the pattern persist across time?**

It must not answer:

> **What did the chatbot decide the student knows?**

## 3. Research and implementation references

### 3.1 OpenHuman — architecture inspiration, not dependency

OpenHuman's current architecture is especially useful for the *shape* of a persistent memory system. It canonicalizes incoming data, preserves provenance, creates bounded chunks, builds hierarchical summaries and retrieves relevant context instead of replaying an entire history. Its Memory Tree and local-first model show how raw experiences can be progressively compressed without requiring every future model call to consume the original transcript.

SyllabAI should borrow the separation of raw source → canonical representation → derived summaries/retrieval context, but not copy OpenHuman's implementation. The `tinyhumansai/openhuman` repository is GPL-3.0, so it is **reference-only** under SyllabAI's permissive-license policy. OpenHuman is also a general agent memory system; SyllabAI needs a stricter educational evidence model.

Reference: https://github.com/tinyhumansai/openhuman

### 3.2 Mem0 — extraction/retrieval pattern

Mem0 demonstrates a useful application-level pattern: conversation turns are processed into durable memories; memories are scoped by user/session; retrieval occurs before a future model request; and the system can combine semantic, lexical and entity signals. Its graph-memory documentation is useful for understanding cross-memory linking.

SyllabAI should **not** adopt generic extracted memories as learner truth. Educational memories must carry evidence type, curriculum scope, confidence and provenance and must feed the existing Learning Evidence / Learner Model rather than bypassing it.

Reference: https://github.com/mem0ai/mem0

### 3.3 Letta / MemGPT — explicit short-term vs long-term memory

Letta's architecture separates current conversation context from durable memory and treats persistence as part of the agent runtime. This is a useful precedent for distinguishing thread-level Tutor context from cross-session learner memory.

SyllabAI should keep that distinction, but its long-term memory is not an unconstrained agent biography. It is a governed learner-evidence layer.

Reference: https://github.com/letta-ai/letta

### 3.4 LangGraph — persistence boundary

LangGraph distinguishes thread-scoped checkpoints from application-defined long-term stores. That separation maps cleanly to SyllabAI's need for current conversation state versus durable learner interaction evidence.

Reference: https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/persistence.mdx

### 3.5 Graphiti / Zep — temporal provenance and evolving facts

Graphiti is particularly relevant to the question of how derived facts can evolve over time. It models episodes as provenance-bearing inputs and derived facts with temporal validity, and combines semantic, keyword and graph retrieval. Its temporal model is a strong reference for longitudinal learner interaction patterns.

SyllabAI should borrow the principles of **episode provenance, temporal history, incremental updates and hybrid retrieval**, while keeping the authoritative educational KG separate from the interaction-memory graph/overlay. Graphiti's external graph-database requirements are not currently justified for Cycle 1 because SyllabAI already uses PostgreSQL/pgvector.

Reference: https://github.com/getzep/graphiti

### 3.6 Dialogue Knowledge Tracing — direct educational evidence

The Dialogue Knowledge Tracing work is the most directly relevant educational research reference. It uses LLMs to identify knowledge components involved in tutor-student dialogue turns and evaluate response correctness, then feeds those labels into knowledge tracing. This supports the core SyllabAI decision that dialogue can become structured learning evidence rather than remaining merely chat history.

SyllabAI should be more conservative than a pure LLMKT pipeline: extracted dialogue evidence is a candidate signal, not an immediate overwrite of learner mastery.

Paper: https://arxiv.org/abs/2409.16490  
Code: https://github.com/umass-ml4ed/dialogue-kt

### 3.7 MemoChat / Generative Agents — useful memory patterns, different objective

MemoChat demonstrates iterative memorization → retrieval → response for long-range conversation. Generative Agents demonstrates storing experiences, producing higher-level reflections and retrieving memories for future decisions. Both support the architectural idea that durable memory should be derived from raw experience rather than repeatedly replaying the full transcript.

They are references for memory mechanics, not educational truth models.

## 4. Memory layers in SyllabAI

SyllabAI will use four distinct layers.

### Layer 1 — Conversation record

Immutable-ish application history of the student's chat:

- Conversation
- Message/turn
- role
- timestamp
- student/session identity
- subject/curriculum scope
- Tutor response metadata
- retrieval/evidence references used by the Tutor
- model/provider/prompt execution metadata where required for reproducibility

This layer is the audit/history source. It is not learner state.

### Layer 2 — Working conversation memory

Short-term context used to answer the current conversation coherently. This can include recent turns and a compact conversation summary. It should be bounded and should not grow without limit.

This memory may be used directly by Tutor generation.

### Layer 3 — Interaction Evidence

Structured, provenance-bearing observations extracted from the conversation. Each item must point back to the exact source turn(s) and carry enough metadata to be audited.

Suggested evidence types:

- `SELF_REPORTED_DIFFICULTY`
- `CONFUSION`
- `MISCONCEPTION_CANDIDATE`
- `REPEATED_CONFUSION`
- `REQUEST_FOR_REEXPLANATION`
- `REQUEST_FOR_EXAMPLE`
- `REQUEST_FOR_SIMPLIFICATION`
- `UNCERTAINTY`
- `CONFIDENCE_SIGNAL`
- `CORRECTED_UNDERSTANDING`
- `REASONING_ERROR`
- `CONCEPTUAL_EXPLANATION_FAILURE`
- `PROCEDURAL_DIFFICULTY_CANDIDATE`
- `STRATEGY_DIFFICULTY_CANDIDATE`
- `SELF_REGULATION_SIGNAL`

Not every message creates evidence.

### Layer 4 — Learner Interaction Patterns

Longitudinal aggregates over Interaction Evidence. Examples:

- recurring confusion about a concept
- repeated requests for alternate explanations
- recurring misconception candidate
- persistent uncertainty despite correct answers
- improvement after an intervention
- repeated difficulty transferring a concept to exam-style questions
- repeated procedural errors in free-form reasoning

Patterns are derived state. They must never erase the underlying evidence.

## 5. Canonical pipeline

```text
Student message
      │
      ├──────────────► Conversation / Message store
      │
      ▼
Tutor turn + current retrieval/evidence context
      │
      ▼
Conversation analysis
      │
      ├── deterministic extraction where possible
      └── LLM structured classification where useful
      │
      ▼
Candidate Interaction Evidence
      │
      ├── source turn IDs
      ├── student + subject scope
      ├── SpecificationPoint / KnowledgeNode candidates
      ├── evidence type
      ├── confidence
      ├── extractor/provider/model/prompt version
      └── created_at / observed_at
      │
      ▼
Evidence validation / normalization
      │
      ├── reject low-value/no-signal candidates
      ├── resolve curriculum references
      ├── deduplicate/idempotency
      └── preserve uncertainty
      │
      ▼
Learning Evidence substrate
      │
      ├──────────────► Learner state / BKT / BDT / decay
      │
      ├──────────────► Diagnostic / struggle inference
      │
      ├──────────────► Interaction Pattern engine
      │                    │
      │                    └──► Recommendations / NBA
      │
      ├──────────────► Tutor context retrieval
      │
      └──────────────► Student / Teacher analytics
```

## 6. Evidence semantics

Interaction evidence must be treated differently from assessment evidence.

### Strong signals

- explicit self-report of persistent difficulty
- explicit statement of a misconception
- repeated incorrect reasoning about the same concept
- repeated confusion across independent conversations
- repeated failure after an explanation, when the source turns support the inference

### Medium signals

- repeated requests for another explanation
- requests for simpler wording or examples
- uncertainty language around a concept
- repeated questions about the same prerequisite relationship

### Weak signals

- a single basic factual question
- asking for a definition
- asking for a worked example without any indication of difficulty

### No learning signal

- greetings
- thanks
- acknowledgement
- conversational filler
- Tutor-generated text alone

A weak or ambiguous signal must not directly lower mastery.

## 7. Curriculum and knowledge-graph integration

The authoritative educational KG remains unchanged by chat.

The correct relationship is:

```text
Authoritative Curriculum / Knowledge Graph
                 │
                 │ canonical anchors
                 ▼
        Interaction Evidence
                 │
                 ▼
       Learner-state overlay
                 │
                 ▼
    Personalized KG / recommendations
```

Interaction analysis may propose a mapping such as:

```text
"I keep mixing oxidation and reduction"
          ↓
concept candidate: oxidation/reduction
          ↓
SpecificationPoint candidates: [resolved official points]
          ↓
MISCONCEPTION_CANDIDATE
          confidence: 0.91
          source: tutor_chat
          message_ids: [...]
```

The LLM must not create an authoritative `KnowledgeNode`, `SpecificationPoint`, prerequisite edge or misconception definition from chat. Unknown concepts are stored as unresolved candidates until mapped against the canonical graph.

The personalized KG may *display* or aggregate interaction-derived evidence, but its underlying canonical nodes and relationships remain authoritative.

## 8. Recommendation integration

Recommendations remain **Next Best Learning Action**, not a chat-sentiment feed.

The recommendation engine should consume interaction patterns alongside:

- mastery
- misconception evidence
- procedural fluency
- confidence
- exposure
- review/decay
- assessment performance
- Smart Mark evidence
- past-paper evidence
- Tutor interaction evidence

Example:

```text
Assessment: 72% correct on moles
Tutor chats: 4 conversations mention confusion about mole ratios
Smart Mark: repeated ratio setup errors
        ↓
High-confidence recurring conceptual/procedural pattern
        ↓
NBA: targeted mole-ratio explanation + worked example
        ↓
short diagnostic question
        ↓
learner-state update
```

The chat signal should strengthen or weaken an existing hypothesis. It should not override stronger direct assessment evidence without an explicit evidence policy.

## 9. Tutor integration

Tutor should have two separate memory paths.

### Thread memory

Used for immediate conversational continuity. The Tutor can see recent turns plus a bounded conversation summary.

### Learner memory

Retrieved only when relevant. Examples:

- "You were unsure about oxidation numbers last time. Want to try a short check?"
- "We have previously worked through mole-ratio setup; let's try a new exam-style example."

The Tutor must not expose hidden learner scores or internal confidence values unless the product UX explicitly intends to do so. Internal memory should be converted into pedagogically appropriate language.

Tutor retrieval should prefer relevant, recent and high-confidence learner evidence rather than dumping a complete student profile into every prompt.

## 10. Smart Mark integration

Smart Mark remains a separate assessment-evidence path. It does not need a separate LLM merely because Interaction Memory exists.

The initial architecture may use the same production generation model for:

- Tutor generation
- Smart Mark candidate generation
- Interaction Evidence extraction

but each workload must have:

- its own system prompt
- structured output schema
- provider/model policy
- validation path
- telemetry
- failure handling

The Interaction Evidence extractor should be a lower-cost, structured-output workload when possible. It does not need the largest Tutor model for every message.

## 11. Agentic capability

SyllabAI's Tutor may become agentic, but agentic behavior is an **application runtime property**, not a magical property of the LLM.

The controlled future loop is:

```text
LLM proposes action
   ↓
Application validates intent + permissions
   ↓
Tool executes read-only / bounded action
   ↓
Result returns to model
   ↓
LLM decides whether another bounded step is useful
   ↓
Termination policy
```

Educational tools should initially be read-only or assessment-safe:

- retrieve learner state
- retrieve relevant KG nodes
- retrieve validated resources
- retrieve prior interaction evidence
- generate a diagnostic question
- start a practice attempt

The model must not directly mutate canonical curriculum, learner mastery, validation state or assessment evidence.

## 12. Storage model — initial target

The exact schema belongs in `syllabai-core`, but the logical model is:

### Conversation

- `conversation_id`
- `student_id`
- `subject_id`
- `curriculum_version_id`
- `created_at`
- `updated_at`
- `status`
- optional bounded summary metadata

### Message

- `message_id`
- `conversation_id`
- `role`
- `content`
- `created_at`
- `sequence_no`
- Tutor execution metadata as applicable

### InteractionEvidence

- `evidence_id`
- `student_id`
- `conversation_id`
- `message_id` / source turn IDs
- `subject_id`
- `curriculum_version_id`
- `specification_point_id` nullable
- `knowledge_node_id` nullable
- `evidence_type`
- `claim`
- `confidence`
- `strength`
- `observed_at`
- `extractor_provider`
- `extractor_model`
- `extractor_prompt_version`
- `status`
- `created_at`

### LearnerInteractionPattern

- `pattern_id`
- `student_id`
- `subject_id`
- `specification_point_id` / `knowledge_node_id`
- `pattern_type`
- `frequency`
- `first_seen`
- `last_seen`
- `confidence`
- `supporting_evidence_count`
- `status`

Patterns are derived and recomputable. Evidence is the durable source.

## 13. Privacy, deletion and governance

Conversation memory is learner data. It must obey the same account, subject and authorization boundaries as learner state.

Requirements:

- strict student scoping on every query
- no cross-student retrieval
- deletion/export must include conversation-derived evidence
- raw chat and derived evidence need explicit retention policy
- provider/model execution metadata must not leak secrets
- LLM prompts must not include unrelated students
- sensitive content should not be retained as a reusable learner memory unless product policy explicitly permits it
- derived evidence must remain traceable to its source turns
- uncertain extraction must be representable without silently becoming fact

## 14. Failure modes and guardrails

### LLM hallucinates a misconception

Store it as `MISCONCEPTION_CANDIDATE` with confidence and source provenance; do not mutate canonical misconception data or directly force a mastery update.

### Student asks a question because they are curious

A single question does not equal weakness. Use evidence strength and longitudinal recurrence.

### Student intentionally tests the Tutor

Tutor-generated tasks and adversarial/curiosity queries must not automatically count as learner evidence.

### Conversation contains multiple subjects

Resolve subject/curriculum scope per evidence item. Do not assume the conversation's initial subject applies to every turn.

### Evidence extractor changes model/provider

Store extractor identity and prompt version so historical derived evidence remains interpretable.

### Duplicate extraction

Use deterministic source-turn IDs plus extractor version and idempotency keys. Re-running an analysis must not create duplicate evidence.

### Contradictory evidence

Keep both source events. Let the learner-model/evidence policy resolve the aggregate; do not overwrite history.

## 15. Evaluation plan

The feature must be evaluated as an evidence system, not only as a chat feature.

### Extraction quality

- evidence precision
- evidence recall
- curriculum-link accuracy
- misconception-candidate precision
- false-positive rate on ordinary curiosity/questions

### Longitudinal quality

- recurrence detection precision
- temporal consistency
- stale-pattern decay behaviour
- evidence-to-pattern traceability

### Educational utility

- recommendation acceptance/usefulness
- improvement on targeted concepts
- calibration of learner-state changes
- reduction in repeated misconception errors
- Tutor continuity quality

### Safety/privacy

- student isolation
- deletion completeness
- no canonical-KG mutation by LLM
- no unvalidated assessment content becoming servable

## 16. Implementation phases

### Phase 1 — durable conversations

Implement conversation/message persistence and bounded thread summaries. No learner-state mutation yet.

### Phase 2 — interaction evidence

Add structured extraction for high-value signals and curriculum linking. Store candidate evidence with provenance and confidence.

### Phase 3 — learner-pattern engine

Aggregate evidence over time. Add recurrence detection, temporal decay and contradiction handling.

### Phase 4 — recommendation integration

Expose interaction patterns to the existing recommendation engine as one evidence source among many.

### Phase 5 — Tutor personalization

Retrieve relevant learner interaction memory into Tutor context. Keep retrieval selective and explainable.

### Phase 6 — evaluation and calibration

Build annotated dialogue sets from real/consented conversations and benchmark extraction, mapping, recurrence and downstream recommendation quality.

### Phase 7 — controlled agent runtime

Add bounded read-only educational tools and multi-step Tutor workflows. Do not give the LLM direct mutation authority.

## 17. Non-goals

- Replacing BKT/BDT with an LLM personality model.
- Treating every chat question as evidence of weakness.
- Letting chat directly modify the authoritative KG.
- Creating a second learner model inside RAG.
- Storing an unlimited transcript in every Tutor prompt.
- Introducing a separate graph database for Cycle 1 solely for memory.
- Making a paid memory SaaS a hard dependency.
- Copying OpenHuman, Mem0, Letta or Graphiti into SyllabAI.

## 18. Architectural conclusion

The correct SyllabAI model is:

```text
Conversation history
       ↓
Interaction evidence
       ↓
Longitudinal learner patterns
       ↓
Existing learner model + diagnosis + recommendation
       ↓
Personalized Tutor / KG views
```

not:

```text
Chat transcript
       ↓
Vector database
       ↓
LLM
```

This makes Tutor dialogue another governed learning-evidence channel and connects it to the existing adaptive-learning loop without creating a competing learner model or corrupting the authoritative educational knowledge graph.
