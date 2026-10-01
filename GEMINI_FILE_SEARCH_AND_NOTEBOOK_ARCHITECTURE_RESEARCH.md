# Gemini File Search / Gemini Notebook-Inspired Architecture Research

**Status:** Accepted research investigation; **no production default is adopted by this document**.
**Research date:** 2026-09-14
**Scope:** Google Gemini File Search / File Search Stores, the architecture lessons suggested by Gemini Notebook (formerly NotebookLM), and implications for SyllabAI's Educational Retrieval Engine.
**Relationship:** This document extends `RAG_RETRIEVAL_RESEARCH.md`; it does not replace it.
**Primary decision boundary:** SyllabAI owns educational truth, curriculum semantics, learner state, validation and evidence provenance. Gemini services may provide retrieval/reasoning infrastructure but must not become the authoritative educational system.

---

## 1. Why this investigation exists

The trigger for this investigation was a strategic question rather than a narrow API question:

> If Gemini Notebook can turn a collection of documents into a highly usable, source-grounded research environment, and Google now exposes persistent File Search Stores as a developer-facing retrieval primitive, how much generic RAG infrastructure should SyllabAI continue to build and operate itself?

This is a first-class architecture question because SyllabAI currently invests in:

- document ingestion;
- chunking and evidence segmentation;
- embeddings;
- pgvector retrieval;
- lexical retrieval;
- hybrid fusion;
- reranking;
- citation/evidence plumbing;
- multimodal document handling;
- retrieval evaluation.

Some of those capabilities are SyllabAI differentiators. Others may be commodity infrastructure that a managed Gemini service can provide well enough.

The correct question is therefore **not** "Can Gemini File Search replace SyllabAI RAG?".

The correct question is:

> **Which retrieval/document-grounding responsibilities should remain SyllabAI-owned, and which can safely be delegated to Gemini File Search without weakening educational correctness, provenance, portability or evaluation?**

---

## 2. Current external evidence

Google's current Gemini API documentation describes File Search as a managed RAG capability that imports, chunks and indexes data for semantic retrieval. A File Search Store is persistent until explicitly deleted; the temporary File API object is deleted after 48 hours, while indexed data remains. Google also exposes File Search Store and Document management APIs. [Official documentation](https://ai.google.dev/gemini-api/docs/file-search)

Current documented capabilities include:

- persistent File Search Stores;
- direct upload into a store or import from the Files API;
- automatic chunking, embedding and indexing;
- semantic retrieval;
- custom document metadata;
- citations in model output;
- PDF page-number information in citations when available;
- multimodal File Search using `gemini-embedding-2` for text and images;
- structured output with Gemini 3 models;
- document-level lifecycle management.

Current documented constraints include:

- 100 MB maximum per File Search document;
- project storage limits by tier;
- Google recommends keeping an individual File Search Store below 20 GB for retrieval latency;
- File Search is not available in the Live API;
- File Search cannot be combined with other built-in grounding tools such as Google Search or URL Context in the same request;
- audio and video are not currently supported by File Search.

Google currently documents free File Search storage and query-time embeddings, with indexing embeddings charged at the applicable embedding rate and retrieved document tokens charged as normal model input tokens. These pricing/limits are time-sensitive and must be rechecked before implementation. [Official File Search docs](https://ai.google.dev/gemini-api/docs/file-search) [Official pricing](https://ai.google.dev/gemini-api/docs/pricing)

Google's July 2026 product announcement says NotebookLM was renamed **Gemini Notebook** while retaining its standalone research-notebook role. Google describes Gemini Notebook as a research tool and has added a secure cloud computer capable of writing/executing code for source-grounded analysis. [Google announcement](https://blog.google/innovation-and-ai/products/gemini-notebook/notebooklm-gemini-notebook/)

Google's June 2026 NotebookLM announcement described new agentic capabilities and more advanced reasoning for complex research projects. This is evidence that the product direction is moving beyond simple retrieve-then-answer RAG, but it is **not evidence that the public File Search API exposes the entire Notebook/Gemini Notebook system**. [Google announcement](https://blog.google/innovation-and-ai/products/notebooklm/better-research-notebooklm/)

---

## 3. Critical distinction: Gemini File Search is not Gemini Notebook

The architecture must distinguish three layers:

```text
Gemini Notebook / NotebookLM-class product
        ↓
product UX + orchestration + research/agent behavior
        ↓
Gemini model/tooling + source grounding
        ↓
Gemini File Search / other retrieval infrastructure
```

File Search is a developer-facing retrieval primitive. Gemini Notebook is a complete product built from retrieval, models, orchestration, source interaction, artifact generation, UI and increasingly agentic capabilities.

Therefore:

> **Do not infer that adopting File Search gives SyllabAI a NotebookLM clone.**

What File Search can potentially give SyllabAI is the managed document-retrieval substrate underneath one class of grounded experiences.

The Notebook product is nevertheless architecturally valuable as a reference because it demonstrates the product value of turning a source set into a persistent, interactive, citation-grounded knowledge workspace.

---

## 4. What File Search could eliminate from SyllabAI infrastructure

A managed File Search path can potentially remove or reduce the need for SyllabAI to independently implement all of the following for selected corpora:

```text
raw document
    ↓
chunking
    ↓
embedding generation
    ↓
vector index construction
    ↓
semantic retrieval
    ↓
retrieval-side source association
    ↓
citation annotations
```

That is strategically important because these are not necessarily SyllabAI's core educational differentiators.

SyllabAI should instead concentrate its engineering ownership on:

```text
curriculum truth
SpecificationPoints
assessment semantics
concept/prerequisite semantics
learner state
learning evidence
teacher validation
resource suitability
educational provenance
evidence sufficiency
claim validation
adaptive intervention
```

This separation can reduce undifferentiated infrastructure work while strengthening the product's differentiated layer.

---

## 5. What File Search cannot become the authority for

File Search must **not** become the authoritative source for:

- curriculum hierarchy;
- SpecificationPoints;
- prerequisite relationships;
- misconception relationships;
- learner mastery;
- learner interaction evidence;
- teacher validation state;
- assessment identity;
- canonical mark-point semantics;
- resource-to-curriculum truth;
- educational claim validity.

An embedding or retrieval result is evidence for retrieval, not a pedagogical fact.

The existing SyllabAI invariant remains:

> **Embeddings and retrieval graphs are not educational truth.**

A Gemini-generated or Gemini-retrieved relationship may be useful for candidate generation, but it must not silently mutate or override the authoritative SyllabAI KG.

---

## 6. Proposed architecture: Retrieval Fabric

The investigation recommends treating Gemini File Search as a possible **retrieval provider** inside a broader SyllabAI Retrieval Fabric.

```text
                         SyllabAI
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ↓                           ↓
   Authoritative Educational        Retrieval Fabric
          Intelligence                    │
              │             ┌─────────────┼─────────────┐
              │             ↓             ↓             ↓
              │           BM25       pgvector      Gemini File
              │             │             │           Search
              │             └─────────────┼─────────────┘
              │                           ↓
              │                    Fusion/deduplication
              │                           ↓
              │                    SyllabAI reranker
              │                           ↓
              │                 Evidence/segment selection
              │                           ↓
              │                 Evidence sufficiency gate
              └──────────────────────────→ Context
                                          ↓
                                       Gemini
                                          ↓
                                Claim/citation validation
                                          ↓
                                   Grounded response
```

The key architectural property is that File Search is **pluggable**. We must be able to benchmark it, use it selectively, disable it, or replace it without rewriting the curriculum, learner or Tutor architecture.

A conceptual interface should therefore resemble:

```text
RetrievalProvider
  retrieve(StructuredRetrievalQuery)
      → RetrievalCandidates
```

Potential providers:

```text
PgVectorRetriever
Bm25Retriever
AuthoritativeKgRetriever
GeminiFileSearchRetriever
```

The returned candidate contract should be normalized before SyllabAI-specific fusion/reranking.

---

## 7. Three resource classes

A useful architectural distinction is to classify source material by how much canonical structure SyllabAI needs to own.

### Class A — Canonical educational data

Examples:

- official specifications;
- curriculum hierarchy;
- SpecificationPoints;
- authoritative KG relations;
- canonical question identity;
- validated mark-point semantics.

**Primary owner:** SyllabAI.

Gemini may receive derived copies for retrieval, but the database/KG remains authoritative.

### Class B — Validated SyllabAI learning resources

Examples:

- validated Revision Notes;
- validated Exam Questions;
- validated Past Papers;
- validated Mark Schemes;
- examiner reports.

**Primary owner:** SyllabAI canonical resource/assessment systems.

A mirrored Gemini File Search representation may be useful as a retrieval index.

### Class C — Unstructured or user-provided study material

Examples:

- teacher-uploaded PDFs;
- supplementary notes;
- school handouts;
- student study material;
- temporary reference documents.

**Potential owner:** File Search as a managed retrieval index, with SyllabAI owning access control, resource identity and product semantics.

This class is where the "upload PDF and immediately use RAG" advantage is strongest.

---

## 8. Why the simple upload workflow matters

The strongest practical argument for File Search is not merely retrieval quality. It is **time-to-grounded-experience**.

A traditional SyllabAI ingestion path can look like:

```text
PDF
 ↓
parse/OCR
 ↓
structure extraction
 ↓
identity
 ↓
normalization
 ↓
validation
 ↓
resource objects
 ↓
SpecificationPoint mapping
 ↓
KG mapping
 ↓
embedding
 ↓
retrieval index
```

That is correct for canonical educational content, but it is excessive for every arbitrary teacher/student document.

For Class C material, a managed path could be:

```text
Upload PDF
    ↓
File Search Store
    ↓
automatic processing/indexing
    ↓
Contextual Learning Assistant
```

This should be considered a major product opportunity, not just an infrastructure convenience.

It could enable a future workflow such as:

```text
Teacher uploads handout
        ↓
selects subject/resource context
        ↓
SyllabAI creates a managed study source
        ↓
student can ask questions
        ↓
citations point back to source
```

The source would still be clearly marked as supplementary/non-canonical unless it passes SyllabAI validation.

---

## 9. Metadata mapping to SyllabAI

File Search supports custom metadata. Current API documentation allows up to 20 custom metadata entries per Document and supports string, string-list and numeric values.

This is useful, but the File Search metadata model must remain a **projection** of SyllabAI metadata rather than a competing schema.

Candidate metadata:

```text
syllabai_resource_id
syllabai_resource_version
subject_id
qualification_id
curriculum_version_id
specification_id
specification_point_ids
concept_ids
resource_type
assessment_session
paper_code
document_role
validation_status
source_provenance_id
```

Not all of these necessarily belong in File Search metadata. The benchmark/prototype should determine which filters materially improve retrieval.

The authoritative representation remains in SyllabAI.

---

## 10. Citation architecture

File Search's citation annotations are promising because they can include source information, PDF page numbers where available, custom metadata and, for multimodal media chunks, a media identifier.

SyllabAI should normalize these into its own evidence chain:

```text
Gemini File Search citation
          ↓
SyllabAI Evidence Candidate
          ↓
resource/version identity
          ↓
evidence segment/page/media identity
          ↓
SpecificationPoint / concept mapping
          ↓
provenance
```

The external citation is therefore an **input to SyllabAI evidence handling**, not the final educational citation model.

The Tutor should ultimately be able to answer:

> Why was this evidence selected, what source did it come from, what curriculum point does it support, and is that evidence sufficient for the claim?

A File Search citation alone does not answer all four questions.

---

## 11. Multimodal opportunity

The current File Search documentation supports multimodal File Search through `gemini-embedding-2`, allowing text and images to participate in retrieval.

This is unusually relevant to SyllabAI because educational PDFs frequently contain:

- chemistry structures;
- apparatus diagrams;
- graphs;
- particle diagrams;
- tables;
- question figures;
- scanned educational layouts.

This could complement the existing `syllabai-parser` multimodal/document-processing research.

However, it should not replace canonical parser extraction where deterministic structure is required. A multimodal embedding can help retrieve a relevant figure; it does not establish the authoritative meaning of that figure.

---

## 12. Gemini Notebook as a product architecture reference

Gemini Notebook provides evidence for a broader design principle:

> Once users have a persistent source set with strong grounding, many downstream learning/research experiences can be generated from the same evidence substrate.

SyllabAI should therefore think beyond a single Tutor answer.

A validated/source-grounded resource context could support:

```text
Resource context
      │
      ├── Ask / Explain
      ├── Summarize
      ├── Common pitfalls
      ├── Exam tips
      ├── Flashcards
      ├── Practice questions
      ├── Audio revision
      ├── Visual summaries
      ├── Revision sessions
      └── Agentic study workflows
```

The important difference is that SyllabAI can condition these experiences on:

- curriculum/specification;
- assessment context;
- learner state;
- misconceptions;
- previous attempts;
- learning evidence;
- next-best-action logic.

That is the opportunity to go **beyond Notebook-style source interaction**, rather than trying to clone NotebookLM.

---

## 13. Agentic implications

The 2026 Gemini Notebook announcements show a product direction toward agentic research and source-grounded execution. That is relevant to SyllabAI, but the architecture should not jump directly from File Search to unrestricted agents.

Recommended progression:

```text
Stage 1
Deterministic retrieval + evidence gate

Stage 2
Structured query transformation + multi-retriever fusion

Stage 3
Bounded tool use around SyllabAI educational APIs

Stage 4
Agentic study/research workflows with explicit budgets and provenance
```

Any SyllabAI agent should use app-controlled tools such as:

- get_current_resource;
- get_specification_context;
- get_related_concepts;
- search_curriculum;
- find_revision_note;
- find_exam_questions;
- get_learner_state;
- get_relevant_learning_evidence;
- create_practice_recommendation;
- navigate_to_resource;
- start_practice.

The agent must not receive unrestricted authority to mutate canonical educational truth.

---

## 14. Critical trade-offs

### Advantages

**A. Lower engineering burden**

Google provides a managed indexing/retrieval path rather than SyllabAI operating every low-level retrieval component.

**B. Very low ingestion friction**

The PDF → searchable source workflow is close to the user experience we want for supplementary resources.

**C. Citation support**

Source/page/media annotations reduce custom citation plumbing for the external retrieval path.

**D. Multimodal retrieval**

Useful for image-rich educational documents.

**E. Gemini-native integration**

The retrieval layer is directly consumable by Gemini models and can participate in the same model/tool ecosystem.

**F. Potentially favorable operating economics**

Google currently documents free storage and query-time embeddings, with indexing embeddings charged and retrieved tokens billed as normal model input. Actual SyllabAI cost must be measured, not assumed.

### Risks

**A. Vendor lock-in**

The retrieval index, chunking behavior and service semantics become dependent on Google.

**B. Retrieval opacity**

SyllabAI does not control every indexing/retrieval detail as it does with its own database.

**C. Educational semantics are externalized incorrectly if misused**

A generic retrieved chunk can be relevant without being pedagogically correct for the learner/curriculum.

**D. Tool composition constraints**

Current File Search cannot be combined with certain other built-in grounding tools in the same request.

**E. Size/scale constraints**

Current documentation imposes 100 MB per document and project/store limits. This requires a corpus-scale feasibility test.

**F. Provider availability / model evolution**

Gemini model and File Search behavior can change. Provider-specific compatibility must be isolated behind SyllabAI interfaces.

**G. Portability**

If the canonical corpus exists only in File Search, migrating away becomes difficult. Therefore File Search must never be the only durable representation of canonical SyllabAI content.

---

## 15. Proposed provider contract

The architecture should eventually expose a provider-neutral contract roughly equivalent to:

```text
StructuredRetrievalQuery
    - normalized query
    - subject/curriculum scope
    - SpecificationPoint scope
    - concept/misconception scope
    - resource type filters
    - learner context signals
    - evidence requirements

RetrievalCandidate
    - provider
    - external document identity
    - SyllabAI resource identity if known
    - evidence locator
    - metadata
    - relevance score
    - provenance
    - validation state
    - citation information
```

The Gemini adapter should translate between this contract and File Search's store/document/metadata model.

This allows us to run:

```text
Provider A: pgvector
Provider B: BM25
Provider C: KG
Provider D: Gemini File Search
```

without changing the Tutor contract.

---

## 16. Benchmark design

Gemini File Search must be added to the existing RAG benchmark rather than evaluated by subjective demo quality.

Use the planned 100–200 representative 4CH1 Tutor queries and add a dedicated File Search arm.

### Required comparison

```text
A  pgvector semantic baseline
B  BM25
C  hybrid BM25 + semantic
D  hybrid + reranker
E  Gemini File Search
F  hybrid + Gemini File Search
G  KG-aware hybrid + Gemini File Search
```

### Query classes

Include:

- direct factual questions;
- conceptual explanations;
- calculations;
- misconception questions;
- prerequisite questions;
- "why did I get this wrong?" questions;
- exam-question retrieval;
- mark-scheme retrieval;
- revision-note retrieval;
- vague learner-language queries;
- multi-SpecificationPoint questions;
- diagram/figure-dependent questions.

### Metrics

Retrieval:

- Recall@5/10/20;
- MRR;
- nDCG;
- SpecificationPoint resolution;
- evidence precision;
- false positives.

Grounding:

- evidence sufficiency;
- citation correctness;
- claim-to-evidence alignment;
- unsupported-claim rate.

Operational:

- p50/p95 latency;
- indexing time;
- query cost;
- index/storage footprint;
- failure/retry rate;
- provider dependency surface.

### Additional provider-specific tests

1. **Metadata filtering accuracy** — does a Chemistry 4CH1 query remain inside the intended scope?
2. **Document identity fidelity** — can a retrieved result be mapped back to the exact SyllabAI resource/version?
3. **Page/figure fidelity** — can citations identify the correct page/media evidence?
4. **Corpus update behavior** — can a superseded resource be removed/replaced without stale retrieval?
5. **Validation boundary** — can SUGGESTED resources be excluded from learner-serving retrieval?
6. **Isolation** — can different subjects/qualifications be kept separate?
7. **Scale** — what happens as the corpus approaches realistic production size?
8. **Portability** — can canonical data reconstruct the File Search representation after loss/provider migration?

---

## 17. Recommended experiments

### Experiment A — Minimal File Search POC

Index a small, known-good 4CH1 corpus:

- a handful of Revision Notes;
- a few Exam Questions;
- matching Mark Schemes;
- a few Past Papers.

Attach SyllabAI metadata and run representative queries.

**Goal:** establish integration correctness and citation fidelity.

### Experiment B — Retrieval benchmark

Run the same gold queries against the existing pgvector baseline and File Search.

**Goal:** compare retrieval quality and cost.

### Experiment C — Multimodal benchmark

Use image/diagram-heavy Chemistry material.

**Goal:** test whether `gemini-embedding-2` retrieval adds meaningful value over text/pgvector retrieval.

### Experiment D — Contextual Learning Assistant

Put File Search behind the existing `RESOURCE_CONTEXT` architecture.

**Goal:** test whether the managed retriever materially improves the Revision Note / Exam Question assistant without changing product semantics.

### Experiment E — Supplementary teacher/student upload

Allow an explicitly non-canonical uploaded PDF to become searchable immediately.

**Goal:** test the strongest product advantage: low-friction personal/teacher source grounding.

### Experiment F — Agentic bounded workflow

After deterministic retrieval is validated, let an agent perform a small bounded study workflow using File Search plus SyllabAI read-only educational tools.

**Goal:** determine whether agentic orchestration produces useful learning outcomes without weakening provenance or control.

---

## 18. Architecture decision matrix

| Question | Current direction |
|---|---|
| Replace SyllabAI KG? | **No** |
| Replace canonical PostgreSQL resource/assessment data? | **No** |
| Replace all pgvector retrieval? | **Not yet; benchmark first** |
| Add File Search as a retrieval provider? | **Yes, investigate immediately** |
| Use File Search for supplementary PDFs? | **Strong candidate** |
| Mirror validated resources into File Search? | **Strong candidate; benchmark** |
| Use File Search as sole canonical storage? | **No** |
| Use Gemini citations directly as final educational provenance? | **No; normalize into SyllabAI evidence** |
| Use Gemini Notebook as a UX/product reference? | **Yes** |
| Rebuild NotebookLM itself? | **No** |
| Introduce unrestricted agentic RAG now? | **No** |
| Build provider-neutral retrieval interface? | **Yes** |

---

## 19. Provisional architecture conclusion

The strongest current conclusion is:

> **Gemini File Search should be treated as a first-class candidate retrieval infrastructure, not as a replacement for SyllabAI's educational architecture.**

The most promising architecture is:

```text
                     SyllabAI
                        │
         ┌──────────────┴──────────────┐
         ↓                             ↓
 Authoritative                    Retrieval Fabric
 Educational KG / DB                    │
         │                  ┌───────────┼───────────┐
         │                  ↓           ↓           ↓
         │                BM25      pgvector    Gemini FS
         │                  └───────────┼───────────┘
         │                              ↓
         │                         Fusion/rerank
         │                              ↓
         └──────────────────────→ Evidence gate
                                       ↓
                                  Gemini Tutor
                                       ↓
                                Claim validation
                                       ↓
                                 Learner evidence
```

This preserves the architectural principle established in `RAG_RETRIEVAL_RESEARCH.md`:

> **SyllabAI should own educational truth and selectively outsource generic retrieval infrastructure where benchmark evidence shows that doing so improves quality, cost, latency or development velocity.**

No production default should change until the benchmark provides evidence.

---

## 20. Research status and next action

**Status:** ACCEPTED RESEARCH INVESTIGATION / PROPOSED ARCHITECTURE.

**Not yet accepted:** replacing pgvector, BM25, the canonical retrieval engine, or any authoritative SyllabAI data store.

**Next action:** build the File Search POC and add it as a benchmark arm against the existing 4CH1 retrieval stack.

**Durability:** This document is the durable record of the Gemini File Search / Gemini Notebook architectural discussion so the reasoning does not depend on conversation history.
