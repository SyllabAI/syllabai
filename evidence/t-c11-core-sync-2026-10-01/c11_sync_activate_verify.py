#!/usr/bin/env python3
"""C11 core-sync post-deploy: operator-path activation + prod verification.

Part 1 (API, teacher-role path — the governed activation):
  login with the cached G-4 teacher creds -> POST concept-graph/activate
  (idempotent; expected nodesCreated=80, edgesCreated=94 anchors + 119 semantic)
Part 2 (DB, read-only via Render env):
  counts, the 7 practical-origin edges, frozen-five exclusion, statuses.
Never prints credentials.
"""
import json, urllib.request, urllib.error, sys
from pathlib import Path
from urllib.parse import urlparse
import pg8000.native

PROJ = Path("/home/z/my-project")
BASE = "https://syllabai-core.onrender.com"

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
            return r.status, json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]

creds = (PROJ / ".g4_creds").read_text().strip().splitlines()
email, password = creds[0].strip(), creds[1].strip()

print("== Part 1: activation (API) ==")
status, body = http("POST", "/api/v1/auth/login", payload={"email": email, "password": password})
print(f"login: {status}, token received: {status == 200 and bool(body.get('token') or body.get('accessToken'))}")
if status != 200:
    print("LOGIN FAILED — activation not attempted"); sys.exit(1)
token = (body or {}).get("token") or (body or {}).get("accessToken")

status, summary = http("POST", "/api/v1/teacher/concept-graph/activate", token=token)
print(f"activate: {status}")
print(json.dumps(summary, indent=1)[:800] if isinstance(summary, dict) else str(summary)[:300])
if status != 200:
    print("ACTIVATION FAILED"); sys.exit(1)

# teacher edge read model sanity (served counts)
status, edges_view = http("GET", "/api/v1/teacher/concept-graph/edges", token=token)
if status == 200 and isinstance(edges_view, dict):
    rows = edges_view.get("edges", [])
    by_rel = {}
    for e in rows:
        by_rel[e.get("relation")] = by_rel.get(e.get("relation"), 0) + 1
    print(f"teacher edges view: {len(rows)} rows, by relation: {by_rel}")
else:
    print(f"teacher edges view: status {status} (path may differ; DB probe below is authoritative)")

PAT = (PROJ / ".render_token").read_text().strip()
SVC = "srv-dagijie7bikc73bc0460"
env = json.load(urllib.request.urlopen(urllib.request.Request(
    f"https://api.render.com/v1/services/{SVC}/env-vars",
    headers={"Authorization": f"Bearer {PAT}", "Accept": "application/json"}), timeout=30))
env = {i["envVar"]["key"]: i["envVar"]["value"] for i in env}
u = urlparse(env["SYLLABAI_DATABASE_URL"].replace("jdbc:postgresql://", "postgresql://", 1))
con = pg8000.native.Connection(user=env["SYLLABAI_DATABASE_USERNAME"],
                               password=env["SYLLABAI_DATABASE_PASSWORD"],
                               host=u.hostname, port=u.port or 5432,
                               database=u.path.lstrip("/"), ssl_context=True)

print("\n== Part 2: prod DB ground truth (read-only; KG is flat, codes carry the 4CH1 namespace) ==")
for r in con.run("""
    SELECT node_type, validation_status, count(*)
    FROM knowledge_nodes WHERE code LIKE '4CH1-%'
    GROUP BY 1, 2 ORDER BY 1, 2"""):
    print(f"  node {r[0]:14s} {r[1]:10s} {r[2]}")
for r in con.run("""
    SELECT e.relation_type, e.validation_status, count(*)
    FROM knowledge_edges e
    JOIN knowledge_nodes sn ON e.source_node_id = sn.id
    WHERE sn.code LIKE '4CH1-%'
    GROUP BY 1, 2 ORDER BY 1, 2"""):
    print(f"  edge {r[0]:24s} {r[1]:10s} {r[2]}")

print("\n== the 7 practical-origin edges (must be VALIDATED) ==")
for r in con.run("""
    SELECT sn.code, tn.code, e.validation_status
    FROM knowledge_edges e
    JOIN knowledge_nodes sn ON e.source_node_id = sn.id
    JOIN knowledge_nodes tn ON e.target_node_id = tn.id
    WHERE (sn.code LIKE '4CH1-PR-0%' OR sn.code = '4CH1-PR-12')
      AND e.relation_type = 'REQUIRES_PREREQUISITE'
    ORDER BY sn.code, tn.code"""):
    print(f"  {r[0]:12s} -[{r[2]}]-> {r[1]}")

print("\n== frozen five must be ABSENT ==")
for r in con.run("""
    SELECT count(*) FROM knowledge_edges e
    JOIN knowledge_nodes sn ON e.source_node_id = sn.id
    JOIN knowledge_nodes tn ON e.target_node_id = tn.id
    WHERE (sn.code, tn.code) IN (
        ('4CH1-CON-REACTING-MASS','4CH1-CON-EQ-SYMBOL'),
        ('4CH1-CON-CRYSTALLISATION','4CH1-CON-SOLUTION'),
        ('4CH1-CON-GAS-VOL-CALC','4CH1-CON-AVOGADRO-LAW'))
      AND e.relation_type != 'PART_OF'"""):
    print(f"  frozen semantic rows on prod: {r[0]} (expect 0: the 3 pilot HOLDs + 2 REVIEW_REQUIRED never materialize)")
