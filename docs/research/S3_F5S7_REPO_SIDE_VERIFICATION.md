# F.5 §7 Pre-Execution Verification Battery — Repo-Side Report (credential-free half)

| Field | Value |
|---|---|
| Mandate | Operator ruling F.5 §7 (trace `1a1582488a8c61ed`, 2026-10-20): contract approved IN PRINCIPLE, execution conditional on this battery |
| Round trace | `1a158320d2c0d41d` ("Proceed with next") |
| Scope this report | Repo-side, read-only, zero credentials: seed paths, loader, schema anchors, predicate dry-run, rollback/idempotency plan |
| DB-gated remainder | 565-row census re-run, provenance-half intersect, 18 non-spec SUBTOPIC identification, DRAFT-variant disposition — need read-only DB credential |
| Verification head | `syllabai-v2` origin/main @ `ad64753260d3865ff1851444e825ff5cef82f40e` (fresh blobless clone; audit head `89962a5`; S3 citation head `3a05332`) |
| Drift check | 32 commits `3a05332..ad64753`; **zero touch** any audited path (concept-seed.ts, bundle-seed.ts, schema.ts, snapshot.ts, verification-evidence.ts, both YAML dirs, spec-boost.ts, spec-tree.ts) — audit citations hold verbatim |
| Dry-run artifact | lane-side script (disclosed, not committed per lane convention) — 15/15 PASS, full output reproduced in §2 (below) |

## 1. Line-verified at the current tip

| Of-record claim (audit §2-§6) | Status at `ad64753` | Evidence |
|---|---|---|
| `ck_node_type` = 6 values, no `SPEC_POINT` | CONFIRMED | `packages/db/src/schema/schema.ts:33`; plus zero DDL in the 32-commit range (e7a6977 receipt: "zero DDL") |
| concept-seed path 1: spec point → `SUBTOPIC` silent mapping | CONFIRMED | `concept-seed.ts` spec-point loop writes `"SUBTOPIC"` (audit :207-212 window); practical → `SUBTOPIC`; section→UNIT, subsection→TOPIC unchanged |
| bundle-seed path 2: SPEC_POINT → `SUBTOPIC` by design | CONFIRMED + **ENRICHED** | header documents THREE new subtopic shapes (letter/dotted/placeholder) AND the **4MB1 ALNUM spec-point law** (`4MB1-S1-1A`) — post-audit addition, see finding V-2 |
| loader SHA-pin + count contract | CONFIRMED | `snapshot.ts` pins all six YAMLs by SHA-256 (constants :55-66); count contract in the doc comment |
| `specificationPointIds` unvalidated `string[]`; delay param no-default | CONFIRMED | `verification-evidence.ts:39-40,43-50` — matches operator DP-5 ruling (fail-closed, explicit required value) |
| Transfer gate admits assisted priors (PF-1) | CONFIRMED | prior gate checks exposure + `UNKNOWN` only; HINT/STEP_BY_STEP/TEACHER_SUPPORT priors admitted — the enactment S4 owes |
| `question_spec_points` FK has NO type companion check | CONFIRMED | `schema.ts:811-835` — FK → `knowledge_nodes.id`, role/state checks only; anchor-type hole intact |

## 2. Predicate dry-run results (15/15 PASS)

Predicate of record (audit §7.2, approved in principle): code-pattern `^[0-9A-Z]+-[0-9]` INTERSECT provenance `spec:|bundle`.

| Check | Result | Detail |
|---|---|---|
| C1 — pinned bytes == repo bytes (all 6 YAMLs) | PASS | SHA-256 of repo files equal `snapshot.ts` constants exactly (b1fea699…, a7b14cbd…, b3b75292…, 24fa91ac…, 8a651dd9…, e53e5f87…) |
| C2 — spec-point census (chemistry) | PASS | 182 entries == `meta.counts.spec_points: 182`; **182/182 match the predicate**; all `4CH1-*`; C-suffix law present (`4CH1-1.5C` etc. — match ✓) |
| C3 — 12 chemistry practicals | PASS | codes of record **`4CH1-PR-01…4CH1-PR-12`**; **0/12 match the pattern** — excluded by the code-pattern half ALONE, before any provenance logic. Operator's "confirm their identities" condition: satisfied at identity level |
| C4 — genuine non-spec rows | PASS | 4 topics + 28 subtopics (`4CH1-S1…`, `4CH1-S1-a…`) and 193 concepts (`4CH1-CON-*`) — **0 matches** |
| C5 — edge-shape regressions | PASS + 1 GAP | `4PH1-1.2P` matches ✓; TOPIC S-form `4MA1-S1-1.1` excluded ✓; **`4MB1-S1-1A` (dormant ALNUM law) does NOT match — recorded gap V-2** |

## 3. Findings for the authority

**V-1 (positive):** On the chemistry path the predicate is provably safe and complete against the pinned bytes: retypes exactly 182 spec-point rows, cannot touch practicals (pattern-excluded), topics, subtopics, or concepts. The practicals' identity confirmation required by your ruling is discharged at the repo level (`4CH1-PR-01..12`).

**V-2 (predicate-coverage gap):** `bundle-seed.ts` (post-audit) carries the 4MB1 ALNUM spec-point law: codes `4MB1-S1-1A`…`10N` (digit+letter). The pattern predicate can NEVER match these — dormant today (no 4MB1 rows; audit census: 565 = 182+188+195), but the law is live in the seeder. **Recommendation:** do not widen the regex (width invites false positives); instead bind bundle-subject retyping to the contract's step-5 **source-registration registry** (authority-approved mapping), which covers 4MB1 on activation and gives maths/physics provenance parity in the same stroke. Chemistry backfills by predicate; bundle subjects backfill by registry.

**V-3 (provenance half is DB-gated):** the intersect `spec:|bundle` is verifiable only against live rows. Chemistry sample of record shows `spec:4CH1-2017|tier:RULE_DERIVED|gate:operator-git-PR…`. The bundle-row provenance shape must be confirmed in the census before the predicate is frozen.

**V-4 (18 residual SUBTOPICs):** audit census: 583 SUBTOPIC − 565 spec-coded = **18 rows** that must remain SUBTOPIC. Their identity is a DB-census deliverable (they sit outside the repo's pinned bytes; likely legacy/ARCHIVED-curriculum rows).

**V-5 (canonical-ID stability — your condition):** structurally satisfied by construction. The backfill mutates `node_type` ONLY; `knowledge_nodes.id` (UUID, the FK target of `question_spec_points.spec_point_node_id` etc.) and `code` (UNIQUE via `uq_knowledge_node_code`) are untouched — zero orphaning is a property of the migration shape, not a hope. Census will verify 7,351/7,351 anchor joins post-retype.

## 4. Idempotency + rollback plan (5 gates, each independently reversible)

| Gate | Action | Idempotency | Rollback |
|---|---|---|---|
| G1 | Additive constraint: extend `ck_node_type` with `'SPEC_POINT'` | Re-run = no-op | Drop back to 6-value constraint (legal ONLY while zero SPEC_POINT rows exist — ordering law) |
| G2 | Deploy seed-path convergence (both seeders emit `SPEC_POINT`) per DP-3's dedicated-table ruling context | New rows land SPEC_POINT | Redeploy prior build; backfill logic absorbs any mixed-type rows |
| G3 | **Backfill** (batched, transactional): retype WHERE `node_type='SUBTOPIC'` AND code-pattern AND provenance-intersect (+ registry list for bundle subjects); **receipt-first**: capture the exact affected id list into a migration receipt BEFORE commit | Re-run matches nothing (node_type filter); `uq_knowledge_node_code` blocks duplicate risk; batched row-locks keep the live graph serving | **Reverse UPDATE keyed on the receipt id list ONLY — never re-derived by pattern** (protects rows legitimately written SPEC_POINT by the G2 path mid-flight) |
| G4 | Close the anchor-type hole: companion check `node_type='SPEC_POINT'` on `question_spec_points` (+ empty `teaching_coverage_*`) — only after census shows 565/565 retyped, 18/18 untouched, 7,351/7,351 joins intact | Re-run = no-op | Drop the check; zero data impact |
| G5 | Source-registration step for bundle subjects (registry = authority-approved mapping; covers 4MB1) | Registry rows additive | Remove registry entries; no graph data touched |

Inter-gate verification battery (after G3, before G4): type census by subject (expect 565 SPEC_POINT + 18 SUBTOPIC + all other types unchanged), anchor join integrity (7,351/7,351 — count re-based at execution time; the graph is live and growing), Hub spec-tree probe (`family: "SPEC_POINT"` view unchanged), spec-boost probe (YAML path — never touches DB, must be byte-unaffected).

## 5. DB-gated remainder (read-only credential needed)

1. 565-row census re-run at current live head (graph moved: CIE phase 3 landed 44 Cambridge bundles — hub-plane, but census must re-baseline).
2. Provenance-shape confirmation for bundle rows (V-3).
3. Identification of the 18 residual SUBTOPICs (V-4).
4. DRAFT ingest-variant disposition (retype-all-spec-shaped vs ACTIVE-only — recommendation: retype all spec-shaped rows regardless of curriculum state; predicate is state-agnostic).
5. Bundle-provenance sample extraction for the registry design (V-2).

## 6. Stop state

Repo-side battery COMPLETE: predicate verified safe-and-complete on the pinned chemistry path; the 12 practicals' exclusion proven at the code level; canonical-ID stability shown structural; rollback plan receipt-first. One predicate-coverage gap recorded (V-2, dormant) with a recommended resolution via the registry. Execution remains locked pending: the DB-gated census half + your explicit go (per your qualification, approval ≠ execution order).
