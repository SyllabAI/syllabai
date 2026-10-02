# Corpus fix wave — 2026-10-02 — F-A2: replace the mis-filed regional (R) papers in the never-ingested specs

Operator-approved fix wave (T-C62): replace the 43 CONFIRMED-MISFILED-R files
registered by the F-A2 verification wave (T-C58, `bench/review/fa2-verification-20261002/`
in the records repo) with the official plain documents, following the
CORPUS-FIX-2026-09-28 precedent.

## Problem

The 2026-09-11-era ingestion populated paper dirs across the never-ingested
specs from PhysicsAndMathsTutor.com. In 44 plain-paper dirs the stored file was
PMT's "(R)" download — the regional-variant paper — filed under the plain-paper
dir. T-C58 verified all 44 by the three-class protocol (PMT "(R)" naming +
cover-print/pixel): **43 CONFIRMED-MISFILED-R + 1 GENUINE-PLAIN** (the
2013-06/6PH05-01 ms, whose PMT "(R)" filename is a naming artifact — untouched
here, exactly as the 2013-06/4PH0-2P/qp precedent of the 09-28 wave).

## Fix (this wave)

40 of the 43 confirmed-mis-filed files were replaced with the official plain
document re-downloaded at wave time from the Pearson qualifications portal
content-dam. Resolution route: Pearson's public course-catalog index (the
qualifications-uk_LIVE_master-content catalog that powers the past-paper
search) resolving exact per-material DAM URLs, then **first-hand identity
verification of the downloaded bytes** (PDF parse; plain paper reference
printed on the cover, R-form absent at token level; sitting match against the
dir session or the replaced copy's own cover print; mark-scheme/question-paper
furniture; sha256 distinct from every mis-filed copy). URLs + new sha256/size
are recorded per material in each manifest. The 09-28 constraint held: correct
DAM asset URLs serve bytes anonymously; unknown paths serve an HTML
interstitial.

Evidence classes used for acceptance (recorded per material in the manifests):

- `cover-ref` — the plain slash reference printed on pages 1–3 (text layer or
  200 dpi OCR);
- `cover-unit+paper-form (GCE cover style)` — GCE mark-scheme covers print the
  unit code + "Paper 01" form rather than a slash reference;
- `cover-ref + catalog-title-session` — newer IGCSE covers print no exam date;
  the session axis comes from Pearson's own catalog title for the exact file.

## Not replaced (3) — documented unresolvable, fail-closed

| dir | file | reason |
|---|---|---|
| 4eb0/2014-06/4EB0-01 | ms.pdf | the official June 2014 4EB0 Paper 1 mark scheme is not on the public DAM (catalog gap across all naming families; bounded filename probes negative) |
| 4ph1/2020-06/4PH1-1P | qp.pdf | the June 2020 sitting plain papers are not on the public DAM; the only catalog files (…que_20201114/…que_20201124) are the November 2020 sitting — different papers (page counts 32 vs 36 / 24 vs 20 vs the mis-filed June-2020 copies, whose covers print May/June 2020). Substituting a different sitting would mis-file by session |
| 4ph1/2020-06/4PH1-2P | qp.pdf | same as above |

These three dirs keep their (verified mis-filed) bytes for now; each manifest
records the finding and an explicit do-not-ingest-off-folder-names note until
an authenticated source provides the June 2020 / June 2014 4EB0 documents.

## Verification after replacement

Per the T-C58 registered shape, the T-C56 L1/L2 checks were re-run on the
touched specs after this commit (results recorded in the records repo pack
`bench/review/fa2-fix-20261002/`).
