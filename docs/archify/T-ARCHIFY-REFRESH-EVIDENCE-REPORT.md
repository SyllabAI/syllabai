# T-ARCHIFY-REFRESH — Evidence Report (2026-10-02)

**Commission:** operator, "Update archify diagrams" (trace `1a0f8e77cd478f29`).
**Scope:** refresh all five source-backed diagrams to the current canonical state —
new `syllabai-core` pin, drifted line anchors re-verified, semantic drift from the
upstream core commits folded into the honest-status layer, Quiet Green re-applied.

## 1. What drove the refresh — including a mid-lane overtake

The five diagrams were pinned at `syllabai-core @ 14b5e3d` (2026-09-21/22). While
this lane was in flight, the concurrent operator lane landed heavily upstream;
the refresh therefore happened in TWO passes and the final pin is the true
current core main:

- **Pass 1** re-pinned to `5e4d155` (the clone's then-HEAD, 97 commits / 66
  first-parent past the diagrams' pin).
- **Pass 2** re-pinned to **`9385011`** (true `origin/main`, 69 commits further)
  after the merge reconciliation surfaced the concurrent lane's results, which
  overtook two facts pass 1 had just written:

1. **κ release gate — G-4 is CLOSED.** Incoming Session 118 (2026-09-24)
   records the operator's genuine human reference round executed end-to-end:
   blind packet → 26/26 human marks → smart-mark batch 26/26 SKIPPED
   (idempotent) → gate row **κ=1.0, observed 1.0, n=113, threshold 0.60,
   PASSED**, persisted and read back; the PASSED row supersedes the unvouchable
   pre-existing one; Step-4 probe returned `authoritative=true`. Pass 1's
   "gate OPEN on an unvouchable row (session 117)" text was already history —
   the diagrams now state the human-backed release honestly.
2. **Embed-rev state — rev1 rollback superseded.** `CURRENT_EMBED_REV` is back
   at **2** at the pin, and the 2026-10-02 wave-1 production record shows the
   QP/MS corpus VALIDATED and serving at rev2 (T-C23 Option B's rev1 rollback
   superseded; the T-C23 trap cannot fire). The "VALIDATED rev1 embed" line
   written in pass 1 was replaced; the pgvector lanes' `PREPARED · UNVERIFIED`
   tags became `IMPLEMENTED · rev2 serving`.

Other drift folded in (both passes): deterministic paper-question resolver +
fail-open guard (second deterministic refusal class; D2 telemetry separates
`deterministic-paper-refusal` from `deterministic-refusal`), §22 session store +
working memory (s139) + cross-session episodic digest (s140), per-kind RRF
weights reaching serving fusion, prompt v3/v4, marking pipeline **1.2.1**
(partial marks within compound points, scaled completion budget,
`TRUNCATED_OUTPUT` self-forensic refusals with persisted raw output), G-5 opt-in
marking-queue pagination, V53 **per-course scope resolution (ADR-030)**, the
09-28 deep-audit security wave (boundary rate limiting — auth tier per client
IP, LLM tier per learner — per-target-account login budgets), `prompt v2` →
`prompt v3` on the marking→LLM edge.

Verified-unchanged (kept): cross-repo pins (web `bfc9850`, workbench `39ad5d8`,
parser `eef89fb` tc17-work, pastpapers `6354773` — still the clone heads),
BM25/fabric non-serving, Gemini File Search stub, **cosine floor 0.15** (the
T-C42 0.50 flip is PR #44, unmerged at the pin), `rules-v0.2`,
`nba-rules/v1.3`, V13/V15/V33 bridge invariants, no automatic producer for the
intervention run ledger.

## 2. Pin bump + evidence re-verification

`meta.repository.revision` → `93850118819053a8a7404902d5a7a83ab09d0dbd` in all
five IRs. Every one of the 60 `sources[]` refs was audited against the pin
(`git show <pin>:<path>` — file exists, range in bounds, cited content still
supports its label). Across both passes 21 anchors were re-anchored where code
growth moved them (class/method declarations; the KaRag pipeline contract
javadoc moved to lines 25-26; the guard+gate range now 512-521). All five IRs
**validate PASS** at the pin with 0 errors / 0 warnings (Archify verifies blobs
at the pinned revision, not the working tree).

## 3. Toolchain note — Archify skill v2.17 → v3.0

The sandbox reset had wiped the skill install; the documented `npx skills add
tt-a1i/archify -g` re-install delivered **Archify v3.0** (was 2.17). Handled:

- v3 requires `meta.output` (added: `docs/archify/<name>.html` — this lane keeps
  the repo-root delivery layout, not the per-request `.archify/<folder>`
  convention; the regeneration workflow stays `finalize →
  apply_quiet_green.py → committed artifact`).
- v3 `finalize` = validate → deliver → strict check → **real-browser
  browser-check**. All five: validate/deliver/check **pass**; browser-check
  failed environmentally (§6).
- v3 renders the IRs' `connections[]` as labeled edges + SRC chips — a renderer
  upgrade; layouts re-solved automatically, containment re-proven.

## 4. Per-diagram changes (final state)

| Diagram | Semantic edits |
|---|---|
| overview | api_core `· rate-limited` + RateLimitFilter ref; tutor sublabel → `fusion · memory · paper anchors`; κ tag `gate closed` → `fail-closed` + gates-card: **G-4 human round κ=1.0 PASSED**; pgvector lane → `IMPLEMENTED · rev2 serving` + wave-1 line; security-wave card line; cross-repo card self-pin → `syllabai @ f1a7eb2 (main)`; proposed-view note updated (≤140 chars) |
| learning-loop | region + card pin → `9385011`; κ tag → `fail-closed`; κ card: **G-4 human round κ=1.0 (n=113) PASSED**, superseding the n=25 agent calibration; tutor API / evidence / scope anchors re-anchored |
| retrieval | region/card pin; `ask()` re-anchored (session-anchored ask) + PaperQuestionResolver ref; sufficiency → `empty / unanchored ⇒ refusal` + guard+gate range (512-521); fusion → `per-kind weights` + PLAN_V2_WEIGHTS ref; selection → `briefs + session memory` + ContextAssembler.TutorContext ref; scope → `per-course · fail-closed (T-C07)` + `resolveForCourse` (ADR-030); not-serving card: rev2 serving supersedes the rev1 rollback; truth-boundaries card: fail-open guard/D2 + s140 digest lines; sources card → new pin + contract lines 25-26 |
| assessment-marking | region/card pin; smartmark → `pipeline 1.2.1 · partial marks` + SmartMarkResult ref; queue/API re-anchored (queue-v2, batch, paginated markingQueue, smartMarkBatch); chain.generate re-anchored; V34 card: first real κ (agent n=25 → **human round κ=1.0 n=113 PASSED**) + refusal family (UNPARSEABLE_OUTPUT / TRUNCATED_OUTPUT, persisted raw output); `prompt v3` on the smartmark→llm edge + view note |
| ingestion | region/card pin; SME anchors re-anchored (ingest L139, schemes-VALIDATED contract L53, QuestionSpecPoint L272); /embed → L101; embedding lane → `IMPLEMENTED · rev2 serving`; paused-card: Embedding v2 wait resolved, rev2 validated + serving in production, remaining SUGGESTED surface is the non-QP/MS axes |

## 5. Delivery receipts (finalize, v3.0, final attempts)

| Diagram | quality | spec sha256 | artifact (delivered) | gates |
|---|---|---|---|---|
| overview | standard | `07f03dc3da78…` | `f72f47d3d417…` 819,489 B | validate/deliver/check pass |
| learning-loop | showcase | `e0585446f861…` | `059e4ecd23b8…` 776,782 B | validate/deliver/check pass |
| retrieval | showcase | `ca8b02cb599d…` | `f6e2a1002bc4…` 778,691 B | validate/deliver/check pass |
| assessment | showcase | `a6e0f430280e…` | `03ffbe58775f…` 780,073 B | validate/deliver/check pass |
| ingestion | showcase | `7a2449a2797a…` | `a90ecd3ae795…` 780,344 B | validate/deliver/check pass |

All specs: 0 errors, 0 warnings. Per-artifact sidecars (`*.finalize.json`,
`*.finalize-summary.json`, `*.delivery.json`, `*.browser-check.json`) committed
beside the artifacts.

## 6. Browser evidence — honest record

The packaged `browser-check` (DevTools transport) **could not complete** in this
sandbox: `Runtime.evaluate` timed out after 15000 ms on every artifact (plus one
`net::ERR_FAILED` navigation) — the same environmental failure recorded in §5/§8
for prior rounds; receipts committed with status `fail`, retried standalone and
on post-QG copies (`tools/qg-browser-check/`). With a delivery sidecar present,
v3 refuses to inspect bytes that differ from the delivered artifact — the QG
post-processor sits outside Archify's provenance chain by design, so the
committed (post-QG) bytes cannot pass the packaged gate; recorded as a pipeline
property, not normalized away.

Manual Playwright evidence (the established fallback, both scripts committed):

- `tools/visual_evidence_quiet_green.py` → **5/5 PASS** — QG cascade proofs
  (tokens + fonts via computed styles), horizontal containment EXACT at
  1440/1600/1920/2048 both themes, 7/7 IR-derived needle labels per artifact;
  12 screenshots regenerated (`tools/quiet-green-evidence/`).
- `tools/visual_evidence_refresh.py` (NEW) → **5/5 PASS** — every new fact
  verified (pin strings, G-4 κ=1.0 PASSED lines, rate-limit sublabel, rev2
  serving lines, per-course scope, pipeline-1.2.1/G-5 anchors, source-ref
  paths): DOM check for visible text, artifact-bytes check for interactive
  SRC-layer refs; 4-viewport horizontal containment exact;
  SHA-256-bound to the committed artifacts
  (`tools/refresh-manual-browser-evidence.json`).

## 7. Quiet Green re-application

`tools/apply_quiet_green.py` re-applied to all five final deliveries
(deterministic, marker-wrapped, byte-stable on re-run — verified). The v3
template carries the same token vocabulary the QG layer targets. Committed
artifact SHAs (post-QG): overview `21f94417f52a…`, learning-loop `f07d5af58bda…`,
retrieval `edc8154e38d2…`, assessment `28e00d9b0043…`, ingestion `32f25e6d78d5…`
— the SHA bindings in `refresh-manual-browser-evidence.json` match exactly.

## 8. Perceptual review

All five artifacts inspected as rendered captures across both themes (overview
light+dark, learning-loop light, retrieval light+dark, assessment dark+light,
ingestion dark): regions, nodes, status chips, SRC chips, labeled edges, guided
views and conclusion cards all render; the new facts are legible on-canvas (κ
gate red/fail-closed, `rate-limited` API, `pipeline 1.2.1 · partial marks`,
`prompt v3`, `empty / unanchored ⇒ refusal`, `RRF k=60 · per-kind weights`,
`briefs + session memory`, `per-course · fail-closed (T-C07)`,
`pinned at 9385011`). Defects found and fixed during review across the rounds:
a stale `prompt v2` edge label, a 140-char view-note overflow, a 3-source node
cap overflow, and a sublabel width violation.

## 9. Honest limits

- The packaged browser gate remains environmentally unavailable in this sandbox;
  its receipts record `fail` — the automated browser_evidence status for this
  round is **failed (environmental)**, not skipped and not passed.
- The QG layer keeps delivery provenance intentionally stale (pre-QG sha in
  `*.delivery.json`); committed bytes are bound by the finalize + refresh
  evidence receipts instead.
- The gate's PASSED row is the concurrent lane's committed record (incoming
  Session 118 + Step-4 probe); this lane cites it rather than re-measuring it.
- The cosine-floor text stays 0.15 — the T-C42 0.50 flip is PR #44, unmerged at
  the pin; when it merges, that one sublabel changes with it.
- No new subsystem NODES were added (session store, resolver, rate limiter are
  carried as facts/refs on existing nodes and in cards) — node counts and
  layouts are unchanged by design.
- Tracker note: the concurrent lane had consumed session numbers through 136;
  this lane's record is **Session 137** in WORKLOG.md (PROGRESS.md per-session
  sections end at 129 by its own header note).
## 10. Post-pin update — 2026-10-02: the scheduled T-C42 floor sublabel (check + flip)

- Core PR #44 (`t-c42-min-cosine-050-flip` @ `8dc315a`) MERGED as `5ef132b`
  (merge-commit method after the concurrent PR #43 lane; PR-head full-suite
  CI green `36919822481`, merge-commit CI green `36921164632`) — the flip
  deferred at §9 is on core main, so the scheduled change is applied here.
- Applied change, exactly as scoped at §9: the Semantic-vector-leg sublabel
  `pgvector · cosine floor 0.15` → `pgvector · cosine floor 0.50` in
  `syllabai-retrieval-architecture.archify.json` (`/components[3]`) and its 4
  mirrored strings in the rendered HTML (aria-label, `data-node-sublabel`,
  `<title>`, context text). No other diagram content moved. Byte-count
  asserted (1 + 4), JSON re-parsed, zero `0.15` floor residuals.
- State note: the content pin stays `9385011`
  (`meta.repository.revision`) and the node's source line-refs stay
  9385011-accurate; the floor TEXT alone reflects core main @ `5ef132b`,
  where `MIN_COSINE = 0.50` sits at `ContentVectorRetriever.java:52`
  (candidacy filter at `:68`) after the T-C42 javadoc expansion — reconcile
  line-refs at the next re-pin.
- Flip gates re-verified from the committed records during this check (not
  re-run): gate 1 `run-005-c-r8` — recall r7→r8 byte-identical
  (0.0386/0.0515/0.0717), MRR −0.0056 (0.0615→0.0559), nDCG@10 −0.0042
  (0.0913→0.0871), §8(d) 0.5618/0.9167 unchanged, zero-result 0/120, floor
  0.50 declared in the r8 header; gate 2 production probe — 1,745/2,935 =
  59.5% above 0.50 (binding mass rule PASS), peak bucket 0.50–0.55 (1,361),
  zero pool mass below 0.40, buckets sum exactly to 2,935, frozen-vector
  transport deviation recorded + SHA-pinned
  (`ADDENDUM-2026-10-02-production-probe.md`). Post-deploy watch item
  unchanged: tutor retrieval refusal rate at the 0.50 floor.
- Browser receipt: this round the rendered-DOM check RAN (the §9
  environmental failure does not recur here) —
  `tools/t42-flip-manual-browser-evidence.json` PASS (needle 0.50 ×8,
  0.15 ×0, 24 SVG nodes).
