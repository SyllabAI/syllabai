#!/usr/bin/env python3
"""fprod1_bank_probe.py — F-PROD-1 second read-only extraction: the BANKED
per-question state for the 25 REVIEW_REQUIRED papers, to sit beside each
bridge reconciliation finding (QP print total vs MS print total vs what the
bank actually serves). Same transport + identity gates as fprod1_bridge_probe.
ALL statements SELECT-only, executed on the throwaway review branch."""
import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

from fprod1_bridge_probe import env, save_env, api_call, wait_compute, sql

ENV_FILE = "/home/z/my-project/scripts/.neon_env.json"
OUT_JSON = "/home/z/my-project/scripts/fprod1_bank_result.json"
OUT_TXT = "/home/z/my-project/scripts/fprod1_bank_output.txt"

_lines = []


def say(s=""):
    print(s)
    _lines.append(str(s))


def main():
    e = env()
    ep = wait_compute(e)
    host = ep["host"]
    say(f"== F-PROD-1 bank probe — READ-ONLY on review branch {e['review_branch_id']} (ep {host}) ==")

    rows = None
    for attempt in range(10):
        try:
            rows = sql(e, host, "select current_database() as db")
            break
        except Exception as ex:
            say(f"connect attempt {attempt+1}: {type(ex).__name__} {str(ex)[:100]} — retry 10s")
            time.sleep(10)
    if not rows or rows[0]["db"] != "neondb":
        raise SystemExit("identity gate failed")
    say("identity gate PASS (neondb)")

    result = {"probe_time_utc": datetime.now(timezone.utc).isoformat(),
              "branch": e["review_branch_id"]}

    # ── banked per-question state, latest version per question ───────────
    rows = sql(e, host, """
        select p.id as paper_id, p.paper_code, p.session_label,
               q.id as question_id, q.external_ref, q.active, q.question_type,
               qv.version as bank_version, qv.validation_state as bank_state,
               qv.marks as bank_marks,
               (select coalesce(sum(pp.marks), 0)::int from question_parts pp
                 where pp.question_version_id = qv.id) as part_marks,
               (select count(*)::int from question_parts pp
                 where pp.question_version_id = qv.id) as n_parts,
               (select count(*)::int from mark_schemes m
                 where m.question_version_id = qv.id) as n_schemes
        from glm_ocr_bridge_records b
        join exam_papers p on p.id = b.paper_id
        join questions q on q.exam_paper_id = p.id
        join question_versions qv on qv.question_id = q.id
         and qv.version = (select max(version) from question_versions v2
                            where v2.question_id = q.id)
        where b.reconciliation_status = 'REVIEW_REQUIRED'
        order by p.paper_code, p.session_label, q.external_ref""")
    result["banked_questions"] = rows
    say(f"banked question rows: {len(rows)}")

    # paper-level census for the 25: how many questions active/versions/states
    rows = sql(e, host, """
        select p.paper_code, p.session_label,
               count(*)::int as n_questions,
               count(*) filter (where q.active)::int as n_active,
               count(*) filter (where qv.validation_state = 'VALIDATED')::int as n_qv_validated,
               count(*) filter (where qv.validation_state = 'SUGGESTED')::int as n_qv_suggested,
               count(*) filter (where qv.validation_state = 'REJECTED')::int as n_qv_rejected,
               sum(qv.marks)::int as total_bank_marks
        from glm_ocr_bridge_records b
        join exam_papers p on p.id = b.paper_id
        join questions q on q.exam_paper_id = p.id
        join question_versions qv on qv.question_id = q.id
         and qv.version = (select max(version) from question_versions v2
                            where v2.question_id = q.id)
        where b.reconciliation_status = 'REVIEW_REQUIRED'
        group by 1, 2 order by 1, 2""")
    result["paper_bank_census"] = rows
    say(f"paper bank census rows: {len(rows)}")

    json.dump(result, open(OUT_JSON, "w"), indent=1, default=str)
    open(OUT_TXT, "w").write("\n".join(_lines) + "\n")
    say(f"written: {OUT_JSON}")


if __name__ == "__main__":
    main()
