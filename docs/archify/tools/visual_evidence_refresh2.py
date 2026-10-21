#!/usr/bin/env python3
"""Refresh-2 browser evidence (2026-10-21 v2-cutover refresh).

Companion to tools/visual_evidence_refresh.py: for each artifact, verifies via
the RENDERED DOM (Playwright, Chromium) that THIS refresh's new facts are
visible text — the syllabai-v2 re-pin, the books-rail component, the Neon/
drizzle posture, pipeline 1.3.0, the honest BM25/fabric not-ported note — plus
the same 4-viewport horizontal-containment proof, SHA-256-bound to the
committed post-QG bytes.

Writes refresh2-manual-browser-evidence.json next to this script.
"""
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent
VIEWPORTS = [(1440, 1000), (1600, 1000), (1920, 1080), (2048, 1200)]

NEEDLES = {
    "syllabai-architecture-overview.html": [
        "syllabai-v2 apps/api — API of record",       # api_core relabel
        "Books rail (interactive)",                    # NEW component
        "ADR-BOOK-0001 · blocks · glossary",           # books_rail sublabel
        "Neon PostgreSQL (production)",                # postgres relabel
        "cutover 2026-10-13",                          # api region label (T-C84)
        "Groq → Gemini 3.6 Flash → OpenRouter",        # llm_chain drift
        "syllabai-hub-v2.vercel.app",                  # hub-of-record card line
        "archived read-only, never deleted",           # cutover card line
        "karag.ts",                                    # tutor anchor (raw layer)
        "books.ts",                                    # books_rail anchor (raw)
        "0005_book-rail-tables.sql",                   # rail migration anchor (raw)
    ],
    "syllabai-learning-loop.html": [
        "syllabai-v2 apps/api — pinned at d07267a",    # region relabel
        "Learner surfaces moved into the pinned monorepo",  # status card
        "The legacy syllabai-web learner surface is retired",  # cross-repo card
        "submit.ts",                                   # evidence anchor (raw)
        "nba.ts",                                      # NBA anchor (raw)
        "struggle-inference.ts",                       # struggle anchor (raw)
    ],
    "syllabai-retrieval-architecture.html": [
        "Serving hybrid — KaRAG tutor + CLA (syllabai-v2 @ d07267a)",
        "NOT PORTED to syllabai-v2",                   # not-serving card honesty
        "No serving behavior was lost at the cutover", # not-serving card
        "shrank from 12 to 10 nodes",                  # sources card
        "T-C20 VALIDATED-only",                        # semantic leg sublabel
        "rrf.ts",                                      # fusion anchors (raw)
        "scope.ts",                                    # scope anchors (raw)
    ],
    "syllabai-assessment-marking.html": [
        "syllabai-v2 @ d07267a — marking fabric",      # region relabel
        "pipeline 1.3.0 · partial marks",              # smartmark drift
        "groq → gemini-3.6 → openrouter",              # llm chain drift
        "evidence once-guard (DECISION_016)",          # evidence sublabel
        "review-writes.ts",                            # scheme review anchor
        "cross-repo text-cited @ cae30ea",             # console card
        "teachermarking.ts",                           # route anchors (raw)
    ],
    "syllabai-ingestion-pipeline.html": [
        "syllabai-v2 @ d07267a — ingestion fabric",    # region relabel
        "the books band (ADR-BOOK-0001, migration 0005)",  # posture card
        "APPLY-READY of record (Session 207)",         # posture card
        "T-C20 keeps search VALIDATED-only",           # posture card
        "JSONB docs · chunks · checksum dedup",        # content_store sublabel
        "glm-ocr.ts",                                  # bridge anchors (raw)
        "concept-seed.ts",                             # seed anchors (raw)
    ],
}


def main():
    report = {
        "generated": "2026-10-21",
        "tool": Path(__file__).name,
        "note": (
            "Refresh-2 evidence: new-fact DOM presence + horizontal containment "
            "on the Quiet Green post-processed artifacts of the 2026-10-21 lane "
            "(re-pin to syllabai-v2 @ d07267ae3d57974c202bf2f4141b9a3ba00a8ee8). "
            "Visible-text facts checked in the rendered DOM; source-ref anchors "
            "live in the interactive SRC/search layer, so they are checked "
            "against the artifact bytes (same method as "
            "visual_evidence_refresh.py). Packaged browser-check attempted on "
            "post-QG bytes in tools/refresh2-browser-check/."
        ),
        "artifacts": {},
    }
    failed = False
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, needles in NEEDLES.items():
            path = DOCS / name
            entry = {"containment": {}, "needles": {}}
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.goto(path.as_uri())
            page.wait_for_timeout(600)
            body = page.inner_text("body")
            svg = page.evaluate("document.querySelector('svg')?.textContent ?? ''")
            rendered = f"{body}\n{svg}"
            raw = path.read_text(errors="replace")
            for n in needles:
                if n.endswith((".ts", ".sql")):
                    entry["needles"][n] = n in raw
                else:
                    entry["needles"][n] = (n in body) or (n in svg)
            for w, h in VIEWPORTS:
                page.set_viewport_size({"width": w, "height": h})
                page.wait_for_timeout(150)
                overflow = page.evaluate(
                    "document.documentElement.scrollWidth - window.innerWidth"
                )
                entry["containment"][f"{w}x{h}"] = overflow <= 0
            entry["ok"] = (
                all(entry["needles"].values()) and all(entry["containment"].values())
            )
            entry["html_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            report["artifacts"][name] = entry
            failed = failed or not entry["ok"]
            page.close()
        browser.close()
    out = HERE / "refresh2-manual-browser-evidence.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    for name, e in report["artifacts"].items():
        missing = [k for k, v in e["needles"].items() if not v]
        print(f"{name}: {'PASS' if e['ok'] else 'FAIL'}"
              + (f" missing={missing}" if missing else ""))
    raise SystemExit(1 if failed else 0)


main()
