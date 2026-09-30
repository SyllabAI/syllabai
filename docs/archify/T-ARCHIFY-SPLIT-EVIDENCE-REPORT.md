# T-ARCHIFY Split Evidence Report — learning-loop + retrieval subsystem diagrams

**Date:** 2026-09-21
**Task:** T-ARCHIFY (stage 2 — split of the 27-node overview into per-subsystem diagrams)
**Diagrams:**
- `docs/archify/syllabai-learning-loop.html` (interactive, self-contained)
- `docs/archify/syllabai-retrieval-architecture.html` (interactive, self-contained)
**IR sources:** `docs/archify/syllabai-learning-loop.archify.json`, `docs/archify/syllabai-retrieval-architecture.archify.json`

---

```text
CONTEXT
- Operator directive: split the overview into a learning-loop diagram and a
  retrieval diagram; both must carry source-backed evidence and explicit
  status, not a copy of the conceptual architecture from documentation.
- Both diagrams are `architecture` type (schema v1) because Archify verifies
  repository evidence (--repo-root) for architecture only; workflow/dataflow
  reject it.

VALIDATION & DELIVERY (showcase profile — achieved by the split)
- learning loop:  validate PASS 9/9, 0 errors, 0 warnings;
  deliver PASS — spec sha256 64d13a3db9aa64b4ecef36e1491f1d17802712e965f96fb69a4e0ffa2ecaf423
  (11,625 B) → artifact sha256 962bf8a599600e55f2ef451bd832fa62f752d8ad53ca4e809829f19ff27151e8
  (825,188 B, self-contained); evidence verification PASS — 22 source
  references verified at syllabai-core @ 14b5e3d780956b39267bce2a8b831865ca4f89bb
- retrieval:      validate PASS 9/9, 0 errors, 0 warnings;
  deliver PASS — spec sha256 60945d3e6e29aec3f253faa4a0302c03ba9f90bbb19e48d565dc3505bc4da5e9
  (12,120 B) → artifact sha256 30a8d291398ae013ed93a9183e3d5e267922dfef1c05f04c7342d6c13bddc7c9
  (826,227 B, self-contained); evidence verification PASS — 23 source references at the same pin
- The split achieved showcase quality (first-screen projected text ≥ 6 px at
  1440 px), which the 27-node overview could not satisfy (it remains standard).

NODE COVERAGE — LEARNING LOOP (11 nodes; every node code-anchored unless stated)
- curriculum & specification: CurriculumScopeResolver.java:46, CurriculumController.java:21 (IMPLEMENTED, canonical)
- learner interaction (web): NO sources — cross-repo syllabai-web @ bfc9850
  (PracticeView.tsx, TutorChatView.tsx, NextBestActionsCard.tsx), text-cited in
  a card (Archify verifies one repository per diagram)
- interaction capture: AttemptController.java:24 (/api/v1/attempts),
  TutorController.java:21 (/api/v1/tutor), TutorEngagementRecorder.java:32
- assessment & Smart Mark: Answer.java:32, SmartMarkService.java:84 (markAnswer),
  SmartMarkPipeline.java:57 (IMPLEMENTED · κ-gated release)
- κ agreement gate: KappaAgreementService.java:22 (cohenKappa),
  SmartMarkService.java:207 (kappaGatePassed) — security node, fail-closed,
  gate closed (no passing calibration on file)
- learning evidence: EvidencePublisher.java:46 (publishGraded),
  AssessmentEvidenceRecordedEvent.java:36 — fires once at first authoritative mark
- governed learner model: LearnerModelService.java:72 (@Order(10) listener),
  bkt/BktEngine.java:36 — overlay on canonical nodes
- learner patterns: StruggleInferenceService.java:54 (@Order(100), reads the
  POST-UPDATE model by documented listener order), :38 (rules-v0.2)
- remediation: TutorPolicyService.java:55 (select), :97 (InterventionType incl.
  MISCONCEPTION_REMEDIATION / PREREQUISITE_REVIEW), InterventionRunService.java:38 —
  tag "run ledger not wired" (grep-verified: zero callers outside its package)
- deterministic NBA: NextBestActionService.java:76, :78 (nba-rules/v1.3)
- next action API: LearnerRecommendationController.java:29
Loop closure drawn: next_action → learner_web (NextBestActionsCard).
Human-marks bypass drawn explicitly: assessment → evidence "human marks ·
always authoritative" (top edge, bypasses κ gate per DECISION_016).

NODE COVERAGE — RETRIEVAL & GROUNDED AI (12 nodes, all syllabai-core)
- query understanding: KaRagService.java:89 (ask), StructuredRetrievalQuery.java:38 —
  deterministic intent, no LLM entity invention (KaRagService javadoc §18 contract)
- curriculum resolution: CurriculumScopeResolver.java:46 — fail-closed T-C07
- authoritative KG: GraphKnowledgeRetriever.java:77, KnowledgeGraphService.java:25,
  AuthoritativeKgRetrievalProvider.java:16 — SERVING
- semantic vector leg: ContentVectorRetriever.java:45 (cosine floor 0.15 at :33,
  honest degradation to empty at :59-64), ContentRetrievalService.java:35 —
  "degrades to KG-only" (ingestion paused pending Embedding v2)
- rank fusion: ReciprocalRankFusion.java:22 — RRF k=60, SERVING
- reranking: EvidenceReranker.java:11 + NoReranker.java:17 — honest "no-op v0"
  (KaRagService.java:117 comment: "v0: NoReranker keeps the fused order")
- evidence selection: KaRagService.java:118 (cap), LearnerContextAssembler.java:37
- evidence sufficiency: KaRagService.java:126 (grounding gate — empty evidence ⇒
  deterministic refusal, no LLM call), EvidenceRequirements.java:25 — security node
- grounded AI: GroundedTutorGenerator.java:37, KaRagService.java:33,
  ClaService.java:86 — tag "KaRAG UNVERIFIED" (code at pin, no verification battery)
- citation validation: SimpleCitationResolver.java:22, CitationResolver.java:29 —
  citations resolve only from surviving evidence; no free-floating claim path
- lexical BM25 arm: Bm25Retriever.java:45 — "NOT SERVED" (T-C13 benchmark-gated;
  its own javadoc: "BM25 enters the served fusion only if the T-C13 benchmark
  promotes it")
- multi-arm fabric: RetrievalFabric.java:102, BoundaryPolicy.java:29 — "UNWIRED"
  (deliberately not a Spring bean; grep-verified zero consumers; "Until that
  promotion lands, nothing consumes this class")
Prepared arms are a separate dashed region — visually disjoint from serving.

EDUCATIONAL-TRUTH BOUNDARIES (enforced on-canvas, not implied)
- Curriculum canonical; learner model overlay-only (skill states keyed to
  canonical nodes) — loop diagram edges + card.
- Raw tutor chat never updates mastery: the ONLY mastery input drawn is the
  assessment-evidence event (@Order(10)); patterns listen afterwards (@Order(100)).
- Smart Mark never modifies curriculum truth (no edge from marking to curriculum).
- Authoritative KG ≠ retrieval-derived graph signals: LIL is PROPOSED and drawn
  NOWHERE in the retrieval serving path (stated in the Truth boundaries card).
- Retrieval is NOT PDF→chunks→embeddings→vector DB→LLM: scope-gated hybrid
  (KG + vector) fused rank-only, capped, deterministic refusal — stated verbatim
  in the card; BM25/fabric drawn as built-but-not-serving.
- LLMs generate from assembled context only; never mark, never own truth.
- sufficiency→generator edge intentionally unlabeled: admission-on-pass is the
  gate's contract; refusal documented in card + report (semantic authoring choice).

VISUAL EVIDENCE (honest record)
- Automated `visual-check` FAILED for both artifacts: Chrome DevTools
  Runtime.evaluate timed out after 15000 ms (same environmental limitation as
  stage 1; Playwright Chromium 1243 via ARCHIFY_CHROME). Sidecars committed:
  syllabai-learning-loop.visual-check.json, syllabai-retrieval-architecture.visual-check.json
  (status: fail, artifact sha pinned per receipt).
- Supplementary manual Playwright evidence (tools/visual_evidence_split.py →
  tools/split-manual-browser-evidence.json):
  * horizontal containment EXACT (scrollWidth == innerWidth) at
    1440×900 / 1600×1000 / 1920×1080 / 2048×1320 for both artifacts;
  * vertical document scroll present at laptop heights (conclusion cards below
    the diagram — same accepted shape as the committed overview);
  * screenshots (download/archify-shots/*1440x900.png) image-reviewed: all 11/12
    nodes, both regions, status chips, SRC markers, 3 guided views each, all 4
    cards render; loop closure edge and top bypass edge legible.

LIMITATIONS / NON-CLAIMS
- learner interaction (web) node is text-cited, not file:line-verified (one
  repository per diagram); its components were verified to exist in
  syllabai-web @ bfc9850 by directory inspection.
- No κ value, calibration, or benchmark claim is made anywhere; the gate is
  drawn closed and the vector leg is drawn degraded.
- Guided-view focus lists are navigation aids, not additional claims.
- The overview (standard) remains the canonical wide map; the two split
  diagrams are subsystem views at showcase quality — all three pin the same
  commit and agree on statuses.

STATUS
- T-ARCHIFY stage 2 (split): VERIFIED for validation/delivery/evidence;
  automated visual-check remains environmentally blocked (documented above).
```
