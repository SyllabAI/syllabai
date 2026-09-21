# T-ARCHIFY Split-2 Evidence Report — assessment & marking + ingestion subsystem diagrams

**Date:** 2026-09-22
**Task:** T-ARCHIFY (stage 3 — continuation of the per-subsystem split; operator: "Proceed with next, and also push")
**Diagrams:**
- `docs/archify/syllabai-assessment-marking.html` (interactive, self-contained)
- `docs/archify/syllabai-ingestion-pipeline.html` (interactive, self-contained)
**IR sources:** `docs/archify/syllabai-assessment-marking.archify.json`, `docs/archify/syllabai-ingestion-pipeline.archify.json`

---

```text
CONTEXT
- Operator directive chain: T-ARCHIFY (overview) → T-ARCHIFY-SPLIT (learning
  loop + retrieval) → "Proceed with next, and also push". The recorded next
  step of the split plan was the two remaining core subsystems; the push of
  the two unpushed archify commits (ad140e0, becaacf) was executed FIRST,
  before this round's authoring began (6df88d3..becaacf tc17-rec -> tc17-rec).
- Both diagrams are `architecture` type (schema v1) because Archify verifies
  repository evidence (--repo-root) for architecture only.
- Node lists are derived from the code sweep below — not copied from the
  conceptual architecture documents (the standing T-ARCHIFY rule).

VALIDATION & DELIVERY (showcase profile)
- assessment & marking: validate PASS (all artifact checks; final composition
  metrics: 0 proper crossings, 0 ambiguous corridors, 0 label-clearance
  issues, min projected node text 6.14 px ≥ 6 px at 1440);
  deliver PASS — spec sha256 83a212ba632f934505c0c160a630dd2ca1a9a9bae4c44c965e66adf0597b4f4c
  (15,033 B) → artifact sha256 fe5ca322d9712030f83af77178e1aa4e7384f365554f4acec5edf2f2a9a57310
  (828,187 B, self-contained); evidence verification PASS — 25 source
  references verified at syllabai-core @ 14b5e3d780956b39267bce2a8b831865ca4f89bb
- ingestion pipeline:   validate PASS (same gate; 0 crossings, 0 corridors,
  0 label issues);
  deliver PASS — spec sha256 2d0a4a150aa58981ee1077a970f5f42f2a45dba3c00e3d6a308660410730465d
  (15,270 B) → artifact sha256 4f2b0341b53e090c87311bac240a6367a4a2b8502232ff349f688d8523b2dfae
  (829,354 B, self-contained); evidence verification PASS — 27 source
  references at the same pin
- Geometry notes: both compositions were restructured during validation —
  the κ gate moved to the row-2 center so the human/smart pairing edges and
  the bank→smartmark lane use separate corridors; the ingestion over-the-top
  curriculum route was lifted clear of the region border (container-border-run
  diagnostic) and the canonical-truth security group was pulled inside the
  viewBox. All repairs were diagnosed by the validator, one subject at a time.

NODE COVERAGE — ASSESSMENT & MARKING (12 nodes)
- syllabai-web — Teacher: NO sources — cross-repo text-cited in a card
  (marking queue v2 surface; Archify verifies one repository per diagram)
- teacher marking API: TeacherMarkingController.java:44 (/api/v1/teacher/marking),
  :104 (queue-v2), :133 (smart-mark-batch)
- marking queue service: TeacherMarkingQueueService.java:49, :84 (markingQueue),
  :240 (smartMarkBatch) — tag "pilot-scope (ADR-027)": the queue reads globally
  under the documented ADR-015 shortcut; enrollment-scoped reads are bound to
  the classroom-lane milestone
- Smart Mark engine: SmartMarkService.java:41, :106 (VALIDATED-only selection,
  V34 gap G-2), :185 (SCHEME_NOT_VALIDATED honest refusal row)
- LLM failover chain: LlmChainProperties.java:64 (groq → gemini → openrouter),
  LlmMarkingCandidateGenerator.java:58 (chain.generate, prompt v2 with
  scheme generalGuidance — gap G-3)
- authoritative human marks: TeacherMarkingService.java:85 (recordHumanMark),
  HumanMark.java:45 (perPointDecisions jsonb {markPointId: 0|1})
- κ agreement gate (security): KappaAgreementService.java:22 (cohenKappa),
  SmartMarkAgreementEvaluation.java:23 (DEFAULT_THRESHOLD = 0.60, recorded
  per row; passed = kappa >= threshold)
- Smart Mark release: SmartMarkService.java:136 (authoritative =
  kappaGatePassed), StudentSmartMarkService.java:95 (reveal policy
  VALIDATED_ONLY; withheld scheme → 409)
- learning evidence (messagebus): EvidencePublisher.java:46 (publishGraded,
  exactly once at first authoritative marking), TeacherMarkingService.java:110
  (override revises marks, never re-fires evidence) — DECISION_016
- teacher content review: ContentReviewService.java:243 (scheme.validate),
  MarkScheme.java:125 (a FLAGGED scheme never backs marking)
- question bank & schemes: Answer.java:34 (PENDING → SMART_MARKED →
  HUMAN_MARKED lifecycle; full state names also in a card),
  MarkScheme.java:32 (SUGGESTED/VALIDATED/REJECTED/FLAGGED)
- SME package ingest: SmeQuestionIngestService.java:111 (package ingest),
  :165 (schemes arrive VALIDATED — human-authored exception)
Edges: human marks reach the κ gate as perPointDecisions; smart breakdowns
reach it as validation-passed results; the gate releases AI marks
(κ ≥ 0.60, security-variant edge). Human marks fire evidence directly
(bypass drawn explicitly). The bank feeds Smart Mark with the
"VALIDATED only (G-2)" edge.

NODE COVERAGE — INGESTION & CONTENT PIPELINE (12 nodes)
- past-papers corpus: SOURCE DATA (no sources — not code)
- syllabai-parser — pdflane: NO sources — cross-repo text-cited
  (engine 1.1.1 @ parser eef89fb: canonical 1.0 bridge + retrieval headers);
  the normalized-papers repo of record (syllabai-pastpapers @ 6354773) is
  cited in the same card
- GlmOcr bridge (T-C02): GlmOcrIngestionService.java:27 (one pair, one
  transaction, one entry point), ContentIngestionService.java:25 (T-013
  validate → checksum dedup → JSONB → deterministic chunks, never embeds),
  GlmOcrBridgeRecord.java:36 (V13 — reconciliation preserved verbatim,
  nothing discarded)
- curriculum bridge (T-010): CurriculumIngestionService.java:21, :28
  (prerequisite edges are never derived), :30 (idempotent provenance
  fingerprint)
- paper ingestion (T-011): PastPaperIngestionService.java:40 (everything
  SUGGESTED + UNVALIDATED ingestion-anchor topic), :46, :78 (ingest)
- question bank: ExamPaper.java:24 (papers + validation states),
  MarkScheme.java:32
- Educational KG: ConceptGraphSeedService.java:24 (V15 SHA-256-pinned seed),
  KnowledgeNode.java:25 (UNVALIDATED/SUGGESTED/VALIDATED),
  KnowledgeEdge.java:55 (per-row validation_status)
- curriculum truth (canonical): CurriculumVersion.java:20 (DRAFT/ACTIVE),
  CurriculumScopeResolver.java:41 (4CH1-2017 serving-scope reality,
  DB-verified comment)
- SME package ingest: SmeQuestionIngestService.java:111, :165, :206
  (QuestionSpecPoint mapping)
- teacher content review (security node, the only promotion):
  ContentReviewService.java:53, :138 (paper.validate), :243 (scheme.validate)
- content corpus & chunks: Document.java:26,
  ContentIngestionService.java:65 (V33 Embedding-v2 identity mirror) —
  tag "ingestion paused" (ops state, pending Embedding v2)
- pgvector semantic lane (dashed): EmbeddingConfig.java:19 (exactly one
  provider by design), :47 (vector(768), migration V11),
  ContentDocumentController.java:87 (/embed re-runnable) — tag
  "PREPARED · UNVERIFIED"
Boundary: red security group "Canonical truth — runtime surfaces never
write" wraps curriculum truth + the KG. The retrieval serving side is
pointed to by card (syllabai-retrieval-architecture.html), not duplicated.

TRUTH BOUNDARIES ENFORCED ON-CANVAS
- Ingestion/review are the ONLY writers of canonical curriculum truth and
  KG state; runtime surfaces (learner model, Smart Mark, chat) never write
  them — drawn as the security group.
- Everything ingestion creates lands SUGGESTED/UNVALIDATED with provenance;
  only teacher/SME review promotes; flagged never backs marking.
- The semantic lane stays PREPARED · UNVERIFIED and paused; no serving
  claims are made for it on this diagram.
- No κ value is claimed anywhere; the threshold semantics (≥ 0.60 recorded
  per row) are drawn, the calibration itself remains the operator's run.

BROWSER EVIDENCE (mixed, recorded honestly)
- visual-check COMPLETED for the ingestion artifact (Playwright Chromium
  1243 via ARCHIFY_CHROME): status fail, diagnostics =
  viewer/viewport-overflow with overflowY true at 1440/1600/1920 (light)
  — overflowX FALSE at every checked viewport/theme; scrollHeight 1368/1450/
  … is the conclusion-card document flow, the same accepted first-screen
  shape as the overview and the §7 split diagrams. The fail status is
  recorded in the committed sidecar, not suppressed. Dark/light captures
  at 1440x900 and 2048x1320 were produced by the same run and perceptually
  reviewed (all nodes, region, security group, labels, guided views,
  cards render; dark theme legible).
- visual-check for the assessment artifact remained environmentally
  unstable: attempt 1 Chrome-unavailable, attempt 2 Runtime.evaluate
  15000 ms timeout, attempt 3 Page.captureScreenshot failure. The last
  receipt is committed as syllaabi note below; per the delivery contract
  this is reported as environmental, not a pass.
- Manual Playwright evidence (tools/round2-manual-browser-evidence.json +
  tools/visual_evidence_round2.py): horizontal containment EXACT
  (scrollWidth == innerWidth) at 1440x900 / 1600x1000 / 1920x1080 / 2048x1320
  on both diagrams; all 14/14 needle labels found per diagram; all four
  guided-view chips render per diagram; full-page screenshots at 1440 and
  1920 perceptually reviewed (assessment-marking fits the viewport entirely
  at 2048x1320: scrollHeight 1320 == innerHeight).

COMMITS
- (this round) tc17-rec: docs(archify) — two HTMLs, two IR sources, evidence
  report, tools sidecars, ARCHIFY_INTEGRATION.md §8 + file table, first
  archify session entries in PROGRESS.md/WORKLOG.md.
```
