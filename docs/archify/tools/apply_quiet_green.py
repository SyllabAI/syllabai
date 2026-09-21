#!/usr/bin/env python3
"""Apply the Open Notebook "Quiet Green" design system to Archify-delivered diagram HTML.

Deterministic, idempotent post-processor. For each target artifact it injects:

  1. a Google Fonts <link> block (Instrument Sans / Bricolage Grotesque / Spline Sans Mono)
     with the design system's fallback stacks (offline use falls back gracefully, and the
     template's embedded JetBrains Mono remains the deepest mono fallback);
  2. a single <style id="quiet-green-theme"> override layer immediately before </head>:
       - the full Archify token vocabulary remapped onto Quiet Green for BOTH
         [data-theme="dark"] and [data-theme="light"] (surfaces, ink, hairlines, lanes,
         arrows, all node-kind stroke/fill pairs, toolbar chrome);
       - chrome geometry (squared 4-6px radii), depth (hairline + one popover shadow),
         typography (sans body, display titles, mono data; SVG interior stays mono),
         and the teal focus ring.

Kind -> hue mapping (Quiet Green laws, "fern acts / teal speaks / red destroys"):

  backend   -> fern   #2e6b4f / #55b285   the system acting (serving components)
  frontend  -> sage   #5e7a54 / #93b084   web surfaces
  database  -> plum   #5d4991 / #a290d3   knowledge / canonical stores
  cloud     -> teal   #0e7268 / #3fb3a5   AI voice (LLM providers)
  messagebus-> gold   #a97b12 / #cfa13e   recorded events (evidence signals)
  external  -> slate  #4e6b84 / #8fafc8   external / paper sources
  security  -> danger #b0432d / #df7c63   fail-closed gates (red destroys, only destroys)

Re-running after a fresh `archify deliver` re-applies cleanly (previous layer replaced
by marker). Never hand-edit delivered HTML: deliver -> re-apply this tool.

Usage: python3 apply_quiet_green.py [file.html ...]   (default: the five diagrams here)
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_TARGETS = [
    HERE.parent / "syllabai-architecture-overview.html",
    HERE.parent / "syllabai-learning-loop.html",
    HERE.parent / "syllabai-retrieval-architecture.html",
    HERE.parent / "syllabai-assessment-marking.html",
    HERE.parent / "syllabai-ingestion-pipeline.html",
]

MARK_BEGIN = "<!-- quiet-green-theme:BEGIN (applied by tools/apply_quiet_green.py) -->"
MARK_END = "<!-- quiet-green-theme:END -->"

FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&amp;family=Bricolage+Grotesque:wght@600;700&amp;family=Spline+Sans+Mono&amp;display=swap">\n'
    '  <!-- Offline: fonts fall back per the Quiet Green stacks; embedded JetBrains Mono remains the mono fallback -->'
)

MONO_STACK = "'Spline Sans Mono', 'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
SANS_STACK = "'Instrument Sans', 'Helvetica Neue', Arial, 'Noto Sans SC', sans-serif"
DISPLAY_STACK = "'Bricolage Grotesque', 'Avenir Next', 'Trebuchet MS', sans-serif"

CSS = """<style id="quiet-green-theme">
/* ==========================================================================
   OPEN NOTEBOOK — "Quiet Green" design system x SyllabAI archify artifacts
   Applied by docs/archify/tools/apply_quiet_green.py (deterministic, re-runnable)
   Laws: fern acts / teal speaks / red destroys, and only destroys / warn is clay /
   color never washes a reading surface / hairlines separate, not shadows /
   geometry is squared, 4-6px / mono is for data, not prose.
   Only raw tokens are overridden per theme; components re-resolve via var().
   ========================================================================== */

:root,
[data-theme="dark"] {
  /* surfaces — the neutral ladder (dark) */
  --bg: #17181b;
  --grid: #26282d;
  --mask: #1e2024;
  --panel: #1e2024;
  --panel-border: #2e3036;
  --lane-fill: rgba(18, 19, 22, 0.55);
  --lane-stroke: #34363d;

  /* ink — 4-step ramp (dark) */
  --text: #ecedea;
  --text-muted: #a9acb1;
  --text-dim: #74777d;
  --text-faint: #74777d;

  /* arrows */
  --arrow: #74777d;
  --arrow-emphasis: #55b285; /* fern: emphasis is the acting flow */

  /* node kinds -> owned hues (fills are dark washed panels; strokes are lightened bases) */
  --frontend-fill: rgba(35, 43, 29, 0.55);
  --frontend-stroke: #93b084;   /* sage — web surfaces */
  --backend-fill: rgba(27, 47, 37, 0.55);
  --backend-stroke: #55b285;    /* fern — the system acting */
  --database-fill: rgba(41, 37, 58, 0.60);
  --database-stroke: #a290d3;   /* plum — canonical stores */
  --cloud-fill: rgba(22, 48, 44, 0.60);
  --cloud-stroke: #3fb3a5;      /* teal — AI voice */
  --messagebus-fill: rgba(50, 43, 27, 0.60);
  --messagebus-stroke: #cfa13e; /* gold — recorded events */
  --external-fill: rgba(33, 43, 52, 0.60);
  --external-stroke: #8fafc8;   /* slate — external / paper */
  --security-fill: rgba(55, 35, 29, 0.60);
  --security-stroke: #df7c63;   /* danger — fail-closed gates */

  /* toolbar chrome */
  --toolbar-bg: rgba(30, 32, 36, 0.92);
  --toolbar-border: #2e3036;
  --toolbar-text: #ecedea;
  --toolbar-hover: #2b2d33;
  --toolbar-menu-bg: #24262b;

  /* Quiet Green extras (shadows + focus ring) */
  --qg-shadow-soft: 0 1px 2px rgba(0, 0, 0, 0.35);
  --qg-shadow-lift: 0 1px 3px rgba(0, 0, 0, 0.45);
  --qg-shadow-pop: 0 1px 2px rgba(0, 0, 0, 0.45), 0 10px 30px rgba(0, 0, 0, 0.5);
  --qg-shadow-overlay: 0 2px 6px rgba(0, 0, 0, 0.4), 0 20px 52px rgba(0, 0, 0, 0.55);
  --qg-ring: #3fb3a5;

  color-scheme: dark;
}

[data-theme="light"] {
  /* surfaces — the neutral ladder (light) */
  --bg: #f5f5f2;
  --grid: #e8e8e2;
  --mask: #fefefc;
  --panel: #fefefc;
  --panel-border: #e0e0da;
  --lane-fill: rgba(238, 238, 233, 0.65);
  --lane-stroke: #d6d6cd;

  /* ink — 4-step ramp (light) */
  --text: #23252a;
  --text-muted: #565a61;
  --text-dim: #878b92;
  --text-faint: #878b92;

  /* arrows */
  --arrow: #878b92;
  --arrow-emphasis: #2e6b4f; /* fern */

  /* node kinds -> owned hues (fills: base at chip-wash alpha; strokes: base) */
  --frontend-fill: rgba(94, 122, 84, 0.13);
  --frontend-stroke: #5e7a54;   /* sage */
  --backend-fill: rgba(46, 107, 79, 0.13);
  --backend-stroke: #2e6b4f;    /* fern */
  --database-fill: rgba(93, 73, 145, 0.13);
  --database-stroke: #5d4991;   /* plum */
  --cloud-fill: rgba(14, 114, 104, 0.12);
  --cloud-stroke: #0e7268;      /* teal */
  --messagebus-fill: rgba(169, 123, 18, 0.13);
  --messagebus-stroke: #a97b12; /* gold */
  --external-fill: rgba(78, 107, 132, 0.13);
  --external-stroke: #4e6b84;   /* slate */
  --security-fill: rgba(176, 67, 45, 0.11);
  --security-stroke: #b0432d;   /* danger */

  /* toolbar chrome */
  --toolbar-bg: rgba(255, 255, 255, 0.92);
  --toolbar-border: #e0e0da;
  --toolbar-text: #23252a;
  --toolbar-hover: #ecece7;
  --toolbar-menu-bg: #ffffff;

  /* Quiet Green extras */
  --qg-shadow-soft: 0 1px 2px rgba(35, 37, 42, 0.06);
  --qg-shadow-lift: 0 1px 3px rgba(35, 37, 42, 0.1);
  --qg-shadow-pop: 0 1px 2px rgba(35, 37, 42, 0.08), 0 8px 26px rgba(35, 37, 42, 0.13);
  --qg-shadow-overlay: 0 2px 6px rgba(35, 37, 42, 0.1), 0 16px 44px rgba(35, 37, 42, 0.18);
  --qg-ring: #0e7268;

  color-scheme: light;
}

/* ---- typography: sans body, display titles, mono data (never prose) ---- */
body {
  font-family: @@SANS@@;
}
h1 {
  font-family: @@DISPLAY@@;
  font-weight: 700;
  letter-spacing: -0.025em;
}
.card h3 {
  font-family: @@DISPLAY@@;
  font-weight: 600;
  letter-spacing: -0.01em;
}
/* diagram interior stays data-mono: node labels, sublabels, file:line citations */
svg text,
svg tspan {
  font-family: @@MONO@@;
}
/* data chrome: kbd, counts, indexes, meta rows */
.export-menu-header kbd, .guided-view-meta, .guided-view-index, .guided-story-caption-index,
.share-chapter-count, .share-chapter-index, .node-finder-status {
  font-family: @@MONO@@;
}

/* ---- geometry: squared, 4-6px, floor 4 (chips 4 / controls+cards 5 / panels 6) ---- */
.diagram-container { border-radius: 6px; }
.card { border-radius: 5px; }
.toolbar { border-radius: 5px; }
.toolbar button { border-radius: 4px; }
.guided-views { border-radius: 5px; }
.guided-view-chapter, .guided-view-stop, .guided-view-beat-link, .guided-view-actions button { border-radius: 4px; }
.node-finder-search { border-radius: 5px; }
.node-finder-results button, .overview-map-surface, .focus-chip { border-radius: 4px; }
.overview-map { border-radius: 6px; }
.archify-toast { border-radius: 5px; }

/* ---- depth: anchored = hairline + soft; floating = one real popover shadow ---- */
.diagram-container { box-shadow: var(--qg-shadow-soft); }
.card { box-shadow: none; }
.toolbar .preset-menu, .toolbar .export-menu, .node-finder, .relationship-lens,
.focus-chip, .archify-toast { box-shadow: var(--qg-shadow-pop); }
.overview-map { box-shadow: var(--qg-shadow-overlay); }

/* ---- the universal teal focus ring ---- */
button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible,
a:focus-visible, [role="button"]:focus-visible, [tabindex]:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--qg-ring) 50%, transparent);
}
</style>""".replace("@@SANS@@", SANS_STACK).replace("@@DISPLAY@@", DISPLAY_STACK).replace("@@MONO@@", MONO_STACK)


def transform(html: str, name: str) -> str:
    if MARK_BEGIN in html and MARK_END in html:
        html = re.sub(re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END), "__QG_SLOT__", html, flags=re.S)
        html = html.replace("__QG_SLOT__", MARK_BEGIN + "\n" + FONT_LINK + "\n" + CSS + "\n" + MARK_END)
        reapplied = True
    else:
        if 'id="quiet-green-theme"' in html or "fonts.googleapis.com/css2?family=Instrument+Sans" in html:
            raise SystemExit(f"{name}: found quiet-green traces but no markers; refusing to guess")
        if html.count("</head>") != 1:
            raise SystemExit(f"{name}: expected exactly one </head>")
        # BOTH the font link and the style live inside the marker span so that
        # re-application is a clean, byte-stable replacement.
        html = html.replace(
            "</head>",
            MARK_BEGIN + "\n" + FONT_LINK + "\n" + CSS + "\n" + MARK_END + "\n</head>",
            1,
        )
        reapplied = False
    return html, reapplied


def main(argv):
    targets = [Path(a) for a in argv[1:]] or DEFAULT_TARGETS
    for path in targets:
        if not path.exists():
            raise SystemExit(f"missing target: {path}")
        original = path.read_text(encoding="utf-8")
        html, reapplied = transform(original, path.name)
        # verification: markers once, both theme blocks present, structure intact
        assert html.count(MARK_BEGIN) == 1 and html.count(MARK_END) == 1, path
        assert 'data-theme="light"' in html and 'data-theme="dark"' in html, path
        assert html.rstrip().endswith("</html>"), path
        assert html.count("</head>") == 1, path
        path.write_text(html, encoding="utf-8", newline="")
        print(f"{path.name}: {'re-applied' if reapplied else 'applied'} "
              f"({len(original):,} -> {len(html.encode('utf-8')):,} bytes)")
    print(f"done: {len(targets)} artifact(s)")


if __name__ == "__main__":
    main(sys.argv)
