#!/usr/bin/env python3
"""Manual browser evidence for the Quiet Green restyle of the archify diagrams.

Per artifact x theme (light, dark):
  - horizontal containment EXACT at 1440/1600/1920/2048;
  - cascade proof: the Quiet Green override layer wins (token + font computed checks);
  - needle labels (taken from the artifact's own IR components) present in the DOM;
  - first-viewport screenshot (1440x1000) committed alongside.
Plus one full-page capture (learning loop, both themes) showing the card flow.

Writes quiet-green-manual-browser-evidence.json next to this script.
Offline note: Google Fonts may not load in the sandbox; the declared stacks are
still verified via getComputedStyle (fonts fall back per the design system).
"""

import html as html_mod
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent
EVID = HERE / "quiet-green-evidence"
EVID.mkdir(exist_ok=True)

ARTIFACTS = [
    "syllabai-architecture-overview.html",
    "syllabai-learning-loop.html",
    "syllabai-retrieval-architecture.html",
    "syllabai-assessment-marking.html",
    "syllabai-ingestion-pipeline.html",
]

VIEWPORTS = [(1440, 1000), (1600, 1000), (1920, 1080), (2048, 1200)]
EXPECT_BG = {"light": "rgb(245, 245, 242)", "dark": "rgb(23, 24, 27)"}
EXPECT_TOKEN = {"light": "#2e6b4f", "dark": "#55b285"}  # --backend-stroke (fern)

TOKEN_PROOF_JS = """(theme) => {
  const root = document.documentElement;
  const cs = getComputedStyle(root);
  const bodyCS = getComputedStyle(document.body);
  const h1 = document.querySelector('h1');
  const svgText = document.querySelector('svg text');
  return {
    bg: bodyCSS_bg(bodyCS),
    backend_stroke: cs.getPropertyValue('--backend-stroke').trim(),
    panel_border: cs.getPropertyValue('--panel-border').trim(),
    security_stroke: cs.getPropertyValue('--security-stroke').trim(),
    body_font: bodyCS.fontFamily,
    h1_font: h1 ? getComputedStyle(h1).fontFamily : null,
    svg_font: svgText ? getComputedStyle(svgText).fontFamily : null,
    instrument_loaded: document.fonts ? document.fonts.check("16px 'Instrument Sans'") : null,
    bricolage_loaded: document.fonts ? document.fonts.check("16px 'Bricolage Grotesque'") : null,
  };
  function bodyCSS_bg(cs) { return cs.backgroundColor; }
}"""


def needles_for(name):
    ir = json.loads((DOCS / (name.replace(".html", ".archify.json"))).read_text())
    labels = [c["label"] for c in ir["components"] if c.get("label")]
    return labels[:7]


def main():
    report = {"generated": "2026-09-22", "tool": Path(__file__).name, "artifacts": {}}
    failed = False
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name in ARTIFACTS:
            entry = {"containment": {}, "themes": {}, "needles": {}, "screenshots": []}
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.goto((DOCS / name).as_uri())
            page.wait_for_timeout(400)
            needles = needles_for(name)
            content = html_mod.unescape(page.content())
            for n in needles:
                entry["needles"][n] = n in content
            for theme in ("light", "dark"):
                page.evaluate(
                    "t => document.documentElement.setAttribute('data-theme', t)", theme
                )
                page.wait_for_timeout(250)
                cont = {}
                for w, h in VIEWPORTS:
                    page.set_viewport_size({"width": w, "height": h})
                    page.wait_for_timeout(120)
                    cont[f"{w}x{h}"] = page.evaluate(
                        "document.documentElement.scrollWidth <= window.innerWidth"
                    )
                entry["containment"][theme] = cont
                proof = page.evaluate(TOKEN_PROOF_JS, theme)
                proof["bg_ok"] = proof["bg"] == EXPECT_BG[theme]
                proof["fern_ok"] = proof["backend_stroke"] == EXPECT_TOKEN[theme]
                proof["sans_declared"] = "Instrument Sans" in (proof["body_font"] or "")
                proof["display_declared"] = "Bricolage Grotesque" in (proof["h1_font"] or "")
                proof["mono_svg_declared"] = "Spline Sans Mono" in (proof["svg_font"] or "")
                entry["themes"][theme] = proof
                shot = EVID / f"{name.replace('.html', '')}.{theme}.1440.png"
                page.set_viewport_size({"width": 1440, "height": 1000})
                page.wait_for_timeout(200)
                page.screenshot(path=str(shot))
                entry["screenshots"].append(shot.name)
            page.close()
            # full-page card flow for one artifact
            if name == "syllabai-learning-loop.html":
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.goto((DOCS / name).as_uri())
                page.wait_for_timeout(400)
                for theme in ("light", "dark"):
                    page.evaluate(
                        "t => document.documentElement.setAttribute('data-theme', t)", theme
                    )
                    page.wait_for_timeout(250)
                    shot = EVID / f"{name.replace('.html', '')}.{theme}.full.png"
                    page.screenshot(path=str(shot), full_page=True)
                    entry["screenshots"].append(shot.name)
                page.close()
            ok = all(all(v.values()) for v in entry["containment"].values())
            ok = ok and all(t["bg_ok"] and t["fern_ok"] and t["sans_declared"]
                            and t["display_declared"] and t["mono_svg_declared"]
                            for t in entry["themes"].values())
            ok = ok and all(entry["needles"].values())
            entry["PASS"] = ok
            failed = failed or not ok
            report["artifacts"][name] = entry
            print(f"{name}: {'PASS' if ok else 'FAIL'} "
                  f"(containment {'ok' if all(all(v.values()) for v in entry['containment'].values()) else 'FAIL'}, "
                  f"cascade {'ok' if all(t['bg_ok'] and t['fern_ok'] for t in entry['themes'].values()) else 'FAIL'}, "
                  f"needles {sum(entry['needles'].values())}/{len(entry['needles'])})")
        browser.close()
    (HERE / "quiet-green-manual-browser-evidence.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
