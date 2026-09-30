# T-C23 Option B executed — CURRENT_EMBED_REV rolled 2→1 (serving restoration from the VALIDATED rev1 corpus)

**Date:** 2026-09-25 · **Lane:** serving restoration (session 129) · **Trace:** 1a0d8ab611374a05
**Operator decision (verbatim):** *"I dont want to manually sit and review papers. We have very less time"*
— this answers the T-C23 menu (session 128): Option A (manual validation of rev2 papers) is eliminated by the
first sentence; Option C (wait for R5) is eliminated by the second. The remaining registered lever is **Option B**,
executed here.

## What was done

- **Commit `d523f57`** (syllabai-core, main): `ChunkVectorRepository.CURRENT_EMBED_REV` 2 → 1 + javadoc rewritten
  to record the full flip history, the operator decision, the honest quality trade-off, and the revert condition.
  Diff verbatim: `d523f57.diff` in this directory.
- **Why this is the designed lever:** V33's own migration comment says "Reads filter
  `embed_rev = ChunkVectorRepository.CURRENT_EMBED_REV` … Rollback = flip the constant back." The javadoc of the
  constant records the 09-20 flip to 2 (eval-gated) and always stated rollback as a one-constant operation.
- **Purely additive:** the rev=2 serving set was EMPTY (that IS the 0-hit anomaly — root-caused in
  `evidence/serving-0hit-anomaly-2026-09-25/REPORT.md`), so rev1 serving cannot displace anything. The T-C20
  VALIDATED-only gate is untouched — only VALIDATED rev1 content (the 4CH1/4CH0 IGCSE practice papers + the
  glmocr-era validated papers) becomes visible. No validation state was asserted, forged, or changed by an agent.

## CI + deploy state

- **core-ci: SUCCESS** — run `36139951583` on `d523f57` (full suite incl. the T-C20/T-C07 serving tests; every
  test references the rev symbolically, verified before the push).
- **Render:** `autoDeploy: true` (render.yaml line 25) should have built and deployed `d523f57` automatically.
  As of **13:54Z** (~38 min after push) the production search endpoint still behaves like the OLD build
  (200 + 0 hits on every probe; the sandbox has no Render API/dashboard access, so the deploy could be queued,
  building, or failed — ONE dashboard check on Deployments for `d523f57` settles it).

## Verification probe (expected signal when the new build is live)

`scripts/verify_serving_restore.py` (sandbox scripts dir, READ-ONLY): teacher login → 5 IGCSE-chemistry queries
against `GET /api/v1/teacher/content/documents/search?limit=5&query=…`. Latest output: `probe_result_1354Z.json`.

- Expected when live: **hits > 0**, documentIds resolving to the VALIDATED rev1 papers' QP/MS documents
  (`1dc68349…`, `e9cb4e28…`, `b7849fb8…`, `48500b4f…`, `0ebc841c…`, `edaf179c…`, `476c5950…`, `144da9ac…` and the
  glmocr-era set). Note `searchServingEligible` has NO score floor — once any VALIDATED rev1 chunk is eligible
  (≈2,333 chunks are), top-k returns rows, so "0 hits" after deploy would be genuinely impossible absent a
  resolver refusal (unchanged since probe 1 of the root-cause report).
- Probe timeline: 13:26Z / 13:31Z / 13:37Z / 13:44Z / 13:54Z — all 0 hits (old build still live).

## Honest trade-off (on the record)

rev1 retrieval measured **0/9 hit@10 vs rev2 9/9** on the frozen gold subset (the eval gates that justified the
09-20 cut-over). This rollback knowingly serves the weaker corpus — the operator chose availability-now over
retrieval quality, with zero manual review. The lexical arm (BM25 over tsvector) is model-independent, so keyword
grounding quality degrades far less than the vector numbers suggest. This posture is **interim**: the moment any
rev2-era paper is teacher-validated (the §7 designed path, no code change needed to benefit — everything is
already embedded), flip the constant back to 2 and serving upgrades instantly; rev1 retirement stays gated at R5.

## Revert / upgrade path

- **Upgrade to rev2 serving:** validate rev2-era papers (operator/teacher action, workbench or
  `POST /exam-papers/{id}/validate-all`), then one commit flipping `CURRENT_EMBED_REV` back to 2.
- **Roll back the rollback:** flip the constant to 2 (restores the exact pre-d523f57 behavior).

## Boundary discipline

Read-only probes throughout (teacher-credential surfaces, sanctioned reads only); the ONE change is a
main-branch code commit through the house hotfix pattern (same shape as cd7e429/4646d4c/20d7ff1), CI-gated.
No content validated by an agent; no gate/threshold/κ semantic touched; no DB writes; no credentials printed
(teacher credential rotation still standing).
