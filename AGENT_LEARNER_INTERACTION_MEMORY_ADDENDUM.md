# Agent Addendum — Learner Interaction Memory

**Status:** Binding implementation guidance  
**Date:** 2026-09-14  
**Primary implementation repo:** `syllabai-core`

## 1. Required reading

Agents implementing Tutor memory, chat analytics, learner recommendations, learner KG personalization or interaction-derived evidence MUST read:

1. `MASTER_SPEC.md`.
2. `MASTER_SPEC_ADDENDUM_1.4_LEARNER_INTERACTION_MEMORY.md`.
3. `LEARNER_INTERACTION_MEMORY_ARCHITECTURE.md`.
4. `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md`.
5. `RECOMMENDATION_SYSTEM_ARCHITECTURE.md`.
6. `KNOWLEDGE_GRAPH_CONTEXT.md`.
7. `RAG_RETRIEVAL_RESEARCH.md` for retrieval behavior.

## 2. Non-negotiable invariants

### Raw chat is not learner truth

Never convert every student message into a mastery update.

### LLM output is candidate evidence

LLM-derived interaction evidence is a candidate observation with provenance and confidence. It must pass the normal evidence/normalization policy before affecting learner-state calculations.

### Canonical KG is protected

Chat-derived inference cannot create or mutate authoritative curriculum nodes, SpecificationPoints, prerequisite relations or canonical misconception definitions.

### Evidence is immutable history

Do not overwrite prior interaction evidence when a later conversation contradicts it. Record later evidence and let the aggregate learner model handle temporal/contradictory evidence.

### Derived patterns are recomputable

A `LearnerInteractionPattern` is derived state. Keep supporting evidence references so it can be recomputed and audited.

### Student isolation is mandatory

Every conversation, evidence and pattern read/write path must be scoped to the authenticated student and authorized subject/class context. No cross-student retrieval.

### Idempotency is mandatory

Repeated extraction of the same source turn with the same extractor version must not create duplicate evidence.

### Model/provider provenance is mandatory

Record provider, model and prompt/extractor version for LLM-derived evidence where the existing telemetry contract supports it.

## 3. Extraction policy

Prefer this order:

```text
persist message
  ↓
deterministic low-cost signal checks
  ↓
structured LLM extraction only when educational substance warrants it
  ↓
validate + normalize + curriculum-link
  ↓
store candidate evidence
  ↓
aggregate patterns asynchronously
```

Do not make the Tutor request wait on a full longitudinal pattern recomputation unless the product explicitly requires synchronous behavior.

## 4. Evidence-strength policy

Treat the following as stronger evidence:

- explicit persistent difficulty;
- explicit misconception statements;
- repeated incorrect reasoning;
- repeated confusion across independent interactions.

Treat the following as weaker evidence:

- a single request for an explanation;
- a definition request;
- asking for an example;
- uncertainty without recurrence.

Greetings, thanks, acknowledgements and Tutor-generated text alone are not learner evidence.

## 5. Tutor context policy

Tutor prompts may receive selected learner interaction memory, not an unlimited transcript or complete student profile.

Retrieval should prefer:

1. subject/curriculum match;
2. relevant SpecificationPoint / concept;
3. recent evidence;
4. repeated/high-confidence patterns;
5. unresolved misconceptions;
6. evidence that can improve the current intervention.

## 6. Smart Mark policy

Do not create a separate LLM dependency solely because interaction memory exists. Tutor, Smart Mark and interaction extraction may share a model/provider, but must keep separate prompts, schemas, validation and telemetry.

## 7. Agentic Tutor policy

The LLM proposes; the application authorizes.

No agent tool may bypass:

- curriculum authority;
- teacher validation;
- assessment evidence immutability;
- learner-model update rules;
- student authorization boundaries.

Start with read-only educational tools wherever possible.

## 8. External repositories

External memory repositories are references, not automatic dependencies.

- OpenHuman: architecture inspiration; GPL-3.0 implementation is reference-only.
- Mem0: useful memory extraction/retrieval reference.
- Letta: useful short-term/long-term memory separation reference.
- LangGraph: useful persistence/checkpoint/store separation reference.
- Graphiti: useful temporal provenance and episode model reference.
- Dialogue-KT: direct educational evidence research/code reference.

Before copying code, check current license and ADR-013.

## 9. Throughput rule

Interaction-memory work should follow the normal autonomous execution policy:

```text
detect → diagnose → implement → test → verify → commit → continue
```

Do not stop for human approval merely because an extraction test fails, a provider changes, or a pattern rule needs repair. Escalate only for genuine credentials/access, destructive irreversible external action, product/business/legal/security decisions or an architecture/scope change that cannot be safely inferred.
