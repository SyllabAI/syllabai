# OpenHuman Graph Archaeology

**Status:** VERIFIED research findings; adoption decisions remain PROPOSED unless explicitly marked otherwise.

**Date:** 2026-09-15

**Canonical SyllabAI baseline:** `main` at `001e0eee1f60752eebf656636faf20aa434db548`.

## 1. Scope

This investigation examines the current OpenHuman implementation, not only its feature documentation, for graph-related patterns that may inform SyllabAI:

1. graph rendering and interaction;
2. graph data modelling and lifecycle;
3. hierarchical memory/context construction;
4. provenance and derived-graph boundaries;
5. version/diff tracking;
6. durable workflow/run graphs;
7. background cognition and bounded agent execution.

OpenHuman remains **REFERENCE ONLY**. Its GPL-3.0-only repository and Rust/Tauri architecture are not SyllabAI runtime dependencies.

## 2. Executive conclusion

The most important OpenHuman findings are **not additional graph UI features**. SyllabAI already has the high-value graph interaction patterns in the v57 prototype.

The stronger architectural references are:

- **Derived graph as a projection:** OpenHuman's entity graph is explicitly read-only and derived from the memory tree/entity index rather than being a second authoritative store.
- **Provenance-bearing retrieval:** retrieval hits carry tree/source identity, hierarchy level, time range, entities/topics, child IDs, and source back-pointers.
- **Authoritative-vs-derived separation:** the memory tree/chunk store is treated as authoritative while graph and diff views are derived.
- **Versioned change ledger:** Memory Diff uses Git commits as snapshots over authoritative memory, allowing source-scoped diffs and read markers.
- **Durable execution graphs:** workflow runs persist run state, checkpoints, graph observations, approvals, and a graph hash used to prevent resuming against a changed workflow.
- **Bounded background cognition:** the subconscious is a separate, explicitly typed execution origin with fail-closed trust semantics.

These map unusually well to SyllabAI's learning-evidence → diagnosis → intervention → reassessment loop, but they must be adapted to SyllabAI's educational truth model rather than copied as a generic memory architecture.

## 3. Renderer findings

### Verified OpenHuman implementation

`PixiGraph.tsx` is a thin React lifecycle host around an imperative Pixi renderer. React forwards graph data and callbacks; Pixi owns canvas interaction. The wrapper deliberately keeps callbacks in refs so callback changes do not tear down/recreate the GPU context. It supports in-place graph updates when graph mode is unchanged and full remounts when mode semantics change. fileciteturn34file0L2-L6

`pixiGraphRenderer.ts` uses Pixi/WebGL with d3-force. It keeps the graph as a single canvas rather than per-node DOM elements, dirty-flags rendering, supports drag/pan/wheel zoom, auto-fit, reset, theme changes, hover, and open/click callbacks, and can hot-swap node/link arrays while preserving existing node positions by stable ID. New nodes are seeded near their parent where possible. fileciteturn35file0L2-L3

`memoryGraphLayout.ts` is renderer-agnostic: d3-force, graph construction, node palette/radii, hit-testing, zoom bounds, and WebGL capability detection are shared across Pixi and SVG. Tree mode derives links from `parent_id`; contacts mode consumes explicit edges. fileciteturn36file0L2-L6

### SyllabAI classification

**Already borrowed / VERIFIED:** force-directed graph, hierarchy, selection, search/navigation, pan/zoom, reset, relationship filtering, learner overlays, Teacher Lens, provenance-aware Connections, SVG accessibility, keyboard interaction hardening, and progressive learning surfaces are already present in the v57 prototype.

**Useful to borrow / PROPOSED:** renderer lifecycle discipline and stable-ID position preservation are useful engineering patterns for a future production KG explorer, but they are not architecture-changing requirements.

**Deliberately reject / PROPOSED:** copying Pixi/d3-force as a SyllabAI dependency merely because OpenHuman uses it. The current SyllabAI graph is an educational semantic interface, not a generic memory canvas; renderer choice should follow scale and accessibility benchmarks.

## 4. Graph data model and lifecycle

OpenHuman's graph export has an explicit wire model: `GraphNode` contains kind/id/label plus optional tree kind, scope, tree id, level, parent, child count, time range, file basename, and entity kind; `GraphEdge` is a simple from/to pair. The graph exporter has an explicit 10,000-node budget and derives source roots, summary hierarchy, document leaves, and parent relationships from the memory-tree forest. fileciteturn41file0L2-L2

The important architectural property is that the graph export is a **projection**. It reads the tree and entity layers; it does not become the source of truth. The implementation comments explicitly distinguish the `MemoryGraph` key/value/relation tier from the exported summary forest/contact graph. fileciteturn41file0L2-L2

OpenHuman's provider boundary also exposes `MemoryEntities`, `MemoryGraph`, and `MemoryDiff` as distinct capabilities. The entity layer supports canonical entity lookup and entity/chunk relationships; the graph layer supports key/value and explicit relations; the diff layer captures snapshots and computes diffs. fileciteturn42file0L2-L2

### SyllabAI implication

**ACCEPTED invariant reinforced:** the authoritative educational KG must remain distinct from retrieval-derived graphs.

A useful target decomposition is:

```text
Authoritative curriculum KG
        |
        +--> retrieval projections
        |      - lexical/semantic candidates
        |      - concept neighborhood
        |      - evidence graph
        |
        +--> learner-state overlay
        |      - attempts/evidence/patterns/mastery
        |
        +--> product projections
               - student graph
               - teacher attention
               - learning path
```

Do not create a second "SyllabAI memory graph" that can drift from SpecificationPoints and canonical educational semantics.

## 5. Provenance and retrieval

OpenHuman's retrieval contract is unusually explicit. Every `RetrievalHit` carries node identity and kind, tree identity/scope/level, content, entities/topics, time range, relevance score, child IDs, and a source back-pointer. The retrieval layer deliberately exposes deterministic primitives while leaving composition/routing to the calling agent. fileciteturn44file0L2-L2

Its entity graph is read-only and derived from co-occurrence on tree nodes; it is a self-join over the entity index rather than a parallel triple-store table. The deterministic walk uses entity relationships to route retrieval before ranking evidence. fileciteturn44file0L2-L2

### SyllabAI mapping

This is highly compatible with the SyllabAI retrieval baseline:

```text
learner query
  -> intent / curriculum resolution
  -> candidate generation
       lexical + semantic + metadata + authoritative KG
  -> fusion / dedup
  -> SyllabAI-aware rerank
  -> evidence selection
  -> evidence sufficiency
  -> grounded AI
  -> claim/citation validation
```

The OpenHuman pattern worth borrowing is **rich evidence identity**, not its retrieval algorithm. SyllabAI should consider a canonical `EvidenceRef`/`EvidenceSegment` contract that can point to:

- SpecificationPoint(s);
- validated resource/segment;
- question/part/mark point;
- learner-evidence record;
- provenance/source/version;
- retrieval method and score;
- evidence role in the generated claim/intervention.

**PROPOSED:** benchmark whether richer evidence identity improves citation validation, diagnosis explainability, and debugging before expanding the production schema.

## 6. Memory Tree: useful pattern, dangerous analogy

OpenHuman's Memory Tree is a write/read architecture that folds a stream into chunks and hierarchical summaries. Retrieval can query sources, drill down summaries, cover time windows, hydrate leaves for exact citations, resolve entities, and perform deterministic graph-assisted walks. fileciteturn44file0L2-L2

The architecture is attractive for a future SyllabAI **context-construction/compression layer**. It is not a replacement for the curriculum KG or learner model.

SyllabAI should preserve:

- curriculum truth in SpecificationPoints/KG;
- learner state as an overlay;
- extracted interaction evidence as provenance-bearing signals;
- raw conversation as audit/history.

A future context layer could compress large validated resource collections and learner histories into scoped summaries, but every summary must remain a derived retrieval/context artifact and must retain provenance to authoritative evidence.

**PROPOSED experiment:** compare direct evidence selection vs hierarchical context summaries on tutor grounding precision, citation completeness, and latency.

## 7. Versioning / Memory Diff

OpenHuman's Memory Diff treats the chunk store as authoritative and the diff ledger as a derived read-only view. Snapshots are Git commits; each source is represented under its own subtree, read markers track what an agent has already consumed, and source-scoped or cross-source diffs can be computed from the commit history. fileciteturn45file0L2-L2

### SyllabAI mapping

This is one of the highest-value architectural references, but the unit of versioning should be different.

Potential SyllabAI applications:

1. **Curriculum/resource version diff:** detect what changed between validated curriculum/resource revisions.
2. **Learner-model audit diff:** show what evidence caused a governed learner-state change.
3. **Intervention lifecycle diff:** compare diagnosis → recommendation → practice → reassessment state transitions.
4. **Evaluation reproducibility:** retain the evidence/version set used for a recommendation so it can be reconstructed later.

Do **not** use Git as the learner database. The lesson is the **immutable, replayable change ledger**, not the specific storage technology.

**PROPOSED:** design a database-native `EvidenceChange` / `LearnerStateChange` event ledger with deterministic before/after snapshots and provenance, then benchmark whether a Git-backed export adds enough value to justify it.

## 8. Durable workflow / execution graph

OpenHuman's workflow runtime has a materially stronger pattern than the visual graph alone. A flow run is persisted, has a checkpointer, a live observer, a per-run graph-event journal, cancellation/timeout handling, terminal-state finalization, and approval state. The run journal can be exported for observability. fileciteturn48file0L2-L2

When a run parks for approval, the implementation computes a graph hash and later compares it against the current workflow graph before allowing resume. This prevents a user from approving one graph and resuming a different graph. fileciteturn48file0L2-L2

### SyllabAI mapping

This maps strongly to adaptive learning orchestration:

```text
Diagnosis snapshot
      |
      v
Intervention plan (versioned)
      |
      v
Practice execution
      |
      v
Evidence collection
      |
      v
Reassessment
      |
      v
Learner-state update
```

Each transition should be auditable and tied to the exact curriculum/evidence/intervention definition used.

**HIGH-VALUE PROPOSAL:** introduce a bounded `LearningRun` / `InterventionRun` concept rather than allowing agents to mutate learner state directly. A run should have:

- immutable run id;
- target SpecificationPoint(s);
- diagnosis/evidence snapshot;
- intervention version/hash;
- allowed app tools;
- step observations;
- approval requirements where relevant;
- terminal outcome;
- learner-state mutation only through governed application logic.

This is more important than adding another graph visualization.

## 9. Background cognition / subconscious

OpenHuman has an explicit `AgentTurnOrigin` taxonomy for web chat, external channels, trusted automation, CLI/direct chat, and unknown origins. Unknown/unscoped execution fails closed; origin can be propagated across spawned tasks without upgrading trust. fileciteturn52file0L2-L2

Its current subconscious configuration defaults to a local graph. The `medulla` option is explicitly accepted for backwards compatibility but is not implemented in the current build; it falls back to local behavior. fileciteturn51file0L2-L2

### SyllabAI mapping

The useful idea is **bounded background evaluation with explicit provenance and trust**, not an autonomous subconscious agent.

A future SyllabAI background evaluator could periodically inspect accumulated learning evidence and propose:

- mastery-confidence recalculation;
- misconception candidate promotion;
- review/decay updates;
- next-best-action candidates;
- data-quality anomalies.

It must **not** directly mutate canonical KG or learner mastery. Outputs should be proposals/evidence that pass the same governed application logic as foreground interactions.

**PROPOSED:** background diagnosis service with deterministic cadence, bounded input scope, explicit evidence window, versioned evaluator, and proposal-only output.

## 10. Classification matrix

| OpenHuman capability | SyllabAI equivalent | Status | Decision |
|---|---|---|---|
| Force-directed graph renderer | KG exploration prototype | IMPLEMENTED / VERIFIED in v57 | Keep; renderer remains replaceable |
| Stable-ID position preservation | Future graph renderer | INFERRED as useful | Borrow pattern, not code |
| Tree graph as projection | Retrieval/derived graph | ACCEPTED | Preserve strongly |
| Canonical entity index | Curriculum concepts/SpecificationPoints | ACCEPTED analogue | Keep SyllabAI semantics authoritative |
| Rich retrieval provenance | Evidence refs / grounded tutor | PROPOSED | Prototype + benchmark |
| Hierarchical summary tree | Context compression | PROPOSED | Research only; never replace KG |
| Derived co-occurrence graph | Retrieval graph | PROPOSED | Evaluate as a retrieval signal |
| Git-backed memory diff | Curriculum/learner evidence change ledger | PROPOSED | Design database-native first |
| Read markers | Incremental evidence processing | PROPOSED | Potentially useful for background evaluation |
| Durable workflow graph | Learning/intervention run | PROPOSED | High priority architecture research |
| Approval checkpoint + graph hash | Governed intervention resume | PROPOSED | Strong safety/reproducibility pattern |
| Background subconscious | Background learner-state evaluator | PROPOSED | Proposal-only; bounded |
| Typed execution origin | Agent/tool trust boundary | PROPOSED | Strong security pattern |
| Pixi/WebGL specifics | SyllabAI graph UI | REJECTED as dependency | Benchmark rather than copy |
| OpenHuman memory store | SyllabAI canonical KG | REJECTED | Violates educational authority boundary |

## 11. What should remain unchanged

1. SpecificationPoints remain first-class canonical anchors.
2. SyllabAI remains authoritative for curriculum and educational semantics.
3. Learner state remains an overlay, never a mutation of curriculum truth.
4. Retrieval-derived graphs remain subordinate to authoritative KG.
5. Imported assessment content remains blocked from learner serving until validation gates pass.
6. Chat output does not directly mutate mastery/KG.
7. Raw conversation remains audit/history; extracted interaction evidence remains the structured learner signal.
8. Grounded Tutor claims require evidence sufficiency and citation/claim validation.
9. Provider-specific retrieval infrastructure remains pluggable.
10. Agents remain bounded and app-controlled.

## 12. What could fail if we borrow the wrong thing

### Failure mode A — Memory Tree becomes a second educational truth
A summary hierarchy could silently become the system's de facto curriculum model. This would violate the authoritative-KG boundary.

**Guardrail:** every derived summary stores provenance and is treated as regenerable retrieval context.

### Failure mode B — Background evaluator writes mastery directly
Periodic evaluation could turn weak signals into false certainty.

**Guardrail:** background output is a proposal/evidence record; governed learner-model logic performs the state transition.

### Failure mode C — Workflow graph becomes autonomous pedagogy
A generic agent workflow could start deciding educational semantics.

**Guardrail:** learning workflows orchestrate approved interventions; they do not define curriculum truth or mastery rules.

### Failure mode D — Versioning records snapshots without causal provenance
A before/after diff alone does not explain why a learner state changed.

**Guardrail:** state-change events must reference the evidence, diagnosis rule/version, intervention, and assessment outcome that caused the change.

### Failure mode E — Graph UI becomes the architecture
Visualizing relationships does not create an educational graph model.

**Guardrail:** canonical domain model and evidence contracts precede visualization.

## 13. Recommended next experiments

### E1 — Evidence identity benchmark
**Status:** PROPOSED

Compare current retrieval evidence records against a richer `EvidenceRef` contract containing source/version/SpecificationPoint/question-part/mark-point/learner-evidence provenance. Measure citation validity, educational precision, diagnosis explainability, and latency.

### E2 — InterventionRun prototype
**Status:** PROPOSED

Create a backend-only run model for one adaptive intervention. No new graph UI. Validate:

- immutable target/evidence snapshot;
- intervention version/hash;
- step observations;
- resumability;
- governed learner update;
- audit reconstruction.

### E3 — Background diagnosis proposal loop
**Status:** PROPOSED

Run a bounded evaluator over a fixed learner-evidence window. It may produce diagnosis/recommendation proposals only. Compare against foreground diagnosis for precision and false-positive rate.

### E4 — Hierarchical context compression benchmark
**Status:** PROPOSED

Use validated revision resources and learner history. Compare direct evidence selection against hierarchical summaries. Do not alter canonical KG.

### E5 — Change-ledger design
**Status:** PROPOSED

Define an append-only learner-state change event with causal provenance. Evaluate PostgreSQL-native implementation first; Git export is optional.

## 14. Current decision summary

**VERIFIED:** OpenHuman's production graph is primarily a projection/view over memory structures, not an authoritative educational-style graph. Its strongest transferable ideas are provenance-rich retrieval, derived graph separation, durable run/checkpoint semantics, graph-version protection, and bounded background execution.

**PROPOSED:** SyllabAI should investigate a first-class `LearningRun` / `InterventionRun` orchestration layer and a causal learner-state change ledger before investing in further graph UI.

**REJECTED:** treating OpenHuman's memory graph, Memory Tree, Pixi renderer, or Rust/Tauri runtime as SyllabAI architectural dependencies.

**Next priority:** E2 (InterventionRun prototype), followed by E1 (Evidence identity benchmark).