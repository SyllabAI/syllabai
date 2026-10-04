#!/usr/bin/env python3
"""bankrepair_probe3.py — third SELECT-only read: ALTERNATE-variant QP chunk texts.

For the attribution leg on the laneD substrate (ingested chunk text, not raw
pdftotext): pulls the serving QP docs' chunk text for the alternate variants:
    4CH0/1CR June 2013 (alt of target q10-6d968517)
    4CH0/1C  June 2017 (alt of target q11-b4e24b82)
    4CH0/1CR June 2017 (alt of target q11-8b9f4957)
(4CH0/1CR June 2018 does not exist — recorded in the plan.)
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
BRANCH_NAME = "bankrepair-ro3"

ALTS = [
    ("4CH0/1CR", "June 2013"),
    ("4CH0/1C", "June 2017"),
    ("4CH0/1CR", "June 2017"),
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
    say(f"== probe3 (SELECT-only) == {stamp}")

    for b in api(key, f"/projects/{PROJECT}/branches").get("branches", []):
        if b["name"] == BRANCH_NAME:
            api(key, f"/projects/{PROJECT}/branches/{b['id']}", method="DELETE")
            say("orphan probe3 branch deleted")

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
        say(f"A. probe3 branch {rb_id} ep {host}")

        assert sql(conn, host, "select current_database() as db")[0]["db"] == "neondb"
        rows = sql(conn, host, "select campaign_label from campaign_db_identity where id = 1")
        assert rows and rows[0]["campaign_label"] == "T-C04-CAMPAIGN"
        say("B. identity PASS")

        result = {"probe3_utc": stamp, "alts": []}
        for code, sess in ALTS:
            r = sql(conn, host, f"""
                select p.id as paper_id, p.paper_code, p.session_label, p.validation_state,
                       p.question_paper_document_id
                from exam_papers p
                where p.paper_code = '{code}' and p.session_label = '{sess}'""")
            if not r:
                say(f"{code} {sess}: NO PAPER ROW")
                result["alts"].append({"paper": f"{code} {sess}", "found": False})
                continue
            p = r[0]
            d = sql(conn, host, f"""
                select id, document_id, checksum, validation_state from documents
                where document_id = '{p['question_paper_document_id']}'""")[0]
            crows = sql(conn, host, f"""
                select c.chunk_index, c.content as txt from document_chunks c
                where c.document_row_id = '{d['id']}' order by c.chunk_index""")
            result["alts"].append({
                "paper": f"{code} {sess}", "found": True,
                "paper_id": p["paper_id"], "paper_state": p["validation_state"],
                "qp_doc": p["question_paper_document_id"],
                "qp_doc_checksum": d["checksum"], "qp_doc_state": d["validation_state"],
                "n_chunks": len(crows),
                "chunk_text_joined": "\n".join((c["txt"] or "") for c in crows)})
            say(f"ALT {code} {sess}: qp doc {p['question_paper_document_id'][:14]}… "
                f"state={d['validation_state']} chunks={len(crows)}")
    finally:
        try:
            api(key, f"/projects/{PROJECT}/branches/{rb_id}", method="DELETE", retries=2)
            say("TEARDOWN: probe3 branch DELETED (credential dead)")
        except SystemExit as ex:
            say(f"TEARDOWN FAILED — delete {rb_id} manually: {ex}")

    json.dump(result, open(f"{OUT_DIR}/probe3_result.json", "w"), indent=1, default=str)
    open(f"{OUT_DIR}/probe3_output.txt", "w").write("\n".join(_lines) + "\n")
    say("written: probe3_result.json")


if __name__ == "__main__":
    main()
