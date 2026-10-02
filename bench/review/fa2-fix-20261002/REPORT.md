# F-A2 fix wave — T-C62 (2026-10-02)

Operator mandate (trace `1a0fc4b91fc4c965`): "① F-A2 fix mandate (replace the 43 with
official plain papers — needs the authenticated content-dam route)". The T-C58
verification wave resolved the 44 "(R)"-named files as 43 CONFIRMED-MISFILED-R +
1 GENUINE-PLAIN and registered the fix shape (the 09-28 precedent). This lane
executed it end to end; corpus commit **`f0ea3a1f9`** on `SyllabAI/syllabai-pastpapers`
main (base `029c6ec92`, the T-C56/T-C58 pin).

## 1. URL resolution (the authenticated/URL-resolved route)

The DAM serves `application/pdf` anonymously for **correct, resolved** asset URLs
(verified against the 09-28 wave's recorded URLs first); HTML interstitials appear
only on unknown/guessed paths. Resolution route: Pearson's public course catalog
(the `qualifications-uk_LIVE_master-content` Algolia index that powers the
qualifications.pearson.com past-paper search) + web-search surface of indexed DAM
URLs, filtered per material to exact filename token + kind suffix + catalog-title
session match. **43/43 materials resolved to candidate official DAM URLs.**

## 2. First-hand verification (fail-closed, per candidate)

Downloaded bytes verified before acceptance: PDF parse; plain paper reference
printed on pages 1–3 (text layer, 200 dpi tesseract OCR fallback); R-form absent
(token-level, incl. SDA-twin furniture like `4SD0/1PR`); sitting match against
{dir session ∪ the replaced copy's own cover prints} (extended print forms:
`Summer 2014` GCE covers, day-month exam dates, `November` series); MS/QP
furniture; sha256 distinct from every mis-filed copy; URL filename must carry the
spec token; catalog titles carrying R-variant paper names rejected.

Evidence classes accepted (recorded per material): `cover-ref` (29) ·
`cover-unit+paper-form` GCE cover style (4) · `cover-ref + catalog-title-session`
(newer IGCSE covers print no exam date) (7).

**Two mis-accepts were caught and reverted by the guards themselves** — the value
of the fail-closed chain: (a) the 2020-06 pair initially accepted the November
2020 catalog files (page counts 32 vs 36 / 24 vs 20 vs the June-2020 R copies,
whose covers print May/June 2020 — different sitting); (b) the 4EB0 2014-06 slot
initially accepted a `4EA0_02R` file before the filename-token + paper-in-title
hard guards landed.

## 3. Outcome — 40 replaced, 3 documented unresolvable

| outcome | count | detail |
|---|---|---|
| REPLACED | **40** | 4ph1 1P/2P QP ×16 (2019-06..2024-06), 4EB0/4EB1 Paper 1 MS ×10, 6PH0x unit MS ×5, 4MA0-1F 2015-06 + 4MA1 ×5 QP, 4MB0-02 2015-01 + 4MB1 ×2 QP — every replacement's URL + sha256 + size recorded in its manifest material block with the 09-28-format source block and correction note |
| UNRESOLVED | **3** | `4EB0-01` 2014-06 ms (the official June 2014 4EB0 Paper 1 MS is absent from the public DAM across all naming families; bounded probes negative) · `4PH1-1P`/`4PH1-2P` 2020-06 qp (the June 2020 sitting's plain papers are not on the public DAM — the only catalog files are the November 2020 sitting, different papers) — bytes unchanged, manifests carry the finding + an explicit do-not-ingest note |

The benign `2013-06/6PH05-01` ms (T-C58 GENUINE-PLAIN) is untouched.

## 4. Post-push verification (T-C56 L1/L2 re-run, scoped to the touched dirs)

Against the pushed commit `f0ea3a1f9`, every manifest re-fetched fresh from the
server and every material PDF re-downloaded: **C1 43/43 · C4 43/43 · L2 sha==pin
93/93 files, zero mismatches**. C3 residue = exactly the 3 documented-unresolvable
dirs (expected, recorded). Pack: `fa2fix_l1l2.json`.

## 5. Concurrent-lane note

`T-C60` (papers-axis completion) was IN_PROGRESS throughout on a disjoint scope
(5-paper ingest + 11 ep heals + 8-doc promotion, staged pending credential — its
writes began landing as this lane finished: the census shows 8 chunkless
SUGGESTED→VALIDATED flips and ep 103→104 with no audit rows from this lane's
instrument). No corpus or DB write of this lane overlapped T-C60's surface.

## 6. Pack

`REPORT.md` (this file) · `fa2fix_verify.json` (per-material candidates, evidence,
accepted URL/sha/size) · `fa2fix_tasks.json` (43 materials + resolved candidates +
catalog titles) · `fa2fix_l1l2.json` (post-push L1/L2) · `fa2fix_commit.json`
(corpus commit f0ea3a1f9) · `CORPUS-FIX-FA2-2026-10-02.md` (the wave doc as pushed)
· `SHA256SUMS`. Scripts: `scripts/fa2fix_search.py`, `fa2fix_search2.py`,
`fa2fix_algolia.py`, `fa2fix_enrich.py`, `fa2fix_verify.py`,
`fa2fix_manifests.py`, `fa2fix_commit.py`, `fa2fix_l1l2.py` (session workspace).

Secrets env-only (GH_PAT + RENDER_KEY — revoke after reading). Remaining open:
F-A1 ep-linked-R-generations relabel ruling (see the fa1-retire pack), the 3
unresolvable replacements, secrets revocation. (Super Z, T-C62)
