# Decision Log — Contextual Learning Assistant

**Date:** 2026-09-14  
**Origin:** Product/architecture discussion  
**Status:** Recorded so the design survives chat/session changes

## 1. Discussion summary

The product discussion established that Revision Notes and Exam Questions should have a floating AI assistant that opens in the context of the resource currently being studied.

The assistant should support quick actions as well as ordinary text input.

### Revision Notes

Initial quick actions:

- Definitions — define key terms in the current note.
- Summary — summarise key points.
- Pitfalls — examine common misconceptions.
- Exam help — explain how to understand the topic for the relevant exam.

### Exam Questions

Initial quick actions:

- Understand — explain what the question is asking.
- Approach — help the learner work through the question.

The assistant should feel contextual rather than like a generic chatbot.

## 2. Product inspiration / research check

Additional current research was performed before recording this decision.

Save My Exams currently documents AI tools named **Revision Note Chat** and **Exam Question Chat**. Its public description says Revision Note Chat can explain tricky concepts, summarise key points and generate quiz questions; Exam Question Chat can help work through an exam question or explain what it is asking and has access to the question and mark scheme. Save My Exams also describes Guided Study and Guided Practice as AI study tools. [Save My Exams — Is Save My Exams AI? What Powers Our Study Tools](https://www.savemyexams.com/learning-hub/sme-articles/is-save-my-exams-ai/) 

Save My Exams explicitly positions its AI around examiner-written content, specifications and real mark schemes. [Save My Exams — Our Commitment to Exam Specificity](https://www.savemyexams.com/learning-hub/support/our-commitment-to-exam-specificity/) 

Its Revision Notes are organized around exam specifications, while its Exam Questions are organized by topic and aligned to specifications. [Revision Notes](https://www.savemyexams.com/study-tools/revision-notes/) and [Exam Questions](https://www.savemyexams.com/study-tools/exam-questions/)

The research confirms that the important idea is not merely “put a chatbot on the page.” The valuable architectural pattern is **resource-grounded AI whose context is tied to the learner's current specification-specific resource and assessment evidence**.

## 3. SyllabAI decision

Name the capability **Contextual Learning Assistant**.

Do not implement it as a separate chatbot stack.

Instead, extend the existing Tutor runtime with:

- `ResourceContext`
- `ContextPolicy`
- `ToolPolicy`
- `ResponseMode`
- `EvidenceCapture`

The assistant should share the existing provider abstraction and can initially use the same generation model as Tutor/Smart Mark/Interaction Evidence extraction, while maintaining separate workload prompts, schemas, validators, telemetry and fallback behavior.

## 4. Context is structured, not pasted blindly

The client may send a resource ID, but the server must derive the actual resource context.

For a Revision Note, context includes resource identity, subject, qualification, exam board, specification/version, SpecificationPoints, KG nodes, current section, validated content and relevant learner evidence/state.

For an Exam Question, context includes question identity, question/subparts, marks, command words, linked SpecificationPoints/KG nodes, validated mark scheme/examiner guidance and relevant learner evidence/state.

## 5. Guardrail decision

The assistant should be able to recognize when a request is outside the current page context.

Example:

> Physics Revision Note + “Explain the Krebs cycle.”

The assistant should not answer as if the Krebs cycle were part of the Physics note. It should explain that the request belongs to Biology and offer navigation to the relevant SyllabAI resource if available.

This is a **route, don't merely refuse** policy for relevant educational requests.

## 6. Exam-question tutoring decision

The Exam Question assistant should prioritize learning support over answer leakage.

The intended progression is:

```text
Understand
→ Hint
→ Approach
→ Step-by-step guidance
→ Student attempt
→ Smart Mark
→ Feedback
→ Improvement
```

The assistant should not silently substitute for Smart Mark. Smart Mark remains the dedicated marking workload with mark-scheme-aware deterministic validation.

## 7. Learner-memory decision

The contextual assistant is part of the Learner Interaction Memory architecture.

A chat is not itself learner truth.

Educationally meaningful turns can produce candidate InteractionEvidence, which then enters the existing evidence/pattern pipeline with provenance, confidence and idempotency.

Examples:

- “I still don't understand this” → potentially strong confusion evidence.
- “Can you explain it another way?” → medium evidence.
- repeated requests for examples → possible recurring difficulty.
- “Thanks” → no meaningful learner evidence by itself.

The assistant cannot directly mutate mastery or the canonical KG.

## 8. Agentic decision

The assistant may be agentic at the application level, but not unrestricted.

The LLM proposes a tool action; the application validates and executes it; the result returns to the LLM.

Candidate tools include current-resource lookup, specification lookup, curriculum/resource search, learner-state retrieval, practice start, similar-question lookup and navigation.

No arbitrary URL execution, canonical KG mutation, direct mastery writes, teacher-validation bypass or cross-student access.

## 9. Research conclusion

No additional broad research phase is currently required before documenting the architecture. The current product evidence is sufficient to make the design decision.

Further research should be **implementation-specific**, not exploratory: evaluate contextual grounding, off-topic routing, answer leakage, navigation accuracy, learner benefit, evidence-extraction precision, latency and provider failure behavior.

## 10. Durable references

Primary SyllabAI documents created/updated from this discussion:

- `CONTEXTUAL_LEARNING_ASSISTANT_ARCHITECTURE.md`
- `MASTER_SPEC_ADDENDUM_1.5_CONTEXTUAL_LEARNING_ASSISTANT.md`
- `AI_RUNTIME_AND_PROVIDER_REPORT_2026-09-14.md` (to incorporate contextual workload mapping)
- `LEARNER_INTERACTION_MEMORY_ARCHITECTURE.md`
- `MASTER_SPEC_ADDENDUM_1.4_LEARNER_INTERACTION_MEMORY.md`

This file exists specifically so the reasoning and product decisions are not lost when work moves between ChatGPT sessions, Z.ai agents or engineering workstreams.
