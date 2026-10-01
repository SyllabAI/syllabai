# T-ARCHIFY Evidence Report — Archify install + first source-backed SyllabAI architecture diagram

**Date:** 2026-09-21
**Task:** T-ARCHIFY
**Diagram:** `docs/archify/syllabai-architecture-overview.html` (self-contained, interactive)
**IR source:** `docs/archify/syllabai-architecture-overview.archify.json`

---

```text
ARCHIFY INSTALLATION
- command: npx skills add tt-a1i/archify -g -y --skill '*' --agent claude-code
  (documented bare form `npx skills add tt-a1i/archify -g` hangs on an
   interactive picker when stdin is not a TTY; flags make it non-interactive)
- version: skills CLI 1.7.0; archify skill metadata v2.17 (installs `archify`
  + `archify-review` to ~/.claude/skills — global, outside all SyllabAI repos)
- verification: `npx skills list -g` lists both skills;
  `node bin/archify.mjs doctor` → "Archify is ready" (all runtimes [ok])

DIAGRAM
- generated: yes — `deliver architecture … --repo-root … --quality standard`
  spec sha256 df568b509df9144bfce7a96898e3874d9c9fa178dc7648b99a1451fc87c60a55
  (25,370 B) → artifact sha256 9f870e491b418bd5507f9db363f41adb6307ea4b234c33ced3a4ccaa35db097b
  (867,999 B, self-contained)
- validation: PASS — 9/9 artifact checks, 0 errors, 1 warning (standard
  composition profile), evidence verification PASS (28 source references
  verified at the pinned commit via --repo-root)
- visual inspection: automated `visual-check` could NOT complete (Chrome
  DevTools Runtime.evaluate timeout ×2 — environmental; chrome binary itself
  functional). Supplementary manual Playwright evidence instead: no horizontal
  overflow at 1440×900 / 1600×1000 / 1920×1080; vertical document scroll to
  conclusion cards; perceptual review of screenshots (image-reviewed) confirms
  all 27 nodes, 9 regions, guided views, status chips, κ-gate rendering.

SOURCE COVERAGE
- implementation-backed (code sources[] verified at syllabai-core @
  14b5e3d780956b39267bce2a8b831865ca4f89bb): api_core, curriculum, knowledge,
  assessment, smartmark, kappa_gate, teacher_marking, evidence, learner_model,
  diagnostic, recommendation, intervention, cla, tutor, retrieval,
  embedding_lane, content, revisionnotes, llm_chain, postgres (20 nodes)
- cross-repo implemented (text-cited repo@SHA in the amber card; no code
  sources — Archify supports one repository per diagram): learner_web +
  teacher_web (syllabai-web @ bfc9850), workbench (syllabai-teacher-workbench
  @ 39ad5d8), parser (syllabai-parser @ eef89fb, tc17-work), pastpapers
  (syllabai-pastpapers @ 6354773) (5 nodes)
- source data: corpus (SyllabAI/Past-Papers) (1 node)
- proposed: lil — Local Intelligence Layer (PROPOSED, dashed region; per
  LOCAL_INTELLIGENCE_LAYER_ARCHITECTURE.md status header) (1 node)
- inferred: none presented as implemented; KaRAG tutor is tagged
  IMPLEMENTED · UNVERIFIED (code exists at the pin; no verification battery on record)
- unverified markers on-nodes: pgvector lane PREPARED · UNVERIFIED;
  κ gate IMPLEMENTED · gate closed (fail-closed, no passing evaluation on file);
  content ingestion paused pending Embedding v2

LIMITATIONS
- One repository per Archify diagram: meta.repository pins syllabai-core, so
  code-level sources[] exist only for core nodes; cross-repo nodes carry
  repo@SHA text citations in the card instead of verified file:line links.
- standard composition profile (not showcase): the 27-node map cannot satisfy
  showcase's first-screen ≥6 px projected text at 1440 px; splitting into
  multiple diagrams is the future path to showcase quality.
- Automated visual-check incomplete in this environment (see above); manual
  Playwright containment + screenshot review substituted and committed.
- Undrawn request paths (API→assessment, API→tutor, pastpapers→API import,
  workbench transport) are omitted for readability and declared in the
  diagram's own cards — absence of an edge is not absence of a relationship.
- syllabai-demo does not exist (no repo, no ownership-map entry) and is omitted.

ARCHITECTURAL QUESTIONS / CONFLICTS
- None encountered between canonical docs and implementation for the nodes
  drawn. Status labels follow the Knowledge Map claim/status discipline
  (IMPLEMENTED = code exists at pin; VERIFIED = acceptance evidence on record).
- KaRAG tutor: implemented code exists (tutor/KaRagService.java et al.) but no
  verification battery was found in PROGRESS/Knowledge Map — tagged
  IMPLEMENTED · UNVERIFIED rather than silently promoted.

STATUS
- T-ARCHIFY: VERIFIED (installation, validation, evidence verification and
  manual visual review all executed; automated visual-check blocked by
  environment, documented above)
```
