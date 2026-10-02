#!/usr/bin/env python3
"""refusal_watch.py — T-C52: the tutor retrieval refusal-rate watch instrument
(read-only), persisting the T-C42/T-C43/T-C48 watch item at the MIN_COSINE 0.50
floor.

Instrument lineage — the same store the baseline came from:
TUTOR_CURRENT_STATE_AUDIT_2026-09-28.md §10 counted 287 live KA_RAG_COMPLETED
research-telemetry rows (77 refusals = 27%; v5-day 27/87 = 31%). This script
reads the same append-only record (telemetry_events, event_type
KA_RAG_COMPLETED, written by TelemetryService.onTutorAnswered) — NOT the small
per-learner session-turn store (17 assistant turns to date; secondary
corroboration only). D2 (audit tranche-1 rider) serializes the refusal
provider into the payload since 2026-09-27 20:07Z, making the class split
measurable: 'deterministic-refusal' (the grounding gate — the ONLY class the
MIN_COSINE floor can move) vs 'deterministic-paper-refusal' (the fail-open
guard on parsed-but-unbound paper identity — floor-INDEPENDENT).

Deploy boundary: the flip (core 5ef132b, 2026-10-01T20:23Z) went live with the
first successful post-flip deploy — flyway V56/V57/V58 installed 2026-10-02
07:14:19–23Z (overnight deploys were crash-gated on the original V56 per
cd5288f 'V56 unblock'). Pre-flip window < 2026-10-02T07:14:19Z (no-op 0.15
floor); post-flip >= that instant.

Privacy: aggregates ONLY. The payload's question text is NEVER selected.

Run (operator or agent; read-only SELECTs against production):
  NEON_API_KEY=<neon api key> python3 bench/refusal_watch.py
Output: stdout report + WATCH_OUT (default evidence/bench-001/
refusal-watch-latest/refusal-watch.json). The Neon API key is DB-credential-
equivalent (console reveal_password quirk) — hold in env only, rotate first.
"""
import json
import os
import urllib.request

API = "https://console.neon.tech/api/v2"
PROJECT = "billowing-cherry-15418366"
BRANCH = "br-muddy-bar-a5huwldd"
DB = "neondb"
ROLE = "neondb_owner"
EP_HOST = "ep-ancient-cake-a52e4kfd.us-east-2.aws.neon.tech"
FLIP_AT = os.environ.get("WATCH_FLIP_AT", "2026-10-02T07:14:19Z")
OUT = os.environ.get("WATCH_OUT",
                     "evidence/bench-001/refusal-watch-latest/refusal-watch.json")
BASELINE = {"refusals": 77, "asks": 287, "pct": 26.8,
            "source": "TUTOR_CURRENT_STATE_AUDIT_2026-09-28.md §10"}


def api(path, secret=False):
    req = urllib.request.Request(
        API + path, headers={"Authorization": "Bearer " + os.environ["NEON_API_KEY"],
                             "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = r.read().decode()
    return out if secret else json.loads(out)


def sql(conn, query):
    body = json.dumps({"query": query, "params": []}).encode()
    req = urllib.request.Request(
        f"https://{EP_HOST}/sql", method="POST",
        headers={"Neon-Connection-String": conn,
                 "Content-Type": "application/json", "Accept": "application/json"},
        data=body)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read()).get("rows") or []


def pct(asks, ref):
    return round(100.0 * ref / asks, 1) if asks else None


def main():
    pw = api(f"/projects/{PROJECT}/branches/{BRANCH}/roles/{ROLE}/reveal_password",
             secret=True)
    pw = json.loads(pw)
    pw = pw["password"] if isinstance(pw, dict) else pw
    conn = f"postgresql://{ROLE}:{pw}@{EP_HOST}/{DB}?sslmode=require"

    db = sql(conn, "select current_database() as x")
    assert db and db[0].get("x") == DB, "not the campaign DB — abort"
    print("preflight:", db, flush=True)
    out = {}

    total = sql(conn, "select count(*) as n from telemetry_events "
                      "where event_type = 'KA_RAG_COMPLETED'")
    print(f"\nKA_RAG_COMPLETED rows to date: {total[0]['n']} "
          f"(audit baseline: 287 on 09-27)")
    out["total_ka_rag_rows"] = int(total[0]["n"])

    win = sql(conn, f"""
        select case when occurred_at >= '{FLIP_AT}'
                    then 'POST_FLIP_050' else 'PRE_FLIP_015' end as w,
               count(*) as asks,
               count(*) filter (where (payload->>'refused')::boolean) as refusals,
               count(*) filter (where (payload->>'evidenceCount')::int = 0)
                   as zero_evidence,
               count(*) filter (where (payload->>'refused')::boolean
                   and payload->>'answerProvider' = 'deterministic-refusal')
                   as grounding_gate_refusals,
               count(*) filter (where (payload->>'refused')::boolean
                   and payload->>'answerProvider' = 'deterministic-paper-refusal')
                   as paper_guard_refusals
        from telemetry_events
        where event_type = 'KA_RAG_COMPLETED'
        group by 1 order by 1""")
    print(f"\n=== flip-window split (0.50 live since {FLIP_AT}) ===")
    summary = {}
    for r in win:
        asks, ref = int(r["asks"]), int(r["refusals"])
        summary[r["w"]] = {"asks": asks, "refusals": ref,
                           "pct": pct(asks, ref),
                           "zero_evidence": int(r["zero_evidence"]),
                           "grounding_gate_refusals": int(r["grounding_gate_refusals"]),
                           "paper_guard_refusals": int(r["paper_guard_refusals"])}
        print(f"  {r['w']:<14} asks={asks:>4}  refusals={ref:>3} "
              f"({summary[r['w']]['pct']}%)  grounding-gate={r['grounding_gate_refusals']} "
              f"paper-guard={r['paper_guard_refusals']} "
              f"zero_evidence={r['zero_evidence']}")
    out["windows"] = summary
    print(f"  audit baseline: {BASELINE['refusals']}/{BASELINE['asks']} "
          f"= {BASELINE['pct']}% (0.15 floor, pre-D2 tagging)")

    daily = sql(conn, """
        select to_char(date_trunc('day', occurred_at), 'YYYY-MM-DD') as day,
               count(*) as asks,
               count(*) filter (where (payload->>'refused')::boolean) as refusals,
               count(*) filter (where (payload->>'refused')::boolean
                   and payload->>'answerProvider' = 'deterministic-refusal')
                   as grounding_gate,
               count(*) filter (where (payload->>'refused')::boolean
                   and payload->>'answerProvider' = 'deterministic-paper-refusal')
                   as paper_guard
        from telemetry_events
        where event_type = 'KA_RAG_COMPLETED'
        group by 1 order by 1 desc limit 12""")
    print("\n=== daily census (class-split) ===")
    for r in daily:
        asks, ref = int(r["asks"]), int(r["refusals"])
        print(f"  {r['day']}  asks={asks:>4}  refusals={ref:>3} ({pct(asks, ref)}%)  "
              f"grounding-gate={r['grounding_gate']}  paper-guard={r['paper_guard']}")
    out["daily"] = daily

    hourly = sql(conn, f"""
        select to_char(date_trunc('hour', occurred_at), 'MM-DD HH24:00Z') as hr,
               count(*) as asks,
               count(*) filter (where (payload->>'refused')::boolean) as refusals
        from telemetry_events
        where event_type = 'KA_RAG_COMPLETED' and occurred_at >= '{FLIP_AT}'
        group by 1 order by 1""")
    print(f"\n=== post-flip hourly (0.50 floor live) ===")
    for r in hourly:
        print(f"  {r['hr']}  asks={r['asks']:>3}  refusals={r['refusals']:>3}")
    if not hourly:
        print("  (no asks since the flip went live — post-flip cell empty)")
    out["post_flip_hourly"] = hourly

    prov = sql(conn, """
        select coalesce(nullif(payload->>'answerProvider', ''), '(untagged)') as p,
               count(*) as n
        from telemetry_events
        where event_type = 'KA_RAG_COMPLETED' and (payload->>'refused')::boolean
        group by 1 order by n desc limit 8""")
    print("\n=== refusal provider tags over ALL refusals ===")
    for r in prov:
        print(f"  {r['p']}: {r['n']}")
    out["refusal_providers"] = prov

    d2 = sql(conn, """
        select min(occurred_at) as first_tagged, max(occurred_at) as last_tagged
        from telemetry_events
        where event_type = 'KA_RAG_COMPLETED'
              and payload->>'answerProvider' like 'deterministic%'""")
    print("\nD2 tag lifetime:", d2[0])
    out["d2_tag_lifetime"] = d2[0]

    pv = sql(conn, """
        select coalesce(nullif(payload->>'promptVersion', ''), 'NULL') as pv,
               count(*) as n
        from telemetry_events
        where event_type = 'KA_RAG_COMPLETED'
        group by 1 order by n desc limit 8""")
    out["prompt_versions"] = pv

    turns = sql(conn, """
        select count(*) as asks, count(*) filter (where refused) as refusals
        from tutor_session_turns where role = 'assistant'""")
    print("\ncorroboration (per-learner session store, secondary):", turns[0])
    out["session_turns_corroboration"] = turns[0]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, default=str)
    print("saved:", OUT)


if __name__ == "__main__":
    main()
