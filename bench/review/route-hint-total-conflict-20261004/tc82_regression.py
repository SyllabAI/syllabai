#!/usr/bin/env python3
"""tc82_regression.py — G4-vs-G5 corpus regression on the pinned print
substrate (syllabai-pastpapers main 7e027cad; the 4CH0 chemistry subtree is
byte-identical to the T-C80 substrate 1f7e8355 — `git diff 1f7e8355..
origin/main` on that path is empty). Parses every 4CH0 MS variant under
BOTH the G4 head (9c538ad) and the G5 branch, and diffs per-question sums.

Expectation (the G5 mandate): the ONLY diff is 2017-06/4CH0-2C q5
(19 -> 15 == printed Total 15 == QP 'Total for Question 5 = 15 marks').
Any other diff = G5 regression, print-adjudicate or narrow the guard (the
T-C80 discipline).
"""
import json
import subprocess
import sys
from pathlib import Path

CORPUS = Path("/home/z/my-project/repos/syllabai-pastpapers/past-papers/"
              "pearson-edexcel/international-gcse/chemistry/4ch0/past-papers")
G4_WT = "/home/z/my-project/repos/parser-g4base/tools"
G5_WT = "/home/z/my-project/repos/parser-g5/tools"


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


def main():
    sessions = sorted(d.name for d in CORPUS.iterdir() if d.is_dir())
    diffs = {}
    n_variants = 0
    for sess in sessions:
        for variant in sorted((CORPUS / sess).iterdir()):
            ms = variant / "ms.pdf"
            if not ms.exists():
                continue
            n_variants += 1
            g4 = parse_with(G4_WT, ms)
            g5 = parse_with(G5_WT, ms)
            key = f"{sess}/{variant.name}"
            for qn in sorted(set(g4) | set(g5), key=lambda x: (len(x), x)):
                a, b = g4.get(qn), g5.get(qn)
                if a != b:
                    diffs.setdefault(key, {})[qn] = (a, b)
            print(f"{key:24s} g4={g4} diffs={diffs.get(key, {})}",
                  flush=True)
    print(f"\n=== {n_variants} variants parsed; TOTAL DIFFS ===")
    print(json.dumps(diffs, indent=1))
    json.dump({"variants": n_variants, "diffs": diffs},
              open("/home/z/my-project/scripts/tc82-lane/"
                   "regression_diffs.json", "w"), indent=1)
    print("saved -> scripts/tc82-lane/regression_diffs.json")


if __name__ == "__main__":
    sys.exit(main())
