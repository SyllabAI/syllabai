#!/usr/bin/env python3
"""validation_worklist.py — T-C40 ①: the corpus-validation throughput worklist.

The 2026-10-01 RAG engine review (R1/R3) measured the binding constraint: 965 of
4,343 chunks are VALIDATED (~22%) and the gold classes with 0.00 recall
(mark_scheme, misconception, multi_spec_point) are exactly where VALIDATED
supply is thinnest. Validation throughput is the only path that moves recall@10
materially — but content validation is OPERATOR-GATED (AGENT.md core rule 6:
no ingestion or repair tooling may auto-validate; the S8D handoff §6: "no agent
may assert the validation"). This tool therefore does NOT flip anything: it
converts the frozen snapshot into a PRIORITIZED WORKLIST so each operator
validation batch buys the most retrieval quality per unit of review effort.

Deterministic: no RNG, no clock-dependent sorting; every output row traces to
committed snapshot/gold bytes. Env: BENCH_SNAPSHOT, BENCH_GOLD, BENCH_OUT.
"""
import gzip, hashlib, json, os
from collections import Counter, defaultdict

SNAP = os.environ.get("BENCH_SNAPSHOT", "evidence/bench-001/snapshots/snap-006")
GOLD = os.environ.get("BENCH_GOLD", "bench/gold-v5")
OUT = os.environ.get("BENCH_OUT", "evidence/bench-001/validation-worklist-2026-10-01")
os.makedirs(OUT, exist_ok=True)

chunks = json.loads(gzip.open(f"{SNAP}/chunks.jsonl.gz").read())
recs = []
for fn in sorted(os.listdir(GOLD)):
    if fn.startswith("class_"):
        recs += json.load(open(f"{GOLD}/{fn}"))

snapshot_version = json.load(open(f"{SNAP}/manifest.json"))["snapshot_version"]

# ── identity: a batch = (document identity, kind). paper_code is the joinable
#    paper identity for QP/MS/EQ chunks; EXTERNAL_NOTES chunks fall back to the
#    content sha (the chunk_ref prefix), which is 1:1 with a note document.
def batch_key(c):
    doc = c.get("paper_code") or c["chunk_ref"].split(":")[0][:16]
    return doc, c.get("kind", "?")

by_batch = defaultdict(list)
for c in chunks:
    by_batch[batch_key(c)].append(c)

# ── gold demand: which batches carry gold evidence, at which tier, for which
#    queries/classes (tier>=1 = recall-relevant; tier==2 = MRR-relevant)
demand = defaultdict(lambda: {"q_tier1": set(), "q_tier2": set(), "classes": Counter()})
ref_to_batch = {}
for c in chunks:
    ref_to_batch[c["chunk_ref"]] = batch_key(c)
for r in recs:
    for g in r.get("gold_evidence") or []:
        b = ref_to_batch.get(g["chunk_ref"])
        if b is None:
            continue  # gold ref not in this snapshot generation (honest skip)
        if g["tier"] >= 1:
            demand[b]["q_tier1"].add(r["id"])
        if g["tier"] == 2:
            demand[b]["q_tier2"].add(r["id"])
        demand[b]["classes"][r["class"]] += 1

rows = []
for key, cs in by_batch.items():
    states = Counter(c["paper_state"] for c in cs)
    d = demand.get(key, {"q_tier1": set(), "q_tier2": set(), "classes": Counter()})
    rows.append({
        "batch": key[0], "kind": key[1],
        "chunks_total": len(cs),
        "VALIDATED": states.get("VALIDATED", 0),
        "SUGGESTED": states.get("SUGGESTED", 0),
        "gold_queries_tier1": len(d["q_tier1"]),
        "gold_queries_tier2": len(d["q_tier2"]),
        "gold_classes": dict(sorted(d["classes"].items())),
        "spec_codes_covered": len({code for c in cs for code in (c.get("spec_codes") or [])}),
    })

# priority: batch is actionable only if it still has SUGGESTED chunks;
# order by gold tier2 unlocks, then tier1, then class diversity, then batch id
def sort_key(r):
    actionable = r["SUGGESTED"] > 0
    return (0 if actionable else 1,
            -r["gold_queries_tier2"], -r["gold_queries_tier1"],
            -len(r["gold_classes"]), r["batch"], r["kind"])
rows.sort(key=sort_key)

census = {
    "chunks_total": len(chunks),
    "VALIDATED": sum(1 for c in chunks if c["paper_state"] == "VALIDATED"),
    "SUGGESTED": sum(1 for c in chunks if c["paper_state"] == "SUGGESTED"),
    "by_kind": dict(Counter(c["kind"] for c in chunks)),
    "suggested_by_kind": dict(Counter(c["kind"] for c in chunks if c["paper_state"] == "SUGGESTED")),
    "batches_total": len(by_batch),
    "batches_fully_validated": sum(1 for r in rows if r["SUGGESTED"] == 0),
}
# zero-recall classes at run-005-c-r7 (review R1) — where does their gold live?
zero_recall_classes = ["mark_scheme", "misconception", "multi_spec_point"]
ref_to_state = {c["chunk_ref"]: c["paper_state"] for c in chunks}
unlock = {}
for cls in zero_recall_classes:
    qs = [r for r in recs if r["class"] == cls and r.get("gold_evidence")]
    reachable_now, total = 0, 0
    for r in qs:
        total += 1
        states = {ref_to_state[g["chunk_ref"]]
                  for g in r["gold_evidence"]
                  if g["tier"] >= 1 and g["chunk_ref"] in ref_to_state}
        if any(s == "VALIDATED" for s in states):
            reachable_now += 1
    unlock[cls] = {"queries": total, "gold_reachable_from_VALIDATED_supply": reachable_now,
                   "gold_locked_behind_SUGGESTED": total - reachable_now}

worklist = {
    "tool": "bench/validation_worklist.py",
    "task": "T-C40 ①",
    "date": "2026-10-01",
    "snapshot": snapshot_version,
    "gold": json.load(open(f"{GOLD}/manifest.json")).get("set_version", "gold-v5"),
    "census": census,
    "zero_recall_class_unlock_analysis": unlock,
    "note": ("Operator-gated validation worklist: rows are PRIORITIES, not authorizations. "
             "Content flips happen only through the teacher validation surface "
             "(ContentReviewServiceV3 / validate-all), never by agent assertion "
             "(AGENT.md core rule 6). Batches already fully VALIDATED are listed "
             "last for completeness only."),
    "rows": rows,
}
open(f"{OUT}/worklist.json", "w").write(json.dumps(worklist, indent=1, sort_keys=True))

md = f"""# Corpus validation worklist — {snapshot_version} × {worklist['gold']} (T-C40 ①, 2026-10-01)

**Status:** RECORDED — deterministic, offline, generated from the committed snapshot/gold bytes (no DB, no keys).
**Purpose:** the review's order item 1 ("validate corpus") as an actionable instrument. It does NOT validate anything:
content flips stay operator-gated (AGENT.md core rule 6; S8D §6 "no agent may assert the validation").

## Census

- Chunks: **{census['VALIDATED']}/{census['chunks_total']} VALIDATED ({100*census['VALIDATED']/census['chunks_total']:.1f}%)**, {census['SUGGESTED']} SUGGESTED
- SUGGESTED by kind: {json.dumps(census['suggested_by_kind'], sort_keys=True)}
- Batches (document × kind): {census['batches_total']} total, {census['batches_fully_validated']} already fully VALIDATED

## Where the zero-recall gold classes are locked

Run-005-c-r7 measured recall@10 = 0.00 on mark_scheme, misconception, multi_spec_point. This worklist shows why:

| class | gold queries | reachable from today's VALIDATED supply | locked behind SUGGESTED |
|---|---:|---:|---:|
""" + "\n".join(
    f"| {k} | {v['queries']} | {v['gold_reachable_from_VALIDATED_supply']} | {v['gold_locked_behind_SUGGESTED']} |\n"
    for k, v in unlock.items()) + f"""
## Priority rows (top 15 of {len(rows)})

| batch | kind | chunks | SUGGESTED | tier1 unlocks | tier2 unlocks | gold classes |
|---|---|---:|---:|---:|---:|---|
""" + "\n".join(
    f"| {r['batch']} | {r['kind']} | {r['chunks_total']} | {r['SUGGESTED']} | "
    f"{r['gold_queries_tier1']} | {r['gold_queries_tier2']} | {', '.join(sorted(r['gold_classes'])) or '—'} |\n"
    for r in rows[:15]) + """
## Reading

- Priority = (tier2 unlocks, tier1 unlocks, class diversity) — validating a top batch makes gold
  evidence REACHABLE by the serving gate, which is the precondition for any recall movement the
  next §8.1-governed run can even measure.
- The full ordered list is in `worklist.json` (`rows`), every row traceable to snapshot bytes.
- Expected effect, honestly bounded: validation moves the REACHABLE pool; it does not by itself
  move vector quality (embeddings already exist for the rev corpus). The §8.1 VALIDATED bars
  (0.0734/0.1184/0.1683) are the first bars a validated-corpus generation can legitimately clear.
"""
open(f"{OUT}/REPORT.md", "w").write(md)
with open(f"{OUT}/SHA256SUMS", "w") as f:
    for fn in ("worklist.json", "REPORT.md"):
        h = hashlib.sha256(open(f"{OUT}/{fn}", "rb").read()).hexdigest()
        f.write(f"{h}  {fn}\n")
print(f"worklist recorded: {len(rows)} batches; top:")
for r in rows[:8]:
    print(f"  {r['batch']} {r['kind']}: SUGGESTED={r['SUGGESTED']} tier1={r['gold_queries_tier1']} tier2={r['gold_queries_tier2']} classes={sorted(r['gold_classes'])}")
