#!/usr/bin/env python3
"""Build the interactive Ruling-3 spot-check worksheet (single self-contained HTML).

Companion to gold_spotcheck.py: renders the recorded deterministic sample as an
offline interactive review page for the owner (ruling 3 verdicts stay human).

Reuses the FROZEN generator's own logic (bench/gold_spotcheck.py) so the sample
shown to the owner is byte-for-byte the recorded one:
  - fail-closed checksum verification of gold-v1 against manifest.json;
  - seed = sha256(manifest.json)[:16], deterministic no-RNG sampling;
  - cross-check the re-derived sample against the recorded
    evidence/bench-001/governance/ruling-3-spot-check-sample.json (abort on drift);
  - resolve every gold-evidence chunk_ref into snap-001 (fail-closed) and embed
    the full chunk content so the owner can judge without opening the snapshot.

Output: evidence/bench-001/governance/ruling-3-spot-check-interactive.html
        (override with argv[1] if needed)

The HTML autosaves verdicts to localStorage and exports commit-ready artifacts
(ruling-3-owner-verdicts-<seed>.json + marked worksheet CSV). The exported
verdicts — never this page itself — are the recorded owner evidence.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]  # bench/r3_interactive/ -> repo root
TEMPLATE = Path(__file__).resolve().parent / "r3_template.html"
OUT = REPO / "evidence" / "bench-001" / "governance" / "ruling-3-spot-check-interactive.html"

sys.path.insert(0, str(REPO / "bench"))
import gold_spotcheck as gs  # noqa: E402


def fail(msg: str) -> int:
    print(f"ABORT: {msg}")
    return 1


def main() -> int:
    if len(sys.argv) > 1:
        out = Path(sys.argv[1])
    else:
        out = OUT

    # --- frozen basis + fail-closed verification (same posture as gold_spotcheck) ---
    manifest_path = gs.GOLD / "manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    manifest_sha = gs.sha256_bytes(manifest_bytes)
    seed = manifest_sha[:16]

    counts = manifest["counts"]
    records_by_class = {}
    for class_name in gs.CLASS_ORDER:
        fname = f"class_{class_name}.json"
        if gs.sha256_file(gs.GOLD / fname) != manifest["files_sha256"][fname]:
            return fail(f"{fname} sha256 mismatch — gold-v1 is frozen, do not proceed")
        records = json.loads((gs.GOLD / fname).read_text())
        if len(records) != counts[class_name]:
            return fail(f"{fname} has {len(records)} records, manifest says {counts[class_name]}")
        records_by_class[class_name] = records

    # re-derive the sample deterministically
    sampled = {c: gs.sample_class(c, records_by_class[c], seed) for c in gs.CLASS_ORDER}

    # cross-check against the RECORDED sample artifact
    recorded = json.loads((gs.OUT / "ruling-3-spot-check-sample.json").read_text())
    if recorded["method"]["seed"] != seed:
        return fail("recorded sample.json seed differs from re-derived seed")
    for c in gs.CLASS_ORDER:
        want = sorted(recorded["per_class"][c]["query_ids"])
        got = sorted(r["id"] for r in sampled[c])
        if want != got:
            return fail(f"sample drift for class {c}: recorded={want} derived={got}")

    # resolve evidence chunks (fail-closed) + build payload records
    chunk_index = gs.resolve_chunk_index()
    classes_meta = []
    records_out = []
    for no, c in enumerate(gs.CLASS_ORDER, start=1):
        classes_meta.append({
            "no": no, "name": c, "label": gs.CLASS_LABELS[c],
            "sampled": len(sampled[c]), "total": counts[c],
            "full": c in gs.FULL_CLASSES,
        })
        for r in sorted(sampled[c], key=lambda x: x["id"]):
            evidence = []
            tiers, refs = {}, []
            for ev in r.get("gold_evidence", []):
                ref = ev["chunk_ref"]
                if ref not in chunk_index:
                    return fail(f"gold evidence {gs.short_ref(ref)} of {r['id']} missing from snap-001")
                ch = chunk_index[ref]
                if ch["page_start"] is None:
                    pages = "?"
                elif str(ch["page_start"]) == str(ch["page_end"]):
                    pages = str(ch["page_start"])
                else:
                    pages = f"{ch['page_start']}-{ch['page_end']}"
                content = " ".join(ch["content"].split())
                truncated = len(content) > 2000
                evidence.append({
                    "chunk_ref": ref,
                    "short_ref": gs.short_ref(ref),
                    "tier": ev["tier"],
                    "rule": ev["rule"],
                    "paper_code": ch["paper_code"] or "—",
                    "kind": ch["kind"],
                    "pages": pages,
                    "paper_state": ch["paper_state"],
                    "content": content[:2000] + ("…" if truncated else ""),
                    "content_truncated": truncated,
                })
                tiers[ev["tier"]] = tiers.get(ev["tier"], 0) + 1
                refs.append(gs.short_ref(ref))
            records_out.append({
                "id": r["id"], "class_no": no, "class": c, "query": r["query"],
                "gold_spec_points": r.get("gold_spec_points", []),
                "gold_concepts": r.get("gold_concepts", []),
                "gold_misconceptions": r.get("gold_misconceptions", []),
                "evidence": evidence,
                "evidence_tiers": ", ".join(f"t{t}×{tiers[t]}" for t in sorted(tiers, reverse=True)) or "none",
                "evidence_refs": " ".join(refs),
                "provenance_str": gs.provenance_text(r),
                "substrate": r.get("substrate", ""),
                "notes": r.get("notes", ""),
            })

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                          capture_output=True, text=True, check=True).stdout.strip()

    payload = {
        "meta": {
            "artifact": "interactive ruling-3 spot-check worksheet v1",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source_commit": head,
            "generator": "bench/r3_interactive/build_r3_interactive.py reusing bench/gold_spotcheck.py logic",
            "gold_version": manifest.get("version", "gold-v1"),
            "manifest_sha256": manifest_sha,
            "seed": seed,
            "seed_derivation": "sha256(bench/gold/manifest.json)[:16]",
            "snapshot": "evidence/bench-001/snapshot (snap-001)",
            "sample_record": "evidence/bench-001/governance/ruling-3-spot-check-sample.json",
            "reproduce": "python3 bench/r3_interactive/build_r3_interactive.py",
            "sampling": recorded["method"]["sampling"],
            "default_reviewer": "Iqra Hoque <ihoque2420347@bscse.uiu.ac.bd>",
        },
        "classes": classes_meta,
        "records": records_out,
        "chunks": {ref: {"content": " ".join(c["content"].split())}
                   for ref, c in chunk_index.items()},
    }

    # embed only chunks actually referenced (keep the file lean)
    used = {ev["chunk_ref"] for rec in records_out for ev in rec["evidence"]}
    payload["chunks"] = {k: v for k, v in payload["chunks"].items() if k in used}

    data_json = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).replace("<", "\\u003c")
    html = TEMPLATE.read_text(encoding="utf-8").replace("__DATA_JSON__", data_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    # validation: the embedded JSON must parse back and count correctly
    tag = html.split('<script id="payload" type="application/json">')[1].split("</script>")[0]
    back = json.loads(tag)
    assert len(back["records"]) == recorded["total_sampled"] == 51, "record count mismatch"
    assert sum(len(b["evidence"]) for b in back["records"]) >= 1
    assert all(r["id"] in {x["id"] for x in back["records"]} for c in gs.CLASS_ORDER
               for x in sampled[c])
    print(f"OK: wrote {out} ({out.stat().st_size/1024:.0f} KB)")
    print(f"    51 records, {len(used)} unique evidence chunks, seed {seed}, base {head[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
