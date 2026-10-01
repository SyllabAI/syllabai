# ADR-030: Per-course tutor scoping — the tutor ask carries a course reference, core resolves it fail-closed against its own curriculum registry, and tutor sessions record the course they served

**Status:** **Accepted (2026-10-01)** — promoted PROPOSED → ACCEPTED on merge (operator decision). Implementation evidence: `syllabai-core` V53 (migration + `resolveForCourse` fail-closed + ask wiring + session write-once, 9 new tests) on `main` as `4cb5714`; `syllabai-hub` registry patch (`curriculumCode` field + `/tutor?course=` gating + `courseRef` pass-through) merged via [PR #5](https://github.com/SyllabAI/syllabai-hub/pull/5) — hub CI `build` + `e2e` green at the merge commit; core `main` CI `build` green post-merge (`f1a3a5e`). This docs record merged via [PR #12](https://github.com/SyllabAI/syllabai/pull/12) as `4c2ffa6`. ERD delta recorded in `docs/DATA_MODEL_ERD.md` §8.
**Date:** 2026-09-30
**Owner:** syllabai (this file + a `DECISIONS.md` entry), syllabai-core (V53 + resolver), syllabai-hub (registry field + tutor surface)
**Supersedes:** nothing (extends the scope policy in ADR-029 tranche work; refines the serving-scope behavior first fixed by T-C07)
**Complies with:** `AGENT.md` mandatory reading items 6 and 9; `LEARNER_INTERACTION_MEMORY_ARCHITECTURE.md` §22 (server tutor sessions); `RAG_RETRIEVAL_RESEARCH.md` / ADR-020 (retrieval subordination); the V47/V48/V49/V51 opaque course-ref ruling

---

## Context

The operator reported that the tutor surface is effectively chemistry-only no matter which course a learner is browsing: a learner sitting in an IGCSE Physics course can ask a physics question and receive an answer grounded in the Chemistry corpus. This is the worst failure shape the retrieval discipline exists to prevent — a confident, cited, *wrong-subject* answer.

Root cause chain (code-verified 2026-09-30 against `syllabai-core` main `5b946ba` and `syllabai-hub` main `0913147`):

1. **The wire contract has no course field.** `TutorController.TutorAskRequest` is `{question, history, sessionId}`. Neither the hub's `/api/ai/chat` proxy nor core's ask/stream endpoints can express "the learner is asking about this course".
2. **Scope resolution is a global singleton.** `CurriculumScopeResolver.resolveActive(learnerId)` resolves exactly one serving scope for the entire platform. Its own Javadoc records the deliberate forcing function: *"When a second curriculum gains serving surface this resolver stops resolving until a per-learner curriculum selector lands"*. Production reality: two ACTIVE `curriculum_versions` rows (`4CH1-2017`, `IAL-CHEM-2018`), but only 4CH1-2017 owns serving surface — so every ask silently resolves to Chemistry. The fail-closed machinery was built for the *second* curriculum; it never fires for the *first* one, because the second curriculum's surface ownership is what triggers refusal.
3. **`tutor_sessions` cannot remember a course.** The V42 schema is `{id, learner_id, created_at, last_active_at}`. Server-side transcripts (§22) cannot be filtered, grouped, or audited by course, and the hub's conversations pane has no honest way to label which course a session served.
4. **The connecting key is not derivable.** The hub's file-based course registry (`content/courses.json`, 49 courses) carries Edexcel official subject codes (`4CH1`, `YCH11`, …); core's `curriculum_versions.code` carries syllabus-era codes (`4CH1-2017`, `IAL-CHEM-2018`). There is no rule that maps `YCH11 → IAL-CHEM-2018` — the bridge must be explicit, hub-maintained data, never inference on either side.

Left implicit, this chain means every retrieval guarantee (per-course bundles, scope-narrowed retrieval, VALIDATED-only serving) is enforced everywhere EXCEPT the tutor — the one surface that generates confident prose.

## Decisions

**D1 — One nullable column: `tutor_sessions.course_ref VARCHAR(64) NULL` (V53).**
V51/V52 are consumed (classroom foundation, teaching coverage), so this tranche migrates as **V53**. The column stores the hub-supplied reference VERBATIM — opaque, no FK, no lookup table, no check beyond width (the V47 `card_id` / V48 `noteId` / V49 `course_slug` / V51 `course_slug` ruling reused without modification). NULL is legitimate history: pre-V53 rows and asks from surfaces with no course context keep NULL, and back-filling is forbidden because it would falsify what the chat really served. No index: the only reader today is per-session; a per-course transcript scan is a teacher-analytics future and the no-speculative-surface rule holds. The ALTER is metadata-only — Neon-safe, no downtime.

**D2 — The ask contract grows an optional `courseRef` (≤64 chars, never parsed by core).**
`TutorAskRequest` gains the field on BOTH `/ask` and `/ask/stream`; blank normalizes to absent so there is exactly ONE absent shape downstream. Core's treatment of the ref is a lookup, not a parse: resolution happens against core's OWN `curriculum_versions` registry, which is a core-native query and does not violate the opaque-ref ruling.

**D3 — `CurriculumScopeResolver.resolveForCourse(ref)`: exact match, fail-closed, no fallback.**
A present ref resolves through `findByCodeAndStatus(ref, ACTIVE)` + the SAME `ownsSurface` test the global path applies. Exactly one owner serves; zero or ≥2 owners (and a blank ref) yield empty, and the ask refuses with a deterministic `COURSE_SCOPE_REFUSAL` that NAMES the ref — blocking and streamed texts byte-identical, provider tag `deterministic-course-refusal`. There is deliberately NO fallback to `resolveActive()` when per-course resolution fails: a wrong-course answer is worse than a refusal. Exact equality only — no prefix, no normalization, no fuzzy variants, because the two code namespaces have no derivable rule between them and any looser match would be a hidden registry in code. The global `resolveActive()` path is untouched for course-less asks (pilot compatibility is a design decision, not a fallback), and the resolver's `learnerId` hook stays reserved for the future per-learner selector.

**D4 — Absent ref = legacy path, byte-identical.**
Every existing caller (hub legacy entry, CLA, SmartLesson, anonymous preview, the whole test suite) compiles and behaves exactly as before. The pilot tutor keeps working through the transition unchanged.

**D5 — The bridge is hub data: `courses.json` gains a nullable `curriculumCode` per course.**
The hub resolves `/tutor?course=<slug>` → registry `curriculumCode` → ask `courseRef`. A course whose registry row has no `curriculumCode` gets the tutor HONESTLY GATED ("Tutor not yet available") — a visible gate, not a silent wrong-corpus answer. The pilot is mapped: `igcse-chemistry-19 → 4CH1-2017`. The hub never invents a mapping, and core never sees the hub's slug namespace.

**D6 — Session integrity: write-once + 409.**
The session's serving course is fixed by its FIRST ref-carrying append. A later ask naming a DIFFERENT course is a `ConflictException` (409) — the same integrity shape as the foreign-session probe — enforced twice: a pre-pipeline consistency probe (before any LLM spend) and an append-time backstop. `SessionView`/`SessionSummaryView` expose `courseRef` so the hub shows what the server ACTUALLY served, not what the client claims.

**D7 — Everything downstream is untouched.**
Retrieval (KG + vector), the CLA surfaces, the learner model, content search (notes/questions are already per-course client-side via bundles), and the Smart Mark state machine are all unchanged. Scope was already a parameterized seam (`CurriculumScope`); this tranche only changes WHO resolves it and from what input.

## Alternatives considered and rejected

- **Core-side slug registry table.** A `courses` table in core mapping slugs→curriculum codes would create a SECOND course registry and directly violate the opaque course-ref ruling (core does not know what a course is; it never has). Rejected.
- **Prefix/normalized matching** (`4CH1` prefix → `4CH1-2017`, or trim the year suffix). There is no derivable rule — `YCH11 → IAL-CHEM-2018` proves it — so any matching scheme is a hidden registry encoded in code, silently wrong the day the next course maps. Rejected.
- **Do nothing.** The wrong-subject answer ships today (the operator report), and the day a second curriculum gains serving surface the global resolver fail-closes ALL asks and breaks the pilot outright. Rejected.

## Consequences

- The wrong-subject failure class is closed at the resolution boundary: a course either resolves to exactly one serving curriculum or the tutor refuses/gates, naming the ref.
- Unmapped courses become GATED, not wrong — a visible product limitation that is honest about corpus coverage instead of a confident fabrication.
- `tutor_sessions` gains provenance (what was served) with zero backfill risk; the hub's conversations pane can group and label by course from server truth.
- Adding a new tutor-enabled course is now a one-line registry edit (`curriculumCode`), gated by the same ACTIVE + owns-surface discipline core already enforces.
- A future per-learner selector (target-EERD G1 `subject_enrollments`) plugs into the reserved `learnerId` hook without touching this design; core-side course-aware content search stays a separate tranche.

## Verification plan (becomes the merge gate)

1. **Core CI `mvn verify`** — the full suite plus the new pins: per-course resolution reaches BOTH retrieval surfaces; unresolved ref refuses naming the ref with no retrieval and no LLM call and NO `resolveActive` fallback; streamed refusal is byte-identical with the course provider tag; null/blank ref keeps the legacy path; session write-once; mismatched ref 409s and persists nothing; views carry the ref. (Core is NOT compiled in the authoring sandbox — Java 25 vs sandbox Java 21 — CI is the gate.)
2. **Hub CI + build** — `tsc --noEmit` clean, `eslint` clean on touched files, full `bun run build` green, `/tutor` dynamic.
3. **Migration** — V53 is a metadata-only `ALTER TABLE ADD COLUMN NULL`; Flyway applies clean on Neon with no downtime and no backfill.
4. **Legacy parity** — the legacy ask path (no `courseRef`) resolves and serves exactly as before; the hub's `/tutor` without a `course` param is byte-identical.

## Provenance states

- Drafted 2026-09-30 (operator authorization "Now proceed"), after the ADR-029-era state check of all repos (core `5b946ba`, hub `0913147`, migration numbers V51/V52 re-verified as consumed).
- Companion artifacts: the DECISIONS.md entry (house condensed block), the ERD delta with the mermaid source (`V53_TUTOR_COURSE_ERD.md`, rendered to `tutor_course_erd_v53.png`), and the implementation patches (core + hub) exported from the `v53-per-course-tutor-scoping` branches.
- Status flips to **Accepted** when both implementation PRs merge (the DECISIONS.md entry carries the same conditional line, and the promotion record is pre-drafted in the PR description).
- **Promoted to Accepted 2026-10-01** on operator go: PR #12 merged as `4c2ffa6` after both implementation PRs were on main (core `4cb5714`; hub PR #5, CI `build` + `e2e` green at `0c75dd6`) — the merge-gate conditions above are met.
