#!/usr/bin/env python3
"""flagged3 flip — apply the operator's named VALIDATE decision for sheet #207/#278/#291.

The 3 FLAGGED T-C27 cards were source-verified 3/3 faithful
(bench/evidence/flagged3-source-verify-2026-09-28/REPORT.md, sha256-pinned).
The operator (Nawaf Al Hussain Khondokar) then gave the named decision, verbatim:
    "flip #207/#278/#291 to VALIDATE. And continue you to work autonomously.
     I dont have time to do anything"            (IM trace 1a0e7865c3b35715)

This script applies EXACTLY that decision and nothing else:
  * documents.validation_state: FLAGGED -> VALIDATED for the 3 pinned UUIDs;
  * one content_review_audit row each (action VALIDATE, target_type 'question' —
    the proven wave-import vocabulary, same table as run a5d13c0a...);
  * nothing else: no content writes, no chunk writes (document_chunks has no
    state column — serving state derives from the parent document via the JOIN),
    no embedding writes, no bank writes.

Connection (the sanctioned per-session pattern, never printed, never persisted):
  1. $SYLLABAI_DATABASE_URL  (per-session handoff, T-C23/snap005 precedent), or
  2. scripts/.render_env.json next to this file's repo root (the snap005 path),
     keys SYLLABAI_DATABASE_URL / SYLLABAI_DATABASE_USERNAME / SYLLABAI_DATABASE_PASSWORD.

Fail-closed guarantees:
  * every card must exist, be kind EXTERNAL_QUESTIONS, and be FLAGGED pre-state;
  * the kind census must match the recorded pre-census exactly (296V/80S/3F — amended 2026-09-28 to the live-probed census; the kit author's original 306V/747S was derived, not probed)
    — if production moved under us, abort and re-verify first;
  * idempotent: a prior application of THIS batch (same batch id in the audit
    detail) is detected and no-ops with SUCCESS+already_applied; audit rows from
    any OTHER prior VALIDATE on these targets abort for manual review;
  * single transaction; commit only if every assert passes; otherwise rollback;
  * post-commit re-probe printed for the run record.

Output: JSON run report on stdout (zero credentials, zero connection material).
"""
import datetime
import hashlib
import json
import os
import sys
import uuid

import psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
RECORDS_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DECISIONS_PATH = os.path.join(HERE, "flip_decisions.json")
RENDER_ENV_PATH = os.path.join(RECORDS_ROOT, "scripts", ".render_env.json")
RENDER_ENV_ALT = "/home/z/my-project/scripts/.render_env.json"

AUDIT_TABLE = "content_review_audit"


def resolve_db_url():
    url = os.environ.get("SYLLABAI_DATABASE_URL")
    if url:
        return url, "env:SYLLABAI_DATABASE_URL"
    for path in (RENDER_ENV_PATH, RENDER_ENV_ALT):
        if os.path.exists(path):
            env = json.load(open(path))
            env = env.get("env", env)
            if isinstance(env, list):
                # sanctioned file format: {"env": [{"key": ..., "value": ...}, ...]}
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


def census(cur):
    cur.execute(
        "SELECT validation_state, count(*) FROM documents "
        "WHERE kind = 'EXTERNAL_QUESTIONS' GROUP BY 1 ORDER BY 1")
    observed = dict(cur.fetchall())
    # zero-count states have no GROUP BY row — normalize so the recorded
    # census format (explicit zeros, e.g. FLAGGED: 0 after the flip) compares equal
    return {s: observed.get(s, 0)
            for s in ("VALIDATED", "SUGGESTED", "FLAGGED", "REJECTED")}


def main() -> int:
    decisions = json.load(open(DECISIONS_PATH))
    batch = decisions["batch"]
    cards = decisions["decisions"]
    assert len(cards) == 3, "the batch is exactly the 3 named cards"
    assert [c["sheet_seq"] for c in cards] == [207, 278, 291]

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
        report["note"] = ("no sanctioned connection material in this session — run from a "
                          "session holding SYLLABAI_DATABASE_URL (per-session handoff) or "
                          "scripts/.render_env.json; the decision itself is already recorded")
        print(json.dumps(report, indent=2))
        return 2
    report["credential_source"] = source

    expected_pre = decisions["expected_census_delta"]["documents_kind_EXTERNAL_QUESTIONS"]["before"]
    expected_post = decisions["expected_census_delta"]["documents_kind_EXTERNAL_QUESTIONS"]["after"]

    conn = psycopg2.connect(url, sslmode="require", connect_timeout=30)
    conn.set_session(readonly=False, autocommit=False)
    cur = conn.cursor()
    committed = False
    try:
        # ---- idempotence: has THIS batch already been applied? ----------------
        # NOTE: resolve rows by document_id (varchar) FIRST — content_review_audit
        # target_id is the documents.id ROW UUID (the proven wave vocabulary, run
        # a5d13c0a: target_id = row uuid, card document_id in the detail text).
        cur.execute(
            "SELECT id::text, document_id, kind, validation_state, source_uri "
            "FROM documents WHERE document_id = ANY(%s) ORDER BY document_id",
            ([c["document_id"] for c in cards],))
        rows = {r[1]: r for r in cur.fetchall()}
        row_ids = []
        for c in cards:
            r = rows.get(c["document_id"])
            if r is None:
                raise AssertionError(f"card #{c['sheet_seq']} {c['document_id']} not found by document_id")
            if r[2] != "EXTERNAL_QUESTIONS":
                raise AssertionError(f"card #{c['sheet_seq']} kind={r[2]} != EXTERNAL_QUESTIONS")
            row_ids.append(r[0])
        cur.execute(
            f"SELECT count(*) FROM {AUDIT_TABLE} WHERE target_type='question' "
            f"AND target_id::text = ANY(%s) AND action='VALIDATE' "
            f"AND to_state='VALIDATED' AND detail LIKE %s",
            (row_ids, "%" + batch + "%"))
        already = cur.fetchone()[0]
        if already == len(cards):
            cur.execute(
                "SELECT id::text, validation_state FROM documents "
                "WHERE id::text = ANY(%s) ORDER BY id",
                (row_ids,))
            states = {r[0]: r[1] for r in cur.fetchall()}
            if all(states.get(rid) == "VALIDATED" for rid in row_ids):
                report["status"] = "ALREADY_APPLIED"
                report["final_states"] = states
                report["census_after"] = census(cur)
                print(json.dumps(report, indent=2))
                conn.rollback()
                return 0
            report["status"] = "INCONSISTENT"
            report["note"] = "audit rows exist for this batch but documents are not all VALIDATED"
            print(json.dumps(report, indent=2))
            conn.rollback()
            return 3

        # ---- pre-assert 1: kind census must equal the recorded pre-census -----
        pre = census(cur)
        report["census_before"] = pre
        if pre != expected_pre:
            report["status"] = "ABORT_CENSUS_DRIFT"
            report["note"] = ("EXTERNAL_QUESTIONS census != recorded pre-census "
                              f"{expected_pre}; production moved since the freeze — "
                              "re-verify before any flip")
            print(json.dumps(report, indent=2))
            conn.rollback()
            return 4

        # ---- pre-assert 2: each card FLAGGED (row already resolved by id) -----
        for c, rid in zip(cards, row_ids):
            r = rows[c["document_id"]]
            if r[3] != "FLAGGED":
                raise AssertionError(
                    f"card #{c['sheet_seq']} pre-state={r[3]} != FLAGGED (fail-closed)")
            report.setdefault("cards", []).append({
                "sheet_seq": c["sheet_seq"], "id": r[0], "document_id_varchar": r[1],
                "pre_state": r[3], "source_uri": r[4], "to_state": "VALIDATED"})

        # ---- pre-assert 3: no foreign VALIDATE rows on these targets ---------
        cur.execute(
            f"SELECT count(*) FROM {AUDIT_TABLE} WHERE target_type='question' "
            f"AND target_id::text = ANY(%s) AND action='VALIDATE' AND to_state='VALIDATED'",
            (row_ids,))
        foreign = cur.fetchone()[0]
        if foreign:
            raise AssertionError(
                f"{foreign} prior VALIDATE audit row(s) exist for these targets from "
                "another batch — manual review required")

        if report["dry_run"]:
            conn.rollback()
            report["status"] = "DRY_RUN_OK"
            report["note"] = "all asserts passed; rolled back (FLIP_DRY_RUN=1)"
            print(json.dumps(report, indent=2))
            return 0

        # ---- the flip: 3 UPDATEs + 3 audit rows, one transaction -------------
        detail_base = json.dumps({
            "batch": batch,
            "batch_run_id": report["batch_run_id"],
            "operator": decisions["decision_authority"]["decision_owner"],
            "operator_trace_id": report["operator_trace_id"],
            "decision_text": decisions["decision_authority"]["decision_medium"],
            "basis_report_sha256": decisions["decision_authority"]["basis_report_sha256"],
            "sheet_sha256": decisions["decision_authority"]["parent_wave"]["sheet_sha256"],
            "decisions_file_sha256": hashlib.sha256(open(DECISIONS_PATH, "rb").read()).hexdigest(),
            "cards": [{"sheet_seq": c["sheet_seq"], "card_document_id": c["document_id"],
                       "external_ref": c["external_ref"]} for c in cards],
            "applied_by": "agent session executing the operator's named instruction "
                          "(the agent asserts no validation of its own)",
        }, sort_keys=True)
        for c, rid in zip(cards, row_ids):
            cur.execute(
                "UPDATE documents SET validation_state = 'VALIDATED' "
                "WHERE document_id = %s AND validation_state = 'FLAGGED'",
                (c["document_id"],))
            if cur.rowcount != 1:
                raise AssertionError(
                    f"card #{c['sheet_seq']} UPDATE rowcount={cur.rowcount} != 1")
            cur.execute(
                f"INSERT INTO {AUDIT_TABLE} "
                "(actor_user_id, actor_label, action, target_type, target_id, "
                " from_state, to_state, detail) VALUES "
                "(NULL, %s, 'VALIDATE', 'question', %s, 'FLAGGED', 'VALIDATED', %s)",
                (decisions["decision_authority"]["decision_owner"][:254],
                 rid, detail_base))
        post = census(cur)
        report["census_after"] = post
        if post != expected_post:
            raise AssertionError(f"post-census {post} != expected {expected_post}")

        conn.commit()
        committed = True
        report["status"] = "APPLIED"

        # ---- post-commit re-probe --------------------------------------------
        cur.execute(
            "SELECT document_id, validation_state FROM documents "
            "WHERE document_id = ANY(%s) ORDER BY document_id",
            ([c["document_id"] for c in cards],))
        report["final_states"] = {r[0]: r[1] for r in cur.fetchall()}
        cur.execute(
            f"SELECT count(*) FROM {AUDIT_TABLE} WHERE detail LIKE %s",
            ("%" + batch + "%",))
        report["audit_rows_committed"] = cur.fetchone()[0]
        report["serving_note"] = ("the 3 cards now satisfy the VALIDATED-only serving "
                                  "gate; whether the live read filter serves them is the "
                                  "embed_rev question recorded in TODO (not assumed here)")
        print(json.dumps(report, indent=2))
        return 0
    except Exception as exc:  # noqa: BLE001 — fail-closed: report, rollback, non-zero
        conn.rollback()
        report["status"] = "ABORTED" if not committed else "POST_COMMIT_PROBE_FAILED"
        report["error"] = str(exc)
        if committed:
            report["note"] = ("commit already succeeded; only the re-probe failed — "
                              "verify manually before re-running")
        print(json.dumps(report, indent=2))
        return 5 if not committed else 6
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    sys.exit(main())

