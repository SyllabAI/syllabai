#!/usr/bin/env python3
"""0-hit serving anomaly — discriminating evidence probe (READ-ONLY, 2026-09-25).

Anomaly (worklog trace 1a0d8239e54492b5): GET /teacher/content/documents/search
returns 200 with 0 hits despite 12 VALIDATED papers under the ACTIVE 4CH1 subject
and a fully embedded corpus (700 docs / 6,120 chunks).

Candidate causes:
  (a) scope refusal — CurriculumScopeResolver.resolveActive() returns empty when
      ACTIVE owners != 1 (IAL-CHEM-2018 stub gained surface -> owners=2 -> refuse)
  (b) chunk filters — embed_rev=2 read filter (V33) or T-C20 VALIDATED-only
      predicate hides the VALIDATED papers' chunks

Discriminators used here (all reachable from the sanctioned teacher surface):
  1. GET /teacher/curriculum/versions  -> per-version status + node validation
     counts (the surface the 09-25 session could not reach; it only knew of
     /knowledge endpoints).
  2. GET /teacher/curriculum/versions/{id}/nodes -> IAL VALIDATED structure nodes
     (KG-side ownership test = resolver's hasValidatedStructure).
  3. GET /teacher/content/review-queue -> SUGGESTED paper subjectIds (paper-side
     ownership test = examPapers.existsBySubjectId, ANY validation state).
  4. Search latency vs DB-only baseline: resolveActive-empty short-circuits
     BEFORE the Gemini embedQuery network call (ContentDocumentController line
     106-108), so search ~= baseline  =>  scope refused (a);
     search >> baseline (+0.5-2s)     =>  embedding ran => scope resolved (b).

No writes. Raw credentials never printed.
"""
import json, sys, time, urllib.request, urllib.error

BASE = "https://syllabai-core.onrender.com"
creds = open("/home/z/my-project/.g4_creds").read().strip().splitlines()
email, password = creds[0].strip(), creds[1].strip()


def http(method, path, token=None, payload=None, timeout=120):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        method=method,
        headers={"Content-Type": "application/json",
                 **({"Authorization": f"Bearer {token}"} if token else {})})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode()
            return r.status, (json.loads(body) if body else None), time.time() - t0
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body), time.time() - t0
        except Exception:
            return e.code, body[:300], time.time() - t0
    except (urllib.error.URLError, TimeoutError) as e:
        return 0, {"raw": str(getattr(e, "reason", e))}, time.time() - t0


def login():
    s, body, _ = http("POST", "/api/v1/auth/login",
                      payload={"email": email, "password": password})
    if s != 200:
        print(f"LOGIN FAILED: {s}")
        sys.exit(1)
    tok = (body or {}).get("token") or (body or {}).get("accessToken")
    print(f"login OK (teacher token acquired)")
    return tok


def main():
    tok = login()

    # ── 1. curriculum versions: status + validation counts ──────────────────
    s, versions, _ = http("GET", "/api/v1/teacher/curriculum/versions", token=tok)
    if s != 200:
        print(f"curriculum/versions failed: {s} {versions}")
        sys.exit(1)
    print("\n=== CURRICULUM VERSIONS ===")
    ial, fourch1 = None, None
    for v in versions:
        print(f"  {v['code']:<14} status={v['status']:<8} "
              f"validated={v['validatedNodes']:<4} suggested={v['suggestedNodes']:<4} "
              f"unvalidated={v['unvalidatedNodes']:<4} id={v['id']}")
        code = (v.get("code") or "").upper()
        if "IAL" in code:
            ial = v
        if "4CH1" in code:
            fourch1 = v

    # ── 2. IAL nodes: KG-side ownership test ────────────────────────────────
    if ial:
        s, nodes, _ = http(
            "GET", f"/api/v1/teacher/curriculum/versions/{ial['id']}/nodes", token=tok)
        print(f"\n=== IAL {ial['code']} NODES (status={s}, total={len(nodes or [])}) ===")
        if s == 200:
            from collections import Counter
            c = Counter((n["nodeType"], n["validationStatus"]) for n in nodes)
            for (ntype, vstat), cnt in sorted(c.items()):
                print(f"  {ntype:<10} {vstat:<12} {cnt}")
            val_struct = [n for n in nodes
                          if n["validationStatus"] == "VALIDATED"
                          and n["nodeType"] in ("UNIT", "TOPIC", "SUBTOPIC")]
            print(f"  -> VALIDATED structure nodes (UNIT/TOPIC/SUBTOPIC): "
                  f"{len(val_struct)}")
            for n in val_struct[:10]:
                print(f"     * {n['nodeType']:<8} {n['code']:<20} {n['title'][:50]}")

    # 4CH1 sanity: expect ~226 VALIDATED structure (09-17 DB verification)
    if fourch1:
        s, nodes4, _ = http(
            "GET", f"/api/v1/teacher/curriculum/versions/{fourch1['id']}/nodes",
            token=tok)
        if s == 200:
            val_struct4 = [n for n in nodes4
                           if n["validationStatus"] == "VALIDATED"
                           and n["nodeType"] in ("UNIT", "TOPIC", "SUBTOPIC")]
            print(f"\n=== 4CH1 {fourch1['code']} (status={fourch1['status']}) "
                  f"VALIDATED structure nodes: {len(val_struct4)} ===")

    # ── 3. review queue: paper-side ownership (subjectIds) ──────────────────
    s, rq, _ = http("GET", "/api/v1/teacher/content/review-queue", token=tok)
    if s == 200:
        papers = rq.get("papers", [])
        subjects = {}
        for p in papers:
            subjects.setdefault(str(p.get("subjectId")), []).append(
                (p.get("title") or "")[:44])
        print(f"\n=== REVIEW QUEUE ({len(papers)} SUGGESTED papers by subject) ===")
        for sid, titles in sorted(subjects.items()):
            print(f"  subject {sid}  papers={len(titles)}")
            for t in titles[:3]:
                print(f"     - {t}")
    else:
        print(f"\nreview-queue failed: {s}")

    # ── 4. timing discrimination ────────────────────────────────────────────
    print("\n=== TIMING PROBE (baseline DB-only vs search) ===")
    base_lat = []
    for i in range(3):
        s, _, lat = http("GET", "/api/v1/teacher/content/review-queue", token=tok)
        base_lat.append(lat)
        time.sleep(1)
    print(f"  baseline review-queue x3: "
          f"{', '.join(f'{l*1000:.0f}ms' for l in base_lat)} "
          f"(median {sorted(base_lat)[1]*1000:.0f}ms)")
    queries = ["electrolysis of molten lead bromide",
               "explain catalytic cracking of alkanes",
               "ionic bonding between sodium and chlorine"]
    for q in queries:
        s, body, lat = http(
            "GET",
            "/api/v1/teacher/content/documents/search?limit=5&query="
            + urllib.request.quote(q),
            token=tok)
        hits = len(body) if isinstance(body, list) else f"non-list({body})"
        print(f"  search [{q[:38]:<38}] -> {s} hits={hits} "
              f"latency={lat*1000:.0f}ms")

    print("\nVERDICT HINT: search latency ~= baseline => scope refused (cause a);")
    print("              search latency >> baseline (+>300ms) => embedding ran,")
    print("              chunk-level filters empty (cause b).")


if __name__ == "__main__":
    main()
