#!/usr/bin/env python3
"""run-005-f post-run verification — from recorded bytes only (T-C67).

Verifies the pre-registered invariants (POOL-RECOVERY-PREREGISTRATION.md,
records d34e038, committed BEFORE the run) for the per-arm depth lever
(BENCH_PER_ARM_LIMIT 20 -> 40, one lever, reranker/weights ABSENT):

  1. superset invariant (per query): run-005-f's served pool SET
     >= run-005-c-r9's pool SET. Expected 89/89. Violations are recorded as
     FINDINGS (per-arm prefix instability under LIMIT growth: HNSW
     approximation + ORDER BY tie nondeterminism) with their exact ledger,
     and (d) monotonicity is then claimed only over the held subset.
  2. (d) recompute + monotonicity: recompute §8(d) for run-005-f from the
     frozen HV projection x gold-v5 x f's recorded ranked_refs; must equal
     f's recorded aggregate (0.5056 / 0.8571), be monotone non-decreasing
     vs r9's recorded (0.4607 / 0.7857), and not exceed the r8 baseline
     ceiling (0.5618 / 0.9167). Machinery self-check: the same recompute on
     r9 and r8 must reproduce their recorded aggregates byte-exactly.
  3. per-flip recovery ledger: the flipped queries are derived MECHANICALLY
     by comparing r8 vs r9 recorded per-query full-coverage booleans (no
     hand-maintained list). For each r9-lost flip the pack records:
     carrier re-entry (covering ref absent from r9's pool, present in f's),
     flip reversion (full 0 -> 1 in f), or miss (carrier still out-of-pool
     at depth 40 — the recorded signal that a pool-COMPOSITION lever, not
     depth, is required). The partial-loss query (g2-061 per the prereg) is
     cross-checked mechanically (r9 covered-points < r8 covered-points).
  4. per-query point-monotonicity on the superset-held subset:
     covered gold points(f) >= covered gold points(r9) per query.
Plus the movement/accounting ledgers for the authored report:
  (a)-(c) deltas vs r9 with the recall@20 pin statement, (g) per-class
  >15% relative flags both directions, and the deep-rank composition of
  what depth 40 added (kinds, by rank band).
"""
import gzip
import json
from collections import defaultdict
from pathlib import Path

RECORDS = Path("/home/z/my-project/audit/syllabai")
RUNS = RECORDS / "evidence/bench-001/runs"
PROJECTION = RECORDS / "bench/evidence/chunk-sp-substrate-2026-09-27/chunk_spec_hv_projection.json"
GOLD_DIR = RECORDS / "bench/gold-v5"
SNAP7 = RECORDS / "bench/inputs/snapshot-r9/chunks.jsonl.gz"

R8 = "run-005-c-r8"
R9 = "run-005-c-r9"
F1 = "run-005-f-r1"


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
    """Mechanical §8(d) per the frozen counting rule (HV projection only)."""
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
    r8, r9, f1 = load_run(R8), load_run(R9), load_run(F1)
    ref_codes = load_projection()
    gold = load_gold()
    kinds = load_kinds()

    failures = []
    findings = []

    # -- 0. manifest posture -------------------------------------------------
    fab = r9["fabric"]["per_arm_limit"]
    fal = f1["fabric"]["per_arm_limit"]
    fw = f1["fabric"]["fusion_weights"]
    print("== 0. manifest posture")
    print(f"  r9 per_arm_limit={fab}  f per_arm_limit={fal}")
    print(f"  f fusion_weights: {fw}")
    print(f"  f determinism: {f1['determinism_check'][:60]}...")
    if fal != 40:
        failures.append(f"per_arm_limit expected 40, got {fal}")
    if "unweighted" not in fw:
        failures.append(f"fusion_weights not unweighted: {fw}")
    if r9["fabric"].get("fusion_weights") != fw:
        findings.append("r9 vs f fusion_weights text differs (both must be unweighted)")

    # -- 1. superset invariant ------------------------------------------------
    print("== 1. superset invariant (per query, f-pool SET >= r9-pool SET)")
    held, violated = [], []
    for qid, e9 in r9["per_query_chunks"].items():
        s9 = set(e9["ranked_refs"])
        sf = set(f1["per_query_chunks"][qid]["ranked_refs"])
        if s9 <= sf:
            held.append(qid)
        else:
            violated.append((qid, sorted(s9 - sf)))
    print(f"  held: {len(held)}/{len(held) + len(violated)}")
    if violated:
        findings.append(f"SUPERSET VIOLATIONS: {len(violated)} queries")
        for qid, missing in violated:
            print(f"  VIOLATION {qid}: refs in r9-pool missing from f-pool: {missing}")
    else:
        print("  per-query superset HOLDS 89/89 (prefix-stability risks did not fire)")

    # -- 2. (d) recompute + monotonicity --------------------------------------
    print("== 2. (d) recompute from frozen bytes + monotonicity")
    comp8 = score_d(r8, gold, ref_codes)
    comp9 = score_d(r9, gold, ref_codes)
    compF = score_d(f1, gold, ref_codes)
    rec8, rec9, recF = recorded_d(r8), recorded_d(r9), recorded_d(f1)
    print(f"  r8 recorded {rec8[0]}/{rec8[1]}  recomputed {comp8['full_rate']}/{comp8['micro']}"
          f"  self-check {'OK' if rec8 == (comp8['full_rate'], comp8['micro']) else 'MISMATCH'}")
    print(f"  r9 recorded {rec9[0]}/{rec9[1]}  recomputed {comp9['full_rate']}/{comp9['micro']}"
          f"  self-check {'OK' if rec9 == (comp9['full_rate'], comp9['micro']) else 'MISMATCH'}")
    print(f"  f  recorded {recF[0]}/{recF[1]}  recomputed {compF['full_rate']}/{compF['micro']}"
          f"  ({compF['full_n']}/{compF['queries']} full, "
          f"{compF['cov_total']}/{compF['gold_total']} points)")
    if recF != (compF["full_rate"], compF["micro"]):
        failures.append("f (d) recompute != recorded aggregate")
    if rec9 != (comp9["full_rate"], comp9["micro"]) or rec8 != (comp8["full_rate"], comp8["micro"]):
        failures.append("verify machinery self-check failed on r8/r9")
    mono = recF[0] >= rec9[0] and recF[1] >= rec9[1]
    print(f"  monotonicity vs r9: {rec9[0]}->{recF[0]} / {rec9[1]}->{recF[1]}  "
          f"{'HOLDS' if mono else 'VIOLATED'}")
    if not mono:
        failures.append("(d) monotonicity violated")
    ceil_ok = recF[0] <= rec8[0] + 1e-9 and recF[1] <= rec8[1] + 1e-9
    print(f"  r8 ceiling {rec8[0]}/{rec8[1]}: f {'below ceiling (partial recovery)' if ceil_ok else 'EXCEEDS ceiling'}")
    d_full_delta = round((recF[0] - rec9[0]) * 10000) / 100
    d_micro_delta = round((recF[1] - rec9[1]) * 10000) / 100
    print(f"  recovery: full +{d_full_delta}pp, micro +{d_micro_delta}pp "
          f"(vs r8-fully-reverted ceiling: full {rec8[0]}, micro {rec8[1]})")

    # -- 3. per-flip recovery ledger (mechanically derived) --------------------
    print("== 3. per-flip recovery ledger (r8 vs r9 vs f, derived from bytes)")
    lost, gained = [], []
    for qid in comp9["rows"]:
        f8, f9 = comp8["rows"][qid]["full"], comp9["rows"][qid]["full"]
        if f8 and not f9:
            lost.append(qid)
        if (not f8) and f9:
            gained.append(qid)
    print(f"  mechanically derived r9-lost flips: {len(lost)} {sorted(lost)}")
    print(f"  mechanically derived r9-gained flips: {len(gained)} {sorted(gained)}")
    reverted = carrier_reentry = missed = 0
    for qid in sorted(lost):
        pts = gold[qid]["points"]
        cov9, covF = comp9["rows"][qid]["covered_pts"], compF["rows"][qid]["covered_pts"]
        s9 = set(r9["per_query_chunks"][qid]["ranked_refs"])
        sf = set(f1["per_query_chunks"][qid]["ranked_refs"])
        # refs whose projection codes cover any still/again-missing gold point
        newly_covering = sorted(sf - s9)
        reentered = []
        for ref in newly_covering:
            if ref_codes.get(ref, set()) & (pts - cov9):
                reentered.append(ref)
        fullF = compF["rows"][qid]["full"]
        status = "REVERTED (full 0->1)" if fullF else (
            "PARTIAL-RECOVERED" if len(covF) > len(cov9) else "MISS")
        if fullF:
            reverted += 1
        elif reentered:
            carrier_reentry += 1
        else:
            missed += 1
        kk = [kinds.get(r, "?") for r in reentered]
        print(f"  {qid}: {status}  covered {len(cov9)}/{len(pts)} -> {len(covF)}/{len(pts)}"
              + (f"  re-entered carriers: {len(reentered)} {sorted(set(kk))}" if reentered else ""))
    print(f"  ledger totals: reverted {reverted} / carrier-reentry-partial {carrier_reentry}"
          f" / miss {missed} (of {len(lost)} lost flips)")
    if missed:
        findings.append(f"{missed} flips STILL MISSED at depth 40 — pool-COMPOSITION lever "
                        "is the recorded next family, not more depth")

    # partial-loss cross-check (prereg names g2-061)
    partial_drops = []
    for qid in comp9["rows"]:
        if not comp8["rows"][qid]["full"] and not comp9["rows"][qid]["full"]:
            n8, n9 = comp8["rows"][qid]["n"], comp9["rows"][qid]["n"]
            if n9 < n8:
                partial_drops.append((qid, n8, n9, compF["rows"][qid]["n"]))
    print(f"  partial-loss queries (r9 < r8 covered points, neither full): {partial_drops}")
    for qid, n8, n9, nf in partial_drops:
        if qid == "g2-061":
            tag = "matches the prereg's named partial-loss query" if nf >= n9 else \
                  "prereg-named g2-061 NOT recovered in f"
            print(f"  g2-061: r8 {n8} -> r9 {n9} -> f {nf} — {tag}")
            if nf < n9:
                findings.append("g2-061 partial loss NOT recovered by depth")

    # -- 4. per-query point monotonicity on the held subset ---------------------
    print("== 4. per-query covered-point monotonicity (superset-held subset)")
    drops = []
    for qid in held:
        n9, nf = comp9["rows"][qid]["n"], compF["rows"][qid]["n"]
        if nf < n9:
            drops.append((qid, n9, nf))
    print(f"  point-drops on held subset: {len(drops)}" + (f" {drops}" if drops else ""))
    if drops:
        failures.append(f"per-query point monotonicity violated on {len(drops)} queries")

    # -- 5. (a)-(c) deltas + the recall@20 pin ---------------------------------
    print("== 5. (a)-(c) served-view deltas vs r9")
    o9, oF = overall(r9), overall(f1)
    pin_note = []
    for m in ["recall@5", "recall@10", "recall@20", "mrr", "ndcg@10",
              "evidence_precision@10", "false_positive_rate@10"]:
        b, n = o9[m], oF[m]
        rel = (n - b) / b if b else None
        flag = ""
        if rel is not None and rel < -0.15:
            flag = "   REG>15%"
        print(f"  {m}: {b} -> {n}" + (f" ({rel * 100:+.1f}%){flag}" if rel is not None else ""))
        if m == "recall@20":
            pin_note.append(f"recall@20 pin {'HELD' if b == n else 'BROKEN'} "
                            f"({b} -> {n}) — prereg declared a break a finding, not failure")
    for s in pin_note:
        print(f"  PIN: {s}")
    g = f1["s8_gate"]
    for k in ["a_recall@10", "b_mrr", "c_ndcg@10", "a2_validated_recall@10",
              "b2_validated_mrr", "c2_validated_ndcg@10"]:
        row = g[k]
        print(f"  gate {k}: {row['value']} vs {row['floor']} -> {'PASS' if row['pass'] else 'FAIL'}")
    print(f"  f boundary: {g['f_boundary']}")
    print(f"  VERDICT recorded: {g['verdict']}")

    # -- 6. (g) per-class >15% both directions ---------------------------------
    print("== 6. (g) per-class deltas vs r9 (flag >15% relative, both directions)")
    p9, pF = per_class(r9), per_class(f1)
    reg_flags = []
    for cls in sorted(p9):
        for m in ["recall@5", "recall@10", "recall@20", "mrr", "ndcg@10"]:
            bv, nv = float(p9[cls][m]), float(pF[cls][m])
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
    zero_bars = [c for c in sorted(p9)
                 if all(float(p9[c][m]) == 0 for m in ["recall@5", "recall@10"])
                 and any(float(pF[c][m]) > 0 for m in ["recall@5", "recall@10"])]
    if zero_bars:
        print(f"  zero->nonzero recovery classes: {zero_bars}")

    # -- 7. what depth 40 added (deep-rank composition) -------------------------
    print("== 7. what depth 40 added (refs in f-pool beyond r9's pool)")
    added_by_kind = defaultdict(int)
    added_by_band = defaultdict(int)
    for qid, e9 in r9["per_query_chunks"].items():
        s9 = set(e9["ranked_refs"])
        refsF = f1["per_query_chunks"][qid]["ranked_refs"]
        for i, ref in enumerate(refsF):
            if ref not in s9:
                added_by_kind[kinds.get(ref, "?")] += 1
                band = "21-40" if i < 40 else "41-80"
                added_by_band[band] += 1
    print(f"  added refs by kind: {dict(sorted(added_by_kind.items()))}")
    print(f"  added refs by f-rank band: {dict(sorted(added_by_band.items()))}")

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
