# SyllabAI Project Context — Sanity-Checked

The current project-control-plane documents are synchronized around the 2026-09-07 architecture decisions.

Canonical architecture decisions:
- ADR-014 — subject-first product and first-class `SpecificationPoint` architecture.
- ADR-015 — teacher/classroom/LMS layer over the shared subject graph/evidence substrate.
- ADR-016 — Question Attempt & Learning Evidence / Learning Log as a foundational evidence subsystem.
- ADR-017 — learning-first Next Best Learning Action recommendation architecture.
- ADR-018 — blueprint-driven Mock Exam Generator architecture.

Current Master Spec: v1.2.0. It is the engineering source of truth; the research papers remain authoritative for scientific claims and research methodology.

Mock Exam feature identity remains **F-051**. Supporting rows are **F-171 through F-176** in `backlog/mock-exam-generator-feature-addendum.tsv`:

```text
F-171  Exam Blueprint Registry & Versioning
F-172  Assessment Block / Shared Context Modeling
F-173  Mock Blueprint Fidelity Validation
F-174  Personalized Mock Allocation
F-175  Validated AI Question Variant Pipeline
F-176  Mock Prediction & Readiness Evaluation
```

The durable architecture discussion index and the mock feature addendum use the same IDs. The older F-169…F-174 numbering was a temporary synchronization mistake and is not authoritative.

The current Cycle-1 scope remains unchanged: Edexcel IAL Chemistry, ~50 retake-path students, 8 weeks, Tutor + Assessor agents only, predictions P1–P8. Mock blueprint work remains outside the pilot unless an explicit future scope decision promotes it.

Agents working on mocks must treat `MOCK_EXAM_GENERATOR_ARCHITECTURE.md`, `MOCK_EXAM_GENERATOR_AGENT_ADDENDUM.md`, `DECISION_018_MOCK_EXAM_GENERATOR.md`, and the Question Attempt/Learning Evidence documents as the relevant canonical context.

Known remaining controlled-documentation task: the Master Spec's section 43 document index still needs a small update to list ADR-018 and the mock architecture documents. This is indexing staleness, not an architecture contradiction. The binary master workbook likewise requires the next controlled workbook sync to fold F-171…F-176 into the canonical XLSX/TSV pair; do not treat older local mock workbook snapshots as authoritative.
