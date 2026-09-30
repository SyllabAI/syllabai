#!/usr/bin/env python3
"""Reconstruct the T-C11 concept->SP projection over the DEPLOYED core store.

Mirrors syllabai-core PR #37 (ClassAnalyticsService): every HUMAN_VALIDATED
concept-level REQUIRES_PREREQUISITE edge projects onto the SpecificationPoint(s)
that teach its endpoint concepts, via the concept->SP PART_OF anchor edges
(concepts.yaml spec_points[] attachments, materialized by the seeder).
Practical nodes project onto their practicals.yaml spec_point.
Self-projections collapse. Pair notation below: PREREQUISITE -> DEPENDENT
(the sheet's notation; the store edge is from=dependent to=prerequisite).
"""
import yaml
from collections import defaultdict
from itertools import product

CG = "/home/z/my-project/repos/syllabai-core/src/main/resources/concept-graph"

edges_doc = yaml.safe_load(open(f"{CG}/concept_edges.yaml"))
concepts_doc = yaml.safe_load(open(f"{CG}/concepts.yaml"))
practicals_doc = yaml.safe_load(open(f"{CG}/practicals.yaml"))

# --- anchors -------------------------------------------------------------
concept_anchor = {}   # concept code -> {sp code: [roles]}
for c in concepts_doc["nodes"]:
    sps = {}
    for att in c.get("spec_points", []):
        sps.setdefault(att["code"], []).append(att.get("role", "?"))
    concept_anchor[c["code"]] = sps

practical_sp = {p["code"]: p["spec_point"] for p in practicals_doc["practicals"]}

def endpoints_sp(code):
    """SP codes a node code projects onto."""
    if code in concept_anchor:
        return set(concept_anchor[code].keys())
    if code in practical_sp:
        return {practical_sp[code]}
    return {code}  # already structure (SP/topic/...)

# --- validated prerequisite edges ----------------------------------------
hv = [e for e in edges_doc["edges"]
      if e["relation"] == "REQUIRES_PREREQUISITE"
      and e.get("validation_status") == "HUMAN_VALIDATED"]
print(f"HUMAN_VALIDATED REQUIRES_PREREQUISITE edges: {len(hv)}")
print(f"  concept->concept: {sum(1 for e in hv if e['source'].startswith('4CH1-CON') and e['target'].startswith('4CH1-CON'))}")
print(f"  practical->concept: {sum(1 for e in hv if e['source'].startswith('4CH1-PR'))}")

# --- project -------------------------------------------------------------
pair_support = defaultdict(list)   # (pre_sp, dep_sp) -> [store edges]
unprojectable = []
for e in hv:
    src, tgt = e["source"], e["target"]
    src_sps = endpoints_sp(src)
    tgt_sps = endpoints_sp(tgt)
    if not src_sps or not tgt_sps:
        unprojectable.append((src, tgt))
        continue
    for pre, dep in product(tgt_sps, src_sps):
        if pre == dep:
            continue  # self-projection collapse
        pair_support[(pre, dep)].append((src, tgt))

print(f"\nprojected SP-level pairs: {len(pair_support)}")
print(f"unprojectable edges: {len(unprojectable)}")

# --- taxonomy -------------------------------------------------------------
# practical-dependent = supported by >=1 practical->concept store edge
practical_pairs = {k: v for k, v in pair_support.items()
                   if any(s.startswith("4CH1-PR") for s, t in v)}
print(f"practical-dependent SP pairs: {len(practical_pairs)}")
for k in sorted(practical_pairs):
    print(f"   {k[0]} -> {k[1]}   via {practical_pairs[k]}")

single = {k: v for k, v in pair_support.items() if len(v) == 1}
multi = {k: v for k, v in pair_support.items() if len(v) > 1}
print(f"\nsingle-supported pairs: {len(single)}  multi-supported (convergent): {len(multi)}")

# order inversions by numeric SP order within a section
def sp_num(code):
    body = code.replace("4CH1-", "")
    sec, rest = body.split(".", 1)
    return (int(sec), float(rest.replace("C", ".5")))

inv = {k: v for k, v in pair_support.items()
       if k[0].startswith("4CH1-") and k[1].startswith("4CH1-")
       and not k[0].startswith("4CH1-PR") and not k[1].startswith("4CH1-PR")
       and sp_num(k[0]) > sp_num(k[1])}
print(f"inverted-order concept pairs: {len(inv)}")
for k in sorted(inv, key=lambda x: sp_num(x[0])):
    print(f"   {k[0]} -> {k[1]}   via {inv[k]}")

# cross-section pairs
cross = {k: v for k, v in pair_support.items() if k[0].split(".")[0] != k[1].split(".")[0]}
print(f"cross-section pairs: {len(cross)}")
for k in sorted(cross):
    print(f"   {k[0]} -> {k[1]}   via {cross[k]}")

# pairs resting only on non-CORE attachments (weaker anchoring)
noncore_only = {}
for k, v in pair_support.items():
    ok = True
    for src, tgt in v:
        src_roles = concept_anchor.get(src, {}).get(k[1])  # dependent-side anchors
        tgt_roles = concept_anchor.get(tgt, {}).get(k[0])  # prerequisite-side anchors
        src_r = src_roles or []
        tgt_r = tgt_roles or []
        if ("CORE" in src_r) or ("CORE" in tgt_r):
            ok = False
            break
    if ok:
        noncore_only[k] = v
print(f"pairs with NO CORE-role anchor on either side: {len(noncore_only)}")

# --- the 8 anomaly pairs from the operator verdict -------------------------
anomalies = [("4CH1-1.3", "4CH1-1.2"), ("4CH1-1.10", "4CH1-1.5C"),
             ("4CH1-1.10", "4CH1-PR-01"), ("4CH1-1.28", "4CH1-1.26"),
             ("4CH1-1.33", "4CH1-1.32"), ("4CH1-1.33", "4CH1-1.31"),
             ("4CH1-3.14C", "4CH1-3.12"), ("4CH1-3.14C", "4CH1-3.13")]
print("\n=== the 8 verdict pairs (prerequisite -> dependent) ===")
for pre, dep in anomalies:
    v = pair_support.get((pre, dep))
    if v:
        print(f"  {pre} -> {dep}: SUPPORTED via {v}")
    else:
        # try the reverse direction in case of notation flip
        rv = pair_support.get((dep, pre))
        print(f"  {pre} -> {dep}: {'NOT in projection' if not rv else f'REVERSE pair exists: {rv}'}")

# dump all pairs grouped, for the record
print("\n=== all projected pairs (prerequisite -> dependent | supporting store edges) ===")
for (pre, dep), v in sorted(pair_support.items()):
    print(f"{pre} -> {dep} | {'; '.join(f'{s}=>{t}' for s, t in v)}")

# --- candidate "inferred-only" union: weak-basis classes -------------------
union = set(practical_pairs) | set(inv) | set(noncore_only)
print(f"\nUNION practical-dependent | inverted | non-CORE-only: {len(union)}")

print("\n=== the 1 non-CORE-only pair identity ===")
for k, v in noncore_only.items():
    print(f"   {k[0]} -> {k[1]}   via {v}")
    for src, tgt in v:
        print(f"     dependent {src} anchors: {concept_anchor.get(src, {})}")
        print(f"     prerequisite {tgt} anchors: {concept_anchor.get(tgt, {})}")
