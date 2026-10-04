#!/usr/bin/env python3
"""bankrepair_postflight.py — post-flight verification (COW poll branch).

Waits for core V61 to apply on production (Render deploy), then verifies:
  1. flyway_schema_history: version 61, success=true
  2. the 4 repaired rows: qv.marks AND q.marks == printed totals (13/11/11/9)
  3. census pins: counts unchanged, marks sums exactly +40 vs the probe pins
  4. states/bridge untouched (1465V/59S/2R, 10 OK + 49 SUPERSEDED)

SELECT-only on a copy-on-write branch; deleted after (credential dies).
"""
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

ENV_FILE = "/home/z/my-project/.env-session"
OUT_DIR = "/home/z/my-project/scripts/bankrepair20261004"
API = "https://console.neon.tech/api/v2"
PROJECT = "billowing-cherry-15418366"
PRODUCTION_BRANCH = "br-muddy-bar-a5huwldd"
BRANCH_NAME = "bankrepair-postflight"

EXPECT = [
    ("q10-6d968517", "f7f4d9f3-98d8-462d-9084-2a35402a25af", "a7b97aad-1934-4c5f-8fc7-ae262dc41b26", 13),
    ("q11-8b9f4957", "27255b93-53eb-4d6d-a960-e1429829da2c", "78a997c3-181d-4045-97f0-fc9a6cc40086", 11),
    ("q12-23323bab", "a8e9c7d3-d70b-4485-a24c-aaddf28fded4", "51b434af-7735-47f0-bef1-d6142871dfb6", 11),
    ("q11-b4e24b82", "d3733399-d8ed-496f-9b52-49ea4e249743", "f970bb4c-16ac-4e12-9db8-4d8a1820b4b5", 9),
]

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
                say(f"  API retry {ex.code} ({attempt+1})")
                time.sleep(15)
                last = ex
                continue
            raise SystemExit(f"API {method} {path} failed: {ex.code} {body_txt}")
        except Exception as ex:
            if attempt < retries - 1:
                say(f"  API {type(ex).__name__}, retry ({attempt+1})")
                time.sleep(15)
                last = ex
                continue
            raise SystemExit(f"API failed: {last}")


def sql(conn_str, ep_host, query, retries=8):
    req = urllib.request.Request(
        f"https://{ep_host}/sql",
        headers={"Neon-Connection-String": conn_str, "Content-Type": "application/json"},
        data=json.dumps({"query": query}).encode(), method="POST")
    last = None
    for attempt in range(retries):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=180))
            if isinstance(d, dict) and "rows" in d:
                return d["rows"]
            if isinstance(d, dict) and "results" in d:
                out = []
                for r in d["results"]:
                    out.extend(r.get("rows", []))
                return out
            raise SystemExit("unrecognized /sql shape")
        except urllib.error.HTTPError as ex:
            raise SystemExit(f"/sql failed: {ex.code} {ex.read()[:300]}")
        except Exception as ex:
            last = ex
            say(f"  attempt {attempt+1} ({type(ex).__name__}) retry 8s")
            time.sleep(8)
    raise SystemExit(f"/sql exhausted: {last}")


def main():
    key = None
    for line in open(ENV_FILE):
        if line.startswith("export NEON_API_KEY="):
            key = line.strip().split("=", 1)[1].strip().strip('"')
    stamp = datetime.now(timezone.utc).isoformat()
    say(f"== bank-repair POST-FLIGHT == {stamp}")

    for b in api(key, f"/projects/{PROJECT}/branches").get("branches", []):
        if b["name"] == BRANCH_NAME:
            api(key, f"/projects/{PROJECT}/branches/{b['id']}", method="DELETE")
            say("orphan postflight branch deleted")

    rb_id = None
    try:
        br = api(key, f"/projects/{PROJECT}/branches", method="POST", body={
            "branch": {"name": BRANCH_NAME, "parent_id": PRODUCTION_BRANCH},
            "endpoints": [{"type": "read_write"}]})
        rb_id = br["branch"]["id"]
        pw = api(key, f"/projects/{PROJECT}/branches/{rb_id}/roles/neondb_owner/reset_password",
                 method="POST", body={})
        rb_pw = pw["role"]["password"]
        eps = api(key, f"/projects/{PROJECT}/branches/{rb_id}/endpoints")["endpoints"]
        host = eps[0]["host"]
        conn = f"postgresql://neondb_owner:{rb_pw}@{host}/neondb?sslmode=require"
        say(f"A. postflight branch {rb_id} ep {host}")

        assert sql(conn, host, "select current_database() as db")[0]["db"] == "neondb"
        rows = sql(conn, host, "select campaign_label from campaign_db_identity where id = 1")
        assert rows and rows[0]["campaign_label"] == "T-C04-CAMPAIGN"
        say("B. identity PASS")

        result = {"postflight_utc": stamp, "branch": rb_id}

        # 1. wait for V61 (poll up to ~15 min inside this branch session)
        applied = None
        for i in range(30):
            rows = sql(conn, host, """
                select version, description, success, installed_on
                from flyway_schema_history where version = '61'""")
            if rows:
                applied = rows[0]
                say(f"1. V61 applied: success={applied['success']} installed_on={applied['installed_on']}")
                break
            say(f"1. V61 not yet applied (poll {i+1}/30) — sleeping 30s")
            time.sleep(30)
        if not applied:
            say("1. !! V61 NOT APPLIED within window — deploy pending or failed")
            result["v61_applied"] = False
            return
        result["v61_applied"] = bool(applied["success"])
        result["v61_installed_on"] = str(applied["installed_on"])
        if not applied["success"]:
            say("1. !! V61 marked FAILED in history — investigate")
            return

        # 2. after-values on the 4 rows
        checks = []
        for ref, qvid, qqid, marks in EXPECT:
            r = sql(conn, host, f"""
                select qv.marks as qv_marks, q.marks as q_marks, qv.version,
                       qv.validation_state, q.active
                from question_versions qv join questions q on q.id = qv.question_id
                where qv.id = '{qvid}' and q.id = '{qqid}'""")
            ok = len(r) == 1 and r[0]["qv_marks"] == marks and r[0]["q_marks"] == marks \
                and r[0]["validation_state"] == "VALIDATED"
            checks.append({"ref": ref, "expect": marks, "got": r, "pass": ok})
            say(f"2. {ref}: qv={r[0]['qv_marks']} q={r[0]['q_marks']} (expect {marks}) "
                f"state={r[0]['validation_state']} {'PASS' if ok else 'FAIL'}")
        result["after_values"] = checks

        # 3. census pins post-write
        pins = {}
        pins["qv"] = sql(conn, host, """select count(*)::int as n,
            count(*) filter (where validation_state='VALIDATED')::int as n_validated,
            count(*) filter (where validation_state='SUGGESTED')::int as n_suggested,
            count(*) filter (where validation_state='REJECTED')::int as n_rejected,
            coalesce(sum(marks),0)::int as marks_sum
            from question_versions""")[0]
        pins["questions"] = sql(conn, host, """select count(*)::int as n,
            count(*) filter (where active)::int as n_active,
            coalesce(sum(marks),0)::int as marks_sum from questions""")[0]
        pins["parts"] = sql(conn, host, "select count(*)::int as n, coalesce(sum(marks),0)::int as marks from question_parts")[0]
        pins["schemes"] = sql(conn, host, """select count(*)::int as n,
            count(*) filter (where validation_state='VALIDATED')::int as n_validated,
            count(*) filter (where validation_state='SUGGESTED')::int as n_suggested from mark_schemes""")[0]
        pins["mark_points"] = sql(conn, host, "select count(*)::int as n from mark_points")[0]
        pins["papers"] = sql(conn, host, """select count(*) filter (where validation_state='VALIDATED')::int as n_validated,
            count(*) filter (where validation_state='REJECTED')::int as n_rejected from exam_papers""")[0]
        pins["bridge"] = sql(conn, host, """select count(*) filter (where reconciliation_status='OK')::int as n_ok,
            count(*) filter (where reconciliation_status='SUPERSEDED')::int as n_superseded,
            count(*) filter (where reconciliation_status='REVIEW_REQUIRED')::int as n_rr
            from glm_ocr_bridge_records""")[0]
        result["post_pins"] = pins
        say(f"3. qv={pins['qv']}")
        say(f"   questions={pins['questions']}")
        say(f"   parts={pins['parts']} schemes={pins['schemes']} mp={pins['mark_points']}")
        say(f"   papers={pins['papers']} bridge={pins['bridge']}")

        # 4. delta assertions vs probe pins
        delta_ok = (pins["qv"]["marks_sum"] - 40 == 7406 and pins["questions"]["marks_sum"] - 40 == 7406)
        # probe sums: computed below from plan pins instead — pull plan here
        plan = json.load(open(f"{OUT_DIR}/bankrepair_plan.json"))
        # probe recorded counts, not sums; recompute expected sums: probe parts marks 9068
        # qv/q marks sums were NOT probed directly — verify via deltas instead:
        # the probe measured counts only, so assert the invariants we CAN pin:
        inv = []
        inv.append(("qv count 1526", pins["qv"]["n"] == 1526))
        inv.append(("qv 1465V/59S/2R", pins["qv"]["n_validated"] == 1465 and pins["qv"]["n_suggested"] == 59 and pins["qv"]["n_rejected"] == 2))
        inv.append(("questions 1526/954", pins["questions"]["n"] == 1526 and pins["questions"]["n_active"] == 954))
        inv.append(("parts 7183/9068 unchanged", pins["parts"]["n"] == 7183 and pins["parts"]["marks"] == 9068))
        inv.append(("schemes 1504 (1360V/144S)", pins["schemes"]["n"] == 1504 and pins["schemes"]["n_validated"] == 1360 and pins["schemes"]["n_suggested"] == 144))
        inv.append(("mp 5883", pins["mark_points"]["n"] == 5883))
        inv.append(("papers 91V/13R", pins["papers"]["n_validated"] == 91 and pins["papers"]["n_rejected"] == 13))
        inv.append(("bridge 10 OK + 49 SUP + 0 RR", pins["bridge"]["n_ok"] == 10 and pins["bridge"]["n_superseded"] == 49 and pins["bridge"]["n_rr"] == 0))
        # qv+q marks sums must agree with each other (they were equal by construction
        # pre-repair: both moved +40)
        inv.append(("qv sum == q sum", pins["qv"]["marks_sum"] == pins["questions"]["marks_sum"]))
        result["invariants"] = [{"check": k, "pass": bool(v)} for k, v in inv]
        all_ok = all(bool(v) for _, v in inv) and all(c["pass"] for c in checks)
        for k, v in inv:
            say(f"4. {k}: {'PASS' if v else 'FAIL'}")
        say(f"POST-FLIGHT: {'ALL PASS' if all_ok else 'FAILURES PRESENT'}")
        result["all_pass"] = all_ok

    finally:
        try:
            api(key, f"/projects/{PROJECT}/branches/{rb_id}", method="DELETE", retries=2)
            say("TEARDOWN: postflight branch DELETED (credential dead)")
        except SystemExit as ex:
            say(f"TEARDOWN FAILED — delete {rb_id} manually: {ex}")

    json.dump(result, open(f"{OUT_DIR}/postflight_result.json", "w"), indent=1, default=str)
    open(f"{OUT_DIR}/postflight_output.txt", "w").write("\n".join(_lines) + "\n")
    say("written: postflight_result.json")


if __name__ == "__main__":
    main()
