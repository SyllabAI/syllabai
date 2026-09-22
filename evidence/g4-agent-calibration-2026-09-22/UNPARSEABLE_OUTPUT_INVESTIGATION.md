# Investigation — the single `UNPARSEABLE_OUTPUT` (session 116 re-audit, 2026-09-22)

Written after the round, from the frozen artifacts plus the canonical code at
core `ad44cee` (deployed 1.2.0 line) and `e7a55fe` (convention-pin tests).
Additive to the frozen evidence; no data file in this directory is modified.

## 1. The observed row

`sme-eq-1-6-ionic-bonding-q7|b` — attempt `7ad844d9-dd03-43e1-8fed-cf99abc27494`,
question `3a79aa09-d4fc-49dd-b386-a21f25164cd2`, partId `2fc44070-…`:

```
marksPossible 5, marksAwarded 0, markingState PENDING,
validationPassed false, failureReason UNPARSEABLE_OUTPUT,
breakdown [], modelId null, confidence null
```

The only failure among the 26 parts; its κ pair was dropped (n=25, not 26)
per the documented pairing rule. The answer honestly stayed PENDING — no
marks, no evidence, no retry.

## 2. Code-path facts (what the failure row can and cannot tell us)

- `LlmMarkingCandidateGenerator.parse` raises `UNPARSEABLE_OUTPUT` at exactly
  three sites: null output; no `{…}` object found in the raw text
  (`extractJsonBody`); JSON that fails `readTree`; plus a missing/ non-array
  `allocations` field. All carry a descriptive message — but:
- `SmartMarkPipeline.run` maps any `CandidateGenerationException` to
  `Decision.rejected(e.reason().name(), null)` — the **candidate is null**, so
  `candidateRawOutput` persists **no raw model output** on this path. The
  response row can only ever carry the enum; the message and the raw text
  existed only in the Render server log line
  `candidate generation failed: <message> (UNPARSEABLE_OUTPUT)`.
- The adapter (`SpringAiChatModelAdapter`) has **no finish-reason awareness**:
  a provider completion truncated at the token cap returns HTTP 200 and its
  (possibly empty or cut) text flows on as a success. The failover chain
  (`FailoverLlmChain`) switches providers on exceptions only — a
  content-level failure is never failed over.
- Forensic recovery is therefore **operator-gated**: Render logs for the
  attempt timestamp, and/or the `smart_mark_results` row in the production DB
  (`failure_reason='UNPARSEABLE_OUTPUT'`, expected `raw_output IS NULL`,
  `model_id IS NULL` — confirming the candidate never parsed).

## 3. Mechanism analysis (most probable root cause)

The marking call pins `maxTokens = 800`
(`LlmMarkingCandidateGenerator.propose` → `LlmRequest.withOptions(…, 0.1, 800)`,
unchanged from prompt v2 through v3). The deployed model, `openai/gpt-oss-120b`
(Groq, OpenAI-compatible path), is a **reasoning model**: reasoning tokens
share the completion budget with the visible JSON.

Under pipeline **1.2.0 / prompt v3** the marking task per point grew: assess
every sub-point of a compound point independently and return `marksAwarded`
(0..N) plus a rationale that names which sub-points were earned/missed.
`q7|b` was the round's reasoning-heaviest judgment:

- the **only 5-mark part** in the sample (a compound "explain why" point
  bundling five sub-items);
- the **largest single scheme-point text** of the round (1,512 chars — five
  sub-bullets with allow / not-allow negation rules plus five guidance
  bullets that the model must respect while judging);
- rank 3 of 26 by total input size (1,853 chars) — the two LARGER inputs
  (`q10|b` 2,153, `q5|a` 1,885) both succeeded, so this is **not** a
  deterministic input-size threshold. At temperature 0.1 the reasoning length
  varies stochastically; the heaviest judgment is the likeliest to push
  reasoning + JSON past the 800-token cap, yielding an empty, brace-less, or
  truncated `allocations` payload → the parse refusal.

This mechanism is consistent with every observed fact (HTTP 200 at the
transport level, `modelId null`, empty breakdown, fail-closed PENDING row).
It cannot be confirmed to certainty from the artifacts because the raw output
was not persisted (§2) — the Render log for the request timestamp is the
decisive record and is operator-accessible.

## 4. What it is NOT

- Not a validator rejection — that path is `VALIDATION_FAILED: …` and retains
  the candidate (and raw output) for audit.
- Not a provider outage (`PROVIDER_UNAVAILABLE`) or an availability event —
  the other 25 parts and both feedback generations around it succeeded.
- Not a scheme problem — the scheme was VALIDATED and served (G-2 honored).
- Not a correctness event: the pipeline refused to guess, which is the
  designed behavior. No mark, no evidence, no authoritative claim.

## 5. Impact

One part of 26 (≈4% of the sample); κ sample n=25 instead of 26. No effect on
the correctness of any measured pair. The README's "longest part" phrasing is
imprecise (see `CORRECTIONS_2026-09-22.md` §3): the failing part is the
reasoning-heaviest compound point, not the longest input.

## 6. Recommendation (RECORDED, NOT IMPLEMENTED)

Deliberately **no code change ships with this investigation**: the round is
handed to the operator and any pipeline change now would alter the surface the
human reference round calibrates against. Recorded for the candidate-generation
follow-up (README finding 3's watch item):

1. **Budget:** raise the marking call's completion cap (800 → ~2,000) or scale
   it with the point count/sub-item count; the JSON payload for a 5-sub-item
   compound point plus reasoning does not comfortably fit 800.
2. **Observability:** surface `finish_reason` at the adapter boundary; map a
   `length`-truncated completion to a distinct failure code (e.g.
   `TRUNCATED_OUTPUT`) instead of the generic parse refusal, and persist the
   truncated raw output so failures are self-forensic.
3. **Trigger:** implement 1–2 if the operator's human round (or any later
   round) shows a second refusal clustering on compound parts.

## 7. Verification pointers

- `LlmMarkingCandidateGenerator` (propose/parse/extractJsonBody, 800 cap,
  prompt v3): core `ad44cee`, `src/main/java/com/syllabai/smartmark/`.
- `SmartMarkPipeline.run` exception mapping (`Decision.rejected(reason, null)`):
  same tree.
- `SpringAiChatModelAdapter.generate/extractText` (no finish-reason check):
  `src/main/java/com/syllabai/infrastructure/llm/`.
- Captured failure row: `smart_results.json` (attempt `7ad844d9…`) and
  `release_state_per_part.json` (partId `2fc44070…`) in this directory.
