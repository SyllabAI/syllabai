# Corpus folder-mislabel audit — T-C56 (2026-10-02)

Operator mandate (trace 1a0fbb6c9d6f14f1): "continue the audit of the corpus
folder-mislabel in the queue." The queued item was registered by the bank-defect
lane (T-C45/T-C49/T-C55 remaining-open line, origin: laneD Finding 4 +
follow-up): *"doc-folder mislabels from Finding 4 — folder/source_uri naming vs
byte identity should be audited before the next ingestion wave trusts folder
names."* Read-only lane end to end: zero DB writes, zero corpus writes.

## 1. Method

Canonical corpus = `SyllabAI/syllabai-pastpapers` @ HEAD `029c6ec92`
(2026-09-28T05:28:19Z). Partial clone (blobs <200k + the four wave-relevant
subject dirs) → all 5,281 manifests, all docs, and every PDF of 4ch0/4ch1/
4ph0/4sd0 (420 files) on disk. Layers:

- **L1** — whole-repo manifest scan (5,239 paper dirs): dir name vs
  `paper.official_reference` (C1); printed-ref consistency vs dir identity with
  an alias/remainder-R rule (C2b); PMT "(R)" filename under a plain dir (C3);
  material/sha coverage of the dir's PDFs (C4).
- **L1b** — git-blob duplicate scan over all 10,808 PDF blobs (content-addressed
  free byte-identity evidence).
- **L2** — byte audit of the 420 PDFs: sha256 vs manifest pin, size vs pin,
  page-1..3 printed refs (slash / "(CODE) Paper N" / space forms) vs dir
  identity, session window match; plus verification of both repair waves'
  `repair.promoted_sha256` claims against current bytes.
- **L3** — live-DB cross-check (SELECT-only): documents census, checksum join
  against every current corpus manifest pin, stale/pre-repair sha detection,
  URI-vs-bytes identity, exam_papers link audit, seeded-mislabel resolution.

## 2. Protocol-② recon changed the audit's shape (all verified first-hand)

1. A concurrent lane already repaired the corpus twice: **REPAIR-2026-09-25**
   (chemistry: 14 4CH1 C-dir QPs replaced from quarantine, 8 4CH0 dirs
   re-paired with R bytes preserved in new R dirs, phantom 2020-06 session
   merged into 2020-11) and **CORPUS-FIX-2026-09-28** (23 mis-filed 4PH0 R
   PDFs replaced with the genuine non-R papers, June 2013–2018).
2. A **re-ingest wave landed 2026-09-28T20:18–20:24Z** creating new document
   generations for the repaired chemistry files and relinking exam_papers.
3. Therefore the audit's live-defect space was the **DB generation layer** and
   the **never-repaired specs**, not the corpus dirs the lanes had already
   cured.

## 3. Results

### Corpus (syllabai-pastpapers @ 029c6ec92)

| check | result |
|---|---|
| C1 dir name ↔ manifest official_reference | 0 defects (5,239 dirs) |
| C2b hard — cover is another paper | **0** |
| C2b soft — extra refs beside own (compilation covers) | 162 (benign) |
| C4 material/sha coverage | 0 gaps |
| L1b duplicate blobs | 73 groups = 50 benign Science-Double-Award twins (4CH1/4PH1/4BI1 ↔ 4SD0, identical bytes, same paper token; includes the documented 2020-06↔2020-11 COVID pairing) + 23 quarantine-involved; **0 hostile** |
| L2 manifest sha256 vs actual bytes | 0 mismatches (420 files) |
| L2 repair-block verification | **30/30 PASS** — every promoted sha == current bytes |
| L2 verdicts | 359 OK; 53 benign cover furniture (own ref printed; KCH0/4CH0 double-print + alias-glued patterns, incl. two content-verified special cases: 4PH0-1P 2017-01 MS is genuinely physics with an official cover print error; 4SD0-1BR 2021-01 MS cover legitimately prints the plain-code SDA convention); 5 identity-unparseable (documented broken-ToUnicode / scan classes); 2 no-text-layer (manifest rank-3 listing identification); 1 "MISFILED" reclassified after repair-block sha match (garbage text artifact on a 09-28-replaced file) |

### Live DB (production, read-only)

- Documents census **864V / 8S / 145R = 1017** — total matches the T-C55 pin
  (567V/305S/145R); ~297 SUGGESTED→VALIDATED flips arrived with the 09-28
  evening re-ingest/validation activity (F-A3, recorded).
- 364 QP/MS documents: **182 checksum-match the current corpus**; 182
  unmatched = 170 md-era legacy (`corpus/igcse-chemistry-*/QP.md|MS.md`; 140
  REJECTED / 22 VALIDATED / 8 SUGGESTED) + 12 orphan PDF/OCR generations.
- **18 documents still carry pre-repair mis-filed R bytes** under plain-C
  identities (4CH0 1C/2C June 2013/2014/2016/2017 × QP+MS, 4CH1-1C-201906 qp,
  4CH1-1C-202206 qp): 17 VALIDATED + 1 REJECTED, **0/18 referenced by any
  exam_papers row** (F-A1). No exam_papers row references ANY unmatched
  document (0 of 182).
- exam_papers link audit: every linked QP/MS document's bytes pin at
  identity-consistent corpus dirs (SDA byte-twins verified benign).

### Seeds

- **Seed (a) — RESOLVED END TO END.** laneD's doc `a7a0e028…`
  (`4CH1-1C-202206/qp.pdf`, sha `f21e970f…`) is the orphaned 2026-09-21
  generation holding the mis-filed 1CR bytes. The corpus was repaired
  2026-09-25 (F10 cure, qp-replaced → `22201906…`), the DB re-ingest of
  09-28T20:23Z created the correct generation and the ep rows link it; the
  orphan (VALIDATED, 0 refs) remains in the table. Nothing serves it; its
  chunk layer is the "wrong-paper front-matter" class core PR `02664958a`
  already excludes structurally in serving.
- **Seed (b) — NOT REPRODUCIBLE against canonical stores.** The canonical
  corpus has no 4ch1 2013/2014 dirs; 4CH0-2CR June 2014 links correctly; no
  4CH1/2CR June 2014 ep row exists. Assessed as a laneD-local artifact of its
  resources-store-era downloaded PDF set and lane docmap.

## 4. Findings register

- **F-A1 (needs mandate)** — 18 orphaned pre-repair document generations in
  the live DB (17 VALIDATED) holding mis-filed R bytes under plain-C
  identities. Serving-contained (0 ep refs; core code-excludes the chunks) but
  the data is un-repaired. Disposition: governed retire with reference guards
  (the F-PROD-4 precedent), then census re-pin.
- **F-A2 (needs mandate before the next ingestion wave)** — 44 "(R)"-named
  files under plain-paper dirs in never-ingested specs: **4ph1 1P/2P MS ×18
  sessions 2019–2024** (the current physics spec — highest future relevance),
  4EB0/4EB1 ×11, 6PH0x ×6, 4MA0/4MA1 ×6, 4MB0/4MB1 ×3. PMT-naming evidence
  class; requires the 09-28 three-class verification (byte-exact DAM sha /
  naming / pixel-render) before any of these specs is ingested.
- **F-A3 (observation)** — documents-state drift vs T-C55 census (same total,
  ~297 flips), concurrent-lane activity; census re-pin stays census-last.
- **F-A4 (observation)** — 170 md-era legacy documents (0 ep refs).
- **F-A5 (residual risk)** — 7 byte-scope files not print-verified (scan /
  broken-ToUnicode classes), identity resting on manifest pins + repair/wave
  evidence.

## 5. Bottom line

Folder names are now **trustworthy for the ingested subjects (4ch0/4ch1) and
the wave-active 4ph0/4sd0** at corpus HEAD: zero hostile identity
contradictions, both repair waves byte-verified, every ep row linked to
identity-consistent bytes. The live defect that remains is **DB-side only**
(F-A1's 18 orphans), and the **next ingestion wave must not trust folder names
for the never-ingested specs** (F-A2) without the three-class verification.

## 6. Pack

`l1_findings.json` · `l1b_duplicates.json` · `l2_bytes.json` · `l3_db.json` ·
`l3b_refstate.json` · `verdicts.json` · `REPORT.md` (this file) ·
`SHA256SUMS`. Scripts (SELECT-only, session workspace):
`caudit_l1_manifests.py`, `caudit_l1b_duplicates.py`, `caudit_l2_bytes.py`,
`caudit_l3_db.py`, `caudit_l3b_refstate.py`.
