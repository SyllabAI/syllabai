# Local Intelligence Layer — Knowledge Map Entry

**Status:** PROPOSED
**Canonical artifact:** `LOCAL_INTELLIGENCE_LAYER_ARCHITECTURE.md`
**Context addendum:** `LOCAL_INTELLIGENCE_LAYER_CONTEXT_ADDENDUM.md`
**Tracking:** T-LIL / GitHub issue #10

## Location

This research belongs in the central `SyllabAI/syllabai` repository because it is cross-project architecture spanning the web client, core services, retrieval, Knowledge Graph, learner model and Tutor.

## What future agents should read

Read `LOCAL_INTELLIGENCE_LAYER_ARCHITECTURE.md` for:

- mobile-browser performance constraints;
- local vs server vs large-model architecture;
- Needle 2 and alternative-model research;
- Semantic Page Context;
- proposed semantic tool surface;
- Knowledge Graph and learner-model integration;
- Revision Notes / Exam Questions / Smart Mark / Tutor integration;
- browser storage/runtime guidance;
- security/governance boundaries;
- benchmark design;
- development phases and rollout.

Read `LOCAL_INTELLIGENCE_LAYER_CONTEXT_ADDENDUM.md` for the concise cross-project orientation.

## Source-of-truth status

This is **PROPOSED** research. It does not modify `MASTER_SPEC.md`, create an accepted ADR, or make Needle 2 a production dependency. Production adoption requires SyllabAI-specific benchmark and target-device evidence.

## Durable invariant introduced by this research

The architecture should remain model-independent:

```text
local model / server model / deterministic path
                    ↓
          common SyllabAI semantic tools
                    ↓
             authoritative app
```

The model may control/read/request actions through governed tools, but it must not become the source of educational truth or bypass application governance.
