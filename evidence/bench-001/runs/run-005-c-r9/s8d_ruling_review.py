#!/usr/bin/env python3
"""§8(d) ruling-question evidence pack — deterministic recompute from recorded bytes.

Recomputes per-query §8(d) (SpecificationPoint resolution) for run-005-c-r8 and
run-005-c-r9 from: (1) the frozen chunk→SP HV projection artifact, (2) gold-v5
labels, (3) each run's recorded per-query served ranked_refs (top-20, ALL view).
Self-check: the recompute must reproduce the recorded aggregates byte-exactly.
Then builds the flip ledger that discriminates the two candidate readings of
§8(d): mapping fidelity vs top-rank resolution compositionality.
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
SNAP7 = RECORDS / "evidence/bench-001/snapshots/snap-007/chunks.jsonl.gz"
SNAP6 = RECORDS / "evidence/bench-001/snapshots/snap-006/chunks.jsonl.gz"


def r4(v):
    return round(v * 10000.0) / 10000.0


def load_projection():
    art = json.loads(PROJECTION.read_text())
    ref_codes = defaultdict(set)
    code_refs = defaultdict(set)
    n_rows = 0
    for row in art["rows"]:
        n_rows += 1
        status = row["provenance"]["validation_status"]
        if status != "HUMAN_VALIDATED":
            sys.exit(f"FAIL-CLOSED: non-HV row {row['mapping_id']} status={status}")
        for ref in row.get("chunk_refs", []):
            ref_codes[ref].add(row["spec_code"])
            code_refs[row["spec_code"]].add(ref)
    return dict(ref_codes), dict(code_refs), n_rows


def load_gold():
    gold = {}
    for p in sorted(GOLD_DIR.glob("class_*.json")):
        for rec in json.loads(p.read_text()):
            gold[rec["id"]] = {
                "class": rec["class"],
                "points": list(rec.get("gold_spec_points") or []),
            }
    return gold


def load_run(run_id):
    d = json.loads((RUNS / run_id / "results.json").read_text())
    return d


def score_all(run, gold, ref_codes):
    rows = {}
    pq = run["per_query_chunks"]
    for qid, entry in pq.items():
        points = gold[qid]["points"]
        covered = set()
        for ref in entry["ranked_refs"]:
            covered.update(ref_codes.get(ref, ()))
        hits = [g for g in points if g in covered]
        rows[qid] = {
            "gold": points,
            "covered": sorted(covered & set(points)),
            "full": bool(points) and len(hits) == len(set(points)),
            "hits": len(hits),
            "refs": entry["ranked_refs"],
        }
    full_hits = sum(1 for r in rows.values() if r["full"])
    gold_total = sum(len(set(r["gold"])) for r in rows.values())
    cov_total = sum(len(set(r["covered"])) for r in rows.values())
    return {
        "rows": rows,
        "full_rate": r4(full_hits / len(rows)),
        "micro": r4(cov_total / gold_total),
        "full_hits": full_hits,
        "gold_total": gold_total,
        "cov_total": cov_total,
        "n": len(rows),
    }


def main():
    ref_codes, code_refs, n_rows = load_projection()
    gold = load_gold()
    print(f"projection: {n_rows} rows, {len(ref_codes)} refs, {len(code_refs)} codes "
          f"(expect 210 / 164 / 181 in-file)")

    r8 = load_run("run-005-c-r8")
    r9 = load_run("run-005-c-r9")

    s8 = score_all(r8, gold, ref_codes)
    s9 = score_all(r9, gold, ref_codes)

    # ── self-check against the recorded aggregates ────────────────────────────
    rec8 = r8["spec_resolution_hv"]["views"]["served_view_all_denominator"]
    rec9 = r9["spec_resolution_hv"]["views"]["served_view_all_denominator"]
    checks = [
        ("r8 full_rate", s8["full_rate"], rec8["spec_points_full_coverage_rate"]),
        ("r8 micro", s8["micro"], rec8["spec_points_micro_average"]),
        ("r8 covered", s8["cov_total"], rec8["gold_points_covered"]),
        ("r8 gold_total", s8["gold_total"], rec8["gold_points_total"]),
        ("r8 n", s8["n"], rec8["queries_scored"]),
        ("r9 full_rate", s9["full_rate"], rec9["spec_points_full_coverage_rate"]),
        ("r9 micro", s9["micro"], rec9["spec_points_micro_average"]),
        ("r9 covered", s9["cov_total"], rec9["gold_points_covered"]),
        ("r9 n", s9["n"], rec9["queries_scored"]),
    ]
    ok = True
    for name, got, want in checks:
        match = got == want
        ok &= match
        print(f"  self-check {name}: recomputed={got} recorded={want} {'OK' if match else 'MISMATCH'}")
    if not ok:
        sys.exit("recompute does not reproduce recorded aggregates — aborting")

    # ── chunk-kind table from snapshots (for competitor classification) ───────
    def load_chunks(path):
        with gzip.open(path, "rt") as f:
            return {c["chunk_ref"]: c for c in json.load(f)}

    chunks7 = load_chunks(SNAP7)
    chunks6 = load_chunks(SNAP6)

    def kind_of(ref):
        c = chunks7.get(ref)
        if c is None:
            return "ABSENT-snap7"
        k = c["kind"]
        in6 = ref in chunks6
        tag = "" if in6 else "+new"
        return f"{k}{tag}"

    # ── flip ledger ────────────────────────────────────────────────────────────
    flips_down = [q for q in s8["rows"] if s8["rows"][q]["full"] and not s9["rows"][q]["full"]]
    flips_up = [q for q in s9["rows"] if s9["rows"][q]["full"] and not s8["rows"][q]["full"]]
    print(f"\nfull-coverage flips: 1->0 : {len(flips_down)}  |  0->1 : {len(flips_up)}")

    point_lost = defaultdict(int)
    point_gained = defaultdict(int)
    for q in s8["rows"]:
        a, b = set(s8["rows"][q]["covered"]), set(s9["rows"][q]["covered"])
        for p in a - b:
            point_lost[p] += 1
        for p in b - a:
            point_gained[p] += 1
    print(f"point-level: lost on {sum(point_lost.values())} query-points "
          f"({len(point_lost)} distinct codes); gained on {sum(point_gained.values())} "
          f"({len(point_gained)} distinct codes)")
    if point_gained:
        print("  gained codes:", dict(point_gained))

    print("\n=== full-coverage flip ledger (1->0) ===")
    all_flips_clean = True
    for q in sorted(flips_down, key=lambda x: (gold[x]["class"], x)):
        a, b = s8["rows"][q], s9["rows"][q]
        lost_pts = sorted(set(a["covered"]) - set(b["covered"]))
        kept_pts = sorted(set(a["covered"]) & set(b["covered"]))
        print(f"\n[{q}] class={gold[q]['class']} gold={a['gold']}")
        print(f"  covered r8={a['covered']}  r9={b['covered']}")
        print(f"  lost points: {lost_pts}")
        # carrier refs of the lost points, ranks in r8, presence in r9
        for pt in lost_pts:
            carriers = sorted(code_refs.get(pt, ()))
            for ref in carriers:
                r8_rank = a["refs"].index(ref) + 1 if ref in a["refs"] else None
                r9_rank = b["refs"].index(ref) + 1 if ref in b["refs"] else None
                state = ("in-r9-top20@" + str(r9_rank)) if r9_rank else "OUT-of-r9-top20"
                print(f"    {pt} <- ref {ref[:16]}… r8_rank={r8_rank} {state}")
        # what occupies r9's top-20 that r8's didn't
        newcomers = [r for r in b["refs"] if r not in set(a["refs"])]
        dropouts = [r for r in a["refs"] if r not in set(b["refs"])]
        kinds_new = {}
        for r in newcomers:
            k = kind_of(r)
            kinds_new[k] = kinds_new.get(k, 0) + 1
        print(f"  r9 newcomers in top20: {len(newcomers)} by kind {kinds_new}")
        print(f"  r8 dropouts from top20: {len(dropouts)}")
        # any lost point whose carriers are ALL absent from the whole corpus?
        for pt in lost_pts:
            carriers = code_refs.get(pt, set())
            if carriers and not any(cr in chunks7 for cr in carriers):
                all_flips_clean = False
                print(f"    !! {pt} carriers ALL absent from snap-7 corpus")

    # ── rank-drift on stable queries (context: competition pressure breadth) ──
    stable = [q for q in s8["rows"] if s8["rows"][q]["full"] and s9["rows"][q]["full"]]
    print(f"\nstable full-coverage queries: {len(stable)}")
    print(f"flip-ledger corpus check: "
          f"{'CLEAN — every lost point still has carrier refs in the snap-7 corpus' if all_flips_clean else 'CORPUS LOSS DETECTED'}")

    # ── summary block for the record ──────────────────────────────────────────
    print("\n=== SUMMARY ===")
    print(f"r8: full {s8['full_hits']}/{s8['n']} = {s8['full_rate']} · micro {s8['cov_total']}/{s8['gold_total']} = {s8['micro']}")
    print(f"r9: full {s9['full_hits']}/{s9['n']} = {s9['full_rate']} · micro {s9['cov_total']}/{s9['gold_total']} = {s9['micro']}")
    print(f"flips 1->0: {len(flips_down)} · flips 0->1: {len(flips_up)} · "
          f"query-points lost {sum(point_lost.values())} · gained {sum(point_gained.values())}")
    print("lost codes:", dict(point_lost))


if __name__ == "__main__":
    main()
