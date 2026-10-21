#!/usr/bin/env python3
"""Refresh-2 screenshot capture (2026-10-21 lane).

12 committed screenshots, mirroring the Quiet Green evidence shape:
5 artifacts x (first-viewport light) + (first-viewport dark) + (full-page dark
for the overview + one alternate full-page light) -> written to
tools/refresh2-evidence/*.png and indexed in refresh2-screenshots.json.
"""
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent
OUT = HERE / "refresh2-evidence"
OUT.mkdir(exist_ok=True)

ARTIFACTS = [
    "syllabai-architecture-overview.html",
    "syllabai-learning-loop.html",
    "syllabai-retrieval-architecture.html",
    "syllabai-assessment-marking.html",
    "syllabai-ingestion-pipeline.html",
]


def main():
    index = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        for name in ARTIFACTS:
            stem = Path(name).stem
            path = DOCS / name
            page.goto(path.as_uri())
            page.wait_for_timeout(600)
            shots = []
            for theme in ("light", "dark"):
                page.evaluate(
                    "t => document.documentElement.setAttribute('data-theme', t)",
                    theme,
                )
                page.wait_for_timeout(200)
                shot = OUT / f"{stem}.first-viewport.{theme}.png"
                page.screenshot(path=str(shot))
                shots.append(shot.name)
            # one full-page capture (dark) as the vertical-scroll record
            page.evaluate(
                "t => document.documentElement.setAttribute('data-theme', t)",
                "dark",
            )
            page.wait_for_timeout(200)
            shot = OUT / f"{stem}.full-page.dark.png"
            page.screenshot(path=str(shot), full_page=True)
            shots.append(shot.name)
            index[name] = {
                "screenshots": shots,
                "html_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            print(f"{name}: {len(shots)} screenshots")
        browser.close()
    (HERE / "refresh2-screenshots.json").write_text(json.dumps(index, indent=2) + "\n")
    print(f"total: {sum(len(v['screenshots']) for v in index.values())} PNGs")


main()
