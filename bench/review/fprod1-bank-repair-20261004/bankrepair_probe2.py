#!/usr/bin/env python3
"""bankrepair_probe2.py — second SELECT-only read (evidence completion).

Pulls, on a fresh COW branch (same transport as the main probe):
  1. qv provenance for the 4 target rows (source_document_id, extraction_method,
     extraction_confidence, created_at) + questions.provenance/created_at
  2. alternate-variant paper existence (4CH0/1CR June 2013 / 2018; 4CH0/1C June 2018)
  3. the mark_points rows under the 4 targets' single schemes (partial-scheme shape)
  4. audit tail (max id + last 5 rows) for the plan's audit pin context
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
BRANCH_NAME = "bankrepair-ro2"

TARGETS = [
    ("4CH0/1C", "June 2013", 10, "q10-6d968517"),
    ("4CH0/1C", "June 2017", 11, "q11-8b9f4957"),
    ("4CH0/1C", "June 2018", 12, "q12-23323bab"),
    ("4CH0/1CR", "June 2017", 11, "q11-b4e24b82"),
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
            raise SystemExit(f"unrecognized /sql shape")
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
    say(f"== probe2 (SELECT-only) == {stamp}")

    for b in api(key, f"/projects/{PROJECT}/branches").get("branches", []):
        if b["name"] == BRANCH_NAME:
            api(key, f"/projects/{PROJECT}/branches/{b['id']}", method="DELETE")
            say("orphan probe2 branch deleted")

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
        say(f"A. probe2 branch {rb_id} ep {host}")

        rows = sql(conn, host, "select current_database() as db")
        assert rows[0]["db"] == "neondb", "identity gate failed"
        rows = sql(conn, host, "select campaign_label from campaign_db_identity where id = 1")
        assert rows and rows[0]["campaign_label"] == "T-C04-CAMPAIGN", "identity row gate failed"
        say("B. identity PASS")

        result = {"probe2_utc": stamp, "branch": rb_id}

        # 1. qv provenance
        refmap = {t[3]: t for t in TARGETS}
        prov = []
        for code, sess, qn, ref in TARGETS:
            r = sql(conn, host, f"""
                select q.id as question_id, q.external_ref, q.provenance as q_prov,
                       q.created_at as q_created,
                       qv.id as qv_id, qv.source_document_id, qv.extraction_method,
                       qv.extraction_confidence, qv.created_at as qv_created
                from questions q join question_versions qv on qv.question_id = q.id
                where q.external_ref = '{ref}'
                order by qv.version desc limit 1""")
            prov.append({"ref": ref, "paper": f"{code} {sess}", "rows": r})
            if r:
                say(f"1. {ref}: src_doc={r[0]['source_document_id']} method={r[0]['extraction_method']} "
                    f"conf={r[0]['extraction_confidence']} qv_created={r[0]['qv_created']}")
            else:
                say(f"1. {ref}: NO ROWS")
        result["provenance"] = prov

        # 2. alternate-variant existence
        alt = sql(conn, host, """
            select paper_code, session_label, validation_state, id
            from exam_papers
            where (paper_code in ('4CH0/1C','4CH0/1CR') and session_label in ('June 2013','June 2017','June 2018'))
            order by paper_code, session_label""")
        result["family_papers"] = alt
        for r in alt:
            say(f"2. {r['paper_code']} {r['session_label']}: {r['validation_state']} id={r['id']}")

        # 3. mark_points under the 4 qvs' schemes
        mps = []
        for code, sess, qn, ref in TARGETS:
            r = sql(conn, host, f"""
                select mp.ref, mp.marks, left(mp.text, 90) as text_head, mp.ordering
                from mark_points mp
                join mark_schemes m on mp.mark_scheme_id = m.id
                join questions q on m.question_version_id = (select qv.id from question_versions qv
                        where qv.question_id = q.id and qv.version =
                          (select max(version) from question_versions v2 where v2.question_id = q.id))
                where q.external_ref = '{ref}'
                order by mp.ordering""")
            mps.append({"ref": ref, "paper": f"{code} {sess}", "points": r})
            say(f"3. {ref}: {len(r)} mark_points")
        result["mark_points_detail"] = mps

        # 4. audit tail
        tail = sql(conn, host, """
            select id, action, occurred_at from content_review_audit
            order by id desc limit 5""")
        mx = sql(conn, host, "select coalesce(max(id),0)::int as n from content_review_audit")
        result["audit_tail"] = {"max": mx[0]["n"], "last5": tail}
        say(f"4. audit_max={mx[0]['n']}; last: " +
            "; ".join(f"{t['id']}:{t['action']}@{str(t['occurred_at'])[:19]}" for t in tail))

    finally:
        try:
            api(key, f"/projects/{PROJECT}/branches/{rb_id}", method="DELETE", retries=2)
            say("TEARDOWN: probe2 branch DELETED (credential dead)")
        except SystemExit as ex:
            say(f"TEARDOWN FAILED — delete {rb_id} manually: {ex}")

    json.dump(result, open(f"{OUT_DIR}/probe2_result.json", "w"), indent=1, default=str)
    open(f"{OUT_DIR}/probe2_output.txt", "w").write("\n".join(_lines) + "\n")
    say("written: probe2_result.json")


if __name__ == "__main__":
    main()
