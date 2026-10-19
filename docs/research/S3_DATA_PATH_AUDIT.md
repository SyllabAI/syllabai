# Gate S3 — SpecificationPoint Data-Path Audit (the F.5 first action)

## Provenance

| Field | Value |
|---|---|
| Ordered by | Operator message "proceed with S3" (trace `1a1553a3531f7da1`, chat `1148fa2b`, 2026-10-19) |
| Mandate | §J.9 ruling **F.5**: SpecificationPoints become a first-class canonical data type **subject to completing the data-path audit first**; no silent mapping to an unrelated existing node type; the curriculum/KG authority must approve the representation and migration contract |
| Stack | Branch `s3-design` cut from `s1-policy-decision-prep` @ `bb778ee` (the S1 rulings of record) |
| Audited v2 head | `syllabai-v2` origin/main @ `89962a5d5443a0fcdcc5a098122b7474072a4d69` ("R0-AUTO receipt: PR #205 merged") — 105 commits past the S2-audited tip `ab6ba58`; all code citations below are line-verified at this head |
| Audited DB state | Neon project `billowing-cherry-15418366`, branch `production` `br-muddy-bar-a5huwldd`, endpoint `ep-ancient-cake-a52e4kfd`, db `neondb`, read at **2026-10-19 17:43:29Z** via the documented console-mirror + serverless `/sql` path |
| Access | Neon org API key re-delivered with the S3 order, staged 0600 outside repo, fp16 `4c2e12da872b6959` = the sealed org key of record |
| Read-only discipline | All DB statements SELECT/information_schema-only by construction. **Disclosure:** the attempted session-level `default_transaction_read_only=on` latch did **not** take effect over the `/sql` transport (`current_setting('transaction_read_only')` = `off`); read-only was maintained by query discipline only. Zero writes issued; audit script of record `scripts/s3-db-audit.js` (lane-side, not committed) |
| Method | Five layers audited first-hand: (A) graph-as-code assets, (B) loader/type mapping, (C) live DB, (D) API/Hub read paths, (E) anchor references. Every claim below is file:line- or row-verified at the heads above; nothing is carried over from S2 without re-verification |

**Sandbox-rollback disclosure:** the sandbox was recycled for the third time this engagement at the start of this round (canonical clone, `.creds`, insurance patches, and the four 2026-10-19 S1 worklog entries destroyed locally). Origin of record survived intact and was re-verified first-hand before any work (`s1-policy-decision-prep` @ `bb778ee` on remote); the worklog entries were re-filed per the established precedent.

---

## §1 Executive verdict

**F.5's precondition is now measured, and the ruling's suspicion is confirmed empirically on all three representations at once.** SpecificationPoints are real, richly structured, and heavily consumed — but they exist **nowhere as a first-class type**. They are silently collapsed into `SUBTOPIC` at every write path, the DB's own check constraint makes the collapse mandatory (`ck_node_type` has six values, `SPEC_POINT` is not among them), and the anchor chain that the verification-evidence transfer gate depends on (`question_spec_points.spec_point_node_id`, 7,351 live rows) binds to nodes whose type is indistinguishable from genuine sub-topics. Identity itself is fragmented across at least four formats (`4CH1-1.1` codes, `knowledge_nodes` UUIDs, SME/content-package `spcpt_*` ids, Hub `CurriculumNode` family strings) with no code-level crosswalk except one local validation in the Hub content-package tooling.

**The audit does not fix any of this.** Per F.5 it measures the path, proposes the representation + migration contract shape for the curriculum/KG authority's approval (§7), and records what S3 still owes (§8). No code, schema, or seed was changed by this lane.

## §2 Layer A — graph-as-code (the repo-pinned source)

Six YAML assets in two directories carry the knowledge graph as settled bytes, each pinned by SHA-256 at load time (`apps/api/src/services/teacher/snapshot.ts:47-68`):

| Asset | Entries | Identity | Notes |
|---|---|---|---|
| `apps/api/src/services/teacher/concept-graph/specification_points.yaml` | **182 (meta `counts.spec_points: 182` — matches the real entry count, verified by parse)** | `code`, e.g. `4CH1-1.1` | `official_wording` verbatim from the Edexcel 4CH1 spec; `section`/`subsection`/`global_order`; `applicability` (double-award rule, papers); `provenance` tier `RULE_DERIVED`; `damage_flags` |
| `teacher/concept-graph/topics.yaml` | 32 | `code`, e.g. `4CH1-S1-a` | each subsection lists its `spec_points` codes verbatim |
| `teacher/concept-graph/relationships.yaml` | 210 | edge list | carries exactly 182 SP→subsection + 28 subsection→section PART_OF edges (loader contract) |
| `learner-me/concept-graph/concepts.yaml` | 193 | `code` | T-C11 settled concepts/misconceptions; some carry their own `spec_points` references |
| `learner-me/concept-graph/concept_edges.yaml` | 488 | edge list | validated semantic edges |
| `learner-me/concept-graph/practicals.yaml` | 12 | `code` | required practicals anchored on a spec point |

The loader's store-fact count contract (4 sections / 28 subsections / 182 spec points / 12 practicals / 193 concepts / 211 anchor edges / 272 validated edges, exclusions by count) is documented at `snapshot.ts:21-44` and fails loudly on drift — **this layer is in good shape**: identity is a stable code, provenance is per-row, bytes are pinned.

**Gap A-1 — coverage is single-subject.** The graph-as-code store covers 4CH1 (Chemistry) only. The DB (Layer C) now also carries 4MA1 (188 spec-shaped rows) and 4PH1 (195), activated 2026-10-19 — and **no YAML for either subject exists anywhere in the repo** (verified: zero hits for `4MA1`/`4PH1` in any non-receipt YAML). Their source of truth is the ingestion bundle pipeline (Layer B, path 2), whose inputs are not repo-pinned bytes. A first-class SpecificationPoint type that only models the chemistry path would silently strand two of three live subjects.

## §3 Layer B — loader/type mapping (two seed paths, one silent collapse)

**Path 1 — graph-as-code seed (chemistry).** `apps/api/src/services/teacher/concept-seed.ts` (the `concept-graph/activate` path) writes `knowledge_nodes` with this family→`node_type` mapping, line-verified at `89962a5`:

| Source family | Written node_type | Lines |
|---|---|---|
| section | `UNIT` | :194-196 |
| subsection | `TOPIC` | :201-203 |
| **spec point** | **`SUBTOPIC` — the silent mapping** | **:207-212** |
| required practical | `SUBTOPIC` | :214-218 |
| concept / misconception | `CONCEPT` / `MISCONCEPTION` | :222-227 |

The collapse is doubly locked: the code has no alternative (`ck_node_type` forbids `SPEC_POINT`), and the row carries no field that distinguishes a spec-point `SUBTOPIC` from a genuine sub-topic — differentiation survives only in the code pattern (`4CH1-1.1` vs `4CH1-S1-a`) and in edge provenance strings ("spec structure (spec point)").

**Path 2 — ingestion bundle seed (maths, physics).** `apps/api/src/services/curriculum/bundle-seed.ts` maps bundle families to the same six types and documents the collapse **by design**: "bundle SPEC_POINT (195, code \"1.1\") → SUBTOPIC `4PH1-1.1`" (`bundle-seed.ts:38`; header rationale at :22-50). This path feeds `4PH1-2017` and `4MA1-2016` (both ACTIVE since 2026-10-19). Its inputs are content bundles, not the repo's pinned YAML — so Layer A's byte-pinning guarantees do not apply to two of three live subjects.

**No `SPEC_POINT` node type exists anywhere in the write path.** The S2-recorded anchor still holds at the current head: `packages/db/src/schema/schema.ts:33` — `ck_node_type` = `{SUBJECT, UNIT, TOPIC, SUBTOPIC, MISCONCEPTION, CONCEPT}`.

**Verification-evidence anchors re-verified at `89962a5`** (`apps/api/src/services/learner-model/verification-evidence.ts`, 158 lines): `answerExposedBeforeAttempt` "exposed before this attempt" :35-36; `specificationPointIds` "Canonical SpecificationPoint ids" :39-40; `minimumTransferDelayMs` versioned experiment parameter :43-50; `masteryMutation: "NONE"` :85, :93 (and throughout); the attempt-local law :89-104 — **the F.1(b) contract revision remains unimplemented, exactly as §J.9 recorded** (S3/S4 scope); transfer-gate overlap :123-138. Drift vs the S2 record (@ `ab6ba58`) is line-number-only.

## §4 Layer C — the live database (2026-10-19 17:43Z, read-only)

| Measure | Result |
|---|---|
| `knowledge_nodes` by type | SUBTOPIC **583**, CONCEPT 167, TOPIC 100, MISCONCEPTION 30, UNIT 19, SUBJECT 4 (total 903) |
| Spec-point-coded rows by subject | `4CH1-` **182**, `4MA1-` **188**, `4PH1-` **195** — **every one typed `SUBTOPIC`** (565 total) |
| Sample row | `4CH1-1.1` → `node_type=SUBTOPIC`, title = the official wording, `VALIDATED`, provenance `spec:4CH1-2017\|tier:RULE_DERIVED\|gate:operator-git-PR…` |
| `ck_node_type` (live) | six values, no `SPEC_POINT` — matches `schema.ts:33` |
| `question_spec_points` | **7,351 rows; 7,351 (100%) join to `SUBTOPIC`-typed nodes** — the silent collapse is load-bearing for the question→spec-point anchor chain |
| Anchor edges into spec points (PART_OF, chemistry) | 223 |
| `knowledge_edges` by relation | PART_OF 913, REQUIRES_PREREQUISITE 213, REMEDIATED_BY 25, WRONG_ANSWER_PATTERN 24, EXPLAINED_BY 11, MISCONCEPTION_OF 6, RELATED_TO 2, COMMONLY_CONFUSED_WITH 2 |
| `curriculum_versions` | 8 total: **ACTIVE** `4CH1-2017` (2026-09-13), `4PH1-2017` (2026-10-19), `4MA1-2016` (2026-10-19); DRAFT ingest variants ×4; ARCHIVED `IAL-CHEM-2018` |
| `teaching_coverage` | table exists, **0 rows** (the teacher coverage family has anchors but no data yet) |

**Moving-target disclosure:** the DB changed **today** (two new ACTIVE curricula). Row counts above are a snapshot, not an invariant; the migration contract must be idempotent against a live, growing graph.

## §5 Layer D — read paths (three subsystems, three representations)

The same curriculum is served to consumers through **three different representations**, only one of which preserves spec-point identity:

1. **Teacher/class KG routes** (DB-native): `knowledge_nodes`/`knowledge_edges` as seeded — spec points are `SUBTOPIC` rows.
2. **Tutor spec-boost** (`apps/api/src/services/tutor/spec-boost.ts:30`): reads the graph-as-code YAML **directly** via `loadConceptGraphSnapshot` — bypasses the DB entirely; chemistry-only.
3. **Hub spec-tree + content packages** (`apps/hub/src/lib/spec-tree.ts:104,123`; `contracts.ts:69`): `CurriculumNode.family === "SPEC_POINT"` is a live filter — the Hub's content-package representation **keeps the family**, with its own `spcpt_*` anchor ids (`contracts.ts:139,158,236`) and one real validation: note codes must be in the course's SPEC_POINT set (`tools/content-package/compile.ts:272`).

**Consequence:** the Hub "knows" spec points as first-class objects while the API's DB cannot express them. Any verification-evidence feature that crosses this seam (e.g., a transfer assessment anchored to a spec point) inherits whichever representation its caller used, and nothing reconciles the three.

## §6 Layer E — anchor references (what the evidence gate would hang on)

| Reference surface | Mechanism | Integrity guarantee |
|---|---|---|
| Question ↔ spec point (DB) | `question_spec_points.spec_point_node_id` FK → `knowledge_nodes(id)` (`schema.ts:811-835`; role PRIMARY/SECONDARY; AI/HUMAN_VALIDATED) | Enforces *existence of a node*; **cannot** enforce *spec-point-ness* (no type to enforce); 7,351 live rows, all SUBTOPIC-typed |
| Teacher coverage ↔ spec point (DB) | `teaching_coverage_events.spec_point_node_id` + `teaching_coverage.spec_point_node_id` FKs (`schema.ts:1246-1262,1300-1315`) | Same ceiling; tables currently empty |
| Revision notes ↔ spec codes (DB) | `revision_notes.spec_point_codes` text + `spec_map` jsonb (`schema.ts:689-690`) | Free-text codes, no FK at all |
| Verification evidence ↔ "canonical SpecificationPoint ids" (API) | `verification-evidence.ts:39-40` — plain `string[]`, compared for set overlap at :123-138 | **No validation of any kind found**: no lookup against `knowledge_nodes`, the YAML snapshot, or the Hub curriculum; format undocumented in code (codes? UUIDs? `spcpt_*`?) |

**The F.3 binding requirement ("transfer must be tied to the relevant canonical SpecificationPoint") currently has no enforceable substrate on the API side** — the field exists, the overlap logic exists, but "canonical" is not yet a property the system can check.

**Identifier fragmentation of record:** (1) graph-as-code / DB `code` — `4CH1-1.1`; (2) DB surrogate — `knowledge_nodes.id` UUID; (3) SME/content-package — `spcpt_*`; (4) Hub `CurriculumNode` — family + code + parents. Only conversion (1)↔(2) is mechanically derivable today (same row); (3) is foreign.

## §7 Representation + migration contract — skeleton for the curriculum/KG authority

Per F.5 this audit proposes; **only the curriculum/KG authority approves**. The skeleton below is the minimum the measured path forces:

1. **Type**: add `SPEC_POINT` to `ck_node_type` (DB) and to the seed mappings' target vocabulary. `node_type` is `varchar(20)` — the value fits; the constraint is the only blocker.
2. **Dual-write + backfill, never rewrite in place**: new writes carry `SPEC_POINT`; a one-time idempotent backfill retypes the 565 spec-shaped rows (code-pattern predicate `^[0-9A-Z]+-[0-9]` intersect provenance `spec:|bundle` — the predicate must be authority-approved before it touches a row) and leaves genuine `SUBTOPIC` rows untouched. The 12 chemistry practical `SUBTOPIC` rows and any non-spec SUBTOPIC rows must remain exactly what they are.
3. **Canonical id**: the `code` (`4CH1-1.1`) is the natural canonical key (stable across all three representations; already the YAML identity; already what teachers see). `knowledge_nodes.id` remains the FK target; `spcpt_*` must gain an authority-owned crosswalk, not a silent alias.
4. **Close the anchor-type hole**: after retyping, `question_spec_points`/`teaching_coverage_*` FKs gain a companion check (node_type = 'SPEC_POINT') — this is the change that makes "canonical" checkable, per F.3/F.5.
5. **Both seed paths converge**: `concept-seed.ts` and `bundle-seed.ts` must emit `SPEC_POINT` from the same authority-approved mapping; the bundle path (no pinned bytes) needs a source-registration step so maths/physics spec points acquire provenance equal to chemistry's.
6. **One read-path truth**: the Hub's `family: "SPEC_POINT"` view and the API's DB view must be formally linked (single migration source), and `verification-evidence.ts`'s `specificationPointIds` must be validated against the canonical registry at intake.

## §8 What S3 still owes after this audit

This round delivered the F.5 first action only. S3 remains open, owing: (a) the **classifier redesign design** implementing the §J.9 rulings — F.1(b) retake law (per-learner per-question exposure chronology via D.4 event instants + question-identity comparison + new test pins, superseding the attempt-local law at `verification-evidence.ts:89-104`), F.2 past-failure exclusion from transfer baselines, F.4's pre-submit/post-submit split (D.6 already revised of record); (b) the **S2 §7 twelve-prerequisite crosswalk** against the now-decided policy; (c) the **transfer-gate design** per F.3 (distinct question + no assistance/exposure + delay; 24h/7d as S9 evaluation candidates); (d) the **producer design** for the 3/8 NO_PRODUCER_FOUND families (assistance / exposure / transfer) that S4 will build; (e) authority review of §7 — the migration contract cannot be executed before it.

**Stop state (S3, 2026-10-19):** the F.5 data-path audit is complete of record (this document): silent `SPEC_POINT → SUBTOPIC` collapse measured on both seed paths and in the live DB; three-representation split and anchor-type hole documented; representation + migration contract skeleton staged for the curriculum/KG authority. Classifier redesign, S2-crosswalk, transfer-gate and producer design are **not started**. No code, schema, seed, or policy text was changed by this lane; the DB was touched read-only (SELECT-only; disclosed latch limitation).
