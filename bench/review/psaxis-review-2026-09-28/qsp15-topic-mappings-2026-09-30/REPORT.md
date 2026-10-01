# qsp15 — real topic mappings for the 15 new ING-anchored questions — EXECUTED (2026-09-30)

**Authorization:** operator IM trace `1a0f2abd20df8e6d` — "Proceed with the 15 new
ING-anchored questions' topic mappings" — the recorded sibling-supersession
follow-up ("the 15 new questions join the next topic-mapping pass (Jan-2021
rows' path via Task 68/69)"). Agent-performed data repair (Task-66/T-QSP2 class):
fail-closed SQL on prod Neon, dry-run first, no code change, no CI lane, no audit
rows, `teacher_validation_events` 0 throughout, no validation-state flips anywhere.

## Cohort (measured, not guessed)

Exactly **15 active questions** carried synthetic `ING-*` per-paper ingestion
anchors as `primary_topic_node_id` — matching the Task-70 supersession output
with zero drift: **8 × `4ch0-2c-201701#qN`** (4CH0/2C Jan 2017, anchor
`ING-4CH02CJANUARY2017`) + **7 × `4ch1/past-papers/2020-01/4ch1-2CR#qN`**
(4CH1/2CR Jan 2020, anchor `ING-4CH12CRJANUARY2017` → `ING-4CH12CRJANUARY2020`),
both papers VALIDATED pdflane drafts, latest versions all VALIDATED v1, marks
multisets [5,6,8,5,8,13,7,8]=60 and [6,9,6,7,13,15,14]=70 (print-exact per the
Task-70 arithmetic gates). Profile: **zero `question_spec_points` rows, zero
`question_topics` rows** → the full two-part assignment (T-QSP2 semantics) was
required. Bank-wide ING-anchored active before this pass: exactly 15 (the
T-QSP3 promise "284 → 0" had held). Bank active 961 = 946 + 15.

## Derivation (content-grounded, mirrors T-QSP2 §10 mapQuestionTopics semantics)

- **Spec points:** PRIMARY = dominant assessed point (largest mark block,
  framing tie-break); SECONDARY = substantively assessed supporting points
  (max 4); grounded in the posted draft packages
  (`bench/review/validated-supersession/{4ch0-2c-201701,4ch1-2cr-202001}`,
  byte-pinned by the Task-70 SHAs) + live stems / 92 part prompts / 75 mark
  points vs the live 182-node 4CH1 vocabulary; 4CH0→4CH1 cross-spec per house
  practice. 59 rows = 15 PRIMARY + 44 SECONDARY, `AI_VALIDATED`.
- **Topics:** PRIMARY topic = parent TOPIC of the PRIMARY spec point via the
  live KG `knowledge_edges` PART_OF edges; SECONDARY topics = distinct parents
  of SECONDARY points minus primary, cap 4, deterministic order (by first
  spec-point code). 36 rows = 15 primary + 21 secondary.
- Full per-question grounding notes are pinned in `qsp15_plan.json`
  (sha256 `bc57e0fe…575a0`). Every referenced point has exactly ONE PART_OF
  TOPIC parent (zero orphans, zero multi-parent conflicts).

## Pre-write validation (4 independent layers, all green)

1. **Reproduction proof bank-wide:** for every active question carrying both a
   qsp PRIMARY row and a real (non-ING) TOPIC primary anchor, the mechanical
   rule reproduces the existing anchor **852/852 for the past-paper families
   (0 non-sme disagreements)**; the 94 disagreements are all pre-existing
   `sme-eq-*` corpus-lane anchors (SME-import judgment vs bank qsp rows, a
   previously-known unreconciled pool) — untouched, out of scope, recorded.
   Additionally 0 bank-wide conflicts between qt primary rows and question
   anchors.
2. **Independent stage-2 source:** repo KG `explorer_blob.json` @ resources
   main HEAD `8430547fcf` — all 59 referenced points' point→TOPIC parents agree
   with the live DB PART_OF edges (59/59, 0 mismatches, 0 KG-missing).
3. **Archived house cross-check (2c-201701):** the Task-70 undo record's 12
   topic rows (created 09-14 on the legacy glmocr rows, content-matched by
   stem) agree 6/8 on primaries and 2/4 on secondaries; the 2 primary
   divergences (2017 q2 → S1-d via 1.20; 2017 q6 → S3-a via the 6m energetics
   block) are the documented point-grounded supersessions of topic-only legacy
   judgments, each recorded in the plan's grounding notes.
4. **Plan pinned:** `qsp15_plan.json` sha256 `bc57e0fe…575a0`; dry-run tx
   (full write set + in-tx asserts, then ROLLBACK) passed before the commit run.

## Execution — single fail-closed tx, dry-run ROLLBACK then COMMIT

15 guarded primary-topic UPDATEs (`… WHERE id=%s AND primary_topic_node_id=<ING
anchor>`, rowcount exactly 1 each) + 59 NOT-EXISTS-guarded `question_spec_points`
INSERTs + 36 NOT-EXISTS-guarded `question_topics` INSERTs. In-tx asserts ALL
GREEN: ING census 15 → 0 bank-wide; qsp 2578 → 2637 (exact); qt 1094 → 1130
(exact); every cohort qsp node a real `4CH1-1.x` SUBTOPIC and every cohort qt
node a real `4CH1-S%` TOPIC; exactly one PRIMARY row per cohort question in both
tables with the planned codes; bank-wide primary-row distribution moves exactly
{0: 593, 1: 353} → {0: 593, 1: 368}. No state flips, no audit rows,
`teacher_validation_events` 0.

## Verification — 3 layers, VERIFIED (fresh connections)

1. **DB (fresh read-only connection):** ING-anchored active **0** (was 15);
   qsp 2637; qt 1130; zero ING refs in question_topics; distribution
   {0: 593, 1: 368}; per-question primaries vs plan 15/15; per-question
   rowcounts vs plan 15/15; bank active 961.
2. **Serve path (prod API, fresh probe learner):** GET /exam-papers on both
   supersession papers — 2CR Jan-2020 renders 7/7 questions and 2C Jan-2017
   renders 8/8 questions, **ALL with specPoints** (before this pass: none —
   the cohort had zero qsp rows).
3. **Evidence path (prod e2e, fresh probe learner):** structured attempt +
   full learner self-mark (reveal-and-self-mark surface) on
   `4ch0-2c-201701#q1` → self-mark **5/5** → evidenceFired=True →
   /learners/me/state skillStates carry **4CH1-S1-b (TOPIC) "Elements,
   compounds and mixtures"** — the REAL topic anchor, the delta this repair
   exists for — + secondaries 4CH1-S2-h/S2-e/S2-b (TOPIC) + spec points
   4CH1-1.8 / 2.44 / 2.5 / 2.23C, and **NO ING-* state**.

## Observations (no action taken)

- 3 disposable probe learners were created across the verification runs (1
  full e2e attempt + 2 shape probes; the final L3 record's learner is
  `qsp15.probe.f7da35ab@example.com`). Probe data only.
- 2CR q7's draft stem is empty (known stem-chrome/thinness family); the
  mapping is grounded in its parts + mark points.
- The 94 sme-corpus L1 disagreements pre-date this task and remain a
  data-lane item for whichever lane owns the SME import anchors.
- `ING-4CH12CRJANUARY2020` / `ING-4CH02CJANUARY2017` anchor nodes remain in
  the KG as unreferenced placeholders by design (Master Spec §7; anchor
  cleanup out of scope for a data repair).

## Files

`qsp15_plan.json` (derivation + per-question grounding + census + pins) ·
`qsp15_run.json` (commit record) · `qsp15_verify.json` (3-layer verification
record) · `qsp15_probe_out.json` (raw SELECT-only probe census) · `SHA256SUMS`

**qsp15 is CLOSED: bank-wide ING-anchored active questions 15 → 0 (T-QSP2/68/69
program complete — the bank's entire active past-paper question set now carries
real primary topics + spec-point mappings).**
