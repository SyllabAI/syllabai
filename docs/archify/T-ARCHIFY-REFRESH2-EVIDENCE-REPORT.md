# T-ARCHIFY REFRESH-2 — Evidence Report (2026-10-21)

**Lane:** T-ARCHIFY refresh-2 — all five diagrams re-pinned to the system of record `syllabai-v2`
**Directive:** operator, trace `1a15e70631f74cc1` — "Update the archify diagrams"
**Trigger:** the 2026-10-13 CUTOVER (T-C84, `CUTOVER_RETIREMENT_2026-10-13.md`) left every diagram pinned to the **archived read-only** `syllabai-core @ 93850118819053a8a7404902d5a7a83ab09d0dbd` (itself 2nd-stale: core was archived at head `6cad6ef`). Per the evidence rule ("use current repository evidence"), the refresh re-pins to the port of record.

## 1. Pin of record

```
repository: https://github.com/SyllabAI/syllabai-v2
revision:   d07267ae3d57974c202bf2f4141b9a3ba00a8ee8  (v2 main at lane start, 2026-10-21T12:12Z)
```

Concurrent lanes advanced v2 main during the lane (the repo is live); the pin is the verified snapshot, not the moving tip. The evidence chain stays two-legged: every v2 port header cites its frozen Java source (`syllabai-core @ 6cad6ef`), so the archival does not orphan any claim.

## 2. Re-anchoring + delivery (toolchain-verified)

| Artifact | Profile | Nodes | Sources | Evidence verified |
|---|---|---|---|---|
| `syllabai-architecture-overview` | **standard** (per §6, see §4) | 28 (+1) | 35 | TRUE · 35 refs |
| `syllabai-learning-loop` | showcase | 11 | 22 | TRUE · 22 refs |
| `syllabai-retrieval-architecture` | showcase | 10 (−2) | 21 | TRUE · 21 refs |
| `syllabai-assessment-marking` | showcase | 12 | 22 | TRUE · 22 refs |
| `syllabai-ingestion-pipeline` | showcase | 12 | 22 | TRUE · 22 refs |

- **122 source references verified at the pin** by `archify deliver` (every `sources[]` path:line checked against the v2 clone; 129 Java anchors were replaced — the delta is the BM25/fabric removal plus consolidation).
- Delivery receipts: `*.delivery.json` (5/5 `ok:true`, stage `deliver`, pre-QG bytes).
- Toolchain: Archify v3 (skill re-installed this lane; `archify doctor` all-ok).

## 3. Semantic drift folded in (of-record facts, per diagram)

- **Overview:** api of record relabeled (`syllabai-v2 apps/api — API of record`, Hono/Vercel); learner surfaces moved INTO the pinned monorepo (`apps/hub`, no longer cross-repo); `syllabai-web` relabeled internal teacher/ops console (ADR-029 posture); region relabeled "TypeScript port of record (cutover 2026-10-13)"; **NEW component `books_rail`** (ADR-BOOK-0001 · blocks · glossary, demo gate c01–c05, migration 0005) added to the surfaces row; postgres relabeled Neon + drizzle; LLM chain drift (`gemini-3.6-flash`, nemotron on OpenRouter per the v2 chain header); cross-repo card re-pinned (web `cae30ea`, workbench `eb997d6`, parser `00901e1`, pastpapers `87b6b98`, resources `aa0b4de`); cutover card line added.
- **Learning loop:** learner_web now pin-verified (was cross-repo); attempts/tutor/engagement anchors to the port; NBA `nba-rules/v1.3` and struggle `rules-v0.2` re-anchored; cross-repo card states the retirement honestly.
- **Retrieval:** **the BM25 lexical arm and the RetrievalFabric orchestrator were NOT ported to v2** (verified absent at the pin — zero `bm25`/`RetrievalFabric` modules; the Java arms were unwired by design, zero consumers, T-C13). The diagram shrinks 12 → 10 nodes; the "What is NOT serving today" card states the removal instead of pretending the arms still exist. Serving path unchanged: deterministic intent → fail-closed scope (ADR-030) → KG + T-C20 VALIDATED-only vector leg → RRF k=60 per-kind weights → NoReranker v0 → cap 6 → sufficiency gate → grounded generation → citations.
- **Assessment & marking:** pipeline **1.3.0** (was 1.2.1); `markPoints` per point (ADR-037 v0.7) on scheme review; kappa anchors moved to the port (`cohenKappa`, threshold 0.6); evidence once-guard (`DECISION_016`) anchor `teachermarking/index.ts:752`; boundary re-pinned.
- **Ingestion:** T-C02 bridge / T-011 / T-013 anchors to `glm-ocr.ts` / `past-paper.ts` / `canonical.ts` (checksum dedup); curriculum component relabeled "Curriculum & KG seed" (the T-010 runtime bridge has no v2 equivalent; seeding is lane-side); content posture card states the books band + ADR-037 official-paper lane and the APPLY-READY books vector arm (Session 207).

## 4. Quality-profile decision (overview)

The overview IR carried `quality_profile: "showcase"` — later drift against the documented §6 decision ("authored and delivered at `standard` … the profile intended for dense maps"). Today's stricter desktop-readability floor (6px projected at the 930px budget; scale 0.3957 at viewBox 2350) cannot hold at showcase for ANY wide map, including the previously delivered text. The refresh **returns the overview to `standard`** (meta now consistent), and the IR passes the strict final artifact check 0-error. The four split diagrams remain showcase and pass.

## 5. Quiet Green re-application

`tools/apply_quiet_green.py` re-applied byte-stably to all five post-deliver (markers `quiet-green-theme:BEGIN/END` once per file, both theme blocks present, structure asserts pass): 889,198→897,072 / 839,229→846,712 / 836,247→843,711 / 841,848→849,343 / 841,265→848,816 bytes.

## 6. Browser evidence (honest record)

- **Packaged `browser-check` on post-QG bytes: 5/5 attempted, 5/5 `delivery/provenance-mismatch`** — receipts committed in `tools/refresh2-browser-check/`. Expected: the QG post-processor changes the bytes the delivery receipt pins; the same record shape as the 2026-09-22 QG lane ("environmental fail, recorded").
- **Manual Playwright evidence: 5/5 PASS** (`tools/refresh2-manual-browser-evidence.json`, script `tools/visual_evidence_refresh2.py`): every refresh new-fact needle present in the RENDERED DOM (region relabels, Books rail, Neon/drizzle, pipeline 1.3.0, NOT-PORTED honesty card, cutover card lines; source-ref paths verified in the artifact bytes), horizontal containment EXACT at 1440/1600/1920/2048, SHA-256-bound to the committed post-QG bytes.
- **15 screenshots committed** (`tools/refresh2-evidence/*.png`, index `tools/refresh2-screenshots.json`): 5 artifacts × first-viewport light/dark + full-page dark. Perceptual review performed (overview light, retrieval dark reviewed closely: QG palette, regions, security-node rendering, card text all correct).

## 7. Lane errata (caught by the toolchain, fixed in-lane)

- `books_rail`/`postgres` initially cited migration 0005 at line 97 — the file has 76 lines; the evidence verifier rejected it (the lane had misread `head -20` output as line numbers). Re-anchored to line 19 (`CREATE TABLE "book_blocks"`).
- Three source labels exceeded the 48-char schema limit; one sublabel tripped the 6px projected floor; `books_rail`'s first free-slot placement sat inside the learner→api edge corridor and its region frame needed explicit membership — all caught by validate/deliver and fixed.

## 8. Files

| Path | Role |
|---|---|
| `docs/archify/*.archify.json` (5) | Refreshed IRs — pin `syllabai-v2 @ d07267a…`, port-anchored sources |
| `docs/archify/*.html` (5) | Re-delivered + QG post-processed artifacts |
| `docs/archify/*.delivery.json` (5) | Delivery receipts (evidence verified at the pin) |
| `docs/archify/T-ARCHIFY-REFRESH2-EVIDENCE-REPORT.md` | This report |
| `docs/archify/tools/visual_evidence_refresh2.py` | Refresh-2 manual evidence script |
| `docs/archify/tools/refresh2-manual-browser-evidence.json` | 5/5 PASS results, SHA-256-bound |
| `docs/archify/tools/visual_screenshots_refresh2.py` | Screenshot capture script |
| `docs/archify/tools/refresh2-screenshots.json` | Screenshot index (SHA-bound) |
| `docs/archify/tools/refresh2-evidence/*.png` | 15 committed screenshots |
| `docs/archify/tools/refresh2-browser-check/*.json` | 5 packaged-check receipts (post-QG attempt, provenance-mismatch recorded) |

## 9. Credential handling (fingerprints only)

gh-pat fp16 `a8ccee736aa8c75b` — the PAT of record (Sessions 206–208), UNROTATED; used inline-env only for clone/deliver evidence and the records push; **zero token in any `.git/config`** (both lane clones scrubbed before commit). Rotation standing order reiterated (the token transited a chat channel this lane).
