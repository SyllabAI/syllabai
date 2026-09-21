# ARCHIFY_INTEGRATION.md — Archify as SyllabAI architecture-documentation tooling

**Status:** ACCEPTED (tooling workflow; executed 2026-09-21)
**Scope:** Developer/documentation capability only. Archify is **not** a dependency of `syllabai-core`, `syllabai-web`, `syllabai-demo` (does not exist), production runtime, or production deployment.
**Task:** T-ARCHIFY
**Diagram type:** `architecture` (Archify schema v1)

---

## 1. What Archify is here

Archify is an agent/developer skill that renders a small typed JSON specification
("IR") into a self-contained interactive HTML diagram (inline SVG, dark/light
themes, guided views, search, export). In SyllabAI it is used for one purpose:
**source-backed architecture diagrams as derived documentation**.

Non-goals, fixed by the task contract (T-ARCHIFY):

- Archify never enters any application dependency manifest.
- The generated diagram is **derived documentation, never the canonical
  architecture source of truth**. Canonical sources remain `MASTER_SPEC.md`,
  the ADR ledger, and the code itself.

## 2. Installation (verified 2026-09-21)

```bash
npx skills add tt-a1i/archify -g -y --skill '*' --agent claude-code
```

- Installs `archify` and `archify-review` skills to `~/.claude/skills/` (global,
  outside every SyllabAI repository).
- CLI version observed: `skills` npm package 1.7.0; Archify skill metadata version 2.17.
- Verification: `npx skills list -g` shows both skills; `node bin/archify.mjs doctor`
  reports "Archify is ready" (renderer, preview runtime, visual-check runtime,
  validators all `[ok]`).

Environment notes: the bare documented command `npx skills add tt-a1i/archify -g`
hangs on an interactive skill/agent picker when stdin is not a TTY; the flags
above make it non-interactive. Global installation to `~/.claude/skills` is the
closest supported non-destructive method in this environment.

## 3. Regeneration workflow (reproducible)

```text
SyllabAI GitHub source (pinned commit)
        ↓
inspect source / canonical docs
        ↓
author Archify JSON IR (docs/archify/*.archify.json)
        ↓
validate   node bin/archify.mjs validate architecture <ir> \
             --repo-root <local syllabai-core clone> --quality standard --json
        ↓
deliver    node bin/archify.mjs deliver architecture <ir> <out.html> \
             --repo-root <local syllabai-core clone> --quality standard --json
        ↓
browser evidence (visual-check; manual Playwright fallback — see §5)
        ↓
commit IR + HTML + evidence (content-only, target paths only)
```

Key rules baked into this workflow:

1. **Evidence is verified, not decorative.** The IR declares
   `meta.repository` (URL + full 40-char commit SHA). Every `sources[]` entry
   (`path`, `line`, `label`) is verified by Archify against the local clone at
   that commit via `--repo-root`. Current pin:
   `SyllabAI/syllabai-core @ 14b5e3d780956b39267bce2a8b831865ca4f89bb`
   (28 references verified at delivery).
2. **Status vocabulary is preserved.** Nodes carry text tags using the project
   vocabulary (`IMPLEMENTED`, `VERIFIED`, `PROPOSED`, `UNVERIFIED`, …). Color
   and dashed variants are secondary signals only; the "How to read status"
   card on the diagram states the semantics in text.
3. **Educational-truth invariants are drawn, not implied** — canonical
   curriculum/authoritative-KG nodes are grouped as "Educational truth
   (canonical)"; learner state is overlay-only; Smart Mark/assessment never
   point at canonical truth; the κ gate is drawn as a security-type node with
   `κ ≥ 0.60 · fail-closed`.
4. **Proposed/unverified components are explicit** — Local Intelligence Layer
   (`PROPOSED`, dashed region), pgvector lane (`PREPARED · UNVERIFIED`),
   KaRAG tutor (`IMPLEMENTED · UNVERIFIED`), κ gate (`IMPLEMENTED · gate closed`).
5. **A passing validation freezes the IR.** Never hand-edit the delivered HTML.

## 4. Files

| Path | Role |
|---|---|
| `docs/archify/syllabai-architecture-overview.archify.json` | Archify IR (source of the diagram; author-editable) |
| `docs/archify/syllabai-architecture-overview.html` | Delivered self-contained interactive HTML (do not edit; regenerate) |
| `docs/archify/T-ARCHIFY-EVIDENCE-REPORT.md` | Installation/validation/visual/evidence report for the first delivery |
| `docs/archify/tools/visual_inspect.py` | Manual browser-evidence script (Playwright containment + screenshots) |
| `docs/archify/tools/manual-browser-evidence.json` | Containment measurements from the manual run |

## 5. Browser evidence status (honest record)

`archify visual-check` (automated Chrome inspection) could not complete in this
environment: Chrome DevTools `Runtime.evaluate` timed out after 15000 ms on two
attempts (Playwright Chromium 1243 via `ARCHIFY_CHROME`; binary itself works —
`--dump-dom` smoke test exits 0). Per the delivery contract this is reported as
an environmental limitation, not a pass.

Supplementary manual evidence was produced instead
(`docs/archify/tools/manual-browser-evidence.json` + `tools/visual_inspect.py`):
no horizontal overflow at 1440×900 / 1600×1000 / 1920×1080; the artifact renders
as a vertically scrolling document (diagram first screen, conclusion cards
below); perceptual review of captured screenshots confirmed all regions, nodes,
status chips, guided views and the κ-gate rendering. Automated `visual-check`
should be re-run in an environment where the DevTools evaluate completes.

## 6. Quality profile decision

The first overview intentionally carries 27 nodes (task bound: 15–30). At
`showcase` quality, Archify enforces first-screen projected text ≥ 6 px at a
1440 px viewport, which a map this wide cannot satisfy; the map is therefore
authored and delivered at `standard` quality (the profile intended for dense
maps). Splitting into multiple diagrams remains the path to `showcase` if later
desired (e.g. separate learning-loop and retrieval diagrams).
