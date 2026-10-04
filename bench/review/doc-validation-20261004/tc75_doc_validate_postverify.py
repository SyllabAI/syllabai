#!/usr/bin/env python3
"""tc75_doc_validate_postverify.py — independent READ-ONLY post-verify for the
T-C75 follow-on act (a): doc-side VALIDATION (batch tc75-doc-validation-20261004).

Separate script, fresh READ-ONLY connection (driver-enforced set_session
readonly + default_transaction_read_only=on), re-derives every claim from the
live DB + the serving app — trusting nothing from the apply run:

  1. census bundle: 1023 docs, ZERO SUGGESTED, per-kind VALIDATED/REJECTED map
  2. the 6 wave docs: VALIDATED, doc_version 1, checksums == staged pins
  3. audit trail re-derivation: exactly 6 VALIDATE/document rows carrying this
     batch_run_id; per-row from_state SUGGESTED -> to_state VALIDATED; decision
     text + operator trace verbatim; one row per document_id (no strays)
  4. non-interference: ep 108 = 95V/13R (and the 4 wave ep rows still link the
     6 docs — the paper branch is untouched), chunks 4740/4740 rev2, tve 0
  5. serving-gate replica: 4,661 (delta 0 as predicted — paper branch already
     covered the 68) + subject-branch count for the 6 docs == 68 (the unlock,
     proven post-hoc from live rows) + per-doc subject-branch breakdown 6/6
  6. app-side probe (production core, read-only GET): the 6 documents now read
     validationState=VALIDATED on the serving surface + one kind-scoped search
     probe still returns the new papers (serving unchanged, no regression)

Output: JSON bundle to work/tc75-w2/tc75_doc_validate_postverify_result.json.
Zero writes; secrets never printed (JWT minted in-memory from the 0600 file).
"""
import base64
import hashlib
import hmac
import json
import pathlib
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import psycopg2

OUT_DIR = pathlib.Path("/home/z/my-project/work/tc75-w2")
SECRETS = pathlib.Path("/home/z/my-project/.secrets")
API = "https://console.neon.tech/api/v2"
PROJECT = "billowing-cherry-15418366"
PRODUCTION_BRANCH = "br-muddy-bar-a5huwldd"
BASE = "https://syllabai-core.onrender.com"
ADMIN_UID = "8f9839ee-2959-4b49-b104-fef78373aa15"
ADMIN_EMAIL = "admin@syllabai.dev"
SUBJECT_ID = "e56dc9ee-aa74-426f-94a6-4b72d3dc346b"
BATCH = "tc75-doc-validation-20261004"
OPERATOR_TRACE_ID = "1a106d1f681a80ad"

WAVE_DOCS = {
    "c6fbb3ac-4056-5838-8732-b71993d7fe61": ("4CH1-1C-202606", "qp", "QUESTION_PAPER", 11),
    "a03447d8-7c1b-5fac-92e7-c2e91ca8db3d": ("4CH1-1C-202606", "ms", "MARK_SCHEME", 18),
    "ea685722-b453-5c5f-8e19-1f4b868bc0b1": ("4CH1-2C-202606", "qp", "QUESTION_PAPER", 9),
    "b5742cb1-c413-5a66-a782-24f90facda89": ("4CH1-2C-202606", "ms", "MARK_SCHEME", 10),
    "b0660052-3ecc-598f-b1c1-7e970eba8efb": ("4CH1-2CR-202606", "qp", "QUESTION_PAPER", 9),
    "e3252e22-9c18-5af2-890d-32275430eecd": ("4CH1-2CR-202606", "ms", "MARK_SCHEME", 11),
}

_results = []


def check(name, ok, detail=""):
    _results.append({"check": name, "pass": bool(ok), "detail": str(detail)[:400]})
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""),
          flush=True)
    return bool(ok)


def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def mint_jwt(secret, tv):
    now = int(time.time())
    header = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    claims = b64url(json.dumps({
        "sub": ADMIN_EMAIL, "jti": ADMIN_UID, "uid": ADMIN_UID,
        "roles": ["ADMIN", "TEACHER"], "ver": tv,
        "iat": now, "exp": now + 600,
    }, separators=(",", ":")).encode())
    sig = hmac.new(secret.encode(), f"{header}.{claims}".encode(), hashlib.sha256).digest()
    return f"{header}.{claims}.{b64url(sig)}"


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat()
    print(f"== T-C75 (a) DOC-SIDE VALIDATION — INDEPENDENT POST-VERIFY (read-only) == {stamp}", flush=True)

    key = (SECRETS / "neon_api_key.txt").read_text().strip()
    req = urllib.request.Request(
        f"{API}/projects/{PROJECT}/connection_uri?branch_id={PRODUCTION_BRANCH}"
        f"&database_name=neondb&role_name=neondb_owner&pooled=true",
        headers={"Authorization": f"Bearer {key}"})
    uri = json.load(urllib.request.urlopen(req, timeout=60))["uri"]
    sep = "&" if "?" in uri else "?"
    conn = psycopg2.connect(uri + sep + "options=-c%20default_transaction_read_only%3Don",
                            sslmode="require", connect_timeout=30)
    conn.set_session(readonly=True, autocommit=True)
    cur = conn.cursor()

    def sql(query, args=None):
        cur.execute(query, args)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    wave_ids = list(WAVE_DOCS)

    # ---- 1. census bundle ---------------------------------------------------
    print("1. census bundle", flush=True)
    state_kind = {f"{r['validation_state']}|{r['kind']}": r["count"] for r in sql(
        "select validation_state, kind, count(*)::int from documents group by 1,2")}
    docs_total = sum(state_kind.values())
    check("docs_total == 1023", docs_total == 1023, docs_total)
    check("documents census == W2 poststate shifted by the 6 flips (0 SUGGESTED, QP 112V/79R, MS 112V/67R)",
          state_kind == {"VALIDATED|EXTERNAL_NOTES": 112, "VALIDATED|EXTERNAL_QUESTIONS": 379,
                         "REJECTED|MARK_SCHEME": 67, "VALIDATED|MARK_SCHEME": 112,
                         "REJECTED|QUESTION_PAPER": 79, "VALIDATED|QUESTION_PAPER": 112,
                         "VALIDATED|SYLLABUS": 162}, state_kind)

    # ---- 2. the 6 wave docs -------------------------------------------------
    print("2. wave docs state + identity", flush=True)
    rows = sql("""select document_id, id::text row_id, kind, validation_state, doc_version,
                         checksum, chunk_count
                  from documents where document_id = any(%s) order by kind, document_id""",
               (wave_ids,))
    ok = len(rows) == 6
    for r in rows:
        d, s, k, c = WAVE_DOCS[r["document_id"]]
        ok = ok and r["validation_state"] == "VALIDATED" and r["doc_version"] == 1 \
            and r["kind"] == k and r["chunk_count"] == c
    check("6/6 wave docs VALIDATED (doc_version 1, kind + chunk pins match the staged inventory)", ok,
          [(r["document_id"][:13], r["validation_state"], r["doc_version"]) for r in rows])
    # checksums vs the live-read rows (pins re-asserted from the staging inventory)
    pins = {
        "c6fbb3ac-4056-5838-8732-b71993d7fe61": "231c05743b0853aa408ae22103faf2645baca81e44fbc839972adc493abbede3",
        "a03447d8-7c1b-5fac-92e7-c2e91ca8db3d": "d4febc1650d2632a220e5ed367d05d99880bcf2b5cf73c434eb2ff7aac3c5040",
        "ea685722-b453-5c5f-8e19-1f4b868bc0b1": "713f1fccc169d6b716b0a2713bc07bbf1aa94a34a25e298fd2e6c3b449dcc9a3",
        "b5742cb1-c413-5a66-a782-24f90facda89": "a42a22c4852946905431acf1190775855ad211e616bb380589e9a057fa4d6960",
        "b0660052-3ecc-598f-b1c1-7e970eba8efb": "5ee0d5b49eac889dbc2dc3f7894a4dc3eff8c0808e3ee94f9425e27c0169f980",
        "e3252e22-9c18-5af2-890d-32275430eecd": "a005acd5e9b80355d7b11492adb598083664f10e076ce557002b2d1911c52b05",
    }
    check("checksums == staging-inventory pins (6/6)",
          all(r["checksum"] == pins[r["document_id"]] for r in rows))

    # ---- 3. audit trail re-derivation ---------------------------------------
    print("3. audit trail re-derivation", flush=True)
    arows = sql("""select occurred_at, actor_label, action, target_type, target_id::text,
                          from_state, to_state, detail
                   from content_review_audit
                   where action = 'VALIDATE' and target_type = 'document'
                     and detail like %s order by id""", (f"%{BATCH}%",))
    check("exactly 6 VALIDATE/document rows carry this batch id", len(arows) == 6, len(arows))
    ok = all(r["from_state"] == "SUGGESTED" and r["to_state"] == "VALIDATED" for r in arows)
    details = [json.loads(r["detail"]) for r in arows]
    ok = ok and {d["document_id"] for d in details} == set(wave_ids)
    ok = ok and all(d.get("decision_text") == "(a) doc-side VALIDATION" for d in details)
    ok = ok and all(d.get("operator_trace_id") == OPERATOR_TRACE_ID for d in details)
    ok = ok and all("Nawaf Al Hussain Khondokar" in (r["actor_label"] or "") for r in arows)
    ok = ok and all(d.get("operator") == "Nawaf Al Hussain Khondokar" for d in details)
    ok = ok and all(d.get("act") == "doc_side_validate" for d in details)
    check("audit rows re-derive: SUGGESTED->VALIDATED x6, one per wave doc, "
          "decision_text + operator trace verbatim, operator named as deciding actor", ok)
    audit_total = sql("select count(*)::int n from content_review_audit")[0]["n"]
    check("audit total 2829 -> 2835 (+6 exactly)", audit_total == 2835, audit_total)

    # ---- 4. non-interference -------------------------------------------------
    print("4. non-interference", flush=True)
    ep = sql("select validation_state, count(*)::int n from exam_papers group by 1")
    ep_states = {r["validation_state"]: r["n"] for r in ep}
    ep_total = sum(ep_states.values())
    check("exam_papers untouched: 108 = 95V/13R", ep_total == 108 and ep_states == {"VALIDATED": 95, "REJECTED": 13},
          f"{ep_total} {ep_states}")
    links = sql("""select question_paper_document_id q, mark_scheme_document_id m
                   from exam_papers
                   where question_paper_document_id = any(%s)
                      or mark_scheme_document_id = any(%s)""", (wave_ids, wave_ids))
    linked = {v for r in links for v in (r["q"], r["m"]) if v}
    check("paper-branch links intact: all 6 wave docs still linked from ep rows "
          "(4 wave rows: the 1C-2025 links pre-existing docs)", linked == set(wave_ids),
          f"{len(linked)}/6 linked")
    chunks = sql("""select coalesce(embed_rev::text,'null') rev, count(*)::int n,
                           count(embedding)::int embedded from document_chunks group by 1""")
    cmap = {r["rev"]: (r["n"], r["embedded"]) for r in chunks}
    check("document_chunks untouched: rev2 4740/4740 embedded",
          cmap.get("2") == (4740, 4740), cmap)
    tve = sql("select count(*)::int n from teacher_validation_events")[0]["n"]
    check("teacher_validation_events delta 0", tve == 0, tve)

    # ---- 5. serving-gate replica + subject branch ----------------------------
    print("5. serving-gate replica + subject branch", flush=True)
    gate = sql("""select count(*)::int n from document_chunks c
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
                            and d.validation_state = 'VALIDATED'))""",
               ("356840e6-81e2-49df-8182-93ab6504d591",) * 2)[0]["n"]
    check("serving gate == 4,661 (delta 0 exactly as predicted — paper branch already covered the 68)",
          gate == 4661, gate)
    sb = sql("""select d.document_id, count(c.id)::int n from document_chunks c
                join documents d on d.id = c.document_row_id
                where c.embedding is not null and c.embed_rev = 2
                  and d.document_id = any(%s)
                  and exists (
                        select 1 from subjects s2
                        where s2.curriculum_version_id = '356840e6-81e2-49df-8182-93ab6504d591'
                          and s2.id = c.subject_id
                          and d.validation_state = 'VALIDATED')
                group by d.document_id""", (wave_ids,))
    sb_map = {r["document_id"]: r["n"] for r in sb}
    expect_map = {doc: WAVE_DOCS[doc][3] for doc in wave_ids}
    check("subject-branch unlock re-derived live: 68/68 wave chunks serve subject-side "
          "(per-doc 11/18/9/10/9/11)", sb_map == expect_map, sb_map)

    # ---- 6. app-side probe (production core, read-only GETs) -----------------
    print("6. app-side probe", flush=True)
    jwt_secret = (SECRETS / "jwt_secret.txt").read_text().strip()
    tv = sql("select token_version::int as v from users where id = %s", (ADMIN_UID,))[0]["v"]
    token = mint_jwt(jwt_secret, tv)
    # route note (honest): GET /documents/{id} is NOT an exposed route (404,
    # probed) and the list DTO carries no validationState field — the teacher
    # API exposes no document-state read. The authoritative state read is the
    # DB live-read above; the serving-semantics proof is the subject-branch
    # count (the deployed core's own searchServingEligible leg 2). The list
    # endpoint still proves the 6 docs exist on the serving surface with the
    # pinned identity (checksum + chunkCount).
    app_ok = True
    app_seen = {}
    for kind, want in (("QUESTION_PAPER",
                        {"c6fbb3ac-4056-5838-8732-b71993d7fe61",
                         "ea685722-b453-5c5f-8e19-1f4b868bc0b1",
                         "b0660052-3ecc-598f-b1c1-7e970eba8efb"}),
                       ("MARK_SCHEME",
                        {"a03447d8-7c1b-5fac-92e7-c2e91ca8db3d",
                         "b5742cb1-c413-5a66-a782-24f90facda89",
                         "e3252e22-9c18-5af2-890d-32275430eecd"})):
        url = f"{BASE}/api/v1/teacher/content/documents?kind={kind}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            body = json.load(urllib.request.urlopen(req, timeout=180))
            items = body if isinstance(body, list) else body.get("content") or []
            for d in items:
                if d.get("documentId") in want:
                    app_seen[d["documentId"]] = (d.get("checksum"), d.get("chunkCount"))
        except Exception as e:  # noqa: BLE001
            app_ok = False
            app_seen[kind] = f"ERROR {type(e).__name__}"
    ok = app_ok and len(app_seen) == 6 and all(
        app_seen.get(doc) == (pins[doc], WAVE_DOCS[doc][3]) for doc in wave_ids)
    check("app-side list GET: 6/6 wave docs present on the serving surface "
          "(checksum + chunkCount == pins; state itself not exposed by the DTO "
          "— DB live-read + subject-branch are the state proof)", ok,
          {k[:13]: v for k, v in app_seen.items()})
    q = urllib.parse.quote("ammonium carbonate")
    url = f"{BASE}/api/v1/teacher/content/documents/search?query={q}&kind=QUESTION_PAPER&limit=10"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    hits = json.load(urllib.request.urlopen(req, timeout=180))
    hit_docs = list({h.get("documentId") for h in hits})
    check("search surface regression probe: 'ammonium carbonate' QP still returns the new 1C-2026 QP",
          bool(hits) and "c6fbb3ac-4056-5838-8732-b71993d7fe61" in hit_docs, hit_docs)

    bundle = {"postverify_utc": stamp, "mode": "READ_ONLY_INDEPENDENT",
              "batch": BATCH, "batch_report": "tc75_doc_validate_report.json",
              "results": _results, "gate": gate, "subject_branch": sb_map}
    (OUT_DIR / "tc75_doc_validate_postverify_result.json").write_text(
        json.dumps(bundle, indent=2, default=str))
    all_pass = all(r["pass"] for r in _results)
    print(f"\nPOST-VERIFY: {'ALL PASS' if all_pass else 'FAILURES PRESENT'} "
          f"({sum(r['pass'] for r in _results)}/{len(_results)})", flush=True)
    conn.close()
    return 0 if all_pass else 4


if __name__ == "__main__":
    import sys
    sys.exit(main())
