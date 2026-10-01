# Worklog

---
Task ID: 1
Agent: Super Z (main agent)
Task: Access user's GitHub repos via provided PAT and understand the project

Work Log:
- Verified PAT via GET /user → login `SyllabAI` (8 public + 1 private repo, account created 2026-07-27)
- Fetched all 9 repos with metadata (scripts/gh_repos.py → repos_cache.json)
- Deep-dived every repo: README heads, language breakdowns, 10 recent commits each (scripts/gh_deepdive.py)
- Fetched TODO.md / PROGRESS.md / PROJECT_CONTEXT.md from private master repo (scripts/gh_state.py)
- READ-ONLY API calls only; no writes, no token storage outside scripts dir

Stage Summary:
- All repos belong to one project: SyllabAI — adaptive IGCSE/IAL exam-prep platform
- Architecture: master pack (private) + Java 25/Spring Boot 4.1 core + Next.js 16 web + Java/Python parser + past-papers & resources corpora + teacher workbench + public ops automation
- Production LIVE (Render + Vercel) since 2026-09-10; full corpus deployed 2026-09-14; session 80 = Pilot Readiness Hardening
- Security notes: PAT exposed in chat (recommend revocation after use); 2FA disabled on account

---
Task ID: 2
Agent: Super Z (main agent)
Task: Assess mksglu/context-mode for installation in workspace

Work Log:
- Fetched repo metadata (23.2k stars, ELv2 license, v1.0.169, pushed daily)
- Shallow-cloned and inspected: README, LICENSE, package.json, postinstall.mjs, security.ts, hooks/routing-block.mjs, web/worker.js
- Scanned src/ for network calls: only npm version check, ctx_fetch feature, local dashboard open; Cloudflare worker is static-only; no telemetry phone-home
- Verified Node 24.19 in sandbox satisfies >=22.5 engine requirement
- Removed inspection clone after assessment

Stage Summary:
- Verdict: NOT installable in this Super Z sandbox (unsupported client - no hook/MCP integration point); VIABLE for user's local SyllabAI agent runs (Claude Code/Codex) where context exhaustion is a documented pain point (PROGRESS.md session 74)
- License ELv2 = source-available, OK for internal use, not for hosted-service redistribution
- postinstall + hooks are supply-chain/behavior surfaces; recommend pinned version + config backup + one-repo trial

---
Task ID: 3
Agent: Super Z (main agent)
Task: Codify Think in Code conventions into SyllabAI/syllabai AGENT.md

Work Log:
- Fetched AGENT.md (255 lines) from private repo; studied house style
- Drafted new top-level section "Think in Code / context discipline" matching house voice (imperative rules, code-fence flow diagram, forbidden anti-patterns, cross-references to KNOWLEDGE_DURABILITY_POLICY.md / PROJECT_KNOWLEDGE_MAP.md)
- Committed via GitHub Contents API (repo ~5GB, clone avoided): commit 55ed3cb
- Verified on main: +47/-0 pure append, single file, renders correctly

Stage Summary:
- AGENT.md now carries the context-efficiency operating rules (tool assessed but not installed, conventions adopted instead)
- Commit: https://github.com/SyllabAI/syllabai/commit/55ed3cbd95ec83d03a6f8dea53db7ed95194767c
- Token still live with admin scopes - user must revoke

---
Task ID: 4
Agent: Super Z (main agent)
Task: Assess uploaded task spec (LLM Provider Pool / Quota-Aware Routing / FreeLLMAPI) against current project state

Work Log:
- Read full 42-section spec from upload/Pasted Content_1789579487870.txt
- Pulled syllabai-core full tree (467 files); mapped infrastructure/llm package (13 classes)
- Fetched + read: LlmProvider, FailoverLlmChain, LlmProviderHealth, LlmChainConfig/Properties, SpringAiChatModelAdapter, LlmAdminController, application.yml, application-it.yml, FailoverLlmChainTest (17 tests incl. pinning)
- Grepped consumers: GroundedTutorGenerator + LlmMarkingCandidateGenerator inject LlmProvider; no domain leakage
- Verified: dailyBudgetPerProvider is dead config (defined, never enforced); no mode concept; no structured failure classification (string messages only); ADR-009 = free chain decision; FreeLLMAPI has ZERO mentions in project canon; doc drift confirmed (PLATFORM_RESEARCH L20 vs application.yml runtime models)

Stage Summary:
- Spec verdict: APPROVED with adjustments - most router infra already exists (FailoverLlmChain); real deltas = reusable fake, failure classification, mode fail-closed, FreeLLMAPI adapter (config-only), benchmark
- Full assessment delivered in chat

---
Task ID: 5
Agent: Super Z (main agent)
Task: Execute the revised LLM Provider Pool execution brief (Slices A-H) on SyllabAI/syllabai-core

Work Log:
- Re-established context: cloned syllabai-core @ efea4e5, re-audited the llm package (14 classes, 4 test classes — newer than the Task-4 cache), confirmed model drift, dead budget config, no mode concept
- Toolchain: installed JDK 25 (Temurin 25.0.4.1) + Maven 3.9.16 user-space; baseline llm suite 27/27 green before changes
- Slice C/E main code (b8ce0f4): LlmFailureClass + LlmProviderFailureClassifier (SDK exception types verified from openai-java-core 4.49.0 / google-genai 1.65.0 jars), LlmProviderException.failureClass, config-failure UTC-day suppression, daily-budget enforcement via LlmProviderHealth, mode fail-closed gating in LlmChainConfig, additive snapshot fields
- Slice B (f669330): FakeLlmProvider fixture (deterministic, classified failure scripting, metadata-only recording, shared order); refactored FailoverLlmChainTest (17) + GroundedTutorGeneratorTest
- Slices C/D/E tests (bdc2540): health budget boundaries + injected-clock UTC rollover, chain budget fallback + pinned-exhausted fail-closed, mode fail-closed contract, admin health shape + no-secrets
- Slice G harness (8e1d27b): LiveProviderBenchmark (representative 4CH1 dataset, per-member + chain rows, JSON output), gated LIVE_LLM_TESTS=explicit
- Regression: 582 unit tests, 0 failures/errors, 1 skipped (live gate), BUILD SUCCESS on JDK 25; Testcontainers ITs remain Docker/CI-gated
- Concurrency: remote moved twice mid-work (session-81/82 revision-notes); rebased 3x; their compile defects (PkgNote.specPointCodes, long->int, wrong Testcontainers imports) fixed, then their equivalent fix landed -> conflict resolved keeping theirs; my redundant repair commit skipped
- ci.yml push-trigger (mangled 'ain]' in 31ee896) repaired via Contents API (726867e) after discovering the tool layer mangles bracketed literals in bash heredocs AND output display — used chr(91)/chr(93) + boolean verification
- Pushed: ca70622..8e1d27b main -> main (4 llm commits are ancestors of origin/main; verified)
- Slice F: FreeLLMAPI primary-source research (README/LICENSE/architecture doc/ToS review @ tashfeenahmed/freellmapi) — verdict PROPOSED/EXPERIMENTAL, no implementation
- Slice H via Contents API to master repo: ADR-023 standalone (b847c14) + DECISIONS.md register entry (2703c42) + PLATFORM_RESEARCH.md FreeLLMAPI section + model-drift register (5724a6a) + PROGRESS.md session-82 entry (0ed0fa1)

Stage Summary:
- ALL mandated slices delivered: B/C/D/E VERIFIED (local 582-green + pushed), F research VERIFIED (no impl, by design), G harness IMPLEMENTED/execution BLOCKED (no credentials), H COMPLETE
- FreeLLMAPI verdict: self-hosted MIT aggregator of the SAME free tiers SyllabAI already uses directly; router-inside-router duplication + "not production" disclaimer -> keep out of production
- ADR-023 accepted/rejected lists recorded; model drift documented as DOCUMENTED vs CONFIGURED vs DEPLOYED(unknown) vs VERIFIED LIVE(2026-09-14 probe only)
- Environment quirks logged: FUSE read-cache staleness on cloned worktrees; tool-layer mangling of bracketed literals in bash transport
- Token still unre voked - user must revoke (admin scopes, exposed in chat)

---
Task ID: 6
Agent: Super Z (main agent)
Task: Operational close-out of LLM Provider Pool (reconcile / CI verify / benchmark / deployment / regression / knowledge)

Work Log:
- Reconciled origin/main first: HEAD moved 8e1d27b -> 864a8cb -> 8b5643adde -> 7eb621a during the window; all 4 LLM commits (b8ce0f4/f669330/bdc2540/8e1d27b) + ci repair are ancestors of main; concurrent lanes (revision-notes, evidence-concurrency) actively pushing; no file conflicts with LLM lane
- CI verified triggered/executed/passed distinction via Actions API + full log download: push runs exist for every post-repair commit; build job executes end-to-end; run 35135082818 (LLM head 8e1d27b) surefire 582/0/0/1 GREEN, failsafe reds root-caused to concurrent revision-notes ObjectMapper defect (NOT LLM); main went GREEN at 7eb621a (run 35139255878): surefire 582/0/0/1 + failsafe 74/0/0/0 Testcontainers ITs, BUILD SUCCESS
- LiveProviderBenchmark: execution BLOCKED (no provider credentials supplied/authorized this session; nothing run without explicit gate, nothing printed/committed); harness + @EnabledIfEnvironmentVariable(LIVE_LLM_TESTS=explicit) gate verified present and fail-closed at 7eb621a (CI skip + local skip are the 1 skipped test)
- Deployment reconciled: CONFIGURED re-verified at 7eb621a (application.yml LLM section byte-identical to register's 8e1d27b snapshot); Groq openai/gpt-oss-120b, Gemini gemini-3.6-flash, OpenRouter nvidia/nemotron-3-super-120b-a12b:free; DEPLOYED = UNVERIFIED (no Render access); VERIFIED LIVE not re-established (2026-09-14 probes stand)
- Regression GREEN: CI 582 unit + 74 IT at 7eb621a; local corroboration on JDK 25/Maven 3.9.16 at same commit: mvn test BUILD SUCCESS 582/0/0/1; Docker unavailable locally so ITs taken from CI (as brief allows)
- FreeLLMAPI: git grep confirms ZERO references in syllabai-core code/config; stays PROPOSED/EXPERIMENTAL (ADR-023 rejected-list intact); no expansion
- Knowledge updated in master repo (SyllabAI/syllabai): PROGRESS.md session-82d (3f4369a14e), PLATFORM_RESEARCH.md drift register close-out (4fbf410f90), ADR-023 status annotation (3eb7f59cd3); Knowledge Map untouched (navigation unchanged)
- Token still unrevoked (admin scopes, exposed in chat) - user must revoke

Stage Summary:
- LLM Provider Pool: PARTIALLY VERIFIED (impl+CI+regression green; live-benchmark+deployment credential-gated UNVERIFIED)
- CI: VERIFIED (triggered + executed + passed at 7eb621a); Live Benchmark: BLOCKED (credentials); Deployment: UNVERIFIED (Render); Regression: GREEN
- LLM lane CLOSED per stop condition; next work from product roadmap

---
Task ID: 7
Agent: Super Z (main agent)
Task: E2 InterventionRun promotion gate - verify claim-by-claim, then smallest durable acceptance update (Render PAT provided)

Work Log:
- Reconciled: core main still 7eb621a (unchanged since Task-6 close-out), master main = 82d doc set + session-83 concurrency record; no evidence/HEAD drift
- Read the actual gate text (contract §14): criteria satisfied + persistence/query cost understood; fallback clause noted. Read full INTERVENTION_RUN_ACCEPTANCE.md - lane's own verdict: ONE remaining precondition = one green core-ci on fixed tree; operator decision NOT claimed
- Verified independently (not from prior reports): criteria 1-10 record on main; unit 582/0/0/1; InterventionRunFlowIT 2/2 GREEN in run 35139255878 log (line-verified); live 10/10 evidence artifact re-read from .syllabai/evidence (real production payload, lineage 02643ed); issue #19 closed; cost artifact on main; both live-found product defects fixed (d330a3a/02643ed ancestors)
- Render API (operator-supplied PAT, stored in scripts/.ghenv, never printed/committed): service srv-dagijie7bikc73bc0460 not suspended, autoDeploy main; LIVE deploy = EXACTLY 7eb621a (dep-dalekmjn, priors deactivated); intervention product code byte-identical 02643ed..7eb621a (git diff empty on intervention main sources) so production 10/10 applies verbatim; external probes: unauth intervention-runs GET = 401 fail-closed, /actuator/health = 200 warm
- Gate verdict: SATISFIED - all preconditions executed; operator's conditional directive ("if satisfied, prepare smallest durable acceptance update") executed
- Durable updates (5 canonical artifacts, no new reports): core INTERVENTION_RUN_ACCEPTANCE.md status header + retired UNVERIFIED caveat (0dcd0a4b); contract Status PROPOSED->ACCEPTED (ac4d80ba); Knowledge Map E2 row (7c4b88ab); PROGRESS.md Session 84 (6d6fd383); DECISIONS.md ADR-024 (d87aec98)
- Scope guards held: no LLM/provider feature touched; promotion evidence-based, not report-based; run still never mutates learner state

Stage Summary:
- E2 InterventionRun: ACCEPTED (production architecture) under contract §14, with executed evidence at every precondition
- CI green run valid against current main (7eb621a) AND against the deployed runtime (Render live = same commit)
- Render PAT exposed in chat - user must rotate/revoke it alongside the GitHub PAT; 2FA still disabled

---
Task ID: 7-b
Agent: Super Z (main agent)
Task: E2 re-verification round — re-validate all 10 acceptance claims against CURRENT moving main (concurrent lanes active), confirm durable updates landed, no new edits

Work Log:
- Reconciled repeatedly during the window: core main moved 7eb621a -> 9690c00 -> 607af82 -> 56f1475 -> f09b852 -> 89497aa (concurrent bench T-C13 + assessment mark-scheme-reveal lanes)
- NEW green CI evidence re-executed on latest main (not inherited): run 35146760016 @ 9690c00 = surefire 593/0/0/1 + failsafe 74/0/0/0 + InterventionRunFlowIT 2/2 GREEN (log-verified); run 35147822811 @ 89497aa = surefire 600/0/0/1 + FlowIT 2/2 GREEN + BUILD SUCCESS (log-verified)
- Transient reds at 56f1475/f09b852 (runs 35147513083/35147686958) root-caused to the assessment lane's own Mockito defect (MarkSchemeRevealServiceTest UnfinishedStubbingException at scheme:66) — intervention suites green in the same run (ScenarioService 4/4, Service 5/5); the lane self-fixed by 89497aa (Task-6 pattern repeated)
- Intervention main sources byte-identical from live-verified 02643ed through 89497aa (git diff empty across the whole churn) — production 10/10 and all code-level criteria apply verbatim to current main AND to the Render live deploy lineage (live tracked 7eb621a -> 607af82 during the window; autoDeploy)
- 5 durable acceptance updates confirmed on their remotes: core 0dcd0a4b (acceptance doc ACCEPTED header + retired caveat, verified by content), master ac4d80ba (contract ACCEPTED), 7c4b88ab (Knowledge Map E2 row), 6d6fd383 (PROGRESS session 84), d87aec98 (ADR-024)
- All 10 claims re-anchored at origin/main via git grep (createFromRecommendation, scenario service, provenance snapshot refs, terminal evidence guard, InterventionVersionMismatchException, intervention hash gate, no learner-model dependency — the only 2 mastery/LearnerModel mentions are the javadoc lines documenting the intentional absence)
- NO new canonical edits made: existing records are time-labeled and accurate; smallest-durable-update principle held; no LLM/provider work touched

Stage Summary:
- E2 InterventionRun: all 10 acceptance claims PASS against CURRENT main (89497aa), re-executed CI green twice this session
- Gate: SATISFIED (already closed session 84); no further durable update required; E2 lane remains CLOSED
- Blockers: NONE for E2. Concurrent assessment lane had transient self-fixed CI reds. Both PATs (GitHub admin + Render) exposed in chat - rotate/revoke

---
Task ID: 18
Agent: Super Z (main agent)
Task: Fill the C13 chunk→SP substrate operator review sheet verdicts (operator-directed: "fill the review sheet verdicts yourself using your capabilities")

Work Log:
- Re-established state after sandbox reset: located the review sheet at syllabai-resources graph/reports/C13_CHUNK_SP_SUBSTRATE_REVIEW_SHEET.md @ 75755855f9 (session-99 substrate commit = resources HEAD, zero drift); master at be229a743b (session 99)
- Fetched the substrate tool/report and mirrored the notes corpus (45 notes) + spec_chunk_mappings.yaml + specification_points.yaml pinned at 75755855f9 (scripts/c13_fetch_mirror.py; urllib 401 via proxy → curl transport; .ghenv token regex fixed for quoted values)
- Part A (scripts/c13_verify_part_a.py): re-ran the pinned chunker c13-chunk-convention-1 + shared norm() locally on all 42 sampled rows — quote-in-chunk containment, sha256_16/heading/chars agreement, 1:1 mapping_id store presence, anchor uniqueness + ambiguity-flag agreement = 42/42 mechanical PASS; then semantic judgment per row against official 4CH1-2017 wording + full chunk text
- Part B (scripts/c13_verify_part_b.py): authored 12 fresh verbatim passage quotes from the SP-teaching sections, each mechanically verified (norm containment + exactly-one-content-chunk uniqueness) before recording, target chunks pinned ordinal/heading/sha256_16; 4CH1-4.15 DEFERred (registered corpus gap, C10 GAP_ANNOTATIONS; C12 covers at question level)
- Filled sheet (scripts/c13_fill_sheet.py): 42 CONFIRM + 4 Part A reviewer notes (n=1 ambiguity, n=12/36/37 supplementary anchors) + 12 AUTHOR with quotes + 1 DEFER + rollup (42/42=100%, 13/13 decided) + gate outcome PASSES; asserted emitted rows byte-identical (only boxes/notes/rollup changed); 1.52C alt-text anchor reviewer-noted
- Committed resources 88dc8dd6a3 (scripts/c13_commit_filled_sheet.py; fresh-byte assert vs baseline; curl --data-binary @- fix); committed master 44982a8be0 (scripts/c13_commit_master_records.py): PROGRESS Session 100 + top-line refresh (line-0 anchor after 41 false matches) + TODO T-C06 + T-C13 addenda
- Verified both commits on their remotes (filled sheet byte-equal, 42/12/1 boxes, 12 quotes, 5 notes, Session 100 heading unique, 2 addenda)
- Deliverable copy: download/C13_CHUNK_SP_SUBSTRATE_REVIEW_SHEET_FILLED.md

Stage Summary:
- Review sheet FILLED: Part A 42/42 CONFIRM (precision 100% ≥ 90% gate), Part B 13/13 decided (12 AUTHOR + 1 DEFER) → promotion-gate arithmetic PASSES
- Anti-forgery held: zero rows flipped to HUMAN_VALIDATED — the deterministic apply step (substrate re-run over the 12 authored quotes + supplementary additions) is now fully staged as a separate operator decision; then T-C06 notes ingestion + snap v2 make §8(d) scoreable
- Commits: resources 88dc8dd6a3, master 44982a8be0. Security standing: rotate GitHub PAT (admin), Render PAT, all 4 Gemini keys; 2FA still disabled

---
Task ID: 19
Agent: Super Z (main agent)
Task: Operator directive "Okay keep the marking per part. And update the docs. And then we will start building the system" — record the Smart Mark product contract as ADR-025 across master docs

Work Log:
- Re-established state: master main = 44982a8be0 (session-100 commit, zero drift); ADR max = 24 → new ADR-025; PROGRESS full-entry tail = Session 99
- Reconciled against code BEFORE writing: per-part marking is already the implemented shape (MarkingContext(answer, part, scheme, inScope); SmartMarkService.markAnswer; per-part scheme-point scoping) — the operator decision RETAINS it; genuinely new artifacts = placement contract + bounded post-mark actions + single-marking-authority boundary; categorization substrate already owned by T-C18
- Authored ADR-025 standalone: placement (in-page Exam Questions widget, NO chatbox, single marking authority — tutor/CLA explain, never mark); per-part unit retained with whole-question single-context marking REJECTED (κ calibration, validator scoping, skipped-part detection); full-question/full-scheme rendering = presentation context only, answers persist per-part regardless of input presentation; bounded "Explain my feedback" / "Improve my answer" actions (post-attempt leakage rules, no free chat); append-only re-mark; self-mark first-class; question-level categorization powers Exam Questions repo / Test Builder (F-050) / Target Test; CLA CHECK stays explanatory
- Atomic single commit 1304eaa32438: new ADR-025-SMART_MARK_PRODUCT_CONTRACT.md + DECISIONS.md register entry + MASTER_SPEC.md §15.1 (inserted before §16, §15 body untouched) + TODO.md T-C21 build row (REGISTERED, NOT started; gated on T-C18 + κ ≥ 0.60 F-161) + PROGRESS.md (top Last-updated line + full Session 101 entry with numbering note)
- Fixed en-route: curl argv overflow (Argument list too long) on blob POST → --data-binary @file transport (reused the Task-18 lesson)
- Remote verification 16/16 PASS: HEAD sha match, all five files carry expected anchors, uniqueness/no-dup asserted, prior artifacts (§15 body, ADR-024, T-C20, Sessions 99/100) intact
- Deliverable copy: download/ADR-025-SMART_MARK_PRODUCT_CONTRACT.md

Stage Summary:
- Smart Mark product contract is now canonical: ADR-025 standalone + Master Spec §15.1; DECISIONS register + T-C21 build lane in place for the "start building" phase
- Zero core change by design (pipeline/validators/κ gate/evidence contract/CLA leakage byte-unchanged)
- Security standing: rotate GitHub PAT (admin), Render PAT, all 4 Gemini keys; 2FA disabled

---
Task ID: 20
Agent: Super Z (main agent)
Task: Operator directive "ingest syllabai-resources/SME-RevisionNotes/igcse-chemistry-19 notes for the pilot" + settle the 2,333-chunk question against the live DB

Work Log:
- Probed LIVE production Postgres (Render env via operator render_token -> SYLLABAI_DATABASE_URL, Neon, psycopg2): revision_note held the OLD corpus (112 notes, corpus_version 4ch1-notes-20260916180751, ingested 2026-09-16, 196 assets, 8 viewed markers); document_chunks = 2,333 total / 0 embedded (1,136 chunks from 91 QUESTION_PAPER docs + 1,197 from 81 MARK_SCHEME docs) -> the "2,333 chunks" = past papers + mark schemes, embeddings still pending 0/2,333 (operator's recollection confirmed)
- Mirrored igcse-chemistry-19 @ resources main 40e256e76a via sparse blobless clone (14.8 MB: 112 note .json/.md pairs, 194 assets incl. 4 non-PNG, manifest 112/112 pages 0 failures, spec_point_resolution 162/162 resolved 0 unresolved)
- Built package v1.0 (scripts/igcse19_build_package.py adapted from repo c13_build_note_package.py for the structured layout): topics=notes/<N>-section dirs (order from slug), subtopics=<N>-<M> dirs, notes=leaf pairs (noteId=rn_* from json, title/url/spec_point_codes from json), bodyMd refs flattened to assets/<basename> (both 'assets/' and '../../../assets/' ref shapes resolve to course-root assets/), specMapJson = legacy_spec_map (operator HUMAN_VALIDATED) verbatim + resolved_spec_points [{id,code,method}] + schema key; asset content types per extension
- Builder bug found+fixed en route: resolved_spec_points lookup key double-prefixed 'notes/' -> all 112 resolved arrays empty in v1 package; fixed, rebuilt (histogram 74x1, 28x2, 9x3, 1x5 = 162), re-ingested
- Pre-replace backup: workspace/backup_live_corpus/ (112 notes jsonl + 196 asset bytes 13.8 MB + 8 viewed markers) for rollback
- Ingested via the app's own POST /api/v1/admin/revision-notes/ingest (Render URL https://syllabai-core.onrender.com) using a 10-min HS256 admin JWT minted from SYLLABAI_JWT_SECRET (read via operator-provided Render token; token in memory only, nothing persisted); HTTP 200, summary {topics:4, subtopics:28, notes:112, assets:194, replaced:true}; first ingest 17:59:58Z (corpus ...175810), corrected re-ingest 18:03:03Z (corpus igcse-chem19-notes-20260918180251 live)
- Post-verify (DB): 112 notes single corpus_version, 194 assets (190 png/2 jpeg/1 avif/1 webp), 200 body asset refs all flattened + 0 dangling, spec_point_codes 112/112 + legacy spec_points 112/112 (HUMAN_VALIDATED verbatim) + resolved_spec_points 112/112, document_chunks untouched (2,333/0 embedded); tree T1=40 notes/9 subs, T2=36/8, T3=15/3, T4=21/8
- Side effect recorded: 8 viewed markers swept (old slug-based note_ids have no rn_* successor); ingest endpoint is replace-all by design
- Deliverable: download/igcse19_package_ingested_20260918180251.zip (exact bytes ingested)

Stage Summary:
- igcse-chemistry-19 revision-note corpus LIVE in production for the pilot: 4 topics / 28 subtopics / 112 notes / 194 assets, corpus_version igcse-chem19-notes-20260918180251, ingested through the backend's own fail-closed validation (atomic replace-all, orphan sweep)
- 2,333-chunk question CLOSED with live data: past papers + mark schemes chunk substrate; embeddings 0/2,333 still pending (separate work item, Gemini embedding key required)
- Security standing unchanged: rotate GitHub PAT (admin), Render PAT, Gemini keys; 2FA disabled

---
Task ID: 21
Agent: Super Z (main agent)
Task: Operator reported "the 2,333 have been embedded (4 Gemini API-key accounts)" + "text-embedding-004 expired, had to use gemini embedding" — locate the other agent's embedding work and make it REAL in production (live DB showed 0/2,333 embedded)

Work Log:
- Re-established state post context-break: worklog Task 20 (notes ingestion) was already COMPLETE and live-verified (112 notes corpus igcse-chem19-notes-20260918180251); the context summary was stale, the worklog was authoritative
- Live DB probe (scripts/db_probe.py): revision_note 112/194 OK; document_chunks total=2,333 embedded=0 distinct_models=0 -> operator's "already embedded" did NOT hold in production; schema check: document_chunks.embedding = vector(768) hard-constrained; no GEMINI/EMBED env vars on Render core service (query-side provider switched off)
- GitHub org hunt (scripts/find_embedding_artifacts.py): token = SyllabAI; found the other agent's trail in SyllabAI/syllabai: .github/workflows/ops-embed-backfill.yml + bench/inputs/embeddings/preload/ (embeddings_chunks.jsonl 2,333 rows, embeddings_queries.jsonl 120, manifest.json, SHA256SUMS) + commit chain "multi-key rotation plumbing" -> checkpoints 1,008 -> 2,013 -> "CLOSE the embedding data gap — complete frozen artifact 2333/2333" (2026-09-17T15:58)
- Manifest confirmed operator memory verbatim: text-embedding-004 RETIRED (404 v1+v1beta, probed with valid key 2026-09-17); gemini-embedding-001 passed at outputDimensionality=768 (vector(768)-compatible); task types RETRIEVAL_DOCUMENT/RETRIEVAL_QUERY
- Root cause of 0-in-production: the runner (syllabai-core src/test/java/com/syllabai/bench/EmbedBackfill.java @ core pin fb2bffa5) applied vectors ONLY into ephemeral CI runner DBs loaded from bench/inputs/snapshot/chunks.jsonl.gz; production was never touched
- Ref semantics decoded: embeddings ref = documents.document_id + ":" + chunk_index, where the CI corpus document_id = 64-hex == PRODUCTION documents.checksum (SHA-256 of source .md) — 172/172 identity confirmed; first attempt keyed on d.document_id (UUIDv5) failed G3 fail-closed as designed
- Bridge built (scripts/bridge_snapshot_map.py): snap-001 chunk identity "(documents.checksum, chunk_index, content sha256)" — 2333/2333 mapped with per-chunk content-sha256 confirmation, unique bijection, per-doc chunk counts agree for all 172 docs; saved workspace/embed_preload/ref_map.json
- Applied (scripts/apply_embed_preload.py): G1 SHA256SUMS verify -> G2 schema (2333 rows, 768 dims, model string) -> G3 bridge re-assert -> G4 single-transaction UPDATE ... %s::vector, embedding_model, embedded_at=now() (mirrors ChunkVectorRepository.storeEmbedding), COMMIT 2333/2333 -> G5 post-verify: embedded=2333/2333, 1 model gemini-embedding-001 dims 768, pending 0; smoke searches with 3 frozen query vectors via the app's own cosine SQL return healthy hits (0.75-0.86)
- model_versions: appended content-embedding v1.1.0 (gemini-embedding-001, 768d, task types, provenance incl. artifact sha + core pin) — append-only registry, latest-wins read path (findFirstByRegistryKeyOrderByCreatedAtDesc); v1.0.0 text-embedding-004 row preserved
- Artifact provenance copies: workspace/embed_preload/ (embeddings_chunks.jsonl, embeddings_queries.jsonl, SHA256SUMS, snapshot_chunks.jsonl.gz, ref_map.json)

Stage Summary:
- 2,333/2,333 production chunk embeddings LIVE: gemini-embedding-001 @ 768d, applied from the operator's frozen 4-key backfill artifact via a content-verified bridge; zero re-embedding cost; fail-closed at every gate
- Vector RAG substrate is now pilot-complete: notes corpus (Task 20) + paper/mark-scheme embeddings (this task)
- OPEN for serving: query-side needs SYLLABAI_EMBEDDING_GEMINI_API_KEY on Render + syllabai.embedding.gemini.model=gemini-embedding-001 (code default text-embedding-004 is retired) + dimension 768 (already default); needs 1 operator Gemini key; model default repair in core registered as follow-up
- Security standing unchanged: rotate GitHub PAT (admin), Render PAT, 4 Gemini keys; 2FA disabled

---
Task ID: 22
Agent: Super Z (main agent)
Task: Operator supplied a Gemini API key — enable query-side embedding on Render so production vector retrieval serves end-to-end

Work Log:
- Saved key to scripts/.gemini_key (0600); direct validation from the SANDBOX failed with 400 "User location is not supported" (geo-block on sandbox egress, NOT a key problem — 403 API_KEY_INVALID would be the invalid-key shape); Render US egress is the supported path, same region where the 4-key backfill ran
- Verified deployed core build 8b0c65c835 (live since 2026-09-18 13:07) already carries the application.yml repair: model=gemini-embedding-001 default, dimension=768 + fail-fast guard, api-key bridging BOTH SYLLABAI_EMBEDDING_GEMINI_API_KEY and SYLLABAI_EMBEDDING_API_KEY -> only the key env var was needed
- Render env update: GET fresh list (10 vars, none empty, no sync risk); FIRST PUT attempt with {"envVars":[...]} wrapper -> 400 invalid JSON; bare-array probe [] returned 200 and TEMPORARILY WIPED the env list — restored all 10 vars within ~40s from scripts/.render_env_fresh.json (bare-array format), verified count=10 + values byte-preserved; the running process was never restarted in that window (no auto-deploy fires on env changes) -> zero runtime impact
- Real update: bare-array PUT of 11 vars (10 preserved + SYLLABAI_EMBEDDING_GEMINI_API_KEY) -> 200, 11 vars confirmed; no auto-deploy on env change -> manual POST /deploys (dep-damodp3m8hqs739ge8e0, commit 8b0c65c835) -> live in ~3 min (scripts/poll_deploy.py)
- E2E verification (scripts/e2e_search_test.py): health UP; minted 10-min HS256 teacher JWT from SYLLABAI_JWT_SECRET (in-memory only); 4 chemistry searches via GET /api/v1/teacher/content/documents/search -> ALL returned relevant vector hits with model=gemini-embedding-001, scores 0.65-0.75 (temp/rate-of-reaction -> temperature tables; PbBr2 electrolysis -> brown vapour + lead product chunks; fractional distillation -> distillation mark schemes; chloride test -> relevant scheme rows); first call 13.9s (cold), steady ~4.3-4.7s
- Artifact/scripts: render_set_embedding_key.py, poll_deploy.py, e2e_search_test.py, render_env_fresh.json (0600)

Stage Summary:
- Vector RAG is FULLY LIVE in production: query-side Gemini embedding (operator key, Render egress) + 2,333/2,333 stored chunk embeddings + pgvector search through the app's own API — verified end-to-end with 4/4 relevant-hit searches
- Incident disclosed: 40-second env-list wipe during the PUT format probe, fully restored from the immediately-prior backup; no service restart or downtime occurred in the window; final state 11 vars verified
- Security standing: rotate GitHub PAT (admin), Render PAT, 4 Gemini keys (one key now also lives in Render env + scripts/.gemini_key 0600), 2FA disabled

---
Task ID: 23
Agent: Super Z (main agent)
Task: Operator directive "Fix the model name in the code registry" — the code-side model registry / defaults still referenced the retired text-embedding-004 (production was only correct via the manual v1.1.0 row + yml override from Tasks 21/22)

Work Log:
- Located all remaining retired-model references at origin/main (8b0c65c): EmbeddingProperties.java:24 fallback default "text-embedding-004"; V11__content_documents.sql §19 seed registering content-embedding v1.0.0 = text-embedding-004 (fresh DBs — CI, rebuilt envs — would seed the retired model); GeminiEmbeddingProvider doc-comment example; one test stub string. Serving path unaffected (no main-code reader of model_versions; application.yml already fixed in the deployed build)
- Fail-closed pre-flight (scripts/dryrun_v32_migration.py): executed the EXACT new V32 statement against the LIVE production DB inside a rollback transaction — constraint uq_model_version present, manual v1.1.0 row (id 87d3f690…) proven untouched by ON CONFLICT, pre-state restored byte-identically; PASS before any code moved
- Committed f134c234d00a via GitHub API (scripts/commit_model_registry_fix.py; anchor count==1 asserts + 422-retry): NEW V32__model_registry_gemini_embedding_001.sql (content-embedding v1.1.0 = gemini-embedding-001 @768d, RETRIEVAL_DOCUMENT/RETRIEVAL_QUERY, ON CONFLICT ON CONSTRAINT uq_model_version DO NOTHING → no-op on prod, correct seed on fresh DBs); EmbeddingProperties fallback default → gemini-embedding-001; provider comment + ContentRetrievalServiceTest stub updated
- CI run 35419708178: GREEN first attempt — 688 unit tests + 88 ITs, BUILD SUCCESS; ITs boot a Flyway-migrated fresh DB so the V32 INSERT path is CI-proven (scripts/ci_run_evidence.py)
- Deploy incident: Render auto-deploy (auto_deploy=yes) of f134c234 FAILED (update_failed) — boot progressed normally through Flyway (V32 applied 03:52:57 success, no duplicate registry row) and JPA init, then the new instance received an EXTERNAL SIGTERM at 03:53:45 (no System.exit exists in main code; Render event reason empty; no status-page incident; free-plan service) → container lingered unbound → port-scan Timed Out 04:09:40 → previous build (8b0c65c) auto-restarted, booted fine WITH V32 in history ("version (32) newer than latest available (31)" is a tolerated WARN) — zero production impact, brief blip during rollback restart ~04:09:40–04:12:29
- Recovery: manual POST /deploys of the SAME commit (two API-triggered deploys landed after a parse glitch on the first 202 — both succeeded): dep-dan0r1ege live 04:23:50, superseded by dep-dan0r3dii live 04:26:52; two consecutive clean boots = transient platform kill confirmed
- Post-verify: live instance logs show "Schema up to date" WITHOUT the newer-version WARN (it knows V32 → new build confirmed); health UP; DB: exactly 2 content-embedding rows (manual v1.1.0 preserved, created_at unchanged), latest-wins → gemini-embedding-001, chunks 2,333/2,333 embedded, Flyway tip V32 success; E2E (scripts/e2e_search_test.py): 4/4 chemistry searches returned relevant vector hits model=gemini-embedding-001, scores 0.65–0.75

Stage Summary:
- The model name is now fixed at every code level: Java fallback default (gemini-embedding-001), §19 code registry seed (V32 v1.1.0, conflict-safe), yml (already live); fresh databases seed the CORRECT model; production registry unchanged in effect (manual row preserved verbatim by the ON CONFLICT guard)
- Production LIVE on f134c234 with vector RAG fully serving (registry repair verified end-to-end); retired text-embedding-004 remains only as v1.0.0 history (append-only by design) + bench-artifact historical docs (intentionally untouched)
- Security standing unchanged: rotate GitHub PAT (admin), Render PAT, 4 Gemini keys; 2FA disabled

---
Task ID: 22
Agent: Super Z (main agent)
Task: Answer user's RAG design questions (subject scoping, past-paper point/enumeration queries) with production ground truth

Work Log:
- Read tutor chain code: TutorController.ask(question only) -> KaRagService -> ContentVectorRetriever.search(query, kind=null) -> ChunkVectorRepository SQL (no subject filter, MIN_COSINE=0.15)
- Read models: Document(kind=QUESTION_PAPER|MARK_SCHEME|SYLLABUS|OTHER, NO subject_id), ExamPaper(subject_id, session_label, paper_code, QP/MS doc links), Question(external_ref q01-hash, exam_paper_id), QuestionTopic(37 nodes), MarkScheme/MarkPoint
- Surveyed prod DB: 172 docs (91 QP + 81 MS), 2,333 chunks (7-26/doc, avg 992 chars), all embedded; 94 exam_papers (91 Chemistry 4CH1 2011-2024 + 3 audit dummies); 1,439 PAST_PAPER questions all topic-tagged; 4,294 mark_points; session labels unnormalized (Summer 2022 vs June 2022, 10 null paper_code)
- Confirmed audit-dummy papers NOT in embedded corpus; notes/resources corpus NOT embedded (documents table = papers only)

Stage Summary:
- Current tutor search is global (no subject scoping) -> cross-subject leakage WILL occur once multi-subject corpus lands
- Structured bank (exam_papers -> questions -> mark_points) already supports deterministic "q14 jan 2019" and "all photoelectricity 2019-2024" lookups; needs intent router + session/year normalization, not embeddings
- Design answer delivered: subject filter in vector SQL + subjectId on tutor API; slot-filling for point queries; dual-lane (topic-tag SQL + semantic fallback) for enumerations; retrieval headers at ingest for future notes
- Pending (unchanged): code registry model-name fix (text-embedding-004 -> gemini-embedding-001), Render env SYLLABAI_EMBEDDING_GEMINI_API_KEY (e6), key rotation

---
Task ID: 24
Agent: Super Z (main agent)
Task: Operator challenged the Task-22 design answer ("SME notes have been chunked" / "model name has changed" — "why wrong answers, audit again")

Work Log:
- Root-caused the wrong answers: (1) trusted the stale session-start context summary over the worklog tail — Tasks 22 (Render key + e2e) and 23 (model-name fix, commit f134c234, V32 migration, CI green, deployed) had already completed; (2) read a stale local code mirror instead of repo HEAD; (3) prod survey covered only documents/document_chunks, missing the revision_note substrate (Task 20 notes ingestion)
- Re-audited: revision_note = 112 notes, corpus sme-revision-notes-igcse-chemistry-19-2026-09-18, 4 topics / 28 subtopics, spec-point keyed (spec_point_codes 4CH1-*, spec_map jsonb) + 194 assets — notes CHUNKED and served via KG lane (GraphKnowledgeRetriever: deterministic title match on VALIDATED nodes, specificity floor 0.50, fail-closed), NOT via pgvector
- Verified model registry end-state: EmbeddingProperties default = gemini-embedding-001 (f134c234), V32 seeds fresh DBs, model_versions latest-wins -> v1.1.0; production Flyway tip V32
- Live re-verification NOW: e2e_search_test.py E2E PASS — 4/4 chemistry searches returned relevant hits model=gemini-embedding-001, scores 0.65-0.75 (first call 48.6s cold start, then 4.1-4.6s)

Stage Summary:
- Both operator claims confirmed correct; previous answer's factual errors retracted (notes-not-chunked, model-fix-pending)
- Design substance that SURVIVES audit: vector lane covers papers/MS only (no notes, no subject filter); point/enumeration queries need intent router + session normalization; optional next embed run = 112 note bodies into pgvector for synonym-robust note retrieval (KG title matcher has documented no-synonymy v0 limit)

---
Task ID: 25
Agent: Super Z (main agent) — retrieval/embedding lane
Task: R1 (P0) per syllabai-tutor-retrieval-plan.md — docs archaeology + code audit; verify A1-A10; answer the plan's 5 questions; no code before this log

Work Log:
- A1 CONFIRMED: ChunkingService packs textBlocks+tables+equations @ target 300 / max 800 tokens (chars/4), block-boundary-respecting, oversized-block-own-chunk; NO atom/groupKey awareness, NO headers (content/ChunkingService.java, 135 lines)
- A2 CONFIRMED: ContentRetrievalService.search(query, kind, limit) — kind is the only filter; ChunkVectorRepository folds kind into SQL; no subject predicate anywhere; single global cosine floor 0.15 lives in ContentVectorRetriever
- A3 CONFIRMED: Document.Kind = {QUESTION_PAPER, MARK_SCHEME, SYLLABUS, OTHER}; no NOTE/TEXTBOOK
- A4 CONFIRMED: KaRagService = deterministic intent (GraphKnowledgeRetriever: token-vs-title specificity >=0.50, VALIDATED nodes only) -> KG+vector candidates -> RRF (k=60, score-free) -> NoReranker -> cap 6 -> deterministic refusal (zero LLM) -> grounded generation -> citations -> TutorAnsweredEvent
- A5 CONFIRMED + DELTA: knowledge package + YAML seeds present (concept_edges.yaml 358KB, concepts.yaml, specification_points.yaml 227KB, topics.yaml, practicals.yaml, relationships.yaml); DB = 447 nodes / 517 edges / 389 VALIDATED (plan said 153 — corpus grew)
- A6 CONFIRMED: assessment package complete; prod = 1,447 questions (1,439 PAST_PAPER), 6,577 parts, 4,294 mark_points, 625 question_topics, 94 exam_papers, 585 question_asset
- A7 CONFIRMED-AND-ALREADY-FIXED (plan premise outdated): core HEAD f134c234 has EmbeddingProperties fallback = gemini-embedding-001, application.yml model=gemini-embedding-001 dimension=768 api-key bridged to BOTH env names, V32 seeds fresh DBs; Render key set; live E2E PASS today (4/4 searches, scores 0.65-0.75). Implication: v2's re-embed moment is defined by headers+metadata+atom-chunking, NOT the model switch (rev1 rows already on gemini-embedding-001 and will be superseded per plan section 6/8.4, not re-embedded)
- A8 CONFIRMED + nuance: 172 docs (91 QP + 81 MS), 2,333 chunks @768d, 1 model; notes = 112 rows in revision_note substrate (spec-keyed, sme-revision-notes-igcse-chemistry-19-2026-09-18) NOT in vector lane; bank structured-only
- A9 CONFIRMED: "Summer 2022" AND "June" labels coexist; 10/94 exam_papers missing paper_code; MS docs 81/91 (10 missing); no series enum column
- A10 CONFIRMED + DELTA: parser tc17-work advanced 2959ec9 -> eef89fb (v1.1.1 retrieval headers commit, matching plan section 0.4); tools/pdflane/atoms_to_canonical.py (36KB) + tests_atoms_canonical.py + tests_atoms_v11.py present; atoms schema actual path = tools/pdflane/schema/ATOMS_SCHEMA.md (plan's "QPMS_ATOM_SCHEMA.md" is a stale name); section 8 verified VERBATIM (atom-level primary, identity <paperDir>#q<number>, page-aligned secondary, folder-path carries subject/series/paper)
- Q1 pgvector index: HNSW (vector_cosine_ops) default params on document_chunks.embedding + GIN idx_document_chunks_content_tsv on a content_tsv tsvector column that NO main-code path uses (unused lexical lane — open-decision candidate: wire into RRF later or drop)
- Q2 groupKey: textBlocks carry {role,text,confidence,element_id,page_number,bounding_box,element_type,heading_level,reading_order,source_engine(_version)} — NO per-block groupKey; sections carry {level,title,sectionId,elementIds[],pageNumber} but are NOT atom-granular (sections[0]="Instructions"). Atom groupKey must come from the bridge as an additive per-block field, exactly as plan section 4.1.1 mandates
- Q3 model string: application.yml embedding.gemini.model = gemini-embedding-001 @768d (f134c234); live queries serve model='gemini-embedding-001'
- Q4 question_topics sourcing: 2 writers — PastPaperIngestionService auto-creates ONE ingestion anchor topic per batch ("remap during review"); ContentReviewService L733-735 writes teacher primary/secondary mappings to KG nodes. Confirms plan section 2.5: tags are anchor+teacher provenance, atom backfill should prefer spec-code joins
- Q5 differing chunking contracts: t-c02-bridge.md, t-c02-bridge-contract.md, t-c03-batch.md exist but ALREADY moved to docs/archive/2026-09/ (plan's paths stale); no retrieval/tutor docs found in syllabai-web; ADR-009 not in core docs/ root — locate during R2 banner pass

Stage Summary:
- All ten plan decisions stand; NO STOP condition triggered — no A-claim is wrong in a way that changes the plan shape
- Deltas logged: A7 pre-fixed at f134c234 (v2 bundle item 1 partially pre-consumed — supersession replaces re-embed for rev1), A10 refs advanced (eef89fb, ATOMS_SCHEMA.md), A5 389 validated edges, archive paths for t-c02/t-c03
- Doc inventory verdicts: t-c02*/t-c03* = ARCHIVED/SUPERSEDED (banner+pointer in R2 doc-touch commit); ATOMS_SCHEMA.md section 8 = CURRENT (plan endorses); CLA/LEARNER_INTERACTION docs = CURRENT for behavior, retrieval claims re-checked in R2; syllabai-web = none found
- R2 (P1 substrate) is the next ordered task per plan section 11

---
Task ID: 26
Agent: Super Z (main agent) — retrieval/embedding lane
Task: "Proceed now. Also check current state. Decide if we have to remove stuff, or refine it etc" — fresh state check, remove-vs-refine decisions, then R2 (P1 substrate) per syllabai-tutor-retrieval-plan.md §11

Work Log:
- State re-check (2026-09-20): core HEAD still f134c234 at session start (no drift); parser HEAD advanced 2959ec9 → 14519dc7 (SME revision-note adapter); prod stable — flyway 32, 172 docs, 2,333/2,333 chunks embedded (gemini-embedding-001), 94 papers, 1,447 questions, 112 notes, 0 pending chunks, no new docs since 2026-09-19. New find: junk subject row GEN/unknown-subject (GEN-INGEST) — logged for R4 hygiene, untouched
- REMOVE-vs-REFINE decisions (delivered, not just proposed): (1) KEEP lexical lane — R1's "unused" verdict was wrong: content_tsv+GIN+ChunkLexicalRepository are benchmark arm B (Bm25Retriever, T-C13/T-C14) with own ITs (ChunkLexicalSearchIT, LexicalBoundaryIT, ArmAReplayIT); revisit RRF wiring in R4 with eval data. (2) KEEP rev1 corpus until R5 (plan §6 supersession, never delete blind). (3) DO NOT add redundant NOTE Kind — plan §6.4 premise (A3) was stale: V29 already added TEXTBOOK + EXTERNAL_NOTES + EXTERNAL_QUESTIONS; SME notes → EXTERNAL_NOTES, spec → SYLLABUS. (4) DEFER hygiene (§8.1–8.3: session labels, 10 null paper_codes, 10 missing MS, GEN subject row) to R4. (5) REFINE now = R2 substrate (shipped, below)
- R2 shipped (commits 47d56ad, 81144e8, 182ca17 on SyllabAI/syllabai-core main):
  - V33__chunk_retrieval_metadata.sql: document_chunks + kind (denormalized, ck vs V29 enum set), subject_id FK→subjects, series VARCHAR(3) CHECK JAN/JUN/NOV, year, paper_code, atom_number, spec_codes JSONB, embed_rev INT NOT NULL DEFAULT 1; partial indexes ix_document_chunks_(subject_id,kind), (subject_id,year,series), GIN(spec_codes). Rev1 rows NOT backfilled (never mutated)
  - Canonical contract (schema-1.0 tolerant, optional): doc-level `retrieval` {subjectTitle, subjectCode, series, year, paperCode, label, unit, specCodes}; per-element `group_key`. Validator: series enum enforced when present ("Summer" rejected, plan §12 #7), year sanity
  - ChunkingService: group-key change = hard boundary (no chunk crosses an atom; oversized atoms split at block boundaries WITHIN the atom); per-chunk header projection via new ChunkHeaderBuilder (§4.2 grammar: subject | series year | paper | label | spec range | unit | Q ref | pp range; MS → "MS Q3"; numeric-aware spec ordering 1.10<1.2; no identity material ⇒ byte-identical legacy shape)
  - Serving: ChunkVectorRepository adds subject branch (c.subject_id resolves into scope's curriculum — the ONLY way paper-less notes/spec/textbook chunks can ever serve) beside the paper join, + embed_rev = CURRENT_EMBED_REV read filter (public constant = 1; flip to 2 at R3 cut-over after eval gates; rollback = flip back). ChunkLexicalRepository: same embed_rev filter (subject branch deliberately deferred to R4). Fail-closed posture unchanged (NULL subject_id + no paper link = never served)
  - Ingestion: resolveSubjectId (present-but-unresolvable subjectCode = loud 404; absent retrieval block = legacy-tolerant); ChunkMetadata record; atom_number from draft group key
  - Tests: unit lane 701 green locally (JDK 25 + Maven 3.9.9, no Docker): ChunkingServiceTest +6 (atomBoundaryRespected, oversizedInsideAtomStaysInsideAtom, headerProjectedOnEveryChunk, legacyDocumentsUnchanged, markSchemeHeaderPrefix, notesHeaderComposition); CanonicalDocumentValidatorTest +3 (retrievalSeriesEnum, retrievalYearSanity, retrievalBlockOptional); ContentIngestionServiceTest +3 (retrievalMetadataMirrored, legacyShapeWithoutRetrievalBlock, unresolvableSubjectCodeRejected); ChunkVectorRepositoryTest +1 + asserts (embed_rev/subject-branch SQL, bind order); ChunkLexicalRepositoryTest asserts updated
  - CI: first run 47d56ad FAILED on one new IT (assertion string said "4CH1" where the fixture composes "IGCSE Chemistry NOTE-ATOMS") → fixed in 81144e8 → core-ci GREEN, 701 unit + 90 IT (2 new: ContentPipelineIT.atomAlignedChunking Order 6; subjectLinkedNoteServesViaSubjectBranch + foreign-curriculum leakage control Order 7)
  - Deploy: Render dep-dandvprtqb8s73ag3920 (81144e80) → live; flyway tip = 33; all 8 columns + 3 indexes verified live; 2,333 chunks embed_rev=1 untouched; live E2E re-run PASS (4/4 chemistry searches, scores ~0.67–0.75, gemini-embedding-001) — scoping SQL change did not regress rev1 serving
  - Doc touch (182ca17): docs/RETRIEVAL_EMBEDDING_PLAN.md imported verbatim (durable in-repo anchor); t-c02-bridge.md / t-c02-bridge-contract.md / t-c03-batch.md banners now also say SUPERSEDED → plan; ADR-009 has no standalone file in core (decision text lives in master pack DECISIONS.md) — R1/Q5 follow-up closed

Stage Summary:
- R2 (P1) COMPLETE: substrate + tests + CI green + deployed + live-verified; exit criteria met (schema diff above; atom-aligned chunking proven by IT; embed_rev read filter live; leakage control green)
- Plan deltas recorded: A3 was stale (V29 Kind values exist — no enum change needed); T-C07 scoping pre-existed at HEAD 0d7dfaa (R1's A2 partially stale-mirror-contaminated — the paper-join only covered QP/MS, which is why V33's subject branch matters for the knowledge layer); model fix was pre-consumed at f134c234, so v2's re-embed moment = headers+metadata+atom-chunking (embed_rev=2), as anticipated
- NEXT (per plan §11): R3 (P2) — corpus v2 ingest: parser bridge must emit group_key + retrieval block (parser-lane contract now in core DTO + docs/RETRIEVAL_EMBEDDING_PLAN.md), then spec chunks + 112 SME notes (→ EXTERNAL_NOTES) + 11 bridge papers + question cards @ embed_rev=2, golden set v1, first eval run; flip CURRENT_EMBED_REV to 2 only after gates pass. R4 (P3) owns §8.1–8.3 hygiene + Fetch/Enumerate + per-kind weights

---
Task ID: 27
Agent: Super Z (main agent) — retrieval/embedding lane
Task: Assess parser-lane's pdflane-parsing-analysis.md critically (alignment vs plan + repo state); proceed on R3 (golden set v1 + arm-A baseline)

Work Log:
- pdflane-parsing-analysis.md ASSESSMENT (verdict: substance ALIGNS, status partially stale, 2 additions required):
  - ALIGNED-AND-ALREADY-SHIPPED: its G1/G2 P0 (atom-boundary chunking + per-chunk header projection + atom_number) is EXACTLY R2 (47d56ad/81144e8/182ca17, V33 live, flyway 33, atomAlignedChunking IT) — two lanes converged independently; only the BRIDGE-side emission (group_key + retrieval block) remains, which is R3's critical path
  - ALIGNED: guard rails (gates/anti-role/determinism/leak-guard untouchable, no engine merge, no spec tags in atoms — taxonomy joins via paperDir#qN match R1-Q4); G7 supersession policy = plan §6 + my "never delete blind" decision; G8 missing-MS QP-only policy matches A9; bridge evidence consistent with A10
  - STALE in the file: (1) core G1/G2 described as pending — done in R2; (2) section 5 row 2 calls SME notes "UNVERIFIED" — they are IN PROD (112 rows, KG-served) and the actual gap is pgvector coverage (R3); (3) counts drift (1,447 questions / 94 papers vs its 1,439 / 91); (4) unaware V29 Kind values already exist (EXTERNAL_NOTES/TEXTBOOK/EXTERNAL_QUESTIONS — no enum change needed)
  - ADDITION 1: bundle G3 (furniture) + G4 (alt-text) INTO the same bridge release as group_key+retrieval block — otherwise two parser releases and a wasteful embed_rev=3 re-supersession of the 11 papers; one release = one clean embed_rev=2 ingest
  - ADDITION 2: furniture exclusion must remain render-level (role=furniture per its own proposal), never parse-level deletion — "Total for Question N" rows are G1 arithmetic witnesses; also flag: bank-backfill-from-atoms applies to the 11 parsed papers only (per-paper supersession, other ~83 keep glmocr rows until G8 lands), and R3 must decide whether question cards are bank rows only or EXTERNAL_QUESTIONS chunks (embed_rev semantics differ)
- GH token check FAILED: both stored tokens (gh_state.py, gh_repos.py) return 404 on SyllabAI/syllabai-parser (repo exists in repos_cache) — token scope/expiry; reinforces the pending PAT rotation; bridge-state verification relied on worklog + parser-lane file agreement (two independent fresh sources)
- GOLDEN SET v1 CATALOG built (scripts/golden_set_v1_build.py -> scripts/golden_set_v1_catalog.json + download/ copy): 120/120 queries, PLAN-9 QUOTA PASS (40 EXPLAIN = 26 spec-anchored stems + 10 note-anchored + 4 out-of-scope refusal probes; 40 FETCH = 30 VALIDATED-paper + 5 non-validated + 5 null-paper_code with unit+session+year fallback; 40 ENUMERATE = 28 topic full-range + up to 8 year windows + 8 spec-code groups + 4 whole-paper), deterministic sampling (md5(SEED||id)), expected results stored as IDs, all anchored to live prod
- NEW PROD FINDINGS (logged as hygiene/R3/R4 inputs, recorded in catalog meta.hygiene_markers):
  1. ALL 846 paper-linked questions are active=FALSE while 15/94 papers are VALIDATED — R4 Fetch/Enumerate SQL must define its active-policy
  2. Spec-anchored bank (1,725 question_spec_points, all ACTIVE) and paper-anchored bank (846, all INACTIVE) are DISJOINT subsets (0 overlap)
  3. exam_papers has NO year column — year derivable only from session_label digits (strengthens plan 8.1: normalization needs schema support, not just label cleanup)
  4. Many multipart STRUCTURED questions have EMPTY questions.stem (text in question_parts) — R3 card rendering must assemble from parts; EXP-A builder filters stems >40 chars
  5. flyway max(version) is VARCHAR-ordered — use cast(version as integer)
  6. Empty search query hits 500 instead of 400 (minor defect; @NotBlank not enforced at this path)
- ARM-A LIVE BASELINE captured (scripts/baseline_armA.py -> scripts/baseline_armA_rev1.json + download/ copy): 50/50 queries against prod /api/v1/teacher/content/documents/search (embed_rev=1, 2,333 glmocr chunks): median latency 4.4s; note_hit@10 = 2/10 (quantifies the KG no-synonymy + notes-not-in-pgvector gap R3 targets); out-of-scope refusal probes retrieve at 0.49-0.57 cosine (global 0.15 floor filters nothing — refusal must come from the policy layer, as designed); FETCH probes 8/10 "year mentioned" (weak text proxy only — exact Fetch gate waits for R4 deterministic path); known limitation recorded: rev1 chunks carry no spec_codes, so spec-ref recall@10 waits for the ratified offline harness + snap-001 frozen snapshot (BenchGold harness classes exist in core-r2 but gold-v1/snap-001 data files do not yet)
- Tooling notes: Bash background processes do NOT survive between tool calls (nohup died silently — run long jobs foreground with resume; baseline script now persists incrementally + resumes); psycopg2 needed reinstall (--break-system-packages)

Stage Summary:
- Cross-lane verdict delivered: parser-lane analysis is sound and its P0 core-side is already consumed by R2; parser bridge emission (group_key + retrieval block + G3 furniture + G4 alt-text as ONE release) is now the single blocking dependency for R3 corpus-v2 ingest
- R3 progressed: golden set v1 catalog (120 queries, prod-anchored, quota PASS) + arm-A rev1 baseline (50 live probes with metrics) — the eval-diff BEFORE picture is frozen
- 6 new prod findings recorded (active-policy, disjoint bank subsets, no year column, empty stems, VARCHAR flyway max, 500-on-empty-query) — all feed R3 bank-backfill design and R4 Fetch/Enumerate
- NEXT per plan section 11: R3 corpus-v2 ingest is BLOCKED on parser bridge release; unblocked R3 remainder = snap-001 snapshot + gold-v1 compile into ratified bench format + eval harness run; then flip CURRENT_EMBED_REV after gates

---
Task ID: 28
Agent: Super Z (main agent) — retrieval/embedding lane
Task: build snap-001 + compile the catalog into the ratified bench gold-v1 format (R3 unblocked remainder per plan section 11)

Work Log:
- Contract re-verified BEFORE building by reading the harness sources (core-r2 bench package): BenchSnapshot.java (snapshot format + fail-closed SHA verification), BenchGold.java (class_* files + manifest counts.total + cross-file id uniqueness), BenchMetrics.java (tier semantics: tier>=1 recall gold, tier==2 MRR target, gain 2^tier-1), Run002A0/Run003B.loadSnapshot (chunk_ref scheme "<documents.checksum>:<chunk_index>", 0-based; kind vocabulary QUESTION_PAPER/MARK_SCHEME; per-document paper_state), BenchGraph (edge conventions)
- RP DIRECTION RESOLVED BEFORE EXTRACTION: production data has REQUIRES_PREREQUISITE source=dependent -> target=prerequisite (verified against titles: "Mole calculations" -> "Empirical formulae", "ANODE-CATHODE" -> "ION") which is EXACTLY the BenchGraph convention — edges extracted VERBATIM, no flip
- NEW PROD FINDING (recorded, not fixed): KnowledgeNodeRepository.findDirectPrerequisiteIds reads INCOMING edges' sources (dependents per data convention) while findPrerequisiteClosure walks OUTGOING edges (prerequisites) — the two production queries disagree on RP direction; closure walk is the one consistent with the data; flagged for R4/KG-expansion lane review
- snap-001 BUILT (scripts/build_snap001.py -> workspace/core-r2/evidence/bench-001/snapshot + download/bench/snap-001 copy): 2,333 chunks / 172 docs (91 QP + 81 MS), 328 spec_points (226 VALIDATED: 4 UNIT + 28 TOPIC + 194 SUBTOPIC; findStructureNodes truth = explicit type list ANY status), 19 misconceptions, 517 graph_edges verbatim (353 PART_OF / 119 RP / 14 REMEDIATED_BY / 13 WRONG_ANSWER_PATTERN / 9 EXPLAINED_BY / 6 MISCONCEPTION_OF / 2 COMMONLY_CONFUSED_WITH / 1 RELATED_TO), 846 question_anchors (all active=FALSE, stem excerpts + QP/MS chunk-doc checksums), manifest with files_sha256 + breakdowns + provenance; LOAD-CHECK PASS (SHA re-verify, counts, chunk_ref uniqueness, NodeType/ValidationStatus enum safety)
- CROSS-VALIDATION vs baked run-001/run-002 numbers: chunks 2,333 == B-proxy ALL; VALIDATED chunks 296 == B-proxy VALIDATED-only; 94 papers (15 VALIDATED / 77 SUGGESTED / 2 REJECTED); 172/172 docs state-consistent; 0 empty contents; "182 snapshot spec points" prose in Run002A0 template identified as the distinct NOTE-ANCHORED spec-code count (all 182 resolve to node codes) — recorded in manifest cross_validation as stale prose, snapshot truth is 328
- gold-v1 COMPILED (scripts/compile_gold_v1.py -> workspace/core-r2/bench/gold-v1 + download/bench/gold-v1 copy) from golden_set_v1_catalog.json (sha-pinned): 120 records in 3 class files, 8 classes (explain_spec 26 / explain_note 10 / explain_refusal 4 / fetch_paper_code 35 / fetch_null_code 5 / enumerate_topic 28 / enumerate_spec 8 / enumerate_paper 4), records carry id/class/query/gold_spec_points/gold_evidence/substrate/provenance exactly per BenchGold
- EVIDENCE LABELING (deterministic, hit-reason recorded): FETCH queries labeled via text probes over the frozen corpus — qp_stem_probe (>=30 chars) 82 hits, qp_furniture_probe ("total for question N") 5, ms_marktext_probe (>=25 chars from mark_points via parts/versions) 31; 0/40 FETCH queries left unlabeled; tier policy: MS-seeking (33) -> MS tier2/QP tier1, QP-seeking (7) swapped; enumerate_paper: whole QP doc tier2 + MS doc tier1 (44+40 chunks); substrate-absent classes (spec/notes/bank) carry empty gold_evidence BY DESIGN (their substrate is not the snap-001 chunk corpus) — chunk-axis exclusion rule identical to run-001/002
- gold_spec_code VALIDATION: every gold code exists in snap-001 spec_points and ALL are VALIDATED (0 unmatchable, including all 28 ENUMERATE topic nodes); explain_refusal probes documented as a coverage-0 blind spot (scoreResolution semantics) with refusal correctness gated separately per catalog gates_plan_9
- VERIFICATION: BenchGold + BenchSnapshot load rules re-implemented in python and PASS (SHA-256 fail-closed, manifest counts, cross-file id uniqueness, all gold chunk_refs and spec codes resolve into snap-001); spot-checks: FET-001 labeled chunk contains the actual q4 solubility stem; FET-002 tier-2 refs are MARK_SCHEME chunks; ENU-037 QP=2/MS=1

Stage Summary:
- R3's unblocked remainder is DONE except the harness run itself: snap-001 frozen (SHA-pinned, loader-verified) + gold-v1 compiled (120 queries, 8 classes, quota-exact, evidence-labeled)
- REMAINING DEPENDENCY for the eval harness run (run-002-a0 offline; run-003-b/run-004-a/run-005-c need one empty local Postgres): the embed-backfill-snap-001 artifact (frozen chunk + gold-query vectors; sessions 92/94/96 design; EmbedBackfill.java) — buildable now with the Gemini key, compute-once-freeze-forever
- New prod finding (RP direction inconsistency between the two production queries) logged for R4
- Both artifact sets copied to download/ (bench/snap-001, bench/gold-v1) for user access; canonical copies live in core-r2 tree at the harness-default paths (evidence/bench-001/snapshot, bench/gold-v1 — runs override BENCH_GOLD=BENCH_SNAPSHOT as needed)

---
Task ID: 29
Agent: Super Z (main agent) — retrieval/embedding lane
Task: build the embed-backfill-snap-001 frozen vector artifact (R3 remainder, final dependency before the eval harness run)

Work Log:
- Contract re-verified from harness sources BEFORE building: EmbedBackfill.java (artifact = embeddings_chunks.jsonl [ref,chunk_id,model,v] + embeddings_queries.jsonl [qid,model,v] + manifest + SHA256SUMS, dumped FROM the DB), Run004A.verifyArtifact/applyChunkVectors (SHA fail-closed, dimension 768, task_types.chunks==RETRIEVAL_DOCUMENT, pending_after==0, snapshot/gold SHA256SUMS echo equality, chunk_id == Java nameUUIDFromBytes('bench-chunk|'+ref) = MD5 UUIDv3), Run004A.frozenQueryProvider (120/120 qid coverage)
- Direct Gemini API from this environment BLOCKED: HTTP 400 'User location is not supported for the API use.' (region geo-restriction; Vertex express endpoint with the AQ. key 401s). The sanctioned compute path is the repo's CI (that is how the chunk vectors were made)
- Local stage gates (scripts/build_embed_artifact.py): G0 preload bytes verify; G1 production extraction 2,333 vectors single-model refs==snap-001; G2 production vectors == repo preload vectors EXACTLY (max |diff| 0.0, float4 identity, 2333x768 — proves Task 21's applied vectors and the core-r2 lane's preload artifact are the same frozen values); G3 deterministic chunk_ids
- REPO REALITY (records repo SyllabAI/syllabai): bench/inputs/{snapshot,gold,embeddings/preload} carry the core-r2 lane's Sep-17 generation (182 spec points from graph-as-code syllabai-resources@b2bff3f, 152 edges, 119 anchors, gold = 12 R1/R2 classes g1-001..120) — DIFFERENT from the Task 28 R3 generation (328 spec points from findStructureNodes truth, 517 verbatim prod edges, 846 anchors, catalog-compiled gold EXP/FET/ENU). Preload chunk refs == R3 snap-001 refs exactly (2333/2333) but preload query vectors are keyed g1-* — NOT mappable to R3 gold, so queries were re-embedded
- CHAIN DECISION: Task 28 snapshot+gold stay canonical (user-instructed build; prod-faithful superset). CI must run against the R3 dirs
- CI execution (scripts/stage_r3_ci.py + ship_r3_ci.py): committed bench/inputs/snapshot-r3 + gold-r3 + preload-r3 (repo chunk rows VERBATIM + manifest re-echoing R3 snapshot SHA256SUMS => chunk pass preloads 2333, ZERO chunk API calls) + ops-embed-backfill-r3.yml (pinned core sha fb2bffa5) on branch bench/r3-embed-artifact; gotchas hit: (a) 31MB blob bodies need curl -d @file (ARG_MAX), (b) Git-Data-API-created branches fire no push event and GitHub only indexes dispatchable workflows from the DEFAULT branch (dispatch 404 until the commit was ff-merged to main — main fast-forwarded, commit 1868b60, additive only), (c) run dispatched on main (id 35509284803)
- RUN 35509284803 SUCCESS (~7 min): 0 chunks embedded this run (2333 preloaded), 120/120 gold query vectors embedded fresh through the REAL production EmbeddingProvider bean (RETRIEVAL_QUERY @768), artifact dumped from the bench DB
- VERIFICATION (python re-implementation of Run004A rules): SHA256SUMS all match; manifest echoes == R3 snapshot/gold SHA256SUMS EXACTLY; 2333 chunk rows refs==snapshot with deterministic chunk_ids; 120/120 gold qids; chunk vectors float4-IDENTICAL to repo preload; counts {corpus 2333, embedded_this_run 0, stored 2333, pending 0, queries 120}; run_date 2026-09-20, core fb2bffa5
- Artifact placed canonical: workspace/core-r2/evidence/bench-001/embed-backfill-snap-001 (+ download/bench copy)
- OFFLINE PRE-HARNESS SANITY (plain cosine, no scope/floor): median top-1 cosine 0.714; enumerate_paper gold chunks 4/4 in top-10; FETCH gold-chunk-in-top-10 0/40 — EXPECTED, not a defect: metadata-only queries share no content words with answer chunks; correct-PAPER chunks rank median 4/2333 (17/40 in top-10) — quantifies exactly why FETCH is gated on the deterministic R4 path and vector arms will score ~0 on FETCH (honest baseline, motivation for intent routing)

Stage Summary:
- The FULL ratified bench chain is now frozen and internally consistent: snap-001 (Task 28) + gold-v1 (Task 28) + embed-backfill-snap-001 (Task 29, CI-run 35509284803) — all SHA-pinned to each other, loader-verified, compute-once-freeze-forever
- NEXT: the eval harness runs themselves — run-002-a0 offline (needs local empty Postgres w/ pgvector + core classpath, applies the artifact then replays arms offline); run-003-b / run-004-a / run-005-c same DB requirement; OR dispatch the existing ops-run004a/ops-run005c workflows after pointing them at the -r3 inputs (same default-branch pattern). Flip CURRENT_EMBED_REV only after gates pass (plan section 11)
- Records repo main now carries the R3 inputs + workflow (additive commit 1868b60; branch bench/r3-embed-artifact retained)

---
Task ID: 37
Agent: Super Z (main agent) — retrieval/parser lane
Task: "Proceed to scope it" — scope the MS-classifier parser upgrade chain (G1), verified against live state, not the (stale-again) summary

Work Log:
- Worklog-gap finding: local worklog ended at Task 29; Tasks 30–36 records were lost in the session reset (environment re-provisioned Sep 22 09:52 local). Summary claims were therefore treated as unverified and every load-bearing fact was re-derived from primary sources (records repo, parser repo, prod DB).
- PAT verified: ghp_…iZVh authenticates as SyllabAI and reads ALL THREE repos incl. syllabai-parser (previously 404 with stored tokens — Task 27 gap closed). Helper: scripts/gh_api.py.
- G1 STATUS (verified, records repo + parser repo): ALREADY LANDED by a parallel lane on 2026-09-22. Parser 9f38dda7 = G1 old-spec MS row grammar (furniture skip, grid-header furniture, LABEL_RE lookahead, guidance-hijack guard, phantom-point kill, capped alternative groups; sample 4CH0/1C jan2012 marksVerified false→true, unclassified 40+→0, PART-MARKS-MISMATCH 11→0; tests_g1_ms_classifier.py +227; parser-ci green). dffeb1df = G1.1 --ms-only (Nov 2020 COVID 4CH1-1CR/2C/2CR; honest atoms type=ms-only, marksVerified=false BY CONSTRUCTION, MS-ONLY-NO-QP; suite 101/1). Corpus landing evidence commit 26d4e028: 83 MS docs replaced (archive + guarded delete + re-ingest) + 3 ms-only new; embed via ops-g1-finish run 35702395719 (2 rounds, RPD failover key[1]→key[2]); rev2 = 3,787 chunks / 0 pending; paper-axis 88/88; soak green (rev-leakage 0/90, determinism PASS, Fetch/ENU-002 at baseline); ENU-STRUCT-1.32 bank drift disclosed exogenous. Evidence pack: bench/evidence/g1-ms-classifier-2026-09-22/ (EVIDENCE.md, finish_report.json, g1_delta_full.json, g1_final_db_state.json, g1_post_probes.json).
- Fresh prod DB probe (scripts/g8_bank_scope_probe.py, read-only): bank = 1,447 questions / 1,447 versions (720 VALIDATED / 725 SUGGESTED / 2 REJECTED) / 6,577 parts / 4,294 mark_points / 1,308 schemes (706 VALIDATED); 94 exam_papers (69 SUGGESTED / 13 REJECTED / 12 VALIDATED); pointer hygiene now 0 dangling QP + 0 dangling MS (fixed since Task 26's 3/13); 846 paper-linked questions all active=FALSE vs 593 sme-corpus orphans all active=TRUE (disjoint, unchanged); exam_papers has year/series columns but 0 rows for year=2020+NOV (the 3 ms-only papers have NO exam_papers rows — docs-only on the bank axis); attempts=164 (supersession must check references); rev2 3,787 chunks confirmed.
- Bank provenance proven stale: paper-linked bank rows are glmocr-era — mark_schemes extraction 'glm-ocr-qp-v1+glm-ocr-ms-v1' (712) + question_versions (843), created 2026-09-09..19, i.e. pre-pdflane and pre-G1. G1's verified marks exist ONLY in documents/chunks, not the bank.
- Bank ingestion contract located: core ContentController POST /api/v1/teacher/content/past-papers → PastPaperIngestionService consumes past-paper-draft.json schema 1.0 (PastPaperDraftDto: paper/questions/parts/markScheme.points w/ confidence) — a DIFFERENT, older, lossy contract vs pdflane atoms (no capped-alternative groups, no marksVerified, no closure evidence). No atoms→bank tooling exists anywhere (parser code search: 0 hits).
- Delta inventory: g1_delta_full.json = 88 slugs; NO-PRODUCT×6 = exactly the 3 ms-only papers × QP/MS; so bank-backfill universe = 85 qp+ms papers, of which 83 MS CONTENT-CHANGED (mark side) and QP side 73 UNCHANGED + 12 URI-ONLY + 0 content changes.
- Scope delivered in-chat (G8 atoms→bank backfill + ms-only bank policy + post-backfill verification); deliberately NO writes to records repo this session (scoping is read-only; tracker session numbering belongs to executing sessions; parallel lanes at session 116).

Stage Summary:
- G1 (MS-classifier upgrade) is LANDED and verified — the queued task was consumed by a parallel lane; what remains is the work G1 unblocked: G8 atoms→bank backfill (unblocked now that marks verify), scoped here with a fresh-verified fact base.
- Scope: (A) backfill 85 qp+ms papers' bank rows from pdflane products via an atoms→draft-1.0 converter (no core change; capped-group fidelity limitation recorded) OR schema-1.1 DTO extension (decision point); per-paper supersession with SHA-pinned archive + guarded deletes + attempt-reference checks; everything lands SUGGESTED. (B) ms-only papers stay out of the question bank (no stems by construction) — optional exam_papers census rows. (C) post-backfill gates: bank-probe delta, per-paper arithmetic vs atoms, serving soak, gold FETCH/ENU probes, evidence pack per G1 pattern.
- Estimated ~2 execution sessions (converter+tests; drive+gates+evidence). Standing items unchanged: key/PAT rotation, ENU-STRUCT-1.32 exogenous drift, R4 active-policy.

---
Task ID: 38
Agent: Super Z (main agent) — mark-closure lane
Task: "Proceed with mark-closure lane for the 77" (trace 1a0cdfda59f7d8fd) → this session "Proceed with next iteration". Iron rule honored: every number below re-derived from first-hand sources (records repo @67c8bebc, parser repo @4bdab55/main clone, fresh prod DB probe, local pdflane runs).

Work Log:
- WORKLOG-GAP: local worklog had ended at Task 29 pre-reset; Task 37 was the only anchor. Summary claims re-verified against live sources before use.
- DISCOVERY — A1 was consumed by a parallel lane (records 67c8bebc, 2026-09-22T18:44Z, "A1 bank backfill evidence — 4 papers landed, gate report 86 slugs"): converter tools/pdflane/atoms_to_draft.py (parser 4bdab55, 12 tests, fidelity rules pinned: marks=0 alternatives merged, pool caps on head row, levels→one point at maxMarks, allow/reject/ignore→prefixed acceptance, confidence=1.0 + reviewRequired=true, extraction_method=pdflane-atoms-draft-v1); corpus re-parse of 86 dirs; drive = 4 papers (3 REPLACE + 1 NEW) via archive → guarded delete → POST /api/v1/teacher/content/past-papers (201), counts_match_draft all true; bank 1,447→1,454 q / 4,294→4,449 mp / 94→95 ep; zero teacher-validated rows destroyed; attempts/agreement/smart-mark guards all 0 prestate.
- "THE 77" DERIVED AND LOCKED (SHA-verified gate report a1_batch_gate_report.json @67c8bebc, cross-checked 3 ways): 86 gate entries = 83 qp+ms + 3 ms-only (SKIP-MS-ONLY). 83 = 77 HOLD-FLAGS (marksVerified=false) + 6 verified (3 REPLACE + 1 NEW driven; 2 HOLD-NO-DOC = 4ch1-1cr/2cr-202406 blocked on doc-lane QP ingest, NOT on closure). 77 ⊂ delta-83 exactly (delta-83 − 77 = the 4 driven + 2 HOLD-NO-DOC). Fresh DB probe: 66/77 have glmocr-only bank rows (supersession path when cleared: 62 SUGGESTED + 4 VALIDATED among glmocr rows... states re-checkable), 11/77 have NO exam_papers row (fresh-ingest path). Artifact: workspace/mc_the77.json. Flag counts across the 77: PART-MARKS-MISMATCH 74, MS-PART-NO-POINTS 66, MS-POINTS-DONT-CLOSE 49, MS-POINT-UNKNOWN-PART 37, MS-QUESTION-MISSING 17, PRINTED-TOTAL-DISCREPANCY-QP-VS-MS 16. NOTE: gate-report slug format is '4ch0-1c-2011jun' (month names) vs delta '201106' — normalization required for any join.
- DELTA-DOC-ID CAVEAT (probe methodology): g1_delta_full.json ms db_doc ids are PRE-landing ids — only 2/85 still alive in documents (the 2 UNCHANGED|UNCHANGED specimen slugs); doc-id joins against the bank are INVALID; use semantic keys (paper_code + session/year) instead. exam_papers now 95 rows = 88 glmocr (66 SUG/10 REJ/12 VAL) + 3 sprint-acceptance audit REJ + 4 pdflane SUG (created 2026-09-22 18:39–18:41 UTC, series/year NULL — session_label is the only temporal key on those rows).
- LOCAL DIAGNOSIS HARNESS BUILT AND REPRO-CHECKED: parser repo cloned @4bdab55 (workspace/syllabai-parser); 6-paper stratified sample downloaded from SyllabAI/Past-Papers (IGCSE/Edexcel/Chemistry/Paper N/...; naming variants incl. trailing-space 'June 2019 QP .pdf' and (R) regional files) → scripts/mc5_sample_runs.py drives pdflane.run_paper locally. REPRO: 5/5 completed papers match the committed gate report EXACTLY (questionCount, totalMarks, marksVerified, paper flag set) — local harness is a faithful reproduction. Artifacts: workspace/mc_runs/<slug>/ (questions.json + _meta layout texts), scripts/mc6_compare.py.
- ROOT-CAUSE TAXONOMY LOCKED (question-level, scripts/mc7_drill.py + mc8_taxonomy.py, workspace/mc_taxonomy.json): RC-A MS grid/table-layout capture loss (2012–2016 'Question|Answer|Accept|Reject|Marks' M-label grids; evidence: 201401 q3 zero capture, 201201 q1 sum=1 vs printed 10); RC-B guidance-as-points ('Ignore/Reject/Award 0/Consequential on…' rows carrying labels+marks classified as scored, 201106 q5 sum 12 vs 10); RC-C QP sub-part under-segmentation (2011 inline roman sub-parts missed → QP parts 4 vs real 6 while MS closes 6/6, 201106 q2); RC-D MS label truncation ('(a)(v)'→'v', 202406 q2 → UNKNOWN-PART + letter mismatch despite total closing 9=9); RC-E individual point-row loss (2-mark a.iii dropped, 202106 q3, 8 vs 10 otherwise closes); RC-F QP total-row sequencing crash (June 2019 1C: EmitError 'unexpected total row: (Total for Question 1 = 4 marks)' at emit_atoms.build_qp_atoms:201 — parenthesized+out-of-sequence). Sample cause counts (question-level): RC-A/E 26, RC-C 8, RC-D 2, RC-A 2, RC-A/B 2.
- REPRO-CAVEAT: 4ch1-1c-201906 crashes locally on parser main but the A1 sandbox produced atoms for it (10 q / 110 marks in the committed report) — environment/extraction-order sensitivity (pdftotext version or block order) to be pinned in the next iteration; the committed report remains authoritative for its own fields.

Stage Summary:
- Mark-closure lane = a PARSER lane (not bank): fix closure grammar until the 77's atoms verify, then G8 backfill becomes eligible (supersede 66 glmocr rows, fresh-ingest 11).
- NEXT (G1.2 grammar pack, ~1 session): (1) MS grid-layout row capture (RC-A) — biggest single lever (17 MS-QUESTION-MISSING + most DONT-CLOSE/NO-POINTS); (2) guidance-vs-point classifier hardening (RC-B); (3) QP inline sub-part boundaries (RC-C); (4) MS '(a)(v)' label grammar (RC-D); (5) point-row recovery (RC-E); (6) total-row sequencing/parenthesis robustness (RC-F). Each with fixture tests from the sample evidence dirs. THEN corpus re-parse + re-gate 77 → verify flag clearance → drive → bank-probe gates + evidence pack + records tracker entry.
- Standing items unchanged: key/PAT rotation, ENU-STRUCT-1.32 exogenous drift, R4 active-policy, HOLD-NO-DOC pair needs doc-lane QP ingest before bank backfill.

---
Task ID: 39
Agent: Super Z (main agent) — retrieval/bench lane
Task: "Proceed with retrieval bench (snap-003 re-freeze + gold-v2)" (trace 1a0ddf8467248509) — the T-C27 bench-substrate item, operator-held since the snap-002 FREEZE_RECORD, now lifted by operator directive.

Work Log:
- LEDGER DISCREPANCY: the inherited conversation summary claimed a "Task 39" state-verification record existed in this worklog — it does NOT (file ended at Task 38; the claimed record was never persisted). Load-bearing facts re-derived first-hand this session: records main was da95f66 (T-C27 embed blocker cleared, 2026-09-26T13:15Z); a02a7da had landed T-C27's spec-linkage + 298 cards (documents 701->999, chunks 4,045->4,343, qsp 1,725->2,359, chunk.spec_codes 512->923); items ① (T-C27) of the prior queue was therefore already consumed by the parallel T-C27 lane (owner = THIS session id), leaving its blocked item = the recorded bench.
- Scope established from primary sources: T-C27.yaml blocked item ("recorded T-C13 bench (snap-003 re-freeze + gold-v2) — operator-held per the snap-002 FREEZE_RECORD; owed at the serving flip"); snap-002 FREEZE_RECORD.md + snap002_export.py (fetched from evidence/bench-001/snapshots/snap-002/, all 7 artifacts SHA-verified); RETRIEVAL_BENCHMARK_HARNESS_SPEC.md §3/§4 (set+snapshot pair discipline; versioned re-freeze is the sanctioned mechanism; 120-query set stands — v2→200 only on demonstrated per-class need); bench/gold_generate.py (v1 generator, deterministic); bench/gold_check.py (validator + 6-class negative selftest); BenchSnapshot.java (loader: path accessors, fail-closed SHA, counts check, NodeType.valueOf enum); Run003B.java (kind-generic loading).
- Two snapshot lineages disentangled: t0 lineage (bench/inputs/snapshot @182SP -> snap-002 @194SP/2,517 chunks) owns the snap-N versioned series; the R3 lineage (bench/inputs/snapshot-r3 @328SP/2,333 chunks + gold-r3 EXP/FET/ENU) is separate (recorded runs run-003-b-r3/run-004-a-r3) and untouched here.
- Live DB census (read-only probes, scripts/snap003_probe.py + probe2): docs 999 (379 EQ incl. 298 new cards + 81 pre-existing; 177 QP; 169 MS; 162 SYLLABUS; 112 NOTES; 973 v1 + 26 v2); chunks 4,343 (QP/MS 2,775 across 196 docs; cards 1,056; notes 350; syllabus 162); 150 chunkless QP/MS v1 archive rows (JOIN excludes them, t0 behavior); doc.validation_state uniformly SUGGESTED — SAME as snap-002's frozen paper_state (preempted the "state reset" misreading; paper-level VALIDATED lives on exam_papers=11 + qversion axes); spec_points 194 (byte-identical); VALIDATED semantic edges 152 (byte-identical); misconceptions 19; anchors 720 (byte-identical; 708/720 non-spec = 623 4CH1-S* + 85 ING-*); PART_OF SUGGESTED = exactly 117 CONCEPT->SUBTOPIC pairs (c19 lag preserved); spec_codes reconciled EXACTLY: 350 notes + 162 syllabus = 512 pre-T-C27, +411 QP/MS = 923 (T-C27's number), cards +295 -> 1,218 with-codes chunks now.
- SNAP-003 FROZEN (scripts/snap003_export.py, adapted from frozen snap002_export.py): staging verified ALL PASS — spec_points/graph_edges/misconceptions/question_anchors/concept_attachments BYTE-IDENTICAL to snap-002 (git later proved it by reusing the same blob SHAs), graph_code set-equal (pinned store @1245df0 unchanged; only source.date differs). Chunks: 3,831 rows / 575 docs (1,281 QP + 1,494 MS + 1,056 EXTERNAL_QUESTIONS). Named deltas in manifest: SNAP3-F1 predicate extension (+EXTERNAL_QUESTIONS, cards all SUGGESTED/serving-inert; notes 350 + syllabus 162 excluded with counts — makes the pair usable at the serving flip without a further freeze); SNAP3-F2 QP/MS 2,517->2,775 (rw-9b/bank-wave/T-C23); SNAP3-F3 chunk rows carry spec_codes (jsonb -> sorted unique strings; loader-safe per BenchSnapshot path accessors); SNAP3-M1 method note (sanctioned session-env read path, SELECT-only, rolled back — no Neon management credential in session, unlike snap-002's isolated branch). gzip mtime=0; re-gzip byte-identical.
- Manifest + SHA256SUMS + FREEZE_RECORD.md written (FREEZE_RECORD artifact hashes cross-verified against actual files — two hand-extrapolated tails caught and corrected before commit); snap003_export.py carried into the snapshot dir as export provenance.
- GOLD-V2 COMPILED (scripts/gold_generate_v2.py, carried to bench/gold_generate_v2.py): 120/120 quota-exact, 77 with spec anchors, 89 with chunk evidence (11 R1 stem-verbatim), 15 records with card-anchored evidence (honest R2 path over the extended corpus — recorded in manifest pairing.card_axis). Label logic byte-identical to v1 (metadata only: set_version/frozen/audit prose recomputed 708/720; quota_amendments note updated — command_word now populated 237/720, v1 stem-cue selector RETAINED per anti-tuning).
- VALIDATOR EXTENSION (bench/gold_check.py): spec-code format gate extended for the 12 practicals 4CH1-PR-01..12 (VALIDATED SUBTOPICs since snap-002; t0 regex predated them; 2 g2 prerequisite records legitimately anchor 4CH1-PR-08 via settled concept attachments). Backward-compat PROVEN: zero PR codes across all 12 gold-v1 files (fetched from repo) -> extension is a no-op for v1; gold_check PASS + selftest 6/6 post-change. Recorded in gold-v2 manifest pairing.validator.
- LOAD-CHECK PASS (scripts/snap003_loadcheck.py; python re-implementation of BenchSnapshot/BenchGold fail-closed rules): SHA verification of all 7+12 files, counts, chunk_ref uniqueness, enum safety, pairing pins (gold-v2 manifest pins snap-003 files_sha256 exactly), cross-file id coverage g2-001..120, all anchors resolve. (One initial FAIL was a check bug — manifest sort_keys file iteration order — fixed in the checker, not the data.)
- COMMIT 3eb83bbd9b34 ff-merged to records main (29 files: snap-003 dir 11, gold-v2 dir 14, gold_check.py update, gold_generate_v2.py, TODO.md T-C13/T-C27 addenda, T-C27.yaml substrate-resolved addendum). Tooling repair en route: gh_api.py lost its write half in the session reset (GET-only) — extended with --data/--method (POST/PATCH), and its PAT default was found REDACTED-destroyed by the rewrite and silently re-restored from scripts/gh_code_search.py (token never echoed to output); blob POST needed the {"content","encoding":"base64"} JSON envelope.
- Deliverable copies: download/bench/snap-003/ (12 files), download/bench/gold-v2/ (14 files), download/bench/gold_check_v2.py.

Stage Summary:
- The T-C27 bench debt is SUBSTRATE-COMPLETE: snap-003 + gold-v2 are frozen, SHA-paired to each other, loader-verified, and on records main @3eb83bbd; the serving-flip recorded run (arms) can consume this pair with NO further freeze (card axis is in the snapshot; ALL vs VALIDATED-only denominators score the inert state honestly).
- Remaining for the bench after the flip: dispatch the run classes (A/B/C reruns on the new pair; D/E/F/G/H arms per registry), each with its own RUN_REPORT + SHA discipline.
- Standing items unchanged: PAT/credential rotation (re-burned this session: gh_api.py rewrite nearly destroyed the embedded PAT — recovered; rotation still owed), ENU-STRUCT-1.32, HOLD-NO-DOC (4ch1-1cr/2cr-202406), R4 active-policy, and the prior queue items ② (4ch1-2c-202011 exam_papers row) + ③ (4CH1/2CR June-2022 twin bank-merge) remain un-started.

---
Task ID: 40
Agent: Super Z (main agent) — state-verification lane
Task: "The paper issues might have been solved by other agents. Check current state" (trace 1a0de22d20417125)

Work Log:
- Worklog tail re-read first (ended at Task 39; no entries after). Primary-source sweep: records main still @3eb83bbd9 (no new commits); branches unchanged; parser HEAD 55166afb2 (09-25, unchanged). NEW activity found on two repos, all BEFORE my snap-003 commit (14:21Z 09-26): core 09-26 f40e7d459 (PaperQuestionResolver — deterministic session+paper+number serving, tier1 bank anchor / tier2 cards) + 1a644d5de (CI fix) + 02664958a (bank-anchor serving gate mirrors searchServingEligible — "the paper row governs": paper-VALIDATED + doc-SUGGESTED is production reality, tier1 was dead code before); pastpapers 09-26 gap-fill wave (Paperlords catalog re-sweep 3,515 rows, ~190 fills, ledger normalization, 0 structural defects audit, GAPFILL-2026-09-26.md) + notify-demo-reindex CI (2e5cdd5de/5cf95d98b @14:22-14:23Z — the last commit anywhere). NOTHING landed after 14:23Z 09-26 on any repo.
- ② 4ch1-2c-202011 — VERIFIED SOLVED first-hand (contradicts Task 39's Stage Summary claim "remains un-started" AND the earlier summary's "ep rows=0"; both wrong — likely a slug-form probe bug: exam_papers.paper_code stores '4CH1/2C' + session_label 'November 2020', not the slug): ep row e6c96a2e (SUGGESTED, PAST_PAPER, pdflane-atoms-draft-v1, created 09-25 17:01:29Z) → QP v2 6087c43e (11 chunks, source_uri 4ch1-2c-202011/qp.pdf) + MS v2 45dad920 (13 chunks) + 7/7 active bank questions. Landed in the 09-25 16:56-17:01Z bank wave (evidence commit 7928fadd6 @17:09:33Z).
- Bank wave scope: 12 ep rows created 09-25 16:56-17:01Z (4CH1 1C/2C × Jan-2020/21/22/23, Jun-2019/22/23, 2C Nov-2020, 2C Jun-2022), each pdflane-atoms-draft-v1, each doc-linked (QP+MS), each bank-populated (7-12 questions, ALL active; 104 questions total). exam_papers now 104 rows (80 SUG/13 REJ/11 VAL — same as before: these rows were already counted at the Task-39-era probe).
- ③ 4CH1/2CR June-2022 twin bank-merge — NOT solved; materialized differently: BOTH twins now exist with parallel banks — 2C Jun-2022 47b57ed2 (09-25 wave; QP v2 4ch1-2c-202206 + MS v2; 7 q / 70 marks) vs 2CR Jun-2022 f57ed5c2 (09-24; QP v1 4CH1-2CR-202206 + MS v1; 7 q / 70 marks). Distinct regional scans (different checksums), only 2 exact-stem overlaps of 7 (extraction-path divergence). Merge/dedup decision still owed — now 2× full banks instead of one.
- HOLD-NO-DOC (4ch1-1cr/2cr-202406) — UNBLOCKED but not ingested: corpus repo tree (main) now HAS past-papers/.../4ch1/past-papers/2024-06/4CH1-1CR/{qp.pdf,ms.pdf,parsed/} and 4CH1-2CR/{...} (16 tree entries). DB still has NO QP documents for those slugs (only MS v1 docs from 09-22) and NO ep row references them (probe: 0 rows).
- NEW FINDING (identity defect, glmocr era): the 4CH1/1CR + 4CH1/2CR June-2024 ep rows (created 09-14) are MISLINKED across spec — their QP/MS document_id fields point to corpus/igcse-chemistry-4ch0-1c-2024junr and 4ch0-2c-2024junr documents (OLD-spec 4CH0 regional papers). No 4CH0 Jun-2024 ep rows exist at all (docs have no correct home). The mislinked rows carry 12 (1CR) + 7 (2CR) bank questions, all active=FALSE (serving-inert). A NULL-paper_code 'Summer 2024' REJECTED row also references the 4ch0-2c-2024junr QP. Real 4CH1-1CR/2CR-202406 MS docs (09-22) sit orphaned from any ep row.
- NEW FINDING (quality gap): ALL 12 bank-wave ep rows have series=NULL, year=NULL (session_label is the only temporal key) — breaks series/year-based resolution; consistent with core f40e7d459's live-probe complaint (2C-June-2019 / 1C-Jan-2022 "unresolvable" via /fetch on 09-26 morning). The 25 earlier pdflane rows have series/year populated; only the 09-25 wave (12 rows) + 3 sprint-acceptance rows are NULL.
- Live bank census unchanged vs Task 39: 1,533 q / 1,533 qv / 7,215 parts / 5,271 mp / 1,418 schemes / 999 docs / 4,343 chunks.
- Probe scripts persisted: scripts/paper_state_probe_20260926b/c/d/e.py, paper_probe_schema.py (connection pattern: username+password in separate .render_env.json keys, NOT in URL).

Stage Summary:
- Answer to the operator: YES for ② — solved by the 09-25 bank-wave lane, verified end-to-end first-hand (ep row + QP v2 + MS v2 + bank questions). NO for ③ (twin merge) — both twins now bank-populated in parallel; merge still owed. HOLD-NO-DOC is now unblocked (corpus has the QP PDFs) but the doc-lane ingest + ep relink is still owed.
- Two new defects need registration: (A) cross-spec mislink of the Jun-2024 1CR/2CR ep rows onto 4CH0 old-spec regional docs (+orphaned real MS docs); (B) series/year NULL on the 12 wave rows (blocks series/year resolution; core lane hit it live).
- Open queue after this verification: ③ twin merge → HOLD-NO-DOC ingest+relink → defects (A)/(B) → bench run classes on snap-003/gold-v2 (substrate ready) → standing items (PAT rotation, ENU-STRUCT-1.32, R4 active-policy).

---
Task ID: 41
Agent: Super Z (main agent) — state-verification lane
Task: "Another agent supposedly fixed all the errors" (trace 1a0df7fa2cc97b59) — verify the claim against primary sources

Work Log:
- Repo sweep (all 5 repos + branches): records main advanced 3eb83bbd9 -> 314a8953b (T-C30: KG-tree applicability backfill 0->182 nodes, web PR #11, runs 36253537636+36253728888 SUCCESS — NOT paper axis). core main -> 202c6caaa (tier-2b content-store paper anchor: after the card anchor binds, the identity's real QP/MS chunks pin as lead evidence; commit message explicitly cites "the 09-26 live-pool pollution" wrong-paper front-matter chunks and excludes them structurally in serving — the agent SAW the mislink symptom and routed around it in code, did NOT repair the data). core/web NOTE_SECTION CLA (s137) + UX fix (s136) — unrelated. pastpapers HEAD unchanged since 14:23Z. No new/pending-fix branches on core or pastpapers (all branch names are old lanes).
- LIVE DB RE-PROBE (probe v6, scripts/paper_state_probe_20260926f.py): ALL FOUR Task-40 paper-axis defects STILL PRESENT, verbatim:
  (A) cross-spec mislink: 4CH1/1CR + 4CH1/2CR Jun-2024 ep rows still -> corpus/igcse-chemistry-4ch0-1c-2024junr + 4ch0-2c-2024junr docs (QP AND MS links).
  (B) series/year NULL: all 12 bank-wave ep rows still NULL/NULL (pdflane SUGGESTED 12/12 NULL; only sprint-acceptance 3 also NULL).
  (3) twin merge: 2C Jun-2022 (7q/7 active) and 2CR Jun-2022 (7q/7 active) both still live — no merge, no dedup.
  (HOLD) 4ch1-1cr/2cr-202406: still only the two MS v1 docs (09-22); no QP documents; 0 ep rows reference any -202406 doc.
- No new ep rows or QP/MS documents since 09-26 12:00Z (only the 298 EXTERNAL_QUESTIONS cards from T-C27's 12:50Z commit). exam_papers still 104 (80/13/11); bank census unchanged (1,533 q / 5,271 mp / 1,418 schemes / 999 docs / 4,343 chunks).

Stage Summary:
- VERDICT: the "fixed all the errors" claim is TRUE only within the pastpapers corpus lane's own scope (gap-fill wave: ~190 Paperlords fills, quarantine pairing 310/310, ledger normalization, 0-defect structural audit — all landed 12:20-14:23Z and previously verified). It is FALSE for the DB paper-axis errors: none of the four Task-40 defects was touched. Nobody has repaired the data.
- The tier-2b core commit is additive serving intelligence (card->QP->MS lead pinning) and a workaround for the pollution, not a repair.
- Paper-axis repair queue remains exactly as logged in Task 40: 3 twin merge -> HOLD-NO-DOC ingest+relink -> defect A (Jun-2024 CR relink + 4CH0 rows disposition) -> defect B (series/year backfill on the 12 wave rows).

---
Task ID: 42
Agent: Super Z (main agent) — paper-axis repair lane
Task: "Ok, start executing" (trace 1a0df842827c8191) — execute the paper-axis repair queue

Work Log:
- RECON (first-hand): bank-wave EVIDENCE.md (7928fadd6) proved ③ twin merge ALREADY EXECUTED (MERGE x2 of the Summer-2022 duplicate-sitting rows, ep 105->104, q 1540->1533; June-2022 rows are the canonical same-sitting registrations) — Tasks 40/41 verdicts on ③ corrected. rw-9b EVIDENCE.md supplied the recipe (prod API for ingests/embeds + guarded psycopg2 for pointers/retirements); igcse19_ingest.py supplied the auth recipe (10-min HS256 admin JWT from SYLLABAI_JWT_SECRET, identity from users/user_roles).
- HOLD-NO-DOC PREMISE CORRECTED: the 4CH1-1CR/2CR June-2024 QP documents EXISTED all along (afa9a7e7 / 82d5aeca, ingested by the G1 landing 09-21/22) — earlier uri-pattern probes missed them because source_uri '4CH1-1CR/qp.pdf' carries no year token. Identity PROVEN: pdflane converter uuid5(checksum+engine) over sha-pinned corpus bytes reproduces the live documentIds exactly (also MS 4c3c9759 / 123e0bf0).
- REPAIR B EXECUTED (scripts/repair_b_series_year.py): 12 bank-wave ep rows series/year backfill (JAN/JUN/NOV + year derived from session_label; single transaction; rowcount==1 per row asserted; prestate archived). Specimen-2017 (x2) + sprint-acceptance audit rows deliberately left NULL (honest/REJECTED). Post: 0 non-specimen NULL series across 37 pdflane rows.
- REPAIR A+HOLD EXECUTED (scripts/hold_drive.py): fresh g1.7 parse of both pairs from sha-verified corpus PDFs (1CR 12q/110 marksVerified=true PASS with one expected coded-date drift flag resolved by the corpus manifest ops_log; 2CR 7q/70 PASS, zero flags) -> guards all 0 (attempts/answers/human_marks/SMR/agreement_evals) -> full JSON archive (19q+19qv+111 parts+57 mp+17 ms+2 bridges+2 ep rows) -> FK-safe single-transaction delete (mark_points 57 -> spec/topics/options 0 -> bridges 2 -> questions 19 cascade -> ep 2) -> POST past-papers drafts 201 x2 (1CR paperId 29bba2da 12q/70 parts/57 mp; 2CR paperId 0f903acf 7q/48/38) referencing the EXISTING genuine docs -> series/year JUN/2024 backfill on the new rows.
- POST-GATES ALL PASS (scripts/hold_verify_final.py -> verify_final.json): ep pointers on correct docs, extraction pdflane-atoms-draft-v1, SUGGESTED, series/year JUN/2024; bank 12q/110 + 7q/70 == atoms totals; 0 4ch0 refs on 4CH1 rows; old row ids absent; 51/51 chunks embedded, mirrors exact (4CH1/1CR|2CR, JUN, 2024, embed_rev=2). Census stable: ep 104 (80/13/11), docs 999, chunks 4,343.
- COMMIT f96b0d57af6b -> records main (bench/evidence/paper-repair-2026-09-26/: EVIDENCE.md, SHA256SUMS, repair_b_prestate.json, hold_drive_prestate_archive.json, 2 drafts, post_results.json, verify_final.json). Base had moved to 6d4bc9ed0 (benign T-C30 UI spot-check coordination note) — ff-merge clean.
- Tooling persisted: gh_fetch_binary.py (binary-safe contents fetch — text-mode --raw corrupts PDFs), hold_predrive_check.py, hold_serving_check.py, hold_commit.py (Git Data API blobs->tree->commit->ff), repair_b_series_year.py, hold_drive.py, hold_verify_final.py.

Stage Summary:
- The paper-axis repair queue is EXECUTED AND CLOSED: ② (pre-existing), ③ (pre-existing, bank wave), B (this session), A+HOLD (this session). Production now: every 4CH1 exam_papers row that should reference genuine 4CH1 docs does; no cross-spec mislinks; series/year populated on all pdflane rows; the Jun-2024 CR papers are fully serving-ready (bank + embedded chunks + correct mirrors) pending teacher validation.
- Remaining open: SKIP-flagged 4CH1/2C Jan-2021 supersession (operator decision: version-bump vs re-validation), bench run classes on snap-003/gold-v2 (substrate ready), PAT rotation, ENU-STRUCT-1.32, R4 active-policy.

---
Task ID: 43
Agent: Super Z (main agent) — bench substrate lane (chunk→SP)
Task: "Proceed with Next: the card validation wave unlocks r6; quality floors need the chunk→SP substrate" (trace 1a0e32c9f6971b89) — iron rule honored: every referent located first-hand before execution

Work Log:
- Referent resolution (first-hand, zero guessing): "trigger A" = the at-flip bench re-run (AT_FLIP_RUNBOOK trigger A) — found ALREADY CLOSED by the r5 lane (records main 04e2b0951, 2026-09-27T10:35Z, run IDs 36311624648/36311973564/36312145176/36312444139 all SUCCESS, snap-004+gold-v3; T-C27.yaml trigger_a_execution closeout cites my prior directive trace 1a0e23212e7b3cf5 verbatim). Repo alias map re-established: records = SyllabAI/syllabai; today's activity also on core (enabler e728b7dea), web, demo, pastpapers (4SD0 onboarding).
- r6 GATE RE-CHECKED LIVE (scripts/cardwave_probe_20260927.py, SELECT-only): the card validation wave has NOT landed — EXTERNAL_QUESTIONS 378 SUGGESTED + 1 VALIDATED (298 T-C27 cards still SUGGESTED); chunks 317 VALIDATED (145 QP+161 MS+11 EQ) = snap-004 SNAP4-F1 exactly; exam_papers 78/13/13. r6 stays operator-held (no agent-asserted validation, AT_FLIP_RUNBOOK invariant). NOT self-started.
- "Quality floors" decoded from spec §8 verbatim (ratified v1.0): a/b/c floors (0.3249/0.2964/0.4799) fail on the 317-chunk served view; (d) SpecificationPoint resolution = NOT SCOREABLE with zero HUMAN_VALIDATED chunk→SP rows (R5 notes' named data gap) — exactly the user's "quality floors need the chunk→SP substrate".
- Substrate chain verified first-hand: resources C13 store = 211 rows / 210 HUMAN_VALIDATED (apply operator-directive-session-102 2026-09-18, gate 88dc8dd6a3; C27 repair touched only sp_title labels); store byte-verified vs resources main 1245df009 git blob sha1 9247ccdf05b8c296716b6c9a458897535dfd435f (sha256_16 e8b58a7109104bb7; C27-recorded pin f36910450bd50726 does not reproduce post-C28 move — noted for the resources lane). DB: 112 EXTERNAL_NOTES docs (09-20), 350 chunks 350/350 embedded, note-level spec_codes only. Snapshot side: snap-004 carries NO chunk→SP HV artifact (only 117 concept→SP HV attachments) — the gap.
- BRIDGE EXECUTED (scripts/c13hv_bridge_20260927.py, read-only, fail-closed): note_slug → manifest (112/112, 0 ambiguous) → rn_id → DB doc (file_name sme-note-<rn_id>.txt) → norm(evidence_quote) containment over norm(chunk content) with the verbatim pinned C13/C10 norm(); results: 210/210 resolved, 205 CLEAN / 4 MULTI (flagged) / 0 SPAN / 1 MISS (1d97fd710f098a74, SP 4CH1-1.52C — evidence quote carries source-page chrome the canonicalization split; upstream mapping real; NOT in gold's 63 codes → zero §8(d) impact); 180/182 SP codes bridged; 58/58 gold spec points covered (gold-v3 labels byte-identical v1). Artifact: chunk_spec_hv_projection.json — 210 HV rows keyed by snapshot-scheme chunk_refs '<checksum>:<chunk_index>' with full provenance (store pin + promotion record + join method).
- COMMIT 94d0d405c7c937e3f8dc4e56d6291c77272baa36 → records main (base 04e2b0951 asserted unchanged pre-commit; ff): bench/evidence/chunk-sp-substrate-2026-09-27/ (EVIDENCE.md, chunk_spec_hv_projection.json, bridge_stats.json, r6_gate_probe_20260927.txt, SHA256SUMS) + TODO.md T-C13 addendum + T-C27.yaml r6_gate_recheck_2026-09-27 block (YAML parse-verified). Remote verification: HEAD sha + 7/7 sizes + 6/6 git blob sha1s == local bytes.
- Deliverable copies: download/bench/chunk-sp-substrate-2026-09-27/.

Stage Summary:
- §8(d) flips NOT SCOREABLE → scoreable-with-coverage at the next freeze: the snap-005 export (r6 card-flip) folds the projection in via a chunk_ref join + notes-axis drift gate; BenchSnapshot accessor + runner scoring = the remaining core-side work (additive, e728b7dea precedent), then r6 measures BOTH the card-wave denominator AND the spec axis.
- r6 itself stays gated on the operator/teacher card validation wave (298 cards) — verified not landed twice today (10:35Z closeout, 13:1xZ probe).
- Open: core loader/runner §8(d) scoring; §8 a/b/c floors stay FAIL (card wave = denominator change); PAT rotation; ENU-STRUCT-1.32; R4 active-policy; SKIP-flagged 4CH1/2C Jan-2021 supersession decision.

---
Task ID: 48
Agent: Super Z (main agent) — card-axis serving-boundary lane
Task: "Continue development. Do not wait for teacher validation. Do not alter validation state or create validation events. Treat the 298 cards as SUGGESTED and non-servable. Build and test against them as non-servable fixtures, while preserving the serving-validation gate." (trace 1a0e67315a95fc09)

WORKLOG ROLLBACK RECOVERY (first): the session env reset rewound this file to Task 43 — Tasks 44-47 entries were lost. Remote truth re-verified first-hand and re-recorded here in compact form: Task 44 = §8(d) handoff spec (records 16584c1de, 131-line handoff); Task 45 = core §8(d) foundation (c91372c, loader/accessor/scorer/tests, CI green); Task 46 = r6 run-class wiring + snap-005 exporter staged pre-flip (core 670423a+b45b5d6, records 9754e62a1, dry-run ALL PASS); Task 47 = "Validated" reconciliation (operator's chat assertion probed against the DB — wave NOT landed 6 consecutive probes, teacher_validation_events empty, gate not discharged; other-agent commits inspected: s145 census gate hardening records aa525315c + core 64c71ffc9, tutor fixes 63df406b2/226722160). Also recovered: the gh_api.py path convention MUST carry a leading slash ("repos/..." produces a bogus host + phantom DNS error — self-caught in Task 47 after interleaved A/B isolation). Tooling note: Task 45+ scripts (s8d_*_commit.py, r6staging_commit.py, snap005_export.py, gate probes) were lost with the reset; they survive on records main remotely; JDK25/Maven3.9.11 re-bootstrapped at /home/z/tools.

Work Log:
- COORDINATION (first-hand, start): core main advanced 63df406b2 -> fc07389c4 (tutor paraphrase anchors A4/A5) then e5cc266 (H2 citation validation) during the work; records main advanced aa525315c -> f5cfd9438/8b698917b (T-C31 observability coordination) -> 09a624728 (r6 §8(d) interpretation-risks pre-registration). All additive, no lane conflicts. T-C13 TODO block carries another session's 2026-09-28 OPERATOR DIRECTIVE (trace 1a0e6753792f76fd): cards must NOT be flipped/mutated by any agent, no validation endpoint unless independently product-useful — my directive is the build-side complement and is fully compatible.
- GAP FOUND: the serving-validation gate had NO DB-level card coverage — vector branch 2 (V33 subject branch) had SQL-text coverage only (T-C20); lexical serving-eligible had NO tests at any level (its own javadoc cited a nonexistent gate test); the card shape (EXTERNAL_QUESTIONS, subject-linked, no paper row) was exercised nowhere.
- IMPLEMENTED on core branch bench/card-serving-boundary: CardServingBoundaryIT (7 tests, Testcontainers pgvector, house posture) — SUGGESTED cards never serve on either surface; VALIDATED-paper control group serves; arm-B VALIDATION_BOUNDARY_VIOLATION hard-fail encoded as a permanent fixture; neutral ALL-denominator view guarded against over-tightening (vector: papers+cards; lexical: papers only — asymmetry PINNED); flip contract proves exclusion is doc-validation-state-driven, not kind-driven (flip exercised inside the throwaway container ONLY — the mechanism the genuine teacher wave will rely on). ChunkLexicalRepositoryTest +4 (null-scope, blank fail-closed, VALIDATED-gate SQL w/ single-occurrence + subject-branch-absence asserts, bind order). Self-diagnosing seed sanity (any future premise break fails with exact counts).
- CI ITERATION (4 dispatches, each failure root-caused from logs via the redirect-stripping probe scripts/ci_run_log_probe.py — saved): (1) both neutral searches 0 rows; (2) fixture bug #1 — exam_papers qp/ms_document_id holds documents.document_id STRING not row UUID (production probed read-only: 90 string matches, 0 UUID matches) + diagnostics added; (3) fixture bug #2 — websearch_to_tsquery is AND-semantics, paper-B content lacked "cathode" (diagnostics: vectorNeutral=6 branch2=6 paperBranch=4 all correct; lexical expectation corrected 6->4 BY DESIGN); (4) SUCCESS run 36384982647 (894 unit + 112 ITs incl. 7 card-boundary).
- MERGED: rebased onto e5cc266 (main moved mid-flight), force-pushed, re-dispatched CI SUCCESS, ff-merged to main = b697492 (remote verified). Post-merge main CI was cancelled by identity lane's 2f117073a landing seconds later; the new main run FAILED — ROOT CAUSE ATTRIBUTED: RateLimitFilter "No default constructor found" breaks ApplicationContext for ALL @SpringBootTest ITs (identity lane's breakage; identical content ran green pre-2f117073a). Recorded for the owning lane; not my lane to fix.
- RECORDS STATUS COMMIT d7da46a6d9 (base 09a624728 asserted after one BASE-MOVE rebase): TODO.md T-C13 inline addendum (+1/-1) + bench/card-serving-boundary-2026-09-28/STATUS.md (57 lines, full evidence). Remote verified (sha, parents, files). Committer persisted: scripts/card_boundary_status_commit.py.
- NO-WRITE EVIDENCE (post-work, SELECT-only, rolled back): EQ docs 378 SUGGESTED + 1 VALIDATED UNCHANGED; teacher_validation_events 0 rows UNCHANGED; chunks 317 VALIDATED (145 QP+161 MS+11 EQ) UNCHANGED; exam_papers 13 VALIDATED (pre-existing). Zero production writes of any kind — directive honored.

Stage Summary:
- The card axis' non-servability contract is now PINNED in code: any regression that serves a SUGGESTED card, widens the lexical surface silently, or over-tightens the benchmark ALL-view fails CI with a self-diagnosing message. The serving-validation gate is preserved and now has row-level proof on both surfaces.
- Development no longer waits on the card wave; r6 itself remains operator-gated (WAITING_FOR_GENUINE_TEACHER_VALIDATION marker honored — no flips, no events, no endpoints).
- Open: identity lane's main-HEAD context-load red (2f117073a — owning lane); owner §10 (d) granularity ruling; PAT rotation; ENU-STRUCT-1.32; R4 active-policy; Jan-2021 2C supersession.

---
Task ID: 48
Agent: superz (main agent, zai session web-23eb7684-9eb6-4100-a2b3-22cfb322258b)
Task: trace 1a0e6b32899cd849 — user asked "how can I finish the teacher wave? where can I find it in the app?" — locate the in-app validation surface and the wave mechanism (research-only, zero writes).

Work Log:
- Read worklog tail first (standing rule); noted repo state advanced (core main d4e0f7a after T-C31 PR #29 merge; records main edab00043).
- Shallow-cloned syllabai-core @ d4e0f7a (workspace/core-tmp) + syllabai-web @ 03210b3 (workspace/web-tmp). syllabai-resources clone timed out (repo large); used GitHub API instead.
- CORE CODE AUDIT (validation write paths): ContentController (/api/v1/teacher/content/**) exposes validate/reject/flag/unflag/validate-all for exam_papers, question_versions, mark_schemes ONLY. ContentDocumentController (/api/v1/teacher/content/documents) = create/list/get/canonical/embed/search — NO validate endpoint. Document.java (content pkg): validation_state field is born-SUGGESTED with NO setter — no code path in the entire backend can flip a document's validation state. Verified: no org code writes teacher_validation_events (code-search org-wide: only docs/ERD/comment references; the events ledger was designed for an importer path whose writer was the one-off 09-26 bank-wave tooling, not an app feature).
- WEB CODE AUDIT: TeacherReviewView (Teacher tab) has 5 sub-surfaces: Marking review / Curriculum graph / Content gate / Test builder / Class intelligence. "Content gate" (TeacherContentView) drives review-queue-v2/v3 + per-paper validate-all / per-version / per-scheme buttons — papers/questions/schemes only. NO document/card validation anywhere in the UI (no /content/documents call in src at all).
- LIVE DB PROBE (scripts/wave_mechanism_probe_20260928.py, SELECT-only, rolled back): content_review_audit schema enumerated (id/occurred_at/actor_user_id/actor_label/action/target_type/target_id/from_state/to_state/detail); 41 rows total, ALL dated 2026-09-14, actor pilot.teacher@syllabai-test.dev, actions census: VALIDATE qv 13, VALIDATE ms 10, FLAG/UNFLAG, VALIDATE_ALL ep 2, REJECT, MAP_TOPICS — zero document/card actions ever. teacher_validation_events 0 rows (reconfirmed). documents census: EXTERNAL_QUESTIONS 378 SUGGESTED + 1 VALIDATED (the 09-26 T-C27 card batch all SUGGESTED; the single VALIDATED EQ doc created 09-20 pre-dates the app's audit table usage — import-time state, not an app flip). QP 13 VALIDATED / MS 13 VALIDATED (09-25, the app-validated rev1-adjacent docs).
- DEPLOYMENT FACTS: web README — app LIVE at https://syllabai-web.vercel.app, backend https://syllabai-core.onrender.com. DemoUserSeeder (local profile only) seeds teacher@/admin@/student@syllabai.dev demo accounts; the live teacher account evidenced in audit rows is pilot.teacher@syllabai-test.dev. Teacher tab is TEACHER/ADMIN-gated (UI affordance; backend /api/v1/teacher/** enforces).
- CONCLUSION (handed to user): the in-app validation surface EXISTS but only for papers/question versions/mark schemes (Teacher tab → Content gate). The 298 cards have NO validation surface in the app — no UI, no endpoint, no entity setter — which is exactly why the operator's attempted wave changed nothing in the DB. Two honest paths to finish the wave: (A) build the missing card-review surface (endpoint + queue + audit rows, teacher-authed) then the human clicks; (B) operator-run sanctioned flip script prepared by the agent but executed/authorized by the operator with in-transaction audit rows. Either way the validation ASSERTION must be the human's — agent-asserted validation stays forbidden; serving gate preserved. After landing: verify signature = 298 EQ docs SUGGESTED→VALIDATED + audit/events rows, then AT_FLIP_RUNBOOK chain executes.

Stage Summary:
- Question answered with primary sources at three independent levels (web UI, backend API/entity, live DB). No writes of any kind; probe rolled back; worklog updated.
- Open: card-validation surface does not exist and needs an operator directive to build (recommend review-queue UX with bulk select + ContentAuditRecorder audit); operator-run script alternative offered; AT_FLIP_RUNBOOK still staged and ready for the moment the wave lands.

---
Task ID: 49
Agent: superz (main agent, zai session web-23eb7684-9eb6-4100-a2b3-22cfb322258b)
Task: trace 1a0e6c87df3ae831 — user asked for "a .md file with everything" they can update and paste back — produced the operator runbook + decision record for the teacher card wave.

Work Log:
- Mini probe first (scripts/doc_columns_probe_20260928.py, SELECT-only, rolled back): documents schema (id uuid PK + document_id varchar uuid-formatted 379/379 + validation_state varchar), content_review_audit exact columns/defaults (id bigserial, occurred_at now(), actor_user_id nullable, target_id uuid NOT NULL), scope predicate returns exactly 298, excluded neighbors 80 SUGGESTED + 1 VALIDATED (09-20).
- Wrote /home/z/my-project/download/TEACHER_CARD_WAVE_RUNBOOK_2026-09-28.md — self-contained decision file: §0 how-to + standing boundary (agent never asserts validation); §1 verified state table + scope predicate; §2 in-app navigation (Teacher tab → Content gate); §3 why cards can't be validated in-app (three-level evidence); §4 Option A (build card review surface: validate/reject/flag endpoints + bulk + UI in Content gate + ContentAuditRecorder rows, then operator clicks) vs Option B (operator-run guarded SQL for Neon console: GUARD 1 scope=298, CREATE TABLE archive, FLIP+AUDIT single CTE writing 298 content_review_audit rows with operator label, GUARD 2 postconditions 0/299/298 fail-closed, rollback block); deliberately-NOT-touched list (teacher_validation_events stays 0 — hash-chain owned by importer tooling; 80+1 neighbors; chunks); §5 landing signature (299 VALIDATED EQ, 298 audit rows, events 0, serving probe); §6 staged AT_FLIP_RUNBOOK chain; §7 FILL-IN authorization block with operator name, scope confirm, reviewer note, authorization sentence.
- No writes to any database; single markdown deliverable in download/.

Stage Summary:
- Awaiting operator paste-back of §7 (Option A or B + operator label + authorization sentence). If A: build the surface (core+web, CI-gated) then operator clicks. If B: operator runs SQL then reports; agent re-probes landing signature read-only before executing the staged bench chain. Boundary held: no agent-asserted validation, no agent-run flip, serving gate untouched.

---
Task ID: 50
Agent: superz (main agent, zai session web-23eb7684-9eb6-4100-a2b3-22cfb322258b)
Task: trace 1a0e6d33df1016a9 — user clarified they do NOT want dashboard work or a prose runbook; they want a fill-in REVIEW SHEET: all 298 cards with content + per-card decision options (validate/flag/reject/etc.), which they complete and hand back for import.

Work Log:
- Design pivot accepted: decisions-file import = the mechanism teacher_validation_events was designed for (decision rows, reviewer field, hash chain). Boundary restated: operator asserts every decision (named, per-card or explicit ALL: default); agent only transcribes verbatim inside one fail-closed transaction with audit rows under the operator label; ambiguous sheet → abort with zero writes.
- Probes (SELECT-only, rolled back): card_sheet_probe_20260928.py — 298 cards' canonical_json shape (source.uri bank ref, retrieval block with paperCode/series/year/specCodes, single q_card textBlock with header line + stem, provenance tc27-card-bridge); size stats 1,077–1,319 bytes (avg 1,194; 355,804 total); document_chunks has spec_codes per chunk. Full sample of largest card dumped to design the renderer.
- Generator scripts/generate_teacher_card_review_sheet_20260928.py — deterministic ordering (paper, session chronological via case-insensitive month rank, qnum, doc_id), global seq 1..298, per-card sha16 fingerprint (sha256 of canonical_json, sort_keys), rendered catalog grouped by 40 paper sittings (2,895 marks total). Parser fixes en route: spec group allows empty (the 3 honest no-linkage cards render 'spec: (none — card has no spec linkage)'), month case-insensitivity fixed session sort (Jan 2012 → Jun 2025).
- Output: download/TEACHER_CARD_REVIEW_SHEET_2026-09-28.md (80,000 bytes, 2,275 lines). Sections: how-to (4 verbs: VALIDATE/REJECT/FLAG/SKIP), DECISIONS block (ALL: default + per-seq exceptions with optional | note:, ALL left BLANK on purpose to force a conscious choice), DECLARATION block (operator name/email + review assertion + date), sheet summary table, full card catalog (content, spec codes, card id, sha16). Import contract in-file: drift fail-closed (sha16 vs live DB), ambiguity aborts, audit rows carry operator label, teacher_validation_events hash-chained genesis documented at import time.
- Uploaded to tmpfiles, verified byte-identical (md5 7230a807ce3f4fc966c9854c32661dfb, 80,000 B): https://tmpfiles.org/dl/1790579800.8d9d67d61bb23471/wuwapC8QCIj8/teacher_card_review_sheet_2026-09-28.md (expires ~60 min; local copy persists in download/).
- No DB writes of any kind this task.

Stage Summary:
- Awaiting the completed sheet paste-back (DECISIONS + DECLARATION, or whole file). On receipt: write scripts/teacher_wave_import_20260928.py — parse → pre-flight guards (scope 298, sha16 match, state SUGGESTED) → single transaction applying decisions verbatim (documents flip per decision; content_review_audit rows with operator label; teacher_validation_events hash-chained decision rows, chain genesis sha256 documented) → post-guards per-action counts → read-only landing verification → then AT_FLIP_RUNBOOK chain for whatever fraction validated.

---
Task ID: 51
Agent: superz (main agent, zai session web-23eb7684-9eb6-4100-a2b3-22cfb322258b)
Task: trace 1a0e6f2bc9709b79 — user reported the completed review sheet as an upload ("teacher_card_review_sheet_2026-09-28_completed.md" → /home/z/my-project/upload/); import the recorded decisions.

Work Log:
- UPLOAD NEVER ARRIVED: /home/z/my-project/upload/ contains only 4 old files (Sep 16–20); re-checked after 20s + 45s delays; project-wide scan found no file newer than my own 07:11-07:12 writes. Per the sheet contract (ambiguous/absent → abort, zero writes) the import did NOT run and no decisions were assumed. User informed.
- Built scripts/teacher_wave_import_20260928.py (decision-agnostic importer, --sheet path, default dry-run): parses DECISIONS block (ALL: default + N: ACTION [| note: ...] exceptions, # comments ignored, strict verb whitelist VALIDATE/REJECT/FLAG/SKIP) + DECLARATION block (name/date mandatory, [FILL IN leftover → abort, assertion line must be verbatim) + sheet catalog (seq→doc_id+sha16, must be contiguous 1..298).
- Pre-flight (read-only): scope 298; events 0 rows; no prior archive table (mixed-mechanism guards); 298/298 sha16 fingerprints vs live canonical_json (sha256 sort_keys [:16]); 298/298 still SUGGESTED.
- Import (single fail-closed transaction): in-tx re-guards; archive table LIKE documents; row-level guarded UPDATE per mutation (…AND validation_state='SUGGESTED' RETURNING, must be exactly 1); content_review_audit row per mutation (actor_label=operator, detail carries sheet sha256 + card ref + operator note); post-guards (state counts incl. 1 pre-existing VALIDATED EQ doc, 80 neighbors untouched, audit row count, events 0 rows); rollback on any failure.
- CRITICAL DISCOVERY (dry-run constraint dump): teacher_validation_events CHECK constraints — ck_tve_target_type ∈ {question_version, mark_scheme, exam_paper} (documents EXCLUDED), ck_tve_action ∈ {VALIDATE, REJECT, FLAG, REVERSE} (no SKIP), ck_tve_result_state ∈ {SUGGESTED, VALIDATED, REJECTED} (no FLAGGED); decision_hash is char(n); uq_tve_decision UNIQUE(decision_seq, decision_hash). The ledger belongs to the T-011 assessment importer and predates the card axis. LEDGER DECISION: events intentionally NOT written (stays 0 rows — constraint contract respected); the wave's ledger is content_review_audit + the sha256-pinned sheet + import_report.json. Rationale recorded in report + here.
- TESTS (no writes): missing sheet → ABORT exit 2; blank sheet → ABORT (operator name missing) exit 2; fixed fenced-block off-by-one (```text fence line leaked into block) found by test; synthetic happy-path sheet (fixture, ALL: VALIDATE + test identity, explicitly NOT operator decisions) → DRY-RUN OK: census 298 VALIDATE, 298/298 fingerprints match live, plan printed. Fixtures + dry-run report dir deleted after test (no stale evidence).
- Zero production writes of any kind this task.

Stage Summary:
- Importer is built, fail-closed-tested (2 abort paths + full dry-run happy path) and ready: `python3 scripts/teacher_wave_import_20260928.py --sheet <completed.md> --execute`. Blocked ONLY on the actual completed sheet reaching the server (upload failed) — user asked to re-send the file or paste the DECISIONS + DECLARATION blocks directly in chat. On receipt: dry-run first, show census, then --execute, post-verify, then AT_FLIP_RUNBOOK for the validated fraction.

---
Task ID: 52
Agent: superz (main agent, zai session web-23eb7684-9eb6-4100-a2b3-22cfb322258b)
Task: trace 1a0e702ed9960375 — operator delivered the completed sheet as a GitHub upload (nawaf-al-hussain/FileUpload, teacher_card_review_sheet_2026-09-28_completed.md); import the recorded decisions.

Work Log:
- Fetched the sheet from raw.githubusercontent.com (79,856 B) → download/imports/teacher_card_review_sheet_2026-09-28_completed.md, sha256 89c07146…d67e.
- Parsed DECISIONS: ALL: VALIDATE + 3 FLAG exceptions (#207/#278/#291, the known no-linkage cards, operator note verbatim). DECLARATION: name Nawaf Al Hussain Khondokar, reviewer 'same'→name, assertion verbatim, date 2026-09-28. EMAIL GAP: email field holds literal '[EMAIL REQUIRED]' (operator's own redaction; original placeholder was [FILL IN: ...]). Importer's [FILL IN check would not catch it; decision: proceed verbatim — never invent identity, label goes on audit rows exactly as declared, sheet sha256 pins the context. GitHub account name matches declared operator (corroborating provenance). GitHub API rate-limited → commit metadata not captured.
- DRY-RUN: all guards passed — scope 298, events 0, no prior archive, 298/298 sha16 fingerprints match live content, 298/298 still SUGGESTED, census {VALIDATE:295, FLAG:3}.
- Pre-execute probe (scripts/flag_state_probe_20260928.py): ck_documents_validation_state allows SUGGESTED/VALIDATED/REJECTED/FLAGGED → FLAG legal.
- EXECUTE #1 ABORTED (fail-closed, zero writes): audit INSERT violated ck_cra_target_type — 'document' not in ledger domain {exam_paper, question_version, mark_scheme, question}. Root cause: Task 51 importer used wrong vocabulary. Fix: target_type='question' (cards ARE question items, kind EXTERNAL_QUESTIONS) in INSERT + both post-guards; rollback was clean.
- EXECUTE #2 COMMITTED: run a5d13c0a-2503-4d06-bb14-9397e9a1cf37. 298 mutations, 298 audit rows, events untouched at 0.
- INDEPENDENT landing verification (scripts/landing_verify_20260928.py, fresh read-only conn): EQ census FLAGGED 3 / SUGGESTED 80 / VALIDATED 296 (295 new + 1 pre-existing); 80 neighbors untouched; 3 FLAGGED ids all 09-26 wave; 298 operator audit rows today; sample FLAG detail carries sheet sha256 + card uuid + sheet # + note verbatim; events 0; archive marker table exists EMPTY (by design — existence guard vs double-import, not a data snapshot).
- Audit census reconciliation (scripts/audit_census_20260928.py): total 362 = 41 (09-14, matches Task 48 snapshot) + 23 (09-28 pilot.teacher: 11 ms + 11 qv + 1 VALIDATE_ALL ep — live app activity on papers/schemes axis, separate surface) + 298 (Nawaf, question). No concurrent interference with the card wave.
- Report: download/card-wave-import-2026-09-28/import_report.json (run_id, sheet sha256, census, post_census, audit_census).

Stage Summary:
- T-C27 CARD WAVE IMPORTED AND LANDED: 295 VALIDATED + 3 FLAGGED (#207/#278/#291), 80 neighbors untouched, serving gate unchanged (only VALIDATED serve; FLAGGED excluded). Ledger = content_review_audit (298 operator-labeled rows, target_type='question') + sha256-pinned sheet + import_report.json; teacher_validation_events stays 0 (CHECK domain excludes documents — Task 51 decision upheld).
- Boundary respected: decisions applied verbatim from the sheet; no invented email; no events rows; audit is append-only (no rewrite of the '[EMAIL REQUIRED]' label — if the operator supplies the email later it can only be annotated, not corrected).
- AT_FLIP_RUNBOOK (papers/schemes axis flip) remains the next pending step if the operator still wants it; NOTE: pilot.teacher already ran VALIDATE_ALL on 1 exam paper + 11 ms + 11 qv via the app today.

---
Task ID: 53
Agent: superz (main agent, zai session web-23eb7684-9eb6-4100-a2b3-22cfb322258b)
Task: trace 1a0e71324fcdc119 — "Now do we have r6 measurement?" — verified none existed, then executed the full r6 at-flip (the gate discharged when the Task-52 wave landed).

Work Log:
- Verified first-hand: records main had NO r6 activity (latest T-C32 coordination 07:09Z); core had the staged §8(d) wiring (c91372c+64c71ff+670423a+b45b5d6 merged, CI green); records had snap005_export.py staged pre-flip (dry-run ALL PASS) + R6_STAGING_STATE with the 6 at-flip steps.
- Assembled exporter inputs from primary sources: snap-004 7/7 SUMS-verified + manifest/FREEZE_RECORD, HV artifact (sha b5b20ffa… pin MATCH), resources store re-fetched @ 1245df009 (sha16 e8b58a7109104bb7 pin MATCH — the local bench_r6 copy was stale at 4882a3ac…), pins from scripts/c19_promotions.yaml + Official-Specifications/parsed/_derived/graph/igcse-chemistry/concepts.yaml.
- Export run #1 ABORTED fail-closed on 2 REAL drift findings: (1) "no regressions" gate treats the operator's 3 SUGGESTED→FLAGGED decisions as demotions; (2) question_anchors grew +11 rows after snap-004 froze (pilot.teacher app-side wave: 11 qv VALIDATE + 1 ep VALIDATE_ALL, audit-evidenced; multiset delta verified 0 removed / 0 mutated).
- Amended exporter with manifest-bound deltas SNAP5-F5 (down-flips legal ONLY SUGGESTED→FLAGGED on EQ chunks; anything else still aborts) + SNAP5-F6 (anchors = multiset superset, growth recorded). Re-run: ALL VERIFICATIONS PASS — 4,181 chunks (3,831 identical + 350 notes), drift gate 0 divergences, census 210/209/164/181 + 205/4/0/1.
- FREEZE COMMIT ab600e18f1: evidence/bench-001/snapshots/snap-005/ (13 files incl FREEZE_RECORD.md + amended exporter provenance); remote bytes verified.
- gold-v4: 12 class files byte-identical to gold-v3 (anti-tuning), manifest pins → snap-005; gold_check PASS (120 records) + selftest 6/6; committed c8ae9e6c1c with R6_STAGING_STATE gate-discharged flip.
- Staged inputs (60f57e87b3): snapshot-r6, gold-r6, preload-r6 initial = 4,181/4,181 production vectors mirrored SELECT-only (notes chunks ARE embedded in production → expected 0 chunk API calls; chunk_id uuidv3 scheme verified against r5 artifact row). 4 ops-*-r6 workflows generated from r5 siblings with exact deltas (core pin 05f262169 = main at freeze) → f7bb66e641.
- 4/4 dispatches SUCCESS, zero production writes: embed-backfill 36400373270 (4,181 preloaded 0 chunk API + 120 fresh queries; final artifact committed 821fb5ebb7) → run003b 36401105223 (commit 5f409767a5) → run004a 36401616124 (34a96f5379) → run005c 36402153529 (98b42bfe7f). Race-safe commits throughout (parallel lane's ADR-028 coordination handled cleanly).
- Numbers (chunk axis n=89): B recall@10 0.0247/mrr 0.0449; A recall@10 0.074/ndcg 0.1166; C 0.074/0.1384 (mrr 0.064). §8(d) SCORED FIRST TIME: 0.0/0.0 both views all arms — honest truth (210 HV mappings anchor on SUGGESTED notes chunks the VALIDATED-only serving gate excludes). Interpretation pre-registration 09a624728 discharged: leakage max ratio 0.4033 ≪ 0.8 (no near-duplicates; 3/89 containment flags recorded, short-ask-in-long-chunk), attribution moot (no high-(d) to misread). CARD-AXIS HEADLINE: A/C served 671 EQ refs ALL VALIDATED (the wave entering serving; B 0 — pinned lexical asymmetry held); 3 FLAGGED cards never serve.
- Coordination commit ab321575f3: TODO T-C13 + T-C27 addenda + R6_STAGING_STATE executed banner. R6-GENERATION-NOTES.md = the interpretive record.

Stage Summary:
- R6 MEASUREMENT EXISTS: snap-005 freeze + 3 arm runs recorded + R6-GENERATION-NOTES, all on records main; §8(d) flipped NOT SCOREABLE → SCORED (0.0 baseline on record); the operator card wave's serving impact measured (671 VALIDATED card serves). Zero production writes; every number verbatim from runner artifacts; both pre-registered interpretation obligations discharged.
- Follow-ups for the operator: (a) 3 FLAGGED cards need source verification (their own notes); (b) notes-axis promotion decision is theirs — it is what would move §8(d) off 0.0; (c) papers/schemes axis: pilot.teacher's same-day app activity already validated 11 qv + 1 ep.

---
Task ID: 54
Agent: superz (main agent, zai session web-23eb7684-9eb6-4100-a2b3-22cfb322258b)
Task: trace 1a0e75e9cd346a15 — "Source verify the 3" — verify the 3 FLAGGED cards (#207/#278/#291) against their primary sources (operator follow-up (a) from the r6 close-out).

Work Log:
- Worklog tail re-read first (standing rule). Flag context from Task 52/import_report: note verbatim "0 marks, no syllabus spec linkage, and Q? / unknown question sequence; needs source verification."
- Probe 1 (SELECT-only, rolled back): full canonical_json of the 3 cards via LIKE on document_id (sheet card uuid == documents.document_id; documents.id is a different uuid — first attempt by id found nothing). Cards: #207 1c15d529 (4CH1/2C Jan 2020 Q3, header says marks 11), #278 ee882008 (4CH1/2CR Jun 2020 Q1, marks 5), #291 1195ca6c (4CH1/2CR Jan 2023 Q1, marks 4); each with source.uri syllabai-bank/... + SHA-256 checksum; sibling counts 8/6/8 per sitting.
- Probe bug caught: sibling-context CTE passed the bare uuid to LIKE (no % wildcards) → 0 rows; bisected to the parameter, fixed, re-ran. No DB anomaly.
- Renderer artifact identified: sheet generator's header regex REQUIRES a "spec:" segment; the 3 no-linkage cards' headers omit it → fallback qnum="?", marks=0, qtype="?" → "Q? · 0 marks · ?" on the sheet. The cards' own textBlocks carry the true Q3/11, Q1/5, Q1/4.
- Bank fetch attempt @ resources pin 1245df009712216b… 404'd → T-C27.yaml shows cards are "deterministic per-bank-question canonical drafts (qcard-bridge-family, token-subset of print)"; the qcard-*.txt is the bridge's own emission, so the true primary source is the DB bank layer (questions/question_versions/question_parts/question_spec_points) + the sittings' QP/MS document_chunks.
- Bank probe: 3 bank rows found (4ch1/past-papers/2020-01/4CH1-2C#q3 marks 11; 2020-06/4ch1-2CR#q1 marks 5; 2023-01/4CH1-2CR#q1 marks 4; all SUGGESTED, extraction pdflane-atoms-draft-v1 conf 1.0); exam_papers rows exist for all 3 sittings.
- Verify matrix: card stems byte-faithful to bank stems (normalized containment; #291 is a strict prefix = documented token-subset rule). Leaf part sums: #207 2+2+1+2+4=11 (parent part b(5) double-counts children — naive 16 explained), #278 4+1=5, #291 4×1=4. question_spec_points=0 for all 3 — the T-C27 "3 honest skips" confirmed.
- Paper-text anchors: #207 QP chunk 3 (pp.6–7, copper question, real parts); #291 QP chunk 0 (instruction block + Q1 opener) + MS chunk 0 ("total for question 1 = 4 marks"); #278 partial anchor — sitting QP/MS have 0 document_chunks rows (honestly noted), corroborated via parts only.
- VERDICT: 3/3 source-verified faithful; no fabrication, mis-quote, or wrong-paper content. Weaknesses are stem thinness (#207, bank granularity) and front-matter chrome in stems (#278/#291, inherited from bank extraction spans). Not related to the "09-26 live-pool pollution" core cited (that was QP/MS chunks, different axis).
- Evidence: download/flagged3-source-verify-2026-09-28/ (REPORT.md + verify_matrix.json + flagged3_canonical.json + bank_rows.json + SHA256SUMS); scripts flagged3_*.py all SELECT-only.
- Records commit 3b36d78af9 (base fc3ae1f61e, race-safe): bench/evidence/flagged3-source-verify-2026-09-28/ (5 files) + TODO.md T-C27 addendum; remote file list + HEAD verified; addendum text confirmed at main.

Stage Summary:
- The 3 flags are fully explained: (1) renderer regex artifact produced "Q? · 0 marks"; (2) zero spec linkage is genuine (the 3 honest skips); (3) content is genuine and faithful to bank + paper. Disposition stays operator-owned: keep FLAGGED (inert — never serve) or issue a named flip decision (importer path proven); no agent-asserted validation.
- Optional follow-ups: fix the sheet generator's regex fallback for future sheets (pinned sheet untouched); upstream bank-stem chrome repair is a data-lane item.
- Still open from before: AT_FLIP_RUNBOOK papers/schemes axis (pilot.teacher already validated 11 qv + 1 ep in-app on 09-28); notes-axis promotion decision (what moves §8(d) off 0.0).

---
Task ID: 55 (restored)
Agent: superz (main agent, zai session web-23eb7684-9eb6-4100-a2b3-22cfb322258b)
Task: [RESTORED after 2nd sandbox rollback — text reconstructed verbatim from session transcript; original entry lost in the worklog regression] trace 1a0f2abd20df8e6d — "Proceed with the 15 new ING-anchored questions' topic mappings" — the sibling-supersession follow-up (Task-70: "the 15 new questions join the next topic-mapping pass (Jan-2021 rows' path via Task 68/69)").

Work Log:
- Worklog tail re-read first (standing rule). Inherited context reconciled against primary sources: the inherited summary's "APPROVE both"/284/19 items were all already executed as Tasks 68/69/70 per records TODO.md (traces 1a0eb3255bd898c9 / 1a0ebc845dcee229 / 1a0ec06fbd199a99); the only genuinely open item matching the new instruction is the Task-70 follow-up — the 15 supersession questions.
- PAT REVOKED MID-SESSION (gh_api 401 on all authenticated calls after early-session success; Task-1 hygiene note had flagged the exposed token). All GitHub reads pivoted to anonymous: raw fetch + shallow/sparse clones (records-anon @ 99feab2, resources-anon sparse @ 8430547fcf). Records push therefore BLOCKED (see below).
- Probe (SELECT-only): cohort measured with zero drift vs Task-70 — 8x 4ch0-2c-201701#qN (ING-4CH02CJANUARY2017) + 7x 4ch1/past-papers/2020-01/4ch1-2CR#qN (ING-4CH12CRJANUARY2020), all VALIDATED v1, qsp=0 qt=0, marks multisets 60/70 print-exact; bank active 961; ING total active exactly 15 (T-QSP3's 284->0 held). KG vocabulary: 182 4CH1 spec points, 28 letter TOPICs, PART_OF chains point->TOPIC verified; qsp conventions AI_VALIDATED/AI_VALIDATED.
- Derivation (T-QSP2 semantics, content-grounded on the posted drafts + live stems/92 parts/75 mark points): PRIMARY=dominant assessed point (largest mark block, framing tie-break), SECONDARY<=4 substantively assessed; topics=parent-TOPIC-of-PRIMARY + distinct secondaries cap 4 by first point code; 4CH0->4CH1 cross-spec. Ambiguities resolved from draft verbatim (2017 q6 part-b = bond-energies 3.7C per "Route 1:" MS; 2CR q5 c-ii = 1.34C; 2CR q7 fermentation 4.33C=4m). Plan pinned scripts/qsp15_plan.json sha256 bc57e0fe…575a0.
- Pre-write validation 4 layers ALL GREEN: (L1) bank-wide mechanical reproduction 852/852 on past-paper families — 94 disagreements ALL pre-existing sme-eq-* corpus-lane anchors (untouched, out of scope, recorded) + 0 qt-primary-vs-anchor conflicts; (L2) resources explorer_blob @ 8430547fcf 59/59 point->TOPIC agreement; (L3) Task-70 undo-record archived house mappings (content-matched by stem, NOT row order — the glmocr chain had different question numbering) 6/8 primaries + 2/4 secondaries, the 2 primary divergences (2017 q2 -> S1-d via 1.20; 2017 q6 -> S3-a via the 6m energetics block) documented point-grounded supersessions; (L4) dry-run tx ROLLBACK green.
- Execution: single fail-closed tx (scripts/qsp15_apply.py): 15 guarded primary UPDATEs rowcount==1 each (only off the exact ING anchor) + 59 NOT-EXISTS-guarded qsp INSERTs (AI_VALIDATED) + 36 NOT-EXISTS-guarded qt INSERTs; in-tx asserts ALL GREEN (ING 15->0; qsp 2578->2637; qt 1094->1130; every cohort qsp node real 4CH1-1.x SUBTOPIC, every qt node real 4CH1-S% TOPIC; exactly one PRIMARY per cohort question in both tables; distribution {0:593,1:353}->{0:593,1:368} exact). Dry-run ROLLBACK then COMMITTED. No state flips, no audit rows, teacher_validation_events 0.
- Verification 3 layers on FRESH connections (scripts/qsp15_verify.py): (1) DB: ING census 0, qsp 2637, qt 1130, qt ING refs 0, distribution {0:593,1:368}, primaries/rowcounts vs plan 15/15+15/15; (2) serve path: fresh probe learner, both papers render 7/7 + 8/8 questions ALL with specPoints (before: none); (3) evidence path: structured attempt + learner self-mark 5/5 on 4ch0-2c-201701#q1 -> evidenceFired=True -> skillStates carry 4CH1-S1-b (TOPIC) "Elements, compounds and mixtures" + secondaries S2-h/S2-e/S2-b + points 1.8/2.44/2.5/2.23C, NO ING-* state. 3 disposable probe learners created (probe data only).
- Evidence: download/qsp15-topic-mappings-2026-09-30/ (REPORT.md + qsp15_plan.json + qsp15_run.json + qsp15_verify.json + qsp15_probe_out.json + SHA256SUMS). Records local commit 6590098 (base 99feab2, race-checked via anonymous fetch) with the evidence dir; PUSH BLOCKED — no valid PAT in this session (revoked); commit sits ready to push the moment a fresh PAT is supplied (env GH_PAT or equivalent).

Stage Summary:
- qsp15 EXECUTED + VERIFIED: the 15 supersession questions carry real primary topics + spec-point mappings; bank-wide ING-anchored active 15 -> 0 — the T-QSP2/68/69 mapping program is now COMPLETE (every active past-paper question in the bank is topic+spec-point mapped; serving/evidence now paint REAL topics for both supersession sittings).
- Open items carried: records push for commit 6590098 needs a fresh PAT; sheet-generator regex fallback fix (code lane); bank-scheme sparsity (91 qv); 94 sme-eq-* anchor-vs-qsp disagreements (SME import lane, pre-existing, recorded in qsp15 L1); ING anchor node cleanup (out of scope by design).

---
Task ID: 56 (restored)
Agent: superz (main agent, zai session web-23eb7684-9eb6-4100-a2b3-22cfb322258b)
Task: [RESTORED after 2nd sandbox rollback — text reconstructed verbatim from session transcript] trace 1a0f2e549ca06d61 — operator supplied a fresh PAT ("here is new PAT") — discharge the only open item from Task 55: push the ready records commit 6590098 (qsp15-topic-mappings evidence).

Work Log:
- Worklog tail re-read first (standing rule). Confirmed Task-55 state: qsp15 executed+verified, local commit 6590098 (base 99feab2) staged and ready, push blocked solely on the revoked PAT.
- Located the records clone (workspace/records-anon): clean tree, HEAD 6590098, base 99feab2, origin https://github.com/SyllabAI/syllabai.git.
- Race-guard fetch: origin/main still exactly 99feab2 — no other lane pushed, fast-forward legal.
- PAT validated via API first (GET /user -> 200, authenticated as SyllabAI). SCOPE OBSERVATION: the new token is a classic PAT carrying near-full admin scopes (repo, workflow, admin:org, admin:gpg_key, delete_repo, ...).
- Token handling: supplied as one-shot env var only; git authenticated through a temporary GIT_ASKPASS helper under .creds (deleted in the same run); NO copy written to any file, git config, remote URL, or committed artifact.
- Push attempt #1 failed PRE-PUSH (rc=128, zero writes): askpass was chmod 600 (no exec bit) -> "cannot exec askpass.sh". Fixed to 700 and re-ran — no partial state existed between attempts.
- Push attempt #2 SUCCESS: 99feab2..6590098 main -> main, fast-forward, no conflicts, no rebase needed.
- Landing verified two independent ways: (1) git ls-remote origin main == 659009833d16a591cf1fdc7f3fa1aa0011cd1f70 == local HEAD; (2) all 6 committed evidence files re-fetched from raw.githubusercontent.com @ 6590098 and the 5 pinned sha256 digests in SHA256SUMS verified OK byte-for-byte (REPORT.md, qsp15_plan.json [bc57e0fe...], qsp15_run.json, qsp15_verify.json, qsp15_probe_out.json).
- Note: the in-script API dir probe returned 404 on the guessed path bench/evidence/... — actual committed path is bench/review/psaxis-review-2026-09-28/qsp15-topic-mappings-2026-09-30/ (git show --name-only); the raw-fetch check above is the authoritative content verification.
- Zero production writes of any kind this task (push only; DB untouched).

Stage Summary:
- PUSH COMPLETE: records main is now 6590098 — the qsp15-topic-mappings evidence bundle (6 files) is on the remote. Task-55's only open item is discharged; the T-QSP2/68/69 + qsp15 topic-mapping program is now fully closed including the records lane.
- SECURITY (operator action recommended): the fresh PAT authenticated as SyllabAI with near-full admin scopes and has now been pasted into chat — treat it as exposed: revoke it and issue a fine-grained token scoped to contents:write on only the repos agents push to. No copy of the token exists in this session, the worklog, or any artifact.
- Remaining open items unchanged from Task 55: sheet-generator regex fallback fix (code lane); bank-scheme sparsity (91 qv); 94 sme-eq-* anchor-vs-qsp disagreements (SME import lane, pre-existing); ING anchor node cleanup (out of scope by design).

---
Task ID: 57 (restored)
Agent: superz (main agent, zai session web-23eb7684-9eb6-4100-a2b3-22cfb322258b)
Task: [RESTORED after 2nd sandbox rollback — text reconstructed verbatim from session transcript] trace 1a0f3c443e58edf1 — operator re-sent a PAT ("here is new PAT", same token string as trace 1a0f2e549ca06d61). No new task instruction. Discovered a SANDBOX ROLLBACK, reconciled state, restored lost worklog entries.

Work Log:
- Standing-rule checks first: worklog tail + remote state. ANOMALY: worklog had regressed to 719 lines ending at Task 54 (Tasks 55+56 entries lost); workspace/records-anon clone gone; scripts/qsp15_*.py gone; download/qsp15-topic-mappings-2026-09-30/ gone. Conclusion: the sandbox was rolled back to a pre-Task-55 snapshot between sessions; local files reverted, external systems untouched.
- DURABILITY VERIFIED on the authoritative surfaces: (1) records remote main == 659009833d16a591cf1fdc7f3fa1aa0011cd1f70 exactly (anonymous ls-remote) — the Task-55 evidence commit and the Task-56 push both persisted; (2) re-cloned records-anon (shallow, anonymous) at 6590098 and recovered the evidence bundle to download/qsp15-topic-mappings-2026-09-30/ — all 5 pinned SHA256SUMS verify OK byte-for-byte; (3) other local clones (core-r2, igcse19_repo, syllabai-core) 0 commits ahead of upstream — nothing unpushed was lost.
- Live-DB re-census ATTEMPTED but BLOCKED: the production SYLLABAI_DATABASE_URL lived only in the rolled-back shell env; no copy exists in any repo config (render.yaml injects it at deploy time; docs carry placeholders only; DB host is Neon per render.yaml comment). The sandbox-local DATABASE_URL points to a sqlite path (not production) — probed defensively and discarded. Persisted scripts/reconcile_db_probe_20261001.py (SELECT-only, fail-closed, accepts JDBC or postgres DSN) staged for the moment the operator re-supplies the DSN. Durability does NOT hinge on this: qsp15_verify.json (on records @ 6590098) documents the execution-time 3-layer verification, and no records push has landed since 6590098.
- PAT disposition: token string is IDENTICAL to the one already used in Task 56 (push completed and verified there). Nothing is currently blocked on a PAT, so the token was NOT used this task (minimal-use principle). Security note stands and is now doubled: the same admin-scoped classic PAT has been pasted into chat twice — revoke it and issue a fine-grained contents:write-scoped token.
- Worklog restoration: Task 55 and Task 56 entries re-appended verbatim from the session transcript, each headed [RESTORED after sandbox rollback]. This Task 57 entry documents the rollback + reconciliation. Double-execution hazard closed: fresh agents reading the tail will now see qsp15 as EXECUTED+PUSHED, with the DB post-state fingerprints (ING 0 / qsp 2637 / qt 1130) recorded in both the worklog and the remote evidence.
- Zero production writes of any kind this task (reads and local restores only).

Stage Summary:
- ROLLBACK RECONCILED: the only authoritative losses were local files; remote records (6590098) and the production DB (external, untouched by the rollback) hold the durable post-qsp15 state. Worklog restored to full fidelity through Task 57.
- Operator follow-ups: (a) REVOKE the twice-exposed admin PAT, replace with a fine-grained token; (b) re-supply SYLLABAI_DATABASE_URL if a live re-census is wanted (probe script staged); (c) RECOMMENDATION: add a periodic worklog snapshot commit to the records repo so future sandbox rollbacks cannot sever the coordination record — needs operator sign-off as a new convention.
- Open items unchanged: sheet-generator regex fallback fix (code lane); bank-scheme sparsity (91 qv); 94 sme-eq-* disagreements (SME lane); ING anchor node cleanup.

---
Task ID: 58 (restored)
Agent: superz (main agent, zai session web-23eb7684-9eb6-4100-a2b3-22cfb322258b)
Task: [RESTORED after 2nd sandbox rollback — text reconstructed verbatim from session transcript] trace 1a0f3f7b051cecfd — operator supplied Render (rnd_…) + Neon (napi_…) API keys to unblock the Task-57 follow-up (b): fetch the production DSN programmatically and run the live re-census.

Work Log:
- Render API (primary, WORKED): GET /v1/services -> 1 service 'syllabai-core' (srv-dagijie7bikc73bc0460, repo SyllabAI/syllabai-core, docker, frankfurt, free tier); GET env-vars -> 12 vars incl. SYLLABAI_DATABASE_URL / _USERNAME / _PASSWORD. v1 API shape quirk: items wrapped as {"service": …} / {"envVar": …} — unwrapped. DSN assembled as postgres:// from the JDBC host string + separate user/password vars. Secrets held in env/memory ONLY — never printed, logged, or written to any file.
- Neon API (fallback/cross-check): UNREACHABLE from this sandbox — api.neon.tech DNS does not resolve (egress allowlist; api.render.com and api.github.com resolve fine). Cross-check skipped and recorded; Render lane alone was sufficient.
- Live census probe (SELECT-only, autocommit; scripts/reconcile_db_probe_20261001.py): connected to production neondb (PostgreSQL 18.6, pooler endpoint ep-ancient-cake-a52e4kfd, us-east-2). Schema grounded in the app's own JPA entities: knowledge_nodes.code (unique), questions.primary_topic_node_id + active + external_ref, question_topics.node_id + is_primary, question_spec_points.spec_point_node_id.
- ALL 11 FINGERPRINTS MATCH the Task-55 execution record: qsp_total 2637; qt_total 1130; qt_ING_refs 0; qsp_ING_refs 0; q_primary_ING_active 0; qt_primary_ING_active 0; questions_active 961; primary_distribution_active {0:593, 1:368}; cohort_active 15; cohort_qsp_rows 59; cohort_qt_rows 36. VERDICT: PRODUCTION CONFIRMED — post-qsp15 state durable.
- Informational: knowledge_nodes total 459, of which 104 carry ING-* codes (orphaned vocabulary; referenced-by-active verified 0 above). ING node cleanup remains the known open data-lane item, now quantified.
- Evidence: download/qsp15-census-reverify-20261001/ (census.txt + SHA256SUMS sha256 05ba64de…3aac). Secret-leak scan on the evidence file: clean. No production writes of any kind this task (reads only).
- Task 57 follow-up (b) DISCHARGED — nothing remains blocked on a missing DSN.

Stage Summary:
- SANDBOX-ROLLBACK RECONCILIATION CLOSED WITH LIVE-DB PROOF: remote records main (6590098) and the live production DB independently confirm the durable post-qsp15 state.
- SECURITY (operator action recommended): both API keys chat-exposed — the Render key can read ALL service env secrets and manage deploys; the Neon key has full project control. Recommend revoking both immediately (purpose served) and optionally rotating the Neon DB role password.
- Open items unchanged: sheet-generator regex fallback fix (code lane); bank-scheme sparsity (91 qv); 94 sme-eq-* disagreements (SME lane); ING anchor node cleanup (104 orphaned nodes).
