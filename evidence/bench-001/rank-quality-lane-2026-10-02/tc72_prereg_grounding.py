#!/usr/bin/env python3
"""T-C72 prereg grounding — all from recorded bytes + the frozen preload-r9
artifact (no run, no bench execution, no tuning).

1. (d) recompute for r8/r9/f/g — byte-exact self-checks against the recorded
   verdicts (the machinery check, same shape as run005f/g_verify).
2. Mechanical derivation of the f-lost flips (r8-full -> f-not-full); per
   flip the missing points, the corpus-wide covering refs (frozen HV
   projection), their kinds, and their presence in the r8/r9/f/g pools.
3. THE REACH CENSUS (new — resolves the unknown T-C69 could not: "arm ranks
   beyond 40 are NOT recorded anywhere"): for every fresh covering carrier,
   its cosine rank GLOBALLY (1..4510, all embedded chunks) and WITHIN the
   EXTERNAL_NOTES kind (1..350, notes competing only against notes), both by
   exact linear algebra on the FROZEN preload-r9 artifact (SHA-verified
   against the recorded echo before use). The production path (HNSW
   approximation, SQL scope, tie behavior) makes the run's admission the
   test — the census numbers are pre-registered EXPECTATIONS, not theorems.
4. K-derivation table: flips whose nearest carrier enters notes-top-K; the
   expected pool growth / notes share / predicted (d) at each candidate K
   (SET arithmetic: the fused output is the full union of arm inputs, so
   every notes-top-K ref enters the pool set by construction).
5. MIN_COSINE reach analysis: carrier cosine vs the f-pool's minimum cosine
   — the threshold arithmetic that makes a cosine filter mechanically
   unable to extend count-cut reach (a threshold admitting a deeper carrier
   excludes nothing above it; the count cut, not the quality cut, binds).
"""
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

RECORDS = Path("/home/z/my-project/audit/syllabai")
RUNS = RECORDS / "evidence/bench-001/runs"
PROJECTION = RECORDS / "bench/evidence/chunk-sp-substrate-2026-09-27/chunk_spec_hv_projection.json"
GOLD_DIR = RECORDS / "bench/inputs/gold-r9"
SNAP7 = RECORDS / "bench/inputs/snapshot-r9/chunks.jsonl.gz"
PRELOAD = RECORDS / "bench/inputs/embeddings/preload-r9"

RUN_IDS = ["run-005-c-r8", "run-005-c-r9", "run-005-f-r1", "run-005-g-r1"]
RECORDED_D = {  # recorded (d) full/micro from the packs — self-check targets
    "run-005-c-r8": (0.5618, 0.9167),
    "run-005-c-r9": (0.4607, 0.7857),
    "run-005-f-r1": (0.5056, 0.8571),
    "run-005-g-r1": (0.5169, 0.8690),
}
K_CANDIDATES = [5, 10, 15, 20, 25, 30, 40, 50, 100, 150, 200, 350]
N_SCORED, N_POINTS = 89, 84  # the recorded chunk-axis denominators (fail-closed)


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
            raise SystemExit("FAIL-CLOSED: projection row not HUMAN_VALIDATED")
        for ref in row.get("chunk_refs", []):
            ref_codes[ref].add(row["spec_code"])
    return dict(ref_codes)


def load_gold():
    gold = {}
    for p in sorted(GOLD_DIR.glob("class_*.json")):
        for rec in json.loads(p.read_text()):
            gold[rec["id"]] = {"class": rec["class"],
                               "points": set(rec.get("gold_spec_points") or [])}
    return gold


def load_kinds():
    return {r["chunk_ref"]: r.get("kind", "?")
            for r in json.load(gzip.open(SNAP7))}


def load_embeddings():
    """Frozen preload-r9 vectors, SHA-verified against the recorded echo."""
    echo = json.loads((RUNS / "run-005-g-r1" / "results.json").read_text())[
        "embedding_artifact"]["sha256_echo"]
    for fname in ["embeddings_chunks.jsonl", "embeddings_queries.jsonl"]:
        actual = sha256(PRELOAD / fname)
        if actual != echo[fname]:
            raise SystemExit(f"FAIL-CLOSED: {fname} sha {actual[:12]}… != recorded echo")
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
        raise SystemExit(f"FAIL-CLOSED: unexpected dims {dims}")
    return chunks, queries


def main():
    ref_codes = load_projection()
    gold = load_gold()
    kinds = load_kinds()
    chunks, queries = load_embeddings()
    runs = {rid: json.loads((RUNS / rid / "results.json").read_text()) for rid in RUN_IDS}
    scored_sets = [set(r["per_query_chunks"].keys()) for r in runs.values()]
    if len({frozenset(s) for s in scored_sets}) != 1:
        raise SystemExit("FAIL-CLOSED: scored sets differ across runs")
    scored_ids = sorted(scored_sets[0])
    if len(scored_ids) != N_SCORED:
        raise SystemExit(f"FAIL-CLOSED: scored {len(scored_ids)} != {N_SCORED}")
    pools = {rid: {qid: set(e["ranked_refs"])
                   for qid, e in run["per_query_chunks"].items()}
             for rid, run in runs.items()}
    for qid in scored_ids:
        if qid not in gold:
            raise SystemExit(f"FAIL-CLOSED: scored query {qid} missing from gold-r9")

    def coverage(rid):
        cov = {}
        for qid in scored_ids:
            codes = set()
            for ref in pools[rid][qid]:
                codes |= ref_codes.get(ref, set())
            pts = gold[qid]["points"]
            cov[qid] = {"covered": pts & codes,
                        "full": bool(pts) and pts <= codes}
        return cov

    print("== 1. (d) recompute self-checks (recorded vs recomputed from pool bytes)")
    gold_total = sum(len(gold[qid]["points"]) for qid in scored_ids)
    if gold_total != N_POINTS:
        raise SystemExit(f"FAIL-CLOSED: gold points across scored {gold_total} != {N_POINTS}")
    covs = {}
    for rid in RUN_IDS:
        c = coverage(rid)
        full = sum(1 for qid in scored_ids if c[qid]["full"])
        micro = sum(len(c[qid]["covered"]) for qid in scored_ids)
        rf, rm = RECORDED_D[rid]
        ok = abs(full / N_SCORED - rf) < 5e-5 and abs(micro / N_POINTS - rm) < 5e-5
        print(f"  {rid}: full {full}/{N_SCORED} = {full/N_SCORED:.4f} · "
              f"micro {micro}/{N_POINTS} = {micro/N_POINTS:.4f} · recorded {rf}/{rm} · "
              f"{'OK' if ok else 'MISMATCH'}")
        if not ok:
            raise SystemExit(f"FAIL-CLOSED: (d) self-check mismatch for {rid}")
        covs[rid] = c

    print("== 2. f-lost flips (r8-full -> f-not-full), mechanically derived")
    lost = sorted(q for q in scored_ids if covs["run-005-c-r8"][q]["full"]
                  and not covs["run-005-f-r1"][q]["full"])
    print(f"  f-lost flips: {len(lost)} {lost}")
    if lost != ["g2-011", "g2-016", "g2-056", "g2-059", "g2-112"]:
        raise SystemExit(f"FAIL-CLOSED: unexpected flip set {lost}")

    print("== 3. reach census per flip (exact cosine on the frozen artifact)")
    mat_refs = sorted(chunks.keys())
    pos = {r: i for i, r in enumerate(mat_refs)}
    mat = np.vstack([chunks[r] for r in mat_refs])
    norms = np.linalg.norm(mat, axis=1)
    notes_idx = np.asarray([i for i, r in enumerate(mat_refs)
                            if kinds.get(r) == "EXTERNAL_NOTES"])
    print(f"  corpus {len(mat_refs)} embedded chunks · EXTERNAL_NOTES {len(notes_idx)} "
          f"(the notes-arm universe)")
    carriers = {}  # qid -> list of dicts
    for qid in lost:
        missing = gold[qid]["points"] - covs["run-005-f-r1"][qid]["covered"]
        if len(missing) != 1:
            raise SystemExit(f"FAIL-CLOSED: {qid} misses {len(missing)} points, expected 1")
        covering = [ref for ref, codes in ref_codes.items() if codes & missing]
        by_kind = defaultdict(list)
        for ref in covering:
            by_kind[kinds.get(ref, "?")].append(ref)
        fresh = sorted(r for r in covering if r not in pools["run-005-f-r1"][qid])
        print(f"  {qid} ({gold[qid]['class']}): missing 1 point {sorted(missing)[0]} · "
              f"covering refs {len(covering)} by kind {dict(sorted(by_kind.items()))} · "
              f"fresh (not in f-pool): {len(fresh)}")
        qv = queries[qid]
        sims = (mat @ qv) / (norms * np.linalg.norm(qv))
        global_rank = np.empty(len(mat_refs), dtype=int)
        global_rank[np.argsort(-sims, kind="stable")] = np.arange(1, len(mat_refs) + 1)
        notes_sorted = notes_idx[np.argsort(-sims[notes_idx], kind="stable")]
        notes_rank = {i: p + 1 for p, i in enumerate(notes_sorted)}
        pool_min_cos = min(sims[pos[r]] for r in pools["run-005-f-r1"][qid])
        rows = []
        for ref in fresh:
            i = pos[ref]
            rows.append({"ref": ref, "gr": int(global_rank[i]),
                         "nr": notes_rank[i], "cos": float(sims[i])})
            print(f"    carrier {ref[:14]}… kind={kinds.get(ref)} · GLOBAL rank "
                  f"{global_rank[i]}/{len(mat_refs)} · NOTES rank {notes_rank[i]}/"
                  f"{len(notes_idx)} · cos {sims[i]:.4f} · f-pool min cos "
                  f"{pool_min_cos:.4f} · in r8: {ref in pools['run-005-c-r8'][qid]} · "
                  f"in g-pool: {ref in pools['run-005-g-r1'][qid]}")
        if rows and all(r["cos"] < pool_min_cos for r in rows):
            print(f"    -> every fresh carrier sits BELOW the f-pool's minimum cosine: "
                  f"no MIN_COSINE threshold admits one without the whole pool already "
                  f"qualifying (the count cut binds, not the quality cut)")
        carriers[qid] = rows

    print("== 4. K-derivation + expected SET effects at each candidate K")
    for K in K_CANDIDATES:
        hits = [q for q in lost if carriers[q]
                and min(r["nr"] for r in carriers[q]) <= K]
        grow = 0
        notes_new = 0
        for qid in scored_ids:
            qv = queries[qid]
            sims = (mat @ qv) / (norms * np.linalg.norm(qv))
            notes_sorted = notes_idx[np.argsort(-sims[notes_idx], kind="stable")][:K]
            new = {mat_refs[i] for i in notes_sorted} - pools["run-005-f-r1"][qid]
            grow += len(new)
            notes_new += sum(1 for r in new if kinds.get(r) == "EXTERNAL_NOTES")
        pred_full = 45 + len(hits)
        pred_micro = 72 + len(hits)
        f_total = sum(len(pools['run-005-f-r1'][q]) for q in scored_ids)
        f_notes = sum(sum(1 for r in pools['run-005-f-r1'][q]
                          if kinds.get(r) == 'EXTERNAL_NOTES') for q in scored_ids)
        share = (f_notes + notes_new) / (f_total + grow) * 100
        print(f"  K={K:>3}: flips admitting a carrier {len(hits)}/5 {hits if hits else ''} · "
              f"expected pool growth +{grow} refs ({notes_new} notes) · predicted notes "
              f"share {share:.1f}% (f 15.3%) · predicted (d) {pred_full}/{N_SCORED}="
              f"{pred_full/N_SCORED:.4f} full, {pred_micro}/{N_POINTS}="
              f"{pred_micro/N_POINTS:.4f} micro")

    print("== 5. ceiling arithmetic (unchanged from T-C69, both framings)")
    print("  from f: 45+5 = 50/89 = 0.5618 full · 72+5 = 77/84 = 0.9167 micro")
    print("  from g: 46+4 = 50/89 = 0.5618 full · 73+4 = 77/84 = 0.9167 micro")
    print("  full success on all 5 flips = byte-exact r8 reversion (the ceiling);")
    print("  r8 is a DIFFERENT-basis reference (snap-006 + chunk vectors 1e22a202…)")
    print("  — the recorded ruling baseline, not a target under the current basis.")


if __name__ == "__main__":
    main()
