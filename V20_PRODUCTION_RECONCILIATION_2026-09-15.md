# V20 Production Reconciliation — 2026-09-15

**Status:** REPORTED / PARTIALLY VERIFIED FROM GIT HISTORY  
**Scope:** reconciliation of the Z.ai V20 production report against the canonical GitHub repositories  
**Important:** this artifact does not promote a reported live result to VERIFIED unless durable repository evidence supports the claim.

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
| Ingestion anchor is visible in teacher question-topic rows | IMPLEMENTED / VERIFIED (code + tests) | Core commit `6ec725c`; live production effect still depends on deployment evidence |
| Self-service password rotation requires current password and logs the event | IMPLEMENTED / VERIFIED (code + tests) | Core commit `6ec725c`; operator credential recovery/rotation completion remains UNVERIFIED |
| Paper cannot become VALIDATED when any version has no mark scheme, unless explicitly forced | IMPLEMENTED / VERIFIED (code + tests) | Core commit `35df8e7`; this closes the learner-servable marking-contract hole |
| V20 teacher-side production battery exists and exercises the intended workflow | IMPLEMENTED / VERIFIED (workflow/code) | Web commit `fe99551`; successful live run result not independently captured here |
| Reported V20 live battery result (103/103, 12-paper dogfood) | REPORTED | Z.ai report; requires durable workflow/run evidence before promotion to VERIFIED |
| Teacher workbench Vercel runtime repair | IMPLEMENTED / VERIFIED (code + local production-build evidence in commit) | Workbench commit `39ad5d8`; live deployment should be rechecked if not backed by a durable run/evidence artifact |
| Bootstrap admin credential recovered/rotated after sandbox loss | UNVERIFIED | No credential is inferred or reconstructed; do not invent or rotate without an authorized current/recovery path |
| Orphan `syllabai.vercel.app` project is safe to delete | REPORTED | Requires operator/platform confirmation before destructive action |

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
