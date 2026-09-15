# Contextual Learning Assistant — Canonical Architecture

**Status:** Steps 1–2 IMPLEMENTED / VERIFIED (core `544bad1`, V24 lineage — KG_TOPIC + PAST_PAPER_QUESTION ResourceContexts, bounded read-only tools, EXPLAIN/SUMMARIZE/HINT/CHECK on the Tutor stack, the §7 deterministic answer-leakage gate with its CI-mandatory negative suite, LIM evidence capture; claim-by-claim acceptance in `syllabai-core/docs/CLA_STEP1_RUNTIME_ACCEPTANCE.md`). Remaining: §10.4 evaluation bundle + further context kinds — PROPOSED-governed work; this document does not claim the complete CLA is implemented
**Date:** 2026-09-15
**Companions:** `MASTER_SPEC_ADDENDUM_1.5_CONTEXTUAL_LEARNING_ASSISTANT.md` (spec addendum), `AGENT_CONTEXTUAL_LEARNING_ASSISTANT_ADDENDUM.md` (binding agent rules), `syllabai-core/docs/CONTEXTUAL_LEARNING_ASSISTANT_IMPLEMENTATION.md` (core implementation contract, resolves syllabai-core#17), ADR-022 (decision record)
**Builds on:** ADR-016 (evidence substrate), ADR-017 (recommendation), ADR-020 (retrieval engine), `LEARNER_INTERACTION_MEMORY_ARCHITECTURE.md`

---

## 1. Motivation

The Grounded Tutor answers free-standing questions. The next conversational step is an assistant that works **in the context of what the learner is currently reading or doing** — a spec point in the syllabus browser, a section of a validated note, a question part in a past paper, a Smart Lesson topic — and that reacts *there*, with the same grounding, evidence and refusal discipline the Tutor already has.

The architectural risk this contract exists to prevent: a context-aware assistant is one shortcut away from becoming a generic chat layer that trivializes assessment content ("just tell me the answer"), mutates learner state from chat, or lets a provider own the context and memory. SyllabAI's answer is a contract-first design where the platform owns context resolution, policy, tools, evidence and leakage control — and the model only generates within them.

## 2. Composition, not replacement

The CLA composes four verified subsystems and must not fork them:

| Subsystem | Role in the CLA |
|---|---|
| Educational Retrieval Engine (ADR-020) | evidence acquisition, context-anchored |
| Grounded Tutor (KA-RAG) | grounded generation, deterministic refusal, citation validation |
| Learner Interaction Memory (V21/V23) | evidence capture of every exchange |
| Learner state + NBA | governed consumption; never chat-written |

## 3. The five contract primitives

1. **ResourceContext** — the server-resolved anchor (kind, canonical reference, curriculum version, validation state, learner). Clients pass opaque references; the server resolves fail-closed. Validation gates apply: SUGGESTED content never enters assistant evidence.
2. **ContextPolicy** — what the resolved context may contribute (spec/notes/concepts ground explanations; question content participates under the leakage policy; learner state personalizes framing, never fabricates facts). Content-derived text is data, not instructions.
3. **ResponseMode** — `EXPLAIN | HINT | CHECK | SUMMARIZE`, explicit per request, safest default, deterministically constraining prompts and leakage behavior.
4. **ToolPolicy** — server-owned registry; v1 read-only tools (retrieval, own-state read, review-schedule read, practice handoff); every invocation telemetry-captured; no tool writes canonical KG or learner state; per-request tool budget server-enforced.
5. **Evidence capture** — every exchange emits LIM-compatible provenance-bearing signals (deterministic anchors only); raw text stays in research telemetry; citations pass the Tutor's claim/citation validation.

## 4. Exam-question answer-leakage policy

The CLA's defining safety property. Answer-protection is **deterministic, application-enforced, and CI-tested** — never prompt-only, never model-judged:

- protected content = question/mark-scheme material with pending attempts or in timed/mock/assignment contexts;
- `HINT` on protected content may scaffold but never reveals final answers or mark-scheme points;
- full worked feedback (`CHECK`, `EXPLAIN`) unlocks only **post-attempt**, proven from attempt evidence on the same substrate Review Hub reads;
- the negative leakage suite is CI-mandatory before any runtime PR merges.

## 5. Security and privacy posture

Student isolation identical to LIM; no cross-learner context composition; teacher surfaces separate and separately evidenced; prompt-injection containment is structural (content is quoted evidence, not instructions); shared-model/separate-workload rules apply unchanged; provider-side memory/session state rejected.

## 6. Evaluation gate

Runtime promotion requires an evaluation bundle on real validated 4CH1 material: grounded-precision per mode, refusal correctness, leakage negative suite, citation-validation pass rate, and no regression in the serving-surface performance guard — the same benchmark discipline ADR-020 applies to retrieval.

## 7. Implementation sequencing (when accepted)

1. `KG_TOPIC` context + read-only tools + `EXPLAIN`/`SUMMARIZE` on the Tutor stack;
2. attempt-aware `CHECK`/`HINT` + leakage gate + negative CI suite;
3. LIM capture for CLA exchanges (deterministic signal extension);
4. evaluation bundle + promotion decision.

Each step lands behind its own tests; none may weaken §§2–6 to ship earlier.

## 8. Scope guard

ADR-022 and this architecture authorize **contract and evaluation design only**. No Cycle-1 scope expansion; the pilot remains 4CH1 with Tutor + Assessor agents. CLA runtime work begins only as a separately planned, separately verified tranche.
