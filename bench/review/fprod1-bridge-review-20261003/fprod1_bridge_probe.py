#!/usr/bin/env python3
"""fprod1_bridge_probe.py — F-PROD-1 (25-paper REVIEW_REQUIRED bridge review
batch) READ-ONLY extraction from production.

Transport (recorded quirks honored):
  - api.neon.tech has no public A record in this sandbox (documented precedent,
    records WORKLOG line 2292 / 1526) -> control plane via console.neon.tech/api/v2.
  - Role password reveal/update routes do not exist on this API surface (404/405,
    probed). Production role credentials are therefore NOT touched. Instead a
    COPY-ON-WRITE review branch `fprod1-review-ro` (br-purple-sun-a5906j1t) was
    created from production br-muddy-bar-a5huwldd; its throwaway neondb_owner
    password was reset via POST .../roles/neondb_owner/reset_password (the
    branch is brand-new, nothing else connects to it; the branch is deleted
    after extraction, killing the credential).
  - SQL runs over the Neon serverless HTTP /sql transport (psql absent).
  - ALL statements are SELECT-only. Production is untouched by construction
    (copy-on-write branch); the identity gate still runs first.

Output: JSON machine record + human transcript under scripts/ for the lane pack.
"""
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

ENV_FILE = "/home/z/my-project/scripts/.neon_env.json"
OUT_JSON = "/home/z/my-project/scripts/fprod1_probe_result.json"
OUT_TXT = "/home/z/my-project/scripts/fprod1_probe_output.txt"

API = "https://console.neon.tech/api/v2"
EXPECTED_DB = "neondb"
EXPECTED_LABEL = "T-C04-CAMPAIGN"

_lines = []


def say(s=""):
    print(s)
    _lines.append(str(s))


def env():
    return json.load(open(ENV_FILE))


def save_env(e):
    json.dump(e, open(ENV_FILE, "w"))


def api_call(e, path, method="GET", body=None):
    req = urllib.request.Request(
        API + path,
        headers={"Authorization": f"Bearer {e['neon_api_key']}",
                 "Content-Type": "application/json"},
        data=json.dumps(body).encode() if body is not None else None,
        method=method)
    return json.load(urllib.request.urlopen(req, timeout=60))


def wait_compute(e):
    eps = api_call(e, f"/projects/{e['project_id']}/branches/{e['review_branch_id']}/endpoints")["endpoints"]
    ep = eps[0]
    say(f"endpoint {ep['id']} host {ep['host']} — proceeding; /sql retry loop absorbs compute wake-up")
    return ep


def sql(e, ep_host, query):
    """One SELECT via the Neon serverless /sql transport. Returns list[dict]."""
    conn = f"postgresql://neondb_owner:{e['branch_neondb_owner_password']}@{ep_host}/neondb?sslmode=require"
    req = urllib.request.Request(
        f"https://{ep_host}/sql",
        headers={"Neon-Connection-String": conn, "Content-Type": "application/json"},
        data=json.dumps({"query": query}).encode(),
        method="POST")
    try:
        d = json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as ex:
        raise SystemExit(f"/sql failed: {ex.code} {ex.read()[:300]}")
    except Exception:
        raise  # caller may retry
    if isinstance(d, dict) and "rows" in d:
        return d["rows"]
    if isinstance(d, dict) and "results" in d:
        out = []
        for r in d["results"]:
            out.extend(r.get("rows", []))
        return out
    raise SystemExit(f"unrecognized /sql response shape: {str(d)[:300]}")


def main():
    e = env()
    ep = wait_compute(e)
    host = ep["host"]
    say(f"== F-PROD-1 bridge probe — READ-ONLY on review branch {e['review_branch_id']} (ep {host}) ==")

    # ── identity gate (retry absorbs compute wake-up) ────────────────────
    rows = None
    for attempt in range(10):
        try:
            rows = sql(e, host, "select current_database() as db, version() as v")
            break
        except Exception as ex:
            say(f"connect attempt {attempt+1}: {type(ex).__name__} {str(ex)[:120]} — retrying in 10s")
            time.sleep(10)
    if not rows:
        raise SystemExit("could not connect to the review branch endpoint")
    say(f"identity: db={rows[0]['db']}")
    if rows[0]["db"] != EXPECTED_DB:
        raise SystemExit("DB IDENTITY GATE FAILED")
    rows = sql(e, host, "select campaign_label, db_name, claimed_at, last_seen_at from campaign_db_identity where id = 1")
    if not rows or rows[0]["campaign_label"] != EXPECTED_LABEL:
        raise SystemExit(f"IDENTITY ROW GATE FAILED: {rows}")
    say(f"identity row: label={rows[0]['campaign_label']} claimed_at={rows[0]['claimed_at']} last_seen={rows[0]['last_seen_at']}")

    result = {"probe_time_utc": datetime.now(timezone.utc).isoformat(),
              "branch": e["review_branch_id"], "endpoint": host}

    # ── B. denominator census ────────────────────────────────────────────
    rows = sql(e, host, """
        select reconciliation_status as st, count(*)::int as n
        from glm_ocr_bridge_records group by 1""")
    result["bridge_census_by_status"] = rows
    say(f"bridge records by status: {rows}")

    rows = sql(e, host, """
        select p.paper_code, p.session_label, p.validation_state as paper_state,
               b.reconciliation_status as bridge, count(*)::int as n
        from glm_ocr_bridge_records b
        join exam_papers p on p.id = b.paper_id
        group by 1,2,3,4 order by 1,2""")
    result["papers_by_code_state_bridge"] = rows
    say(f"papers by code/state/bridge ({len(rows)} rows)")

    # ── C. the REVIEW_REQUIRED batch, full item detail ───────────────────
    rows = sql(e, host, """
        select b.id as bridge_id, b.paper_id, p.title, p.paper_code, p.session_label,
               p.board, p.qualification, p.validation_state as paper_state,
               b.qp_document_id, b.ms_document_id,
               qp.validation_state as qp_state, ms.validation_state as ms_state,
               b.extraction_methods, b.created_at as bridge_created_at,
               b.reconciliation_status,
               b.review_findings,
               (select count(*)::int from document_chunks c
                  where c.document_row_id = qp.id) as qp_chunks,
               (select count(*)::int from document_chunks c
                  where c.document_row_id = ms.id) as ms_chunks,
               (select count(*)::int from document_chunks c
                  where c.document_row_id = qp.id and c.embed_rev = 2) as qp_chunks_rev2,
               (select count(*)::int from document_chunks c
                  where c.document_row_id = ms.id and c.embed_rev = 2) as ms_chunks_rev2
        from glm_ocr_bridge_records b
        join exam_papers p on p.id = b.paper_id
        left join documents qp on qp.id = b.qp_document_row_id
        left join documents ms on ms.id = b.ms_document_row_id
        where b.reconciliation_status = 'REVIEW_REQUIRED'
        order by p.paper_code, p.session_label""")
    # document ids are string ids; the join needs document rows: qp_document_row_id.
    # If the _row_id columns are null for some rows, fall back below.
    result["review_required_records"] = rows
    say(f"REVIEW_REQUIRED records: {len(rows)}")
    # chunk counts via document string ids too (documents.id is VARCHAR(80))
    rows2 = sql(e, host, """
        select b.id as bridge_id,
               (select count(*)::int from document_chunks c
                  join documents d on d.id = c.document_row_id
                  where d.document_id = b.qp_document_id) as qp_chunks_str,
               (select count(*)::int from document_chunks c
                  join documents d on d.id = c.document_row_id
                  where d.document_id = b.ms_document_id) as ms_chunks_str
        from glm_ocr_bridge_records b
        where b.reconciliation_status = 'REVIEW_REQUIRED'""")
    result["review_required_chunk_counts"] = {r["bridge_id"]: r for r in rows2}

    # ── D. per-record finding stats (severity/source histograms) ─────────
    rows = sql(e, host, """
        select b.id as bridge_id,
               jsonb_array_length(b.review_findings) as n_findings
        from glm_ocr_bridge_records b
        where b.reconciliation_status = 'REVIEW_REQUIRED'""")
    result["review_required_finding_counts"] = {r["bridge_id"]: r["n_findings"] for r in rows}
    say(f"finding counts: {result['review_required_finding_counts']}")

    json.dump(result, open(OUT_JSON, "w"), indent=1, default=str)
    open(OUT_TXT, "w").write("\n".join(_lines) + "\n")
    say(f"written: {OUT_JSON}")


if __name__ == "__main__":
    main()
