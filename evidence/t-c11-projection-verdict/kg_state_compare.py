#!/usr/bin/env python3
"""Quantify the T-C11 store gap: resources canonical vs syllabai-core deployed."""
import yaml
from collections import Counter

RES = "/home/z/my-project/tc17-work/c11-probe/resources_concept_edges.yaml"
CORE = "/home/z/my-project/repos/syllabai-core/src/main/resources/concept-graph/concept_edges.yaml"

def load(p):
    with open(p) as f:
        return yaml.safe_load(f)

res = load(RES)
core = load(CORE)

def edge_key(e):
    return (e["source"], e["relation"], e["target"])

def index(d):
    out = {}
    for e in d["edges"]:
        out.setdefault(edge_key(e), []).append(e)
    return out

ri, ci = index(res), index(core)
res_keys, core_keys = set(ri), set(ci)

print("=== meta.stage ===")
print("resources:", res["meta"].get("stage"))
print("core     :", core["meta"].get("stage"))

print("\n=== edge counts by validation_status ===")
def by_status(d):
    c = Counter(e.get("validation_status") for e in d["edges"])
    return dict(c)
print("resources:", by_status(res), "total", len(res["edges"]))
print("core     :", by_status(core), "total", len(core["edges"]))

print("\n=== relation mix (HUMAN_VALIDATED only) ===")
def hv_rel(d):
    c = Counter(e["relation"] for e in d["edges"] if e.get("validation_status") == "HUMAN_VALIDATED")
    return dict(c)
print("resources:", hv_rel(res))
print("core     :", hv_rel(core))

only_res_hv = [k for k in res_keys - core_keys
               if any(e.get("validation_status") == "HUMAN_VALIDATED" for e in ri[k])]
only_core_hv = [k for k in core_keys - res_keys
                if any(e.get("validation_status") == "HUMAN_VALIDATED" for e in ci[k])]
print("\n=== HUMAN_VALIDATED edges in resources but NOT deployed to core:", len(only_res_hv))
hv_pr = [k for k in only_res_hv if k[0].startswith("4CH1-PR") or k[2].startswith("4CH1-PR")]
print("  of which practical-origin:", len(hv_pr))
for k in sorted(hv_pr):
    print("   ", k)
print("  concept->concept sample (first 12 of", len(only_res_hv)-len(hv_pr), "):")
for k in sorted(only_res_hv)[:12]:
    if k not in hv_pr:
        print("   ", k)
print("\n=== HUMAN_VALIDATED edges in core but NOT in resources:", len(only_core_hv))
for k in sorted(only_core_hv)[:10]:
    print("   ", k)
