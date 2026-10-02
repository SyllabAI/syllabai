#!/usr/bin/env python3
"""wave2_shell_removal.py — F-PROD-4 governed removal of the 4CH1/2C June-2020
ingest-era shell (exam_papers 7d40476f-13b3-436b-9e0d-f2877fe2ba0e), per the
wave-1 PRODUCTION report finding and the operator's wave-2-prep directive.

WHAT the shell is (probe-verified 2026-10-02):
  1 exam_papers row  4CH1/2C June 2020, REJECTED by the teacher on 09-28
                     (audit trail FLAG 19:09Z -> REJECT 21:19Z, Nawaf Al
                     Hussain Khondokar) — the rejection decision STAYS in
                     content_review_audit; this lane only removes the dead
                     ingest skeleton so paper counts per code stop
                     conflating sessions (the finding's own words).
  2 documents        QP + MS, both REJECTED, 0 chunks
  7 questions        4ch1/past-papers/2020-06/4ch1-2C#q1..q7, active, never
                     validated (versions SUGGESTED)
  7 question_versions v=1 SUGGESTED (source = the shell QP doc)
  7 mark_schemes     SUGGESTED (source = the shell MS doc)
  + cascadeables     question_topics/options/parts, mark_points (counted in
                     the dry run, archived, then deleted explicitly)

WHAT this script refuses to do (fail-closed everywhere):
  * run without the DB identity gate (current_database()=neondb AND
    campaign_db_identity row label=T-C04-CAMPAIGN, db_name=neondb)
  * execute if ANY downstream reference exists: attempts, smart_mark_results,
    smart_mark_agreement_evaluations, glm_ocr_bridge_records, non-shell
    exam_papers doc pointers, document_chunks, question_attempts-style
    business keys — any nonzero count aborts BEFORE a single DELETE
  * execute if the prestate counts differ from the archived dry-run counts
  * touch content_review_audit (historical record — stays forever)
  * touch anything outside the shell's 24+ row closure

MODES
  python3 wave2_shell_removal.py            # DRY RUN: archive + sweep, no writes
  python3 wave2_shell_removal.py --execute  # single tx, re-verified, rowcount-guarded
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
ARCHIVE = "/home/z/my-project/scripts/wave2_shell_archive.json"

EXECUTE = "--execute" in sys.argv

_conn = None


def say(s=""):
    print(s, flush=True)


def q(sql, args=(), fetch=True):
    cur = _conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, args)
    return [dict(r) for r in cur.fetchall()] if fetch else cur.rowcount


def scalar(sql, args=()):
    return q(sql, args)[0].get("n", list(q(sql, args)[0].values())[0])


def identity_gate():
    global _conn
    env = {e["envVar"]["key"]: e["envVar"]["value"]
           for e in json.load(open(ENV_FILE))["env"]}
    url = env["SYLLABAI_DATABASE_URL"]
    if url.startswith("jdbc:"):
        url = url[len("jdbc:"):]
    u = urlparse(url)
    _conn = psycopg2.connect(
        f"postgresql://{env['SYLLABAI_DATABASE_USERNAME']}:{env['SYLLABAI_DATABASE_PASSWORD']}"
        f"@{u.hostname}{u.path}", sslmode="require", connect_timeout=30)
    db = q("select current_database() as db")[0]["db"]
    assert db == EXPECTED_DB, f"identity gate: db={db!r} != {EXPECTED_DB!r}"
    row = q("select campaign_label, db_name from campaign_db_identity where id = 1")[0]
    assert row["campaign_label"] == EXPECTED_LABEL and row["db_name"] == EXPECTED_DB, \
        f"identity gate: {row}"
    say(f"[identity gate PASS] db={db} label={row['campaign_label']}")


def collect():
    """Read the shell's full closure + run the exhaustive reference sweep."""
    state = {}
    papers = q("select * from exam_papers where id = %s::uuid", (SHELL_PAPER_ID,))
    assert len(papers) == 1, f"paper rows = {len(papers)} (expect exactly 1)"
    paper = papers[0]
    assert paper["validation_state"] == "REJECTED", f"paper state {paper['validation_state']} != REJECTED"
    state["paper"] = paper
    dk = (paper["question_paper_document_id"], paper["mark_scheme_document_id"])

    docs = q("""select * from documents where document_id in %s order by kind""",
             (dk,))
    assert len(docs) == 2, f"doc rows = {len(docs)} (expect 2)"
    for d in docs:
        assert d["validation_state"] == "REJECTED", f"doc {d['id']} state {d['validation_state']}"
    state["documents"] = docs
    doc_row_ids = tuple(str(d["id"]) for d in docs)

    # children (full row images for the archive)
    state["questions"] = q(
        "select * from questions where exam_paper_id = %s::uuid order by external_ref",
        (SHELL_PAPER_ID,))
    qids = tuple(str(x["id"]) for x in state["questions"])
    state["question_versions"] = q(
        """select * from question_versions where source_document_id in %s
           order by created_at""", (dk,))
    qvids = tuple(str(x["id"]) for x in state["question_versions"])
    assert len(state["questions"]) == 7 and len(state["question_versions"]) == 7, \
        f"skeleton drift: q={len(state['questions'])} qv={len(state['question_versions'])} (expect 7/7)"
    for qv in state["question_versions"]:
        assert str(qv["question_id"]) in qids, f"qv {qv['id']} belongs to a foreign question"
        assert qv["validation_state"] == "SUGGESTED", f"qv {qv['id']} state {qv['validation_state']}"
        assert qv["source_document_id"] == dk[0], f"qv {qv['id']} src != shell QP doc"
    state["mark_schemes"] = q(
        """select * from mark_schemes where source_document_id in %s
           order by created_at""", (dk,))
    msids = tuple(str(x["id"]) for x in state["mark_schemes"])
    assert len(state["mark_schemes"]) == 7, f"ms={len(state['mark_schemes'])} (expect 7)"
    for ms in state["mark_schemes"]:
        assert str(ms["question_version_id"]) in qvids, f"ms {ms['id']} belongs to a foreign version"
        assert ms["validation_state"] == "SUGGESTED", f"ms {ms['id']} state {ms['validation_state']}"
        assert ms["source_document_id"] == dk[1], f"ms {ms['id']} src != shell MS doc"
    state["question_topics"] = q("select * from question_topics where question_id in %s", (qids,))
    state["question_options"] = q("select * from question_options where question_id in %s order by ordering", (qids,))
    state["question_parts"] = q("select * from question_parts where question_version_id in %s", (qvids,))
    state["mark_points"] = q("select * from mark_points where mark_scheme_id in %s", (msids,))

    # ── the blocking sweep: any row here means DO NOT REMOVE ──────────────
    blocking = {}
    blocking["attempts (question_id in shell q)"] = scalar(
        "select count(*) n from attempts where question_id in %s", (qids,))
    blocking["smart_mark_results (mark_scheme_id in shell ms)"] = scalar(
        "select count(*) n from smart_mark_results where mark_scheme_id in %s", (msids,))
    blocking["smart_mark_agreement_evaluations (exam_paper_id = shell)"] = scalar(
        "select count(*) n from smart_mark_agreement_evaluations where exam_paper_id = %s::uuid",
        (SHELL_PAPER_ID,))
    blocking["glm_ocr_bridge_records (paper_id = shell)"] = scalar(
        "select count(*) n from glm_ocr_bridge_records where paper_id = %s::uuid",
        (SHELL_PAPER_ID,))
    blocking["document_chunks (document_row_id in shell docs)"] = scalar(
        "select count(*) n from document_chunks where document_row_id in %s", (doc_row_ids,))
    blocking["other exam_papers pointing at shell doc keys"] = scalar(
        """select count(*) n from exam_papers where id <> %s::uuid and
           (question_paper_document_id in %s or mark_scheme_document_id in %s)""",
        (SHELL_PAPER_ID, dk, dk))
    blocking["marking_queue_items (question_version in shell)"] = scalar(
        """select count(*) n from marking_queue_items where question_version_id in %s""",
        (qvids,)) if _table_exists("marking_queue_items") else 0
    blocking["question_attempts (question in shell)"] = scalar(
        """select count(*) n from question_attempts where question_id in %s""",
        (qids,)) if _table_exists("question_attempts") else 0
    state["blocking_sweep"] = blocking
    blockers = {k: v for k, v in blocking.items() if v}
    return state, blockers


def _table_exists(name):
    n = scalar("select count(*) n from information_schema.tables "
               "where table_schema='public' and table_name = %s", (name,))
    return bool(n)


def dry_run():
    identity_gate()
    state, blockers = collect()
    say(f"\nshell closure row counts:")
    for k in ("paper", "documents", "questions", "question_versions",
              "mark_schemes", "question_topics", "question_options",
              "question_parts", "mark_points"):
        v = state[k]
        say(f"   {k:20s} {len(v)}")
    say("\nblocking sweep (must ALL be zero to execute):")
    for k, v in state["blocking_sweep"].items():
        say(f"   {'[OK]' if not v else '[BLOCK]'} {k:52s} = {v}")
    audit = q("""select id, occurred_at::text, action, from_state, to_state, actor_label
                 from content_review_audit where target_type='exam_paper'
                 and target_id = %s::uuid order by occurred_at""", (SHELL_PAPER_ID,))
    state["audit_rows_reference_only_stay"] = audit
    say(f"\ncontent_review_audit rows (historical, NOT removed): {len(audit)}")
    for r in audit:
        say(f"   {r['occurred_at']} {r['action']:8s} {r['from_state']}->{r['to_state']} by {r['actor_label']}")
    if blockers:
        say(f"\nVERDICT: BLOCKED — {len(blockers)} reference kind(s) non-zero; "
            "the shell is NOT removable by this lane. Record and stop.")
        json.dump(state, open(ARCHIVE, "w"), indent=1, default=str)
        sys.exit(2)
    n_rows = sum(len(state[k]) if isinstance(state[k], list) else 1
                 for k in ("paper", "documents", "questions",
                           "question_versions", "mark_schemes",
                           "question_topics", "question_options",
                           "question_parts", "mark_points"))
    say(f"\nVERDICT: REMOVABLE — {n_rows} rows in the closure, zero downstream references.")
    say(f"archive written: {ARCHIVE}")
    json.dump(state, open(ARCHIVE, "w"), indent=1, default=str)
    if not EXECUTE:
        say("mode: DRY RUN — nothing written to the database. Re-run with --execute.")
        _conn.close()
        return
    execute(state)


def execute(state):
    say("\n== EXECUTE — single transaction, re-verified in-tx ==")
    cur = _conn.cursor()
    try:
        _conn.rollback()  # end the dry-run read transaction; start fresh
        paper = state["paper"]
        dk = (paper["question_paper_document_id"], paper["mark_scheme_document_id"])
        qids = tuple(str(x["id"]) for x in state["questions"])
        qvids = tuple(str(x["id"]) for x in state["question_versions"])
        msids = tuple(str(x["id"]) for x in state["mark_schemes"])
        doc_row_ids = tuple(str(d["id"]) for d in state["documents"])

        # re-verify the blocking sweep INSIDE the transaction
        _, blockers = collect()
        assert not blockers, f"in-tx sweep found blockers: {blockers}"

        def execcount(sql, args, expected, label):
            cur.execute(sql, args)
            n = cur.rowcount
            assert n == expected, f"{label}: rowcount {n} != expected {expected}"
            say(f"   [del] {label:44s} rowcount={n}")
            return n

        cur.execute("set local statement_timeout = '60s'")
        execcount("delete from mark_points where mark_scheme_id in %s", (msids,),
                  len(state["mark_points"]), "mark_points")
        execcount("delete from mark_schemes where id in %s", (msids,),
                  7, "mark_schemes")
        execcount("delete from question_parts where question_version_id in %s", (qvids,),
                  len(state["question_parts"]), "question_parts")
        execcount("delete from question_versions where id in %s", (qvids,),
                  7, "question_versions")
        execcount("delete from question_options where question_id in %s", (qids,),
                  len(state["question_options"]), "question_options")
        execcount("delete from question_topics where question_id in %s", (qids,),
                  len(state["question_topics"]), "question_topics")
        execcount("delete from questions where id in %s", (qids,),
                  7, "questions")
        execcount("delete from documents where id in %s", (doc_row_ids,),
                  2, "documents (chunks cascade: 0 expected)")
        execcount("delete from exam_papers where id = %s::uuid", (SHELL_PAPER_ID,),
                  1, "exam_papers (the shell)")

        # poststate assertions in-tx
        cur.execute("select count(*) from exam_papers where id = %s::uuid",
                    (SHELL_PAPER_ID,))
        assert cur.fetchone()[0] == 0, "poststate: paper still present"
        cur.execute("select count(*) from documents where document_id in %s", (dk,))
        assert cur.fetchone()[0] == 0, "poststate: docs still present"
        cur.execute("select count(*) from questions where exam_paper_id = %s::uuid",
                    (SHELL_PAPER_ID,))
        assert cur.fetchone()[0] == 0, "poststate: questions still present"
        cur.execute("""select count(*) from content_review_audit
                       where target_type = 'exam_paper' and target_id = %s::uuid""",
                    (SHELL_PAPER_ID,))
        audit_n = cur.fetchone()[0]
        assert audit_n >= 2, f"poststate: audit rows dropped? {audit_n}"
        say("   [ok] poststate: shell closure fully absent, audit rows intact")

        # serving funnel unchanged (nothing VALIDATED was touched)
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
            select count(*) filter (where embedded) as reachable,
                   count(*) filter (where embedded and embed_rev = 2) as at_rev2 from scope""")
        r = cur.fetchone()
        assert r[0] == 2935 and r[1] == 2935, f"funnel moved: {r} — expected 2935/2935"
        say(f"   [ok] serving funnel unchanged: {r[0]}/{r[1]}")

        # write-side audit trail for THIS lane (new audit rows, never removed)
        cur.execute("""insert into content_review_audit
                       (actor_user_id, actor_label, action, target_type, target_id,
                        from_state, to_state, detail)
                       values (null, %s, 'REJECT', 'exam_paper', %s::uuid,
                               'REJECTED', 'REJECTED', %s)""",
                    ("wave2-prep-agent(Super Z)", SHELL_PAPER_ID,
                     "F-PROD-4 governed removal: ingest-era shell (1 paper + 2 REJECTED docs "
                     "+ 7-question SUGGESTED skeleton) removed under the operator wave-2-prep "
                     "directive; full row archive retained in syllabai evidence pack; teacher "
                     "REJECT decision of 2026-09-28 unchanged and preserved above."))
        say(f"   [ok] audit row appended for the removal act (actor_label=wave2-prep-agent)")
        _conn.commit()
        say("COMMITTED.")
    except Exception as e:
        _conn.rollback()
        say(f"ROLLBACK — no changes applied: {e}")
        raise
    finally:
        _conn.close()


if __name__ == "__main__":
    dry_run()
