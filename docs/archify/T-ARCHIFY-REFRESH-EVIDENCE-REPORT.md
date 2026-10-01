# T-ARCHIFY-REFRESH — Evidence Report (2026-10-02)

**Commission:** operator, "Update archify diagrams" (trace `1a0f8e77cd478f29`).
**Scope:** refresh all five source-backed diagrams to the current canonical state —
new `syllabai-core` pin, drifted line anchors re-verified, semantic drift from 97
upstream core commits folded into the honest-status layer, Quiet Green re-applied.

## 1. What drove the refresh

The five diagrams were pinned at `syllabai-core @ 14b5e3d` (2026-09-21/22). Core
main has since moved **97 commits** (66 first-parent) to `5e4d155`, including
material architecture change:

- **κ release gate live state** — sessions 115–117 (canonical tracker): agent
  calibration measured the first real κ (n=25, any-credit convention pinned in
  core `e7a55fe`); a passed κ evaluation row of unknowable provenance was
  live-verified holding the release gate OPEN (session 117, keep-and-document);
  the operator's genuine human round (G-4) supersedes. Every diagram said
  "gate closed" — now honestly re-stated (code semantics unchanged, live state
  recorded).
- **Retrieval/tutor** — deterministic paper-question resolver + fail-open guard
  (second deterministic refusal class; D2 telemetry separates
  `deterministic-paper-refusal` from `deterministic-refusal`), §22 session store
  + working memory (s139) + cross-session episodic digest (s140), per-kind RRF
  weights reaching serving fusion, prompt v3/v4, untrusted prompt-block fencing,
  CURRENT_EMBED_REV rolled back to the VALIDATED rev1 corpus (T-C23 Option B).
- **Assessment/marking** — marking pipeline **1.2.1** (partial marks within
  compound points, scaled completion budget, `TRUNCATED_OUTPUT` self-forensic
  refusals with persisted raw output), G-5 opt-in marking-queue pagination,
  prompt v3.
- **Security wave (deep-audit 09-28, R1–R19)** — boundary rate limiting (auth
  tier per client IP, LLM tier per learner), per-target-account login budgets,
  `@PreAuthorize` layer, FK closure, token revocation, content-type allowlist.
- **Verified-unchanged facts** (kept): cross-repo pins (web `bfc9850`, workbench
  `39ad5d8`, parser `eef89fb` tc17-work, pastpapers `6354773` — all still the
  clone heads), BM25/fabric non-serving, Gemini File Search stub, cosine floor
  0.15, `rules-v0.2`, `nba-rules/v1.3`, V13/V15/V33 bridge invariants,
  InterventionRunService having no automatic producer, ingestion paused.

## 2. Pin bump + evidence re-verification

`meta.repository.revision` → `5e4d155f26e2d2bcd02b64799019de46f86fb83a` in all
five IRs. Every one of the 60 `sources[]` refs was audited against the new pin
(`git show <pin>:<path>` — file exists, range in bounds, cited content still
supports its label). 12 anchors had drifted with code growth and were re-anchored
(class/method declarations that moved); new facts carry new refs. All five IRs
**validate PASS** at the new pin (Archify verifies blobs at the revision, not
the working tree).

## 3. Toolchain note — Archify skill v2.17 → v3.0

The sandbox reset had wiped the skill install; the documented `npx skills add
tt-a1i/archify -g` re-install delivered **Archify v3.0** (was 2.17 at the
original delivery). Consequences, handled:

- v3 requires `meta.output` (added: `docs/archify/<name>.html`, matching this
  repo's committed layout — the per-request `.archify/<folder>` convention was
  NOT adopted; this lane's regeneration workflow stays `deliver →
  apply_quiet_green.py → committed artifact`, §9).
- v3 `finalize` = validate → deliver → strict check → **real-browser
  browser-check**. All five: validate/deliver/check **pass**; browser-check
  failed environmentally (below).
- v3 renders the IRs' `connections[]` as labeled edges + SRC chips — a renderer
  upgrade; layouts re-solved automatically, containment re-proven.

## 4. Per-diagram changes (summary)

| Diagram | Semantic edits |
|---|---|
| overview | api_core `· rate-limited` + RateLimitFilter ref; tutor sublabel → `fusion · memory · paper anchors`; κ tag `gate closed` → `fail-closed` + gates-card live-state line + security-wave line; cross-repo card self-pin → `syllabai @ f1a7eb2 (main)`; proposed-view note honest gate state; KaRag/Cla/prompt line anchors |
| learning-loop | region + card pin → `5e4d155`; κ tag → `fail-closed`; κ card records the agent calibration (n=25) and the OPEN live state with operator supersession; tutor API re-anchored (s139 javadoc) |
| retrieval | region/card pin; `ask()` re-anchored (session-anchored ask, L151) + PaperQuestionResolver ref; sufficiency → `empty / unanchored ⇒ refusal` + guard+gate range (L243–252); fusion → `per-kind weights` + PLAN_V2_WEIGHTS ref; selection → `briefs + session memory` + ContextAssembler.TutorContext ref; not-serving card + rev1 pin (T-C23 Option B); truth-boundaries card + fail-open guard/D2 + s140 digest lines; sources card → new pin + contract lines 21-22 |
| assessment-marking | region/card pin; smartmark → `pipeline 1.2.1 · partial marks` + SmartMarkResult ref (3-source cap respected); marking API/queue re-anchored (queue-v2 L204, batch L231, paginated markingQueue L109, smartMarkBatch L340); chain.generate → L80; V34 card: first real κ + OPEN live state + refusal family (UNPARSEABLE_OUTPUT / TRUNCATED_OUTPUT, persisted raw output); smartmark→llm edge + view note → `prompt v3` |
| ingestion | region/card pin; QuestionSpecPoint → L204; /embed → L101 (content unchanged otherwise — verified still accurate) |

## 5. Delivery receipts (finalize, v3.0)

| Diagram | quality | spec sha256 | artifact (delivered) | gates |
|---|---|---|---|---|
| overview | standard | `bab4cff97eb1…` | `e3a30c817fea…` 819,403 B | validate/deliver/check pass |
| learning-loop | showcase | `65e549e85860…` | `273860877653…` 776,794 B | validate/deliver/check pass |
| retrieval | showcase | `d50d9514b8a2…` | `ea5e05629a8b…` 778,648 B | validate/deliver/check pass |
| assessment | showcase | `f9697055d8c4…` | `c941fba1e7d3…` 780,073 B | validate/deliver/check pass |
| ingestion | showcase | `695f24f3558f…` | `97decb988fa6…` 780,232 B | validate/deliver/check pass |

All specs: 0 errors, 0 warnings. Overview/assessment were re-finalized once each
after late text fixes (view-note 140-char limit; `prompt v2` → `prompt v3`
connection label found during perceptual review) — the receipts above are the
final attempts; per-artifact sidecars (`*.finalize.json`,
`*.finalize-summary.json`, `*.delivery.json`, `*.browser-check.json`) are
committed beside the artifacts.

## 6. Browser evidence — honest record

The packaged `browser-check` (DevTools transport) **could not complete** in this
sandbox: `Runtime.evaluate` timed out after 15000 ms on every artifact (plus one
`net::ERR_FAILED` navigation) — the same environmental failure recorded in §5/§8
of this document for prior rounds. Retried standalone per the contract; receipts
committed (`*.browser-check.json`, status `fail`, reason recorded).

Additionally attempted on the post-QG bytes in a sidecar-free copy directory
(`tools/qg-browser-check/` receipts): same environmental timeout. With a
delivery sidecar present, v3 refuses to inspect bytes that differ from the
delivered artifact — so the post-QG committed artifacts cannot pass the packaged
gate while the QG post-processor stays outside Archify's provenance chain. This
is recorded as a pipeline property, not normalized away.

Manual Playwright evidence (the established fallback, both scripts committed):

- `tools/visual_evidence_quiet_green.py` → **5/5 PASS** — QG cascade proofs
  (tokens + fonts via computed styles), horizontal containment EXACT at
  1440/1600/1920/2048 both themes, 7/7 IR-derived needle labels per artifact;
  12 screenshots regenerated (`tools/quiet-green-evidence/`).
- `tools/visual_evidence_refresh.py` (NEW, this round) → **5/5 PASS** —
  refresh-specific: every new fact (pin strings, κ live-state lines, rate-limit
  sublabel, refusal-family card text, G-5/pipeline-1.2.1 anchors, source-ref
  paths) verified present; DOM check for visible text, artifact-bytes check for
  interactive SRC-layer refs (same method as the committed needle check); 4-viewport
  horizontal containment exact. SHA-256-bound to the committed artifacts
  (`tools/refresh-manual-browser-evidence.json`).

## 7. Quiet Green re-application

`tools/apply_quiet_green.py` re-applied to all five fresh v3 deliveries
(deterministic, marker-wrapped, byte-stable on re-run — verified). The v3
template carries the same token vocabulary the QG layer targets (verified before
application), so no tool change was needed. Committed artifact SHAs (post-QG):
overview `a74ff926aaf4…`, learning-loop `a0ef08088826…`, retrieval
`3dc52f1525f0…`, assessment `22259832e982…`, ingestion `6446c5e8489d…` — the
SHA bindings in `refresh-manual-browser-evidence.json` match exactly.

## 8. Perceptual review

All five artifacts inspected as rendered captures across both themes (overview
light+dark, learning-loop light, retrieval light, assessment dark+light,
ingestion dark): regions, nodes, status chips, SRC chips, labeled edges, guided
views and conclusion cards all render; the new facts are legible on-canvas (κ
gate red/fail-closed, `rate-limited` API, `pipeline 1.2.1 · partial marks`,
`prompt v3`, `empty / unanchored ⇒ refusal`, `RRF k=60 · per-kind weights`,
`briefs + session memory`, `pinned at 5e4d155`). One defect found and fixed
during review: a stale `prompt v2` edge label on the assessment diagram.

## 9. Honest limits

- The packaged browser gate remains environmentally unavailable in this sandbox;
  its receipts record `fail`, and the automated browser_evidence status for this
  round is **failed (environmental)**, not skipped and not passed.
- The QG layer keeps delivery provenance intentionally stale (pre-QG sha in
  `*.delivery.json`); committed bytes are bound by the finalize + refresh
  evidence receipts instead.
- Live gate state ("OPEN") is a point-in-time operational fact (session 117
  method); the diagrams' code-semantics claims carry the architecture truth and
  the card text dates the observation (2026-10-02).
- No new subsystem NODES were added (session store, resolver, rate limiter are
  carried as facts/refs on existing nodes and in cards) — node counts and
  layouts are unchanged by design; adding nodes is a future authoring decision.
