#!/usr/bin/env python3
"""Extract the 7 practical->concept edges (PR-05/06/07/08/12) evidence blocks
from the resources batch decision records — the Batch-5 authoring evidence."""
import yaml, json

D = "/home/z/my-project/tc17-work/c11-probe"
BATCHES = {5: "c11_batch5_decisions.yaml", 6: "c11_batch6_decisions.yaml",
           7: "c11_batch7_decisions.yaml", 11: "c11_batch11_decisions.yaml"}
PRS = {"4CH1-PR-05", "4CH1-PR-06", "4CH1-PR-07", "4CH1-PR-08", "4CH1-PR-12"}

out = []
for b, fname in BATCHES.items():
    doc = yaml.safe_load(open(f"{D}/{fname}"))
    # decision records may nest edges under different keys — walk
    def walk(node):
        if isinstance(node, dict):
            if node.get("source") in PRS and node.get("relation") == "REQUIRES_PREREQUISITE":
                out.append({"batch": b, "file": fname, **node})
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(doc)

print(f"found {len(out)} practical->concept decision records")
for r in out:
    print(f"\n=== batch {r['batch']}: {r['source']} REQUIRES {r['target']} ===")
    print(f"  validation_status: {r.get('validation_status')}  confidence: {r.get('confidence')}")
    ev = r.get("evidence", [])
    for e in ev:
        print(f"  evidence [{e.get('kind')}] {e.get('file','')}")
        print(f"    quote: {e.get('quote','')!r}")
    p = r.get("provenance", {})
    print(f"  derivation_method: {p.get('derivation_method')}")
    print(f"  notes: {p.get('derivation_notes','')[:300]}")
    print(f"  upstream: {p.get('upstream','')}")

with open(f"{D}/practical_batch5_evidence.json", "w") as f:
    json.dump(out, f, indent=2, default=str)
print(f"\nsaved -> {D}/practical_batch5_evidence.json")
