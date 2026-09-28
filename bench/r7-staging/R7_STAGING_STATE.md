# r7 staging unit — the serving-set eval generation (REGISTERED 2026-09-28)

> **EXECUTING 2026-09-28 (same day):** the notes-axis promotion landed
> mid-staging (records `9ea54e1`, operator trace `1a0e88af08e12df5` "pursue
> (a)") — **scope UPDATED**: snap-006 captures BOTH operator decisions (the
> flagged3 flip 3 EQ FLAGGED→VALIDATED + the notes-axis promotion 350 EN
> SUGGESTED→VALIDATED); the serving pool this generation scores is
> **612 → 965** (not the 612 → 615 this file was registered with — the plan
> text below is preserved as registered; expectations in the freeze artifacts
> govern). Freeze executed FOR REAL: ALL VERIFICATIONS PASS (4,181 chunks,
> 353 up-flips, 0 down-flips, zero content/kind/spec drift, drift gate
> 205/4/0/1, census EQ 309V/747S/0F + EN 350V → gate-eligible 965) —
> `evidence/bench-001/snapshots/snap-006/` + `bench/inputs/snapshot-r7/`.
> gold-v5 re-paired (set byte-identical; `gold_check` PASS, all 120 anchors
> resolve into snap-006) → `bench/inputs/gold-r7/`. preload-r7 staged from the
> BYTE-IDENTICAL frozen r6 vector rows (production embeddings unchanged — the
> promotions touched states/stamps only; per-row deterministic-id + coverage
> 4,181/4,181 + qid 120/120 guards PASS) →
> `bench/inputs/embeddings/preload-r7/`. r7 workflows committed. Dispatches:
> `ops-run003-b-r7` then `ops-run004-a-r7` (A consumes B's results), core pin
> `d9cb3ddcf2`.

**Commission.** Operator directive **"Proceed with (1) eval"** (IM trace
`1a0e88bb060ed3b5`, 2026-09-28) executing item **(1)** of the corrected standing
menu recorded in `evidence/serving-rev2-flipback-refutation-2026-09-28/REPORT.md`:
**"Run the bench harness (run-004-a pattern) against today's serving set"** —
recommended, zero production writes — to answer the decision question
*"does what serves today score bridge-quality?"* and thereby gate menu item (2)
(the eval-gated 1→2 re-stamp) with data instead of assumption.

## Reconciliation recorded up-front (before any result exists)

The refutation report's line "the 09-25/26 rev1-stamped VALIDATED corpus … has
NEVER been eval'd" is **imprecise and is corrected here before the run**: the
r6 recorded generation (`run-004-a-r6`, core pin `05f262169`, gold-v4, snap-005)
already served and scored the post-card-wave VALIDATED corpus through the exact
production gate — arms A/C served 671 EXTERNAL_QUESTIONS refs, "every one
VALIDATED" (R6-GENERATION-NOTES), and the r6 served view at that pin is the
T-C07-scoped, T-C05/T-C20 VALIDATED-only surface (code-verified in
`Run004A.java` javadoc + evaluation_contract). What r6 did **not** and could not
evaluate is the **post-flagged3-flip serving set**: the operator's own
`FLAGGED → VALIDATED` decision on cards #207/#278/#291 (batch
`0d5e4c4a-cacc-454c-9dfe-5983e1f11661`, decision trace `1a0e7865c3b35715`,
executed 2026-09-28T11:32:05Z, independently verified @ records `35b5166`) which
grows the VALIDATED serving pool **612 → 615**. The r7 generation freezes
**today's** production truth (snap-006) and records the eval over it — the
literal commission — with the r6↔r7 delta accounted in the run report.

## Plan (each step precedent-shaped; the r6 generation is the template)

1. **snap-006 freeze** — `bench/r7-staging/snap006_export.py`, adapted from the
   snap-005 provenance exporter (`evidence/bench-001/snapshots/snap-005/snap005_export.py`,
   the post-F5/F6 amended bytes) with ALL producer queries preserved verbatim;
   comparison base advances snap-004 → **snap-005**; expected delta vs snap-005:
   **exactly the 3 flagged3 up-flips** (FLAGGED→VALIDATED, EXTERNAL_QUESTIONS) —
   everything else (chunk row set, contents, spec codes, spec_points,
   graph_edges, misconceptions, question_anchors superset, concept_attachments,
   graph_code, HV projection + drift gate) byte-identical or FAIL. Reads
   production **SELECT-only** (`set_session(readonly=True)`, rolled back) via
   `scripts/.render_env.json` (the sanctioned Render LIST form).
   Dependencies byte-verified before use: resources store
   `graph/igcse-chemistry/spec_chunk_mappings.yaml` @ `1245df009` (sha256_16
   `e8b58a7109104bb7`, blob `9247ccdf…` re-verified at download),
   `graph/igcse-chemistry/concepts.yaml` (`24fa91ac…`),
   `scripts/c19_promotions.yaml` (transitively verified by the
   concept_attachments byte-identity anchor); HV projection `b5b20ffa…`.
2. **Stage `bench/inputs/snapshot-r7`** from the frozen staging tree
   (records-commit shape identical to snapshot-r6).
3. **Stage `bench/inputs/embeddings/preload-r7`** — the vectors are
   **unchanged in production** since the snap-005 freeze (no ingest after the
   09-26 card import; the flagged3 flip touched only document/chunk validation
   states, never embeddings), so preload-r7 = the frozen r6 artifact's vector
   rows (byte-copy) with the manifest **re-pinned to snap-006 file hashes** and
   every row's `content_sha256` guard re-verified against snap-006 chunk bytes
   by a fail-closed staging script (any drift = abort + fresh SELECT-only
   production vector mirror instead). Query vectors are the frozen r6 rows —
   gold-r7 class files are byte-identical to gold-r6 (same validator mechanism),
   so the compute-once-freeze-forever doctrine forbids re-burning API calls for
   byte-identical texts. Zero embedding API calls in this generation unless a
   guard fails.
4. **gold-v5 re-pair → `bench/inputs/gold-r7`** — set carried byte-identical;
   snapshot pairing pins re-issued against snap-006 per the §3/§4 set+snapshot
   pair discipline (the gold-v3→v4 mechanism; gold_check PASS + selftest).
5. **r7 workflows** — `ops-run003b-r7` then `ops-run004a-r7` (run004a consumes
   run-003-b-r7's results for the cross-arm context table), workflow_dispatch
   only, benchmark-only, disposable pgvector:pg17 service container, core pin =
   **origin/main at the staging commit** (d9cb3dd at registration; NOTE: the
   delta 05f262169..d9cb3dd touches `ChunkVectorRepository`/`ContentDocumentController`
   via c37582d hygiene tranche — verified SQL-emission-identical for every
   Document.Kind, serving semantics unchanged; recorded in the run report).
6. **Run records** — `evidence/bench-001/runs/run-003-b-r7/` +
   `run-004-a-r7/` (results.json + RUN_REPORT.md + SHA256SUMS), a generation
   report reconciling r6 ↔ r7 (the 612→615 delta per-query), the
   bridge-quality verdict on the corrected menu question, and the item-(2)
   re-stamp gate input. TODO row + worklog closeout.

## Honest scope / boundaries

- Production: **SELECT-only** reads (readonly session, rollback); zero writes to
  any production table; zero serving-semantics changes; no constant flips; no
  re-stamp — menu items (2)/(3) remain operator-gated and are NOT part of this
  commission.
- Dispatches: benchmark-only `workflow_dispatch` workflows on the records repo,
  the established r5/r6 pattern; disposable containers; no production secrets
  involved beyond the exporter's sanctioned SELECT path.
- If dispatch credentials prove insufficient, the generation lands
  **staged-and-handoff** (the flagged3-kit pattern: one dispatch away, RUNBOOK
  recorded) — never faked.
- No overlap with open lanes: locks empty at registration; psaxis/ADR-029 lanes
  touch neither bench inputs nor the serving surface.
