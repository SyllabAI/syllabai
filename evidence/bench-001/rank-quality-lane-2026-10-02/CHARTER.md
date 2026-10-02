# Rank-quality lane — charter (T-C63, commissioning tranche)

**Status:** COMMISSIONED (operator IM trace `1a0fc8c1e8b73939`, "commission the rank-quality lane").
**Why this lane exists:** run-005-c-r9 measured the wave unlock and located the residual gap: recall@10 **doubled** (0.0515 → 0.1043) and the first §8.1 bar ever passed is the VALIDATED recall bar — but MRR is **0.0700 at recall@20 0.1612**, i.e. the gold evidence is *found* at median depth ~14 and the bars price it at depth ≤10. The (d) recompute ledger (`run-005-c-r9/S8D-RULING-REVIEW.md`) shows the same shape at the spec-point layer: the HV-mapped notes carriers were displaced from r8 ranks 7–20 past the top-20 horizon by newly-served QP/MS/EQ paper mass. The binding constraint is **rank quality**, not pool coverage. Validation volume is nearly exhausted anyway: the wave-2 post-verify census shows the subject-branch SUGGESTED surface at zero (paper axis 4 QP + 4 MS remain).

## The two levers (registry + fabric natives)

1. **Arm D (this tranche):** registry row D — "C + reranker behind the `EvidenceReranker` port". The production fabric is rank-only by construction (`RetrievalFabric` doc: "the fabric does NOT truncate", "fusion ranks-only, provider scores never read", `NoReranker` default); the reranker lives downstream of fusion, exactly where the tutor path's port sits (T-024). The bench measures arm D by re-running the *same* run-005 replay with a deterministic reranker applied to the fused pool — no new fusion code, no boundary change, no main-code change.
2. **Fusion weights (tranche 3, separately pre-registered):** the shipped 4-arg `RetrievalFabric` ctor accepts per-kind `sourceWeights` (`PLAN_V2_WEIGHTS` posture); the bench replay currently uses the unweighted 3-arg ctor. A weighted replay is one measured datapoint away — but it is a DIFFERENT lever and gets its own pre-registration AFTER arm D's verdict is recorded (one lever at a time, attribution honesty).

## Arm D instrument (tranche 1, this commission)

- `bench/LexicalPrecisionReranker` — implements the main `EvidenceReranker` port in bench scope: deterministic query×content rescoring of the fused pool. Algorithm **pre-registered here, before any run** (spec §9 forbids tuning loops against the frozen set; r3 anti-gaming doctrine):
  - Tokenizer: lowercase; split on non-alphanumeric; digit- and letter-runs are tokens (spec-code fragments like `4ch1`, `2`, `5c` are ordinary tokens — NO spec-code special-casing, NO kind-awareness, NO gold knowledge).
  - IDF: per-query, over the rerank pool itself: `idf(t) = ln(1 + (N − df(t) + 0.5)/(df(t) + 0.5))`, N = pool size (self-contained ⇒ no corpus-statistics dependency ⇒ no snapshot drift; boilerplate present in every candidate self-annihilates).
  - Score: `Σ_{t ∈ unique query tokens} idf(t) · tf(t)·(k1+1)/(tf(t)+k1)` with **k1 = 1.2 (the BM25 default) and b = 0 (NO length normalization)**. The b=0 choice is deliberate and declared now: the spec-mapped notes carriers are systematically longer than QP/MS chunks; a length penalty would demote exactly the evidence §8(d) prices. Changing k1/b after seeing results is the anti-gaming violation — it requires a dated new pre-registration and a new run.
  - Ordering: score desc; ties broken by fused rank ascending (stable, deterministic). `rerankScore` set on every item. Never invents or drops candidates (port contract).
- `bench/RerankedRetrieval` — wraps a `RetrievalFabric` + the reranker: `retrieve()` = fabric output → bridge to `EvidenceItem`s (locator in `documentId` for the bridge back) → `rerank(query, items)` → reorder the SAME `FusedCandidate`s. The boundary stays inside the inner fabric (pre-fusion, untouched); the reranker can only reorder what fusion produced — (f) is structurally unaffected.
- `Run005C` surgical extension (absent-path byte-identity precedent, S8D §5): `BENCH_ARM_D_RERANKER` (default "" → NoReranker path byte-identical) + `BENCH_RUN_ID` (default "run-005-c"; fixes the r9-era hardcode per the T-C40 bproxy env-identity lesson). Both views' fabrics wrap identically; §8(d) scores the RERANKED served lists (that is the point — compositionality recovery is what the run measures); the double-pass determinism contract covers the reranked path (pure function ⇒ byte-identical second pass or abort).

## Pre-registered expectations (recorded BEFORE the run; the run records PASS/FAIL honestly)

- MRR and nDCG@10 are the targets (the bars' rank-quality axes): expected to rise from r9's 0.0700/0.1113.
- recall@20 is set-invariant when the reranked top-20 is a permutation of the fused top-20; if deeper gold is pulled into the top-20 it may rise — a material DROP would itself be a finding.
- recall@10 may move in either direction (reordering across the 10/20 boundary is the mechanism).
- §8(d): the 9 flipped queries' carriers (r8 ranks 7–20) are the recovery candidates; partial recovery expected, not guaranteed — the (d) 1pp rule is evaluated against the r8 baseline as recorded, with the spec-owner ruling still pending (the S8D-RULING-REVIEW pack is the ruling input; under the compositionality reading the raw movement counts as recorded).
- (g): any per-class regression >15% relative gets its written tradeoff note; (f) must stay 0/0.

## Evaluation protocol (tranche 2)

`BENCH_RUN_ID=run-005-d BENCH_ARM_D_RERANKER=lexical_precision` over the SAME frozen inputs as r9 (snap-007 × gold-r9 × preload-r9 — no re-freeze: the comparison basis is the recorded r9 fabric), output `evidence/bench-001/runs/run-005-d-r1/`, full §8.1 v1.1 dual-view gate + (d)(e)(f)(g), verdict recorded honestly (NOT PROMOTED is a finding, not an argument). Environment recipe per T-C59: JDK 25.0.4.1 + Maven 3.9.9 + user-space PostgreSQL 17.11 + pgvector 0.8.0 (Debian-native debs, apt-get download + dpkg -x), disposable cluster, Flyway V1→V59.

## Guardrails (restated)

No production serving change — nothing in production constructs a reranking fabric; arm promotion happens in the owning lane with its own verification discipline after the owner accepts a §8-passing verdict (harness spec §9). No frozen artifact is mutated. No tuning against the frozen set. No recorded verdict is re-judged; new thresholds or parameters mean new runs.
