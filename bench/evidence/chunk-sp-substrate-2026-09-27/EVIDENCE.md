# Chunk→SP HUMAN_VALIDATED substrate bridge — evidence record (2026-09-27)

Session: web-23eb7684 (task trace `1a0e32c9f6971b89` — "Proceed with Next: the card
validation wave unlocks r6; quality floors need the chunk→SP substrate").

## 0. What this session established

Two facts were demanded first-hand before any action (standing verification rule):

1. **The r6 gate is UNCHANGED — the card validation wave has NOT landed.** Live
   production probe (read-only, `r6_gate_probe_20260927.txt`): EXTERNAL_QUESTIONS
   documents = 378 SUGGESTED + 1 VALIDATED (the 298 T-C27 cards remain SUGGESTED);
   chunks = 317 VALIDATED (145 QP + 161 MS + 11 EQ) — exactly snap-004's SNAP4-F1
   flip cohort; exam_papers = 78 SUG / 13 REJ / 13 VAL. The trigger-A at-flip
   closeout (`04e2b0951`, records main, 2026-09-27T10:35Z) already recorded "r6
   stays available"; this probe re-verifies the gate as of ~13:1xZ the same day.
   r6 remains **operator-held** per AT_FLIP_RUNBOOK trigger A (no agent-asserted
   content validation; invariant `unvalidated_content_must_not_serve`).
2. **The §8(d) substrate is now bridged and ready** — the deliverable of this
   session (below).

## 1. The substrate chain, first-hand (no summary trusted)

| Stage | Status at session start | Source verified |
|---|---|---|
| C13 substrate store (chunk→SP, quote-anchored, `c13-chunk-convention-1`) | 211 rows = **210 HUMAN_VALIDATED** (apply `operator-directive-session-102`, 2026-09-18, gate `review-sheet@88dc8dd6a3` 42/42 + 13/13) + 1 worklist (4CH1-4.15) | `graph/igcse-chemistry/spec_chunk_mappings.yaml` @ resources main `1245df009` — git blob sha1 `9247ccdf05b8c296716b6c9a458897535dfd435f` byte-verified; census 211/210 matches C27 sweep S3 |
| C27 repair | sp_title labels re-sourced only; "mapping decisions, spec codes, note anchors, evidence quotes, HUMAN_VALIDATED promotion state — all untouched" | `C27_FINAL_ALL_STORE_SWEEP_RECORD.md` (fetched) |
| Notes corpus in production | 112 EXTERNAL_NOTES docs (created 2026-09-20), 350 chunks, **350/350 embedded**, all with note-level spec_codes | live DB probe (this session) |
| Corpus identity bridge | manifest 112 pages ↔ DB `file_name` `sme-note-<rn_id>.txt` | `SME-RevisionNotes/igcse-chemistry-19/manifest.json` @ resources main |
| Bench snapshot side | snap-004 carries NO chunk→SP HV artifact (chunks carry only rule/AI-tier spec_codes; 117 HV rows are concept→SP attachments) | `snap004_export.py` (fetched) — the named §8(d) data gap in R5-GENERATION-NOTES |

## 2. The bridge (this session's execution)

`scripts/c13hv_bridge_20260927.py` — read-only over production (SELECT-only,
rolled back); fail-closed joins, no fuzzy matching, no invented rows:

- join 1: store `note_slug` → manifest page (112/112 distinct, 0 ambiguous) → `rn_id`
- join 2: `rn_id` → DB document (`sme-note-<rn_id>.txt`) → document row (checksum, id)
- join 3: `norm(evidence_quote)` — **verbatim copy of the pinned C13/C10 `norm()`** —
  containment over every DB chunk of that note (`norm(content)`); unique hit = CLEAN;
  multi-hit = MULTI (attach all, flagged); consecutive-chunk concatenation hit = SPAN
  (attach all involved, flagged); no hit = MISS (recorded, never force-matched)

### Results (chunk_spec_hv_projection.json, bridge_stats.json)

| Measure | Value |
|---|---|
| HV rows resolved to a production note document | **210/210** |
| CLEAN (unique single-chunk quote anchor) | **205** |
| MULTI (quote appears in 2–3 chunks of the note; attached to all, flagged) | 4 |
| SPAN | 0 |
| MISS (unbridged) | **1** — `1d97fd710f098a74`, SP **4CH1-1.52C** (2-D metallic lattice): the evidence quote carries source-page chrome ("…IGCSE & GCSE Chemistry revision notes…") that the production canonicalization split apart; the upstream T-C10 mapping itself is real (operator-validated 2026-09-11). 4CH1-1.52C is NOT among the gold's 63 distinct spec points → zero §8(d) impact |
| Distinct spec codes with ≥1 bridged row | **180/182** (unbridged: 4.15 worklist gap + 1.52C) |
| **Gold coverage: distinct gold spec points (63, labels byte-identical v1→v3) covered by bridged HV rows** | **58/58 — COMPLETE** |
| Snapshot-scheme keys | `chunk_refs` = `"<checksum>:<chunk_index>"` — the exact snap-003/004 chunks.jsonl scheme; joins at freeze time without translation |
| Store pin (in every provenance block) | resources main `1245df009`, store sha256_16 `e8b58a7109104bb7` (byte-exact, git-blob-verified) |

## 3. What this changes for the bench

- **§8(d) SpecificationPoint resolution flips NOT SCOREABLE → scoreable** at the next
  freeze that carries the projection artifact: the runner scores served evidence whose
  HUMAN_VALIDATED mapping covers the query's gold spec points (§5 flagship metric),
  with the coverage denominator (209 bridged rows / 180 codes / 112 notes docs)
  reported honestly alongside.
- The floors (a)/(b)/(c) stay FAIL on the current 317-chunk served view — unchanged
  finding; the card wave is the denominator change (r6), the substrate is the
  scoreability change. Both are now ready; neither is self-startable.
- **Consumption path (next freeze, snap-005 at the r6 card-flip):** extend the export
  (snap004_export.py pattern) to include `chunk_spec_hv.json` = the projection rows
  keyed by chunk_ref (plus a drift gate: EXTERNAL_NOTES chunk_ref set and contents
  vs the live bridge re-run); BenchSnapshot gains the accessor (additive, e728b7dea
  precedent); the runner reports the spec axis from HV rows only.

## 4. Integrity and scope guards held

- Zero production writes (probes SELECT-only, rolled back; the bridge writes only to
  the local workspace).
- No content validation asserted anywhere: the 210 rows' HUMAN_VALIDATED status was
  applied by `operator-directive-session-102` on 2026-09-18 through the review-sheet
  gate — this session only joins and projects, never promotes.
- Frozen artifacts untouched: snap-002/003/004, gold-v1/v2/v3, preload-r5 all
  read-only; the projection is a NEW artifact staged for the NEXT freeze (versioned
  re-freeze is the sanctioned mechanism — no in-place mutation).
- Resources store pin byte-verified against the git blob sha1 before use; the C27
  record's `f36910450bd50726` pin does not reproduce against HEAD bytes (the C28
  store move commit `b3bca02aa` post-dates it); integrity here rests on the
  git-blob-verified bytes + the census agreement with C27's S3 (211 codes / 210
  mapped quotes). Flagged for the resources lane's awareness, not repaired here.

## 5. Files

| File | Purpose |
|---|---|
| `chunk_spec_hv_projection.json` | the §8(d) ground-truth artifact (210 HV rows; snapshot-scheme chunk_refs; full provenance per row) |
| `bridge_stats.json` | bridge run stats (kinds, misses, multis, coverage) |
| `r6_gate_probe_20260927.txt` | the live-DB r6-gate re-verification output |
| `SHA256SUMS` | integrity over this pack |
