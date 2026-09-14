# Master Specification Addendum — Learner Interaction Memory and Current AI Runtime

**Applies to:** `MASTER_SPEC.md` v1.3.0  
**Date:** 2026-09-14  
**Status:** Canonical addendum pending next numbered Master Spec revision

This addendum is part of the Master Specification architecture. Until the next controlled `MASTER_SPEC.md` revision folds these clauses into the numbered sections, agents must treat this document as binding for Tutor memory, interaction evidence and AI-provider architecture.

## A. Product architecture amendment

SyllabAI's product definition includes a fourth evidence path alongside assessment, Smart Mark and direct learner-state evidence:

```text
Official curriculum + assessment evidence
                  ↓
        Structured knowledge / KG
                  ↓
          Learner state model
                  ↑
        Learning Evidence
          ↑      ↑      ↑
     Attempts  Smart Mark  Tutor Interaction
                              ↓
                    Interaction Evidence
                              ↓
                    Longitudinal Patterns
                              ↓
                 Diagnosis / Recommendation
```

Tutor conversations are therefore both a user-facing interaction and a potential source of structured learning evidence.

## B. New bounded-context responsibility

Within `syllabai-core`, the existing learner/diagnostic/recommendation/tutor boundaries gain an explicit **Learner Interaction Memory** responsibility.

Its responsibilities are:

- durable conversation history;
- bounded thread memory;
- structured interaction-evidence extraction;
- provenance and source-turn linkage;
- curriculum/knowledge resolution;
- longitudinal interaction-pattern aggregation;
- retrieval of relevant learner interaction context for Tutor;
- downstream integration with Learning Evidence, diagnosis and recommendation.

This is not a second learner model and not a generic RAG memory store.

## C. Canonical memory layers

1. **Conversation record** — raw ordered messages and execution metadata.
2. **Working conversation memory** — bounded context for the active Tutor thread.
3. **Interaction Evidence** — structured observations tied to source turns.
4. **Learner Interaction Patterns** — derived longitudinal aggregates.

The underlying evidence remains the source of truth for derived patterns.

## D. Knowledge-graph rule

The authoritative educational KG is never mutated by Tutor chat or an LLM.

Interaction evidence may reference existing `SpecificationPoint` and `KnowledgeNode` identifiers. Unresolved concepts remain candidates until mapped to the authoritative graph. Personalized KG views may aggregate interaction evidence, but the canonical curriculum and relationship definitions remain immutable to chat-derived inference.

## E. Learner-state rule

Chat evidence must not directly set mastery.

The existing Learning Evidence / Learner Model policy combines interaction evidence with assessment evidence, Smart Mark, confidence, exposure, procedural fluency, misconceptions and temporal factors. A single question or request for explanation is insufficient evidence of weakness unless the evidence policy says otherwise.

## F. Recommendation rule

Recommendations remain **Next Best Learning Action**. Interaction patterns are an evidence input, not the recommendation itself.

Example:

```text
Repeated chat confusion
+ assessment errors
+ Smart Mark reasoning errors
        ↓
Recurring concept-level pattern
        ↓
Diagnosis
        ↓
Targeted learning action
        ↓
Assessment / evidence update
```

## G. Tutor-memory rule

Tutor has two memory paths:

- **thread memory** for immediate conversational continuity;
- **learner memory** for selectively retrieved longitudinal evidence.

Do not place the full learner history into every prompt. Retrieve relevant, recent, high-confidence evidence only.

## H. AI workload rule

SyllabAI does not require one LLM per feature.

The provider-neutral `LlmProvider` may serve:

- Tutor generation;
- Smart Mark candidate generation;
- Interaction Evidence extraction;
- future bounded agent workflows.

These are distinct workloads and must retain separate prompts, schemas, validators, telemetry and provider policies even when they share a model.

Embeddings remain a separate `EmbeddingProvider` workload used for retrieval. Vector similarity is never educational truth.

## I. Agent runtime rule

Agentic Tutor behavior is an application runtime property. Models propose actions; application policy validates permissions and educational safety; bounded tools execute; termination rules control the loop.

LLMs cannot directly mutate:

- authoritative curriculum;
- authoritative KG structure;
- learner mastery;
- assessment evidence;
- teacher validation state;
- another student's data.

## J. Current provider position

The current production generation path is Groq `openai/gpt-oss-120b`, with official Gemini and OpenRouter free models available through the provider abstraction as fallbacks/alternatives. Current embeddings use Gemini `gemini-embedding-001` at 768 dimensions.

Provider/model identifiers are configuration, not architecture invariants. Availability, quotas and model catalog entries must be re-verified before deployment changes.

See `AI_RUNTIME_AND_PROVIDER_REPORT_2026-09-14.md` for the current provider analysis and free/no-card strategy.

## K. External-reference policy

OpenHuman, Mem0, Letta, LangGraph, Graphiti/Zep and dialogue knowledge-tracing research are reference architectures. SyllabAI should learn from their separation of raw experience, memory, provenance, retrieval and temporal aggregation, but must not import a generic memory layer that bypasses the SyllabAI learner-evidence contract.

OpenHuman's GPL-3.0 implementation is reference-only under ADR-013. Permissively licensed projects such as Mem0/Graphiti may be studied, but adoption still requires an explicit architecture and license review.

## L. Canonical detailed design

`LEARNER_INTERACTION_MEMORY_ARCHITECTURE.md` is the detailed architecture and implementation blueprint for this addendum.
