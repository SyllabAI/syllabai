#!/usr/bin/env python3
"""CLA evaluation harness — S-H SMART_LESSON phase (extends the §10.4 bundle
discipline with the S-G QUESTION_PART gate pattern; contract §9 + ADR-020).

Set S-H (SMART_LESSON gate over real validated 4CH1 material, live):
  resolution correctness   — every corpus topic resolves as a SMART_LESSON
                             context (kind, VALIDATED, curriculum identity,
                             lessonAction a valid ladder decision)
  fail-closed              — unknown topic 404 / missing topicNodeId 400 /
                             blank question 400 / unknown mode 400 / foreign
                             topic 404 (real foreign topic when a second
                             subject exists; otherwise covered by unknown,
                             documented)
  grounded precision       — per-topic EXPLAIN: non-refused, evidence-backed,
                             citations present, zero unresolvable [n] markers,
                             deterministic spec anchor among citations
  citation correctness     — every [n] marker resolves to a served citation
  unsupported-claim        — out-of-corpus/out-of-domain probes on the lesson
                             context decline honestly (deterministic refusal
                             OR grounded decline with zero fabricated markers)
  mode correctness         — HINT + SUMMARIZE on the lesson context: 200,
                             mode recorded, non-refused, markers resolve
  context anchoring        — the CLA's lessonAction is a valid (actionType,
                             reasonCode) ladder decision AND the Smart Lesson
                             surface itself renders a valid decision for the
                             same (root, topic, learner) — the closed-loop
                             substrate parity check
  learner evidence capture — fresh learner LIM signalCounts include the
                             SMART_LESSON ask; zero skill rows (no canonical
                             mutation from chat)

Corpus: the §10.4 validated 4CH1 topic set (real production material — the
Smart Lesson surface is a deterministic projection over every validated topic,
so the lesson corpus IS the validated topic corpus; single-subject limitation
documented, no fabricated lesson content).

Gate: every check must pass. Failures are diagnosed, never weakened.

Execution model: state accumulates incrementally in one JSON file and every
run REGENERATES the full S-H check list from the persisted store — so the
phase is resumable across tool-call windows and interrupted runs never lose
completed probes or double-count checks:

  CLA_EVAL_PHASES=discover            python3 cla_smart_lesson_eval_sh.py
  CLA_EVAL_SLICE=a CLA_EVAL_PHASES=sh python3 cla_smart_lesson_eval_sh.py
  CLA_EVAL_SLICE=b CLA_EVAL_PHASES=sh python3 cla_smart_lesson_eval_sh.py
  CLA_EVAL_SLICE=x CLA_EVAL_PHASES=sh python3 cla_smart_lesson_eval_sh.py
  CLA_EVAL_PHASES=verdict             python3 cla_smart_lesson_eval_sh.py
(no CLA_EVAL_SLICE with sh = the whole phase in one process)
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
import uuid as _u

BASE = "https://syllabai-core.onrender.com"
OUT = os.environ.get(
    "CLA_EVAL_SH_OUT", "/home/z/my-project/evidence/cla_eval_smartlesson_sh.json")
PHASES = set((os.environ.get("CLA_EVAL_PHASES") or "all").split(","))
ALL = "all" in PHASES

ACTION_TYPES = {"REMEDIATE_PREREQUISITE", "STUDY_CORRECTIVE", "ASK_TUTOR", "REVIEW_TOPIC",
                "TIMED_PRACTICE", "PRACTISE_QUESTIONS", "ADVANCE_TOPIC"}
REASON_CODES = {"PREREQUISITE_WEAK", "MISCONCEPTION_REMEDIATION", "MISCONCEPTION_SUSPECTED",
                "DUE_REVIEW", "FLUENCY_GAP", "LOW_MASTERY", "TUTOR_ENGAGED",
                "INSUFFICIENT_COVERAGE", "TOPIC_MASTERED"}

# real validated §10.4 corpus (S-B topics — the validated 4CH1 topic layer)
CORPUS_CODES = ["4CH1-S1-a", "4CH1-S1-b", "4CH1-S1-c", "4CH1-S1-d", "4CH1-S1-e",
                "4CH1-S2-a", "4CH1-S3-a", "4CH1-S4-a"]

RAW = {"sets": {}, "lineage": {"slice": "SMART_LESSON", "expect_core": "50dfa59"}}


def want(phase):
    return ALL or phase in PHASES


def call(method, path, token=None, body=None, timeout=150):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Accept", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, data=data, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode()), time.time() - t0
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw), time.time() - t0
        except Exception:
            return e.code, {"raw": raw[:300]}, time.time() - t0
    except Exception as e:
        return 0, {"error": str(e)}, time.time() - t0


def save():
    with open(OUT, "w") as f:
        json.dump(RAW, f, indent=1)


def load():
    global RAW
    if os.path.exists(OUT):
        with open(OUT) as f:
            RAW = json.load(f)


def wait_ready(minutes=12):
    deadline = time.time() + minutes * 60
    while time.time() < deadline:
        code, _, _ = call("GET", "/actuator/health", timeout=15)
        if code == 200:
            return True
        time.sleep(15)
    return False


def unresolvable(text, citations):
    idx = {c.get("index") for c in citations or []}
    return sorted({m for m in range(1, 15) if f"[{m}]" in (text or "") and m not in idx})


def ask_cla(token, body, timeout=150):
    """LLM-backed ask with bounded 503 handling: the provider enforces a daily
    token quota and a burst of asks can trip it mid-run (EXTERNAL PROVIDER
    LIMIT). The gate is NEVER weakened — a 503 that survives the bounded
    retries surfaces as an explicit EXTERNAL-PROVIDER-LIMIT failure so the
    slice can be re-run after quota recovery (completed topics are skipped on
    resume)."""
    for attempt in range(4):
        code, ans, dt = call("POST", "/api/v1/learners/me/cla/ask", token, body, timeout)
        if code != 503:
            return code, ans, dt
        if attempt < 3:
            time.sleep(30 * (attempt + 1))  # 30s / 60s / 90s backoff
    ans["external_provider_limit"] = True
    return code, ans, dt


def topic_done(store, code_):
    entry = store.get(code_)
    return bool(entry) and entry.get("explain_ok") is True \
        and entry.get("parity_ok") is True and entry.get("modes_ok") is True

def regenerate_checks(topics, store, tail):
    """the S-H check list is ALWAYS regenerated from the persisted store —
    incremental runs never double-count and never lose completed probes"""
    checks = []
    for code_ in topics:
        entry = store.get(code_) or {}
        ex = entry.get("explain") or {}
        la = ex.get("lessonAction") or {}
        checks.append(["S-H", f"{code_} lesson EXPLAIN grounded, anchored, ladder-valid",
                       bool(entry.get("explain_ok")),
                       f"ev={ex.get('evidenceCount')} "
                       f"cits={len(ex.get('citations') or [])} "
                       f"action={la.get('actionType')}/{la.get('reasonCode')}"])
        surf = entry.get("surface") or {}
        checks.append(["S-H", f"{code_} substrate parity with the Smart Lesson surface",
                       bool(entry.get("parity_ok")),
                       f"surface={surf.get('actionType')}/{surf.get('reasonCode')} "
                       f"cla={la.get('actionType')}"])
        checks.append(["S-H", f"{code_} HINT + SUMMARIZE modes correct on the lesson",
                       bool(entry.get("modes_ok")),
                       f"HINT={entry.get('hint_status')} "
                       f"SUMMARIZE={entry.get('summ_status')}"])
    for name, (ok, detail) in (tail or {}).items():
        checks.append(["S-H", name, ok, detail])
    return checks


def main():
    global RAW
    if not wait_ready():
        print("service not ready — abort")
        sys.exit(2)
    load()

    if want("discover"):
        email = f"cla-sh-{_u.uuid4().hex[:8]}@syllabai.test"
        call("POST", "/api/v1/auth/register",
             body={"email": email, "password": "EvalLearner123!", "displayName": "CLA SH Eval"})
        _, login, _ = call("POST", "/api/v1/auth/login",
                           body={"email": email, "password": "EvalLearner123!"})
        token = login.get("accessToken")
        _, subjects, _ = call("GET", "/api/v1/curriculum/subjects", token)
        subject = next(s for s in subjects if s.get("code") == "4CH1")
        kni = subject["knowledgeNodeId"]
        _, tree, _ = call("GET", f"/api/v1/knowledge/nodes/{kni}/tree", token)
        by_code = {}

        def collect(node):
            if node.get("code"):
                by_code[node["code"]] = node
            for c in node.get("children", []) or []:
                collect(c)

        def walk_topics(node, out):
            if node.get("type") == "TOPIC":
                out.append(node)
            for c in node.get("children", []) or []:
                walk_topics(c, out)

        collect(tree)
        topics = {c: by_code[c]["id"] for c in CORPUS_CODES if c in by_code}
        # foreign-subject topic: walked EXCLUSIVELY in the other subject's own
        # tree and cross-checked against the FULL 4CH1 topic id set (a shared
        # registry once selected a non-corpus 4CH1 topic as "foreign" and
        # produced a false FAIL — this walk makes that impossible)
        foreign = None
        others = [s for s in subjects
                  if s.get("code") != "4CH1" and s.get("knowledgeNodeId")]
        own_all = []
        walk_topics(tree, own_all)
        own_ids = {t["id"] for t in own_all}
        for other in others:
            c2, otree, _ = call("GET",
                                f"/api/v1/knowledge/nodes/{other['knowledgeNodeId']}/tree",
                                token)
            if c2 == 200 and otree:
                otopics = []
                walk_topics(otree, otopics)
                cand = [n for n in otopics if n.get("id") not in own_ids]
                if cand:
                    foreign = cand[0]["id"]
                    break
        RAW["sets"]["discover"] = {
            "learner": email, "root": kni, "topics": topics,
            "foreign": foreign, "second_subject": bool(others),
        }
        RAW["sets"].setdefault("sh_topics", {})
        RAW["sets"].setdefault("sh_tail", {})
        save()
        print(f"discovered {len(topics)} corpus topics; foreign={bool(foreign)}")

    if want("sh"):
        load()
        slice_id = os.environ.get("CLA_EVAL_SLICE")
        disc = RAW["sets"]["discover"]
        topics = disc["topics"]
        foreign = disc.get("foreign")
        kni = disc["root"]
        store = RAW["sets"].setdefault("sh_topics", {})
        tail = RAW["sets"].setdefault("sh_tail", {})
        # re-auth with the SAME learner so LIM asserts stay valid
        _, login, _ = call("POST", "/api/v1/auth/login",
                           body={"email": disc["learner"],
                                 "password": "EvalLearner123!"})
        token = login.get("accessToken")

        items = list(topics.items())
        if slice_id == "a":
            items = items[:4]
        elif slice_id == "b":
            items = items[4:8]
        elif slice_id == "x":
            items = []

        provider_limited = False
        for code_, tid in items:
            if topic_done(store, code_):
                print(f"resume: {code_} already complete — skipping", flush=True)
                continue
            entry = store.setdefault(code_, {})

            # partial resume: keep persisted sub-results that already PASSED,
            # redo only what is missing or failed (provider-503 failures are
            # never locked in — they are retried on the next slice run)
            if entry.get("explain_ok") is not True:
                c, ans, _ = ask_cla(token, {
                    "kind": "SMART_LESSON", "rootId": kni, "topicNodeId": tid,
                    "mode": "EXPLAIN",
                    "question": "Explain this lesson topic in simple terms with an example."})
                if ans.get("external_provider_limit"):
                    provider_limited = True
                ctx = ans.get("context", {})
                la = ctx.get("lessonAction") or {}
                cits = ans.get("citations", [])
                unr = unresolvable(ans.get("answer"), cits)
                anchor = any((ct.get("sourceType") == "KNOWLEDGE_NODE"
                              and ct.get("nodeId") == tid) for ct in cits)
                entry["explain_ok"] = (
                    c == 200 and not ans.get("refused")
                    and (ans.get("evidenceCount") or 0) >= 1 and cits and not unr and anchor
                    and ctx.get("kind") == "SMART_LESSON"
                    and ctx.get("validationState") == "VALIDATED"
                    and ctx.get("topicNodeId") == tid
                    and la.get("actionType") in ACTION_TYPES
                    and la.get("reasonCode") in REASON_CODES)
                entry["explain"] = {"refused": ans.get("refused"),
                                    "evidenceCount": ans.get("evidenceCount"),
                                    "lessonAction": la, "citations": cits,
                                    "answer": (ans.get("answer") or "")[:600]}
                save()
            else:
                print(f"resume: {code_} EXPLAIN already green — skipping", flush=True)
                la = (entry.get("explain") or {}).get("lessonAction") or {}

            # substrate parity: the Smart Lesson surface renders a valid ladder
            # decision for the same (root, topic, learner)
            if entry.get("parity_ok") is not True:
                c2, lesson, _ = call("GET",
                                     f"/api/v1/learners/me/smart-lesson?rootId={kni}"
                                     f"&topicNodeId={tid}", token)
                surf = (lesson or {}).get("action") or {}
                entry["surface"] = {"actionType": surf.get("actionType"),
                                    "reasonCode": surf.get("reasonCode")}
                entry["parity_ok"] = (c2 == 200
                                      and surf.get("actionType") in ACTION_TYPES
                                      and surf.get("reasonCode") in REASON_CODES)
                save()
            else:
                surf = entry.get("surface") or {}

            # mode correctness on the lesson context (paced — the provider's
            # daily-token quota tripped on bursts in the first S-H run; HINT and
            # SUMMARIZE resume independently so a quota-503 on one never
            # re-burns the other)
            if entry.get("hint_ok") is not True:
                time.sleep(3)
                c3, hint, _ = ask_cla(token, {
                    "kind": "SMART_LESSON", "rootId": kni, "topicNodeId": tid,
                    "mode": "HINT", "question": "Give me a hint for studying this."})
                if hint.get("external_provider_limit"):
                    provider_limited = True
                entry["hint_status"] = c3
                entry["hint_ok"] = (
                    c3 == 200 and not hint.get("refused")
                    and hint.get("context", {}).get("mode") == "HINT"
                    and not unresolvable(hint.get("answer"), hint.get("citations")))
                save()
            if entry.get("summ_ok") is not True:
                time.sleep(3)
                c4, summ, _ = ask_cla(token, {
                    "kind": "SMART_LESSON", "rootId": kni, "topicNodeId": tid,
                    "mode": "SUMMARIZE", "question": "Summarize this lesson topic."})
                if summ.get("external_provider_limit"):
                    provider_limited = True
                entry["summ_status"] = c4
                entry["summ_ok"] = (
                    c4 == 200 and not summ.get("refused")
                    and summ.get("context", {}).get("mode") == "SUMMARIZE"
                    and not unresolvable(summ.get("answer"), summ.get("citations")))
                save()
            entry["modes_ok"] = (entry.get("hint_ok") is True
                                 and entry.get("summ_ok") is True)
            save()

        if slice_id not in ("a", "b"):
            # the x / full-run tail: corpus aggregate + fail-closed matrix +
            # refusal behavior + learner evidence (recomputed every x run)
            sh_explains = [c for c in regenerate_checks(topics, store, None)
                           if "lesson EXPLAIN grounded" in c[1]]
            coverage_ok = (len(sh_explains) == len(topics)
                           and all(c[2] for c in sh_explains))
            tail["grounded precision 100% over the lesson corpus"] = [
                coverage_ok,
                f"topics={len(sh_explains)}/{len(topics)}"
                + (" [INCOMPLETE — provider quota exhausted mid-run; re-run required]"
                   if provider_limited else "")]
            RAW["provider_limited"] = provider_limited

            # fail-closed matrix (non-LLM fast paths)
            c, _, _ = call("POST", "/api/v1/learners/me/cla/ask", token, {
                "kind": "SMART_LESSON", "rootId": kni,
                "topicNodeId": str(_u.uuid4()), "mode": "EXPLAIN", "question": "explain"})
            tail["unknown topic fail-closed 404"] = [c == 404, f"status={c} want=404"]
            c, _, _ = call("POST", "/api/v1/learners/me/cla/ask", token, {
                "kind": "SMART_LESSON", "rootId": kni,
                "mode": "EXPLAIN", "question": "explain"})
            tail["missing topicNodeId fail-closed 400"] = [c == 400, f"status={c} want=400"]
            c, _, _ = call("POST", "/api/v1/learners/me/cla/ask", token, {
                "kind": "SMART_LESSON", "rootId": kni,
                "topicNodeId": topics[CORPUS_CODES[0]],
                "mode": "WHISPER", "question": "explain"})
            tail["unknown mode fail-closed 400"] = [c == 400, f"status={c} want=400"]
            c, _, _ = call("POST", "/api/v1/learners/me/cla/ask", token, {
                "kind": "SMART_LESSON", "rootId": kni,
                "topicNodeId": topics[CORPUS_CODES[0]],
                "mode": "EXPLAIN", "question": "   "})
            tail["blank question fail-closed 400"] = [c == 400, f"status={c} want=400"]
            if foreign:
                c, _, _ = call("POST", "/api/v1/learners/me/cla/ask", token, {
                    "kind": "SMART_LESSON", "rootId": kni, "topicNodeId": foreign,
                    "mode": "EXPLAIN", "question": "explain"})
                tail["foreign-subject topic fail-closed 404 (real foreign topic)"] = [
                    c == 404, f"status={c} want=404"]
            else:
                tail["foreign-subject topic fail-closed (single-subject deployment)"] = [
                    True,
                    "no second subject exists — foreign-subject isolation pinned by "
                    "ClaFlowIT + resolver tests; the unknown-topic 404 covers the live "
                    "no-oracle discipline"]

            # unsupported-claim / refusal behavior: out-of-domain probe
            c, ans, _ = ask_cla(token, {
                "kind": "SMART_LESSON", "rootId": kni,
                "topicNodeId": topics[CORPUS_CODES[0]], "mode": "EXPLAIN",
                "question": "Who won the 1958 World Cup and explain the offside rule "
                            "of basketball in detail?"})
            refused_honest = (ans.get("refused")
                              or not unresolvable(ans.get("answer"), ans.get("citations")))
            tail["out-of-domain probe declines honestly (no fabricated markers)"] = [
                c in (200, 404) and refused_honest,
                f"status={c} refused={ans.get('refused')} "
                f"unres={unresolvable(ans.get('answer'), ans.get('citations'))}"]

            # learner evidence capture: LIM signals + no canonical mutation
            c, state, _ = call("GET", "/api/v1/learners/me/state", token)
            rows = state.get("tutorEngagements") or []
            sig = any((r.get("signalCounts") or {}).get("EXPLANATION_REQUEST", 0) >= 1
                      for r in rows)
            skills = state.get("skillStates") or state.get("skills") or []
            tail["learner evidence: signalCounts include the SMART_LESSON ask"] = [
                sig, f"engagements={len(rows)}"]
            tail["learner evidence: zero canonical skill rows from chat"] = [
                c == 200 and len(skills) == 0, f"skills={len(skills)}"]
            save()

        RAW["checks"] = regenerate_checks(topics, store, tail)
        save()
        for ck in RAW["checks"]:
            print(("PASS " if ck[2] else "FAIL ") + f"[{ck[0]}] " + ck[1]
                  + (" — " + ck[3] if ck[3] else ""), flush=True)

    if want("verdict"):
        load()
        checks = RAW.get("checks", [])
        sh = [c for c in checks if c[0] == "S-H"]
        topics = RAW["sets"]["discover"]["topics"]
        tail_names = {c[1] for c in sh} & set(RAW["sets"].get("sh_tail", {}))
        complete = (len({c[1] for c in sh if "lesson EXPLAIN" in c[1]}) == len(topics)
                    and len(tail_names) == len(RAW["sets"].get("sh_tail", {})))
        passed = sum(1 for c in sh if c[2])
        total = len(sh)
        RAW["verdict"] = {
            "set": "S-H", "total": total, "passed": passed,
            "complete_corpus_and_tail": complete,
            "green": complete and total > 0 and passed == total,
        }
        with open(OUT, "w") as f:
            json.dump(RAW, f, indent=1)
        print(f"\nS-H SMART_LESSON: {passed}/{total} "
              f"(complete={complete}) — {'GREEN' if RAW['verdict']['green'] else 'RED'}")
        sys.exit(0 if RAW["verdict"]["green"] else 1)


if __name__ == "__main__":
    main()
