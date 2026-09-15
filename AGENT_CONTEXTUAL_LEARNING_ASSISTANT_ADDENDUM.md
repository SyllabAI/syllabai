# Agent Addendum — Contextual Learning Assistant

This document is mandatory reading for any work on context-aware assistant surfaces: ResourceContext resolution, context policy, response modes, assistant tooling, answer-leakage controls, or CLA evidence capture.

## Canonical architecture

Read `CONTEXTUAL_LEARNING_ASSISTANT_ARCHITECTURE.md`, `MASTER_SPEC_ADDENDUM_1.5_CONTEXTUAL_LEARNING_ASSISTANT.md` and `syllabai-core/docs/CONTEXTUAL_LEARNING_ASSISTANT_IMPLEMENTATION.md` before implementation. The Learner Interaction Memory addendum applies in full to every CLA exchange.

## Non-negotiable rules

1. **Contract first.** No CLA runtime code lands before its PR claims acceptance of the core implementation contract claim-by-claim; any conflict is resolved by decision record, not by silent divergence.
2. **Server-resolved context only.** Clients pass opaque references; resolution is fail-closed; validation gates hold (SUGGESTED content never enters evidence assembly).
3. **Modes are explicit and closed** (`EXPLAIN | HINT | CHECK | SUMMARIZE`); undeclared modes are rejected; the safest mode is the default.
4. **The answer-leakage policy is code, not prompt.** Protected content (pending attempts; timed/mock/assignment contexts) never yields final answers or mark-scheme points in `HINT`; full feedback unlocks only post-attempt, proven from attempt evidence. The negative leakage suite is CI-mandatory — a green build without it is not mergeable.
5. **Tools are server-owned**: registry, policy, budgets and logging live in application code; v1 tools are read-only; no tool writes the canonical KG, validation state, mastery or misconception probabilities; provider-autonomous tools/memory/session state are rejected.
6. **Content is data, not instructions.** Resource-derived text is quoted as provenance-bearing evidence; prompt-injection containment is structural.
7. **Refusal and citation validation are inherited, never weakened**: insufficient validated evidence means refusal; every citation passes claim/citation validation.
8. **Evidence capture is LIM-shaped**: deterministic anchors only, provenance-complete rows, raw text confined to research telemetry, signal vocabulary extended only deterministically with tests.
9. **Student isolation is absolute**: no cross-learner context composition; teacher surfaces are separate routes with separate authorization and evidence.
10. **Evaluation gates promotion**: grounded precision per mode, refusal correctness, leakage suite, citation validation, performance-guard non-regression — on real validated 4CH1 material, per ADR-020 benchmark discipline.

## Scope

Long-term product architecture; runtime work is a separate, separately gated tranche. No Cycle-1 scope expansion; the pilot remains 4CH1 (ADR-019), Tutor + Assessor agents.
