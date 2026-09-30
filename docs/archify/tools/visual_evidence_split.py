#!/usr/bin/env python3
"""Supplementary manual browser evidence for the two split Archify diagrams.

Replaces the environmentally-blocked `archify visual-check` (Chrome DevTools
Runtime.evaluate 15s timeout — known sandbox issue, recorded in
T-ARCHIFY-EVIDENCE-REPORT.md). Collects:
  - viewport containment at 1440x900, 1600x1000, 1920x1080, 2048x1320
    (scrollWidth <= innerWidth and scrollHeight <= innerHeight)
  - full-page screenshots at 1440x900 and 1920x1080 for perceptual review
  - node/region/tag spot counts from the live DOM (svg text search)
Writes JSON evidence to download/archify-split-visual-evidence.json
and PNGs to download/archify-shots/.
"""
import json
import os
from playwright.sync_api import sync_playwright

BASE = "/home/z/my-project/repos/syllabai/docs/archify"
OUT_JSON = "/home/z/my-project/download/archify-split-visual-evidence.json"
SHOT_DIR = "/home/z/my-project/download/archify-shots"
VIEWPORTS = [(1440, 900), (1600, 1000), (1920, 1080), (2048, 1320)]

DIAGRAMS = [
    ("learning-loop", os.path.join(BASE, "syllabai-learning-loop.html"),
     ["Learning Loop (source-backed)", "assess", "agreement gate", "learner model",
      "Struggle", "Remediation", "NBA", "Next learning action", "Curriculum & specification",
      "human marks", "IMPLEMENTED"]),
    ("retrieval", os.path.join(BASE, "syllabai-retrieval-architecture.html"),
     ["Retrieval & Grounded AI (source-backed)", "Curriculum resolution", "Authoritative KG",
      "Semantic vector leg", "Rank fusion", "Reranking", "Evidence selection",
      "Evidence sufficiency", "Grounded AI", "Citation validation", "BM25", "Multi-arm fabric"]),
]

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
            entry["containment"].append(
                {"viewport": f"{w}x{h}", "ok": ok, **m}
            )
            if (w, h) in [(1440, 900), (1920, 1080)]:
                shot = os.path.join(SHOT_DIR, f"{name}-{w}x{h}.png")
                page.screenshot(path=shot, full_page=True)
                entry["shots"].append(shot)
        # DOM spot checks at 1440x900: page text contains key labels
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
            "view_buttons": [v for v in ["Main loop", "Gated release", "Truth anchors",
                                         "Serving path", "Grounding & provenance",
                                         "Prepared arms", "Prepared arms"] if v in body],
        }
        results[name] = entry
        page.close()
    browser.close()

with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=2)

for name, entry in results.items():
    all_ok = all(c["ok"] for c in entry["containment"])
    needles_ok = all(entry["dom_checks"]["needles_found"].values())
    print(f"{name}: containment={'PASS' if all_ok else 'FAIL'} "
          f"needles={'PASS' if needles_ok else 'MISSING: ' + str([k for k, v in entry['dom_checks']['needles_found'].items() if not v])} "
          f"shots={len(entry['shots'])}")
print(f"JSON -> {OUT_JSON}")
