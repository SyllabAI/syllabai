#!/usr/bin/env python3
"""run-005-e post-run verification — from recorded bytes only (T-C65).

Checks the two pre-registered invariants (FUSION-WEIGHTS-PREREGISTRATION.md,
records 3880dd5, committed BEFORE the run):
  1. pool set identity: per query, run-005-e's ranked_refs SET == r9's SET (89/89)
  2. §8(d) exact invariance: recompute (d) for run-005-e from the frozen
     projection x gold-v5 x recorded ranked_refs; must equal the recorded
     aggregates AND r9's exactly (0.4607 / 0.7857)
Plus the movement ledger for the authored report:
  - first-20 entry/exit per query with document kinds
  - gold tier-2 hit-depth movement (first-hit rank, count within first 20)
  - per-class chunk-axis deltas vs r9 and vs run-005-d-r1 (>15% relative flagged)
"""
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

RECORDS = Path("/home/z/my-project/repos/syllabai")
RUNS = RECORDS / "evidence/bench-001/runs"
PROJECTION = RECORDS / "bench/evidence/chunk-sp-substrate-2026-09-27/chunk_spec_hv_projection.json"
GOLD_DIR = RECORDS / "bench/gold-v5"
SNAP7 = RECORDS / "bench/inputs/snapshot-r9/chunks.jsonl.gz"

R9 = "run-005-c-r9"
DR1 = "run-005-d-r1"
E1 = "run-005-e-r1"


def r4(v):
    return round(v * 10000.0) / 10000.0


def load_projection():
    art = json.loads(PROJECTION.read_text())
    ref_codes = defaultdict(set)
    for row in art["rows"]:
        if row["provenance"]["validation_status"] != "HUMAN_VALIDATED":
            sys.exit(f"FAIL-CLOSED: non-HV row {row['mapping_id']}")
        for ref in row.get("chunk_refs", []):
            ref_codes[ref].add(row["spec_code"])
    return dict(ref_codes)


def load_gold():
    gold = {}
    for p in sorted(GOLD_DIR.glob("class_*.json")):
        for rec in json.loads(p.read_text()):
            gold[rec["id"]] = {
                "class": rec["class"],
                "points": list(rec.get("gold_spec_points") or []),
                "chunks": {e["chunk_ref"]: e["tier"]
                           for e in (rec.get("gold_evidence") or [])},
            }
    return gold


def load_run(run_id):
    return json.loads((RUNS / run_id / "results.json").read_text())


def load_kinds():
    recs = json.load(gzip.open(SNAP7))
    return {r["chunk_ref"]: r.get("kind", "?") for r in recs}


def score_d(run, gold, ref_codes):
    rows = {}
    for qid, entry in run["per_query_chunks"].items():
        points = set(gold[qid]["points"])
        covered = set()
        for ref in entry["ranked_refs"]:
            covered.update(ref_codes.get(ref, ()))
        hits = points & covered
        rows[qid] = {"full": bool(points) and len(hits) == len(points),
                     "n": len(hits), "gold_n": len(points)}
    full = sum(1 for r in rows.values() if r["full"])
    gold_total = sum(r["gold_n"] for r in rows.values())
    cov_total = sum(r["n"] for r in rows.values())
    return {"full_rate": r4(full / len(rows)), "micro": r4(cov_total / gold_total),
            "full_n": full, "queries": len(rows), "gold_total": gold_total,
            "cov_total": cov_total}


def recorded_d(run):
    views = run["spec_resolution_hv"]["views"]
    sv = views["served_view_all_denominator"]
    return r4(sv["spec_points_full_coverage_rate"]), r4(sv["spec_points_micro_average"])


def first20_ledger(r9, e1, kinds, gold):
    entries, exits = defaultdict(int), defaultdict(int)
    changed_sets = 0
    depth_moves = []
    for qid, e9 in r9["per_query_chunks"].items():
        refs9 = e9["ranked_refs"]
        refsE = e1["per_query_chunks"][qid]["ranked_refs"]
        s9, sE = set(refs9[:20]), set(refsE[:20])
        if s9 != sE:
            changed_sets += 1
        for ref in sE - s9:
            entries[kinds.get(ref, "?")] += 1
        for ref in s9 - sE:
            exits[kinds.get(ref, "?")] += 1
        gchunks = gold[qid]["chunks"]
        t2 = [c for c, t in gchunks.items() if t == 2]
        if t2:
            d9 = min((refs9.index(c) + 1 for c in t2 if c in refs9), default=None)
            dE = min((refsE.index(c) + 1 for c in t2 if c in refsE), default=None)
            n9 = sum(1 for c in t2 if c in refs9[:20])
            nE = sum(1 for c in t2 if c in refsE[:20])
            depth_moves.append((qid, d9, dE, n9, nE))
    return changed_sets, dict(entries), dict(exits), depth_moves


def cls_delta(base, new):
    b = base["chunk_axis"]["served_view"]["per_class"]
    n = new["chunk_axis"]["served_view"]["per_class"]
    out = {}
    for cls in sorted(b):
        row = {}
        for m in ["recall@5", "recall@10", "recall@20", "mrr", "ndcg@10"]:
            bv, nv = float(b[cls][m]), float(n[cls][m])
            rel = (nv - bv) / bv if bv > 0 else None
            row[m] = (bv, nv, rel)
        out[cls] = row
    return out


def main():
    r9, e1, dr1 = load_run(R9), load_run(E1), load_run(DR1)
    ref_codes = load_projection()
    gold = load_gold()
    kinds = load_kinds()

    print("== invariant 1: pool set identity (ranked_refs as SETS, r9 vs run-005-e)")
    same = diff = 0
    for qid, e9 in r9["per_query_chunks"].items():
        if set(e9["ranked_refs"]) == set(e1["per_query_chunks"][qid]["ranked_refs"]):
            same += 1
        else:
            diff += 1
            print("  MISMATCH:", qid)
    print(f"  identical pools: {same}/{same + diff}")

    print("== invariant 2: (d) exact invariance")
    rec9 = recorded_d(r9)
    recE = recorded_d(e1)
    compE = score_d(e1, gold, ref_codes)
    print(f"  r9 recorded:      full={rec9[0]} micro={rec9[1]}")
    print(f"  e1 recorded:      full={recE[0]} micro={recE[1]}")
    print(f"  e1 recomputed:    full={compE['full_rate']} micro={compE['micro']} "
          f"({compE['full_n']}/{compE['queries']} full, {compE['cov_total']}/{compE['gold_total']} points)")
    ok = (rec9 == recE == (compE["full_rate"], compE["micro"]))
    print("  invariant 2:", "HOLDS (all three agree)" if ok else "VIOLATED — investigate")

    print("== first-20 movement (r9 -> e1)")
    changed, entries, exits, depth_moves = first20_ledger(r9, e1, kinds, gold)
    print(f"  queries with changed first-20 SET: {changed}/89")
    print(f"  entries by kind: {entries}")
    print(f"  exits by kind:   {exits}")

    print("== gold tier-2 hit-depth movement (per labeled query with tier-2 chunks)")
    better = worse = same20 = 0
    t2_in20_9 = t2_in20_E = 0
    d9s, dEs = [], []
    for qid, d9, dE, n9, nE in depth_moves:
        t2_in20_9 += n9
        t2_in20_E += nE
        if d9 is not None:
            d9s.append(d9)
        if dE is not None:
            dEs.append(dE)
        if d9 is not None and dE is not None:
            if dE < d9:
                better += 1
            elif dE > d9:
                worse += 1
            else:
                same20 += 1
        elif d9 is None and dE is not None:
            better += 1
        elif d9 is not None and dE is None:
            worse += 1
    d9s.sort()
    dEs.sort()
    med = lambda a: a[len(a) // 2] if a else None
    print(f"  first tier-2 hit: improved {better}, worsened {worse}, same {same20}")
    print(f"  median first-hit depth: r9={med(d9s)} e1={med(dEs)} (n_r9={len(d9s)}, n_e1={len(dEs)})")
    print(f"  tier-2 chunks inside first-20: r9={t2_in20_9} e1={t2_in20_E}")

    print("== per-class served-view deltas (e1 vs r9; flag >15% relative regression)")
    for cls, row in cls_delta(r9, e1).items():
        flags = [f"{m} {bv}->{nv} ({rel * 100:+.1f}%)" for m, (bv, nv, rel) in row.items()
                 if rel is not None and rel < -0.15]
        base = " | ".join(f"{m} {bv}->{nv}" for m, (bv, nv, rel) in row.items())
        print(f"  {cls}: {base}" + ("   REG>15%: " + "; ".join(flags) if flags else ""))

    print("== overall served-view: r9 vs d-r1 vs e1")
    for name, run in [("r9 ", r9), ("d-r1", dr1), ("e1 ", e1)]:
        o = run["chunk_axis"]["served_view"]["overall"]
        print(f"  {name}: r@5={o['recall@5']} r@10={o['recall@10']} r@20={o['recall@20']} "
              f"mrr={o['mrr']} ndcg@10={o['ndcg@10']}")
    gE = e1["s8_gate"]
    print("== gate:")
    for k, v in gE.items():
        if isinstance(v, dict) and "pass" in v:
            print(f"  {k}: value={v.get('value', v.get('served_violations'))} pass={v['pass']}")
    print("  verdict:", gE["verdict"])


if __name__ == "__main__":
    main()
