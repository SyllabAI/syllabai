# Doc-lane fixes #2 — Paperlords sourcing closes 6 of the 7 remaining PDF-MAPPING-AMBIGUOUS slugs (2026-09-25)

Lane: doc-lane (Session 125, second pass). Operator tip: "Paperlords has those
papers" — verified first-hand and it did (for Nov 2023/2024/2025; not Nov 2020).

## 1. Source verification and URL discovery

paperlords.org is a Next.js UI over an OPEN archive CDN. The download URL
scheme was discovered by clicking Chemistry → Nov 2023 → P1 QP in a scripted
browser and reading the network log:

    https://archive.paperlords.org/library/IGCSE/Chemistry/<session>/IGCSE_CHEMISTRY_<y>_Nov_P<n>_{QP,MS}.pdf

Nov-2024 P2 filenames carry upload-dedup timestamp suffixes
(`_1781196095966` QP / `_1777793506071` MS). The site's Chemistry session
list: June 2026 … Nov 2025 / May-June 2025 / Nov 2024 / May-June 2024 /
Nov 2023 / … Jan 2019 — **no Nov 2020 sitting exists there**.

## 2. Downloads and cover verification (12 PDFs, 6 papers)

All 12 covers read from page 1 (pdftotext) and matched against the printed
identity — see `source-forensics-paperlords.json` for the full table:

- Nov 2023: 1C QP "Tuesday 14 November 2023" (4CH1/1C 4SD0/1C), 2C QP
  "Monday 20 November 2023" (4CH1/2C); MS "November 2023" Paper 1C/2C
- Nov 2024: 1C QP "Tuesday 12 November 2024", 2C QP "Monday 18 November 2024";
  MS "November 2024" Paper 1C/2C
- Nov 2025: 1C QP "Tuesday 11 November 2025", 2C QP "Monday 17 November 2025";
  MS "November 2025" 4CH1/1C / 4CH1/2C

## 3. Corpus landing

Past-Papers commit `d422e19af3` (Git Data API, single commit): 12 files under
`IGCSE/Edexcel/Chemistry/Paper 1|2/November 2023|2024|2025 {QP,MS}.pdf`
(naming per the Nov-2021 precedent). Commit message carries provenance + covers.

## 4. Re-gate (blob-verified from repo HEAD; parser f4ec81f)

6/6 **VERIFIED, zero flags**: 1C papers 10-11 q / 110 marks, 2C papers 6-7 q /
70 marks. Pre-validation on the paperlords downloads and the blob-verified
re-parse from the repo agree exactly. Corpus-wide VERIFIED: 23 → **29**.

## 5. Bank drive (6 NEW fresh ingests, sequential + probe-safe)

One POST per paper, per-paper landed-check before each POST, no blind retries
(the first POST absorbed a 190.8 s Render cold start and still returned 201).
All 6 → HTTP 201, all SUGGESTED, `pdflane-atoms-draft-v1`, doc pointers null.

| slug | Q | parts | mp | POST |
|---|---|---|---|---|
| 4ch1-1c-202311 | 10 | 79 | 66 | 201 |
| 4ch1-2c-202311 | 7 | 45 | 37 | 201 |
| 4ch1-1c-202411 | 11 | 68 | 56 | 201 |
| 4ch1-2c-202411 | 7 | 41 | 34 | 201 |
| 4ch1-1c-202511 | 10 | 72 | 59 | 201 |
| 4ch1-2c-202511 | 6 | 39 | 31 | 201 |

**C-gates: 6/6 PASS** — refs match, per-question marks bank=draft=atoms EXACT,
mark_points bank=draft, attempts=0. Zero rows deleted (all NEW).

Bank totals: 1,489 → **1,540 questions** / 4,914 → **5,197 mark points** /
99 → **105 exam_papers**; pdflane versions 215 → **266**.

## 6. Remaining gap

**4ch1-1c-202011 (Nov-2020 1C)** is the only PDF-MAPPING-AMBIGUOUS slug left —
the COVID sitting that paperlords does not carry and no anonymous channel
reached. Operator channels (Pearson Exam Officer / dynamicpapers password /
manual upload) remain the unblock.

## 7. Artifacts

- `source-forensics-paperlords.json` — URL scheme, per-file sha256 + covers
- `doclane_gate_report_pl.json` / `doclane_regate_report_pl.json` — pre-validation and blob-verified re-gate
- `doclane_drive_report_pl.json` / `doclane_poststate_pl.json` — drive responses + C-gates
- `SHA256SUMS`
- Past-Papers commit: `d422e19af3`
