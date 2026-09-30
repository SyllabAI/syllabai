# T-QSP3 — real primary topics for the 284 remaining ING-anchored questions — EXECUTED (2026-09-29)

**Authorization:** operator IM trace `1a0ebc845dcee229` — "now clear the
remaining 284 ING-anchored questions in one pass" — the named open item
T-QSP3 from the T-QSP2 and Task-68 close-outs. Agent-performed data repair
(Task-66/T-QSP2 class): fail-closed SQL on prod Neon, dry-run first, no code
change, no CI lane, no audit rows, teacher_validation_events 0 throughout,
no validation-state flips anywhere.

## Cohort (measured, not guessed)

Exactly 284 active questions carried a synthetic `ING-*` per-paper ingestion
anchor (`PastPaperIngestionService.createIngestionAnchor`, Master Spec §7) as
`primary_topic_node_id` — matching the Task-68 census 302 → 284 exactly, zero
drift. Profile: all 284 carry `question_spec_points` rows (exactly 1 PRIMARY +
335 SECONDARY total, AI_VALIDATED) and **zero `question_topics` rows**; 35 ING
anchor nodes across 65 paper refs (4CH0 cross-spec 2011-2019 legacy + 4CH1
2020-2025 batches); latest question-version states 278 VALIDATED / 6 SUGGESTED
(untouched — this task flips no states). Bank-wide: 946 active, 946/946
spec-point mapped.

## Derivation (mechanical, mirrors T-QSP2 / mapQuestionTopics §10)

PRIMARY topic = parent TOPIC of the question's PRIMARY spec point via the live
KG `knowledge_edges` PART_OF edges (SUBTOPIC → 4CH1-S% TOPIC); SECONDARY topics
= distinct parent TOPICs of the question's SECONDARY points, minus the primary
topic, cap 4, deterministic order (by first spec-point code). All 148 distinct
cohort spec points have exactly ONE PART_OF TOPIC parent — zero orphans, zero
multi-parent conflicts.

## Pre-write validation (4 independent layers, all green)

1. **Reproduction proof at scale:** for every active question already carrying
   a real primary topic row (the 69 wave-mapped by earlier house waves), the
   mechanical rule reproduces the existing primary topic **69/69 exactly** —
   zero disagreements (the Task-68 18/18 reproduction, generalized bank-wide).
2. **Independent stage-2 source:** repo KG explorer_blob.json @ resources main
   HEAD `4ad167376f` (separate PDF emitter) — primary 284/284 + secondary
   56/56 point→TOPIC parents agree with the live DB PART_OF edges; 0 mismatches,
   0 KG-missing entries.
3. **Title agreement:** all 28 distinct parent TOPIC codes/titles match the
   repo subtopics 1:1.
4. **Plan pinned:** `plan_tqsp3.json` sha256 5e50d067704525a7…; dry-run tx
   (full write set + in-tx asserts, then ROLLBACK) passed before the commit run.

## Execution — single fail-closed tx, dry-run ROLLBACK then COMMIT

284 guarded primary-topic UPDATEs (`… WHERE id=%s AND
primary_topic_node_id=<ING anchor node> RETURNING` semantics, rowcount must be
exactly 1 each — any concurrent interference aborts) + 340 `question_topics`
INSERTs (284 primary + 56 secondary, uuid-pk, NOT-EXISTS-guarded). In-tx
asserts ALL GREEN: ING census 284 → 0 bank-wide; question_topics 766 → 1106
(exact); question_spec_points unchanged 2578; every cohort question carries
exactly one primary topic row with the planned code; bank-wide primary-row
distribution moves exactly {0: 877, 1: 69} → {0: 593, 1: 353} (the 593 zero-row
remainder = the known sme-corpus orphan pool, untouched); every row this tx
inserted references a real 4CH1-S% TOPIC; zero `question_topics` rows
reference ING anchors bank-wide (pre-existing non-TOPIC secondary rows from
earlier waves — 9 rows WCH11/4CH1-PR/4CH1-1.x — observed, untouched, out of
scope).

## Verification — 3 layers, VERIFIED

1. **DB (fresh read-only connection):** ING-anchored active **0** (was 284);
   qt 1106; qsp 2578; zero ING refs in question_topics; per-question primaries
   vs plan 284/284, per-question rowcounts vs plan 284/284; distribution
   {0: 593, 1: 353}; bank active 946.
2. **Serve path (prod API, fresh probe learner):** GET /exam-papers on 6
   papers spanning the cohort — 5 papers render 55 questions, ALL with
   specPoints; 1 paper (4ch1/past-papers/2023-06/4CH1-2CR) honestly SKIP
   (no exam_papers row — docs-only bank axis, recorded not failed).
3. **Evidence path (prod e2e, fresh probe learner):** structured attempt +
   full self-mark on repaired `4ch1/past-papers/2022-01/4CH1-2C#q1`
   (primary 4CH1-S4-d) → evidenceFired=True → /learners/me/state carries
   skillStates **4CH1-S4-d (TOPIC)** — the REAL topic anchor, the delta this
   repair exists for — + spec points 4CH1-4.23 / 4.25, and NO ING-* state.
   A second probe (2022-01 4CH1-1C#q4 → 4CH1-S2-c "Gases in the atmosphere")
   confirmed the same delta on a different paper family.

## Observations (no action taken)

- Probe learners: 4 disposable registrations created across verification runs
  (2 full e2e attempts fired; one mid-timeout recovery). Probe data only.
- Self-mark marksTotal vs awarded discrepancy on some probes (e.g. 13/8,
  19/12, 10/7) = the known parent/child part-sum artifact (Task-54 class:
  parent parts double-count leaf children in DB marks columns) — evidence
  path unaffected (evidenceFired on every full self-mark). Not this task's
  scope; recorded for the data-lane ledger.
- The 593 sme-corpus orphan questions remain active with no topic rows (their
  topic evidence runs off `primary_topic_node_id`, which they carry) — a
  separate, previously-known pool, untouched here.
- `ING-*` anchor knowledge_nodes remain in the KG (104 before this repair;
  none referenced by questions or question_topics any more) — anchor cleanup
  is out of scope for a data repair (Master Spec §7 placeholders by design).

## Files

`plan_tqsp3.json` (full per-question derivation + census + pins) ·
`verify_tqsp3.json` (3-layer verification record) · `SHA256SUMS`

**T-QSP3 is CLOSED: bank-wide ING-anchored active questions 284 → 0.**
