#!/usr/bin/env python3
"""run-005-g post-run verification — from recorded bytes only (T-C69).

Verifies the pre-registered invariants (POOL-COMPOSITION-PREREGISTRATION.md,
records ee3e019, committed BEFORE the run) for the per-kind quota lever in
FLOOR form (BENCH_NOTES_FLOOR=5 at the recorded depth-40 posture; one lever,
reranker/weights ABSENT):

  1. superset invariant (per query): run-005-g's served pool SET
     >= run-005-f's pool SET. Expected 89/89 (the floor is pure-additive;
     the g2-024 HNSW/tie re-execution risk is the declared residual).
     Violations are recorded as FINDINGS with their exact ledger, and (d)
     monotonicity is then claimed only over the held subset.
  2. (d) recompute + monotonicity + ceiling: recompute the section-8(d)
     aggregates for run-005-g from the frozen HV projection x gold x g's
     recorded ranked_refs; must equal g's recorded aggregate, be monotone
     non-decreasing vs f's recorded (0.5056 / 0.8571), and not exceed the
     r8 ceiling (0.5618 / 0.9167 — the pre-registered exact-reversion
     ceiling). Machinery self-check: the same recompute on r8, r9 and f
     must reproduce their recorded aggregates byte-exactly.
  3. per-flip admission ledger (mechanically derived, no hand-maintained
     lists): for every f-lost flip (r8-full -> f-not-full) the pack records
     ADMITTED+REVERTED (a census covering ref enters g's union via the
     floor and the query reverts to full), ADMITTED+PARTIAL (covering ref
     enters; other points still missing), or MISS-AT-FLOOR (no census
     covering ref in g's union — the recorded signal that the carrier's
     arm rank exceeds the floor's reach; the next lever is
     arm-composition / MIN_COSINE, NOT a bigger floor). Non-regression
     watch: every f-full query must stay full in g (the floor removes
     nothing) and g2-061's covered-point count must not drop.
  4. per-query covered-point monotonicity on the superset-held subset:
     covered gold points(g) >= covered gold points(f) per query.
  5. notes-share ledger: per-query EXTERNAL_NOTES share of the union pools
     across r9 -> f -> g (the prereg's 20.4% -> 15.3% -> g reading).
Plus the movement/accounting ledgers for the authored report:
  what the floor admitted (refs, kinds, g-rank bands), (a)-(c) deltas vs f
  with the recall@20 pin statement, the section-8.1 v1.1 gate rows, and the
  (g) per-class >15% relative flags both directions.
"""
import gzip
import json
import statistics
from collections import defaultdict
from pathlib import Path

RECORDS = Path(__file__).resolve().parents[4]
RUNS = RECORDS / "evidence/bench-001/runs"
PROJECTION = RECORDS / "bench/evidence/chunk-sp-substrate-2026-09-27/chunk_spec_hv_projection.json"
GOLD_DIR = RECORDS / "bench/inputs/gold-r9"
SNAP7 = RECORDS / "bench/inputs/snapshot-r9/chunks.jsonl.gz"

R8 = "run-005-c-r8"
R9 = "run-005-c-r9"
F1 = "run-005-f-r1"
G1 = "run-005-g-r1"


def r4(v):
    return round(v * 10000.0) / 10000.0


def load_projection():
    art = json.loads(PROJECTION.read_text())
    ref_codes = defaultdict(set)
    for row in art["rows"]:
        if row["provenance"]["validation_status"] != "HUMAN_VALIDATED":
            raise SystemExit(f"FAIL-CLOSED: non-HV row {row['mapping_id']}")
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
            }
    return gold


def load_run(run_id):
    return json.loads((RUNS / run_id / "results.json").read_text())


def load_kinds():
    recs = json.load(gzip.open(SNAP7))
    return {r["chunk_ref"]: r.get("kind", "?") for r in recs}


def score_d(run, gold, ref_codes):
    """Mechanical section-8(d) per the frozen counting rule (HV projection only)."""
    rows = {}
    for qid, entry in run["per_query_chunks"].items():
        points = gold[qid]["points"]
        covered = set()
        for ref in entry["ranked_refs"]:
            covered.update(ref_codes.get(ref, ()))
        hits = points & covered
        rows[qid] = {
            "full": bool(points) and hits == points,
            "n": len(hits),
            "gold_n": len(points),
            "covered_pts": hits,
        }
    full = sum(1 for r in rows.values() if r["full"])
    gold_total = sum(r["gold_n"] for r in rows.values())
    cov_total = sum(r["n"] for r in rows.values())
    return {
        "full_rate": r4(full / len(rows)),
        "micro": r4(cov_total / gold_total),
        "full_n": full,
        "queries": len(rows),
        "gold_total": gold_total,
        "cov_total": cov_total,
        "rows": rows,
    }


def recorded_d(run):
    v = run["spec_resolution_hv"]["views"]["served_view_all_denominator"]
    return r4(v["spec_points_full_coverage_rate"]), r4(v["spec_points_micro_average"])


def overall(run):
    return run["chunk_axis"]["served_view"]["overall"]


def per_class(run):
    return run["chunk_axis"]["served_view"]["per_class"]


def main():
    r8, r9, f1, g1 = load_run(R8), load_run(R9), load_run(F1), load_run(G1)
    ref_codes = load_projection()
    gold = load_gold()
    kinds = load_kinds()

    failures = []
    findings = []

    # -- 0. manifest posture -------------------------------------------------
    print("== 0. manifest posture")
    fab = r9["fabric"]["per_arm_limit"]
    fal = f1["fabric"]["per_arm_limit"]
    gal = g1["fabric"]["per_arm_limit"]
    gfl = g1["fabric"].get("notes_floor")
    print(f"  r9 per_arm_limit={fab}  f per_arm_limit={fal}  g per_arm_limit={gal}")
    print(f"  g notes_floor: {gfl}   g fusion_weights: {g1['fabric']['fusion_weights']}")
    print(f"  g determinism: {g1['determinism_check'][:60]}...")
    print(f"  g code_version: {g1['code_version']}")
    if gal != 40:
        failures.append(f"per_arm_limit expected 40, got {gal}")
    if gfl != 5:
        failures.append(f"notes_floor expected 5, got {gfl}")
    if "unweighted" not in g1["fabric"]["fusion_weights"]:
        failures.append("fusion_weights not unweighted — one-lever guard broken")
    if "reranker" in g1["fabric"].get("reranker", ""):
        failures.append("reranker active — one-lever guard broken")

    # -- 1. superset invariant ------------------------------------------------
    print("== 1. superset invariant (per query, g-pool SET >= f-pool SET)")
    held, violated = [], []
    for qid, ef in f1["per_query_chunks"].items():
        sf = set(ef["ranked_refs"])
        sg = set(g1["per_query_chunks"][qid]["ranked_refs"])
        if sf <= sg:
            held.append(qid)
        else:
            violated.append((qid, sorted(sf - sg)))
    print(f"  held: {len(held)}/{len(held) + len(violated)}")
    if violated:
        findings.append(f"SUPERSET VIOLATIONS: {len(violated)} queries "
                        "(HNSW/tie re-execution risk fired)")
        for qid, missing in violated:
            print(f"  VIOLATION {qid}: refs in f-pool missing from g-pool: {missing}")
    else:
        print("  per-query superset HOLDS 89/89 (pure-additive admission; the "
              "re-execution risk did not fire)")

    # -- 2. (d) recompute + monotonicity + ceiling -----------------------------
    print("== 2. (d) recompute from frozen bytes + monotonicity + r8 ceiling")
    comp8 = score_d(r8, gold, ref_codes)
    comp9 = score_d(r9, gold, ref_codes)
    compF = score_d(f1, gold, ref_codes)
    compG = score_d(g1, gold, ref_codes)
    rec8, rec9, recF, recG = (recorded_d(r8), recorded_d(r9),
                              recorded_d(f1), recorded_d(g1))
    print(f"  r8 recorded {rec8[0]}/{rec8[1]}  recomputed {comp8['full_rate']}/{comp8['micro']}"
          f"  self-check {'OK' if rec8 == (comp8['full_rate'], comp8['micro']) else 'MISMATCH'}")
    print(f"  r9 recorded {rec9[0]}/{rec9[1]}  recomputed {comp9['full_rate']}/{comp9['micro']}"
          f"  self-check {'OK' if rec9 == (comp9['full_rate'], comp9['micro']) else 'MISMATCH'}")
    print(f"  f  recorded {recF[0]}/{recF[1]}  recomputed {compF['full_rate']}/{compF['micro']}"
          f"  self-check {'OK' if recF == (compF['full_rate'], compF['micro']) else 'MISMATCH'}")
    print(f"  g  recorded {recG[0]}/{recG[1]}  recomputed {compG['full_rate']}/{compG['micro']}"
          f"  ({compG['full_n']}/{compG['queries']} full, "
          f"{compG['cov_total']}/{compG['gold_total']} points)")
    if recG != (compG["full_rate"], compG["micro"]):
        failures.append("g (d) recompute != recorded aggregate")
    if rec9 != (comp9["full_rate"], comp9["micro"]) or rec8 != (comp8["full_rate"], comp8["micro"]) \
            or recF != (compF["full_rate"], compF["micro"]):
        failures.append("verify machinery self-check failed on r8/r9/f")
    mono = recG[0] >= recF[0] and recG[1] >= recF[1]
    print(f"  monotonicity vs f: {recF[0]}->{recG[0]} / {recF[1]}->{recG[1]}  "
          f"{'HOLDS (conditional theorem: premise 89/89 => unconditional)' if mono and not violated else ('HOLDS' if mono else 'VIOLATED')}")
    if not mono:
        failures.append("(d) monotonicity violated")
    ceil_ok = recG[0] <= rec8[0] + 1e-9 and recG[1] <= rec8[1] + 1e-9
    print(f"  r8 ceiling {rec8[0]}/{rec8[1]}: g {'below ceiling (partial recovery)' if ceil_ok else 'EXCEEDS ceiling'}")
    d_full_delta = round((recG[0] - recF[0]) * 10000) / 100
    d_micro_delta = round((recG[1] - recF[1]) * 10000) / 100
    print(f"  recovery vs f: full +{d_full_delta}pp, micro +{d_micro_delta}pp "
          f"(ceiling: exact r8 reversion {rec8[0]}/{rec8[1]})")

    # -- 3. per-flip admission ledger (mechanically derived) --------------------
    print("== 3. per-flip admission ledger (r8 vs f vs g, derived from bytes)")
    lostF, gainedF = [], []
    for qid in compF["rows"]:
        f8, fF = comp8["rows"][qid]["full"], compF["rows"][qid]["full"]
        if f8 and not fF:
            lostF.append(qid)
        if (not f8) and fF:
            gainedF.append(qid)
    print(f"  f-lost flips (r8-full -> f-not-full): {len(lostF)} {sorted(lostF)}")
    print(f"  f-gained flips (r8-not-full -> f-full): {len(gainedF)} {sorted(gainedF)}")
    reverted = partial = missed = 0
    for qid in sorted(lostF):
        pts = gold[qid]["points"]
        covF, covG = compF["rows"][qid]["covered_pts"], compG["rows"][qid]["covered_pts"]
        sf = set(f1["per_query_chunks"][qid]["ranked_refs"])
        sg = set(g1["per_query_chunks"][qid]["ranked_refs"])
        admitted = sorted(sg - sf)
        reentered = [r for r in admitted if ref_codes.get(r, set()) & (pts - covF)]
        fullG = compG["rows"][qid]["full"]
        if fullG:
            status, reverted = "ADMITTED+REVERTED (full 0->1)", reverted + 1
        elif reentered:
            status, partial = "ADMITTED+PARTIAL", partial + 1
        else:
            status, missed = "MISS-AT-FLOOR", missed + 1
        kk = sorted({kinds.get(r, "?") for r in reentered})
        print(f"  {qid}: {status}  covered {len(covF)}/{len(pts)} -> {len(covG)}/{len(pts)}"
              f"  admitted {len(admitted)} refs"
              + (f"; covering carriers admitted: {len(reentered)} {kk}" if reentered else ""))
    print(f"  ledger totals of {len(lostF)} f-lost flips: admitted+reverted {reverted} / "
          f"admitted+partial {partial} / miss-at-floor {missed}")
    if missed:
        findings.append(f"{missed} flips MISS-AT-FLOOR — the carriers' arm ranks exceed "
                        "the floor's reach; next lever is arm-composition / MIN_COSINE "
                        "(own dated pre-registration), NOT a bigger floor")

    # non-regression: the floor removes nothing
    print("== 3b. non-regression watch")
    drops_full = [q for q in compF["rows"] if compF["rows"][q]["full"]
                  and not compG["rows"][q]["full"]]
    print(f"  f-full queries that lost full coverage in g: {len(drops_full)}")
    if drops_full:
        failures.append(f"floor REMOVED coverage: {sorted(drops_full)}")
    if "g2-061" in compF["rows"]:
        nF, nG = compF["rows"]["g2-061"]["n"], compG["rows"]["g2-061"]["n"]
        print(f"  g2-061 covered points: f {nF} -> g {nG} "
              f"({'non-regression OK' if nG >= nF else 'DROP — finding'})")
        if nG < nF:
            findings.append("g2-061 covered-point count dropped under the floor")

    # -- 4. per-query point monotonicity on the held subset ---------------------
    print("== 4. per-query covered-point monotonicity (superset-held subset)")
    drops = []
    for qid in held:
        nf, ng = compF["rows"][qid]["n"], compG["rows"][qid]["n"]
        if ng < nf:
            drops.append((qid, nf, ng))
    print(f"  point-drops on held subset: {len(drops)}" + (f" {drops}" if drops else ""))
    if drops:
        failures.append(f"per-query point monotonicity violated on {len(drops)} queries")

    # -- 5. notes-share ledger ---------------------------------------------------
    print("== 5. notes-share ledger (EXTERNAL_NOTES share of the union pools)")
    shares = {}
    for name, run in (("r9", r9), ("f", f1), ("g", g1)):
        tot = notes = 0
        for qid, e in run["per_query_chunks"].items():
            for ref in e["ranked_refs"]:
                tot += 1
                if kinds.get(ref, "?") == "EXTERNAL_NOTES":
                    notes += 1
        shares[name] = (notes, tot, r4(notes / tot))
        print(f"  {name}: {notes}/{tot} = {shares[name][2]} ({100 * notes / tot:.1f}%)")
    print(f"  reading: r9 {shares['r9'][2]} -> f {shares['f'][2]} -> g {shares['g'][2]} "
          "(the floor re-admits notes; the share recovers only partially)")

    # -- 6. what the floor admitted ----------------------------------------------
    print("== 6. what the floor admitted (refs in g-pool beyond f-pool)")
    added_by_kind = defaultdict(int)
    added_by_band = defaultdict(int)
    admitted_per_query = []
    for qid, ef in f1["per_query_chunks"].items():
        sf = set(ef["ranked_refs"])
        refsG = g1["per_query_chunks"][qid]["ranked_refs"]
        n_new = 0
        for i, ref in enumerate(refsG):
            if ref not in sf:
                n_new += 1
                added_by_kind[kinds.get(ref, "?")] += 1
                added_by_band["1-10" if i < 10 else "11-20" if i < 20 else
                              "21-40" if i < 40 else "41+"] += 1
        admitted_per_query.append(n_new)
    print(f"  admitted refs total: {sum(admitted_per_query)} over "
          f"{sum(1 for n in admitted_per_query if n)} queries "
          f"(mean {statistics.mean(admitted_per_query):.2f}, max {max(admitted_per_query)})")
    print(f"  by kind: {dict(sorted(added_by_kind.items()))}")
    print(f"  by g-rank band: {dict(sorted(added_by_band.items()))}")

    # -- 7. (a)-(c) deltas vs f + the recall@20 pin ------------------------------
    print("== 7. (a)-(c) served-view deltas vs f")
    oF, oG = overall(f1), overall(g1)
    pin_note = []
    for m in ["recall@5", "recall@10", "recall@20", "mrr", "ndcg@10",
              "evidence_precision@10", "false_positive_rate@10"]:
        b, n = oF[m], oG[m]
        rel = (n - b) / b if b else None
        flag = ""
        if rel is not None and rel < -0.15:
            flag = "   REG>15%"
        print(f"  {m}: {b} -> {n}" + (f" ({rel * 100:+.1f}%){flag}" if rel is not None else ""))
        if m == "recall@20":
            pin_note.append(f"recall@20 pin (4-run hold at {b}) "
                            f"{'HELD' if b == n else 'BROKEN -> recorded finding'} "
                            f"({b} -> {n})")
    for s in pin_note:
        print(f"  PIN: {s}")
    gat = g1["s8_gate"]
    for k in ["a_recall@10", "b_mrr", "c_ndcg@10", "a2_validated_recall@10",
              "b2_validated_mrr", "c2_validated_ndcg@10"]:
        row = gat[k]
        print(f"  gate {k}: {row['value']} vs {row['floor']} -> {'PASS' if row['pass'] else 'FAIL'}")
    print(f"  g boundary: {gat['f_boundary']}")
    print(f"  latency: f p50 {f1['latency']['served']['p50_ms']:.1f} ms -> g p50 "
          f"{g1['latency']['served']['p50_ms']:.1f} ms (the probe-doubling cost, "
          "retrieval-only, recorded)")

    # -- 8. (g) per-class >15% both directions -----------------------------------
    print("== 8. (g) per-class deltas vs f (flag >15% relative, both directions)")
    pF, pG = per_class(f1), per_class(g1)
    reg_flags = []
    for cls in sorted(pF):
        for m in ["recall@5", "recall@10", "recall@20", "mrr", "ndcg@10"]:
            bv, nv = float(pF[cls][m]), float(pG[cls][m])
            if bv == 0 and nv == 0:
                continue
            rel = (nv - bv) / bv if bv else None
            if rel is not None and abs(rel) > 0.15:
                direction = "RECOVERY" if rel > 0 else "REGRESSION"
                reg_flags.append((cls, m, bv, nv, rel, direction))
    if reg_flags:
        for cls, m, bv, nv, rel, d in reg_flags:
            print(f"  {cls} {m}: {bv} -> {nv} ({rel * 100:+.1f}%)  [{d}]")
    else:
        print("  no per-class movement beyond 15% relative on any axis")

    # -- close-out ---------------------------------------------------------------
    print("== FINDINGS ==")
    if findings:
        for f in findings:
            print("  FINDING:", f)
    else:
        print("  none")
    print("== FAILURES ==")
    if failures:
        for f in failures:
            print("  FAILURE:", f)
        raise SystemExit(1)
    print("  none — all pre-registered checks recorded above")


if __name__ == "__main__":
    main()
