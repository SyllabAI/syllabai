#!/usr/bin/env python3
"""g8-finish CI orchestrator (records repo bench/inputs/g8-finish/).

Completes the G8 backfill embed: the 2026-09-21 G8 batch (66 papers x qp/ms
ingested as rev2 paper-axis chunks) was cut twice by daily key quota — the
serving key was 91fdfb06ac (index 1, exhausted 13:27 UTC mid-run) and then
797b77a879 (index 2, also exhausted the same day), leaving 538+ chunks pending
across ~60 docs plus the final 8 papers posted after the parser fix.

Vectors are produced BY THE PRODUCTION APP (POST /{id}/embed, Spring AI batched
transport — the canonical vector space per the Task-33 transport guard; direct
CI REST calls are a DIFFERENT vector space and are FORBIDDEN for corpus rows).

Per round (key = remaining keys only, in KEY_ORDER):
  1. read the full Render env, swap SYLLABAI_EMBEDDING_GEMINI_API_KEY to
     keys[idx] (all other vars preserved byte-for-byte), PUT back
  2. POST /deploys and poll until live (env changes do not auto-deploy)
  3. mint a 10-min ADMIN/TEACHER JWT from the live SYLLABAI_JWT_SECRET
  4. drive POST /{id}/embed for every pending doc; a doc is done when
     embedded + skipped == totalChunks (idempotent endpoint, resumable)
  5. docs that fail or come back partial go to the next round with the next key

RAW KEY VALUES NEVER REACH THE REPORT — fingerprints only. G8 default KEY_ORDER
is 3,0,1,2 (1 and 2 are the keys exhausted today; 3 and 0 are untouched).

Stdlib only.
import base64
import hashlib
import hmac
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

SERVICE = os.environ.get("RENDER_SERVICE_ID", "srv-dagijie7bikc73bc0460")
RENDER = "https://api.render.com/v1"
BASE = "https://syllabai-core.onrender.com"
HERE = pathlib.Path(__file__).parent
OUT = pathlib.Path(os.environ.get("FINISH_OUT", "finish-out-pending-v2"))
OUT.mkdir(parents=True, exist_ok=True)


def parse_keys(raw):
    out, cur = [], ""
    for ch in raw:
        if ch in ",; \n\t":
            if cur:
                out.append(cur)
                cur = ""
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def fp(key):
    return "sha256:" + hashlib.sha256(key.encode()).hexdigest()[:10]


def http_json(method, url, body=None, headers=None, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Accept": "application/json"}
    if body is not None:
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"{method} {url} -> HTTP {e.code}: {detail}") from None


def render(method, path, body=None, timeout=120):
    return http_json(method, f"{RENDER}/{path}", body,
                     {"Authorization": f"Bearer {os.environ['RENDER_API_TOKEN']}"}, timeout)


def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def mint_jwt(identity, secret):
    now = int(time.time())
    header = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    claims = b64url(json.dumps({
        "sub": identity["admin_email"], "jti": identity["admin_uid"],
        "uid": identity["admin_uid"], "roles": identity["roles"],
        "iat": now, "exp": now + 600,
    }, separators=(",", ":")).encode())
    sig = hmac.new(secret.encode(), f"{header}.{claims}".encode(), hashlib.sha256).digest()
    return f"{header}.{claims}.{b64url(sig)}"


def swap_key(key):
    items = render("GET", f"services/{SERVICE}/env-vars")
    # items: [{envVar:{key,value,...}}, ...] — normalize to CLEAN {key,value}
    # pairs: the PUT contract rejects the GET payload's extra fields (cursor etc.)
    raw = [it.get("envVar", it) for it in items]
    current_fp = None
    jwt_secret = None
    changed = False
    env = []
    for e in raw:
        k, v = e["key"], e.get("value") or ""
        if k == "SYLLABAI_JWT_SECRET":
            jwt_secret = v
        if k == "SYLLABAI_EMBEDDING_GEMINI_API_KEY":
            current_fp = fp(v) if v else None
            if v != key:
                v = key
                changed = True
        env.append({"key": k, "value": v})
    assert jwt_secret, "SYLLABAI_JWT_SECRET not found in Render env"
    print(f"  current embedding key: {current_fp} -> {fp(key)} "
          f"({'PUT' if changed else 'already set'})", flush=True)
    if changed:
        # Render env-vars PUT contract: BARE ARRAY body ({"envVars": ...} is
        # rejected as invalid JSON — verified 400 vs 200 by probe 2026-09-21)
        render("PUT", f"services/{SERVICE}/env-vars", env)
    return changed, jwt_secret


def deploy_and_wait(timeout_s=900):
    dep = render("POST", f"services/{SERVICE}/deploys", {"clearCache": "do_not_clear"})
    dep_id = dep.get("id") or dep.get("deploy", {}).get("id")
    print(f"  deploy {dep_id} requested", flush=True)
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        time.sleep(15)
        d = render("GET", f"services/{SERVICE}/deploys/{dep_id}")
        d = d.get("deploy", d) if isinstance(d, dict) else d
        # handle both raw and wrapped shapes
        if isinstance(d, dict) and "deploy" in d:
            d = d["deploy"]
        status = d.get("status") if isinstance(d, dict) else None
        print(f"  deploy status: {status} ({int(time.time() - t0)}s)", flush=True)
        if status == "live":
            return dep_id, int(time.time() - t0)
        if status in ("build_failed", "update_failed", "canceled", "deactivated"):
            raise RuntimeError(f"deploy {dep_id} reached {status}")
    raise RuntimeError(f"deploy {dep_id} not live after {timeout_s}s")


def wait_health(minutes=6):
    t0 = time.time()
    last = None
    while time.time() - t0 < minutes * 60:
        try:
            with urllib.request.urlopen(f"{BASE}/actuator/health", timeout=20) as r:
                body = r.read().decode()
                if '"UP"' in body or '"status":"up"' in body.lower():
                    return True
                last = body[:80]
        except Exception as e:
            last = str(e)[:80]
        time.sleep(10)
    raise RuntimeError(f"health not UP after {minutes}min: {last}")


def drive(docs, token):
    embedded = skipped = 0
    failures = []
    consecutive_http = 0
    last_http_code = None
    for i, d in enumerate(docs, 1):
        did = d["document_row_id"]
        try:
            view = http_json("POST", f"{BASE}/api/v1/teacher/content/documents/{did}/embed",
                             headers={"Authorization": f"Bearer {token}"}, timeout=300)
            consecutive_http = 0
            last_http_code = None
            embedded += view.get("embedded", 0)
            skipped += view.get("skipped", 0)
            done = view.get("embedded", 0) + view.get("skipped", 0) == view.get("totalChunks", 0)
            print(f"  [{i}/{len(docs)}] {did[:8]} embedded={view.get('embedded')} "
                  f"skipped={view.get('skipped')}/{view.get('totalChunks')}"
                  f"{'' if done else '  PARTIAL'}", flush=True)
            if not done:
                failures.append({"doc": did, "reason": "partial", "view": view})
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:220]
            print(f"  [{i}/{len(docs)}] {did[:8]} HTTP {e.code}: {body}", flush=True)
            failures.append({"doc": did, "reason": f"http{e.code}", "body": body})
            # fail fast: 3 consecutive failures of the same class (e.g. provider
            # quota surfacing as 500) means the rest of the round will fail too —
            # rotate to the next key immediately.
            if e.code == last_http_code:
                consecutive_http += 1
            else:
                consecutive_http, last_http_code = 1, e.code
            if consecutive_http >= 3:
                print(f"  fail-fast: {consecutive_http}x HTTP {e.code} in a row — "
                      f"aborting round for key rotation", flush=True)
                break
        except Exception as e:
            consecutive_http = 0
            print(f"  [{i}/{len(docs)}] {did[:8]} ERROR {str(e)[:120]}", flush=True)
            failures.append({"doc": did, "reason": "transport", "body": str(e)[:220]})
        time.sleep(0.5)
    return embedded, skipped, failures


def main():
    keys = parse_keys(os.environ["SYLLABAI_EMBEDDING_GEMINI_API_KEYS"])
    key_order = [int(x) for x in os.environ.get("KEY_ORDER", "1,3,0").split(",") if x.strip()]
    for idx in key_order:
        assert 0 <= idx < len(keys), f"key index {idx} out of range ({len(keys)} keys)"
    docs = [json.loads(l) for l in (HERE / "pending_docs.jsonl").read_text().splitlines() if l]
    identity = json.loads((HERE / "identity.json").read_text())
    total_pending = sum(d["pending"] for d in docs)
    print(f"finish-pending-v2: {len(docs)} docs / {total_pending} chunks; "
          f"key_order={key_order} fingerprints="
          f"{ {i: fp(keys[i]) for i in key_order} }", flush=True)

    report = {
        "artifact": "finish-pending-v2",
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "docs": len(docs), "chunks_pending": total_pending,
        "key_order": key_order,
        "fingerprints": {str(i): fp(keys[i]) for i in range(len(keys))},
        "rounds": [],
    }
    open_docs = list(docs)
    for round_no, idx in enumerate(key_order, 1):
        if not open_docs:
            break
        key = keys[idx]
        print(f"ROUND {round_no}: key[{idx}] {fp(key)}", flush=True)
        r = {"round": round_no, "key_index": idx, "key_fingerprint": fp(key)}
        changed, jwt_secret = swap_key(key)
        r["env_changed"] = changed
        dep_id, dt = deploy_and_wait()
        r["deploy_id"], r["deploy_seconds"] = dep_id, dt
        wait_health()
        print("  health UP", flush=True)
        token = mint_jwt(identity, jwt_secret)
        embedded, skipped, failures = drive(open_docs, token)
        r.update({"docs_posted": len(open_docs), "embedded": embedded,
                  "skipped": skipped, "failures": failures})
        report["rounds"].append(r)
        open_docs = [d for d in open_docs if any(f["doc"] == d["document_row_id"] for f in failures)]
        print(f"ROUND {round_no} done: embedded={embedded} skipped={skipped} "
              f"open_docs={len(open_docs)}", flush=True)

    report["open_docs_after"] = [d["document_row_id"] for d in open_docs]
    report["complete"] = not open_docs
    (OUT / "finish_report.json").write_text(json.dumps(report, indent=1) + "\n")
    h = hashlib.sha256((OUT / "finish_report.json").read_bytes()).hexdigest()
    (OUT / "SHA256SUMS").write_text(f"{h}  finish_report.json\n")
    print("COMPLETE" if report["complete"] else "INCOMPLETE — open docs remain",
          flush=True)
    return 0 if report["complete"] else 2


if __name__ == "__main__":
    sys.exit(main())
