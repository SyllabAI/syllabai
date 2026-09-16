#!/usr/bin/env python3
"""Ruling-3 gold-label spot-check worksheet generator (T-C13 spec §10, ruling 3).

Ruling 3 (RATIFIED v1.0): gold-v1 labels are auto-derived, therefore the owner
spot-checks a sample — 20% stratified + 100% of classes 4/5/6 — before the
class can be trusted; any class below 90% owner-agreement is manually
re-authored before the next recorded run.

Determinism contract (same posture as gold_generate.py — generators, no
freehand):
  - inputs are the FROZEN gold-v1 files; every file's SHA-256 is verified
    against bench/gold/manifest.json before anything is sampled (fail-closed);
  - the sampling seed is derived from the manifest bytes themselves
    (seed = sha256(manifest.json)[:16]), so any gold-set change resamples and
    is visible in the recorded seed;
  - selection inside a class sorts query ids ascending, then orders them by
    sha256(f"{seed}:{query_id}") ascending and takes the first k — no RNG,
    no Python-version-dependent behavior;
  - sampling rule: classes 4/5/6 (prerequisite, misconception, why_wrong per
    spec §3.1) → 100%; every other class → ceil(0.2 * n), minimum 1.

Outputs (all under evidence/bench-001/governance/):
  ruling-3-spot-check-sample.json   machine-readable sample + method + checksums
  ruling-3-spot-check-worksheet.md  the owner-facing review worksheet
  ruling-3-spot-check-worksheet.csv the same sample as a marking spreadsheet

Every gold_evidence chunk_ref of every sampled record must resolve into the
snap-001 chunk index (fail-closed) and is emitted with paper/page metadata and
a content excerpt so the owner can judge labels without extra tooling.
"""

import csv
import gzip
import hashlib
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GOLD = REPO / "bench" / "gold"
SNAPSHOT = REPO / "evidence" / "bench-001" / "snapshot"
OUT = REPO / "evidence" / "bench-001" / "governance"

# spec §3.1 quota table order → class numbers used by ruling 3
CLASS_ORDER = [
    "factual", "conceptual", "calculation", "prerequisite", "misconception",
    "why_wrong", "exam_question", "mark_scheme", "revision_note",
    "vague_learner", "multi_spec_point", "diagram_dependent",
]
CLASS_LABELS = {
    "factual": "Direct factual questions",
    "conceptual": "Conceptual explanations",
    "calculation": "Calculations",
    "prerequisite": "Prerequisite questions",
    "misconception": "Misconception questions",
    "why_wrong": "Why did I get this wrong?",
    "exam_question": "Exam-question retrieval",
    "mark_scheme": "Mark-scheme retrieval",
    "revision_note": "Revision-note retrieval",
    "vague_learner": "Vague learner-language queries",
    "multi_spec_point": "Multi-SpecificationPoint questions",
    "diagram_dependent": "Diagram/figure-dependent questions",
}
FULL_CLASSES = {"prerequisite", "misconception", "why_wrong"}  # classes 4/5/6
STRATIFIED_FRACTION = 0.2
EXCERPT_CHARS = 150


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def excerpt(text: str) -> str:
    flat = " ".join(text.split())
    if len(flat) <= EXCERPT_CHARS:
        return flat
    return flat[: EXCERPT_CHARS - 1].rstrip() + "…"


def short_ref(chunk_ref: str) -> str:
    checksum, _, ordinal = chunk_ref.rpartition(":")
    return f"{checksum[:10]}…:{ordinal}"


def sample_class(class_name: str, records: list, seed: str) -> list:
    ids = sorted(r["id"] for r in records)
    if class_name in FULL_CLASSES:
        k = len(ids)
    else:
        k = max(1, math.ceil(len(ids) * STRATIFIED_FRACTION))
    ranked = sorted(ids, key=lambda q: sha256_bytes(f"{seed}:{q}".encode()))
    chosen = set(ranked[:k])
    return sorted((r for r in records if r["id"] in chosen), key=lambda r: r["id"])


def evidence_counts(record: dict) -> str:
    tiers = {}
    for ev in record.get("gold_evidence", []):
        tiers[ev["tier"]] = tiers.get(ev["tier"], 0) + 1
    return ", ".join(f"t{t}×{tiers[t]}" for t in sorted(tiers, reverse=True)) or "none"


def provenance_text(record: dict) -> str:
    prov = record.get("provenance", {})
    return " · ".join(f"{k}={prov[k]}" for k in sorted(prov))


def resolve_chunk_index() -> dict:
    with gzip.open(SNAPSHOT / "chunks.jsonl.gz", "rt", encoding="utf-8") as f:
        chunks = json.load(f)
    return {c["chunk_ref"]: c for c in chunks}


def main() -> int:
    manifest_path = GOLD / "manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    manifest_sha = sha256_bytes(manifest_bytes)
    seed = manifest_sha[:16]

    # fail-closed: verify every class file against the frozen manifest
    counts = manifest["counts"]
    records_by_class = {}
    for class_name in CLASS_ORDER:
        fname = f"class_{class_name}.json"
        digest = sha256_file(GOLD / fname)
        expected = manifest["files_sha256"][fname]
        if digest != expected:
            print(f"ABORT: {fname} sha256 mismatch — gold-v1 is frozen, do not proceed")
            return 1
        records = json.loads((GOLD / fname).read_text())
        if len(records) != counts[class_name]:
            print(f"ABORT: {fname} has {len(records)} records, manifest says {counts[class_name]}")
            return 1
        records_by_class[class_name] = records

    # sample
    sampled = {c: sample_class(c, records_by_class[c], seed) for c in CLASS_ORDER}
    total = sum(len(v) for v in sampled.values())

    # resolve evidence excerpts (fail-closed)
    chunk_index = resolve_chunk_index()
    for class_name, records in sampled.items():
        for record in records:
            for ev in record.get("gold_evidence", []):
                if ev["chunk_ref"] not in chunk_index:
                    print(f"ABORT: gold evidence {short_ref(ev['chunk_ref'])} of "
                          f"{record['id']} does not resolve in snap-001")
                    return 1

    # machine-readable sample record
    sample_doc = {
        "purpose": "T-C13 spec §10 ruling 3 — owner spot-check of auto-derived gold-v1 labels",
        "method": {
            "sampling": "classes 4/5/6 (prerequisite, misconception, why_wrong) 100%; "
                        f"every other class ceil({STRATIFIED_FRACTION} * n), minimum 1",
            "selection": "ids sorted ascending, ranked by sha256(seed + ':' + id) ascending, first k",
            "seed": seed,
            "seed_derivation": "sha256(bench/gold/manifest.json)[:16]",
            "reproduce": "python3 bench/gold_spotcheck.py",
        },
        "basis": {
            "gold_version": manifest.get("version", "gold-v1"),
            "manifest_sha256": manifest_sha,
            "snapshot": "evidence/bench-001/snapshot (snap-001)",
        },
        "total_sampled": total,
        "per_class": {
            c: {
                "sampled": len(sampled[c]),
                "total": counts[c],
                "query_ids": [r["id"] for r in sampled[c]],
            }
            for c in CLASS_ORDER
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    sample_path = OUT / "ruling-3-spot-check-sample.json"
    sample_path.write_text(json.dumps(sample_doc, indent=1) + "\n")

    # CSV marking sheet
    csv_path = OUT / "ruling-3-spot-check-worksheet.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["class_no", "class", "query_id", "query", "gold_spec_points",
                    "gold_concepts", "gold_misconceptions", "evidence_tiers",
                    "evidence_refs", "provenance", "substrate", "notes",
                    "VERDICT (CORRECT/INCORRECT)", "corrected_labels", "owner_notes"])
        for class_name in CLASS_ORDER:
            for r in sampled[class_name]:
                refs = " ".join(short_ref(ev["chunk_ref"]) for ev in r.get("gold_evidence", []))
                w.writerow([
                    CLASS_ORDER.index(class_name) + 1, class_name, r["id"], r["query"],
                    " | ".join(r.get("gold_spec_points", [])),
                    " | ".join(r.get("gold_concepts", [])),
                    " | ".join(r.get("gold_misconceptions", [])),
                    evidence_counts(r), refs, provenance_text(r),
                    r.get("substrate", ""), r.get("notes", ""), "", "", "",
                ])

    # owner-facing worksheet
    lines = []
    lines.append("# Ruling-3 Gold-Label Spot-Check Worksheet — gold-v1")
    lines.append("")
    lines.append("**Owner action item (T-C13 spec §10, ruling 3, RATIFIED v1.0):** gold-v1 labels are")
    lines.append("auto-derived; the owner spot-checks this sample before the labels are trusted.")
    lines.append("**Decision rule (binding):** any class below **90% owner agreement**")
    lines.append("(CORRECT / sampled) is **manually re-authored** before the next recorded run.")
    lines.append("")
    lines.append(f"- Basis: `bench/gold/` gold-v1 (manifest SHA-256 `{manifest_sha[:16]}…`), frozen")
    lines.append(f"- Snapshot: `evidence/bench-001/snapshot/` (snap-001) — chunk excerpts below resolve here")
    lines.append(f"- Sample: **{total} of 120** queries — classes 4/5/6 at 100%, all others ceil(20%)")
    lines.append(f"- Seed: `{seed}` (= sha256(manifest.json)[:16]; deterministic, no RNG)")
    lines.append("- Reproduce: `python3 bench/gold_spotcheck.py` → identical sample + this worksheet")
    lines.append("- Machine-readable: `ruling-3-spot-check-sample.json` · spreadsheet: `ruling-3-spot-check-worksheet.csv`")
    lines.append("")
    lines.append("## How to judge one query")
    lines.append("")
    lines.append("1. **Spec points** — would a competent teacher accept every listed gold")
    lines.append("   SpecificationPoint as a correct anchor for this query? (missing obvious")
    lines.append("   anchors count as INCORRECT; note the missing codes)")
    lines.append("2. **Evidence tiers** — tier 2 = *directly answers* the query, tier 1 =")
    lines.append("   *legitimate supporting* evidence, tier 0 = not relevant. Each excerpt")
    lines.append("   below carries its paper code, kind, page and the leading content so the")
    lines.append("   tier can be judged without opening the snapshot; full text lives in")
    lines.append("   `snapshot/chunks.jsonl.gz` under the printed chunk ref.")
    lines.append("3. Mark **CORRECT** only if (1) and (2) both hold; otherwise INCORRECT with")
    lines.append("   corrected labels in the notes column (CSV carries a dedicated column).")
    lines.append("")
    lines.append("## Roster")
    lines.append("")
    lines.append("| # | Class | Sampled / Total | Rate |")
    lines.append("|---|-------|----------------:|------|")
    for class_name in CLASS_ORDER:
        no = CLASS_ORDER.index(class_name) + 1
        n, tot = len(sampled[class_name]), counts[class_name]
        rate = "100% (ruling 3)" if class_name in FULL_CLASSES else f"ceil(20%) = {n}/{tot}"
        lines.append(f"| {no} | {CLASS_LABELS[class_name]} | {n} / {tot} | {rate} |")
    lines.append(f"| | **Total** | **{total} / 120** | |")
    lines.append("")
    lines.append("## Review records")
    lines.append("")
    for class_name in CLASS_ORDER:
        no = CLASS_ORDER.index(class_name) + 1
        lines.append(f"### Class {no} — {CLASS_LABELS[class_name]} (`{class_name}`, "
                     f"{len(sampled[class_name])}/{counts[class_name]} sampled)")
        lines.append("")
        for r in sampled[class_name]:
            lines.append(f"#### `{r['id']}` — verdict: ☐ CORRECT ☐ INCORRECT")
            lines.append("")
            lines.append(f"> **Query:** {r['query']}")
            if r.get("gold_spec_points"):
                lines.append(f"> **Gold spec points:** {' · '.join(r['gold_spec_points'])}")
            if r.get("gold_concepts"):
                lines.append(f"> **Gold concepts:** {' · '.join(r['gold_concepts'])}")
            if r.get("gold_misconceptions"):
                lines.append(f"> **Gold misconceptions:** {' · '.join(r['gold_misconceptions'])}")
            lines.append(f"> **Provenance:** {provenance_text(r)} — substrate `{r.get('substrate','')}`")
            if r.get("notes"):
                lines.append(f"> **Generator notes:** {r['notes']}")
            lines.append("> **Notes:** ________________________________________________________")
            lines.append("")
            if r.get("gold_evidence"):
                lines.append("Gold evidence (tier → chunk):")
                lines.append("")
                for ev in r["gold_evidence"]:
                    c = chunk_index[ev["chunk_ref"]]
                    paper = c["paper_code"] or "—"
                    if c["page_start"] is None:
                        pages = "?"
                    elif str(c["page_start"]) == str(c["page_end"]):
                        pages = str(c["page_start"])
                    else:
                        pages = f"{c['page_start']}-{c['page_end']}"
                    lines.append(f"- **tier {ev['tier']}** (`{ev['rule']}`) → `{short_ref(ev['chunk_ref'])}` "
                                 f"· {paper} {c['kind']} p.{pages} · state {c['paper_state']}")
                    lines.append(f"  > {excerpt(c['content'])}")
            else:
                lines.append("_No gold evidence chunks for this record (spec-point-only anchor)._")
            lines.append("")
    lines.append("## Rollup (owner fills)")
    lines.append("")
    lines.append("| Class | CORRECT | Sampled | Precision | ≥90%? |")
    lines.append("|-------|--------:|--------:|----------:|-------|")
    for class_name in CLASS_ORDER:
        n = len(sampled[class_name])
        lines.append(f"| {CLASS_LABELS[class_name]} | | {n} | | ☐ |")
    lines.append("")
    lines.append("Any class below 0.90 → manual re-author of that class before the next")
    lines.append("recorded run (ruling 3). Record the outcome in TODO T-C13 + PROGRESS.")
    lines.append("")

    ws_path = OUT / "ruling-3-spot-check-worksheet.md"
    ws_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"SPOTCHECK OK: {total}/120 sampled (seed {seed})")
    for class_name in CLASS_ORDER:
        n = len(sampled[class_name])
        print(f"  class {CLASS_ORDER.index(class_name)+1:>2} {class_name:<18} {n:>2}/{counts[class_name]}")
    print(f"  sample  -> {sample_path.relative_to(REPO)}")
    print(f"  sheet   -> {csv_path.relative_to(REPO)}")
    print(f"  sheet   -> {ws_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
