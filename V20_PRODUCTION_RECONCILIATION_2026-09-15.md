# V20 Production Reconciliation — 2026-09-15

**Status:** IMPLEMENTED / VERIFIED (final deployed state, claim-by-claim below)  
**Scope:** reconciliation of the Z.ai V20 production report against the canonical GitHub repositories  
**Important:** this artifact does not promote a reported live result to VERIFIED unless durable repository evidence supports the claim.  
**Evidence closure (2026-09-15Z):** the V20 Verify workflow was re-run at the final `syllabai-web` main commit against the final deployed `syllabai-core` and returned **GREEN 55/55** — see §8. Two dispositions remain deliberately open: bootstrap-admin credential rotation (**UNVERIFIED**, §8.6) and the orphan `syllabai.vercel.app` project (**REPORTED / UNVERIFIED**, §8.7).

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
| V20 live battery passes against the FINAL deployed state | VERIFIED | Workflow run **34896406018** (job 104151496506), `syllabai-web` main `c11c5e3` × deployed core `26fec63`: GREEN 55/55 incl. 11 scheme-less guard refusals, 1 complete-paper lifecycle, topic-mapping B17a–e, census 78→77 (§8) |
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

## 8. Final deployed-state evidence (captured 2026-09-14T21:01Z / 2026-09-15)

### 8.1 Final SHAs (GitHub main = deployed)

| Artifact | main SHA | Deployed-identity evidence |
|---|---|---|
| `syllabai-core` | `26fec634f2bb2e75fa7f0e2bd4a0f1e57cd3f183` | Live route fingerprint: `/api/v1/teacher/test-builder` (deb235a) and `/api/v1/tutor/memory` (4faef96) both exist pre-auth (401, not 404); Render autoDeploy of the last main push |
| `syllabai-web` | `c11c5e37792d7a246286c1f1be3b8dd180300bfe` | Live bundle grep of `https://syllabai-web.vercel.app/` chunks: all 5 markers — `Test Builder` (c11c5e3), `Recently asked` (ee4b661), `Map to curriculum topic` (fe26852), `Unflag (back to suggested)` (V20), `Place into subject` (placement) |
| `syllabai-teacher-workbench` | `39ad5d833f4e912a2a23a21c289ac8317bf9d86c` | Live behavior matches the readonly-mirror implementation (§8.4) |
| `syllabai` (central) | `2d7a4fe43ebe466f18223c4f171461b42d83343e` + this update | This artifact is the evidence record |

Core commits between the last battery-covered SHA and final main: `4faef96` (V21 learner-memory pipeline), `94af728` (engagement topic titles), `be5221b` (REQUIRES_PREREQUISITE direction), `deb235a` (Test Builder), `26fec63` (NBA policy tests). The battery below therefore covers a deployment that post-dates all V20 fixes and includes the V21/P9 features.

### 8.2 V20 Verify workflow run (durable evidence)

- **Workflow run ID:** `34896406018` — job `104151496506`, workflow_dispatch, `target_count=12`
- **Commit SHA (battery):** `syllabai-web` main `c11c5e37792d7a246286c1f1be3b8dd180300bfe`
- **Backend identity:** `https://syllabai-core.onrender.com` at deployed SHA `26fec63` (§8.1), B0 backend healthy PASS
- **Started / finished:** 2026-09-14T21:01:40Z → 2026-09-14T21:05Z, `completed success`
- **Result:** **VERDICT: GREEN — 55/55 checks passed**
- **Secrets:** PILOT_TEACHER_* used in-workflow only; logs carry statuses, ids, counts — no secret values
- **Verdicts (summary):** B0 healthy; B1a/b teacher login+role; B2a/b bootstrap window closed (available=false, claim 409); B3 teacher→admin 403; B4a/b student registered + student→teacher 403; B5 census; per-paper B6/B11a/B7/B9/B10/B11/B12/B13/B14/B16 as applicable; B17a–e topic mapping; B18 census delta
- **Job log (durable):** committed to the verification workspace; verbatim verdict lines reproduced in §8.3/§8.5

### 8.3 Marking-contract guard — live negative results (11 papers, no mutation)

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

### 8.5 Complete-paper lifecycle + topic mapping (Specimen 2017, run 34896406018)

One complete paper (`23ef5e6e` "Specimen 2017", 9 versions, 9 with schemes) through the full §7 sequence, all PASS:

`B6b answer key visible to teacher (versions=9 withScheme=9) → B7a flag version → B7b batch blocked 409 → B9 paper-validate refused while versions unvalidated 409 → B10 unflag → B11 validate-all → paper VALIDATED (9 versions) → B12a student sees paper VALIDATED → B12b student structured attempt 201 → B13a flag paper → B13b attempt under FLAGGED paper 404 → B13c batch on FLAGGED paper 409 → B14a unflag → SUGGESTED (never straight to VALIDATED) → B14b attempt 201 again → B14c paper restored VALIDATED → B16a attempt on FLAGGED version 404 → B16b attempt on SUGGESTED version 404 → B16c attempt on re-VALIDATED version 201`

Topic mapping (B17, all PASS): `B17a` current mapping readable — anchor row visible (`primary=ING-4CH12CSPECIMEN2017`); `B17b` anchor-as-primary refused 409; `B17c` remap onto real curriculum topic 200; `B17d` re-map onto the SAME node stays 200 (uq_question_topic flush regression `80b1ff8`); `B17e` mapping persisted (`primary=4CH1-1.9`).

### 8.6 Credential state

**UNVERIFIED.** The bootstrap-admin password generated during activation died with the wiped verification sandbox; it was never logged or committed, and no authorized current/recovery path (in-product rotation requires the current password; no Neon DSN is available to the verification environment) exists. Per the mission rule no password was invented, reconstructed, or reset destructively. The rotation **capability** itself is IMPLEMENTED / VERIFIED (core `6ec725c`, plus a live 6/6 rotation exercise on a teacher credential: wrong-current 401 without mutation → correct-current 204 → old password rejected → new accepted, audit-logged). Operator action remains: rotate `admin@syllabai.dev` via an authorized path.

### 8.7 Orphan Vercel project

**REPORTED / UNVERIFIED.** `syllabai.vercel.app` still returns 500 `MIDDLEWARE_INVOCATION_FAILED`; no repo history contains a `middleware.ts`, and its static-asset fingerprint matches neither deployed app. Deletion was NOT performed: platform-side project identity and operator authorization could not be verified from the verification environment. CORS for the canonical apps is already covered by explicit `SYLLABAI_CORS_ORIGINS`, so the orphan is inert but unresolved.

### 8.8 Corpus scope and census

- Scope: Edexcel International GCSE Chemistry **4CH1** past-paper corpus in production Neon (papers ingested through the sanctioned GLM-OCR pipeline, all content SUGGESTED until teacher-validated).
- Census at battery start: **78 SUGGESTED papers / 743 suggested question versions** (queue v2 view; total 4CH1 population = 78 SUGGESTED + 13 previously validated = 91 placed papers).
- Census at battery end: **77 SUGGESTED** (delta = exactly the one complete paper validated this run; the 11 scheme-less papers remained SUGGESTED and unmutated).
- Cumulative dogfood state after this run: 14 papers teacher-validated through the real workflow (3 E2E + ~10 prior dogfood + Specimen 2017), 0 FLAGGED, 0 REJECTED; June-2014 remains in queue awaiting mark-scheme authoring (guard holds it out of learner serving).

**Decision (updated):** the V20 production verification claim is promoted from REPORTED to VERIFIED on the strength of run 34896406018 at the final deployed state, together with the workbench live battery. The Content Package consequence in §4 stands and is exercised next by the bounded real-corpus proof.
