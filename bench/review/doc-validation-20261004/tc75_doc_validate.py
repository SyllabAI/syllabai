#!/usr/bin/env python3
"""tc75_doc_validate.py — T-C75 follow-on act (a): doc-side VALIDATION.

Batch: tc75-doc-validation-20261004. The T-C75 card records, as its FIRST
next_safe_action, "(a) doc-side VALIDATION of the 6 new 2026-06 SUGGESTED
docs (unlocks subject-side serving on top of the ep-side serving delivered
today)" — a separate operator-gated act. The operator's word for THIS batch,
verbatim: "(a) doc-side VALIDATION" (IM trace 1a106d1f681a80ad, 2026-10-04).

The instrument is the T-C54 wave-2 governed doc-validation batch shape
(bench/review/wave2-validation-2026-10-02/apply_wave2_validation.py, 297
docs APPLIED 2026-10-02) narrowed to the wave's own 6 documents:

  ACT — documents.validation_state: SUGGESTED -> VALIDATED for exactly the
        6 W2-ingested 2026-06 docs (3 QP + 3 MS; documentId + checksum +
        chunk-count pins == the staged inventory / ingest report), per-row
        UPDATE ... WHERE validation_state='SUGGESTED' asserting rowcount==1;
  + one content_review_audit row per document (action VALIDATE,
        target_type 'document' — live constraint pre-read; if 'document' is
        not allowed this runner ABORTS, it performs no DDL), actor_label
        naming the OPERATOR as deciding actor; the agent asserts no
        validation of its own;
  + nothing else: zero document_chunks writes, exam_papers untouched
        (108 = 95V/13R), teacher_validation_events delta 0 enforced, full
        documents state x kind census snapshot compared pre/post with only
        the 6 flips allowed.

Serving-gate semantics (the honest difference vs the T-C54 wave-2 act):
the wave docs' 68 chunks ALREADY serve via the PAPER branch (the W2
governed ep batch 3507fb0f linked them from 4 VALIDATED exam_papers rows;
gate 4,593 -> 4,661 realized). This flip adds the SUBJECT branch
(d.validation_state = 'VALIDATED' + chunk subject in the ACTIVE cv) for
the same 68 chunks, so the predicted gate delta is EXACTLY 0 (4,661 ->
4,661) while the per-doc subject-branch count goes 0 -> 68. Both numbers
are asserted in-transaction; a non-zero gate delta ABORTS for re-derivation.

Fail-closed chain (single transaction, no DDL):
  identity gate (neondb / neondb_owner / T-C04-CAMPAIGN) -> idempotence
  (prior batch audit rows) -> exactly-one-ACTIVE cv 356840e6… (4CH1-2017)
  -> live drift rule (the SUGGESTED QP/MS-with-chunks surface == exactly
  the 6 wave document_ids) -> per-doc fidelity (kind, state, doc_version 1,
  checksum, chunks, embedded, subject-scope 68/68) -> census prestate ==
  W2 poststate pins -> gate replica 4,661 pre -> constraint pre-read
  -> 6 flips -> 6 audit rows -> post-asserts (census shift, chunks equal,
  audit +6, tve 0, ep unchanged, gate delta 0, subject-branch 68/68).

DRY_RUN default (all asserts pass, transaction ROLLED BACK, status
DRY_RUN_OK). EXECUTE=1 (or --execute) commits. Re-run after apply ->
status ALREADY_APPLIED (clean no-op). Raw secrets never reach
stdout/reports (Neon key read from 0600 .secrets file; URI never printed).
Stdlib + psycopg2 only.
"""
import hashlib
import json
import os
import pathlib
import sys
import urllib.request
import uuid
from datetime import datetime, timezone

import psycopg2

HERE = pathlib.Path(__file__).resolve().parent
OUT_DIR = pathlib.Path("/home/z/my-project/work/tc75-w2")
SECRETS = pathlib.Path("/home/z/my-project/.secrets")
API = "https://console.neon.tech/api/v2"
PROJECT = "billowing-cherry-15418366"
PRODUCTION_BRANCH = "br-muddy-bar-a5huwldd"

BATCH = "tc75-doc-validation-20261004"
OPERATOR = "Nawaf Al Hussain Khondokar"
OPERATOR_TRACE_ID = "1a106d1f681a80ad"      # the operator word (this batch)
W2_TRACE_ID = "1a106209161c8e75"            # the operator word 'run W2'
DECISION_TEXT = "(a) doc-side VALIDATION"
AUTHORITY = ("T-C75 card next_safe_actions (a) — doc-side VALIDATION of the 6 new "
             "2026-06 SUGGESTED docs (unlocks subject-side serving); operator word "
             "per DB batch; instrument shape = the T-C54 wave-2 governed "
             "doc-validation batch (297 docs, 2026-10-02) narrowed to the wave docs")

ADMIN_UID = "8f9839ee-2959-4b49-b104-fef78373aa15"
SUBJECT_ID = "e56dc9ee-aa74-426f-94a6-4b72d3dc346b"
CORPUS_PIN = "b8d53f7"
EP_BATCH_RUN = "3507fb0f-317c-4c96-bbd2-0be99ce49e38"

# The worklist: the 6 W2-ingested 2026-06 docs. Pins == the staged inventory
# (w2-doc-inventory.json) + tc75_w2_ingest_report.json + the ep batch's
# EP_INSERTS row_state pins. The live re-derivation asserts every field.
WORKLIST = [
    {"dir": "4CH1-1C-202606", "side": "qp", "kind": "QUESTION_PAPER",
     "document_id": "c6fbb3ac-4056-5838-8732-b71993d7fe61",
     "checksum": "231c05743b0853aa408ae22103faf2645baca81e44fbc839972adc493abbede3",
     "chunks": 11},
    {"dir": "4CH1-1C-202606", "side": "ms", "kind": "MARK_SCHEME",
     "document_id": "a03447d8-7c1b-5fac-92e7-c2e91ca8db3d",
     "checksum": "d4febc1650d2632a220e5ed367d05d99880bcf2b5cf73c434eb2ff7aac3c5040",
     "chunks": 18},
    {"dir": "4CH1-2C-202606", "side": "qp", "kind": "QUESTION_PAPER",
     "document_id": "ea685722-b453-5c5f-8e19-1f4b868bc0b1",
     "checksum": "713f1fccc169d6b716b0a2713bc07bbf1aa94a34a25e298fd2e6c3b449dcc9a3",
     "chunks": 9},
    {"dir": "4CH1-2C-202606", "side": "ms", "kind": "MARK_SCHEME",
     "document_id": "b5742cb1-c413-5a66-a782-24f90facda89",
     "checksum": "a42a22c4852946905431acf1190775855ad211e616bb380589e9a057fa4d6960",
     "chunks": 10},
    {"dir": "4CH1-2CR-202606", "side": "qp", "kind": "QUESTION_PAPER",
     "document_id": "b0660052-3ecc-598f-b1c1-7e970eba8efb",
     "checksum": "5ee0d5b49eac889dbc2dc3f7894a4dc3eff8c0808e3ee94f9425e27c0169f980",
     "chunks": 9},
    {"dir": "4CH1-2CR-202606", "side": "ms", "kind": "MARK_SCHEME",
     "document_id": "e3252e22-9c18-5af2-890d-32275430eecd",
     "checksum": "a005acd5e9b80355d7b11492adb598083664f10e076ce557002b2d1911c52b05",
     "chunks": 11},
]

GUARDS = {
    "expected_database": "neondb",
    "expected_campaign_label": "T-C04-CAMPAIGN",
    "active_curriculum_version_id": "356840e6-81e2-49df-8182-93ab6504d591",
    "active_curriculum_version_code": "4CH1-2017",
    "subject_id_4ch1": SUBJECT_ID,
    "docs_total": 1023,
    # documents state x kind census, W2 poststate (ep batch GUARDS + wave docs)
    "docs_census_pre": {
        "VALIDATED|EXTERNAL_NOTES": 112,
        "VALIDATED|EXTERNAL_QUESTIONS": 379,
        "REJECTED|MARK_SCHEME": 67,
        "VALIDATED|MARK_SCHEME": 109,
        "REJECTED|QUESTION_PAPER": 79,
        "VALIDATED|QUESTION_PAPER": 109,
        "VALIDATED|SYLLABUS": 162,
        "SUGGESTED|QUESTION_PAPER": 3,
        "SUGGESTED|MARK_SCHEME": 3,
    },
    "ep_total": 108,
    "ep_states": {"VALIDATED": 95, "REJECTED": 13},
    "chunks_rev2_embedded": 4740,
    "audit_pre": 2829,
    "tve": 0,
    "gate_expected": 4661,
    "gate_expected_delta": 0,          # the honest prediction: paper branch covers
    "subject_branch_pre": 0,           # all 68 already; the flip adds the subject branch
    "subject_branch_post": 68,
}

# The exact searchServingEligible replica (ChunkVectorRepository
# SCOPE_EXISTS_VALIDATED at CURRENT_EMBED_REV=2) — same SQL the W2 ep batch
# and the T-C54 wave-2 batch asserted.
GATE_SQL = """
    select count(*)::int as n from document_chunks c
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
"""

# SUBJECT-branch-only count for the wave docs (leg 2 alone): 0 pre-flip
# (docs SUGGESTED), 68 post-flip (docs VALIDATED + every chunk in scope).
SUBJECT_BRANCH_SQL = """
    select count(*)::int from document_chunks c
    join documents d on d.id = c.document_row_id
    where c.embedding is not null and c.embed_rev = 2
      and d.document_id = any(%s)
      and exists (
            select 1 from subjects s2
            where s2.curriculum_version_id = %s
              and s2.id = c.subject_id
              and d.validation_state = 'VALIDATED')
"""


def resolve_db_url():
    key = (SECRETS / "neon_api_key.txt").read_text().strip()
    req = urllib.request.Request(
        f"{API}/users/me/organizations",
        headers={"Authorization": f"Bearer {key}"})
    orgs = json.load(urllib.request.urlopen(req, timeout=60))["organizations"]
    assert len(orgs) == 1
    req = urllib.request.Request(
        f"{API}/projects/{PROJECT}/connection_uri?branch_id={PRODUCTION_BRANCH}"
        f"&database_name=neondb&role_name=neondb_owner&pooled=true",
        headers={"Authorization": f"Bearer {key}"})
    d = json.load(urllib.request.urlopen(req, timeout=60))
    uri = d.get("uri") or d.get("connection_uri")
    assert uri, f"connection_uri shape: {d}"
    return uri, "neon-api:pooled-uri (T-C54 pin)"


def one(cur, sql, args=None):
    cur.execute(sql, args)
    return cur.fetchone()


def census_docs(cur):
    cur.execute("select validation_state, kind, count(*)::int from documents group by 1, 2")
    return {f"{r[0]}|{r[1]}": r[2] for r in cur.fetchall()}


def census_chunks(cur):
    cur.execute("""select coalesce(embed_rev::text,'null') rev, count(*)::int n,
                   count(embedding)::int embedded from document_chunks group by 1 order by 1""")
    return {r[0]: {"chunks": r[1], "embedded": r[2]} for r in cur.fetchall()}


def gate_eligible(cur, active_cv):
    cur.execute(GATE_SQL, (active_cv, active_cv))
    return cur.fetchone()[0]


def subject_branch(cur, active_cv):
    cur.execute(SUBJECT_BRANCH_SQL, ([w["document_id"] for w in WORKLIST], active_cv))
    return cur.fetchone()[0]


def audit_actor():
    return (f"operator — {OPERATOR} (operator word '{DECISION_TEXT}' IM trace "
            f"{OPERATOR_TRACE_ID}; governed batch {BATCH}; the agent asserts no "
            f"validation of its own)")


def detail_base(batch_run_id, plan_sha):
    return {
        "applied_by": "agent session executing the operator's named instruction "
                      "(the agent asserts no validation of its own)",
        "batch": BATCH, "batch_run_id": batch_run_id, "plan_sha256": plan_sha,
        "operator": OPERATOR,
        "operator_trace_id": OPERATOR_TRACE_ID,
        "w2_trace_id": W2_TRACE_ID,
        "decision_text": DECISION_TEXT,
        "instrument": "T-C54 wave-2 governed doc-validation batch shape "
                      "(apply_wave2_validation.py, 297 docs 2026-10-02) narrowed "
                      "to the 6 T-C75 wave docs",
        "authority": AUTHORITY,
        "corpus_pin": CORPUS_PIN,
        "ep_batch_run_id": EP_BATCH_RUN,
    }


def main() -> int:
    execute = os.environ.get("EXECUTE") == "1" or "--execute" in sys.argv
    stamp = datetime.now(timezone.utc).isoformat()
    report = {"batch": BATCH, "mode": "EXECUTE" if execute else "DRY_RUN",
              "started_at_utc": stamp, "operator_trace_id": OPERATOR_TRACE_ID}

    plan_bytes = HERE.joinpath("tc75_doc_validate.py").read_bytes()
    plan_sha = hashlib.sha256(plan_bytes).hexdigest()
    report["plan_sha256"] = plan_sha

    url, source = resolve_db_url()
    report["credential_source"] = source
    conn = psycopg2.connect(url, sslmode="require", connect_timeout=30)
    conn.set_session(readonly=False, autocommit=False)
    cur = conn.cursor()
    batch_run_id = str(uuid.uuid4())
    report["batch_run_id"] = batch_run_id

    try:
        # ---- identity gate --------------------------------------------------
        a = one(cur, "select current_database(), current_user")
        assert a[0] == GUARDS["expected_database"], f"DB identity gate: {a}"
        assert a[1] == "neondb_owner", f"DB role gate: {a}"
        idrow = one(cur, "select campaign_label, db_name from campaign_db_identity where id = 1")
        assert idrow and idrow[0] == GUARDS["expected_campaign_label"] \
            and idrow[1] == GUARDS["expected_database"], f"campaign identity gate: {idrow}"
        report["identity"] = {"database": a[0], "role": a[1], "campaign": idrow[0]}
        print(f"identity gate PASS: {a[0]}/{a[1]} {idrow[0]}", flush=True)

        # ---- idempotence ----------------------------------------------------
        cur.execute("""select count(*)::int from content_review_audit
                       where action = 'VALIDATE' and target_type = 'document'
                         and detail like %s""", (f"%{BATCH}%",))
        prior = cur.fetchone()[0]
        wave_ids = [w["document_id"] for w in WORKLIST]
        cur.execute("""select document_id, validation_state from documents
                       where document_id = any(%s)""", (wave_ids,))
        states = {r[0]: r[1] for r in cur.fetchall()}
        if prior:
            if (len(states) == 6 and all(v == "VALIDATED" for v in states.values())):
                report["status"] = "ALREADY_APPLIED"
                report["prior_audit_rows"] = prior
                report["wave_docs_all_VALIDATED"] = True
                print(json.dumps(report, indent=2))
                conn.rollback()
                return 0
            report["status"] = "ABORT_MANUAL_REVIEW"
            report["error"] = (f"batch appears applied ({prior} audit rows) but "
                               f"wave-doc states drifted: {states}")
            print(json.dumps(report, indent=2))
            conn.rollback()
            return 3
        assert not any(v == "VALIDATED" for v in states.values()), \
            f"wave docs already (partially) VALIDATED without this batch's audit rows: {states}"

        # ---- ACTIVE cv + subject -------------------------------------------
        cur.execute("select id::text, code from curriculum_versions where status='ACTIVE' order by created_at desc")
        actives = cur.fetchall()
        assert len(actives) == 1, f"ACTIVE cv count {len(actives)}"
        active_id, active_code = actives[0]
        assert active_id == GUARDS["active_curriculum_version_id"] \
            and active_code == GUARDS["active_curriculum_version_code"], f"ACTIVE cv drifted: {actives}"
        subj = one(cur, "select id::text, code, curriculum_version_id::text from subjects where id = %s",
                   (SUBJECT_ID,))
        assert subj and subj[0] == SUBJECT_ID and subj[2] == active_id, f"subject gate: {subj}"
        report["active_cv"] = {"id": active_id, "code": active_code}
        print(f"cv gate PASS: {active_code} / subject {subj[1]}", flush=True)

        # ---- live drift rule: SUGGESTED QP/MS-with-chunks surface == the 6 ---
        cur.execute("""
            select d.document_id, count(c.id)::int as chunks
            from documents d
            join document_chunks c on c.document_row_id = d.id
            where d.validation_state = 'SUGGESTED'
              and d.kind in ('QUESTION_PAPER','MARK_SCHEME')
            group by d.document_id
        """)
        drift = {r[0]: r[1] for r in cur.fetchall()}
        assert set(drift) == set(wave_ids), (
            f"live SUGGESTED QP/MS surface drifted vs the wave worklist: "
            f"only-live={sorted(set(drift) - set(wave_ids))[:5]} "
            f"only-worklist={sorted(set(wave_ids) - set(drift))[:5]}")
        print("live drift rule PASS: the SUGGESTED QP/MS-with-chunks surface is exactly the 6 wave docs",
              flush=True)

        # ---- per-doc fidelity ----------------------------------------------
        cur.execute("""
            select d.document_id, d.id::text, d.kind, d.validation_state, d.doc_version,
                   d.checksum, count(c.id)::int, count(c.embedding)::int,
                   count(*) filter (where s2.curriculum_version_id = %s)::int
            from documents d
            join document_chunks c on c.document_row_id = d.id
            left join subjects s2 on s2.id = c.subject_id
            where d.document_id = any(%s)
            group by d.document_id, d.id, d.kind, d.validation_state, d.doc_version, d.checksum
        """, (active_id, wave_ids))
        live = {r[0]: {"row_id": r[1], "kind": r[2], "state": r[3], "doc_version": r[4],
                       "checksum": r[5], "chunks": r[6], "embedded": r[7], "in_scope": r[8]}
                for r in cur.fetchall()}
        for w in WORKLIST:
            l = live.get(w["document_id"])
            assert l is not None, f"{w['dir']}/{w['side']}: doc missing live"
            assert l["kind"] == w["kind"], f"{w['dir']}/{w['side']}: kind {l['kind']} != {w['kind']}"
            assert l["state"] == "SUGGESTED", f"{w['dir']}/{w['side']}: state {l['state']}"
            assert l["doc_version"] == 1, f"{w['dir']}/{w['side']}: doc_version {l['doc_version']}"
            assert l["checksum"] == w["checksum"], f"{w['dir']}/{w['side']}: checksum drift"
            assert l["chunks"] == w["chunks"], f"{w['dir']}/{w['side']}: chunks {l['chunks']} != {w['chunks']}"
            assert l["embedded"] == l["chunks"], f"{w['dir']}/{w['side']}: non-embedded chunks"
            assert l["in_scope"] == l["chunks"], f"{w['dir']}/{w['side']}: chunks outside ACTIVE scope"
        assert sum(l["chunks"] for l in live.values()) == 68, "wave chunk mass != 68"
        report["per_doc_fidelity"] = "6/6 PASS (kind, state, doc_version, checksum, chunks, embedded, subject-scope)"
        print("per-doc fidelity PASS: 6/6 (checksums + chunk pins + 68/68 in-scope)", flush=True)

        # ---- non-interference prestate ---------------------------------------
        docs_pre_map = census_docs(cur)
        docs_pre = sum(docs_pre_map.values())
        assert docs_pre == GUARDS["docs_total"], f"docs_total drifted: {docs_pre}"
        assert docs_pre_map == GUARDS["docs_census_pre"], \
            f"documents census drifted: {docs_pre_map} != {GUARDS['docs_census_pre']}"
        cur.execute("select count(*)::int from exam_papers")
        ep_pre = cur.fetchone()[0]
        assert ep_pre == GUARDS["ep_total"], f"ep_total drifted: {ep_pre}"
        cur.execute("select validation_state, count(*)::int from exam_papers group by 1")
        ep_states_pre = dict(cur.fetchall())
        assert ep_states_pre == GUARDS["ep_states"], f"ep states drifted: {ep_states_pre}"
        chunks_pre = census_chunks(cur)
        assert chunks_pre.get("2", {}).get("embedded") == GUARDS["chunks_rev2_embedded"], \
            f"chunks drifted: {chunks_pre}"
        cur.execute("select count(*)::int from content_review_audit")
        audit_pre = cur.fetchone()[0]
        assert audit_pre == GUARDS["audit_pre"], f"audit_pre drifted: {audit_pre}"
        cur.execute("select count(*)::int from teacher_validation_events")
        tve_pre = cur.fetchone()[0]
        assert tve_pre == GUARDS["tve"], f"teacher_validation_events drifted: {tve_pre}"
        report["pre"] = {"docs": docs_pre, "ep": ep_pre, "audit": audit_pre,
                         "tve": tve_pre}
        print(f"prestate PASS: docs {docs_pre} (6 SUGGESTED wave docs), ep {ep_pre} {ep_states_pre}, "
              f"audit {audit_pre}, tve {tve_pre}", flush=True)

        # ---- serving-gate replica pre + subject-branch pre --------------------
        gate_pre = gate_eligible(cur, active_id)
        assert gate_pre == GUARDS["gate_expected"], \
            f"gate replica drifted pre: {gate_pre} != {GUARDS['gate_expected']} — census re-derive required"
        sb_pre = subject_branch(cur, active_id)
        assert sb_pre == GUARDS["subject_branch_pre"], \
            f"subject-branch pre {sb_pre} != {GUARDS['subject_branch_pre']} (wave docs should not serve subject-side yet)"
        report["pre_gate_eligible"] = gate_pre
        report["pre_subject_branch"] = sb_pre
        print(f"gate replica PASS: {gate_pre} (== 4,661 W2 poststate); "
              f"subject-branch for the wave docs: {sb_pre} (pre-flip)", flush=True)

        # ---- constraint present? (no DDL — abort if missing) -------------------
        cons = one(cur, """
            select
              (select pg_get_constraintdef(oid) from pg_constraint where conname = 'ck_cra_action'),
              (select pg_get_constraintdef(oid) from pg_constraint where conname = 'ck_cra_target_type')
        """)
        assert cons and cons[0] and cons[1], f"audit constraints missing: {cons}"
        assert "VALIDATE" in cons[0], f"ck_cra_action lacks VALIDATE: {cons[0]}"
        assert "'document'" in cons[1], \
            f"ck_cra_target_type missing 'document': {cons[1]} — aborting (no DDL in this batch)"
        report["audit_constraints"] = "present (VALIDATE allowed; 'document' target allowed)"
        print("constraint pre-check PASS (VALIDATE / 'document' allowed — no DDL)", flush=True)

        # ---- the flip: 6 documents, worklist order, rowcount==1 each ----------
        flipped = []
        for w in WORKLIST:
            cur.execute("""update documents set validation_state = 'VALIDATED'
                           where id = %s::uuid and validation_state = 'SUGGESTED'
                             and doc_version = 1""", (live[w["document_id"]]["row_id"],))
            assert cur.rowcount == 1, \
                f"{w['dir']}/{w['side']}: flip rowcount {cur.rowcount} != 1"
            flipped.append({"document_id": w["document_id"], "kind": w["kind"],
                            "dir": w["dir"], "side": w["side"], "chunks": w["chunks"],
                            "checksum_sha256": w["checksum"]})
        report["docs_flipped"] = flipped
        print("flip OK: 6/6 rowcount==1 (SUGGESTED -> VALIDATED, doc_version 1)", flush=True)

        # ---- audit rows --------------------------------------------------------
        base = detail_base(batch_run_id, plan_sha)
        for w in WORKLIST:
            detail = dict(base)
            detail.update({
                "act": "doc_side_validate",
                "document_id": w["document_id"],
                "document_kind": w["kind"],
                "source_dir": w["dir"], "source_side": w["side"],
                "checksum_sha256": w["checksum"],
                "chunks": w["chunks"],
                "serving_semantics": ("gate delta predicted 0 — the 68 chunks already serve "
                                      "ep-side via the 4 VALIDATED ep rows (batch "
                                      f"{EP_BATCH_RUN}); this flip adds the SUBJECT branch "
                                      "(d.validation_state=VALIDATED + chunk subject in the "
                                      "ACTIVE cv) for the same 68 chunks: subject-side serving "
                                      "unlocked on top of ep-side serving"),
                "preflight": {"gate_eligible_before": gate_pre,
                              "expected_after": gate_pre + GUARDS["gate_expected_delta"],
                              "subject_branch_before": sb_pre,
                              "subject_branch_after_expected": GUARDS["subject_branch_post"]},
            })
            cur.execute("""insert into content_review_audit
                               (occurred_at, actor_user_id, actor_label, action,
                                target_type, target_id, from_state, to_state, detail)
                           values (now(), %s, %s, 'VALIDATE', 'document', %s::uuid,
                                   'SUGGESTED', 'VALIDATED', %s)""",
                        (ADMIN_UID, audit_actor(), live[w["document_id"]]["row_id"],
                         json.dumps(detail)))
        report["audit_rows_written"] = len(WORKLIST)
        print("audit OK: 6 VALIDATE/document rows, operator named as deciding actor", flush=True)

        # ---- in-transaction post-asserts --------------------------------------
        docs_post_map = census_docs(cur)
        # expected post-census = pre-census minus every SUGGESTED key, plus the
        # per-kind flip counts moved into VALIDATED (3 QP + 3 MS -> +3/+3)
        flip_by_kind = {}
        for w in WORKLIST:
            flip_by_kind[w["kind"]] = flip_by_kind.get(w["kind"], 0) + 1
        expected_map = {k: v for k, v in GUARDS["docs_census_pre"].items()
                        if not k.startswith("SUGGESTED|")}
        for kind, n in flip_by_kind.items():
            key = f"VALIDATED|{kind}"
            expected_map[key] = expected_map.get(key, 0) + n
        assert docs_post_map == expected_map, \
            f"documents census post != pre shifted by exactly the 6 flips: " \
            f"{docs_post_map} != {expected_map}"
        chunks_post = census_chunks(cur)
        assert chunks_post == chunks_pre, f"document_chunks changed: {chunks_pre} -> {chunks_post}"
        cur.execute("select count(*)::int from content_review_audit")
        audit_post = cur.fetchone()[0]
        assert audit_post == audit_pre + len(WORKLIST), \
            f"audit delta {audit_post - audit_pre} != {len(WORKLIST)}"
        cur.execute("select count(*)::int from teacher_validation_events")
        tve_post = cur.fetchone()[0]
        assert tve_post == tve_pre, "teacher_validation_events changed"
        cur.execute("select count(*)::int from exam_papers")
        ep_post = cur.fetchone()[0]
        cur.execute("select validation_state, count(*)::int from exam_papers group by 1")
        ep_states_post = dict(cur.fetchall())
        assert ep_post == ep_pre and ep_states_post == ep_states_pre, \
            f"exam_papers changed: {ep_post} {ep_states_post}"
        gate_post = gate_eligible(cur, active_id)
        assert gate_post == gate_pre + GUARDS["gate_expected_delta"], \
            f"gate post {gate_post} != {gate_pre} + {GUARDS['gate_expected_delta']} — " \
            "the wave docs' chunks were expected to already serve ep-side; re-derive"
        assert gate_post == GUARDS["gate_expected"], f"gate post {gate_post} != 4,661"
        sb_post = subject_branch(cur, active_id)
        assert sb_post == GUARDS["subject_branch_post"], \
            f"subject-branch post {sb_post} != {GUARDS['subject_branch_post']} — " \
            "the flip did not unlock the subject branch for the wave chunks"
        # every wave doc now VALIDATED
        cur.execute("""select document_id, validation_state from documents
                       where document_id = any(%s)""", (wave_ids,))
        states_post = {r[0]: r[1] for r in cur.fetchall()}
        assert len(states_post) == 6 and all(v == "VALIDATED" for v in states_post.values()), \
            f"post states: {states_post}"

        report["post"] = {"docs": sum(docs_post_map.values()),
                          "docs_census": docs_post_map, "ep": ep_post,
                          "ep_states": ep_states_post, "audit": audit_post,
                          "tve": tve_post, "gate": gate_post,
                          "gate_delta": gate_post - gate_pre,
                          "subject_branch": sb_post}
        print(f"post-asserts PASS: docs {sum(docs_post_map.values())} (0 SUGGESTED), "
              f"ep {ep_post} unchanged, audit {audit_post} (+6), tve {tve_post}, "
              f"gate {gate_pre} -> {gate_post} (delta {gate_post - gate_pre} as predicted), "
              f"subject-branch {sb_pre} -> {sb_post} (68/68 wave chunks unlocked)", flush=True)

        if execute:
            conn.commit()
            report["status"] = "APPLIED"
            report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
            print("BATCH APPLIED (committed)", flush=True)
        else:
            conn.rollback()
            report["status"] = "DRY_RUN_OK"
            report["note"] = "all asserts passed; transaction rolled back (dry run)"
            print("DRY_RUN OK — all gates passed, transaction ROLLED BACK", flush=True)
    except AssertionError as e:
        conn.rollback()
        report["status"] = "ABORTED_ASSERT"
        report["error"] = str(e)
        (OUT_DIR / "tc75_doc_validate_report.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        return 4
    except Exception as e:  # noqa: BLE001 — fail-closed on any error
        conn.rollback()
        report["status"] = "ABORTED_ERROR"
        report["error"] = f"{type(e).__name__}: {e}"
        (OUT_DIR / "tc75_doc_validate_report.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        return 5

    (OUT_DIR / "tc75_doc_validate_report.json").write_text(json.dumps(report, indent=2, default=str))
    print("written: work/tc75-w2/tc75_doc_validate_report.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
