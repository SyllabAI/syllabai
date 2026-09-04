# SyllabAI Exam Content & Question Feature Architecture

**Status:** Approved architectural direction  
**Date:** 2026-09-04  
**Scope:** Past-paper question content, rendering, assessment composition, and reusable question embeds

## 1. Purpose

SyllabAI's GLM-OCR-converted past papers and mark schemes are not merely an ingestion convenience. The Markdown files and their extracted image assets provide a reusable presentation representation of exam content while the canonical question model provides the stable domain representation used by assessment, learner modelling, Smart Mark, retrieval, and future features.

The system must therefore preserve both representations:

```text
Original PDF
    │
    ├── GLM-OCR Markdown
    │      ├── extracted text
    │      ├── equations
    │      ├── tables
    │      └── image references
    │
    └── extracted image assets
           ├── diagrams
           ├── graphs
           ├── chemical structures
           └── other visual question content
                    │
                    ▼
          Canonical SyllabAI content
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   Semantic/domain       Presentation source
   representation       Markdown + assets
          │                   │
          └─────────┬─────────┘
                    ▼
              Feature layer
```

The raw Markdown must not become the domain model, and the canonical model must not discard the source Markdown or visual assets needed for faithful rendering.

## 2. First-class question content

A question must be represented as a stable domain object and may contain multiple parts. Presentation content must support text and visual elements.

```text
Question
 ├── QuestionVersion
 ├── QuestionPart[]
 │    ├── text/content
 │    ├── equations
 │    ├── tables
 │    ├── figures/images
 │    └── marks
 ├── MarkScheme
 ├── curriculum/KG links
 └── source/provenance
```

The existing canonical document format remains the language-neutral ingestion contract. Question/QuestionPart objects are the assessment-facing projection of that content.

## 3. GLM-OCR Markdown as a presentation source

The project has a corpus in which question papers and mark schemes were converted to Markdown using Z.ai GLM OCR, with extracted images retained alongside the Markdown files.

This representation should be retained and indexed rather than re-OCRing the same corpus unnecessarily.

The parser/content pipeline should normalize the GLM-OCR representation into the canonical document format while preserving:

- Markdown/source provenance;
- image references and stable asset identities;
- page associations;
- question and part boundaries where detected;
- equations and tables;
- source document/version identifiers.

OCR-derived question boundaries remain subject to the same validation rules as other automated extraction. The real-corpus T-011 extraction experience demonstrated that draft extraction can contain boilerplate spillover, so the presentation source must never be treated as proof that semantic question boundaries are correct.

## 4. Frontend rendering principle

The frontend should render questions through a stable Question/QuestionPart content API rather than directly depending on filesystem paths or repository layout.

The backend/API resolves a question to its presentation representation and assets. This keeps the web application independent of whether assets ultimately live in the parser workspace, Cloudflare R2, another object store, or another content provider.

Conceptually:

```text
Next.js
   │
   │ Question/QuestionPart API
   ▼
syllabai-core
   │
   ├── canonical question metadata
   ├── Markdown/renderable content
   └── asset references
          │
          ▼
       object storage
```

The browser should receive stable URLs or content references, not internal parser filesystem locations.

## 5. Shared feature foundation

All exam-question features should reference canonical question IDs/versions instead of copying question content into each feature.

```text
                         Canonical Question
                                │
          ┌─────────────┬───────┼─────────┬─────────────┐
          ▼             ▼       ▼         ▼             ▼
    Exam Questions  Target   Test      Mock Exams   Notes Embed
                     Test    Builder
```

If question metadata, rendering, KG mapping, Smart Mark support, or provenance improves, every feature benefits automatically.

## 6. Exam Questions

The Exam Questions experience is the searchable/browsable question bank over the canonical assessment corpus.

Expected filters and views include, as supported by available metadata:

- subject;
- qualification;
- exam board;
- paper;
- exam session/year;
- topic/subtopic;
- learning objective;
- marks;
- question type;
- completion history;
- learner mastery/recommendation state.

A question may be displayed using the source-faithful Markdown-derived presentation, including extracted diagrams, graphs, equations and tables.

## 7. Target Test

Target Test is a personalized practice session selected from the learner's current needs.

Candidate selection signals include:

```text
Learner state
+ knowledge graph/prerequisites
+ misconceptions
+ struggle inferences
+ timed/untimed performance
+ assessment history
+ question metadata
+ exam relevance
        ↓
Target Test question selection
```

Target Test must continue to use canonical question references so selected questions remain connected to learner evidence, Smart Mark, KG relationships and future recommendations.

## 8. Test Builder

Test Builder is a controlled composition workflow for creating an assessment from canonical questions.

Potential controls include:

- subject/qualification;
- topic selection;
- difficulty mix;
- question source;
- mark target;
- time target;
- selected questions;
- generated question set.

A test should store QuestionRefs/QuestionVersionRefs rather than duplicate Markdown or image binaries.

```text
Test
 ├── QuestionRef → Q001
 ├── QuestionRef → Q037
 ├── QuestionRef → Q142
 └── QuestionRef → Q281
```

## 9. Mock Exams

Mock Exams should support at least two conceptual modes:

1. **Real-paper mode:** reproduce an actual past paper using its canonical questions, ordering, instructions, timing and mark structure.
2. **Generated/mock composition mode:** assemble a new exam that follows a configured assessment structure using eligible canonical questions.

The distinction should be preserved for analytics and research because a reproduced historical paper and a constructed mock are different assessment artifacts.

## 10. Notes with embedded past-paper questions

Notes should be able to embed a canonical question by reference rather than copying its content.

```text
Note
 ├── learner-authored Markdown/content
 ├── QuestionEmbed → Q001
 ├── QuestionEmbed → Q087
 └── QuestionEmbed → Q213
```

The rendered note can provide actions such as:

- open/view the original question;
- practice the question;
- view the mark scheme when permitted;
- add the question to a test;
- ask the tutor about the question;
- find related/similar questions.

Question embeds should remain linked to their source question/version so content provenance is preserved.

## 11. Visual evidence is first-class

Text-only extraction is insufficient for many exam questions. A question may depend on a graph, diagram, chemical structure, apparatus image, map, table, or other visual element.

Therefore:

```text
QuestionPart
 ├── text
 ├── equation
 ├── table
 └── visual asset reference
```

The same original visual evidence should be available to the tutor/retrieval and Smart Mark pipelines when appropriate, not only to the frontend.

This is especially important for Physics, Chemistry and Mathematics questions where the visual or mathematical layout can carry semantic information that OCR text alone does not preserve.

## 12. Relationship to Smart Mark and KA-RAG

The shared question representation should support the following flow:

```text
Question
 + QuestionPart
 + original/source visual evidence
 + mark scheme
 + curriculum/KG links
 + learner context
       │
       ├── Smart Mark
       ├── KA-RAG / Tutor
       ├── Target Test
       ├── Test Builder
       ├── Mock Exam
       └── Exam Questions UI
```

KA-RAG evidence items should be able to resolve back to the exact document/version/chunk/page/element and, where applicable, the question/part that produced the evidence.

Smart Mark should likewise be able to access the source question context, including relevant visual evidence, when judging an answer.

## 13. Storage boundary

Large binaries must not be stored on the Render filesystem. The canonical application model should store metadata and stable references; object storage is the intended home for source PDFs, Markdown-derived assets and other large binaries.

The initial deployment architecture uses Cloudflare R2 for object storage. The storage provider remains an infrastructure concern and must not leak into the frontend domain model.

## 14. Future features enabled by this foundation

The same canonical question/reference architecture can support additional features without creating another question representation, including:

- Practice Again based on missed marks or misconceptions;
- Similar Questions;
- topic/question sets;
- question-to-note and note-to-question navigation;
- question-to-tutor assistance;
- question-to-target-practice generation;
- question-to-mock composition;
- post-exam lost-mark/topic analysis;
- teacher assignments;
- evidence-linked explanations;
- historical paper exploration;
- adaptive revision sets.

These are feature candidates, not all committed Cycle-1 scope.

## 15. Non-negotiable implementation rules

1. Do not discard GLM-OCR Markdown merely after extracting plain text.
2. Preserve extracted images and their provenance.
3. Do not make the frontend depend on parser filesystem paths.
4. Do not duplicate question Markdown/assets separately for every feature.
5. Use stable Question/QuestionPart/QuestionVersion references across features.
6. Preserve source document/version/page/element provenance.
7. Keep automated extraction explicitly distinguishable from human-validated assessment structure.
8. Keep visual evidence available wherever it is semantically relevant, not only where it is convenient to render.
9. Keep source/presentation storage behind content APIs and infrastructure ports.
10. Reuse the same question representation across assessment, learner modelling, Smart Mark, KA-RAG, and future recommendation features.
