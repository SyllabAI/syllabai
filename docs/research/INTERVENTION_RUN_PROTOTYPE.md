# SyllabAI — InterventionRun Prototype

**Status:** ACCEPTED (2026-09-17 — §14 decision gate closed: acceptance criteria 1–10 demonstrated
(`syllabai-core/docs/INTERVENTION_RUN_ACCEPTANCE.md`, live 10/10 on production at `02643ed`),
persistence/query cost understood (`syllabai-core/docs/INTERVENTION_RUN_PERSISTENCE_QUERY_COST.md`),
`InterventionRunFlowIT` 2/2 GREEN in real Docker core-ci run `35139255878` at `7eb621a`, Render live
deploy verified on the same commit; operator's conditional promotion directive given and executed)
**Date:** 2026-09-15
**Research origin:** `docs/research/OPENHUMAN_GRAPH_ARCHAEOLOGY.md` — E2
**Scope:** backend orchestration contract only; no graph UI changes

## 1. Purpose

Introduce a bounded, auditable execution record for one adaptive learning intervention without allowing an agent, Tutor response, or recommendation UI to mutate learner state directly.

The prototype exists to test whether SyllabAI can make the learning loop reconstructable:

```text
learner evidence
      ↓
diagnosis snapshot
      ↓
next-best learning action
      ↓
InterventionRun
      ↓
practice / tutor / assessment steps
      ↓
new learning evidence
      ↓
reassessment
      ↓
governed learner-state update
```

This is an orchestration boundary, not a new learner model and not a second curriculum graph.

## 2. Architectural position

The run sits between recommendation/diagnosis and governed learner-state mutation:

```text
Authoritative curriculum KG
            │
Learner evidence + learner state
            │
            ▼
     Diagnosis / NBA
            │
            ▼
   ┌───────────────────┐
   │   InterventionRun  │
   │                   │
   │ target SPs         │
   │ evidence snapshot  │
   │ diagnosis snapshot │
   │ intervention hash  │
   │ allowed tools      │
   │ step observations  │
   │ terminal outcome   │
   └─────────┬─────────┘
             │
             ▼
      governed update
             │
             ▼
       learner state
```

The run may *request* a learner-state transition, but the application/learner-model layer remains the only authority allowed to perform it.

## 3. Non-goals

The first prototype must not:

- replace the existing recommendation engine;
- create a second learner model;
- make the run the source of curriculum truth;
- allow arbitrary LLM-generated workflow steps;
- add autonomous background intervention;
- add graph visualization;
- use Git as runtime learner storage;
- encode mastery arithmetic inside intervention code.

## 4. Proposed run contract

A run has a stable immutable identity and a mutable execution status.

### 4.1 Identity / snapshot fields

```text
runId
learnerId
subjectId
curriculumVersionId
createdAt
createdBy / origin

Target:
  specificationPointIds[]
  questionPartIds[] (optional)

Evidence snapshot:
  evidenceRefs[]
  learnerStateVersion / snapshot reference
  capturedAt

Diagnosis snapshot:
  diagnosisCode(s)
  diagnosisVersion
  reason/evidence references

Intervention:
  actionType
  interventionVersion
  interventionHash
  allowedToolIds[]
```

The exact physical schema is implementation work. The semantic requirement is that a resumed/replayed run can identify the exact evidence, learner-state view, curriculum version, and intervention definition it was based on.

### 4.2 Execution fields

```text
status
startedAt
completedAt
cancelledAt
terminalOutcome
currentStep

step observations:
  stepId
  sequence
  startedAt
  completedAt
  input/evidence references
  output/evidence references
  observation type
  failure/blocked reason
```

Raw learner conversation should not be copied into the run. Store references to audit/history or evidence records instead.

## 5. Status machine

Initial prototype states:

```text
CREATED
  ↓
ACTIVE
  ├── PAUSED
  │     ↓
  │   ACTIVE
  ├── COMPLETED
  ├── CANCELLED
  └── FAILED
```

Terminal states are immutable. A retry/restart creates a new run or a governed continuation record; it does not rewrite the terminal history.

## 6. Version / resume invariant

A run must not resume against a materially different intervention definition.

At minimum, persist:

```text
interventionVersion
interventionHash
curriculumVersionId
```

Before resume, the application must verify that the current intervention definition matches the recorded hash/version. If not, fail closed and require a new run or explicit migration policy.

This is the SyllabAI adaptation of the strongest OpenHuman workflow finding: approval/resume must refer to the same executable definition that was originally presented.

## 7. Evidence snapshot invariant

The run records references to the evidence that justified the intervention at creation time.

It must not silently recompute its original diagnosis from today's learner state during replay.

```text
Run created on D0
  evidence snapshot = E0
  learner-state snapshot = S0

Learner state changes on D1

Replay/audit of D0 run
  → uses E0/S0 references
  → does not reinterpret the run as if created on D1
```

Current learner state can still be read for serving, but that is a new decision context, not a mutation of historical run meaning.

## 8. Allowed tools / bounded execution

A run may only invoke application-controlled tools explicitly listed in its contract.

Examples:

```text
get_current_resource
get_specification_context
get_related_concepts
search_curriculum
find_revision_note
find_exam_questions
get_learner_state
get_relevant_learning_evidence
start_practice
```

Tool authorization belongs to SyllabAI application logic. Providers/LLMs do not define or expand the tool boundary.

## 9. Learner-state mutation boundary

The most important invariant is:

```text
InterventionRun observation
        ≠
LearnerState mutation
```

A completed practice step can produce learning evidence. The governed learner-model service then decides whether and how learner state changes.

Forbidden examples:

```text
practice_completed → mastery += 0.1
correct_answer → mastery += fixed constant
resolved_flag → mastery += fixed constant
```

Those transitions must remain inside the accepted learner-model/evidence architecture.

## 10. Minimal persistence model

Conceptual entities:

```text
intervention_run
intervention_run_step
intervention_run_evidence
```

Potential shape:

```sql
intervention_run (
  run_id,
  learner_id,
  subject_id,
  curriculum_version_id,
  status,
  origin,
  target_specification_points,
  diagnosis_version,
  diagnosis_snapshot_ref,
  learner_state_snapshot_ref,
  intervention_version,
  intervention_hash,
  allowed_tool_ids,
  created_at,
  started_at,
  completed_at,
  terminal_outcome
)

intervention_run_step (
  run_id,
  sequence_no,
  step_id,
  status,
  started_at,
  completed_at,
  observation_type,
  input_evidence_ref,
  output_evidence_ref,
  blocked_reason
)

intervention_run_evidence (
  run_id,
  evidence_ref,
  role,
  captured_at
)
```

Array/JSON fields are acceptable for the first experiment only where they do not destroy queryability or provenance. If the run becomes production infrastructure, normalize the evidence/target relationships as required by actual query patterns.

## 11. First end-to-end scenario

Use one deterministic, low-risk intervention:

```text
Measured weak SpecificationPoint
        ↓
NBA selects PRACTICE
        ↓
Create InterventionRun
        ↓
Capture target SP + evidence refs + learner-state snapshot
        ↓
Expose practice action
        ↓
Learner submits an existing validated QuestionPart
        ↓
Attempt evidence is recorded by the existing evidence subsystem
        ↓
Run records the evidence reference
        ↓
Run completes with outcome = EVIDENCE_COLLECTED
        ↓
Governed learner model consumes the attempt evidence
```

The prototype should use an existing validated question rather than generated content. This isolates orchestration correctness from question-generation correctness.

## 12. Acceptance criteria for E2

E2 is **VERIFIED** only when evidence demonstrates all of the following:

1. A run can be created from a recommendation/diagnosis snapshot.
2. The run stores immutable target/evidence/intervention identity.
3. A run can record ordered step observations.
4. A run cannot resume after its intervention hash/version has materially changed.
5. Attempt evidence can be attached to the run without duplicating the canonical attempt record.
6. Completion of a run does not directly mutate mastery.
7. The governed learner-model path remains the only state-mutation authority.
8. A completed run can be reconstructed from persisted records and evidence references.
9. Terminal run history is append-only at the domain level.
10. The implementation has tests for resume/version mismatch and mutation-boundary behavior.

## 13. Research questions

E2 should answer:

- Does a run boundary materially improve audit reconstruction?
- Is the evidence snapshot sufficient to reproduce the recommendation/diagnosis context?
- Which fields must be immutable versus versioned?
- Is intervention hashing stable enough across deployments?
- What is the minimum step model needed for tutor/practice/assessment without creating a workflow engine prematurely?
- Does the run create useful research telemetry without duplicating existing evidence logs?

## 14. Decision gate

Do not promote `InterventionRun` from PROPOSED to ACCEPTED production architecture until the prototype satisfies the acceptance criteria and the resulting persistence/query cost is understood.

If the prototype becomes unnecessary overhead for simple one-step interventions, retain the contract as a lightweight audit record rather than building a general workflow engine.

## 15. Relationship to existing architecture

This proposal builds on, and does not replace:

- `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` — canonical question-level evidence;
- `RECOMMENDATION_SYSTEM_ARCHITECTURE.md` — next-best-action orchestration;
- learner-model implementation contracts in `syllabai-core`;
- authoritative curriculum/KG contracts.

The core principle is:

```text
Evidence is the signal.
Recommendation selects an action.
InterventionRun records the bounded execution.
Learner-model logic governs state change.
```
