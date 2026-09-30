# SyllabAI Local Intelligence Layer

**Status:** PROPOSED — architecture/research direction; not a production commitment.
**Research date:** 2026-09-17
**Scope:** Browser-local intelligence for the SyllabAI website, with emphasis on mobile browsers, low/mid-range devices, fast perceived performance, bounded tool use, Knowledge Graph navigation, learner-state-aware actions, and escalation to server/large-model paths.
**Primary artifact:** This document is the durable research and architecture record for the Local Intelligence Layer discussion.

## 1. Executive summary

SyllabAI should investigate a **Local Intelligence Layer** that makes the website locally agentic without making browser LLM inference a prerequisite for using SyllabAI.

> A very small local model acts as a language-to-action controller over SyllabAI's existing semantic application surface. SyllabAI remains authoritative for curriculum, Knowledge Graph semantics, learner state, evidence, assessment, recommendations and educational responses.

The proposed architecture is deliberately different from a local chatbot:

```text
Learner language / UI context
          ↓
Local AI Controller (optional)
          ↓
SyllabAI semantic tools
          ↓
SyllabAI deterministic services
          ↓
KG / curriculum / learner state / evidence / retrieval
          ↓
Large Tutor AI only when the task requires it
```

The local controller should understand current page/resource/question context; classify intent; resolve natural-language requests into SyllabAI tools; navigate semantically; search curriculum and SpecificationPoints; traverse the authoritative KG through read-only APIs; retrieve learner-state summaries and learning evidence; find revision notes and exam questions; start governed learning actions; and route complex requests to server/large-model paths.

It must **not** directly mutate canonical educational truth, mastery, the authoritative KG, assessment semantics, or learner state.

**Current architectural position: PROPOSED — focused benchmark/research spike warranted.** No local model is currently accepted as a production default.

## 2. Why this fits SyllabAI

SyllabAI already connects:

```text
official curriculum
      ↓
validated educational content
      ↓
knowledge graph
      ↓
learner state
      ↓
learning evidence
      ↓
diagnosis
      ↓
targeted intervention
      ↓
assessment
      ↓
learner update
      ↓
next best action
```

The website already contains structured objects a local agent can operate over: subject/qualification context, curriculum/specification version, SpecificationPoints, Revision Notes, Exam Questions, Past Papers, KG concepts/relationships, learner summaries, learning evidence, review state, recommendations, Smart Mark results, practice/intervention flows and Tutor context.

The local model does not need to recreate this intelligence. It needs to **operate it**. This can make ordinary interactions feel like application behavior rather than waiting for a general-purpose AI model.

## 3. Hard product constraint: mobile browser speed

SyllabAI will be used through mobile browsers, including devices without high-performance GPUs. Therefore local LLM inference must not be a prerequisite.

> **SyllabAI should feel fast and snappy even when local model inference is unavailable. Local intelligence is an optional accelerator, not a prerequisite.**

Do not design the core experience around downloading a 300M–3B model, initializing WebGPU, waiting for warm-up, then using the application. This creates first-use latency, storage/network cost, hardware variability and battery pressure.

WebLLM is a useful optional high-capability path: its official project provides browser-local WebGPU inference and an OpenAI-compatible interface. It should not be the baseline for SyllabAI's broad mobile audience. citeturn0search8

**Proposed principle:**

```text
Fast deterministic website
        ↓
optional tiny local controller
        ↓
server/controller fallback
        ↓
large Tutor only for deep work
```

## 4. Candidate model research

### 4.1 Needle 2 — primary research candidate

Cactus currently describes Needle 2 as an open **45M-parameter** model for tool calling, device use and structured extraction. The official repository describes a single **14 MB** binary and approximately **28 MB RAM** for a full session. Its output is schema-constrained structured tool calls rather than general free-form chat. citeturn0search0turn0search1

Relevant capabilities:

- structured tool calling;
- byte-level grammar constrained to declared schemas;
- confidence score and confidence-gated escalation;
- tool retrieval for larger catalogues, exposing only the top five tools per turn;
- 256-token sliding window with tools pinned as KV sinks;
- offline inference after runtime/model availability;
- WebAssembly component distribution;
- LoRA fine-tuning/export.

The official API documentation says that more than five tools activates a retrieval head that selects the top five tools for a turn; an unselected tool is unreachable for that turn. Confidence combines a calibrated head and decoding probability and is intended for threshold-based escalation. citeturn0search3

Needle maps unusually well to SyllabAI because the intended task is:

```text
learner language
      ↓
intent
      ↓
tool
      ↓
arguments
      ↓
SyllabAI service
```

Needle 2 is **not a general-purpose conversational tutor**; that is a reason to use it as a controller, not a reason to make it the Tutor. citeturn0search0turn0search1

A recent third-party evaluation reported weaknesses with a 16-tool catalogue and persistent argument-grounding errors after small fine-tuning, while showing better tool selection on a smaller subset. This is not a SyllabAI benchmark, but it reinforces the need for category-specific tool sets, strict argument validation and confidence/fallback testing. citeturn0search7

**Status: PROPOSED primary candidate; benchmark required.**

### 4.2 FunctionGemma 270M

FunctionGemma is a function-calling model attractive for concrete API specialization and fine-tuning. Mobile deployment footprint is the concern. A current ecosystem deployment example reports an INT8 artifact around 271 MB, substantially larger than Needle's reported 14 MB. This example is not an official SyllabAI benchmark. citeturn0search9

**Status: PROPOSED secondary benchmark candidate; potentially useful as a higher-capacity/fine-tuned controller, not yet the default mobile-browser choice.**

### 4.3 LFM2.5 230M/350M class

LFM2.5 models are an interesting middle ground between an ultra-small controller and a general local LLM. They are worth testing for richer local intent understanding, structured extraction, tool use and possibly short transformations over already-supplied SyllabAI context.

They must not become a source of educational truth.

**Status: PROPOSED comparison candidate.**

### 4.4 Qwen3-0.6B and larger local models

A ~0.6B model or larger may provide more general reasoning capability but increases download, memory, warm-up, battery/CPU/GPU and low-end-device risk. Test only after identifying a real capability gap in the 45M–350M class.

**Status: PROPOSED higher-capability optional tier.**

### 4.5 WebLLM / WebGPU

WebLLM is valuable for high-end browser-local experiments but should remain optional because SyllabAI must work on devices without capable WebGPU paths. citeturn0search8

**Status: PROPOSED optional enhancement/runtime.**

## 5. Recommended model strategy

Do not choose one universal model. Make the **tool contract** the stable architecture and models interchangeable:

```text
                    SyllabAI Tool Contract
                             │
              ┌──────────────┼──────────────┐
              │              │              │
          local tiny     server small    large Tutor
          controller      controller        model
              │              │              │
          Needle 2       server model     deep AI
              │
       optional richer local
       model on capable devices
```

### Device tiers

**Tier A — constrained/unsupported local inference**
- no local model required;
- server-side controller/tool routing;
- deterministic UI remains fully functional.

**Tier B — ordinary mobile**
- Needle 2 or equivalent tiny controller;
- WASM/CPU path;
- local tool routing/navigation/extraction;
- no WebGPU requirement.

**Tier C — capable device**
- optional richer 230M–600M class model;
- potentially WebGPU;
- additional local language functionality.

All tiers use the same semantic tool contract.

## 6. Local Intelligence Layer architecture

```text
                         SyllabAI Web
                              │
                  ┌───────────▼───────────┐
                  │ Fast deterministic UI │
                  │ + local cached state  │
                  └───────────┬───────────┘
                              │
                    optional local agent
                              │
                  ┌───────────▼───────────┐
                  │ Local AI Controller   │
                  │ Needle / equivalent   │
                  └───────────┬───────────┘
                              │
                    semantic tool calls
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
       ▼                      ▼                      ▼
   Website/UI              Curriculum/KG         Learner/evidence
   semantic state          read APIs             read APIs
       │                      │                      │
       └──────────────────────┼──────────────────────┘
                              │
                         Tool Broker
                              │
                      SyllabAI backend
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
          retrieval           NBA            Tutor AI
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                       governed response
```

The local model can **read, resolve, navigate, search and request governed actions**. It cannot directly rewrite canonical educational truth.

## 7. Semantic Page Context

A foundational addition should be a **Semantic Page Context** layer. The model should not infer website state from arbitrary DOM text. The application should expose structured context such as:

```json
{
  "pageType": "EXAM_QUESTION",
  "subjectId": "...",
  "qualificationId": "...",
  "curriculumVersionId": "...",
  "resourceId": "...",
  "specificationPointIds": ["..."],
  "conceptIds": ["..."],
  "questionId": "...",
  "questionPartId": "..."
}
```

This reduces model burden and prevents it from guessing where the learner is. Context should be versioned and privacy-conscious.

## 8. Proposed SyllabAI local tool surface

The first version should remain small and semantic.

### Context

```text
get_current_context()
get_current_resource()
get_current_question()
get_selected_content()
```

### Navigation

```text
navigate_to_resource(resource_id)
navigate_to_question(question_id)
navigate_to_specification_point(specification_point_id)
navigate_to_past_paper(paper_id)
open_review_item(item_id)
```

### Curriculum/KG

```text
search_curriculum(query)
get_concept(concept_id)
get_related_concepts(concept_id)
get_prerequisites(concept_id)
get_resources_for_concept(concept_id)
get_questions_for_concept(concept_id)
```

### Learner/evidence

```text
get_learner_summary()
get_learner_state(specification_point_id)
get_recent_learning_evidence()
get_review_due()
get_learning_gaps()
get_recent_attempts()
```

### Learning actions

```text
find_revision_note(query)
find_exam_questions(query)
create_practice_recommendation()
start_practice(specification_point_id)
```

### Assessment/remediation

```text
get_current_marking_result()
get_marking_result(question_attempt_id)
get_related_remediation(question_attempt_id)
```

These names are conceptual and must be reconciled with actual web/core APIs before implementation.

## 9. Semantic UI tools, not arbitrary browser control

Do not give the model arbitrary DOM/JavaScript/network capabilities.

Rejected:

```text
click(selector)
executeJavascript(code)
POST arbitrary URL
modifyLocalStorage(key,value)
```

Preferred:

```text
navigate_to_resource()
open_question()
start_practice()
focus_question_part()
get_current_context()
```

This preserves authorization, auditability, deterministic behavior, testability, model independence and security boundaries.

## 10. Knowledge Graph integration

Expose the authoritative KG as **read-only semantic services**.

Example:

```text
Learner:
"What should I know before equilibrium?"

Local model:
find_concepts("equilibrium")

SyllabAI:
resolve canonical concept

Local model:
get_prerequisites(concept_id)

SyllabAI:
return validated prerequisite relations

Local model:
present/navigation action
```

The model does not infer a prerequisite relation from similarity. Authoritative educational KG semantics remain distinct from retrieval-derived relationships. Embeddings and local-model similarity remain retrieval/control signals, never educational truth.

## 11. Learner model integration

The local model should consume **read-only structured learner summaries**, for example:

```json
{
  "currentTopic": "...",
  "reviewDue": ["..."],
  "recentStruggles": ["..."],
  "recentAttempts": ["..."],
  "confidenceSignals": ["..."]
}
```

The existing learner architecture remains authoritative:

```text
Raw conversation
      ↓
interaction evidence
      ↓
learner patterns
      ↓
governed learner model
      ↓
recommendations
```

The local model can request and present these signals. It cannot promote a single utterance into mastery or misconception state.

## 12. Recommendation integration

The local agent should be a natural-language interface to the existing recommendation engine, not a replacement for it:

```text
local model
  → understand request
  → get_learner_summary / get_review_due / get_learning_gaps
  → create_practice_recommendation

SyllabAI recommendation engine
  → hard constraints
  → candidates
  → scoring/selection
  → evidence-backed reason

local model
  → explain/present result
```

## 13. Retrieval integration

The Local Intelligence Layer should front the existing Educational Retrieval Engine.

The accepted flow is:

```text
Learner query
  → intent/query understanding
  → curriculum + concept + learner resolution
  → lexical + semantic + metadata + authoritative-KG candidates
  → fusion/deduplication
  → SyllabAI-aware reranking
  → evidence/segment selection
  → evidence sufficiency
  → grounded downstream AI
  → claim/citation validation
```

The local model can assist the first stage by turning learner language into structured intent/query information. The backend owns educationally sensitive retrieval and evidence decisions.

## 14. Revision Notes

Natural-language navigation can make Revision Notes active:

> "Take me to the section on oxidation."

→ `find_revision_note` → `navigate_to_resource`

> "Show me the prerequisite for this."

→ `get_current_context` → `get_prerequisites`

> "What are the three key things here?"

→ `get_current_resource` → local summarization only when supplied context is sufficient, otherwise Tutor escalation.

Local summarization must not invent curriculum facts.

## 15. Exam Questions / Past Papers

Example:

> "Give me a harder question like this."

```text
get_current_question()
      ↓
get_question_specification_points()
      ↓
find_exam_questions(...)
      ↓
validated candidate filtering
      ↓
present/open candidate
```

Difficulty semantics remain owned by SyllabAI assessment/recommendation logic.

## 16. Smart Mark → remediation

A particularly strong loop is:

```text
Question attempt
      ↓
Smart Mark
      ↓
mark-point/evidence result
      ↓
local agent understands request
      ↓
get_marking_result()
      ↓
get_related_concepts()
      ↓
get_remediation resources
      ↓
Revision Note / targeted practice
```

The local agent does not independently grade. It retrieves and navigates from governed Smart Mark results.

## 17. Tutor integration and escalation

The Local Intelligence Layer should make Tutor less necessary for trivial work and better prepared for deep work.

**Fast path:** navigation, search, context, KG lookup, learner-state lookup, practice selection, simple structured actions.

**Deep path:** complex teaching, multi-step reasoning, misconception remediation, open-ended explanation, complex exam feedback, long-form grounded responses.

Proposed escalation:

```text
learner request
      ↓
local controller
      │
      ├── high-confidence bounded action → local tool
      │
      └── low confidence / complex intent
              ↓
          server controller
              ↓
          retrieval/evidence
              ↓
             Tutor
```

## 18. Offline and cache architecture

Do not hard-code IndexedDB as the public abstraction. Use a browser-local abstraction such as:

```text
LocalStore
├── session/context
├── recent resources
├── recent questions
├── small KG neighbourhoods
├── learner summary/review cache
└── model metadata/artifact cache
```

The implementation may use IndexedDB, Cache Storage, OPFS or browser-managed caches depending on artifact type and browser support.

**IndexedDB is storage, not the inference runtime.** Conceptually:

```text
model artifact storage
       ↓
WASM/native/browser runtime
       ↓
Web Worker
       ↓
local controller
```

First-load sequence:

```text
critical HTML/JS/data
       ↓
website interactive
       ↓
idle/background capability detection
       ↓
optional model download
       ↓
worker initialization
       ↓
local agent becomes available
```

## 19. Performance architecture

Performance must be a product requirement, not just a model benchmark.

These are **PROPOSED research targets**, not accepted SLAs:

| Interaction | Target direction |
|---|---|
| Cached navigation | ~100–200 ms perceived response |
| Local intent/tool routing | sub-second, preferably near-immediate |
| UI thread blocking | 0 ms attributable to inference |
| Initial website interactivity | independent of model availability |
| Local controller download | small enough for mobile networks |
| Local controller RAM | low tens of MB preferred |
| Deep Tutor | immediate acknowledgement + streamed response |

Benchmark at minimum on low-end Android Chrome, mid-range Android Chrome, representative iPhone Safari, desktop without WebGPU and desktop with WebGPU.

Measure cold/warm startup, first/steady inference, RAM, CPU, battery/thermal behavior where practical, UI responsiveness, network use, cache persistence, model download, tool/argument accuracy and confidence/abstention.

Vendor throughput claims are not sufficient evidence for production adoption.

## 20. Local intelligence should be invisible when unavailable

A user should not see an "AI unavailable" state. The same request should use:

```text
local model
server model
or deterministic path
```

without changing the semantic product contract.

## 21. Security and governance boundaries

### May

- read current semantic UI context;
- query approved curriculum/KG APIs;
- query approved learner/evidence summaries;
- request navigation;
- request search/retrieval;
- request governed practice/recommendation actions;
- route to Tutor.

### Must not

- mutate authoritative curriculum content;
- mutate SpecificationPoints;
- create/promote authoritative KG edges;
- directly change mastery;
- create learner evidence as if it were validated evidence;
- bypass assessment validation or authorization;
- execute arbitrary browser code;
- access arbitrary network resources;
- fabricate unsupported tool arguments;
- treat semantic similarity as educational truth.

All state-changing operations remain behind normal application/provenance/authorization boundaries.

## 22. Failure modes to test

### Model

- wrong intent;
- correct tool/wrong argument;
- invented arguments;
- failure to abstain;
- similar-tool confusion;
- context loss;
- multilingual learner phrasing;
- over-triggering.

### Tool catalogue

Tiny models may degrade as tool count and semantic overlap grow. Needle's top-five retrieval must be benchmarked with the actual SyllabAI catalogue. A third-party evaluation reported poorer end-to-end argument accuracy with a 16-tool catalogue than with a smaller subset. citeturn0search7

### Device

- low RAM;
- browser process eviction;
- WASM limitations;
- thermal throttling;
- background tab suspension;
- storage eviction;
- slow model acquisition;
- Safari/Chrome differences.

### Product

- local agent makes the site slower;
- suggestions distract from learning;
- local summaries bypass grounded Tutor evidence;
- learner state is unnecessarily exposed;
- actions become difficult to audit.

## 23. What must remain unchanged

1. SyllabAI remains authoritative for curriculum and educational semantics.
2. SpecificationPoints remain first-class canonical anchors.
3. Authoritative educational KG remains distinct from retrieval-derived graphs.
4. Learner state remains an overlay on curriculum truth.
5. Embeddings/semantic similarity remain retrieval/control signals, not educational truth.
6. Imported assessment content remains gated before learner serving.
7. Raw conversation remains history/audit data.
8. Extracted interaction evidence remains provenance-bearing learner signal.
9. Chat output cannot directly mutate canonical KG or mastery.
10. Retrieval remains evaluated for educational precision.
11. Grounded Tutor responses require evidence and claim/citation validation.
12. Provider-specific infrastructure must not become the canonical data model.

## 24. What needs to be added

No rewrite is implied. The main additions are:

1. **Semantic Page Context** — structured application context for controllers.
2. **SyllabAI Local Tool Contract** — stable semantic tools independent of model/vendor.
3. **Local Agent Runtime abstraction** — Needle, another local model, or no local model.
4. **Escalation/capability policy** — local/server/deep selection using confidence, task class, device capability and cost/latency policy.

## 25. Development plan

### Phase 0 — architecture contract
**Status: PROPOSED**

Deliverables:
- this architecture/research document;
- semantic page-context contract;
- initial tool taxonomy;
- local/server/deep execution policy;
- authorization boundary;
- benchmark dataset specification.

Exit gate: tool contract reviewed against current web/core APIs and no tool bypasses canonical logic.

### Phase 1 — deterministic semantic tool broker

Build the useful part without a model:

```text
get_current_context
get_current_resource
get_current_question
navigate_to_resource
navigate_to_question
search_curriculum
get_related_concepts
find_revision_note
find_exam_questions
get_learner_summary
get_review_due
```

Exit gate: typed tools, authorization, structured errors, observability, no model dependency.

### Phase 2 — local controller benchmark

Primary candidate: Needle 2.

Build a benchmark using real SyllabAI utterances + page contexts. Test intent, tool selection, arguments, abstention, ambiguity, multi-turn results and confidence thresholds.

Compare:

```text
Needle 2
server controller baseline
LFM2.5 230M/350M (optional)
FunctionGemma 270M (optional)
```

Exit gate: agreed SyllabAI accuracy/abstention thresholds and target-device latency; no unacceptable fabricated arguments.

### Phase 3 — mobile runtime prototype

Integrate the winning tiny controller into a Web Worker/WASM path. Test low/mid Android, iOS Safari, desktop fallback, cold/warm initialization, cache behavior, storage eviction, tab lifecycle and network interruption.

Exit gate: no visible UI jank, deterministic fallback works, memory/startup budgets acceptable.

### Phase 4 — website agent MVP

Enable:
1. natural-language navigation;
2. current-page understanding;
3. curriculum/KG lookup;
4. Revision Note lookup;
5. Exam Question lookup;
6. learner review lookup;
7. governed practice launch.

No direct mastery or KG mutation.

### Phase 5 — evidence-aware remediation

Integrate Smart Mark → remediation, learning evidence → concept/resource, review → practice, recommendation → action and Tutor escalation.

Demonstrate:

```text
assessment → evidence → learner state → local agent
→ governed recommendation → intervention → assessment
```

### Phase 6 — optional richer local intelligence

Only if Phase 2 exposes a capability gap, evaluate LFM2.5 230M/350M, FunctionGemma 270M, Qwen3 0.6B and WebGPU on capable devices.

Do not add a larger model merely because generic benchmarks are better.

### Phase 7 — SyllabAI-specific fine-tuning

Only after enough real tool traces exist. Training/evaluation records should contain learner utterance, semantic page context, tool set, expected tool, expected arguments and expected abstention/escalation.

Potential specialization: SyllabAI terminology, SpecificationPoints, learner phrasing, navigation language, tool schemas and multilingual/local phrasing.

Needle-specific caveat: official documentation states base confidence calibration does not carry over to fine-tuned weights; a fine-tuned agent reports confidence as `None`. Fine-tuned controllers therefore require separate calibrated confidence/abstention evaluation. citeturn0search3

## 26. Benchmark specification

The first benchmark should use realistic SyllabAI tasks, not generic function-call prompts.

| Class | Example |
|---|---|
| Navigation | "Take me to oxidation" |
| Current context | "What is this section about?" |
| KG | "What should I know first?" |
| Revision | "Find the note on ionic bonding" |
| Assessment | "Give me another question like this" |
| Learner state | "What should I revise?" |
| Review | "What is due today?" |
| Remediation | "Why did I lose marks?" |
| Ambiguous | "That thing we did yesterday" |
| Unsupported | unrelated request |
| Multi-step | "Find a harder question on this and start practice" |

Metrics:

- tool-selection accuracy;
- argument correctness;
- end-to-end action correctness;
- unsupported-request abstention;
- escalation precision/recall;
- confidence calibration;
- p50/p95 latency;
- memory;
- CPU;
- UI responsiveness;
- download size/time;
- recovery rate.

Educational safety metrics:

- incorrect SpecificationPoint resolution;
- unauthorized learner-state access;
- invalid navigation;
- unvalidated assessment selection;
- fabricated tool arguments;
- unsupported educational claims;
- direct state-mutation attempts.

## 27. Observability

Recommended event shape:

```text
local_agent_event
├── controller_type
├── model_version
├── tool_catalogue_version
├── page_context_version
├── tool_selected
├── confidence (if available)
├── execution_result
├── escalation_reason
├── latency_ms
└── error_code
```

Raw learner text should follow existing privacy/audit policies and should not be copied into telemetry merely because a local model saw it.

## 28. Rollout strategy

Use a capability flag rather than a model-specific product flag:

```text
local_agent_capability =
  unavailable | available | enabled | disabled
```

Rollout:

```text
internal benchmark
   ↓
developer-only
   ↓
small opt-in cohort
   ↓
low-risk navigation tools
   ↓
KG/resource lookup
   ↓
learner/review read paths
   ↓
practice actions
```

Do not begin with state-changing educational actions.

## 29. Open questions

1. What exact WASM/browser integration does current Needle 2 support in Next.js 16/React 19?
2. What are cold/warm startup and memory characteristics on representative low-end Android devices?
3. Is the 256-token Needle context sufficient for SyllabAI tool schemas + page context?
4. How should tool categories be selected before Needle's own top-five retrieval?
5. How does Needle perform with actual multilingual learner phrasing?
6. What confidence threshold gives acceptable precision/latency?
7. How should confidence be recalibrated after SyllabAI fine-tuning?
8. Which browser storage mechanism is most reliable on iOS/Android?
9. What cache eviction behavior occurs under mobile storage pressure?
10. Should KG neighbourhoods be prefetched from navigation/learner schedule?
11. Which interactions should remain deterministic rather than model-driven?
12. Does a 230M/350M model justify its larger footprint?
13. Can local routing materially reduce server LLM calls and perceived latency?
14. What privacy policy is appropriate for local-agent telemetry?
15. Can the same tool contract serve a future teacher-facing local agent?

## 30. Architectural verdict

**Status: PROPOSED**

The strongest direction is not “put a local LLM in SyllabAI.” It is:

> **Build SyllabAI as a semantic application that can be driven by a tiny local intelligence controller when available, a server controller when not, and deterministic application logic underneath both.**

Needle 2 is currently the most compelling first candidate because its documented deployment footprint and tool-calling contract align unusually well with SyllabAI's mobile-browser requirements. Its weaknesses — narrow general language capability, small context, tool/argument accuracy limitations and fine-tuned confidence calibration caveat — are precisely why the benchmark must be SyllabAI-specific. citeturn0search0turn0search3turn0search7

The key architectural commitment is **not Needle**. It is the **common semantic tool contract**:

```text
                    SyllabAI Tool Contract
                           │
             ┌─────────────┼─────────────┐
             │             │             │
         local tiny     server AI    large Tutor
          controller    controller       AI
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                  SyllabAI authoritative
                       application
```

This preserves flexibility while allowing SyllabAI to become locally agentic without sacrificing speed, correctness, provenance or educational governance.

## 31. Source and evidence notes

### SyllabAI sources

This document builds on the canonical project architecture, especially `MASTER_SPEC.md`, `PROJECT_CONTEXT.md`, `PROJECT_KNOWLEDGE_MAP.md`, `RAG_RETRIEVAL_RESEARCH.md`, `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md`, `RECOMMENDATION_SYSTEM_ARCHITECTURE.md`, `SUBJECT_ARCHITECTURE.md`, `CONTEXTUAL_LEARNING_ASSISTANT_ARCHITECTURE.md`, and current `syllabai-core` / `syllabai-web` implementation contracts.

### External research performed 2026-09-17

- Cactus Compute Needle 2 official repository/API: 45M model, 14 MB artifact, ~28 MB session RAM, tool retrieval, confidence gating, 256-token window and WASM component support. citeturn0search0turn0search1turn0search3
- Cactus package metadata: Apache-2.0, version 2.0.12 at research time. citeturn0search11
- WebLLM official repository: browser-local WebGPU inference and OpenAI-compatible interface. citeturn0search8
- Independent Needle evaluation: evidence of tool/argument accuracy degradation with larger catalogues and the need for confidence-gated fallback. citeturn0search7

External claims are research evidence, not SyllabAI verification. Device performance and production suitability remain **UNVERIFIED** until measured on SyllabAI's target device matrix.
