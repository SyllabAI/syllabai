# T-QSP2 — real primary topics + spec-point mappings for the 51 ING-anchored questions (2026-09-29)

Trace: `1a0eaa53be2628f5` · operator ask: "assign those real primary topics +
mappings" (the named open item T-QSP2 from the qsp-repair disposition) ·
mechanics: Task-66 class (fail-closed SQL on prod Neon, dry-run first, data
repair only — no code change, no CI lane).

## Cohort identification (measured, not guessed)

Bank active = 946. `question_spec_points` coverage after the 09-29 qsp-repair:
895/946 mapped; the 51 unmapped ALL carry synthetic `ING-*` per-paper ingestion
anchors (`PastPaperIngestionService.createIngestionAnchor`, Master Spec §7
"pipeline never guesses curriculum placement") as `primary_topic_node_id`.
Landing census: 09-24 ×12, 09-25 ×13, 09-26 ×19 (4CH1/1CR Jun-2024 + 4CH1/2CR
Jun-2024 full papers), 09-28 ×7 (4CH1/2C Jan-2021 full paper). All STRUCTURED,
provenance PAST_PAPER, spread over 21 papers. The 09-26 mapping wave gave
spec-point mappings to same-paper siblings but never remapped primaries.

## Two-part assignment (mirrors `ContentReviewService.mapQuestionTopics` §10
semantics — real TOPIC primary + question_topics rows — plus spec-point
mappings in the qsp-repair style)

- PRIMARY spec point = dominant assessed point (largest coherent mark block,
  ties broken by the framing/first part); SECONDARY points = substantively
  assessed supporting points (max 4) — grounded in each question's stem, 350
  part prompts and 283 mark points against the live 194-node 4CH1 SUBTOPIC
  vocabulary (evidence pack: scripts/qsp_tqsp2_evidence.json; derivation per
  question recorded in qsp_tqsp2_plan_resolved.json).
- PRIMARY topic = parent TOPIC of the PRIMARY point (mechanical, from the
  canonical KG `pointSubtopics` hierarchy); SECONDARY topics = distinct parent
  TOPICs of the SECONDARY points (cap 4, mapQuestionTopics cap-5 spirit).
- 4CH0→4CH1 cross-spec mapping continues per house practice (2012-2C q1/q2,
  2014-2C q7, 2019-1C q4 mapped against the 4CH1 vocabulary like their mapped
  siblings).

## Execution

`scripts/qsp_tqsp2_execute.py` — single fail-closed transaction: 51 guarded
primary-topic UPDATEs (only while the current primary is still an ING-
anchor), 120 `question_topics` rows (51 primary + 69 secondary, uq-guarded,
expected-zero deletes asserted), 189 `question_spec_points` rows (PRIMARY +
SECONDARY, NOT-EXISTS-guarded, provenance/validation_state AI_VALIDATED).
In-tx asserts: 51 refs on real 4CH1-S% TOPIC nodes, exactly one primary row
per question in both tables, row-deltas exact, all new spec-point nodes live
4CH1 SUBTOPICs, all new topic nodes 4CH1 TOPICs, bank-wide active unmapped 0,
ING census 353 → 302. Dry-run ROLLBACK then COMMIT: table 2389 → 2578 (qsp),
625 → 745 (question_topics).

## Verification (all green)

1. DB post-commit: bank-wide active unmapped **0** (was 51); ING-anchored
   active 353 → 302 (the remaining 302 are the already-spec-point-mapped
   questions still on anchors — named open item **T-QSP3** below).
2. Serve path (prod API, fresh probe learner): `GET /exam-papers/{id}`
   exposes the planned specPoints on 12 spot-checked repaired questions
   across 6 papers spanning all 4 landing days (4CH0/2C Jan-2012, 4CH1/1C
   Jan-2020, 4CH1/2C Jan-2021, 4CH1/1CR + 2CR Jun-2024, 4CH1/2C Nov-2025) —
   ALL PASS, indistinguishable from house-mapped siblings.
   `scripts/qsp_tqsp2_api_verify.py`.
3. Evidence path (prod, end-to-end): fresh learner → structured attempt +
   full self-mark on the repaired 4CH1/2CR Jun-2024 q2 (was
   ING-4CH12CRJUNE2024) → evidenceFired=True → `/learners/me/state` carries 4
   skillStates: **4CH1-S1-c "Atomic structure"** (the REAL topic anchor — the
   delta vs the qsp-repair e2e, whose topic row was still the invisible ING
   anchor) + SUBTOPIC 4CH1-1.16 PRIMARY / 1.15 / 1.17 SECONDARY at mastery
   0.357. The topic-level evidence now paints in the KG instead of firing
   into a disconnected placeholder. `scripts/qsp_tqsp2_e2e_evidence_probe.py`.

## Observations recorded (no action taken)

- **T-QSP3 (new named open item): 302 mapped questions still carry ING-*
  primary topics** (bank-wide 353 ING-anchored − the 51 repaired). Their
  spec-point evidence already paints; their topic-level evidence still fires
  at disconnected placeholder nodes (invisible to the KG + practice scope).
  Same mechanical derivation as this repair (parent TOPIC of the PRIMARY
  spec point) can clear them in one pass.
- 104 `ING-*` anchor nodes remain in knowledge_nodes (placeholders by design,
  Master Spec §7); anchor cleanup/outlining is out of scope for a data repair.
- Durability note: the 09-26/09-28 batch stems carry page furniture ("DO NOT
  WRITE IN THIS AREA") from the PDF extraction; content still fully readable,
  mapping unaffected (same recorded shape as earlier batches).
