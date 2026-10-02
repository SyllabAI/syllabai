#!/usr/bin/env python3
"""T-C66 — governed source_uri relabel of the 16 4CH0 R-paper generations
(operator IM trace 1a0fcf4d0a035c8d: "① Relabel source_uri" — executes the
T-C62/F-A1 follow-up ruling #1, fa1-retire-20261002 REPORT §5.1).

Instrument: the T-C54 wave-2 governed SQL-batch pattern (single transaction,
DB identity gate, idempotence, scope/drift/reference guards, in-transaction
census/chunks/audit/events non-interference asserts, exact searchServingEligible
gate replica with DELTA-0 expectation, content_review_audit rows in the same
transaction, no DDL). Action vocabulary is constrained by ck_cra_action; this
batch uses 'PLACE' — the app's own definition of a factual association update
that leaves validation states and the serving boundary untouched
(ContentReviewService.placePaper javadoc).

The UPDATE touches documents.source_uri ONLY: no state change, no checksum
change, no document_id change, no chunk change — gate replica must move by
exactly 0.
"""
import json, os, pathlib, sys, uuid, datetime
import psycopg2

HERE = pathlib.Path(__file__).resolve().parent
PLAN_PATH = pathlib.Path("/home/z/my-project/tool-results/fa_recon/relabel_plan.json")
OUT_PATH = pathlib.Path("/home/z/my-project/tool-results/fa_recon/relabel_apply_report.json")

BATCH = "fa1-relabel-2026-10-02"
OPERATOR = "Nawaf Al Hussain Khondokar"
OPERATOR_TRACE_ID = "1a0fcf4d0a035c8d"
DECISION_TEXT = "① Relabel source_uri on line"
AUTHORITY = ("T-C66 (executes the T-C62/F-A1 follow-up ruling #1 — "
             "fa1-retire-20261002 REPORT §5.1; corpus proof at syllabai-pastpapers "
             "HEAD f0ea3a1f9 manifests; audit d4_identity_mismatches byte-identity)")

# guards (derived live at probe time 2026-10-02, post-fa1 baseline)
GUARDS = {
    "expected_database": "neondb",
    "expected_campaign_label": "T-C04-CAMPAIGN",
    "active_curriculum_version_id": "356840e6-81e2-49df-8182-93ab6504d591",
    "active_curriculum_version_code": "4CH1-2017",
    "gate_expected_pre": 4593,
    "docs_total": 1017,
    "ep_total": 104,
    "audit_pre": 2798,
}

def resolve_db_url():
    url = os.environ.get("SYLLABAI_DATABASE_URL")
    if url:
        return url, "env:SYLLABAI_DATABASE_URL"
    env = json.loads(pathlib.Path("/home/z/my-project/scripts/.render_env.json").read_text())
    env = {e["key"]: e["value"] for e in env["env"]}
    import re
    raw = env["SYLLABAI_DATABASE_URL"]
    m = re.match(r"jdbc:postgresql://([^:/?]+)(?::(\d+))?/([^?]+)", raw)
    return (f"host={m.group(1)} port={m.group(2) or '5432'} dbname={m.group(3)} "
            f"user={env['SYLLABAI_DATABASE_USERNAME']} password={env['SYLLABAI_DATABASE_PASSWORD']}"), "render_env_cache"

def one(cur, sql, args=None):
    cur.execute(sql, args)
    return cur.fetchone()

def census_snapshot(cur):
    cur.execute("select validation_state, kind, count(*) from documents group by 1, 2")
    return {(r[0], r[1]): r[2] for r in cur.fetchall()}

def chunks_snapshot(cur):
    cur.execute("""select coalesce(embed_rev::text,'null') rev, count(*) n, count(embedding) embedded
                   from document_chunks group by 1 order by 1""")
    return {r[0]: {"chunks": r[1], "embedded": r[2]} for r in cur.fetchall()}

def gate_eligible(cur, active_cv, rev):
    """Exact searchServingEligible replica (T-C54 instrument)."""
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

def main() -> int:
    plan = json.loads(PLAN_PATH.read_text())
    rows = plan["plan"]
    assert len(rows) == 16, f"plan rows {len(rows)} != 16"
    assert plan["corpus_head"] == "f0ea3a1f9"
    report = {
        "batch": BATCH,
        "batch_run_id": str(uuid.uuid4()),
        "started_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "operator_trace_id": OPERATOR_TRACE_ID,
        "dry_run": os.environ.get("FLIP_DRY_RUN", "") == "1",
        "plan_sha256": None,
        "target_documents": 16,
        "expected_gate_delta": 0,
    }
    import hashlib
    report["plan_sha256"] = hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest()

    url, source = resolve_db_url()
    conn = psycopg2.connect(url, sslmode="require", connect_timeout=30)
    conn.set_session(readonly=False, autocommit=False)
    cur = conn.cursor()
    try:
        # ---- identity gate --------------------------------------------------
        a = one(cur, "select current_database()")
        assert a[0] == GUARDS["expected_database"], f"DB IDENTITY GATE FAILED: {a[0]!r}"
        idrow = one(cur, "select campaign_label, db_name from campaign_db_identity where id = 1")
        assert idrow and idrow[0] == GUARDS["expected_campaign_label"] and idrow[1] == GUARDS["expected_database"], \
            f"DB IDENTITY GATE FAILED: {idrow}"
        report["identity"] = {"database": a[0], "label": idrow[0]}

        # ---- idempotence ----------------------------------------------------
        cur.execute("select count(*) from content_review_audit where detail like %s", (f"%{BATCH}%",))
        prior = cur.fetchone()[0]
        cur.execute("""select count(*) from documents d where d.id::text = any(%s) and d.source_uri = any(%s)""",
                    ([r["row_id"] for r in rows], [r["new_source_uri"] for r in rows]))
        already = cur.fetchone()[0]
        if prior >= 16 or already == 16:
            report["status"] = "ALREADY_APPLIED"
            report["prior_audit_rows"] = prior
            report["rows_already_at_target"] = already
            print(json.dumps(report, indent=2))
            return already == 16 and 0 or 3

        # ---- ACTIVE cv resolution (exactly one) ------------------------------
        cur.execute("select id::text, code from curriculum_versions where status='ACTIVE' order by created_at desc")
        actives = cur.fetchall()
        assert len(actives) == 1, f"ACTIVE cv count {len(actives)}"
        active_id, active_code = actives[0]
        assert active_id == GUARDS["active_curriculum_version_id"] and active_code == GUARDS["active_curriculum_version_code"], \
            f"ACTIVE cv drifted: {active_id}/{active_code}"
        rev = 2

        # ---- scope/drift guard: all 16 rows exactly as planned ---------------
        cur.execute("""
            select d.id::text row_id, d.document_id::text document_id, d.kind, d.source_uri,
                   d.checksum, d.validation_state, count(c.id) chunks
            from documents d left join document_chunks c on c.document_row_id = d.id
            where d.id::text = any(%s)
            group by d.id, d.document_id, d.kind, d.source_uri, d.checksum, d.validation_state
        """, ([r["row_id"] for r in rows],))
        live = {r[0]: dict(zip(["row_id", "document_id", "kind", "source_uri", "checksum", "validation_state", "chunks"], r)) for r in cur.fetchall()}
        assert len(live) == 16, f"live rows {len(live)} != 16"
        for r in rows:
            l = live[r["row_id"]]
            assert l["source_uri"] == r["old_source_uri"], f"{r['row_id']} uri drifted: {l['source_uri']}"
            assert l["checksum"] == r["checksum"], f"{r['row_id']} checksum drifted"
            assert l["kind"] == r["kind"] and l["validation_state"] == "VALIDATED", f"{r['row_id']} kind/state drifted"
            assert l["chunks"] == r["chunks"], f"{r['row_id']} chunks drifted"

        # ---- reference guard: each row ep-linked by exactly 1 VALIDATED ep ---
        cur.execute("""
            select d.id::text, count(p.id)
            from documents d
            join exam_papers p on p.question_paper_document_id = d.document_id
                              or p.mark_scheme_document_id = d.document_id
            where d.id::text = any(%s) and p.validation_state = 'VALIDATED'
            group by d.id
        """, ([r["row_id"] for r in rows],))
        refs = {r[0]: r[1] for r in cur.fetchall()}
        assert all(refs.get(r["row_id"]) == 1 for r in rows), f"ep reference guard failed: {refs}"

        # ---- collision guard: no OTHER live doc holds any target URI ---------
        cur.execute("""
            select count(*) from documents
            where lower(source_uri) = any(%s) and id::text <> all(%s)
        """, ([r["new_source_uri"].lower() for r in rows], [r["row_id"] for r in rows]))
        collisions = cur.fetchone()[0]
        assert collisions == 0, f"target URI collision with {collisions} live row(s) — aborting"

        # ---- non-interference prestate ---------------------------------------
        census_pre = census_snapshot(cur)
        chunks_pre = chunks_snapshot(cur)
        cur.execute("select count(*) from documents"); docs_pre = cur.fetchone()[0]
        assert docs_pre == GUARDS["docs_total"], f"docs_total drifted: {docs_pre}"
        cur.execute("select count(*) from exam_papers"); ep_pre = cur.fetchone()[0]
        assert ep_pre == GUARDS["ep_total"], f"ep_total drifted: {ep_pre}"
        cur.execute("select count(*) from content_review_audit"); audit_pre = cur.fetchone()[0]
        assert audit_pre == GUARDS["audit_pre"], f"audit_pre drifted: {audit_pre}"
        cur.execute("select count(*) from teacher_validation_events"); events_pre = cur.fetchone()[0]
        report["pre"] = {"docs": docs_pre, "ep": ep_pre, "audit": audit_pre, "tve": events_pre}

        # ---- serving-gate replica pre (must equal the pinned baseline) -------
        gate_pre = gate_eligible(cur, active_id, rev)
        assert gate_pre == GUARDS["gate_expected_pre"], \
            f"gate replica drifted pre: {gate_pre} != {GUARDS['gate_expected_pre']} — census re-derive required"
        report["pre_gate_eligible"] = gate_pre

        # ---- the relabel: 16 rows, per-row identity-guarded UPDATE -----------
        for r in rows:
            cur.execute("""
                update documents set source_uri = %s
                where id = %s::uuid and source_uri = %s and checksum = %s
                  and validation_state = 'VALIDATED'
            """, (r["new_source_uri"], r["row_id"], r["old_source_uri"], r["checksum"]))
            assert cur.rowcount == 1, f"{r['row_id']} update rowcount {cur.rowcount} != 1"
        report["rows_relabeled"] = 16

        # ---- audit rows (16 × PLACE, states unchanged by design) -------------
        detail_base = {
            "applied_by": "agent session executing the operator's named instruction (the agent asserts no validation of its own; factual metadata correction only)",
            "batch": BATCH,
            "batch_run_id": report["batch_run_id"],
            "plan_sha256": report["plan_sha256"],
            "operator": OPERATOR,
            "operator_trace_id": OPERATOR_TRACE_ID,
            "decision_text": DECISION_TEXT,
            "instrument": "T-C54 wave-2 governed SQL-batch pattern (identity gate, idempotence, scope/drift/reference/collision guards, census+gate non-interference, no DDL)",
            "authority": AUTHORITY,
            "corpus_head": plan["corpus_head"],
            "change_class": "source_uri-only relabel; validation_state, document_id, checksum, chunks, ep links and serving boundary untouched; gate delta 0",
        }
        actor_label = f"operator — {OPERATOR} (4CH0 R-generation source_uri relabel; T-C66; factual metadata correction)"
        for r in rows:
            detail = dict(detail_base)
            detail.update({
                "document_row_id": r["row_id"], "document_id": r["document_id"], "kind": r["kind"],
                "old_source_uri": r["old_source_uri"], "new_source_uri": r["new_source_uri"],
                "checksum_sha256": r["checksum"], "chunks": r["chunks"],
                "corpus_pin_path": r["corpus_pin_path"],
                "corpus_official_reference": r["corpus_official_reference"],
                "corpus_series": r["corpus_series"],
            })
            cur.execute("""
                insert into content_review_audit
                    (occurred_at, actor_user_id, actor_label, action,
                     target_type, target_id, from_state, to_state, detail)
                values (now(), null, %s, 'PLACE', 'document', %s::uuid,
                        'VALIDATED', 'VALIDATED', %s)
            """, (actor_label, r["row_id"], json.dumps(detail)))
        report["audit_rows_written"] = 16

        # ---- in-transaction post-asserts --------------------------------------
        census_post = census_snapshot(cur)
        assert census_post == census_pre, "documents census changed (forbidden — source_uri-only batch)"
        chunks_post = chunks_snapshot(cur)
        assert chunks_post == chunks_pre, f"document_chunks changed: {chunks_pre} -> {chunks_post}"
        cur.execute("select count(*) from documents"); docs_post = cur.fetchone()[0]
        assert docs_post == docs_pre, "documents total changed"
        cur.execute("select count(*) from exam_papers"); ep_post = cur.fetchone()[0]
        assert ep_post == ep_pre, "exam_papers total changed"
        cur.execute("select count(*) from content_review_audit"); audit_post = cur.fetchone()[0]
        assert audit_post == audit_pre + 16, f"audit delta {audit_post - audit_pre} != 16"
        cur.execute("select count(*) from teacher_validation_events"); events_post = cur.fetchone()[0]
        assert events_post == events_pre, "teacher_validation_events changed"
        gate_post = gate_eligible(cur, active_id, rev)
        assert gate_post == gate_pre, f"gate moved {gate_pre} -> {gate_post} (expected delta 0)"
        # post reference guard: ep topology intact
        cur.execute("""
            select count(*) from documents d
            join exam_papers p on p.question_paper_document_id = d.document_id
                              or p.mark_scheme_document_id = d.document_id
            where d.id::text = any(%s) and p.validation_state = 'VALIDATED'
        """, ([r["row_id"] for r in rows],))
        assert cur.fetchone()[0] == 16, "ep reference count changed post"

        report.update({
            "post_gate_eligible": gate_post,
            "audit_rows_total": audit_post,
            "teacher_validation_events": events_post,
            "docs_total": docs_post, "ep_total": ep_post,
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
        OUT_PATH.write_text(json.dumps(report, indent=2))
        return 4
    except Exception as e:  # noqa: BLE001 — fail-closed on any error
        conn.rollback()
        report["status"] = "ABORTED_ERROR"
        report["error"] = f"{type(e).__name__}: {e}"
        print(json.dumps(report, indent=2))
        OUT_PATH.write_text(json.dumps(report, indent=2))
        return 5
    finally:
        cur.close()
        conn.close()

    print(json.dumps(report, indent=2))
    OUT_PATH.write_text(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
