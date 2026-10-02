# PAST_PAPER_RUN_MODE_DESIGN.md — Interactive Paper Run ("take any past paper like Pearson's interactive QP, and mark it for real")

**Status:** PROPOSED — detailed design draft **v2** (2026-10-03). v1 (2026-10-01) was reviewed by the operator via an external reviewer; v2 folds in the adjudicated amendments and the operator's scoping decision (**implementation focus = 4CH1**, operator message 2026-10-03). Not yet landed as an implementation tranche; opening the tranche registers a task yaml per the task-DAG README.

**Benchmark evidence base:** `wph11-01-que-20240511.pdf` (print QP, 28 pp, 0 form fields) vs `Interactive electronic QP WPH11_01.pdf` (28 pp, **43 static AcroForm fields, zero JavaScript** — 4 candidate-detail text boxes, 10 four-kid radio groups for Section A MCQs, 33 text boxes on the q11–q19 answer lines; no marking logic anywhere; plot/table parts skipped even by Pearson). WPH11 remains the *motivating* benchmark; per the 2026-10-03 operator decision, **implementation focuses on 4CH1 first** (see §6 and §8).

**Verified corpus facts (2026-10-03, hub content bundle `igcse-chemistry-19`):** 524 questions / 1,404 parts — 1,176 `structured` + **228 `multiple_choice` carrying attested keys in the data itself** (`choices[].isCorrect`), plus `sourcePaper` provenance (`date`, `number`, `questionNumber`, `questionPart`) as the reconstruction join key. Paper runs on 4CH1 therefore exercise **real auto-mark from day one**, not a demo stub.

---

## 1. Context — what exists today, precisely

The hub's Past Papers surface already has **two modes** (both honest about provenance):

### Mode 1 — PDF archive + Mock (`/courses/[course]/past-papers`)
- SME-style session-grouped index over the `syllabai-pastpapers` corpus (QP + MS PDFs streamed from raw.githubusercontent via pdf.js; AI-IDENTIFIED provenance banner, operator ratification pending).
- **View**: QP / MS / Split panes (side-by-side on desktop, A/B toggle on mobile) for **every** archived paper of every course.
- **Mock**: fullscreen QP + **official timer** (`durationMin` from the corpus index), finish → **self-grade by typing a marks total** (optional per-question tally, `MockResult.questions[]` v2 field) → saved to the local SIMULATED overlay (`syllabai.mockResults.v1`) and shown in the Mock Results Strip. Build-time QP text parsing (`ms-questions.ts`, PP-FIND-SCORE-3) already powers the question-jump overlay; build-time extraction already emits **PaperBlueprint** JSON (official per-question marks, paper total, inferred gaps, optional-choice papers).

### Mode 2 — Interactive reconstruction (`/past-papers/[paperKey]`)
- Questions the parsed corpus attests via `sourcePaper` provenance, replayed **in paper order** through the Exam-Questions `QuestionPlayer`; every surface declares the PARTIAL RECONSTRUCTION framing and shows coverage vs the official blueprint.
- **MCQ parts**: select → submit → instant auto-mark with explanation/mark-scheme and Try again.
- **Structured parts**: "How did you do?" self-score (x/marks) against the full-screen mark-scheme modal, plus an **AI-mark probe** (`/api/ai/mark`, AI_SUGGESTED, provider-gated, explicitly "check against the mark scheme").
- **attempt-bridge**: when the course is the pilot (4CH1) AND the learner is signed in AND core is reachable, each answered question also becomes a **real core attempt** (Smart Mark, learner model, mastery decay, review queue, attempt history). A question the join cannot verify is never submitted (no fabricated evidence). Everything degrades gracefully to the local experience.

### The gap (why this design exists)

| Capability | Pearson interactive QP | Mode 1 (PDF/Mock) | Mode 2 (reconstruction) | This design |
|---|---|---|---|---|
| Full official paper | ✅ | ✅ (PDF) | ❌ partial only | ✅ (Mode 1 papers) |
| Typed answers on structured lines | ✅ | ❌ | ❌ (whole-question flow) | ✅ |
| Clickable MCQs | ✅ | ❌ | ✅ | ✅ |
| Auto-marked MCQs | ❌ (selection only, no JS) | ❌ | ✅ | ✅ (where the key is attested) |
| Whole-paper exam run (timer, palette, answer-later) | ❌ | timer only, no capture | ❌ | ✅ |
| Paper-level result out of official total | ❌ | ✅ (typed total) | ❌ | ✅ (per-question → per-paper) |
| Feeds the learner model | ❌ | ❌ (local mock tally) | ✅ (pilot, per question) | ✅ (4CH1; see scope note) |

**Scope note (stated plainly, 2026-10-03):** the learner model is **chemistry-only** today — the attempt-bridge joins on the 4CH1 pilot course. A Paper Run of a non-4CH1 paper (e.g. the WPH11 physics paper that motivated this design) delivers auto-marked MCQs where keys are attested, self-marked structured parts, and **local SIMULATED results with no learner-model feed** until that course is parsed and bridged. That is the honest ladder, and every surface must label it.

**One-sentence thesis:** Pearson digitized the *answer sheet*; we already own the *question corpus, the mark schemes, the attempt pipeline and the learner model* — the missing piece is an exam-run shell with an interactive answer layer over the PDFs we already stream, plus a grading console that turns "type your total" into per-question evidence.

---

## 2. Goals

1. **G-1 — Paper Run mode (4CH1 first)**: archived corpus papers can be taken as an interactive paper: on-PDF typed answers, clickable MCQs, official timer, question palette, flag-for-review, save/resume, auto-submit at time-up. v1 scope is the **4CH1 archive** (operator decision 2026-10-03); other courses' papers keep today's Mock (+ draft-manifest hint layer when §Track C drafts exist) until their courses are wired.
2. **G-2 — Real grading, honestly tiered**: MCQs auto-mark **only where the answer key is attested** (parsed corpus or confirmed key); everything else grades in a per-question console beside the MS pane; results carry per-question marks out of the official blueprint total **and a per-mark provenance label** (§5.4–5.5).
3. **G-3 — Model integration without fabrication**: paper answers flow through the existing attempt-bridge (4CH1 pilot, verified identities only) and the existing honesty stack (local SIMULATED overlay otherwise). No new core surface is required for v1.
4. **G-4 — Reconstruction upgrade**: Mode 2 papers get the same exam-run shell (timer, palette, deferred feedback) with their existing auto-mark/self-mark/AI-mark per part, and a paper report that reconciles against the official blueprint.
5. **G-5 — Provenance discipline carried forward**: AI-IDENTIFIED corpus status, partial-reconstruction framing, "options/marks not captured" honesty, and **practice-integrity labeling** (§5.1) all persist unchanged.

## 3. Non-goals (v1)

- **N-1 — No fillable-PDF generation.** A Pearson-parity AcroForm artifact is explicitly deferred (a generator in the parser lane is possible later; the web surface supersedes it for product purposes).
- **N-2 — No core schema/migration.** v1 composes existing per-part attempts; a first-class paper/exam session entity in core is a future ADR (would touch ADR-030 session-integrity territory and needs its own record).
- **N-3 — No graph-drawing/table UX.** Plot/table parts keep the "answer on paper, self-mark against the MS" convention (Pearson's own interactive QP skips them too); the run captures a "done on paper" flag so grading and totals stay honest.
- **N-4 — No auto-detection-only overlay trust.** Heuristic answer-region detection may *draft* an annotation map, but a Paper Run uses curated/confirmed maps; drafts render read-only hints, never interactive fields (see R-1).
- **N-5 — No learner-model evidence re-weighting by mark provenance.** (v2, after external review.) Provenance is **recorded and displayed** (§5.5) but v1 does not change what feeds the learner model: self-marked structured parts already feed core attempts via the live Mode 2 bridge, and that contract is unchanged. Re-weighting evidence strength (e.g. demoting self-marks) is a learner-model policy question that would alter existing live behavior — it needs its own ADR, not a rider on this design.

---

## 4. Architecture overview

Three tracks, one shell:

```
Track A · Paper Run (4CH1 archive papers)       Track B · Reconstruction run (parsed papers)
┌──────────────────────────────────────┐        ┌──────────────────────────────────────┐
│  ExamRunner shell                    │        │  ExamRunner shell (same component)   │
│  timer · palette · flags · resume    │        │  + QuestionPlayer in exam mode       │
│  ┌────────────────────────────────┐  │        │  (feedback deferred to grading)      │
│  │ PDF pane (pdf.js, existing)    │  │        └──────────────────────────────────────┘
│  │ + AnswerOverlay (capture)      │  │                     │
│  └────────────────────────────────┘  │                     ▼
│                 │ answers            │        grading console (per part,
│                 ▼                    │        auto-mark where attested)
│  GradingConsole (answers ∥ MS pane)  │
│  MCQ auto-mark (attested keys)       │
│  per-question score entry (MS ∥ QP)  │
└──────────────────────────────────────┘
                  │                               both tracks
                  ▼
   PaperRunResult v3 ──► MockResults strip / My Progress (local, SIMULATED where applicable)
                  └────► attempt-bridge ──► core attempts (4CH1 pilot, verified joins only)

Track C · Data (build time + parser lane)
  corpus QP/MS ──► build-time extractor (already emits PaperBlueprint)
                   ──► NEW: PaperInteractivityManifest draft (regions, MCQ keys)
                   ──► curation queue ──► confirmed manifests committed to hub content
```

---

## 5. Detailed design

### 5.1 The annotation artifact — `PaperInteractivityManifest` (Track C first, everything consumes it)

The single new artifact. One JSON file per paper, committed alongside the hub content (build-time drafts land in the repo only after curation), versioned and provenance-stamped:

```jsonc
{
  "version": 2,
  "paper": { "corpusKey": "2024-06:4ch1-2c", "ref": "4CH1/2C", "session": "2024-06",
              "durationMin": 105, "totalMarks": 100, "blueprintRef": "official (extracted)",
              "integrity": "practice" },                       // v2: PRACTICE (v1) | CONTROLLED (future)
  "provenance": {
    "source": "build-time-draft|curated",
    "draftGeneratedAt": "2026-10-03T12:00:00Z",
    "curatedBy": "operator|agent:<task-id>",          // required before fields go interactive
    "status": "draft|confirmed"                        // draft = read-only hint layer only (N-4)
  },
  "questions": [
    {
      "number": "1", "page": 2, "kind": "mcq",
      "mcq": {
        "options": ["A", "B", "C", "D"],
        "zones": [ { "rect": [x, y, w, h], "option": "A" } ],   // pdf.js viewport-normalized
        "key": "B", "keyAttested": true,
        "keyProvenance": "parsed-corpus|ms-extracted|operator-confirmed"
      }
    },
    {
      "number": "11", "page": 7, "kind": "structured",
      "parts": [
        { "part": "a", "marks": 2,
          "answerAreas": [ { "rect": [x, y, w, h], "lines": 4 } ],
          "answerKind": "text" }                        // text | paper-only (plots/tables)
      ]
    }
  ]
}
```

**Authority stratification (v2 invariant — what the manifest is and is not):**

| Manifest content | Authority |
|---|---|
| Question/part identity join (`sourcePaper`, blueprint refs) | Canonical assessment truth lives in core (`Question`/`QuestionPart`) and the PaperBlueprint — the manifest *points at* it, never redefines it |
| Answer rectangles / hit zones | **UI metadata only** — presentation hints for the overlay; wrong rects can never corrupt educational data |
| MCQ keys | **Assessment evidence, but only with named provenance** (`keyAttested` + `keyProvenance`); unattested keys are inert (captured, graded by a human in the console, never auto-marked) |
| Mark allocations | From the PaperBlueprint (official totals), never invented by the manifest |

The manifest as a whole is **presentation/interactivity metadata**. Provider- and UI-specific infrastructure must not become the canonical data model — same principle as the content-compiler and tutor-scoping ADRs.

Rules:
- Rects are normalized to the pdf.js viewport at a pinned scale per page (the renderer applies the current viewport transform) — resilient to zoom/device.
- **`status: draft` manifests never render interactive fields** (they render a translucent "answer areas detected — pending curation" hint). Only `confirmed` maps go live. This is the N-4 honesty gate.
- MCQ `keyAttested: true` requires a named provenance; the grader auto-marks only then. For 4CH1 papers, `parsed-corpus` keys are available for the 228 attested MCQ parts (bundle `choices[].isCorrect`). Unattested-key MCQs are captured and graded in the console (5.3), and **the confirmed key from grading flows back** into the manifest candidate set (coverage grows with use, never fabricated).
- `answerKind: "paper-only"` parts render a checkbox row ("done on paper") instead of text areas (N-3) — they participate in grading and totals with the same self-mark flow.

### 5.2 The ExamRunner shell (shared by Tracks A and B)

A new client component (target `src/components/pastpapers/exam-runner/`, composed into both the corpus paper route and the reconstruction route):

- **Setup**: duration pre-filled with the official `durationMin`. Runs longer than official are **accommodated runs, not hidden ones** (v2): a configurable ceiling (default official +25%, operator-tunable — resolves v1 open question #3 as policy, not hard-code) and every result records `durationPolicy: "OFFICIAL" | "ACCOMMODATED"` so surfaces can label non-standard-duration runs. Starting-paper/starting-question skip (optional-choice papers already modeled by the blueprint's `optional` flag).
- **Run state machine (v2, with crash recovery)**:
  `intro → running → (paused) → time-up → time-up-pending-submission → submitted → grading → done`, with terminal `abandoned | corrupted`.
  - `time-up-pending-submission` is a **durable recovery state**: answers are persisted to IndexedDB at every transition, so a browser closed exactly as the timer hits zero deterministically reconstructs "deadline passed, never submitted" on next load and offers submit/recover — the run never depends on the timer callback having executed.
  - Immutable timestamps on every record: `startedAt`, `lastSavedAt`, `submittedAt`, `endedAt`; `timeUpAutoSubmitted: true|false` distinguishes auto-submit from manual submit.
  - States mirror `MockPhase` where possible so the existing results plumbing slots in.
- **Timer**: official countdown, top bar; < 5 min warning; auto-advance at zero via the recovery-safe path above.
- **Palette**: per-question chips (answered / flagged / paper-only / unanswered), jump navigation; mobile = horizontal strip, desktop = side rail.
- **Persistence**: answer drafts in **IndexedDB** (new `lib/paper-run-store.ts`; localStorage is already carrying mock results and would collide at ~hundreds of text answers), keyed `runId = course:corpusKey:startedAt`; save/resume honored ("Resume run?" banner on return); abandoned runs GC'd after 30 days. Resume survives device reload but is not cross-device (same convention as all local learner progress today).
- **Reconstruction mode (Track B)**: the same shell wraps `QuestionPlayer` with a new `examMode` prop — MCQ submit records the answer without revealing correctness; "View answer"/"How did you do?" surfaces unlock only in grading. All existing core-submission paths fire **at grading time** (batched), preserving the never-fabricate join rules.

### 5.3 Answer layer over the PDF (Track A rendering + capture)

- The pdf.js pane is already streaming corpus QPs (CSP-clean, raw.githubusercontent). The overlay is an absolutely-positioned sibling layer driven by the manifest rects through the live viewport transform: text areas (auto-grow, scroll-with-page), MCQ radio zones (whole-option-row hit target, keyboard accessible), paper-only checkbox rows.
- Capture writes `{ question, part, value, editedAt }` into the run store; a subtle "saved" tick per question mirrors the existing saved-bookmark affordance.
- Where a manifest is `draft`, the page shows the honest hint layer and the run button degrades to today's Mock (no capture) — Pearson-parity is earned per paper, never faked.

### 5.4 Grading console (where Pearson stops and we don't)

Post-run, per question:

1. **Layout**: QP pane (with the learner's typed answer rendered in-place in the overlay, or the option highlighted) ∥ MS pane (existing pdf.js pane, same document set as today's Split view) — one question at a time, prev/next, palette carries over.
2. **MCQ, key attested**: auto-marked on entry, shown as `✓ 1/1 (auto-marked, key: parsed-corpus)`. Disputing is allowed (records the challenge; operator-reviewable, never silently overrides).
3. **MCQ, key unattested**: the console asks the grader to click the correct option **once** while looking at the MS — records score AND the key as `ms-extracted` **candidate** for the manifest. Candidates require the same confirmation gate as any other educational-truth promotion (one grading interaction must never silently mutate the manifest into auto-mark authority). Second run on a confirmed paper auto-marks.
4. **Structured**: per-part score entry (x/marks stepper pre-filled from the blueprint), exactly the QuestionPlayer's self-score semantics; MS points visible beside. Where the AI-mark provider is configured, the existing AI_SUGGESTED probe is offered on typed text — and v2 closes the record gap: **an accepted AI suggestion records `how: "ai-suggested"`** on that part (the learner confirmed it; it is not silently folded into self-mark).
5. **Totals**: per-question and paper-level marks out of the **official blueprint total** (the blueprint already handles optional-choice papers and inferred gaps); the result record carries `coverageState` (full/partial) and `marked: { auto, self, aiSuggested, paperOnly }` counts so every surface can say how each mark was made.

### 5.5 Results and model feeds

- **`PaperRunResult` v3** (additive evolution of `MockResult`): `mode: "run"`, `perQuestion: [{ number, marks, max, how: "auto"|"self"|"ai-suggested"|"paper-only", partScores? }]`, `manifestVersion`, `coverageState`, plus v2 fields `integrity: "practice"` and `durationPolicy: "OFFICIAL"|"ACCOMMODATED"`. v1/v2 records keep rendering (the strip already tolerates optional fields).
- **Provenance is display-honest, not model-weighted (N-5)**: `how` labels are carried on every surface, but v1 does not change what the learner model consumes — the attempt-bridge contract is byte-identical to Mode 2's today. Re-weighting is a future learner-model ADR if ever wanted.
- **Local surfaces**: Mock Results Strip gains a run row (same SIMULATED labeling rules as today where the course is not core-backed); My Progress rings consume per-question marks where the questions join.
- **Core (4CH1 pilot)**: at grading, per-part submissions ride the existing attempt-bridge contract (`mcq` + `structured` maps). Paper-level rollup stays hub-local in v1 (N-2); the bridge's verified-identity rule means non-joining papers/questions degrade to local exactly as they do today. Smart Mark thus sees structured typed answers from paper runs wherever identities join — no new endpoint.

### 5.6 Which papers get what, day one (4CH1 scope)

- **4CH1 papers with a confirmed manifest** (starting with the P0 pilot paper): Track A Paper Run — the complete Pearson-parity-plus experience, with real auto-mark for attested-key MCQs and core-backed attempts for verified joins.
- **Parsed+matched 4CH1 papers** (the `playable` set): Track B run (exam-mode reconstruction) — full interactivity on the questions we hold, blueprint-coverage framing intact.
- **Everything else** (non-4CH1 courses until parsed + bridged): today's Mock, plus the draft-manifest hint layer once Track C drafts exist. The honest ladder is visible per row on the Past Papers index (run / mock / hint), replacing none of the existing entries.

---

## 6. Phasing

| Phase | Scope | Exit evidence |
|---|---|---|
| **P0 — pilot proof (4CH1, confirmed 2026-10-03)** | Manifest v2 schema + ONE curated 4CH1 paper end-to-end (Track A): runner, capture, MCQ auto-mark (attested keys — real, not stubbed: 228 attested MCQ parts exist in the bundle), grading console, result v3, bridge submissions on the pilot. Curation proceeds incrementally inside the tranche (probe 2–3 regions/parts first, then the full paper) so the geometry risk is priced before the full manifest is built. | A full mock-style run of one real 4CH1 paper on desktop + mobile; per-question result visible in My Progress via core; no honesty regressions |
| **P1 — reconstruction exam mode** | ExamRunner wraps QuestionPlayer (Track B) for the 4CH1 playable set; batched grading-time core submissions; paper report vs blueprint | A playable reconstruction taken under exam conditions; feedback verifiably deferred; core attempts recorded once at grading |
| **P2 — archive-wide drafts** | Build-time extractor emits manifest drafts (regions + MCQ keys from MS text) alongside PaperBlueprint; curation queue in the repo (CI-parseable, registry-gated like the task yamls) | Every 4CH1 corpus paper shows either run (confirmed) or hint (draft); other courses keep Mock + hint; keys never auto-live without confirmation |
| **P3 — deferred** | Fillable-PDF generator (parser lane, Pearson-parity artifact); non-4CH1 course wiring (parse + bridge) | Explicitly out of scope until requested |

**Sequencing adjudication (v2):** the external reviewer proposed Track B first (lower unit risk: reconstruction reuses QuestionPlayer; PDF overlay geometry is the fragile surface). **P0 stays Track A on one 4CH1 paper**, because (a) Track B papers are *already* interactive today — exam mode adds timer/palette/deferred feedback only, so its incremental value is small; (b) the P0 paper exercises both the overlay geometry AND real attested-key auto-mark in a single bounded tranche (the reviewer's P0 would exercise neither new hard part); (c) the only irreversible piece — the manifest schema and the curation pipeline — remains deferred until P2 in *both* orderings, so the ordering decision is reversible. The reviewer's genuine risk concern is absorbed by the incremental-curation probe inside P0. If P0's geometry probe fails structurally, Track B first becomes the fallback at zero sunk cost (shell work is source-agnostic).

## 7. Risks and mitigations

- **R-1 — Overlay geometry fragility** (paper styles differ: lined answer areas vs answer grids vs tables). *Mitigation*: normalized rects + per-paper curated confirmation (N-4); drafts never interactive; template-level heuristics only ever propose; P0 prices this with the incremental probe before any pipeline investment.
- **R-2 — Honesty drift** (auto-mark on unattested keys would be fabricated marking; run results could masquerade as official marks). *Mitigation*: `keyAttested` provenance gate, `how: auto|self|ai-suggested|paper-only` on every score, SIMULATED/coverage/practice-integrity labels carried onto every new surface, blueprint totals (not invented ones) for paper marks, `durationPolicy` labeling for accommodated runs.
- **R-3 — Client storage limits/diversity** (hundreds of text answers). *Mitigation*: IndexedDB store with schema versioning + GC; localStorage keeps only the small v3 result records; durable `time-up-pending-submission` recovery (5.2) closes the timer-crash edge.
- **R-4 — Mobile pointer precision on PDF overlays.** *Mitigation*: whole-row MCQ hit targets, auto-grow text areas, zoom-preserved rects; P0 exit requires a mobile run.
- **R-5 — Scope creep into core** (paper-session entity, grade-boundary logic, evidence re-weighting). *Mitigation*: N-2 and N-5 hard lines for v1; a core exam-session ADR or learner-model policy ADR is the recorded path if/when operator wants either.
- **R-6 — Key-return contamination** (a wrong "confirmed" key from console grading poisoning future runs). *Mitigation*: keys graded in the console enter the manifest as **candidates requiring the same confirmation gate**; disputes recorded, operator-reviewable; one grading interaction can never silently promote educational truth.
- **R-7 — Curation identity (v2).** All agents share the SyllabAI identity, so `curatedBy: agent:<task-id>` provenance + the registry-gated curation queue (P2) are the audit trail; confirmation events must name their task, matching the main-integrity ruleset regime.

## 8. Open questions for the operator

1. **Pilot paper pick** (the remaining sub-choice of the 4CH1 decision): a recent 4CH1 paper maximizing overlap with the playable set (maximizes Track A+B synergy and the bridge yield), or the paper whose MS is cleanest for key extraction? *Default proposal: maximize overlap.*
2. **Curation ownership** (unchanged): manifest confirmation as an operator-gated lane (content-validation-flip territory, AGENT.md rule 6) or an agent lane with CI parse-gates only? *Default proposal: agent lane + CI gates + task-registry provenance, flipping to operator-gated if any contamination event occurs (R-6/R-7).*
3. ~~**Accessibility cap**~~ — **resolved (v2)**: `durationPolicy` field + operator-tunable ceiling (default official +25%); accommodated runs are labeled, never hidden.
4. ~~**Track B priority**~~ — **resolved (2026-10-03)**: P0 = Track A on 4CH1, P1 = Track B (see §6 adjudication).

## 9. Amendment log v1 → v2

| # | Change | Source |
|---|---|---|
| 1 | Scope fixed to **4CH1** for the implementation tranche; WPH11/physics named as motivating benchmark with the honest local-SIMULATED expectation for non-4CH1 runs (scope note, §1) | Operator decision (Discord, 2026-10-03) |
| 2 | `how: "ai-suggested"` tier added to grading + result records; accepted AI suggestions no longer fold into self-mark (§5.4.4, §5.5) | External review, adopted |
| 3 | Crash-recovery state machine: `time-up-pending-submission` durable state, immutable timestamps, `timeUpAutoSubmitted` (§5.2) | External review, adopted |
| 4 | `integrity: "practice"` on manifest + results; CONTROLLED named as future-only (§5.1, §5.5) | External review, adopted |
| 5 | `durationPolicy: OFFICIAL\|ACCOMMODATED` + operator-tunable ceiling replaces the hard +25% cap; resolves v1 open question #3 (§5.2) | External review, adopted (strawman noted: v1 already flagged this as open question #3) |
| 6 | Authority-stratification invariant: manifest = presentation/interactivity metadata; keys = provenance-gated evidence; rects = UI metadata; marks from blueprint (§5.1) | External review, adopted as written-down invariant (design already operated this way) |
| 7 | **N-5**: no learner-model evidence re-weighting by mark provenance in v1 — rejected amendment recorded with rationale (§3) | External review, **rejected** (would change live Mode 2 behavior; learner-model ADR territory) |
| 8 | **TEACHER_VERIFIED tier rejected for v1** — no teacher-marking flow exists for paper runs; extensible enum instead (§5.4) | External review, **rejected** (speculative scope) |
| 9 | P0 stays Track A on one 4CH1 paper with incremental-curation probe; Track-B-first adjudicated with explicit fallback (§6) | External review, **partially adopted** |
| 10 | Verified corpus facts recorded (524 questions / 1,404 parts / 228 attested-key MCQs) replacing assumptions about pilot feasibility (header, §5.1, §6) | Repo verification, 2026-10-03 |

Restated-without-change (external review points already satisfied by v1, for the record): single ExamRunner shell shared across sources; no new core assessment model (N-2); draft manifests never interactive (N-4); console keys enter as gated candidates, not auto-live (R-6).
