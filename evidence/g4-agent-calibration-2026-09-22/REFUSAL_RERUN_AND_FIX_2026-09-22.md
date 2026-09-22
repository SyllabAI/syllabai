# Session 117 — Step 0.3 resolution, refusal re-run, and the deployed fix (2026-09-22)

Additive to the frozen session-115/116 record. Nothing in the frozen files was
modified; `SHA256SUMS` still covers the original nine. This document records the
execution of `HUMAN_CALIBRATION_EXECUTION_PACKAGE_2026-09-22.md` (session 117,
trace `1a0ca34d760cdc31`) as far as it could honestly execute from the sandbox,
and the one engineering fix it triggered. Verbatim probe responses sit in
`probe_2026-09-22_session117/` (checksums in `SHA256SUMS.session117`).

## 1. Step 0.3 — κ-row preflight and its resolution

**What the package prescribed:** `GET /api/v1/teacher/marking/kappa/latest`
(ALL + paper scope) before any marking, then an explicit keep-vs-supersede
decision on any passed row of unvouchable provenance.

**What executed:**

- `POST /api/v1/auth/login` as `pilot.teacher@syllabai-test.dev` → **HTTP 401**
  (`invalid_credentials`). The operator password is not held in this environment
  (re-verified this session; matches session 115's credential audit) and ADR-025
  forbids provisioning any new teacher account. The teacher κ-row read is
  therefore operator-gated, exactly as the package assumed.
- `GET /api/v1/teacher/marking/kappa/latest` without a token → **HTTP 401**,
  documenting the auth wall (`/teacher/**` is TEACHER|ADMIN-gated).
- **Gate-state probe (student surface):** an idempotent Smart Mark re-read on the
  round's own attempt `a4349f23…` (q0, learner `pilot.g4agent`, STUDENT token)
  returned **`authoritative: true` on every part** (verbatim:
  `gate_state_probe_q0_verbatim.txt`). The code chain is byte-unchanged
  (`a86c30d → e7a55fe → d2849fc`; fail-closed `kappaGatePassed`), so
  `authoritative=true` entails: **a passed κ evaluation row exists in production
  NOW (17:49Z 2026-09-22) and the release gate is currently OPEN** — re-confirmed
  live, not just inferred from the round-time captures.

**The recorded resolution (package's decision gate):**

- Provenance of the passing row remains **unvouchable from the sandbox** — the
  row was created operator-side (teacher/admin activity) between 2026-09-16 and
  2026-09-22; nothing here labels it agent work, and nothing here can vouch for
  it either.
- Decision taken: **(a) keep-and-document.** This document is the record. The
  operator's genuine human round — when run — writes a NEWER row that supersedes
  it (newest-by-computedAt); a failing human round re-closes the gate. The open
  gate is NOT treated as G-4 verification: ADR-025/027 require the human
  reference round, which remains the only action that can produce a valid
  release-gate row.

## 2. The refusal re-run — the investigation's trigger FIRED

The package's Step 2 notes the refused part (`q7|b`, attempt `7ad844d9…`,
partId `2fc44070…`) has no validation-passed result, so a batch re-run genuinely
re-executes it. The same re-run was performed now (idempotent re-run; the 25
marked parts came back untouched):

**Result: the refusal REPRODUCED.** `q7|b` again returned
`UNPARSEABLE_OUTPUT`, `validationPassed=false`, `modelId=null`, empty breakdown,
answer honestly PENDING (verbatim: `refusal_rerun_q7_pre_fix_verbatim.txt`).

This is the **second independent refusal on the same compound part** —
`UNPARSEABLE_OUTPUT_INVESTIGATION.md` §6's recorded trigger ("implement the
budget/observability items if any later round shows a second refusal clustering
on compound parts") FIRED. It also sharpens the mechanism finding: two
deterministic refusals at temperature 0.1 on identical input make the
"stochastic reasoning overflow" reading less likely than a **hard budget
overflow** — the flat 800-token completion cap cannot fit this point's reasoning
plus its JSON payload, reliably.

## 3. The fix (core `d2849fc`, deployed via auto-deploy)

Executed under the operator's standing fix-authorization. Scope discipline:
**κ pairing (`KappaAgreementService`), `evaluateAgreement` pairing, the 0.60
threshold, G-2 VALIDATED-only selection, and all gate semantics are untouched.**
Changed:

1. **Scaled completion budget** (`LlmMarkingCandidateGenerator`): the marking
   call's cap now scales with the in-scope point marks — 800 base + 400 per
   mark, capped at 4,000 (the refused 5-mark point gets 2,800; 1-mark points
   get 1,200). The reasoning model's shared budget can no longer starve the
   heaviest compound points.
2. **Truncation observability**: the adapter surfaces the provider finish
   reason (`LlmResponse.finishReason`); a `length`/`max_tokens` completion now
   refuses as **`TRUNCATED_OUTPUT`** carrying the verbatim raw text, instead of
   a generic `UNPARSEABLE_OUTPUT` with no forensic trace.
3. **Self-forensic refusal rows**: `CandidateGenerationException` carries the
   raw output where one exists; `SmartMarkPipeline` persists it on refused
   decisions — failure rows explain themselves without Render log access.
4. **Regression tests** (9 new assertions across
   `LlmMarkingCandidateGeneratorTest` + `SmartMarkPipelineTest`): budget
   scaling + the request actually carries it; truncated refusal mapping;
   `stop`-finished completions parse normally; raw-output persistence both
   when present and absent.

Merge `d2849fc` reconciled origin `10edc84` (assessment lane, zero file
overlap). CI owns the green; production verification below.

## 4. Post-deploy verification of the refused part

Recorded in `verification_q7_post_fix_verbatim.txt` (this directory) after the
Render deploy of `d2849fc`:

<!-- SESSION-117-VERIFICATION-RESULT -->

**PASSED — the part now parses.** After the Render deploy of `d2849fc`, the same
idempotent re-run returned `q7|b` as `SMART_MARKED`, `marksAwarded 3/5`
(partial credit across the compound point's sub-items),
`validationPassed=true`, `failureReason=null`, `modelId=openai/gpt-oss-120b`,
`confidence=0.92`, `authoritative=true` — with a v3-shaped per-sub-point
rationale naming which sub-items earned and missed. Same model, same prompt v3,
same answer text; only the completion budget changed. This confirms:

1. the deployed build is post-fix (the pre-fix build refused this input
   deterministically twice);
2. the root cause was token-budget starvation of the reasoning model's shared
   completion budget, not a prompt/parsing/model defect;
3. the calibration sample is now **26/26 validation-passed** (was 25) — the
   operator's human round can pair all 26 parts.

`q7|b`'s AI mark was written while the gate is OPEN (authoritative=true), under
the same conditions as the round's other 25 parts; its provenance is
AGENT-surface pipeline output on an agent-authored test answer, unchanged.
Follow-up commit `1e47696` stamps post-fix run rows `pipeline 1.2.1`.

## 5. What the human round still owns

Everything in the package's Steps 1–3 that requires the operator's teacher
credentials is UNEXECUTED and cannot be executed from this environment:

- No human/teacher per-point decision was written anywhere (the production
  HumanMark store is untouched; every decision in this whole lane remains
  AGENT_MARKING).
- No teacher-surface Smart Mark batch was run; no κ evaluation row was written
  or superseded by this session.
- The gate stays as found: OPEN on a passed row of unvouchable provenance,
  pending the operator's genuine human reference round (Steps 0.4–3 of the
  package, ~30–60 min) — which supersedes the row either way.
