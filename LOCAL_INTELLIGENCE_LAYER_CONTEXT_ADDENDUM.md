# Local Intelligence Layer — Project Context Addendum

**Status:** PROPOSED
**Date:** 2026-09-17
**Canonical detail:** `LOCAL_INTELLIGENCE_LAYER_ARCHITECTURE.md`
**Tracking:** T-LIL / issue #10

## What this is

SyllabAI is investigating a browser-local **Local Intelligence Layer** that makes the website locally agentic without making local LLM inference a requirement for the product.

The product requirement is especially important because SyllabAI will run in mobile browsers on low/mid-range devices:

> SyllabAI must feel fast and snappy even when the device has no capable GPU and no local model runtime.

Therefore the architecture is:

```text
fast deterministic website
        ↓
optional local controller
        ↓
server controller fallback
        ↓
large Tutor for deep work
```

## Core architectural principle

The stable architecture is the **SyllabAI semantic tool contract**, not any specific model.

```text
local tiny model
server controller
large Tutor
       ↓
common SyllabAI tool contract
       ↓
SyllabAI authoritative application
```

The local model is a language-to-action controller over structured SyllabAI capabilities. It is not the curriculum authority, KG authority, learner-model authority, assessment engine or Tutor replacement.

## Primary research candidate

**Needle 2 — PROPOSED candidate.** Current official documentation describes a 45M-parameter, 14 MB model with approximately 28 MB full-session RAM, structured/schema-constrained tool calls, tool retrieval, confidence gating, 256-token sliding context and a WebAssembly component. These are external/vendor claims and remain UNVERIFIED for SyllabAI until measured on target devices.

Secondary candidates:

- LFM2.5 230M/350M class;
- FunctionGemma 270M;
- Qwen3 0.6B class;
- WebLLM/WebGPU only as an optional high-capability path.

## Existing SyllabAI features that benefit

The Local Intelligence Layer can sit over existing:

- subject/curriculum context;
- SpecificationPoints;
- Revision Notes;
- Exam Questions/Past Papers;
- authoritative Knowledge Graph;
- learner state and learning evidence;
- recommendations/next-best-action;
- Smart Mark;
- practice/intervention flows;
- Tutor.

This does not imply those systems need redesign. The likely additions are:

1. Semantic Page Context;
2. a stable semantic local-tool contract;
3. a model/runtime abstraction;
4. confidence/capability-based escalation.

## Non-negotiable boundaries

The local model must not:

- mutate authoritative curriculum or SpecificationPoints;
- create/promote authoritative KG edges;
- directly change mastery;
- create validated learner evidence by itself;
- bypass assessment validation;
- execute arbitrary browser JavaScript/DOM/network operations;
- treat semantic similarity as educational truth.

## Development direction

1. Define Semantic Page Context and semantic tool contract.
2. Build deterministic tool broker first, with no model dependency.
3. Benchmark Needle 2 against real SyllabAI utterances/page contexts.
4. Prototype WASM/Web Worker execution on low/mid Android and iOS Safari.
5. Enable natural-language navigation, KG/curriculum lookup, Revision Notes, Exam Questions, learner review and governed practice.
6. Add Smart Mark/evidence/remediation and Tutor escalation.
7. Only then consider richer local models or SyllabAI-specific fine-tuning.

## Post-research updates (2026-10-01 — recorded in full in the canonical document's correction block; verbatim-preserving)

1. **ADR-029 alignment:** "the website" now means `syllabai-hub` (product frontend per ADR-029, 2026-09-28); `syllabai-web` is the internal teacher/ops console. Semantic Page Context and the deterministic tool broker belong in the hub, through core proxies.
2. **Retrieval-quality gate:** LIL's fast-path value is gated on the retrieval promotion lane (VALIDATED-only serving is 317/3,831 chunks; all RAG §8 promotion verdicts NOT PROMOTED; live refusal 27–31% per the Tutor current-state audit 2026-09-28). Phases 2+ must not be scheduled ahead of it.
3. **Model refresh:** Cactus released Needle 3 (121M params, 8–29 MB weight slices, tool-calling-only) on 2026-09-17/19 — see the canonical document §4.1b. The Phase 2 benchmark set is now Needle 2 vs Needle 3. All external claims remain UNVERIFIED for SyllabAI.

See `LOCAL_INTELLIGENCE_LAYER_ARCHITECTURE.md` for the full research, tool catalogue, performance plan, benchmark, failure modes, security boundaries and rollout plan.
