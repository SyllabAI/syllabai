# SyllabAI Subject-First Product & Specification-Point Architecture

**Status:** Canonical product/engineering decision
**Date:** 2026-09-07
**Applies to:** All boards, qualifications, and subjects; current Cycle-1 execution remains Edexcel IAL Chemistry unless the scope is explicitly changed.

## 1. Decision

SyllabAI is **subject-first** from the student's point of view.

A new student may have **zero subjects** in the dashboard. The student explicitly adds a course using:

```text
Board → Qualification → Subject → Curriculum / Specification Version
```

Example:

```text
Edexcel → International GCSE → Chemistry → 4CH1 / applicable specification version
```

After enrollment, that subject becomes a self-contained student workspace containing the subject's academic resources, assessment tools, learner state, tutor context, and knowledge graph.

The global account remains separate from academic state. Shared curriculum/content is not copied per student; the student's enrollment and learner-state overlay are the personalized layer.

## 2. Subject workspace

A subject workspace is expected to expose:

- Overview / subject dashboard
- Revision Notes
- Exam Questions
- Past Papers
- Flashcards
- Target Test
- Mock Exams
- Smart Lesson
- Tutor
- Knowledge Graph

These are product-level capabilities. Save My Exams is a **UX/product reference only**, not a runtime dependency or source of SyllabAI content.

Current external reference checks (2026-09-07):
- Save My Exams exposes exam-board/course-specific IGCSE Chemistry resources and an "Add to my subjects" flow.
- Its IGCSE Chemistry course pages expose Revision Notes, Exam Questions, Flashcards, Smart Lesson, Target Test, Mock Exams, and Past Papers where supported by the selected course.
- Smart Lesson is described as an adaptive path using Exam Questions, Revision Notes, and Flashcards, with feedback and weaker-area follow-up.
- Target Test allows topic, question-type, difficulty, and test-length selection to create custom practice.
- Cambridge IGCSE Chemistry 0620 has a detailed syllabus structure with numbered sections/subsections and learning-objective statements; its 2026–2028 syllabus separates Core and Supplement outcomes.

Sources:
- https://www.savemyexams.com/igcse/chemistry/
- https://www.savemyexams.com/igcse/chemistry/cie/23/
- https://www.savemyexams.com/igcse/chemistry/cie/23/smart-lesson/
- https://www.savemyexams.com/igcse/chemistry/cie/23/target-tests/
- https://www.savemyexams.com/igcse/chemistry/flashcards/
- https://www.savemyexams.com/igcse/chemistry/past-papers/
- https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-chemistry-0620/
- https://www.cambridgeinternational.org/Images/697205-2026-2028-syllabus.pdf

## 3. Canonical curriculum hierarchy

Do not stop the curriculum model at Topic/SubTopic. Official specifications can be significantly more granular.

```text
Board
  └── Qualification
       └── Subject
            └── CurriculumVersion / SpecificationVersion
                 └── Unit / Section
                      └── Topic / SubTopic
                           └── SpecificationPoint
```

For boards that use a numbered objective scheme, a SpecificationPoint is the authoritative learning-objective anchor, for example `1.1`, `1.2`, `1.3`, etc. The exact hierarchy and numbering are **parsed from the selected official specification**, not invented by an agent.

A specification point is a first-class object/node, not merely a string tag attached to a note.

### Minimum SpecificationPoint data

- stable internal id
- curriculum_version_id
- official code (`1.2`, `C3.4`, etc.)
- verbatim official learning-objective statement
- display title where the source provides one
- official ordering/sequence
- parent hierarchy node(s)
- source document/version id
- source page/section/element provenance
- extraction/validation status
- applicability metadata when explicitly present in the specification (for example Core/Supplement, tier, paper, or unit)
- source-engine/parser version where relevant

Never silently paraphrase an official objective into the canonical field. A human-readable summary may be added separately, with provenance.

## 4. Why specification points are first-class

This is a good idea and should be part of the core architecture because specification points form the most precise shared anchor across the learning system.

They connect:

```text
Official specification
       ↓
Specification Point
       ↓
Revision Note
       ↓
Flashcard
       ↓
Exam Question / Question Part
       ↓
Mark Point / assessment evidence
       ↓
Learner state
       ↓
Target Test / Smart Lesson / Tutor
```

This directly matches the student's existing revision-note structure, which is organized around the official specification points.

It also prevents an important failure mode: forcing a question, note, or learner state to belong to a broad topic when the real evidence is about one or several finer-grained objectives.

## 5. Separate hierarchy from knowledge

The specification hierarchy is authoritative, but it is not the whole knowledge graph.

### Curriculum hierarchy

```text
Unit
  → Topic
    → SubTopic
      → SpecificationPoint
```

### Knowledge relationships

```text
SpecificationPoint / Concept A
      │
      ├── REQUIRES_PREREQUISITE ──→ Concept B
      ├── RELATED_TO ─────────────→ Concept C
      ├── EXPLAINS ───────────────→ Concept D
      └── CONTRASTS_WITH ─────────→ Concept E
```

This means two specification points may be siblings in the official specification while still having a prerequisite relationship, and a single specification point may depend on knowledge elsewhere in the course.

The official hierarchy is therefore preserved exactly while the graph can represent the actual conceptual structure.

## 6. Resources map to specification points

Revision Notes should be able to link directly to the specification point(s) they cover.

The same applies to:

- Flashcards
- Smart Lesson steps
- Examples/counterexamples
- Approved explanations
- Future interactive learning resources

A resource may cover more than one specification point. The mapping must preserve provenance and validation status.

Do not force one-to-one resource → topic relationships when the resource genuinely covers multiple objectives.

## 7. Future question tagging

Past-paper and other assessment items should eventually be taggable to specification points such as `1.2`, `1.3`, etc.

The canonical relationship should be:

```text
QuestionVersion / QuestionPart
        │
        ├── ASSESSES / MAPS_TO ──→ SpecificationPoint A
        ├── ASSESSES / MAPS_TO ──→ SpecificationPoint B
        └── ASSESSES / MAPS_TO ──→ SpecificationPoint C
```

A question may map to multiple specification points. This is important for multi-concept and multi-part chemistry questions.

The first implementations do **not** need to tag the whole corpus. Empty/unmapped relationships are valid. When tagging is introduced, prefer teacher/SME validation or an explicit review workflow; do not silently convert an LLM suggestion into truth.

This extends the existing multi-topic question direction (F-152) rather than replacing it.

## 8. Learner state attaches to the graph; it does not mutate the curriculum

The subject graph is versioned and comparatively stable.

The student's state is a time-aware overlay:

```text
Student
  ↓
Subject Enrollment
  ↓
Curriculum Graph
  ↓
Learner Overlay
       ├── mastery
       ├── misconception probability/state
       ├── confidence
       ├── procedural fluency
       ├── exposure / attempt evidence
       └── review / decay state
```

The most precise evidence may live at SpecificationPoint level when available. Higher-level Topic/SubTopic/Unit displays can aggregate those states.

Do not write "mastery = 70%" back into the curriculum node itself. Store learner state separately and compose the personalized graph at read time.

## 9. Example: Edexcel IGCSE Chemistry

A simplified subject graph might look like:

```text
Edexcel IGCSE Chemistry
│
├── Unit / Section
│    ├── Topic
│    │    ├── SubTopic
│    │    │    ├── 1.1  [official objective]
│    │    │    ├── 1.2  [official objective]
│    │    │    └── 1.3  [official objective]
│    │    │
│    │    └── ...
│    └── ...
│
├── Cross-topic knowledge edges
│    ├── prerequisite
│    ├── related
│    ├── explains
│    └── ...
│
├── Assessment links
│    ├── past paper
│    ├── question
│    ├── question part
│    └── mark point
│
└── Learning resources
     ├── revision note
     ├── flashcard
     └── smart-lesson step
```

The graph visualizer can show specification points as the fine-grained anchors, while optionally grouping/hiding lower levels for readability.

## 10. Product behavior around the graph

The intended learner loop is:

```text
Student opens Chemistry
       ↓
Sees Chemistry dashboard
       ↓
Chooses a topic / graph node / activity
       ↓
Studies or attempts questions
       ↓
Assessment + confidence + timing evidence
       ↓
Learner model updates
       ↓
Graph overlay changes
       ↓
Target Test / Smart Lesson / Tutor adapts
       ↓
Student reassesses
```

Examples:

- Weak SpecificationPoint → Target Test can generate practice specifically around that objective.
- Wrong + high confidence → Tutor can investigate a likely misconception instead of merely repeating a note.
- Correct + low confidence → system can reinforce and reassess rather than treating the point as secure.
- Timed weak / untimed strong → the learner overlay can expose a procedural-fluency issue rather than a pure knowledge gap.

These are implementation directions built from the existing learner-model architecture; they are not claims that the system has validated those diagnoses.

## 11. Subject isolation rules

All student-facing academic reads and mutations should be scoped through the student's subject enrollment and the selected curriculum version.

A subject must not accidentally leak:

- questions from another board/qualification/version
- revision notes from another specification
- learner state from another subject
- Smart Lesson state from another course
- tutor context from another subject
- past papers from a different board/version unless deliberately surfaced as a cross-course reference

The API should therefore prefer explicit subject/curriculum identifiers over free-form topic names.

## 12. Current product architecture vs Cycle-1 scope

This document defines the **long-term product architecture**.

It does not authorize scope expansion of the current pilot.

Current Cycle-1 execution remains Edexcel IAL Chemistry according to ADR-010 and the Master Spec. The same subject-first architecture is designed to support IGCSE Chemistry and other board/qualification combinations later.

Do not start bulk IGCSE ingestion merely because this document now models IGCSE explicitly.

## 13. Required future implementation sequence

1. Preserve/strengthen the Board → Qualification → Subject → CurriculumVersion identity model.
2. Make SpecificationPoint a canonical curriculum object/node.
3. Map the user's existing revision notes to SpecificationPoints.
4. Expose subject enrollment and subject-scoped navigation.
5. Refactor feature surfaces to consume subject/curriculum context.
6. Add reviewed question → SpecificationPoint mapping.
7. Extend the personalized KG read model to expose specification points cleanly.
8. Build Smart Lesson on these shared anchors.

Do not implement these all at once. Follow the project backlog and Cycle-1 gate.

## 14. Non-negotiable agent rules for this architecture

- Treat this document as canonical for the subject-first product boundary and SpecificationPoint concept.
- Read the selected board/qualification's **official current specification** before inventing or manually encoding its hierarchy.
- Preserve official codes and wording exactly in canonical source fields.
- Never infer a subject/board/specification from a resource filename when an explicit curriculum identity is available.
- Never force multi-topic questions into a single topic or specification point.
- Preserve unmapped/uncertain links instead of fabricating tags.
- Keep curriculum versioning and provenance intact.
- Keep learner state separate from curriculum content.
- Do not pull IGCSE into Cycle 1 without an explicit scope decision.
