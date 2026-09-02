# Definitive Research Dossier: Learning, Knowledge, Document Intelligence, RAG & Agent Repositories

**Research date:** 2026-09-02  
**Scope:** The repositories/organization URL supplied in the research request.  
**Primary evidence:** Repository README pages, repository structure, published metadata, release notes where visible, and official project documentation linked from those repositories.  
**Important:** GitHub stars/forks and feature sets are fast-moving. This document intentionally emphasizes architecture, capabilities, integration role, maturity signals, licensing, and practical fit rather than treating star counts as quality scores.

---

## Executive summary

The 38 supplied URLs are not one homogeneous technology set. They form a fairly coherent **learning/knowledge-engine stack** with several distinct layers:

1. **Pedagogy / tutoring**
   - SocraticLM
   - Scientific Learning Skills
   - DeepTutor
   - Get It.
   - Student LLM Wiki
   - Marble Skill Taxonomy
   - HouseLearning

2. **Knowledge transformation / agent skills**
   - book-to-skill
   - cheatsheet-generator-skill
   - Awesome LLM Apps
   - Understand Anything
   - Graphify
   - Hyper-Extract
   - A11Y.md

3. **Notebook / research / knowledge-base applications**
   - Open Notebook
   - PageLM
   - Memorwise
   - SurfSense
   - OpenKnowledge
   - Cognee
   - iii

4. **Document ingestion, OCR and parsing**
   - OpenDataLoader PDF
   - anydoc
   - MinerU
   - Surya
   - Unlimited-OCR
   - pdf-inspector
   - pdfcn
   - Infinite Bookshelf

5. **Retrieval, vector, graph and database infrastructure**
   - SurrealDB
   - Zvec
   - HelixDB
   - pgContext
   - Blockify
   - Graphify
   - Cognee
   - Hyper-Extract

6. **Adjacent developer/data tooling**
   - Chat2DB
   - system-design-101
   - Leantime
   - awesome-research
   - the `zvec-ai` organization page

### The strongest architectural insight

If the objective is to build a serious AI learning/research system, **do not choose one of these projects as the entire stack**. The strongest combination is usually:

> **Document parser → normalized knowledge representation → prerequisite/knowledge graph → hybrid retrieval → learner model/memory → diagnostic tutor → assessment/feedback → UI**

The supplied repositories collectively cover nearly every stage of that pipeline.

---

# 0. SyllabAI integration verdicts (verified 2026-09-03)

This section was added when the pack was merged and corrected. It is the **authoritative per-repo verdict** for SyllabAI under the actual constraints: Java 25/Spring Boot 4.1/Spring AI 2.0 backend, Next.js frontend, Neon Postgres + pgvector, free tiers, no credit card. Where this section disagrees with a dossier entry below, **this section wins**. License data re-verified against GitHub API + project sites.

**Roles:** USE-DIRECT (embeddable, permissive license) · OFFLINE-PIPELINE (runs locally in `syllabai-parser` content ops, not deployed) · REFERENCE (study patterns; no code copying beyond permissive snippets) · WATCH (revisit when constraints change) · SKIP.

| Repo | License (verified) | Stack fit | Verdict & role for SyllabAI |
|---|---|---|---|
| opendataloader-project/opendataloader-pdf | Apache-2.0 | **Java 11+ (embeddable in-process, Maven Central `org.opendataloader:opendataloader-pdf-core`)** | **USE-DIRECT.** Top extraction benchmark (0.907 overall / 0.928 tables); Markdown+JSON with bounding boxes → citation grounding. Embed inside `syllabai-core` for text PDFs. |
| withmarbleapp/os-taxonomy | ODbL-1.0 (content CC BY-SA) | Data, any stack | **USE-DIRECT (data).** 1,590 micro-topics + 3,221 prerequisite edges + evidence criteria — KG schema template and bootstrap seed for Paper B §3.2. Attribution required; chemistry subset must be authored ourselves (it covers primary-level). |
| hwl668/Scientific-learning-skills- | MIT | Prompt design, language-neutral | **USE-DIRECT (prompts).** Diagnosis-first 9-skill tutoring system — Paper A's philosophy implemented; port into Tutor/Assessor agent prompt design. |
| shadcn-labs/pdfcn | MIT | TypeScript/React | **USE-DIRECT (frontend).** React PDF generation components for Test Builder / print-friendly exports. |
| opendatalab/mineru | Custom Apache-2.0-based (recently moved off AGPL — verify at pin time) | Python, GPU-friendly | **OFFLINE-PIPELINE.** Complex academic PDF parsing; runs locally in `syllabai-parser`, output feeds the KG. |
| datalab-to/surya | Code Apache-2.0; **model weights modified-OpenRAIL** | Python | **OFFLINE-PIPELINE.** OCR/layout/tables for scanned past papers. Do not redistribute weights. |
| firecrawl/anydoc, firecrawl/pdf-inspector | MIT | Rust core, multi-lang bindings | **OFFLINE-PIPELINE.** anydoc for office docs → Markdown; pdf-inspector for cheap text/scan classification & routing. |
| yifanfeng97/Hyper-Extract, Graphify-Labs/graphify | Apache-2.0 | Python / TS | **OFFLINE-PIPELINE / REFERENCE.** LLM-driven docs→graph extraction (education templates included) and deterministic graph construction — KG candidate mining. |
| HKUDS/DeepTutor | Apache-2.0 | Python + Next 16 | **REFERENCE.** Closest cousin (personalized deep-doc tutoring); study retrieval fusion + tutor orchestration. Too large to deploy parts of. |
| lfnovo/open-notebook | MIT | Python + Next + SurrealDB(Docker) | **REFERENCE only.** Uses BSL-licensed SurrealDB + Docker — not free-tier-hostable; run locally as internal examiner-report mining tool. |
| Egonex-AI/Understand-Anything | MIT | TypeScript | **REFERENCE.** Interactive KG explorer UI patterns for the mastery map. |
| beltromatti/get-it | Apache-2.0 | Next 16 + React 19 + Tailwind 4 | **REFERENCE.** "PDF→mastery map" product twin — UX reference for the student dashboard. |
| Ljyustc/SocraticLM | Code Apache-2.0; **dataset CC-BY-NC** | Python research | **REFERENCE.** 35K Socratic dialogues, 6 student types — informs Cycle-2 Socratic agent prompts. Dataset: inspiration only, no redistribution. |
| CaviraOSS/PageLM | Custom Community License | Node/TS | **REFERENCE (UX only).** License forbids copying into SyllabAI. |
| OtterMind/Chat2DB | Source-available, conditions (GitHub: NOASSERTION) | Java | **REFERENCE.** Java NL2SQL patterns for the teacher DAT (Cycle 2+). Do not embed. |
| topoteretes/cognee | Apache-2.0 | Python | **REFERENCE.** ETL→graph+vector memory patterns. |
| shubhamsaboo/awesome-llm-apps | Apache-2.0 | Multi | **REFERENCE.** Pattern library for agent/RAG implementations. |
| robzilla1738/Memorwise | MIT | Node | **REFERENCE.** Multi-provider LLM config pattern. |
| evokoa/pgcontext | Apache-2.0 | PG17/18 extension | **WATCH.** Hybrid search inside Postgres — not in Neon's extension catalog; revisit if we self-host PG. |
| helixdb/helix-db | Apache-2.0 | Rust | **WATCH.** Graph+vector+FTS single DB — young, no Java client; revisit for Cycle 3+. |
| alibaba/zvec | Apache-2.0 | C++ core, Python bindings | **WATCH.** In-process vector DB — no Java binding; `zvec-grep` is a nice local CLI. pgvector stays default. |
| baidu/Unlimited-OCR | MIT | GPU/Transformers | **SKIP for Cycle 1** (GPU-only). Watch for hosted inference later. |
| MODSetter/SurfSense | Unspecified | .NET/TS | **SKIP.** License unclear + pivoted to live-web research agents. |
| fecarrico/A11Y.md | MIT | Rules/context files | **USE-DIRECT (rules feed).** WCAG behavior contract for our coding agents + accessibility baseline. |
| surrealdb/surrealdb | **BSL 1.1 — NOT Apache-2.0 (v1.0 dossier error, corrected)** | Rust | **STRUCK (ADR-013).** Not open source; commercial use restricted. Removed from all tiers. |
| inkeep/open-knowledge | GPL-3.0 | TS desktop | **SKIP.** Copyleft desktop app, not embeddable. |
| leantime/leantime | AGPL-3.0 | PHP | **SKIP.** Not relevant + copyleft. |
| iternal-technologies-partners/blockify | Custom + patented | SaaS | **SKIP.** Patented, closed pipeline. |
| houselearning/home | Apache-2.0 | Browser games | **SKIP.** Kids' mini-games; engagement layer only, out of scope. |
| iii-hq/iii | No license | — | **SKIP.** No license = no rights. |
| Bklieger/infinite-bookshelf | MIT | Python/Streamlit | **SKIP (concept only).** Generative books without grounding — contradicts provenance policy. |
| virgiliojr94/book-to-skill, Evan715823/cheatsheet-generator-skill | MIT | Prompt pipelines | **REFERENCE.** Notes-distillation and cheatsheet output patterns (Cycle 2+ study artifacts). |
| IssacW228/student-llm-wiki | MIT | Markdown workflow | **REFERENCE.** Minimal personal knowledge-base pattern. |
| emptymalei/awesome-research, ByteByteGoHq/system-design-101 | CC / reading material | — | **SKIP (reading only).** |
| zvec-ai org page | — | — | Discovery only; not a runtime component. |

**Key Java-fit findings** (missing from the v1.0 dossier): opendataloader-pdf is the only Java-embeddable parser and should run **in-process** in `syllabai-core` (no separate service); zvec/HelixDB/pgcontext lack Java clients or Neon availability, so pgvector remains the vector substrate; open-notebook is not free-tier-hostable (Docker + SurrealDB). No repo in this set provides BKT/BDT/IRT engines, learning-log telemetry, or Smart Mark grading logic — the scientific core is greenfield Java, which is the entire point of the course project.

---

# 1. Comparative architecture map

| Layer | Strongest candidates | Primary role |
|---|---|---|
| Curriculum graph | Marble Skill Taxonomy | Prerequisite graph and learning ontology |
| Socratic tutoring | SocraticLM | Research-backed personalized Socratic dialogue |
| Diagnosis-first tutoring | Scientific Learning Skills | Agent-skill behavior for identifying misconceptions before explaining |
| Full tutoring platform | DeepTutor | End-to-end personalized tutor, RAG, memory, agents |
| Mastery-oriented study | Get It. | PDF → concept/mastery map and assessment |
| Student knowledge wiki | Student LLM Wiki | Course slides → persistent Obsidian wiki |
| Agent skill generation | book-to-skill | Books/docs → modular Agent Skills |
| Dense study output | cheatsheet-generator-skill | Course material → compact LaTeX cheatsheet |
| General AI templates | Awesome LLM Apps | Reusable agent/RAG/MCP implementations |
| Code knowledge graph | Understand Anything | Codebase → interactive graph |
| Universal code/docs graph | Graphify | Code/docs/configs/PDFs → deterministic graph |
| Structured knowledge extraction | Hyper-Extract | Text → graphs/hypergraphs/spatio-temporal relations |
| NotebookLM-like app | Open Notebook | Self-hosted multimodal research notebook |
| NotebookLM-like education app | PageLM | Study material → quizzes/flashcards/notes/podcasts |
| Local NotebookLM | Memorwise | Local-first document chat |
| Live-web research | SurfSense | Agent-accessible live web connectors + knowledge base |
| Markdown knowledge environment | OpenKnowledge | Local/private markdown IDE + AI/MCP |
| Agent memory | Cognee | Persistent graph-backed AI memory |
| Service/agent runtime | iii | Compose/discover/observe workers |
| PDF parsing | MinerU / OpenDataLoader | High-quality structured document extraction |
| General office-doc parsing | anydoc | Multi-format → Markdown |
| PDF routing | pdf-inspector | Classify PDFs and selectively OCR |
| OCR/layout | Surya | OCR + layout + reading order + tables |
| Long-document OCR | Unlimited-OCR | One-shot long-horizon OCR/parsing |
| Vector DB | Zvec | Embedded high-performance vector search |
| Graph-vector DB | HelixDB | Graph + vector + KV/document/relational storage |
| Multi-model DB | SurrealDB | Document + graph + vector + relational + realtime |
| Postgres-native retrieval | pgContext | Hybrid AI search inside PostgreSQL |
| Semantic compression | Blockify | Raw content → deduplicated IdeaBlocks |
| PDF rendering UI | pdfcn | React PDF generation components |
| Generated books | Infinite Bookshelf | LLM-generated educational books |
| Accessibility rules | A11Y.md | Enforceable AI/developer accessibility contract |
| DB/SQL workbench | Chat2DB | Database management + AI SQL |
| Research directory | awesome-research | Curated research workflow resources |
| System-design curriculum | system-design-101 | Visual system-design learning material |
| Browser learning games | HouseLearning | Interactive educational mini-games |
| Project execution | Leantime | Goals/project/task management |

---

# 2. Repository dossiers

## 2.1 SocraticLM

**Repository:** https://github.com/Ljyustc/SocraticLM

**Category:** Research / personalized tutoring / fine-tuning

**What it is:**  
SocraticLM is the implementation/data repository for the NeurIPS 2024 Spotlight paper *SocraticLM: Exploring Socratic Personalized Teaching with Large Language Models*. The repository contains the SocraTeach datasets and code for fine-tuning ChatGLM3-6B into a Socratic teaching model.

**Core assets**
- `SocraTeach_multi.json`: approximately 35K multi-round teacher/student dialogues.
- `SocraTeach_single.json`: approximately 22K single-round teaching examples.
- Fine-tuning and evaluation scripts.
- Student-response types and simulated student scenarios.
- Evaluation includes conversation and mathematical problem-solving tasks.

**Architecture**
```text
Teaching data
   ↓
SocraTeach dataset
   ↓
ChatGLM3-6B fine-tuning
   ↓
Socratic teaching model
   ↓
Conversation / problem-solving evaluation
```

**Why it matters:** It is one of the most directly relevant repositories for a system whose tutor should **guide reasoning rather than immediately reveal answers**.

**Best use:** Training/evaluating a Socratic tutor policy.

**Limitations:** The repository is research-oriented and tied to an older ChatGLM-era fine-tuning stack. It is not an end-to-end modern learning platform.

**License / usage:** Check the repository license and dataset terms separately before redistributing the dataset or model artifacts.

**Verdict:** **High-value research component, not a complete product stack.**

---

## 2.2 Marble Skill Taxonomy / os-taxonomy

**Repository:** https://github.com/withmarbleapp/os-taxonomy

**Category:** Curriculum ontology / prerequisite graph / learning data

**What it is:**  
A structured taxonomy of primary/elementary learning represented as a graph rather than a flat curriculum list.

**v1 dataset**
- 1,590 micro-topics.
- 3,221 prerequisite edges.
- 8 subjects.
- Topics include descriptions, evidence criteria, type, subject/domain and approximate age range.
- Dependencies are directed and classified as `hard` or `soft`.
- Curriculum alignment includes frameworks such as Common Core and NGSS.

**Subjects**
- Science
- Mathematics
- English
- History
- Personal & Social Development
- Life Skills
- Computing
- Learning to Learn

**Important data model**
```text
Topic
 ├── id
 ├── type
 ├── subject
 ├── domain
 ├── description
 ├── age range
 ├── evidence
 ├── assessment prompt
 └── curriculum standards

Dependency
 ├── topicId
 ├── prerequisiteId
 ├── strength
 └── reason
```

**Why it matters:** This is arguably the most important repository in the list if the goal is a **real learner model** rather than generic RAG.

**Best use:** Seed ontology, prerequisite graph, mastery planning, diagnostic routing, curriculum sequencing.

**Critical licensing note:** The database is ODbL 1.0; Marble-authored textual content is CC BY-SA 4.0; upstream curriculum standards retain their own licensing. A product should not treat the entire directory as a generic MIT/Apache dataset.

**Verdict:** **Exceptional foundational data model for curriculum-aware learning.**

---

## 2.3 Understand Anything

**Repository:** https://github.com/Egonex-AI/Understand-Anything

**Category:** Code intelligence / knowledge graph / agent skill

**What it is:**  
An open-source Claude Code-oriented system that analyzes codebases using a multi-agent pipeline, builds a knowledge graph of files/functions/classes/dependencies, and exposes the result through an interactive dashboard.

**Core idea**
```text
Codebase
  ↓
Multi-agent analysis
  ↓
Entities + relationships
  ↓
Knowledge graph
  ↓
Interactive exploration / search / Q&A
```

**Strengths**
- Code-centric graph representation.
- Designed for large codebases.
- Agent-compatible.
- Useful precedent for converting unstructured/technical source material into navigable semantic structure.

**Best use:** Developer knowledge systems, course-code understanding, repository tutoring, technical documentation graphs.

**License:** MIT.

**Verdict:** **Excellent reference architecture for graph-first technical knowledge.**

---

## 2.4 DeepTutor

**Repository:** https://github.com/HKUDS/DeepTutor

**Category:** End-to-end AI tutor / agent platform / RAG / memory

**What it is:**  
A very large, actively evolving open-source personalized tutoring platform. Its current architecture goes substantially beyond a simple chat-with-PDF application.

**Major capabilities visible in the project**
- Agentic tutoring.
- Deep Research.
- Deep Solve.
- Question generation.
- Guided Learning.
- Knowledge bases.
- RAG.
- GraphRAG / LightRAG / PageIndex-related retrieval.
- Persistent memory.
- Skills.
- Books / living-book compilation.
- Visualize and Animator.
- Question Bank.
- TutorBot / Partners.
- CLI and SDK.
- MCP integrations.
- Multiple document parsers.
- Multiple LLM and embedding providers.
- Multi-user/resource isolation.
- Docker deployment.

The repository's recent releases show a rapid architectural evolution, including canonical routes, recoverable streams, learner/guardian accounts, grounded reading, WeKnora, broader parsing, and Python 3.14 support.

**Why it matters:** This is the closest repository in the list to an **integrated operating system for AI-powered learning**.

**Strengths**
- Broadest feature surface.
- Agent-native architecture.
- Multiple retrieval strategies.
- Persistent memory.
- Learning-specific workflows.
- Extensible tools/skills.
- Production/deployment concerns are explicitly addressed.

**Risks**
- Large and complex codebase.
- Fast release cadence means architecture can change quickly.
- Integrating only a small part may be harder than using smaller focused projects.

**License:** Apache-2.0.

**Verdict:** **Best end-to-end reference implementation in the list.**

---

## 2.5 Awesome LLM Apps

**Repository:** https://github.com/shubhamsaboo/awesome-llm-apps

**Category:** Cookbook / reference implementations

**What it is:**  
A large collection of runnable AI agents, agent skills, RAG systems, MCP agents, voice agents, and other LLM applications.

**Repository structure includes**
- `agent_skills`
- `starter_ai_agents`
- `advanced_ai_agents`
- `advanced_llm_apps`
- `mcp_ai_agents`
- `rag_tutorials`
- `voice_ai_agents`
- `generative_ui_agents`
- `always_on_agents`

**Why it matters:** It is not a single framework. It is a **pattern library**.

**Best use**
- Discover implementation patterns.
- Compare agent orchestration strategies.
- Copy small working examples.
- Prototype RAG/MCP/agent functionality.

**License:** Apache-2.0.

**Verdict:** **High-value reference library; do not mistake it for one coherent platform.**

---

## 2.6 Scientific Learning Skills

**Repository:** https://github.com/hwl668/Scientific-learning-skills-

**Category:** Agent Skills / diagnosis-first tutoring

**Core philosophy:**  
The system explicitly promotes **diagnosis before explanation**.

Instead of:
```text
Question → Answer
```

it aims for:
```text
Student statement
   ↓
Diagnose misconception / missing prerequisite
   ↓
Targeted repair
   ↓
Verification
   ↓
Transfer / variation
```

**Notable behavior**
- Vocabulary support with contextual distinctions and memory.
- Misconception diagnosis.
- Prerequisite identification.
- Verification questions.
- Variations designed to test whether understanding transfers.
- Skill-oriented architecture rather than a monolithic application.

**Why it matters:** This complements SocraticLM extremely well. SocraticLM focuses on the teaching interaction; Scientific Learning Skills adds a practical **diagnostic policy layer**.

**License:** MIT.

**Caveat:** The repository itself explicitly distinguishes illustrative behavior examples from controlled experiments or real-user learning evidence.

**Verdict:** **Excellent behavioral blueprint for a modern learning agent.**

---

## 2.7 book-to-skill

**Repository:** https://github.com/virgiliojr94/book-to-skill

**Category:** Document transformation / Agent Skills

**What it does:**  
Converts books, document folders, or source collections into structured Agent Skills.

**Generated structure**
```text
SKILL.md
chapters/
glossary.md
patterns.md
cheatsheet.md
```

The main skill stays relatively small while chapter content is loaded on demand.

**Key concept:**  
It does not merely summarize a book. It converts the material into **frameworks, decision rules, anti-patterns, chapter structure, glossary and patterns** for agent retrieval.

**Notable claim:** The repository reports 24×–51× fewer tokens than repeatedly dumping a book into context, based on its own measurements.

**Installation model**
- Claude Code
- GitHub Copilot CLI
- Amp / compatible Agent Skills hosts
- Optional standalone Python extraction package

**Security/privacy:** Processing is designed to happen locally; the tool does not upload the user's source documents.

**License:** MIT.

**Verdict:** **One of the strongest repos for turning static books into reusable agent knowledge.**

---

## 2.8 PageLM

**Repository:** https://github.com/CaviraOSS/PageLM

**Category:** Education platform / NotebookLM alternative

**What it does:**  
Transforms study material into:
- Quizzes
- Flashcards
- Structured notes
- Podcasts

**Stack**
- Backend: Node.js / TypeScript / LangChain / LangGraph
- Frontend: React / Vite / Tailwind
- Storage: JSON by default, optional vector DB
- LLMs: multiple providers
- TTS: Edge TTS, ElevenLabs, Google TTS
- Document processing: pdf-lib, mammoth, pdf-parse
- Docker / Docker Compose

**Strengths**
- Student-oriented UI.
- Multiple learning output types.
- Straightforward full-stack architecture.
- Good starting point for an educational NotebookLM clone.

**Limitations**
- More application-oriented than learning-science-oriented.
- JSON/default persistence is less sophisticated than dedicated graph/database stacks.

**License:** Repository currently describes personal/educational use and requires permission for commercial use; inspect the current license before commercial deployment.

**Verdict:** **Good product/UI reference; combine with stronger learner modeling for serious adaptive tutoring.**

---

## 2.9 Get It.

**Repository:** https://github.com/beltromatti/get-it

**Category:** Mastery learning / PDF study companion

**Core idea:**  
A PDF is converted into a **measurable mastery map**, emphasizing concepts rather than pages.

The project explicitly distinguishes itself from:
- generic summaries,
- ordinary flashcards,
- static mind maps.

It asks whether the learner could survive a **novel question**.

**Input**
- Text-based PDF
- Markdown

The current implementation rejects scan/image-only PDFs because it reads text rather than performing image OCR.

**Architecture**
```text
PDF / Markdown
   ↓
Document processing
   ↓
Concept structure
   ↓
Visual mastery map
   ↓
Assessment / learning interaction
```

**Strengths**
- Strong mastery-oriented product concept.
- Visually communicates conceptual structure.
- Good complement to a curriculum graph.

**Limitation:** It is not a universal document parser; scanned PDFs need preprocessing elsewhere.

**License:** Apache-2.0.

**Verdict:** **Excellent UX/product concept for a mastery dashboard.**

---

## 2.10 cheatsheet-generator-skill

**Repository:** https://github.com/Evan715823/cheatsheet-generator-skill

**Category:** Study artifact generation / Agent Skill

**Inputs**
- PDF
- PPTX
- Markdown
- Plain text
- PNG/JPG

**Output:** Dense XeLaTeX cheatsheet.

**Pipeline**
```text
Course materials
   ↓
Topic hierarchy + exam prioritization
   ↓
Dense content generation
   ↓
LaTeX
   ↓
XeLaTeX / Overleaf
```

**Features**
- Browser configuration.
- 2–6 columns.
- Paper size/margins/fonts.
- Multiple print-oriented color schemes.
- Formula-heavy density.
- Image-aware editing.
- Natural-language iterative editing.

**Verdict:** **Very useful as a final-stage study-material generator.**

---

## 2.11 Student LLM Wiki

**Repository:** https://github.com/IssacW228/student-llm-wiki

**Category:** Student knowledge base / Obsidian / AI compilation

**Workflow**
```text
Course slides
   ↓
AI compilation
   ↓
Structured wiki/
   ↓
Obsidian
   ↓
Feynman review / exam prep / weak-topic analysis
```

**Key characteristics**
- Course PDFs go into `raw/`.
- AI generates structured notes in `wiki/`.
- Designed around Obsidian.
- Uses Dataview for a dynamic dashboard.
- Includes schema/instruction files.
- Supports several coding/AI-agent environments.

**Strengths**
- Extremely simple mental model.
- Markdown is durable and portable.
- Great foundation for student-owned knowledge.

**Limitation:** It is primarily a file/wiki workflow, not a sophisticated backend learner model.

**License:** MIT.

**Verdict:** **Excellent minimalist personal knowledge-base pattern.**

---

## 2.12 HouseLearning

**Repository:** https://github.com/houselearning/home

**Category:** Educational games / browser learning

**What it is:**  
A browser-based collection of bite-sized educational games and activities.

**Features**
- Interactive games.
- Immediate feedback.
- Points/progress.
- Responsive browser UI.
- No installation requirement.

**Stack:** HTML5, CSS3 and browser JavaScript.

**Why it matters:** It represents the **active-practice/game layer** that most RAG/tutoring platforms lack.

**License:** Apache-2.0.

**Verdict:** **Useful for the practice/engagement layer, not the knowledge layer.**

---

## 2.13 Memorwise

**Repository:** https://github.com/robzilla1738/Memorwise

**Category:** Local-first NotebookLM alternative

**Inputs**
- PDFs
- Images
- Audio
- Video
- URLs
- YouTube links

**Workflow**
```text
Sources
   ↓
Local chunking + embeddings
   ↓
Notebook
   ↓
LLM chat
```

**Local-first model**
- Runs on the user's machine.
- Supports Ollama and LM Studio.
- Also supports OpenAI, Anthropic and Gemini.
- Simple `npx memorwise` setup.
- Current README requires Node.js 22.13+ or 24+.

**License:** MIT.

**Strengths**
- Simple local deployment.
- Provider flexibility.
- Multimodal ingestion.
- Privacy-friendly architecture.

**Verdict:** **Strong lightweight alternative when DeepTutor/Open Notebook are too large.**

---

## 2.14 awesome-research

**Repository:** https://github.com/emptymalei/awesome-research

**Category:** Research-resource directory

**Status:** **Deprecated.**

The repository itself states that its contents have moved to the maintainer's website.

**Coverage historically includes**
- Notes
- Presentations
- Programming
- Academic research
- Open source
- Data visualization
- LaTeX
- Miscellaneous research tools

**Verdict:** **Useful as a historical resource map, but should not be selected as active infrastructure.**

---

## 2.15 Open Notebook

**Repository:** https://github.com/lfnovo/open-notebook

**Category:** Self-hosted NotebookLM alternative

**Core capabilities**
- Local/self-hosted research notebook.
- 18+ AI providers.
- PDFs, video, audio, web pages and other multimodal content.
- Full-text and vector search.
- Contextual chat.
- Multi-speaker podcast generation.
- REST API.
- Docker deployment.
- Multi-language UI including Bengali.

**Architecture**
The current repository uses a Python application plus supporting services including SurrealDB and configurable AI providers.

**Strengths**
- Mature feature set.
- Provider independence.
- Self-hosting.
- Strong multimodal notebook concept.
- API access makes it useful as a subsystem.

**Weakness:** The project's own comparison acknowledges that citation behavior is less comprehensive than Google's NotebookLM.

**License:** MIT.

**Verdict:** **One of the strongest practical bases for a private research/learning workspace.**

---

## 2.16 OpenDataLoader PDF

**Repository:** https://github.com/opendataloader-project/opendataloader-pdf

**Category:** PDF parser / accessibility / AI-ready extraction

**Outputs**
- Markdown
- JSON with bounding boxes
- HTML
- Tagged PDF

**Architecture**
- Deterministic local parsing.
- Optional AI hybrid mode for complex pages.
- OCR for scanned documents.
- Layout and reading-order reconstruction.
- Table/formula/image handling.

**Current README highlights**
- Reports a 0.907 overall benchmark score.
- Reports 0.928 table accuracy across 200 real-world PDFs.
- Built-in hybrid OCR supporting 80+ languages.
- Java 11+ and Python 3.10+ for the Python path.

**SyllabAI integration note (2026-09-03):** This is the **only Java-embeddable parser** in the set — Apache-2.0, available on Maven Central (`org.opendataloader:opendataloader-pdf-core`), so it runs **in-process inside `syllabai-core`** (no separate parsing service) for text PDFs, with bounding boxes feeding the citation/provenance chain. Scanned pages route to MinerU/Surya offline.

**Why it matters:** It is a strong **document-normalization front end** for RAG.

**License:** Apache-2.0 for current 2.x; older versions had different licensing.

**Verdict:** **Top-tier PDF ingestion candidate.**

---

## 2.17 anydoc

**Repository:** https://github.com/firecrawl/anydoc

**Category:** Universal office/document parser

**What it does:** A fast Rust library that converts:
- Word
- PowerPoint
- Excel
- OpenDocument
- RTF
- EPUB
- CSV
- PDF

into GitHub-Flavored Markdown.

**Bindings**
- Rust
- Node.js
- Python
- CLI
- Agent Skill

**Important distinction:** anydoc is optimized for **clean deterministic document conversion**, while scanned PDFs requiring OCR are better handled by an OCR-capable system such as MinerU, Surya, OpenDataLoader hybrid mode or Unlimited-OCR.

**Verdict:** **Excellent general-purpose preprocessor for heterogeneous office/document corpora.**

---

## 2.18 SurfSense

**Repository:** https://github.com/MODSetter/SurfSense

**Category:** Live-web research infrastructure / NotebookLM alternative

**Current strategic direction:**  
The project has shifted strongly toward giving agents **live web-research primitives**.

**Connectors include**
- Reddit
- YouTube
- Instagram
- TikTok
- Amazon
- Walmart
- Google Maps
- Google Search
- Indeed
- Arbitrary web pages

**Architecture**
```text
Agent
  ↓
SurfSense REST/MCP
  ↓
Typed live-data connector
  ↓
Structured result
  ↓
Research / citation / knowledge base
```

**Strengths**
- Live rather than static knowledge.
- MCP-native.
- Structured data instead of browser-driving.
- Self-hostable.
- Agent harness with retries and structured output.

**Verdict:** **Best fit in this list for a tutor/research agent that needs current external information.**

---

## 2.19 SurrealDB

**Repository:** https://github.com/surrealdb/surrealdb

**Category:** Multi-model database

**Data models**
- Document
- Graph
- Relational
- Time-series
- Geospatial
- Key-value
- Full-text search
- Vector/hybrid retrieval

**Capabilities**
- Transactions.
- WebSockets.
- Graph queries.
- Authentication/authorization.
- Realtime updates.
- Embedded JavaScript.
- Browser/edge/embedded/cloud deployment.
- MCP support.

**Why it matters:** It can consolidate several infrastructure roles that would otherwise require separate services.

**Best use:** Knowledge objects + graph edges + metadata + vector retrieval + application state.

**License / usage:** **CORRECTION (2026-09-03):** SurrealDB core is licensed under the **Business Source License 1.1**, not Apache-2.0 as this dossier originally stated. It is not open source; commercial/production use is restricted. Struck from SyllabAI consideration by ADR-013.

**Verdict:** ~~**Very strong general backend candidate for an integrated learning system.**~~ **STRUCK from SyllabAI (ADR-013): BSL 1.1 license. PostgreSQL + pgvector remains the sole substrate.**

---

## 2.20 Unlimited-OCR

**Repository:** https://github.com/baidu/Unlimited-OCR

**Category:** Long-document OCR / document intelligence model

**Core idea:**  
One-shot, long-horizon OCR/parsing intended to reduce the traditional page-by-page OCR limitation.

**Current repository information**
- Hugging Face model: `baidu/Unlimited-OCR`.
- Transformers-based inference.
- CUDA/NVIDIA-oriented reference environment.
- Supports image/PDF workflows.

**Why it matters:** Long textbooks and scans are exactly where conventional OCR pipelines become expensive and structurally fragile.

**Caveat:** This is a model/research component, not a complete document-management system.

**Verdict:** **Interesting specialized OCR component for difficult/long documents.**

---

## 2.21 MinerU

**Repository:** https://github.com/opendatalab/mineru

**Category:** Document intelligence / PDF & Office parsing

**Capabilities**
- PDF
- DOCX
- PPTX
- XLSX
- Images
- Web pages
- Markdown/JSON output
- Formula → LaTeX
- Tables → HTML
- Scanned documents
- Handwriting
- Multi-column layouts
- Cross-page table merging
- Reading-order reconstruction
- Header/footer removal
- VLM + OCR dual engine
- 109-language OCR

**Integrations**
- MCP
- LangChain
- LlamaIndex
- RAGFlow
- RAG-Anything
- Flowise
- Dify
- FastGPT
- Python/Go/TypeScript SDKs
- CLI
- REST
- Docker

**Why it matters:** This is one of the most comprehensive **document-ingestion layers** in the list.

**Verdict:** **Top candidate for complex educational PDFs.**

---

## 2.22 Graphify

**Repository:** https://github.com/Graphify-Labs/graphify

**Category:** Deterministic knowledge graph / code & documentation intelligence

**Core idea:**  
Turn codebases and their supporting artifacts into a queryable graph.

**Supported knowledge sources include**
- Source code
- Documentation
- SQL schemas
- Configurations
- PDFs

**Architecture**
- Local deterministic AST parsing.
- Explicit/explainable graph edges.
- Agent Skill interface.
- No vector store required for its core graph representation.

**Why it matters:** Graphify is particularly valuable for a system that wants **explainable structural relationships**, not just semantic similarity.

**Verdict:** **Excellent graph-construction reference and potentially complementary to vector RAG.**

---

## 2.23 Surya

**Repository:** https://github.com/datalab-to/surya

**Category:** OCR / layout / table recognition

**Current model:** Surya 2 is described as a 650M-parameter OCR model.

**Capabilities**
- OCR
- Text detection
- Layout analysis
- Reading order
- Table recognition
- 90+ language capability
- OCR error detection

**Current README metrics**
- 83.3% on olmOCR-bench.
- 5 pages/s on an RTX 5090 in the stated benchmark.
- 87.2% on an internal 91-language benchmark.

**Architecture**
Surya 2 uses a shared VLM inference manager for OCR/layout/table tasks and can use vLLM or llama.cpp.

**Important licensing distinction**
- Code: Apache-2.0.
- Model weights: separate modified AI Pubs Open Rail-M terms.

**Verdict:** **Excellent OCR/layout engine, but check model-weight licensing for commercial products.**

---

## 2.24 OpenKnowledge

**Repository:** https://github.com/inkeep/open-knowledge

**Category:** Local markdown IDE / AI-native knowledge environment

**Core capabilities**
- WYSIWYG Markdown.
- Desktop app for macOS/Windows/Linux.
- Web UI.
- File navigator.
- Search.
- Tabs.
- Graph wiki-link viewer.
- AI editing.
- Claude/Codex/OpenCode/Pi integrations.
- MCP.
- Skills.
- Agentic search.
- Git/GitHub-backed sync.
- Embeddable HTML/rich components.

**Why it matters:** This is the **human-facing knowledge workspace** layer rather than the ingestion/database layer.

**License:** GPL-3.0.

**Verdict:** **Excellent UX reference for a local/private knowledge environment; copyleft license matters for derivatives.**

---

## 2.25 Zvec

**Repository:** https://github.com/alibaba/zvec

**Category:** Embedded vector database

**Core idea:**  
A lightweight in-process vector database designed for low-latency similarity search.

**Architecture**
- Native/C++ core.
- Python bindings.
- Embedded operation.
- HNSW/ANN-oriented retrieval.
- Quantization/index optimization.
- Cross-platform distribution.

**Current v0.7.0 highlights**
- `zvec-grep` for combined ripgrep/BM25/vector workspace search.
- ReMe integration as a memory file-store backend.
- DiskANN productionization.
- IVF-RaBitQ.
- PQ-INT8.
- ARM64 support.
- Multiple prebuilt SDK targets.

**License:** Apache-2.0.

**Verdict:** **Strong candidate when an application needs local embedded vector retrieval without a separate vector service.**

---

## 2.26 zvec-ai organization page

**URL:** https://github.com/orgs/zvec-ai/repositories

**Type:** Organization/repository index, not a single implementation repository.

**Use:** Discovery only. The important implementation candidate supplied alongside it is Alibaba's `zvec` repository.

**Verdict:** **Do not treat this URL as an additional runtime component.**

---

## 2.27 HelixDB

**Repository:** https://github.com/helixdb/helix-db

**Category:** Graph-vector database / AI data layer

**Core model**
- Graph
- Vector
- Key-value
- Document
- Relational support

**Architecture**
- Built from scratch in Rust.
- Object-storage-oriented architecture.
- Native graph + vector + full-text search.
- CLI for local instances/cloud.
- Agent-oriented tooling.
- `helix chef` can bootstrap projects and agent skills.

**Why it matters:** It attempts to reduce the need for separate graph DB + vector DB + application data layers.

**License:** Apache-2.0.

**Verdict:** **Highly relevant for an integrated knowledge graph + semantic retrieval backend.**

---

## 2.28 Chat2DB

**Repository:** https://github.com/OtterMind/Chat2DB

**Category:** Database client / SQL / AI developer tool

**Capabilities**
- 40+ databases.
- SQL editing/completion/formatting/execution.
- Database metadata management.
- DDL/DML editing.
- Data import/export.
- Dashboards/charts.
- AI SQL generation/explanation/optimization.
- Desktop, web, Docker and CLI.
- MCP support.

**Why it matters:** It is not a learning engine, but it can be useful for **operating/debugging the database layer** of a knowledge platform.

**License:** Open-source license in repository; inspect the current LICENSE before embedding or redistribution.

**Verdict:** **Adjacent operational tool, not a core learning component.**

---

## 2.29 Hyper-Extract

**Repository:** https://github.com/yifanfeng97/Hyper-Extract

**Category:** LLM knowledge extraction / graph / hypergraph

**Core idea:**  
Transform unstructured text into structured knowledge using:
- Graphs
- Hypergraphs
- Spatio-temporal extraction

**Notable features**
- Chunk-level fault isolation.
- Partial results instead of losing an entire extraction.
- Directed relation preservation.
- MCP server.
- Multiple LLM providers.
- Education templates:
  - `education/course_concept_graph`
  - `education/curriculum_structure`

**Why it matters:** This is particularly aligned with converting textbooks and lectures into **course concept graphs**.

**Verdict:** **One of the most directly useful repositories for educational knowledge extraction.**

---

## 2.30 system-design-101

**Repository:** https://github.com/ByteByteGoHq/system-design-101

**Category:** Educational content / technical curriculum

**What it contains:**  
A large visual/simple-language collection explaining system-design and software-engineering concepts.

**Examples**
- HTTP
- WebSockets
- load balancing
- API gateways
- GraphQL
- networking
- browser rendering
- API design
- distributed-system concepts

**Why it matters:** It is principally **content**, not a software framework.

**Best use**
- Knowledge corpus.
- Benchmark content for technical tutoring.
- Example of visual-first educational documentation.

**Verdict:** **Excellent source material; not infrastructure.**

---

## 2.31 iii

**Repository:** https://github.com/iii-hq/iii

**Category:** Agent runtime / service composition / observability

**Core idea:**  
A live system surface for composing, extending and observing backend services.

Workers can represent:
- queues
- HTTP
- state
- agents
- cron
- other capabilities

**Agent model**
```text
Agent needs capability
      ↓
Discover worker
      ↓
Add/compose worker
      ↓
Call worker
      ↓
Observe/trace result
```

**Why it matters:** It provides an interesting answer to the question:

> How does a learning agent dynamically acquire tools instead of having every capability hard-coded?

**Verdict:** **Infrastructure/reference architecture for agentic orchestration.**

---

## 2.32 A11Y.md

**Repository:** https://github.com/fecarrico/A11Y.md

**Category:** Accessibility engineering / AI behavioral contract

**Core idea:**  
A context system intended to make accessibility a default engineering constraint for both developers and AI agents.

**Notable design**
- 18-rule AI behavioral contract.
- Framework adaptation.
- Platform awareness.
- Component reuse.
- Decision memory.
- Release evidence.
- Independent verification.
- Image/media evidence handling.
- Cognitive-load considerations.
- Explicit anti-pattern prevention.

**Compliance profiles**
- Shield / AAA
- Standard / AA
- Launchpad / A

**Why it matters:** For an educational platform, accessibility is not a cosmetic layer. It affects how explanations, assessments, navigation, diagrams, audio and cognitive load are designed.

**Verdict:** **Excellent policy/agent-instruction layer for an accessible learning product.**

---

## 2.33 pgContext

**Repository:** https://github.com/evokoa/pgcontext

**Category:** PostgreSQL-native AI search

**Core idea:**  
Turn PostgreSQL into the AI retrieval engine instead of copying data into a separate vector service.

**Capabilities**
- Dense vector search.
- Metadata-filtered ANN.
- Hybrid dense + full-text retrieval.
- HNSW and acceleration state.
- Exact re-scoring against live rows.
- MVCC-aware retrieval.
- PostgreSQL RLS/ACL compatibility.

**Architecture**
```text
PostgreSQL source of truth
 ├── application rows
 ├── metadata
 ├── vectors
 ├── permissions/RLS
 └── retrieval indexes
```

**Why it matters:** This is particularly attractive for applications where **authorization and retrieval must remain synchronized**.

**License:** Apache-2.0.

**Verdict:** **Excellent option if PostgreSQL is already the application's source of truth.**

---

## 2.34 Blockify

**Repository:** https://github.com/iternal-technologies-partners/blockify-agentic-data-optimization

**Category:** Semantic chunking / knowledge compression / RAG optimization

**Core concept:**  
Replace naive fixed-size chunks with **IdeaBlocks**.

An IdeaBlock contains:
- name
- critical question
- trusted answer
- tags
- entities
- keywords

**Pipeline**
```text
Enterprise content
   ↓
Semantic ingestion
   ↓
IdeaBlocks
   ↓
Embedding + LSH clustering
   ↓
LLM distillation / deduplication
   ↓
Optimized retrieval corpus
```

**Claimed benefits**
- Large compression.
- Better vector retrieval.
- Higher token efficiency.
- Deduplication.

**Important caution:** Performance figures in the repository are project claims and should be independently benchmarked on your corpus.

**Verdict:** **Highly relevant to reducing RAG noise and duplicated knowledge.**

---

## 2.35 pdfcn

**Repository:** https://github.com/shadcn-labs/pdfcn

**Category:** PDF generation UI / React components

**What it is:**  
A collection of customizable React PDF components.

**Features**
- Takumi and Forme rendering bases.
- Zero-config defaults.
- Live previews.
- Custom themes/props.
- shadcn/ui-compatible registry workflow.

**Why it matters:** This is a **presentation/output** component, not an ingestion/parser.

**Best use**
- Generate study guides.
- Generate reports.
- Export personalized learning plans.
- Produce polished PDFs from structured learner knowledge.

**License:** MIT.

**Verdict:** **Useful final-mile rendering layer.**

---

## 2.36 Cognee

**Repository:** https://github.com/topoteretes/cognee

**Category:** AI memory / knowledge graph / agent memory

**Core idea:**  
Persistent long-term memory for AI agents, backed by a self-hosted knowledge graph engine.

**Relevant concepts**
- Persistent memory.
- Knowledge graph.
- Agent recall.
- Data ingestion.
- Search/retrieval.
- Multiple integrations.
- Docker deployment.
- Python package architecture.

**Why it matters:** A tutor needs memory at multiple levels:
```text
Learner profile
   ↓
Known concepts
   ↓
Misconceptions
   ↓
Past attempts
   ↓
Spacing history
   ↓
Preferences
   ↓
Long-term knowledge graph
```

Cognee is highly relevant to the **memory layer** of that design.

**Verdict:** **Strong candidate for agent memory, especially when knowledge relationships matter.**

---

## 2.37 pdf-inspector

**Repository:** https://github.com/firecrawl/pdf-inspector

**Category:** PDF classification / routing / Rust

**Core idea:**  
Inspect a PDF cheaply before deciding how expensive the processing path needs to be.

**Classification**
- TextBased
- Scanned
- ImageBased
- Mixed

**Features**
- Confidence score.
- Position-aware extraction.
- Multi-column reading order.
- Table detection.
- Font/encoding diagnostics.
- Selective OCR.
- Page-level OCR routing.
- Rust core.
- Python, Node and WebAssembly bindings.

**Strategic value:** It enables:
```text
PDF
 ↓
Inspect
 ↓
Text PDF? ─────────→ cheap parser
 ↓
Scanned/mixed?
 ↓
OCR only necessary pages
```

**Verdict:** **Excellent routing layer and a very good optimization companion to heavyweight OCR.**

---

## 2.38 Infinite Bookshelf

**Repository:** https://github.com/Bklieger/infinite-bookshelf

**Category:** Generative educational content

**Core idea:**  
Generate complete books using LLMs, with scaffolded prompting that balances smaller/larger models.

**Features**
- Scaffolded prompting.
- Markdown book rendering.
- Tables/code.
- Text export.
- Streamlit UI.
- Groq/Llama-oriented workflow.

**Why it matters:** It represents a **content synthesis layer** that could sit downstream of a curriculum graph.

**Potential educational use**
```text
Learner gaps
   ↓
Selected concepts
   ↓
Generate targeted mini-book
   ↓
Study
   ↓
Assessment
```

**Caveat:** Generated books require strong factuality/citation controls before educational deployment.

**Verdict:** **Useful generation pattern, but should never be treated as an authoritative knowledge source.**

---

## 2.39 Leantime

**Repository:** https://github.com/leantime/leantime

**Category:** Project/goal management

**Core idea:**  
A goals-focused project management system designed for people who are not traditional project managers.

**Relevant characteristics**
- Goals.
- Tasks.
- Project organization.
- Planning.
- Accessibility-oriented design philosophy.
- PHP/web application architecture.
- Docker/Kubernetes-related deployment assets.

**Why it matters:** It is not an AI learning engine, but could inspire the **execution/planning layer** for:
- study plans,
- course projects,
- learning goals,
- milestones,
- assignments.

**Verdict:** **Adjacent planning infrastructure, not core knowledge infrastructure.**

---

# 3. Deep comparison by problem

## 3.1 If the problem is "understand a PDF"

### Best stack

**First-pass inspection**
- `pdf-inspector`

**General structured extraction**
- `anydoc`
- `OpenDataLoader PDF`

**Complex/scanned academic documents**
- `MinerU`
- `Surya`
- `Unlimited-OCR`

### Recommended routing

```text
PDF
 │
 ├── pdf-inspector
 │      │
 │      ├── clean text PDF
 │      │       ↓
 │      │     anydoc / OpenDataLoader
 │      │
 │      └── scan/mixed/complex
 │              ↓
 │           MinerU / Surya
 │              ↓
 │       difficult long-horizon OCR
 │              ↓
 │        Unlimited-OCR
 │
 ↓
Normalized Markdown + structured JSON + coordinates
```

---

# 4. If the problem is "turn documents into knowledge"

The strongest candidates are:

### 1. Hyper-Extract
Best for explicit graph/hypergraph extraction.

### 2. Graphify
Best for deterministic structural graph extraction.

### 3. book-to-skill
Best for agent-oriented modular knowledge.

### 4. Blockify
Best for semantic compression and retrieval-oriented knowledge units.

### 5. Cognee
Best for persistent agent memory after knowledge has been extracted.

### Recommended conceptual pipeline

```text
Raw document
    ↓
Document parser
    ↓
Canonical document model
    ↓
Semantic extraction
    ↓
 ┌───────────────┬─────────────────┬──────────────────┐
 │               │                 │
Skills       Concept graph     Knowledge blocks
 │               │                 │
book-to-skill  Hyper-Extract    Blockify
 │               │                 │
 └───────────────┴───────────────┘
                    ↓
             Persistent memory
                    ↓
                 Cognee
```

---

# 5. If the problem is "build a learning graph"

The strongest combination is:

**Marble Skill Taxonomy + Hyper-Extract + Graphify/Cognee/HelixDB**

### Marble contributes
- Curriculum ontology.
- Stable concept IDs.
- Prerequisite edges.
- Assessment prompts.
- Standards alignment.

### Hyper-Extract contributes
- Extraction of course-specific relationships.

### Graphify contributes
- Deterministic structural relationships.

### Cognee contributes
- Agent memory.

### HelixDB contributes
- Graph + vector storage.

### Example

```text
Official curriculum
       │
       ↓
Marble taxonomy
       │
       ├── prerequisite graph
       │
Course PDF ──→ MinerU
       │
       ↓
Hyper-Extract
       │
       ├── concepts
       ├── relations
       ├── examples
       └── dependencies
       │
       ↓
Course knowledge graph
       │
       ↓
HelixDB / SurrealDB / Cognee
```

---

# 6. If the problem is "build an adaptive tutor"

The strongest research/product combination is:

### Pedagogy
**SocraticLM**

### Diagnosis
**Scientific Learning Skills**

### Full agent platform
**DeepTutor**

### Learner/mastery UX
**Get It.**

### Curriculum
**Marble Skill Taxonomy**

### Memory
**Cognee**

### Retrieval
**pgContext / Zvec / HelixDB / SurrealDB**

### Live research
**SurfSense**

### Document ingestion
**MinerU / OpenDataLoader / Surya**

This produces a much more sophisticated architecture than ordinary RAG:

```text
                     ┌───────────────────┐
                     │ Curriculum Graph  │
                     │ Marble Taxonomy   │
                     └─────────┬─────────┘
                               │
Student ──→ Tutor Agent ───────┼────────→ Knowledge Graph
              │                │              │
              │                │              │
              ↓                ↓              ↓
          Diagnosis         Retrieval       Memory
              │                │              │
      Scientific Skills    pgContext/       Cognee
              │             Zvec/Helix
              ↓
        Socratic Dialogue
              │
              ↓
        Assessment
              │
              ↓
        Mastery Update
              │
              └──────────────→ Learner Model
```

---

# 7. Database decision matrix

| Requirement | Best candidate |
|---|---|
| Existing PostgreSQL stack | pgvector first (Neon-supported); pgContext if self-hosted PG |
| Embedded vector DB | Zvec (no Java binding — watch) |
| Graph + vector + application data | HelixDB (watch; no Java client) |
| Multi-model database | ~~SurrealDB~~ **STRUCK — BSL 1.1, not open source (corrected 2026-09-03)** |
| Agent memory/knowledge graph abstraction | Cognee |
| Retrieval-focused external vector layer | pgvector on Neon (default) |
| Maximum application consolidation | PostgreSQL (Neon) + pgvector |
| Rust-native graph/vector architecture | HelixDB |

### Practical recommendation

If you already have PostgreSQL (SyllabAI does — Neon):

> **pgvector on Neon first.** pgContext if self-hosting PG. HelixDB/Zvec remain watch-list items. **SurrealDB is struck (BSL 1.1).**

---

# 8. Document-parser decision matrix

| Requirement | Recommended |
|---|---|
| Office documents → Markdown | anydoc |
| PDF → Markdown/JSON/HTML | OpenDataLoader |
| Complex academic PDFs | MinerU |
| OCR + layout + tables | Surya |
| Long-horizon OCR research | Unlimited-OCR |
| Cheap PDF classification/routing | pdf-inspector |
| Local deterministic preprocessing | anydoc / OpenDataLoader |
| Hybrid AI PDF processing | OpenDataLoader / MinerU |
| Maximum OCR/layout specialization | Surya |

### Best overall architecture

```text
pdf-inspector
      ↓
Route cheaply
      ↓
anydoc / OpenDataLoader
      ↓
MinerU / Surya for difficult pages
      ↓
Normalized document representation
```

This avoids sending every page through the most expensive model.

---

# 9. Agent-skill decision matrix

| Project | Best contribution |
|---|---|
| book-to-skill | Convert books into reusable structured skills |
| Scientific Learning Skills | Tutor behavior + diagnosis |
| cheatsheet-generator-skill | Study artifact generation |
| Understand Anything | Code knowledge graph skill |
| Graphify | Deterministic graph skill |
| A11Y.md | Accessibility behavior contract |
| Awesome LLM Apps | Example implementations |
| DeepTutor | Large integrated agent platform |

---

# 10. Which projects overlap heavily?

## NotebookLM-like overlap

### Open Notebook
Most complete privacy-focused general notebook.

### DeepTutor
Much more learning/agent oriented.

### PageLM
Education-focused NotebookLM-style product.

### Memorwise
Simpler local-first NotebookLM alternative.

### SurfSense
Increasingly differentiated toward live-web agent research.

### Practical ranking by role

```text
General private notebook       → Open Notebook
Learning/tutoring platform     → DeepTutor
Education UX prototype         → PageLM
Simple local document chat     → Memorwise
Live web research agent        → SurfSense
```

---

# 11. What should NOT be combined blindly?

## Do not run multiple vector databases just because they exist

Choose one primary retrieval substrate unless benchmarking proves otherwise.

## Do not make the LLM the curriculum graph

Use explicit structured relationships for prerequisites and mastery.

## Do not use raw PDF chunks as the learner model

A chunk is an ingestion artifact, not necessarily a learning concept.

## Do not generate authoritative knowledge from Infinite Bookshelf

Generated content should be derived from verified source knowledge and carry provenance.

## Do not use OCR output without provenance

For educational material, retain:
- document ID,
- page,
- bounding box where possible,
- source passage/element ID,
- extraction confidence,
- parser/model version.

---

# 12. Recommended canonical architecture

For a serious AI-powered personal/university learning platform, the repositories suggest this architecture:

```text
                         ┌─────────────────────┐
                         │     User / UI       │
                         │ Web / Desktop / App │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Tutor / Agent     │
                         │  DeepTutor-like     │
                         └──────────┬──────────┘
                                    │
                ┌───────────────────┼────────────────────┐
                │                   │                    │
                ▼                   ▼                    ▼
          Diagnosis            Retrieval              Memory
      Scientific Skills      pgContext/Zvec       Cognee/graph
                │                   │                    │
                ▼                   ▼                    ▼
           SocraticLM        Knowledge store      Learner model
                │                   │                    │
                └───────────────────┼────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Learning Graph      │
                         │ Marble + extracted  │
                         │ course graph        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Knowledge ingestion  │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                   PDF / Office             Web
                         │                     │
                         ▼                     ▼
              pdf-inspector             SurfSense
                         │
                         ▼
                anydoc/OpenDataLoader
                         │
                         ▼
                    MinerU/Surya
                         │
                         ▼
                 Canonical document
                         │
                         ▼
              Hyper-Extract / Graphify
                         │
                         ▼
                   Blockify
                         │
                         ▼
                 Graph + retrieval
```

---

# 13. Canonical internal data model

A major lesson from this repository set is that a future system should separate **source documents**, **concepts**, **relationships**, **learning evidence**, and **learner state**.

A useful conceptual schema:

```text
Document
 ├── document_id
 ├── source_uri
 ├── title
 ├── version
 └── provenance

DocumentElement
 ├── element_id
 ├── document_id
 ├── page
 ├── bbox
 ├── type
 ├── text
 └── confidence

Concept
 ├── concept_id
 ├── canonical_name
 ├── definition
 ├── domain
 ├── evidence
 └── provenance[]

Relation
 ├── source_concept
 ├── target_concept
 ├── relation_type
 ├── strength
 └── explanation

Prerequisite
 ├── concept_id
 ├── prerequisite_id
 ├── strength
 └── reason

LearnerConceptState
 ├── learner_id
 ├── concept_id
 ├── mastery_probability
 ├── confidence
 ├── last_seen
 ├── attempts
 ├── errors
 └── next_review

Assessment
 ├── assessment_id
 ├── concept_id
 ├── difficulty
 ├── source
 ├── answer
 └── rubric

LearnerAttempt
 ├── learner_id
 ├── assessment_id
 ├── response
 ├── score
 ├── misconception
 ├── hints_used
 └── timestamp
```

This separation is more important than choosing a particular database.

---

# 14. Recommended roles for the supplied repositories

## Tier A — foundational

These deserve serious architectural consideration:

1. **DeepTutor** — integrated tutor/agent architecture.
2. **Marble Skill Taxonomy** — curriculum/prerequisite ontology.
3. **MinerU** — complex document ingestion.
4. **OpenDataLoader PDF** — structured PDF extraction.
5. **HelixDB / pgContext / Zvec** — watch-list storage candidates (no Java client / not on Neon yet); **SurrealDB removed (BSL 1.1, ADR-013)**.
6. **Cognee** — agent memory.
7. **SocraticLM** — Socratic pedagogy research.
8. **Scientific Learning Skills** — diagnosis-first tutor behavior.
9. **Hyper-Extract** — course knowledge extraction.
10. **SurfSense** — live web research.

## Tier B — highly useful product components

- Open Notebook
- PageLM
- Memorwise
- Get It.
- book-to-skill
- Graphify
- Understand Anything
- Blockify
- Surya
- pdf-inspector
- anydoc

## Tier C — specialized/adjacent

- cheatsheet-generator-skill
- pdfcn
- Infinite Bookshelf
- Student LLM Wiki
- HouseLearning
- iii
- A11Y.md
- Chat2DB
- system-design-101
- Leantime
- Awesome LLM Apps
- awesome-research

---

# 15. Suggested "best of each" stack

If forced to construct a new system from these projects rather than inventing every component:

### Knowledge ingestion
**pdf-inspector → MinerU/OpenDataLoader**

### General document support
**anydoc**

### Knowledge extraction
**Hyper-Extract**

### Curriculum ontology
**Marble Skill Taxonomy**

### Semantic compression
**Blockify**

### Graph/memory
**Cognee**

### Retrieval
**pgvector on Neon (default)**; pgContext if self-hosted; HelixDB/Zvec on the watch-list. ~~SurrealDB~~ (struck, BSL 1.1).

### Tutor orchestration
**DeepTutor-inspired architecture**

### Tutor behavior
**Scientific Learning Skills + SocraticLM principles**

### Live research
**SurfSense**

### Study UX
**Get It. + PageLM/Open Notebook patterns**

### Agent knowledge packaging
**book-to-skill**

### Study output
**cheatsheet-generator-skill + pdfcn**

### Accessibility
**A11Y.md**

### Practice
**HouseLearning-style interactive exercises**

---

# 16. Most important architectural lessons

## Lesson 1 — RAG is not a learner model

Vector similarity can retrieve:
> "What is photosynthesis?"

It does not inherently know:
> "This student can recite the definition but cannot explain the causal chain and is missing chloroplast structure as a prerequisite."

That requires an explicit learner state.

---

## Lesson 2 — Prerequisites should be first-class data

Marble's graph model is a strong example:

```text
A prerequisite for B
B prerequisite for C
```

This allows:

```text
Student fails C
     ↓
Inspect prerequisite graph
     ↓
Identify A/B weakness
     ↓
Diagnose
     ↓
Repair
     ↓
Retry C
```

This is much stronger than retrieving another chunk about C.

---

## Lesson 3 — Document parsing should be routed

Not every page deserves VLM/OCR processing.

Use:

```text
inspect → classify → cheap path or expensive path
```

The `pdf-inspector` approach is therefore architecturally valuable even if another parser ultimately performs the extraction.

---

## Lesson 4 — Knowledge units should be semantic

Blockify's IdeaBlock concept and book-to-skill's structured chapter/skill approach point toward the same principle:

> The unit retrieved by an agent should correspond to a meaningful unit of knowledge, not an arbitrary 500-token slice.

---

## Lesson 5 — Graph + vector is stronger than vector alone for learning

Vectors answer:
> "What is semantically similar?"

Graphs answer:
> "What depends on what?"

Learning requires both.

---

## Lesson 6 — Provenance is mandatory

For educational systems, every generated claim should ideally be traceable to:

```text
Source
 → document
 → page
 → element
 → extracted concept
 → generated explanation
 → assessment
```

This is especially important when OCR, LLM extraction and generated study materials are chained together.

---

# 17. Final assessment

The repositories fall into three broad generations of AI-learning architecture.

### Generation 1 — "Chat with my documents"

Examples:
- Memorwise
- Open Notebook
- PageLM

Useful, but largely retrieval-centric.

### Generation 2 — "Understand and structure my knowledge"

Examples:
- Marble Skill Taxonomy
- Hyper-Extract
- Graphify
- Blockify
- Cognee
- book-to-skill

These introduce graphs, structured knowledge, modular skills and persistent memory.

### Generation 3 — "Model how the learner learns"

Examples:
- SocraticLM
- Scientific Learning Skills
- DeepTutor
- Get It.

This is the most important direction for an actual intelligent tutor.

The strongest future architecture therefore combines all three:

```text
Documents
   ↓
Document Intelligence
   ↓
Structured Knowledge
   ↓
Curriculum / Prerequisite Graph
   ↓
Learner Model
   ↓
Diagnosis
   ↓
Socratic Teaching
   ↓
Assessment
   ↓
Mastery Update
   ↓
Spaced / Adaptive Next Step
```

That is the core architectural pattern that emerges from the complete repository set.

---

# 18. Source index

1. SocraticLM — https://github.com/Ljyustc/SocraticLM
2. Marble Skill Taxonomy — https://github.com/withmarbleapp/os-taxonomy
3. Understand Anything — https://github.com/Egonex-AI/Understand-Anything
4. DeepTutor — https://github.com/HKUDS/DeepTutor
5. Awesome LLM Apps — https://github.com/shubhamsaboo/awesome-llm-apps
6. Scientific Learning Skills — https://github.com/hwl668/Scientific-learning-skills-
7. book-to-skill — https://github.com/virgiliojr94/book-to-skill
8. PageLM — https://github.com/CaviraOSS/PageLM
9. Get It. — https://github.com/beltromatti/get-it
10. cheatsheet-generator-skill — https://github.com/Evan715823/cheatsheet-generator-skill
11. Student LLM Wiki — https://github.com/IssacW228/student-llm-wiki
12. HouseLearning — https://github.com/houselearning/home
13. Memorwise — https://github.com/robzilla1738/Memorwise
14. awesome-research — https://github.com/emptymalei/awesome-research
15. Open Notebook — https://github.com/lfnovo/open-notebook
16. OpenDataLoader PDF — https://github.com/opendataloader-project/opendataloader-pdf
17. anydoc — https://github.com/firecrawl/anydoc
18. SurfSense — https://github.com/MODSetter/SurfSense
19. SurrealDB — https://github.com/surrealdb/surrealdb
20. Unlimited-OCR — https://github.com/baidu/Unlimited-OCR
21. MinerU — https://github.com/opendatalab/mineru
22. Graphify — https://github.com/Graphify-Labs/graphify
23. Surya — https://github.com/datalab-to/surya
24. OpenKnowledge — https://github.com/inkeep/open-knowledge
25. Zvec — https://github.com/alibaba/zvec
26. zvec-ai repositories — https://github.com/orgs/zvec-ai/repositories
27. HelixDB — https://github.com/helixdb/helix-db
28. Chat2DB — https://github.com/OtterMind/Chat2DB
29. Hyper-Extract — https://github.com/yifanfeng97/Hyper-Extract
30. system-design-101 — https://github.com/ByteByteGoHq/system-design-101
31. iii — https://github.com/iii-hq/iii
32. A11Y.md — https://github.com/fecarrico/A11Y.md
33. pgContext — https://github.com/evokoa/pgcontext
34. Blockify — https://github.com/iternal-technologies-partners/blockify-agentic-data-optimization
35. pdfcn — https://github.com/shadcn-labs/pdfcn
36. Cognee — https://github.com/topoteretes/cognee
37. pdf-inspector — https://github.com/firecrawl/pdf-inspector
38. Infinite Bookshelf — https://github.com/Bklieger/infinite-bookshelf
39. Leantime — https://github.com/leantime/leantime

---

## Research-quality note

This dossier is an **architecture and implementation research synthesis**, not a source-code audit of every file in every repository. Repository pages and documentation are live projects and can change after the research date. Claims about performance, benchmark scores, or project-reported improvements should be treated as **maintainer-reported until independently reproduced**.

For production adoption, the next diligence pass should inspect:
- exact commit/tag to pin,
- dependency/SBOM,
- license of code vs model weights vs datasets,
- security advisories,
- persistence/backup behavior,
- authentication and authorization,
- data retention,
- benchmark methodology,
- failure behavior,
- observability,
- API stability,
- and test coverage.
