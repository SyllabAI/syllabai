#!/usr/bin/env python3
"""0-hit anomaly probe #3 (READ-ONLY) — pin a VALIDATED paper's doc generation.

From probe #2 + sessions 121-127: rev2 (09-20/21/22) docs all belong to papers
born SUGGESTED; the teacher-VALIDATED rows are glmocr-era (rev1, 09-14 docs).
This probe pins that directly: the G-4 practice papers (queue_pending.json,
served through the always-VALIDATED-only question surface) -> exam-papers/{id}
review (paper validationState) + provenance (QP/MS documentIds) -> documents
census (createdAt => rev1 vs rev2 era).

Then (separate execution step) the operator-decided IAL archive runs.
"""
import json, sys, urllib.request, urllib.error
from collections import defaultdict

BASE = "https://syllabai-core.onrender.com"
creds = open("/home/z/my-project/.g4_creds").read().strip().splitlines()
email, password = creds[0].strip(), creds[1].strip()


def http(method, path, token=None, payload=None, timeout=180):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        method=method,
        headers={"Content-Type": "application/json",
                 **({"Authorization": f"Bearer {token}"} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode()
            return r.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body[:300]
    except (urllib.error.URLError, TimeoutError) as e:
        return 0, {"raw": str(getattr(e, "reason", e))}


s, body = http("POST", "/api/v1/auth/login",
               payload={"email": email, "password": password})
if s != 200:
    print(f"LOGIN FAILED: {s}")
    sys.exit(1)
tok = (body or {}).get("token") or (body or {}).get("accessToken")
print("login OK")

# documents census (logical id -> rows)
s, docs = http("GET", "/api/v1/teacher/content/documents", token=tok)
doc_by_logical = defaultdict(list)
for d in docs:
    doc_by_logical[d.get("documentId")].append(d)
print(f"documents census: {len(docs)} rows, {len(doc_by_logical)} logical ids")

# G-4 practice paper ids (queue_pending.json, 2026-09-23 snapshot)
pids = set()
q = json.load(open("/home/z/my-project/download/g4-kappa-calibration/queue_pending.json"))
rows = q if isinstance(q, list) else q.get("items", q.get("rows", []))
for r in rows:
    if isinstance(r, dict) and r.get("paperId"):
        pids.add(r["paperId"])
print(f"queue_pending paperIds: {sorted(pids)}")

for pid in sorted(pids):
    s, rev = http("GET", f"/api/v1/teacher/content/exam-papers/{pid}/review", token=tok)
    if s != 200:
        print(f"\npaper {pid}: review status={s} (row may be archived/superseded)")
        continue
    top = rev if isinstance(rev, dict) else {}
    paper = top.get("paper") or top
    print(f"\npaper {pid}")
    print(f"  title={paper.get('title')} validationState={paper.get('validationState')} "
          f"subjectId={paper.get('subjectId')}")
    s2, prov = http("GET", f"/api/v1/teacher/content/exam-papers/{pid}/provenance",
                    token=tok)
    if s2 != 200:
        print(f"  provenance: status={s2}")
        continue
    for side in ("questionPaper", "markScheme"):
        ident = (prov.get(side) or {})
        lid = ident.get("documentId")
        rows2 = doc_by_logical.get(lid, [])
        tag = "NOT-IN-STORE" if not rows2 else ", ".join(
            f"v{r.get('docVersion')} created={(r.get('createdAt') or '')[:10]} "
            f"chunks={r.get('chunkCount')}" for r in rows2)
        print(f"  {side}: {lid} -> {tag}")
