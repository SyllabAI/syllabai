# T-C73 — F-A2 slot completion final (3 of 3): 4EB0-01 2014-06 ms ← plain MS via operator-supplied PMT URL

- Date: 2026-10-03. Operator trace: `1a10278c4e1f2171` (direct PMT URL pasted in chat).
- Standing authority: F-A2 fix mandate (trace 1a0fc4b91fc4c965) + operator sourcing guidance
  (trace 1a0fdbc82e010361, "2014 one, you will find in PMT") + Session 162 close-out option (a)
  (sanctioned-source bytes subject to T-C62 evidence-class verification).
- Slot: `past-papers/pearson-edexcel/international-gcse/english-language-b/4eb0/past-papers/2014-06/4EB0-01/ms.pdf`

## Guards at execution time

| Guard | Value |
|---|---|
| corpus main HEAD | `15291f50c…` (the T-C71 commit; unchanged since) |
| slot bytes at HEAD | sha256 `edba020d8e33298048f151bb840cc39958accda4d62f6afc585944cf84a4bf4d` == manifest pin (62,870 B) |
| records main HEAD at recon | `3e62afbf0` (Sessions 167–170 = other lanes: T-C72 rank-quality, F-PROD-1) |
| residue bullet | still open ("F-A2 residue (1 of 3, still blocked") — nobody closed it |
| task claim | T-C72 taken (web-123877e4 rank-quality lane) → **this lane = T-C73** |
| dir QP/insert | untouched (qp `d76c222a…`, insert `67525a7f…`) |

## Identity verification matrix (fail-closed, all first-hand)

| # | Check | Result |
|---|---|---|
| V1 | HTTP 200, `application/pdf`, 63,157 B, `%PDF` magic | PASS |
| V2 | text extracts (34,933 chars); "Mark Scheme (Results)" present | PASS |
| V3 | cover prints "Paper 01" (plain); NO "01R" token in the whole text | PASS |
| V4 | session print "Summer 2014" (Pearson's June-series print; PMT filename "June 2014"; corpus series 2014-06) | PASS |
| V5 | sha256 `0796517f320979c5a788a82ddd8cdd72a9ebf1d6a0d66829ad7a112b78c373b0` ≠ mis-filed R pin `edba020d…` | PASS |
| V6 | pairing with the dir's plain QP (pin `d76c222a…`, cover "4EB0/01", Thu 22 May 2014, Total Marks 100): MS Section A "(30 marks)" == QP Q1–Q10 sum (1+3+3+2+3+3+2+4+3+6 = 30); MS writing grids 10+20+5 = 35 == QP Q11; 25+10 = 35 == QP Q12; MS sections A/B/C == QP structure | PASS |
| V7 | Publications Code **UG038775** (new) vs **UG038773** (mis-filed R) — distinct documents | PASS |
| V8 | cover renders: new = "Paper 01", mis-filed = "Paper 01R" (plain_ms_cover_p1.png / misfiled_R_ms_cover_p1.png) | PASS |
| V9 | 18 pages (same as the R file — R shares the question skeleton; discriminators are V3/V7/V8) | PASS |
| V10 | PMT watermark present (top of pages) — consistent with this dir's recorded PMT provenance | noted |

## Cover prints (exact)

- New (plain): "Mark Scheme (Results) / Summer 2014 / Pearson Edexcel International GCSE / in English
  Language B (4EB0) / **Paper 01**" + Publications Code UG038775.
- Mis-filed (R): same cover frame but "**Paper 01R**" + Publications Code UG038773.

## Provenance

- source_url (recorded on the manifest material block): https://pmt.physicsandmathstutor.com/download/English-Language/GCSE/Past-Papers/Edexcel-IGCSE-B/Paper-1/June%202014%20MS%20-%20Paper%201%20Edexcel%20(B)%20English%20Language%20IGCSE.pdf
- archive: PhysicsAndMathsTutor.com (third-party archive; the operator's named source for this
  sitting, trace 1a0fdbc82e010361; direct URL supplied by the operator, trace 1a10278c4e1f2171).
- collected_by: SyllabAI agent (2026-10-03 corpus-fix wave (F-A2 slot completion)).
- The DAM (Pearson qualifications portal) does NOT carry this document (T-C62/T-C71 exhaustive
  catalog re-scans: Jun 2014 absent) — PMT is the only sanctioned route, per the operator.

## New bytes

- sha256: `0796517f320979c5a788a82ddd8cdd72a9ebf1d6a0d66829ad7a112b78c373b0`
- size: 63,157 bytes
- original_filename: `June 2014 MS - Paper 1 Edexcel (B) English Language IGCSE.pdf`

## Files in this pack

- `fa2r_guard.json` — protocol ①② guard outputs + the full pre-edit slot manifest
- `fa2r_download_verify.json` — download + first verification pass
- `fa2r_deep_verify.json` — plain-vs-R contrast (refs, pub codes, pages, furniture, similarity)
- `fa2r_pair.json` — exact furniture lines + QP/MS pairing extraction
- `plain_ms_cover_p1.png` / `misfiled_R_ms_cover_p1.png` — cover render evidence
- `SHA256SUMS` — this pack's checksums
