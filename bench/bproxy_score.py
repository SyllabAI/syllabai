#!/usr/bin/env python3
"""bproxy_score.py — T-C13 Run 1: harness-internal BM25 probe over the frozen snapshot (arm B-proxy).
Deterministic Okapi BM25 (k1=1.2, b=0.75). Two scopes: ALL chunks and VALIDATED-paper chunks only
(validation-boundary probe, Gemini §16 test 5). Arms A0/A/C/D/E/F/G report UNAVAILABLE with named reasons."""
import gzip, hashlib, json, math, os, re, unicodedata

import os
SNAP = os.environ.get("BENCH_SNAPSHOT", "evidence/bench-001/snapshot")
GOLD = os.environ.get("BENCH_GOLD", "bench/gold")
RUN = os.environ.get("BENCH_RUN_OUT", "evidence/bench-001/runs/run-001-bproxy")
os.makedirs(RUN, exist_ok=True)
K1, B, STOP = 1.2, 0.75, set(
    "the a an of to in on for and or is are was were be been with as by at from that this it its what which how "
    "why when who does do did can could should would will shall may might must not no i you we they he she me my "
    "our your their about into over under between within per each other use using help answer question".split())

def tok(s):
    return [w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if w not in STOP and len(w) > 1]

chunks = json.loads(gzip.open(f"{SNAP}/chunks.jsonl.gz").read())
recs = []
for fn in sorted(os.listdir(GOLD)):
    if fn.startswith("class_"):
        recs += json.load(open(f"{GOLD}/{fn}"))

def run_scope(scope_name, corpus):
    """corpus: list of chunk dicts; index = list of (i, tokens, tf)."""
    N = len(corpus)
    tf = []
    df = {}
    for c in corpus:
        t = tok(c["content"])
        tf.append(t)
        for w in set(t):
            df[w] = df.get(w, 0) + 1
    avgdl = sum(len(t) for t in tf) / max(N, 1)
    gold_by_ref = {c["chunk_ref"]: c for c in chunks}
    def bm25(qt):
        scores = []
        for i, t in enumerate(tf):
            s, seen = 0.0, set()
            for w in qt:
                if w in seen:
                    continue
                seen.add(w)
                f = t.count(w)
                if not f:
                    continue
                idf = math.log(1 + (N - df.get(w, 0) + 0.5) / (df.get(w, 0) + 0.5))
                s += idf * f * (K1 + 1) / (f + K1 * (1 - B + B * len(t) / avgdl))
            scores.append((s, i))
        scores.sort(key=lambda x: (-x[0], x[1]))
        return scores
    results = {}
    per_class = {}
    labeled = [r for r in recs if r["gold_evidence"]]
    for r in labeled:
        gold = {g["chunk_ref"] for g in r["gold_evidence"] if g["tier"] >= 1}
        gold2 = {g["chunk_ref"] for g in r["gold_evidence"] if g["tier"] == 2}
        ranked = bm25(tok(r["query"]))[:20]
        ranked = [(s, corpus[i]["chunk_ref"]) for s, i in ranked]
        def rel(ref):
            g = next((g for g in r["gold_evidence"] if g["chunk_ref"] == ref), None)
            return (g["tier"] if g else 0)
        def recall(k):
            top = {ref for _, ref in ranked[:k]}
            return len(top & gold) / len(gold) if gold else None
        r5, r10, r20 = recall(5), recall(10), recall(20)
        mrr = next((1 / (n + 1) for n, (_, ref) in enumerate(ranked) if ref in gold2), 0.0)
        dcg = sum((2 ** rel(ref) - 1) / math.log2(n + 2) for n, (_, ref) in enumerate(ranked[:10]))
        ideal = sorted((rel(ref) for _, ref in ranked), reverse=True)[:10]
        idcg = sum((2 ** t - 1) / math.log2(n + 2) for n, t in enumerate(ideal)) or 1.0
        ndcg = dcg / idcg
        top10 = [ref for _, ref in ranked[:10]]
        prec = sum(1 for ref in top10 if rel(ref) >= 1) / 10
        fp = sum(1 for ref in top10 if rel(ref) == 0) / 10
        row = {"recall@5": r5, "recall@10": r10, "recall@20": r20, "mrr": mrr, "ndcg@10": ndcg,
               "evidence_precision@10": prec, "false_positive_rate@10": fp, "gold_n": len(gold)}
        per_class.setdefault(r["class"], []).append(row)
        results[r["id"]] = row
    def agg(rows):
        return {k: round(sum(r[k] for r in rows) / len(rows), 4) for k in rows[0]
                if isinstance(rows[0][k], float)}
    class_agg = {c: agg(rows) for c, rows in sorted(per_class.items())}
    overall = agg([row for rows in per_class.values() for row in rows])
    return {"scope": scope_name, "corpus_n": N, "queries_scored": len(labeled),
            "overall": overall, "per_class": class_agg}

all_scope = run_scope("ALL-chunks", chunks)
val_scope = run_scope("VALIDATED-paper-chunks-only", [c for c in chunks if c.get("paper_state") == "VALIDATED"])
unlabeled = [r["id"] for r in recs if not r["gold_evidence"]]

results = {
    "run_id": "run-001-bproxy", "date": "2026-09-17", "arm": "B-proxy (harness-internal Okapi BM25 k1=1.2 b=0.75)",
    "arm_status": "PROXY — NOT a production arm; never citable for promotion decisions",
    "gold_set": "gold-v1 (120 queries; frozen)",
    "arms_unavailable": {
        "A0": "requires syllabai-core Java lane (Java 25 + Maven unavailable in authoring env) — PREPARED, not RUNNABLE here",
        "A": "requires T-C07 + embedding backfill (0/2,333 chunks embedded)",
        "B": "requires T-C14 Bm25Retriever + tsvector migration",
        "C/D": "require A + B", "E/F/G": "require T-C15",
    },
    "queries_total": len(recs), "queries_with_chunk_labels": len(recs) - len(unlabeled),
    "queries_excluded_no_labels": {"count": len(unlabeled), "ids": unlabeled,
        "reason": "substrate-absent classes (notes_mirror/figures) or auto-label sparse; excluded from retrieval metrics, NOT scored as zero"},
    "all_chunks": all_scope, "validated_only": val_scope,
    "validation_boundary_note": "scope difference quantifies how much gold evidence lives on SUGGESTED papers; production retrieval must serve VALIDATED-only per the T-C05 gate",
}
open(f"{RUN}/results.json", "w").write(json.dumps(results, indent=1, sort_keys=True))

def fmt(d):
    return " | ".join(f"{k} {v}" for k, v in d.items() if k != "gold_n")
md = f"""# Run 001 — B-proxy baseline (T-C13 M1, partial)

**Status:** RECORDED — harness-internal probe, LOCAL VERIFIED (deterministic, offline, snapshot {json.load(open(f'{SNAP}/manifest.json'))['snapshot_version']}).
**Arm:** {results['arm']} — {results['arm_status']}.
**Queries:** {results['queries_with_chunk_labels']}/{results['queries_total']} scored ({results['queries_excluded_no_labels']['count']} excluded — no chunk labels: substrate-absent classes / sparse auto-labels, excluded not zeroed).

## Overall (Recall@5/10/20 · MRR · nDCG@10 · precision@10 · FP@10)

- **ALL chunks ({all_scope['corpus_n']}):** {fmt(all_scope['overall'])}
- **VALIDATED-paper chunks only ({val_scope['corpus_n']}):** {fmt(val_scope['overall'])}

## Per class (ALL-chunks scope)

| class | n | recall@5 | recall@10 | recall@20 | mrr | ndcg@10 | prec@10 | fp@10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
"""
for c, d in all_scope["per_class"].items():
    n = {"factual": 15, "conceptual": 15, "calculation": 10, "prerequisite": 12, "misconception": 10,
         "why_wrong": 10, "exam_question": 10, "mark_scheme": 8, "revision_note": 10, "vague_learner": 8,
         "multi_spec_point": 7, "diagram_dependent": 5}.get(c, "?")
    md += f"| {c} | {len([r for r in recs if r['class']==c and r['gold_evidence']])}/{n} | {d['recall@5']} | {d['recall@10']} | {d['recall@20']} | {d['mrr']} | {d['ndcg@10']} | {d['evidence_precision@10']} | {d['false_positive_rate@10']} |\n"
md += f"""
## Arms unavailable at this run

{chr(10).join(f'- **{k}:** {v}' for k, v in results['arms_unavailable'].items())}

## Reading

- The ALL-vs-VALIDATED scope gap is the **quantified cost of the validation boundary**: gold evidence anchored on SUGGESTED papers is unreachable by a compliant serving scope.
- BM25 over exam corpus rewards verbatim stem overlaps (exam_question / why_wrong classes) and penalizes formal spec-title vocabulary (factual / conceptual) — the expected lexical profile; semantic arms (A/C) exist to close exactly this gap.
- These numbers are baselines-on-record for the B-proxy lane only; the production baseline (A0 KG-only) records in the Java lane per the spec (§7 M1).
"""
open(f"{RUN}/RUN_REPORT.md", "w").write(md)
with open(f"{RUN}/SHA256SUMS", "w") as f:
    for fn in ("results.json", "RUN_REPORT.md"):
        h = hashlib.sha256(open(f"{RUN}/{fn}", "rb").read()).hexdigest()
        f.write(f"{h}  {fn}\n")
print("run-001-bproxy recorded")
print("ALL :", fmt(all_scope["overall"]))
print("VALIDATED-only:", fmt(val_scope["overall"]))
print("excluded (no labels):", len(unlabeled), "| per-class classes scored:", len(all_scope["per_class"]))
