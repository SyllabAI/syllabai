#!/usr/bin/env python3
"""Supplementary manual browser evidence for round 2 of the Archify split:
assessment-marking + ingestion-pipeline diagrams.

Same contract as tools/visual_evidence_split.py: the packaged
`archify visual-check` is environmentally blocked in this sandbox (Chrome
DevTools Runtime.evaluate 15s timeout — recorded in the evidence reports).
This substitute collects:
  - viewport containment at 1440x900, 1600x1000, 1920x1080, 2048x1320
  - full-page screenshots at 1440x900 and 1920x1080 for perceptual review
  - node/region/tag spot counts from the live DOM (svg text search)
Writes JSON to download/archify-split2-visual-evidence.json and PNGs to
download/archify-shots2/.
"""
import json
import os
from playwright.sync_api import sync_playwright

BASE = "/home/z/my-project/repos/syllabai/docs/archify"
OUT_JSON = "/home/z/my-project/download/archify-split2-visual-evidence.json"
SHOT_DIR = "/home/z/my-project/download/archify-shots2"
VIEWPORTS = [(1440, 900), (1600, 1000), (1920, 1080), (2048, 1320)]

DIAGRAMS = [
    ("assessment-marking", os.path.join(BASE, "syllabai-assessment-marking.html"),
     ["Assessment & Marking (source-backed)", "Teacher marking API", "Marking queue service",
      "Smart Mark engine", "LLM failover chain", "Authoritative human marks",
      "agreement gate", "Smart Mark release", "Learning evidence",
      "Teacher content review", "Question bank", "SME package ingest",
      "pilot-scope", "VALIDATED-only"]),
    ("ingestion-pipeline", os.path.join(BASE, "syllabai-ingestion-pipeline.html"),
     ["Ingestion & Content Pipeline (source-backed)", "Past-papers corpus",
      "syllabai-parser", "GlmOcr bridge", "Curriculum bridge", "Paper ingestion",
      "Question bank", "Educational KG", "Curriculum truth", "SME package ingest",
      "Teacher content review", "Content corpus", "pgvector semantic lane",
      "ingestion paused", "PREPARED"]),
]

VIEW_BUTTONS = {
    "assessment-marking": ["Human marking flow", "Smart Mark & κ gate",
                            "Scheme validation", "Release rules"],
    "ingestion-pipeline": ["Main ingest flow", "Canonical truth",
                            "Validation & promotion", "Paused lane"],
}

os.makedirs(SHOT_DIR, exist_ok=True)
results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    for name, path, needles in DIAGRAMS:
        page = browser.new_page()
        entry = {"containment": [], "dom_checks": {}, "shots": []}
        for w, h in VIEWPORTS:
            page.set_viewport_size({"width": w, "height": h})
            page.goto(f"file://{path}")
            page.wait_for_timeout(600)
            m = page.evaluate(
                "() => ({sw: document.documentElement.scrollWidth,"
                " iw: window.innerWidth,"
                " sh: document.documentElement.scrollHeight,"
                " ih: window.innerHeight})"
            )
            ok = m["sw"] <= m["iw"] and m["sh"] <= m["ih"]
            entry["containment"].append({"viewport": f"{w}x{h}", "ok": ok, **m})
            if (w, h) in [(1440, 900), (1920, 1080)]:
                shot = os.path.join(SHOT_DIR, f"{name}-{w}x{h}.png")
                page.screenshot(path=shot, full_page=True)
                entry["shots"].append(shot)
        page.set_viewport_size({"width": 1440, "height": 900})
        page.goto(f"file://{path}")
        page.wait_for_timeout(600)
        body = page.evaluate("() => document.body.innerText")
        svg_texts = page.evaluate(
            "() => Array.from(document.querySelectorAll('svg text')).map(t => t.textContent.trim())"
        )
        joined = " ".join(svg_texts)
        entry["dom_checks"] = {
            "svg_text_count": len(svg_texts),
            "needles_found": {n: (n in joined) or (n in body) for n in needles},
            "view_buttons": [v for v in VIEW_BUTTONS[name] if v in body],
        }
        results[name] = entry
        page.close()
    browser.close()

with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=2)

for name, entry in results.items():
    all_ok = all(c["ok"] for c in entry["containment"])
    missing = [k for k, v in entry["dom_checks"]["needles_found"].items() if not v]
    needles_ok = not missing
    print(f"{name}: containment={'PASS' if all_ok else 'FAIL'} "
          f"needles={'PASS' if needles_ok else 'MISSING: ' + str(missing)} "
          f"views={entry['dom_checks']['view_buttons']} shots={len(entry['shots'])}")
print(f"JSON -> {OUT_JSON}")
