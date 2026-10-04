#!/usr/bin/env python3
"""run-005-i post-run verification — from recorded bytes only (T-C77).

Verifies the pre-registered invariants (RANK-BOUNDED-KIND-ADMISSION-PREREGISTRATION.md,
records 5c0b6b5, committed BEFORE the run) for the rank-bounded kind-admission lever in
RANK-CAP form (BENCH_NOTES_RANK_CAP=20 on the recorded kind-arm posture
BENCH_NOTES_KIND_ARM=15 at depth 40; one lever — the kind-arm + its bound —
floor/reranker/weights ABSENT; code fa2dddb = merged main):

  1. (d) recompute + self-checks: recompute the section-8(d) aggregates for
     run-005-i from the frozen HV projection x gold x i's recorded ranked_refs;
     must equal i's recorded aggregate AND h's recorded (d) byte-exact (the
     theorem-shaped prediction: a pure served-order permutation of the h pool
     leaves (d) unchanged). Machinery self-check: the same recompute on r8, r9,
     f, g, h must reproduce their recorded aggregates byte-exactly.
  2. SET-preservation — the primary endpoint: per query, i's served pool SET ==
     h's pool SET (expected 89/89; the partition is set-preserving by
     construction) and >= f's pool (superset invariant, expected 89/89, the
     standing findings rule).
  3. the H=20 horizon assertion + the demotion ledger: ZERO kind-arm-only refs
     at fused ranks 1..20 on every query; every two-arm ref precedes every
     kind-arm-only ref in i's served order (the partition definition, checked
     per query); kind-arm-only total expected 797 (min 0 / max 15 per query).
  4. top-20 identity vs f's recorded lists: set-identity expected 87/89 and
     order-identity 86/89 from the grounding simulation; run-identity below
     that = FINDINGS with ledgers (the declared re-execution band; the
     g2-024/g2-086-class diffs are the named tolerance shape).
  5. rank-slice recompute with the byte-stability predictions: recall@5
     0.0616 / recall@10 0.1043 / recall@20 0.1612 / evidence_precision@10
     0.0303 BYTE-EXACT vs the recorded pre-kind-arm values; mrr inside
     [0.0626, 0.07] and nDCG@10 inside [0.1057, 0.1095] (the recorded f<->g
     re-execution band). A recall-slice miss is a FAIL-CLOSED grounding
     failure recorded honestly.
  6. section-8.1 v1.1 gates evaluated fresh under the UNCHANGED bars (Ruling
     8): (a)/(b)/(c)/(b2)/(c2) FAIL expected, (a2) PASS RESTORED expected —
     compliant recall@10 = 0.1043 >= floor 0.0734; NOT PROMOTED is the pinned
     expected verdict (the tranche's question is SEPARABILITY, not promotion).
  7. non-regression: f-full losses 0 (the lever removes nothing); the 5
     f-lost flips stay reverted; g2-061/g2-109 beyond-flip covered points held.
  8. (e) latency (~h's shape; the transform adds one O(n) partition pass) and
     the (g) per-class >15% relative flags vs f (the declared give-back: the
     fresh-note first-relevant credit serves below the horizon).
"""
import gzip
import hashlib
import json
import statistics
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

R8 = "run-005-c-r8"
R9 = "run-005-c-r9"
F1 = "run-005-f-r1"
G1 = "run-005-g-r1"
H1 = "run-005-h-r1"
I1 = "run-005-i-r1"
SELFCHECK_RUNS = [R8, R9, F1, G1, H1]
RECORDED_D = {  # recorded (d) full/micro from the packs — self-check targets
    R8: (0.5618, 0.9167),
    R9: (0.4607, 0.7857),
    F1: (0.5056, 0.8571),
    G1: (0.5169, 0.8690),
}
N_SCORED, N_POINTS = 89, 84  # the recorded chunk-axis denominators (fail-closed)
K_KIND_ARM = 15
H_HORIZON = 20
FRESH_PRED = 797  # the census demotion ledger (kind-arm-only refs)
SLICE_PINS = {"recall@5": 0.0616, "recall@10": 0.1043,
              "recall@20": 0.1612, "evidence_precision@10": 0.0303}
BANDS = {"mrr": (0.0626, 0.07), "ndcg@10": (0.1057, 0.1095)}
GATES_V11 = {  # spec section-8.1 v1.1 bars (T-C40 (2), 2026-10-01)
    "a_recall@10": ("ALL", "recall@10", 0.1920),
    "b_mrr": ("ALL", "mrr", 0.1237),
    "c_ndcg@10": ("ALL", "ndcg@10", 0.2316),
    "a2_validated_recall@10": ("VALIDATED", "recall@10", 0.0734),
    "b2_validated_mrr": ("VALIDATED", "mrr", 0.1184),
    "c2_validated_ndcg@10": ("VALIDATED", "ndcg@10", 0.1683),
}
I_CODE = "fa2dddbdf57af2c1f2906d3bc3cf0876f7970553"

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


def load_kinds():
    return {r["chunk_ref"]: r.get("kind", "?") for r in json.load(gzip.open(SNAP7))}


# ---- BenchMetrics.scoreChunks mirror (byte-exact machinery check) ----------
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
    dcg = sum((2 ** tier_by_ref.get(ranked[n], 0) - 1) / np.log2(n + 2)
              for n in range(min(len(ranked), 10)))
    ideal = sorted((tier_by_ref.get(r, 0) for r in ranked), reverse=True)
    idcg = sum((2 ** ideal[n] - 1) / np.log2(n + 2) for n in range(min(len(ideal), 10)))
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
    kinds = load_kinds()
    runs = {rid: json.loads((RUNS / rid / "results.json").read_text())
            for rid in SELFCHECK_RUNS + [I1]}
    i = runs[I1]

    print("# run-005-i verify — from recorded bytes only (T-C77 RANK-CAP form)")
    print(f"# code {i['code_version']} | run_id {i['run_id']} | date {i['date']}")
    fb = i["fabric"]
    print(f"# posture: providers {fb['providers']} | per_arm_limit {fb['per_arm_limit']} | "
          f"notes_kind_arm {fb['notes_kind_arm']} | notes_rank_cap {fb.get('notes_rank_cap')} | "
          f"notes_floor {fb['notes_floor']} | "
          f"weights {'null' if 'unweighted' in fb['fusion_weights'] else 'NON-NULL'}")
    if fb["providers"] != ["pgvector", "bm25", "notes-kind-arm"]:
        fail(f"providers {fb['providers']} != the five-guard posture")
    if fb["notes_kind_arm"] != K_KIND_ARM or fb["notes_floor"] != 0:
        fail(f"posture mismatch: kind_arm {fb['notes_kind_arm']} floor {fb['notes_floor']}")
    if fb.get("notes_rank_cap") != H_HORIZON:
        fail(f"posture mismatch: notes_rank_cap {fb.get('notes_rank_cap')} != {H_HORIZON}")
    if i["code_version"] != I_CODE:
        fail(f"code_version {i['code_version']} != merged main fa2dddb")
    print(f"# determinism: {i['determinism_check'][:88]}...")
    uf = i.get("notes_rank_cap_underfill", {})
    print(f"# rank-cap under-fill: served {uf.get('served_queries')} / compliant "
          f"{uf.get('compliant_queries')} at H={uf.get('horizon')} (expected 0/0; "
          f"grounding min two-arm prefix 40)")
    if uf.get("served_queries") != 0 or uf.get("compliant_queries") != 0:
        finding(f"rank-cap under-fill {uf} — the H=20 guarantee is conditional; recorded honestly")
    kuf = i.get("notes_kind_arm_underfill", {}).get("underfilled_queries")
    if kuf != 0:
        finding(f"kind-arm under-filled {kuf} queries — recorded honestly")

    scored_sets = [set(r["per_query_chunks"].keys()) for r in runs.values()]
    if len({frozenset(s) for s in scored_sets}) != 1:
        fail("scored sets differ across runs")
    scored_ids = sorted(scored_sets[0])
    if len(scored_ids) != N_SCORED:
        fail(f"scored {len(scored_ids)} != {N_SCORED}")
    pools = {rid: {qid: set(e["ranked_refs"]) for qid, e in run["per_query_chunks"].items()}
             for rid, run in runs.items()}
    ranks = {rid: {qid: list(e["ranked_refs"]) for qid, e in run["per_query_chunks"].items()}
             for rid, run in runs.items()}
    for qid in scored_ids:
        if qid not in gold:
            fail(f"scored query {qid} missing from gold-r9")

    # == 1. (d) recompute self-checks + the byte-exact-vs-h prediction =======
    print("\n== 1. (d) recompute self-checks (recorded vs recomputed from pool bytes)")
    gold_total = sum(len(gold[qid]["points"]) for qid in scored_ids)
    if gold_total != N_POINTS:
        fail(f"gold points across scored {gold_total} != {N_POINTS}")

    def coverage(rid):
        cov = {}
        for qid in scored_ids:
            codes = set()
            for ref in pools[rid][qid]:
                codes |= ref_codes.get(ref, set())
            pts = gold[qid]["points"]
            cov[qid] = {"covered": pts & codes, "full": bool(pts) and pts <= codes}
        return cov

    covs = {}
    for rid in SELFCHECK_RUNS + [I1]:
        c = coverage(rid)
        full = sum(1 for qid in scored_ids if c[qid]["full"])
        micro = sum(len(c[qid]["covered"]) for qid in scored_ids)
        if rid in RECORDED_D:
            rf, rm = RECORDED_D[rid]
            ok = abs(full / N_SCORED - rf) < 5e-5 and abs(micro / N_POINTS - rm) < 5e-5
            tag = "OK" if ok else "MISMATCH"
            print(f"  {rid}: full {full}/{N_SCORED} = {full/N_SCORED:.4f} · "
                  f"micro {micro}/{N_POINTS} = {micro/N_POINTS:.4f} · recorded {rf}/{rm} · {tag}")
            if not ok:
                fail(f"(d) self-check mismatch for {rid}")
        else:
            rec_view = runs[rid]["spec_resolution_hv"]["views"]["served_view_all_denominator"]
            rec_full = rec_view["spec_points_full_coverage_rate"]
            rec_micro = rec_view["spec_points_micro_average"]
            ok = abs(full / N_SCORED - rec_full) < 5e-5 and abs(micro / N_POINTS - rec_micro) < 5e-5
            print(f"  {rid}: full {full}/{N_SCORED} = {full/N_SCORED:.4f} (recorded {rec_full}) · "
                  f"micro {micro}/{N_POINTS} = {micro/N_POINTS:.4f} (recorded {rec_micro}) · "
                  f"{'OK' if ok else 'MISMATCH'}")
            if not ok:
                fail(f"(d) recompute mismatch for {rid}")
        covs[rid] = c
    ifull = sum(1 for q in scored_ids if covs[I1][q]["full"])
    imicro = sum(len(covs[I1][q]["covered"]) for q in scored_ids)
    hfull = sum(1 for q in scored_ids if covs[H1][q]["full"])
    hmicro = sum(len(covs[H1][q]["covered"]) for q in scored_ids)
    print(f"  byte-exact vs h (the theorem-shaped prediction): i {ifull}/{N_SCORED} · "
          f"{imicro}/{N_POINTS} vs h {hfull}/{N_SCORED} · {hmicro}/{N_POINTS} · "
          f"{'IDENTICAL' if (ifull, imicro) == (hfull, hmicro) else 'DIFFERS'}")
    if (ifull, imicro) != (hfull, hmicro):
        fail("(d) is not byte-identical to h — the set-preserving permutation "
             "contract broke (reorder-only leaves (d) unchanged on all recorded runs)")
    print(f"  (d) chain: r8 0.5618/0.9167 -> r9 0.4607/0.7857 -> f 0.5056/0.8571 -> "
          f"g 0.5169/0.8690 -> h 0.5843/0.9405 -> i {ifull/N_SCORED:.4f}/{imicro/N_POINTS:.4f}")

    # == 2. SET-preservation (primary endpoint) + superset ===================
    print("\n== 2. SET-preservation: i pool == h pool per query (primary endpoint)")
    set_diffs = {qid: (pools[I1][qid] - pools[H1][qid], pools[H1][qid] - pools[I1][qid])
                 for qid in scored_ids}
    set_breaches = {q: d for q, d in set_diffs.items() if d[0] or d[1]}
    print(f"  set-identity held: {N_SCORED - len(set_breaches)}/{N_SCORED} queries")
    if set_breaches:
        fail(f"SET-preservation VIOLATIONS on {len(set_breaches)} queries — the partition "
             f"changed the served SET (fail-closed contract); exact ledger follows")
        for qid, (added, dropped) in list(set_breaches.items())[:10]:
            print(f"    {qid}: i-only {sorted(added)[:6]} h-only {sorted(dropped)[:6]}")
    violations = []
    for qid in scored_ids:
        missing = pools[F1][qid] - pools[I1][qid]
        if missing:
            violations.append((qid, sorted(missing)))
    print(f"  superset vs f held: {N_SCORED - len(violations)}/{N_SCORED} queries")
    if violations:
        finding(f"superset vs f VIOLATIONS on {len(violations)} queries — the g2-024 "
                f"HNSW/tie re-execution residual (the standing findings rule); exact ledger:")
        for qid, refs in violations[:10]:
            print(f"    {qid}: f-only refs {refs[:6]}{' …' if len(refs) > 6 else ''}")

    # == 3. the H=20 horizon assertion + the demotion ledger =================
    print("\n== 3. H=20 horizon assertion + demotion ledger (kind-arm-only refs)")
    kind_only = {qid: {r for r in (pools[I1][qid] - pools[F1][qid])
                       if kinds.get(r) == "EXTERNAL_NOTES"} for qid in scored_ids}
    konly_total = sum(len(s) for s in kind_only.values())
    print(f"  kind-arm-only refs (h-era fresh admissions, EXTERNAL_NOTES): {konly_total} "
          f"(predicted {FRESH_PRED})")
    if konly_total != FRESH_PRED:
        fail(f"kind-arm-only total {konly_total} != predicted {FRESH_PRED}")
    in_horizon = [(qid, r) for qid in scored_ids
                  for r in kind_only[qid]
                  if ranks[I1][qid].index(r) < H_HORIZON]
    print(f"  kind-arm-only refs at fused ranks 1..{H_HORIZON}: {len(in_horizon)} "
          f"(asserted 0 on all {N_SCORED} queries)")
    if in_horizon:
        fail(f"H=20 horizon assertion BREACH: {len(in_horizon)} kind-arm-only refs "
             f"inside ranks 1..{H_HORIZON}: {in_horizon[:6]}")
    part_breaches = []
    per_q_counts = {}
    for qid in scored_ids:
        iranks = ranks[I1][qid]
        kpos = [iranks.index(r) for r in kind_only[qid]]
        tpos = [n for n, r in enumerate(iranks) if r not in kind_only[qid]]
        per_q_counts[qid] = len(kind_only[qid])
        if kpos and tpos and max(tpos) > min(kpos):
            part_breaches.append((qid, max(tpos), min(kpos)))
    print(f"  two-arm-before-kind-only order (the partition definition): "
          f"{N_SCORED - len(part_breaches)}/{N_SCORED} queries clean")
    if part_breaches:
        fail(f"partition ORDER breaches on {len(part_breaches)} queries "
             f"(last two-arm rank > first kind-only rank): {part_breaches[:6]}")
    counts = [c for c in per_q_counts.values() if c]
    print(f"  per-query demotions: min {min(per_q_counts.values())} · max "
          f"{max(per_q_counts.values())} (predicted 0/15) · queries carrying >0: {len(counts)}")
    if max(per_q_counts.values()) > K_KIND_ARM:
        fail(f"per-query demotions exceed the kind-arm size K={K_KIND_ARM}")

    # == 4. top-20 identity vs f (the declared re-execution tolerance) =======
    print("\n== 4. top-20 set/order identity vs f's recorded lists")
    t20_set_diff, t20_order_diff = [], []
    for qid in scored_ids:
        f20, i20 = ranks[F1][qid][:20], ranks[I1][qid][:20]
        if set(f20) != set(i20):
            t20_set_diff.append(qid)
        elif f20 != i20:
            t20_order_diff.append(qid)
    set_identity = N_SCORED - len(t20_set_diff)
    order_identity = N_SCORED - len(t20_set_diff) - len(t20_order_diff)
    print(f"  top-20 set-identity {set_identity}/{N_SCORED} (simulation: 87/89) · "
          f"order-identity {order_identity}/{N_SCORED} (simulation: 86/89) · "
          f"exact-order matches {order_identity}")
    for qid in t20_set_diff + t20_order_diff:
        f20, i20 = ranks[F1][qid][:20], ranks[I1][qid][:20]
        only_f = [r for r in f20 if r not in set(i20)]
        only_i = [r for r in i20 if r not in set(f20)]
        print(f"    {qid}: f-only {only_f} i-only {only_i}")
    if set_identity < 87 or order_identity < 86:
        finding(f"top-20 identity BELOW the simulation's 87/89 set + 86/89 order shape: "
                f"set diffs {t20_set_diff} · order-only {t20_order_diff} — the declared "
                f"re-execution band (findings with ledgers, not failures)")
    else:
        print(f"  run identity == the simulation's predicted shape exactly "
              f"(the grounding's three named queries {t20_set_diff + t20_order_diff} — "
              f"the declared re-execution band; confirmation, not a finding)")

    # == 5. rank-slice recompute + byte-stability pins =======================
    print("\n== 5. rank-slice recompute (chunk_axis served view) + pins")
    tiers = {qid: dict(gold[qid]["evidence"]) for qid in scored_ids}
    agg = {rid: defaultdict(float) for rid in (F1, I1)}
    pq = {rid: {} for rid in (F1, I1)}
    for rid in (F1, I1):
        for qid in scored_ids:
            row = score_chunks(ranks[rid][qid], tiers[qid])
            pq[rid][qid] = row
            for k, v in row.items():
                agg[rid][k] += v
    for rid in (F1, I1):
        for k in agg[rid]:
            agg[rid][k] = r4(agg[rid][k] / len(scored_ids))
    rec = {rid: runs[rid]["chunk_axis"]["served_view"]["overall"] for rid in (F1, I1)}
    for k in agg[F1]:
        ok = abs(agg[F1][k] - rec[F1][k]) < 5e-5 and abs(agg[I1][k] - rec[I1][k]) < 5e-5
        print(f"  {k}: f {agg[F1][k]} -> i {agg[I1][k]} · recorded "
              f"{rec[F1][k]} -> {rec[I1][k]} · {'OK' if ok else 'MISMATCH'}")
        if not ok:
            fail(f"rank-slice recompute mismatch for {k}")
    moved = {k: sum(1 for q in scored_ids if abs(pq[I1][q][k] - pq[F1][q][k]) > 1e-12)
             for k in ("recall@5", "recall@10", "recall@20", "mrr", "ndcg@10")}
    print(f"  per-query movement vs f: " + " · ".join(f"{k} moved on {n}" for k, n in moved.items()))
    for k, pin in SLICE_PINS.items():
        ok = abs(rec[I1][k] - pin) < 5e-5
        print(f"  BYTE-STABILITY PIN {k}: recorded {rec[I1][k]} vs pre-kind-arm {pin} · "
              f"{'HELD' if ok else 'MISSED'}")
        if not ok:
            fail(f"recall-slice byte-stability pin MISSED for {k}: {rec[I1][k]} vs {pin} "
                 f"(fail-closed grounding failure per the prereg)")
    for k, (lo, hi) in BANDS.items():
        ok = lo - 5e-5 <= rec[I1][k] <= hi + 5e-5
        print(f"  BAND {k}: recorded {rec[I1][k]} inside [{lo}, {hi}] · "
              f"{'HELD' if ok else 'OUT'}")
        if not ok:
            fail(f"band check MISSED for {k}: {rec[I1][k]} outside [{lo}, {hi}]")

    # == 6. section-8.1 v1.1 gates + (a2) restoration ========================
    print("\n== 6. section-8.1 v1.1 gates (evaluated fresh, both views; UNCHANGED bars)")
    for name, (view, metric, floor) in GATES_V11.items():
        src = (i["chunk_axis"]["served_view"]["overall"] if view == "ALL"
               else i["chunk_axis"]["compliant_view"]["overall"])
        val = src[metric]
        ok = val >= floor
        print(f"  gate {name}: {val} vs {floor} -> {'PASS' if ok else 'FAIL'}")
    a2 = i["chunk_axis"]["compliant_view"]["overall"]["recall@10"]
    print(f"  (a2) restoration: compliant recall@10 {a2} vs floor 0.0734 -> "
          f"{'PASS RESTORED (h failed it at 0.0612)' if a2 >= 0.0734 else 'STILL FAILING'}")
    if a2 < 0.0734:
        fail(f"(a2) gate-level prediction falsified: {a2} < 0.0734")
    i_compliant = i["spec_resolution_hv"]["views"]["compliant_view"]
    i_served = i["spec_resolution_hv"]["views"]["served_view_all_denominator"]
    same = (i_compliant["spec_points_full_coverage_rate"]
            == i_served["spec_points_full_coverage_rate"]
            and i_compliant["spec_points_micro_average"] == i_served["spec_points_micro_average"])
    print(f"  compliant-vs-served (d): identical = {same} (the §2 prediction: the "
          f"compliant pool equals the served pool — the recorded subject-level-branch shape)")
    if not same:
        finding("compliant view differs from served — recorded honestly")
    verdict = i["s8_gate"].get("verdict", i["s8_gate"].get("promotion_verdict"))
    print(f"  s8 verdict: {verdict} (NOT PROMOTED is the pinned expected outcome)")

    # == 7. non-regression watch =============================================
    print("\n== 7. non-regression watch")
    f_full_losses = [q for q in scored_ids if covs[F1][q]["full"] and not covs[I1][q]["full"]]
    print(f"  f-full losses: {len(f_full_losses)}"
          + (f" {f_full_losses}" if f_full_losses else " (zero — the lever removes nothing)"))
    if f_full_losses:
        fail(f"f-full queries lost in i: {f_full_losses}")
    lost = sorted(q for q in scored_ids if covs[R8][q]["full"] and not covs[F1][q]["full"])
    reverted = [q for q in lost if covs[I1][q]["full"]]
    print(f"  f-lost flips {lost}: reverted in i {len(reverted)}/{len(lost)}")
    if len(reverted) != len(lost):
        fail(f"flips lost in i: {[q for q in lost if q not in reverted]}")
    for qid in ("g2-061", "g2-109"):
        if qid in scored_ids:
            fp61, ip61 = len(covs[F1][qid]["covered"]), len(covs[I1][qid]["covered"])
            hp61 = len(covs[H1][qid]["covered"])
            print(f"  {qid} covered points: f {fp61} -> h {hp61} -> i {ip61} "
                  f"{'(held)' if ip61 >= fp61 else '(DROP — finding)'}")
            if ip61 < fp61:
                fail(f"{qid} covered points dropped vs f: {fp61} -> {ip61}")

    # == 8. (e) latency + per-class flags ====================================
    print("\n== 8. (e) latency + (g) per-class flags")
    lat_i = i["latency"]["served"]
    lat_h = runs[H1]["latency"]["served"]
    print(f"  latency p50: h {lat_h['p50_ms']:.1f} ms -> i {lat_i['p50_ms']:.1f} ms "
          f"(expected ~= h's shape; the transform adds one O(n) partition pass per query "
          f"per view — the memo keeps the kind-arm read O(1))")
    for cls, vals in sorted(i["chunk_axis"]["served_view"]["per_class"].items()):
        fvals = runs[F1]["chunk_axis"]["served_view"]["per_class"].get(cls, {})
        for m in ("recall@20", "mrr", "ndcg@10"):
            fv, iv = fvals.get(m), vals.get(m)
            if fv and iv and fv > 0 and abs(iv - fv) / fv > 0.15:
                print(f"  [g-flag] {cls} {m}: f {fv} -> i {iv} ({(iv-fv)/fv*100:+.1f}%)")

    print("\n== FINDINGS ==")
    if findings:
        for f_ in findings:
            print(f"  FINDING: {f_.split('FINDING: ', 1)[-1]}")
    else:
        print("  none")
    print("== FAILURES ==")
    if failures:
        for f_ in failures:
            print(f"  FAIL: {f_}")
        sys.exit(1)
    print("  none — all pre-registered checks recorded above")


if __name__ == "__main__":
    main()
