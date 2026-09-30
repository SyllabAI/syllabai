# Learner Interaction Memory — Canonical Architecture

**Status:** IMPLEMENTED (V21/V23 runtime in `syllabai-core`, battery-verified surfaces) — this document is the canonical cross-project architecture record
**Date:** 2026-09-15
**Companions:** `MASTER_SPEC_ADDENDUM_1.4_LEARNER_INTERACTION_MEMORY.md` (spec addendum), `AGENT_LEARNER_INTERACTION_MEMORY_ADDENDUM.md` (binding agent rules), `syllabai-core/docs/LEARNER_INTERACTION_MEMORY_IMPLEMENTATION.md` (core implementation contract, resolves syllabai-core#16)
**Upstream contracts:** `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` (evidence substrate), ADR-017 (recommendation), ADR-020 (retrieval), `DECISIONS.md` ADR-016

---

## 1. What Learner Interaction Memory is

Learner Interaction Memory (LIM) is SyllabAI's bounded, provenance-bearing memory layer for *conversational* learning interactions. It is the component that lets the Tutor (and, later, the Contextual Learning Assistant) leave a governed trace in the learner model — without ever storing chat transcripts as learner truth.

The three-layer separation it enforces:

```text
Raw conversation            → research telemetry / audit-history only
Extracted interaction evidence → structured, append-only, provenance-bearing rows
Derived learner state       → mastery / misconceptions / struggle / review (governed pipeline)
```

This mirrors the assessment-side invariant (immutable evidence ≠ mutable review state ≠ derived mastery) for the conversational modality, and it is the architectural reason the product can personalize from chat without becoming a privacy hazard or letting an LLM redefine what a learner knows.

## 2. Canonical semantics

### 2.1 Signal rows, not transcripts

The unit of learner interaction memory is a **per-topic interaction fact**: "the learner asked about topic X at time T; the ask was grounded by N evidence items (or was refused); the answering model was M; the deterministic signal class is S". Topic anchors come exclusively from the deterministic intent matcher over VALIDATED curriculum nodes — never from model output. This makes every row provenance-complete: it can be audited, windowed, and consumed by downstream policies without trusting any generative component.

### 2.2 Deterministic signal classification

Exactly one signal class per interaction, precedence-ordered, all computed at record time from facts already in the pipeline:

1. `MISCONCEPTION_RELATED` — the diagnosis-aware tutor policy intervened on an active BDT misconception (a rule output over measured learner state);
2. `DOUBT_SIGNAL` — explicit confusion phrase in the learner's own words (fixed substring list — the learner's self-report, deterministically detected);
3. `EXPLANATION_REQUEST` — explanation command vocabulary;
4. `TOPIC_ENGAGEMENT` — the topic-match fact alone.

Refused asks keep their topic rows: an unanswered ask is still an unresolved learning signal. Signal classification is deterministic by design — an LLM-judged classification would make learner memory model-dependent and un-auditable, and is rejected.

### 2.3 Bounded memory

Interaction memory is consumed through explicit time windows (Smart Lesson's tutor-engagement window; the learner-state view's 30-day signal counts). Boundedness is semantic (facts about topics, not transcripts) and operational (windowed reads). Unbounded history reads require an architecture decision.

### 2.4 Student isolation

Every read path is learner-scoped at the repository level. Teacher/research consumption goes through the evidence-lineage and authorization rules of the learning-evidence contract, never through ad-hoc queries.

## 3. Where it sits in the system

```text
Tutor / future CLA surface
        ↓  answer + deterministic pipeline facts (in-process event)
Learner Interaction Memory (append-only signal rows)
        ↓  read-only, windowed, learner-scoped
LearnerStateController signal counts · Smart Lesson legs · NBA (T7a tier)
        ↓  governed learner-model logic only
Learner state (mastery, misconceptions, review) — never written by chat
```

Consumers are read-only. The conversational path has **no write path** into the canonical knowledge graph or into mastery/misconception probabilities; conversational evidence influences the learner only by being *consumed as evidence* by the same governed learner-model logic that consumes assessment evidence.

## 4. Implemented vs proposed

| Capability | Status |
|---|---|
| Per-topic engagement rows with provenance (V21 P7) | **IMPLEMENTED / VERIFIED** (battery-covered) |
| Deterministic V23 signal classification | **IMPLEMENTED / VERIFIED** |
| Learner-state signal counts (30-day) | **IMPLEMENTED / VERIFIED** |
| Smart Lesson tutor-engaged leg + NBA T7a (`nba-rules/v1.2`) | **IMPLEMENTED / VERIFIED** |
| Smart Lesson advance leg consuming doubt/misconception signals | **IMPLEMENTED / VERIFIED** |
| CLA exchange capture (context-aware signals) | **PROPOSED** (ADR-022 + core contract) |
| Cross-session conversational threading | **REJECTED for now** — bounded topic-fact memory is the product semantics; transcripts are audit data |

## 5. Extension contract

New conversational surfaces attach by emitting provenance-bearing events with deterministic anchors, classifying deterministically at record time, appending rows under the binding rules, and consuming read-only with declared windows. The full binding rule set lives in `AGENT_LEARNER_INTERACTION_MEMORY_ADDENDUM.md`; the core implementation binding lives in `syllabai-core/docs/LEARNER_INTERACTION_MEMORY_IMPLEMENTATION.md`.

## 6. Privacy and provenance posture

Raw conversation text remains in research telemetry under the existing telemetry contract (audit/history; never learner-servable, never in learner state). Learner interaction memory stores no free text at all. This is the property that lets SyllabAI claim "the system learns from your questions" without retaining your questions as learner data.
