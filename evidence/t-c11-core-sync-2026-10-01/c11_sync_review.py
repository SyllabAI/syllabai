#!/usr/bin/env python3
"""C11 core-sync preflight + the 7-edge package review (operator GO, trace 1a0f3e20d4f963e9).

Verifies, against ground truth (no memory):
  A. sync census + field-level drift discipline (core batch-4 -> canonical batch-11)
  B. referential integrity of the PARTIAL sync (2 files) against core's unsynced substrate
  C. the 7-edge practical package evidence (§3 of C11_PROJECTION_REVIEW_VERDICT_2026-10-01.md)
  D. the sync manifest: new SHAs + the loader/test constants
Exits non-zero on any failed require().
"""
import yaml, hashlib, json, sys
from collections import Counter

RES = "/home/z/my-project/repos/syllabai-resources/graph/igcse-chemistry"
CORE = "/home/z/my-project/repos/syllabai-core/src/main/resources/concept-graph"

def load(p):
    with open(p, "rb") as f:
        b = f.read()
    return b, yaml.safe_load(b)

def sha(b):
    return hashlib.sha256(b).hexdigest()

failures = []
def require(cond, msg):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {msg}")
    if not cond:
        failures.append(msg)

# ── load everything ──────────────────────────────────────────────────────────
core_edges_b, core_edges = load(f"{CORE}/concept_edges.yaml")
res_edges_b, res_edges = load(f"{RES}/concept_edges.yaml")
core_conc_b, core_conc = load(f"{CORE}/concepts.yaml")
res_conc_b, res_conc = load(f"{RES}/concepts.yaml")
core_spec_b, core_spec = load(f"{CORE}/specification_points.yaml")
core_prac_b, core_prac = load(f"{CORE}/practicals.yaml")

def ekey(e): return (e["source"], e["relation"], e["target"])
def index(doc): 
    out = {}
    for e in doc["edges"]: out.setdefault(ekey(e), []).append(e)
    return out

ci, ri = index(core_edges), index(res_edges)
core_nodes = {n["code"]: n for n in core_conc["nodes"]}
res_nodes = {n["code"]: n for n in res_conc["nodes"]}
sp_codes = {sp["code"] for sp in core_spec["specification_points"]}
prac_codes = {p["code"] for p in core_prac["practicals"]}

print("== A1. store identity ==")
print(f"core stage     : {core_edges['meta']['stage']}")
print(f"canonical stage: {res_edges['meta']['stage']}")
require("s16-batch-11" in res_edges["meta"]["stage"], "canonical store is at batch-11")
require("s16-batch-4" in core_edges["meta"]["stage"] and "s16-batch-5" not in core_edges["meta"]["stage"],
        "core store still batch-4 (gap intact)")

print("\n== A2. key-set discipline ==")
core_keys, res_keys = set(ci), set(ri)
require(core_keys <= res_keys, f"every core edge key exists in canonical (core-only: {sorted(core_keys-res_keys)[:5]})")
added = res_keys - core_keys
added_hv = [k for k in added if any(e.get("validation_status")=="HUMAN_VALIDATED" for e in ri[k])]
added_other = added - set(added_hv)
print(f"added keys: {len(added)} (HV: {len(added_hv)}, non-HV: {len(added_other)})")

print("\n== A3. field-level drift on common keys ==")
status_flips, other_drift = [], []
ALLOWED_PATH_FIX = ("graph/specification_points.yaml", "graph/igcse-chemistry/specification_points.yaml")
def evidence_drift_allowed(cv, rv):
    """Only the C24/C26-era evidence path normalization is cosmetic-allowed."""
    if not isinstance(cv, list) or not isinstance(rv, list) or len(cv) != len(rv):
        return False
    for a, b in zip(cv, rv):
        if a == b: continue
        if set(a) == set(b):
            for f in set(a):
                if a.get(f) != b.get(f):
                    if a.get(f) == ALLOWED_PATH_FIX[0] and b.get(f) == ALLOWED_PATH_FIX[1]:
                        continue
                    return False
        else:
            return False
    return True
spec_quotes = []
def spec_quote_refresh(cv, rv):
    """C26 wording-authority refresh: SPEC-kind evidence re-quoted from the canonical
    PDF-direct parse. NOTE-kind (SME corpus) quotes must NEVER change — enforced below."""
    if not isinstance(cv, list) or not isinstance(rv, list) or len(cv) != len(rv):
        return False
    changed = False
    for a, b in zip(cv, rv):
        if a == b: continue
        if a.get("kind") != b.get("kind") or a.get("kind") != "SPEC":
            return False
        if not str(a.get("file","")).endswith("specification_points.yaml") or \
           not str(b.get("file","")).endswith("specification_points.yaml"):
            return False
        changed = True
    return changed

for k in core_keys & res_keys:
    ce, re_ = ci[k][0], ri[k][0]
    if len(ci[k]) != 1 or len(ri[k]) != 1:
        other_drift.append((k, "DUPLICATE KEYS"))
        continue
    for f in set(ce) | set(re_):
        cv, rv = ce.get(f), re_.get(f)
        if cv == rv: continue
        if f == "validation_status" and ce.get("relation") == "PART_OF" \
           and ce.get("validation_status") == "SUGGESTED" and rv == "HUMAN_VALIDATED":
            status_flips.append(k)
        elif f in ("validated_by", "validated_date") and ce.get("relation") == "PART_OF" \
           and rv and ce.get("validation_status") == "SUGGESTED" and re_.get("validation_status") == "HUMAN_VALIDATED":
            pass  # operator validation stamps accompanying the anchor promotion (session-106 round)
        elif f == "evidence" and evidence_drift_allowed(cv, rv):
            pass  # evidence path normalization only
        elif f == "evidence" and spec_quote_refresh(cv, rv):
            spec_quotes.append((k, cv, rv))  # C26 wording-authority refresh, SPEC-kind only, recorded verbatim
        else:
            other_drift.append((k, f))
require(not other_drift, f"zero drift on common keys beyond allowed classes (drift: {other_drift[:6]})")
require(all(q[0][1] == "PART_OF" for q in spec_quotes), "SPEC-quote refreshes confined to anchor rows")
print(f"anchor status flips: {len(status_flips)}; SPEC-quote wording refreshes: {len(spec_quotes)} (recorded verbatim below)")
for k, cv, rv in spec_quotes:
    for a, b in zip(cv, rv):
        if a != b:
            print(f"   {k[0]}@{k[2]}: {str(a.get('quote'))[:75]!r} -> {str(b.get('quote'))[:75]!r}")

print("\n== A4. loader contract counts (canonical) ==")
part_of = [e for e in res_edges["edges"] if e["relation"] == "PART_OF"]
hv_sem  = [e for e in res_edges["edges"] if e["relation"] != "PART_OF" and e.get("validation_status") == "HUMAN_VALIDATED"]
excl    = [e for e in res_edges["edges"] if e["relation"] != "PART_OF" and e.get("validation_status") != "HUMAN_VALIDATED"]
core_part_of = [e for e in core_edges["edges"] if e["relation"] == "PART_OF"]
core_hv_sem  = [e for e in core_edges["edges"] if e["relation"] != "PART_OF" and e.get("validation_status") == "HUMAN_VALIDATED"]
core_excl    = [e for e in core_edges["edges"] if e["relation"] != "PART_OF" and e.get("validation_status") != "HUMAN_VALIDATED"]
print(f"anchors (PART_OF all statuses): core {len(core_part_of)} -> canonical {len(part_of)}")
print(f"validated semantic           : core {len(core_hv_sem)} -> canonical {len(hv_sem)}")
print(f"excluded (frozen) semantic   : core {len(core_excl)} -> canonical {len(excl)}")
print(f"concept nodes                : core {len(core_nodes)} -> canonical {len(res_nodes)}")
require(len(part_of) == 211 and len(hv_sem) == 272 and len(excl) == 5,
        f"canonical counts == (211 anchors, 272 validated semantic, 5 excluded); got {len(part_of)}/{len(hv_sem)}/{len(excl)}")
frozen_core = {ekey(e) for e in core_excl}
frozen_res  = {ekey(e) for e in excl}
require(frozen_core == frozen_res, f"the frozen 5 are the SAME keys (new/exiting: {frozen_res ^ frozen_core})")

print("\n== A5. anchor delta decomposition ==")
core_anchor_keys = {ekey(e) for e in core_part_of}
res_anchor_keys  = {ekey(e) for e in part_of}
require(core_anchor_keys == set(status_flips) or core_anchor_keys <= res_anchor_keys,
        "core anchors are a strict subset of canonical anchors")
new_anchors = res_anchor_keys - core_anchor_keys
anchor_status_by_key = {ekey(e): e.get("validation_status") for e in part_of}
new_anchor_status = Counter(anchor_status_by_key[k] for k in new_anchors)
print(f"anchors preserved+flipped: {len(status_flips)}; new anchors: {len(new_anchors)} {dict(new_anchor_status)}")
require(len(status_flips) == 117 and new_anchors == res_anchor_keys - core_anchor_keys and len(new_anchors) == 94,
        "anchor delta == 117 flips + 94 new (operator-validated attachments from batches 5-11)")

print("\n== A6. concept node drift ==")
common_nodes = set(core_nodes) & set(res_nodes)
node_drift = []
for c in common_nodes:
    if core_nodes[c] != res_nodes[c]:
        node_drift.append(c)
# node rows: only spec_points[].evidence SPEC-quote/path refreshes allowed (loader reads code/family/title/aliases ONLY)
node_bad = []
for c in node_drift:
    a, b = core_nodes[c], res_nodes[c]
    if set(a) != set(b) or any(a[f] != b[f] for f in a if f != "spec_points"):
        node_bad.append((c, "non-spec_points field changed"))
        continue
    for sa, sb in zip(a["spec_points"], b["spec_points"]):
        if sa == sb: continue
        if set(sa) != set(sb) or any(sa[f] != sb[f] for f in sa if f != "evidence"):
            node_bad.append((c, sa.get("code"), "anchor row non-evidence field changed"))
        elif not spec_quote_refresh(sa.get("evidence", []), sb.get("evidence", [])) and \
             not evidence_drift_allowed(sa.get("evidence", []), sb.get("evidence", [])):
            node_bad.append((c, sa.get("code"), "evidence drift outside allowed classes"))
require(not node_bad, f"node-row drift confined to spec_points evidence refresh classes (bad: {node_bad[:4]})")
new_nodes = sorted(set(res_nodes) - set(core_nodes))
print(f"new concept nodes: {len(new_nodes)} (113 -> {len(res_nodes)})")

print("\n== A7. referential integrity of the PARTIAL sync vs core substrate ==")
bad_anchor_sp  = [k for k in res_anchor_keys if not (k[0] in res_nodes and k[2] in sp_codes)]
bad_sem_endpts = [k for k in res_keys if k[0] != "PART_OF" and k[1] != "PART_OF"
                  and not (k[0] in res_nodes or k[0] in prac_codes)
                  and not (k[2] in res_nodes or k[2] in prac_codes)]
bad_sem = []
for k in hv_sem:
    s, t = ekey(k)[0], ekey(k)[2]
    if not (s in res_nodes or s in prac_codes): bad_sem.append(("src", s))
    if not (t in res_nodes or t in prac_codes): bad_sem.append(("tgt", t))
require(not bad_anchor_sp, f"every anchor resolves: concept in canonical nodes AND SP in core's 182 (bad: {bad_anchor_sp[:4]})")
require(not bad_sem, f"every HV semantic endpoint resolves vs canonical concepts + core's 12 practicals (bad: {bad_sem[:4]})")
print("\n== A7b. node-row drift detail (what exactly changed for pre-existing nodes)")
for c in sorted(node_drift):
    a, b = core_nodes[c], res_nodes[c]
    fields = [f for f in set(a) | set(b) if a.get(f) != b.get(f)]
    print(f"  {c}: fields changed: {fields}")
    for f in fields:
        if f == "aliases":
            print(f"    aliases: {a.get(f)} -> {b.get(f)}")
        elif f == "spec_points":
            sa = {(s.get('code'), s.get('role')) for s in a.get(f, [])}
            sb = {(s.get('code'), s.get('role')) for s in b.get(f, [])}
            print(f"    (code,role) added: {sorted(sb - sa)}; removed: {sorted(sa - sb)}; evidence-path-only changes not shown")
        else:
            print(f"    {f}: {str(a.get(f))[:80]} -> {str(b.get(f))[:80]}")

print("\n== B. the 7-edge package review (§3 verdict table) ==")
PACKAGE = [
    ("4CH1-PR-05", "4CH1-CON-O2-PERCENT-DETERMINATION", "c11-s16-batch-5",  "USED_WITHOUT_RETEACHING",
     ["To determine the percentage of oxygen in air using the oxidation of iron", "percentage of oxygen ="]),
    ("4CH1-PR-06", "4CH1-CON-REACT-ARRANGE",            "c11-s16-batch-6",  "USED_WITHOUT_RETEACHING",
     ["The metals can be ranked in reactivity order Mg > Zn > Fe"]),
    ("4CH1-PR-07", "4CH1-CON-SALT-INSOLUBLE-REACTANT",  "c11-s16-batch-7",  "USED_WITHOUT_RETEACHING",
     ["Add the copper(II) oxide slowly to the hot dilute acid and stir until the base is in excess"]),
    ("4CH1-PR-08", "4CH1-CON-SALT-PRECIPITATION",       "c11-s16-batch-7",  "USED_WITHOUT_RETEACHING",
     ["The solid salt obtained is the precipitate", "Filter to remove precipitate from mixture"]),
    ("4CH1-PR-12", "4CH1-CON-ESTERS",                   "c11-s16-batch-11", "EXPLICIT_TEACH_SEQUENCE",
     ["To prepare a small sample of ethyl ethanoate"]),
    ("4CH1-PR-12", "4CH1-CON-SIMPLE-DISTILLATION",      "c11-s16-batch-11", "USED_WITHOUT_RETEACHING",
     ["The ester is then distilled off as soon as it is formed"]),
    ("4CH1-PR-12", "4CH1-CON-ACID-REACTIONS",           "c11-s16-batch-11", "USED_WITHOUT_RETEACHING",
     ["sodium carbonate solution can be added"]),
]
prac_spec = {p["code"]: p.get("spec_point") or p.get("specPointCode") or p.get("spec_point_code") for p in core_prac["practicals"]}
package_rows = []
for src, tgt, batch, method, quotes in PACKAGE:
    k = (src, "REQUIRES_PREREQUISITE", tgt)
    rows = ri.get(k, [])
    ok = len(rows) == 1
    require(ok, f"{src} REQUIRES {tgt}: present exactly once in canonical")
    if not ok: continue
    e = rows[0]
    pv = e.get("provenance", {})
    require(e.get("validation_status") == "HUMAN_VALIDATED", f"  {tgt}: HUMAN_VALIDATED")
    require(pv.get("extraction_pass") == batch, f"  {tgt}: extraction_pass == {batch}")
    require(pv.get("derivation_method") == method, f"  {tgt}: derivation_method == {method}")
    require(bool(e.get("validated_by")) and bool(e.get("validated_date")),
            f"  {tgt}: validated_by/date present ({e.get('validated_by')}, {e.get('validated_date')})")
    ev_quotes = [ev.get("quote","") for ev in e.get("evidence", []) if ev.get("kind") == "NOTE"]
    for q in quotes:
        require(any(q in eq for eq in ev_quotes), f"  {tgt}: NOTE quote present: '{q[:60]}...'")
    concept = res_nodes.get(tgt, {})
    core_anchors = [sp["code"] for sp in concept.get("spec_points", []) if sp.get("role") == "CORE"]
    ruling = "session-66 ruling" in str(pv.get("derivation_notes", ""))
    package_rows.append({
        "edge": f"{src} REQUIRES {tgt}", "batch": batch.split("-")[-1], "method": method,
        "concept_core_anchors": core_anchors, "practical_sp": prac_spec.get(src),
        "projected_pair": f"{core_anchors[0]} -> {prac_spec.get(src)}" if core_anchors else None,
        "boundary_ruling_noted": ruling if tgt.startswith("4CH1-CON-SIMPLE") or tgt.startswith("4CH1-CON-ACID") else None,
        "notes_head": str(pv.get("derivation_notes",""))[:120],
    })
    print(f"  -> {tgt}: concept CORE anchors {core_anchors}, practical SP {prac_spec.get(src)}, "
          f"projected pair {core_anchors[:1]} -> {prac_spec.get(src)}")

print("\n== B2. practical-origin delta census ==")
prac_added = [k for k in added_hv if k[0].startswith("4CH1-PR-") or k[2].startswith("4CH1-PR-")]
c2c_added  = [k for k in added_hv if k not in prac_added]
require(len(prac_added) == 7, f"exactly 7 new practical-origin HV edges (got {len(prac_added)})")
require(len(c2c_added) == 112, f"exactly 112 new concept->concept HV edges (got {len(c2c_added)})")
rel_mix = Counter(k[1] for k in added_hv)
print(f"added HV by relation: {dict(rel_mix)}")

print("\n== D. sync manifest ==")
man = {
    "copy_files": {
        "concepts.yaml":    {"sha256": sha(res_conc_b), "bytes": len(res_conc_b)},
        "concept_edges.yaml": {"sha256": sha(res_edges_b), "bytes": len(res_edges_b)},
    },
    "loader_constants": {
        "CONCEPT_NODE_COUNT": len(res_nodes),
        "ANCHOR_EDGE_COUNT": len(part_of),
        "VALIDATED_SEMANTIC_EDGE_COUNT": len(hv_sem),
        "EXCLUDED_SEMANTIC_EDGE_COUNT": len(excl),
        "CONCEPTS_SHA256": sha(res_conc_b),
        "CONCEPT_EDGES_SHA256": sha(res_edges_b),
    },
    "test_sums": {
        "nodes": 1 + 4 + 28 + 182 + 12 + len(res_nodes),
        "edges_ever_saved": 4 + 28 + 182 + 12 + len(part_of) + len(hv_sem),
    },
    "package": package_rows,
    "new_nodes": new_nodes,
    "added_hv_practical": [list(k) for k in prac_added],
}
with open("/home/z/my-project/tc17-work/c11-probe/sync_manifest.json", "w") as f:
    json.dump(man, f, indent=1, default=str)
print(json.dumps({k: man[k] for k in ("loader_constants", "test_sums")}, indent=1))

print("\n" + ("ALL CHECKS PASSED" if not failures else f"{len(failures)} FAILURES: {failures}"))
sys.exit(1 if failures else 0)
