# Post-Review Metadata Completion — Difficulty, Question Type, Spec-Point Mapping

**Status:** **Ratified 2026-09-17** (owner-delegated self-review, §11) — one material design correction applied: the type gap is closed on the *existing* `Question.Type` substrate (§3 v1.1), not via a new version-level column
**Date:** 2026-09-17
**Tracker row:** T-C18 (registered in the master workbook TODO.md, content-ops track; sub-rows T-C18a–e per §10)
**Governing spec sections:** Master Spec §6.2/ADR-014 (curriculum hierarchy, `SpecificationPoint` as canonical anchor), §7 (KG, SUGGESTED→VALIDATED lifecycle), §10 (question bank, F-168), ADR-017 (recommendations over one evidence substrate), ADR-020 (retrieval: benchmark before promotion)
**Related rows:** T-C02 (ingestion bridge — hardcodes the placeholder), T-C12 (question↔spec-point tagger — supplies candidate mappings), T-C13 (bench — defines what "VALIDATED" corpus exists today), F-050 (Test Builder — the consumer this proposal serves)
**Code touchpoints:** `syllabai-core` → `Question` (existing `Type` enum — see §3 correction) and `QuestionVersion` (difficulty/commandWord), `PastPaperIngestionService` (hardcoded `3` verified; also hardcodes `Question.Type.STRUCTURED`), `GlmOcrDraftMapper`, Flyway migrations (**V27 current — verified in-tree; next migration is V28**); `syllabai-resources` → T-C12 tagger (`scripts/c12_spec_tagger.py`) + `c12_promote` operator gate (`scripts/c12_promote.py`, verified); `syllabai-teacher-workbench` → staged intent UI (review surface)

---

## 1. Verified current state (claims below are checked against code and the T-C13 DB reconciliation, 2026-09-17)

| Claim | State |
|---|---|
| `QuestionVersion.difficulty` exists as `int, nullable = false` | ✅ but `PastPaperIngestionService` hardcodes `3` at ingestion with the honest comment *"difficulty unknown until review"* — every parsed question presents a fiction of medium difficulty |
| `QuestionVersion.commandWord` extracted | ✅ populated from the draft's command-word signal (`CommandWordLexicon`) |
| MCQ detection | ✅ extractor-side (`GlmOcrQuestionExtractor` MCQ hindsight validation), and the pair-CLI draft bundle carries the signal forward (`mcq` + `options` fields — verified in a real bundle). **Correction made at ratification:** a type column *does* exist — `Question.Type { MCQ_SINGLE, SHORT_ANSWER, STRUCTURED }` — but `PastPaperIngestionService` **hardcodes `STRUCTURED`** for every ingested question, so the MCQ signal still dies at the ingestion boundary; worse, the draft-level signal was never persisted anywhere |
| Spec-point relation on questions | ❌ none in the assessment module; questions land on an *ingestion-anchor topic* only. Mapping exists **corpus-side**: the T-C12 hybrid tagger + `c12_promote` operator gate in `syllabai-resources` produce reviewable mapping artifacts, but nothing in core DB consumes them |
| KG spec points | ✅ 182/182 4CH1 spec-point nodes VALIDATED (per T-C13 preconditions) — the mapping *target* side is ready |
| Question corpus | 127 VALIDATED question versions over 94 papers; 172 documents; 2,333 chunks, **zero embeddings** (gated by T-C07); production retrieval = arm A0 KG-only |
| Test Builder (F-050) | functional for test creation, but filtered composition on difficulty/type/topic is **not trustworthy** while difficulty is a hardcoded 3 and type/mapping don't exist in DB |

**Conclusion:** the learner-facing idea of "filter the bank by difficulty, type, and
syllabus point" is currently blocked by three different gaps: a placeholder value, a
missing column, and a mapping that lives outside the database. This proposal closes
all three with one governance model.

## 2. Design principles (inherited, restated for this layer)

1. **Nothing auto-promotes.** Every metadata value enters as SUGGESTED with provenance
   (method, model/version where applicable, evidence reference, actor, timestamp) and
   becomes VALIDATED only through the existing operator/SME gates. The parser "never
   guesses" and neither does metadata.
2. **Unknown is a first-class value.** Where truth is absent, the system records
   UNKNOWN and downstream consumers treat it explicitly — a blueprint filter never
   silently falls back to a guess.
3. **Additive migrations only.** New columns/tables behind Flyway; no reshaping of
   existing validated entities.
4. **One substrate.** Metadata lives on the existing question-bank entities consumed
   by Test Builder, Smart Mark, recommendations and analytics — no parallel shadow
   tables (the ADR-017 lesson).

## 3. Question type (close the cheapest gap first) — v1.1, corrected at ratification

**Correction:** the draft proposed a new `question_type` column on `QuestionVersion`.
Ratification review found that a type substrate **already exists**: `Question.Type {
MCQ_SINGLE, SHORT_ANSWER, STRUCTURED }` (DB column on `questions`, V3/V8 lineage), and
it is **load-bearing** — `ServableQuestionService`, `AssessmentService` and
`ServableQuestionSpec` all gate serving paths on `type == STRUCTURED`, and the enum's
own comment marks MCQ end-to-end support as a known *future* project. Adding a parallel
version-level column would violate this proposal's own Principle 4, and blindly writing
`MCQ_SINGLE` into the existing column at ingestion would silently drop those questions
out of every STRUCTURED-gated serving path.

**Corrected change — persist the signal, keep serving semantics untouched:** add three
additive columns on `Question`:

- `detected_type` enum `MCQ_SINGLE | SHORT_ANSWER | STRUCTURED | UNKNOWN`, default
  `UNKNOWN` — the honest parser observation, persisted so it stops dying at the
  boundary;
- `type_source` enum `UNKNOWN | PARSER | SME`;
- `type_state` reusing the corpus validation-state vocabulary (`SUGGESTED | VALIDATED`).

The existing `Question.type` column stays the **serving-authoritative** type and its
behavior is unchanged (past papers keep flowing as STRUCTURED until the MCQ end-to-end
project lands). Promoting `detected_type` into serving `type` for MCQ_SINGLE is
explicitly **out of scope** here and must ride the MCQ end-to-end work, not sneak in
through metadata.

**Fill path:**

1. **At ingestion (SUGGESTED):** the GLM-OCR draft already carries MCQ signals
   (`mcq` + `options` in the pair-CLI bundle, verified). Map them deterministically in
   `GlmOcrDraftMapper`: MCQ-detected → `MCQ_SINGLE / PARSER / SUGGESTED`; otherwise →
   `STRUCTURED / PARSER / SUGGESTED` **only when** the draft shows explicit part
   structure; else `UNKNOWN / PARSER / SUGGESTED`.
2. **At validation:** the existing review pass (workbench staged importer) confirms or
   corrects the detected type alongside the content review it already performs — one
   extra field on an existing human step, not a new human step.
3. **Legacy backfill (non-destructive):** existing PAST_PAPER rows get `detected_type =
   'UNKNOWN'`, `type_source = 'UNKNOWN'`, `type_state = 'SUGGESTED'` — history stops
   pretending it classified anything, while `Question.type` stays STRUCTURED so
   serving and Smart Mark flows are untouched. TEACHER_AUTHORED / SEED_DEMO rows keep
   their type with `type_source = 'SME'`, `type_state = 'VALIDATED'` (the author chose
   it deliberately).

**Why this is safe:** the signal is persisted without touching a serving-gated column;
error cost is low; and Test Builder behavior on `UNKNOWN` is defined (§6).

## 4. Difficulty (replace the fiction, keep the column)

**Change:** `difficulty` becomes nullable; add `difficulty_source` enum
(`UNKNOWN | SME | EVIDENCE | HEURISTIC`) and `difficulty_rated_at`, `difficulty_rated_by`.
Migration backfills: existing rows keep `3` but get `difficulty_source = 'UNKNOWN'` —
history stops lying without breaking reads.

**Two-axis rule (clarified at ratification):** `difficulty_source` records *where the
value came from* and never changes after write; the validation *state* is what flips.
When an SME ratifies an `EVIDENCE` or `HEURISTIC` proposal, `difficulty_state` moves to
`VALIDATED` while the source preserves its origin — this is what §6's
"EVIDENCE-validated" means (state VALIDATED ∧ source EVIDENCE). The same two-axis model
governs §3's type columns.

**Fill paths, in governance order:**

1. **SME (authoritative, primary):** during question validation, the reviewer assigns
   difficulty on the same staged-intent surface as §3. `SME`-sourced values are the
   only ones Test Builder treats as fully trusted.
2. **EVIDENCE (post-launch, derivative):** once the Learning Evidence subsystem
   accumulates attempts, per-part mean-mark ratio / first-attempt success can propose
   difficulty. These are **proposals** (SUGGESTED, `EVIDENCE`, with model + version +
   cohort window recorded) surfaced to SME for one-click ratification — never
   self-applied to serving. This mirrors the project's evidence-not-arithmetic stance
   on mastery (F-rules: flags are evidence, never deterministic mastery arithmetic).
3. **HEURISTIC (pre-fill only):** marks count + command-word tier
   (`CommandWordLexicon` already maps command words to cognitive levels) produce a
   *suggested band* shown in the review UI to speed SME work. Stored only when the
   SME adopts it (then its source becomes `SME`), or stored as
   `HEURISTIC/SUGGESTED` for analytics visibility — **excluded from Test Builder
   filters either way**.

**Explicitly rejected:** LLM-estimated difficulty auto-VALIDATED from question text.
If an LLM rater is ever added, it enters through the same SUGGESTED + benchmarked
proposal path (per Master Spec rule 12: no technique adopted without benchmark).

## 5. Spec-point mapping (promote T-C12 from artifact to substrate)

**Change:** new table `question_spec_points`:

```text
id                       pk
question_version_id      fk → question_versions (must exist; question VALIDATED or the mapping row itself is gated)
spec_point_id            fk → specification_points (must be VALIDATED)
relation                 enum {PRIMARY, SECONDARY}
state                    enum {SUGGESTED, VALIDATED, REJECTED}
provenance               jsonb: {method, model, version, batch_id, evidence_ref}
mapped_by / mapped_at    actor + timestamp (operator or SME)
unique(question_version_id, spec_point_id, relation)
```

**Fill path:** the T-C12 tagger's output (operator-promoted via `c12_promote`) becomes
the SUGGESTED feed; promotion happens through a new importer that reuses the
workbench's staged-intent pattern (propose → operator verdicts → applied batch with
evidence pack), consistent with how the corpus tooling already governs promotions.

**Fail-closed rules for the importer:**

- both referenced entities must exist and be VALIDATED (spec-point side already is:
  182/182);
- **curriculum scoping:** the spec point must belong to the curriculum version family
  matching the paper's qualification (4CH1 → IGCSE family; WCH1x → `IAL-CHEM-2018`).
  Cross-family mappings are rejected loudly, not clamped;
- exactly-zero PRIMARY mappings on a question is legal (coverage gaps are information —
  the teaching-coverage lens already distinguishes absent from weak); **more than one
  PRIMARY on a question is also legal** (multi-spec-point questions are a real class —
  the retrieval bench has a dedicated `class_multi_spec_point` gold file) but the
  importer surfaces it in the review batch so the operator sees it; it never blocks;
- re-import of an identical batch is idempotent by provenance fingerprint; a conflicting
  re-import fails loudly (the CurriculumIngestionService precedent).

**Non-goal correction (records vs truth):** revision notes are deliberately *not*
mapped here — notes map to spec points on their own side; the join happens through the
spec point, which is the canonical anchor (ADR-014). Keeping questions and notes joined
only through spec points prevents a second mapping substrate from forming.

## 6. Test Builder enablement (the consumer contract)

Blueprint composition under F-050/F-171–F-174 may filter on metadata **only under
these rules**:

- `difficulty`: filterable when `difficulty_source IN (SME, EVIDENCE-validated)`;
  `UNKNOWN`/`HEURISTIC` values are excluded from filtered candidate pools (never
  approximated into a band);
- `question_type`: filterable when state = VALIDATED; `UNKNOWN` excluded from typed
  filters;
- topic/spec scoping: expansion happens through the KG from the selected spec-point
  subtree; a question joins a blueprint only via a VALIDATED `question_spec_points`
  row whose spec point falls inside the scoped subtree;
- every blueprint records the metadata filter + candidate-pool size at assembly time —
  filtering decisions are auditable, not folklore;
- empty pools surface as explicit blueprint validation failures ("no candidates match"),
  never as silent substitution.

This keeps the existing hard-validity constraints (F-173) intact: metadata filtering
narrows candidates; it can never relax a hard rule.

## 7. Migration & rollout sequence (each step gated on the previous)

1. **V-next migration:** nullable `difficulty` + `difficulty_source` + type columns
   (backfill `UNKNOWN` as in §4); `question_spec_points` table. Read-only rollout —
   no consumer reads the new fields yet.
2. **Ingestion changes** (`GlmOcrDraftMapper`/`PastPaperIngestionService`): stop
   hardcoding 3; emit type SUGGESTED from draft signals. New ingests are honest;
   the 127 already-VALIDATED question versions are untouched (retro-type them in the
   next SME sweep if wanted — optional).
3. **Workbench UI:** type + difficulty fields on the existing staged review surface
   (smallest possible increment to a human flow that already exists).
4. **T-C12 importer:** promote corpus-side mappings into `question_spec_points` as
   SUGGESTED → operator batch → VALIDATED.
5. **Test Builder:** enable filters strictly per §6; behind the same acceptance
   discipline as other serving features (integration tests pin the UNKNOWN-exclusion
   behavior).
6. **(Post-launch)** evidence-derived difficulty proposals per §4.2.

## 8. Risks & controls

| Risk | Control |
|---|---|
| Prematurely VALIDATED metadata pollutes blueprints | §6 source/state rules; filters hard-exclude non-trusted sources |
| Mixed-source difficulty confuses analytics | `difficulty_source` travels with every read; dashboards group by source |
| Mapping explosion (a question mapped to half the spec) | PRIMARY/SECONDARY + unique constraint + importer-side per-question cap warning (e.g. >3 SECONDARY surfaces for review, doesn't block) |
| Migration churn on a hot entity | additive-only; nullable; no reads until consumers ship |
| Tagger drift after curriculum revisions | importer re-validates curriculum family at import time; spec-point ids are versioned (ADR-014), so a curriculum bump invalidates by construction |

## 9. Non-goals

- No auto-validation of any metadata value, ever, by any model.
- No learner-facing difficulty labels until SME/EVIDENCE coverage is meaningful
  (serving UI can show nothing rather than a guess).
- No embeddings changes — the T-013/T-C07 embedding gate is orthogonal and untouched.
- No new recommendation behavior — ADR-017 consumes this substrate later, unchanged.

## 10. Tracker rows (suggested, for the master workbook sync)

- **T-C18a** — migration V-next: nullable difficulty + source + `question_type` +
  `question_spec_points` (core).
- **T-C18b** — ingestion honesty: replace hardcoded difficulty, emit parser-sourced
  type (core).
- **T-C18c** — workbench review fields for type/difficulty (teacher-workbench).
- **T-C18d** — T-C12 mapping importer with fail-closed curriculum scoping (core +
  resources).
- **T-C18e** — Test Builder filter enablement under §6 contract (core + web).

## 11. Ratification record (self-review, 2026-09-17)

Reviewer: main agent (owner-delegated). Claims re-verified against primary sources:

- **Hardcoded difficulty** — `PastPaperIngestionService` re-read: `3` with the exact
  comment *"difficulty unknown until review"*, in **both** the `Question` and
  `QuestionVersion` constructions; `QuestionVersion.difficulty` is a primitive `int`
  (→ NOT NULL) as §4 assumes; `command_word` present.
- **Type substrate (the material correction)** — `Question.java` line 26:
  `enum Type { MCQ_SINGLE, SHORT_ANSWER, STRUCTURED }` with the comment
  *"MCQ end-to-end; STRUCTURED = multi-part (V8)"*; ingestion hardcodes
  `Question.Type.STRUCTURED`; STRUCTURED-gated serving paths verified at
  `ServableQuestionService` (×2), `AssessmentService` (×2), `ServableQuestionSpec`.
  §1 table and §3 rewritten accordingly; the proposed version-level `question_type`
  column is **dropped** in favor of additive `detected_type`/`type_source`/`type_state`
  on `Question` (no parallel substrate, no serving-path blast radius).
- **Draft signal** — a real pair-CLI bundle (`tools/content-package-v0.1/
  real_corpus/source/bundle/qp-draft.json`) confirmed `mcq` + `options` fields on
  questions, so the §3 mapper mapping is deterministic.
- **Migrations** — `syllabai-core` `db/migration/` lists **V27__revision_notes.sql**;
  the draft's "V26 current" was stale; next migration is V28. Workbook row corrected
  in the same pass.
- **T-C12** — `c12_spec_tagger.py`, `c12_promote.py`, verdicts/promotions YAMLs all
  present in `syllabai-resources/scripts/`; `CommandWordLexicon` verified in
  syllabai-parser (`structure/`), feeding the §4.3 heuristic path.
- **Multi-PRIMARY** — §5 amended: multiple PRIMARY rows are legal (multi-spec-point
  questions are a bench gold class) but surfaced for operator review.

**Verdict: RATIFIED with the corrections above.** Sub-rows T-C18a–e stand; T-C18a's
scope now reads "V28: nullable difficulty + source/state columns + detected-type
columns on Question + `question_spec_points` table".
