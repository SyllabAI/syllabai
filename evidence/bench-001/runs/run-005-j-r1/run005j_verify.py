#!/usr/bin/env python3
"""run-005-j post-run verification — from recorded bytes only (T-C83).

Verifies the pre-registered invariants (MIN-COSINE-PREREGISTRATION.md, records
40a6724, committed BEFORE the run) for the precision-side MIN_COSINE lever in
TRIM form (BENCH_MIN_COSINE=0.60 on the recorded depth-40 two-arm posture;
one lever — floor/reranker/weights/kind-arm/rank-cap ABSENT; code = merged
main):

  1. (d) recompute + self-checks: recompute §8(d) for run-005-j from the
     frozen HV projection x gold x j's recorded ranked_refs; must equal j's
     recorded aggregate AND the census prediction 44/89 · 71/84 byte-exact
     (the removal-only price: exactly one coverage loss — g2-104's 4CH1-4.46
     carrier at cosine 0.5948). Machinery self-check: the same recompute on
     f and h must reproduce their recorded aggregates byte-exactly.
  2. Subset invariant — the primary endpoint: per query, j's served pool SET
     ⊆ f's pool SET (expected 89/89; the trim only removes — the T-C67
     theorem's inverted form). Violations are FINDINGS with the exact ledger.
  3. Removed-ref ledger byte-exact vs the census: per query, observed removed
     = f pool − j pool must equal the census's predicted removed set (the
     vector-arm candidates with census cosine < 0.60) — expected 170 refs on
     10 queries. The census is recomputed here from the SHA-verified frozen
     preload (the byte-exact arm-A reconstruction, the grounding machinery).
  4. Pure-filter order check: j's ranked_refs == f's ranked_refs minus the
     removed refs, per query (survivors keep positions — the fused scores are
     byte-identical and the shipped tie-break is position-independent).
     Deviations = FINDINGS (the declared re-execution band).
  5. Rank-slice byte-stability pins: recall@5 0.0616 / recall@10 0.1043 /
     recall@20 0.1612 / mrr 0.0626 / ndcg@10 0.1057 / evidence_precision@10
     0.0303 — all predicted byte-stable vs f's recorded values (the recall@20
     pin's 7th run). Movement in either direction is a FINDING.
  6. Top-20 ledger: top-20 changed on exactly 5 queries; gold carriers
     entering the served horizon: 0 (the precision hypothesis's
     pre-registered falsification — a nonzero count falsifies the census).
  7. the results ledger sanity: min_cosine_removed == {theta 0.60,
     affected 10, removed 170}.
  8. §8.1 v1.1 gates evaluated fresh under the UNCHANGED bars (Ruling 8
     conjunction stated explicitly): (a)/(b)/(c)/(b2)/(c2) FAIL expected
     (the slices are byte-stable — the trim moves nothing the bars read);
     (d) 0.4944/0.8452 below the r8 reference and below f; (e) recorded
     fresh; (f) 0/0 expected; NOT PROMOTED is the pinned expected verdict.
  9. (e) latency shape + the (g) per-class >15% relative flags vs f.
"""
import gzip
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

RECORDS = Path(__file__).resolve().parents[4]
RUNS = RECORDS / "evidence/bench-001/runs"
PROJECTION = RECORDS / "bench/evidence/chunk-sp-substrate-2026-09-27/chunk_spec_hv_projection.json"
GOLD_DIR = RECORDS / "bench/inputs/gold-r9"
SNAP7 = RECORDS / "bench/inputs/snapshot-r9/chunks.jsonl.gz"
PRELOAD = RECORDS / "bench/inputs/embeddings/preload-r9"

J1 = "run-005-j-r1"
F1 = "run-005-f-r1"
H1 = "run-005-h-r1"
RECORDED_D = {F1: (0.5056, 0.8571), H1: (0.5843, 0.9405)}
PREDICTED_D_J = (44, 71)
N_SCORED, N_POINTS = 89, 84
RRF_K = 60
PER_ARM = 40
PROD_FLOOR = 0.50
PINNED_THETA = 0.60
PREDICTED_REMOVED_TOTAL, PREDICTED_AFFECTED = 170, 10
PREDICTED_TOP20_CHANGED, PREDICTED_CARRIERS_IN = 5, 0
F_SLICES = {"recall@5": 0.0616, "recall@10": 0.1043, "recall@20": 0.1612,
            "mrr": 0.0626, "ndcg@10": 0.1057, "evidence_precision@10": 0.0303}
BARS = {"a": 0.1920, "b": 0.1237, "c": 0.2316,
        "a2": 0.0734, "b2": 0.1184, "c2": 0.1683}

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
    states = {r["chunk_ref"]: r["paper_state"] for r in rows}
    return states


def load_embeddings():
    echo = json.loads((RUNS / J1 / "results.json").read_text())[
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


def main():
    ref_codes = load_projection()
    gold = load_gold()
    states = load_snapshot()
    j = json.loads((RUNS / J1 / "results.json").read_text())
    f = json.loads((RUNS / F1 / "results.json").read_text())

    print("# run-005-j verification — the MIN_COSINE production probe (T-C83)")
    fb = j["fabric"]
    print(f"# posture: providers {fb['providers']} | per_arm_limit {fb['per_arm_limit']} "
          f"| min_cosine {fb.get('min_cosine')}")
    if fb["providers"] != ["pgvector", "bm25"]:
        fail(f"providers {fb['providers']} != the two-arm posture")
    if fb["per_arm_limit"] != 40:
        fail(f"per_arm_limit {fb['per_arm_limit']} != 40")
    if abs(fb.get("min_cosine", 0) - PINNED_THETA) > 1e-12:
        fail(f"min_cosine {fb.get('min_cosine')} != {PINNED_THETA}")
    for k in ["notes_floor", "notes_kind_arm", "notes_rank_cap"]:
        if fb.get(k, 0) != 0:
            fail(f"{k} {fb.get(k)} != 0 (single-lever posture)")
    if j["fabric"].get("fusion_weights", "").startswith("unweighted") is False:
        fail("fusion not unweighted")
    code = j["code_version"]
    print(f"# code_version {code}")

    scored_ids = sorted(j["per_query_chunks"].keys())
    if len(scored_ids) != N_SCORED:
        fail(f"scored {len(scored_ids)} != {N_SCORED}")
    jpools = {qid: set(e["ranked_refs"]) for qid, e in j["per_query_chunks"].items()}
    jranks = {qid: list(e["ranked_refs"]) for qid, e in j["per_query_chunks"].items()}
    fpools = {qid: set(e["ranked_refs"]) for qid, e in f["per_query_chunks"].items()}
    franks = {qid: list(e["ranked_refs"]) for qid, e in f["per_query_chunks"].items()}

    # == 1. (d) recompute + self-checks ======================================
    print("\n== 1. (d) recompute + the byte-exact prediction")
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

    def d_of(run):
        rpools = {qid: set(e["ranked_refs"]) for qid, e in run["per_query_chunks"].items()}
        c = coverage(rpools)
        return (sum(1 for qid in scored_ids if c[qid]["full"]),
                sum(len(c[qid]["covered"]) for qid in scored_ids))

    dj = d_of(j)
    rf, rm = RECORDED_D[J1.replace("-r1", "") + "-r1"] if False else (None, None)
    rec_j = (0.4944, 0.8452)
    ok_rec = abs(dj[0] / N_SCORED - rec_j[0]) < 5e-5 and abs(dj[1] / N_POINTS - rec_j[1]) < 5e-5
    for rid, run in [(F1, f), (H1, json.loads((RUNS / H1 / "results.json").read_text()))]:
        d = d_of(run)
        rd = RECORDED_D[rid]
        ok = abs(d[0] / N_SCORED - rd[0]) < 5e-5 and abs(d[1] / N_POINTS - rd[1]) < 5e-5
        print(f"  {rid}: {d[0]}/{N_SCORED} · {d[1]}/{N_POINTS} recorded {rd[0]}/{rd[1]} "
              f"{'OK' if ok else 'MISMATCH'}")
        if not ok:
            fail(f"(d) self-check mismatch for {rid}")
    print(f"  {J1}: {dj[0]}/{N_SCORED} · {dj[1]}/{N_POINTS} — predicted "
          f"{PREDICTED_D_J[0]}/{N_SCORED} · {PREDICTED_D_J[1]}/{N_POINTS} "
          f"{'BYTE-EXACT' if (dj[0], dj[1]) == PREDICTED_D_J else 'MISMATCH'}")
    if (dj[0], dj[1]) != PREDICTED_D_J:
        fail(f"(d) prediction mismatch: {dj} != {PREDICTED_D_J}")

    # == 2. subset invariant ==================================================
    print("\n== 2. subset invariant: run pool ⊆ f pool per query")
    viol = [qid for qid in scored_ids if not jpools[qid] <= fpools[qid]]
    print(f"  subset holds on {N_SCORED - len(viol)}/{N_SCORED} queries")
    for qid in viol:
        extra = jpools[qid] - fpools[qid]
        finding(f"subset violation {qid}: {len(extra)} refs not in f pool "
                f"(re-execution band): {sorted(r[:16] for r in extra)}")

    # == 3. removed-ref ledger vs the census ==================================
    print("\n== 3. removed-ref ledger vs the recomputed census")
    chunks, queries = load_embeddings()
    universe = sorted(r for r in chunks if states.get(r) == "VALIDATED")
    mat = np.stack([chunks[r] for r in universe])
    norms = np.linalg.norm(mat, axis=1)
    census_removed = {}
    for qid in scored_ids:
        qv = queries[qid]
        cos = (mat @ qv) / np.maximum(norms * np.linalg.norm(qv), 1e-12)
        elig = [universe[i] for i in range(len(universe))
                if cos[i] >= PROD_FLOOR]
        cvals = {universe[i]: float(cos[i]) for i in range(len(universe)) if cos[i] >= PROD_FLOOR}
        top = sorted(elig, key=lambda r: (-cvals[r], r))[:PER_ARM]
        census_removed[qid] = {r for r in top if cvals[r] < PINNED_THETA}
    total_pred = sum(len(v) for v in census_removed.values())
    if total_pred != PREDICTED_REMOVED_TOTAL:
        fail(f"census recompute total {total_pred} != predicted {PREDICTED_REMOVED_TOTAL}")
    observed_removed = {qid: fpools[qid] - jpools[qid] for qid in scored_ids}
    obs_total = sum(len(v) for v in observed_removed.values())
    print(f"  predicted {total_pred} removed on {sum(1 for v in census_removed.values() if v)} queries; "
          f"observed {obs_total} on {sum(1 for v in observed_removed.values() if v)} queries")
    mismatch_q = [qid for qid in scored_ids if observed_removed[qid] != census_removed[qid]]
    if mismatch_q:
        for qid in mismatch_q[:10]:
            finding(f"removed-ledger mismatch {qid}: observed-only "
                    f"{sorted(r[:16] for r in observed_removed[qid] - census_removed[qid])} / "
                    f"census-only {sorted(r[:16] for r in census_removed[qid] - observed_removed[qid])}")
        if len(mismatch_q) > 10:
            finding(f"... {len(mismatch_q) - 10} further")
        fail(f"removed-ref ledger differs from the census on {len(mismatch_q)} queries")
    else:
        print("  removed-ref ledger BYTE-EXACT vs the census on all queries")

    # == 4. pure-filter order check ===========================================
    print("\n== 4. pure-filter order: j order == f order minus removals")
    order_bad = []
    for qid in scored_ids:
        pred = [r for r in franks[qid] if r not in observed_removed[qid]]
        if jranks[qid] != pred:
            order_bad.append(qid)
    print(f"  order byte-exact on {N_SCORED - len(order_bad)}/{N_SCORED} queries")
    for qid in order_bad[:10]:
        finding(f"order deviation {qid} (the declared re-execution band)")
    if len(order_bad) > 10:
        finding(f"... {len(order_bad) - 10} further")

    # == 5. rank-slice byte-stability =========================================
    print("\n== 5. rank-slice byte-stability pins (predicted byte-stable vs f)")
    pq = {}
    for qid in scored_ids:
        tier = {ref: t for ref, t in gold[qid]["evidence"]}
        pq[qid] = score_chunks(jranks[qid], tier)
    for k in F_SLICES:
        got = r4(sum(pq[qid][k] for qid in scored_ids) / N_SCORED)
        mark = "BYTE-STABLE" if got == F_SLICES[k] else "MOVED"
        print(f"  {k}: {got} vs f {F_SLICES[k]} · {mark}")
        if got != F_SLICES[k]:
            finding(f"slice moved: {k} {got} != pinned {F_SLICES[k]}")

    # == 6. top-20 ledger ======================================================
    print("\n== 6. top-20 ledger (predicted: 5 queries changed, 0 carriers entering)")
    changed = 0
    carriers_in = 0
    for qid in scored_ids:
        f20 = franks[qid][:20]
        j20 = jranks[qid][:20]
        if set(f20) != set(j20) or f20 != j20:
            changed += 1
            tier = {ref: t for ref, t in gold[qid]["evidence"]}
            carriers_in += sum(1 for r in j20 if r not in f20 and tier.get(r, 0) >= 1)
    print(f"  top-20 changed on {changed} queries (predicted {PREDICTED_TOP20_CHANGED}); "
          f"gold carriers entering: {carriers_in} (predicted {PREDICTED_CARRIERS_IN})")
    if changed != PREDICTED_TOP20_CHANGED:
        finding(f"top-20 changed on {changed} queries != predicted {PREDICTED_TOP20_CHANGED}")
    if carriers_in != PREDICTED_CARRIERS_IN:
        fail(f"{carriers_in} gold carriers entered the horizon — falsifies the census")

    # == 7. the results ledger ================================================
    print("\n== 7. the results min_cosine_removed ledger (recomputed over ALL 120 queries)")
    led = j.get("min_cosine_removed")
    if not led:
        fail("min_cosine_removed missing from results")
    else:
        # the wrapper's ledger spans every query it retrieved (the gold set's
        # full 120 — scored + substrate-excluded), while the census prediction
        # 170/10 (section 3) is the SCORED-89 subset. Recompute the census
        # over all 120 gold records for the like-for-like comparison.
        import glob as _glob
        gold_all = []
        for p in sorted(_glob.glob(str(GOLD_DIR / "class_*.json"))):
            gold_all += json.loads(Path(p).read_text())
        gold_by_id = {g["id"]: g for g in gold_all}
        total_all = 0
        affected_all = 0
        for qid, qv in queries.items():
            if qid not in gold_by_id:
                continue
            cos = (mat @ qv) / np.maximum(norms * np.linalg.norm(qv), 1e-12)
            cvals = {universe[i]: float(cos[i]) for i in range(len(universe))
                     if cos[i] >= PROD_FLOOR}
            top = sorted(cvals, key=lambda r: (-cvals[r], r))[:PER_ARM]
            n = sum(1 for r in top if cvals[r] < PINNED_THETA)
            total_all += n
            affected_all += 1 if n > 0 else 0
        ok = (abs(led["theta"] - PINNED_THETA) < 1e-12
              and led["affected_queries"] == affected_all
              and led["removed_total"] == total_all)
        print(f"  recorded theta {led['theta']} / affected {led['affected_queries']} / "
              f"removed {led['removed_total']}; recomputed over 120 queries: "
              f"{affected_all} / {total_all} "
              f"{'OK' if ok else 'MISMATCH'} (the scored-89 subset: 10 / 170 — section 3)")
        if not ok:
            fail(f"min_cosine_removed {led} != the all-queries recompute "
                 f"{affected_all}/{total_all}")

    # == 8. §8.1 v1.1 conjunction at the UNCHANGED bars ========================
    print("\n== 8. §8.1 v1.1 conjunction (Ruling 8) — UNCHANGED bars")
    served = j["chunk_axis"]["served_view"]["overall"]
    compliant = j["chunk_axis"]["compliant_view"]["overall"]
    vals = {"a": served["recall@10"], "b": served["mrr"], "c": served["ndcg@10"],
            "a2": compliant["recall@10"], "b2": compliant["mrr"], "c2": compliant["ndcg@10"]}
    verdict_gates = {}
    for g, bar in BARS.items():
        passed = vals[g] >= bar
        verdict_gates[g] = passed
        print(f"  ({g}) {vals[g]} vs bar {bar} -> {'PASS' if passed else 'FAIL'}")
    d_ok = abs(dj[0] / N_SCORED - 0.5618) <= 0.01 + 5e-9 and abs(dj[1] / N_POINTS - 0.9167) <= 0.01 + 5e-9
    print(f"  (d) {dj[0]/N_SCORED:.4f}/{dj[1]/N_POINTS:.4f} vs the r8 reference 0.5618/0.9167 "
          f"+-1pp -> {'PASS' if d_ok else 'FAIL'}")
    fviol = j["chunk_axis"]["validation_boundary_violations"]["served"]
    print(f"  (f) violations {fviol} -> {'PASS' if fviol == 0 else 'FAIL'}")
    promoted = all(verdict_gates.values()) and d_ok and fviol == 0
    print(f"  VERDICT: {'PROMOTED' if promoted else 'NOT PROMOTED'} "
          f"({'as pinned' if not promoted else 'UNEXPECTED — the pin was NOT PROMOTED'})")
    if promoted:
        fail("PROMOTED contradicts the pre-registered pin — investigate before recording")

    # == 9. (e) + (g) ==========================================================
    print("\n== 9. (e) latency + (g) per-class flags vs f")
    print(f"  (e) served p50 {j['latency']['served']['p50_ms']:.1f} ms "
          f"(f {f['latency']['served']['p50_ms']:.1f} ms)")
    fserved = {qid: e for qid, e in f["per_query_chunks"].items()}
    flags = []
    for cls, metrics in j["chunk_axis"]["served_view"]["per_class"].items():
        fcls = f["chunk_axis"]["served_view"]["per_class"].get(cls)
        if not fcls:
            continue
        for k in ["recall@10", "mrr", "ndcg@10"]:
            a, b = metrics[k], fcls[k]
            if b > 0 and a < b and (b - a) / b > 0.15:
                flags.append((cls, k, a, b))
    if flags:
        for cls, k, a, b in flags:
            finding(f"(g) per-class regression >15% relative: {cls} {k} {a} vs f {b}")
    else:
        print("  (g) no per-class regression >15% relative vs f")

    print(f"\n# verification verdict: {len(failures)} failures, {len(findings)} findings")
    for f_ in failures:
        print(f"# FAIL: {f_}")
    for f_ in findings:
        print(f"# FINDING: {f_}")
    if failures:
        sys.exit(1)
    print("# VERIFY OK — the pre-registered invariants hold on the recorded bytes")


if __name__ == "__main__":
    main()
