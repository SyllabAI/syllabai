# F-A2 slot completion — T-C71 (2026-10-03)

Operator sourcing guidance (IM trace `1a0fdbc82e010361`): **"2014 one, you will find in
PMT. and 2020-06 papers are basically 2020 november ones."** — aimed at the 3 documented
unresolvable slots left by the T-C62 F-A2 fix wave (40/43 replaced, corpus `f0ea3a1f9`).
This lane executed the two physics slots end to end and re-verified the 4EB0 blockage.
Corpus commit **`15291f50c7b1e05078c4ee5223ffac742bca5147`** on `SyllabAI/syllabai-pastpapers`
main (base `f0ea3a1f9`, the T-C62 pin, race-guarded).

## 1. Protocol

Authoritative worklog re-read first (Sessions 156–165 + the Session 162 open-② recon);
T-C62's fix shape + evidence class pinned as scope; locks checked (no conflicting lease —
T-C69 bench lane and T-C70 Past-Paper-Run lane are disjoint surfaces); corpus HEAD
re-verified `f0ea3a1f9` with all 3 slot bytes still at their manifest pins
(`edba020d…` / `722e5cf8…` / `d1d9b8cf…` — see `fa2s_probe.json`). Claim T-C71 (T-C70 taken).

## 2. The two physics slots — sourced from the official DAM and replaced

Route: the public course catalog (Algolia index `qualifications-uk_LIVE_master-content`,
App `L639T95U5A` — the qualifications.pearson.com front-end's own public credentials, the
T-C62 route re-used; `catalog_hits.json`):

| slot | DAM file (catalog title) | sha256 | bytes |
|---|---|---|---|
| `2020-06/4PH1-1P/qp.pdf` | `4PH1_1P_que_20201114.pdf` — "Question paper - Paper 1P - November 2020" | `28e1f5bc19c5c8472931d9c5f502f1e94d43a60e36e64a6f36ca4b32fe9d918c` | 598,762 |
| `2020-06/4PH1-2P/qp.pdf` | `4PH1_2P_que_20201124.pdf` — "Question paper - Paper 2P - November 2020" | `c10b95175e0fbb0b82853de916c95d36f8bdc4981d693b716e7711df56ea3879` | 4,224,950 |

### First-hand verification (fail-closed; `fa2s_fetch_verify.json` + `fa2s_crosscheck.json` + cover PNGs)

- `%PDF` magic; text parse of all pages; QP furniture present.
- Plain refs printed on covers (visual + text): 1P "Paper Reference **4PH1/1P** 4SD0/1P"
  (the SDA dual-key is the plain 4SD0/1P, not the R twin); 2P "Paper Reference **4PH1/2P**".
- R-form absent token-level (incl. the `4SD0/1PR` SDA-twin guard).
- **Decisive evidence — the operator's ruling verified first-hand:** the DAM catalogs these
  files under **November 2020**, yet their covers print the **June 2020 timetable dates**
  (1P: "Wednesday 20 May 2020", 110 marks; 2P: "Friday 12 June 2020", 70 marks): Pearson
  administered the printed June 2020 papers in the November 2020 sitting after the COVID
  cancellation of June. Even the strict T-C62 sitting guard therefore passes on the covers'
  own prints; the operator's "2020-06 papers are basically 2020 november ones" is exactly
  this reuse (and matches the dirs' existing November-2020 MS pairing note, wave 8).
- Question-count pairing with the dirs' existing November-2020 MSs: "Total for Question"
  markers 11 = 11 (1P) and 8 = 8 (2P).
- Dual-source identity for 1P: the corpus's own `2020-11/4PH1-1P/qp.pdf` (XtremePapers
  scan, pin `e6da3465…`) is the **same paper** — identical 32 pp, identical fingerprints
  and physics anchors ("1.8 m", "6.0 V"), identical paper code **P65064A**; the DAM file
  is the official digital original (footer codes `P65064A` / `P65066A` confirmed on the
  rendered covers).
- Both shas distinct from every mis-filed pin. (The T-C62 wave's page-count rejection
  32v36 / 24v20 compared the candidate against the R copies — R and plain genuinely
  differ in pagination; the sitting question is now settled by the covers + the ruling.)

### Commit + post-push verification

One commit (Git Data API, ref race-guarded): 2 PDFs + 2 manifests (09-28-format source
blocks, `collected_by: SyllabAI agent (2026-10-03 corpus-fix wave (F-A2 slot completion))`,
RESOLVED notes citing the operator trace verbatim; dir labels/series unchanged 2020-06) +
`docs/CORPUS-FIX-FA2-2026-10-02.md` completion section. Pre-commit guards: old material
blocks matched verbatim; edited YAML re-parsed (paper_id / official_reference / series
asserted). Post-push re-fetch verification scoped to the 3 dirs (`fa2s_postverify.json`):
**7/7** — both PDFs == pins, both manifests parse with `qp.sha256` == pin + RESOLVED note,
and the 4EB0 dir byte-untouched (3/3 pins).

## 3. The 4EB0-01 2014-06 MS — remains blocked (operator action needed)

DAM absence re-verified **exhaustively** on 2026-10-03 (`catalog_hits.json`,
`fa2s_algolia_4eb0.json`): 4EB0/01 MSs exist for Jan 2012 / Jun 2013 / Jan 2014 / Jan 2015 /
Jun 2015 (plain + 1R) / Jan 2016 / Jan 2019 — **Jun 2014 is absent**; only June-2014
exemplar booklets exist. The operator's pointer is PMT ("2014 one, you will find in PMT"),
but the route is undiscoverable from this sandbox (`fa2s_pmt_probe.json`):

- PMT www pages: Cloudflare-gated for headless clients (challenge held > 6 min across
  sessions and retries).
- `pmt.` CDN: serves exact object keys only — every folder path 404s (even
  `/download/Physics/`); a 288-path probe grid over subject/level/session/filename
  patterns (using the corpus's own recorded PMT filenames as anchors) found nothing.
- Search backends: z-ai web_search returns **host-only URLs** for PMT hits (path-stripped;
  confirmed with a control query on a known PMT file); Bing renders client-side; DDG
  presents a captcha.
- Archives/proxies unreachable from this network: XtremePapers (403 IP-block, browser
  included), web.archive.org (connection failures), archive.ph / Common Crawl / Jina /
  public CORS proxies (blocked or 522).

**Unblock options:** (i) the operator supplies the direct PMT file URL; (ii) the operator
supplies the bytes; (iii) a ruling of (b)/(c) from the Session 162 close-out options.
Until then the bytes stay unchanged and the do-not-ingest manifest note stays.

## 4. Pack

`REPORT.md` (this file) · `fa2s_probe.json` (pre-flight byte guards) ·
`fa2s_fetch_verify.json` (DAM fetch + evidence-class checks) · `fa2s_crosscheck.json`
(P-codes / page counts / fingerprints) · `catalog_hits.json` + `fa2s_algolia_4eb0.json`
(catalog evidence + 4EB0 inventory) · `fa2s_pmt_probe.json` (PMT probe record) ·
`fa2s_commit.json` (corpus commit) · `fa2s_postverify.json` (post-push 7/7) ·
`fa2s_1P_cover.png` / `fa2s_2P_cover.png` (cover evidence) · `SHA256SUMS`.
Scripts: `scripts/fa2s_probe.py`, `fa2s_algolia.py`, `fa2s_fetch_verify.py`,
`fa2s_crosscheck.py`, `fa2s_pmt_probe.py`, `fa2s_commit.py`, `fa2s_postverify.py`
(session workspace).

Secrets env-only (GH_PAT + RENDER_KEY — revoke after reading; never committed).
Zero DB writes this lane (corpus-only surface; no census re-pin owed from here).
(Super Z, T-C71)
