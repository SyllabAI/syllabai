# SyllabAI Architecture Research / Reference Register

This register records external projects that are useful as **architecture, UX, orchestration, visualization, or implementation-pattern references** for SyllabAI.

These references are not runtime dependencies unless explicitly approved by an ADR and the integration verdict in `REPOSITORY_RESEARCH.md`.

| Reference | Role for SyllabAI | What to study | Adoption boundary | Status |
|---|---|---|---|---|
| [OpenHuman](https://github.com/tinyhumansai/openhuman) | Agent orchestration, persistent memory/context, graph UI | Durable/checkpointed agent graphs; Memory Tree / hierarchical summarization; context compression; approval-gated workflows; interactive force-directed memory visualization | **REFERENCE ONLY.** Rust/Tauri architecture is not our Java/Spring runtime. Repository is GPL-3.0-only; do not copy code into SyllabAI without a separate license review. | ADDED 2026-09-05 |
| [The-Brain](https://github.com/Hastur-HP/The-Brain) | Knowledge-graph UX, RAG observability | 3D graph exploration, node/type visualization, neighborhood exploration, evidence highlighting, SSE ingestion progress | **REFERENCE / SELECTIVE CODE REUSE** subject to existing `REPOSITORY_RESEARCH.md` verdict and license/dependency review | Existing |
| [Understand Anything](https://github.com/Egonex-AI/Understand-Anything) | Interactive knowledge-graph UX | Search/explore graph patterns and technical-knowledge navigation | **REFERENCE.** Do not replace SyllabAI's pedagogical KG with a code-oriented graph model. | Existing |
| [DeepTutor](https://github.com/HKUDS/DeepTutor) | End-to-end learning-agent architecture | Retrieval fusion, tutor orchestration, persistent learning context, study workflows | **REFERENCE.** SyllabAI retains its own Java learner-model and evidence architecture. | Existing |
| [Get It.](https://github.com/beltromatti/get-it) | Mastery-map/student UX | Concept-first visualization and mastery-oriented interaction | **REFERENCE.** Use as product/UX inspiration for T-028. | Existing |

## OpenHuman research notes

OpenHuman is especially relevant to two future SyllabAI concerns:

1. **Context construction rather than context dumping.** Its Memory Tree canonicalizes, chunks, scores, and folds material into hierarchical source/topic/global summaries. This is a useful reference for a future learner-context selection/compression layer, while SyllabAI's BKT/BDT/Ebbinghaus/KG state remains the authoritative educational model.
2. **Interactive graph presentation.** OpenHuman's Memory Graph uses a force-directed layout and separates tree/contacts views. The production renderer uses Pixi.js/WebGL with `d3-force`; it falls back to SVG where WebGL is unavailable. Node dragging, background panning, wheel zooming, reset/recentering, and node-click preview/open are part of the interaction model. See the live implementation notes in the OpenHuman repository and use this as a T-028 visual reference.

## Licensing / architecture guardrail

OpenHuman's repository declares **GPL-3.0-only**. It is therefore a reference for architectural ideas and UI behavior, not a drop-in SyllabAI dependency. SyllabAI's production stack remains Java 25 + Spring Boot + Spring AI, Next.js/React, Neon PostgreSQL + pgvector, and the existing evidence-first learner model.
