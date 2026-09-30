# ADR-025: Smart Mark product contract — the bounded per-part marker inside Exam Questions; no chatbox

**Status:** Accepted (operator decision, 2026-09-18)
**Date:** 2026-09-18
**Scope:** Smart Mark product placement and UX contract (Master Spec §15.1 amendment; build lane T-C21). No change to the Smart Mark pipeline's semantics, the deterministic validator stack, the κ agreement gate, the question-attempt evidence contract, or the CLA leakage policy.

## Context

The Master Spec (§15) describes Smart Mark as an explainable assessment subsystem — answer normalization → question/scheme decomposition → evidence-to-mark-point alignment → partial credit → misconception detection → score + explanation + confidence → teacher review — but never states the **product contract**: where Smart Mark lives, what its surface is, and what it is not. An operator product-clarification round (session 101) also surfaced a proposal to move to whole-question marking (all parts of a question marked in one context against the full scheme). The operator has now fixed both questions.

## Accepted

- **Placement.** Smart Mark is the in-page marking widget on **Exam Questions pages** and the **single marking authority** in the product. The tutor/CLA explain; Smart Mark marks. Smart Mark has **no chatbox** — it is a bounded marking flow, never a conversational surface.
- **The marking unit stays per-part** (operator decision, 2026-09-18): one `Answer` per `QuestionPart`; the marker scores each part against that part's in-scope validated scheme points (`MarkingContext(answer, part, scheme, inScope)` unchanged). Full-question/full-scheme rendering is **presentation context only** and never widens the marking scope. Rationale: per-point κ calibration (F-161), the bounds/mark-sum/coverage validators, and skipped/unattempted-part detection (evidence contract) all depend on the per-part unit.
- **Input presentation is a web-layer choice.** A combined input box for multi-part questions is permitted as presentation; whatever the UI collects, answers persist **per-part**, preserving the evidence contract.
- **Bounded post-mark actions.** After a Smart Mark the learner gets exactly two single-purpose actions — **"Explain my feedback"** and **"Improve my answer"** — served as governed grounded generation over the learner's answer and the question's own validated scheme points. These are not a conversation: no free-form chat UI, no multi-turn agent. Post-attempt leakage rules apply (scheme-point evidence only post-attempt; never into HINT-style scaffolding). Submitting a new answer re-runs Smart Mark; results are append-only (`SmartMarkResult` history preserved).
- **Self-mark remains a first-class alternative** (View Mark Scheme + human self-mark). Smart Mark is optional, never forced.
- **Question-level categorization powers three surfaces.** Atomized questions categorized at question level (topics/subtopics) drive: the **Exam Questions** repo (browsable, categorized), **Test Builder** (teacher paper authoring with filters — F-050), and **Target Test** (student-selected topics/subtopics → escalating difficulty → end-of-test strong/weak topic diagnosis). The filter/difficulty/type substrate is owned by T-C18 (`question_spec_points`, difficulty source, detected type); Target Test difficulty values are SME/EVIDENCE-validated only.
- **Boundary with the tutor/CLA.** The CLA's post-attempt `CHECK` feedback on question contexts stays *explanatory* — the tutor never awards marks, and Smart Mark never converses. One marking authority, one explanation surface.

## Rejected

- Whole-question marking with the full scheme as one marking context (dilutes per-point calibration, breaks validator scoping and skipped-part detection).
- A Smart Mark chatbox or any free-form conversation on the marking surface.
- A second marking authority (tutor/CLA awarding marks).

## Consequences

- Master Spec §15.1 records the contract; the build lane is registered as **T-C21** (Exam Questions Smart Mark surface). No core contract change is required: the existing per-part pipeline (`MarkingContext`, `SmartMarkService.markAnswer`, validator stack, κ gate) is already the accepted shape.
- Student-facing Smart Mark expansion remains behind the κ ≥ 0.60 agreement gate (F-161).

**Scope guard:** product placement/UX only — `SmartMarkPipeline`, validators, κ threshold, evidence contract and CLA leakage policy are byte-unchanged by design; build execution is separately tracked (T-C21) and gated on T-C18 for filter/difficulty substrates.
