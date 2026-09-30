#!/usr/bin/env python3
"""SMART_LESSON browser-session companion: API-side snapshot/verification with
the *browser session's own learner token* (same learner the UI acts on).

Checks the §4.1 items that the UI cannot express directly:
  - unknown-topic fail-closed 404 (UI picker only lists real topics)
  - foreign-subject topic fail-closed 404 (real second-subject topic id)
  - no learner-state/mastery mutation from asking (skillStates stays empty;
    only the sanctioned tutorEngagements signal appears)
  - backend fingerprint: SMART_LESSON lineage markers live

Usage: python3 sl_browser_session_snapshot.py <jwt> <phase>
  phase = pre | post
"""
import json
import sys
import urllib.request

BASE = "https://syllabai-core.onrender.com"
TOPIC_S1A = "2fa5ee0e-1bd1-44a7-b993-83b08241d882"   # 4CH1-S1-a (corpus)
FOREIGN = "20000000-0000-0000-0000-000000000011"     # other subject's topic
ROOT_4CH1 = "297a8706-b957-40cb-8bb6-0bfed66980b7"


def call(method, path, token=None, body=None, timeout=120):
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
            return e.code, {"raw": raw[:200]}


def state_snapshot(token):
    code, st = call("GET", "/api/v1/learners/me/state", token)
    eng = st.get("tutorEngagements") or []
    skills = st.get("skillStates") or st.get("skills") or []
    signals = {}
    for e in eng:
        for k, v in (e.get("signalCounts") or {}).items():
            signals[k] = signals.get(k, 0) + int(v)
    return {
        "status": code,
        "skill_row_count": len(skills),
        "engagement_count": len(eng),
        "signal_counts_total": signals,
    }


def main():
    token = sys.argv[1]
    phase = sys.argv[2]
    out = {"phase": phase, "state": state_snapshot(token)}

    if phase == "pre":
        # backend fingerprint: pre-auth CLA ask must be 401 (route exists),
        # smart-lesson GET pre-auth must be 401
        c1, _ = call("POST", "/api/v1/learners/me/cla/ask",
                     body={"kind": "SMART_LESSON"})
        c2, _ = call("GET", "/api/v1/learners/me/smart-lesson"
                     f"?rootId={ROOT_4CH1}&topicNodeId={TOPIC_S1A}")
        out["fingerprint"] = {"cla_ask_unauth": c1, "smart_lesson_unauth": c2}
        # browser-context probes on the deployed lineage:
        c3, b3 = call("POST", "/api/v1/learners/me/cla/ask", token, {
            "kind": "KG_TOPIC", "mode": "EXPLAIN",
            "rootId": ROOT_4CH1, "topicNodeId": TOPIC_S1A,
            "question": "What are the three states of matter?"})
        out["kg_topic_explain"] = {
            "status": c3,
            "kind": (b3.get("context") or {}).get("kind") if c3 == 200 else None,
            "evidence": len([b3.get("evidenceCount")]) if c3 == 200 else None,
            "citations": len(b3.get("citations") or []) if c3 == 200 else None,
        }
        # unknown topic -> 404 fail-closed
        c4, _ = call("POST", "/api/v1/learners/me/cla/ask", token, {
            "kind": "SMART_LESSON", "mode": "EXPLAIN",
            "rootId": ROOT_4CH1,
            "topicNodeId": "00000000-0000-0000-0000-000000000000",
            "question": "x"})
        out["unknown_topic"] = {"status": c4, "expect": 404}
        # foreign-subject topic -> 404 fail-closed
        c5, _ = call("POST", "/api/v1/learners/me/cla/ask", token, {
            "kind": "SMART_LESSON", "mode": "EXPLAIN",
            "rootId": ROOT_4CH1, "topicNodeId": FOREIGN,
            "question": "x"})
        out["foreign_topic"] = {"status": c5, "expect": 404}
    else:
        c1, b1 = call("POST", "/api/v1/learners/me/cla/ask", token, {
            "kind": "SMART_LESSON", "mode": "EXPLAIN",
            "rootId": ROOT_4CH1, "topicNodeId": TOPIC_S1A,
            "question": "Explain particle arrangement in solids vs gases."})
        ctx = b1.get("context") or {}
        la = ctx.get("lessonAction") or {}
        out["smart_lesson_explain"] = {
            "status": c1, "kind": ctx.get("kind"),
            "validation": ctx.get("validationStatus"),
            "actionType": la.get("actionType"),
            "targetCode": la.get("targetCode"),
            "evidence": b1.get("evidenceCount"),
            "citations": len(b1.get("citations") or []),
        }
    out["state_after"] = state_snapshot(token)
    print(json.dumps(out, indent=1))
    with open(f"/tmp/sl_browser_{phase}.json", "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
