#!/usr/bin/env python3
"""Refresh-specific browser evidence (2026-10-02 archify refresh, trace 1a0f8e77cd478f29).

Companion to tools/visual_evidence_quiet_green.py: for each artifact, verifies via
the RENDERED DOM (Playwright, Chromium) that the refresh's new facts are actually
visible text — the pin bump, the κ-gate live-state honesty, the new component
facts — plus the same 4-viewport horizontal-containment proof.

Writes refresh-manual-browser-evidence.json next to this script.
"""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent
VIEWPORTS = [(1440, 1000), (1600, 1000), (1920, 1080), (2048, 1200)]

NEEDLES = {
    "syllabai-architecture-overview.html": [
        "rate-limited",                       # api_core sublabel (security wave)
        "RateLimitFilter.java",           # api_core new source anchor
        "IMPLEMENTED · fail-closed",          # kappa_gate tag (was: gate closed)
        "κ=1.0 (n=113, threshold 0.60) — PASSED",  # gates card: G-4 closed
        "deep-audit 09-28",                   # security hardening line
        "SyllabAI/syllabai @ f1a7eb2 (main)", # cross-repo self pin refresh
        "serving rev2",                        # pgvector lane tag/sublabel
            ],
    "syllabai-learning-loop.html": [
        "pinned at 9385011",                  # region label
        "IMPLEMENTED · fail-closed",          # kappa_gate tag
        "κ=1.0 (n=113, threshold 0.60) — PASSED",  # kappa card: G-4 closed
        "unvouchable row (n=25 calibration)", # agent calibration superseded
    ],
    "syllabai-retrieval-architecture.html": [
        "pinned at 9385011",                  # region label
        "PaperQuestionResolver.java",     # query_intent new source anchor
        "empty / unanchored ⇒ refusal",       # sufficiency sublabel (both classes)
        "KaRagService.java",             # sufficiency guard+gate anchor
        "RRF k=60 · per-kind weights",        # fusion sublabel
        "briefs + session memory",            # selection sublabel
        "ContextAssembler.java",          # assembler briefs anchor
        "fail-open guard",                    # truth-boundaries card (D2 text)
        "cross-session episodic digest (s140)",     # truth-boundaries card
        "CURRENT_EMBED_REV=2 on the validated corpus",  # not-serving card rev state
        "per-course · fail-closed (T-C07)",   # scope sublabel (ADR-030)
        "KaRagService.java:25-26",            # sources card contract lines
    ],
    "syllabai-assessment-marking.html": [
        "@ 9385011",                          # region label
        "pipeline 1.2.1 · partial marks",     # smartmark sublabel
        "SmartMarkResult.java",           # pipeline version anchor
        "TeacherMarkingQueueService.java",  # G-5 pagination anchor
        "TRUNCATED_OUTPUT",                   # V34 refusal-family line
        "κ=1.0 (n=113, threshold 0.60) PASSED",  # V34 card: G-4 closed
        "any-credit convention pinned in core e7a55fe",  # V34 card
    ],
    "syllabai-ingestion-pipeline.html": [
        "@ 9385011",                          # region label
        "ContentDocumentController.java",   # /embed anchor
        "Embedding v2 wait is resolved",      # paused card rev2 state
        "SmeQuestionIngestService.java",    # QuestionSpecPoint anchor
    ],
}


def main():
    report = {
        "generated": "2026-10-02",
        "tool": Path(__file__).name,
        "note": (
            "Refresh evidence: new-fact DOM presence + horizontal containment on the "
            "Quiet Green post-processed committed artifacts. QG cascade + needle "
            "evidence: quiet-green-manual-browser-evidence.json (5/5 PASS, same run "
            "shape). Packaged browser-check: environmentally unavailable (DevTools "
            "Runtime.evaluate 15000 ms timeout, recorded per artifact in "
            "tools/qg-browser-check/)."
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
                # visible-text facts are checked in the rendered DOM; source-ref
                # anchors live in the interactive SRC/search layer, so they are
                # checked against the artifact bytes (same method as the
                # committed visual_evidence_quiet_green.py needle check)
                if n.endswith(".java"):
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
            entry["html_sha256"] = __import__("hashlib").sha256(path.read_bytes()).hexdigest()
            report["artifacts"][name] = entry
            failed = failed or not entry["ok"]
            page.close()
        browser.close()
    out = HERE / "refresh-manual-browser-evidence.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    for name, e in report["artifacts"].items():
        missing = [k for k, v in e["needles"].items() if not v]
        print(f"{name}: {'PASS' if e['ok'] else 'FAIL'}"
              + (f" missing={missing}" if missing else ""))
    raise SystemExit(1 if failed else 0)


main()
