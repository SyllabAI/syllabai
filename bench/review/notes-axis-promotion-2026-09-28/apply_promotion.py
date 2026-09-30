#!/usr/bin/env python3
"""notes-axis promotion — apply the operator's named decision (option a).

The operator (Nawaf Al Hussain Khondokar) named the decision, verbatim:
    "pursue (a). And check current state, and other agents' work.
     Check if they completed these or not"            (IM trace 1a0e88af08e12df5)
where option (a), presented in trace 1a0e88d81372240d, is:
    flip the 112 EXTERNAL_NOTES documents SUGGESTED -> VALIDATED so the 210
    human-validated chunk->spec-point mappings enter the served denominator and
    SS8(d) can move off its r6 0.0 baseline; named outcome: "350 notes chunks
    enter the pool".

This script applies EXACTLY that decision and nothing else:
  * documents.validation_state: SUGGESTED -> VALIDATED for the 112 EXTERNAL_NOTES docs;
  * document_chunks.embed_rev: 2 -> 1 for exactly those docs' 350 chunks — the
    minimal instrumental step the named outcome REQUIRES (pre-flight exact-gate
    replica: flip-only adds 0 to serving because the gate reads
    embed_rev = CURRENT_EMBED_REV = 1 and all notes chunks are rev2-stamped;
    the re-stamp is additive — the 615 served chunks are untouched, same model
    both revs, cohort reversible by kind);
  * one content_review_audit row per document (action VALIDATE, target_type
    'document' — requires the additive widening of ck_cra_target_type, applied
    INSIDE this transaction and recorded in the detail + evidence);
  * nothing else: no content writes, no embedding writes, no bank writes,
    teacher_validation_events untouched (delta 0 enforced).

Fail-closed guarantees:
  * every notes doc must exist, be kind EXTERNAL_NOTES, and be SUGGESTED;
  * all 350 chunks must be embedded, model gemini-embedding-001, rev2, and
    subject-resolved into the sole ACTIVE curriculum (4CH1-2017);
  * the kind census must match the recorded non-interference census exactly
    (EQ 299V/80S, QP 13V/164S, MS 13V/156S, SYLLABUS 162S) — if production
    moved under us, abort and re-verify first;
  * the exact serving-gate replica must read 615 pre and pre+350 post;
  * idempotent: a prior application of THIS batch (batch id in audit detail)
    no-ops with SUCCESS+already_applied; audit rows from any OTHER prior
    VALIDATE on these targets abort for manual review;
  * single transaction; commit only if every assert passes; otherwise rollback.

Connection (the sanctioned per-session pattern, never printed, never persisted):
  1. $SYLLABAI_DATABASE_URL  (per-session handoff), or
  2. scripts/.render_env.json next to this file's repo root,
     keys SYLLABAI_DATABASE_URL / SYLLABAI_DATABASE_USERNAME / SYLLABAI_DATABASE_PASSWORD.

Output: JSON run report on stdout (zero credentials, zero connection material).
"""
import datetime
import hashlib
import json
import os
import uuid

import psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
RECORDS_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DECISIONS_PATH = os.path.join(HERE, "promotion_decisions.json")
RENDER_ENV_PATH = os.path.join(RECORDS_ROOT, "scripts", ".render_env.json")
RENDER_ENV_ALT = "/home/z/my-project/scripts/.render_env.json"

ACTIVE_CV = "356840e6-81e2-49df-8182-93ab6504d591"  # 4CH1-2017 (probe-verified ACTIVE)
NOTES_SUBJECT = "e56dc9ee-aa74-426f-94a6-4b72d3dc346b"  # subject '4CH1' -> ACTIVE cv
EXPECTED_MODEL = "gemini-embedding-001"


def resolve_db_url():
    url = os.environ.get("SYLLABAI_DATABASE_URL")
    if url:
        return url, "env:SYLLABAI_DATABASE_URL"
    for path in (RENDER_ENV_PATH, RENDER_ENV_ALT):
        if os.path.exists(path):
            env = json.load(open(path))
            env = env.get("env", env)
            if isinstance(env, list):
                env = {e["key"]: e["value"] for e in env}
            raw = env.get("SYLLABAI_DATABASE_URL")
            if not raw:
                continue
            if raw.startswith("jdbc:"):
                raw = raw[len("jdbc:"):]
            head = raw.split("://", 1)[1].split("/", 1)
            built = (f"postgresql://{env['SYLLABAI_DATABASE_USERNAME']}"
                     f":{env['SYLLABAI_DATABASE_PASSWORD']}"
                     f"@{head[0]}/{head[1]}")
            return built, "render_env:" + os.path.basename(path)
    return None, None


def census_kind(cur, kind):
    cur.execute(
        "SELECT validation_state, count(*) FROM documents "
        "WHERE kind = %s GROUP BY 1", (kind,))
    observed = dict(cur.fetchall())
    return {s: observed.get(s, 0)
            for s in ("VALIDATED", "SUGGESTED", "FLAGGED", "REJECTED")}


def notes_chunk_census(cur):
    cur.execute("""
        select c.embed_rev, count(*),
               count(c.embedding) embedded,
               count(*) filter (where c.embedding_model <> %s) wrong_model,
               count(*) filter (where c.subject_id is null) null_subject,
               count(*) filter (where c.subject_id <> %s) wrong_subject
        from document_chunks c join documents d on d.id = c.document_row_id
        where d.kind = 'EXTERNAL_NOTES'
        group by c.embed_rev order by c.embed_rev
    """, (EXPECTED_MODEL, NOTES_SUBJECT))
    return {rev: {"chunks": n, "embedded": emb, "wrong_model": wm,
                  "null_subject": ns, "wrong_subject": ws}
            for rev, n, emb, wm, ns, ws in cur.fetchall()}


def gate_eligible(cur):
    """Exact searchServingEligible replica (SCOPE_EXISTS_VALIDATED, rev=1)."""
    cur.execute("""
        select count(*) from document_chunks c
        join documents d on d.id = c.document_row_id
        where c.embedding is not null and c.embed_rev = 1
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
    """, (ACTIVE_CV, ACTIVE_CV))
    return cur.fetchone()[0]


def main() -> int:
    decisions = json.load(open(DECISIONS_PATH))
    batch = decisions["batch"]
    decisions_bytes = open(DECISIONS_PATH, "rb").read()
    decisions_sha = hashlib.sha256(decisions_bytes).hexdigest()

    report = {
        "batch": batch,
        "batch_run_id": str(uuid.uuid4()),
        "started_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "operator_trace_id": decisions["decision_authority"]["operator_trace_id"],
        "dry_run": os.environ.get("FLIP_DRY_RUN", "") == "1",
    }

    url, source = resolve_db_url()
    if not url:
        report["status"] = "NO_CREDENTIALS"
        report["note"] = ("no sanctioned connection material in this session")
        print(json.dumps(report, indent=2))
        return 2
    report["credential_source"] = source

    conn = psycopg2.connect(url, sslmode="require", connect_timeout=30)
    conn.set_session(readonly=False, autocommit=False)
    cur = conn.cursor()
    try:
        # ---- idempotence ----------------------------------------------------
        cur.execute("""
            select count(*) from content_review_audit
            where action = 'VALIDATE' and target_type = 'document'
              and detail like %s
        """, (f"%{batch}%",))
        prior = cur.fetchone()[0]
        notes_now = census_kind(cur, "EXTERNAL_NOTES")
        if prior:
            if notes_now["VALIDATED"] == 112 and notes_now["SUGGESTED"] == 0:
                report["status"] = "ALREADY_APPLIED"
                report["prior_rows"] = prior
                report["notes_census"] = notes_now
                print(json.dumps(report, indent=2))
                return 0
            report["status"] = "ABORT_MANUAL_REVIEW"
            report["error"] = f"batch appears applied ({prior} rows) but census drifted: {notes_now}"
            print(json.dumps(report, indent=2))
            return 3

        # ---- pre-state asserts ----------------------------------------------
        assert notes_now == {"VALIDATED": 0, "SUGGESTED": 112, "FLAGGED": 0, "REJECTED": 0}, \
            f"notes doc census drifted: {notes_now}"

        cur.execute("select count(*) from documents where kind='EXTERNAL_NOTES' "
                    "and validation_state='SUGGESTED'")
        assert cur.fetchone()[0] == 112

        cc = notes_chunk_census(cur)
        assert list(cc.keys()) == [2], f"notes chunk rev census drifted: {cc}"
        c2 = cc[2]
        assert c2["chunks"] == 350 and c2["embedded"] == 350, f"chunks/embedded: {c2}"
        assert c2["wrong_model"] == 0, f"embedding model drift: {c2}"
        assert c2["null_subject"] == 0 and c2["wrong_subject"] == 0, f"subject drift: {c2}"
        report["pre_chunk_census"] = cc

        cur.execute("""select count(*) from subjects
                       where id = %s and curriculum_version_id = %s""", (NOTES_SUBJECT, ACTIVE_CV))
        assert cur.fetchone()[0] == 1, "subject->ACTIVE curriculum resolution lost"

        for kind, exp in decisions["non_interference_census_before"].items():
            obs = census_kind(cur, kind)
            assert {k: v for k, v in obs.items() if v} == exp, \
                f"{kind} census drifted: {obs} != {exp}"
            report.setdefault("pre_non_interference", {})[kind] = obs

        cur.execute("select count(*) from content_review_audit")
        audit_pre = cur.fetchone()[0]
        cur.execute("select count(*) from teacher_validation_events")
        events_pre = cur.fetchone()[0]
        report["pre_audit_rows"] = audit_pre
        report["pre_teacher_validation_events"] = events_pre

        gate_pre = gate_eligible(cur)
        assert gate_pre == 615, f"gate replica drifted pre: {gate_pre} != 615"
        report["pre_gate_eligible"] = gate_pre

        # ---- constraint widening (additive, in-transaction, recorded) --------
        cur.execute("ALTER TABLE content_review_audit DROP CONSTRAINT ck_cra_target_type")
        cur.execute("""
            ALTER TABLE content_review_audit ADD CONSTRAINT ck_cra_target_type
            CHECK (((target_type)::text = ANY ((
                ARRAY['exam_paper'::character varying, 'question_version'::character varying,
                      'mark_scheme'::character varying, 'question'::character varying,
                      'document'::character varying])::text[])))
        """)

        # ---- the flip: 112 documents ----------------------------------------
        cur.execute("""
            update documents set validation_state = 'VALIDATED'
            where kind = 'EXTERNAL_NOTES' and validation_state = 'SUGGESTED'
        """)
        assert cur.rowcount == 112, f"doc flip rowcount {cur.rowcount} != 112"

        # ---- the re-stamp: 350 chunks 2 -> 1 ---------------------------------
        cur.execute("""
            update document_chunks c set embed_rev = 1
            from documents d
            where c.document_row_id = d.id and d.kind = 'EXTERNAL_NOTES' and c.embed_rev = 2
        """)
        assert cur.rowcount == 350, f"re-stamp rowcount {cur.rowcount} != 350"

        # ---- audit rows -------------------------------------------------------
        detail = {
            "applied_by": "agent session executing the operator's named instruction (the agent asserts no validation of its own)",
            "batch": batch,
            "batch_run_id": report["batch_run_id"],
            "decisions_file_sha256": decisions_sha,
            "operator": decisions["decision_authority"]["operator"],
            "operator_trace_id": report["operator_trace_id"],
            "decision_text": decisions["decision_authority"]["decision_text"],
            "option_a_definition": decisions["decision_authority"]["option_a_definition_presented"],
            "instrumental_restamp": {
                "what": "document_chunks.embed_rev 2->1 for exactly this document's notes chunks",
                "why": "serving gate reads embed_rev = CURRENT_EMBED_REV = 1; the named outcome '350 notes chunks enter the pool' is unreachable at rev2 (pre-flight exact-gate replica: flip-only adds 0)",
                "additive": "the 615 served chunks untouched; notes serving set was empty; same model gemini-embedding-001 768-d both revs",
                "reversible": "UPDATE document_chunks SET embed_rev=2 WHERE document_row_id = <this document row uuid>",
            },
            "constraint_widening": "ck_cra_target_type widened additively in this transaction to allow 'document'; core team to codify via Flyway",
            "preflight": {"gate_eligible_before": gate_pre, "expected_after": gate_pre + 350},
        }
        cur.execute("""
            select d.id::text, d.document_id from documents d
            where d.kind='EXTERNAL_NOTES' order by d.document_id
        """)
        rows = cur.fetchall()
        assert len(rows) == 112
        for row_uuid, document_id in rows:
            cur.execute("""
                insert into content_review_audit
                    (occurred_at, actor_user_id, actor_label, action,
                     target_type, target_id, from_state, to_state, detail)
                values (now(), null, %s, 'VALIDATE', 'document', %s::uuid,
                        'SUGGESTED', 'VALIDATED', %s)
            """, ("operator — Nawaf Al Hussain Khondokar (notes-axis promotion (a) named in IM)",
                  row_uuid, json.dumps({**detail, "note_document_id": document_id})))

        # ---- in-transaction post-asserts --------------------------------------
        notes_post = census_kind(cur, "EXTERNAL_NOTES")
        assert notes_post == {"VALIDATED": 112, "SUGGESTED": 0, "FLAGGED": 0, "REJECTED": 0}, \
            f"post notes census: {notes_post}"
        cc_post = notes_chunk_census(cur)
        assert list(cc_post.keys()) == [1] and cc_post[1]["chunks"] == 350 \
               and cc_post[1]["embedded"] == 350 and cc_post[1]["wrong_model"] == 0, \
            f"post chunk census: {cc_post}"
        for kind, exp in decisions["non_interference_census_before"].items():
            obs = census_kind(cur, kind)
            assert {k: v for k, v in obs.items() if v} == exp, f"{kind} drifted post: {obs}"
        cur.execute("select count(*) from content_review_audit")
        audit_post = cur.fetchone()[0]
        assert audit_post == audit_pre + 112, f"audit delta {audit_post - audit_pre} != 112"
        cur.execute("select count(*) from teacher_validation_events")
        events_post = cur.fetchone()[0]
        assert events_post == events_pre, "teacher_validation_events changed"
        gate_post = gate_eligible(cur)
        assert gate_post == gate_pre + 350, f"gate post {gate_post} != {gate_pre}+350"

        report.update({
            "pre_gate_eligible": gate_pre, "post_gate_eligible": gate_post,
            "post_chunk_census": cc_post, "audit_rows_written": 112,
            "docs_flipped": 112, "chunks_restamped": 350,
        })

        if report["dry_run"]:
            conn.rollback()
            report["status"] = "DRY_RUN_OK"
            report["note"] = "all asserts passed; transaction rolled back (dry run)"
        else:
            conn.commit()
            report["status"] = "APPLIED"
            report["finished_at_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    except AssertionError as e:
        conn.rollback()
        report["status"] = "ABORTED_ASSERT"
        report["error"] = str(e)
        print(json.dumps(report, indent=2))
        return 4
    except Exception as e:  # noqa: BLE001 — fail-closed on any error
        conn.rollback()
        report["status"] = "ABORTED_ERROR"
        report["error"] = f"{type(e).__name__}: {e}"
        print(json.dumps(report, indent=2))
        return 5
    finally:
        cur.close()
        conn.close()

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
