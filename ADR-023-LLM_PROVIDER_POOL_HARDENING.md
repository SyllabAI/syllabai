# ADR-023: LLM provider pool hardening — extend FailoverLlmChain, classify failures, enforce the local daily budget, fail-closed test/live mode

**Status:** Accepted for slices B/C/D/E/G-harness (implementation evidence on main); FreeLLMAPI portion PROPOSED/EXPERIMENTAL
**Date:** 2026-09-17
**Scope:** `syllabai-core` `infrastructure/llm` + test sourceset; research in `PLATFORM_RESEARCH.md`; no retrieval, KG, SpecificationPoint, learner-state, evidence, InterventionRun or CLA semantics touched.

## Context

The 42-section LLM Provider Pool specification (revised execution brief, 2026-09-17) assumed the routing layer might not exist. The repository audit established the opposite: `LlmProvider`, `FailoverLlmChain`, `LlmProviderHealth` (threshold/cooldown/requestsToday), experiment pinning with NO silent failover, `SpringAiChatModelAdapter` (Groq/Gemini/OpenRouter), the admin chain-health endpoint, and Tutor/SmartMark callers all exist and are verified in production. The real gaps were: no structured failure classification (string messages only), `daily-budget-per-provider` configured but never enforced, no mode concept (a test boot with leaked keys could construct real adapters), an observability snapshot too thin for routing diagnosis, and two duplicated hand-written fake providers across test files. The revised brief's premise — extend, do not rewrite — held and is now implemented.

## Accepted

- **Existing boundaries stay.** `LlmProvider` is the port; `FailoverLlmChain` is THE routing abstraction (Groq → Gemini → OpenRouter, §26.1/ADR-009). No new router type exists or is wanted.
- **Structured failure classification at the adapter boundary.** `LlmFailureClass` = RATE_LIMITED, AUTHENTICATION_FAILURE, PROVIDER_UNAVAILABLE, TIMEOUT, BAD_REQUEST, MODEL_NOT_FOUND, INVALID_RESPONSE, UNKNOWN. Assigned ONCE by `LlmProviderFailureClassifier` from SDK exception TYPES and HTTP status codes (the `com.openai.errors` hierarchy for Groq/OpenRouter — verified against openai-java-core 4.49.0; `com.google.genai.errors.ApiException` `code()` for Gemini — verified against google-genai 1.65.0; JDK transport timeouts). Message string-matching (e.g. a "429" substring) is rejected.
- **Configuration-failure suppression.** AUTHENTICATION_FAILURE (dead key) and MODEL_NOT_FOUND (retired model) cannot heal mid-deployment: a SINGLE such failure suppresses future attempts on that provider until the end of the UTC day. Transient classes keep the existing failureThreshold/cooldown semantics. The chain still fails over within the request.
- **Local daily budget enforced.** `syllabai.llm.chain.daily-budget-per-provider` (previously dead config) is enforced through `LlmProviderHealth`: `requestsToday >= budget` makes the provider ineligible until UTC-day rollover; the chain fails over to the next eligible member; a pinned experiment on a budget-exhausted provider fails closed (pins never fail over). Both successful and failed attempts count. This is a configured LOCAL routing guard — it is NOT a claim about any provider's official quota and must never be documented as one.
- **Fail-closed modes.** `syllabai.llm.mode` = production (default) | test | live. TEST mode never constructs real provider adapters — keys present in the environment are ignored with a warning, so no code path can silently spend Groq/Gemini/OpenRouter quota; generation fails loudly. Live-provider tests additionally require `LIVE_LLM_TESTS=explicit` in the test layer. Production depends on no test-only environment variable.
- **One reusable deterministic fake.** `FakeLlmProvider` (test sourceset, NOT a production bean) replaces the duplicated fakes in `FailoverLlmChainTest` and `GroundedTutorGeneratorTest`: deterministic responses, classified failure scripting, queued fail-then-succeed sequences, call recording (count, model, experiment id, sampling options, cross-provider invocation order via a shared list). Prompt TEXT is deliberately not recorded — learner data must not accumulate in fixtures.
- **Additive admin observability.** Chain-health snapshots gain enabled/healthy/coolingDown/dailyBudget/remainingLocalBudget/lastFailureClass/effectiveModel. The enabled=true + configured=false pair is the drift signal (enabled but key missing / suppressed). No keys, authorization material, prompts or learner data in the output.

## Proposed / Experimental

- **FreeLLMAPI** (tashfeenahmed/freellmapi — MIT, self-hosted OpenAI-compatible free-tier aggregator): primary-source research recorded in `PLATFORM_RESEARCH.md`; integration NOT implemented. If ever promoted: through the existing `SpringAiChatModelAdapter` with an OpenAI-compatible base-url, as an OPTIONAL, experiment-pinnable chain member — never canonical, never a dependency of Tutor, CLA, SmartMark, InterventionRun or the learner model. Promotion requires an operated self-hosted instance, live verification, a benchmark through the Slice-G harness, and a fresh ToS review for learner-serving traffic.

## Rejected

- Replacing `FailoverLlmChain` with another router (QuotaAwareLlmRouter, ProviderRouterV2, NewLlmRouter, an aggregator's internal router as the primary layer).
- Making FreeLLMAPI — or any aggregator — the canonical LLM layer.
- Using real providers for ordinary tests; real-provider runs live only behind `LIVE_LLM_TESTS=explicit`.
- Quota circumvention: multiple accounts, credential rotation, artificial account pools, automated account creation. Provider pooling exists ONLY for resilience, controlled experimentation, provider diversity, testing and legitimate configured capacity.
- Classifying failures by parsing exception text.
- Provider-specific educational domain models baked into the routing layer.

## Evidence

- `syllabai-core` commits (2026-09-17, rebased onto session-81/82 main): `b8ce0f4` (feat: classification + budget + mode + observability), `f669330` (test: reusable FakeLlmProvider fixture), `bdc2540` (test: budget/rollover, fail-closed mode, admin-health suites), `8e1d27b` (test: live-gated provider benchmark harness). CI push-trigger repaired server-side (`726867ea6d`).
- Regression on the rebased main (JDK 25, local surefire): **582 tests, 0 failures, 0 errors, 1 skipped** (the live-gated benchmark — skipped by design without `LIVE_LLM_TESTS=explicit`), BUILD SUCCESS. Testcontainers ITs remain Docker/CI-gated by design.
- Slice G benchmark: harness implemented and gated; execution BLOCKED in the authoring environment (no provider credentials). Operator run: `LIVE_LLM_TESTS=explicit SYLLABAI_*_API_KEY=... mvn test -Dtest=LiveProviderBenchmark` → `target/benchmark/benchmark-results.json`.

**Scope guard:** this ADR changes provider-routing mechanics only. It must not alter retrieval, KG, SpecificationPoint, learner-state, evidence, InterventionRun state-machine or CLA pedagogy semantics; any such change stops and re-opens as a separate architecture task.
