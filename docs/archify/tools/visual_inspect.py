"""Manual browser evidence for the delivered Archify HTML (T-ARCHIFY).
Measures viewport containment and captures screenshots at canonical desktop sizes.
Complements (does not replace) archify visual-check, which cannot complete here.
"""
import json
from playwright.sync_api import sync_playwright

ARTIFACT = "/home/z/my-project/repos/syllabai/docs/archify/syllabai-architecture-overview.html"
OUT = "/home/z/my-project/scripts/t-archify"
CHROME = "/home/z/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"
VIEWPORTS = [(1440, 900), (1600, 1000), (1920, 1080)]

results = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--disable-dev-shm-usage"])
    for w, h in VIEWPORTS:
        page = browser.new_page(viewport={"width": w, "height": h})
        page.goto(f"file://{ARTIFACT}", wait_until="load", timeout=60000)
        page.wait_for_timeout(2500)  # let the viewer runtime settle
        metrics = page.evaluate(
            """() => ({
                scrollWidth: document.documentElement.scrollWidth,
                scrollHeight: document.documentElement.scrollHeight,
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                title: document.title,
                svgCount: document.querySelectorAll('svg').length,
                nodeTexts: document.querySelectorAll('svg text').length,
                hasHScroll: document.documentElement.scrollWidth > window.innerWidth,
                hasVScroll: document.documentElement.scrollHeight > window.innerHeight,
            })"""
        )
        metrics["viewport"] = f"{w}x{h}"
        metrics["containmentOk"] = (not metrics["hasHScroll"]) and (not metrics["hasVScroll"])
        page.screenshot(path=f"{OUT}/shot-{w}x{h}.png", full_page=False)
        results.append(metrics)
        page.close()
    browser.close()

print(json.dumps(results, indent=1))
with open(f"{OUT}/manual-browser-evidence.json", "w") as f:
    json.dump(results, f, indent=1)
