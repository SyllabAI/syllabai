#!/usr/bin/env python3
"""tc80_scheme_verify.py — verify the two unrecorded v4 production schemes
against the G4 parse of the same checksum-pinned prints (T-C45 standard:
normalized point-text containment, marks exact, sum == QP echo == qv.marks,
zero fabrication either way).

  q03-51fea326  4CH0/2C Jan 2013 Q3   scheme e1436ccc (8 points, sum 8)
  q10-5273dfa3  4CH0/1CR Jun 2016 Q10 scheme 4613c2e5 (8 points, sum 15)
"""
import json
import re
import unicodedata

preflight = json.load(open(
    "/home/z/my-project/scripts/tc80-lane/preflight_result.json"))["probes"]
targets = {
    "q03-51fea326": {
        "parse": "/home/z/my-project/scripts/tc80-lane/parse/2013-01-4CH0-2C/questions.json",
        "qnum": 3, "paper": "4CH0/2C Jan 2013",
        "scheme_id": "e1436ccc-3ed1-4b84-aca4-fc1ad5d67aa3",
    },
    "q10-5273dfa3": {
        "parse": "/home/z/my-project/scripts/tc80-lane/parse/2016-06-4CH0-1CR/questions.json",
        "qnum": 10, "paper": "4CH0/1CR Jun 2016",
        "scheme_id": "4613c2e5-9a39-475e-bd42-18a4aca1a0ba",
    },
}


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("−", "-").replace("–", "-").replace("⎯", "-")
    s = re.sub(r"[\s\-]+", " ", s.lower())
    return s.strip()


def blob(p):
    parts = []
    for k in ("text", "md", "allow", "reject", "ignore", "notes"):
        v = p.get(k)
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            parts.extend(str(x) for x in v)
    return norm(" ".join(parts))


report = {}
for ref, t in targets.items():
    q = json.load(open(t["parse"]))
    qi = [x for x in q["questions"] if int(x["number"]) == t["qnum"]][0]
    parsed = qi["markScheme"]["points"]
    parsed_sum = sum(p["marks"] for p in parsed)
    prod = [r for r in preflight["G_points"] if r[0] == t["scheme_id"]]
    prod_sum = sum(int(r[3]) for r in prod)
    matches = 0
    detail = []
    for r in prod:
        pt = norm(r[4])
        hits = [pp for pp in parsed if pt and pt in blob(pp)]
        md_hits = [pp for pp in hits
                   if pt in norm(str(pp.get("md") or ""))]
        mk = int(r[3])
        hit = (next((h for h in md_hits if h["marks"] == mk), None)
               or next((h for h in hits if h["marks"] == mk), None)
               or (md_hits[0] if md_hits else None)
               or (hits[0] if hits else None))
        if hit is not None and hit["marks"] == mk:
            matches += 1
        detail.append({"prod_marks": mk, "prod_text": r[4][:60],
                       "matched": hit is not None,
                       "marks_match": hit is not None and hit["marks"] == mk})
    qv_marks = {"q03-51fea326": 8, "q10-5273dfa3": 15}[ref]
    ok = (matches == len(prod) and prod_sum == parsed_sum == qv_marks)
    report[ref] = {
        "paper": t["paper"], "scheme_id": t["scheme_id"],
        "production_points": len(prod), "production_sum": prod_sum,
        "parsed_points": len(parsed), "parsed_sum": parsed_sum,
        "qv_marks": qv_marks, "point_text_matches": matches,
        "verdict": "VERIFIED" if ok else "MISMATCH",
        "detail": detail,
    }
    print(f"{ref} [{t['paper']}]: prod {len(prod)}pts/{prod_sum} vs parsed "
          f"{len(parsed)}pts/{parsed_sum} (qv {qv_marks}) -> {report[ref]['verdict']}")

json.dump(report, open("/home/z/my-project/scripts/tc80-lane/scheme_verify.json", "w"), indent=1)
