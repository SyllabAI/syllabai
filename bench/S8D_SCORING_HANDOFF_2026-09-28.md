# §8(d) scoring handoff — chunk→SP HUMAN_VALIDATED projection → snap-005 export, BenchSnapshot, runner

**Date:** 2026-09-28. **From:** bench/evidence lane (session web-23eb7684). **To:** core lane (syllabai-core).
**Status:** READY FOR IMPLEMENTATION — additive only, no threshold change, no frozen artifact touched.
**Why now:** R5 recorded §8(d) verbatim as "NOT SCOREABLE (zero HUMAN_VALIDATED chunk→SP rows — named data gap)"
(`evidence/bench-001/runs/R5-GENERATION-NOTES.md`). That gap is now closed on the data side; the remaining work is
code, and it belongs to core. This document specifies it so nothing is guessed at implementation time.

---

## 0. One-paragraph summary

The resources C13 store (210 HUMAN_VALIDATED chunk→SP rows, operator-promoted 2026-09-18 via
`review-sheet@88dc8dd6a3`) has been bridged onto production `document_chunks` with snapshot-scheme keys and committed
as `bench/evidence/chunk-sp-substrate-2026-09-27/chunk_spec_hv_projection.json` (records main `94d0d405c`,
2026-09-27). Coverage as recorded at bridge time: 209/210 rows bridged (205 CLEAN / 4 MULTI / 1 MISS), 180/182 SP
codes, **58/58 gold spec points covered**. §8(d) flips NOT SCOREABLE → scoreable-with-coverage at the next freeze
that carries the artifact. Three code changes remain, all additive: (1) the snap-005 export copies the artifact in
with a fail-closed drift gate; (2) `BenchSnapshot` gains an accessor; (3) the runner scores §8(d) from HV rows only.

## 1. Artifact contract (byte-frozen; do not re-serialize)

- Repo path: `bench/evidence/chunk-sp-substrate-2026-09-27/chunk_spec_hv_projection.json`
- Shape: `{"meta": {...}, "rows": [ ... 210 rows ... ]}`
- Row fields (verbatim): `mapping_id`, `spec_code`, `sp_title`, `note_slug`, `rn_id`, `document_id`, `checksum`,
  `chunk_refs` (list of `"<sha256>:<chunk_index>"` — the **exact** `chunks.jsonl.gz` chunk_ref scheme, so joins at
  freeze time need no translation), `chunk_indexes`, `anchor_kind` (`CLEAN` | `MULTI` | `MISS`), `store_chunk`
  (ordinal/heading/sha256_16/chars/convention), `provenance` (tier / validation_status / promoted_by / promoted_date
  / gate / store / store_sha256_16 / join).
- Exact census (recomputed 2026-09-28 from the committed bytes): **210 rows; 209 rows carry chunk_refs (205 CLEAN +
  4 MULTI); 1 MISS row (`mapping_id 1d97fd710f098a74`, `spec_code 4CH1-1.52C`) carries NO chunk_refs — the loader
  must tolerate empty refs**; **164 distinct chunk_refs**; **181 distinct spec_codes in-file** (= 180 bridged + the
  MISS's code; the second unbridged code, 4.15, is the store's worklist row and is not in the artifact at all).
- Many-to-many: several mappings can anchor the same chunk (one chunk can prove several spec points) → the accessor
  must build `ref → Set<code>`, never `ref → code`.

## 2. The provenance-counting rule (the one that silently zeroes the metric if wrong)

Harness spec §5: only `HUMAN_VALIDATED` mappings count as resolution ("AI_SUGGESTED / RULE_DERIVED mappings never
count, per the four-tier provenance contract"). The projection rows carry `tier: RULE_DERIVED` **together with**
`validation_status: HUMAN_VALIDATED` — rule-derived origin, operator-promoted status through the 09-18 review-sheet
gate. **The counting predicate is `validation_status`, NOT `tier`.** A naive `tier == HUMAN_VALIDATED` check would
exclude every row and silently re-create the data gap in code. This is the T-C06/F-168 "HUMAN_VALIDATED chunk→SP
substrate" the R5 notes named; the promotion gate is precisely what makes it count.

## 3. Export change (snap-005; pattern: `snap004_export.py`)

1. Copy the artifact **byte-identical** into the snapshot staging as `chunk_spec_hv.json` (byte-identity to the
   committed evidence file is the integrity property — no re-derivation, no re-serialization at export time).
   Manifest + SHA256SUMS entry like every snapshot file (§4 snapshot discipline).
2. Manifest-bound delta declaration (SNAP4-F1/F2/F3 precedent; suggest id `SNAP5-H1`): "additive projection:
   chunk→SP HUMAN_VALIDATED mappings over EXTERNAL_NOTES chunks; chunk row set and contents remain governed by the
   snap-003-lineage identity checks".
3. **Drift gate, fail-closed, executed at export time:** re-verify at freeze that (a) every chunk_ref in the
   artifact exists in the exported `chunks.jsonl.gz` and its (checksum, chunk_index) is unchanged; (b) the bridge
   re-run against live DB + pinned store bytes still yields 209/210 bridged with anchor kinds 205/4/1. Any drift →
   the export aborts (no silent partial). The join method and norm() definition are documented in the substrate
   pack's `EVIDENCE.md`; the store pin to re-verify against is `syllabai-resources@1245df009`,
   store `sha256_16 e8b58a7109104bb7`.

## 4. BenchSnapshot accessor (additive; precedent: enabler `e728b7dea`)

File: `src/test/java/com/syllabai/bench/BenchSnapshot.java` (syllabai-core).

- When `chunk_spec_hv.json` is present in the snapshot dir: parse it; expose at minimum
  `Map<String, Set<String>> hvSpecCodesByChunkRef()` (and optionally `Set<String> allHvCodes()`).
- When absent (snap-001..004): accessor returns empty and the runner reports §8(d) NOT SCOREABLE exactly as today —
  backward-compatible by construction, the same principle as the subject_id enabler.
- Loader guards: tolerate the MISS row's empty `chunk_refs`; assert `spec_code` matches `^4CH1-[0-9]+\.[0-9A-Za-z]+$`;
  assert `mapping_id` uniqueness; record the parsed census (rows / rows-with-refs / distinct refs / distinct codes)
  in the run report and fail-closed on mismatch against the manifest-recorded 210/209/164/181.

## 5. Runner scoring (§8(d) — SpecificationPoint resolution accuracy)

Metric definition (harness spec §5, verbatim): "does the arm surface evidence whose `HUMAN_VALIDATED` spec mapping
covers the query's gold spec points". Inputs: gold-v3 labels' gold SpecificationPoints, the arm's served evidence
chunk_refs, and the §4 accessor.

- Per gold query with gold points G (≥1) and served evidence refs R: HV-covered codes
  `C = ⋃ hvSpecCodesByChunkRef[r] for r ∈ R`.
- **Open granularity point** (no §10 ruling pins it; R5 scored (d) NOT SCOREABLE, so there is no precedent to
  match): (i) per-query full coverage — hit iff `G ⊆ C`; (ii) per-point micro-average — `mean over g ∈ G of [g ∈ C]`.
  They differ only on multi-SP queries (class 11, 7 of 120). **Recommendation: record BOTH in every run report**
  (same spirit as ruling 1's dual-denominator view), evaluate gate arithmetic on (i) full coverage as the stricter
  reading of "covers the query's gold spec points", and flag the choice for the next owner §10 ratification. This is
  a metric-definition clarification, not a §8 threshold change (§8 numbers stay v1.0 untouched) — but the run report
  must state the rule explicitly either way.
- **Dual-denominator view (ruling 1) applies to (d) too, and here it is material:** every chunk_ref in the
  projection belongs to an EXTERNAL_NOTES chunk whose content `validation_state` is SUGGESTED (the HV status is on
  the *mapping*, not the chunk content — the bridge never promoted content). On a VALIDATED-only denominator the
  HV-covered code set collapses and (d) would silently zero. Gate arithmetic on the ALL denominator per ruling 1;
  report VALIDATED-only alongside, with this note attached so nobody "fixes" it by coercion later.
- Hard guards: the no-unvalidated-mappings-count assertion exists in code even though the artifact contains none;
  unbridged codes (1.52C MISS; 4.15 worklist) surface as explicit coverage misses, never coerced into matches;
  §8(a)(b)(c) and (e)(f)(g) mechanics untouched by this change.
- Honest denominators in the report, computed live from the artifact (never hardcoded from this doc): 210 rows /
  209 bridged / 164 distinct refs / 181 in-file codes; gold coverage recomputed at run time from gold-v3 labels
  (58/58 as recorded at bridge time 2026-09-27; the 1.52C MISS code is not among gold's codes, so it cannot cost
  coverage).

## 6. Sequencing and scope

- The runner change lands **with the r6 run class** (the card-flip freeze that carries snap-005) — not before; there
  is no §8(d) number to produce on snap-004 and none should be produced.
- r6 itself stays gated on the operator/teacher card validation wave (re-probed live 2026-09-28: 298 cards still
  SUGGESTED, 317 VALIDATED chunks unchanged — the gate has not flipped; no agent may assert the validation).
- No frozen artifact (snap-002/003/004, gold-v1/v2/v3, preload-r5) is mutated; the snap-005 re-freeze is the
  sanctioned mechanism (§4 snapshot discipline).

## 7. Verification vectors (self-test material for the implementation)

| Check | Expected |
|---|---|
| `hvSpecCodesByChunkRef.get("795770f2c297c26e66b349266212a0b4d0de3d320d8c2e470f8fde15936432ac:1")` | contains `4CH1-1.1` (mapping `efc19a2773331632`, CLEAN) |
| MISS row lookup | `mapping_id 1d97fd710f098a74` parses with empty `chunk_refs`, code `4CH1-1.52C`, contributes no refs |
| MULTI expansion | mapping `c19e1b3cca1d9eee` anchors chunk_indexes [1,2,4] of its note → 3 refs, `anchor_kind=MULTI` |
| Loader census | rows=210, with-refs=209, distinct refs=164, distinct codes=181 |
| Absent-artifact path | on snap-004 the accessor is empty and the runner prints §8(d) NOT SCOREABLE (current behavior preserved) |

## 8. Provenance chain

- Substrate evidence pack: `bench/evidence/chunk-sp-substrate-2026-09-27/` (records main `94d0d405c`, 2026-09-27):
  `EVIDENCE.md`, `chunk_spec_hv_projection.json`, `bridge_stats.json`, `r6_gate_probe_20260927.txt`, `SHA256SUMS`.
- Harness spec: `RETRIEVAL_BENCHMARK_HARNESS_SPEC.md` (ratified v1.0) — §5 flagship metric, §8 thresholds, §10
  rulings 1 (dual denominator) and 5 (non-production arms ineligible for gate arithmetic).
- The named gap: `evidence/bench-001/runs/R5-GENERATION-NOTES.md` ("§8(d) NOT SCOREABLE — zero HUMAN_VALIDATED
  chunk→SP rows").
- Core baseline this handoff was written against: main `a28e932b1` (2026-09-27); the §8(d) work had not been started
  there as of 2026-09-28 (verified first-hand).

*Handoff authored by the bench/evidence lane, 2026-09-28. Implementation scheduling belongs to the core lane.*

---

## 9. Implementation status (appended 2026-09-28, same day)

**Sections 1, 2 and 4 + the §5 scorer mechanics are IMPLEMENTED AND LANDED on core main:**
commit `c91372c435ed56d34c2f3d0702073393cf103913` (ff `fe5983f..c91372c`; branch CI
`36341510062` SUCCESS on `bench/s8d-hv-foundation` — dispatched run, full build + suite, Java 25;
local suite 21/21 incl. subject-id/metrics regressions before dispatch).

- `BenchSnapshot` gained the optional `chunk_spec_hv.json` load with every fail-closed guard this
  document specified: present-but-unpinned aborts; non-HUMAN_VALIDATED `provenance.validation_status`
  aborts (the §5 counting rule in code); malformed spec codes, duplicate mapping ids and chunk_refs
  unknown to the snapshot abort; MISS rows (empty refs) are recorded in the census, never force-matched.
- Accessors: `chunkSpecHvPresent()`, `hvSpecCodesByChunkRef()` (ref → Set<code>, many-to-many),
  `chunkSpecHvCensus()` (rows / rowsWithRefs / distinctRefs / distinctCodes / missCodes).
- New `ChunkSpecHvResolution` (pure, deterministic, BenchMetrics-discipline): per-query
  full-coverage + per-point micro-average, BOTH reported (`spec_points_full_coverage_rate`,
  `spec_points_micro_average`), empty served lists = honest zeros, `unbridgedGoldPoints()` surfaces
  the structurally unbridged codes (1.52C / 4.15) as explicit misses.
- Tests carry the REAL bridge vectors (efc19a2773331632 → 4CH1-1.1; c19e1b3cca1d9eee MULTI over
  3 refs; the 1d97fd710f098a74 / 4CH1-1.52C MISS row) — `BenchSnapshotChunkSpecHvTest` (7) +
  `ChunkSpecHvResolutionTest` (7).
- **Still sequenced to the r6 staging per §6:** the run-class wiring (the conditional §8(d) section
  in Run003B/Run004A/Run005C + report text) and the snap-005 export + drift gate land as one unit at
  the card-flip freeze, exactly as r4/r5 staged their generations. On every frozen snapshot the
  recorded-generation behavior is unchanged by construction (absent artifact path is byte-identical).
