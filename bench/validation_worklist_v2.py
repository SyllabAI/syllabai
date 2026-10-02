#!/usr/bin/env python3
"""validation_worklist_v2.py — T-C41 ②: the WAVE-2 validation worklist.

Wave-1 (T-C40/T-C41, 2026-10-01) composed from the snap-006 worklist on the
QP/MS paper axis. The wave-1 PRODUCTION run proved that axis stale in
production (F-PROD-3): every paper-axis unit was already validated, and the
live SUGGESTED mass lives on the SUBJECT-BRANCH surface instead. This v2
generator composes wave-2 from the LIVE census (F-PROD-3 sanctions "a FRESH
snapshot re-freeze (or live probes)"; the census manifest records the method).

The wave-2 actionable surface (probe-verified 2026-10-02, live_census_chunks):
  EXTERNAL_QUESTIONS  747 chunks / 80 docs  SUGGESTED, in ACTIVE scope
  SYLLABUS            162 chunks / 162 docs SUGGESTED, in ACTIVE scope
  QUESTION_PAPER      369 chunks / 28 docs  SUGGESTED, in ACTIVE scope —
  MARK_SCHEME         395 chunks / 27 docs  SUGGESTED   orphaned (no paper
                                                                 row, ever)
  All four blocks are owned by the SUBJECT_BRANCH serving gate
  (documents.validation_state = VALIDATED + chunk subject in the ACTIVE
  curriculum) — every actionable chunk is ONE document-state flip from
  serving. Zero ingestion repair is needed.

THE INSTRUMENT GAP (recorded, not hidden): the teacher surface has no
document-level validate endpoint (ContentController validates papers, paper
versions and mark schemes only; ContentDocumentController ingests/embeds/
searches but never flips documents.validation_state). Corpus documents are
born SUGGESTED (V29) and no code path on core main flips them. The 09-28
notes-axis promotion (112 EXTERNAL_NOTES docs, operator trace
1a0e88af08e12df5, batch records 9ea54e1) established the governed-SQL-batch
precedent; wave-2 either repeats that pattern under explicit operator
authorization or adds the missing teacher endpoint first. This tool, as
always, flips NOTHING (AGENT.md core rule 6).

Deterministic: no RNG, no clock-dependent sorting; every output row traces to
the census + gold-v5 bytes. Env: BENCH_CENSUS, BENCH_GOLD, BENCH_OUT.
"""
import gzip
import hashlib
import json
import os
from collections import Counter, defaultdict

CENSUS = os.environ.get(
    "BENCH_CENSUS",
    "evidence/bench-001/wave2-prep-2026-10-02/live_census_chunks.json.gz")
GOLD = os.environ.get("BENCH_GOLD", "bench/gold-v5")
OUT = os.environ.get("BENCH_OUT",
                     "evidence/bench-001/wave2-prep-2026-10-02")
os.makedirs(OUT, exist_ok=True)

chunks = json.load(gzip.open(CENSUS))
manifest = json.load(open(os.path.join(os.path.dirname(CENSUS),
                                       "live_census_manifest.json")))
recs = []
for fn in sorted(os.listdir(GOLD)):
    if fn.startswith("class_"):
        recs += json.load(open(f"{GOLD}/{fn}"))

# ── identity: a wave-2 batch = ONE document (the unit a document-validate
#    act flips). Paper-axis documents owned by a paper are OUT OF SCOPE for
#    wave-2 (that axis is the wave-1 kit's business); REJECTED docs are dead
#    by teacher decision and are NEVER actionable.
by_batch = defaultdict(list)
for c in chunks:
    if c["owner"] == "PAPER":
        continue  # wave-1 kit territory (currently zero SUGGESTED there anyway)
    if c["owner"] == "UNPLACEABLE":
        continue  # fail-closed: no serving path exists, nothing to unlock
    by_batch[(c["document_id"], c["kind"])].append(c)

# gold demand per batch (tier>=1 = recall-relevant; tier==2 = MRR-relevant)
demand = defaultdict(lambda: {"q_tier1": set(), "q_tier2": set(), "classes": Counter()})
ref_to_batch = {}
for c in chunks:
    ref_to_batch[c["chunk_ref"]] = (c["document_id"], c["kind"])
for r in recs:
    for g in r.get("gold_evidence") or []:
        b = ref_to_batch.get(g["chunk_ref"])
        if b is None:
            continue
        if g["tier"] >= 1:
            demand[b]["q_tier1"].add(r["id"])
        if g["tier"] == 2:
            demand[b]["q_tier2"].add(r["id"])
        demand[b]["classes"][r["class"]] += 1

rows = []
for key, cs in by_batch.items():
    states = Counter(c["gate_state"] for c in cs)
    d = demand.get(key, {"q_tier1": set(), "q_tier2": set(), "classes": Counter()})
    in_scope = all(c["in_active_scope"] for c in cs)
    rows.append({
        "document_id": key[0], "kind": key[1],
        "chunks_total": len(cs),
        "VALIDATED": states.get("VALIDATED", 0),
        "SUGGESTED": states.get("SUGGESTED", 0),
        "REJECTED": states.get("REJECTED", 0),
        "in_active_scope": in_scope,
        "embedded": sum(1 for c in cs if c["embedded"]),
        "gold_queries_tier1": len(d["q_tier1"]),
        "gold_queries_tier2": len(d["q_tier2"]),
        "gold_classes": dict(sorted(d["classes"].items())),
        "spec_codes_covered": len({code for c in cs for code in (c.get("spec_codes") or [])}),
    })

# actionable = still has SUGGESTED chunks AND fully inside the ACTIVE scope
# (out-of-scope docs would validate but still not serve — honest exclusion)
def sort_key(r):
    actionable = r["SUGGESTED"] > 0 and r["in_active_scope"]
    return (0 if actionable else 1,
            -r["gold_queries_tier2"], -r["gold_queries_tier1"],
            -len(r["gold_classes"]), -r["spec_codes_covered"],
            r["document_id"])
rows.sort(key=sort_key)

suggested = [r for r in rows if r["SUGGESTED"] > 0]
census = {
    "chunks_total": len(chunks),
    "gate_VALIDATED": sum(1 for c in chunks if c["gate_state"] == "VALIDATED"),
    "gate_SUGGESTED": sum(1 for c in chunks if c["gate_state"] == "SUGGESTED"),
    "gate_REJECTED": sum(1 for c in chunks if c["gate_state"] == "REJECTED"),
    "owner_breakdown": dict(Counter(c["owner"] for c in chunks)),
    "suggested_by_kind": dict(Counter(c["kind"] for c in chunks
                                      if c["gate_state"] == "SUGGESTED")),
    "batches_total": len(by_batch),
    "batches_actionable": sum(1 for r in rows
                              if r["SUGGESTED"] > 0 and r["in_active_scope"]),
}

# zero-recall class unlock analysis (same classes as the T-C40 review)
zero_recall_classes = ["mark_scheme", "misconception", "multi_spec_point"]
ref_to_gate = {c["chunk_ref"]: (c["gate_state"], c["owner"]) for c in chunks}
unlock = {}
for cls in zero_recall_classes:
    qs = [r for r in recs if r["class"] == cls and r.get("gold_evidence")]
    reachable_now, locked, total = 0, 0, 0
    for r in qs:
        total += 1
        states = {ref_to_gate[g["chunk_ref"]]
                  for g in r["gold_evidence"] if g["tier"] >= 1
                  and g["chunk_ref"] in ref_to_gate}
        if any(s == ("VALIDATED", o) for s, o in states if o in ("PAPER", "SUBJECT_BRANCH")):
            reachable_now += 1
        elif any(s == "SUGGESTED" for s, o in states if o == "SUBJECT_BRANCH"):
            locked += 1
    unlock[cls] = {"queries": total,
                   "gold_reachable_from_VALIDATED_supply": reachable_now,
                   "gold_unlockable_by_wave2_document_validate": locked}

worklist = {
    "tool": "bench/validation_worklist_v2.py",
    "task": "T-C41 ② wave-2 prep (operator directive 'Wave-2 prep (F-PROD-2/3/4)', 2026-10-02)",
    "date": "2026-10-02",
    "census_source": os.path.basename(CENSUS),
    "census_manifest": "live_census_manifest.json",
    "gold": json.load(open(f"{GOLD}/manifest.json")).get("set_version", "gold-v5"),
    "census": census,
    "zero_recall_class_unlock_analysis": unlock,
    "instrument_gap": (
        "No teacher-surface endpoint flips documents.validation_state on core main "
        "(ContentController/ContentDocumentController audited 2026-10-02). Wave-2 "
        "execution needs either the governed-SQL-batch precedent (notes-axis "
        "promotion, 09-28) under explicit operator authorization, or the new "
        "teacher endpoint. This worklist authorizes nothing."),
    "note": ("Operator-gated wave-2 worklist: rows are PRIORITIES, not authorizations. "
             "REJECTED documents are dead by teacher decision and appear only for "
             "completeness. Paper-axis (owner=PAPER) batches belong to the wave-1 kit."),
    "rows": rows,
}
json.dump(worklist, open(f"{OUT}/worklist2.json", "w"), indent=1, sort_keys=True)

sug_kinds = census["suggested_by_kind"]
md = f"""# Wave-2 validation worklist — LIVE census × {worklist['gold']} (T-C41 ②, 2026-10-02)

**Status:** RECORDED — deterministic, offline, generated from the live census + gold-v5 bytes
(no writes, no keys beyond the sanctioned read path). **No validation is asserted here**
(AGENT.md core rule 6): this is a priority instrument, not an authorization.

## Why wave-2 is NOT the wave-1 surface (F-PROD-3, probe-verified)

Wave-1 composed from snap-006 on the QP/MS paper axis; production had already
executed that unlock. The live truth: the paper axis (owner=PAPER) has **zero
SUGGESTED chunks**; every actionable chunk is SUBJECT_BRANCH-owned:

| surface | chunks | docs | gate | in ACTIVE scope |
|---|---:|---:|---|---|
| EXTERNAL_QUESTIONS | {sug_kinds.get('EXTERNAL_QUESTIONS', 0)} | 80 | SUGGESTED | yes |
| SYLLABUS | {sug_kinds.get('SYLLABUS', 0)} | 162 | SUGGESTED | yes |
| QUESTION_PAPER (orphaned) | {sug_kinds.get('QUESTION_PAPER', 0)} | 28 | SUGGESTED | yes (via chunk subject) |
| MARK_SCHEME (orphaned) | {sug_kinds.get('MARK_SCHEME', 0)} | 27 | SUGGESTED | yes (via chunk subject) |

- Combined actionable: **{sum(sug_kinds.values())} chunks / 297 documents** — every one a
  single document-validation act away from serving (subject-branch gate).
- "Orphaned": these QP/MS documents have NO exam_papers row (never had —
  ingest-era partial imports); no paper placement or repair is needed, the
  subject branch serves them once their document is VALIDATED.
- The 64 REJECTED chunks (30 MS + 34 QP) are dead by teacher decision —
  excluded from wave-2 by construction.

## The instrument gap (decision required before execution)

`documents.validation_state` has NO write path on core main: the teacher
surface validates papers/versions/schemes only. Corpus documents are born
SUGGESTED (V29) and nothing on main flips them. Wave-2 execution options:

1. **Governed SQL batch** (notes-axis precedent, 09-28): operator authorizes,
   batch_run_id recorded, flip SUGGESTED->VALIDATED per document, fail-closed
   prestate/poststate, zero chunks mutated. Reusable for the full 297.
2. **New teacher endpoint** (`POST /teacher/content/documents/{{id}}/validate`
   + audit row): the durable instrument; product work on core before wave-2.

## Where the zero-recall gold classes are locked

Run-005-c-r8 measured recall@10 = 0.00 on mark_scheme, misconception,
multi_spec_point (standing arm-C §8.1 verdict). Wave-2's reach into that:

| class | gold queries | reachable from today's VALIDATED supply | unlockable by wave-2 doc-validate |
|---|---:|---:|---:|
""" + "\n".join(
    f"| {k} | {v['queries']} | {v['gold_reachable_from_VALIDATED_supply']} | "
    f"{v['gold_unlockable_by_wave2_document_validate']} |\n"
    for k, v in unlock.items()) + f"""
## Priority rows (top 20 of {len(suggested)} actionable)

| document | kind | chunks | tier1 unlocks | tier2 unlocks | gold classes | spec codes |
|---|---|---:|---:|---:|---|---:|
""" + "\n".join(
    f"| {r['document_id'][:13]}… | {r['kind']} | {r['SUGGESTED']} | "
    f"{r['gold_queries_tier1']} | {r['gold_queries_tier2']} | "
    f"{', '.join(sorted(r['gold_classes'])) or '—'} | {r['spec_codes_covered']} |\n"
    for r in suggested[:20]) + """
## Reading

- Priority = (tier2 unlocks, tier1 unlocks, class diversity, spec coverage).
- The full ordered list is in `worklist2.json` (`rows`), every row traceable to
  the census bytes + gold refs (chunk_ref contract identical to snap-006).
- Expected effect, honestly bounded: document validation moves the REACHABLE
  pool (2935 -> up to 2935 + 1673); it does not move vector quality. The
  §8.1 VALIDATED bars are the first bars a validated-corpus generation can
  legitimately clear; the Run005C re-record after wave-2 measures it.
"""
open(f"{OUT}/WORKLIST2_REPORT.md", "w").write(md)
with open(f"{OUT}/SHA256SUMS", "w") as f:
    for fn in ("worklist2.json", "WORKLIST2_REPORT.md"):
        h = hashlib.sha256(open(f"{OUT}/{fn}", "rb").read()).hexdigest()
        f.write(f"{h}  {fn}\n")
print(f"wave-2 worklist recorded: {len(rows)} batches "
      f"({len(suggested)} actionable, {census['batches_total']} total)")
top = suggested[:8]
for r in top:
    print(f"   {r['document_id'][:13]}… {r['kind']:18s} SUGGESTED={r['SUGGESTED']:3d} "
          f"t1={r['gold_queries_tier1']} t2={r['gold_queries_tier2']} "
          f"classes={sorted(r['gold_classes'])}")
