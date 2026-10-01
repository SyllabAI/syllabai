#!/usr/bin/env python3
"""gold_check.py — deterministic validator for the frozen gold set (T-C13 M0).
Usage: python3 gold_check.py <snapshot_dir> <gold_dir> [--selftest]"""
import hashlib, json, re, sys

SPEC_RE = re.compile(r"^4CH1-(PR-[0-9]+|[0-9]+\.[0-9]+[A-Z]?)$")  # v2: + the 12 practicals 4CH1-PR-01..12 (VALIDATED SUBTOPICs in the registry since snap-002; t0 regex predated them — backward-compatible, gold-v1 has no PR codes)
ALLOWED_SUBSTRATE = {"chunks", "kg", "chunks+kg", "kg+chunks", "notes_mirror", "figures"}
KNOWN_RULES = {"R1-stem-verbatim", "R2-term-cooccurrence", "R3-paper-cohort", "none-substrate-absent"}

def fail(msg):
    raise SystemExit("GOLD_CHECK FAIL: " + msg)

def load(manifest_dir, name):
    return json.load(open(f"{manifest_dir}/{name}"))

def validate(snap_dir, gold_dir):
    man = load(gold_dir, "manifest.json")
    snap_man = load(snap_dir, "manifest.json")
    # 1. hashes
    for fn, h in man["files_sha256"].items():
        if hashlib.sha256(open(f"{gold_dir}/{fn}", "rb").read()).hexdigest() != h:
            fail(f"hash mismatch {fn}")
    for fn, h in man["snapshot"]["files_sha256"].items():
        if snap_man["files_sha256"].get(fn) != h:
            fail(f"snapshot hash drift {fn}")
    if man["snapshot"]["version"] != snap_man["snapshot_version"]:
        fail("snapshot version mismatch")
    # 2. load records
    recs = []
    for fn in man["files_sha256"]:
        if fn.startswith("class_"):
            recs += load(gold_dir, fn)
    if len(recs) != man["total"]:
        fail(f"total mismatch {len(recs)} != {man['total']}")
    counts = {}
    for r in recs:
        counts[r["class"]] = counts.get(r["class"], 0) + 1
    if counts != man["quota"]:
        fail(f"quota break {counts}")
    # 3. anchors exist in snapshot
    chunk_refs = {c["chunk_ref"] for c in json.load(__import__("gzip").open(f"{snap_dir}/chunks.jsonl.gz"))}
    spec_codes = {s["code"] for s in load(snap_dir, "spec_points.json")}
    gc = load(snap_dir, "graph_code.json")
    concept_codes = {c["code"] for c in gc["concepts"]}
    misc_codes = {m["code"] for m in gc["misconceptions"]}
    seen_q = set()
    for r in recs:
        if r["substrate"] not in ALLOWED_SUBSTRATE:
            fail(f"{r['id']}: bad substrate")
        if r["query"] in seen_q:
            fail(f"{r['id']}: duplicate query text")
        seen_q.add(r["query"])
        if not r["provenance"].get("source"):
            fail(f"{r['id']}: missing provenance")
        for c in r["gold_spec_points"]:
            if not SPEC_RE.match(c):
                fail(f"{r['id']}: bad spec code format {c}")
            if c not in spec_codes:
                fail(f"{r['id']}: spec code not in snapshot {c}")
        for c in r["gold_concepts"]:
            if c not in concept_codes:
                fail(f"{r['id']}: unknown concept {c}")
        for c in r["gold_misconceptions"]:
            if c not in misc_codes:
                fail(f"{r['id']}: unknown misconception {c}")
        for g in r["gold_evidence"]:
            if g["tier"] not in (1, 2):
                fail(f"{r['id']}: bad tier {g['tier']}")
            if g["rule"] not in KNOWN_RULES:
                fail(f"{r['id']}: unknown rule {g['rule']}")
            if g["chunk_ref"] not in chunk_refs:
                fail(f"{r['id']}: phantom chunk {g['chunk_ref']}")
    return len(recs), counts

if __name__ == "__main__":
    snap_dir, gold_dir = sys.argv[1], sys.argv[2]
    n, counts = validate(snap_dir, gold_dir)
    print(f"GOLD_CHECK PASS: {n} records, quotas ok, all anchors resolve into snapshot")
    if "--selftest" in sys.argv:
        import copy, os, tempfile
        def mutate_all(mutate, man, tmp_g, eligible):
            for fn in os.listdir(tmp_g):
                if not fn.startswith("class_"):
                    continue
                d = load(tmp_g, fn)
                for r in d:
                    if eligible(r):
                        mutate(r)
                        body = json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True)
                        open(f"{tmp_g}/{fn}", "w").write(body)
                        man["files_sha256"][fn] = hashlib.sha256(body.encode()).hexdigest()
                        open(f"{tmp_g}/manifest.json", "w").write(json.dumps(man))
                        return True
            return False

        def run_corrupt(mutate, expect, eligible=lambda r: True):
            tmp_g = tempfile.mkdtemp()
            for fn in os.listdir(gold_dir):
                open(f"{tmp_g}/{fn}", "wb").write(open(f"{gold_dir}/{fn}", "rb").read())
            man = load(gold_dir, "manifest.json")
            if not mutate_all(mutate, man, tmp_g, eligible):
                raise SystemExit(f"SELFTEST SETUP FAIL: no eligible record for {expect}")
            try:
                validate(snap_dir, tmp_g)
                raise SystemExit(f"SELFTEST FAIL: corruption {expect} NOT detected")
            except SystemExit as e:
                if str(e).startswith("GOLD_CHECK FAIL"):
                    print(f"  negative ok ({expect}): {str(e)[17:60]}...")
                else:
                    raise
        m_badcode = lambda r: r.__setitem__("gold_spec_points", ["4CH1-9.99Z"])
        m_phantom = lambda r: r["gold_evidence"].append({"chunk_ref": "deadbeef:0", "tier": 1, "rule": "R1-stem-verbatim"})
        m_dupq = None  # duplicate handled below via two-record mutation
        m_tier = lambda r: r["gold_evidence"][0].__setitem__("tier", 3)
        m_noprov = lambda r: r.__setitem__("provenance", {})
        for mut, name, elig in ((m_badcode, "bad spec code", lambda r: r["gold_spec_points"]),
                                (m_phantom, "phantom chunk", lambda r: True),
                                (m_tier, "bad tier", lambda r: r["gold_evidence"]),
                                (m_noprov, "missing provenance", lambda r: True)):
            run_corrupt(mut, name, elig)

        def run_dupq():
            tmp_g = tempfile.mkdtemp()
            for fn in os.listdir(gold_dir):
                open(f"{tmp_g}/{fn}", "wb").write(open(f"{gold_dir}/{fn}", "rb").read())
            man = load(gold_dir, "manifest.json")
            for fn in sorted(os.listdir(tmp_g)):
                if fn.startswith("class_"):
                    d = load(tmp_g, fn)
                    if len(d) >= 2:
                        d[1]["query"] = d[0]["query"]
                        body = json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True)
                        open(f"{tmp_g}/{fn}", "w").write(body)
                        man["files_sha256"][fn] = hashlib.sha256(body.encode()).hexdigest()
                        break
            open(f"{tmp_g}/manifest.json", "w").write(json.dumps(man))
            try:
                validate(snap_dir, tmp_g)
                raise SystemExit("SELFTEST FAIL: duplicate query NOT detected")
            except SystemExit as e:
                if str(e).startswith("GOLD_CHECK FAIL"):
                    print(f"  negative ok (duplicate query): {str(e)[17:60]}...")
                else:
                    raise

        def run_quota():
            tmp_g = tempfile.mkdtemp()
            for fn in os.listdir(gold_dir):
                open(f"{tmp_g}/{fn}", "wb").write(open(f"{gold_dir}/{fn}", "rb").read())
            man = load(gold_dir, "manifest.json")
            for fn in os.listdir(tmp_g):
                if fn.startswith("class_"):
                    d = load(tmp_g, fn)
                    if len(d) > 1:
                        d.pop()
                        body = json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True)
                        open(f"{tmp_g}/{fn}", "w").write(body)
                        man["files_sha256"][fn] = hashlib.sha256(body.encode()).hexdigest()
                        break
            open(f"{tmp_g}/manifest.json", "w").write(json.dumps(man))
            try:
                validate(snap_dir, tmp_g)
                raise SystemExit("SELFTEST FAIL: quota break NOT detected")
            except SystemExit as e:
                if str(e).startswith("GOLD_CHECK FAIL"):
                    print(f"  negative ok (quota break): {str(e)[17:60]}...")
                else:
                    raise
        run_dupq()
        run_quota()
        print("GOLD_CHECK SELFTEST PASS: 6/6 corruption classes detected")
