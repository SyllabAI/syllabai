#!/usr/bin/env python3
"""T-C83 prereg grounding — the MIN_COSINE production probe (precision-side
tranche licensed by the T-C72 prereg, Ruling 8 §3.2, Ruling 9 §3). All from
recorded bytes + the frozen preload-r9 artifact (no run, no bench execution,
no tuning).

v2 — the arm-A universe is the VALIDATED-only serving universe (the post-T-C20
production vector surface: ContentRetrievalService.search -> searchServingEligible,
4446 of snap-007's 4510 chunks; the 64 REJECTED-paper chunks never candidacy —
v1's 4510-universe census mis-slotted exactly them and was discarded, the
discrepancy ledger recorded here as the grounding's own finding trail). The
recorded run-005-f pools are byte-identical across the served and compliant
views (verified below) — the central boundary has nothing further to exclude.

Grounding chain:
1. (d) recompute self-checks on f (+ h for context) — byte-exact (machinery).
2. ARM-A RECONSTRUCTION: per query, the production vector-arm candidate list
   = top-40 over the VALIDATED universe by exact cosine (frozen preload,
   SHA-verified), production floor 0.50 applied, cosine DESC / chunk_ref ASC
   tiebreak. Cross-validated three ways against the recorded f bytes:
   (a) every reconstructed arm-A ref is in the recorded pool (89/89);
   (b) |R_A| = 40 on all queries (no floor under-fill at 0.50);
   (c) SCORE-CONSISTENCY: every pool ref's recorded fused score decomposes
       exactly under the reconstruction — arm-A-listed: s == 1/(60+r_A) or
       s == 1/(60+r_A) + 1/(60+r_B); bm25-only: s == 1/(60+r_B), r_B in
       [1,40]; and |pool| == 80 - |A∩B| (the union identity).
3. THE MIN_COSINE TRIM CENSUS at the T-C42 grid {0.55, 0.60, 0.65}:
   removed(q) = {r in R_A(q): cos(r) < theta} (the production constant's own
   post-cut filter shape, applied at the bench wrapper); the PURE-FILTER
   THEOREM (survivors' fused scores byte-identical — within-arm ranks and
   arm memberships unchanged; the shipped fusion's tie-break is
   (score, source, stableKey), position-independent) makes the predicted
   served order = f's recorded order minus removed, byte-exact. Predicted
   pools -> predicted (d) via the HV projection; predicted slices; per-query
   top-20 identity; the refill analysis (gold carriers entering the served
   horizon — the precision-side hypothesis test); the carrier-loss ledger
   (the exact (d) price); the under-fill ledger.
4. θ pinning — the declared interior-boundary rule: the T-C72 census band
   (f-pool minima on the flip queries) is 0.5859..0.6497 and the T-C42
   production probe's bucket grid is 0.05 wide; the unique grid boundary
   strictly inside the band is 0.60. Neighbors recorded as context, no sweep.
"""
import gzip
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

RECORDS = Path(__file__).resolve().parents[3]
RUNS = RECORDS / "evidence/bench-001/runs"
PROJECTION = RECORDS / "bench/evidence/chunk-sp-substrate-2026-09-27/chunk_spec_hv_projection.json"
GOLD_DIR = RECORDS / "bench/inputs/gold-r9"
SNAP7 = RECORDS / "bench/inputs/snapshot-r9/chunks.jsonl.gz"
PRELOAD = RECORDS / "bench/inputs/embeddings/preload-r9"

F1 = "run-005-f-r1"
H1 = "run-005-h-r1"
RECORDED_D = {F1: (0.5056, 0.8571), H1: (0.5843, 0.9405)}
N_SCORED, N_POINTS = 89, 84
RRF_K = 60
PER_ARM = 40
PROD_FLOOR = 0.50
THETAS = [0.55, 0.60, 0.65]
PINNED_THETA = 0.60
F_SLICES = {"recall@5": 0.0616, "recall@10": 0.1043, "recall@20": 0.1612,
            "mrr": 0.0626, "ndcg@10": 0.1057, "evidence_precision@10": 0.0303}
TOL = 1e-9

failures = []
findings = []


def fail(msg):
    failures.append(msg)
    print(f"  FAIL-CLOSED: {msg}")


def finding(msg):
    findings.append(msg)
    print(f"  FINDING: {msg}")


def r4(v):
    return round(v * 10000.0) / 10000.0


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_projection():
    art = json.loads(PROJECTION.read_text())
    ref_codes = defaultdict(set)
    for row in art["rows"]:
        if row["provenance"]["validation_status"] != "HUMAN_VALIDATED":
            fail(f"projection row not HUMAN_VALIDATED: {row.get('spec_code')}")
        for ref in row.get("chunk_refs", []):
            ref_codes[ref].add(row["spec_code"])
    return dict(ref_codes)


def load_gold():
    gold = {}
    for p in sorted(GOLD_DIR.glob("class_*.json")):
        for rec in json.loads(p.read_text()):
            gold[rec["id"]] = {
                "class": rec["class"],
                "points": set(rec.get("gold_spec_points") or []),
                "evidence": [(e["chunk_ref"], int(e["tier"])) for e in rec.get("gold_evidence") or []],
            }
    return gold


def load_snapshot():
    rows = json.load(gzip.open(SNAP7))
    kinds = {r["chunk_ref"]: r["kind"] for r in rows}
    states = {r["chunk_ref"]: r["paper_state"] for r in rows}
    return kinds, states


def load_embeddings():
    """Frozen preload-r9 vectors, SHA-verified against the recorded echo."""
    echo = json.loads((RUNS / H1 / "results.json").read_text())[
        "embedding_artifact"]["sha256_echo"]
    for fname in ["embeddings_chunks.jsonl", "embeddings_queries.jsonl"]:
        actual = sha256(PRELOAD / fname)
        if actual != echo[fname]:
            fail(f"{fname} sha {actual[:12]}... != recorded echo {echo[fname][:12]}...")
    chunks = {}
    for line in open(PRELOAD / "embeddings_chunks.jsonl"):
        r = json.loads(line)
        chunks[r["ref"]] = np.asarray(r["v"] if isinstance(r["v"], list)
                                      else json.loads(r["v"]), dtype=np.float64)
    queries = {}
    for line in open(PRELOAD / "embeddings_queries.jsonl"):
        r = json.loads(line)
        queries[r["qid"]] = np.asarray(r["v"] if isinstance(r["v"], list)
                                       else json.loads(r["v"]), dtype=np.float64)
    dims = {len(v) for v in chunks.values()} | {len(v) for v in queries.values()}
    if dims != {768}:
        fail(f"unexpected embedding dims {dims}")
    return chunks, queries


def score_chunks(ranked_refs, tier_by_ref):
    gold = {ref for ref, tier in tier_by_ref.items() if tier >= 1}
    gold2 = {ref for ref, tier in tier_by_ref.items() if tier == 2}
    ranked = list(ranked_refs)

    def recall(k):
        if not gold:
            return 0.0
        hits = sum(1 for ref in ranked[:k] if ref in gold)
        return hits / len(gold)

    r5, r10, r20 = recall(5), recall(10), recall(20)
    mrr = 0.0
    for n in range(min(len(ranked), 20)):
        if ranked[n] in gold2:
            mrr = 1.0 / (n + 1)
            break
    dcg = sum((2 ** tier_by_ref.get(ranked[n], 0) - 1) / math.log2(n + 2)
              for n in range(min(len(ranked), 10)))
    ideal = sorted((tier_by_ref.get(r, 0) for r in ranked), reverse=True)
    idcg = sum((2 ** ideal[n] - 1) / math.log2(n + 2) for n in range(min(len(ideal), 10)))
    ndcg = 0.0 if idcg == 0.0 else dcg / idcg
    hits = sum(1 for n in range(min(len(ranked), 10)) if tier_by_ref.get(ranked[n], 0) >= 1)
    precision = hits / 10.0
    fp = sum(1 for n in range(min(len(ranked), 10)) if tier_by_ref.get(ranked[n], 0) == 0) / 10.0
    return {"recall@5": r5, "recall@10": r10, "recall@20": r20,
            "mrr": mrr, "ndcg@10": ndcg, "evidence_precision@10": precision,
            "false_positive_rate@10": fp}


def agg(scored_ids, per_query_scores):
    out = {}
    for k in ["recall@5", "recall@10", "recall@20", "mrr", "ndcg@10",
              "evidence_precision@10", "false_positive_rate@10"]:
        out[k] = r4(sum(per_query_scores[qid][k] for qid in scored_ids) / len(scored_ids))
    return out


def main():
    ref_codes = load_projection()
    gold = load_gold()
    kinds, states = load_snapshot()
    runs = {rid: json.loads((RUNS / rid / "results.json").read_text())
            for rid in [F1, H1]}
    h = runs[H1]

    print("# T-C83 prereg grounding — the MIN_COSINE production probe (precision side)")
    fb = h["fabric"]
    print(f"# h posture: providers {fb['providers']} | per_arm_limit {fb['per_arm_limit']}")
    if h["code_version"] != "c346d645d119708bcf0f5d9cac2ae15131654970":
        fail(f"h code_version {h['code_version']} != merged main c346d64")

    scored_ids = sorted(h["per_query_chunks"].keys())
    if len(scored_ids) != N_SCORED:
        fail(f"scored {len(scored_ids)} != {N_SCORED}")
    pools = {qid: set(e["ranked_refs"]) for qid, e in runs[F1]["per_query_chunks"].items()}
    ranks = {qid: list(e["ranked_refs"]) for qid, e in runs[F1]["per_query_chunks"].items()}
    scores = {qid: dict(zip(e["ranked_refs"], e["fused_scores"]))
              for qid, e in runs[F1]["per_query_chunks"].items()}
    cpools = {qid: set(e["ranked_refs"]) for qid, e in runs[F1]["per_query_compliant"].items()}
    cranks = {qid: list(e["ranked_refs"]) for qid, e in runs[F1]["per_query_compliant"].items()}
    cscores = {qid: dict(zip(e["ranked_refs"], e["fused_scores"]))
               for qid, e in runs[F1]["per_query_compliant"].items()}

    # == 1. (d) self-checks ==================================================
    print("\n== 1. (d) recompute self-checks (recorded vs recomputed)")
    gold_total = sum(len(gold[qid]["points"]) for qid in scored_ids)
    if gold_total != N_POINTS:
        fail(f"gold points across scored {gold_total} != {N_POINTS}")

    def coverage(pool_by_qid):
        cov = {}
        for qid in scored_ids:
            codes = set()
            for ref in pool_by_qid[qid]:
                codes |= ref_codes.get(ref, set())
            pts = gold[qid]["points"]
            cov[qid] = {"covered": pts & codes, "full": bool(pts) and pts <= codes}
        return cov

    d_values = {}
    for rid in [F1, H1]:
        rpools = {qid: set(e["ranked_refs"]) for qid, e in runs[rid]["per_query_chunks"].items()}
        c = coverage(rpools)
        full = sum(1 for qid in scored_ids if c[qid]["full"])
        micro = sum(len(c[qid]["covered"]) for qid in scored_ids)
        rf, rm = RECORDED_D[rid]
        ok = abs(full / N_SCORED - rf) < 5e-5 and abs(micro / N_POINTS - rm) < 5e-5
        d_values[rid] = (full, micro)
        print(f"  {rid}: full {full}/{N_SCORED} = {full/N_SCORED:.4f} · "
              f"micro {micro}/{N_POINTS} = {micro/N_POINTS:.4f} · recorded {rf}/{rm} · "
              f"{'OK' if ok else 'MISMATCH'}")
        if not ok:
            fail(f"(d) self-check mismatch for {rid}")

    # == 2. the two views are one on this snapshot ===========================
    print("\n== 2. served vs compliant pools (the recorded subject-level-branch shape)")
    identical = sum(1 for qid in scored_ids if pools[qid] == cpools[qid])
    print(f"  pool(f) served == compliant on {identical}/{N_SCORED} queries")
    if identical != N_SCORED:
        fail(f"served/compliant pools differ on {N_SCORED - identical} queries — "
             f"the census must then model the views separately")

    # == 3. arm-A reconstruction (VALIDATED universe) =========================
    print("\n== 3. arm-A reconstruction from the frozen preload "
          "(VALIDATED universe, exact cosine, floor 0.50, top-40)")
    chunks, queries = load_embeddings()
    universe = sorted(chunks.keys())
    val_universe = sorted(r for r in universe if states.get(r) == "VALIDATED")
    print(f"  snap-007 universe {len(universe)}; VALIDATED serving universe "
          f"{len(val_universe)} (the post-T-C20 arm-A surface; "
          f"{len(universe) - len(val_universe)} REJECTED-paper chunks never candidacy)")
    if len(val_universe) != 4446:
        fail(f"VALIDATED universe {len(val_universe)} != 4446")
    mat = np.stack([chunks[r] for r in val_universe])
    norms = np.linalg.norm(mat, axis=1)

    arm = {}
    cos_of = {}
    for qid in scored_ids:
        qv = queries[qid]
        qn = np.linalg.norm(qv)
        cos = (mat @ qv) / np.maximum(norms * qn, 1e-12)
        elig = sorted(((val_universe[i], float(cos[i])) for i in range(len(val_universe))
                       if cos[i] >= PROD_FLOOR), key=lambda t: (-t[1], t[0]))
        arm[qid] = {ref: i + 1 for i, (ref, _) in enumerate(elig[:PER_ARM])}
        for ref, c in elig[:PER_ARM]:
            cos_of[(qid, ref)] = c

    n_in = n_tot = 0
    bad = []
    overlap_by_q = {}
    for qid in scored_ids:
        a = arm[qid]
        n_tot += len(a)
        n_in += sum(1 for r in a if r in pools[qid])
        for r in a:
            if r not in pools[qid]:
                finding(f"arm-A ref not in recorded pool (tie band): {qid} {r[:16]}")
        ov = 0
        for r in pools[qid]:
            s = scores[qid].get(r)
            if s is None:
                bad.append((qid, r, "no recorded score"))
                continue
            if r in a:
                resid = s - 1.0 / (RRF_K + a[r])
                if abs(resid) < TOL:
                    pass
                elif 1.0 / (RRF_K + PER_ARM) - TOL <= resid <= 1.0 / (RRF_K + 1) + TOL:
                    ov += 1
                else:
                    bad.append((qid, r, f"A-listed resid {resid:.9f} not a bm25 term"))
            else:
                if not (1.0 / (RRF_K + PER_ARM) - TOL <= s <= 1.0 / (RRF_K + 1) + TOL):
                    bad.append((qid, r, f"bm25-only score {s:.9f} outside the rank window"))
        overlap_by_q[qid] = ov
    # per-query bm25-list-size identity: the bm25 arm may under-fill (FTS
    # matches fewer than the limit), so |B| is DERIVED, not assumed 40:
    #   |pool| = |A| + |B| - |A∩B|  =>  |B| = |pool| - 40 + ov
    # and independently |B| = (refs carrying a bm25 term) = ov + bm25_only.
    bm25_sizes = {}
    bm25_identity_ok = True
    for qid in scored_ids:
        bm25_only = 0
        for r in pools[qid]:
            if r in arm[qid]:
                continue
            s = scores[qid][r]
            if 1.0 / (RRF_K + PER_ARM) - TOL <= s <= 1.0 / (RRF_K + 1) + TOL:
                bm25_only += 1
        derived = len(pools[qid]) - PER_ARM + overlap_by_q[qid]
        counted = overlap_by_q[qid] + bm25_only
        bm25_sizes[qid] = derived
        if derived != counted or not (0 <= derived <= PER_ARM):
            bm25_identity_ok = False
            finding(f"bm25 identity {qid}: derived |B|={derived} != counted {counted}")
    print(f"  arm-A refs in recorded pool: {n_in}/{n_tot} "
          f"({'BYTE-EXACT' if n_in == n_tot else 'FINDINGS ABOVE'})")
    if n_in != n_tot:
        fail(f"arm-A reconstruction membership imperfect: {n_in}/{n_tot}")
    print(f"  |R_A| = {PER_ARM} on all queries: "
          f"{'OK' if all(len(a) == PER_ARM for a in arm.values()) else 'FAIL'}")
    print(f"  score-consistency violations: {len(bad)}")
    for qid, r, why in bad[:6]:
        finding(f"score {qid} {r[:16]}: {why}")
    if bad:
        fail(f"{len(bad)} score-consistency violations — reconstruction unusable")
    n_bm25_firing = sum(1 for v in bm25_sizes.values() if v > 0)
    print(f"  bm25-list identity |pool| = 40 + |B| - |A∩B| with |B| = ov + bm25_only "
          f"on all queries: {'OK' if bm25_identity_ok else 'FAIL'}")
    if not bm25_identity_ok:
        fail("bm25-list identity broken")
    n_bm25_only = sum(len(pools[qid] - set(arm[qid])) for qid in scored_ids)
    n_bm25_listed = sum(overlap_by_q.values()) + n_bm25_only
    print(f"  bm25 arm fires on {n_bm25_firing}/{N_SCORED} queries; bm25-listed refs "
          f"total {n_bm25_listed} (bm25-only {n_bm25_only}, both-arms "
          f"{sum(overlap_by_q.values())}) — the lexical arm's recorded sparsity")

    # == 4. the MIN_COSINE trim census ========================================
    print("\n== 4. trim census at the T-C42 grid {0.55, 0.60, 0.65}")
    bands = defaultdict(int)
    for qid in scored_ids:
        for r in pools[qid]:
            c = cos_of.get((qid, r))
            if c is None:
                bands["bm25-only (no cosine candidacy)"] += 1
            elif c < 0.55:
                bands["cos in [0.50, 0.55)"] += 1
            elif c < 0.60:
                bands["cos in [0.55, 0.60)"] += 1
            elif c < 0.65:
                bands["cos in [0.60, 0.65)"] += 1
            else:
                bands["cos >= 0.65"] += 1
    print("  recorded f-pool refs by cosine band:")
    for k in ["bm25-only (no cosine candidacy)", "cos in [0.50, 0.55)",
              "cos in [0.55, 0.60)", "cos in [0.60, 0.65)", "cos >= 0.65"]:
        print(f"    {k}: {bands.get(k, 0)}")

    census = {}
    for theta in THETAS:
        removed = {qid: {r for r in arm[qid] if cos_of[(qid, r)] < theta}
                   for qid in scored_ids}
        trim_total = sum(len(v) for v in removed.values())
        qhit = sum(1 for qid in scored_ids if removed[qid])
        pred_pools = {qid: pools[qid] - removed[qid] for qid in scored_ids}
        pred_lists = {qid: [r for r in ranks[qid] if r not in removed[qid]]
                      for qid in scored_ids}
        cov = coverage(pred_pools)
        full = sum(1 for qid in scored_ids if cov[qid]["full"])
        micro = sum(len(cov[qid]["covered"]) for qid in scored_ids)
        pq = {}
        for qid in scored_ids:
            tier = {ref: t for ref, t in gold[qid]["evidence"]}
            pq[qid] = score_chunks(pred_lists[qid], tier)
        sl = agg(scored_ids, pq)
        top20_changed = 0
        gold_into_top20 = 0
        underfill_total = sum(len(removed[qid]) for qid in scored_ids)
        for qid in scored_ids:
            f20 = ranks[qid][:20]
            p20 = pred_lists[qid][:20]
            if set(f20) != set(p20) or f20 != p20:
                top20_changed += 1
                tier = {ref: t for ref, t in gold[qid]["evidence"]}
                entered = [r for r in p20 if r not in f20]
                gold_into_top20 += sum(1 for r in entered if tier.get(r, 0) >= 1)
        # subset invariant check (the trimmed pool must be a subset of f's)
        subset_ok = all(pred_pools[qid] <= pools[qid] for qid in scored_ids)
        census[theta] = {
            "trim_total": trim_total, "queries_hit": qhit, "full": full,
            "micro": micro, "slices": sl, "top20_changed": top20_changed,
            "gold_into_top20": gold_into_top20, "underfill": underfill_total,
            "removed": removed, "pred_lists": pred_lists, "pred_pools": pred_pools,
            "subset_ok": subset_ok,
        }
        print(f"  θ={theta:.2f}: trimmed {trim_total} vector refs on {qhit} queries "
              f"(under-fill {underfill_total} slots; subset invariant "
              f"{'OK' if subset_ok else 'BROKEN'})")
        print(f"        predicted (d): full {full}/{N_SCORED} = {full/N_SCORED:.4f} · "
              f"micro {micro}/{N_POINTS} = {micro/N_POINTS:.4f} "
              f"(f: {d_values[F1][0]}/{d_values[F1][1]})")
        print(f"        predicted slices vs f: " +
              " ".join(f"{k} {sl[k]}" for k in ["recall@5", "recall@10", "recall@20",
                                                 "mrr", "ndcg@10", "evidence_precision@10"]))
        print(f"        top-20 changed on {top20_changed} queries; gold carriers "
              f"entering top-20: {gold_into_top20}")

    # == 5. carrier-loss ledger at the pinned theta ===========================
    print(f"\n== 5. carrier-loss ledger at the pinned θ={PINNED_THETA:.2f}")
    pin = census[PINNED_THETA]
    losses = []
    for qid in scored_ids:
        pts = gold[qid]["points"]
        codes_before = set()
        for r in pools[qid]:
            codes_before |= ref_codes.get(r, set())
        codes_after = set()
        for r in pin["pred_pools"][qid]:
            codes_after |= ref_codes.get(r, set())
        lost_pts = (pts & codes_before) - (pts & codes_after)
        if lost_pts:
            carriers = sorted(r for r in pin["removed"][qid]
                              if ref_codes.get(r, set()) & lost_pts)
            losses.append((qid, sorted(lost_pts), carriers))
    if losses:
        for qid, pts, carriers in losses:
            print(f"    {qid}: loses {pts} (carriers "
                  f"{[(c[:16], round(cos_of[(qid, c)], 4)) for c in carriers]})")
        pf, pm = d_values[F1]
        print(f"    predicted (d): {pin['full']}/{N_SCORED} · {pin['micro']}/{N_POINTS} "
              f"vs f {pf}/{pm} (full Δ{pin['full']-pf:+d}, micro Δ{pin['micro']-pm:+d})")
    else:
        pf, pm = d_values[F1]
        print(f"    no coverage losses — (d) predicted BYTE-STABLE vs f "
              f"({pin['full']}/{N_SCORED} · {pin['micro']}/{N_POINTS})")

    # == 6. θ pinning =========================================================
    print("\n== 6. θ pinning — the declared interior-boundary rule")
    print("  Recorded T-C72 census band (f-pool minima on the flip queries): "
          "0.5859 .. 0.6497; carrier cosines 0.5811 .. 0.6336.")
    print("  The T-C42 production probe's bucket grid is 0.05 wide; the unique grid")
    print("  boundary strictly inside the recorded band is 0.60. 0.55 sits below the")
    print("  band (the census above: ZERO pool refs in [0.50, 0.55) — a null probe);")
    print("  0.65 sits above it (trims the whole band — superset of every recorded")
    print("  carrier). θ = 0.60; any other value = a dated new prereg (no sweep).")
    pin_slices = pin["slices"]
    print(f"\n  PINNED θ=0.60 predictions (the run's falsifiable targets):")
    print(f"    (i) subset invariant: run pool ⊆ f pool per query, 89/89")
    print(f"    (ii) removed-ref ledger byte-exact: {pin['trim_total']} vector refs "
          f"on {pin['queries_hit']} queries")
    print(f"    (iii) (d) full {pin['full']}/{N_SCORED} = {pin['full']/N_SCORED:.4f} · "
          f"micro {pin['micro']}/{N_POINTS} = {pin['micro']/N_POINTS:.4f}")
    print(f"    (iv) served order = f's recorded order minus removals on every query")
    f_exact = sum(1 for qid in scored_ids
                  if pin["pred_lists"][qid] == [r for r in ranks[qid]
                                                if r not in pin["removed"][qid]])
    print(f"         (holds by construction on {f_exact}/{N_SCORED} predicted lists)")
    print(f"    (v) slices: " + " ".join(f"{k} {pin_slices[k]}" for k in F_SLICES))
    print(f"    (vi) top-20 changed on {pin['top20_changed']} queries; gold carriers "
          f"entering the served horizon: {pin['gold_into_top20']}")

    print(f"\n# grounding verdict: {len(failures)} failures, {len(findings)} findings")
    for f_ in failures:
        print(f"# FAIL: {f_}")
    for f_ in findings:
        print(f"# FINDING: {f_}")
    if failures:
        sys.exit(1)
    print("# GROUNDING OK — the prereg's numbers are pinned from these bytes")


if __name__ == "__main__":
    main()
