#!/usr/bin/env python3
"""T-C66 stage-1 READ-ONLY probe: the 16 4CH0 R-generation rows ahead of the
governed source_uri relabel (operator trace 1a0fcf4d0a035c8d, "① Relabel
source_uri"). SELECT-only: no writes anywhere."""
import json, pathlib, re, sys
import psycopg2

ENV = json.loads(pathlib.Path("/home/z/my-project/scripts/.render_env.json").read_text())["env"]
E = {e["key"]: e["value"] for e in ENV}
m = re.match(r"jdbc:postgresql://([^:/?]+)(?::(\d+))?/([^?]+)", E["SYLLABAI_DATABASE_URL"])
conn = psycopg2.connect(host=m.group(1), port=m.group(2) or "5432", dbname=m.group(3),
                        user=E["SYLLABAI_DATABASE_USERNAME"], password=E["SYLLABAI_DATABASE_PASSWORD"],
                        sslmode="require", connect_timeout=30)
conn.set_session(readonly=True, autocommit=True)
cur = conn.cursor()
out = {}

def q(key, sql, args=None):
    cur.execute(sql, args if args is not None else None)
    cols = [d[0] for d in cur.description]
    out[key] = [dict(zip(cols, r)) for r in cur.fetchall()]

# --- identity gate ---
cur.execute("select current_database()")
out["database"] = cur.fetchone()[0]
q("campaign_identity", "select id, campaign_label, db_name from campaign_db_identity where id = 1")

# --- the 16 target rows (row ids from fa1_ep_topology.json) ---
ROWS16 = [
 ("a0efc38b-2397-4078-b772-6f6a79f12da2","8936b097-52a6-57f7-a6cb-b464c6524d49","4CH0-1C-201306/ms.pdf","b45e7d8549f7f3fd7029d8b9d9ff5ab1c8483c435823503981e40db825294a3e"),
 ("0da22314-cd97-4a8f-9a3d-bfac859b7c90","712079d5-3b8c-58a4-9569-e1c803364520","4CH0-1C-201406/ms.pdf","b81fd2bc25bac1fb611e44b68b38d6f771ae1aca261f4c84962ddcd8f437a026"),
 ("4aa18ec4-5398-4bb2-9c09-d7a9c7414c27","b27f9358-bd57-5545-8c69-aeeb5cdbd476","4CH0-1C-201606/ms.pdf","cfe40a1bb0954221cd71a43bdfca46eecd3707818b29264cdefb2a6f7f2eabda"),
 ("7122d0b5-eebe-4e67-b9ca-6ea81b949d6d","7195d701-ad3b-5667-8d4c-1dd743021e27","4CH0-1C-201706/ms.pdf","f1b6e819adc5bfbdfb64c095c7b53d18b4b95dcdc1c5b6a63218c52e1d300eac"),
 ("58755452-9e92-4903-9c0f-66cb1668a982","1d17abcc-fb53-5115-b266-911fbab52ab9","4CH0-2C-201306/ms.pdf","8aacda5ad15110f8ab88ae158afbf6ab1af475ebab59f99f16be2840585d3a6c"),
 ("cd1607f7-6c6b-401a-9051-19d97f6760d8","e0a32b5b-dcd1-5eea-bdf8-604c6dc36ef4","4CH0-2C-201406/ms.pdf","3f6d336dc271c76ae2d882ec0b5d2b137879768288e26bc7ae8593a3119b1ee5"),
 ("11a85cd3-3fab-4750-9710-6f24aadb374a","9fcd9d72-6811-5985-b3c2-af93a25f97ca","4CH0-2C-201606/ms.pdf","95ede68db0160975035273a5460bf94725aa970bab2139a431a293df46265ad0"),
 ("676bde63-f57a-4707-b239-335d78022704","a03f9ddf-8f22-54ea-aa64-68e8304bca9a","4CH0-2C-201706/ms.pdf","8f78764dd2c1e35423ec2821cdf61004a71b80b3db3cf1ba054e6fb19f92e11e"),
 ("dd3cb429-2231-4319-ae07-5d5e6f3bf1e6","2f52e30b-1dc7-5b6a-8e0e-84ddb845ce8a","4CH0-1C-201306/qp.pdf","bdbf981128aa3ef1392480c4da928aa13f70597219fa7694a35006569ec75722"),
 ("6eb3a67b-e95c-486c-99c9-5a9a1ee5d781","7762dfe6-4b6a-51b9-800f-32049f0f7ff6","4CH0-1C-201406/qp.pdf","b1fa10107dad8964471cf4bd0b119f520bc56c65daf15d1eabc67c34b65d5da0"),
 ("a7f145ae-ca0d-4226-a08d-a5b2717b1436","78510d0f-ae39-5d13-9126-70e6c4940d41","4CH0-1C-201606/qp.pdf","d5d0f929000f076cfd5e753ac711646ba8c33d3819dcef189e64127448dd8b2d"),
 ("f5428103-e451-47dd-b61c-2fc220c6aaf6","c6437e05-c992-5844-b3d2-a71991795044","4CH0-1C-201706/qp.pdf","fa8769bea3b6ef523b0e2c6a3f339fab8502ddf317ba7d9444cb8da034bc1c5b"),
 ("853ae02d-0090-4c40-89ef-b69681c8bb40","33ba399c-4640-5b04-b1bb-b520fa2ba94c","4CH0-2C-201306/qp.pdf","9394357770611a6a9d6653ea2f9715bfa7a0198fec8a59ec254ac2235bc1f774"),
 ("8690ac3e-6b4e-4e50-afd2-88e343574226","712f005c-55bb-543b-8237-e5dc0d873265","4CH0-2C-201406/qp.pdf","aa1b11cff9c757c6805cf0fe2c0b0b8975c161e73b9efdbda6cc339bc8ed178b"),
 ("66a2b835-1ea6-4ba8-a49e-631a552cd63b","e075a114-11fc-5994-828b-435dea3d824c","4CH0-2C-201606/qp.pdf","af18b5e37a089345ebff06e7ed04d0e5d414943c23b49425ca07311c125ccd2d"),
 ("d8f94fa2-a872-4896-903a-60f156635478","e9ebba09-cfa9-5fcf-86ad-f4624448f4f5","4CH0-2C-201706/qp.pdf","50d9308f0b5534aee8c0c27d5387e84d73e156158154bdbc34394d08fd9d0d43"),
]
out["expected_rows"] = len(ROWS16)

q("rows16_state", """
    select d.id::text row_id, d.document_id::text document_id, d.kind, d.source_uri,
           d.checksum, d.validation_state, d.file_name,
           count(c.id) chunks, count(c.embedding) embedded
    from documents d left join document_chunks c on c.document_row_id = d.id
    where d.id::text = any(%s)
    group by d.id, d.document_id, d.kind, d.source_uri, d.checksum, d.validation_state, d.file_name
    order by d.source_uri
""", ([r[0] for r in ROWS16],))

# ep topology (correct join: exam_papers.*_document_id = documents.document_id)
q("rows16_ep_topology", """
    select d.document_id::text doc, p.id::text ep_id, p.validation_state ep_state,
           p.paper_code, p.session_label, p.qualification, p.unit,
           (p.question_paper_document_id = d.document_id) qp_slot,
           (p.mark_scheme_document_id = d.document_id) ms_slot
    from documents d
    join exam_papers p on p.question_paper_document_id = d.document_id
                      or p.mark_scheme_document_id = d.document_id
    where d.id::text = any(%s)
    order by p.session_label, p.paper_code
""", ([r[0] for r in ROWS16],))

# generation map: every live doc sharing any of the 16 source_uris
q("generation_map", """
    select d.source_uri, d.id::text row_id, d.document_id::text document_id, d.kind,
           d.validation_state, d.checksum, d.created_at::text, d.source_engine,
           count(c.id) chunks
    from documents d left join document_chunks c on c.document_row_id = d.id
    where d.source_uri in (select source_uri from documents where id::text = any(%s))
    group by d.source_uri, d.id, d.document_id, d.kind, d.validation_state, d.checksum, d.created_at, d.source_engine
    order by d.source_uri, d.created_at
""", ([r[0] for r in ROWS16],))

# --- target collision + convention probe ---
targets = [r[2].replace("-1C-", "-1CR-").replace("-2C-", "-2CR-") for r in ROWS16]
out["targets"] = targets
cur.execute("""
    select d.source_uri, d.id::text row_id, d.validation_state, d.kind
    from documents d
    where lower(d.source_uri) = any(%s)
""", ([t.lower() for t in targets],))
out["target_collisions"] = [dict(zip([c[0] for c in cur.description], r)) for r in cur.fetchall()]

q("r_uri_convention_live", """
    select d.source_uri, d.id::text row_id, d.validation_state, d.kind, d.checksum
    from documents d
    where d.source_uri ~* '^4CH0-[12]CR'
    order by d.source_uri
""")

q("documents_columns", """
    select column_name, data_type from information_schema.columns
    where table_name='documents' order by ordinal_position""")

# --- census baseline (mirror census_bundle_fa1 pins) ---
q("census_state_kind", "select validation_state, kind, count(*) from documents group by 1,2 order by 1,2")
cur.execute("select count(*) from documents"); out["docs_total"] = cur.fetchone()[0]
q("chunks_by_rev", """
    select coalesce(embed_rev::text,'null') rev, count(*) n, count(embedding) embedded
    from document_chunks group by 1 order by 1""")
q("ep_states", "select validation_state, count(*) from exam_papers group by 1")
cur.execute("select count(*) from exam_papers"); out["ep_total"] = cur.fetchone()[0]
cur.execute("select count(*) from content_review_audit"); out["audit_rows"] = cur.fetchone()[0]
cur.execute("select count(*) from teacher_validation_events"); out["tve"] = cur.fetchone()[0]

def try_count(key, table):
    try:
        cur.execute(f"select count(*) from {table}")
        out[key] = cur.fetchone()[0]
    except Exception as e:  # noqa: BLE001 — census tolerates schema drift, mirrors fa1 bundle
        conn.rollback()
        out[key] = f"ERR {type(e).__name__}"

q("tables_like_scheme", """
    select table_name from information_schema.tables
    where table_schema='public' and (table_name like '%scheme%' or table_name like '%mark_point%'
      or table_name like '%spec_point%' or table_name like '%knowledge%') order by 1""")

for key, tbl in [("schemes_total", "schemes"), ("mark_points", "mark_points"),
                 ("question_spec_points", "question_spec_points"),
                 ("knowledge_nodes", "knowledge_nodes")]:
    try_count(key, tbl)
try:
    cur.execute("select validation_state, count(*) from schemes group by 1")
    out["schemes_states"] = dict(cur.fetchall())
except Exception as e:  # noqa: BLE001
    conn.rollback()
    out["schemes_states"] = f"ERR {type(e).__name__}"

# ACTIVE cv + exact searchServingEligible replica
cur.execute("select id, code from curriculum_versions where status='ACTIVE' order by created_at desc")
act = cur.fetchall()
assert len(act) == 1, f"ACTIVE cv count {len(act)}"
out["active_cv"] = {"id": str(act[0][0]), "code": act[0][1]}
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
""", (str(act[0][0]), str(act[0][0])))
out["gate_replica_rev2"] = cur.fetchone()[0]

# latest audit rows — concurrent activity watch
q("audit_latest", """
    select id, occurred_at::text, actor_label, action, target_type,
           from_state, to_state, left(detail, 160) detail_head
    from content_review_audit order by occurred_at desc, id desc limit 12""")

# audit table constraints (allowed actions / target types)
q("audit_constraints", """
    select conname, pg_get_constraintdef(oid) def from pg_constraint
    where conrelid = 'content_review_audit'::regclass order by conname""")

# schema drift watch on documents.source_uri (unique index?)
q("documents_indexes", """
    select indexname, indexdef from pg_indexes where tablename='documents'""")

pathlib.Path("/home/z/my-project/tool-results/fa_recon/probe_out.json").write_text(json.dumps(out, indent=1, default=str))
print("WROTE probe_out.json")
print("identity:", out["database"], out["campaign_identity"])
print("rows16 fetched:", len(out["rows16_state"]), "| ep topo rows:", len(out["rows16_ep_topology"]))
print("docs_total:", out["docs_total"], "| audit:", out["audit_rows"], "| ep:", out["ep_total"], "| gate:", out["gate_replica_rev2"])
print("target_collisions:", len(out["target_collisions"]))
