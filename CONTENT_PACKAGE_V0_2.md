# SyllabAI Content Package v0.2 Specification

**Status:** ACCEPTED (2026-09-29 — the operator's ADR-021 forward-gate directive, chat bb263437, trace 1a0ea03c8fe4a9c1; implemented and CI-verified the same day, ADR-029 tranche 4.14)
**Date:** 2026-09-29
**Related:** `ADR_021_CONTENT_COMPILER_AND_PORTABLE_CONTENT_PACKAGE.md` (ACCEPTED), `CONTENT_PACKAGE_V0_1.md` (ACCEPTED as implemented), `CONTENT_COMPILER_AND_PACKAGE_ARCHITECTURE.md` (PROPOSED — the staged roadmap this contract advances)

## 1. Purpose

v0.2 extends the accepted v0.1 package contract with the two ADR-021 forward gates: the **KG projection policy** (which knowledge-graph semantics may enter a package, under what provenance rules) and the **distribution/versioning form** (the §7 bundle, scoped packages, deterministic zips). It changes nothing about v0.1's boundaries: the package remains a derived, portable, reproducible snapshot — never a second database, never authoritative learner/curriculum/KG truth, never a serving gate bypass.

## 2. KG projection policy

### 2.1 Eligibility and non-authoritativeness

KG semantics (the per-course concept graphs) MAY be projected into a package as `kg_node`, `kg_node_specification_point`, and `kg_edge` rows, under these rules:

1. **Provenance is preserved verbatim.** Every row carries its source `provenance_tier` and `extraction_pass`; a tier is never re-labelled, upgraded, or defaulted. The governed tier vocabulary: `AI_SUGGESTED`, `RULE_DERIVED`, `OPERATOR_REVIEWED`, `HUMAN_VALIDATED`, `VALIDATED`. An unknown tier fails closed.
2. **KG rows are non-authoritative by construction.** They never confer authority, curriculum truth, KG truth, or learner-serving eligibility. The package records the corpus's own graph-level `validationGate` text verbatim as a finding (measured 2026-09-29: 100% of corpus KG rows are `AI_SUGGESTED`; the pilot's gate declares operator review pending, no promotion from generated state).
3. **Measured corpus reality is projected honestly.** Only `igcse-chemistry-19` carries a graph (113 nodes / 275 edges; the other 48 courses are empty shells with `counts: null`). Empty graphs project zero rows — an empty graph is the corpus's state, not an error.
4. **Node bodies are projection content, not fabricated semantics.** Titles, aliases, summaries, evidence quotes, derivation methods are carried from the source graph verbatim; the compiler adds no semantics of its own.

### 2.2 Identity and resolution (measured, not guessed)

- Node identity is composite `(course_slug, code)`; codes are course-local (measured: 0 of 113 codes shared across courses).
- Edge identity is `(course_slug, edge_index)` preserving source-array order, with a UNIQUE constraint on `(course_slug, source, relation, target)` — parallel duplicate triples fail closed (measured: 275/275 distinct; a future parallel edge is a corpus change to adjudicate, never silently projected).
- **Two-namespace endpoint resolution:** every edge endpoint must resolve against the course's `kg_node` codes OR its curriculum `SPEC_POINT` codes (measured: `PART_OF` = CONCEPT→SPEC, 117 edges over 77 distinct spec points — the same 77 as `node.specPoints`; `REQUIRES_PREREQUISITE` = CON→CON (103) + SPEC→CON (12); misconception relations `MISCONCEPTION_OF`/`WRONG_ANSWER_PATTERN`/`REMEDIATED_BY` = MIS→CON; `EXPLAINED_BY`/`RELATED_TO`/`COMMONLY_CONFUSED_WITH` = CON→CON).
- Node anchoring: every `node.specPoints` entry must resolve against the course's SPEC_POINT set (measured 77/77; MISCONCEPTION nodes are unanchored by design — they attach via edges).

### 2.3 Compiler gates (G6, fail closed)

| Gate | Enforces |
|------|----------|
| G6a | graph shape: `nodes`/`edges` arrays present; non-empty graphs' own `counts` block reconciles with its arrays (nodes/concepts/misconceptions/part_of_edges/semantic_edges) |
| G6b | node shape: code/family/title/provenanceTier/extractionPass required; family ∈ {CONCEPT, MISCONCEPTION}; duplicate code within course fails; tier ∈ vocabulary |
| G6c | edge shape: source/relation/target/provenanceTier/extractionPass required; relation ∈ the frozen upstream vocabulary (8 relations); tier ∈ vocabulary; duplicate triple within course fails |
| G6d | two-namespace endpoint resolution (kg_node codes ∪ course SPEC_POINT codes) |
| G6e | node.specPoints ⊆ course SPEC_POINT set |

### 2.4 Verification (V9) and reconstruction (R-extension)

- **V9**: independent re-derivation from the package's own `concept-graph.json` — row counts, per-row fields (nodes ordered by code, edges by edge_index), and the tier census must match the SQLite projection exactly; every edge endpoint must resolve against the package's OWN `kg_node`/`specification_point` tables.
- **R2/R3**: the G1–G6 gates re-run against the restored tree; semantic equivalence extends to kg_node/kg_edge/kg_node_specification_point counts.

## 3. Distribution and versioning

### 3.1 The bundle form (§7 realized)

A verified package directory may be wrapped as:

```text
syllabai-content-<scopeId>-<packageVersion>-<buildId12>.zip
└── syllabai-content-<scopeId>-<packageVersion>-<buildId12>/
    ├── MANIFEST.json
    ├── content/
    └── database/content.sqlite
```

The bundle wraps the package under a single top-level directory (the v0.1 §2 layout, named). Extraction must round-trip: every entry CRC-verified on read; extraction fails closed on any corruption.

### 3.2 Versioning semantics — no invented version axis

The name carries the three honest identity components: `scopeId` (which courses), `packageVersion` (which contract format), `buildId` prefix (which content — the deterministic digest over the sorted artifact digests). There is deliberately no human-bumped distribution version number: content identity is the buildId, which changes exactly when content changes; format identity is the packageVersion. A consumer can verify name ↔ MANIFEST consistency and buildId re-derivation independently (V8).

### 3.3 Determinism — two layers, stated exactly

- **Package layer** (v0.1 claim, unchanged): same source tree + same compiler → byte-identical `content.sqlite` and stable buildId. `MANIFEST.createdAt` is wall-clock informational, excluded from buildId.
- **Zip layer** (v0.2): same package directory → byte-identical zip. The writer is self-contained (no external zip binary): entries sorted by path, fixed DOS timestamp (1980-01-01 00:00:00), fixed deflate level, no extra fields, no comments. Zips of two independent compiles may differ in exactly the `MANIFEST.createdAt` bytes — content identity never differs. Byte-identity across zlib/toolchain versions is not claimed.

### 3.4 Scoped packages

`compile --courses=<slugs>` builds a bounded package over a course subset. Rules:

1. Unknown slugs fail closed; the scope is recorded (`scopeCourses`, deterministic `scopeId` = `scope-<sha8 of sorted slugs>`, `hub-corpus` for the full set).
2. **The verbatim-registry rule:** `courses.json` is copied unedited — scoping never fabricates a registry state that never existed. The difference is recorded as a finding.
3. Registry consistency under scope (R4): restored dirs ⊆ registry AND the excluded set == registry minus scope. Full scope keeps the v0.1 strict equality.
4. Course-agnostic artifacts (registry, pastpapers index/blueprints) are included in every package.
5. The bounded proof of this contract is the pilot-scoped package (`--courses=igcse-chemistry-19`): the only KG-bearing course — the "concrete bounded package" v0.1 §6 said would justify KG tables.

### 3.5 Import boundary (§12 restated)

Distributing or importing a bundle NEVER publishes content to learners and never confers serving eligibility. Import into a development/QA environment is a corpus-restore operation; learner serving remains governed by the same validated-content and paper/question serving boundaries used by PostgreSQL-backed production flows.

## 4. Schema additions (v0.2)

```text
kg_node                    (course_slug, code) PK — family, title, aliases, summary, provenance_tier, extraction_pass
kg_node_specification_point (course_slug, node_code, spec_code) PK
kg_edge                    (course_slug, edge_index) PK — source, relation, target, role, evidence_quote, provenance_tier, extraction_pass, derivation_method; UNIQUE (course_slug, source, relation, target)
```

MANIFEST additions: `scopeId`, `scopeCourses`, counts `kgNodes`/`kgEdges`/`kgNodeSpecMappings`/`kgCourses`. `package_metadata` additions: `scopeId`, `scopeCourses`, `kgProjection` (the non-authoritative pin).

## 5. Non-goals (inherited + extended)

Everything v0.1 §9 lists, plus:

- KG rows as authoritative curriculum/KG truth (they are a preserved-tier projection of the corpus's own review-pending state);
- corpus-wide KG compilation beyond what the corpus actually carries (the 48 empty graphs are projected as empty — this contract does not authorize generating graphs);
- delta/incremental distribution between package versions (a possible later gate; the v0.2 bundle is a full snapshot);
- cross-toolchain byte-identical zips.

## 6. Status

**ACCEPTED** (2026-09-29, operator forward-gate directive — chat bb263437, trace 1a0ea03c8fe4a9c1). Implemented in `SyllabAI/syllabai-hub` `tools/content-package/` (hub `7ed728e`, ADR-029 tranche 4.14): the full-corpus and pilot-scoped packages both compile, verify (V1–V9), restore (R1–R4, scope-aware), and are deterministic at both layers; tamper fails closed at both the artifact and zip layers; the whole chain runs in hub-ci as the selftest step. The KG projection is bounded honestly: it proves the projection POLICY and mechanism on the real corpus (one graph, 100% AI_SUGGESTED), not corpus-wide graph coverage — the architecture companion's broader claims (corpus-wide KG at scale, distribution infrastructure beyond the single-bundle form, canonical-store integration) remain staged there (PROPOSED) until separately proven.
