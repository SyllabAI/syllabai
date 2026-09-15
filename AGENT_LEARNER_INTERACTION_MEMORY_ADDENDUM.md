# Agent Addendum — Learner Interaction Memory

This document is mandatory reading for work involving tutor chat, conversational surfaces, learner interaction signals, engagement memory, Smart Lesson tutor legs, NBA tutor-engagement tiers, or any future Contextual Learning Assistant code.

## Canonical architecture

Read `LEARNER_INTERACTION_MEMORY_ARCHITECTURE.md` (canonical), `MASTER_SPEC_ADDENDUM_1.4_LEARNER_INTERACTION_MEMORY.md` (spec layer) and `syllabai-core/docs/LEARNER_INTERACTION_MEMORY_IMPLEMENTATION.md` (core implementation binding) before implementation.

## Non-negotiable rules

1. Raw chat text is audit/history (research telemetry) — never learner truth, never learner memory, never a serving input.
2. LLM output is candidate evidence; only deterministic pipeline outputs (intent matcher, tutor policy plan, fixed pattern classification) may back interaction-memory rows or serving decisions.
3. Every interaction-memory row carries provenance: grounding strength, refusal flag, answering-model identity, deterministic signal class. No provenance, no row.
4. Signal classification is deterministic and precedence-ordered (misconception-related > doubt > explanation-request > topic engagement); never classify with an LLM; keep precedence pinned by tests.
5. Refused asks keep their topic rows — an unanswered ask is an unresolved signal, not a non-event.
6. All read paths are learner-scoped; no cross-learner view outside the evidence-lineage rules of the assessment-evidence contract.
7. No chat path mutates the canonical knowledge graph, validation state, mastery, or misconception probabilities — conversational evidence reaches learner state only through the governed evidence → learner-model pipeline.
8. Never implement chat-triggered learner arithmetic (including the forbidden `−0.02`/`+0.01`/self-doubt-halving rules) on the conversational path.
9. Bounded reads only: declare the window for every consumer; unbounded history reads need an architecture decision.
10. Shared LLM chain, separate workloads: tutor, Smart Mark, extraction and embeddings stay separately pinned, separately telemetry-tagged, independently replaceable; no workload consumes another's prompt, budget or output.
11. Agentic tools are application-controlled: server-owned registry and policy; provider-autonomous tools, memory or session state are rejected.
12. The Contextual Learning Assistant implements its core contract (`syllabai-core/docs/CONTEXTUAL_LEARNING_ASSISTANT_IMPLEMENTATION.md`) and the answer-leakage policy before any runtime code lands; its evidence capture extends, never replaces, this memory contract.

## Scope

Long-term product architecture; no Cycle-1 scope expansion. Cycle 1 remains 4CH1 (ADR-019), Tutor + Assessor agents.
