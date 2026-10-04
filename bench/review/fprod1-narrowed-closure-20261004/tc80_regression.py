#!/usr/bin/env python3
"""tc80_regression.py — G3-vs-G4 corpus regression on the pinned print
substrate (1f7e8355). Parses every available 4CH0 MS paper under BOTH the
G3 head (0fc5c32) and the G4 branch, and diffs per-question sums.

Expectation (the G4 mandate): the ONLY diff is 1CR-2016 Q7 (13 -> 12).
Any other diff = G4 regression, lane aborts.
"""
import json
import subprocess
import sys
from pathlib import Path

CORPUS = Path("/tmp/pp-1f7e8355/past-papers/pearson-edexcel/"
              "international-gcse/chemistry/4ch0/past-papers")
G3_WT_MARKER = "unused"
G4_TOOLS = "/home/z/my-project/wt-parser-g4/tools"


def parse_with(tools, pdf):
    code = f"""
import subprocess, sys, json
sys.path.insert(0, {tools!r})
from pdflane import parse_ms as pm
out = subprocess.run(['pdftotext', '-layout', {str(pdf)!r}, '-'],
                     capture_output=True, text=True).stdout
pages = [{{'page': i, 'text': t}} for i, t in enumerate(out.split(chr(12)), 1)
         if t.strip()]
r = pm.parse_pages(pages)
print(json.dumps({{str(q['number']): q['sum_points'] for q in r['questions']}}))
"""
    res = subprocess.run([sys.executable, "-c", code], capture_output=True,
                         text=True)
    if res.returncode != 0:
        return {"__error__": res.stderr[-300:]}
    return json.loads(res.stdout.strip().splitlines()[-1])


# G3 snapshot: the records-repo parser clone's local main is stale, so the
# G3 side is taken from the parser repo's origin/main object store via a
# second worktree prepared by the caller (see G3_WT below).
G3_WT = "/home/z/my-project/wt-parser-g3"

sessions = sorted(d.name for d in CORPUS.iterdir() if d.is_dir())
diffs = {}
for sess in sessions:
    for variant in sorted((CORPUS / sess).iterdir()):
        ms = variant / "ms.pdf"
        if not ms.exists():
            continue
        g3 = parse_with(G3_WT + "/tools", ms)
        g4 = parse_with(G4_TOOLS, ms)
        key = f"{sess}/{variant.name}"
        for qn in sorted(set(g3) | set(g4), key=lambda x: (len(x), x)):
            a, b = g3.get(qn), g4.get(qn)
            if a != b:
                diffs.setdefault(key, {})[qn] = (a, b)
        print(f"{key:24s} g3={ {k: g3[k] for k in sorted(g3)} } "
              f"diffs={diffs.get(key, {})}")

print("\n=== TOTAL DIFFS ===")
print(json.dumps(diffs, indent=1))
json.dump(diffs, open("/home/z/my-project/scripts/tc80-lane/regression_diffs.json", "w"), indent=1)
