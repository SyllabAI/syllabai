# SyllabAI Teacher, Classroom & LMS Architecture

**Status:** Canonical long-term product architecture
**Date:** 2026-09-07
**Applies to:** Teacher experience, class-enrolled student experience, subject-scoped LMS workflows, teacher intelligence, and teacher-facing knowledge-graph visualization.
**Scope guard:** This document defines the long-term product architecture. It does not expand Cycle 1. Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010.

---

## 1. Product vision

SyllabAI has two role-specific learning environments built on the same academic substrate:

```text
                                SYLLABAI
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
              STUDENT                             TEACHER
                 │                                   │
        ┌────────┴────────┐                 ┌────────┴─────────┐
        │                 │                 │                  │
   Independent        Classroom        Subject Workspace   Classes/LMS
     student           student
```

The teacher product is **not** a copy of the student dashboard with more buttons. It is a role-specific operating surface for teaching, assessment, class management, communication, analytics, and intervention.

The student product asks primarily:

> What do I know, what do I need to learn, and what should I do next?

The teacher product asks primarily:

> What have I taught, what does my class understand, which students need attention, and what should I teach or assign next?

Both views use the same specification-grounded academic graph and evidence architecture.

---

## 2. Shared academic substrate

The teacher and student products must not create parallel representations of the curriculum.

```text
Board
  ↓
Qualification
  ↓
Subject
  ↓
Curriculum / Specification Version
  ↓
Unit / Section
  ↓
Topic / SubTopic
  ↓
SpecificationPoint
  ↓
Concept / Skill / Practical / Knowledge Relations
  ↓
Resources + Questions + Mark Points
  ↓
Assessment Evidence
```

The learner layer is separate:

```text
Student
  ↓
Subject Enrollment
  ↓
LearnerState Overlay
       ├── mastery
       ├── misconception state
       ├── confidence
       ├── procedural fluency
       ├── evidence/exposure
       └── review/decay
```

The teacher layer is an aggregation and instructional overlay:

```text
Teacher
  ↓
Teaching Assignment
  ↓
Class
  ↓
Student Enrollments
  ↓
Aggregated Learner Evidence
  ↓
Teaching Coverage / Taught-State Overlay
```

The official curriculum remains immutable/versioned. Teaching state and learner state are separate from it.

---

## 3. Teacher subject-first experience

Teachers also work through explicit subjects rather than one mixed-subject resource area.

Example:

```text
Teacher Dashboard
│
├── Edexcel IGCSE Chemistry
│   ├── 4CH1
│   ├── Classes: 10A, 10B, 11A
│   └── Subject workspace
│
└── Cambridge IGCSE Biology
    ├── 0610
    ├── Classes: 10C, 11B
    └── Subject workspace
```

Clicking a subject opens a subject-scoped workspace. Every resource query, question query, class query, assessment action, and analytics read must retain explicit subject/curriculum identity.

### Teacher subject workspace

Long-term information architecture:

```text
SUBJECT
├── Overview
│
├── RESOURCES
│   ├── Revision Notes
│   ├── Exam Questions
│   ├── Past Papers
│   └── Flashcards
│
├── ASSESSMENT
│   ├── Test Builder
│   ├── Mock Exams
│   └── Assignments
│
├── TEACHING
│   ├── Classes
│   ├── Announcements
│   └── Teaching Coverage
│
├── ANALYTICS
│   ├── Class Performance
│   ├── Knowledge Graph
│   ├── At-Risk Students
│   └── Reports
│
└── AI
    ├── AI Assistant
    └── Data Assistant
```

Smart Lesson remains primarily a **student-facing adaptive learning feature**. Teachers can inspect or use its underlying learning-path logic indirectly through the data/teaching surfaces, but the teacher navigation does not need a teacher Smart Lesson product unless a future explicit decision adds one.

---

## 4. Student experience modes

There are two student modes, but they share one identity and learner model.

### 4.1 Independent student

A student may begin with zero subjects and add subjects explicitly.

```text
Student
└── My Subjects
    ├── Chemistry
    ├── Biology
    └── Mathematics
```

The subject workspace contains student learning tools:

```text
Dashboard
Revision Notes
Exam Questions
Past Papers
Flashcards
Target Test
Mock Exams
Smart Lesson
Tutor
Knowledge Graph
```

### 4.2 Classroom-enrolled student

A teacher may add/enroll a student into a class. The student still has the same core subject workspace, but additional classroom capabilities become available.

```text
Subject
├── Learn
│   ├── Revision Notes
│   ├── Exam Questions
│   ├── Flashcards
│   ├── Smart Lesson
│   ├── Target Test
│   ├── Mock Exams
│   └── Tutor
│
├── Explore
│   └── Knowledge Graph
│
└── CLASSROOM
    ├── Announcements
    ├── Assignments
    └── My Results / Feedback
```

The classroom interface should not fork the academic model. Assignments and teacher-created assessments should feed into the same assessment/evidence pipeline whenever their configuration makes them evidence-bearing.

A student can conceptually be both independent and classroom-enrolled. The classroom relationship grants additional capabilities; it does not create a second student account or a second learner model.

---

## 5. Teacher resource surfaces

Teachers should have subject-scoped access to the same core academic resource families that students use, subject to role and content permissions:

- Revision Notes
- Exam Questions
- Past Papers
- official Mark Schemes where licensed/available
- Flashcards
- Mock Exams
- question-bank search and filtering

Teacher resources are not simply copied student pages. The teacher surface adds actions such as:

- preview
- assign
- reuse
- add to custom test
- attach to an announcement
- inspect specification coverage
- inspect class performance for the mapped knowledge area

---

## 6. Test Builder

Test Builder is a first-class teacher assessment tool inspired by the workflow of Save My Exams, but implemented using SyllabAI's own question bank, provenance model, specification-point graph, learner evidence, and validation rules.

Current external reference finding (2026-09-07): Save My Exams describes Test Builder as a teacher-only workflow for creating custom exam-board-aligned tests, filtering by topic and difficulty, adding teacher-only questions, reusing/editing tests, and producing print-ready PDFs. Its teacher guidance also describes use for quizzes, homework, focused revision tests, and mock-style practice. These capabilities are product references, not dependencies or content sources for SyllabAI.

Sources:
- https://www.savemyexams.com/study-tools/test-builder/
- https://www.savemyexams.com/teachers/
- https://www.savemyexams.com/learning-hub/sme-articles/how-to-use-test-builder/

### 6.1 Test Builder flow

```text
Choose Subject / Specification
        ↓
Choose Content
        ↓
Filter / Target
        ↓
Select Questions
        ↓
Arrange / Edit Test
        ↓
Preview
        ↓
Export / Assign / Save
```

### 6.2 Filters

The long-term builder should support filters such as:

```text
Curriculum identity
Unit / Section
Topic / SubTopic
SpecificationPoint
Concept / skill
Question type
Command word
Difficulty
Marks
Year / exam session
Paper / variant
Calculator requirement
Practical / experimental skill
Assessment objective
Past-paper / authored
Validation status
```

Later, evidence-driven filters may include:

```text
Class weak area
Student weak area
Misconception
Mastery band
Timed-vs-untimed gap
Recently taught / not taught
```

### 6.3 Class-targeted Test Builder

A major SyllabAI extension is:

> Build a test around what my class actually needs.

For example:

```text
Class: Chemistry 10A
Target: weakest measured specification points
Length: 40 marks
Time: 45 minutes
Constraint: only validated exam-style questions
```

The system may use class-level evidence to propose a candidate set, but it must show the teacher why questions were selected and must never silently turn a probabilistic recommendation into an authoritative assessment rule.

### 6.4 Export

Teacher export should support, as applicable:

- student question-paper PDF
- mark-scheme PDF
- combined teacher pack
- saved test/template
- assignment-ready test

Generated PDFs must retain question/mark provenance and avoid inventing content. Any AI-generated question must be visibly distinguishable from official past-paper content and follow the project's content-validation policy.

---

## 7. Assignments

Assignments are an LMS object connecting teacher intent, selected content/assessment, student submissions, feedback, and optionally learner evidence.

### 7.1 Assignment creation

```text
Create Assignment
│
├── Title
├── Instructions
├── Subject / Curriculum Version
├── Class(es) / selected students
├── Content
│   ├── Exam Questions
│   ├── Revision Notes
│   ├── Flashcards
│   ├── Past-paper questions
│   ├── Custom Test
│   └── approved external/resource link
├── Availability
│   ├── Start
│   ├── Due date
│   └── Late policy
├── Attempt settings
├── Timing
└── Assessment / marking settings
```

### 7.2 Submission portal

```text
Assignment
   ↓
Submissions
   ↓
Smart Mark where enabled
   ↓
Teacher review / override
   ↓
Feedback + result
   ↓
Evidence event where configured
   ↓
Learner state update
```

The product must explicitly distinguish:

- completion tracking
- formative evidence
- authoritative/validated assessment evidence

An assignment should not automatically change mastery merely because a student opened or completed a resource. Assessment-bearing submissions need an explicit evidence policy.

---

## 8. Class Management

Classes are the teacher-side organizational boundary for cohorts.

```text
Teacher
  ↓
Teaching Assignment
  ↓
Subject / Specification Version
  ↓
Class
  ├── Student Enrollments
  ├── Assignments
  ├── Assessments
  ├── Announcements
  ├── Teaching Coverage
  └── Aggregated Learner State
```

Long-term class management capabilities:

- create/edit/archive class
- invite/add students
- remove students
- move students between classes where authorized
- class code/invitation flow
- roster view
- bulk import where appropriate
- export class reports
- view class membership history
- inspect per-student subject status

A teacher must only be able to access classes and students covered by their authorization scope.

Cycle 1 currently has no persistent Class entity; T-029's implemented minimal teacher surface uses the enabled STUDENT cohort as an honest pilot roster. A future class-management implementation must replace that pilot shortcut with explicit class membership rather than stretching the cohort query indefinitely.

---

## 9. Announcements

Announcements provide teacher-to-class communication.

Long-term capabilities:

- publish to one class
- publish to multiple classes
- publish to selected students
- schedule publication
- edit/delete subject to audit policy
- attach approved resources or assignment links
- categorize as homework, notice, exam reminder, resource, or general
- student read state

Announcements are not intended to be another AI tutoring channel.

---

## 10. Teacher AI Assistant

Teacher AI Assistant is a general academic/teaching copilot grounded in the selected subject and its source material.

Example questions:

```text
What does specification point 3.4 require?

Create five questions on electrolysis at this difficulty.

Explain this concept at IGCSE level.

Which specification points cover this revision note?

Suggest a lesson starter for rates of reaction.
```

Primary grounding sources:

```text
Official specification
Validated curriculum graph
Validated Revision Notes
Validated question bank
Validated mark schemes
Approved teaching resources
```

The assistant should expose provenance/citations where a claim depends on a source. It must not silently fabricate board requirements or present generated material as official content.

The AI Assistant may create **draft** questions/resources, but generated content follows the project's existing validation wall before it can become learner-servable authoritative content.

---

## 11. Teacher Data Assistant

Data Assistant is deliberately separate from Teacher AI Assistant.

### Teacher AI Assistant asks:

> What can you help me teach/create/explain?

### Data Assistant asks:

> What does the evidence say about my class/students?

Examples:

```text
Which topics is Class 10A struggling with?

Which specification points have the largest number of struggling students?

Why is electrolysis showing as weak?

Who is currently at risk?

What did Sara score in the latest mock?

Which students have a persistent high-confidence misconception?

Which students have a large timed-vs-untimed gap?
```

The Data Assistant should query structured, authorized data first. The LLM layer should translate natural language into supported analytics queries or summarize returned evidence; it must not invent statistics.

Every answer should be traceable to the underlying evidence, with the relevant subject/class/student scope and time window made visible.

---

## 12. At-Risk Students

At-Risk Students is a teacher-facing early-warning surface.

The feature must be evidence-first. It must never present a student as "at risk" solely because an LLM believes so.

Potential signals include:

```text
Recent mastery decline
Persistent low mastery
Repeated misconception evidence
Missed assignments
Missing assessments
Low recent activity relative to expected class activity
Rapid forgetting / review backlog
Large timed-vs-untimed performance gap
Repeated high-confidence incorrect responses
Declining assessment trajectory
```

A risk screen should show both a status and the evidence behind it:

```text
Nabil — High attention

Evidence
• mastery declined 14% over 4 weeks
• 2 assignments missing
• repeated electrolysis misconception in 5 recent attempts
• last assessment below class baseline

Recommended teacher review
• inspect electrolysis node
• open recent attempts
• consider targeted assignment
```

Risk thresholds and combinations must be configurable/versioned when they become research-sensitive. The system must preserve the distinction between observed evidence, rule-based inference, and research hypothesis.

---

## 13. Teacher knowledge graph

The teacher graph is a **different lens over the same subject graph**.

Student graph asks:

> What do I know?

Teacher graph asks:

> What have I taught, what does my class understand, and where is intervention needed?

### 13.1 Core visual states

Every subject-graph node may have two major dimensions:

1. **Teaching coverage**
2. **Class understanding**

Suggested teaching coverage:

```text
GREY = not taught / no teaching coverage recorded
```

Suggested class-understanding bands for taught nodes:

```text
Strong understanding
Good / secure
Developing
Weak
Critical weakness
```

The exact visual palette is a UI decision; the semantic states are architectural.

### 13.2 Example

```text
                        Chemistry
                            │
             ┌──────────────┴──────────────┐
             │                             │
      Atomic Structure 🟢             Bonding
                                        │
                                ┌───────┴────────┐
                                ▼                ▼
                         Ionic Bonding 🟡   Covalent ⚪
                                │
                                ▼
                         Electrolysis 🔴
```

Here:

- ⚪ means **not taught**, not "students are weak".
- 🔴 means taught, but current class evidence shows critical weakness.
- 🟢 means taught and strong class understanding.

### 13.3 Aggregation

Class mastery must not be represented by a single average alone.

A node may expose:

```text
Mean mastery
Proficient percentage
Developing percentage
Struggling percentage
Student count with evidence
Misconception prevalence
Confidence calibration indicators
```

This prevents a polarized class from being hidden by a misleading average.

### 13.4 Teaching coverage state

Teaching coverage is a separate teacher-side overlay:

```text
Curriculum Graph
      +
Teaching Coverage
      +
Class Learner Aggregation
```

The graph can therefore distinguish:

| | High understanding | Low understanding |
|---|---|---|
| **Taught** | secure teaching outcome | intervention opportunity |
| **Not taught** | prior knowledge / unexpected evidence | not-yet-taught |

This is an important difference from a student graph.

### 13.5 Node interaction

Clicking a node should open a teacher detail panel containing, as available:

```text
Specification point / concept
Teaching status
Class understanding distribution
Recent class evidence
Common misconceptions
Student list
Associated resources
Associated questions
Past-paper coverage
Suggested teacher actions
```

The teacher must be able to drill from:

```text
Class graph
   ↓
Weak node
   ↓
Affected students
   ↓
Individual student graph
   ↓
Evidence / attempts
   ↓
Intervention / assignment / test
```

---

## 14. Individual student graph from teacher view

Teachers should be able to open an individual student's subject graph without creating a second graph implementation.

```text
Teacher Class Graph
       │
       ├── Student A
       ├── Student B
       ├── Student C
       └── ...
             │
             ▼
      Individual Student Graph
```

The individual graph uses the same learner-state semantics as the student's own graph, but the teacher sees additional authorized context:

- class position/comparison where policy permits
- assignment history
- assessment history
- teacher notes/overrides where introduced
- evidence behind risk flags

Privacy controls must prevent a teacher from seeing students outside their authorization scope.

---

## 15. Teacher analytics model

Long-term teacher analytics should aggregate evidence upward through the same graph hierarchy:

```text
SpecificationPoint evidence
        ↓
SubTopic aggregation
        ↓
Topic aggregation
        ↓
Unit aggregation
        ↓
Subject summary
        ↓
Class summary
```

Where data volume permits, the UI should also expose distributions rather than only means.

Analytics answers should preserve:

- subject/curriculum version
- class scope
- student scope
- time window
- evidence count
- data freshness / as-of timestamp
- calculation definition/version

This makes Data Assistant answers auditable.

---

## 16. Teacher action loop

The teacher equivalent of the student adaptive loop is:

```text
Class evidence
      ↓
Class / student knowledge graph
      ↓
Weak topic / specification point / misconception
      ↓
Teacher inspection
      ↓
Choose action
      ├── Revision Note
      ├── Exam Questions
      ├── Test Builder
      ├── Assignment
      ├── Mock Exam
      ├── Announcement
      └── one-to-one intervention
      ↓
Student activity / assessment
      ↓
New evidence
      ↓
Updated learner aggregation
      ↓
Teacher graph updates
```

This closes the loop between analytics and instruction.

---

## 17. Authorization and privacy

Teacher intelligence is strictly authorization-scoped.

The UI may hide unavailable data, but backend authorization is mandatory.

At minimum:

```text
Teacher
  → classes they teach
  → students enrolled in those classes
  → subjects/specifications they teach
```

Data Assistant, At-Risk Students, class graphs, student graphs, assignments, reports, and assessment details must enforce this scope at the backend/API boundary.

Teacher access must not imply access to another teacher's class merely because the same student or subject exists.

---

## 18. Evidence and AI integrity

Teacher-facing AI must follow the same core project philosophy:

> AI proposes or summarizes; structured evidence and validation determine truth.

Therefore:

- Official specification claims require authoritative provenance.
- Past-paper claims require source provenance.
- Generated questions remain drafts until validated according to content policy.
- Data Assistant statistics are computed from structured data, not hallucinated by an LLM.
- At-Risk flags show evidence and rule/version information.
- Teacher overrides are recorded and auditable.
- AI model/provider/prompt metadata are retained where AI output materially affects a decision.

---

## 19. Long-term domain model direction

The conceptual domain should eventually support:

```text
Teacher
 ├── TeachingAssignment
 │      ├── Subject / CurriculumVersion
 │      └── Class
 │
 └── TeacherPermissions / Scope

Class
 ├── StudentEnrollment[]
 ├── Assignment[]
 ├── Assessment[]
 ├── Announcement[]
 └── TeachingCoverage[]

TeachingCoverage
 ├── specification_point_id / graph_node_id
 ├── status (NOT_TAUGHT / TAUGHT / REVIEWED etc.)
 ├── recorded_at
 ├── teacher_id
 └── provenance / audit metadata
```

The exact entity model, relationships, and migrations must be designed through the existing modular-monolith contracts and project tracker; this document does not authorize premature schema implementation.

---

## 20. Relationship to existing T-029

T-029 is the **minimal teacher surface** already implemented and merged in Cycle-1-era product work:

- teacher roster endpoint
- Smart Mark review queue
- learner names in teacher read models
- Run Smart Mark
- human-mark overrides
- κ-gate view
- backend RBAC enforcement

T-029 should be treated as a foundation, not as the complete teacher product.

The future architecture in this document extends the teacher module without redefining T-029's historical acceptance criteria.

---

## 21. Relationship to subject architecture

`SUBJECT_ARCHITECTURE.md` remains canonical for the subject-first product boundary and specification-point curriculum model.

This document extends that model to:

- teacher subject workspaces
- class-enrolled student mode
- LMS workflows
- Test Builder
- Assignments
- Announcements
- Teacher AI Assistant
- Data Assistant
- At-Risk Students
- teaching coverage
- class knowledge graph
- teacher drill-down into individual student graphs

When the documents need to be interpreted together:

```text
SUBJECT_ARCHITECTURE.md
    = subject/curriculum/specification-point foundation

TEACHER_ARCHITECTURE.md
    = teacher/classroom/LMS product layer on that foundation
```

---

## 22. Scope and sequencing

This architecture is intentionally long-term.

Do not pull all features into Cycle 1.

Suggested future grouping:

```text
Foundation
├── explicit Class entity
├── subject-scoped teacher workspaces
├── classroom student capability layer
└── teaching coverage model

Assessment / LMS
├── Test Builder
├── Assignments
├── submission portal
├── Mock Exam management
└── Announcements

Teacher Intelligence
├── class KG / heatmap
├── individual student graphs
├── At-Risk Students
├── reports
└── Data Assistant

Teacher Copilot
└── grounded Teacher AI Assistant
```

Each feature must receive a tracker row, explicit dependencies, acceptance criteria, authorization requirements, and—when it changes research constructs—a research review.

---

## 23. Non-negotiable agent rules

- Read this document for teacher, classroom, LMS, teacher-analytics, or teacher-KG work.
- Treat teacher and student as different product lenses over shared academic data, not two unrelated curricula.
- Preserve Board → Qualification → Subject → CurriculumVersion isolation.
- Preserve SpecificationPoint as the fine-grained academic anchor.
- Never mutate official curriculum nodes with teacher teaching state or learner state.
- Treat NOT_TAUGHT as semantically different from LOW_MASTERY.
- Never label a student at risk without evidence and an inspectable reason.
- Data Assistant answers must be grounded in authorized structured data.
- Teacher AI Assistant must be grounded in authoritative/validated academic sources.
- Do not present AI-generated questions as official exam questions.
- Keep class aggregation distinct from individual learner state.
- Preserve distribution information; do not assume a class average fully represents the class.
- Enforce teacher authorization in the backend, not only in the frontend.
- Do not treat T-029's pilot roster shortcut as the final Class domain model.
- Do not expand Cycle 1 merely because these long-term capabilities are documented.
