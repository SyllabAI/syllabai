#!/usr/bin/env python3
"""tc80_preflight.py — T-C80 preflight probes (READ-ONLY, SELECT-only).

Lane authority: operator trace 1a10622b96c017d5 ("the 3 narrowed
2016-family rows (MS prints no totals), the engine-grade grid-layout
lane,"). Records: syllabai T-C80 (claim dd60112, Session 189).

Access recipe: the M6-era Render-PAT direct recipe (scripts/m6_prod_verify.py
precedent) — Render API service env-vars -> direct pg8000 connection.
The Neon COW-branch recipe needs a Neon session key which does NOT exist
in this sandbox; direct SELECT-only probes are the established read-only
alternative (M6/data-fix lanes). ZERO writes here; all writes go through
core Flyway on deploy.

Probes:
  A. identity gates (current_database, campaign identity, server version)
  B. census pins (post-V61 state, from the Session 188 receipt)
  C. the two grid-lane qv refs full state (q03-51fea326, q10-5273dfa3)
  D. the 4 papers' exam_paper rows + serving doc ids + checksums
  E. banked questions on the 3 June-2016 papers (Lane A cross-check)
  F. mark_schemes / mark_points schema (INSERT shape for the fill)

Output: JSON + transcript under scripts/tc80-lane/. Secrets never printed.
"""
import json
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import pg8000.native

PROJ = Path("/home/z/my-project")
PAT = (PROJ / ".render_token").read_text().strip()
SVC = "srv-dagijie7bikc73bc0460"
OUT = PROJ / "scripts" / "tc80-lane"

env = json.load(urllib.request.urlopen(urllib.request.Request(
    f"https://api.render.com/v1/services/{SVC}/env-vars",
    headers={"Authorization": f"Bearer {PAT}", "Accept": "application/json"}),
    timeout=30))
env = {i["envVar"]["key"]: i["envVar"]["value"] for i in env}
u = urlparse(env["SYLLABAI_DATABASE_URL"].replace("jdbc:postgresql://",
                                                  "postgresql://", 1))
result = {"probes": {}}

_conn_args = dict(
    user=env["SYLLABAI_DATABASE_USERNAME"],
    password=env["SYLLABAI_DATABASE_PASSWORD"],
    host=u.hostname, port=u.port or 5432,
    database=u.path.lstrip("/"), ssl_context=True)
_con = None


def conn():
    global _con
    if _con is None:
        _con = pg8000.native.Connection(**_conn_args)
    return _con


def q(sql, args=None):
    """Run SELECT with one reconnect retry (Neon pgbouncer drops idle conns)."""
    global _con
    if args:
        raise SystemExit("no params by design — inline literals only")
    try:
        return conn().run(sql)
    except Exception:
        try:
            _con.close()
        except Exception:
            pass
        _con = None
        return conn().run(sql)


# A. identity gates
db, ver = q("SELECT current_database(), version()")[0][:2]
ident = q("SELECT * FROM campaign_db_identity")
result["probes"]["A_identity"] = {
    "database": db, "server": ver.split(",")[0],
    "campaign_identity": [list(map(str, r)) for r in ident],
}
print("A. database:", db, "| identity rows:", len(ident))

# B. census pins (post-V61 receipt, Session 188)
pins = {}
pins["papers"] = q("SELECT validation_state, count(*) FROM exam_papers GROUP BY validation_state ORDER BY validation_state")
pins["question_versions"] = q("SELECT validation_state, count(*) FROM question_versions GROUP BY validation_state ORDER BY validation_state")
pins["questions"] = q("SELECT count(*), count(*) FILTER (WHERE active) FROM questions")[0]
pins["parts"] = q("SELECT count(*), coalesce(sum(marks),0) FROM question_parts")[0]
pins["schemes"] = q("SELECT validation_state, count(*) FROM mark_schemes GROUP BY validation_state ORDER BY validation_state")
pins["mark_points"] = q("SELECT count(*) FROM mark_points")[0][0]
pins["marks_sums"] = {
    "questions": q("SELECT coalesce(sum(marks),0) FROM questions")[0][0],
    "question_versions": q("SELECT coalesce(sum(marks),0) FROM question_versions")[0][0],
}
pins["bridge"] = q("SELECT reconciliation_status, count(*) FROM glm_ocr_bridge_records GROUP BY reconciliation_status ORDER BY reconciliation_status")
pins["flyway_latest"] = q("SELECT version, description, success FROM flyway_schema_history ORDER BY installed_rank DESC LIMIT 3")
result["probes"]["B_census"] = {
    "papers": [list(r) for r in pins["papers"]],
    "qv": [list(r) for r in pins["question_versions"]],
    "questions_total_active": list(pins["questions"]),
    "parts_count_sum": list(pins["parts"]),
    "schemes": [list(r) for r in pins["schemes"]],
    "mark_points": pins["mark_points"],
    "marks_sums": pins["marks_sums"],
    "bridge": [list(r) for r in pins["bridge"]],
    "flyway_latest": [list(map(str, r)) for r in pins["flyway_latest"]],
}
print("B. census:", json.dumps(result["probes"]["B_census"]["flyway_latest"]))

# C. the two grid-lane qv refs
refs = ["q03-51fea326", "q10-5273dfa3"]
crows = {}
for ref in refs:
    rows = q(f"""
        SELECT qv.id, q.external_ref, qv.marks, qv.version, qv.validation_state,
               q.id AS question_id, q.marks AS q_marks, q.active,
               p.id AS paper_id, p.paper_code, p.session_label,
               (SELECT count(*) FROM mark_schemes ms WHERE ms.question_version_id = qv.id) AS schemes,
               (SELECT count(*) FROM mark_points mp JOIN mark_schemes ms ON mp.mark_scheme_id = ms.id
                 WHERE ms.question_version_id = qv.id) AS points,
               (SELECT coalesce(sum(mp.marks),0) FROM mark_points mp JOIN mark_schemes ms ON mp.mark_scheme_id = ms.id
                 WHERE ms.question_version_id = qv.id) AS point_sum,
               qv.source_document_id AS qv_source_doc
        FROM questions q
        JOIN question_versions qv ON qv.question_id = q.id
        LEFT JOIN exam_papers p ON p.id = q.exam_paper_id
        WHERE q.external_ref LIKE '{ref}%'
        ORDER BY qv.version
    """)
    crows[ref] = [list(map(str, r)) for r in rows]
result["probes"]["C_gridlane_qv"] = crows
print("C. grid-lane qv:", json.dumps(crows))

# D. the 4 papers + serving docs
papers = q("""
    SELECT p.id, p.paper_code, p.session_label, p.validation_state,
           p.question_paper_document_id, p.mark_scheme_document_id,
           dqp.checksum AS qp_checksum, dms.checksum AS ms_checksum,
           dqp.validation_state AS qp_doc_state, dms.validation_state AS ms_doc_state
    FROM exam_papers p
    LEFT JOIN documents dqp ON dqp.document_id = p.question_paper_document_id
    LEFT JOIN documents dms ON dms.document_id = p.mark_scheme_document_id
    WHERE (p.paper_code IN ('4CH0/1C','4CH0/1CR','4CH0/2CR') AND p.session_label = 'June 2016')
       OR (p.paper_code = '4CH0/2C' AND p.session_label = 'January 2013')
    ORDER BY p.paper_code, p.session_label
""")
result["probes"]["D_papers"] = [list(map(str, r)) for r in papers]
print("D. papers:", len(papers), "rows")

# E. banked questions on the 3 June-2016 papers
banked = q("""
    SELECT p.paper_code, q.external_ref, qv.version, qv.marks, q.marks, qv.validation_state, q.active
    FROM exam_papers p
    JOIN questions q ON q.exam_paper_id = p.id
    JOIN question_versions qv ON qv.question_id = q.id
    WHERE (p.paper_code IN ('4CH0/1C','4CH0/1CR','4CH0/2CR') AND p.session_label = 'June 2016')
    ORDER BY p.paper_code, q.external_ref, qv.version
""")
result["probes"]["E_banked_2016"] = [list(map(str, r)) for r in banked]
print("E. banked questions on June-2016 papers:", len(banked))

# G. scheme provenance for the two grid-lane qvs (drift forensics)
gschemes = q("""
    SELECT ms.id, ms.version_label, ms.validation_state, ms.extraction_method,
           ms.source_document_id, ms.created_at,
           (SELECT count(*) FROM mark_points mp WHERE mp.mark_scheme_id = ms.id) AS points,
           (SELECT coalesce(sum(mp.marks),0) FROM mark_points mp WHERE mp.mark_scheme_id = ms.id) AS point_sum,
           d.checksum AS src_checksum, d.source_uri
    FROM mark_schemes ms
    LEFT JOIN documents d ON d.document_id = ms.source_document_id
    WHERE ms.question_version_id IN ('e6a160c7-cb91-46dc-bc3d-cbe15c3df826',
                                     '65aff0a8-bbfd-49f7-957b-63d0dddf169c')
    ORDER BY ms.created_at
""")
result["probes"]["G_scheme_provenance"] = [list(map(str, r)) for r in gschemes]
gpoints = q("""
    SELECT mp.mark_scheme_id, mp.ref, mp.ordering, mp.marks, mp.text
    FROM mark_points mp
    WHERE mp.mark_scheme_id IN (SELECT id FROM mark_schemes WHERE question_version_id IN
        ('e6a160c7-cb91-46dc-bc3d-cbe15c3df826','65aff0a8-bbfd-49f7-957b-63d0dddf169c'))
    ORDER BY mp.mark_scheme_id, mp.ordering
""")
result["probes"]["G_points"] = [list(map(str, r)) for r in gpoints]
print("G. scheme provenance rows:", len(gschemes), "| points:", len(gpoints))

# F. mark_schemes / mark_points schema
cols = q("""
    SELECT table_name, column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_schema='public' AND table_name IN ('mark_schemes','mark_points')
    ORDER BY table_name, ordinal_position
""")
result["probes"]["F_schema"] = [list(map(str, r)) for r in cols]
print("F. schema rows:", len(cols))

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "preflight_result.json").write_text(json.dumps(result, indent=1))
print("\nsaved ->", OUT / "preflight_result.json")
