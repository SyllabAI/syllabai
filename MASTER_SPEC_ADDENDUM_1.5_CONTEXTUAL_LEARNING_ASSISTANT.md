# Master Spec Addendum 1.5 — Contextual Learning Assistant

**Status:** Accepted as contract direction (operator-registered contract, syllabai-core#17); runtime PROPOSED and separately gated
**Date:** 2026-09-15
**Amends:** Master Spec §6.8 (tutor), §5.2 (application layer), §6.6 (learner model, via Addendum 1.4)
**Canonical architecture:** `CONTEXTUAL_LEARNING_ASSISTANT_ARCHITECTURE.md`
**Agent rules:** `AGENT_CONTEXTUAL_LEARNING_ASSISTANT_ADDENDUM.md`
**Core implementation contract:** `syllabai-core/docs/CONTEXTUAL_LEARNING_ASSISTANT_IMPLEMENTATION.md`
**Decision record:** ADR-022 in `DECISIONS.md`

## 1. Purpose

This addendum admits the **Contextual Learning Assistant (CLA)** as a planned conversational surface: a grounded assistant that operates in the resolved context of the resource the learner is viewing (spec point, KG topic, note section, question part, Smart Lesson), composing the verified retrieval, tutor, interaction-memory and learner-state subsystems rather than introducing a new generative stack.

## 2. Contract primitives (normative)

1. **ResourceContext** — server-resolved, fail-closed, validation-gated; the client never asserts context semantics.
2. **ContextPolicy** — validated material grounds; question content participates under the leakage policy; learner state personalizes framing only; content-derived text is data, not instructions.
3. **ResponseMode** — closed vocabulary (`EXPLAIN | HINT | CHECK | SUMMARIZE`), explicit per request, safest default.
4. **ToolPolicy** — server-owned registry, v1 read-only, telemetry-captured invocations, server-enforced budgets; no tool writes canonical KG or learner state.
5. **Evidence capture** — every exchange emits provenance-bearing interaction signals under the Learner Interaction Memory contract (Addendum 1.4); raw conversation remains research telemetry.

## 3. Non-negotiable constraints

1. **Answer-leakage policy is deterministic and application-enforced**: protected content (pending attempts; timed/mock/assignment contexts) never yields final answers or mark-scheme points in `HINT`; full feedback unlocks only post-attempt, proven from attempt evidence. The negative leakage suite is CI-mandatory.
2. The CLA inherits the Tutor's **deterministic refusal** and **claim/citation validation** without weakening either.
3. The conversational path remains **write-free** against canonical KG and learner state (Addendum 1.4 §3).
4. Provider infrastructure never becomes canonical SyllabAI state: no provider-side memory, session, tools or context.
5. Runtime promotion requires the evaluation bundle (grounded precision, refusal correctness, leakage suite, citation validation, performance guard) per ADR-020 benchmark discipline.

## 4. Interaction with existing layers

- **Master Spec §39a / pilot scope:** the CLA is not part of the Cycle-1 pilot commitment; it is long-term product architecture that must not delay the pilot.
- **ADR-016 evidence contract:** attempt evidence is the unlock key for post-attempt feedback; the CLA reads the same substrate as Review Hub.
- **ADR-020 retrieval:** the CLA's context is an additional authoritative prior in the existing retrieval hierarchy — not a parallel retrieval path.
- **Addendum 1.4 (LIM):** CLA exchanges are captured as interaction evidence; signal vocabulary extends only deterministically.

## 5. Scope guard

Contract and evaluation design only. No runtime code is authorized by this addendum; each implementation step is a separately planned, separately verified tranche under the core contract's sequencing. Cycle 1 remains 4CH1 (ADR-019).
