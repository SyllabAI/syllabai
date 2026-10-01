#!/usr/bin/env python3
"""0-hit anomaly probe #2 (READ-ONLY) — which serving-eligibility predicate fails?

Established by probe #1:
  - 4CH1-2017 ACTIVE (227 VALIDATED incl. subject node), IAL-CHEM-2018 ACTIVE
    but 0 VALIDATED STRUCTURE nodes (its 1 VALIDATED node is the SUBJECT node,
    which hasValidatedStructure does not count) -> KG-side IAL not an owner.
  - search latency 4.5-9s vs 2.4s DB baseline — ambiguous (resolveActive N+1
    node walk could also explain it), so scope-refusal vs SQL-empty still open.

This probe pins ground truth on the chunk-level predicates:
  1. Documents census (GET /teacher/content/documents): createdAt buckets,
     chunkCount sums, duplicate logical documentIds across docVersions.
  2. v1 marking queue state=SMART_MARKED: distinct examPaperIds (papers whose
     questions were served for smart marking => VALIDATED papers).
  3. GET /teacher/content/exam-papers/{id}/provenance for 2-3 of them:
     the exact QP/MS logical documentIds those VALIDATED papers point at.
  4. Cross-reference those documentIds in the census: pre-V33 (rev1 era,
     ~09-13/14) vs post-V33 (rev2 era, >=09-20) — the embed_rev=2 serving
     filter either sees them or not.

No writes. Credentials never printed.
"""
import json, sys, time, urllib.request, urllib.error
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


tok = None
s, body = http("POST", "/api/v1/auth/login",
               payload={"email": email, "password": password})
if s != 200:
    print(f"LOGIN FAILED: {s}")
    sys.exit(1)
tok = (body or {}).get("token") or (body or {}).get("accessToken")
print("login OK")

# ── 1. documents census ──────────────────────────────────────────────────────
s, docs = http("GET", "/api/v1/teacher/content/documents", token=tok)
if s != 200:
    print(f"documents failed: {s}")
    sys.exit(1)
by_day = defaultdict(lambda: {"docs": 0, "chunks": 0})
for d in docs:
    day = (d.get("createdAt") or "")[:10]
    by_day[day]["docs"] += 1
    by_day[day]["chunks"] += d.get("chunkCount", 0) or 0
print(f"\n=== DOCUMENTS CENSUS ({len(docs)} rows) — by createdAt day ===")
for day in sorted(by_day):
    b = by_day[day]
    print(f"  {day}  docs={b['docs']:<4} chunks={b['chunks']:<6}")

doc_by_logical = defaultdict(list)
for d in docs:
    doc_by_logical[d.get("documentId")].append(d)
dupes = {k: v for k, v in doc_by_logical.items() if len(v) > 1}
print(f"\nlogical documentIds: {len(doc_by_logical)} | with >1 doc_version row: "
      f"{len(dupes)}")
for k, v in list(dupes.items())[:5]:
    for r in sorted(v, key=lambda x: x.get("docVersion", 0)):
        print(f"  {k[:8]}… v{r.get('docVersion')} created={(r.get('createdAt') or '')[:10]} "
              f"chunks={r.get('chunkCount')} kind={r.get('kind')}")

# ── 2. smart-marked queue -> VALIDATED papers ────────────────────────────────
s, rows = http("GET", "/api/v1/teacher/marking/answers?state=SMART_MARKED", token=tok)
print(f"\n=== v1 marking queue state=SMART_MARKED (status={s}, rows="
      f"{len(rows) if isinstance(rows, list) else rows}) ===")
papers = {}
if isinstance(rows, list):
    for r in rows:
        pid = r.get("examPaperId")
        if pid:
            papers.setdefault(pid, r.get("paperTitle"))
print(f"distinct exam papers referenced: {len(papers)}")
for pid, title in list(papers.items())[:12]:
    print(f"  {pid}  {title}")

# ── 3+4. provenance of 3 VALIDATED papers -> census cross-ref ───────────────
print("\n=== PROVENANCE of sampled VALIDATED papers vs census ===")
for pid, title in list(papers.items())[:3]:
    s, prov = http("GET", f"/api/v1/teacher/content/exam-papers/{pid}/provenance",
                   token=tok)
    print(f"\npaper {pid} ({(title or '')[:44]}) -> status={s}")
    if s != 200 or not isinstance(prov, dict):
        print(f"  body: {str(prov)[:200]}")
        continue
    for side in ("questionPaper", "markScheme"):
        ident = prov.get(side) or {}
        lid = ident.get("documentId")
        rows2 = doc_by_logical.get(lid, [])
        print(f"  {side}: documentId={lid}")
        if not rows2:
            print(f"    !! NOT FOUND in documents store")
        for r in rows2:
            day = (r.get("createdAt") or "")[:10]
            print(f"    row v{r.get('docVersion')} created={day} "
                  f"chunks={r.get('chunkCount')} kind={r.get('kind')} "
                  f"rowId={r.get('id')}")

print("\nNOTE: pre-V33 (<= 2026-09-14) doc rows carry rev1 chunks — invisible to")
print("the CURRENT_EMBED_REV=2 serving filter. Post-V33 rows carry rev2.")
