# T-ARCHIFY — Quiet Green design-system restyle — evidence report

**Date:** 2026-09-22
**Task:** Apply the operator-supplied Open Notebook "Quiet Green" design system
(`open-notebook-design-system.md`, extracted from `lfnovo/open-notebook` v1.14)
to the five Archify-delivered diagram artifacts — **both light and dark themes**.
**Artifacts:** `syllabai-architecture-overview.html`, `syllabai-learning-loop.html`,
`syllabai-retrieval-architecture.html`, `syllabai-assessment-marking.html`,
`syllabai-ingestion-pipeline.html` (all `data-preset="classic"`).

---

## 1. Why a post-processor, not hand edits or IR changes

The Archify IR schema (v2.17) exposes **no palette/theme vocabulary** — only
`visualPreset` (`classic`/`signal-flow`/`blueprint`/`editorial`), component
`type`, edge `variant`, and legend dot enums. A design-system pass therefore
cannot be expressed in the IR. Per the repo rule "never hand-edit the delivered
HTML" (ARCHIFY_INTEGRATION.md §3 rule 5), the restyle is applied by a
**committed, deterministic, idempotent post-processor**:
`tools/apply_quiet_green.py`. The regeneration pipeline for every diagram is now:

```text
archify deliver (pristine HTML)  →  tools/apply_quiet_green.py  →  committed artifact
```

Re-running the tool after a fresh `archify deliver` re-applies cleanly; the
injected layer sits between marker comments (`quiet-green-theme:BEGIN/END`) and
re-application is a byte-stable replacement (verified). No other byte of the
generated artifacts was touched.

## 2. What the design system maps onto

Archify's delivered HTML is fully token-driven: `[data-theme="dark|light"]` on
`<html>` carries ~30 CSS custom properties consumed by both the HTML chrome and
the SVG (via `color-mix` and `.t-*` fill classes). The override layer remaps
**only raw tokens per theme** (the Quiet Green dark-mode architecture, §9 of the
design system: tints become dark washed panels, bases lighten — nothing else
re-declared). Mapping decisions follow the design system's laws:

| Archify token group | Quiet Green mapping (light / dark) |
|---|---|
| Surfaces `--bg` `--panel` `--panel-border` `--grid` `--mask` | neutral ladder `#f5f5f2`/`#17181b`, surface `#fefefc`/`#1e2024`, hairline `#e0e0da`/`#2e3036`, grid = `--line-soft`, mask = surface |
| Ink `--text` `--text-muted` `--text-dim` `--text-faint` | 4-step ramp `#23252a`/`#ecedea`, `#565a61`/`#a9acb1`, `#878b92`/`#74777d` |
| Lanes `--lane-fill` `--lane-stroke` | `bg-deep` washes + hairline strokes |
| Arrows `--arrow` `--arrow-emphasis` | ink-faint / **fern** (emphasis = the acting flow) |
| `backend` (core services, serving) | **fern** `#2e6b4f` / `#55b285` — "fern acts" |
| `frontend` (web surfaces) | **sage** `#5e7a54` / `#93b084` — the web hue |
| `database` (KG, curriculum truth, banks) | **plum** `#5d4991` / `#a290d3` |
| `cloud` (LLM providers; unused in current IRs) | **teal** `#0e7268` / `#3fb3a5` — "teal speaks" (AI voice) |
| `messagebus` (evidence events) | **gold** `#a97b12` / `#cfa13e` — recorded signals |
| `external` (corpus, parser, cross-repo) | **slate** `#4e6b84` / `#8fafc8` — paper/external |
| `security` (κ gate, sufficiency gate, write-protection group) | **danger** `#b0432d` / `#df7c63` — "red destroys, and only destroys" (fail-closed gates) |
| Toolbar `--toolbar-*` | surface-raised / line / ink / surface-sunken hover |

Node fills use the design system's chip-wash pattern (light: base at ~12–13%
alpha; dark: the dark washed-panel tints at ~55–60% alpha), preserving the
template's fill/stroke/mask mechanics unchanged.

**Component-level overrides** (appended after the token layer, winning the
cascade at equal specificity):

- **Geometry** — squared, floor 4px: diagram container 6px (the system max),
  cards/toolbar/search/guided-views 5px, chips/buttons/finder results 4px.
  Dots and pill shapes untouched (sanctioned exceptions).
- **Depth** — hairlines separate; the one real shadow belongs to floating
  layers: popover menus/finder/lenses/focus-chip/toast get `--shadow-pop`, the
  overview-map dialog gets `--shadow-overlay`, the anchored container gets
  `--shadow-soft`, cards get none (border only).
- **Typography** — three fonts, strict roles, loaded via Google Fonts with the
  design system's fallback stacks: Instrument Sans (body/UI chrome),
  Bricolage Grotesque 600/700 (page + card titles), Spline Sans Mono (data:
  kbd, counts, meta rows). **The SVG interior stays mono** (Spline Sans Mono →
  embedded JetBrains Mono fallback): every diagram label there is technical
  data (component names, `file:line` citations, status tags), which the design
  system assigns to mono.
- **Focus ring** — the universal teal ring on interactive chrome.

## 3. Verification (manual Playwright — `tools/visual_evidence_quiet_green.py`)

All five artifacts, **PASS 5/5**, evidence JSON
`tools/quiet-green-manual-browser-evidence.json`, screenshots in
`tools/quiet-green-evidence/` (12 committed PNGs):

- **Cascade proof (the override layer wins):** per artifact × theme,
  `getComputedStyle` asserts body background = `rgb(245,245,242)` /
  `rgb(23,24,27)`; `--backend-stroke` = `#2e6b4f` / `#55b285` (fern);
  declared font stacks resolve to Instrument Sans (body), Bricolage Grotesque
  (h1), Spline Sans Mono (SVG text). **Fonts actually loaded** in the evidence
  run (`document.fonts.check` = true for Instrument Sans and Bricolage
  Grotesque), so screenshots show the real typography, not fallbacks.
- **Horizontal containment EXACT** at 1440×1000, 1600×1000, 1920×1080,
  2048×1200 — every artifact, both themes (28 viewport checks, zero
  overflow). Vertical flow below the first screen is the conclusion cards
  (the accepted artifact shape, unchanged).
- **Needle labels** — 7 component labels per artifact taken from the
  artifact's own IR, all found in the rendered DOM (entity-unescape applied;
  the security group's "Canonical truth — runtime surfaces never write" and
  the κ-gate labels render in the danger hue as designed).
- **Interaction sanity** (separate one-off check, not committed): the theme
  toggle button flips `data-theme` light→dark and the body background follows
  the Quiet Green tokens; guided-view chips activate without errors.
- **Perceptual review** of committed screenshots: light learning-loop (warm
  neutral canvas, fern/sage/plum/gold/danger nodes, display-font title,
  hairline cards), dark learning-loop (tint-inverted washed panels, legible
  chips), dark overview (all 27 nodes/9 regions render; canonical-truth region
  plum, κ gate danger), light ingestion (red dashed security group
  "runtime surfaces never write", honest paused-lane tag).

## 4. Honest records and limits

- **Automated `archify visual-check` was NOT re-run** after the restyle — the
  command is environmentally unstable in this sandbox (recorded in §5/§8 of
  ARCHIFY_INTEGRATION.md: DevTools `Runtime.evaluate` timeouts). The existing
  per-artifact `*.visual-check.json` sidecars describe the **pre-restyle**
  deliver output and remain valid for structure/containment facts only; color
  and typography claims are superseded by this report's manual evidence.
- **Fonts require network.** The Google Fonts `<link>` degrades gracefully:
  offline, the stacks fall back (Instrument Sans → Helvetica Neue/Arial;
  Bricolage Grotesque → Avenir Next/Trebuchet MS; Spline Sans Mono → the
  artifact's embedded JetBrains Mono → system mono). No rendering depends on
  the fonts loading (verified: layout containment holds regardless; the
  design system itself specifies these fallbacks).
- **The self-contained property is preserved in substance**: no JS, no
  runtime services, no build step; the only external reference is the
  optional stylesheet link, with full in-file fallbacks.
- The tool is idempotent and refuses to touch artifacts with quiet-green
  traces but no markers (no guessing); marker absence + trace presence
  aborts loudly.

## 5. File inventory (this round)

| Path | Role |
|---|---|
| `docs/archify/tools/apply_quiet_green.py` | The deterministic post-processor (idempotent; part of the regeneration pipeline) |
| `docs/archify/tools/visual_evidence_quiet_green.py` | Manual browser-evidence script (containment + cascade proofs + needles + screenshots) |
| `docs/archify/tools/quiet-green-manual-browser-evidence.json` | Evidence results (5/5 PASS) |
| `docs/archify/tools/quiet-green-evidence/*.png` | 12 committed screenshots (5 artifacts × light/dark @1440 + learning-loop full-page ×2) |
| `docs/archify/T-ARCHIFY-QUIET-GREEN-EVIDENCE-REPORT.md` | This report |

## 6. What was NOT done

- No IR source was modified (the restyle is presentation-only; IRs still
  validate against the same pin, `syllabai-core @ 14b5e3d…`).
- No evidence-report content from earlier rounds was rewritten; earlier
  receipts stand for what they covered.
- No claim that "classic preset" now equals the Open Notebook app pixel-for-
  pixel: the mapping ports the token layer, geometry, depth and type roles;
  Archify's information design (node/edge/region grammar) is intentionally
  unchanged.
