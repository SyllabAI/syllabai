#!/usr/bin/env python3
"""tc80_ms_debug.py — instrument parse_ms on the 1CR June 2016 MS print;
dump Q7's raw points (label/part/sub/text/marks) and the block structure."""
import json
import subprocess
import sys

sys.path.insert(0, "/tmp/parser-g3/tools")
from pdflane import parse_ms as pm

PDF = ("/tmp/pp-1f7e8355/past-papers/pearson-edexcel/international-gcse/"
       "chemistry/4ch0/past-papers/2016-06/4CH0-1CR/ms.pdf")

out = subprocess.run(["pdftotext", "-layout", PDF, "-"], capture_output=True,
                     text=True).stdout
pages = []
for i, page in enumerate(out.split("\f"), start=1):
    if page.strip():
        pages.append({"page": i, "text": page})

r = pm.parse_pages(pages)
for q in r["questions"]:
    if str(q["number"]) == "7":
        print("Q7 total_row:", q.get("total_row"), "sum_points:", q.get("sum_points"),
              "arithmetic_ok:", q.get("arithmetic_ok"))
        for p in q["points"]:
            print(f"  label={p.get('label')!r} part={p.get('part')!r} sub={p.get('sub')!r} "
                  f"marks={p.get('marks')} page={p.get('page')} "
                  f"text={' '.join(p.get('text') or [])[:60]!r}")
        print("unresolved_marks:", q.get("unresolved_marks"))
