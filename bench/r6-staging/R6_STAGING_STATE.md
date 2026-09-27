# r6 staging unit — READY (staged pre-flip, 2026-09-28)

The r6 gate is the operator/teacher **card validation wave** (298 T-C27 cards; re-probed
NOT landed 2026-09-28 four times). Per the operator directive ("proceed with Next: the
small r6-staging unit ... ready to execute the moment you flip the card wave", trace
`1a0e4325cefc7b51`), the unit is STAGED NOW so the real freeze at the flip is execution,
not engineering — the r4 pre-flip staging precedent.

## What is in place

| Piece | State | Where |
|---|---|---|
| §8(d) data substrate | CLOSED 2026-09-27 (Task 43) | records `94d0d405c` `bench/evidence/chunk-sp-substrate-2026-09-27/` |
| Handoff spec (accessor/scorer/export contract) | COMMITTED 2026-09-28 (Task 44) | records `16584c1de` `bench/S8D_SCORING_HANDOFF_2026-09-28.md` |
| Core foundation: loader + accessor + scorer + tests | LANDED, CI green (Task 45) | core `c91372c` (branch CI `36341510062` SUCCESS) |
| **Core run-class wiring (this unit)** | **LANDED, CI green** | core `670423a` + `b45b5d6` (null-guard fix; branch CI `36343466505` SUCCESS after the ArmAReplayIT null-snapshot catch; main CI `36343727171` dispatched) |
| **snap-005 exporter + drift gate (this unit)** | **STAGED, dry-run ALL PASS** | records (this commit) `bench/r6-staging/snap005_export.py` + `dry_run_2026-09-28.log` |

## What the wiring does (core `b45b5d6`)

- `Run003B`/`Run004A`/`Run005C` score §8(d) via `ChunkSpecHvResolution` **only when the
  loaded snapshot carries `chunk_spec_hv.json`** (`chunkSpecHvPresent()`). On every frozen
  snapshot (snap-001..004) and the seeded-corpus replay mode (`ArmAReplayIT`, `snapshot=null`)
  the recorded NOT SCOREABLE behavior is byte-identical — the CI run that failed on the
  missing null-guard proves the IT exercises exactly that path.
- Arm B scores its served (VALIDATED-served) view; arms A/C score BOTH views
  (served ALL-denominator = the ruling-1 gate input, compliant alongside). §8 gate line
  `d_spec_resolution` flips NOT SCOREABLE → SCORED with the first-scoreable-run baseline
  note (no promotion claim on (d) at r6).
- Determinism: second-pass §8(d) recomputation folded into each runner's fail-closed
  byte-identical aggregate check.

## What the exporter does (`snap005_export.py`)

- Producer queries preserved **verbatim** from `snap004_export.py`; comparison base
  snap-003 → snap-004.
- Chunk lineage: snap-004's 3,831 refs carried with IDENTICAL contents/kinds/spec_codes;
  only `paper_state` flips (SNAP5-F1, captured at run time — expected at the flip: the
  card wave) + metadata-only paper_code stamps (SNAP5-F2).
- **SNAP5-F4 notes-axis inclusion**: the 350 EXTERNAL_NOTES chunks join the corpus
  (additive; SUGGESTED = production truth, so VALIDATED-only serving views are unchanged —
  they exist so the §8(d) chunk_ref join and the ALL-denominator resolution view work).
- **SNAP5-H1**: `chunk_spec_hv.json` copied BYTE-IDENTICAL (sha256-pinned to the
  records-committed artifact) + manifest-pinned for the fail-closed loader.
- **DRIFT GATE (fail-closed)**: all 210 HV mappings re-verified over the frozen chunk
  bytes against the pinned resources store (`e8b58a7109104bb7` @ `1245df009`); recomputed
  anchor kinds must equal the recorded census (205 CLEAN / 4 MULTI / 0 SPAN / 1 MISS).
- Dry-run (2026-09-28, pre-flip): **ALL VERIFICATIONS PASS** — 4,181 chunks
  (3,831 + 350 notes), 0 flips (expected pre-wave), drift gate 0 divergences.

## Remaining AT THE FLIP (after the operator card wave lands — AT_FLIP_RUNBOOK)

1. Re-probe the gate; assert the wave landed (298 cards VALIDATED — no agent-asserted
   validation, ever).
2. Run `snap005_export.py` for real (it captures SNAP5-F1 flips at run time) → review →
   freeze commit `evidence/bench-001/snapshots/snap-005/` (+ FREEZE_RECORD.md).
3. gold re-pair: gold-v3 class files BYTE-IDENTICAL, only the manifest snapshot pins move
   to snap-005 (the validator's designed mechanism; gold_check must PASS).
4. `preload-r6` (production-derived chunk-vector mirror incl. the notes chunks if they are
   embedded by then; 0-chunk-API-calls preload pattern).
5. `ops-{embed-backfill,run003b,run004a,run005c}-r6.yml` (core pin = main at freeze time).
6. Dispatches in runbook order → record runs → R6-GENERATION-NOTES + §8 verdict.
