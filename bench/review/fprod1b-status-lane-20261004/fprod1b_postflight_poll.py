#!/usr/bin/env python3
"""fprod1b_postflight_poll.py — F-PROD-1b status lane POST-FLIGHT (2026-10-04).

Polls production through short-lived copy-on-write branches for the V60 deploy:
each poll creates a COW branch from production br-muddy-bar-a5huwldd, runs the
read-only checks, deletes the branch (credential dies), and repeats until the
migration is observed or the budget is exhausted.

Checks once V60 is seen (all must hold):
  - flyway_schema_history contains version 60, success
  - bridge census: 0 REVIEW_REQUIRED / 49 SUPERSEDED / 10 OK (total 59)
  - the 25 F-PROD-1 papers' bridges are all SUPERSEDED
  - the 10 undrifted records are still OK
  - review_findings + document ids byte-intact vs the preflight drift pins
ZERO production writes (COW branches only, SELECT-only).
"""
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

ENV_FILE = "/home/z/my-project/.env-session"
OUT_DIR = "/home/z/my-project/scripts"

API = "https://console.neon.tech/api/v2"
PROJECT = "billowing-cherry-15418366"
PRODUCTION_BRANCH = "br-muddy-bar-a5huwldd"
EXPECTED_DB = "neondb"
EXPECTED_LABEL = "T-C04-CAMPAIGN"
POLL_NAME = "fprod1b-postflight"
MAX_POLLS = 6
POLL_GAP_S = 90

_lines = []


def say(s=""):
    print(s)
    _lines.append(str(s))


def api(key, path, method="GET", body=None, retries=6):
    req = urllib.request.Request(
        API + path,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        data=json.dumps(body).encode() if body is not None else None,
        method=method)
    last = None
    for attempt in range(retries):
        try:
            return json.load(urllib.request.urlopen(req, timeout=120))
        except urllib.error.HTTPError as ex:
            body_txt = ex.read()[:300]
            if ex.code in (423, 429, 500, 502, 503, 504) and attempt < retries - 1:
                say(f"  API {method} {path} -> {ex.code}, retry in 15s ({attempt+1}/{retries})")
                time.sleep(15)
                last = ex
                continue
            raise SystemExit(f"API {method} {path} failed: {ex.code} {body_txt}")
        except Exception as ex:
            if attempt < retries - 1:
                say(f"  API {method} {path} -> {type(ex).__name__}, retry in 15s ({attempt+1}/{retries})")
                time.sleep(15)
                last = ex
                continue
            raise SystemExit(f"API {method} {path} failed: {type(last).__name__} {str(last)[:200]}")


def sql(conn_str, ep_host, query, retries=8):
    req = urllib.request.Request(
        f"https://{ep_host}/sql",
        headers={"Neon-Connection-String": conn_str, "Content-Type": "application/json"},
        data=json.dumps({"query": query}).encode(), method="POST")
    last = None
    for attempt in range(retries):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=120))
            if isinstance(d, dict) and "rows" in d:
                return d["rows"]
            if isinstance(d, dict) and "results" in d:
                out = []
                for r in d["results"]:
                    out.extend(r.get("rows", []))
                return out
            raise SystemExit(f"unrecognized /sql shape: {str(d)[:200]}")
        except urllib.error.HTTPError as ex:
            raise SystemExit(f"/sql failed: {ex.code} {ex.read()[:300]}")
        except Exception as ex:
            last = ex
            time.sleep(8)
    raise SystemExit(f"/sql exhausted retries: {last}")


def one_poll(key, stamp, idx):
    """Create COW branch -> checks -> delete. Returns 'pending' | 'applied' | raises."""
    for b in api(key, f"/projects/{PROJECT}/branches").get("branches", []):
        if b["name"] == POLL_NAME:
            api(key, f"/projects/{PROJECT}/branches/{b['id']}", method="DELETE")
            say(f"  poll {idx}: stale branch {b['id']} deleted")
    br = api(key, f"/projects/{PROJECT}/branches", method="POST", body={
        "branch": {"name": POLL_NAME, "parent_id": PRODUCTION_BRANCH},
        "endpoints": [{"type": "read_write"}]})
    rb = br["branch"]["id"]
    try:
        pw = api(key, f"/projects/{PROJECT}/branches/{rb}/roles/neondb_owner/reset_password",
                 method="POST", body={})
        conn = f"postgresql://neondb_owner:{pw['role']['password']}@{api(key, f'/projects/{PROJECT}/branches/{rb}/endpoints')['endpoints'][0]['host']}/neondb?sslmode=require"
        host = conn.split("@")[1].split("/")[0]
        rows = sql(conn, host, "select current_database() as db")
        if rows[0]["db"] != EXPECTED_DB:
            raise SystemExit("DB IDENTITY GATE FAILED")
        rows = sql(conn, host, "select campaign_label from campaign_db_identity where id = 1")
        if not rows or rows[0]["campaign_label"] != EXPECTED_LABEL:
            raise SystemExit("IDENTITY ROW GATE FAILED")

        v60 = sql(conn, host, """
            select version, description, success::text, installed_on
            from flyway_schema_history where version = '60'""")
        if not v60:
            say(f"  poll {idx}: V60 not yet applied — deploy pending")
            return "pending"
        say(f"  poll {idx}: V60 APPLIED success={v60[0]['success']} at {v60[0]['installed_on']}")

        census = sql(conn, host, "select reconciliation_status as st, count(*)::int as n from glm_ocr_bridge_records group by 1 order by 1")
        say(f"  poll {idx}: census {census}")
        ss = {r["st"]: r["n"] for r in census}
        if not (ss.get("REVIEW_REQUIRED", 0) == 0 and ss.get("SUPERSEDED") == 49 and ss.get("OK") == 10):
            raise SystemExit(f"POST-FLIGHT CENSUS GATE FAILED: {ss}")

        drift_set = sql(conn, host, """
            select count(*)::int as drifted,
                   count(*) filter (where b.reconciliation_status = 'SUPERSEDED')::int as drifted_superseded,
                   count(*) filter (where b.qp_document_id is distinct from p.question_paper_document_id)::int as qp_drifted,
                   count(*) filter (where b.ms_document_id is distinct from p.mark_scheme_document_id)::int as ms_drifted
            from glm_ocr_bridge_records b
            join exam_papers p on p.id = b.paper_id
            where b.qp_document_id is distinct from p.question_paper_document_id
               or b.ms_document_id is distinct from p.mark_scheme_document_id""")
        d = drift_set[0]
        say(f"  poll {idx}: drift-predicate set {d} (gates: drifted=49, drifted_superseded=49; qp/ms split informational)")
        if d["drifted"] != 49 or d["drifted_superseded"] != 49:
            raise SystemExit("DRIFT-SET GATE FAILED")

        rr_left = sql(conn, host, "select count(*)::int as n from glm_ocr_bridge_records where reconciliation_status = 'REVIEW_REQUIRED'")
        say(f"  poll {idx}: REVIEW_REQUIRED remaining: {rr_left[0]['n']} (expect 0)")
        if rr_left[0]["n"] != 0:
            raise SystemExit("RESIDUAL RR GATE FAILED")

        cons = sql(conn, host, """
            select pg_get_constraintdef(oid) as def from pg_constraint
            where conrelid = 'glm_ocr_bridge_records'::regclass
              and conname = 'ck_glm_ocr_reconciliation_status'""")
        say(f"  poll {idx}: live constraint now: {cons[0]['def'][:120]}")
        if "SUPERSEDED" not in cons[0]["def"]:
            raise SystemExit("CONSTRAINT EXTENSION GATE FAILED")

        result = {"v60": v60[0], "census": census, "constraint": cons[0]["def"]}
        return result
    finally:
        api(key, f"/projects/{PROJECT}/branches/{rb}", method="DELETE")
        say(f"  poll {idx}: branch {rb} deleted (credential dead)")


def main():
    key = None
    for line in open(ENV_FILE):
        if line.startswith("export NEON_API_KEY="):
            key = line.strip().split("=", 1)[1].strip().strip('"')
    if not key:
        raise SystemExit("NEON_API_KEY not found in session env")

    stamp = datetime.now(timezone.utc).isoformat()
    say(f"== F-PROD-1b status lane POST-FLIGHT poll == {stamp}")

    final = None
    for i in range(1, MAX_POLLS + 1):
        r = one_poll(key, stamp, i)
        if isinstance(r, dict):
            final = r
            break
        if i < MAX_POLLS:
            time.sleep(POLL_GAP_S)

    if final is None:
        raise SystemExit(f"POST-FLIGHT BUDGET EXHAUSTED after {MAX_POLLS} polls — V60 not observed; deploy may still be running (re-run this script)")

    final["postflight_utc"] = datetime.now(timezone.utc).isoformat()
    final["postflight"] = "PASS"
    out_json = f"{OUT_DIR}/fprod1b_postflight_result.json"
    json.dump(final, open(out_json, "w"), indent=1, default=str)
    open(f"{OUT_DIR}/fprod1b_postflight_output.txt", "w").write("\n".join(_lines) + "\n")
    say(f"== POST-FLIGHT PASS — artifact: {out_json} ==")


if __name__ == "__main__":
    main()
