# V20 Production Reconciliation — 2026-09-15

**Status:** IMPLEMENTED / VERIFIED (current deployed state, claim-by-claim below)  
**Scope:** reconciliation of the Z.ai V20 production report against the canonical GitHub repositories  
**Important:** this artifact does not promote a reported live result to VERIFIED unless durable repository evidence supports the claim.  
**Evidence closure (2026-09-15Z, two-run chain):** the V20 Verify battery first returned **GREEN 55/55** at deployed core `26fec63` (run `34896406018`). Three commits then landed on core main after that battery — the provenance endpoint (`9471b36`, `35df167`) followed by the V23 learner/tutor lineage up to `c76966f` — so the claim was explicitly **demoted** to "`26fec63` = VERIFIED; current main = IMPLEMENTED / UNVERIFIED for the complete V20 contract". The battery was then re-run unchanged (byte-identical workflow + script, verified by git diff between both dispatch points) against the current deployment and returned **GREEN 55/55** again (run `34906678758`), re-promoting **the current deployed state to VERIFIED**. The provenance endpoint introduced by `9471b36`/`35df167` was additionally probed directly (non-regression GREEN 4/4, §8.2b). Two dispositions remain deliberately open: bootstrap-admin credential rotation (**UNVERIFIED**, §8.6) and the orphan `syllabai.vercel.app` project (**REPORTED / UNVERIFIED**, §8.7).

## 1. Source-of-truth reconciliation

The Z.ai report claimed a V20 production verification covering teacher review, learner serving gates, topic mapping, credential rotation, and the teacher workbench deployment.

GitHub ground truth confirms the relevant implementation lineage exists:

- `SyllabAI/syllabai-core` commit `6ec725c530b26f93fedf8bca8fc88a7a068c2571` implements the ingestion-anchor read-model projection and self-service password rotation, with the commit recording 379/379 tests.
- `SyllabAI/syllabai-core` commit `35df8e7c21870036eae31aa93e1a615123c2d9c7` adds the fail-closed marking-contract completeness guard to both paper validation paths and records 381/381 tests.
- `SyllabAI/syllabai-web` commit `fe99551c5f1ecc61b77ee713a14e3978c3078413` adds the on-demand V20 teacher-side production battery. The workflow targets the live Render backend and uses `PILOT_TEACHER_*` secrets without printing them.
- `SyllabAI/syllabai-teacher-workbench` commit `39ad5d833f4e912a2a23a21c289ac8317bf9d86c` implements Vercel readonly mirror mode plus explicit runtime tracing for deployed data, preserving fail-closed startup on undeclared hosts.

These commits are durable implementation evidence. They do **not by themselves prove that the reported live battery actually passed after the final fixes**.

## 2. Findings and status

| Finding | Status | Evidence boundary |
|---|---|---|
| Ingestion anchor is visible in teacher question-topic rows | IMPLEMENTED / VERIFIED (code + tests + live) | Core commit `6ec725c`; live effect proven in run 34896406018 (B17a anchor row visible, `ING-4CH12CSPECIMEN2017`) |
| Self-service password rotation requires current password and logs the event | IMPLEMENTED / VERIFIED (code + tests) | Core commit `6ec725c`; rotation capability also exercised live 6/6 on a teacher credential (2026-09-14). Operator bootstrap-admin rotation remains UNVERIFIED (§8.6) |
| Paper cannot become VALIDATED when any version has no mark scheme, unless explicitly forced | IMPLEMENTED / VERIFIED (code + tests + live) | Core commit `35df8e7`; live effect proven in run 34896406018: 11 distinct scheme-less papers each refused with 409 naming the scheme-less count, no mutation (queue delta = exactly 1) |
| V20 teacher-side production battery exists and exercises the intended workflow | IMPLEMENTED / VERIFIED (workflow/code) | Web commit `fe99551` (later hardened `66f72d2`, `f07b7af`, `c11c5e3`) |
| V20 live battery passes against the FINAL deployed state | VERIFIED | Battery #1: run **34896406018** (job 104151496506), web `c11c5e3` × deployed core `26fec63`, GREEN 55/55 — superseded as "final" when core main advanced. Battery #2 (closing): run **34906678758** (job 104184869529), web main `96d7a34` × deployed core `c76966f` lineage: GREEN 55/55 incl. 11 scheme-less guard refusals, 1 complete-paper lifecycle (Summer 2021 `c30856ff`), topic-mapping B17a–e, census 78→77 (§8.2, §8.2b). The battery workflow + script are byte-identical between both dispatch points (git diff verified) — no weakening, modification, or fork |
| Teacher workbench Vercel runtime repair | IMPLEMENTED / VERIFIED (code + live deployment) | Workbench commit `39ad5d8`; live battery GREEN 9/9 on `https://syllabai-teacher-workbench.vercel.app` (reads 200, canonical data visible, readonly explicit, staging writes 503 pre-auth, zero ENOENT — §8.4) |
| Bootstrap admin credential recovered/rotated after sandbox loss | UNVERIFIED | No credential is inferred or reconstructed; the generated password is unrecoverable (destroyed with the sandbox, never logged/committed) and no authorized current/recovery path exists in the verification environment. Do not invent or rotate without an authorized path; no destructive reset performed |
| Orphan `syllabai.vercel.app` project is safe to delete | REPORTED | Requires operator/platform confirmation before destructive action; still serving 500 MIDDLEWARE_INVOCATION_FAILED and matching no repo's middleware fingerprint, but ownership/authorization remains unverified |

## 3. Architectural conclusions

### 3.1 Assessment validation must prove a learner-servable marking contract

The zero-mark-scheme production finding is not merely a teacher-workflow bug. A `VALIDATED` assessment artifact must imply that a deterministic marking contract exists for every learner-servable question version. Otherwise the platform can accept attempts that can never progress beyond `PENDING`.

This reinforces the existing invariant:

> Imported assessment content is not learner-servable until required validation gates pass.

The marking-contract completeness guard should therefore remain a validation/serving invariant, not be weakened for ingestion convenience.

### 3.2 Ingestion anchors and curriculum mappings are different semantics

The topic-row repair correctly exposes an ingestion anchor without allowing that anchor to become the learner-facing canonical topic. The mapping workflow remains responsible for moving a question from ingestion provenance onto an authoritative curriculum node.

Do not collapse ingestion anchors into the authoritative educational KG.

### 3.3 Deployment convenience must not become a new source of truth

The workbench Vercel readonly mirror is a deployment/runtime adaptation. It must remain a projection of canonical validation state, not a second authoritative data model. Staging writes must remain governed and explicitly disabled where the deployment cannot safely persist them.

## 4. Content Package consequence

Do **not** change the Content Compiler / Portable Content Package architecture based on the V20 fixes alone.

The next Content Package proof should use real, already validated production/canonical content rather than expanding the synthetic fixture set. The target proof should include:

1. one real Revision Note with canonical identity, provenance and SpecificationPoint mapping;
2. one real learner-servable QP/MS pair with a complete marking contract;
3. source hashes and parser/compiler provenance;
4. lifecycle/validation state;
5. semantic reconstruction from the package into equivalent domain records;
6. negative proof that a scheme-less or otherwise non-servable assessment cannot be promoted by the package compiler;
7. clean-environment reconstruction evidence.

The architecture remains **PROPOSED** until that real-corpus proof is captured and reviewed.

**Update (later on 2026-09-15):** the bounded real-corpus proof has since been executed — one real operator-validated Revision Note + one real production-VALIDATED QP/MS pair with a complete marking contract, five fail-closed negative gates, and a clean-room semantic reconstruction, CI-executed GREEN 17/17 (`parser-ci` run 34903192847, parser main `a0a599b`). Exact evidence in `CONTENT_PACKAGE_V0_1_IMPLEMENTATION_STATUS.md`. The architecture itself remains PROPOSED.

**Provenance distinction (kept explicit):** campaign-imported papers currently lack `documents`-table rows in production, so the teacher provenance endpoint fail-closes with 404 for them. No `documents` rows were manufactured and the canonical provenance model was not changed to satisfy the endpoint. The real-corpus package proof used the independently verified workbench protective snapshot bundle + manifest/source identity chain — that is evidence for the package proof only, **not** proof that the production `documents` relationship exists.

## 5. Next verification gate

Before promoting the reported V20 production result to VERIFIED, capture durable evidence for the final deployed state:

- workflow run ID and successful job for `V20 Verify` at the final `syllabai-web` main commit;
- final core deployment SHA and health evidence;
- final workbench deployment/route evidence;
- final 12-paper dogfood result, including the 8 scheme-less papers being rejected by the new guard and the complete papers completing validate → attempt → flag/unflag → revalidate;
- final topic-anchor projection and real curriculum remapping result;
- credential rotation result only if performed through an authorized path;
- no secrets in evidence.

Once captured, update this artifact from `REPORTED` to `VERIFIED` claim-by-claim rather than promoting the entire report wholesale.

## 6. Durable references

- `PROJECT_KNOWLEDGE_MAP.md`
- `CONTENT_COMPILER_AND_PACKAGE_ARCHITECTURE.md`
- `CONTENT_PACKAGE_V0_1.md`
- `CONTENT_PACKAGE_V0_1_IMPLEMENTATION_STATUS.md`
- `ADR_021_CONTENT_COMPILER_AND_PORTABLE_CONTENT_PACKAGE.md`
- `RAG_RETRIEVAL_RESEARCH.md`
- `GEMINI_FILE_SEARCH_AND_NOTEBOOK_ARCHITECTURE_RESEARCH.md`

## 7. Decision

**Decision:** accept the two production-discovered defects as real architectural/implementation lessons, retain their fail-closed fixes, and require durable live-run evidence before claiming full V20 production verification. Do not introduce a new architecture or provider dependency as a reaction to these fixes.

## 8. Final deployed-state evidence (battery #1 2026-09-14T21:01Z; closing battery #2 2026-09-14T22:58Z; written 2026-09-15)

### 8.1 Final SHAs (GitHub main = deployed)

| Artifact | main SHA | Deployed-identity evidence |
|---|---|---|
| `syllabai-core` | **`c76966f`** (current main; lineage `26fec63` → `9471b36` → `35df167` → V23 commits → `c76966f`) | Live fingerprint GREEN 8/8 (2026-09-14T22:54–22:57Z): pre-auth provenance route `/api/v1/teacher/content/exam-papers/{id}/provenance` → 401 (route exists ⇒ deployment ≥ `9471b36`); fresh-student Smart Lesson response carries the V23 KG panels `prerequisites` + `misconceptions` (introduced `0977010`) ⇒ deployment ≥ `0977010`, strictly after `35df167`; Render push-to-deploy of main `c76966f` (last push 2026-09-14T22:25:51Z, no later push), `core-ci` run 34904068391 **success** on `c76966f`. Residual ambiguity window (`0977010`…`c76966f`) touches **no V20-critical file** (git diff `35df167..c76966f`: learner/tutor Smart Lesson + Test Builder marks assembly + tests + V23 migration only) |
| `syllabai-web` | **`96d7a34`** (current main; battery dispatch point for run 34906678758) | Battery workflow + `v20_battery.py` byte-identical to the sanctioned `c11c5e3` version (git diff `c11c5e3..96d7a34` empty for both files); post-`60bc7f3` commits are web UI only (Test Builder marks input, Smart Lesson topic panels, decision audit panel) |
| `syllabai-teacher-workbench` | `39ad5d833f4e912a2a23a21c289ac8317bf9d86c` | Live behavior matches the readonly-mirror implementation (§8.4) |
| `syllabai-parser` | `a0a599b` | `parser-ci` run 34903192847 success incl. real-corpus Content Package proof GREEN 17/17 |
| `syllabai` (central) | `217b7e0` + this update | This artifact is the evidence record |

Core commits between the battery-#1-covered SHA and current main: `9471b36` (teacher provenance endpoint — deterministic parser document ids + source checksums, read-only, fail-closed 404), `35df167` (provenance reads the content store — source identity for every ingested paper), then the V23 lineage `ad9d071`/`0977010`/`b9eeeeb`/`34bd963`/`4954cdb`/`c76966f` (learner tutor-engagement signals, Smart Lesson KG panels, Test Builder marks-aware assembly, performance guard IT, tutor precision floor, Smart Lesson advance leg). **Integrity note:** the "final deployed state" claim was demoted when `9471b36`/`35df167` landed after battery #1, and re-closed by battery #2 on the current deployment. No file touched by `35df167..c76966f` belongs to a V20 gate (validation lifecycle, serving boundary, marking-contract guard, topic mapping); the closing battery is nonetheless the authoritative evidence because it ran against the live current deployment.

### 8.2 V20 Verify workflow run (battery #1, durable evidence — superseded as "final" by §8.2b)

- **Workflow run ID:** `34896406018` — job `104151496506`, workflow_dispatch, `target_count=12`
- **Commit SHA (battery):** `syllabai-web` main `c11c5e37792d7a246286c1f1be3b8dd180300bfe`
- **Backend identity:** `https://syllabai-core.onrender.com` at deployed SHA `26fec63` (§8.1), B0 backend healthy PASS
- **Started / finished:** 2026-09-14T21:01:40Z → 2026-09-14T21:05Z, `completed success`
- **Result:** **VERDICT: GREEN — 55/55 checks passed**
- **Secrets:** PILOT_TEACHER_* used in-workflow only; logs carry statuses, ids, counts — no secret values
- **Verdicts (summary):** B0 healthy; B1a/b teacher login+role; B2a/b bootstrap window closed (available=false, claim 409); B3 teacher→admin 403; B4a/b student registered + student→teacher 403; B5 census; per-paper B6/B11a/B7/B9/B10/B11/B12/B13/B14/B16 as applicable; B17a–e topic mapping; B18 census delta
- **Job log (durable):** committed to the verification workspace; verbatim verdict lines reproduced in §8.3/§8.5

### 8.2b Closing battery on the CURRENT deployment (run 34906678758)

After core main advanced to `c76966f`, the SAME battery (byte-identical workflow + script) was re-dispatched:

- **Workflow run ID:** `34906678758` — job `104184869529`, workflow_dispatch, `target_count=12`
- **Commit SHA (battery):** `syllabai-web` main `96d7a34`
- **Backend identity:** `https://syllabai-core.onrender.com`, deployment ≥ `0977010` by live fingerprint with main = CI-green `c76966f` (§8.1), B0 backend healthy PASS
- **Started / finished:** 2026-09-14T22:58:39Z → 2026-09-14T23:01:48Z, `completed success` (~3 min)
- **Result:** **VERDICT: GREEN — 55/55 checks passed, 0 FAIL**
- **Verdict highlights:** B0 healthy; B1/B2/B3/B4 auth/RBAC/bootstrap closed; B5 census start papers=78 suggested=78 suggestedVersions=735; 11 scheme-less papers refused by the marking-contract guard (409 naming the count: June 2014 ×6, January 2019 ×3, Summer 2019 ×3, January 2020 ×2, January 2022 ×2, January 2023 ×1, Summer 2022 ×1, Summer 2024 ×1, January 2021 ×1, June 2011 ×1, January 2015 ×1); complete paper **Summer 2021 `c30856ff`** (10 versions, withScheme=10) through B6a→B16c full lifecycle; B17a–e topic mapping (anchor `ING-4CH11CSUMMER2021` visible → anchor-as-primary 409 → remap 200 → same-node re-map 200 → persisted `4CH1-1.2`); B18 census end suggested=77 (delta = exactly 1)
- **Post-battery independent census (fresh student, subject-scoped):** 91 papers = **76 SUGGESTED + 15 VALIDATED**; `c30856ff` (4CH1/1C Summer 2021) VALIDATED — delta matches exactly one completed lifecycle. (The queue-v2 view counts one SUGGESTED paper the subject-scoped student listing does not surface — a scoping artifact; both views agree on the run delta.)
- **Job log (durable):** `/home/z/my-project/evidence/v20_run34906678758_job104184869529.log`; deployment fingerprint log `evidence/deploy_fingerprint_35df167_lineage.log`

**Provenance endpoint non-regression (introduced `9471b36`/`35df167`), live GREEN 4/4** (`evidence/provenance_nonregression_c76966f.log`): P1 no token → 401; P2 student token on a real paper id → 403 (no data); P3 student token on unknown id → 403 (no existence oracle). The six regression surfaces are covered by the GREEN battery: authentication (B1a/B1b, B2a/B2b, B4a), teacher authorization (B1b roles, B3 teacher→admin 403, B6a review header subjectId), paper/version serving gates (B12a, B13b, B16a–c), topic mapping (B17a–e), marking-contract guard (B11a × 11), learner-serving boundary (B12b/B14b attempts 201, 404s under FLAGGED, answer-key boundary B6b). The battery's target selection also consumed the bridge-record projection (`reconciliationStatus=OK`, `bridge=OK` on all 12 targets) — the provenance data path exercised live in passing. CI unit coverage of the fail-closed 404 (no bridge record) path is green at `c76966f` (`core-ci` run 34904068391, 413/413 lineage).

### 8.3 Marking-contract guard — live negative results (11 papers, no mutation; reproduced in run 34906678758)

Every attempted flip of a scheme-less paper was refused with `409` naming the scheme-less count, and the queue census moved by exactly the one complete paper (B18: 78→77), proving no unintended mutation on rejected validation:

| Target paper (session) | Scheme-less versions | Guard verdict |
|---|---|---|
| June 2014 | 6 | 409, refused |
| January 2019 | 3 | 409, refused |
| Summer 2019 | 3 | 409, refused |
| January 2020 | 2 | 409, refused |
| January 2022 | 2 | 409, refused |
| January 2023 | 1 | 409, refused |
| Summer 2022 | 1 | 409, refused |
| Summer 2024 | 1 | 409, refused |
| January 2021 | 1 | 409, refused |
| June 2011 | 1 | 409, refused |
| January 2015 | 1 | 409, refused |

The explicit `force=true` override remains available and was NOT used in any of these refusals (the guard path is the default; forced path stays a deliberate, separate action).

### 8.4 Workbench live deployment (readonly mirror)

Probe battery on `https://syllabai-teacher-workbench.vercel.app` (unauthenticated read surface): **GREEN 9/9**

- W1 app shell 200 + expected title — PASS
- W2 read APIs 200: `/api/review/index`, `/api/decisions`, `/api/canonical/events` — PASS
- W3 canonical data visible: review index 19,838 bytes of real 4CH1 paper data — PASS
- W4 readonly mode explicit: `X-Durable-Copy: skipped (readonly deployment)` on the export route — PASS
- W5 staging writes refused 503 BEFORE auth: `POST /api/decisions` and `POST /api/session` both 503 with explicit `readonly deployment` reason — PASS
- W6 `/api/decisions/export` 200 — PASS
- W7 zero ENOENT in any response (runtime file tracing intact) — PASS

Undeclared-host fail-closed startup remains intact in code (`src/lib/prod-config.ts`: VERCEL=1 defaults to readonly; any undeclared host refuses to boot) and was previously verified live-fatal on a local standalone production build. No gate was weakened to make the deployment work: the mirror can only read, never stage.

### 8.5 Complete-paper lifecycle + topic mapping (Specimen 2017, run 34896406018; re-proven on Summer 2021 in run 34906678758)

**Battery #2 (closing, on the current deployment) re-proved the entire sequence** with complete paper Summer 2021 `c30856ff` (10 versions, withScheme=10): `B6a header subjectId → B6b answer key (versions=10 withScheme=10) → B7a flag version → B7b batch blocked 409 → B9 paper-validate refused 409 → B10 unflag → B11 validate-all → VALIDATED (10 versions) → B12a student sees VALIDATED → B12b attempt 201 → B13a flag paper → B13b attempt 404 → B13c batch 409 → B14a unflag → SUGGESTED → B14b attempt 201 → B14c restored VALIDATED → B16a/B16b attempts 404 → B16c re-VALIDATED attempt 201`, then B17a–e mapping (`ING-4CH11CSUMMER2021` anchor visible → anchor-as-primary 409 → remap 200 → same-node 200 → persisted `4CH1-1.2`) and B18 queue 78→77. All PASS.

**Battery #1 (historical, at core `26fec63`):** One complete paper (`23ef5e6e` "Specimen 2017", 9 versions, 9 with schemes) through the full §7 sequence, all PASS:

`B6b answer key visible to teacher (versions=9 withScheme=9) → B7a flag version → B7b batch blocked 409 → B9 paper-validate refused while versions unvalidated 409 → B10 unflag → B11 validate-all → paper VALIDATED (9 versions) → B12a student sees paper VALIDATED → B12b student structured attempt 201 → B13a flag paper → B13b attempt under FLAGGED paper 404 → B13c batch on FLAGGED paper 409 → B14a unflag → SUGGESTED (never straight to VALIDATED) → B14b attempt 201 again → B14c paper restored VALIDATED → B16a attempt on FLAGGED version 404 → B16b attempt on SUGGESTED version 404 → B16c attempt on re-VALIDATED version 201`

Topic mapping (B17, all PASS): `B17a` current mapping readable — anchor row visible (`primary=ING-4CH12CSPECIMEN2017`); `B17b` anchor-as-primary refused 409; `B17c` remap onto real curriculum topic 200; `B17d` re-map onto the SAME node stays 200 (uq_question_topic flush regression `80b1ff8`); `B17e` mapping persisted (`primary=4CH1-1.9`).

### 8.6 Credential state

**UNVERIFIED.** The bootstrap-admin password generated during activation died with the wiped verification sandbox; it was never logged or committed, and no authorized current/recovery path (in-product rotation requires the current password; no Neon DSN is available to the verification environment) exists. Per the mission rule no password was invented, reconstructed, or reset destructively. The rotation **capability** itself is IMPLEMENTED / VERIFIED (core `6ec725c`, plus a live 6/6 rotation exercise on a teacher credential: wrong-current 401 without mutation → correct-current 204 → old password rejected → new accepted, audit-logged). Operator action remains: rotate `admin@syllabai.dev` via an authorized path.

### 8.7 Orphan Vercel project

**REPORTED / UNVERIFIED.** `syllabai.vercel.app` still returns 500 `MIDDLEWARE_INVOCATION_FAILED`; no repo history contains a `middleware.ts`, and its static-asset fingerprint matches neither deployed app. Deletion was NOT performed: platform-side project identity and operator authorization could not be verified from the verification environment. CORS for the canonical apps is already covered by explicit `SYLLABAI_CORS_ORIGINS`, so the orphan is inert but unresolved.

### 8.8 Corpus scope and census

- Scope: Edexcel International GCSE Chemistry **4CH1** past-paper corpus in production Neon (papers ingested through the sanctioned GLM-OCR pipeline, all content SUGGESTED until teacher-validated).
- Census at battery-#2 start (run 34906678758): **78 SUGGESTED / 735 suggested versions** (queue v2 view; independent student-scoped census minutes earlier read 77 SUGGESTED + 14 VALIDATED = 91 placed papers — the queue counts one SUGGESTED paper the subject-scoped student listing does not surface; scoping artifact, deltas agree).
- Census at battery-#2 end: **77 SUGGESTED** in queue; independent student census **76 SUGGESTED + 15 VALIDATED**, Summer 2021 `c30856ff` VALIDATED (delta = exactly the one complete paper validated this run; the 11 scheme-less papers remained SUGGESTED and unmutated).
- Cumulative dogfood state after battery #2: 15 papers teacher-validated through the real workflow (3 E2E + prior dogfood + Specimen 2017 + Summer 2021), 0 FLAGGED, 0 REJECTED; June-2014 remains in queue awaiting mark-scheme authoring (guard holds it out of learner serving).

**Decision (updated, evidence chain complete):** the V20 production verification claim was promoted REPORTED → VERIFIED on battery #1 (run 34896406018 at `26fec63`), **demoted to `26fec63`-scoped when `9471b36`/`35df167` and the V23 lineage advanced main beyond the battery-covered state**, and re-promoted to the **current deployed state = VERIFIED** by closing battery #2 (run 34906678758, GREEN 55/55, byte-identical battery, provenance-endpoint non-regression GREEN 4/4, deployment fingerprint GREEN 8/8). The Content Package consequence in §4 stands; its bounded real-corpus proof is complete and the ADR-021 architecture remains PROPOSED.
