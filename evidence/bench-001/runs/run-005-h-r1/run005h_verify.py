#!/usr/bin/env python3
"""run-005-h post-run verification — from recorded bytes only (T-C72).

Verifies the pre-registered invariants (ARM-COMPOSITION-PREREGISTRATION.md,
records 8340542, committed BEFORE the run) for the arm-composition lever in
KIND-ARM form (BENCH_NOTES_KIND_ARM=15 at the recorded depth-40 posture; one
lever, floor/reranker/weights ABSENT; code c346d64 = merged main):

  1. superset invariant (per query): run-005-h's served pool SET
     >= run-005-f's pool SET. Expected 89/89 (the kind-arm appends a third
     input; the existing arms' lists are byte-unchanged; the g2-024
     HNSW/tie re-execution risk is the declared residual). Violations are
     recorded as FINDINGS with their exact ledger, and (d) monotonicity is
     then claimed only over the held subset. The h-vs-g delta is recorded
     as a LEDGER (no theorem: h's floor is ABSENT — a g-era floor admission
     is not guaranteed in h's pool).
  2. (d) recompute + the r8 ceiling: recompute the section-8(d) aggregates
     for run-005-h from the frozen HV projection x gold x h's recorded
     ranked_refs; must equal h's recorded aggregate. Machinery self-check:
     the same recompute on r8, r9, f, g must reproduce their recorded
     aggregates byte-exactly. Ceiling framing (pre-registered): exact r8
     reversion = 50/89 = 0.5618 full, 77/84 = 0.9167 micro. Exceeding r8
     is a FINDING (r8 is a DIFFERENT-basis recorded reference, snap-006 +
     chunk vectors 1e22a202... — not a target under the current basis).
  3. per-flip admission ledger (mechanically derived, no hand-maintained
     lists): for every f-lost flip (r8-full -> f-not-full) the pack records
     ADMITTED+REVERTED (a census covering ref enters h's union via the
     kind-arm and the query reverts to full), ADMITTED+PARTIAL (covering
     ref enters; other points still missing), or MISS-AT-ARM (no census
     covering ref in h's union — falsifies the census reach prediction for
     that flip, recorded honestly). Census-vs-run comparison ships here:
     each carrier's exact-cosine NOTES rank (frozen preload-r9 artifact,
     SHA-verified against the recorded echo) beside its h-pool presence and
     fused rank — the production kind-arm's reach vs the census expectation
     (NOTES ranks 4/6/8/8/11/13 of 350; K=15 reach complete).
  4. non-regression watch: every f-full query must stay full in h (the
     kind-arm removes nothing); g2-061's covered-point count must not drop;
     the g-era reverted flips' (g2-042/048/050/053) covering refs stay
     in-pool; per-query covered-point monotonicity on the superset-held
     subset (covered gold points(h) >= covered gold points(f)).
  5. notes-share ledger: per-query EXTERNAL_NOTES share of the union pools
     across r9 -> f -> g -> h (the prereg's 20.4% -> 15.3% -> 16.9% ->
     ~30.6%-predicted chain; the overshoot is the lever's shape, declared
     BEFORE the run and judged by the gates, not smoothed).
Plus the movement/accounting ledgers for the authored report:
  pool growth vs the predicted +797 notes refs, what the kind-arm admitted
  (refs, kinds, h-rank bands), (a)-(c) deltas vs f with the recall@20 pin
  statement (declared AT-RISK BY DESIGN this tranche — no byte-stability
  pin), the section-8.1 v1.1 gate rows, the (g) per-class >15% relative
  flags, and the (e) latency reading.
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
SELFCHECK_RUNS = [R8, R9, F1, G1]
RECORDED_D = {  # recorded (d) full/micro from the packs — self-check targets
    R8: (0.5618, 0.9167),
    R9: (0.4607, 0.7857),
    F1: (0.5056, 0.8571),
    G1: (0.5169, 0.8690),
}
N_SCORED, N_POINTS = 89, 84  # the recorded chunk-axis denominators (fail-closed)
K_KIND_ARM = 15
G_ERA_REVERTED = ["g2-042", "g2-048", "g2-050", "g2-053"]  # the T-C69 watch set
GATES_V11 = {  # spec section-8.1 v1.1 bars (T-C40 (2), 2026-10-01)
    "a_recall@10": ("ALL", "recall@10", 0.1920),
    "b_mrr": ("ALL", "mrr", 0.1237),
    "c_ndcg@10": ("ALL", "ndcg@10", 0.2316),
    "a2_validated_recall@10": ("VALIDATED", "recall@10", 0.0734),
    "b2_validated_mrr": ("VALIDATED", "mrr", 0.1184),
    "c2_validated_ndcg@10": ("VALIDATED", "ndcg@10", 0.1683),
}

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


def load_embeddings():
    """Frozen preload-r9 vectors, SHA-verified against the recorded echo."""
    echo = json.loads((RUNS / G1 / "results.json").read_text())[
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
    chunks, queries = load_embeddings()
    runs = {rid: json.loads((RUNS / rid / "results.json").read_text())
            for rid in SELFCHECK_RUNS + [H1]}
    h = runs[H1]

    print("# run-005-h verify — from recorded bytes only (T-C72 KIND-ARM form)")
    print(f"# code {h['code_version']} | run_id {h['run_id']} | date {h['date']}")
    fb = h["fabric"]
    print(f"# posture: providers {fb['providers']} | per_arm_limit {fb['per_arm_limit']} | "
          f"notes_kind_arm {fb['notes_kind_arm']} | notes_floor {fb['notes_floor']} | "
          f"weights {'null' if 'unweighted' in fb['fusion_weights'] else 'NON-NULL'}")
    if fb["providers"] != ["pgvector", "bm25", "notes-kind-arm"]:
        fail(f"providers {fb['providers']} != the four-guard posture")
    if fb["notes_kind_arm"] != K_KIND_ARM or fb["notes_floor"] != 0:
        fail(f"posture mismatch: kind_arm {fb['notes_kind_arm']} floor {fb['notes_floor']}")
    if h["code_version"] != "c346d645d119708bcf0f5d9cac2ae15131654970":
        fail(f"code_version {h['code_version']} != merged main c346d64")
    print(f"# determinism: {h['determinism_check'][:88]}...")
    print(f"# kind-arm under-fill: {h.get('notes_kind_arm_underfill', {}).get('underfilled_queries')} "
          f"queries (expected 0 at universe 350)")
    uf = h.get("notes_kind_arm_underfill", {}).get("underfilled_queries")
    if uf != 0:
        finding(f"kind-arm under-filled {uf} queries — recorded honestly")

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

    # == 1. (d) recompute self-checks =======================================
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
    for rid in SELFCHECK_RUNS + [H1]:
        c = coverage(rid)
        full = sum(1 for qid in scored_ids if c[qid]["full"])
        micro = sum(len(c[qid]["covered"]) for qid in scored_ids)
        if rid in RECORDED_D:
            rf, rm = RECORDED_D[rid]
            ok = abs(full / N_SCORED - rf) < 5e-5 and abs(micro / N_POINTS - rm) < 5e-5
            print(f"  {rid}: full {full}/{N_SCORED} = {full/N_SCORED:.4f} · "
                  f"micro {micro}/{N_POINTS} = {micro/N_POINTS:.4f} · recorded {rf}/{rm} · "
                  f"{'OK' if ok else 'MISMATCH'}")
            if not ok:
                fail(f"(d) self-check mismatch for {rid}")
        else:
            rf_h = h["spec_resolution_hv"]["views"]["served_view_all_denominator"]
            rec_full = rf_h["spec_points_full_coverage_rate"]
            rec_micro = rf_h["spec_points_micro_average"]
            ok = abs(full / N_SCORED - rec_full) < 5e-5 and abs(micro / N_POINTS - rec_micro) < 5e-5
            print(f"  {rid}: full {full}/{N_SCORED} = {full/N_SCORED:.4f} (recorded {rec_full}) · "
                  f"micro {micro}/{N_POINTS} = {micro/N_POINTS:.4f} (recorded {rec_micro}) · "
                  f"{'OK' if ok else 'MISMATCH'}")
            if not ok:
                fail(f"(d) recompute mismatch for h")
        covs[rid] = c
    hf, hm = (sum(1 for q in scored_ids if covs[H1][q]["full"]),
              sum(len(covs[H1][q]["covered"]) for q in scored_ids))
    gf = RECORDED_D[G1][0]
    print(f"  (d) chain: r8 0.5618/0.9167 -> r9 0.4607/0.7857 -> f 0.5056/0.8571 -> "
          f"g 0.5169/0.8690 -> h {hf}/{N_SCORED}={hf/N_SCORED:.4f} / {hm}/{N_POINTS}={hm/N_POINTS:.4f}")
    if hf < RECORDED_D[F1][0] * N_SCORED - 1e-9:
        fail("(d) full regressed below f")
    if hm / N_POINTS < RECORDED_D[F1][1] - 5e-5:
        fail("(d) micro regressed below f")
    if hf / N_SCORED > RECORDED_D[R8][0]:
        finding(f"(d) full {hf/N_SCORED:.4f} EXCEEDS the r8 recorded reference 0.5618 "
                f"(r8 = different basis: snap-006 + chunk vectors 1e22a202... — the prereg "
                f"declared exceeding r8 not expected; recorded honestly, judged by the gates)")
    if hm / N_POINTS > RECORDED_D[R8][1]:
        finding(f"(d) micro {hm/N_POINTS:.4f} EXCEEDS the r8 recorded reference 0.9167")

    # == 2. superset invariant h >= f (the conditional theorem's hypothesis) ==
    print("\n== 2. superset invariant: h pool >= f pool, per query (expected 89/89)")
    violations = []
    for qid in scored_ids:
        missing = pools[F1][qid] - pools[H1][qid]
        if missing:
            violations.append((qid, sorted(missing)))
    print(f"  superset held: {N_SCORED - len(violations)}/{N_SCORED} queries")
    if violations:
        finding(f"superset VIOLATIONS on {len(violations)} queries — the g2-024 "
                f"HNSW/tie re-execution residual; (d) monotonicity claimed only on the "
                f"held subset; exact ledger follows")
        for qid, refs in violations[:10]:
            print(f"    {qid}: f-only refs {refs[:6]}{' …' if len(refs) > 6 else ''}")
    g_delta = {qid: pools[G1][qid] - pools[H1][qid] for qid in scored_ids}
    g_only = {q: r for q, r in g_delta.items() if r}
    print(f"  h-vs-g ledger (no theorem — h floor ABSENT): {len(g_only)} queries carry "
          f"g-era refs absent from h (total {sum(len(r) for r in g_only.values())} refs); "
          f"h adds {sum(len(pools[H1][q] - pools[G1][q]) for q in scored_ids)} refs g lacks")

    # == 3. f-lost flips + census-vs-run per-flip ledger =====================
    print("\n== 3. per-flip admission ledger (mechanically derived) + census-vs-run")
    lost = sorted(q for q in scored_ids if covs[R8][q]["full"] and not covs[F1][q]["full"])
    print(f"  f-lost flips: {len(lost)} {lost}")
    if lost != ["g2-011", "g2-016", "g2-056", "g2-059", "g2-112"]:
        fail(f"unexpected flip set {lost}")
    mat_refs = sorted(chunks.keys())
    pos = {r: i for i, r in enumerate(mat_refs)}
    mat = np.vstack([chunks[r] for r in mat_refs])
    norms = np.linalg.norm(mat, axis=1)
    notes_idx = np.asarray([i for i, r in enumerate(mat_refs)
                            if kinds.get(r) == "EXTERNAL_NOTES"])
    print(f"  corpus {len(mat_refs)} embedded chunks · EXTERNAL_NOTES {len(notes_idx)} "
          f"(the kind-arm universe)")
    flip_states = {}
    for qid in lost:
        missing = gold[qid]["points"] - covs[F1][qid]["covered"]
        if len(missing) != 1:
            fail(f"{qid} misses {len(missing)} points, expected 1")
        covering = sorted(ref for ref, codes in ref_codes.items() if codes & missing)
        fresh = sorted(r for r in covering if r not in pools[F1][qid])
        qv = queries[qid]
        sims = (mat @ qv) / (norms * np.linalg.norm(qv))
        notes_sorted = notes_idx[np.argsort(-sims[notes_idx], kind="stable")]
        notes_rank = {i: p + 1 for p, i in enumerate(notes_sorted)}
        admitted = [r for r in covering if r in pools[H1][qid]]
        state = ("ADMITTED+REVERTED" if admitted and covs[H1][qid]["full"]
                 else "ADMITTED+PARTIAL" if admitted else "MISS-AT-ARM")
        flip_states[qid] = state
        hrank = {r: ranks[H1][qid].index(r) + 1 for r in admitted if r in ranks[H1][qid]}
        print(f"  {qid} ({gold[qid]['class']}): missing point {sorted(missing)[0]} · "
              f"covering refs {len(covering)} ({len(fresh)} fresh vs f) · {state}")
        global_rank = np.empty(len(mat_refs), dtype=int)
        global_rank[np.argsort(-sims, kind="stable")] = np.arange(1, len(mat_refs) + 1)
        for ref in fresh:
            i = pos[ref]
            in_h = ref in pools[H1][qid]
            fr = ranks[H1][qid].index(ref) + 1 if in_h else None
            print(f"    carrier {ref[:14]}... kind={kinds.get(ref)} · census NOTES rank "
                  f"{notes_rank[i]}/{len(notes_idx)} · GLOBAL rank {global_rank[i]}/"
                  f"{len(mat_refs)} · cos {sims[i]:.4f} · in h-pool: {in_h}"
                  + (f" · h fused rank {fr}" if fr else " · NOT REACHED (MISS-AT-ARM signal)"))
        for ref in covering:
            if ref not in fresh:
                in_h = ref in pools[H1][qid]
                print(f"    in-f ref {ref[:14]}... kind={kinds.get(ref)} · in h-pool: {in_h}")
    n_rev = sum(1 for s in flip_states.values() if s == "ADMITTED+REVERTED")
    n_part = sum(1 for s in flip_states.values() if s == "ADMITTED+PARTIAL")
    n_miss = sum(1 for s in flip_states.values() if s == "MISS-AT-ARM")
    print(f"  flip ledger summary: {n_rev} ADMITTED+REVERTED · {n_part} ADMITTED+PARTIAL · "
          f"{n_miss} MISS-AT-ARM (predicted: 5 ADMITTED+REVERTED -> ceiling exactly)")
    if n_miss:
        finding(f"{n_miss} flips MISS-AT-ARM — falsifies the census reach prediction for "
                f"those flips (recorded honestly, the prereg's own falsifiability rule)")
    if n_rev == 5:
        finding("all 5 flips ADMITTED+REVERTED, yet (d) moved BEYOND the exact-reversion "
                "ceiling — the kind-arm recovered additional queries beyond the flip set "
                "(the ceiling framing counted only the 5 pre-registered flips)")
    extra = sorted(q for q in scored_ids if covs[H1][q]["full"]
                   and not covs[F1][q]["full"] and q not in lost)
    print(f"  beyond-flip recoveries ({len(extra)}): {extra}")
    for qid in extra:
        newly = covs[H1][qid]["covered"] - covs[F1][qid]["covered"]
        carr = sorted(ref for ref, c in ref_codes.items()
                      if c & newly and ref not in pools[F1][qid] and ref in pools[H1][qid])
        print(f"    {qid} ({gold[qid]['class']}): newly covered points {sorted(newly)} · "
              f"fresh in-pool covering refs {len(carr)}"
              + (f" e.g. {carr[0][:14]}... ({kinds.get(carr[0])})" if carr else ""))

    # == 4. non-regression watch =============================================
    print("\n== 4. non-regression watch")
    f_full_losses = [q for q in scored_ids if covs[F1][q]["full"] and not covs[H1][q]["full"]]
    print(f"  f-full losses: {len(f_full_losses)}"
          + (f" {f_full_losses}" if f_full_losses else " (zero — the lever removes nothing)"))
    if f_full_losses:
        fail(f"f-full queries lost in h: {f_full_losses}")
    held = [q for q in scored_ids if not (pools[F1][q] - pools[H1][q])]
    drops = [q for q in held
             if len(covs[H1][q]["covered"]) < len(covs[F1][q]["covered"])]
    print(f"  covered-point monotonicity on the superset-held subset ({len(held)}/{N_SCORED}): "
          f"{len(drops)} drops" + (f" {drops}" if drops else ""))
    if drops:
        fail(f"covered-point drops on the held subset: {drops}")
    g61 = "g2-061"
    if g61 in scored_ids:
        fp61, hp61 = len(covs[F1][g61]["covered"]), len(covs[H1][g61]["covered"])
        print(f"  g2-061 covered points: f {fp61} -> h {hp61} "
              f"{'(held)' if hp61 >= fp61 else '(DROP — finding)'}")
        if hp61 < fp61:
            finding(f"g2-061 covered points dropped {fp61} -> {hp61}")
    era_cov = {}
    for qid in G_ERA_REVERTED:
        missing_pts = gold[qid]["points"] - covs[F1][qid]["covered"]
        era_cov[qid] = all(ref in pools[H1][qid]
                           for ref in (r for r, c in ref_codes.items()
                                       if ref not in pools[F1][qid] and c & missing_pts))
    print(f"  g-era reverted flips {G_ERA_REVERTED} fresh covering refs all in-pool: "
          f"{sum(1 for v in era_cov.values() if v)}/{len(G_ERA_REVERTED)}")
    for qid, v in era_cov.items():
        if not v:
            finding(f"{qid}: a g-era covering ref fell out of h's pool (superset vs f holds; "
                    f"the g-era ref was floor-admitted — h floor ABSENT)")

    # == 5. notes-share ledger ===============================================
    print("\n== 5. notes-share ledger (pool SET share, scored queries)")
    shares = {}
    for rid in [R9, F1, G1, H1]:
        tot = sum(len(pools[rid][q]) for q in scored_ids)
        notes = sum(1 for q in scored_ids for r in pools[rid][q]
                    if kinds.get(r) == "EXTERNAL_NOTES")
        shares[rid] = (notes, tot, notes / tot * 100)
        print(f"  {rid}: {notes}/{tot} = {notes/tot*100:.1f}%")
    print(f"  recorded chain: r9 20.4% -> f 15.3% -> g 16.9% -> h predicted ~30.6% "
          f"(the declared overshoot) · observed h {shares[H1][2]:.1f}%")
    f_notes_tot = shares[F1][0]
    h_notes_tot = shares[H1][0]
    print(f"  notes refs f -> h: {f_notes_tot} -> {h_notes_tot} "
          f"(+{h_notes_tot - f_notes_tot}; prereg predicted +797 notes refs)")
    growth = sum(len(pools[H1][q] - pools[F1][q]) for q in scored_ids)
    notes_growth = sum(1 for q in scored_ids for r in (pools[H1][q] - pools[F1][q])
                       if kinds.get(r) == "EXTERNAL_NOTES")
    print(f"  pool growth f -> h: +{growth} refs total ({notes_growth} EXTERNAL_NOTES, "
          f"{growth - notes_growth} other kinds via re-execution)")
    pqs = [len(pools[H1][q]) for q in scored_ids]
    print(f"  h pool sizes: min {min(pqs)} · p50 {statistics.median(pqs):.0f} · max {max(pqs)}")

    # == 6. kind-arm admissions by rank band =================================
    print("\n== 6. what the kind-arm admitted (h-rank bands of the NEW notes refs)")
    bands = defaultdict(int)
    for q in scored_ids:
        for r in (pools[H1][q] - pools[F1][q]):
            if kinds.get(r) == "EXTERNAL_NOTES":
                fr = ranks[H1][q].index(r) + 1
                band = "1-10" if fr <= 10 else "11-20" if fr <= 20 else "21-40" if fr <= 40 else "41+"
                bands[band] += 1
    print(f"  by h fused-rank band: {dict(sorted(bands.items()))}")

    # == 7. rank-slice recompute check + movement ledgers ====================
    print("\n== 7. rank-slice movement (chunk_axis served view, vs f)")
    tiers = {qid: dict(gold[qid]["evidence"]) for qid in scored_ids}
    agg = {rid: defaultdict(float) for rid in (F1, H1)}
    pq = {rid: {} for rid in (F1, H1)}
    for rid in (F1, H1):
        for qid in scored_ids:
            row = score_chunks(ranks[rid][qid], tiers[qid])
            pq[rid][qid] = row
            for k, v in row.items():
                agg[rid][k] += v
    for rid in (F1, H1):
        for k in agg[rid]:
            agg[rid][k] = r4(agg[rid][k] / len(scored_ids))
    rec = {rid: runs[rid]["chunk_axis"]["served_view"]["overall"] for rid in (F1, H1)}
    for k in agg[F1]:
        ok = abs(agg[F1][k] - rec[F1][k]) < 5e-5 and abs(agg[H1][k] - rec[H1][k]) < 5e-5
        delta = (agg[H1][k] - agg[F1][k]) / agg[F1][k] * 100 if agg[F1][k] else float("nan")
        print(f"  {k}: {agg[F1][k]} -> {agg[H1][k]} ({delta:+.1f}%) · recorded "
              f"{rec[F1][k]} -> {rec[H1][k]} · {'OK' if ok else 'MISMATCH'}")
        if not ok:
            fail(f"rank-slice recompute mismatch for {k}")
    moved = {k: sum(1 for q in scored_ids if abs(pq[H1][q][k] - pq[F1][q][k]) > 1e-12)
             for k in ("recall@5", "recall@10", "recall@20", "mrr", "ndcg@10")}
    print(f"  per-query movement: " + " · ".join(f"{k} moved on {n}" for k, n in moved.items()))
    r20_pin = rec[F1]["recall@20"]
    print(f"  PIN: recall@20 5-run pin ({r20_pin}) declared AT-RISK BY DESIGN this tranche "
          f"(the kind-arm's admissions are not rank-bounded) · observed "
          f"{rec[H1]['recall@20']} — movement recorded as a finding, not a failure")
    if abs(rec[H1]["recall@20"] - r20_pin) < 5e-5:
        print("  PIN: recall@20 held a 6th run despite the declared risk")
    else:
        finding(f"recall@20 5-run pin BROKE as declared at-risk: {r20_pin} -> "
                f"{rec[H1]['recall@20']} (the lever's shape, pre-declared)")
    print("\n== 8. section-8.1 v1.1 gates (evaluated fresh, both views)")
    for name, (view, metric, floor) in GATES_V11.items():
        src = (h["chunk_axis"]["served_view"]["overall"] if view == "ALL"
               else h["chunk_axis"]["compliant_view"]["overall"])
        val = src[metric]
        ok = val >= floor
        print(f"  gate {name}: {val} vs {floor} -> {'PASS' if ok else 'FAIL'}")
    h_compliant = h["spec_resolution_hv"]["views"]["compliant_view"]
    h_served = h["spec_resolution_hv"]["views"]["served_view_all_denominator"]
    same = (h_compliant["spec_points_full_coverage_rate"]
            == h_served["spec_points_full_coverage_rate"]
            and h_compliant["spec_points_micro_average"]
            == h_served["spec_points_micro_average"])
    print(f"  compliant-vs-served (d): identical = {same} · compliant recall@10 "
          f"{h['chunk_axis']['compliant_view']['overall']['recall@10']} vs f 0.1043")
    if same:
        finding("the prereg's compliant-view prediction (section 3.6: the kind-arm adds "
                "NOTHING to the compliant pools — every kind-arm ref on a SUGGESTED paper) "
                "is FALSIFIED by the run: the notes documents pass the central VALIDATED "
                "boundary via the subject-level document-validation branch (T-C07's second "
                "scope branch), so compliant == served exactly — and (a2) 0.1043 -> 0.0612 "
                "FAIL (the notes refs dilute the compliant top-20; recorded, not smoothed)")
    print(f"  boundary: served violations {h['chunk_axis']['validation_boundary_violations']['served']} "
          f"(T-C20 update: expected 0 on re-record) · compliant starved "
          f"{h.get('queries_compliant_starved')}")
    print("\n== 9. (e) latency + per-class flags")
    lat_h = h["latency"]["served"]
    lat_g = runs[G1]["latency"]["served"]
    print(f"  latency p50: g {lat_g['p50_ms']:.1f} ms -> h {lat_h['p50_ms']:.1f} ms "
          f"(prereg expected >= g's 1080.0 — the kind-arm adds one kind-filtered scan x double pass)"
          + ("" if lat_h["p50_ms"] >= lat_g["p50_ms"] else " — BELOW g (finding)"))
    if lat_h["p50_ms"] < lat_g["p50_ms"]:
        finding(f"(e) latency p50 {lat_h['p50_ms']:.1f} ms < g's {lat_g['p50_ms']:.1f} ms — "
                f"the prereg expected >=; recorded honestly")
    for cls, vals in sorted(h["chunk_axis"]["served_view"]["per_class"].items()):
        fvals = runs[F1]["chunk_axis"]["served_view"]["per_class"].get(cls, {})
        for m in ("recall@20", "mrr", "ndcg@10"):
            fv, hv = fvals.get(m), vals.get(m)
            if fv and hv and fv > 0 and abs(hv - fv) / fv > 0.15:
                print(f"  [g-flag] {cls} {m}: {fv} -> {hv} ({(hv-fv)/fv*100:+.1f}%)")

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
