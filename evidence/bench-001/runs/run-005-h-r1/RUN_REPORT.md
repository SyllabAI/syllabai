# Run 005 — C hybrid arm, per-kind notes arm posture (the T-C72 kind-arm lever, KIND-ARM form)

**Status:** RECORDED — production hybrid arm on record (deterministic, offline replay, zero API calls; snapshot snap-007 (frozen snapshot)).
**Arm:** C hybrid — PRODUCTION retrieval fabric (com.syllabai.retrieval.RetrievalFabric: explicit arms [pgvector, bm25, notes-kind-arm], central BoundaryPolicy, shipped ReciprocalRankFusion k=60, rank-only, NoReranker) over arm A's production vector path and arm B's production lexical path with the per-kind EXTERNAL_NOTES arm K=15 as a THIRD fusion input, PRE-boundary (the T-C72 kind-arm lever, KIND-ARM form — notes compete only against notes, the existing arms' lists untouched, pre-registered BEFORE this run); chunk+query vectors replayed from the frozen artifact embed-backfill-snap-007-preload, zero API calls at run time
**Executor:** production code over a real Flyway-migrated Postgres (PostgreSQL 17.11 + pgvector 0.8.0, version-exact with the T-C59 pin), corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served through the production EmbeddingProvider port; no PRODUCTION retrieval SQL changed, no fusion code written (the shipped ReciprocalRankFusion runs unchanged); the per-kind EXTERNAL_NOTES arm (K=15) runs as a third pre-boundary fusion input (the kind-scoped production candidate SQL + deterministic chunk_ref ASC tiebreak through the production EmbeddingProvider port, zero API calls, no boundary interaction; pre-registered in ARM-COMPOSITION-PREREGISTRATION.md BEFORE this run) — code `c346d645d119708bcf0f5d9cac2ae15131654970` (PR syllabai-core#70, MERGED on the operator's explicit word, trace `1a10277a0d19ccfd`).
**Date:** 2026-10-03 | **Gold:** gold-v5 (120 queries; frozen) | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Fabric provenance

- Orchestrator: `RetrievalFabric` composes the explicit arms [pgvector, bm25, notes-kind-arm] (the third appended via `composeArms` — the absent path returns the recorded two-arm list unchanged), applies the serving boundary ONCE centrally pre-fusion, and fuses with the shipped `ReciprocalRankFusion` k=60 — no new fusion code, no PRODUCTION retrieval SQL changed. Per-arm candidate bound 40.
- Notes kind arm: per query, the top K=15 EXTERNAL_NOTES chunks by arm A's production candidate SQL (same distance operator `<=>`, same embedding column, same embed_rev stamp, both T-C20 VALIDATED scope branches) + `AND kind = 'EXTERNAL_NOTES'` + `LIMIT 15` + a deterministic `document_id ASC, chunk_index ASC` final tiebreak; the SAME frozen query vector through the production EmbeddingProvider port. No cosine floor (the census basis; MIN_COSINE is the rejected CAP-form lever). Under-fill 0 queries at the 350-note universe. FOUR-way one-lever guard (reranker × weights × floor × kind-arm), fail-closed; floor/reranker/weights ABSENT this run.
- Frozen artifact `embed-backfill-snap-007-preload`: model `gemini-embedding-001` @ 768 dims; verified fail-closed against this run's frozen inputs before anything ran; SHA-256 echo in results.json `embedding_artifact.sha256_echo` (chunks `1fd6a617…`, queries `bca55841…` — byte-verified in this workspace before the run as well).

## Overall (chunk axis, n=89 labeled queries)

- **C served (fabric over components as they stand, ALL denominator, 4510 embedded chunks):** recall@5 0.041 · recall@10 0.0612 · recall@20 0.1178 · mrr 0.0581 · ndcg@10 0.0683 · evidence_precision@10 0.018 · false_positive_rate@10 0.982
- **C compliant (central VALIDATED gate pre-fusion):** IDENTICAL to served — the prereg's §3.6 compliant-prediction is FALSIFIED by the run: the notes documents pass the central VALIDATED boundary via the subject-level document-validation branch (T-C07's second scope branch), so the kind-arm's refs enter BOTH fabrics' pools. Recorded, not smoothed.

## §8(d) — the ruled metric (§10 Ruling 7, gate reading = per-query full coverage)

- **(d) full 52/89 = 0.5843 · micro 79/84 = 0.9405** — the recorded chain r8 0.5618/0.9167 → r9 0.4607/0.7857 → d-r1/e-r1 0.4607/0.7857 → f 0.5056/0.8571 → g 0.5169/0.8690 → **h 0.5843/0.9405**.
- **Superset invariant 89/89** (h pool ⊇ f pool per query) — the conditional theorem's hypothesis holds; (d) monotonicity unconditional. Zero f-full losses; zero covered-point drops on the held subset; g2-061 GAINS a point (f 1 → h 2); the g-era reverted flips' covering refs 4/4 in-pool.
- **All 5 f-lost flips ADMITTED+REVERTED** (g2-011, g2-016, g2-056, g2-059, g2-112) — the census's reach prediction CONFIRMED on the production path: every fresh carrier entered h's pool at fused ranks 8–26 (census NOTES ranks 4/6/8/8/11/13 of 350; K=15 reach complete, 0 MISS-AT-ARM).
- **BEYOND the exact-r8-reversion ceiling (a pre-registered FINDING, not a target hit):** the ceiling framing counted only the 5 flips (50/89 · 77/84). The kind-arm additionally recovered **g2-061** (4CH1-1.28 via the same fresh carrier `986612e9…` that reverted g2-016) and **g2-109** (4CH1-1.34C via `54cfe5a8…`) — both EXTERNAL_NOTES carriers, neither reachable at depth 40 in f/g. (d) 0.5843/0.9405 is the highest recorded value on the series; r8 remains a DIFFERENT-basis reference (snap-006 + chunk vectors `1e22a202…`), not a target under the current basis.
- **Census SET arithmetic byte-exact:** +797 notes refs predicted → **+797 observed**; notes share 15.3% → **30.6%** (predicted ~30.6%, the declared overshoot); pool growth +801 total (797 EXTERNAL_NOTES + 4 re-execution refs).

## Rank-slice ledger (NEW shape — the prereg's declared at-risk axes, movement = finding, not failure)

- recall@5 0.0616 → 0.041 (−33.4%) · recall@10 0.1043 → 0.0612 (−41.3%) · **recall@20 0.1612 → 0.1178 (the 5-run pin BROKE, declared at-risk BY DESIGN — the kind-arm's admissions are not rank-bounded)** · mrr 0.0626 → 0.0581 (−7.2%; intra-horizon re-ranking as notes enter top-20) · ndcg@10 0.1057 → 0.0683 (−35.4%) · evidence_precision@10 0.0303 → 0.018 (−40.6%).
- Per-query movement: recall@5 moved on 5 queries · recall@10 on 10 · recall@20 on 8 · mrr on 8 · ndcg@10 on 14. The kind-arm's notes admissions land inside the served horizon (124 at fused ranks 1–10, 346 at 11–20, 325 at 21–40, 2 at 41+ — the mechanism working exactly as pre-registered: "kind-arm rank r contributes 1/(60+r) — its top ranks compete INSIDE the fused top-20"), displacing paper mass from the top-20 slices while the SET-level (d) rises.
- exam_question mrr 0.494 → 0.5833 (+18.1%); factual ndcg@10 −61.0%; conceptual recall@20 −34.2% (per-class flags >15% in the verify output).

## §8.1 v1.1 gate arithmetic (evaluated fresh, both views; ruling 1: ALL bars on the served view)

- (a) ALL bars, served view — Recall@10: **0.0612** vs floor 0.1920 -> FAIL
- (b) ALL bars, served view — MRR: **0.0581** vs floor 0.1237 -> FAIL
- (c) ALL bars, served view — nDCG@10: **0.0683** vs floor 0.2316 -> FAIL
- (a2) VALIDATED bars, compliant view — Recall@10: **0.0612** vs floor 0.0734 -> **FAIL (held PASS through g; the kind-arm's notes refs dilute the compliant top-20 — the falsified §3.6 prediction's gate consequence)**
- (b2) VALIDATED bars, compliant view — MRR: **0.0581** vs floor 0.1184 -> FAIL
- (c2) VALIDATED bars, compliant view — nDCG@10: **0.0683** vs floor 0.1683 -> FAIL
- Boundary: served violations **0** (T-C20 update: zero expected on re-record); compliant-starved 0; zero-result queries 0.

## (e) latency

- Retrieval-only p50 346.5 ms / p95 366.1 ms (served; compliant 346.6/371.0) — BELOW g's 1080.0 ms (the prereg expected ≥; recorded as a finding). The kind-arm is one kind-filtered vector scan per pass — far cheaper than the floor's deterministic probe doubling that drove g's p50. Attribution: the prereg's (e) expectation inherited g's probe-doubling shape, which the KIND-ARM form does not have.

## Per class (C served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.065 | 0.085 | 0.085 | 0.2111 | 0.2301 | 0.04 | 0.96 |
| conceptual | 0.0 | 0.0 | 0.1282 | 0.0 | 0.0 | 0.0 | 1.0 |
| exam_question | 0.625 | 0.75 | 1.0 | 0.5833 | 0.5656 | 0.125 | 0.875 |
| factual | 0.0 | 0.1 | 0.2091 | 0.0 | 0.0645 | 0.0364 | 0.9636 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 0.0 | 0.0 | 0.02 | 0.0 | 0.0 | 0.0 | 1.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0286 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.0 | 0.0 | 0.0167 | 0.0 | 0.0 | 0.0 | 1.0 |
| vague_learner | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| why_wrong | 0.05 | 0.05 | 0.1067 | 0.0727 | 0.0808 | 0.03 | 0.97 |

## Verdict: NOT PROMOTED — and the (d) recovery arc is complete

- All six §8.1 v1.1 gates FAIL (first (a2) FAIL of the series — the compliant-dilution consequence, recorded above). NOT PROMOTED is a finding, not an argument.
- The (d) mechanism ledger is now COMPLETE on all four levers: reorder levers (d-r1 rerank, e-r1 weights) freeze (d); set-growth levers recover it — depth (f) +4.49pp (4/9 flips), floor (g) +1.13pp (1/5), **kind-arm (h) +6.74pp full / +7.15pp micro (5/5 flips + 2 beyond-flip recoveries) — the first lever to move (d) ABOVE the r8 recorded reference** (0.5843 > 0.5618, 0.9405 > 0.9167), on a superset invariant that held 89/89 with zero re-execution findings.
- The §10 Ruling 7 promotion rule ("(d) within 1pp of r8 on the full-coverage gate reading") is satisfied on the (d) axis — but promotion requires the §8.1 v1.1 gates on BOTH views, which FAIL; the rank-slice cost of the kind-arm's horizon-unbounded admissions is the recorded tension for the operator's next ruling (horizon/shape questions are operator-gated, not a lane tuning surface — any K/shape change = a dated new prereg per the anti-gaming rules).
- recall@20 0.1612 (5-run pin) broke exactly as declared at-risk BY DESIGN; the pin's SET-level counterpart (the superset invariant and its (d) theorem) held everywhere it was claimed.

## Run environment (recorded for reproducibility)

- PostgreSQL 17.11 (Debian 17.11-1.pgdg13+2) + pgvector 0.8.0 (built from source tag v0.8.0 against the same server headers), user-space deployment (PGDG debs + same-length binary-path patches), cluster on :5433 — version-exact with the T-C59/Session-165 pin. Flyway V1→V59 applied in-run; snapshot loader = the production loader; paired embed_rev stamp: 4510 chunks → rev 2, all serving-eligible.
- Toolchain: OpenJDK 25.0.4.1 (Corretto build 25.0.4.1+10-LTS) + Maven 3.9.9 (the T-C59 recipe). Offline suite on the merged head: **1237 run / 0 failures / 0 errors / 2 skipped** (1223 recorded + 14 new T-C72 tests), re-executed first-hand BEFORE the merge gate; head CI build SUCCESS at `553261c`; post-merge main CI build SUCCESS at `c346d64`.
- Zero API calls at run time; zero frozen-artifact mutation (fail-closed SHA echo re-verified post-reset: chunks `1fd6a617…`, queries `bca55841…`, manifest `39df600f…`).
