# Tutor Current-State Audit — 2026-09-28

**Author:** senior engineering agent (session-144), per the Master Engineering Brief §27.
**Method:** repository evidence only — code read at `syllabai-core@ a28e932` (main, core-ci SUCCESS 2026-09-27 14:23 UTC, `mvn verify` = unit + Testcontainers ITs), `syllabai-web@ 03210b3`, master repo `syllabai@ 16584c1`; plus read-only production verification (Neon aggregates, Render health, GitHub Actions) on 2026-09-27 ~18:30 UTC. Chat history was not used as truth.
**Status vocabulary** (Brief §1): PROPOSED / ACCEPTED / IMPLEMENTED / VERIFIED / INFERRED / REPORTED / UNVERIFIED / REJECTED. Nothing below is marked VERIFIED without named evidence.

---

## 1. Actual architecture (diagram)

```text
WEB  TutorChatView (syllabai-web) — client transcript; historyFor() last-8 turns;
     lazy POST /tutor/sessions on first ask; localStorage anchor "syllabai.tutor.sessionId"
  │  POST /api/v1/tutor/ask  {question ≤2000, history ≤12 turns, sessionId?}
  ▼
TutorController (@Valid; TutorSessionService.requireOwned BEFORE pipeline — foreign id 404s fast)
  ▼
KaRagService.ask(learnerId, question, history, sessionId)          [337 lines, the orchestrator]
  0   CurriculumScopeResolver.resolveActive(learnerId)     ── fail-closed (null ⇒ both arms empty)
  0.5 ConversationTurn.sanitize(history) + retrievalQuery()  ── 4-turn window, 1200 chars, question last
  1   GraphKnowledgeRetriever          ── deterministic token-overlap on VALIDATED node titles (KG arm)
  2   ContentVectorRetriever           ── pgvector, VALIDATED-only serving gate, cosine ≥ 0.15, rev1 embeddings
  2.5 PaperQuestionResolver.resolveWithVerdict ── deterministic paper identity → pinned lead evidence
  3   ReciprocalRankFusion.fuseWithPlanWeights ── RRF k=60; NOTE 1.0 > SYLLABUS .9 > QP .8 > TEXTBOOK .7 > MS .6 > CARD .3
  4   NoReranker (identity) → pinned-first dedup merge → evidenceLimit 6
  4.5 FAIL-OPEN GUARD ── identityParsed && pinned empty ⇒ evidence := ∅ (wrong-paper misattribution class)
  5   GROUNDING GATE ── evidence empty ⇒ deterministic refusal, NO LLM call (generic | paper-identity echo)
  │ else
  ├─  LearnerContextAssembler.assemble ── learner brief (BKT mastery/fluency/misconceptions, relevant nodes only)
  │      + TutorMemoryService.digest      ── §22 episodic cross-session digest (asks/practice/review, ≤3 topics, ≤700 chars)
  │      + TutorPolicyService.select      ── deterministic intervention plan (rules-v0.2)
  ├─  GroundedTutorGenerator.generate    ── prompt v5 (tutor-grounded/v5), T=0.2, ≤900 tokens,
  │      "Answer ONLY from numbered SOURCES", mhchem/LaTeX rules, conversation + memory blocks
  └─  SimpleCitationResolver.resolve     ── citation labels/deeplinks rendered from evidence (NO validation)
  ▼
TutorAnsweredEvent ──▶ TelemetryService (KA_RAG_COMPLETED: question, evidenceCount, sources,
  │                     refused, promptVersion, historyTurns, sessionId, interventionType, latency)
  └─(async @Order(30), @Transactional)─▶ TutorEngagementRecorder ──▶ tutor_topic_engagements
                                          (deterministic signal classification v2; no raw text)
Controller epilogue: sessionId ⇒ TutorSessionService.append (user turn + marker-stripped assistant turn)
```

Parallel surface — **CLA** (`ClaService`, 5 context kinds × 4 modes) composes the same generator/policy/LIM stack with server-resolved `ResourceContext` and the deterministic `ClaLeakagePolicy` (§7: HINT never sees scheme points; CHECK gated on attempt state, 409 pre-attempt). CLA asks are single-turn (no history field), not persisted as sessions.

## 2. Actual request → response path (verified)

`POST /api/v1/tutor/ask` — authenticated (`@CurrentUserId`); request `TutorAskRequest{question ≤2000 @NotBlank, history ≤12 @Valid turns (role user|assistant, ≤2000 chars), sessionId?}`. Teachers preview with their own identity. Anonymous preview exists at the service layer (`learnerId == null` flows allowed) but NOT via this endpoint (auth required; the anonymous path is exercised by `KaRagServiceTest.anonymousAsk`). Foreign/unknown `sessionId` 404s **before** the pipeline (LLM spend protected — proven by `TutorSessionStoreFlowIT.foreignSessionIdFailsAskFast`). The controller epilogue appends the exchange only after a completed ask; a pipeline exception persists nothing (DESIGN DOCUMENTED + unit-level `appendWritesPair`; the exception path itself is UNTESTED — see §12-D6).

VERIFIED: `KaRagFlowIT.groundedAsk` (real pgvector + real fixtures end-to-end), 287 live `KA_RAG_COMPLETED` rows.

## 3. Actual retrieval path (verified — and the central risk)

Serving = **two arms + pinned lead**: KG deterministic intent (whole-token match on VALIDATED UNIT/TOPIC/SUBTOPIC titles, single-token floor 0.50, stop list; prerequisites + misconceptions gathered but misconception attachments fire 0× in production — concept nodes SUGGESTED) fused with VALIDATED-gated pgvector (cosine ≥ 0.15, embedding rev1 — deliberately rolled back from rev2 after the 0-hit anomaly, serving the weaker corpus knowingly), plus identity-pinned paper evidence outside fusion.

Pipeline-stage reality vs the documented §5 14-stage engine (from `RAG_RETRIEVAL_RESEARCH.md`): query understanding PARTIAL (deterministic only, by design); curriculum resolution EXISTS (T-C07 fail-closed everywhere); **concept resolution DOES NOT EXIST as retrieval input** (concept nodes invisible; `conceptIds` never populated); learner-aware ranking DOES NOT EXIST (`LearnerSignals.empty()`); lexical retrieval EXISTS as code but **NOT in serving** (benchmark arm B only — KaRagService fuses KG+vector only); semantic EXISTS; metadata filtering PARTIAL (kind + scope only); fusion EXISTS (RRF + plan weights); dedup EXISTS; **reranking DOES NOT EXIST beyond identity** (`NoReranker`; arm D never built); evidence selection PARTIAL (`limit 6`); **evidence sufficiency DOES NOT EXIST programmatically** (prompt-level only).

Benchmark record (ratified harness spec, frozen gold sets/snapshots, anti-tuning SHA manifests): **every §8 promotion verdict to date is NOT PROMOTED**. Latest (r5 at-flip, snap-004, 2026-09-27): hybrid recall@10 **0.0762** vs floor 0.3249; MRR **0.0674** vs 0.2964; nDCG@10 **0.1473** vs 0.4799; boundary violations **0** (T-C20 VALIDATED-only gate holds); determinism byte-identical ×3. The floors are indexed to the Run-1 ALL-corpus baseline while serving is VALIDATED-only (317 of 3,831 chunks) — the tracker's own conclusion: *"the promotion path is corpus work (validation throughput) + the chunk→SP substrate… not a better scorer."* Flagship §8(d) SpecPoint resolution has **never been scored** (NOT SCOREABLE in every run; the 210-row HUMAN_VALIDATED chunk→SP substrate was bridged 2026-09-27, but the scoring code is unwritten — `bench/S8D_SCORING_HANDOFF_2026-09-28.md` READY FOR IMPLEMENTATION, core main not started).

## 4. Actual learner-state path

Read-only, per-ask: `LearnerContextAssembler` renders a learner brief from BKT skill states (mastery, procedural fluency gaps) and BDT misconception states, **filtered to relevant nodes only** (matched topics + prerequisites); "no prior evidence" renders honestly, never a fabricated profile (proven by `LearnerContextAssemblerTest`). Cross-session: `TutorMemoryService.digest` weaves prior asks / practice outcomes / review-due into ≤3-topic, ≤700-char prose — counts and recency only, **never mastery probabilities** (leakage-pinned by `doesNotContain("0.4")`). The Tutor NEVER mutates learner state: no write path exists from chat to mastery/misconceptions (invariant holds structurally — the only writer is the assessment evidence path). Learner state influences **generation/policy only, never retrieval ranking**.

## 5. Actual intervention / pedagogy path

`TutorPolicyService` (T-026, rules-v0.2) — deterministic, evidence-backed, precedence: teacher-CONFIRMED struggle inference > active inference p≥0.65 on matched topic > active BDT misconception ≥0.50 on matched topic > source-grounded EXPLANATION fallback. Types: EXPLANATION, MISCONCEPTION_REMEDIATION, PREREQUISITE_REVIEW, PROCEDURAL_FLUENCY, METACOGNITIVE_CHECK. Selection emits `TutorInterventionSelectedEvent` (policy version recorded). The plan rides the prompt as an instructional strategy; the system prompt forbids presenting it as diagnosis.

**Production reality (verified from telemetry):** 817 selections = EXPLANATION 808, METACOGNITIVE_CHECK 9, and **zero** MISCONCEPTION_REMEDIATION / PREREQUISITE_REVIEW / PROCEDURAL_FLUENCY. The diagnosis-aware branches are production-unexercised — no active struggle inferences co-occur with matched topics. Root cause undiagnosed (inference substrate output vs topic-match co-occurrence). The free Tutor has NO learner-facing mode selection (§9's Understand→Hint→…→escalation exists only in the CLA surfaces, where it is deterministic and leakage-gated).

## 6. Actual evidence / citation validation path

What exists: (a) prompt-instructed citation ("cite [n] exactly where content supports a statement; never invent spec refs/pages"); (b) `SimpleCitationResolver` renders labels/deeplinks **from the evidence list** (citations cannot reference evidence that wasn't assembled); (c) the web frontend renders `[n]`/`【n】` markers as chips and **out-of-range markers as plain text** (a rendering safety net, not validation); (d) the CLA §10.4 offline evaluation gate measured citation validity 100% / leakage 0 / refusal correctness 100% on the evaluated lineages (`CLA_EVALUATION_BUNDLE.md`).

**What does NOT exist: any runtime post-generation validation** — no claim extraction, no claim-to-evidence entailment check, no marker-range enforcement server-side, no unsupported-claim removal. The architecture docs' phrase "grounded generation + citation validation" (CLA contract composition table; ADR-022) overstates the runtime: validation is an offline evaluation property, not a serving gate. This is the single largest correctness gap between the intended architecture and the implementation.

## 7. Actual conversation persistence path (§22 session store, s140–s143)

Schema (V42, live in production): `tutor_sessions` (learner-owned, `last_active_at` index) + `tutor_session_turns` (per-session `seq` UNIQUE, role CHECK, §19 footer fields per assistant turn, ON DELETE CASCADE); V44 widened role to VARCHAR(16) after the 09-27 incident. Service: create / view (seq-ordered) / latest / **list (recency, ≤50, derived title = opening user question ≤120 chars, batched queries, defensive "never title from a non-user row")** / **delete (transcript rows then anchor, InOrder-pinned)** / append (user+assistant pair, marker-stripped answer, content ≤9000 chars). Ownership: every op resolves against the caller; foreign id indistinguishable from unknown (404) — proven for view/append/delete/list. Assistant turns store citation markers REMOVED (the citation archive of record is the immutable `KA_RAG_COMPLETED` telemetry row). Web: conversations pane (list/resume/new/delete, no rename — title server-derived), refresh hydration with the s141 anchor-reattach fix, unsent input preserved on switch.

Concurrency: append computes next seq via `findTopBySessionIdOrderBySeqDesc` inside a transaction — the UNIQUE(session_id, seq) constraint backstops races (a concurrent double-append would fail loudly, not corrupt). Retention/deletion: learner-side delete exists; account cascade deletes; **no time-based retention policy** (e.g. auto-expire old chats) — acceptable for the pilot's data-minimization posture but unrecorded as a decision.

## 8. Actual LIM / evidence path

`TutorAnsweredEvent` → `TutorEngagementRecorder` (@Order(30), @Transactional) → one `tutor_topic_engagements` row per deterministically matched topic. Signal classification v2 (deterministic precedence): MISCONCEPTION_RELATED (policy intervened on active misconception) > PREREQUISITE_HELP > DOUBT_SIGNAL (fixed phrase list) > CLARIFICATION_REQUEST > EXPLANATION_REQUEST > TOPIC_ENGAGEMENT. Anonymous / no-match / null-learner write **nothing** (data minimization). Raw question text is read for classification and discarded — never stored in learner memory (it lives only in research telemetry). Consumers (read-only): LearnerStateView signal counts (30-day window), SmartLessonService tutor-engagement leg, NBA tutor-engagement tier. CLA attaches via the same recorder with the surface triple (surface/mode/context). **VERIFIED live:** 613 engagement rows in production (FREE_TUTOR 285, CONTEXTUAL_ASSISTANT 328), signal distribution consistent with the classifier.

## 9. Current test coverage (inventory, CI-verified on main HEAD a28e932)

17 Tutor test classes, 137 methods (131 unit + 6 IT) + ~6 adjacent classes. Highlights of what is **proven**: every refusal path is deterministic-no-LLM (`verify(generator, never())`); serving-law fail-closed at every resolver tier (SUGGESTED/REJECTED/stale rows never pin — 20 `PaperQuestionResolverTest` negatives); ownership 404-indistinguishability on all session ops incl. the G1 bank-ambiguity shape; marker stripping + prompt-injection-shaped role rejection (`"system"`/`"ignore previous instructions"` drop out); no mastery probabilities in digests; no raw text in engagement rows; prompt-version lineage (v1–v5 registry, exactly 5 rows — also asserted against the live registry); role-width incident pinned twice (reflection test + real-schema IT); memory-digest content bounds; list/delete semantics incl. title honesty.

**Coverage gaps (tests exercise but do not prove):** TutorController bean-validation never tested at HTTP layer (the IT invokes the controller method directly, bypassing `@Valid`); TutorSessionController REST endpoints untested at HTTP level; s139 history-aware ask and the fail-open guard have **no integration test** with real fixtures (unit-only); memory-digest production wiring has no test (`LearnerContextAssemblerTest` still uses the legacy no-memory constructor — the 3-arg production path is unproven); "pipeline exception ⇒ session untouched" untested; telemetry `sessionId` mapping never asserted by any test (only `historyTurns` is); ContextAssembler/NoReranker have no dedicated tests.

## 10. Current production verification (read-only, 2026-09-27 ~18:30 UTC)

| Check | Result |
|---|---|
| Render core health | `{"status":"UP"}` 200 in 0.43 s (warm) |
| Deployed schema | Flyway **V44** (installed 09-27 09:47 UTC) ⇒ production ≥ s141 `e5aac11` |
| Prompt v5 live | 87 v5 asks on 09-27 (v2 64 that week; v3/v4 transition same day); registry v1–v5 |
| §22 store live | 6 sessions / 6 turns / 4 learners; last active 09-27 12:13 UTC; 3 complete exchanges + 3 empty sessions (residue of the role-width 500 incident, honestly rendered as "Empty conversation") |
| Session-anchored asks | 8 v5 telemetry rows carry a real sessionId (linkage works); 79 carry `""` (see §12-D1) |
| Refusals | 77/287 overall (27%); v5-day 27/87 (31%) — the honest cost of a VALIDATED-only corpus that is 317/3,831 chunks |
| LIM live | 613 engagement rows; CLA_EXCHANGE_COMPLETED 328; signal distribution matches classifier design |
| Intervention live | EXPLANATION 808 / METACOGNITIVE_CHECK 9 / everything else 0 (see §5) |
| **s143 list/delete deployed?** | **UNVERIFIED** — no migration to fingerprint, read endpoints emit no telemetry, and no credentials are held to probe; the web pane degrades honestly on 404. OPERATOR: confirm the Render deploy of `a28e932`. |
| CI on main HEAD | core-ci SUCCESS (mvn verify: unit + Testcontainers ITs) 2026-09-27 14:23 UTC |

## 11. Architecture / document conflicts

1. **`syllabai-core/docs/CONTEXTUAL_LEARNING_ASSISTANT_IMPLEMENTATION.md` status header is stale**: "PROPOSED — contract only. No runtime code is authorized by this document" vs a fully implemented, deployed, learner-exposed runtime (328 live exchanges; the master-repo `CONTEXTUAL_LEARNING_ASSISTANT_ARCHITECTURE.md` status IS current and detailed). Two companion docs now disagree about the same subsystem.
2. **ADR-022 scope guard** ("authorizes contract and evaluation design only — no runtime implementation") is superseded in reality (runtime shipped; learner exposure authorized in the CLA architecture status) but the DECISIONS.md entry still reads as the governing text.
3. **CLA architecture status says NOTE_SECTION "SUBSTRATE-BLOCKED/architecture decision required"** — but NOTE_SECTION is implemented and live (core `ResourceContext.noteId`; web NoteClaOverlay s135/s137).
4. **MASTER_SPEC §14** decision path includes "Understanding check → Variation/transfer" as tutor responsibilities; in the implementation these exist only as optional prompt actions in the EXPLANATION fallback ("Finish with a brief understanding check") — no loop, no enforcement, no follow-up. Documented intent is ahead of runtime.
5. **MASTER_SPEC §22** API examples (`POST /api/v1/tutor/query`, `GET /tutor/sessions/{id}/stream`) diverge from the implemented `POST /api/v1/tutor/ask` and no-stream reality (SSE deferred, recorded in T-025). Illustrative, but worth a spec sync.
6. **"Citation validation" language** in the CLA contract composition table and ADR-022 reads as a runtime property; it is an offline-evaluation property (see §6). The distinction should be stated wherever the phrase appears.

## 12. Known defects (all code-level, from this audit; classified)

**Production defects / live residue**
- **D1 (minor, telemetry hygiene):** `TelemetryService:202` writes `sessionId: ""` when null — 79/87 v5 rows carry an empty string rather than an absent key. Linkage for anchored asks works; the convention pollutes the research payload.
- **D2 (observability gap):** the refusal **provider** (`deterministic-refusal` vs `deterministic-paper-refusal`) is not serialized into telemetry (only `answerModel`, which is null on refusals) — the two refusal paths are indistinguishable in the research record; the G1 guard evidence lives only in server logs.
- **D3 (cosmetic):** 3 empty session rows are permanent residue of the 09-27 role-width incident (no cleanup path exists; they render honestly as "Empty conversation" but never disappear except by learner delete).

**Test defects / unproven claims**
- **D4:** TutorController + TutorSessionController have zero HTTP-layer tests (bean validation, routing, security wiring).
- **D5:** s139 history-aware ask + fail-open guard + PaperQuestionResolver are unit-proven only — no Testcontainers IT drives them against real fixtures.
- **D6:** "a failed ask persists nothing" is documented design but untested (only refusals-which-do-persist are covered).
- **D7:** memory-digest production wiring (3-arg LearnerContextAssembler → digest → prompt) has no test; `LearnerContextAssemblerTest` pins the legacy constructor.

**Web-side flags (from the s141–s143 surface)**
- **D8:** CLA transcripts are client-only and CLA asks carry no history (single-turn contract) — asymmetric with the Tutor, undocumented in the UI.
- **D9:** `openConversation` fetch failure silently removes the row (no error surface); transient network failure makes a conversation vanish until next refresh.
- **D10:** multi-tab localStorage session-anchor race (two tabs each lazily create/overwrite the shared key).
- **D11 (known v0 decision):** auth token in localStorage; httpOnly-cookie hardening deferred to Wave 4.
- **D12 (known v0 decision):** hydrated answers restore without citations (`[n]` renders as dead text; archive of record = telemetry). Documented, but a UX regression on resume.
- **D13:** `SPECIFICATION_POINT`/`specCode` client capability is dead (never sent by any surface).

**Architectural gaps (not defects — absent by decision or priority)**
- Runtime claim/citation validation (§6); programmatic evidence sufficiency (binary gate at zero evidence; thin evidence generates confidently); learner-aware ranking (`LearnerSignals.empty()`); reranking (identity only); lexical arm not in serving; policy diagnosis branches production-dead (§5); no retention policy for transcripts; no rename (derived titles only).

## 13. Highest-value gaps (evidence-ranked)

1. **Retrieval relevance is the binding constraint on every Tutor quality category** — 27–31% live refusal rate; §8 floors unreachable by construction while most gold sits on SUGGESTED papers; §8(d) never scored. The promotion path is corpus validation (OPERATOR-HELD card wave) + the §8(d) scoring code (agent-executable, fully specified, not started).
2. **No runtime claim/citation validation** — grounding is prompt-trust + offline-eval-proven; the §23 categories "citation correctness" and "grounding" have no serving-time enforcement. (The brief §11: "an unvalidated citation is a correctness defect" — today every citation is technically unvalidated at runtime.)
3. **Evidence sufficiency is binary at zero** — one weak VALIDATED chunk passes the gate and generates a confident answer; no sufficiency threshold, no per-class evidence requirements.
4. **Policy diagnosis branches are production-dead** (0 firings) — either the struggle-inference substrate produces nothing usable or topic co-occurrence never aligns; undiagnosed.
5. **Test-proven vs deployed-behavior gap** — D4–D7 leave the newest surface's HTTP contract and memory wiring unproven.

## 14. Recommended first implementation tranche

Per Brief §28 ("if retrieval is demonstrably the bottleneck, do not spend the next iteration polishing prompts" — it is, and we won't):

**Tranche 1 (recommended): implement the §8(d) scoring handoff** — `bench/S8D_SCORING_HANDOFF_2026-09-28.md` (master repo, READY FOR IMPLEMENTATION): snap-005 export contract (byte-identical `chunk_spec_hv.json` + fail-closed drift gate), `BenchSnapshot.hvSpecCodesByChunkRef()` accessor (absent-artifact = NOT SCOREABLE preserved), runner §8(d) scoring with the pinned counting rule (validation_status, never tier; dual granularity, gate on full coverage pending the §10 owner ruling), verification vectors included. Fully specified, agent-executable without the operator, unblocks the flagship metric for the r6 card-flip run, lands as the r6 run class per the handoff's own sequencing. Unit + replay tests; no serving-path change (bench lane only).

Riders (small, independent, same discipline — only if budget allows, else next tranche): (a) **D2 fix** — serialize the refusal provider into `KA_RAG_COMPLETED` telemetry + assert it (makes the fail-open guard's live firing rate measurable in the research record); (b) **D7 fix** — a wiring test for the 3-arg `LearnerContextAssembler` + digest.

**Human gates (not agent work):** the card-validation wave (r6 trigger), the §10 §8(d)-granularity ruling, the lexical OR-form gold re-freeze decision, confirmation of the Render deploy of `a28e932` (s143), and the policy dead-branches root-cause is a *diagnosis* item that may or may not surface an operator decision.

## 15. Status classification (every major component)

| Component | Status | Evidence |
|---|---|---|
| `POST /api/v1/tutor/ask` endpoint | IMPLEMENTED + VERIFIED | KaRagFlowIT (real pgvector); 287 live telemetry rows |
| Deterministic intent (KG matcher) | IMPLEMENTED + VERIFIED | GraphKnowledgeRetrieverTest 10 tests incl. T-C07 negatives |
| Vector arm (VALIDATED-only) | IMPLEMENTED + VERIFIED | ContentVectorRetrieverTest; ContentPipelineIT negative controls; run reports |
| Paper-question resolver + fail-open guard | IMPLEMENTED + VERIFIED (unit + live incident) | 20+6 tests; b17214a cites 09-27 G1 live evidence |
| RRF fusion + plan weights | IMPLEMENTED + VERIFIED | ReciprocalRankFusionTest; ServingPlanWeightsTest (bit-identical unweighted posture) |
| Reranking | IDENTITY ONLY (NoReranker) | code; arm D never built |
| Evidence sufficiency | NOT IMPLEMENTED (prompt-level only) | code; EvidenceRequirements defaults unpopulated |
| Lexical arm in serving | IMPLEMENTED as code, NOT in serving | Bm25Retriever (bench-only); run-003-b |
| Grounded generation (prompt v5) | IMPLEMENTED + VERIFIED | GroundedTutorGeneratorTest 12; v5 live 09-27 |
| Deterministic refusal (both paths) | IMPLEMENTED + VERIFIED | never()-proofs; 77 live refusals |
| Working memory (s139) | IMPLEMENTED + VERIFIED (unit); IT-gap D5 | ConversationTurnTest; KaRagServiceTest ×4 |
| §22 session store (s140) | IMPLEMENTED + VERIFIED | TutorSessionServiceTest 12; TutorSessionStoreFlowIT (real schema); live rows |
| Conversation list/delete (s143) | IMPLEMENTED (CI-green); production deploy UNVERIFIED | TutorSessionServiceTest +6; IT +1; no live fingerprint |
| Cross-session memory digest | IMPLEMENTED; wiring UNPROVEN (D7) | TutorMemoryServiceTest 5; no e2e test |
| Intervention policy (T-026) | IMPLEMENTED + unit-VERIFIED; production-dead branches | TutorPolicyServiceTest 16; telemetry 808/9/0/0/0 |
| Learner brief assembly | IMPLEMENTED + VERIFIED | LearnerContextAssemblerTest 3 (legacy ctor) |
| Claim validation (runtime) | NOT IMPLEMENTED | code search; offline eval only |
| Citation validation (runtime) | NOT IMPLEMENTED (rendering safety net + offline eval only) | §6 |
| CLA runtime (5 kinds × 4 modes, leakage gate) | IMPLEMENTED + VERIFIED | ClaServiceTest; §10.4 bundle (leakage 0, 100% citation validity offline); 328 live exchanges |
| CLA leakage gate (§7 deterministic) | IMPLEMENTED + VERIFIED | S-D 10/10; CI-mandatory negative suite |
| LIM recorder + signals v2 | IMPLEMENTED + VERIFIED | TutorEngagementRecorderTest 14; 613 live rows |
| Telemetry (§19) | IMPLEMENTED + VERIFIED (with D1/D2 hygiene gaps) | payload keys live; KaRagFlowIT |
| Web chat + conversations pane | IMPLEMENTED (Vercel auto-deploy); s143 pane depends on unconfirmed core deploy | verify scripts s139/s143; agent report D8–D13 |
| Retrieval quality vs promotion thresholds | NOT PROMOTED (all §8 runs) | r5 numbers; TODO.md T-C13 open |
| §8(d) SpecPoint scoring | NOT SCOREABLE (data bridged; code not started) | S8D_SCORING_HANDOFF |
| Progressive pedagogy escalation (§9) | PARTIAL — CLA modes only; free Tutor has no modes | code; CLA eval |

---

**Bottom line:** the Tutor's *safety* properties (fail-closed scope, deterministic refusal, leakage gating, ownership isolation, LIM provenance discipline, no chat→mastery mutation) are implemented and, unusually for the industry, **evidence-backed at every layer** — unit, integration, benchmark, and live production. Its *quality* properties (retrieval relevance, claim validation, pedagogy beyond the explanation fallback) are the honest frontier, and the record itself says the next leverage is corpus validation + the §8(d) scoring lane, not generation polish. Recommended first tranche: **§8(d) scoring handoff implementation**, with the D2 telemetry rider.
