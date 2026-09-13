# Content Corpus Architecture — Manually Prepared Edexcel International GCSE Chemistry (Pre-Ingestion Standard)

**Status:** T-C05 design (2026-09-10, Session 25) · **Scope:** contract & architecture only — no code, no Cycle-1 changes
**Applies to:** the operator-prepared 4CH1 corpus (specification, Student Book, past papers, Save My Exams notes & questions)
**Governing spec sections:** Master Spec §6.2 (ADR-014 curriculum hierarchy), §6.4/§8 (canonical documents), §6.5/§10 (question bank, F-168), §7 (KG), ADR-017 (recommendations), ADR-018 (mock blueprints), T-C02/C03/C04 content-ops track

---

## 0. Purpose and non-negotiables

The operator is manually converting — outside SyllabAI, using ocr.z.ai plus hand-correction — an Edexcel **International GCSE Chemistry (4CH1)** corpus into Markdown. SyllabAI is NOT converting these resources and is NOT changing Cycle 1 (Edexcel IAL Chemistry, `IAL-CHEM-2018`, WCH11 seed). This document defines everything needed so the manually produced files can be imported later **without rework**: a Markdown convention the human follows now, the metadata each file must carry, the validation lifecycle the files enter, and the small set of schema extensions the corpus exposes as future work.

Design principles (all inherited, none invented):

1. **The existing spine is the spine.** The corpus flows through the already-proven path: source → canonical document (schema 1.0, `documents` V11) → structured content (`exam_papers` / `questions` / `question_versions` / `question_parts` / `mark_schemes` / `mark_points`, V8) → teacher review (SUGGESTED → VALIDATED) → servable. The corpus adds a *new ingestion adapter*, not a new pipeline.
2. **Official structure is authoritative.** Where the specification provides hierarchy, codes and wording, the system stores it verbatim (ADR-014: agents must never flatten points into tags or invent numbering). AI-created taxonomy is only ever a suggestion with provenance (§7).
3. **AI proposes; evidence and validation determine truth** — the 0-non-VALIDATED-servable rule, the SUGGESTED state, and the bridge-record pattern (T-C02) all carry over unchanged.
4. **The human's job is minimized.** Every convention below is checkable by grep or lint, GitHub-renderable, and sustainable across hundreds of files. Nothing requires the human to write JSON or invent metadata the system can derive.

---

## 1. Corpus overview — five source roles, never flattened

| Role | `role` value | Source | Function | Authority |
|---|---|---|---|---|
| A. Official specification | `specification` | Edexcel 4CH1 spec | Defines curriculum structure + SpecificationPoints | **Curriculum authority** — verbatim, never paraphrased |
| B. Student Book | `student-book` | Pearson Edexcel | Instructional content (explanations, worked examples, practicals) | Pedagogical authority *within* the spec's frame |
| C. Past papers | `past-paper` (+ paired `-ms`) | Edexcel 4CH1/1C, 4CH1/2C sessions | Assessment corpus | Assessment authority (questions + mark schemes verbatim) |
| D. SME notes | `external-notes` | Save My Exams | Supplementary explanations | Third-party explanatory material — never authoritative |
| E. SME exam questions | `external-questions` | Save My Exams | Supplementary question bank | Third-party assessment material — clearly branded, never confused with board papers |

These five roles are the **only** place role semantics live. Everything downstream (structure schema, validation axes, serving rules, tutor source labels) keys off `role`. The system never treats a Student Book paragraph, a spec point and an exam question as "the same kind of document".

---

## 2. Content source model — one spine, three structural families

**Layer 1 — SourceDocument (provenance root).** One row per logical source document (a spec edition, a book edition, one exam session paper or mark scheme, one SME page). Carries: role, provider, board/qualification/subject/curriculum_code, identifiers, edition/session, rights note, import batch, checksum. This is the *common abstraction* — and it is the **only** common abstraction. It maps onto the existing `documents` store (V11: `document_id` + `doc_version` + `kind` + `source_uri` + `checksum` + `source_engine` + `canonical_json`), which already implements idempotency (unique checksum) and stable identity (unique `document_id, doc_version`).

**Layer 2 — role-specific structural trees** (three families, not one generic tree):

| Family | Roles | Structure |
|---|---|---|
| Curriculum family | specification | Section → **SpecificationPoint** (first-class, verbatim code + wording + ordering) — materializes as KG nodes (Master Spec §7) |
| Instructional family | student-book, external-notes | Chapter → Section → Subsection (the book's/provider's own pedagogical tree), mapped many-to-many to SpecificationPoints |
| Assessment family | past-paper, external-questions | Question → QuestionPart → MarkPoint, plus shared **stimulus** blocks (passage/graph/dataset/scenario) referenced by the question and its parts |

These map to existing entities: the assessment family is exactly V8 (`question_versions` + `question_parts` + `mark_schemes` + `mark_points`, all present today); the curriculum family is exactly the `CurriculumDraftDto` → KG path (T-010, schema 1.1, with per-node provenance); the instructional family is new territory for the `documents` store (see §13 gap audit — `kind` enum extension).

**Layer 3 — validation + versioning on every servable unit.** Validation state attaches at the unit level (question version, part, scheme, section, KG node), not just the document, because a paper can be 95% clean with 2 flagged parts. This is already true in the schema (`question_versions.validation_state`, `mark_schemes.validation_state`, `knowledge_nodes.validation_status`) and stays.

**Explicitly rejected:** a single "Resource/ContentNode with a type string" model. A textbook section and an exam question validate differently, map differently, and serve differently; flattening them into one entity is exactly the failure mode ADR-014 forbids for spec points. The shared part is the *document/provenance/lifecycle* layer (Layer 1), not the content structure.

---

## 3. The Corpus Markdown Convention (CMC v1.0) — the human contract

Every corpus file = **YAML front matter + Markdown body**. The convention is deliberately boring: strict heading grammar, one marks notation, HTML sub/sup tags, plain-Unicode arrows, local `assets/` folders, HTML comments for machine flags. All of it is greppable; none of it needs tooling to produce.

### 3.1 Universal file anatomy

```text
┌─────────────────────────────────────────────┐
│ --- (YAML front matter, §3.2)              │  identity + provenance
│ ---                                         │
│ # H1  — document title (exactly once)      │  document level
│ body per role (§3.3):                      │
│   ## H2  — question | chapter | section    │  major unit
│   ### H3 — part | subsection | spec point  │  working unit
│   #### H4 — sub-part (roman i/ii, 1./2.)   │  deepest level
│ assets/ — images next to the file          │
└─────────────────────────────────────────────┘
```

Rules that hold for **every** role:

1. Exactly one `#` H1 per file, matching the front-matter `title`.
2. Heading levels mean what §3.3 says they mean — never skip levels, never use headings for emphasis.
3. **Numbering is verbatim from the source.** Never renumber questions, parts, chapters or spec points. If the paper numbers Q1–Q12, the file has `## Question 1` … `## Question 12`. If a part is printed `(b)(ii)`, the file has `#### (ii)` under `### (b)`.
4. Machine flags are HTML comments: `<!-- page: 7 -->`, `<!-- qwc -->`, `<!-- figure-missing: ... -->`, `<!-- either-or: Q8|Q9 -->`, `<!-- spec: 4CH1 1.36B -->`. They render invisibly, lint trivially, and never affect reading.
5. Mark-scheme content NEVER appears in a paper file (and vice versa). Answers live only in the paired `-ms.md` file.

### 3.2 Front matter (paste-ready templates)

**Universal required keys** (all roles): `source.role`, `source.board`, `source.qualification`, `source.subject`, `source.curriculum_code`, `source.provider`, `source.doc_id`, `source.title`, `conversion.method`, `conversion.converted_by`, `conversion.converted_date`, `conversion.conversion_status`.

Canonical value vocabulary (fixed, do not improvise):

| Key | Values |
|---|---|
| `role` | `specification` · `student-book` · `past-paper` · `mark-scheme` · `external-notes` · `external-questions` |
| `board` | `edexcel` |
| `qualification` | `international-gcse` (this corpus) · `ial` (Cycle 1) |
| `subject` | `chemistry` |
| `curriculum_code` | `4CH1-2017` (spec code + series; the DB `curriculum_versions.code` mirrors this exactly) |
| `provider` | `edexcel` · `pearson` (Student Book) · `save-my-exams` |
| `conversion.method` | `manual-ocr.z.ai` (papers currently) · `manual` (typed/retyped) |
| `conversion.conversion_status` | `draft` (raw OCR pass) · `reviewed` (human checked once) |

**Past paper (`4CH1-1C-2020-01.md`):**

```yaml
---
source:
  role: past-paper
  board: edexcel
  qualification: international-gcse
  subject: chemistry
  curriculum_code: 4CH1-2017
  provider: edexcel
  doc_id: qp-4CH1-1C-2020-01
  title: "Pearson Edexcel International GCSE Chemistry Paper 1C, January 2020"
  paper: 1C
  session: 2020-01
  variant: null
  total_marks: 110
  duration_minutes: 120
conversion:
  method: manual-ocr.z.ai
  converted_by: <operator>
  converted_date: 2026-09-10
  conversion_status: draft
  notes: ""
pages: "2-24"
---
```

**Mark scheme (`4CH1-1C-2020-01-ms.md`)** — same block with `role: mark-scheme`, `doc_id: ms-4CH1-1C-2020-01`, plus `paper_doc: qp-4CH1-1C-2020-01` (the pairing key).

**Student Book chapter (`ch05-....md`):**

```yaml
---
source:
  role: student-book
  board: edexcel
  qualification: international-gcse
  subject: chemistry
  curriculum_code: 4CH1-2017
  provider: pearson
  doc_id: sb-4CH1-ed2017-ch05
  title: "Edexcel International GCSE (9–1) Chemistry Student Book"
  edition: "2017"
  isbn: "..."                # optional but valuable
  chapter: 5
  chapter_title: "..."
conversion: { ... }
pages: "76-95"
---
```

**Specification (`spec-s1.md`, one file per spec section):**

```yaml
---
source:
  role: specification
  board: edexcel
  qualification: international-gcse
  subject: chemistry
  curriculum_code: 4CH1-2017
  provider: edexcel
  doc_id: spec-4CH1-2017-s1
  title: "Pearson Edexcel International GCSE in Chemistry (4CH1) Specification"
  issue: "..."              # verbatim issue/first-assessment info from the doc's own cover
  section: 1
conversion: { ... }
pages: "..."
---
```

**SME notes / questions:**

```yaml
---
source:
  role: external-notes        # or: external-questions
  board: edexcel
  qualification: international-gcse
  subject: chemistry
  curriculum_code: 4CH1-2017
  provider: save-my-exams
  doc_id: sme-notes-4CH1-ionic-bonding
  title: "Save My Exams — Edexcel IGCSE Chemistry — Ionic Bonding"
  provider_topic: "Ionic Bonding"   # THEIR heading, verbatim, never remapped by us
  provider_ref: "..."               # their URL/slug, optional but valuable
conversion: { ... }
---
```

Why so few keys: everything else (topic mappings, difficulty, question type, AO, skills, misconception links) is **system-derived or AI-suggested** and lives in the database with provenance — never hand-maintained in files. `conversion.conversion_status` describes the *file* (did a human check the OCR?); the *serving* lifecycle (§6) is system state and never appears in front matter. The DB `qualification` column for this corpus is the string `International GCSE` (the CMC key `international-gcse` is normalized by the converter; case-insensitive matching already exists in `PastPaperIngestionService.resolveSubject`).

### 3.3 Body grammar per role

**Past paper.** The stem rule: *everything between `## Question N` and the first `###` part is the shared stimulus* (passage, diagram, graph, dataset, scenario). No special syntax needed — the parser gets it for free from the heading grammar, and several parts sharing one stem is the normal, correct representation.

```markdown
# 4CH1/1C January 2020

## Question 3

<!-- page: 7 -->

A student investigates the rate of reaction between excess marble chips
and hydrochloric acid.

![line graph of volume of gas produced against time](assets/fig-q03-1.png)

The student repeated the experiment using the same volume of more
concentrated hydrochloric acid.

### (a)

Explain why the rate of reaction is greater with more concentrated acid.

**(2 marks)**

### (b)

Calculate the mean rate of reaction in the first 30 seconds. State your
answer in cm<sup>3</sup> min<sup>-1</sup>.

**(3 marks)**

**(Total for Question 3 = 5 marks)**
```

- Marks: end of each part as `**(N marks)**` on its own line; question total as `**(Total for Question N = M marks)**` where printed (these are the two exact forms the lint will grep).
- MCQs (4CH1/2C multiple-choice section): options are a tight list under the part heading, letters bold — `- **A** ...`. **Never** mark the correct answer in the paper file.
- EITHER/OR questions: `<!-- either-or: Q8|Q9 -->` on the line after the H2 of the first of the pair.
- Quality-of-written-communication parts: `<!-- qwc -->` at the end of the part (only where the paper itself flags it).
- Do not transcribe ruled answer lines / dotted answer spaces — omit them entirely.
- Sub-sub-parts deeper than H4 (rare): keep bold labels inline (`**(i)** …`) rather than H5.

**Mark scheme.** One file per paper, paired by `paper_doc` + filename `-ms.md`; mirrors the question structure:

```markdown
# 4CH1/1C January 2020 — Mark Scheme

## Question 3

### (a)

| Answer | Marks | Additional guidance |
|---|---|---|
| more frequent collisions (1) | 2 | allow: more collisions per second |
| more particles per unit volume (1) | | ignore: references to collision energy |

### (b)

| Answer | Marks | Additional guidance |
|---|---|---|
| (mean volume read from graph) (1) | 3 | ECF from misread graph value |
| volume ÷ 30 (1) | | accept: 1.0 cm³ min⁻¹ … |
| answer with unit (1) | | award unit mark independently |
```

- Three fixed columns: `Answer | Marks | Additional guidance` (the converter reuses the GLM-OCR parser's MS contract: marking points are split on the inline `(N)` markers, guidance lines classified by leading keyword — so keep `(N)` markers **exactly as printed** and keep the marking vocabulary verbatim: *allow / accept / ignore / reject / not accept / ECF / dependent on / or / any two from*).
- Preserve a mark point's row even when its printed marks cell is empty/rowspanned — leave the cell blank rather than guessing (same "never guess marks" rule as the parser: unknown stays unknown).
- MS files carry question totals as printed (`**Total: 5**` row or the paper's own form) — the lint cross-checks them against the paper file (§5).

**Specification.** The spec's own hierarchy becomes headings; each spec point is an H3 whose heading IS the official code, body verbatim:

```markdown
# 4CH1 Specification — Section 1: Principles of chemistry

## Section 1: Principles of chemistry

### 1.36B

Write balanced equations (full and ionic) for reactions studied in this
specification, including state symbols where appropriate.
```

- Preserve any code suffixes (`1.36B`) and any bold/letter conventions **exactly as printed** — the system stores them verbatim and never interprets them; meaning comes from the spec's own legend.
- The spec's own tables (assessment overview, practicals, mathematical skills, AO weightings) are transcribed as Markdown tables under the section they belong to — they become first-class spec metadata on ingestion, not decorative text.

**Student Book / SME notes.** The source's own pedagogical structure: `## 5.1 ...` / `### ...`, preserving explanations, definitions, worked examples, equations, tables, summary boxes (a bolded `**Summary**` run-in or a `## Summary` heading — either is fine, one per file). SME files use their own section headings verbatim under the H1.

**SME exam questions.** Grammar identical to past papers (question → parts → marks), plus `**(N marks)**` where SME states marks; answers/mark schemes SME provides go in a paired `-ms.md` file exactly like papers, with `role: mark-scheme` and `provider: save-my-exams`.

### 3.4 Chemistry notation (the anti-OCR-decay rules)

These rules exist because OCR systematically destroys chemistry notation, and because a corpus with mixed notations cannot be machine-checked. They are the single highest-value convention in this document — retrofitting notation across hundreds of files is the most expensive miss possible.

| Construct | Convention | Example | Forbidden |
|---|---|---|---|
| Subscripts | HTML `<sub>` | `H<sub>2</sub>O`, `C<sub>6</sub>H<sub>12</sub>O<sub>6</sub>` | `H₂O`, `H2O` |
| Superscripts (charges, ions, exponents) | HTML `<sup>` | `Fe<sup>2+</sup>`, `SO<sub>4</sub><sup>2-</sup>`, `mol dm<sup>-3</sup>` | `Fe²⁺`, `Fe2+`, `mol dm-3` |
| Minus sign | ASCII hyphen `-` | `Fe<sup>3-</sup>`, `-5 kJ` | en-dash `–`, em-dash `—` as minus |
| Irreversible arrow | Unicode `→` | `Zn + 2HCl → ZnCl<sub>2</sub> + H<sub>2</sub>` | `->`, `=>`, `=` |
| Reversible/equilibrium arrow | Unicode `⇌` | `N<sub>2</sub> + 3H<sub>2</sub> ⇌ 2NH<sub>3</sub>` | `<->`, `↔`, `⇄` |
| State symbols | plain `(s)(l)(g)(aq)` | `CaCO<sub>3</sub>(s)` | `(aq.)`, spacing |
| Isotope notation | `<sup>14</sup>C` (mass number as sup before symbol) | `<sup>235</sup>U` | `14C`, `U-235` (unless the source itself writes it that way — then verbatim) |
| Electron | `e<sup>-</sup>` in half-equations | `Ag<sup>+</sup> + e<sup>-</sup> → Ag` | `e-`, `ē` |
| Simple arithmetic | `×` `÷` as Unicode, decimals with `.` | `0.5 × 24 = 12` | `x`, `*` |
| Display mathematics (real derivations) | LaTeX `$$...$$` — **optional**, only where the source is genuinely mathematical | | LaTeX-everywhere |
| Units | superscripted exponents, no space inside unit | `25 cm<sup>3</sup>`, `3.0 mol dm<sup>-3</sup>` | `moldm-3`, `cm3` |
| Percent | `25%` (no space), consistent within a file | | mixed `25 %` / `25%` in one file |

Structural/skeletal formulae, reaction mechanisms, diagrams and graphs are **images, never ASCII art** (§3.5). Never "repair" a garbled formula by guessing what it should be — mark it and re-check against the PDF (`conversion.notes` is the place to record persistent doubt).

### 3.5 Assets and figures

- Every directory that contains files with images has its own `assets/` subfolder; image references are always relative (`assets/fig-q03-1.png`) — files stay movable.
- Naming: `fig-<locator>-<seq>.png` where locator is the structural unit — `fig-q03-1.png`, `fig-c05-2.png`, `fig-spec-s1-1.png`.
- Alt text is mandatory and functional — say **what kind** of thing it is ("line graph of volume of gas against time", "labelled diagram of apparatus", "periodic table extract"). Alt text drives later figure OCR (GLM-OCR on assets), retrieval chunking, and accessibility.
- When a figure could not be extracted from the source, leave an explicit marker at the exact position: `<!-- figure-missing: line graph of volume vs time -->`. Never fake, never skip silently — this mirrors the parser's `availability: unavailable-signed-url` honesty pattern from T-C02.
- Image format: keep whatever ocr.z.ai/the source exports (png/jpg); no conversion required.

### 3.6 Provenance comments (optional but valuable)

- `<!-- page: 7 -->` at each source page boundary in papers and books (enables page-level provenance for every question/section, which the canonical format already models via `page_number`).
- `<!-- spec: 4CH1 1.36B -->` **only** where the source itself states the mapping (Student Book front-matter mapping tables, SME pages that name the spec point). These are *source facts* — our own mapping guesses never go into files; they belong to the AI-suggestion/human-validation workflow in the DB (§7).

### 3.7 Explicitly forbidden in corpus files

Per-question YAML blocks or JSON in bodies · fenced-div DSLs (`:::`) · cross-file relative references other than images · "improved" wording of any official text · renumbering · answer content in paper files · AI-generated metadata (difficulty, topics, AO) hand-written into front matter · unicode sub/superscript characters · ASCII arrows.

---

## 4. Metadata contract — canonical schema per role

The front matter in §3.2 IS the file-side metadata contract. The table below fixes the canonical DB-side mapping (what the converter derives vs what it stores verbatim), so nothing is ambiguous at import time.

| Field | Past paper | Mark scheme | Spec | Student Book | SME notes | SME questions | Becomes in DB |
|---|---|---|---|---|---|---|---|
| board / qualification / subject | R | R | R | R | R | R | `exam_papers.board/qualification/subject`, `curriculum_versions` resolution, `subjects` |
| curriculum_code | R | R | R | R | R | R | `curriculum_versions.code` (e.g. `4CH1-2017`; IAL: `IAL-CHEM-2018`) |
| doc_id | R | R | R | R | R | R | `documents.document_id` + `exam_papers.*_document_id` / `question_versions.source_document_id` |
| role | R | R | R | R | R | R | `documents.kind` (extended enum, §13) |
| provider | R | R | R | R | R | R | provenance label on document + serving-source label for tutor |
| title / edition / issue / isbn | R | R | R | R | O | O | document provenance (verbatim inside `canonical_json.provenance`) |
| paper / session / variant / total_marks / duration | R | R | – | – | – | – | `exam_papers.paper_code` + `session_label` (+ unique identity `(paper_code, session_label)` — already enforced) |
| chapter / chapter_title / section | – | – | R | R | – | – | structural heading path (section provenance) |
| provider_topic / provider_ref | – | – | – | – | R | R | third-party taxonomy label — verbatim, never remapped |
| pages | O | O | O | O | O | O | `documents.page_count`; inline `<!-- page -->` → element `page_number` |
| conversion block | R | R | R | R | R | R | `documents.source_engine` (`corpus-md`), `extraction_method` (`corpus-md-v1` + `manual-ocr.z.ai`), `extracted_at`, `ingested_by`; checksum = SHA-256 of the .md file |
| marks / question numbering / MS tables | body | body | – | – | – | body | `question_versions`, `question_parts`, `mark_schemes`, `mark_points` (structure from §3.3, not front matter) |

R = required, O = optional. Fields that are **derived** (topic placement, spec mappings, difficulty, AO, skills, misconceptions, question type beyond MCQ/STRUCTURED) never appear in files — they are produced by rules or AI with provenance, and validated by humans (§7–§8).

---

## 5. OCR reliability — chemistry-specific ingestion lint vs human review

Parse success ≠ academic correctness. The ingestion lint (converter-side, deterministic, per file + per batch) separates machine-checkable risks from the ones only a human can close.

**Machine checks (hard errors — block import):**

1. Mark arithmetic: Σ part marks = question total; Σ question totals = `total_marks` (when stated) — both paper-side and MS-side.
2. Paper↔MS pairing: same question set, same part labels; per-part marks consistent between the two files (the parser's QP↔MS reconciliation, extended to file pairs).
3. Numbering continuity: `## Question N` strictly increasing, no gaps/duplicates; part letters `(a)(b)(c)…` ordered; roman `i, ii, iii` ordered.
4. Heading grammar: exactly one H1; H2/H3/H4 used per §3.3; no skipped levels.
5. Front matter schema: required keys present, enum values valid, date formats valid, `doc_id` unique in corpus, paper/MS pairing resolvable.
6. Image refs: every `assets/…` reference exists on disk; count of `![` + `figure-missing` reported per question (any question with a `figure-missing` inside or before its parts is flagged for mandatory human review of that question).
7. Table integrity: consistent column count per Markdown table.

**Machine checks (warnings — flag for review, do not block):**

8. Unicode sub/superscript characters anywhere (₂, ², ⁻ …) — must be tags (§3.4).
9. Formula-adjacent bare digits in chemistry context: `[A-Z]\d` patterns (`H2O`, `C6H12O6`, `Fe2+`, `dm-3`, `10-3`) — likely missing `<sub>/<sup>`.
10. ASCII arrows (`->`, `<->`, `=>`) or `=` between two formula-like tokens; `↔`/`⇄` used as equilibrium arrow.
11. En/em-dash adjacent to digits (minus-sign decay); `[0-9],[0-9]` (comma decimals — OCR of European layouts).
12. Equilibrium-context heuristic: `⇌` missing where surrounding text says equilibrium/reversible, or `→` present where it says reversible.
13. Isotope pattern `^\d+[A-Z]` at word start (`14C`).
14. Mixed percent/units spacing within one file.
15. Answer-key leakage scan: paper file containing `answer`, `mark scheme`-style sections; MS vocabulary (`allow:`, `reject:`, `ECF`) appearing in paper files.
16. Either/or pairs: `either-or` comment present exactly once per declared pair; both members exist.
17. Duplicate content fingerprints (normalized-text hash) within the corpus — §11.

**Human review (cannot be auto-validated — the OCR-fidelity axis of §6):** every chemical equation (species, balancing, state symbols) at least on a sampling basis with 100% for equations inside mark schemes; all numeric values inside calculations (both question data and MS answers); every question adjacent to a `figure-missing` or containing a graph/diagram (the parts' meaning depends on the image); MS guidance placement (allow/reject/ECF semantics); all spec-point wording (never auto-corrected — if OCR is suspect, retype from the PDF); definitions in book/SME notes. The file-level `conversion.conversion_status: reviewed` is the human's attestation that this pass happened; the system does not trust it blindly — it feeds the OCR-fidelity axis and prioritizes the sampling queue.

---

## 6. Validation lifecycle — pipeline stages × six validation axes

The existing truth model is kept exactly: every unit is `SUGGESTED` on import, may only serve when `VALIDATED` (0 non-VALIDATED versions serve), and `REVIEW_REQUIRED` is a *flag* the pipeline raises (the bridge record's `reconciliation_status` pattern), not a stage you wait in.

**Pipeline stages** (the user's proposed spine, mapped onto existing machinery):

```text
RAW (file registered: checksum + doc_id + provenance captured — import batch)
 → PARSED (CMC lint hard errors clean; structure extracted)
 → NORMALIZED (notation + metadata canonicalized; enums validated)
 → STRUCTURED (entities built: questions/parts/schemes, KG nodes, mappings proposed)
 → CROSS_CHECKED (mark arithmetic, QP↔MS reconciliation, dedup fingerprints, scope guards)
 → [REVIEW_REQUIRED flag] (any axis raised findings — visible on the teacher review surface)
 → VALIDATED (human sign-off per axis below)
 → SERVABLE (VALIDATED + role-specific serving prerequisites, below)
```

**The six axes** — orthogonal, separately recorded (validator kind: rule / human; validator id; evidence; date). A document can be structurally perfect (axes 1–2 green) and academically wrong (axis 3 red):

| Axis | What it certifies | Validator | Applies to |
|---|---|---|---|
| 1. Parse/structure | grammar, schema, pairing, numbering | machine (lint §5) | all roles |
| 2. OCR fidelity | transcription matches the source PDF | machine flags + human attestation | all roles |
| 3. Academic/semantic correctness | the chemistry is right (formulae balanced, values sane, guidance placement) | human | all roles |
| 4. Curriculum mapping | spec-point mappings are correct | machine-checked refs + human validation (§7) | papers, book, SME |
| 5. Question/marks & MS alignment | mark points correspond to parts; totals coherent; answer-key complete | machine arithmetic + human semantics | papers, SME questions |
| 6. Release approval | role-based human sign-off to serve this unit | human | all roles |

**Serving rules per role (SERVABLE gate, extending the existing one):**

- `QuestionPart` serves only when: its question version is VALIDATED **and** its paper's mark scheme is VALIDATED **and** it has ≥1 VALIDATED spec-point mapping. (Today's `ServableQuestionService` boundary — active + MCQ or STRUCTURED-with-VALIDATED-scheme — is exactly this shape already.)
- Specification points serve (to tutor grounding, coverage, blueprints) when the KG node is VALIDATED (existing `knowledge_nodes.validation_status`) — and spec wording is always served **from the specification**, never paraphrased from third-party notes.
- Student Book / SME sections serve to retrieval/tutor only when VALIDATED, always carrying their provider label in the evidence item (tutor must be able to say "according to your Student Book" vs "according to the specification").
- SME content additionally never feeds mock-exam blueprints as board-authoritative items without explicit reclassification (ADR-018's official-rules evidence classes).

LLM checks may attach findings and suggestions to any axis; they can never set VALIDATED on axes 2–6 (AI proposes; humans decide). Axis records are append-only (auditable), matching the research-reproducibility posture (§19).

---

## 7. Curriculum mapping — many-to-many with four provenance tiers

One mapping entity: `(content_unit, specification_point)` where content_unit ∈ {QuestionVersion, QuestionPart, ContentSection} — mapped by F-168's rules (multi-point coverage, mapping confidence, provenance, validation state; unreviewed mappings never authoritative).

| Mapper (provenance tier) | Meaning | Trust semantics |
|---|---|---|
| `PUBLISHER` / `PROVIDER` | the source itself states the mapping (book front matter, SME spec-point labels) | a *source fact* — stored, but still validated by a human before it becomes authoritative (third parties make mapping errors) |
| `AI_SUGGESTED` | LLM/rule proposes the mapping | never authoritative; carries confidence + model version (§19) |
| `RULE_DERIVED` | deterministic derivation (e.g. spec-stated `<!-- spec: -->` comments, MCQ tagged by the exam's own section) | authoritative after cross-check |
| `HUMAN_VALIDATED` | a human confirmed | authoritative |

Rules that prevent the classic failure modes:

- **Many-to-many is the default.** A textbook section spanning three spec points maps to all three; a part maps at part level (different parts of Q3 may hit different points); MCQs map at question level (single unit). A `primary` flag may order mappings for display but never truncates them.
- **A mapping never crosses curricula.** A 4CH1 question can never map to an `IAL-CHEM-2018` spec point — enforced as a hard check in the converter and at review time (this is the single most important §13 guard: because `attempts`/mastery flow through `question_topics` → KG nodes, a cross-curriculum mapping would silently contaminate learner state).
- Papers with no validated mapping can be VALIDATED (content-wise) but stay **un-servable** until mapped — mirroring today's ingestion-anchor design (pipeline never guesses placement; teachers map during review).
- Specification: no mapping needed — it *defines* the points (via the `CurriculumDraftDto` path with per-node provenance, already built in T-010).

---

## 8. Question taxonomy — source facts vs canonical vs derived vs suggested

| Class | Fields | Rules |
|---|---|---|
| **Source facts** (verbatim, immutable) | question/part text, part labels, marks, printed totals, MS text + guidance vocabulary, figures, `provider_topic`, either/or groupings | never rewritten; a correction = new version with provenance (§10) |
| **Canonical metadata** (structured, load-bearing, human-validated) | `QuestionType` (existing enum: MCQ_SINGLE / SHORT_ANSWER / STRUCTURED), `CommandWord` (controlled vocabulary — Edexcel's official command-word list), spec-point mappings (§7), structure (stem/parts/stimulus), paper identity, **difficulty *state*** (§9 — the *state* is canonical, the *value* is evidence) | used by serving decisions; changes are versioned |
| **Derived metadata** (recomputable — never hand-entered, never imported) | topic placement (from validated spec mapping → spec's own topic hierarchy), attempt counts, p-value, discrimination, response-time stats, mastery contributions | system-owned; regeneration is always safe |
| **AI-suggested → human-validated tags** | skills, misconceptions (beyond source-stated), provisional difficulty prior, AO when not officially derivable, categorical flags (calculation / practical / data-interpretation / graph / equation-writing / extended-response) | stored with provenance + status; validation promotes them; they never gate serving |

Decision on the specific list the operator asked about: **canonical** = QuestionType, CommandWord, AssessmentObjective *where officially derivable* (spec's own AO tables; else suggested), spec-point mapping, difficulty-evidence state. **Source facts** = marks, topic-as-printed, provider metadata. **Secondary tags (suggested-tier)** = calculation/practical/data/graph flags, skills, misconceptions, provisional difficulty. **Derived** = system topic (from mapping), all statistics. Nothing is deleted from this list — the tiers are what keep "fake precision" out.

---

## 9. Question difficulty — evidence-based, never LLM-truth

Philosophy already fixed by ADR-018 ("difficulty is contextual evidence") and the existing design (imported questions land `difficulty=3` as "unknown until review"). The corpus model makes that explicit:

```text
DifficultyEvidence (per question part, per CurriculumVersion population, per cohort window):
  attempts_n, mean_mark_proportion (p̂), discrimination (point-biserial),
  median_response_time, sample_state, computed_at, window
DifficultyState: UNEVIDENCED → PROVISIONAL → EMERGING (n < min_n) → EVIDENCED (n ≥ min_n) → STALE
```

- **UNEVIDENCED** at import — the honest default; the existing INT `difficulty` column is reinterpreted as the *provisional prior* (3 = unknown), which is already today's behavior; no migration forced by this contract.
- **PROVISIONAL** = an explicit, labeled prior only: deterministic heuristic blend (marks, command word, AO, calculation flag) with named weights, plus optionally an LLM estimate recorded as one low-weight signal with model version — never the sole source, never displayed as "difficulty: hard".
- **EVIDENCED** = empirical: p̂, discrimination, sample size, response time, learner population — computed **per CurriculumVersion population** (IGCSE and IAL statistics never pool; a 4CH1 cohort's p-value on a question is meaningless for an IAL learner's adaptive decisions).
- Serving policy: recommendations and mock blueprints weight by evidence state (never by prior alone); new questions get a bounded exploration share precisely to *acquire* evidence — that is how the corpus questions graduate from prior to truth.
- Raw aggregates are stored separately from any calibrated ability-scale difficulty (IRT/Elo) — the calibrated layer is the existing learner-model domain and stays untouched by this contract.

---

## 10. Provenance & versioning — "where exactly did this come from?"

The chain already exists in pieces; the corpus contract makes it end-to-end answerable:

```text
SourceDocument (documents row: provider, title, edition/issue, paper+session, doc_id,
                checksum, source_uri = corpus file path, source_engine = corpus-md,
                extraction_method = corpus-md-v1 + manual-ocr.z.ai, ingested_by, extracted_at)
  → canonical_json.provenance (front matter verbatim: conversion block, pages, provider refs)
  → structured units (question_versions.source_document_id, mark_schemes.source_document_id,
                      KG node provenance strings — already column-backed)
  → SourceLocator (document_id + page + structural path "Question 3/(a)" — page from `<!-- page -->` markers)
  → ValidationRecord trail (§6 axes: who/what/when)
```

- **Corrections without losing lineage:** an edit creates a new `doc_version` of the document and a new `question_version` (V8's immutable snapshots) superseding the old; provenance points at the *SourceDocument*, which never changes — so fixing an OCR typo preserves the entire source chain. Old versions are retained (research reproducibility §19: an attempt in a past study must resolve to the exact content version the learner saw).
- **AI-generated content** (future worked solutions, remediation snippets) is stored as derived content with its own provenance (`generated_by` model version) and is never merged into source content — the tutor's evidence items already separate document evidence from generated answers.
- Import batches record operator, method, date, file list, lint results — the batch is the unit of human review (matches T-C03's controlled-batch discipline: one bounded batch, one audit, one decision).

---

## 11. Deduplication — five distinct concepts, never auto-deleted

| Concept | Definition | Detection | Action |
|---|---|---|---|
| Same source object | the same underlying document (same paper code + session + variant) | import-time identity: `doc_id`, `exam_papers (paper_code, session_label)` unique index, checksum | resolves to the same entity — re-import is idempotent (already enforced by V11/V8) |
| Duplicate representation | two files/imports of the same source object (e.g. re-OCR after fixing a file) | same `doc_id` (or same normalized fingerprint) | new `doc_version` of the same document; the older version is superseded, never deleted; only one version serves |
| Similar content | Student Book §5.1 and SME "Ionic Bonding" explain the same spec points | shared spec-point mappings / similarity candidates | both retained — they are *different sources with different pedagogical value*; linked as related content for retrieval diversity |
| Variant question | same stem with changed values (SME exam-style question modeled on a real past-paper question; repeated stems across sessions) | normalized-text fingerprint (whitespace/notation-normalized hash), then fuzzy candidates | linked `variant_of` + variant type (numeric / reworded / same-concept); serving dedupes exposure (a mock never shows a question and its variant together); recommendation dedupes per session |
| Related content | connected via shared spec points / skills | graph query (existing KG edges `RELATED_TO`, `EXPLAINED_BY`) | feeds recommendations/tutor |

Detection is machine (hashes, fingerprints); **classification is human** (AI may propose the relation type). Deletion or merge happens only through an explicit human decision that preserves both provenances. The existing `documents` checksum-uniqueness already gives "duplicate representation" detection for free; question-level identity comes from `questions.external_ref` = `{doc_id}#Q{n}` (e.g. `qp-4CH1-1C-2020-01#Q3`) — the converter must set this consistently, which also blocks double-import of the same paper's questions.

---

## 12. Corpus repository organization

**A fourth repo: `syllabai-corpus` (private).** *(Amended 2026-09-13: the corpus repo was in fact created as **`syllabai-resources`** (public) — this section's paths describe that repo's layout; `syllabai-corpus` never existed. The assumed-private posture also needs re-validation — see the visibility correction in `KNOWLEDGE_GRAPH_BUILD_PLAN.md`.)* Rationale: content volume and access control (publisher/SME copyright) differ from code repos; review cadence is per-batch; ingestion treats it as a data source. Structure (path = human convenience; **front matter is the truth** — the converter never derives identity from paths, so files can be moved):

```text
syllabai-corpus/
  _templates/                    # paste-ready front matter per role (from §3.2)
  edexcel/
    international-gcse/          # qualification family
      chemistry/                 # subject
        4CH1-2017/               # curriculum code = version root
          specification/
            spec-s1.md  spec-s2.md  ... (assets/ where needed)
          student-book/
            ed2017/
              ch01-intro.md ... ch05-....md   assets/
          past-papers/
            2020-01/
              4CH1-1C-2020-01.md
              4CH1-1C-2020-01-ms.md
              assets/
            2020-06/
              4CH1-2C-2020-06.md  ...
          save-my-exams/
            notes/
              ionic-bonding.md  ...  assets/
            questions/
              ionic-bonding.md  ionic-bonding-ms.md  assets/
```

Scales without chemistry hardcoding: `edexcel/ial/chemistry/IAL-CHEM-2018/…`, `edexcel/international-gcse/physics/4PH1-2017/…`, other boards by name. File naming: papers `{spec-code}{paper}-{session}.md` (+ `-ms`), book `ch{NN}-{slug}.md`, spec `spec-s{N}.md`, SME `{topic-slug}.md` (+ `-ms`). One file per paper (10–14 questions is a manageable unit), one file per book chapter, one file per spec section, one file per SME topic page.

---

## 13. Relationship to existing SyllabAI systems — gap audit

What the 4CH1 corpus reveals, system by system (✓ = architecture already supports it; ⚠ = real gap registered as future work):

| System | Verdict | Detail |
|---|---|---|
| Subject Architecture (§6.2, ADR-014) | ✓ | `curriculum_versions` (board/qualification/code/title/status) takes a `4CH1-2017` row with no changes; both qualifications coexist as siblings. The `CurriculumDraftDto` path (T-010) already ingests spec → KG with per-node provenance |
| SpecificationPoint (§7) | ⚠ | Conceptually first-class in the spec, but V2's `node_type` CHECK has no `SPEC_POINT` value and seed granularity stops at SUBTOPIC. Registered as **T-C06**: extend node type + namespaced codes (`4CH1-1.36B`) |
| Spec-point mapping (F-168) | ⚠ | `question_topics` (question_id, node_id, is_primary) lacks mapper/provenance/validation/confidence columns. Registered in **T-C06** |
| Exam Content (V8) | ✓ (+1 gap) | Question/QuestionVersion/QuestionPart/MarkScheme/MarkPoint all exist and match the corpus structure; `exam_papers` identity `(paper_code, session_label)` is exactly the corpus's paper identity. Gap: shared stimulus/figures are not attached to question versions (stem text only) — AssessmentBlock is designed (ADR-018 F-171/172) but not materialized |
| `documents.kind` (V11) | ⚠ | Enum is QUESTION_PAPER / MARK_SCHEME / SYLLABUS / OTHER — needs `TEXTBOOK`, `EXTERNAL_NOTES`, `EXTERNAL_QUESTIONS` (T-C06) |
| `questions.provenance` | ⚠ | PAST_PAPER / TEACHER_AUTHORED / SEED_DEMO — needs `EXTERNAL_BANK` for SME questions (T-C06) |
| Question Attempt & Learning Evidence | ✓ | Isolation is structural (mastery flows question → topic node → one curriculum's tree) provided the §7 no-cross-curriculum-mapping rule is enforced |
| Smart Mark | ✓ | `mark_points.acceptance_criteria` JSONB + the parser's structured MS vocabulary (allow/ignore/reject/ECF/alternatives/anyTwoFrom) is exactly what CMC MS files preserve; Smart Mark consumes VALIDATED schemes only (already the κ-gated design) |
| Mock Exam Generator (ADR-018) | ✓ | Blueprint scoping Board→…→CurriculumVersion→PaperCode→BlueprintVersion is definitionally qualification-isolated; corpus supplies validated candidates + spec points for coverage; difficulty from §9's evidence states |
| Recommendation (ADR-017) | ✓ | Candidate pools are topic/mastery-scoped (hence curriculum-scoped); §9's per-population statistics preserve that |
| Tutor / grounded retrieval | **⚠ — the important one** | `ContentRetrievalService.search(query, kind, limit)` has **no curriculum/subject scope**, and `ContentVectorRetriever` is kind-agnostic by design. Harmless today (only the seed curriculum serves; GLM-OCR corpus is quarantined + unembedded), but with an ingested IGCSE corpus an IAL learner's tutor could ground on 4CH1 chunks. Registered as **T-C07**: scope documents/chunks + the vector query path by the learner's active CurriculumVersion — a hard prerequisite before corpus embeddings are switched on |
| Knowledge Graph | ✓ (+ discipline) | Node `code` is globally unique (V2) and the IAL seed uses bare `CHM` for the subject root — all 4CH1 node codes MUST be namespaced (`4CH1-*`), which the spec-draft ingestion must generate deterministically |
| Content validation/servability | ✓ | Tri-state SUGGESTED/VALIDATED/REJECTED + bridge `REVIEW_REQUIRED` pattern + `ServableQuestionService` boundary — the §6 lifecycle is a refinement of exactly this machinery, not a replacement |
| GLM-OCR ingestion (T-C01–C04) | ✓ | Same spine: the CMC converter is a new ingestion adapter registering `extraction_method = corpus-md-v1` (manual provenance preserved). Bonus: the manually corrected corpus doubles as a **golden labeled set** for evaluating automated GLM-OCR extraction fidelity later (research value) |
| Research telemetry | ✓ | `attempts` provenance + `question_versions.source_document_id` give content-version traceability; events referencing content should carry the version ids they served (T-C07-era detail) |

The honest summary: the assessment family and the validation machinery are already corpus-grade (built during T-C02/C03 with real WPH11/4CH0 fixtures); the genuine deltas are (a) the instructional family (documents.kind + SME/textbook serving labels), (b) SpecificationPoint materialization + mapping provenance, (c) the tutor retrieval scoping guard, and (d) evidence-based difficulty states. None block the manual conversion work — they are all post-corpus implementation tasks.

---

## 14. IAL ↔ IGCSE coexistence — contamination audit

Cycle 1 stays untouched (IAL-CHEM-2018, WCH11 seed, V7 MCQ bank). 4CH1 enters as a sibling CurriculumVersion. `Board → Qualification → Subject → CurriculumVersion` is sufficient for isolation **if** the following six guards hold:

| Contamination vector | Guard |
|---|---|
| Tutor grounding against the wrong syllabus | (1) KG traversal starts at the learner's enrolled subject root (existing behavior via topic nodes); (2) **T-C07**: vector retrieval filters by the learner's active CurriculumVersion — index-time and query-time (double guard) |
| Question mixing in practice/mock | question pools resolve through topic nodes inside one curriculum's tree; serving gate requires ≥1 validated mapping; cross-curriculum mapping is a hard error (§7) |
| Recommendation contamination | NBA traverses mastery on nodes of the enrolled curriculum; candidate pools inherit the same scoping |
| Learner state associations | enrollment key = (learner, curriculum_version); mastery/misconception states live on nodes inside one tree — never key anything on `subject` alone (subject `code` is per-curriculum-version in V2, already correct) |
| Difficulty pooling | statistics computed per CurriculumVersion population (§9); never pooled across qualifications |
| Retrieval index contamination | embeddings are chunk-scoped; T-C03's "no implicit embedding" rule stays until T-C07 lands; spec-point code uniqueness is *within* CurriculumVersion (never a global key) |

Plus the KG discipline: globally-unique node codes mean 4CH1 nodes are namespaced `4CH1-*` (and future IAL additions continue `WCH11-*`-style) — collision-free by construction. And the qualification string itself: `International GCSE` vs `IAL` in `curriculum_versions.qualification` / `exam_papers.qualification` (case-insensitive match already in the ingestion path).

---

## 15. Pre-Ingestion Standard — what to standardize NOW

### MUST STANDARDIZE NOW (retrofitting = touching every file)

1. **CMC front matter (§3.2)** with the fixed key set + value vocabulary — pasting metadata into 300 files later is the single most expensive possible miss.
2. **doc_id scheme + file naming + paper↔MS pairing** (`qp-…` / `ms-…` / `-ms.md` suffix / `paper_doc` key).
3. **Heading grammar** (§3.1/§3.3): H1 document · H2 question/chapter/section · H3 part/spec point · H4 sub-part; numbering always verbatim.
4. **Marks notation**: `**(N marks)**` per part and `**(Total for Question N = M marks)**` — the two exact forms.
5. **Chemistry notation (§3.4)**: `<sub>`/`<sup>` tags, `→`/`⇌` literals, ASCII minus, superscripted unit exponents; no unicode sub/sup characters, no ASCII arrows.
6. **assets/ local to each folder + `fig-<locator>-<seq>` naming + mandatory descriptive alt text + `<!-- figure-missing: ... -->` markers**.
7. **Never mix answers into paper files** (and MS vocabulary only in `-ms` files).
8. **conversion block** (method / converted_by / date / status) — cheap now, irreplaceable provenance later.
9. **MS table convention** (§3.3): `Answer | Marks | Additional guidance`, inline `(N)` markers preserved verbatim, marking vocabulary never paraphrased.

### SHOULD STANDARDIZE SOON (consistency; fixable in a later pass)

10. `<!-- page: N -->` markers at page boundaries (papers, book, spec).
11. `<!-- qwc -->`, `<!-- either-or: Q8|Q9 -->` flags.
12. `provider_topic` captured verbatim on every SME file.
13. `<!-- spec: 4CH1 1.36B -->` comments **only** where the source itself states a mapping; book front-matter mapping tables transcribed once per edition.
14. Habit: re-check mark sums while converting (the lint will audit later; catching at conversion time is cheapest).

### CAN EVOLVE LATER (add once the corpus exists)

15. AI-suggested mapping format, skills/misconception vocabularies (DB-side — files never carry them).
16. Corpus-level lint tooling / CI / `_templates` maintenance discipline; a `_meta/` source register if the repo grows beyond browsing comfort.
17. Figure enrichment (GLM-OCR over assets), spec-file splitting granularity decisions.
18. SME question-set grouping metadata (sets, difficulty bands SME prints).

### DO NOT OVER-ENGINEER YET (explicitly wait)

19. No per-question YAML/JSON in bodies, no custom DSLs, no fenced-div syntax.
20. No LaTeX mandate (plain text + tags is sufficient at IGCSE level); no SMILES/molecular formats — structures are images.
21. No re-formatting or "improving" official wording; no self-invented remapping of spec points; no renumbering.
22. No ingestion/validation **pipeline code** until a starter tranche (~20 files across roles) exercises the convention — the converter is deliberately a later task (T-C06), informed by the T-C04 human-validation verdict.
23. No scaffolding for other subjects/boards beyond the directory pattern; no corpus tooling before corpus content.

---

## 16. Roadmap (registered, parked — no Cycle-1 impact)

- **T-C05 (this document)** — done: contract + architecture for the manually prepared corpus.
- **T-C06 (parked)**: CMC → canonical converter + corpus lint (syllabai-parser adapter + core ingestion endpoint); `documents.kind` + `questions.provenance` enum extensions; `SPEC_POINT` node type with namespaced codes; F-168 mapping-provenance columns; stimulus/figure attachment design. Prerequisite: starter tranche of corpus files + T-C04 verdict.
- **T-C07 (registered, pre-embedding prerequisite)**: curriculum-scoped retrieval for the tutor evidence path (documents/chunks scope + query filter + evidence source labels for provider distinction).
- **T-C08 (future)**: evidence-based difficulty states (§9) wired into serving policies; per-population statistic jobs.

**Acceptance reminder for any future implementation:** every corpus import starts SUGGESTED; nothing serves without human VALIDATED; nothing is deleted on import; provenance survives every correction; AI-suggested anything is labeled as such. AI proposes; evidence and validation determine truth.




