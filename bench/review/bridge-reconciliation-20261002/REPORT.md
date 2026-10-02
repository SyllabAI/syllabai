# T-C64 — Notes-bridge number reconciliation: the "180 bridged spec points" vs the live 155/175 tag census

**Lane:** Super Z (trace `1a0fcb9aef3bc611`, operator "Okay, proceed") · claim `2de992a20fe8`
**Date:** 2026-10-02 · **Read path:** sanctioned SELECT-only Neon probe (`t0_readonly`), module `scripts/neon_sql.py`
**Probe script:** `scripts/tc64_bridge_recon.py` · **Machine evidence:** `tc64_bridge_recon.json` (this pack)
**Question (T-DB-VERIFY 2026-10-02):** the T-C56-era pack states the notes bridge carries "180 bridged spec points (1 MISS + 4 MULTI)", but the live distinct-code census says notes 155 / all-kinds union 175 — "PACK NOT REPRODUCIBLE — reconcile before reuse."

---

## 0. Verdict

**The pack number is TRUE of its own instrument and was mis-carried as a live-serving statistic.**
"180 bridged spec points" is the bridge-time census of the **C13 HV chunk→SP projection artifact**
(`bench/evidence/chunk-sp-substrate-2026-09-27/chunk_spec_hv_projection.json`, store pin `1245df009`,
records `94d0d405c`, 2026-09-27): 210 HUMAN_VALIDATED store mapping rows, 209 of which carry
`chunk_refs` (205 CLEAN + 4 MULTI, 1 MISS), joined **offline** to the notes corpus. It counts
**distinct `spec_code` values on mapping rows** — 180 bridged (181 in-file incl. the MISS row's
`4CH1-1.52C`).

The live numbers (155 / 175) count **`document_chunks.spec_codes` jsonb tags** — the production
tag instrument the serving pool actually reads. These are **two different tag systems on the same
chunks**; neither number is wrong, and nothing drifted. The pack's sentence conflated the two.

## 1. No drift — the notes corpus and every artifact anchor are intact

- Notes corpus today: **112 docs / 350 chunks**, all VALIDATED, all Chemistry (4CH1) — byte-for-byte
  the same counts the artifact's `bridge_stats.json` recorded at bridge time.
- Artifact doc-checksum set vs live notes doc-checksum set: **identical both directions** (0 either way).
- **All 164 artifact `chunk_refs` are ALIVE in the live DB** (`<doc_checksum>:<chunk_index>` join,
  164/164). The 09-28 re-ingest wave did not touch the notes corpus.
- Artifact bytes: substrate pack SHA256SUMS all OK; snap-007's `chunk_spec_hv.json` copy
  **byte-identical** (`b5b20ffa96b6…`), so the frozen bench world is unaffected by any of this.

## 2. The delta, mechanically decomposed

| Set | Size | |
|---|---|---|
| Artifact in-file codes (210 rows) | 181 | = 180 bridged + the MISS code `4CH1-1.52C` |
| Artifact **bridged** codes (209 rows with refs) | **180** | the pack's number |
| Live `spec_codes` on the **same 164 anchored chunks** | **155** | all live notes tags live on these chunks |
| Live `spec_codes`, notes total | 155 | = the anchored subset exactly |
| Live `spec_codes`, all kinds union | 175 | re-pinned this run; ⊆ axis |

- `bridged(180) ∖ live(155)` = **26 codes**, and the disposition of each is pinned:
  **154/180 bridged codes are tagged live on their OWN anchored chunks**; **0** are tagged
  elsewhere-only; **26 are not tagged anywhere in the live notes tags**
  (`2.24C, 2.27C, 2.35, 2.45, 2.50, 3.13, 3.17, 3.19C, 4.1, 4.10, 4.11, 4.19, …` — full list in the JSON,
  `bridged_code_disposition.nowhere_list`). This is a **production-tagger coverage gap against the
  HV mapping substrate**, not a bridge or drift defect.
- `live(155) ∖ artifact(181)` = **exactly 1 code: `4CH1-4.15`** — the C13 store's *worklist row*
  (per the S8D scoring handoff §1: "not in the artifact at all"), which the production tagger
  **did** tag. Honest asymmetry in the right direction.
- **Normalization is excluded as a cause**: the raw delta (27/1) is invariant under
  case/dash canonicalization **and** under C-suffix folding (`1.52C → 1.52`): the live tags
  simply do not carry those codes in any spelling.

**Instrument shape (why the counts diverge structurally):** the artifact claims 209 mapping rows →
215 (row × ref) incidences over 164 chunks with 180 distinct codes; the production tagger wrote
**264 tag pairs on those same 164 chunks** covering only 155 distinct codes — a different,
coarser tag distribution (more repetition, fewer distinct codes), produced by a pipeline that
never carried the 26 HV codes above.

## 3. Axis correction (secondary finding)

The "182-point 4CH1 axis" quoted in the T-DB-VERIFY report was the **bridge-time** axis (S8D
handoff's "180/182 SP codes", 2026-09-27). Live today the 4CH1 SUBTOPIC VALIDATED axis is
**194 codes** (`knowledge_nodes`, node_type SUBTOPIC, validation VALIDATED, code LIKE `4CH1-%`)
— the curriculum axis grew since bridge time, exactly as snap-007's 194-row `spec_points.json`
fidelity anchor recorded. Coverage ceilings against live tags:

- notes tags cover **155/194** axis codes → **39 axis codes uncovered by notes**;
- the all-kinds union (175) covers **175/194** → **19 uncovered by any serving tag**;
- all live-tag codes (155 and 175 alike) are valid axis codes (0 outside the axis).

## 4. Gold-coverage cross-check (read-only, frozen gold inputs)

Distinct `4CH1-*` spec-code tokens across the frozen gold-r9 labels: **76**; the artifact's bridged
codes cover **76/76** (consistent with the bridge-time "58/58 gold spec points" claim at its own
granularity); the live notes tags alone would cover **67/76** — the 9 lost are all members of the
26-code tagger gap (`2.27C, 3.13, 4.19, 4.29C, 4.34C, 4.37C, 4.43C, 4.48C, 4.5`).

**This costs the bench nothing:** §8(d) is scored from the frozen artifact at freeze time
(snap-007 carries it byte-identically with a fail-closed drift gate; census 210/209/164/181
re-verified this run). The exposure is only for anyone re-deriving "bridged coverage" from
production tags.

## 5. Downstream guidance (the point of the exercise)

1. **Bench/§8(d): keep the frozen artifact.** The number 180 (and its census 210/209/164/181)
   remains the truth of the HV projection instrument; no action.
2. **Serving-side claims: use the tag census.** Any statement like "the notes surface bridges N
   spec points" must quote **155 (notes) / 175 (union) against the 194-code axis** — never 180.
3. **If the 26-code gap matters productively**, the fix is a governed re-tag (or a projection of
   the 26 missing HV codes into `document_chunks.spec_codes` under the wave-2 instrument) — a
   write-lane card on its own authority; NOT done here (read-only lane).
4. The T-DB-VERIFY report line "Live ceiling … vs the 182-point 4CH1 axis → ≥7 points uncovered"
   is **superseded** by §3 above (axis 194; notes-uncovered 39; union-uncovered 19).
5. The T-C56-era pack sentence "桥接 180 spec points (1 MISS + 4 MULTI)" should be read as
   "the C13 HV projection bridges 180 codes at bridge time" — historical text stays untouched;
   this pack is the correction of record.

## 6. Evidence inventory

- `tc64_bridge_recon.json` — machine evidence: artifact census re-pin (asserted 210/209/164/181/180),
  I1 identity, L1–L6 live censuses, ref liveness (164/164), checksum-set identity, raw +
  canonicalized deltas, per-code disposition, instrument shape, gold cross-check, axis containment.
- `SHA256SUMS` — this pack.
- Upstream pins: substrate pack `bench/evidence/chunk-sp-substrate-2026-09-27/` (SHA256SUMS OK),
  snap-007 `chunk_spec_hv.json` (byte-identity asserted), S8D handoff `bench/S8D_SCORING_HANDOFF_2026-09-28.md`,
  T-DB-VERIFY report `download/chem-live-db-verification-2026-10-02.md`.
- Probe lineage: `scripts/tc64_bridge_recon.py` (SELECT-only; zero writes; no credential echoed).
