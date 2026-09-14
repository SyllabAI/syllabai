# SyllabAI AI Runtime and Provider Report

**Date:** 2026-09-14  
**Status:** Current architecture/report  
**Constraint:** $0 / no-credit-card default for Cycle 1

## Executive conclusion

SyllabAI does **not** need one LLM per feature. It needs a provider-neutral AI layer with workload-specific policies.

The current architecture should be:

```text
                    SyllabAI AI layer
                           │
          ┌────────────────┴────────────────┐
          │                                 │
      Generation                         Embeddings
          │                                 │
    LlmProvider                       EmbeddingProvider
          │                                 │
    ┌─────┼─────────────┐                  │
    │     │             │                  │
   Groq  Gemini   OpenRouter/local     Gemini embeddings
    │
    ├── Tutor
    ├── Smart Mark candidate generation
    └── Interaction Evidence extraction
```

Tutor, Smart Mark and interaction analysis may share a model initially, but they are separate workloads with separate prompts, schemas, validators, telemetry and fallback policies.

The model itself is **not** the agent. Agentic capability will come from an application-controlled loop with bounded educational tools, permissions, state and termination rules.

## 1. Current production/runtime position

The recent production debugging established the following operational facts:

- Tutor generation is live through Groq using `openai/gpt-oss-120b`.
- The application now uses provider-specific Spring AI runtime option factories rather than unsafe generic chat options.
- Groq's base URL requires `/v1`.
- Gemini's retired/invalid model references must not be treated as stable provider contracts; model IDs are configuration and must be probed/verified.
- OpenRouter free models are volatile and must be treated as a fallback pool rather than a permanent model identity.
- Embeddings use the Gemini embedding API, currently `gemini-embedding-001` at the SyllabAI 768-dimensional configuration.
- The production code bridges the embedding-key naming mismatch that previously caused embeddings to be silently disabled.
- The live Tutor has been verified to return grounded responses with specification citations and honest refusal outside the educational domain.

These runtime facts are implementation evidence; provider quotas and model catalog entries remain volatile and must be rechecked before deployment changes.

## 2. Workload map

| Workload | Needs generation LLM? | Needs embeddings? | Initial model strategy |
|---|---:|---:|---|
| Tutor answer | Yes | Indirectly, for retrieval | Groq `openai/gpt-oss-120b` primary |
| Smart Mark candidate generation | Yes | No hard requirement | Same provider abstraction; separate marking prompt/schema |
| Interaction Evidence extraction | Yes | Optional | Same provider initially; structured-output workload |
| Learner model / BKT / BDT / decay | No | No | Deterministic/application logic |
| Recommendation scoring | No hard requirement | Optional retrieval support | Existing rule/evidence-based engine |
| Knowledge graph authority | No | No | Canonical database state |
| Educational retrieval | No | Yes | Gemini embedding + lexical/KG/reranking |
| Agent tool orchestration | Model proposes actions | No | Application-controlled runtime |

## 3. Do Tutor and Smart Mark need separate LLMs?

No.

They need separate **workload policies**, not necessarily separate model deployments.

Smart Mark already follows the important architecture of LLM candidate generation plus deterministic validation. The LLM can propose marking interpretations; validators remain responsible for bounds, coverage, mark-sum and other hard constraints.

A separate marking model becomes worthwhile only if measurement shows that:

- marking accuracy needs a specialized model;
- Tutor latency/cost competes with marking throughput;
- structured output reliability differs materially;
- a smaller local model is good enough for marking; or
- provider failures make workload isolation necessary.

Until then, sharing the generation provider reduces operational complexity and keeps Cycle 1 within the free/no-card requirement.

## 4. Embeddings are a separate model class

Yes. Generation and embedding solve different problems.

Generation LLM:

```text
question/context → language output
```

Embedding model:

```text
text → vector representation
```

SyllabAI uses embeddings for semantic retrieval, not for educational truth. Vector similarity must remain subordinate to curriculum anchors, validated resources, KG structure and learner evidence.

Google documents `gemini-embedding-001` as a stable text-embedding model supporting flexible dimensions from 128 to 3072, with 768/1536/3072 recommended. Source: https://ai.google.dev/gemini-api/docs/models/gemini-embedding-001

Google also documents `gemini-embedding-2`, a newer multimodal embedding model supporting text, image, audio, video and PDF inputs. It is a future upgrade candidate, not an automatic Cycle-1 migration. Source: https://ai.google.dev/gemini-api/docs/models/gemini-embedding-2

## 5. Free provider strategy

### Groq — primary generation provider

Groq remains the strongest default for the current no-card pilot because it offers OpenAI-compatible inference and useful free-tier limits. Current Groq documentation lists `openai/gpt-oss-120b` at 30 RPM, 1,000 requests/day, 8K TPM and 200K TPD on the current published table. Limits are model/account dependent and can change. Source: https://console.groq.com/docs/rate-limits

The production system should therefore treat provider limits as runtime state, not as constants in architecture prose.

### Gemini API — fallback / embedding provider

Google's Gemini API remains useful as a second generation provider and as the current embedding provider. Free-tier availability and quotas are volatile, so the application should surface quota/provider failures rather than silently degrading educational functionality.

### OpenRouter — tertiary free generation pool

OpenRouter is useful because it provides an OpenAI-compatible interface and a rotating collection of free models. Current documentation says accounts without purchased credits receive 50 free-model API requests/day; purchasing at least $10 of credits raises the free-model allowance to 1,000/day. OpenRouter explicitly warns that free models have low limits and are usually unsuitable as a sole production dependency. Source: https://openrouter.ai/docs/faq

For SyllabAI's no-card constraint, only the 50/day tier should be assumed. Never architect around the paid $10 allowance.

### Local models

Ollama, llama.cpp, vLLM and LM Studio remain valid zero-API-cost options for development, batch work and eventual workload specialization. They require suitable hardware and therefore are not the default hosted Cycle-1 path.

## 6. Gemini-web2api assessment

`Sophomoresty/gemini-web2api` is technically interesting: it converts Gemini Web into an OpenAI-compatible API, supports streaming/tool-calling patterns and advertises anonymous/free access. The project is MIT licensed. Source: https://github.com/Sophomoresty/gemini-web2api

However, it reverse-engineers Gemini Web rather than using a stable official developer API. Its own README warns about throttling and sustained-use blocking, proxy/network issues and the fact that free-account access does not provide real paid Pro routing. It also simulates multi-turn context by including prior messages in requests. Source: https://github.com/Sophomoresty/gemini-web2api#limitations

**Decision:** do not make Gemini-web2api a production-critical SyllabAI dependency. It can be an experimental/local fallback behind the existing OpenAI-compatible provider abstraction.

## 7. Agentic capability

The Tutor can become agentic without changing the underlying model.

Correct architecture:

```text
LLM
 ↓ proposes
Application policy
 ↓ validates
Educational tool
 ↓ executes
Tool result
 ↓
LLM
 ↓
termination / next step
```

Examples of safe initial tools:

- resolve a SpecificationPoint
- retrieve validated resources
- retrieve learner interaction evidence
- retrieve learner state
- generate a short diagnostic question
- start a practice activity
- inspect the result of a completed practice attempt

The model must not directly:

- edit canonical curriculum nodes;
- change authoritative KG relationships;
- validate assessment content;
- rewrite raw assessment evidence;
- directly set mastery values;
- bypass teacher validation;
- access another student's data.

## 8. AI provider architecture for SyllabAI

The stable boundary should be:

```text
TutorService
SmartMarkService
InteractionEvidenceService
AgentRuntime
       │
       ▼
     LlmProvider
       │
 ┌─────┼─────────────┐
 Groq  Gemini  OpenRouter/local

Retriever / Embedding jobs
       │
       ▼
 EmbeddingProvider
       │
       ▼
 Gemini Embeddings / future local alternative
```

Provider-specific model IDs, URLs, temperature/options and rate-limit behavior belong in provider configuration. Domain services should not depend on provider-specific classes.

## 9. Interaction Memory changes the AI workload map

The new Learner Interaction Memory feature adds a fourth generation workload: **Interaction Evidence extraction**.

It should not be implemented as an always-on expensive call after every token. Prefer analysis at message/turn boundaries and batch/async processing where latency is not user-visible.

A cost-aware policy is:

1. Persist the conversation immediately.
2. Detect obvious deterministic signals first.
3. Run structured LLM extraction only when the turn contains educational substance.
4. Store candidate evidence with model/provider/prompt version.
5. Aggregate evidence asynchronously.
6. Retrieve only relevant patterns into Tutor prompts.

This reduces both cost and noise.

## 10. Current final AI recommendation

```text
Generation primary:
  Groq → openai/gpt-oss-120b

Generation fallback:
  Gemini official API

Generation tertiary:
  OpenRouter free pool

Experimental/local:
  Ollama / llama.cpp / vLLM / LM Studio
  Gemini-web2api only as an experimental provider

Embeddings:
  Gemini embedding API
  Current SyllabAI production target: gemini-embedding-001, 768 dimensions
  Future evaluation: gemini-embedding-2 at 768 dimensions

Smart Mark:
  same generation provider initially, separate marking policy + validators

Interaction Evidence:
  same generation provider initially, separate structured extractor

Agent runtime:
  application-controlled tools, permissions and termination
```

## 11. Operational rule

Provider/model availability is not an architecture invariant. The invariant is the provider abstraction and the safety/grounding contract around it.

When a provider/model disappears:

```text
probe → select compatible replacement → update configuration → run workload tests → verify grounding/structured output → continue
```

Do not redesign SyllabAI merely because a free model was retired.
