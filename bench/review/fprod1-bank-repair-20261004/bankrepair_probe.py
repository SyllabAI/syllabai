#!/usr/bin/env python3
"""bankrepair_probe.py — F-PROD-1 bank-repair lane PROBE (2026-10-04).

The F-PROD-1 print pass (records 2ffbbb3, Session 183) referred 4 defect rows
to the bank-repair lane: ms-only rows where the bank serves a 1-mark partial
entry against 9-13-mark prints:
    4CH0/1C  June 2013 Q10  bank 1, print 13
    4CH0/1C  June 2017 Q11  bank 1, print 11
    4CH0/1C  June 2018 Q12  bank 1, print 11
    4CH0/1CR June 2017 Q11  bank 1, print 9
Operator word (trace 1a1047d4ad41baf9): "repair the 4 bank entries".

This probe is SELECT-ONLY on a COPY-ON-WRITE branch (production untouched):
  A. provision COW branch `bankrepair-ro` from production br-muddy-bar-a5huwldd
     (throwaway neondb_owner password; production creds never touched)
  B. identity gates (neondb / campaign_db_identity T-C04-CAMPAIGN)
  C. shape probe: information_schema for the tables this lane touches
  D. resolve the 4 target qv rows (paper x question), full bank state
  E. census pins (fresh, post-V57/V60 production state)
  F. document identity: rows matching the 8 corpus checksums + bridge rows
     for the 4 papers + MS chunk TOT corroboration text
  G. stems for attribution scoring (done client-side after teardown)

Output: JSON + transcript under scripts/bankrepair20261004/.
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
EXPECTED_DB = "neondb"
EXPECTED_LABEL = "T-C04-CAMPAIGN"
BRANCH_NAME = "bankrepair-ro"

# the 4 targets: (paper_code, session_label, qnum)
TARGETS = [
    ("4CH0/1C", "June 2013", 10),
    ("4CH0/1C", "June 2017", 11),
    ("4CH0/1C", "June 2018", 12),
    ("4CH0/1CR", "June 2017", 11),
]

CORPUS_SHA = [
    "d9e5ef81faaccb51026796af0f05b86bb5c4cef991e4ab8a11157512d45ff189",  # 2013-06 1C qp
    "5e73646769942e9cd5745673e2f1103233f2efd221e76ca89648187c8839ae9c",  # 2013-06 1C ms
    "a4f7eb2c6d9b93fe678416af270b578acc567fd8a47cdfae1f3d98c9b6e4813b",  # 2017-06 1C qp
    "28008020cb90708bfe438195b02417a0bb7d57232e3094220ad808971aa29a75",  # 2017-06 1C ms
    "1ff0f7955d3fa61a03d10af626a3a4daa733cd719a987d3be7a784839e8905ae",  # 2018-06 1C qp
    "5381d95189fe3d5b4958ac2d2ab5636735aa458e7dffbca94b44b16f1eaa9b30",  # 2018-06 1C ms
    "fa8769bea3b6ef523b0e2c6a3f339fab8502ddf317ba7d9444cb8da034bc1c5b",  # 2017-06 1CR qp
    "f1b6e819adc5bfbdfb64c095c7b53d18b4b95dcdc1c5b6a63218c52e1d300eac",  # 2017-06 1CR ms
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
            d = json.load(urllib.request.urlopen(req, timeout=180))
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
    say(f"== bank-repair lane PROBE (SELECT-only) == {stamp}")
    say(f"project {PROJECT}; production {PRODUCTION_BRANCH} (READ-ONLY parent)")

    # idempotency: remove orphaned probe branches from prior aborted runs
    for b in api(key, f"/projects/{PROJECT}/branches").get("branches", []):
        if b["name"] == BRANCH_NAME:
            api(key, f"/projects/{PROJECT}/branches/{b['id']}", method="DELETE")
            say(f"A. pre-existing orphan probe branch {b['id']} deleted")

    rb_id = None
    try:
        br = api(key, f"/projects/{PROJECT}/branches", method="POST", body={
            "branch": {"name": BRANCH_NAME, "parent_id": PRODUCTION_BRANCH},
            "endpoints": [{"type": "read_write"}]})
        rb_id = br["branch"]["id"]
        say(f"A. probe branch created: {rb_id} (child of {PRODUCTION_BRANCH})")
        pw = api(key, f"/projects/{PROJECT}/branches/{rb_id}/roles/neondb_owner/reset_password",
                 method="POST", body={})
        rb_pw = pw["role"]["password"]
        say("A. throwaway neondb_owner password reset on the probe branch only")
    except SystemExit:
        if rb_id:
            api(key, f"/projects/{PROJECT}/branches/{rb_id}", method="DELETE", retries=1)
            say("teardown: probe branch DELETED (provision-abort path)")
        raise

    eps = api(key, f"/projects/{PROJECT}/branches/{rb_id}/endpoints")["endpoints"]
    host = eps[0]["host"]
    say(f"A. endpoint {host}")
    conn = f"postgresql://neondb_owner:{rb_pw}@{host}/neondb?sslmode=require"

    result = {"probe_utc": stamp, "probe_branch": rb_id, "endpoint": host,
              "production_branch": PRODUCTION_BRANCH}

    try:
        # ── B. identity gates ────────────────────────────────────────────
        rows = sql(conn, host, "select current_database() as db")
        if rows[0]["db"] != EXPECTED_DB:
            raise SystemExit("DB IDENTITY GATE FAILED")
        rows = sql(conn, host, "select campaign_label, claimed_at from campaign_db_identity where id = 1")
        if not rows or rows[0]["campaign_label"] != EXPECTED_LABEL:
            raise SystemExit(f"IDENTITY ROW GATE FAILED: {rows}")
        say(f"B. identity PASS ({EXPECTED_DB} / {EXPECTED_LABEL})")

        # ── C. shape probe ───────────────────────────────────────────────
        tbls = ["questions", "question_versions", "question_parts", "mark_schemes",
                "mark_points", "documents", "document_chunks", "exam_papers",
                "glm_ocr_bridge_records"]
        shape = {}
        for t in tbls:
            cols = sql(conn, host, f"""
                select column_name, data_type from information_schema.columns
                where table_name = '{t}' order by ordinal_position""")
            shape[t] = [c["column_name"] for c in cols]
        result["table_shapes"] = shape
        say("C. table shapes captured")
        for t in tbls:
            say(f"   {t}: {', '.join(shape[t])}")

        # ── D. resolve the 4 target rows (pull whole papers, match client-side) ──
        paper_rows = []
        for code, sess, qn in TARGETS:
            rows = sql(conn, host, f"""
                select p.id as paper_id, p.paper_code, p.session_label,
                       p.validation_state as paper_state, p.title,
                       p.question_paper_document_id, p.mark_scheme_document_id,
                       q.id as question_id, q.external_ref, q.active, q.marks as q_marks,
                       qv.id as qv_id, qv.version, qv.validation_state as qv_state,
                       qv.marks as qv_marks,
                       (select coalesce(sum(pp.marks),0)::int from question_parts pp
                         where pp.question_version_id = qv.id) as part_marks,
                       (select count(*)::int from question_parts pp
                         where pp.question_version_id = qv.id) as n_parts,
                       (select count(*)::int from mark_schemes m
                         where m.question_version_id = qv.id) as n_schemes,
                       (select count(*)::int from mark_points mp
                         join mark_schemes m2 on mp.mark_scheme_id = m2.id
                         where m2.question_version_id = qv.id) as n_mark_points,
                       (select count(*)::int from question_versions v2
                         where v2.question_id = q.id) as n_versions
                from exam_papers p
                join questions q on q.exam_paper_id = p.id
                join question_versions qv on qv.question_id = q.id
                 and qv.version = (select max(version) from question_versions v2
                                    where v2.question_id = q.id)
                where p.paper_code = '{code}' and p.session_label = '{sess}'
                order by q.id""")
            paper_rows.append({"paper": f"{code} {sess}", "qn": qn, "all_questions": rows})
            say(f"D. {code} {sess}: {len(rows)} question(s); serving qp={rows[0]['question_paper_document_id'] if rows else None} ms={rows[0]['mark_scheme_document_id'] if rows else None}")
        result["paper_rows"] = paper_rows

        # ── E. census pins (fresh) ───────────────────────────────────────
        census = {}
        census["papers"] = sql(conn, host, """select validation_state as st, count(*)::int as n
            from exam_papers group by 1 order by 1""")
        census["qv"] = sql(conn, host, """select count(*)::int as n,
            count(*) filter (where validation_state='VALIDATED')::int as n_validated,
            count(*) filter (where validation_state='SUGGESTED')::int as n_suggested,
            count(*) filter (where validation_state='REJECTED')::int as n_rejected
            from question_versions""")[0]
        census["questions"] = sql(conn, host, """select count(*)::int as n,
            count(*) filter (where active)::int as n_active from questions""")[0]
        census["parts"] = sql(conn, host, "select count(*)::int as n, coalesce(sum(marks),0)::int as marks from question_parts")[0]
        census["schemes"] = sql(conn, host, """select count(*)::int as n,
            count(*) filter (where validation_state='VALIDATED')::int as n_validated,
            count(*) filter (where validation_state='SUGGESTED')::int as n_suggested
            from mark_schemes""")[0]
        census["mark_points"] = sql(conn, host, "select count(*)::int as n from mark_points")[0]
        census["audit_max"] = sql(conn, host, "select coalesce(max(id),0)::int as n from content_review_audit")[0]["n"] if sql(conn, host, """select count(*)::int as n from information_schema.tables
            where table_name='content_review_audit'""")[0]["n"] else None
        census["bridge"] = sql(conn, host, """select reconciliation_status as st, count(*)::int as n
            from glm_ocr_bridge_records group by 1 order by 1""")
        result["census"] = census
        say(f"E. census: papers={[(r['st'], r['n']) for r in census['papers']]} "
            f"qv={census['qv']} questions={census['questions']} parts={census['parts']} "
            f"schemes={census['schemes']} mp={census['mark_points']} audit_max={census['audit_max']}")
        say(f"   bridge={[(r['st'], r['n']) for r in census['bridge']]}")

        # ── F. document identity + MS chunk corroboration ────────────────
        # F1: documents whose checksum matches the 8 corpus bytes
        inlist = ",".join(f"'{h}'" for h in CORPUS_SHA)
        rows = sql(conn, host, f"""
            select id, document_id, kind, checksum, validation_state, page_count,
                   (select count(*)::int from document_chunks c where c.document_row_id = d.id) as n_chunks,
                   (select count(*)::int from document_chunks c where c.document_row_id = d.id and c.embed_rev = 2) as n_chunks_rev2
            from documents d where lower(checksum) in ({inlist})""")
        result["corpus_docs_in_db"] = rows
        say(f"F1. documents matching the 8 corpus checksums: {len(rows)}")
        for r in rows:
            say(f"    {r['checksum'][:12]}… doc_id={r['document_id']} kind={r['kind']} "
                f"state={r['validation_state']} chunks={r['n_chunks']}/{r['n_chunks_rev2']}@rev2")

        # F2: bridge rows for the 4 papers
        conds = " or ".join(f"(p.paper_code='{c}' and p.session_label='{s}')" for c, s, _ in TARGETS)
        rows = sql(conn, host, f"""
            select b.id as bridge_id, p.paper_code, p.session_label,
                   b.reconciliation_status, b.qp_document_id, b.ms_document_id,
                   qp.validation_state as qp_state, ms.validation_state as ms_state
            from glm_ocr_bridge_records b
            join exam_papers p on p.id = b.paper_id
            left join documents qp on qp.document_id = b.qp_document_id
            left join documents ms on ms.document_id = b.ms_document_id
            where {conds} order by p.paper_code, p.session_label""")
        result["bridge_rows"] = rows
        say(f"F2. bridge rows for the 4 papers: {len(rows)}")
        for r in rows:
            say(f"    {r['paper_code']} {r['session_label']} bridge={r['bridge_id'][:8]}… "
                f"status={r['reconciliation_status']} qp={r['qp_state']} ms={r['ms_state']}")

        # F3: full chunk text of the SERVING MS + QP docs (p.*_document_id),
        #     corpus-checksum identity asserted per doc; parsed client-side
        sha_ms = {
            ("4CH0/1C", "June 2013"): "5e73646769942e9cd5745673e2f1103233f2efd221e76ca89648187c8839ae9c",
            ("4CH0/1C", "June 2017"): "28008020cb90708bfe438195b02417a0bb7d57232e3094220ad808971aa29a75",
            ("4CH0/1C", "June 2018"): "5381d95189fe3d5b4958ac2d2ab5636735aa458e7dffbca94b44b16f1eaa9b30",
            ("4CH0/1CR", "June 2017"): "f1b6e819adc5bfbdfb64c095c7b53d18b4b95dcdc1c5b6a63218c52e1d300eac",
        }
        sha_qp = {
            ("4CH0/1C", "June 2013"): "d9e5ef81faaccb51026796af0f05b86bb5c4cef991e4ab8a11157512d45ff189",
            ("4CH0/1C", "June 2017"): "a4f7eb2c6d9b93fe678416af270b578acc567fd8a47cdfae1f3d98c9b6e4813b",
            ("4CH0/1C", "June 2018"): "1ff0f7955d3fa61a03d10af626a3a4daa733cd719a987d3be7a784839e8905ae",
            ("4CH0/1CR", "June 2017"): "fa8769bea3b6ef523b0e2c6a3f339fab8502ddf317ba7d9444cb8da034bc1c5b",
        }
        doc_texts = []
        for code, sess, qn in TARGETS:
            pr = [p for p in paper_rows if p["paper"] == f"{code} {sess}"][0]["all_questions"]
            if not pr:
                continue
            r0 = pr[0]
            for role, docid, want_sha in (("ms", r0["mark_scheme_document_id"], sha_ms[(code, sess)]),
                                          ("qp", r0["question_paper_document_id"], sha_qp[(code, sess)])):
                drows = sql(conn, host, f"""
                    select id, document_id, kind, checksum, validation_state
                    from documents where document_id = '{docid}'""")
                if not drows:
                    say(f"F3. {code} {sess} {role}: serving doc {docid} NOT FOUND in documents")
                    doc_texts.append({"paper": f"{code} {sess}", "role": role, "doc_id": docid,
                                      "found": False})
                    continue
                d = drows[0]
                sha_ok = str(d["checksum"]).lower() == want_sha
                crows = sql(conn, host, f"""
                    select c.id as chunk_id, c.chunk_index, c.kind as chunk_kind, c.content as txt
                    from document_chunks c where c.document_row_id = '{d['id']}'
                    order by c.chunk_index""")
                doc_texts.append({"paper": f"{code} {sess}", "role": role, "doc_id": docid,
                                  "doc_row": d["id"], "kind": d["kind"], "checksum": d["checksum"],
                                  "checksum_matches_corpus": sha_ok,
                                  "validation_state": d["validation_state"],
                                  "chunks": [{"chunk_id": c["chunk_id"], "chunk_index": c["chunk_index"],
                                              "kind": c["chunk_kind"], "text": c["txt"]} for c in crows]})
                say(f"F3. {code} {sess} {role} doc {str(docid)[:14]}…: state={d['validation_state']} "
                    f"chunks={len(crows)} checksum-match-corpus={sha_ok}")
        result["serving_doc_texts"] = doc_texts

        # ── G. stems for attribution (client-side scoring later) ─────────
        stems = []
        for code, sess, qn in TARGETS:
            prows_all = [p for p in paper_rows if p["paper"] == f"{code} {sess}"][0]["all_questions"]
            cands = [r for r in prows_all
                     if str(r["external_ref"] or "").lower().startswith(f"q{qn:02d}-")
                     or str(r["external_ref"] or "").lower().startswith(f"q{qn}-")]
            say(f"G. {code} {sess} q{qn}: {len(cands)} candidate ref(s) "
                f"{[c['external_ref'] for c in cands]}")
            for r in cands:
                srows = sql(conn, host, f"""
                    select q.stem as q_stem, qv.stem as qv_stem
                    from questions q join question_versions qv on qv.question_id = q.id
                    where q.id = '{r['question_id']}' and qv.id = '{r['qv_id']}'""")
                pprows = sql(conn, host, f"""
                    select pp.id as part_id, pp.label, pp.prompt, pp.marks
                    from question_parts pp where pp.question_version_id = '{r['qv_id']}'
                    order by pp.ordering limit 20""")
                stems.append({"paper": f"{code} {sess}", "qn": qn,
                              "external_ref": r["external_ref"],
                              "question_id": r["question_id"], "qv_id": r["qv_id"],
                              "q_stem": srows[0]["q_stem"] if srows else None,
                              "qv_stem": srows[0]["qv_stem"] if srows else None,
                              "parts": pprows})
        result["stems"] = stems
        say(f"G. stems captured for {len(stems)} targets")

    finally:
        # ── teardown: delete branch, credential dies with it ─────────────
        try:
            api(key, f"/projects/{PROJECT}/branches/{rb_id}", method="DELETE", retries=2)
            say("TEARDOWN: probe branch DELETED (credential dead)")
            result["teardown"] = "deleted"
        except SystemExit as ex:
            say(f"TEARDOWN FAILED — delete branch {rb_id} manually: {ex}")
            result["teardown"] = f"FAILED: {ex}"

    json.dump(result, open(f"{OUT_DIR}/probe_result.json", "w"), indent=1, default=str)
    open(f"{OUT_DIR}/probe_output.txt", "w").write("\n".join(_lines) + "\n")
    say(f"written: {OUT_DIR}/probe_result.json")


if __name__ == "__main__":
    main()
