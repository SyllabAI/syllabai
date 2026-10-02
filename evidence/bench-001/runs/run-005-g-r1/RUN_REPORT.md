# Run 005 — C hybrid arm, per-arm notes floor posture (the T-C69 per-kind quota lever, floor form)

**Status:** RECORDED — production hybrid arm on record (deterministic, offline replay, zero API calls; snapshot snap-007 (frozen snapshot)).
**Arm:** C hybrid — PRODUCTION retrieval fabric (com.syllabai.retrieval.RetrievalFabric: explicit arms [pgvector, bm25], central BoundaryPolicy, shipped ReciprocalRankFusion k=60, rank-only, NoReranker) over arm A's production vector path and arm B's production lexical path with the per-arm EXTERNAL_NOTES floor N=5 appended beyond each arm's cut, PRE-boundary (the T-C69 per-kind quota lever, floor form — pure-additive admission, pre-registered BEFORE this run); chunk+query vectors replayed from the frozen artifact embed-backfill-snap-007-preload, zero API calls at run time
**Executor:** production code over a real Flyway-migrated Postgres, corpus loaded from the frozen snapshot; chunk vectors applied from the checksummed compute-once-freeze-forever artifact and query vectors served through the production EmbeddingProvider port; no retrieval SQL changed, no fusion code written (the shipped ReciprocalRankFusion runs unchanged); the per-arm EXTERNAL_NOTES floor (N=5) runs as a pure pre-boundary arm extension (deterministic probe doubling, zero API calls, no boundary interaction; pre-registered in POOL-COMPOSITION-PREREGISTRATION.md BEFORE this run) — code `8d7880b58d686b58fb09a81eb45fa82ee8ac936c`.
**Date:** 2026-10-02 | **Gold:** gold-v5 (120 queries; frozen) | **Determinism:** double retrieval pass, byte-identical aggregates (both views).

## Fabric provenance

- Orchestrator: the registered gap CLOSED — `RetrievalFabric` composes the explicit arms [pgvector, bm25] (never injection-implied, E-1 forward note), applies the serving boundary ONCE centrally pre-fusion, and fuses with the shipped `ReciprocalRankFusion` k=60 — no new fusion code, no retrieval SQL changed. Per-arm candidate bound 40.
- Notes floor: per-arm EXTERNAL_NOTES floor N=5 appended beyond each arm's candidate bound, PRE-boundary (the T-C69 per-kind quota lever, floor form — pure-additive admission: the recorded cut is untouched, the union can only grow, the boundary and the fusion are unchanged; deterministic probe doubling; pre-registered in POOL-COMPOSITION-PREREGISTRATION.md BEFORE this run).
- Frozen artifact `embed-backfill-snap-007-preload`: model `gemini-embedding-001` @ 768 dims; verified fail-closed against this run's frozen inputs before anything ran; SHA-256 echo in results.json `embedding_artifact.sha256_echo`.

## Overall (chunk axis, n=89 labeled queries)

- **C served (fabric over components as they stand, ALL denominator, 4510 embedded chunks):** recall@5 0.0616 · recall@10 0.1043 · recall@20 0.1612 · mrr 0.07 · ndcg@10 0.1095 · evidence_precision@10 0.0303 · false_positive_rate@10 0.9697
- **C compliant (central VALIDATED gate pre-fusion, 702 reachable chunks — the T-C05-closed configuration):** recall@5 0.0616 · recall@10 0.1043 · recall@20 0.1612 · mrr 0.07 · ndcg@10 0.1095 · evidence_precision@10 0.0303 · false_positive_rate@10 0.9697

## Per class (C served view)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.085 | 0.085 | 0.085 | 0.25 | 0.2631 | 0.04 | 0.96 |
| conceptual | 0.0256 | 0.1282 | 0.1949 | 0.0 | 0.0708 | 0.0308 | 0.9692 |
| exam_question | 0.75 | 1.0 | 1.0 | 0.6607 | 0.7104 | 0.15 | 0.85 |
| factual | 0.0727 | 0.1727 | 0.2273 | 0.0 | 0.1652 | 0.0727 | 0.9273 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 0.0 | 0.0 | 0.12 | 0.0 | 0.0 | 0.0 | 1.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0286 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.0 | 0.0 | 0.0833 | 0.0 | 0.0 | 0.0 | 1.0 |
| vague_learner | 0.0 | 0.0 | 0.25 | 0.0 | 0.0 | 0.0 | 1.0 |
| why_wrong | 0.05 | 0.0867 | 0.1067 | 0.1091 | 0.1533 | 0.05 | 0.95 |

## Per class (C compliant view — T-C05-closed configuration)

| class | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| calculation | 0.085 | 0.085 | 0.085 | 0.25 | 0.2631 | 0.04 | 0.96 |
| conceptual | 0.0256 | 0.1282 | 0.1949 | 0.0 | 0.0708 | 0.0308 | 0.9692 |
| exam_question | 0.75 | 1.0 | 1.0 | 0.6607 | 0.7104 | 0.15 | 0.85 |
| factual | 0.0727 | 0.1727 | 0.2273 | 0.0 | 0.1652 | 0.0727 | 0.9273 |
| mark_scheme | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| misconception | 0.0 | 0.0 | 0.12 | 0.0 | 0.0 | 0.0 | 1.0 |
| multi_spec_point | 0.0 | 0.0 | 0.0286 | 0.0 | 0.0 | 0.0 | 1.0 |
| prerequisite | 0.0 | 0.0 | 0.0833 | 0.0 | 0.0 | 0.0 | 1.0 |
| vague_learner | 0.0 | 0.0 | 0.25 | 0.0 | 0.0 | 0.0 | 1.0 |
| why_wrong | 0.05 | 0.0867 | 0.1067 | 0.1091 | 0.1533 | 0.05 | 0.95 |

## S8 gate arithmetic (§8 v1.1 re-index 2026-10-01, spec §8.1; ruling 1: ALL denominator = served view; VALIDATED bars on the compliant view; v1.0 reference retained)

- (a) ALL bars, served view — Recall@10: **0.1043** vs floor 0.192 -> FAIL

- (b) ALL bars, served view — MRR: **0.07** vs floor 0.1237 -> FAIL

- (c) ALL bars, served view — nDCG@10: **0.1095** vs floor 0.2316 -> FAIL

- (a2) VALIDATED bars, compliant view — Recall@10: **0.1043** vs floor 0.0734 -> PASS

- (b2) VALIDATED bars, compliant view — MRR: **0.07** vs floor 0.1184 -> FAIL

- (c2) VALIDATED bars, compliant view — nDCG@10: **0.1095** vs floor 0.1683 -> FAIL

- (d) SpecificationPoint resolution: SCORED (spec_resolution_hv): full-coverage 0.5169 · micro-average 0.869 on the ALL-denominator view over 84 gold points — first §8(d)-scoreable run: this run SETS the chunk-arm baseline; the §8(d) 'no regression beyond 1pp' rule applies from the next run onward, and no promotion claim is made on (d) here
- (e) p95 latency: not evaluable from records (A0 p95 not recorded); this run records retrieval-only p50/p95; a deployed hybrid adds the production query-embedding round-trip.
- (f) Validation boundary: served view surfaced **0** non-VALIDATED hits (the T-C20 vector-surface gap) — hard fail per §5.1 for the as-served configuration; the compliant view audited **0** by construction.
- (g) Per-class regression: trivially satisfied vs the zero A0 baseline.
- **VERDICT: NOT PROMOTED**

## Boundary + resolution axes

- VALIDATION_BOUNDARY_VIOLATIONS (served view): 0. **Named finding, not a silent patch:** the production vector surface predates T-C05; the compliant view's central pre-fusion gate (this run's new production capability) audited ZERO violations across all 120 queries — the gate is the T-C20 closure shape.
- Zero-result queries (served): 0/120.
- Compliant-starved queries: 0 (served non-empty but every eligible-rank hit sits on a non-VALIDATED paper).
- SpecificationPoint resolution: SCORED (spec_resolution_hv) — full-coverage 0.5169 · micro-average 0.869 over 84 gold points on 89 scored queries (served ALL-denominator view; the HV-mapped notes chunks are SUGGESTED content, so a near-zero number on a compliant view is honest production truth — see the section's dual-view caveat). First §8(d)-scoreable run: this run sets the chunk-arm baseline.
## Reading

- The fabric is production code but NOT a serving default: nothing in production constructs a RetrievalFabric; promotion happens in the owning lane with its own verification discipline after the owner accepts a verdict.
- C vs A/B: fusion rewards agreement; read the dual view against the recorded arms. The compliant view is the configuration a promotion would actually serve; the served view is the production-truth measurement the ratified gate runs on.
- Determinism: no clocks in scoring (latency is an ops field, measured outside rankings); aggregates byte-identical across the double pass.

## Authored analysis (T-C69 closeout — from recorded bytes + run005g_verify.py)

**Verdict: NOT PROMOTED (recorded honestly — a finding, not an argument).** The §8.1 v1.1 dual-view bars stand: (a) 0.1043 vs 0.1920 FAIL, (b) 0.0700 vs 0.1237 FAIL, (c) 0.1095 vs 0.2316 FAIL, (a2) 0.1043 vs 0.0734 **PASS (held)**, (b2)/(c2) FAIL. **(f) 0/0** (zero boundary violations, both views). The tranche's headline is the admission ledger below, independent of promotion.

### The primary endpoint — (d) partial recovery, 1 of 5 flips

- **(d) full-coverage 0.5056 → 0.5169 (45 → 46/89), micro 0.8571 → 0.8690 (72 → 73/84)** — monotone non-decreasing vs f with the superset premise **89/89** (the conditional theorem holds unconditionally; the HNSW/tie re-execution risk did not fire on the set), and still below the pre-registered exact-r8-reversion ceiling (0.5618/0.9167).
- **Admission ledger (mechanically derived):** g2-056 **ADMITTED+REVERTED** (1 covering EXTERNAL_NOTES carrier entered via the floor; full 0→1) — the lever works exactly as designed when the carrier is within reach. g2-011, g2-016, g2-059, g2-112 **MISS-AT-FLOOR** (4): the carriers' arm ranks exceed the floor's reach — g2-011/g2-059/g2-112 had 1–2 notes admitted, none covering; g2-016 admitted nothing (no notes surfaced beyond its cut at all). Per the prereg's own rule: the next lever is **arm-composition / MIN_COSINE (own dated pre-registration), NOT a bigger floor**.
- **Non-regression held everywhere:** zero f-full queries lost coverage, g2-061 unchanged (1/1 covered points), zero per-query covered-point drops on the held subset — the floor removed nothing, as the FLOOR-form design required.

### What the floor admitted (76 pool-growth refs; 72 are the lever)

- 72 EXTERNAL_NOTES refs admitted over 44 queries (mean 0.85, max 6/query) — all at fused ranks 41+ (the declared low-RRF-contribution surface; the fused top-20 stayed stable exactly as the prereg expected: recall@5/@10/@20 and evidence_precision@10 are **byte-identical to f**).
- **4 QUESTION_PAPER refs also appear in g's pools beyond f's** — NOT floor admissions (the wrapper admits only EXTERNAL_NOTES): these are ORDER-BY tie re-executions at the arms' limit-40 boundary (the g2-024 mechanism, additive-only this time — the superset invariant still held 89/89). Recorded as observed mechanism, not lever effect.
- Notes share: **r9 20.4% → f 15.3% → g 16.9%** — partial share recovery (+1.6pp); expectation deviation recorded: g's per-query notes maximum (24) exceeds the prereg's declared r9-era range top (f's max was 21; +N=5 on one query is arithmetically consistent) — benign under pure-additive admission, recorded honestly.

### The (a)/(b) movement is tie-re-execution, not admission

- **MRR 0.0626 → 0.0700 (+11.8%) and exam_question MRR 0.494 → 0.6607 (+33.7%)** — both recover EXACTLY to their r9-era values (f's dilution flags revert). With the top-20 SET stable (recall identical), the only mechanism that moves MRR without moving recall is an intra-top-20 ORDER swap among equal-fused-score refs — the same tie re-execution that added the 4 QP boundary refs. nDCG@10 0.1057 → 0.1095 (+3.6%) reads the same way. Attribution: re-execution noise, not the floor's doing; recorded so the movement is not mistaken for a lever effect.

### Cost

- Retrieval-only latency p50 308.2 → 1080.0 ms (p95 322.0 → 1206.5) — the probe-doubling's deterministic re-asks (~3.5× per query, both arms, both determinism passes). No API calls. Recorded as the (e) axis truth; a serving-side floor would need the same re-ask shape and this latency is part of its price.

### Guardrails held

- No production serving change (nothing in production reads `BENCH_NOTES_FLOOR`); no frozen artifact mutated (fail-closed verification echoed the preload-r9 SHAs); no recorded verdict re-judged; one lever only (reranker/weights ABSENT; the three-way guard executed in the run's own posture parse); no gold knowledge, no query-kind awareness, no per-query parameters in the mechanism (same N=5 for every query and both arms). Environment: PG 17.11 + pgvector 0.8.0 (version-exact vs the T-C59 recipe; Docker Hub anonymous auth was unavailable from this workspace, so PG came from PGDG debs and pgvector 0.8.0 was built from source — deviation from the image route recorded, versions pinned), JDK Corretto 25.0.4.1 + Maven 3.9.9, code `8d7880b` (merged main only).
