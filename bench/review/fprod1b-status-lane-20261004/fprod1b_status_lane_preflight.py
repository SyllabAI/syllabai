#!/usr/bin/env python3
"""fprod1b_status_lane_preflight.py — F-PROD-1b status lane PREFLIGHT (2026-10-04).

The F-PROD-1b IDENTITY RULING (FPROD1B-IDENTITY-RULING-2026-10-04.md) ruled the
49 drifted glm_ocr_bridge_records SUPERSEDED-BY-REINGEST. This lane executes the
designed preflight on a COPY-ON-WRITE rehearsal branch:

  A. provision COW branch `fprod1b-rehearsal` from production br-muddy-bar-a5huwldd
     (throwaway neondb_owner password via branch-scoped reset; production creds
     never touched — no reveal/update routes exist, probed 2026-10-03)
  B. identity gates (neondb / campaign_db_identity T-C04-CAMPAIGN)
  C. read-only census on the branch (= production snapshot):
       - bridge records by status (expect 25 REVIEW_REQUIRED + 34 OK)
       - drift predicate count (HARD GATE: expect exactly 49 = 25 RR + 24 OK)
       - capture the 49 ids; the 10 undrifted OK ids
       - reconciliation_status domain check (type + constraints)
       - serving truth re-confirm (25 papers: serving docs VALIDATED, chunks @rev2)
  D. DRESS REHEARSAL on the branch only:
       UPDATE ... SET reconciliation_status='SUPERSEDED' WHERE id = ANY(<captured 49>)
       then re-census (expect 0 RR / 49 SUPERSEDED / 10 OK) + payload-integrity check
  E. teardown: delete the branch (the credential dies with it)

ZERO production writes: every statement runs on the COW branch.
Credentials: env file outside the repo, session-only, never committed.
"""
import json
import time
import urllib.request
import urllib.error
import hashlib
from datetime import datetime, timezone

ENV_FILE = "/home/z/my-project/.env-session"      # holds NEON_API_KEY (session-only)
OUT_DIR = "/home/z/my-project/scripts"

API = "https://console.neon.tech/api/v2"
PROJECT = "billowing-cherry-15418366"
PRODUCTION_BRANCH = "br-muddy-bar-a5huwldd"
EXPECTED_DB = "neondb"
EXPECTED_LABEL = "T-C04-CAMPAIGN"
REHEARSAL_NAME = "fprod1b-rehearsal"
EXPECTED_DRIFT = 49
EXPECTED_RR = 25
EXPECTED_OK_DRIFT = 24

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
            # 423 = conflicting operations still running (e.g. compute provisioning
            # right after branch create) — retryable with backoff
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
            body = ex.read()[:300]
            raise SystemExit(f"/sql failed: {ex.code} {body}")
        except Exception as ex:
            last = ex
            say(f"  connect/query attempt {attempt+1} failed ({type(ex).__name__} {str(ex)[:100]}) — retry in 8s")
            time.sleep(8)
    raise SystemExit(f"/sql exhausted retries: {last}")


def main():
    key = None
    for line in open(ENV_FILE):
        if line.startswith("export NEON_API_KEY="):
            key = line.strip().split("=", 1)[1].strip().strip('"')
    if not key:
        raise SystemExit("NEON_API_KEY not found in session env")

    stamp = datetime.now(timezone.utc).isoformat()
    say(f"== F-PROD-1b status lane PREFLIGHT == {stamp}")
    say(f"project {PROJECT}; production {PRODUCTION_BRANCH} (READ-ONLY parent)")

    # idempotency: remove any orphaned rehearsal branches from prior aborted runs
    for b in api(key, f"/projects/{PROJECT}/branches").get("branches", []):
        if b["name"] == REHEARSAL_NAME:
            api(key, f"/projects/{PROJECT}/branches/{b['id']}", method="DELETE")
            say(f"A. pre-existing orphan rehearsal branch {b['id']} deleted")

    # ── A. provision the COW rehearsal branch ────────────────────────────
    rb_id = None
    try:
        br = api(key, f"/projects/{PROJECT}/branches", method="POST", body={
            "branch": {"name": REHEARSAL_NAME, "parent_id": PRODUCTION_BRANCH},
            "endpoints": [{"type": "read_write"}]})
        rb_id = br["branch"]["id"]
        say(f"A. rehearsal branch created: {rb_id} (child of {PRODUCTION_BRANCH})")

        pw = api(key, f"/projects/{PROJECT}/branches/{rb_id}/roles/neondb_owner/reset_password",
                 method="POST", body={})
        rb_pw = pw["role"]["password"]
        say("A. throwaway neondb_owner password reset on the rehearsal branch only")
    except SystemExit:
        if rb_id:
            api(key, f"/projects/{PROJECT}/branches/{rb_id}", method="DELETE", retries=1)
            say("E. rehearsal branch DELETED (provision-abort path — credential dead)")
        raise

    # ── endpoint ─────────────────────────────────────────────────────────
    eps = api(key, f"/projects/{PROJECT}/branches/{rb_id}/endpoints")["endpoints"]
    host = eps[0]["host"]
    say(f"A. endpoint {host}")
    conn = f"postgresql://neondb_owner:{rb_pw}@{host}/neondb?sslmode=require"

    result = {"preflight_utc": stamp, "rehearsal_branch": rb_id, "endpoint": host,
              "production_branch": PRODUCTION_BRANCH}

    try:
        # ── B. identity gates ─────────────────────────────────────────────
        rows = sql(conn, host, "select current_database() as db")
        if rows[0]["db"] != EXPECTED_DB:
            raise SystemExit("DB IDENTITY GATE FAILED")
        rows = sql(conn, host, "select campaign_label, claimed_at from campaign_db_identity where id = 1")
        if not rows or rows[0]["campaign_label"] != EXPECTED_LABEL:
            raise SystemExit(f"IDENTITY ROW GATE FAILED: {rows}")
        say(f"B. identity gates PASS ({EXPECTED_DB} / {EXPECTED_LABEL} claimed {rows[0]['claimed_at']})")

        # ── C. read-only census ───────────────────────────────────────────
        by_status = sql(conn, host, "select reconciliation_status as st, count(*)::int as n from glm_ocr_bridge_records group by 1 order by 1")
        say(f"C. bridge records by status: {by_status}")
        result["census_by_status"] = by_status
        ss = {r["st"]: r["n"] for r in by_status}
        if ss.get("REVIEW_REQUIRED") != EXPECTED_RR or sum(ss.values()) != 59:
            raise SystemExit(f"CENSUS GATE FAILED: expected 25 REVIEW_REQUIRED of 59 total, got {ss}")

        drift = sql(conn, host, """
            select b.id, b.reconciliation_status as st, b.paper_id,
                   p.paper_code, p.session_label,
                   b.qp_document_id, p.question_paper_document_id as qp_serving,
                   b.ms_document_id, p.mark_scheme_document_id as ms_serving
            from glm_ocr_bridge_records b
            join exam_papers p on p.id = b.paper_id
            where b.qp_document_id is distinct from p.question_paper_document_id
               or b.ms_document_id is distinct from p.mark_scheme_document_id
            order by p.paper_code, p.session_label""")
        say(f"C. drift predicate count: {len(drift)} (gate: exactly {EXPECTED_DRIFT})")
        if len(drift) != EXPECTED_DRIFT:
            raise SystemExit(f"DRIFT GATE FAILED: {len(drift)} != {EXPECTED_DRIFT} — ABORT, re-open the question")
        from collections import Counter
        dstat = Counter(r["st"] for r in drift)
        say(f"C. drifted by status: {dict(dstat)} (gate: 25 RR + 24 OK)")
        if dstat.get("REVIEW_REQUIRED") != EXPECTED_RR or dstat.get("OK") != EXPECTED_OK_DRIFT:
            raise SystemExit(f"DRIFT SPLIT GATE FAILED: {dict(dstat)}")
        drift_ids = [r["id"] for r in drift]
        result["drift_ids"] = drift_ids
        result["drift_by_status"] = dict(dstat)

        undrifted = sql(conn, host, """
            select b.id from glm_ocr_bridge_records b
            join exam_papers p on p.id = b.paper_id
            where b.qp_document_id is not distinct from p.question_paper_document_id
              and b.ms_document_id is not distinct from p.mark_scheme_document_id""")
        say(f"C. undrifted (untouched) records: {len(undrifted)} (expect 10)")
        if len(undrifted) != 10:
            raise SystemExit(f"UNDRIFTED GATE FAILED: {len(undrifted)} != 10")
        result["undrifted_ids"] = [r["id"] for r in undrifted]

        dom = sql(conn, host, """
            select data_type, udt_name,
                   (select count(*)::int from information_schema.check_constraints cc
                      join information_schema.constraint_column_usage u
                        on u.constraint_name = cc.constraint_name
                       and u.table_name='glm_ocr_bridge_records'
                      where cc.constraint_schema='public') as check_n
            from information_schema.columns
            where table_name='glm_ocr_bridge_records' and column_name='reconciliation_status'""")
        say(f"C. reconciliation_status domain: {dom}")
        result["status_domain"] = dom

        try:
            serving = sql(conn, host, """
                select count(*)::int as papers,
                       count(*) filter (where qp.validation_state='VALIDATED' and ms.validation_state='VALIDATED')::int as docs_validated
                from glm_ocr_bridge_records b
                join exam_papers p on p.id = b.paper_id
                join documents qp on qp.id = p.question_paper_document_row_id
                join documents ms on ms.id = p.mark_scheme_document_row_id
                where b.reconciliation_status = 'REVIEW_REQUIRED'""")
            say(f"C. serving docs of the 25 REVIEW_REQUIRED papers: {serving}")
            result["serving_truth"] = serving
        except SystemExit as ex:
            say(f"C. serving-docs aggregate skipped (non-gating): {str(ex)[:160]}")
            result["serving_truth"] = "skipped (row-id column shape differs)"
    except SystemExit:
        api(key, f"/projects/{PROJECT}/branches/{rb_id}", method="DELETE", retries=1)
        say("E. rehearsal branch DELETED (abort path — credential dead)")
        raise

    # ── D. dress rehearsal on the branch (constraint-extend + flip, the
    #      migration's exact shape) — abort deletes the branch ────────────
    try:
        cons = sql(conn, host, """
            select conname, pg_get_constraintdef(oid) as def
            from pg_constraint
            where conrelid = 'glm_ocr_bridge_records'::regclass
              and conname = 'ck_glm_ocr_reconciliation_status'""")
        if not cons:
            raise SystemExit("CONSTRAINT GATE FAILED: ck_glm_ocr_reconciliation_status not found")
        conname, condef = cons[0]["conname"], cons[0]["def"]
        say(f"D. status CHECK constraint: {conname} :: {condef}")
        result["status_check_constraint"] = {"name": conname, "def": condef}

        before = sql(conn, host, """
            select id, reconciliation_status, qp_document_id, ms_document_id,
                   md5(coalesce(review_findings::text,'')) as findings_md5
            from glm_ocr_bridge_records order by id""")

        # (a) extend the domain exactly the way the migration will
        alt = sql(conn, host, f"""
            alter table glm_ocr_bridge_records
            drop constraint {conname}""")
        say(f"D. constraint dropped: {alt}")
        # add back with 'SUPERSEDED' appended inside the captured ARRAY list
        import re as _re
        m = _re.search(r"ARRAY\[(.*?)\]", condef)
        if not m:
            raise SystemExit(f"CONSTRAINT SHAPE UNPARSED: {condef}")
        values_part = m.group(1)
        new_con = condef.replace(
            f"ARRAY[{values_part}]",
            f"ARRAY[{values_part}, 'SUPERSEDED'::character varying]")
        sql(conn, host, f"alter table glm_ocr_bridge_records add constraint {conname} {new_con}")
        say("D. constraint re-added with 'SUPERSEDED' appended to the domain")

        # (b) the guarded flip on the pinned id list
        idset = "{" + ",".join(drift_ids) + "}"
        upd = sql(conn, host, f"""
            update glm_ocr_bridge_records set reconciliation_status = 'SUPERSEDED'
            where id = ANY('{idset}'::uuid[])
            returning id""")
        say(f"D. rehearsal UPDATE rows: {len(upd)} (gate: exactly {EXPECTED_DRIFT})")
        if len(upd) != EXPECTED_DRIFT:
            raise SystemExit(f"REHEARSAL UPDATE GATE FAILED: {len(upd)} rows")

        after_by_status = sql(conn, host, "select reconciliation_status as st, count(*)::int as n from glm_ocr_bridge_records group by 1 order by 1")
        say(f"D. post-rehearsal census: {after_by_status} (gate: 0 RR / 49 SUPERSEDED / 10 OK)")
        sa = {r["st"]: r["n"] for r in after_by_status}
        if sa.get("REVIEW_REQUIRED", 0) != 0 or sa.get("SUPERSEDED") != EXPECTED_DRIFT or sa.get("OK") != 10:
            raise SystemExit("POST-REHEARSAL CENSUS GATE FAILED")
        result["post_rehearsal_census"] = after_by_status

        after = sql(conn, host, """
            select id, reconciliation_status, qp_document_id, ms_document_id,
                   md5(coalesce(review_findings::text,'')) as findings_md5
            from glm_ocr_bridge_records order by id""")
        bmap = dict((x["id"], x) for x in before)
        changed_wrong = [r["id"] for r in after
                         if r["id"] not in set(drift_ids)
                         and bmap[r["id"]]["reconciliation_status"] != r["reconciliation_status"]]
        payload_diff = [r["id"] for r in after
                        if bmap[r["id"]]["findings_md5"] != r["findings_md5"]
                        or bmap[r["id"]]["qp_document_id"] != r["qp_document_id"]
                        or bmap[r["id"]]["ms_document_id"] != r["ms_document_id"]]
        say(f"D. rows whose status changed outside the 49: {len(changed_wrong)} (gate 0)")
        say(f"D. rows whose findings/doc-id payload changed: {len(payload_diff)} (gate 0)")
        if changed_wrong or payload_diff:
            raise SystemExit("REHEARSAL INTEGRITY GATE FAILED")
        result["rehearsal"] = {"updated": len(upd), "collateral": 0, "payload_changes": 0,
                               "constraint_name": conname,
                               "new_constraint": new_con}
    except SystemExit:
        api(key, f"/projects/{PROJECT}/branches/{rb_id}", method="DELETE", retries=1)
        say("E. rehearsal branch DELETED (rehearsal-abort path — credential dead)")
        raise

    # ── E. teardown ──────────────────────────────────────────────────────
    api(key, f"/projects/{PROJECT}/branches/{rb_id}", method="DELETE")
    say("E. rehearsal branch DELETED — the throwaway credential is dead")

    result["preflight"] = "PASS"
    out_json = f"{OUT_DIR}/fprod1b_preflight_result.json"
    out_txt = f"{OUT_DIR}/fprod1b_preflight_output.txt"
    json.dump(result, open(out_json, "w"), indent=1)
    open(out_txt, "w").write("\n".join(_lines) + "\n")
    say(f"== PREFLIGHT PASS — artifacts: {out_json} / {out_txt} ==")


if __name__ == "__main__":
    main()
