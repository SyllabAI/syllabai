#!/usr/bin/env python3
"""wave2 post-verify — independent READONLY verification on a fresh connection.

Runs AFTER apply_wave2_validation.py reports APPLIED. Never writes (session
is readonly at the driver level; autocommit). Re-derives every headline
number from production independently of the runner's in-transaction asserts:
census by kind, the exact searchServingEligible replica at rev2, the audit
trail by batch_run_id, teacher_validation_events, chunk-table integrity.
"""
import datetime
import json
import sys

import psycopg2

sys.path.insert(0, "/home/z/my-project/repos/syllabai/bench/review/wave2-validation-2026-10-02")
from apply_wave2_validation import resolve_db_url, gate_eligible, census_kind  # noqa: E402

BATCH = "wave2-validation-2026-10-02"
RUN_ID = "14cb8ae4-beca-4b25-8568-2e99249e7fb4"
ACTIVE_CV = "356840e6-81e2-49df-8182-93ab6504d591"
REV = 2

EXPECT_KINDS = {
    "EXTERNAL_QUESTIONS": {"VALIDATED": 379, "SUGGESTED": 0, "FLAGGED": 0, "REJECTED": 0},
    "SYLLABUS": {"VALIDATED": 162, "SUGGESTED": 0, "FLAGGED": 0, "REJECTED": 0},
    "QUESTION_PAPER": {"VALIDATED": 106, "SUGGESTED": 4, "FLAGGED": 0, "REJECTED": 78},
    "MARK_SCHEME": {"VALIDATED": 105, "SUGGESTED": 4, "FLAGGED": 0, "REJECTED": 67},
    "EXTERNAL_NOTES": {"VALIDATED": 112, "SUGGESTED": 0, "FLAGGED": 0, "REJECTED": 0},
}


def main() -> int:
    url, source = resolve_db_url()
    assert url, "no connection material"
    conn = psycopg2.connect(url, sslmode="require", connect_timeout=30)
    conn.set_session(readonly=True, autocommit=True)  # independent + cannot write
    cur = conn.cursor()
    out = {
        "batch": BATCH,
        "batch_run_id": RUN_ID,
        "verified_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "connection": {"readonly": True, "autocommit": True, "source": source},
    }

    a = cur.execute("select current_database() as db, current_user").fetchone() if False else None
    cur.execute("select current_database()")
    assert cur.fetchone()[0] == "neondb", "identity gate failed"
    cur.execute("select campaign_label, db_name from campaign_db_identity where id = 1")
    r = cur.fetchone()
    assert r and r[0] == "T-C04-CAMPAIGN" and r[1] == "neondb", "identity row mismatch"
    out["identity"] = {"database": "neondb", "label": r[0]}

    # census by kind
    census = {k: census_kind(cur, k) for k in EXPECT_KINDS}
    for k, exp in EXPECT_KINDS.items():
        assert census[k] == exp, f"{k} census drifted: {census[k]} != {exp}"
    out["documents_census"] = census

    # serving gate replica (independent read)
    gate_post = gate_eligible(cur, ACTIVE_CV, REV)
    assert gate_post == 4608, f"gate replica {gate_post} != 4608"
    out["gate_eligible"] = gate_post

    # the 1,673 newly-served chunks, by kind — derived from the AUDIT TRAIL
    # (join the batch's 297 VALIDATE rows to their documents), independent of
    # the runner's worklist-driven UPDATE path
    cur.execute("""
        select d.kind, count(c.id) as chunks
        from content_review_audit cra
        join documents d on d.id = cra.target_id
        join document_chunks c on c.document_row_id = d.id
        where cra.action = 'VALIDATE' and cra.target_type = 'document'
          and cra.detail like %s
          and c.embedding is not null and c.embed_rev = %s
          and exists (select 1 from subjects s2 where s2.curriculum_version_id = %s
                        and s2.id = c.subject_id)
        group by d.kind order by d.kind
    """, (f"%{RUN_ID}%", REV, ACTIVE_CV))
    subject_branch = {k: n for k, n in cur.fetchall()}
    assert sum(subject_branch.values()) == 1673, \
        f"subject-branch newly-served mass {subject_branch} != 1673"
    out["subject_branch_serving_by_kind"] = subject_branch

    # audit trail by batch_run_id
    cur.execute("""
        select count(*), min(occurred_at)::text, max(occurred_at)::text
        from content_review_audit
        where action = 'VALIDATE' and target_type = 'document'
          and detail like %s
    """, (f"%{RUN_ID}%",))
    n, t0, t1 = cur.fetchone()
    assert n == 297, f"audit rows for batch: {n} != 297"
    out["audit_batch_rows"] = {"count": n, "window_utc": [t0, t1]}
    cur.execute("""
        select actor_label, from_state, to_state, detail::jsonb->'decision_text'
        from content_review_audit where detail like %s limit 1
    """, (f"%{RUN_ID}%",))
    label, fs, ts, dt = cur.fetchone()
    assert fs == "SUGGESTED" and ts == "VALIDATED" and dt == "Proceed. Here is neon api if you need it."
    out["audit_sample"] = {"actor_label": label, "from": fs, "to": ts,
                           "decision_text": dt}
    cur.execute("select count(*) from content_review_audit")
    out["audit_total"] = cur.fetchone()[0]

    # teacher_validation_events must still be empty
    cur.execute("select count(*) from teacher_validation_events")
    ev = cur.fetchone()[0]
    assert ev == 0, f"teacher_validation_events = {ev}"
    out["teacher_validation_events"] = ev

    # chunk-table integrity: all rev2, all embedded, count unchanged
    cur.execute("""
        select coalesce(embed_rev::text,'null'), count(*), count(embedding)
        from document_chunks group by 1
    """)
    ch = {r[0]: {"chunks": r[1], "embedded": r[2]} for r in cur.fetchall()}
    assert ch == {"2": {"chunks": 4672, "embedded": 4672}}, f"chunk table drifted: {ch}"
    out["chunks"] = ch

    conn.close()
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
