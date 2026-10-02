# F-A2 verification wave — T-C58 (2026-10-02)

Operator mandate (trace `1a0fbf2dec8babe5`): "F-A2 verification wave." F-A2 was
registered by the corpus folder-mislabel audit (T-C56): 44 "(R)"-named files under
plain-paper dirs in NEVER-ingested specs, requiring the 09-28 three-class
verification before any ingestion wave trusts those folders. Verification only —
zero corpus writes, zero DB writes; any fix is a separate mandate.

## 1. Method (three-class protocol per CORPUS-FIX-2026-09-28)

Scope = the 44 C3 findings of T-C56 (`l1_findings.json`), one file per dir, across
9 specs: 4ph1 ×18 (1P/2P QP, 2019-01..2024-06), 4EB0/4EB1 ×11 (Paper 1 MS),
6PH0x ×6 (unit MS, physics-2008), 4MA0/4MA1 ×6 + 4MB0/4MB1 ×3 (QP).

- **Class 1 — byte-exact DAM sha**: attempted; Pearson content-dam serves an HTML
  interstitial to anonymous clients (probe recorded; matches the
  `docs/4SD0-2026-09-27.md` precedent). NOT obtainable from this environment.
- **Class 2 — naming**: PMT "(R)" original_filename on all 44 + manifest
  identification blocks (sha256 == manifest pin verified 44/44 before analysis).
- **Class 3 — cover-print verification**: pymupdf text layer where present;
  150–300 dpi grayscale render + tesseract 5.5.0 OCR for image-only covers
  (7) and broken-ToUnicode garbles (2 re-reads). Conclusive on 44/44.

## 2. Results — 44/44 resolved

### The 44 "(R)"-named files

| verdict | count | detail |
|---|---|---|
| **CONFIRMED-MISFILED-R** | **43** | cover prints the R reference — 4PH1 QP ×18 (`4PH1/1PR` + `4SD0/1PR` SDA-twin furniture, or `4PH1/2PR`), 4EB0/4EB1 MS ×11 (`Paper 01R`/`1R`), 6PH0x MS ×5 (`Paper 01R: …`), 4MA0-1F 2015-06 (`Paper 1FR` / `4MA0/1FR`, 300 dpi), 4MA1 QP ×5 (`1FR`/`1HR`/`2FR`/`2HR`), 4MB0-02 2015-01 (`02R`), 4MB1 ×2 (`01R`/`02R`) |
| **GENUINE-PLAIN** | **1** | 2013-06/6PH05-01 ms.pdf — cover prints "Paper 01: Physics-Creation/Collapse" + Publications Code UA036644; the PMT "(R)" filename is a naming artifact (the 2013-06/4PH0-2P/qp precedent of the 09-28 wave) |

Zero UNRESOLVED. Per-dir picture: the disease is confined to the "(R)"-named
file — the sibling material in every affected dir verified genuine plain bytes
(44/44; the 2015-06/4EB0-01 QP via 300 dpi OCR `4EB0/01`).

### Sibling R dirs (the complement)

All 44 affected dirs have a same-session sibling R dir (4PH1-1PR/2PR, 4MA1-1FR/1HR/
2FR/2HR, 4MB0-02R, 4MB1-01R/02R, 4EB0/4EB1-01R, 6PH0x-01R). 45 material
cover-checks across them (33 text-layer + 6 OCR of garbled ToUnicode + 2 refetched
4PH1-2PR 2024-06 + 4 other-material dirs): **ALL R-BYTES, zero swap shape** — the
R dirs hold genuine regional papers (different scans from the PMT copies in the
plain dirs; 0 byte-identical twins). 4 R dirs hold only the sibling material
(verified R). The 2013-06/6PH05-01R QP prints `6PH05/01R` — consistent with the
one genuine-plain MS staying in the plain dir.

### Not obtainable

- Class 1 (byte-exact DAM): HTML interstitial (see above). The 09-28 wave also
  accepted naming + pixel evidence as conclusive for 20/23 of its files.

## 3. Bottom line + fix shape (NOT executed — separate mandate)

The F-A2 hazard is **confirmed and quantified**: 43 of the 44 "(R)"-named files
are regional-variant bytes sitting under plain-paper dirs in never-ingested specs
(the same disease the 09-28 wave cured for 4PH0); 1 is benign. Every affected dir
still needs its plain counterpart for the mis-filed material (the genuine plain
QP/MS is absent wherever the R copy sits), while R bytes already exist correctly
in the sibling R dirs. Fix shape when mandated = the 09-28 precedent: replace the
43 mis-filed files with the official plain documents (content-dam URLs recorded
per material at wave time; the DAM interstitial constraint means the fix lane
needs the authenticated/URL-resolved route), correction notes in
`identification.notes`, benign 6PH05-2013 MS needs no byte change (manifest note
optional), then re-run the T-C56 L1/L2 checks on the touched specs. Until then:
**do not ingest the 4ph1/4eb0/4eb1/physics-2008/4ma0/4ma1/4mb0/4mb1 specs off
folder names alone.**

## 4. Pack

`inventory.json` · `fa2_class2_covers.json` · `fa2_class3_ocr_maths.json` ·
`fa2_rdir_crosscheck.json` · `fa2_rdir_complement.json` ·
`fa2_siblings_and_rdirs.json` · `fa2_stragglers_ocr.json` · `verdicts.json` ·
`REPORT.md` (this file) · `SHA256SUMS`. Scripts (read-only, session workspace):
`fa2_build_inventory.py`, `fa2_class2_covers.py`, `fa2_class3_ocr_maths.py`,
`fa2_rdir_crosscheck.py`, `fa2_rdir_complement.py`, `fa2_siblings_rdirs.py`,
`fa2_verdicts.py`.
