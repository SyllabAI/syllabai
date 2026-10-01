# T-C27 / T-C13 — the serving-flip recorded bench: RUNBOOK

Recorded 2026-09-26T21:4xZ (session web-98866c45) at the operator's direction to pick up
the "T-C27 bench-at-serving-flip" item. This file is the staged, ready-to-execute runbook;
it commissions nothing. The recorded run itself remains **operator-held** per the snap-002
FREEZE_RECORD discipline ("not self-started") and is owed **at the serving flip** — when
the 298 T-C27 question cards enter the serving set.

## State at recording (all verified, not assumed)

| prerequisite | status |
|---|---|
| snap-003 freeze (card axis IN via SNAP3-F1; 3,831 chunks = 1,281 QP + 1,494 MS + 1,056 cards; 575 docs) | IN GIT `evidence/bench-001/snapshots/snap-003/` — `sha256sum -c SHA256SUMS` 7/7 OK (re-verified 2026-09-26) |
| gold-v2 (120 queries / 12 classes, label logic byte-identical to v1, 15 card-anchored records) | IN GIT `bench/gold-v2/` — SHA256SUMS all OK (re-verified) |
| set+snapshot pair validation | `python3 bench/gold_check.py evidence/bench-001/snapshots/snap-003 bench/gold-v2` → **PASS: 120 records, quotas ok, all anchors resolve** (reproduced locally 2026-09-26) |
| harness (Arms A0/A/B/C + runners Run002A0/Run003B/Run004A/Run005C) | `syllabai-core/src/test/java/com/syllabai/bench/` — unit-green via core-ci (runs 36251591706 / 36272382294 on main, SUCCESS) |
| embed blocker (the 403 key denial) | CLEARED 2026-09-26 (key swap + 298 card chunks embedded, gemini-embedding-001@768 — da95f668) |
| serving flip | **NOT HAPPENED** as of 2026-09-26T21:4xZ: no validation-wave record anywhere in coordination since snap-003; live teacher search endpoint verified auth-gated (401 unauth / 403 learner-role — the sanctioned TEST learner cannot probe card serving; recorded honestly) |
| dual-denominator semantics on snap-003 | chunk `paper_state` is uniformly SUGGESTED at doc level (the known re-ingestion state lag, FREEZE_RECORD finding 4) → the compliant view on this snapshot is honestly starved; the ALL denominator is the scored axis and the card axis enters it via SNAP3-F1 |

## Trigger (the operator's call, one of exactly two)

- **(A) The flip, then the run (the owed path):** the operator/teacher validation wave
  promotes the 298 cards (all SUGGESTED today) — the T-C20 boundary then serves them —
  and this runbook executes as the recorded at-flip bench. No agent may perform the
  validation (T-C27 forbidden list: agent-asserted content validation; invariant:
  unvalidated_content_must_not_serve).
- **(B) Commission the run pre-flip:** the operator explicitly directs the recorded run on
  snap-003+gold-v2 as-is (ALL-denominator measurement of the card axis in the candidate
  pool, honest compliant-starved reporting). Discipline-legal only as an explicit
  operator directive recorded in T-C27.yaml — never self-started.

## Steps (either trigger; mirroring the r3 generation exactly)

1. **Vector freeze for snap-003 (arm A prerequisite).** New dispatch-only workflow
   `ops-embed-backfill-r4.yml` cloned from `ops-embed-backfill-r3.yml`: same
   production-shaped `EmbedBackfill` runner (pin the core sha at dispatch), inputs
   `bench/inputs/snapshot-r4` (= snap-003 staged) + gold-v2; chunk-vector preload from the
   production vectors where present (QP/MS + the T-C27-embedded cards are all 768-dim in
   the content DB), fresh `gemini-embedding-001@768` calls only for the residual, 
   checkpoint-resumable, min_interval 600 ms. Output: the frozen r4 chunk-vector artifact
   (compute-once-freeze-forever). Expected API load ≈ (3,831 − preloaded) + 120 gold
   query embeddings — within the free-tier wall the r3 lane already operated under.
2. **Stage inputs.** `bench/inputs/snapshot-r4/` ← snap-003 seven artifacts (SHA-verified
   in-workflow, fail-closed); `bench/inputs/gold-r4/` ← gold-v2 (the pair discipline:
   gold-v2 stays SHA-paired with snap-003; nothing in `bench/gold/` or `bench/gold-v2/`
   is touched).
3. **Generate the r4 run workflows** (`ops-run003b-r4.yml` / `ops-run004a-r4.yml` /
   `ops-run005c-r4.yml`), cloned from their -r3 siblings with exactly three deltas:
   input paths → the r4 staged dirs; `BENCH_RUN003B_RESULTS`/`BENCH_RUN004A_RESULTS` →
   the r4 run dirs committed before the arm-C dispatch; pinned core sha → main at
   dispatch. A0 stays deliberately unset (stale-premise note carried from r3).
4. **Dispatch in order:** arm B (lexical, no vectors needed) → arm A (replays the frozen
   r4 vector artifact through the production vector serving path) → arm C (RetrievalFabric
   hybrid RRF k=60, consuming B's and A's results.json). Zero API calls at run time for
   A/C (compute-once); B is offline by construction. Double-pass determinism per runner.
5. **Record.** `results.json` + `RUN_REPORT.md` + `SHA256SUMS` per run under
   `evidence/bench-001/runs/run-00{3b,4a,5c}-r4/`; commit artifacts + the workflow files;
   append the run rows to the T-C13 TODO entry; dual-denominator metrics verbatim (ALL +
   compliant), VALIDATION_BOUNDARY findings counted, spec-resolution axis reported on the
   V33 spec_codes substrate (SNAP3-F3 made it loadable), §8 arithmetic + promotion verdict
   on the ALL denominator per ratified ruling 1.
6. **Close T-C27.** With the recorded run on file: the last §5 item is cashed —
   `T-C27.yaml → DONE` with the run IDs as outcome evidence (the embeds + spec-linkage +
   cards lanes were already landed and verified 2026-09-26).

## Guardrails (unchanged, restated)

- gold-v1 byte-untouched; gold-v2 read-only after its freeze; no in-place mutation of any
  frozen artifact; every workflow fail-closed on SHA mismatch.
- Benchmark-only dispatches (workflow_dispatch, never push/PR); zero production writes;
  the production read path stays SELECT-only (SNAP3-M1 discipline).
- No agent-asserted content validation anywhere in this lane.
