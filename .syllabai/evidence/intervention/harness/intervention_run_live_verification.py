#!/usr/bin/env python3
"""InterventionRun (E2) live verification — production, deterministic (no LLM).

Verifies the bounded intervention-run boundary end-to-end against the real
deployment, at the exact lineage this script was written for:

  G1  route auth gate (pre-auth 401, route exists)
  G2  fresh learner register+login
  G3  deterministic NBA: fresh learner under a real subject root gets a
      PRACTISE_QUESTIONS action (UNCOVERED_TOPIC — honest cold start)
  G4  run created FROM the recommendation snapshot (origin/diagnosis refs/
      bounded tools/stable hash/CREATED)
  G5  lifecycle: activate → server-assigned step → evidence by reference
  G6  completion + full reconstruction (steps + evidence refs)
  G7  mutation boundary: zero skill rows before/after; run ops touched no
      learner state (the contract §9 invariant, live)
  G8  terminal immutability: second complete 409; late evidence 409
  G9  resume gate: wrong identity 409 intervention_version_mismatch;
      correct identity resumes; ownership 404 for a stranger
  G10 ownership: another learner's run is an indistinguishable 404

Usage: python3 intervention_run_live_verification.py [core_base_url]
Output: evidence/intervention_run_live_verification_<sha>.log/.json (committed)
"""
import json
import sys
import time
import urllib.error
import urllib.request
import uuid as _u

BASE = sys.argv[1] if len(sys.argv) > 1 else "https://syllabai-core.onrender.com"
LINEAGE = "02643ed"  # core HEAD this verification was authored against
OUT_JSON = "intervention_run_live_verification.json"

results = []
RAW = {"base": BASE, "lineage": LINEAGE, "gates": {}}


def record(name, ok, detail, key=None):
    results.append((name, ok, detail))
    print(("PASS " if ok else "FAIL ") + name + " — " + detail)
    if key:
        RAW["gates"][key] = {"ok": ok, "detail": detail}


def call(method, path, token=None, body=None, timeout=90):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=timeout) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw[:300]}


def wait_ready(minutes=12):
    print("waiting for the backend (cold starts take ~2 min)…")
    deadline = time.time() + minutes * 60
    while time.time() < deadline:
        code, body = call("GET", "/actuator/health")
        if code == 200 and (body.get("status") == "UP" or body.get("groups")):
            print("backend UP")
            return True
        time.sleep(20)
    return False


def main():
    if not wait_ready():
        print("backend never became ready — INFRASTRUCTURE, not a product failure")
        sys.exit(2)

    # G1 route auth gate
    c1, _ = call("GET", f"/api/v1/learners/me/intervention-runs/{_u.uuid4()}")
    c1b, _ = call("POST", "/api/v1/learners/me/intervention-runs?rootId=" + str(_u.uuid4()))
    record("G1 intervention-run route auth gate (pre-auth 401)",
           c1 == 401 and c1b == 401, f"get={c1} create={c1b}", key="G1")

    # G2 fresh learner
    email = f"run-live-{_u.uuid4().hex[:8]}@syllabai.test"
    call("POST", "/api/v1/auth/register",
         body={"email": email, "password": "LiveLearner123!", "displayName": "Run Live"})
    _, login, _ = None, None, None
    code, login = call("POST", "/api/v1/auth/login",
                       body={"email": email, "password": "LiveLearner123!"})
    token = login.get("accessToken")
    record("G2 fresh learner register+login", code == 200 and bool(token),
           f"status={code} learner={email}", key="G2")

    # G3 deterministic NBA cold start under a real subject root
    _, subjects = call("GET", "/api/v1/curriculum/subjects", token)
    subject = next(s for s in subjects if s.get("code") == "4CH1")
    root = subject["knowledgeNodeId"]
    code, nba = call("GET", f"/api/v1/learners/me/recommendations?rootId={root}", token)
    actions = nba.get("actions") or []
    practice = next((a for a in actions if a.get("actionType") == "PRACTISE_QUESTIONS"), None)
    record("G3 deterministic NBA PRACTISE_QUESTIONS (cold start)",
           code == 200 and practice is not None
           and practice.get("reasonCode") == "UNCOVERED_TOPIC",
           f"status={code} top={actions[0].get('actionType') if actions else None} "
           f"reason={practice.get('reasonCode') if practice else None}", key="G3")

    # G4 create run FROM the recommendation
    code, run = call("POST", f"/api/v1/learners/me/intervention-runs?rootId={root}", token)
    ok = (code == 201 and run.get("origin") == "NBA"
          and run.get("status") == "CREATED"
          and run.get("actionType") == "PRACTISE_QUESTIONS"
          and run.get("diagnosisVersion") == nba.get("policy")
          and str(run.get("targetSpecificationPoints")).__contains__(practice["targetNodeId"])
          and str(run.get("diagnosisSnapshotRef")).startswith("nba:")
          and run.get("learnerStateSnapshotRef", "").endswith(":unmeasured")
          and "start_practice" in (run.get("allowedToolIds") or [])
          and len(run.get("interventionHash") or "") == 64
          and run.get("interventionVersion") == "practice-intervention/v1")
    record("G4 run created from the recommendation snapshot", ok,
           f"status={code} origin={run.get('origin')} diagRef={str(run.get('diagnosisSnapshotRef'))[:60]}",
           key="G4")
    RAW["run"] = run
    run_id = run.get("runId")

    # G5 lifecycle: activate, step (server-assigned sequence), evidence by ref
    code_a, run_a = call("POST", f"/api/v1/learners/me/intervention-runs/{run_id}/activate", token)
    code_s, run_s = call("POST", f"/api/v1/learners/me/intervention-runs/{run_id}/steps", token,
                         {"status": "DONE", "observationType": "PRACTICE_SUBMITTED",
                          "outputEvidenceRef": f"nba:{nba.get('policy')}:{practice['targetNodeId']}"})
    code_e, run_e = call("POST", f"/api/v1/learners/me/intervention-runs/{run_id}/evidence", token,
                         {"evidenceRef": f"recommendation:{run.get('diagnosisSnapshotRef')}",
                          "role": "RECOMMENDATION_EVIDENCE"})
    step_ok = bool(run_s.get("steps")) and run_s["steps"][0].get("sequenceNo") == 0
    ev_ok = bool(run_e.get("evidence")) and run_e["evidence"][0].get("role") == "RECOMMENDATION_EVIDENCE"
    record("G5 lifecycle activate→step→evidence-by-reference",
           code_a == 200 and code_s == 200 and code_e == 200 and step_ok and ev_ok,
           f"activate={code_a} step={code_s} (seq={run_s['steps'][0]['sequenceNo'] if run_s.get('steps') else None}) "
           f"evidence={code_e}", key="G5")

    # pre-complete learner state (mutation-boundary baseline)
    _, state_pre = call("GET", "/api/v1/learners/me/state", token)

    # G6 completion + reconstruction
    code_c, run_c = call("POST", f"/api/v1/learners/me/intervention-runs/{run_id}/complete", token,
                         {"terminalOutcome": "EVIDENCE_COLLECTED"})
    code_g, got = call("GET", f"/api/v1/learners/me/intervention-runs/{run_id}", token)
    ok = (code_c == 200 and code_g == 200 and got.get("status") == "COMPLETED"
          and got.get("terminalOutcome") == "EVIDENCE_COLLECTED"
          and len(got.get("steps") or []) == 1 and len(got.get("evidence") or []) == 1)
    record("G6 completion + full reconstruction", ok,
           f"complete={code_c} get={code_g} status={got.get('status')} "
           f"steps={len(got.get('steps') or [])} evidence={len(got.get('evidence') or [])}", key="G6")

    # G7 mutation boundary: no skill rows, run ops changed no learner state
    _, state_post = call("GET", "/api/v1/learners/me/state", token)
    skills_pre = state_pre.get("skillStates") or state_pre.get("skills") or []
    skills_post = state_post.get("skillStates") or state_post.get("skills") or []
    eng_pre = json.dumps(state_pre.get("tutorEngagements") or [], sort_keys=True)
    eng_post = json.dumps(state_post.get("tutorEngagements") or [], sort_keys=True)
    record("G7 mutation boundary (zero skill rows; engagement rows untouched by run ops)",
           len(skills_pre) == 0 and len(skills_post) == 0 and eng_pre == eng_post,
           f"skills pre/post={len(skills_pre)}/{len(skills_post)} engagements unchanged={eng_pre == eng_post}",
           key="G7")

    # G8 terminal immutability
    c8, b8 = call("POST", f"/api/v1/learners/me/intervention-runs/{run_id}/complete", token,
                  {"terminalOutcome": "EVIDENCE_COLLECTED"})
    c8b, b8b = call("POST", f"/api/v1/learners/me/intervention-runs/{run_id}/evidence", token,
                    {"evidenceRef": "late:ref", "role": "ATTEMPT_EVIDENCE"})
    record("G8 terminal immutability (second complete 409; late evidence 409)",
           c8 == 409 and c8b == 409, f"complete={c8} evidence={c8b}", key="G8")

    # G9 resume gate on a second run
    code2, run2 = call("POST", f"/api/v1/learners/me/intervention-runs?rootId={root}", token)
    rid2 = run2.get("runId")
    call("POST", f"/api/v1/learners/me/intervention-runs/{rid2}/activate", token)
    call("POST", f"/api/v1/learners/me/intervention-runs/{rid2}/pause", token)
    cw, bw = call("POST", f"/api/v1/learners/me/intervention-runs/{rid2}/resume", token,
                  {"interventionVersion": run2.get("interventionVersion"),
                   "interventionHash": "0" * 64})
    cr, br = call("POST", f"/api/v1/learners/me/intervention-runs/{rid2}/resume", token,
                  {"interventionVersion": run2.get("interventionVersion"),
                   "interventionHash": run2.get("interventionHash")})
    record("G9 resume gate (wrong identity 409 intervention_version_mismatch; correct resumes)",
           cw == 409 and (bw.get("error") == "intervention_version_mismatch") and cr == 200
           and br.get("status") == "ACTIVE",
           f"wrong={cw} ({bw.get('error')}) right={cr} status={br.get('status')}", key="G9")

    # G10 ownership: stranger gets an indistinguishable 404
    email2 = f"run-live-{_u.uuid4().hex[:8]}@syllabai.test"
    call("POST", "/api/v1/auth/register",
         body={"email": email2, "password": "LiveLearner123!", "displayName": "Run Live 2"})
    _, login2 = call("POST", "/api/v1/auth/login",
                     body={"email": email2, "password": "LiveLearner123!"})
    token2 = login2.get("accessToken")
    c10, _ = call("GET", f"/api/v1/learners/me/intervention-runs/{run_id}", token2)
    c10b, _ = call("POST", f"/api/v1/learners/me/intervention-runs/{run_id}/complete", token2,
                   {"terminalOutcome": "X"})
    record("G10 ownership fail-closed (stranger 404 on get and complete)",
           c10 == 404 and c10b == 404, f"get={c10} complete={c10b}", key="G10")

    RAW["meta"] = {"learner": email, "run_id": run_id}
    with open(OUT_JSON, "w") as f:
        json.dump(RAW, f, indent=1)

    failed = [r for r in results if not r[1]]
    print(f"\nINTERVENTION RUN LIVE VERIFICATION: {len(results) - len(failed)}/{len(results)} PASS")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
