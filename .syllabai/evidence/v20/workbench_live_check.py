#!/usr/bin/env python3
"""Live Vercel workbench verification battery (readonly mirror mode).

Checks on the ACTUAL deployed https://syllabai-teacher-workbench.vercel.app:
  W1  app shell 200 + expected title
  W2  read APIs 200 (review index, decisions, canonical events honest-degrade)
  W3  canonical data visible (review index carries real targets/papers)
  W4  readonly mode explicit (marker in responses / headers)
  W5  staging write refused 503 BEFORE auth (POST staging endpoints)
  W6  decisions export 200
  W7  no ENOENT evidence in any response body (filesystem tracing intact)
Verdicts printed; no secrets involved (unauthenticated read surface only).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

BASE = "https://syllabai-teacher-workbench.vercel.app"
UA = {"User-Agent": "syllabai-v20-evidence/1.0", "Accept": "application/json"}

RESULTS: list[tuple[str, bool, str]] = []


def check(name, ok, detail):
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} — {detail}")


def req(method, path, payload=None, headers=None, timeout=30):
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    h = dict(UA)
    if data is not None:
        h["Content-Type"] = "application/json"
    if headers:
        h.update(headers)
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "replace")
            return resp.status, dict(resp.headers), body
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), (e.read().decode("utf-8", "replace") if e.fp else "")
    except Exception as e:  # noqa: BLE001
        return 0, {}, f"<{type(e).__name__}: {e}>"


def main() -> int:
    # W1 app shell
    s, _, b = req("GET", "/")
    title_ok = "Teacher Validation Workbench" in b
    check("W1 app shell 200 + title", s == 200 and title_ok, f"status={s} title_ok={title_ok}")

    # W2 read APIs
    read_paths = ["/api/review/index", "/api/decisions", "/api/canonical/events"]
    reads_ok = True
    details = []
    for p in read_paths:
        s, _, b = req("GET", p)
        details.append(f"{p}={s}")
        if s != 200:
            reads_ok = False
    check("W2 read APIs 200", reads_ok, " ".join(details))

    # W3 canonical data visible
    s, _, b = req("GET", "/api/review/index")
    canon = False
    detail = "n/a"
    if s == 200:
        try:
            d = json.loads(b)
            blob = json.dumps(d)
            # real paper identity expected (4CH1 corpus)
            canon = ("paper" in blob.lower() and len(blob) > 500)
            detail = f"bytes={len(blob)} papers_field={'paper' in blob.lower()}"
        except Exception as e:  # noqa: BLE001
            detail = f"unparseable: {e}"
    check("W3 canonical data visible", canon, detail)

    # W4 readonly mode explicit: export route declares X-Durable-Copy skip
    s, h, b = req("GET", "/api/decisions/export")
    xdc = (h.get("X-Durable-Copy") or h.get("x-durable-copy") or "")
    explicit = "readonly deployment" in xdc.lower()
    check("W4 readonly mode explicit (X-Durable-Copy)", explicit,
          f"status={s} x_durable_copy={xdc!r}")

    # W5 staging writes refused 503 BEFORE auth (real readonly mirror routes)
    s1, _, b1 = req("POST", "/api/decisions",
                    payload={"action": "VALIDATE", "targetType": "PAPER", "targetId": "probe"})
    w5a = (s1 == 503 and "readonly deployment" in b1)
    check("W5a POST /api/decisions -> 503 readonly (pre-auth)", w5a,
          f"status={s1} body={b1[:90]}")
    s2, _, b2 = req("POST", "/api/session", payload={"token": "probe"})
    w5b = (s2 == 503 and "readonly deployment" in b2)
    check("W5b POST /api/session -> 503 readonly (pre-auth)", w5b,
          f"status={s2} body={b2[:90]}")
    check("W5 staging writes refused 503 before auth", w5a and w5b,
          f"decisions={s1} session={s2}")

    # W6 decisions export
    s, _, b = req("GET", "/api/decisions/export")
    check("W6 decisions export 200", s == 200, f"status={s} bytes={len(b)}")

    # W7 no ENOENT anywhere
    enoent = False
    for p in ["/", "/api/review/index", "/api/decisions", "/api/decisions/export", "/api/canonical/events"]:
        s, _, b = req("GET", p)
        if "ENOENT" in b:
            enoent = True
    check("W7 no ENOENT runtime errors", not enoent, f"enoent_found={enoent}")

    fails = [r for r in RESULTS if not r[1]]
    print(f"\nWORKBENCH LIVE VERDICT: {'GREEN' if not fails else 'RED'} "
          f"{len(RESULTS) - len(fails)}/{len(RESULTS)}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
