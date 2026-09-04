# WORKLOG.md — SyllabAI Chronological Work Log

## 2026-09-02 — Project pack bootstrap (external assistant)

**Task:** Establish canonical engineering context for SyllabAI.

**Completed:**
- consolidated research-paper concepts into the Master Technical Specification (v1.0);
- defined Java 25 + Spring Boot 4.1.x backend; Next.js 16 frontend on Vercel; Neon PostgreSQL + pgvector;
- defined multi-repository, modular-monolith architecture;
- added learner-model, diagnostic, Smart Mark, provenance, research, and experiment architecture;
- converted the feature inventory into a definitive project-management workbook (158 rows).

**Findings:** the full architecture is broader than a chatbot (learner model, assessment, diagnostics, KG, provenance, telemetry are equally structural); Paper B's storage proposal simplifies operationally to PostgreSQL + pgvector behind abstractions; specialist parsers belong behind contracts, not inside Java.

## 2026-09-03 — Verification, merge, and repository bootstrap

**Task:** Independently verify the v1.0 pack, merge corrections, and stand up the GitHub repositories.

**Completed:**
- verified platform claims with 7 fresh searches: Spring Boot 4.1.1 (Java 17-26) ✅, Spring Boot 3.x EOL 2026-06-30 ✅, Spring AI 2.0 GA (requires Boot 4.x) ✅, Next.js 16.3.3 Active LTS (2026-08-25 security release) ✅, Cloudflare R2 free tier no-credit-card ✅, Groq free tier ~14.4K req/day no-card ✅, **SurrealDB = BSL 1.1, NOT Apache-2.0 ❌ (v1.0 dossier error)**;
- merged pack → v1.1: free-LLM chain added (Groq → Gemini 2.5 Flash → OpenRouter, ADR-009); Cycle-1 pilot scope locked (ADR-010, Master Spec §39a); polyglot policy (ADR-011); 4 repos (ADR-012); license wall (ADR-013); SurrealDB struck everywhere;
- merged backlog → v2: 160 rows; ADDED F-159 decay job, F-160 learning-log telemetry, F-161 Smart Mark κ gate, F-162 timed-vs-untimed fluency gap, F-163 free-LLM chain; PATCHED 10 legacy rows (F-001 AWS→Render/Vercel/Neon, F-008 Celery→Spring jobs, F-020/F-032/F-033/F-034/F-039/F-040/F-122 stack-contradiction fixes, F-047 κ metric); removed blank rows F-110/112/114; added `Cycle` column (34 Cycle-1 rows, 12-spine);
- integrated 38-repo Java-fit analysis into `REPOSITORY_RESEARCH.md` section 0 (verdicts: USE-DIRECT opendataloader-pdf/os-taxonomy/Scientific-learning-skills/pdfcn/A11Y.md; OFFLINE mineru/surya/anydoc/pdf-inspector; REFERENCE DeepTutor/get-it/Understand-Anything/open-notebook; WATCH zvec/helix-db/pgcontext; STRUCK SurrealDB);
- created GitHub repositories (private): `syllabai`, `syllabai-core`, `syllabai-web`, `syllabai-parser`; pushed this pack to `syllabai` (main repo).

**Mistakes / regressions:**
- Mistake (inherited from v1.0, corrected): SurrealDB recommended as Tier-A "Apache-2.0" backend — verified BSL 1.1 and struck (ADR-013). Any future doc claiming permissive licensing of an external repo must cite the license text, not the dossier.
- Mistake (caught pre-merge): v1.0 backlog contradicted its own ADRs (Neo4j rows vs ADR-005 Postgres graph; Celery row vs ADR-001 Java; Pinecone row vs ADR-004). All fixed and marked `PATCHED v2`.

**Breakthroughs / useful insights:**
- opendataloader-pdf is Java + Apache-2.0 on Maven Central — runs in-process inside `syllabai-core`; no separate parsing service for text PDFs; bounding boxes feed the citation chain.
- Pilot LLM budget fits Groq free tier: 50 students × ~20 queries/day ≈ 1K req/day vs ~14.4K/day capacity.
- Nothing in the 38-repo set implements BKT/BDT/IRT/telemetry/Smart Mark — the scientific core is greenfield Java, which is exactly the course project's showcase.

**Open questions:**
- Exact Edexcel IAL Chemistry content licensing posture for a private pilot (fine; re-check before any public flip).
- Gemini 2.5 Flash free-tier stability at build time (re-verify).
- κ-gate marker capacity for double-marking (recruiting task, Wave 4).

**Next action:** TODO T-001 — bootstrap `syllabai-core` (Spring Boot 4.1 + Java 25 + Spring AI 2.0 skeleton).

---

## 2026-09-03 — Build session: Wave 0 + science core (T-001…T-018, T-020, T-023)

**Repos / commits:**

- `syllabai-core` @ `71f873d` — T-001…T-007 + T-012/T-014…T-018/T-020/T-023 (see core README "Implemented so far").
- `syllabai-web` @ `3c410ed` — T-005 Learner Workbench (login, practice, mastery map, my state).

**What landed:**

- Java 25 + Spring Boot 4.1.1 + Spring AI 2.0.1 modular monolith; 13-module package map per ADR-012.
- Flyway V1–V7: identity (roles/users/user_roles), curriculum + KG nodes/edges, question bank + attempts, learner states, research telemetry/registries, seed (Edexcel IAL Chemistry WCH11: 3 topics × 2 subtopics, 4 documented misconceptions, 8 MCQs with distractor→misconception tags, model registry v1-cycle1 rows).
- JWT auth + RBAC; springdoc OpenAPI; global error handling; GH Actions CI (JDK 25).
- Science: BKT engine (paper params, config + model_versions registry), BDT engine (prior 0.3), Ebbinghaus decay (τ 30/90/365 by band, floor, review threshold) + nightly job; evidence contract as domain events (Observer): attempts → `AssessmentEvidenceRecordedEvent` → learner model + telemetry.
- KG: recursive-CTE prerequisite closure, subtree, misconceptions; tree/prereq/misconception endpoints.
- LLM: `LlmProvider` port + Spring AI adapters + `FailoverLlmChain` (Groq → Gemini → OpenRouter, health/cooldown/failover, admin health endpoint) — app boots with zero keys.
- Storage: `ObjectStorage` port + local + R2 (S3 SDK) adapters.
- Web: single-page workbench, typed API client, mobile-first responsive, a11y, CI (lint + type-checked build).

**Mistakes / regressions (caught and fixed):**

- MISCONCEPTION_OF edge direction inverted in `KnowledgeEdgeRepository` query → misconceptions silently absent from trees; fixed + re-verified.
- Spring AI autoconfig requires keys at boot → excluded all model autoconfigs; manual provider construction.
- Unauthenticated requests returned 403 via the /error dispatch → permitted `/error` + explicit 401 entry point.
- BKT/BDT unit-test expected values initially wrong (my arithmetic, not the engine) — corrected against hand-computed posteriors.
- Web `apiPath()` double-`?` when the path already carried a query (tree 404) — fixed with `&`-aware separator.

**Verification:**

- `mvn verify`: 32/32 unit tests green.
- Live end-to-end smoke (portable Postgres 17.11 + `local` profile): login → tree → prerequisites (depth-3 chain) → wrong answer (BKT 0.1131, BDT 0.75 exact) → correct answer (0.3832) → telemetry rows; RBAC 401/403; OpenAPI reachable; browser-verified via agent-browser (login, quiz submit, misconception alert, mastery map, state views, mobile viewport).

**Next action:** Wave 1 — T-008/T-009 canonical format + opendataloader-pdf; T-010/T-011 ingestion; T-013 pgvector; then T-019/T-021/T-022.

## 2026-09-03 — Build session 2: code audit + fixes 1–3

**Task:** Independent code-level audit of the five repositories (external audit cross-checked line-by-line), then implement the three highest-risk audit findings in `syllabai-core`.

**Audit verdict (all 19 external findings verified true; 5 highest-risk):**
1. BDT `updateOnCorrect` was provably dead code — `misconceptionIds` assembled only from the *chosen* option, and correct options are never tagged (V7 seed).
2. `FailoverLlmChain.pinnedProvider()` returned `null` — experiment pinning claimed but not implemented (schema + config existed, nobody consulted them).
3. Telemetry emitted only 2 of the 6 event types declared in the V5 schema.
4. (lower priority, deferred) `SHORT_ANSWER` declared in schema but MCQ-only submission API.
5. (docs, deferred) Master Spec says 4 repositories; `Past-Papers` (public, 689 MB, IAL/IGCSE) makes 5.

**What landed (`syllabai-core` @ `508d95d`):**

- **Fix 1 — BDT evidence assembly:** `AssessmentEvidenceRecordedEvent` now carries `observedMisconceptionIds` (every misconception the item's distractors monitor) alongside the expressed list. `LearnerModelService`: correct answer weakens all monitored misconceptions (`updateOnCorrect`), tagged wrong answer strengthens the expressed one, untagged wrong stays neutral.
- **Fix 2 — experiment pinning, fail-loud:** new `ExperimentPinResolver` port; `PropertiesExperimentPinResolver` (`syllabai.llm.experiment-pins`, `"provider"` or `"provider:model"`) + `JpaExperimentPinResolver` (V5 `experiments` registry, `RUNNING` only, read-only entity) composed config-first. Unpinned experiment ids throw with a self-documenting message; pinned experiments never fail over; pinned model flows through a new `LlmRequest.model` field into Spring AI runtime options.
- **Fix 3 — full telemetry stream:** four new domain events (`MasteryUpdated`, `MisconceptionUpdated`, `DecayApplied`, `ReviewScheduled`) published by the learner model and the nightly decay job; `TelemetryService` persists them as `BKT_UPDATED` / `BDT_UPDATED` / `DECAY_APPLIED` / `REVIEW_SCHEDULED`. All six V5 event types now flow.
- Side-fix discovered while wiring: the decay job evaluated the review threshold by re-decaying the already-decayed stored value (double-decay) — now compares the effective mastery directly.

**Verification:**

- `mvn test`: **60/60 green** (was 32): +14 chain/pinning, +4 pin parsing, +6 learner model BDT wiring, +2 evidence assembly, +6 telemetry coverage, +3 decay-job events.
- Live end-to-end on Postgres 17 (portable, `local` profile): login → Q1 wrong (BDT 0.3→0.75) → Q1 wrong again (0.75→0.9545) → **Q2 correct weakened the monitored misconception 0.9545→0.875** (hand-checked exact) with `BDT_UPDATED` evidence `CORRECT_ANSWER`, `BKT_UPDATED` mastery 0.1131→0.3869; app boots with the `experiments` entity validated by Hibernate (`ddl-auto: validate`).

**Known follow-ups (audit items 4–5, deliberately deferred):** short-answer submission strategy, 5-repo topology doc refresh (Master Spec §3 + AGENT), T-016 wording, seeder password log line, localStorage→httpOnly cookie hardening.

**Next action:** Wave 1 — T-008/T-009 canonical document format + opendataloader-pdf; T-010/T-011 syllabus/past-paper ingestion; T-013 pgvector embeddings.

## 2026-09-03 — Build session 3: content/assessment fabric (T-008–T-011, T-019, T-021, T-022 + audit fix 4)

**Task:** Execute the next build phase with a content/assessment-first strategy (no tutor UI, no broad feature expansion): multi-part assessment model, Smart Mark pipeline with the κ agreement gate, timed/untimed conditions, ingestion bridge, Testcontainers CI, structured player.

**Repos / commits:**

- `syllabai-core` @ `b745bf4` (audit fix 4) → `003b6c0` (V8–V10 + services + 91/91 tests) → `1803988` (Testcontainers IT + CI).
- `syllabai-parser` @ `a43ad24` — T-008/T-009 recovered from the interrupted session and pushed (was local-only).
- `syllabai-web` @ `3b1b5cd` — structured question player + fluency-gap Δ.
- `syllabai` — this update (5-repo topology, T-016 wording, status).

**What landed:**

- **Audit fix 4 (in-flight when the previous session died):** experiment-pin model precedence — a caller-supplied model can no longer override a registered experiment's pinned model (§26.1 precedence: pin > caller model > provider default); `LlmResponse` now reports the model actually used so telemetry never misattributes pinned requests. 61/61 at the time.
- **V8 multi-part assessment model:** exam_papers, question_versions (immutable snapshots, SUGGESTED/VALIDATED lifecycle), question_parts, mark_schemes/mark_points (decomposition + teacher-authored acceptance criteria, JSONB), answers (per-part PENDING → SMART_MARKED → HUMAN_MARKED/OVERRIDDEN), smart_mark_results + human_marks (append-only), smart_mark_agreement_evaluations, attempts marking lifecycle + `evidence_emitted` single-fire guard, skill_states.procedural_fluency_gap. Existing MCQ flow unchanged; V7 seed MCQs backfilled as VALIDATED v1.
- **Smart Mark pipeline (Strategy + validators):** `MarkingCandidateGenerator` port (LLM adapter: pinned prompt v1, temp 0.1, strict-JSON parsing, temperature provenance) → deterministic validators (bounds: no invented/duplicate point ids; coverage: every in-scope point decided; mark-sum: awards ≤ scheme bound) → append-only `SmartMarkResult` with per-point breakdown (evidence + rationale) and failure codes. Blank answers short-circuit to a deterministic zero-mark decision — no LLM call, no hallucination surface.
- **κ agreement gate (F-161):** Cohen's κ over paired per-mark-point binary decisions (latest accepted smart run × latest human mark); degenerate-marginals convention documented (κ = 1 when pe = 1 and agreement perfect); threshold 0.60 recorded per evaluation row; **fail-closed** — no evaluation rows = gated. Pre-gate smart marks are provisional (never fire evidence); post-gate smart marks are authoritative; human overrides revise marks for research and never re-fire BKT.
- **Structured submission (audit item 4 closed):** POST /api/v1/attempts/structured — one answer per part of the current version, Paper B §3.5 fields, timed/untimed tag. Evidence fires exactly once at first authoritative marking; documented conservative correctness rule for partial credit (full marks = mastery evidence; raw marks ride in the event).
- **T-011 ingestion bridge:** parser's past-paper-draft.json (schema 1.0) → POST /api/v1/teacher/content/past-papers → exam paper + STRUCTURED questions + v1 versions + parts + scheme + points, all SUGGESTED, single transaction, idempotent (409 on paper+session re-ingest). Ingestion-anchor KG topic per paper (the pipeline never guesses curriculum placement); teachers remap during review. Teacher review workflow: review queue, validate/reject paper (all-versions-first guard), version, scheme (with atomic acceptance-criteria authoring).
- **Fluency gap (T-019, F-162):** skill_states.procedural_fluency_gap = untimed accuracy − timed accuracy over graded attempts per node, recomputed on evidence, null until both conditions observed. Exposed in /learners/me/state.
- **ServableQuestionSpec (Specification pattern):** unvalidated structured content never serves — the student API filters by active + current-version VALIDATED.
- **Testcontainers IT (CI):** `MultipartMarkingFlowIT` walks the whole loop on pgvector/pgvector:pg17 via @ServiceConnection; failsafe plugin; skipped locally without Docker (this sandbox), runs in CI. TC 2.0.5 coordinates (artifacts renamed testcontainers-junit-jupiter / testcontainers-postgresql).
- **Web:** structured player (per-part textareas, submit-for-marking, pending-marks panel), Δ fluency gap in My-state. Practice submit guard bug fixed (structured path blocked by the MCQ `chosen` guard).

**Mistakes / regressions (caught and fixed):**

- LazyInitializationExceptions on detached DTO access (open-in-view is intentionally false): fixed with the repo's established pattern — EntityGraphs on the lazy collections used by controllers + read-only FK mirror columns (question_id / question_version_id) so detached views read FKs without touching proxies. First attempt preferred the proxy (non-null even when detached) — corrected to prefer the mirror.
- Scheme validation NPE on `{}` body (missing @Valid + missing null-guard) — both added.
- `Map.copyOf` in TelemetryEvent rejects null payload values → NPE for null modelId/failureReason; handlers now omit null entries.
- My κ hand-computation in a test was wrong (expected −0.4; correct 0.0 for (1,1),(0,1) with human marginal 1.0) — fixed against the formula.
- Test pitfalls: entities without ids outside JPA (TestIds reflection helper), a mock EvidencePublisher that never flips the single-fire guard (switched to the real publisher in tests), event-index assumption in the override test (select last, not get(1)).
- Testcontainers 2.x artifact rename broke the pom (junit-jupiter → testcontainers-junit-jupiter) — BOM 2.0.5 + renamed coordinates.
- Session recovery: the previous session died mid-fix with the pin-precedence diff uncommitted and T-008/T-009 committed only locally — both recovered, tested, pushed. The portable Postgres data dir had been corrupted by the tmp cleaner (pg_notify missing) — re-initialized (dev data only, re-seeded via Flyway).
- A wedged backend instance (stuck OPTIONS/health requests after heavy e2e + a logback ThrowableProxy ClassNotFound in error dispatch) — resolved by restart; the fresh instance serves identical traffic correctly. Root not fully diagnosed; watch for recurrence.

**Verification:**

- `mvn verify`: **91/91 unit tests** (was 61; +30 κ hand-computed, pipeline validators, authority/gate, human-mark evidence + override, ingestion, structured submit, telemetry marking, servable spec) + IT correctly skipped without Docker.
- Live end-to-end (portable Postgres 17.11, `local` profile): real 4CH0/1C Jan 2012 parser draft ingested (27 questions / 62 parts / 33 mark points, all SUGGESTED; duplicate ingestion → 409) → student sees 0 structured questions pre-validation (8 MCQs only) → teacher validates q7's version + scheme → paper validation correctly blocked (409, 26 versions still SUGGESTED) → student sees q7 with 3 parts → timed structured submit (blank part) → smart-mark the blank answer (deterministic, no LLM: accepted, 0 marks, provisional — no evidence) → human mark (0 marks, per-point decisions) → evidence fired exactly once, BKT 0.1151 after 2 attempts, fluencyGap computed → κ evaluation (sample=1, κ=1.00, gate PASSED) → second blank-answer smart mark became AUTHORITATIVE (evidence fired without human) → telemetry shows SMART_MARK_COMPLETED + HUMAN_MARK_RECORDED.
- Browser (agent-browser): login → 8 MCQ answers (BKT live-updating in My-state) → structured q7 player (3 part textareas) → submit for marking (201, pending-marks panel) → My-state renders Δ on the paired anchor node.

**Known follow-ups:**

- T-013 pgvector embeddings — next session (prerequisite for KA-RAG).
- Real Smart Mark LLM runs need free-tier keys (Groq/Gemini; ADR-009); no-key path fails honestly (PROVIDER_UNAVAILABLE) by design.
- Parser v0 draft quality: non-unique externalRefs, many unsplit stems, marks=0 parts (confidence ~0.55) — all SUGGESTED by design; the validation workflow is the mitigation. Parser refinement + IAL Chemistry syllabus ingestion (T-010 core side) pending.
- localStorage JWT → httpOnly cookie hardening still deferred (Wave 4).
- Teacher marking/content UI is API-only (the web workbench is learner-facing); build when Wave 4 starts.
- Webhook drift: MASTER_SPEC 5-repo topology now fixed; ADR-012 amendment noted inline.

**Next action:** T-013 pgvector embedding pipeline (Gemini embeddings, mark schemes + notes) → then T-024 KA-RAG orchestration.

**Session 3 postscript — CI hardening (4 iterations, all landed green):** the first Testcontainers CI run failed and each failure was a genuine find: (1) ingestion-anchor KG code could exceed `knowledge_nodes.code` VARCHAR(40) with long paper codes — deterministic 31+8-hex-hash cap; (2) exam-paper VARCHAR fields fed from untrusted parser drafts (paper_code etc.) — all bounded; (3) IT assertions read stale in-memory entities after each service call commits its own transaction — re-fetch pattern (unit tests never see this because they share instances); (4) **real product bug: `attempts.correct` stayed the placeholder false for structured attempts after marks landed** — the fluency-gap native query reads the raw column, so every structured attempt would have zeroed its contribution to the gap. `recordTotalMarks(total, marksTotal)` now settles correctness with the same documented full-marks rule as the evidence event. Web CI fixed too (bun setup order + corrupted `branches: ain]` → `[main]` in both repos). Core @ `5b626ca`: 91/91 unit + full IT green in CI; web @ `0c09b52`: green.

## 2026-09-04 — Build session 4: T-013 retrieval spine + The-Brain assessment

- Assessed `Hastur-HP/The-Brain` (user-supplied repo): MIT, ~3.9k LOC, multimodal RAG dashboard + 3D force-graph KG explorer over LightRAG + RAG-Anything + MinerU + Neo4j + NanoVectorDB. Verdict: Tier-A reference + selective code reuse — 3D KG visualizer patterns for T-028 (mastery map UI), SSE job/progress event schema for ingestion ops, query-evidence node-highlighting pattern for tutor XAI; NOT adoptable as runtime (Python/Docker/Neo4j, not free-tier-hostable; LightRAG auto-extraction ≠ curated pedagogical KG). Entry added to REPOSITORY_RESEARCH.md.
- Re-synced all repos after handoff: live state was AHEAD of the handoff summary (core @ 5b626ca with Wave-1/2 fabric + CI green; parser @ a43ad24 with T-008/T-009; web @ 0c09b52 with structured player). Handoff's "13 gaps" list obsolete — control repo TODO.md is authoritative.
- Built T-013 in syllabai-core (content module, 14 new files + V11 + tests):
  - V11 migration: `CREATE EXTENSION vector` (first time), `documents` (canonical JSONB verbatim, checksum-unique idempotency, kind enum), `document_chunks` (deterministic chunk index, element_ids JSONB provenance, `vector(768)` + HNSW cosine, embedding NULL until embedded), `model_versions` seed `content-embedding` (§19 reproducibility).
  - `com.syllabai.content`: CanonicalDocumentDto (parser schema 1.0 mirror, §27 contract), CanonicalDocumentValidator (all §8 invariants re-validated core-side; full violation list in one rejection), ChunkingService (deterministic: page+reading_order, block boundaries, ceil(chars/4) estimate, oversized blocks kept whole), Document/DocumentChunk entities + repos, EmbeddingProvider port (no failover by design — mixed-model index is inconsistent), GeminiEmbeddingProvider (Spring AI `spring-ai-google-genai-embedding` 2.0.1, manually constructed like the chat chain; text-embedding-004, 768 dims; RETRIEVAL_DOCUMENT/RETRIEVAL_QUERY instances), EmbeddingConfig (@ConditionalOnProperty on api-key; fail-fast dimension check vs V11 column), ChunkVectorRepository (JdbcTemplate + `?::vector` casts; owns the vector column), ContentIngestionService (validate → dedup → verbatim persist → chunk), DocumentEmbeddingService (idempotent pending-only, loud no-key failure), ContentRetrievalService (query embed + cosine search, limit clamp), ContentDocumentController (/api/v1/teacher/content/documents: ingest/list/get/canonical/embed/search).
  - Tests: 30 new unit tests (validator, chunking determinism/bounds/provenance, ingestion dedup/conflict, embedding idempotency + dimension-mismatch loudness, retrieval clamping) → 121/121 green locally (JDK 25 + Maven 3.9.9 toolchain set up in sandbox). ContentPipelineIT: real 4CH0/1C Jan 2012 canonical fixtures (QP+MS), full ingest→chunk→embed→cosine search with deterministic hashing embeddings (no network in CI), kind filter, idempotent re-ingest, tampered-doc rejection.
  - Verified the Spring AI 2.0.1 embedding API surface by inspecting `spring-ai-google-genai-embedding` jar from Central BEFORE writing the adapter (chat starter does not pull it — added explicit dependency).
- Fixed during session: 4 test-double bugs (mock verify times, self-consistent stubs that couldn't trigger dimension checks), README staleness (module map, task table, 60→121 test count, API tour).
- Parser repo was NOT polluted (the nested syllabai-web/ dir seen locally was a self-inflicted clone slip in this session, never pushed).
- Next: T-010 core-side syllabus ingestion (parser CurriculumDraft → curriculum + KG seed), then Wave 3 T-024 (KA-RAG — T-013 is its prerequisite, now in place).
- CI postscript (session 4): run 10 caught 2 real bugs in T-013 — (1) validator rejected the real QP fixture's one layout-only textless textBlock (e000034): text-required invariant dropped, chunking already skipped blanks; (2) SqlTypes.JSON storage is content-preserving, not byte-exact (writer normalizes formatting): IT now compares parsed JSON trees, docs corrected — source checksum is the file's provenance spine. Fix @ 5c576d9, CI run 11 green. The IT again proved its worth (3 real bugs across 2 sessions).

## 2026-09-04 — Build session 5: T-010 syllabus ingestion + T-024 KA-RAG foundation

- Fetched the real Edexcel IAL Chemistry 2018 specification from Pearson (108 pp, text PDF; corpus had only past papers) — the missing T-010 input.
- Parser: `EdexcelSyllabusOutlineExtractor` (deterministic Unit/Topic/NC pattern match — opendataloader heading LEVELS are font-derived and unreliable; per-node provenance: sourceSectionId, elementIds, page, confidence; first-match dedup; trailing assessment-noise title cleanup) + CurriculumDraft schema 1.1 + CLI `--extractor outline|heuristic`. Fixed a pre-existing subtopic code collision in the heuristic extractor (U1-T1-S1 shape). Real-spec result pinned by tests: 6 units / 20 topics / 15 subtopics. corpus/ial-chemistry-2018-spec fixture committed. 27/27 tests.
- Core T-010: CurriculumDraftDto + CurriculumIngestionService (resolve-or-create curriculum/subject/root — V6's IAL-CHEM-2018/CHM/CHM reused; namespaced IALCHEM2018-* codes; idempotent by provenance fingerprint; whole-draft tx; all SUGGESTED; prerequisites NEVER derived from an outline) + CurriculumReviewService (node validate/reject flips node+PART_OF edge; version gate ACTIVE only when the whole tree is VALIDATED) + TeacherCurriculumController.
- Core T-024 (tutor package): EvidenceItem first-class evidence; six ports (KnowledgeRetriever, VectorRetriever, EvidenceReranker, ContextAssembler, CitationResolver, TutorGenerator); GraphKnowledgeRetriever (deterministic token intent over VALIDATED nodes, symmetric plural normalization); ContentVectorRetriever (cosine floor 0.15 — zero-relevance chunks must not tie with KG evidence in rank fusion); ReciprocalRankFusion (rank-only k=60); NoReranker; LearnerContextAssembler (mastery/misconception/fluency-gap briefs); GroundedTutorGenerator (tutor-grounded/v1, temp 0.2, free-LLM chain, refuse-on-insufficient-sources); SimpleCitationResolver (labels + deep links); KaRagService (grounding gate: empty evidence → deterministic refusal, no LLM call); TutorAnsweredEvent → KA_RAG_COMPLETED; V12 (telemetry type + §19 prompt/model registry seeds); POST /api/v1/tutor/ask (backend only — chat UI stays T-025).
- 159/159 unit tests (was 121); 2 new ITs (CurriculumIngestionIT, KaRagFlowIT — real-corpus fixtures both sides; KaRagFlowIT verified a TRUE hybrid answer: spec subtopic U2-T8-C "…limited to chlorine, bromine and iodine" AND the 4CH0/1C mark-scheme table chunk both cited).
- CI postscript (4 fix iterations, all genuine finds): bean-name collision (CurriculumController × 2 packages → TeacherCurriculumController); LazyInitializationException on review reads (class-level read-only tx); fixture identity drift (subject CH vs V6's CHM; board "=Edexcel" from a CLI `=` spelling slip — core correctly refused to guess and built a parallel tree; fixture regenerated, CLI tolerates both spellings); fake-embedding hash collisions (plant↔ions) faked cosine 0.25 on the refusal query (zero-collision query chosen; real embeddings unaffected).
- Doc drift fixed (external audit findings): core README (smartmark "placeholder" label, module map, task table, API tour, test counts), AGENT.md (five-repo topology incl. Past-Papers).
- Both repos CI green: core @ 1267265, parser @ 9fe052c.
- Next: T-026 tutor policy + T-027 struggle inference v0 (intelligence layer BEFORE the T-025 chat UI), plus the Past-Papers corpus batch pipeline as the parallel content-ops track.

## Session 6 — T-026/T-027 branch audit & hardening

- Resynced from live repos (four private repos cloned with read/write PAT; Past-Papers public at d198223).
- Audited `codex/session-6-diagnosis-policy` (3 commits over main @1267265) before editing: read diagnostic + tutor packages, V13, events, learner model, telemetry, all affected tests.
- Found and PROVED with `mvn compile`: branch did not compile (enum/DB drift after the telemetry-revert commit); existing tests not updated for prompt v2 → branch tests had never run.
- Hardened (commit e9ef476, pushed to the remote branch): compile fix, listener ordering, Map.entry NPE fix, supersede-keeps-history, deterministic ordering, teacher-override reads, anonymous sentinel, V13 superseded_at + partial index, rules-v0.2 registration.
- Added 36 tests covering the mandated matrix (boundaries, absence of evidence, multi-signal, unsupported-not-emitted, precedence, determinism, anonymous, expiry, telemetry). 195/195 unit green locally on JDK 25.0.4; 10 Testcontainers ITs skipped (no Docker in sandbox) — merge gate = CI green with Docker.
- Control docs updated: TODO.md (T-026/T-027 annotated, still open until CI+merge), PROGRESS.md (session record).
- Remaining before merge: CI run on the branch (unit + ITs + Flyway V13 against real Postgres), then T-025 UI may start on top.
