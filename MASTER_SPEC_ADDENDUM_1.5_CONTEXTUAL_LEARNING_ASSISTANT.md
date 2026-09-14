# MASTER SPEC ADDENDUM 1.5 — Contextual Learning Assistant

**Date:** 2026-09-14  
**Status:** Proposed product capability / architecture decision  
**Supersedes:** None; additive to Master Spec v1.4 Learner Interaction Memory

## 1. Purpose

SyllabAI will provide a floating **Contextual Learning Assistant** on resource pages, initially Revision Notes and Exam Questions.

The assistant is a context-aware mode of the existing Tutor/AI runtime. It is not an independent chatbot, independent learner model, or independent knowledge graph.

## 2. Core product principle

> The page the learner is studying is a trusted context anchor, but the page is not the source of canonical truth by itself.

The application resolves the current resource, its specification anchors, validated content, assessment evidence and relevant learner evidence. The LLM receives a structured context package and operates under a context policy.

## 3. Required resource modes

### Revision Note mode

Required context:

- resource identity;
- subject, qualification, exam board and specification version;
- linked SpecificationPoints;
- linked canonical KG nodes;
- validated note content/current section;
- relevant learner state/evidence.

Required quick actions:

- Definitions;
- Summary;
- Pitfalls / misconceptions;
- Exam help;
- free-form contextual question.

### Exam Question mode

Required context:

- question identity;
- subject, qualification, exam board and specification version;
- question/subparts;
- marks and command words;
- linked SpecificationPoints/KG nodes;
- validated mark scheme and examiner guidance where available;
- relevant learner state/evidence.

Required quick actions:

- Understand;
- Approach;
- free-form contextual question.

## 4. Context policy

The assistant must apply three levels:

1. **Page-locked:** answer from the current resource and its authoritative context.
2. **SyllabAI-aware:** locate another SyllabAI resource when the learner's question belongs elsewhere.
3. **General educational:** only answer beyond SyllabAI context when policy allows and the distinction from authoritative resource content is clear.

Off-topic educational requests should normally be routed to the correct SyllabAI subject/resource instead of being answered as though they belonged to the current page.

## 5. Authority and grounding

The existing SyllabAI authority hierarchy remains unchanged:

```text
Official curriculum / assessment evidence
→ validated SyllabAI resource
→ SpecificationPoint / canonical KG
→ validated assessment / mark-scheme evidence
→ learner evidence/state
→ retrieval
→ general LLM knowledge
```

Semantic retrieval cannot promote content into educational truth.

## 6. Tool contract

The application may expose bounded educational tools including resource lookup, specification lookup, KG lookup, learner-state retrieval, resource navigation, practice start and similar-question lookup.

The LLM may propose tool calls. The application validates identity, authorization, scope and arguments before execution.

The LLM must never directly mutate canonical educational state, mastery values, assessment truth, teacher validation state or another learner's data.

## 7. Exam-question tutoring policy

Exam Question mode should teach rather than immediately solve.

Default progression:

```text
Understand → Hint → Approach → Guided steps → Attempt → Smart Mark → Improve
```

The product must define explicit answer-leakage rules before production rollout. Smart Mark remains the dedicated marking system and must not be replaced by a conversational claim of “official marking.”

## 8. Learner Interaction Memory

All assistant interactions are eligible for the existing Interaction Evidence pipeline.

```text
chat turn
→ candidate interaction evidence
→ provenance/confidence/idempotency
→ learner evidence
→ recurring pattern aggregation
→ diagnosis/recommendation/learner-state consumers
```

Chat evidence cannot directly set mastery or mutate the canonical KG.

## 9. Security and trust

The client may provide a resource identifier but cannot be trusted to define the resource's subject, specification, mark scheme, answer or educational content.

The server must resolve the resource and build `ResourceContext` from authorized canonical/validated data.

Resource content, learner content and tool results are data, not system instructions. Prompt-injection defenses and structured tool validation are mandatory.

## 10. Non-goals

This amendment does not authorize:

- unrestricted web browsing by the Tutor;
- arbitrary agent actions;
- a separate assistant-specific KG;
- a separate learner model;
- direct LLM writes to canonical curriculum/assessment data;
- automatic promotion of imported assessment content;
- mandatory use of a new LLM provider/model.

## 11. Likely implementation boundary

Introduce a shared contextual runtime around the existing Tutor service:

```text
ResourceContext
ContextPolicy
ToolPolicy
ResponseMode
EvidenceCapture
       ↓
Existing Tutor / LlmProvider abstraction
```

This allows Revision Note Chat, Exam Question Chat and general Tutor interactions to share provider infrastructure while keeping workload-specific policy and evaluation separate.

## 12. Acceptance criteria

The feature is not product-ready until the implementation can demonstrate:

- correct resource/specification context;
- student authorization and isolation;
- grounded responses;
- reliable off-topic routing;
- no unauthorized tool actions;
- controlled exam-answer disclosure;
- interaction evidence capture with provenance;
- honest provider failure behavior;
- measurable latency;
- no mutation of canonical KG/assessment truth by the LLM.
