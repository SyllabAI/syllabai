#!/usr/bin/env python3
"""Sanctioned production action (operator decision, trace 1a0d88b65a04bb55):
"we are not doing the ial chemistry for pilot 1. We moved to igcse chemistry"

-> POST /teacher/curriculum/versions/{IAL-CHEM-2018 id}/archive
   (the designed, reversible status surface: ACTIVE -> ARCHIVED; nothing is
    deleted; the version keeps its 11 KG nodes for audit).

Fail-closed: abort unless exactly one IAL-CHEM-2018 ACTIVE row matches the
known id prefix 10000000-0000-0000-0000-000000000001; abort on any non-2xx.
After the archive: verify via /versions, then re-probe the search surface
(honest expectation: still 0 hits — probe #1-#3 proved the 0-hit cause is the
rev1×rev2/VALIDATED intersection, not the scope resolver; the archive removes
the LATENT scope-refusal risk and implements the curriculum decision).
"""
import json, sys, time, urllib.request, urllib.error

BASE = "https://syllabai-core.onrender.com"
creds = open("/home/z/my-project/.g4_creds").read().strip().splitlines()
email, password = creds[0].strip(), creds[1].strip()

EXPECTED_IAL_ID = "10000000-0000-0000-0000-000000000001"


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

# precheck: exactly one ACTIVE IAL row with the expected id
s, versions = http("GET", "/api/v1/teacher/curriculum/versions", token=tok)
if s != 200:
    print(f"versions precheck failed: {s}")
    sys.exit(1)
ial = [v for v in versions if v["id"] == EXPECTED_IAL_ID]
if len(ial) != 1:
    print(f"ABORT: expected exactly 1 IAL row {EXPECTED_IAL_ID}, got {len(ial)}")
    sys.exit(1)
v = ial[0]
if v["status"] != "ACTIVE":
    print(f"ABORT: IAL status is {v['status']} (expected ACTIVE) — nothing to do")
    sys.exit(1)
print(f"precheck OK: {v['code']} status=ACTIVE id={v['id']}")

# the sanctioned action
s, result = http("POST",
                 f"/api/v1/teacher/curriculum/versions/{EXPECTED_IAL_ID}/archive",
                 token=tok)
if s not in (200, 201):
    print(f"ABORT: archive failed: {s} {result}")
    sys.exit(1)
print(f"archive POST -> {s}: code={result.get('code')} "
      f"status={result.get('status')}")

# postcheck: version list reflects ARCHIVED, 4CH1-2017 still ACTIVE
s, versions = http("GET", "/api/v1/teacher/curriculum/versions", token=tok)
for row in versions:
    print(f"  {row['code']:<14} status={row['status']}")
archived = [r for r in versions
            if r["id"] == EXPECTED_IAL_ID and r["status"] == "ARCHIVED"]
active_4ch1 = [r for r in versions
               if r["code"] == "4CH1-2017" and r["status"] == "ACTIVE"]
if not archived or not active_4ch1:
    print("POSTCHECK FAILED — do not proceed")
    sys.exit(1)
print("postcheck OK: IAL ARCHIVED, 4CH1-2017 ACTIVE")

# honest re-probe: the 0-hit expectation must be unchanged (archive is NOT
# the 0-hit fix — the fix is the rev2 validation decision, operator-owned)
time.sleep(2)
for q in ("electrolysis of molten lead bromide",
          "explain catalytic cracking of alkanes"):
    s, hits, = http(
        "GET",
        "/api/v1/teacher/content/documents/search?limit=5&query="
        + urllib.request.quote(q), token=tok)
    n = len(hits) if isinstance(hits, list) else hits
    print(f"  search [{q[:40]:<40}] -> {s} hits={n}")
print("done")
