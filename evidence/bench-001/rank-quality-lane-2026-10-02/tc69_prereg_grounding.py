#!/usr/bin/env python3
"""T-C69 prereg grounding — all from recorded bytes (no run, no tuning).

1. Covering-ref census for the 5 flips MISSED at depth 40 (g2-011, g2-016,
   g2-056, g2-059, g2-112): for each, the gold points still uncovered in f,
   the corpus-wide refs whose HV projection covers them, those refs' kinds,
   and their presence in the r8/r9/f recorded pools.
2. Per-query notes-kind (EXTERNAL_NOTES) counts in the r9 and f union pools —
   the distribution the floor value N is derived from.
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

MISSED = ["g2-011", "g2-016", "g2-056", "g2-059", "g2-112"]


def load_projection():
    art = json.loads(PROJECTION.read_text())
    ref_codes = defaultdict(set)
    for row in art["rows"]:
        if row["provenance"]["validation_status"] != "HUMAN_VALIDATED":
            raise SystemExit("FAIL-CLOSED")
        for ref in row.get("chunk_refs", []):
            ref_codes[ref].add(row["spec_code"])
    return dict(ref_codes)


def load_gold():
    gold = {}
    for p in sorted(GOLD_DIR.glob("class_*.json")):
        for rec in json.loads(p.read_text()):
            gold[rec["id"]] = {"class": rec["class"], "points": set(rec.get("gold_spec_points") or [])}
    return gold


def load_kinds():
    return {r["chunk_ref"]: r.get("kind", "?") for r in json.load(gzip.open(SNAP7))}


def main():
    ref_codes = load_projection()
    gold = load_gold()
    kinds = load_kinds()
    runs = {rid: json.loads((RUNS / rid / "results.json").read_text())
            for rid in ["run-005-c-r8", "run-005-c-r9", "run-005-f-r1"]}
    pools = {rid: {qid: set(e["ranked_refs"]) for qid, e in run["per_query_chunks"].items()}
             for rid, run in runs.items()}

    print("== 1. covering-ref census for the 5 depth-40 MISSED flips")
    for qid in MISSED:
        pts = gold[qid]["points"]
        cov_f = set()
        for ref in pools["run-005-f-r1"][qid]:
            cov_f.update(ref_codes.get(ref, ()))
        missing = pts - cov_f
        print(f"  {qid} ({gold[qid]['class']}): gold {len(pts)} pts, missing in f: {sorted(missing)}")
        covering = [ref for ref, codes in ref_codes.items() if codes & missing]
        by_kind = defaultdict(list)
        for ref in covering:
            by_kind[kinds.get(ref, "?")].append(ref)
        for kind, refs in sorted(by_kind.items()):
            in8 = sum(1 for r in refs if r in pools["run-005-c-r8"][qid])
            in9 = sum(1 for r in refs if r in pools["run-005-c-r9"][qid])
            inf = sum(1 for r in refs if r in pools["run-005-f-r1"][qid])
            print(f"    covering refs kind={kind}: {len(refs)}  (in r8 pool: {in8}, r9: {in9}, f: {inf})")

    print("== 2. per-query EXTERNAL_NOTES count in the union pools (r9 vs f)")
    dist = {}
    for rid in ["run-005-c-r9", "run-005-f-r1"]:
        counts = sorted(sum(1 for r in refs if kinds.get(r) == "EXTERNAL_NOTES")
                        for refs in pools[rid].values())
        n = len(counts)
        med = counts[n // 2]
        dist[rid] = counts
        print(f"  {rid}: min {counts[0]} · p25 {counts[n // 4]} · median {med} · "
              f"p75 {counts[3 * n // 4]} · max {counts[-1]} · mean {sum(counts) / n:.2f}")
    tot = {rid: sum(c) for rid, c in dist.items()}
    print(f"  total notes refs: r9 {tot['run-005-c-r9']} -> f {tot['run-005-f-r1']}")
    # notes share of the pools
    for rid in ["run-005-c-r9", "run-005-f-r1"]:
        sizes = [len(x) for x in pools[rid].values()]
        print(f"  {rid}: union pool sizes min {min(sizes)} / max {max(sizes)}; "
              f"notes share {tot[rid] / sum(sizes) * 100:.1f}%")


if __name__ == "__main__":
    main()
