#!/usr/bin/env python3
"""wave2_shell_poststate.py — independent read-only poststate verification of
the F-PROD-4 governed removal (run AFTER wave2_shell_removal.py --execute)."""
import json
from urllib.parse import urlparse

import psycopg2

env = {e["envVar"]["key"]: e["envVar"]["value"]
       for e in json.load(open("/home/z/my-project/scripts/.render_env.json"))["env"]}
url = env["SYLLABAI_DATABASE_URL"]
if url.startswith("jdbc:"):
    url = url[len("jdbc:"):]
u = urlparse(url)
conn = psycopg2.connect(
    f"postgresql://{env['SYLLABAI_DATABASE_USERNAME']}:{env['SYLLABAI_DATABASE_PASSWORD']}"
    f"@{u.hostname}{u.path}", sslmode="require", connect_timeout=30)
cur = conn.cursor()
SHELL = "7d40476f-13b3-436b-9e0d-f2877fe2ba0e"
QP_KEY = "41bc5a1a-63e6-5668-9245-6176567cc3a8"
MS_KEY = "1cf11a41-f60f-51ba-90e3-b34c7ceefd74"

cur.execute("select count(*) from exam_papers where id = %s::uuid", (SHELL,))
print("exam_papers shell rows:", cur.fetchone()[0], "(expect 0)")
cur.execute("select count(*) from documents where document_id in (%s, %s)", (QP_KEY, MS_KEY))
print("shell doc rows:", cur.fetchone()[0], "(expect 0)")
cur.execute("select count(*) from questions where exam_paper_id = %s::uuid", (SHELL,))
print("shell questions:", cur.fetchone()[0], "(expect 0)")
cur.execute("select count(*) from question_versions where source_document_id = %s", (QP_KEY,))
print("shell question_versions:", cur.fetchone()[0], "(expect 0)")
cur.execute("select count(*) from mark_schemes where source_document_id = %s", (MS_KEY,))
print("shell mark_schemes:", cur.fetchone()[0], "(expect 0)")
cur.execute("select count(*) from mark_schemes where question_version_id in "
            "(select id from question_versions where source_document_id = %s)", (QP_KEY,))
print("shell mark_schemes (by qv):", cur.fetchone()[0], "(expect 0)")
cur.execute("""select count(*) from content_review_audit
               where target_type = 'exam_paper' and target_id = %s::uuid""", (SHELL,))
print("audit rows total:", cur.fetchone()[0], "(expect 3 = 2 historical + 1 lane)")
cur.execute("""select occurred_at::text, actor_label, action, from_state, to_state
               from content_review_audit where target_type = 'exam_paper'
               and target_id = %s::uuid order by occurred_at desc limit 1""", (SHELL,))
print("latest audit row:", cur.fetchone())
cur.execute("""
with scope as (
  select c.id, c.embed_rev, c.embedding is not null as embedded
  from document_chunks c
  join documents d on d.id = c.document_row_id
  where (exists (select 1 from exam_papers p join subjects s on s.id = p.subject_id
                 where s.curriculum_version_id = (select id from curriculum_versions
                       where status = 'ACTIVE' order by created_at desc limit 1)
                   and p.validation_state = 'VALIDATED'
                   and (p.question_paper_document_id = d.document_id
                     or p.mark_scheme_document_id = d.document_id)))
     or (exists (select 1 from subjects s2
                 where s2.curriculum_version_id = (select id from curriculum_versions
                       where status = 'ACTIVE' order by created_at desc limit 1)
                   and s2.id = c.subject_id and d.validation_state = 'VALIDATED')))
select count(*) filter (where embedded), count(*) filter (where embedded and embed_rev = 2)
from scope""")
r = cur.fetchone()
print(f"serving funnel reachable/at_rev2: {r[0]}/{r[1]} (expect 2935/2935)")
cur.execute("""select count(*) from exam_papers p
               join subjects s on s.id = p.subject_id
               join curriculum_versions cv on cv.id = s.curriculum_version_id
               where cv.status = 'ACTIVE' and p.paper_code = '4CH1/2C'""")
print("4CH1/2C papers in ACTIVE scope:", cur.fetchone()[0], "(expect 12 — conflation resolved)")
conn.close()
