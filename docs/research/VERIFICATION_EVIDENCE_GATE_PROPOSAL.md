# Verification Evidence Gate Proposal

**Status:** PROPOSED — not an accepted architecture change.
**Date:** 2026-10-18
**Owner:** SyllabAI learner evidence / learner model.
**Implementation PoC:** [syllabai-v2 PR #190](https://github.com/SyllabAI/syllabai-v2/pull/190).

## Decision question

Should SyllabAI maintain an explicit, provenance-backed verification-evidence view alongside BKT/BDT so product and recommendation layers can distinguish an attempted answer, supported success, independent success, and delayed transfer success?

## Current source-verified v2 findings

- The v2 assessment evidence event drives BKT skill-state and BDT misconception updates. The current event includes correctness, canonical topic/SpecificationPoint anchors, question identity/type, misconception tags and timestamp.
- The event contract does not include a first-class, application-authored assistance/solution-exposure field or a transfer-assessment designation.
- The v2 tutor reads the governed learner model; deterministic NBA selects bounded next actions; InterventionRun preserves diagnosis/state references and bounded intervention execution.
- The model updater documents a concurrency seam: optimistic-lock conflict handling is not ported, so concurrent updates may lose a version bump. This is a separate hardening issue, not solved by this proposal.

The implementation evidence and detailed gap analysis are recorded in the linked v2 PoC. The PoC branch's full v2 CI passed in run [39108437035](https://github.com/SyllabAI/syllabai-v2/actions/runs/39108437035), including typecheck, full API/package tests, golden self-check, retrieval eval harness, zero-core census gate and Hub build. This is code/CI verification only, not evidence of educational outcome gains or production integration.

## Proposed semantics

A parallel evidence classification may use:

- `ATTEMPTED`: incorrect, ungraded, or support provenance unknown.
- `SUPPORTED_SUCCESS`: correct after a recorded hint, step-by-step support, teacher support, or answer/solution exposure.
- `INDEPENDENT_SUCCESS`: correct with explicit, trusted `assistance=NONE` and no prior answer exposure.
- `TRANSFER_SUCCESS`: independent correct on an explicitly designated transfer assessment, using a distinct canonical question linked to at least one same SpecificationPoint as prior evidence, after an explicitly configured delay.

The delay is an experiment parameter requiring versioning and evaluation; this proposal does not declare a scientifically correct threshold. These labels are evidence descriptions, not mastery scores or causal claims.

## Invariants

1. **No replacement of BKT/BDT.** The ladder is a parallel evidence view, not a new mastery model.
2. **No direct mastery mutation.** Classification alone never updates mastery, the authoritative KG, or SpecificationPoint semantics.
3. **Trusted provenance only.** Assistance, answer exposure, transfer designation, question identity and SpecificationPoint mapping must come from application-controlled validated data, never free-form LLM assertions.
4. **Fail closed.** Unknown assistance, missing SpecificationPoint anchors, ungraded evidence, duplicate/same-question attempts, invalid chronology, or insufficient delay cannot yield transfer success.
5. **Immutable attempt evidence.** Corrections and interpretations remain linked records; raw attempt history is not silently rewritten.
6. **Governed update boundary.** Any future learner-state transition stays inside the v2 application/learner-model layer, with provenance and audit.
7. **No Git-native learner store.** GitLearnOS contributes design patterns only; SyllabAI's canonical learner record remains in its governed application/database model.

## What is strong / weak / could fail

**Strong:** SyllabAI already has canonical question/part identity, SpecificationPoint anchors, BKT/BDT, deterministic next-best-action selection, and InterventionRun snapshots. The proposal can be tested as a narrow additive layer.

**Weak:** current assessment evidence does not yet capture all the trusted assistance/exposure facts needed for reliable classification. A pure classifier with fabricated or inferred inputs would create false confidence.

**Failure modes:** hint usage is not recorded; answer reveal and attempt chronology are ambiguous; transfer questions have bad/missing SpecificationPoint mapping; repeated variants are incorrectly treated as novel; model state is updated from labels outside governed application logic.

**Must remain unchanged:** curriculum truth, SpecificationPoints, immutable attempts, the learner-state overlay, BKT/BDT calibration, validated-content serving gates, and bounded InterventionRun orchestration.

## Promotion gates

Do not promote beyond PROPOSED until all of these pass:

1. CI typecheck and full test suite pass on [v2 PR #190](https://github.com/SyllabAI/syllabai-v2/pull/190).
2. A schema/source audit confirms reliable app-authored support and answer-exposure provenance; if not, stop at the pure prototype.
3. Adversarial scenario and property tests cover unknown support, answer exposure, repeated question, delayed distinct transfer question, unrelated SpecificationPoints, contradictory evidence and concurrent attempts.
4. A frozen held-out evaluation reports false-positive rates for independent/transfer success and separately measures BKT calibration.
5. Any persistent representation is specified in the canonical data model/ADR before production wiring; no new schema should be added just to make the PoC appear complete.

## Decision

**No production adoption yet.** Review the PoC and evidence-provenance feasibility first. The next decision is whether a separate verification-evidence record belongs in the existing attempt/learner-model contract—not whether to replace BKT.
