#!/usr/bin/env python3
"""wave2_prep_probe.py — Wave-2 prep (F-PROD-2/3/4) READ-ONLY reconnaissance.

 SELECT-ONLY against production (Neon `neondb` via the sanctioned session-env
 read path: Render env-vars API -> SYLLABAI_DATABASE_URL, snap-006 lineage).
 No writes anywhere in this script.

 Establishes, with the DB identity gate first (AGENT.md rule 2 pattern):
   A. identity          current_database() == neondb, campaign identity row
   B. scope             curriculum_versions census + the single ACTIVE owner
                        (resolveActive mirror; F-PROD-2's corrected predicate)
   C. serving funnel    reachable_chunks / reachable_at_rev2 via the CORRECTED
                        poststate predicate (wave-1 PRODUCTION pack copy)
   D. SUGGESTED surface wave-2 actionable census:
                          - corpus documents (non-paper axis): documents with
                            SUGGESTED chunks, by kind, split by in-scope/out
                          - unplaced ingest-era papers: SUGGESTED QP/MS chunk
                            mass on papers outside the ACTIVE scope
   E. F-PROD-4 shell    full row image + FK sweep for exam_papers
                        7d40476f-13b3-436b-9e0d-f2877fe2ba0e (4CH1/2C REJECTED
                        empty pair) — every table that references the paper or
                        its two documents, to size the governed removal.
   F. documents census  documents.validation_state overall (corpus law check)

 Output: JSON machine record + human transcript, printed; caller files them
 into the evidence pack.
"""
import json
import sys
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras

ENV_FILE = "/home/z/my-project/scripts/.render_env.json"
SHELL_PAPER_ID = "7d40476f-13b3-436b-9e0d-f2877fe2ba0e"
EXPECTED_DB = "neondb"
EXPECTED_LABEL = "T-C04-CAMPAIGN"

OUT_JSON = "/home/z/my-project/scripts/wave2_prep_probe_result.json"
OUT_TXT = "/home/z/my-project/scripts/wave2_prep_probe_output.txt"

_lines = []


def say(s=""):
    print(s)
    _lines.append(s)


def load_db_url():
    env = {e["envVar"]["key"]: e["envVar"]["value"]
           for e in json.load(open(ENV_FILE))["env"]}
    url = env["SYLLABAI_DATABASE_URL"]
    if url.startswith("jdbc:"):
        url = url[len("jdbc:"):]
    u = urlparse(url)
    return (f"postgresql://{env['SYLLABAI_DATABASE_USERNAME']}:"
            f"{env['SYLLABAI_DATABASE_PASSWORD']}@{u.hostname}{u.path}"), u


def one(cur, sql, args=()):
    cur.execute(sql, args)
    return cur.fetchone()


def main():
    db_url, u = load_db_url()
    say("== wave-2 prep probe — READ-ONLY (F-PROD-2/3/4 reconnaissance) ==")
    say(f"host: {u.hostname}  db-path: {u.path}")

    conn = psycopg2.connect(db_url, sslmode="require", connect_timeout=30)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    result = {}

    # ── A. identity gate (fail-closed) ─────────────────────────────────────
    a = one(cur, "select current_database() as db")
    if a["db"] != EXPECTED_DB:
        say(f"DB IDENTITY GATE FAILED: current_database()={a['db']!r} != {EXPECTED_DB!r}")
        sys.exit(1)
    cur.execute("""
        select campaign_label, db_name, claimed_at, last_seen_at
        from campaign_db_identity where id = 1""")
    idrow = cur.fetchone()
    if (idrow is None or idrow["campaign_label"] != EXPECTED_LABEL
            or idrow["db_name"] != EXPECTED_DB):
        say(f"DB IDENTITY GATE FAILED: identity row mismatch: {dict(idrow) if idrow else None}")
        sys.exit(1)
    say(f"[PASS] identity: db={a['db']} label={idrow['campaign_label']} "
        f"claimed_at={idrow['claimed_at']} last_seen={idrow['last_seen_at']}")
    result["identity"] = {"database": a["db"], "label": idrow["campaign_label"],
                          "claimed_at": str(idrow["claimed_at"]),
                          "last_seen_at": str(idrow["last_seen_at"])}

    # ── B. scope: curriculum_versions + ACTIVE owner ───────────────────────
    cur.execute("""
        select id, code, title, status, created_at::text
        from curriculum_versions order by created_at""")
    cvs = [dict(r) for r in cur.fetchall()]
    active = [c for c in cvs if c["status"] == "ACTIVE"]
    say(f"\n-- B. curriculum_versions: {len(cvs)} rows, ACTIVE={len(active)} --")
    for c in cvs:
        mark = "  <== ACTIVE" if c["status"] == "ACTIVE" else ""
        say(f"   {c['code']:22s} {c['status']:10s} {c['id']}{mark}")
    assert len(active) == 1, f"resolveActive refuses: ACTIVE count = {len(active)}"
    active_id = str(active[0]["id"])
    result["scope"] = {"versions": cvs, "active_id": active_id,
                       "active_code": active[0]["code"]}
    # the F-PROD-2 defect demonstration: what the OLD predicate resolves to
    old_scope = one(cur, """
        select id, code, status from curriculum_versions
        order by created_at limit 1""")
    say(f"   old kit predicate (order by created_at limit 1) resolves: "
        f"{old_scope['code']} [{old_scope['status']}]  <- F-PROD-2 defect demo")
    result["scope"]["old_predicate_resolves_to"] = dict(old_scope)

    # ── C. serving funnel via the CORRECTED predicate ──────────────────────
    corrected = """
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
    select 'reachable_chunks' as metric, count(*) as n from scope where embedded
    union all
    select 'reachable_at_rev2', count(*) from scope where embedded and embed_rev = 2
    """
    cur.execute(corrected)
    funnel = {r["metric"]: r["n"] for r in cur.fetchall()}
    say(f"\n-- C. serving funnel (CORRECTED predicate) --\n   {funnel}")
    result["serving_funnel"] = funnel

    # old-predicate funnel for the defect record
    old_funnel_sql = corrected.replace(
        "status = 'ACTIVE' order by created_at desc limit 1",
        "true order by created_at limit 1")
    cur.execute(old_funnel_sql)
    funnel_old = {r["metric"]: r["n"] for r in cur.fetchall()}
    say(f"   (old-predicate funnel for the record: {funnel_old})")
    result["serving_funnel_old_predicate"] = funnel_old

    # ── D. wave-2 SUGGESTED surface census ─────────────────────────────────
    # D1. corpus (non-paper-axis) documents with SUGGESTED chunks, by kind
    cur.execute("""
        select d.kind,
               count(distinct d.id) filter (where s2.curriculum_version_id = %(cv)s) as docs_in_scope,
               count(distinct d.id) filter (where s2.curriculum_version_id is distinct from %(cv)s) as docs_out_of_scope,
               count(c.id) filter (where s2.curriculum_version_id = %(cv)s) as chunks_in_scope,
               count(c.id) filter (where s2.curriculum_version_id is distinct from %(cv)s) as chunks_out_of_scope,
               count(c.id) filter (where s2.curriculum_version_id = %(cv)s
                                     and c.embedding is not null) as chunks_in_scope_embedded
        from documents d
        join document_chunks c on c.document_row_id = d.id
        left join subjects s2 on s2.id = c.subject_id
        where d.validation_state = 'SUGGESTED'
          and d.kind not in ('QUESTION_PAPER', 'MARK_SCHEME')
          and not exists (select 1 from exam_papers p
                          where p.question_paper_document_id = d.document_id
                             or p.mark_scheme_document_id = d.document_id)
        group by d.kind order by d.kind
    """, {"cv": active_id})
    corpus = [dict(r) for r in cur.fetchall()]
    say("\n-- D1. corpus SUGGESTED surface (non-paper axis, by kind) --")
    for r in corpus:
        say(f"   {r['kind']:20s} docs_in={r['docs_in_scope']:4d} docs_out={r['docs_out_of_scope']:4d} "
            f"chunks_in={r['chunks_in_scope']:5d} (emb {r['chunks_in_scope_embedded']:5d}) chunks_out={r['chunks_out_of_scope']}")
    result["corpus_suggested_by_kind"] = corpus

    # D2. paper-axis SUGGESTED chunk mass, grouped by the OWNING paper's scope
    #     and state (F-PROD-3: the 369 QP + 395 MS live on unplaced ingest-era
    #     papers — papers outside the ACTIVE scope whose DOCUMENTS are still
    #     born-SUGGESTED; the paper rows themselves may read any state)
    cur.execute("""
        select coalesce(s2.curriculum_version_id::text, 'NO_SUBJECT') as cv,
               coalesce(s2.code, '-') as subject_code,
               coalesce(s2.curriculum_version_id::text, 'NO_SUBJECT') is distinct from %(cv)s as in_active_scope,
               p.validation_state as paper_state,
               d.kind,
               count(distinct p.id) as papers,
               count(distinct d.id) as docs,
               count(c.id) as chunks,
               count(c.id) filter (where c.embedding is not null) as embedded
        from documents d
        join document_chunks c on c.document_row_id = d.id
        left join exam_papers p on p.question_paper_document_id = d.document_id
                               or p.mark_scheme_document_id = d.document_id
        left join subjects s2 on s2.id = p.subject_id
        where d.validation_state = 'SUGGESTED'
          and d.kind in ('QUESTION_PAPER', 'MARK_SCHEME')
        group by 1, 2, 3, 4, 5 order by 1, 4, 5
    """, {"cv": active_id})
    unplaced = [dict(r) for r in cur.fetchall()]
    say("\n-- D2. SUGGESTED QP/MS chunk mass by owning paper's scope/state --")
    for r in unplaced:
        say(f"   cv={r['cv']} subject={r['subject_code']:10s} paper={r['paper_state'] or 'NO_PAPER':10s} "
            f"{r['kind']:15s} papers={r['papers']:3d} docs={r['docs']:3d} "
            f"chunks={r['chunks']:5d} (emb {r['embedded']})")
    result["paper_axis_suggested_by_scope"] = unplaced

    # D3. in-scope paper axis: any SUGGESTED left on VALIDATED-scope papers?
    cur.execute("""
        select count(*) as suggested_chunks, count(distinct d.id) as docs
        from documents d
        join document_chunks c on c.document_row_id = d.id
        where d.validation_state = 'SUGGESTED'
          and d.kind in ('QUESTION_PAPER', 'MARK_SCHEME')
    """)
    r = dict(one(cur, """
        select count(*) as suggested_chunks, count(distinct d.id) as docs
        from documents d
        join document_chunks c on c.document_row_id = d.id
        where d.validation_state = 'SUGGESTED'
          and d.kind in ('QUESTION_PAPER', 'MARK_SCHEME')"""))
    say(f"\n-- D3. paper-axis SUGGESTED documents overall (any scope): {r}")
    result["paper_axis_suggested_total"] = r

    # D4. the orphaned paper-axis chunks' subject_id — is the V33 denormalized
    #     identity set (→ doc-validate alone would make them serve via the
    #     subject branch) or NULL (→ fail-closed invisible; paper rows needed)?
    cur.execute("""
        select coalesce(s.curriculum_version_id::text,
               case when c.subject_id is null then 'NULL_SUBJECT'
                    else 'SUBJECT_OTHER_CV' end) as cv,
               d.kind, count(*) as chunks
        from documents d
        join document_chunks c on c.document_row_id = d.id
        left join subjects s on s.id = c.subject_id
        where d.validation_state = 'SUGGESTED'
          and d.kind in ('QUESTION_PAPER', 'MARK_SCHEME')
          and not exists (select 1 from exam_papers p
                          where p.question_paper_document_id = d.document_id
                             or p.mark_scheme_document_id = d.document_id)
        group by 1, 2 order by 1, 2
    """)
    orphan_subjects = [dict(r) for r in cur.fetchall()]
    say("\n-- D4. orphaned paper-axis chunks: denormalized subject identity --")
    for r in orphan_subjects:
        say(f"   {r['cv']}  {r['kind']:15s} chunks={r['chunks']}")
    result["orphan_paper_chunks_by_subject"] = orphan_subjects

    # ── E. F-PROD-4 shell: row image + FK sweep ────────────────────────────
    say(f"\n-- E. F-PROD-4 shell sweep: exam_papers.id = {SHELL_PAPER_ID} --")
    cur.execute("select * from exam_papers where id = %s::uuid", (SHELL_PAPER_ID,))
    papers = cur.fetchall()
    if len(papers) != 1:
        say(f"   [WARN] paper row count = {len(papers)} (expected 1; already removed?)")
        result["shell"] = {"present": False}
    else:
        paper = dict(papers[0])
        for k, v in paper.items():
            paper[k] = str(v)
        say(f"   paper: {paper.get('paper_code')} {paper.get('session_label')} "
            f"state={paper.get('validation_state')}")
        cur.execute("""
            select id, document_id, kind, validation_state,
                   (select count(*) from document_chunks c where c.document_row_id = d.id) as chunks
            from documents d
            where d.document_id = %s or d.document_id = %s
            order by kind
        """, (paper["question_paper_document_id"], paper["mark_scheme_document_id"]))
        docs = [dict(r) for r in cur.fetchall()]
        for d in docs:
            say(f"   doc: {d['id']} {d['kind']:15s} {d['validation_state']} chunks={d['chunks']}")
        # FK sweep — generic: every table carrying a paper/exam_paper pointer
        # column, probed for the shell's uuid; every *_document_id-style column
        # probed for the two business keys. (document_id is a VARCHAR business
        # key with NO FK constraint, so information_schema constraints alone
        # would miss the real references.)
        sweeps = {}
        doc_keys = (paper["question_paper_document_id"], paper["mark_scheme_document_id"])
        cur.execute("""
            select table_name, column_name from information_schema.columns
            where table_schema = 'public'
              and (column_name in ('paper_id', 'exam_paper_id')
                   or column_name like '%%document_id%%')
            order by table_name
        """)
        candidates = [(r["table_name"], r["column_name"]) for r in cur.fetchall()]
        for t, col in candidates:
            if t == "documents" and col == "document_id":
                continue  # the shell's own doc rows, counted separately below
            if t == "exam_papers" and col in ("question_paper_document_id", "mark_scheme_document_id"):
                cur.execute(f"""select count(*) n from exam_papers
                               where id <> %s::uuid and (%s in (question_paper_document_id, mark_scheme_document_id)
                                  or question_paper_document_id = %s or mark_scheme_document_id = %s)""",
                            (SHELL_PAPER_ID, doc_keys[0], doc_keys[0], doc_keys[0]))
                sweeps["exam_papers.self_or_other_doc_refs"] = cur.fetchone()["n"]
                continue
            try:
                if col in ("paper_id", "exam_paper_id"):
                    cur.execute(f'select count(*) n from "{t}" where "{col}" = %s::uuid',
                                (SHELL_PAPER_ID,))
                else:
                    cur.execute(f'select count(*) n from "{t}" where "{col}" = any(%s)',
                                (list(doc_keys),))
                n = cur.fetchone()["n"]
                if n:
                    sweeps[f"{t}.{col}"] = n
            except Exception as e:
                conn.rollback()
                sweeps[f"{t}.{col}"] = f"ERR: {e}"
        say("   non-empty references (generic sweep): "
            + (json.dumps(sweeps) if sweeps else "NONE beyond the paper+2 docs themselves"))
        result["shell"] = {"present": True, "paper": paper, "documents": docs,
                           "fk_sweep": sweeps}

        # the skeleton details (removal design needs states, not just counts)
        cur.execute("""
            select q.id, q.external_ref, q.active,
                   qv.id as version_id, qv.version, qv.validation_state as v_state,
                   qv.source_document_id
            from questions q
            left join question_versions qv on qv.question_id = q.id
            where q.exam_paper_id = %s::uuid
            order by qv.version
        """, (SHELL_PAPER_ID,))
        skeleton_qv = [dict(r) for r in cur.fetchall()]
        say(f"   question skeleton ({len(skeleton_qv)} rows):")
        for r in skeleton_qv:
            say(f"     q={r['id']} ext={r['external_ref']} active={r['active']} "
                f"v={r['version']} v_state={r['v_state']} src={r['source_document_id']}")
        cur.execute("""
            select ms.id, ms.source_document_id, ms.validation_state,
                   ms.version_label, ms.question_version_id, ms.created_at::text
            from mark_schemes ms
            where ms.source_document_id in %s
            order by ms.created_at
        """, (tuple(doc_keys),))
        skeleton_ms = [dict(r) for r in cur.fetchall()]
        say(f"   mark_schemes skeleton ({len(skeleton_ms)} rows):")
        for r in skeleton_ms:
            say(f"     ms={r['id']} state={r['validation_state']} "
                f"label={r['version_label']} qv={r['question_version_id']} src={r['source_document_id']}")
        # targeted audit probe (content_review_audit uses target_type/target_id,
        # invisible to the column-name sweep)
        cur.execute("""
            select target_type, action, from_state, to_state, occurred_at::text, actor_label
            from content_review_audit
            where (target_type = 'exam_paper' and target_id = %s::uuid)
               or (target_type = 'question' and target_id in (select id from questions where exam_paper_id = %s::uuid))
               or (target_type = 'question_version' and target_id in (select id from question_versions
                   where source_document_id in %s))
               or (target_type = 'mark_scheme' and target_id in (select id from mark_schemes
                   where source_document_id in %s))
            order by occurred_at
        """, (SHELL_PAPER_ID, SHELL_PAPER_ID, tuple(doc_keys), tuple(doc_keys)))
        audit_rows = [dict(r) for r in cur.fetchall()]
        say(f"   content_review_audit rows touching the shell: {len(audit_rows)}")
        for r in audit_rows:
            say(f"     {r['occurred_at']} {r['target_type']:16s} {r['action']:12s} "
                f"{r['from_state']}->{r['to_state']} by {r['actor_label']}")
        result["shell"].update({"skeleton_questions": skeleton_qv,
                                "skeleton_mark_schemes": skeleton_ms,
                                "audit_rows": audit_rows})

    # ── F. documents.validation_state census ───────────────────────────────
    cur.execute("""
        select d.validation_state, d.kind, count(distinct d.id) as docs,
               count(c.id) as chunks
        from documents d
        left join document_chunks c on c.document_row_id = d.id
        group by 1, 2 order by 1, 2
    """)
    doccens = [dict(r) for r in cur.fetchall()]
    say("\n-- F. documents census by validation_state × kind --")
    for r in doccens:
        say(f"   {r['validation_state']:10s} {r['kind']:20s} docs={r['docs']:4d} chunks={r['chunks']:5d}")
    result["documents_census"] = doccens

    conn.close()
    json.dump(result, open(OUT_JSON, "w"), indent=1, default=str)
    open(OUT_TXT, "w").write("\n".join(_lines) + "\n")
    say(f"\nprobe complete: {OUT_JSON}")


if __name__ == "__main__":
    main()
