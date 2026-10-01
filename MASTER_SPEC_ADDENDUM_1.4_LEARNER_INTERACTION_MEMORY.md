# Master Spec Addendum 1.4 — Learner Interaction Memory

**Status:** Accepted (operator-registered contract, syllabai-core#16)
**Date:** 2026-09-15
**Amends:** Master Spec §6.6 (learner model), §6.8 (tutor), §6.12-era conversational surfaces
**Canonical architecture:** `LEARNER_INTERACTION_MEMORY_ARCHITECTURE.md`
**Agent rules:** `AGENT_LEARNER_INTERACTION_MEMORY_ADDENDUM.md`
**Core implementation binding:** `syllabai-core/docs/LEARNER_INTERACTION_MEMORY_IMPLEMENTATION.md`

## 1. Purpose

This addendum admits **Learner Interaction Memory (LIM)** as a named layer of the Master Spec's learner model: the bounded, provenance-bearing memory that conversational surfaces write and learner-model logic reads. It formalizes what the V21 (P7) and V23 runtime lineage already implemented and battery-verified, so that every future conversational surface inherits one contract instead of re-inventing its own.

## 2. Additions to the learner model (§6.6)

1. **Interaction evidence** joins the learner-model substrate beside assessment evidence: per-topic, append-only interaction facts with deterministic anchors and full provenance (grounding strength, refusal, answering-model identity, signal class).
2. Signal classes are a closed, precedence-ordered vocabulary: `MISCONCEPTION_RELATED` > `DOUBT_SIGNAL` > `EXPLANATION_REQUEST` > `TOPIC_ENGAGEMENT`, computed deterministically at record time. Extension of the vocabulary is a spec-level change, not a code-level convenience.
3. Interaction evidence is **windowed**: consumers declare their read windows; memory semantics are topic-facts, never transcripts.

## 3. Constraints on the tutor (§6.8) and all future conversational surfaces

1. The conversational path has **no write path** into the canonical knowledge graph or into mastery/misconception state. It may read; it may emit evidence events; nothing else.
2. Raw conversation is research telemetry (audit/history). It never enters learner memory, learner state, or serving decisions.
3. LLM output on the conversational path is **candidate evidence only**; only deterministic pipeline outputs may back memory rows or serving decisions.
4. The free-LLM chain is **shared model, separate workloads**: tutor generation, Smart Mark, extraction and embeddings are separately prompt-pinned, separately telemetry-tagged, independently replaceable.
5. Any agentic tooling is **application-controlled**: server-owned registry and policy; provider-autonomous tools/memory/session state are rejected.

## 4. Interaction with existing layers

- **Assessment evidence (ADR-016):** interaction evidence and assessment evidence remain distinct substrates; both are consumed by the same governed learner-model logic. A tutor ask is never scored like an attempt, and an attempt is never recorded as a chat fact.
- **Recommendation (ADR-017) / NBA:** the tutor-engagement tier (T7a, `nba-rules/v1.2`) consumes interaction evidence as an exploration prior — asked-but-not-practiced — without promoted mastery semantics.
- **Retrieval (ADR-020):** interaction signals may steer *retrieval* (what evidence to assemble), never *education truth* (what the curriculum says or what the learner knows).
- **Contextual Learning Assistant (ADR-022):** the CLA is the first new surface planned under this addendum; its contract (`syllabai-core/docs/CONTEXTUAL_LEARNING_ASSISTANT_IMPLEMENTATION.md`) inherits every rule here.

## 5. Scope guard

This addendum formalizes implemented behavior and binding rules; it authorizes **no new runtime scope**. Cycle 1 remains Edexcel IGCSE Chemistry 4CH1 under ADR-019, agents in scope: Tutor + Assessor.
