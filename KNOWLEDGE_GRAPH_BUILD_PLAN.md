# Knowledge Graph Build Plan — 4CH1 Academic Graph (T-C09 / T-C10 / T-C11)

**Status:** assessment + execution plan. No code yet; Cycle 1 (IAL) scope untouched.
**Date:** 2026-09-10 (Session 27)
**Input assessed:** the operator-forwarded external proposal ("specification = canonical curriculum skeleton, revision notes = instructional enrichment layer, four build phases").
**Relationship to existing docs:** this plan *executes* the contracts already fixed in `CONTENT_CORPUS_ARCHITECTURE.md` (CMC v1.0; §7 four-tier mapping provenance; §8 taxonomy tiers; §13/§14 coexistence guards). DB wiring rides the parked **T-C06** converter. Nothing here replaces that architecture — it sequences it.

---

## 0. Purpose and non-negotiables

Build the academic knowledge graph for Edexcel International GCSE Chemistry (4CH1, Issue 3) so that **mastery, misconceptions, and next-best-action serve a real curriculum structure**, not a graph-shaped visualization of documents.

Non-negotiables carried over unchanged:

1. The specification **defines** the points; every other source (SME notes, Student Book, questions) only **maps to** them — many-to-many, never reorganizing the syllabus.
2. Every node and edge carries **provenance** (one of the four §7 tiers) and a validation state; nothing AI-extracted is ever authoritative.
3. No cross-curriculum edges, ever (`4CH1-*` codes only; the 4CH0 fixture and `IAL-CHEM-2018` are hard-separated by the converter and by validator checks).
4. All corpus-derived artifacts that quote copyrighted text live in the **private** `syllabai-resources` repo; this repo carries structure, schemas, and counts only.
5. Cycle 1 serving is untouched until T-C06 + T-C04 unlock; until then the graph is built and validated as **graph-as-code** in the resources repo.

---

## 1. Verdict on the external proposal

The proposal is directionally sound and independently converges on architecture we already fixed in Session 25 — which is good validation. As an *execution* plan it is ~half redundant with our contracts and underspecified exactly where the risk lives. Adopt the skeleton, amend the assumptions:

| Proposal claim | Verdict | Grounding |
|---|---|---|
| Spec = canonical skeleton; revision notes = enrichment layer | **ADOPT — already ours** | Source-role model (§1 of the corpus architecture) + §7; spec wording is always served from the specification, never paraphrased from notes |
| Many-to-many note ↔ spec-point mapping | **ADOPT — already §7** | Default in the contract; a `primary` flag may order mappings for display but never truncates them |
| "Don't let revision notes define the syllabus" | **ADOPT** | Matches the contamination-guard philosophy; SME note ordering/wording never becomes curriculum structure |
| Phase order: skeleton → mapping → concepts → assessment | **ADOPT, amended** | Phases 1–3 can start now; Phase 4 is corpus-blocked (no past-paper corpus exists yet) |
| `prerequisite_of` edges as extractable facts | **AMEND — hardest edges, not free** | No 4CH1 source declares prerequisites; they enter as `AI_SUGGESTED` with evidence quotes and are promoted to `HUMAN_VALIDATED` only on review (the serving side — recursive-CTE prerequisite closure — already exists in core) |
| "We have enough corpus material to start designing this mapping now" | **TRUE for Phases 1–3 only** | Spec md + 112 SME notes are in hand; the assessment graph needs past papers we have not yet converted/ingested (the 11 SME topic-question pages are a seed, not a bank) |
| Learner-lens overlay (mastery / misconception / evidence / NBA) | **ALREADY LIVE** | BKT/BDT/Ebbinghaus engines, misconception evidence loop, NBA endpoints, and the personalized KG read model are running in production today; the graph populates them, it does not rebuild them |
| Example: "SpecPoint 3.4 → concepts moles, molar mass" | **Factually off** | In 4CH1 the mole family is Section 1 (1.26–1.35C), not 3.4 — a small but perfect demonstration of why the graph is built by **parsing the real spec**, never by trusting (or hand-writing) examples |
| (unstated) trust/provenance model for extracted edges | **Gap we already own** | Four tiers: `PUBLISHER/PROVIDER · AI_SUGGESTED · RULE_DERIVED · HUMAN_VALIDATED`, plus evidence quotes + confidence + model version on every AI-suggested unit |
| (unstated) where the graph lives, who reviews it, how it serves | **This plan, §10** | Graph-as-code in the private resources repo; git PR = the human validation gate; compiler + serving ride T-C06 |

**Net:** the ChatGPT message is a good external cross-check of the *shape*; the *epistemics* (who says so, at what trust tier, with what evidence) and the *corpus-blocked sequencing* are what our plan adds.

---

## 2. What already exists — build on it, not beside it

### Corpus (syllabai-resources, private)

| Asset | State | Graph role |
|---|---|---|
| 4CH1 Issue 3 spec md (1159 lines, `status: raw_ocr`) | Backbone intact; notation degraded (CJK leak, lost sub/superscripts, full-width punctuation); **45 HTML tables, 167 unique spec codes** (S1: 60, S2: 46, S3: 22, S4: 39; 40 C-points; zero duplicate codes), 12 practicals, Appendix 5 command words | Phase 1 source |
| 112 SME revision notes (Save My Exams clippings) | 244/247 image refs repaired; canonical source URLs embed spec-aligned slugs (e.g. `…/1-5-3-moles-mass-and-rfm/`); 14 notes carry "Test yourself" links → 11 distinct topic-question pages | Phase 2 source + Phase 4 seed |
| Student Book, 383-page 1-up image-only | OCR path decided (Unlimited-OCR, pilot STRONG YES, driver + runbook shipped); full run pending (rented GPU, ~30–60 min) | Phase 3 enrichment with page-level provenance |
| 3 genuinely missing note images | Awaiting operator re-clip | Cosmetic, non-blocking |

### Core machinery (syllabai-core, live)

| Existing capability | Reuse in this plan |
|---|---|
| `curriculum_versions` + `CurriculumDraftDto` path (T-010, schema 1.1, per-node provenance) | The spec skeleton ingests through this exact path — **no new ingestion surface** |
| `knowledge_nodes` with `validation_status` | Node validation states; needs the registered T-C06 `SPEC_POINT` node-type + namespaced codes (`4CH1-…`) |
| Recursive-CTE prerequisite closure | Serves validated `PREREQ_OF` edges the day they are promoted |
| Misconception nodes + read path (MISCONCEPTION_OF flow) | Phase 3 misconception nodes land in an existing, verified serving family |
| BKT/BDT/Ebbinghaus + evidence contract + NBA | The learner lens — already in production for IAL; graph populates the IGCSE instance |
| SUGGESTED→VALIDATED workflow + κ-gated human decisions | The review machinery graph edges flow through |

---

## 3. Target graph shape

Nodes (all codes namespaced `4CH1-*`; `knowledge_nodes.code` is globally unique):

| Node | Code shape | Source of truth | Provenance |
|---|---|---|---|
| `SPEC_POINT` | `4CH1-1.26`, `4CH1-1.34C`, `4CH1-4.49C` | parsed from the spec md (verbatim statement text kept in the private repo; anchor = md line + table index) | `RULE_DERIVED` (deterministic parse), cross-checked against the PDF |
| `TOPIC` / `SUBTOPIC` | `4CH1-S1`, `4CH1-S1-E` | spec section/subsection headers (table header rows like `(e) Chemical formulae, equations and calculations`) | `RULE_DERIVED` |
| `COMMAND_WORD` | `4CH1-CW-CALCULATE` | Appendix 5 command-word list | `RULE_DERIVED` |
| `PRACTICAL` | `4CH1-PR-MGOXIDE` | the 12 spec practicals | `RULE_DERIVED` |
| `CONCEPT` | `4CH1-C-MOLE`, `4CH1-C-MOLAR-VOLUME` | extracted (LLM + rules) from spec statements + notes; canonical name + alias list + split-first identity policy (§7) | `AI_SUGGESTED` → `HUMAN_VALIDATED` |
| `MISCONCEPTION` | `4CH1-MIS-…` | SME note text or question distractors — **source quote mandatory** | `AI_SUGGESTED` → `HUMAN_VALIDATED` |
| `SKILL` | `4CH1-SK-…` | leading verbs of spec statements (know/understand/calculate/draw/explain…) + Appendix 5 + practicals | `RULE_DERIVED` skeleton, `AI_SUGGESTED` refinement |

Edges (every edge: `type`, `provenance tier`, `confidence`, `evidence quote + anchor`, `validation state`):

| Edge | From → To | Notes |
|---|---|---|
| `CONTAINS` (ordered) | TOPIC → SUBTOPIC → SPEC_POINT | deterministic; ordering = spec's own print order |
| `COVERS` | SPEC_POINT ↔ CONCEPT | many-to-many; the anchor edge of the whole graph |
| `PREREQ_OF` | CONCEPT → CONCEPT | lifecycle: `AI_SUGGESTED` (never served) → `HUMAN_VALIDATED` (serves through the existing CTE closure) |
| `RELATED_TO` | CONCEPT ↔ CONCEPT | suggested-tier only unless human-confirmed |
| `EXPLAINED_BY` | SPEC_POINT/CONCEPT → ContentSection (note or book page) | Phase 2 (notes) + Phase 3 (book pages, page-level provenance) |
| `MISCONCEPTION_OF` | MISCONCEPTION → CONCEPT | existing serving family |
| `ASSESSED_BY` | SPEC_POINT/CONCEPT → QuestionPart | Phase 4; rides F-168 mapping provenance |

---

## 4. Phase 0 — readiness gates (already in flight, no new work)

1. **Spec notation lint pilot** — the lint owns the documented damage classes (CJK leak, `CO32-` → `CO₃²⁻`, `mol/dm3` → `mol/dm³`, full-width punctuation); mechanical fixes applied by script with auditable diffs, ambiguous cases flagged for human review. Never hand-edited.
2. **Student Book full run** — per `BOOK_OCR_RUNBOOK.md` (rented GPU + official vLLM image recommended; driver is resumable). Produces 383 CMC pages with chapter map + page anchors.
3. **Operator re-clips the 3 missing note images.**

Gates: lint report with ≥95% of damage instances classified fixable/unfixable; book manifest 100% pages (or explicit failure list); these are *parallel* — Phase 1 does not wait for the book.

---

## 5. Phase 1 — specification skeleton graph (T-C09) — READY TO START

**Deterministic, zero-LLM.** A parser (`scripts/c09_spec_graph_extract.py`, resources repo) over the real md structure:

- 45 HTML tables, classified: spec-statement tables vs. AO grids vs. appendix tables vs. front-matter tables.
- Two row shapes: `<td>1.25</td><td>statement</td>` (128 rows) and `<td colspan="2">1.34C statement</td>` (39 rows) — both must parse, plus subsection header rows (`(e) Chemical formulae…`) and "Students should:" markers.
- Appendices: 12 practicals, Appendix 5 command words, AO tables, the 29-subsection topic tree.
- Output: `graph/spec_points.yaml` + `graph/topics.yaml` (graph-as-code, CMC front matter, per-node provenance: spec issue, md line anchor, table index), plus a **completeness report** and a **spot-check sheet** (20 random statements vs. the PDF) for the operator.

Acceptance gates (hard):

- Exactly **167 unique codes** (60/46/22/39 per section; 40 C-points), zero duplicates, zero orphans (every code under a subsection).
- 100% of the 12 practicals + the full Appendix 5 command-word list extracted.
- Spot-check pass: every sampled statement text matches the PDF semantically (notation damage documented, not silently "fixed" by the parser).
- Statement-leading verbs extracted → draft `SKILL` tags (deterministic tier).

DB wiring (ingest via `CurriculumDraftDto` → `SPEC_POINT` nodes) rides T-C06 and needs no new design — it was already built and proven in T-010.

---

## 6. Phase 2 — revision-note mapping (T-C10) — after Phase 1

Map each of the **112 SME notes** to spec points, many-to-many:

1. **PROVIDER signal (free):** the notes' source URLs embed SME's own spec-aligned slugs (`…/1-5-3-moles-mass-and-rfm/`) → a first-cut section-level mapping (stored as a source fact; still needs human confirmation — third parties make mapping errors).
2. **AI_SUGGESTED candidates:** LLM proposes point-level mappings with an evidence quote from the note + confidence + model version. Nothing authoritative.
3. **Human validation via PR:** mapping lands in the note's front matter (`spec_points: [4CH1-1.26, 4CH1-1.27]` + per-mapping provenance); git review is the validation gate — the workflow the operator already runs.
4. **Coverage report:** which of the 167 points have **zero** notes → the explicit enrichment queue handed to Phase 3 (Student Book) and, later, question mapping.

Acceptance gates: every note ≥1 validated mapping; coverage report generated; no note maps to points outside 4CH1.

---

## 7. Phase 3 — concept graph (T-C11) — after Phase 2

Concepts, prerequisites, misconceptions — the enrichment layer:

- **Concept identity (the real design risk):** split-first policy — extract narrowly (e.g. `MOLE`, `MOLAR_VOLUME`, `RELATIVE_FORMULA_MASS` as separate nodes even though notes use them interchangeably); alias tables record synonyms; merges happen only on human review. Over-splitting is recoverable; over-merging quietly corrupts mastery attribution.
- **Prerequisite lifecycle:** `AI_SUGGESTED` edges with evidence quotes (from spec ordering hints and note structure) → human promotion → served by the existing recursive-CTE closure. Never fabricated wholesale: if evidence is weak, the edge is not proposed at all.
- **Misconceptions:** each node carries a source quote (SME note text or question distractor); the phase-4 seed (11 topic-question pages) is a rich distractor source.
- **Student Book enrichment (after the full OCR run):** `EXPLAINED_BY` edges from concepts/spec points to book pages, page-level provenance, chapter map already built into the driver's CMC front matter.

Acceptance gates: no orphan concepts (every concept `COVERS`-anchored to ≥1 spec point); every edge carries provenance + evidence anchor; 100% of misconception nodes source-quoted.

---

## 8. Phase 4 — assessment graph (rides T-C06; corpus-blocked)

Blocked on past-paper material (none converted yet) and the T-C04 verdict — **not started by this plan**. Seeded when it opens:

- The 11 SME topic-question pages are the seed tranche (Role E ingestion map, already identified).
- Question-part → spec-point mapping runs under F-168's four-tier provenance at part level; MCQs map at question level — all already contracted in §7.
- **4CH0 guard:** the canonical 4CH0 Jan 2012 fixture is a *different spec* — the no-cross-curriculum check must reject any 4CH0→4CH1 mapping attempt loudly.
- Copyright stance: verbatim paper text stays in the private repo; the serving layer uses structure + mapping + short evidence quotes.

---

## 9. Learner lens — already live; per-phase deltas

| Phase | Learner-visible change (post T-C06 ingest) |
|---|---|
| 1 | Tutor grounding + coverage surfaces can cite real 4CH1 points (today IGCSE has none in the DB) |
| 2 | Notes become grounded evidence sources (needs T-C07 curriculum-scoped retrieval — registered, mandatory before embeddings) |
| 3 | Mastery maps to concepts; prerequisite closure + misconception watch work on real IGCSE structure |
| 4 | Evidence → mastery → NBA loop fully populated for 4CH1 |

---

## 10. Storage, review workflow, compiler

- **Source of truth:** `graph/` directory in the *private* `syllabai-resources` repo — versioned YAML with CMC front matter, one file per node family + edges, every unit carrying provenance + validation state. Git history = the audit trail; PR review = the human validation gate (the operator's existing workflow).
- **Validator now, compiler later:** `scripts/graph_check.py` runs in the resources repo **immediately** (schema conformance, code namespace = `4CH1-*` only, no cross-curriculum references, provenance completeness, phase gates) — no core changes needed. The **T-C06 converter** later compiles the same files through the canonical contracts into Postgres.
- **Serving** stays exactly the existing core surfaces; no Neo4j, no new graph store — Postgres + the existing KG machinery. (Explicit anti-goal: infrastructure novelty for its own sake.)

---

## 11. Risks & mitigations

| Risk | Mitigation |
|---|---|
| LLM-hallucinated edges become "curriculum" | Four-tier provenance; AI_SUGGESTED never authoritative; evidence quotes mandatory; validator rejects unprovenanced edges |
| Concept identity chaos (mole vs molar mass vs Mr) | Split-first + alias table + human-merged only; canonical names from spec wording |
| Cross-curriculum contamination (4CH0 / IAL into 4CH1) | Namespaced codes + hard validator check + converter guard (§14 of the corpus architecture) |
| Prerequisite edges invented wholesale | No-source rule: an edge without an evidence anchor is not proposed; promotion is human-only |
| Copyright exposure | All verbatim text in the private repo; this repo holds structure/counts; serving quotes stay short + provenance-labeled |
| OCR residual damage leaking into statements | Phase 1 parser preserves text as-is + flags damage (lint-owned); never silently corrected |
| Scope creep into "graph visualization" vanity | Anti-goal §13; the graph exists to power mastery/NBA, not pictures |

---

## 12. Sequencing & immediate next actions

Unchanged operator-critical path first: **T-036 close-out (teacher account + human six-tab browser E2E)** — this plan does not touch it and runs in parallel.

1. **Now (agent, next session):** build Phase 1 — `c09_spec_graph_extract.py` + `graph_check.py` in the resources repo; produce `spec_points.yaml` + completeness + spot-check report.
2. **Now (operator):** T-036 close-out; spec lint review when the pilot report lands; re-clip 3 images.
3. **When operator is ready:** Student Book full run (runbook Path A or B).
4. **After Phase 1 report:** Phase 2 mapping pilot on ~10 notes (slug signal + AI candidates + PR review), then scale to 112.
5. **T-C04 verdict + starter tranche** → T-C06 unlock → DB wiring + serving (unchanged parked conditions).

## 13. Anti-goals

- No Neo4j/new graph infrastructure; no rewrite of the live learner lens.
- No hand-authored spec statements or examples (parse, never transcribe — see the "3.4 → moles" lesson).
- No ingestion of unvalidated content; no cross-curriculum edges; no public exposure of copyrighted text.
- No graph work that gates T-036 or any Cycle 1 task.
