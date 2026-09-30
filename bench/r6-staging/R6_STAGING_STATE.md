> **EXECUTED 2026-09-28 (same day):** the gate discharged (operator wave landed, run a5d13c0a…); steps 1-6 complete — snap-005 frozen (ab600e18f1), gold-v4 (c8ae9e6c1c), inputs + workflows (60f57e87b3, f7bb66e641), 4/4 dispatches SUCCESS, run records + R6-GENERATION-NOTES.md under evidence/bench-001/runs/. The staging record below is preserved as history.

# r6 staging unit — EXECUTING (the gate discharged 2026-09-28)

**Status 2026-09-28 (records `ab600e18f1` + this commit): the r6 gate — the operator/teacher
card validation wave — LANDED 2026-09-28 ~08:03Z.** The operator (Nawaf Al Hussain Khondokar)
completed the 298-card review sheet (sha256 `89c07146…`, delivered via their own GitHub upload)
and the recorded decisions — 295 VALIDATE + 3 FLAG (#207/#278/#291) — were applied VERBATIM in
one fail-closed transaction (content_review_audit run `a5d13c0a-2503-4d06-bb14-9397e9a1cf37`,
298 operator-labeled rows). No agent-asserted validation anywhere. The earlier
WAITING_FOR_GENUINE_TEACHER_VALIDATION marker is therefore DISCHARGED — the wave is genuine,
operator-named, audit-evidenced.

At-flip execution state (per the "Remaining AT THE FLIP" list below):

1. Gate re-probed first-hand: documents census 296 VALIDATED / 3 FLAGGED / 80 SUGGESTED
   neighbors untouched; chunks mirror (295 up-flips + 3 flag decisions, 0 regressions). DONE.
2. `snap005_export.py` run FOR REAL — ALL VERIFICATIONS PASS after two narrowly-scoped,
   manifest-bound exporter amendments (SNAP5-F5: SUGGESTED→FLAGGED card decisions are the
   operator's own, not regressions; SNAP5-F6: question_anchors grew +11 rows additively from
   the app-side teacher wave on the papers/schemes axis — multiset superset, audit-evidenced).
   Freeze committed: `evidence/bench-001/snapshots/snap-005/` @ records `ab600e18f1`
   (+ FREEZE_RECORD.md + amended exporter as provenance). DONE.
3. gold re-pair: **gold-v4** — 12 class files BYTE-IDENTICAL to gold-v3 (anti-tuning held),
   manifest pins move to snap-005; `gold_check.py (snap-005, gold-v4)` PASS (120 records,
   quotas ok, all anchors resolve; selftest 6/6). DONE (this commit).
4. preload-r6 — NEXT.
5. `ops-{embed-backfill,run003b,run004a,run005c}-r6.yml` — NEXT.
6. Dispatches in runbook order → run records → R6-GENERATION-NOTES + §8 verdict (the
   interpretation pre-registration `09a624728` binds the first §8(d) reading). PENDING.

The original staging record is preserved below (historical).

---

# r6 staging unit — READY (staged pre-flip, 2026-09-28)

The r6 gate is the operator/teacher **card validation wave** (298 T-C27 cards; re-probed
NOT landed 2026-09-28 four times). Per the operator directive ("proceed with Next: the
small r6-staging unit ... ready to execute the moment you flip the card wave", trace
`1a0e4325cefc7b51`), the unit is STAGED NOW so the real freeze at the flip is execution,
not engineering — the r4 pre-flip staging precedent.

> **Status 2026-09-28 (operator directive, trace `1a0e6753792f76fd`): the r6 execution
> dependency is WAITING_FOR_GENUINE_TEACHER_VALIDATION.** The 298 T-C27 cards stay
> SUGGESTED and byte-untouched — no agent flip, no DB mutation; no validation endpoint
> is to be implemented unless independently product-useful. This unit executes only
> when a genuine teacher validation wave lands.

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

## Addendum 2026-09-28 (s145, post-landing hardening): the §4 census gate

The handoff §4 census requirement is now enforced END-TO-END on both sides of the freeze
boundary (core `64c71ff`, records-side amendment here):

- **Exporter** (this directory's `snap005_export.py`): the manifest now records
  `counts.hv_projection` — rows / rows_with_refs / distinct_chunk_refs /
  distinct_spec_codes + anchor_kinds — computed LIVE from the artifact bytes and asserted
  against the handoff census (210/209/164/181 + 205/4/0/1) at export time
  (`dry_run_2026-09-28b.log`: ALL PASS incl. the new census check, run twice 2026-09-28).
- **Loader** (core `64c71ff` on top of `c91372c`+`670423a`+`b45b5d6`):
  `BenchSnapshot` re-derives the census from the pinned bytes and fail-closes on any
  mismatch against the manifest record — AND on a manifest that declares no census. A
  snapshot carrying `chunk_spec_hv.json` without `counts.hv_projection` therefore ABORTS
  by design: pre-freeze staging trees from before this amendment (incl. the 09-28 first
  dry run) will not load — that is the intended fail-closed behavior, not a regression.
  The r6 freeze re-runs the amended exporter, so the frozen manifest always carries the
  census and loads clean.
- Cross-lane note (disclosed, s145 reconciliation): a PARALLEL s145 draft of the same
  export ran in this container 2026-09-27 (its evidence preserved at
  `workspace/s145-reconciliation/` in the session sandbox, never committed — superseded by
  this unit per the never-duplicate discipline). The two independently written exporters
  converged byte-identical on 7/8 files (chunk_spec_hv.json b5b20ffa…, chunks.jsonl.gz
  fe076aaf…, spec_points/graph_edges/misconceptions/question_anchors/concept_attachments
  all equal); `graph_code.json` differs across ALL runs BY DESIGN (embedded source.date;
  the invariant is rows-set-equal + counts-equal, verified in every dry run).

D2 rider landed alongside (core `2267221`): `TutorAnsweredEvent.answerProvider` persists
the deterministic refusal identity (`deterministic-refusal` vs `deterministic-paper-refusal`)
into `KA_RAG_COMPLETED` telemetry — audit finding D2 closed; unrelated to the r6 freeze
mechanics but part of the same §8(d) tranche.

## Addendum 2026-09-28 (interpretation pre-registration): the first §8(d) number must be read against two unmitigated risks

Recorded per the operator's external-review follow-up (trace `1a0e699e61629235`). The
tranche's structural safeguards are already pinned (dual granularity both reported; dual
denominator with the SUGGESTED-notes caveat; unbridged codes surface as explicit misses,
never coerced; absent artifact = NOT SCOREABLE; census fail-closed on both sides of the
freeze). Two risks, however, are **interpretation obligations only** — the runner records
the inputs but nothing in the code flags them. The R6-GENERATION-NOTES interpretation pass
MUST check both before any §8(d) reading is trusted:

1. **Gold-query leakage into the corpus (inflation risk).** If any of the 120 gold asks
   near-duplicates an ingested chunk (card bodies, notes prose — the arms retrieve over the
   same corpus the gold was authored against), a semantic arm can serve the right refs by
   embedding/lexical memorization, not by retrieval quality. §8(d) inherits this: correct SP
   coverage via a memorized serve proves nothing about serving real learners. The
   interpretation pass must (a) measure the overlap (gold ask vs its top served chunk, per
   arm), (b) mark any near-duplicate serve as leakage-suspect, and (c) carry the flag into
   the reading — the recorded NUMBER stays verbatim in the run report (no post-hoc
   exclusion); only the interpretation is qualified.

2. **Correct SP attribution via the wrong retrieval path (attribution risk).** §8(d) scores
   the SERVED SET's mapping coverage — it never asks HOW a ref was surfaced. A chunk ranked
   for the wrong reason (lexical accident, fusion noise) that happens to carry the right HV
   code — especially a chunk holding several codes through the §1 many-to-many — scores (d)
   well while (a)/(b)/(c) stay weak. A high (d) beside weak (a)/(b)/(c) is therefore a
   coverage signal, NOT a retrieval-quality signal, and must be read as such; §8(d) alone
   must never be cited as "retrieval works" or used to promote anything.

Both checks use inputs the runners already record (per-query served refs, per-arm
rankings); neither requires a code change, a contract change, or a threshold change. The
pinned rules are untouched: gate arithmetic stays on the ALL denominator per ruling 1,
full-coverage granularity pending the §10 ruling, no promotion claim on (d) at r6. The r6
gate itself is unchanged — WAITING_FOR_GENUINE_TEACHER_VALIDATION (trace
`1a0e6753792f76fd`).
