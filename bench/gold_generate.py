#!/usr/bin/env python3
"""T-C13 M0: generate gold set v1 (120 queries, 12 classes) from the frozen snapshot.
Deterministic (no RNG): selection via sha256-derived ordering. Labels carry rule ids (R1/R2/R3)."""
import hashlib, json, os, re, unicodedata

import os
SNAP = os.environ.get("BENCH_SNAPSHOT", "evidence/bench-001/snapshot")
OUT = os.environ.get("BENCH_GOLD_OUT", "bench/gold")
os.makedirs(OUT, exist_ok=True)

snap_man = json.load(open(f"{SNAP}/manifest.json"))
chunks = json.load(gzip.open(f"{SNAP}/chunks.jsonl.gz")) if False else json.loads(__import__("gzip").open(f"{SNAP}/chunks.jsonl.gz").read())
specs = {s["code"]: s for s in json.load(open(f"{SNAP}/spec_points.json"))}
edges = json.load(open(f"{SNAP}/graph_edges.json"))
gc = json.load(open(f"{SNAP}/graph_code.json"))
qas = json.load(open(f"{SNAP}/question_anchors.json"))
concepts = {c["code"]: c for c in gc["concepts"]}
miscs = {m["code"]: m for m in gc["misconceptions"]}

STOP = set("the a an of to in on for and or is are was were be been with as by at from that this it its "
           "what which how why when who does do did can could should would will shall may might must not no "
           "i you we they he she me my our your their about into over under between within per each other".split())

def norm(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    return re.sub(r"[^a-z0-9]+", "", s)

def det_order(items, salt):
    return sorted(items, key=lambda x: hashlib.sha256((salt + "|" + str(x)).encode()).hexdigest())

def short_title(t, n=60):
    t = re.sub(r"\s*\(.*?\)\s*", " ", t or "").strip(" .;")
    return (t[: n - 1] + "…") if len(t) > n else t

def title_terms(title, df, k=3):
    toks = [w for w in re.findall(r"[a-z]{4,}", (title or "").lower())
            if w not in STOP and 2 <= df.get(w, 0) < 300]
    toks = sorted(set(toks), key=lambda w: (df.get(w, 0), w))
    return toks[:k]

# precompute normalized chunk text + document frequency of terms
for c in chunks:
    c["_n"] = norm(c["content"])
DF = {}
for c in chunks:
    for w in set(re.findall(r"[a-z]{4,}", c["content"].lower())):
        DF[w] = DF.get(w, 0) + 1

def R1(stem, kind):
    """tier-2: chunk whose normalized content contains the normalized stem prefix."""
    n = norm(stem)[:80]
    if len(n) < 40:
        return []
    hits = [c for c in chunks if c["kind"] == kind and n in c["_n"]]
    return [{"chunk_ref": c["chunk_ref"], "tier": 2, "rule": "R1-stem-verbatim"} for c in det_order(hits, "R1")[:3]]

def R2(terms, kind=None, cap=5, min_match=2):
    """tier-1: chunks containing >=min_match of the distinctive terms."""
    if not terms:
        return []
    hits = [c for c in chunks if sum(t in c["content"].lower() for t in terms) >= min_match
            and (kind is None or c["kind"] == kind)]
    return [{"chunk_ref": c["chunk_ref"], "tier": 1, "rule": "R2-term-cooccurrence"} for c in det_order(hits, "R2")[:cap]]

def R3(paper_code, kind, cap=5):
    """tier-1: same-paper cohort chunks."""
    hits = [c for c in chunks if c["paper_code"] == paper_code and c["kind"] == kind]
    return [{"chunk_ref": c["chunk_ref"], "tier": 1, "rule": "R3-paper-cohort"} for c in det_order(hits, "R3")[:cap]]

SPEC_RE = re.compile(r"^4CH1-[0-9]+\.[0-9]+[A-Z]?$")

def spec_of(a):
    """Validated question anchor as gold spec code — quarantined to 4CH1 spec-point codes only.
    Non-4CH1 anchor codes (ING-* paper-scrape nodes wired as primary_topic anchors) are NOT valid
    gold spec anchors; they are recorded in provenance as anchor_code_non_spec (audit finding 2026-09-17)."""
    ok = a["anchor_code"] and SPEC_RE.match(a["anchor_code"])
    return [a["anchor_code"]] if ok else []

def prov_anchor(a, base):
    p = dict(base)
    if a["anchor_code"] and not SPEC_RE.match(a["anchor_code"]):
        p["anchor_code_non_spec"] = a["anchor_code"]
    return p

REC = []
USED_QUERIES = set()
def add(cls, substrate, query, gold_specs, gold_evidence, concepts_, misc_, prov, note=""):
    assert query not in USED_QUERIES, f"dup query: {query[:60]}"
    USED_QUERIES.add(query)
    REC.append({"id": f"g1-{len(REC)+1:03d}", "class": cls, "substrate": substrate,
                "query": query, "gold_spec_points": sorted(gold_specs),
                "gold_evidence": gold_evidence, "gold_concepts": sorted(concepts_),
                "gold_misconceptions": sorted(misc_), "provenance": prov, "notes": note})

sp_codes = det_order([c for c in specs if specs[c]["title"]], "specs")
anchor_calc = [a for a in qas if re.search(r"\b(calculate|determine|deduce|how many|how much|what mass|what volume|concentration|moles?|average rate|energy released)\b", a["stem"] or "", re.I)]
anchor_numeric = [a for a in qas if a not in anchor_calc and re.search(r"\d", a["stem"] or "")]
anchor_any = [a for a in qas if a["stem"]]
draw_anchor = [a for a in qas if re.search(r"\b(draw|label|complete the|plot|graph|diagram|sketch)\b", a["stem"] or "", re.I)]
prereq_edges = det_order([e for e in edges if e["relation"] == "REQUIRES_PREREQUISITE"], "prereq")
rem_edges = det_order([e for e in edges if e["relation"] in ("REMEDIATED_BY", "WRONG_ANSWER_PATTERN")], "rem")

# 1. factual (15)
for i, code in enumerate(sp_codes[:15]):
    t = short_title(specs[code]["title"])
    add("factual", "chunks+kg", f"What are the key facts I should know about {t}?", [code],
        R2(title_terms(specs[code]["title"], DF)), [], [], {"source": "spec_point:" + code, "rule": "R2"}, note="auto-derived v1")

# 2. conceptual (15)
for i, code in enumerate(sp_codes[15:30]):
    t = short_title(specs[code]["title"]).rstrip(".?")
    add("conceptual", "chunks+kg", f"Explain {t[0].lower() + t[1:]}.", [code],
        R2(title_terms(specs[code]["title"], DF)), [], [], {"source": "spec_point:" + code, "rule": "R2"}, note="auto-derived v1")

# 3. calculation (10 = 4 cue-matched + 6 numeric-stem fill; command_word column is unpopulated in production)
for a in det_order(anchor_calc, "calc"):
    if len([r for r in REC if r["class"] == "calculation"]) >= 10:
        break
    stem = re.sub(r"\s+", " ", a["stem"]).strip()
    q = stem[:180] + ("…" if len(stem) > 180 else "")
    if q in USED_QUERIES:
        continue
    ev = R1(a["stem"], "QUESTION_PAPER") + R3(a["paper_code"], "MARK_SCHEME", 3)
    add("calculation", "chunks", q, spec_of(a), ev, [], [],
        prov_anchor(a, {"source": f"qversion[{a['paper_code']}]", "rule": "R1+R3"}), note="auto-derived v1; selector=cue-word")
used = {r["provenance"]["source"] for r in REC if r["class"] == "calculation"}
for a in det_order(anchor_numeric, "numfill"):
    if len([r for r in REC if r["class"] == "calculation"]) >= 10:
        break
    stem = re.sub(r"\s+", " ", a["stem"]).strip()
    q = stem[:180] + ("…" if len(stem) > 180 else "")
    if q in USED_QUERIES:
        continue
    add("calculation", "chunks", q, spec_of(a),
        R1(a["stem"], "QUESTION_PAPER") + R3(a["paper_code"], "MARK_SCHEME", 3), [], [],
        prov_anchor(a, {"source": f"qversion[{a['paper_code']}]", "rule": "R1+R3"}), note="auto-derived v1; selector=numeric-stem fill (quota amendment, command_word unpopulated)")

# 4. prerequisite (12) — DB semantics: source REQUIRES_PREREQUISITE target (source = the advanced concept)
# Endpoints may include PRACTICAL nodes (4CH1-PR-*) — non-concept endpoints are quarantined to provenance.
for e in det_order(prereq_edges, "prereq"):
    if len([r for r in REC if r["class"] == "prerequisite"]) >= 12:
        break
    sc, tc = e["source"], e["target"]
    st, tt = concepts.get(tc, {}).get("title", tc), concepts.get(sc, {}).get("title", sc)
    gold_specs = set(concepts.get(sc, {}).get("spec_points", [])) | set(concepts.get(tc, {}).get("spec_points", []))
    gold_con = [c for c in (sc, tc) if c in concepts]
    q = f"Do I need to master {short_title(st)} before I can understand {short_title(tt)}?"
    if q in USED_QUERIES:
        continue
    prov = {"source": f"edge:REQUIRES_PREREQUISITE:{sc}->{tc}", "rule": "R2"}
    nc = [c for c in (sc, tc) if c not in concepts]
    if nc:
        prov["endpoint_non_concept"] = nc
    add("prerequisite", "kg", q, gold_specs,
        R2(title_terms(st, DF) + title_terms(tt, DF)), gold_con, [], prov, note="auto-derived v1")

# 5. misconception (10) — DB semantics: misconception -> REMEDIATED_BY -> concept (source=MIS, target=CON)
for e in det_order(rem_edges, "rem"):
    if len([r for r in REC if r["class"] == "misconception"]) >= 10:
        break
    mc, cc = e["source"], e["target"]  # misconception code, concept code
    m = miscs.get(mc, {})
    src_specs = set(concepts.get(cc, {}).get("spec_points", []))
    mt = short_title(m.get("title") or mc, 70).rstrip(".")
    q = f"Why is '{mt.lower()}' a wrong idea, and what is the correct picture?"
    if q in USED_QUERIES:
        continue
    add("misconception", "kg+chunks", q,
        src_specs, R2(title_terms(m.get("title"), DF) or title_terms(concepts.get(cc, {}).get("title"), DF)),
        [cc] if cc.startswith("4CH1-CON") else [], [mc],
        {"source": f"edge:{e['relation']}:{mc}->{cc}", "rule": "R2"}, note="auto-derived v1")

# 6. why-wrong (10)
for a in det_order(anchor_any, "whywrong"):
    if len([r for r in REC if r["class"] == "why_wrong"]) >= 10:
        break
    stem1 = re.sub(r"\s+", " ", a["stem"]).split(". ")[0][:140]
    q = f"For this exam question: '{stem1}' — what are the common mistakes students make?"
    if q in USED_QUERIES:
        continue
    add("why_wrong", "chunks", q, spec_of(a),
        R1(a["stem"], "QUESTION_PAPER") + R3(a["paper_code"], "MARK_SCHEME", 4), [], [],
        prov_anchor(a, {"source": f"qversion[{a['paper_code']}]", "rule": "R1+R3"}), note="auto-derived v1")

# 7. exam-question retrieval (10)
for a in det_order(anchor_any, "examq"):
    if len([r for r in REC if r["class"] == "exam_question"]) >= 10:
        break
    stem = re.sub(r"\s+", " ", a["stem"]).strip()
    q = stem[:190] + ("…" if len(stem) > 190 else "")
    if q in USED_QUERIES:
        continue
    add("exam_question", "chunks", q, spec_of(a),
        R1(a["stem"], "QUESTION_PAPER"), [], [],
        prov_anchor(a, {"source": f"qversion[{a['paper_code']}]", "rule": "R1"}), note="auto-derived v1")

# 8. mark-scheme retrieval (8) — command_word unpopulated; selector = det_order over paper-linked anchors
for a in det_order([x for x in anchor_any if x["paper_code"]], "msq"):
    if len([r for r in REC if r["class"] == "mark_scheme"]) >= 8:
        break
    stem1 = re.sub(r"\s+", " ", a["stem"]).split(". ")[0][:120]
    q = f"What does the mark scheme accept for the {a['paper_code']} question: '{stem1}'?"
    if q in USED_QUERIES:
        continue
    add("mark_scheme", "chunks", q, spec_of(a), R3(a["paper_code"], "MARK_SCHEME", 5), [], [],
        prov_anchor(a, {"source": f"qversion[{a['paper_code']}]", "rule": "R3"}), note="auto-derived v1; selector=paper-linked (command_word unpopulated)")

# 9. revision-note retrieval (10) — substrate notes_mirror (no arm indexes notes at t0)
for i, code in enumerate(sp_codes[30:40]):
    t = short_title(specs[code]["title"])
    add("revision_note", "notes_mirror", f"Give me quick revision notes covering {t}.", [code], [],
        [], [], {"source": "spec_point:" + code, "rule": "none-substrate-absent"}, note="substrate notes_mirror; per-class N/A at t0")

# 10. vague learner language (8)
VAGUE = ["I don't get {} at all — help me understand it.",
         "so what exactly is {}? like in simple words",
         "my teacher said {} but I'm confused, what does it mean?",
         "can someone break down {} for me please",
         "whats the point of {} and when do I use it",
         "i keep getting {} wrong, what am I missing",
         "quick question — {} — what is that about?",
         "explain {} like I'm having a bad day"]
vag_src = det_order(sp_codes[40:60], "vague")[:8]
for i, code in enumerate(vag_src):
    t = short_title(specs[code]["title"], 45).rstrip(".?")
    add("vague_learner", "chunks+kg", VAGUE[i].format(t), [code],
        R2(title_terms(specs[code]["title"], DF)), [], [], {"source": "spec_point:" + code, "rule": "R2"}, note="auto-derived v1")

# 11. multi-SpecificationPoint (7)
by_unit = {}
for c in sorted(specs):
    by_unit.setdefault(c.rsplit(".", 1)[0], []).append(c)
pairs = []
allc = det_order(sp_codes, "multi")
for i in range(len(allc) - 1):
    a, b = allc[i], allc[i + 1]
    if a.rsplit(".", 1)[0] != b.rsplit(".", 1)[0] and (a, b) not in pairs:
        pairs.append((a, b))
    if len(pairs) == 7:
        break
for a, b in pairs:
    ta, tb = short_title(specs[a]["title"]), short_title(specs[b]["title"])
    add("multi_spec_point", "chunks+kg", f"How do {ta} and {tb} connect in this topic?",
        [a, b], R2(title_terms(specs[a]["title"], DF) + title_terms(specs[b]["title"], DF)), [], [],
        {"source": f"spec_points:{a}+{b}", "rule": "R2"}, note="auto-derived v1")

# 12. diagram/figure-dependent (5) — substrate figures; selector = draw/label cue stems (command_word unpopulated)
for a in det_order(draw_anchor, "draw"):
    if len([r for r in REC if r["class"] == "diagram_dependent"]) >= 5:
        break
    q = f"Draw / label the diagram required for: {short_title(a['stem'], 90)}"
    if q in USED_QUERIES:
        continue
    add("diagram_dependent", "figures", q, spec_of(a), [], [], [],
        prov_anchor(a, {"source": f"qversion[{a['paper_code']}] selector=draw-cue-stem", "rule": "none-substrate-absent"}),
        note="substrate figures; per-class N/A at t0")

# quota check
QUOTA = {"factual": 15, "conceptual": 15, "calculation": 10, "prerequisite": 12, "misconception": 10,
         "why_wrong": 10, "exam_question": 10, "mark_scheme": 8, "revision_note": 10,
         "vague_learner": 8, "multi_spec_point": 7, "diagram_dependent": 5}
counts = {}
for r in REC:
    counts[r["class"]] = counts.get(r["class"], 0) + 1
assert counts == QUOTA, (counts, QUOTA)

# per-class files + manifest
rules = {"R1-stem-verbatim": "normalized stem prefix (>=40 chars) contained verbatim in chunk content -> tier 2",
         "R2-term-cooccurrence": "gte 2 of 3 distinctive title terms (df-filtered 2..300) co-occur in chunk -> tier 1, cap 5",
         "R3-paper-cohort": "same-paper same-kind chunks -> tier 1, cap 5",
         "none-substrate-absent": "no chunk substrate at t0 (notes_mirror / figures); gold = spec anchors only"}
man = {"set_version": "gold-v1", "frozen": "2026-09-17", "total": len(REC), "quota": QUOTA, "counts": counts,
       "quota_amendments": {"calculation": "command_word column unpopulated in production (119/119 NULL); 4 cue-matched + 6 numeric-stem fill, each record notes its selector; spec §3.1 table annotated accordingly"},
       "snapshot": {"version": snap_man["snapshot_version"],
                    "files_sha256": snap_man["files_sha256"]},
       "label_rules": rules, "anti_leakage": "queries authored without executing any retrieval arm; set frozen + hashed before Run 1",
       "audit_findings": {"non_spec_question_anchors": "85/119 VALIDATED question anchors carry primary_topic_node_id pointing at ING-* paper-scrape nodes (not 4CH1 spec points); such anchors are quarantined OUT of gold_spec_points and recorded per-record as provenance.anchor_code_non_spec"},
       "files_sha256": {}}
for cls in QUOTA:
    body = json.dumps([r for r in REC if r["class"] == cls], ensure_ascii=False, indent=1, sort_keys=True)
    fn = f"class_{cls}.json"
    open(f"{OUT}/{fn}", "w").write(body)
    man["files_sha256"][fn] = hashlib.sha256(body.encode()).hexdigest()
open(f"{OUT}/manifest.json", "w").write(json.dumps(man, indent=2, sort_keys=True))
with open(f"{OUT}/SHA256SUMS", "w") as f:
    for n, h in sorted(man["files_sha256"].items()):
        f.write(f"{h}  {n}\n")

# coverage stats (verdicts only)
ev = sum(1 for r in REC if r["gold_evidence"])
gspec = sum(1 for r in REC if r["gold_spec_points"])
r1 = sum(1 for r in REC if any(g["rule"] == "R1-stem-verbatim" for g in r["gold_evidence"]))
print(f"gold v1: {len(REC)} queries | with gold specs: {gspec} | with chunk evidence: {ev} (R1 hits: {r1})")
print("evidence counts per class:", {k: sum(1 for r in REC if r['class'] == k and r['gold_evidence']) for k in QUOTA})
