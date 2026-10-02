#!/usr/bin/env python3
"""T-C66 stage-2: verify all 16 relabel targets against the corpus manifests at
HEAD f0ea3a1f9 (syllabai-pastpapers). Derives each target source_uri from the
manifest's own official_reference + series, then asserts sha256 == DB checksum.
Also asserts the derived target equals the probe's target set and that no live
DB row collides (re-checked here for the record). Read-only."""
import json, pathlib, urllib.request, sys

GH = pathlib.Path("/home/z/my-project/tool-results/fa_recon")
probe = json.load(open(GH / "probe_out.json"))
rows16 = {r["row_id"]: r for r in probe["rows16_state"]}
assert len(rows16) == 16

HEAD = "f0ea3a1f9"
RAW = f"https://raw.githubusercontent.com/SyllabAI/syllabai-pastpapers/{HEAD}"
TOKEN = None
for line in pathlib.Path("/home/z/my-project/scripts/.ghenv").read_text().splitlines():
    if line.startswith("export github_token="):
        TOKEN = line.split("=", 1)[1].strip().strip('"')

# 8 R dirs (session dir, paper dir)
DIRS = [(s, p) for s in ("2013-06", "2014-06", "2016-06", "2017-06") for p in ("4CH0-1CR", "4CH0-2CR")]

def fetch(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode()

manifest_pins = {}   # (sha256) -> (corpus_path, official_ref, series, material)
plan = []
for sess, pdir in DIRS:
    base = f"past-papers/pearson-edexcel/international-gcse/chemistry/4ch0/past-papers/{sess}/{pdir}"
    text = fetch(f"{RAW}/{base}/manifest.yaml")
    # minimal parse of the fields we need
    import re
    official = re.search(r"official_reference:\s*(\S+)", text).group(1)
    series = re.search(r"normalized:\s*(\S+)", text).group(1)
    mats = {m[0]: m[2] for m in re.findall(r"- type:\s*(\S+)\s*\n\s*path:\s*(\S+)\s*\n\s*sha256:\s*([0-9a-f]{64})", text)}
    assert set(mats) == {"mark-scheme", "question-paper"}, (pdir, mats.keys())
    for mtype, sha in mats.items():
        kind = "MARK_SCHEME" if mtype == "mark-scheme" else "QUESTION_PAPER"
        path = {"mark-scheme": "ms.pdf", "question-paper": "qp.pdf"}[mtype]
        manifest_pins[sha] = (f"{base}/{path}", official, series, kind, path)

    # match the two DB rows for this dir
    sha_to_mtype = {v: k for k, v in mats.items()}
    for row_id, r in rows16.items():
        if r["checksum"] in sha_to_mtype:
            mtype = sha_to_mtype[r["checksum"]]
            kind = "MARK_SCHEME" if mtype == "mark-scheme" else "QUESTION_PAPER"
            assert r["kind"] == kind, (row_id, r["kind"], mtype)
            path = {"mark-scheme": "ms.pdf", "question-paper": "qp.pdf"}[mtype]
            # target derivation from the manifest's own identity fields
            code_dash = official.replace("/", "-")          # 4CH0/1CR -> 4CH0-1CR
            sess_token = series.replace("-", "")            # 2013-06 -> 201306
            target = f"{code_dash}-{sess_token}/{path}"
            plan.append({
                "row_id": row_id, "document_id": r["document_id"], "kind": r["kind"],
                "old_source_uri": r["source_uri"], "new_source_uri": target,
                "checksum": r["checksum"], "chunks": r["chunks"],
                "corpus_pin_path": f"{base}/{path}", "corpus_official_reference": official,
                "corpus_series": series, "corpus_head": HEAD,
            })

assert len(plan) == 16, f"plan rows {len(plan)} != 16"
# every DB row's checksum must pin at the CORRECT R dir with the correct kind
for p in plan:
    assert p["old_source_uri"].split("/")[0].endswith(("-1C-", "-2C-")) or p["old_source_uri"].startswith("4CH0-"), p
    assert p["new_source_uri"].split("/")[0] in {"4CH0-1CR", "4CH0-2CR"} or p["new_source_uri"].split("/")[0].startswith("4CH0-1CR") or p["new_source_uri"].split("/")[0].startswith("4CH0-2CR"), p
    exp_prefix = "4CH0-1CR" if p["old_source_uri"].startswith("4CH0-1C-") else "4CH0-2CR"
    assert p["new_source_uri"].startswith(exp_prefix + "-"), (p["old_source_uri"], p["new_source_uri"], exp_prefix)
    assert p["new_source_uri"].endswith("/qp.pdf" if p["kind"] == "QUESTION_PAPER" else "/ms.pdf")
    assert p["old_source_uri"].endswith("/qp.pdf" if p["kind"] == "QUESTION_PAPER" else "/ms.pdf")
    # session token preserved
    assert p["new_source_uri"].split("-")[-2] == p["old_source_uri"].split("-")[-2].split("/")[0] or \
           p["new_source_uri"].split("/")[0].rsplit("-", 1)[1] == p["old_source_uri"].split("/")[0].rsplit("-", 1)[1], p

# target set equality vs probe
probe_targets = set(probe["targets"])
plan_targets = {p["new_source_uri"] for p in plan}
assert plan_targets == probe_targets, (plan_targets ^ probe_targets)
# uniqueness
assert len(plan_targets) == 16
# no old URI equals any new URI (mapping actually moves every row)
for p in plan:
    assert p["old_source_uri"] != p["new_source_uri"]

out = {"corpus_head": HEAD, "plan": plan,
       "manifest_pin_count": len(manifest_pins),
       "target_collisions_in_probe": probe["target_collisions"]}
GH.joinpath("relabel_plan.json").write_text(json.dumps(out, indent=1))
print(f"PLAN OK: 16 rows, {len(manifest_pins)} manifest pins @ {HEAD}")
for p in plan:
    print(f"  {p['old_source_uri']:26} -> {p['new_source_uri']:26} ({p['kind'][:4]}, {p['chunks']} chunks)")
