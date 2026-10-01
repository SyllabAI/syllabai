# Subject Intelligence Build (SIB) v1

**Status:** PROPOSED  
**Scope:** Cross-subject research-generation protocol for SyllabAI  
**Primary research tool:** NotebookLM / Gemini Notebook-class workflow  
**Durable authority:** SyllabAI repository research artifacts; NotebookLM is an authoring/research instrument, not the runtime source of truth.

## 1. Purpose

SIB defines a repeatable process for turning a subject corpus into a structured research library that can be ingested by SyllabAI and selectively retrieved by the Subject Tutor.

The same protocol applies across subjects. The taxonomy is stable; applicability is subject-specific.

The intended pipeline is:

```
official/trusted subject corpus
  -> NotebookLM subject research
  -> research artifacts
  -> artifact QA
  -> SyllabAI staging
  -> provenance + metadata validation
  -> research corpus
  -> Subject Tutor retrieval
```

SIB does **not** replace canonical curriculum/KG truth. Research artifacts provide subject intelligence and evidence. SpecificationPoints, curriculum semantics, validated assessment identity, learner state and governed learner evidence remain authoritative SyllabAI concerns.

## 2. Subject notebook contract

Use one NotebookLM notebook per subject/qualification context.

A notebook may contain:
- current specification;
- current student/textbook sources;
- current official QP/MS corpus;
- examiner reports;
- validated supplementary resources;
- legacy specifications/books/QP/MS;
- other explicitly classified research sources.

Current and legacy sources must be clearly labelled. Legacy material is historical evidence, not current curriculum truth.

## 3. Research families

### 01 Curriculum Intelligence — CUR
CUR-01 Curriculum Overview  
CUR-02 Specification Interpretation  
CUR-03 Concept Taxonomy  
CUR-04 Concept Relationships  
CUR-05 Prerequisite Knowledge Map  
CUR-06 Cross-Topic Connections  
CUR-07 Terminology & Definitions  
CUR-08 Curriculum Boundaries

### 02 Explanation Intelligence — EXP
EXP-01 Core Concept Explanations  
EXP-02 Simple Explanations  
EXP-03 Deep Explanations  
EXP-04 Alternative Explanations  
EXP-05 Analogies & Mental Models  
EXP-06 Conceptual Distinctions  
EXP-07 Why It Works  
EXP-08 Common Why Questions

### 03 Misconception & Error Intelligence — MIS
MIS-01 Misconception Atlas  
MIS-02 Concept Confusion Atlas  
MIS-03 Common Student Errors  
MIS-04 Reasoning Errors  
MIS-05 Calculation Errors  
MIS-06 Terminology Errors  
MIS-07 Exam Answer Errors  
MIS-08 Misconception Diagnostics  
MIS-09 Misconception Interventions

### 04 Assessment Intelligence — ASM
ASM-01 Assessment Overview  
ASM-02 Question Taxonomy  
ASM-03 Question Archetypes  
ASM-04 Command Word Analysis  
ASM-05 Mark Allocation Patterns  
ASM-06 Question Difficulty Patterns  
ASM-07 Multi-Concept Question Patterns  
ASM-08 Context Patterns  
ASM-09 Question Progression Patterns  
ASM-10 Assessment Coverage Analysis

### 05 Mark Scheme Intelligence — MS
MS-01 Mark Scheme Structure  
MS-02 Mark Point Taxonomy  
MS-03 Required Answer Elements  
MS-04 Acceptable Alternatives  
MS-05 Common Mark-Loss Patterns  
MS-06 Partial Credit Patterns  
MS-07 Examiner/Marking Language  
MS-08 Answer Quality Patterns

### 06 Examiner Intelligence — EXM
EXM-01 Examiner Report Synthesis  
EXM-02 Recurring Examiner Warnings  
EXM-03 What Examiners Reward  
EXM-04 What Examiners Penalize  
EXM-05 Question-Specific Examiner Insights  
EXM-06 Exam Technique Insights

### 07 Learning & Pedagogy Intelligence — PED
PED-01 Learning Sequence Analysis  
PED-02 Prerequisite Learning Paths  
PED-03 Difficulty Progression  
PED-04 Explanation Strategies  
PED-05 Practice Strategies  
PED-06 Retrieval Practice Opportunities  
PED-07 Interleaving Opportunities  
PED-08 Scaffolding Strategies  
PED-09 Diagnostic Teaching Strategies

### 08 Practical / Procedural Intelligence — PRA
PRA-01 Core Procedures  
PRA-02 Method/Technique Patterns  
PRA-03 Practical/Experimental Intelligence  
PRA-04 Procedure Errors & Failure Modes  
PRA-05 Method Selection Guide

### 09 Problem-Solving Intelligence — PRO
PRO-01 Problem-Solving Frameworks  
PRO-02 Problem Type → Method Mapping  
PRO-03 Multi-Step Reasoning Patterns  
PRO-04 Decision Points  
PRO-05 Dead Ends & Failed Approaches  
PRO-06 Worked-Reasoning Patterns  
PRO-07 Transfer Patterns

### 10 Historical / Longitudinal Intelligence — HIS
HIS-01 Specification Evolution  
HIS-02 Legacy → Current Mapping  
HIS-03 Assessment Evolution  
HIS-04 Terminology Evolution  
HIS-05 Question Evolution  
HIS-06 Persistent Patterns  
HIS-07 Historical Relevance Analysis

### 11 Tutor Intelligence — TUT
TUT-01 Subject Tutor Knowledge Base  
TUT-02 Common Student Questions  
TUT-03 Follow-Up Question Patterns  
TUT-04 Socratic Question Patterns  
TUT-05 Hint Strategies  
TUT-06 Misconception Response Patterns  
TUT-07 Exam Feedback Patterns  
TUT-08 Concept Comparison Guides  
TUT-09 Deep-Dive Explanations  
TUT-10 Subject-Specific Tutor Guidance

### 12 Gap Intelligence — GAP
GAP-01 Curriculum Coverage Gaps  
GAP-02 KG Coverage Gaps  
GAP-03 Assessment Coverage Gaps  
GAP-04 Misconception Coverage Gaps  
GAP-05 Resource Quality Gaps  
GAP-06 Retrieval Risk Analysis  
GAP-07 Tutor Knowledge Gaps  
GAP-08 Subject Research Backlog

The taxonomy defines 95 possible artifacts. A subject manifest marks each artifact REQUIRED, OPTIONAL or NOT_APPLICABLE.

## 4. Generation order

Generate in dependency-aware passes:

1. Corpus orientation and source inventory.
2. CUR.
3. EXP.
4. MIS.
5. ASM + MS + EXM.
6. PED + PRA + PRO.
7. HIS.
8. TUT.
9. GAP.

Later artifacts may use earlier generated artifacts as research context, but source claims must remain traceable to the underlying source corpus.

## 5. Artifact status lifecycle

NotebookLM-generated output begins as:

GENERATED

Then SyllabAI processing may move it through:

GENERATED -> QA_PASSED -> STAGED -> PUBLISHED

or:

GENERATED -> QA_FAILED

SIB does not silently promote generated research into canonical educational truth.

## 6. Subject-specific applicability

The taxonomy is universal; applicability is not.

Examples:
- PRA-03 is normally REQUIRED for sciences and fieldwork/practical subjects, but may be NOT_APPLICABLE for some subjects.
- PRO artifacts are especially important for Mathematics, Physics, Chemistry, Computer Science and Economics.
- Literary analysis, source evaluation, causation, interpretation and argument structures should be represented through subject-specific extensions under the same family model rather than forcing inappropriate science-style artifacts.

## 7. Runtime boundary

The research library is an evidence source for Subject Tutor mode.

It must not:
- mutate the authoritative KG;
- mutate mastery;
- create learner evidence directly;
- redefine SpecificationPoints;
- override validated assessment identity;
- bypass provenance or evidence-sufficiency rules.

Research retrieval remains subordinate to SyllabAI curriculum resolution, learner context and evidence policy.

## 8. Required deliverables per subject build

Each completed SIB build produces:
- `manifest.yaml`
- generated research Markdown artifacts;
- artifact QA report;
- source manifest/provenance record;
- research-library inventory;
- optional structured extraction files where a family needs machine-readable data;
- SIB build report with counts and unresolved gaps.

## 9. Completion metrics

Report at minimum:
- artifacts defined;
- REQUIRED / OPTIONAL / NOT_APPLICABLE;
- GENERATED;
- QA_PASSED / QA_FAILED;
- STAGED;
- PUBLISHED;
- source coverage;
- unresolved research gaps;
- current-vs-legacy separation status.

These are coverage/process metrics, not educational quality scores.

## 10. Architectural position

**PROPOSED:** Adopt SIB v1 as the standard cross-subject research-generation protocol.

NotebookLM/Gemini Notebook is an offline research accelerator. The durable research corpus belongs to SyllabAI. SyllabAI owns ingestion, metadata, provenance, retrieval semantics, serving boundaries and learner integration.
