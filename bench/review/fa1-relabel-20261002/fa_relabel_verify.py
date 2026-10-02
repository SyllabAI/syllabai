#!/usr/bin/env python3
"""T-C66 stage-4: INDEPENDENT fresh-connection verification of the applied
source_uri relabel (batch_run_id bf3485f8-e504-47bc-b1ce-a29fbbdb725d) plus the
census-last re-pin bundle. SELECT-only; separate connection from the apply run."""
import json, pathlib, re, sys, datetime
import psycopg2

ENV = json.loads(pathlib.Path("/home/z/my-project/scripts/.render_env.json").read_text())["env"]
E = {e["key"]: e["value"] for e in ENV}
m = re.match(r"jdbc:postgresql://([^:/?+]+)(?::(\d+))?/([^?]+)", E["SYLLABAI_DATABASE_URL"])
conn = psycopg2.connect(host=m.group(1), port=m.group(2) or "5432", dbname=m.group(3),
                        user=E["SYLLABAI_DATABASE_USERNAME"], password=E["SYLLABAI_DATABASE_PASSWORD"],
                        sslmode="require", connect_timeout=30)
conn.set_session(readonly=True, autocommit=True)
cur = conn.cursor()

BATCH_RUN_ID = "bf3485f8-e504-47bc-b1ce-a29fbbdb725d"
plan = json.loads(open("/home/z/my-project/tool-results/fa_recon/relabel_plan.json").read())
rows = plan["plan"]
out = {"batch_run_id": BATCH_RUN_ID, "checks": {}}
fails = []

def check(name, cond, detail=""):
    out["checks"][name] = {"pass": bool(cond), "detail": detail}
    if not cond:
        fails.append(name)

# 1) all 16 rows at new URIs, everything else byte-identical
cur.execute("""
    select d.id::text, d.source_uri, d.checksum, d.validation_state, d.kind,
           count(c.id) chunks, count(c.embedding) embedded
    from documents d left join document_chunks c on c.document_row_id = d.id
    where d.id::text = any(%s) group by d.id, d.source_uri, d.checksum, d.validation_state, d.kind
""", ([r["row_id"] for r in rows],))
live = {r[0]: r for r in cur.fetchall()}
ok = len(live) == 16 and all(
    live[r["row_id"]][1] == r["new_source_uri"] and live[r["row_id"]][2] == r["checksum"]
    and live[r["row_id"]][3] == "VALIDATED" and live[r["row_id"]][4] == r["kind"]
    and live[r["row_id"]][5] == r["chunks"] and live[r["row_id"]][6] == r["chunks"]
    for r in rows)
check("rows16_at_new_uri_state_sha_chunks_intact", ok,
      f"{sum(1 for r in rows if live.get(r['row_id'],[None]*7)[1]==r['new_source_uri'])}/16 at target")

# 2) none of the 16 rows still holds an old URI; each old URI now held only by the 09-28 sibling
cur.execute("""
    select d.source_uri, d.id::text, d.created_at::text from documents d
    where d.source_uri in (select unnest(%s::text[]))
""", ([r["old_source_uri"] for r in rows],))
by_old = {}
for uri, rid, created in cur.fetchall():
    by_old.setdefault(uri, []).append((rid, created))
ok2 = all(r["row_id"] not in {x[0] for x in by_old.get(r["old_source_uri"], [])} for r in rows)
check("old_uris_released_by_targets", ok2,
      "; ".join(f"{u}: {len(v)} holder(s)" for u, v in sorted(by_old.items())[:4]) + " …")

# 3) target URI uniqueness: exactly one holder per target
cur.execute("""
    select lower(source_uri), count(*) from documents
    where lower(source_uri) = any(%s) group by 1
""", ([r["new_source_uri"].lower() for r in rows],))
counts = dict(cur.fetchall())
check("target_uris_unique_holders", all(counts.get(r["new_source_uri"].lower()) == 1 for r in rows),
      str(counts))

# 4) audit rows: 16 PLACE rows with batch_run_id + verbatim decision text + old/new URIs
cur.execute("""
    select id, occurred_at::text, actor_label, action, target_type, from_state, to_state, detail
    from content_review_audit where detail like %s order by id
""", (f"%{BATCH_RUN_ID}%",))
audit = cur.fetchall()
det_ok = 0
for a in audit:
    d = json.loads(a[7])
    if (a[3] == "PLACE" and a[4] == "document" and a[5] == "VALIDATED" and a[6] == "VALIDATED"
            and d.get("operator_trace_id") == "1a0fcf4d0a035c8d"
            and d.get("decision_text") == "① Relabel source_uri on line"
            and d.get("batch") == "fa1-relabel-2026-10-02"
            and "old_source_uri" in d and "new_source_uri" in d):
        det_ok += 1
check("audit_16_place_rows_verbatim", len(audit) == 16 and det_ok == 16,
      f"{len(audit)} rows, {det_ok} fully conforming")

# 5) ep topology intact: 16 VALIDATED refs, 8 distinct ep rows, both slots each
cur.execute("""
    select p.id::text, p.paper_code, p.session_label, p.validation_state,
           (p.question_paper_document_id = d.document_id) qp, (p.mark_scheme_document_id = d.document_id) ms
    from documents d join exam_papers p
      on p.question_paper_document_id = d.document_id or p.mark_scheme_document_id = d.document_id
    where d.id::text = any(%s)
""", ([r["row_id"] for r in rows],))
ep = cur.fetchall()
eps = {}
for pid, code, sess, st, qp, ms in ep:
    e = eps.setdefault(pid, {"code": code, "sess": sess, "st": st, "qp": False, "ms": False})
    e["qp"] |= qp; e["ms"] |= ms
ok5 = (len(ep) == 16 and len(eps) == 8
       and all(v["st"] == "VALIDATED" and v["qp"] and v["ms"] and v["code"] in ("4CH0/1CR", "4CH0/2CR")
               for v in eps.values()))
check("ep_topology_intact_8_rows_both_slots", ok5, f"{len(eps)} ep rows, {len(ep)} refs")

# 6) URI identity alignment: target dir token == ep paper_code (slash form)
align = all(
    live[r["row_id"]][1].split("/")[0].replace("-", "/", 1).replace("CR-", "CR/") == None or True
    for r in rows)  # informational only; real alignment check below
mismatch = []
for r in rows:
    target_code = r["new_source_uri"].split("/")[0].rsplit("-", 1)[0]  # 4CH0-1CR
    official = r["corpus_official_reference"]                           # 4CH0/1CR
    if target_code != official.replace("/", "-"):
        mismatch.append((r["new_source_uri"], official))
check("target_code_matches_corpus_official_reference", not mismatch, f"{len(mismatch)} mismatches")

# 7) census re-pin (census-last) — full bundle
def q1(sql):
    cur.execute(sql); return cur.fetchone()[0]

cur.execute("select validation_state, kind, count(*) from documents group by 1,2 order by 1,2")
state_kind = {f"{a}|{b}": c for a, b, c in cur.fetchall()}
cur.execute("select coalesce(embed_rev::text,'null') rev, count(*) n, count(embedding) embedded from document_chunks group by 1 order by 1")
chunks = {r[0]: {"chunks": r[1], "embedded": r[2]} for r in cur.fetchall()}
cur.execute("select validation_state, count(*) from exam_papers group by 1")
ep_states = dict(cur.fetchall())
bundle = {
    "name": "census_bundle_fa1_relabel_20261002.json",
    "base": f"post fa1-relabel-2026-10-02 (run {BATCH_RUN_ID}) — census-last",
    "pins": {
        "docs_state_x_kind": state_kind,
        "docs_total": q1("select count(*) from documents"),
        "chunks_by_rev": chunks,
        "ep_rows": q1("select count(*) from exam_papers"),
        "ep_states": ep_states,
        "audit_rows": q1("select count(*) from content_review_audit"),
        "teacher_validation_events": q1("select count(*) from teacher_validation_events"),
        "mark_schemes_total": q1("select count(*) from mark_schemes"),
        "mark_points": q1("select count(*) from mark_points"),
        "question_spec_points": q1("select count(*) from question_spec_points"),
        "knowledge_nodes": q1("select count(*) from knowledge_nodes"),
    },
}
cur.execute("select id::text, code from curriculum_versions where status='ACTIVE' order by created_at desc")
act = cur.fetchone()
bundle["pins"]["active_cv"] = {"id": act[0], "code": act[1]}
cur.execute("""
    select count(*) from document_chunks c
    join documents d on d.id = c.document_row_id
    where c.embedding is not null and c.embed_rev = 2
      and (exists (
            select 1 from exam_papers p join subjects s on s.id = p.subject_id
            where s.curriculum_version_id = %s
              and p.validation_state = 'VALIDATED'
              and (p.question_paper_document_id = d.document_id
                or p.mark_scheme_document_id = d.document_id))
       or exists (
            select 1 from subjects s2
            where s2.curriculum_version_id = %s
              and s2.id = c.subject_id
              and d.validation_state = 'VALIDATED'))
""", (act[0], act[0]))
bundle["pins"]["search_serving_eligible_gate"] = cur.fetchone()[0]
cur.execute("select validation_state, count(*) from mark_schemes group by 1")
bundle["pins"]["mark_schemes_states"] = dict(cur.fetchall())
out["census_bundle"] = bundle

# census-vs-pre equality (everything except audit must equal the fa1 baseline)
pre = {"REJECTED|MARK_SCHEME": 67, "REJECTED|QUESTION_PAPER": 79, "VALIDATED|EXTERNAL_NOTES": 112,
       "VALIDATED|EXTERNAL_QUESTIONS": 379, "VALIDATED|MARK_SCHEME": 109,
       "VALIDATED|QUESTION_PAPER": 109, "VALIDATED|SYLLABUS": 162}
check("census_unchanged_vs_fa1_baseline", state_kind == pre and
      bundle["pins"]["docs_total"] == 1017 and bundle["pins"]["ep_rows"] == 104
      and ep_states == {"REJECTED": 13, "VALIDATED": 91}
      and chunks == {"2": {"chunks": 4672, "embedded": 4672}}
      and bundle["pins"]["teacher_validation_events"] == 0
      and bundle["pins"]["search_serving_eligible_gate"] == 4593
      and bundle["pins"]["audit_rows"] == 2814,
      json.dumps({k: bundle["pins"][k] for k in ("docs_total", "ep_rows", "audit_rows")}, default=str))

print(json.dumps({"status": "VERIFIED" if not fails else "FAILED", "fails": fails,
                  "census_bundle": bundle}, indent=1, default=str))
pathlib.Path("/home/z/my-project/tool-results/fa_recon/relabel_verify.json").write_text(
    json.dumps(out, indent=1, default=str))
sys.exit(0 if not fails else 1)
