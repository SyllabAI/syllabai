#!/usr/bin/env python3
"""wave2-validation batch — apply the operator's named decision (T-C54).

The operator (Nawaf Al Hussain Khondokar) named the decision, verbatim:
    "Proceed. Here is neon api if you need it."     (IM trace 1a0fb9dd09110041)
answering the wave-2 prep REPORT's single open instrument decision. The
in-session Neon API key sanctions the governed-SQL-batch instrument
(notes-axis precedent 9ea54e1). This script applies EXACTLY that decision
and nothing else, on the worklist composed by F-PROD-3
(evidence/bench-001/wave2-prep-2026-10-02/worklist2.json, sha pinned in
wave2_decisions.json):

  * documents.validation_state: SUGGESTED -> VALIDATED for exactly the 297
    worklist documents (per-doc fidelity asserted: kind, state, chunk count,
    embedding, subject resolution into the sole ACTIVE curriculum version);
  * one content_review_audit row per document (action VALIDATE, target_type
    'document' — the constraint was already widened additively by the 09-28
    batch; if absent this runner ABORTS, it performs no DDL);
  * nothing else: zero document_chunks writes (the dry-run must prove the
    1,673 chunks already serve at CURRENT_EMBED_REV = 2 via the exact
    searchServingEligible replica: 2935 -> 4608), teacher_validation_events
    untouched (delta 0 enforced), full documents state x kind census snapshot
    compared pre/post with only the 297 flips allowed.

Fail-closed guarantees:
  * DB identity gate first (AGENT.md rule 2 pattern): current_database() =
    neondb AND campaign_db_identity row T-C04-CAMPAIGN/neondb;
  * scope resolution mirrors resolveActive with the F-PROD-2 fail-closed
    census guard: exactly one ACTIVE curriculum_version, pinned by id;
  * live drift rule: the live SUGGESTED surface across the four kinds must
    equal the worklist exactly (297 docs / 1,673 chunks) — any production
    movement since the 07:38Z census aborts for re-composition;
  * idempotent: a prior application of THIS batch no-ops with
    SUCCESS+already_applied; audit rows from any OTHER prior VALIDATE on
    these targets abort for manual review;
  * single transaction; commit only if every assert passes; else rollback.

Connection (sanctioned per-session pattern, never printed, never persisted
into any git-tracked path):
  1. $SYLLABAI_DATABASE_URL (per-session handoff), or
  2. /home/z/my-project/scripts/.syllabai_db_url.json (this session's Neon
     API-key path, 0600, operator-provided in-session), or
  3. scripts/.render_env.json next to this file's repo root (legacy).

Output: JSON run report on stdout (zero credentials, zero connection material).
"""
import datetime
import hashlib
import json
import os
import sys
import uuid

import psycopg2
import psycopg2.extras

HERE = os.path.dirname(os.path.abspath(__file__))
RECORDS_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DECISIONS_PATH = os.path.join(HERE, "wave2_decisions.json")
NEON_URL_PATH = "/home/z/my-project/scripts/.syllabai_db_url.json"
RENDER_ENV_PATH = os.path.join(RECORDS_ROOT, "scripts", ".render_env.json")
RENDER_ENV_ALT = "/home/z/my-project/scripts/.render_env.json"

KINDS = ("EXTERNAL_QUESTIONS", "SYLLABUS", "QUESTION_PAPER", "MARK_SCHEME")


def resolve_db_url():
    url = os.environ.get("SYLLABAI_DATABASE_URL")
    if url:
        return url, "env:SYLLABAI_DATABASE_URL"
    if os.path.exists(NEON_URL_PATH):
        env = json.load(open(NEON_URL_PATH))
        if env.get("uri"):
            return env["uri"], "neon_api_key:" + os.path.basename(NEON_URL_PATH)
    for path in (RENDER_ENV_PATH, RENDER_ENV_ALT):
        if os.path.exists(path):
            env = json.load(open(path))
            env = env.get("env", env)
            if isinstance(env, list):
                if "envVar" in env[0]:
                    env = {e["envVar"]["key"]: e["envVar"]["value"] for e in env}
                else:
                    env = {e["key"]: e["value"] for e in env}
            raw = env.get("SYLLABAI_DATABASE_URL")
            if not raw:
                continue
            if raw.startswith("jdbc:"):
                raw = raw[len("jdbc:"):]
            from urllib.parse import urlparse
            u = urlparse(raw)
            return (f"postgresql://{env['SYLLABAI_DATABASE_USERNAME']}"
                    f":{env['SYLLABAI_DATABASE_PASSWORD']}"
                    f"@{u.hostname}{u.path}"), "render_env:" + os.path.basename(path)
    return None, None


def one(cur, sql, args=()):
    cur.execute(sql, args)
    return cur.fetchone()


def census_kind(cur, kind):
    cur.execute(
        "SELECT validation_state, count(*) FROM documents "
        "WHERE kind = %s GROUP BY 1", (kind,))
    observed = dict(cur.fetchall())
    return {s: observed.get(s, 0)
            for s in ("VALIDATED", "SUGGESTED", "FLAGGED", "REJECTED")}


def documents_census_snapshot(cur):
    """Full state x kind census of documents (chunkless docs included)."""
    cur.execute("""
        select validation_state, kind, count(*) as docs
        from documents group by 1, 2
    """)
    return {(r[0], r[1]): r[2] for r in cur.fetchall()}


def chunks_snapshot(cur):
    cur.execute("""
        select coalesce(embed_rev::text, 'null') as rev, count(*) as n,
               count(embedding) as embedded
        from document_chunks group by 1 order by 1
    """)
    return {r[0]: {"chunks": r[1], "embedded": r[2]} for r in cur.fetchall()}


def gate_eligible(cur, active_cv, rev):
    """Exact searchServingEligible replica (SCOPE_EXISTS_VALIDATED)."""
    cur.execute("""
        select count(*) from document_chunks c
        join documents d on d.id = c.document_row_id
        where c.embedding is not null and c.embed_rev = %s
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
    """, (rev, active_cv, active_cv))
    return cur.fetchone()[0]


def load_worklist(decisions):
    wl_path = os.path.join(RECORDS_ROOT, decisions["worklist"]["path"])
    sha = hashlib.sha256(open(wl_path, "rb").read()).hexdigest()
    assert sha == decisions["worklist"]["sha256"], \
        f"worklist sha drifted: {sha}"
    wl = json.load(open(wl_path))
    rows = [r for r in wl["rows"] if r["SUGGESTED"] > 0]
    return rows


def main() -> int:
    decisions = json.load(open(DECISIONS_PATH))
    batch = decisions["batch"]
    decisions_bytes = open(DECISIONS_PATH, "rb").read()
    decisions_sha = hashlib.sha256(decisions_bytes).hexdigest()
    rows = load_worklist(decisions)
    exp = decisions["worklist"]
    guards = decisions["scope_guards"]
    gate = decisions["serving_gate"]

    assert len(rows) == exp["expected_actionable_documents"], \
        f"worklist actionable count drifted: {len(rows)}"
    assert sum(r["SUGGESTED"] for r in rows) == exp["expected_actionable_chunks"]
    assert len({r["document_id"] for r in rows}) == len(rows), "duplicate ids"

    report = {
        "batch": batch,
        "batch_run_id": str(uuid.uuid4()),
        "started_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "operator_trace_id": decisions["decision_authority"]["operator_trace_id"],
        "dry_run": os.environ.get("FLIP_DRY_RUN", "") == "1",
        "worklist_sha256": exp["sha256"],
        "decisions_sha256": decisions_sha,
        "target_documents": len(rows),
        "target_chunks": sum(r["SUGGESTED"] for r in rows),
    }

    url, source = resolve_db_url()
    if not url:
        report["status"] = "NO_CREDENTIALS"
        report["note"] = "no sanctioned connection material in this session"
        print(json.dumps(report, indent=2))
        return 2
    report["credential_source"] = source

    conn = psycopg2.connect(url, sslmode="require", connect_timeout=30)
    conn.set_session(readonly=False, autocommit=False)
    cur = conn.cursor()
    try:
        # ---- identity gate (AGENT.md rule 2 pattern, fail-closed) -----------
        a = one(cur, "select current_database() as db")
        assert a[0] == guards["expected_database"], \
            f"DB IDENTITY GATE FAILED: current_database()={a[0]!r}"
        idrow = one(cur, """
            select campaign_label, db_name from campaign_db_identity
            where id = 1""")
        assert idrow is not None and \
            idrow[0] == guards["expected_campaign_label"] and \
            idrow[1] == guards["expected_database"], \
            f"DB IDENTITY GATE FAILED: identity row mismatch: {idrow}"
        report["identity"] = {"database": a[0], "label": idrow[0]}

        # ---- idempotence ----------------------------------------------------
        cur.execute("""
            select count(*) from content_review_audit
            where action = 'VALIDATE' and target_type = 'document'
              and detail like %s
        """, (f"%{batch}%",))
        prior = cur.fetchone()[0]
        notes_now = census_kind(cur, "EXTERNAL_NOTES")
        if prior:
            if (notes_now == decisions["non_interference"]["EXTERNAL_NOTES_census"]
                    and not [r for r in census_actionable(cur, guards)]):
                report["status"] = "ALREADY_APPLIED"
                report["prior_rows"] = prior
                report["notes_census"] = notes_now
                print(json.dumps(report, indent=2))
                return 0
            report["status"] = "ABORT_MANUAL_REVIEW"
            report["error"] = (f"batch appears applied ({prior} rows) but "
                               f"state drifted: notes={notes_now}")
            print(json.dumps(report, indent=2))
            return 3

        # ---- scope resolution (F-PROD-2 doctrine: exactly one ACTIVE) -------
        cur.execute("""
            select id, code, status from curriculum_versions
            where status = 'ACTIVE' order by created_at desc
        """)
        actives = cur.fetchall()
        assert len(actives) == 1, \
            f"resolveActive refuses: ACTIVE count = {len(actives)}"
        active_id, active_code = str(actives[0][0]), actives[0][1]
        assert active_id == guards["active_curriculum_version_id"], \
            f"ACTIVE cv drifted: {active_id} / {active_code}"
        report["active_cv"] = {"id": active_id, "code": active_code}
        rev = gate["current_embed_rev"]

        # ---- live drift rule: SUGGESTED surface == worklist exactly ---------
        drift = census_actionable(cur, guards)
        assert len(drift) == len(rows), \
            f"live SUGGESTED doc count {len(drift)} != worklist {len(rows)}"
        live_ids = {d["document_id"] for d in drift}
        wl_ids = {r["document_id"] for r in rows}
        assert live_ids == wl_ids, \
            f"live SUGGESTED surface drifted vs worklist: " \
            f"only-live={sorted(live_ids - wl_ids)[:5]} " \
            f"only-worklist={sorted(wl_ids - live_ids)[:5]}"
        live_chunks = sum(d["chunks"] for d in drift)
        assert live_chunks == exp["expected_actionable_chunks"], \
            f"live SUGGESTED chunk mass {live_chunks} != {exp['expected_actionable_chunks']}"

        # ---- per-doc fidelity (worklist vs live, chunk-level) ---------------
        kind_counts = {}
        cur.execute("""
            select d.document_id, d.id::text as row_id, d.kind, d.validation_state,
                   count(c.id) as chunks,
                   count(c.embedding) as embedded,
                   count(*) filter (where s2.curriculum_version_id = %s) as in_scope
            from documents d
            join document_chunks c on c.document_row_id = d.id
            left join subjects s2 on s2.id = c.subject_id
            where d.document_id = any(%s)
            group by d.document_id, d.id, d.kind, d.validation_state
        """, (active_id, [r["document_id"] for r in rows]))
        live = {r[0]: {"row_id": r[1], "kind": r[2], "state": r[3],
                       "chunks": r[4], "embedded": r[5], "in_scope": r[6]}
                for r in cur.fetchall()}
        for r in rows:
            doc_id = r["document_id"]
            l = live.get(doc_id)
            assert l is not None, f"worklist doc missing live: {doc_id}"
            assert l["kind"] == r["kind"], f"{doc_id} kind {l['kind']} != {r['kind']}"
            assert l["state"] == "SUGGESTED", f"{doc_id} state {l['state']}"
            assert l["chunks"] == r["chunks_total"], \
                f"{doc_id} chunks {l['chunks']} != {r['chunks_total']}"
            assert l["embedded"] == l["chunks"], \
                f"{doc_id} has {l['chunks'] - l['embedded']} non-embedded chunks"
            assert l["in_scope"] == l["chunks"], \
                f"{doc_id}: {l['chunks'] - l['in_scope']} chunks resolve outside ACTIVE scope"
            kind_counts[r["kind"]] = kind_counts.get(r["kind"], 0) + 1
        assert kind_counts == {k: v["docs"] for k, v in exp["expected_by_kind"].items()}, \
            f"kind census drifted: {kind_counts}"
        report["per_doc_fidelity"] = "297/297 PASS (kind, state, chunks, embedded, subject-scope)"

        # ---- non-interference prestate ---------------------------------------
        assert notes_now == decisions["non_interference"]["EXTERNAL_NOTES_census"], \
            f"EXTERNAL_NOTES census drifted: {notes_now}"
        report["pre_non_interference"] = {"EXTERNAL_NOTES": notes_now}

        census_pre = documents_census_snapshot(cur)
        chunks_pre = chunks_snapshot(cur)
        cur.execute("select count(*) from content_review_audit")
        audit_pre = cur.fetchone()[0]
        cur.execute("select count(*) from teacher_validation_events")
        events_pre = cur.fetchone()[0]
        report["pre_audit_rows"] = audit_pre
        report["pre_teacher_validation_events"] = events_pre

        # ---- serving-gate replica pre ----------------------------------------
        gate_pre = gate_eligible(cur, active_id, rev)
        assert gate_pre == gate["expected_pre"], \
            f"gate replica drifted pre: {gate_pre} != {gate['expected_pre']}"
        report["pre_gate_eligible"] = gate_pre

        # ---- constraint present? (no DDL — abort if missing) ------------------
        cur.execute("""
            select pg_get_constraintdef(oid) from pg_constraint
            where conname = 'ck_cra_target_type'
        """)
        cdef = cur.fetchone()
        assert cdef is not None and "'document'" in (cdef[0] or ""), \
            f"ck_cra_target_type missing/'document' not allowed: {cdef} — aborting (no DDL in this batch)"
        report["ck_cra_target_type"] = "includes 'document' (pre-verified, no DDL)"

        # ---- the flip: 297 documents, worklist order --------------------------
        ordered_ids = [live[r["document_id"]]["row_id"] for r in rows]
        cur.execute("""
            update documents set validation_state = 'VALIDATED'
            where id = any(%s::uuid[]) and validation_state = 'SUGGESTED'
        """, (ordered_ids,))
        assert cur.rowcount == len(rows), \
            f"doc flip rowcount {cur.rowcount} != {len(rows)}"
        report["docs_flipped"] = cur.rowcount

        # ---- audit rows --------------------------------------------------------
        detail_base = {
            "applied_by": "agent session executing the operator's named instruction (the agent asserts no validation of its own)",
            "batch": batch,
            "batch_run_id": report["batch_run_id"],
            "decisions_file_sha256": decisions_sha,
            "worklist_sha256": exp["sha256"],
            "operator": decisions["decision_authority"]["operator"],
            "operator_trace_id": report["operator_trace_id"],
            "decision_text": decisions["decision_authority"]["decision_text"],
            "instrument": decisions["instrument"]["chosen"],
            "authority": "T-C54 (wave-2 execution; worklist composed by F-PROD-3 / T-C41 wave-2 prep)",
            "preflight": {"gate_eligible_before": gate_pre,
                          "expected_after": gate_pre + exp["expected_actionable_chunks"]},
        }
        actor_label = decisions["audit_row_shape"]["actor_label"]
        for r in rows:
            row_uuid = live[r["document_id"]]["row_id"]
            detail = dict(detail_base)
            detail["note_document_id"] = r["document_id"]
            detail["note_kind"] = r["kind"]
            detail["note_chunks"] = r["chunks_total"]
            cur.execute("""
                insert into content_review_audit
                    (occurred_at, actor_user_id, actor_label, action,
                     target_type, target_id, from_state, to_state, detail)
                values (now(), null, %s, 'VALIDATE', 'document', %s::uuid,
                        'SUGGESTED', 'VALIDATED', %s)
            """, (actor_label, row_uuid, json.dumps(detail)))
        # per-row INSERTs: cur.rowcount is the last statement's (1); the
        # audit_post == audit_pre + N post-assert below is the real total check.
        report["audit_rows_written"] = len(rows)

        # ---- in-transaction post-asserts ---------------------------------------
        census_post = documents_census_snapshot(cur)
        expected_post = dict(census_pre)
        for r in rows:
            k = r["kind"]
            expected_post[("SUGGESTED", k)] -= 1
            expected_post[("VALIDATED", k)] = expected_post.get(("VALIDATED", k), 0) + 1
        # zero-count combos vanish from the live census (GROUP BY) — drop them
        # from the expected model before the equality compare
        expected_post = {k: v for k, v in expected_post.items() if v}
        assert census_post == expected_post, \
            "documents census post != pre shifted by exactly the 297 flips: " + json.dumps({
                "unexpected_delta": {f"{s}|{k}": census_post.get((s, k), 0) - expected_post.get((s, k), 0)
                                     for s, k in set(census_post) | set(expected_post)
                                     if census_post.get((s, k), 0) != expected_post.get((s, k), 0)},
                "pre": {f"{s}|{k}": v for (s, k), v in census_pre.items()},
                "post": {f"{s}|{k}": v for (s, k), v in census_post.items()},
            })
        chunks_post = chunks_snapshot(cur)
        assert chunks_post == chunks_pre, \
            f"document_chunks changed: {chunks_pre} -> {chunks_post} (forbidden)"
        cur.execute("select count(*) from content_review_audit")
        audit_post = cur.fetchone()[0]
        assert audit_post == audit_pre + len(rows), \
            f"audit delta {audit_post - audit_pre} != {len(rows)}"
        cur.execute("select count(*) from teacher_validation_events")
        events_post = cur.fetchone()[0]
        assert events_post == events_pre, "teacher_validation_events changed"
        gate_post = gate_eligible(cur, active_id, rev)
        assert gate_post == gate_pre + exp["expected_actionable_chunks"], \
            f"gate post {gate_post} != {gate_pre}+{exp['expected_actionable_chunks']} — " \
            "some actionable chunk does not serve at the current rev (would need a disclosed re-stamp)"

        report.update({
            "post_gate_eligible": gate_post,
            "chunks_snapshot": chunks_post,
            "audit_rows_total": audit_post,
            "teacher_validation_events": events_post,
        })

        if report["dry_run"]:
            conn.rollback()
            report["status"] = "DRY_RUN_OK"
            report["note"] = "all asserts passed; transaction rolled back (dry run)"
        else:
            conn.commit()
            report["status"] = "APPLIED"
            report["finished_at_utc"] = datetime.datetime.now(
                datetime.timezone.utc).isoformat()
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


def census_actionable(cur, guards):
    """Live SUGGESTED surface across the four kinds (drift detector).

    A document is actionable iff it is SUGGESTED, of a wave-2 kind, and has
    at least one chunk; the caller separately asserts the full per-doc
    fidelity for every worklist row. This census catches docs that APPEARED
    or DISAPPEARED since the worklist census even before fidelity runs.
    """
    cur.execute("""
        select d.document_id, count(c.id) as chunks
        from documents d
        join document_chunks c on c.document_row_id = d.id
        where d.validation_state = 'SUGGESTED'
          and d.kind = any(%s)
        group by d.document_id
    """, (list(KINDS),))
    return [{"document_id": r[0], "chunks": r[1]} for r in cur.fetchall()]


if __name__ == "__main__":
    sys.exit(main())
