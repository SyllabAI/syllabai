#!/usr/bin/env python3
"""T-C77 prereg grounding — all from recorded bytes + the frozen preload-r9
artifact (no run, no bench execution, no tuning). The rank-bounded
kind-admission tranche, TWO-ARM HORIZON PARTITION form.

Grounding chain:
1. (d) recompute self-checks on f/g/h — byte-exact against the recorded
   verdicts (the machinery check).
2. Fresh-notes attribution from the recorded pools: pool(h) \\ pool(f) by
   snapshot kind — expected +797 EXTERNAL_NOTES / +4 re-execution refs;
   the h fused-rank band census of the fresh notes — expected
   124 / 346 / 325 / 2 (the displacement the tranche bounds).
3. KIND-ARM RECONSTRUCTION from the frozen preload (SHA-verified against the
   recorded echo): per query, the top-15 EXTERNAL_NOTES chunks by exact
   cosine — the production kind-arm's input as the census modelled it.
   BYTE-LEVEL CROSS-VALIDATION against the recorded h/f scores: for every
   f-pool ref, h_score - f_score must be exactly 0 (not kind-arm-listed) or
   exactly 1/(60+r) for its reconstructed kind-arm rank r (listed); for
   every fresh kind-arm-only ref, h_score must equal its 1/(60+r)
   contribution alone. This proves the two premises the design rests on:
   (a) the kind-arm's ONLY effect on existing refs' scores is the additive
   1/(60+r) kind-arm term, and (b) the two-arm (paper+existing) score
   surface is byte-identical between the f execution and the h execution.
4. THE PARTITION SIMULATION — the tranche's design grounding: the
   rank-bounded served order = [h-pool refs WITH a two-arm score, sorted by
   that two-arm score (h_score minus the kind-arm contribution), ref ASC
   tiebreak] ++ [the kind-arm-only admissions (the fresh notes), sorted by
   kind-arm rank, ref ASC tiebreak]. The kind-arm admits to the SET; the
   served RANK surface is the two-arm surface; kind-arm-only mass serves
   below it. Recomputed: the six slices vs f's recorded values (the
   pre-kind-arm reference) and g's (the floor band); per-query top-20
   identity vs f; the simulated SET == h's SET; (d) == h byte-exact;
   the demotion ledger (0 kind-arm-only refs inside the simulated top-20;
   min two-arm prefix length vs the 20 horizon).
This is grounding on recorded bytes, NOT a bench execution — the run remains
the test of the production path's fidelity (the T-C72 census honesty rule).
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
G1 = "run-005-g-r1"
H1 = "run-005-h-r1"
RECORDED_D = {F1: (0.5056, 0.8571), G1: (0.5169, 0.8690), H1: (0.5843, 0.9405)}
N_SCORED, N_POINTS = 89, 84
K_KIND_ARM = 15
RRF_K = 60
F_SLICES = {"recall@5": 0.0616, "recall@10": 0.1043, "recall@20": 0.1612,
            "mrr": 0.0626, "ndcg@10": 0.1057, "evidence_precision@10": 0.0303}
G_SLICES = {"recall@5": 0.0616, "recall@10": 0.1043, "recall@20": 0.1612,
            "mrr": 0.07, "ndcg@10": 0.1095, "evidence_precision@10": 0.0303}
H_BANDS_RECORDED = {"1-10": 124, "11-20": 346, "21-40": 325, "41+": 2}
FRESH_NOTES_RECORDED, FRESH_OTHER_RECORDED = 797, 4
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


def load_kinds():
    return {r["chunk_ref"]: r.get("kind", "?") for r in json.load(gzip.open(SNAP7))}


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
    kinds = load_kinds()
    runs = {rid: json.loads((RUNS / rid / "results.json").read_text())
            for rid in [F1, G1, H1]}
    h = runs[H1]

    print("# T-C77 prereg grounding — recorded bytes + frozen preload (no run, no tuning)")
    fb = h["fabric"]
    print(f"# h posture: providers {fb['providers']} | per_arm_limit "
          f"{fb['per_arm_limit']} | notes_kind_arm {fb['notes_kind_arm']}")
    if fb["providers"] != ["pgvector", "bm25", "notes-kind-arm"]:
        fail(f"h providers {fb['providers']} != the kind-arm posture")
    if h["code_version"] != "c346d645d119708bcf0f5d9cac2ae15131654970":
        fail(f"code_version {h['code_version']} != merged main c346d64")

    scored_ids = sorted(h["per_query_chunks"].keys())
    if len(scored_ids) != N_SCORED:
        fail(f"scored {len(scored_ids)} != {N_SCORED}")
    pools = {rid: {qid: set(e["ranked_refs"]) for qid, e in run["per_query_chunks"].items()}
             for rid, run in runs.items()}
    ranks = {rid: {qid: list(e["ranked_refs"]) for qid, e in run["per_query_chunks"].items()}
             for rid, run in runs.items()}
    scores = {rid: {qid: dict(zip(e["ranked_refs"], e["fused_scores"]))
                    for qid, e in run["per_query_chunks"].items()}
              for rid, run in runs.items()}

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
    for rid in [F1, G1, H1]:
        c = coverage(pools[rid])
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

    # == 2. fresh attribution + band census ==================================
    print("\n== 2. fresh attribution pool(h)\\\\pool(f) by kind + h band census")
    fresh_notes_by_qid, fresh_other_by_qid = {}, {}
    for qid in scored_ids:
        delta = pools[H1][qid] - pools[F1][qid]
        fresh_notes_by_qid[qid] = {r for r in delta if kinds.get(r) == "EXTERNAL_NOTES"}
        fresh_other_by_qid[qid] = delta - fresh_notes_by_qid[qid]
    sum_notes = sum(len(v) for v in fresh_notes_by_qid.values())
    sum_other = sum(len(v) for v in fresh_other_by_qid.values())
    print(f"  fresh notes {sum_notes} (recorded {FRESH_NOTES_RECORDED}) · "
          f"fresh non-notes {sum_other} (recorded {FRESH_OTHER_RECORDED}) · "
          f"queries with >=1 fresh note: {sum(1 for q in scored_ids if fresh_notes_by_qid[q])}")
    if sum_notes != FRESH_NOTES_RECORDED:
        fail(f"fresh notes {sum_notes} != recorded {FRESH_NOTES_RECORDED}")
    if sum_other != FRESH_OTHER_RECORDED:
        fail(f"fresh non-notes {sum_other} != recorded {FRESH_OTHER_RECORDED}")
    bands = defaultdict(int)
    for qid in scored_ids:
        pos = {ref: i + 1 for i, ref in enumerate(ranks[H1][qid])}
        for ref in fresh_notes_by_qid[qid]:
            r = pos.get(ref)
            if r is None:
                fail(f"fresh note absent from h ranked_refs: {qid} {ref[:12]}")
                continue
            band = "1-10" if r <= 10 else "11-20" if r <= 20 else "21-40" if r <= 40 else "41+"
            bands[band] += 1
    got = {b: bands.get(b, 0) for b in ["1-10", "11-20", "21-40", "41+"]}
    print(f"  bands {got} (recorded {H_BANDS_RECORDED})")
    if got != H_BANDS_RECORDED:
        fail(f"band census {got} != recorded {H_BANDS_RECORDED}")

    # == 3. kind-arm reconstruction + byte-level cross-validation ============
    print("\n== 3. kind-arm top-15 reconstruction from the frozen preload (exact cosine)")
    chunks, queries = load_embeddings()
    notes_universe = sorted(ref for ref, k in kinds.items() if k == "EXTERNAL_NOTES")
    print(f"  notes universe: {len(notes_universe)} (the recorded 350)")
    if len(notes_universe) != 350:
        fail(f"notes universe {len(notes_universe)} != 350")
    note_mat = np.stack([chunks[r] for r in notes_universe])
    note_norms = np.linalg.norm(note_mat, axis=1)

    def kind_arm_top15(qid):
        qv = queries[qid]
        qn = np.linalg.norm(qv)
        cos = (note_mat @ qv) / np.maximum(note_norms * qn, 1e-12)
        order = sorted(range(len(notes_universe)), key=lambda i: (-cos[i], notes_universe[i]))
        return [notes_universe[i] for i in order[:K_KIND_ARM]]

    ka_rank = {qid: {ref: i + 1 for i, ref in enumerate(kind_arm_top15(qid))}
               for qid in scored_ids}

    print("  byte-level cross-validation of h scores against reconstruction:")
    n_checked_two_arm = n_ok_two_arm = 0
    n_checked_fresh = n_ok_fresh = 0
    contrib_mismatches = []
    for qid in scored_ids:
        kr = ka_rank[qid]
        for ref, hs in scores[H1][qid].items():
            if ref in pools[F1][qid]:
                fs = scores[F1][qid].get(ref)
                if fs is None:
                    continue  # f-pool membership by SET; score row absent only if drift
                delta = hs - fs
                if abs(delta) < TOL:
                    n_checked_two_arm += 1
                    if ref in kr:
                        contrib_mismatches.append((qid, ref, "kind-listed but no contribution"))
                    else:
                        n_ok_two_arm += 1
                elif delta > 0 and ref in kr:
                    n_checked_two_arm += 1
                    if abs(delta - 1.0 / (RRF_K + kr[ref])) < TOL:
                        n_ok_two_arm += 1
                    else:
                        contrib_mismatches.append(
                            (qid, ref, f"delta {delta:.9f} != 1/(60+{kr[ref]}) "
                             f"{1.0/(RRF_K + kr[ref]):.9f}"))
                else:
                    contrib_mismatches.append((qid, ref, f"unexpected delta {delta:.9f}"))
            elif ref in kr and kinds.get(ref) == "EXTERNAL_NOTES":
                n_checked_fresh += 1
                if abs(hs - 1.0 / (RRF_K + kr[ref])) < TOL:
                    n_ok_fresh += 1
                else:
                    contrib_mismatches.append(
                        (qid, ref, f"fresh contribution {hs:.9f} != "
                         f"1/(60+{kr[ref]}) {1.0/(RRF_K + kr[ref]):.9f}"))
    print(f"    two-arm-surface refs (in f pool): {n_ok_two_arm}/{n_checked_two_arm} "
          f"byte-exact under the additive-contribution model")
    print(f"    fresh kind-arm-only refs: {n_ok_fresh}/{n_checked_fresh} "
          f"score == their 1/(60+r) contribution alone")
    for qid, ref, why in contrib_mismatches[:10]:
        finding(f"contribution mismatch {qid} {ref[:12]}: {why}")
    if len(contrib_mismatches) > 10:
        finding(f"... {len(contrib_mismatches) - 10} further contribution mismatches")
    if n_ok_two_arm != n_checked_two_arm or n_checked_two_arm == 0:
        fail(f"two-arm score-identity premise broken: {n_ok_two_arm}/{n_checked_two_arm}")
    if n_checked_fresh and n_ok_fresh != n_checked_fresh:
        fail(f"fresh contribution model broken: {n_ok_fresh}/{n_checked_fresh}")
    reach_ok = all(len(v) == K_KIND_ARM for v in ka_rank.values())
    print(f"    reconstruction reach: 15/15 notes per query on all "
          f"{N_SCORED} queries: {'OK' if reach_ok else 'FAIL'}")
    if not reach_ok:
        fail("kind-arm reconstruction under-filled")

    # == 4. THE TWO-ARM HORIZON PARTITION SIMULATION =========================
    print("\n== 4. partition simulation: [two-arm surface by two-arm score] ++ [kind-arm-only mass]")
    per_query_scores, sim_lists = {}, {}
    top20_set_same = top20_order_same = 0
    min_two_arm_prefix = 10 ** 9
    ka_only_in_top20 = 0
    for qid in scored_ids:
        kr = ka_rank[qid]
        fresh = fresh_notes_by_qid[qid]
        two_arm = {}
        for ref, hs in scores[H1][qid].items():
            contrib = 1.0 / (RRF_K + kr[ref]) if ref in kr else 0.0
            base = hs - contrib
            two_arm[ref] = base
        # two-arm-surface refs: anything with a nonzero two-arm score (arm A/B
        # ranked it) — the fresh kind-arm-only refs have base == 0 and are
        # excluded from the prefix by construction
        prefix = sorted((ref for ref, s in two_arm.items() if s > TOL),
                        key=lambda ref: (-two_arm[ref], ref))
        tail = sorted(fresh & set(kr), key=lambda ref: (kr[ref], ref))
        sim_list = prefix + tail
        min_two_arm_prefix = min(min_two_arm_prefix, len(prefix))
        ka_only_in_top20 += sum(1 for r in sim_list[:20] if r in fresh)
        sim_lists[qid] = sim_list
        if set(sim_list) != pools[H1][qid]:
            fail(f"simulated SET != h SET (partition must be set-preserving): {qid}")
        tier_by_ref = {ref: tier for ref, tier in gold[qid]["evidence"]}
        per_query_scores[qid] = score_chunks(sim_list, tier_by_ref)
        f_top20 = ranks[F1][qid][:20]
        if set(sim_list[:20]) == set(f_top20):
            top20_set_same += 1
            if sim_list[:20] == f_top20:
                top20_order_same += 1
    print(f"  simulated SET == h SET on all queries (the set-preservation check)")
    print(f"  min two-arm prefix length: {min_two_arm_prefix} (vs the 20 horizon)")
    print(f"  kind-arm-only refs inside simulated top-20: {ka_only_in_top20} (predicted 0)")
    if ka_only_in_top20 != 0:
        fail(f"{ka_only_in_top20} kind-arm-only refs remain inside the simulated top-20")
    print(f"  simulated top-20 vs f's recorded top-20: set-identical "
          f"{top20_set_same}/{N_SCORED} · order-identical {top20_order_same}/{N_SCORED} "
          f"(diffs = the declared re-execution band, g2-024 precedent)")
    if top20_set_same != N_SCORED:
        finding(f"top-20 set-identity {top20_set_same}/{N_SCORED} — the re-execution "
                f"band, recorded as the prereg's declared tolerance")

    sim_slices = agg(scored_ids, per_query_scores)
    print("  simulated slices vs f (recorded) and g (band):")
    for k in ["recall@5", "recall@10", "recall@20", "mrr", "ndcg@10",
              "evidence_precision@10"]:
        mark = "EXACT" if sim_slices[k] == F_SLICES[k] else "BAND"
        print(f"    {k}: simulated {sim_slices[k]} · f {F_SLICES[k]} · g {G_SLICES[k]} · {mark}")
        if k.startswith("recall") and sim_slices[k] != F_SLICES[k]:
            fail(f"{k}: simulated {sim_slices[k]} != f's recorded {F_SLICES[k]}")

    sim_cov = coverage({qid: set(sim_lists[qid]) for qid in scored_ids})
    full = sum(1 for qid in scored_ids if sim_cov[qid]["full"])
    micro = sum(len(sim_cov[qid]["covered"]) for qid in scored_ids)
    hf, hm = d_values[H1]
    ok = full == hf and micro == hm
    print(f"  simulated (d): full {full}/{N_SCORED} · micro {micro}/{N_POINTS} — "
          f"h recomputed {hf}/{hm} · {'BYTE-EXACT (set-preservation theorem shape)' if ok else 'MISMATCH'}")
    if not ok:
        fail("simulated (d) != h's (d) — the partition must be set-preserving")
    tail_total = sum(len(sim_lists[qid]) - min(len(sim_lists[qid]),
                     len([r for r in sim_lists[qid] if r not in fresh_notes_by_qid[qid]]))
                     for qid in scored_ids)
    print(f"  demotion ledger: kind-arm-only refs demoted below the two-arm surface: "
          f"{sum(len(fresh_notes_by_qid[qid] & set(ka_rank[qid])) for qid in scored_ids)} "
          f"(the fresh admission mass; predicted {FRESH_NOTES_RECORDED})")

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
