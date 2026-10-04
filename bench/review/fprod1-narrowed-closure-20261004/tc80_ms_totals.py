#!/usr/bin/env python3
"""tc80_ms_totals.py — Lane A evidence: MS-side derived per-question totals
from the G3 engine parse products, vs QP printed totals (both from the same
checksum-pinned print substrate). Also asserts the 2016 format fact
(printed == null: the MS prints no totals anywhere)."""
import json

PAPERS = [
    ("2016-06-4CH0-1C", "4CH0/1C June 2016", 120),
    ("2016-06-4CH0-1CR", "4CH0/1CR June 2016", 120),
    ("2016-06-4CH0-2CR", "4CH0/2CR June 2016", 60),
    ("2013-01-4CH0-2C", "4CH0/2C January 2013", 60),
]

out = {}
all_ok = True
for slug, label, paper_total in PAPERS:
    q = json.load(open(f"/tmp/tc80-parse/{slug}/questions.json"))
    rows = []
    printed_total_seen = None
    for qi in q["questions"]:
        t = qi["markScheme"]["totals"]
        rows.append({
            "q": qi["number"],
            "ms_printed_total": t["printed"],
            "ms_derived_sum": t["sum"],
            "verified_against": t.get("verifiedAgainst"),
            "verified": t["verified"],
            "n_points": len(qi["markScheme"]["points"]),
        })
        if t["printed"] is not None:
            printed_total_seen = t["printed"]
        if not t["verified"] or t["sum"] != qi["marks"]:
            all_ok = False
    total = sum(r["ms_derived_sum"] for r in rows)
    out[label] = {
        "slug": slug,
        "per_question": rows,
        "derived_paper_sum": total,
        "qp_printed_paper_total": paper_total,
        "paper_sum_matches_qp_print": total == paper_total,
        "any_ms_printed_total_seen": printed_total_seen,
        "n_questions": len(rows),
    }
    ok = total == paper_total and printed_total_seen is None
    all_ok = all_ok and ok
    print(f"== {label}: {len(rows)} questions, MS-derived paper sum {total} "
          f"vs QP printed {paper_total} -> {'MATCH' if total == paper_total else 'MISMATCH'}; "
          f"MS printed totals present: {printed_total_seen is not None}")

print("\nALL FOUR PAPERS AGREE:", all_ok)
out["_all_ok"] = all_ok
json.dump(out, open("/home/z/my-project/scripts/tc80-lane/ms_derived_totals.json", "w"), indent=1)
print("saved -> scripts/tc80-lane/ms_derived_totals.json")
