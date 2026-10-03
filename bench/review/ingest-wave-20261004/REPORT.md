# T-C75 W1 — Ingest-wave parse lane evidence (ingest-wave-20261004)

Task: **T-C75 W1 (parse wave)** — the pdflane direct-PDF route (G8 precedent) for the 4
un-ingested late 4CH1 papers: 2025-06 4CH1/1C; 2026-06 4CH1/{1C, 2C, 2CR}.
Operator word: **"run T-C75 W1"** (trace `1a1032937d19bf51`, 2026-10-04).
Executor: Super Z (main agent, zai session `web-98866c45-e4fe-46b3-b477-af00c7d7a422`).

## Pins and bases

| What | Value |
|---|---|
| Corpus base → landed | `syllabai-pastpapers` main `1f7e8355` → **`b8d53f7`** (products commit) |
| Records base at claim | `e3a566d`; claim commit **`592eea7`** (T-C75 → IN_PROGRESS, corpus lease taken) |
| Card | `.syllabai/tasks/T-C75.yaml` (registered `ef61d57`) |
| Lease | `locks.yaml` — syllabai-pastpapers parsed/ writes, base `1f7e8355`, expires 2026-10-06 (fulfilled by this pack; released at W1 close) |

## Pre-flight (all first-hand, 2026-10-04)

- **8/8 input PDFs sha256-match their manifest pins** at corpus pin `1f7e8355`
  (2025-06 1C qp `d860cbae…`/ms `a3e855a6…`; 2026-06 1C qp `231c0574…`/ms `d4febc16…`;
  2C qp `713f1fcc…`/ms `a42a22c4…`; 2CR qp `5ee0d5b4…`/ms `a005acd5…`).
- Printed covers read from page-1 text: 2025-06 1C "Monday 19 May 2025";
  2026-06 1C "Monday 18 May 2026"; 2C/2CR "Friday 12 June 2026".
- **Identity claims:** `--paper-code 4CH1/{1C,2C,2CR}` (printed refs agree on all four);
  `--session "June 2025"/"June 2026"` — the canonical series month per manifest
  `series.normalized`. The two 1C papers print May exam dates, so
  **IDENTITY-SESSION-DRIFT flags on both are the expected outcome** — the Pearson
  coded-date convention (June-series papers administered in May), pairing confirmed by
  the corpus manifests; same handling as the paper-repair-2026-09-26 lane's
  4ch1-1cr-202406 parse (claimed June 2024, drift flag disclosed).

## Toolchain (restored/re-verified in-sandbox after the recycle)

| Engine | Version / provenance |
|---|---|
| pdftotext (poppler) | 25.03.0 |
| PyMuPDF | 1.26.7 (MuPDF 1.26.12) |
| OpenDataLoader CLI (second opinion) | **2.5.7 shaded jar, restored from the pinned GitHub release** `opendataloader-project/opendataloader-pdf` v2.5.7 — jar sha256 `74f0d797bea8088bd4a58137e372eb38a5fa24639e06b633cef7f78eba14cd62`; present on **all 4** parses (no ODL-SECOND-OPINION-UNAVAILABLE escalations) |
| Java | OpenJDK 21.0.12.1 (Debian) |
| Python | 3.12.14 |
| Parser code | `SyllabAI/syllabai-parser` `tools/pdflane/` working tree (lane "pdflane deterministic phase-1", provenance class `pdf-parsed`) |

Determinism: run_paper outputs carry no timestamps; identical inputs + code produce
byte-identical `parsed/` trees (S0–S1 invariant). A pymupdf advisory line
("Consider using the pymupdf_layout package…") prefixes the run's stdout; it is
environment noise, not product content — the gate summaries in `gates/` are the
advisory-stripped JSON.

## Results (per paper)

| Paper | Overall | G1 | G2 | G3 | G4 | G5 | G6 | Census (QP/MS) | Product (atoms/1.1) | V1–V4 |
|---|---|---|---|---|---|---|---|---|---|---|
| 4ch1-1c-202506 | **FAIL** | **FAIL** | PASS | PASS | PASS | PASS | PASS_WITH_FLAGS | 10q/110 · 10q, 49 labels, 8 total rows | 10q/110, marksVerified=true | PASS |
| 4ch1-1c-202606 | PASS_WITH_FLAGS | PASS | PASS | PASS | PASS | PASS | PASS_WITH_FLAGS | 9q/110 · 9q, 56 labels, 9 total rows | 9q/110, marksVerified=true | PASS |
| 4ch1-2c-202606 | **PASS (clean)** | PASS | PASS | PASS | PASS | PASS | PASS | 6q/70 · 6q, 36 labels, 6 total rows | 6q/70, marksVerified=true | PASS |
| 4ch1-2cr-202606 | **FAIL** | **FAIL** | PASS | PASS | PASS | PASS | PASS | 7q/70 · 7q, 35 labels, **0 total rows** | 7q/70, marksVerified=true | PASS |

- **G1 FAILs (2 papers) = PRINTED-QP-MS-TOTAL-DISCREPANCY**, disclosed not smoothed:
  - 2025-06 1C: Q5 QP-printed 14 vs MS total row absent; Q7 QP-printed 12 vs MS absent
    (8 MS total rows found, 2 questions unmatched).
  - 2026-06 2CR: **all 7 questions** QP-printed totals (6/7/8/12/13/10/14) have no
    matching MS total row — the MS prints 0 recognizable total rows
    (a layout class the deterministic classifier does not recognize; the S2
    llm-structured accepted-run lane is the designed cure, out of W1 scope).
  - Semantics: these are **review-flagged, search-substrate-grade products** — exactly
    the G8 posture (72/72 G1-unverified at parse time). They are NOT bank-grade and
    **no bank tables were touched** (bank-grade G1 discipline, G8 §5 precedent).
- **G6 identity:** printed refs == claimed refs on all four; session drift flags only
  where predicted (both 1C papers, May-printed vs June-claimed).
- **Escalations:** GATE-FAIL x1 on each G1-FAIL paper; zero on the other two.

## Review-flag ledger (full counts; `review-flag-ledger.json` + per-paper jsonl)

| Paper | FURNITURE-DROPPED | FRONT-MATTER-PRUNED | MS-UNCLASSIFIED-ROW | TOTAL-DISCREPANCY | SESSION-DRIFT | total |
|---|---|---|---|---|---|---|
| 4ch1-1c-202506 | 27 | 29 | 5 | 1 | 1 | 63 |
| 4ch1-1c-202606 | 27 | 30 | 0 | 0 | 1 | 58 |
| 4ch1-2c-202606 | 19 | 25 | 1 | 0 | 0 | 45 |
| 4ch1-2cr-202606 | 19 | 21 | 0 | 1 | 0 | 41 |

- `QP-IMAGE-FURNITURE-DROPPED` / `FRONT-MATTER-ASSET-PRUNED` are by-design margin
  strips and unreferenced cover crops — disclosed so the counts are auditable.
- **6 x `MS-UNCLASSIFIED-ROW`** (5 on 2025-06 1C, 1 on 2026-06 2C) are genuine
  content-page rows the deterministic MS classifier could not place — HARNESS-DEFECT
  review items for a future grammar wave, NOT silently dropped.

## Products landed (corpus `b8d53f7`)

12 files — `parsed/{questions.json, qp.md, ms.md}` per paper, the per-paper layout
(products only; `_meta` staging stays ephemeral per corpus AGENT.md rule 4 and is
preserved here in `gates/`). All four `questions.json` are `syllabai.pastpaper.atoms/1.1`,
V1–V4 validation PASS, marksVerified=true. No `assets/` committed: every extracted
raster crop was either furniture or unreferenced front matter (pruned by the run), so
no atom references an asset — chemistry figures in these papers are vector drawings,
which the pdflane deterministic lane does not rasterize (known lane property vs
GLM-OCR, part of the recorded route trade-off). Checksums: `SHA256SUMS-products.txt`
(corpus-relative paths as committed).

## What this wave does NOT claim

- **Zero DB writes, zero ingest, zero embed, zero ep rows** — W2–W5 stay blocked on
  (1) core JWT secret (2) Gemini embedding key (3) Neon key re-provision; every
  DB-write batch is operator-gated (T-C54 wave-2 / T-C60 instrument precedents).
- No bank content, no canonical/ingest side effects, no frozen artifacts touched.
- G1 arithmetic on the two FAIL papers is **unresolved**, recorded as review items;
  W2 ingestion of these products should treat them exactly as G8 treated its 72.

## Reproduce

```
python3 -m pdflane.run_paper \
  --qp <corpus>/2025-06/4CH1-1C/qp.pdf --ms <corpus>/2025-06/4CH1-1C/ms.pdf \
  --out <stage>/4ch1-1c-202506/parsed --slug 4ch1-1c-202506 \
  --qualification international-gcse --board "Pearson Edexcel" --subject chemistry \
  --paper-code 4CH1/1C --session "June 2025"
```
(x4 with the per-paper dir/code/session above; corpus at `b8d53f7`, inputs
sha-pinned by the manifests.)
