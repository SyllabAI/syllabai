# T-PS1 OCR LANE + COVID RESOLUTION — the last 3 FLAGGED papers resolved (2026-09-28)

**Authorization:** operator IM trace `1a0e9c4c5305d55d` — "Research web for what
happened in covid and do whatever feels right. And green light the OCR lane."
Extends the Task-58/59/60 delegation chain; same honest provenance on all audit
rows (agent-performed, operator-delegated, NOT an in-app teacher session).

## Outcome

**Census 87 V / 3 F / 1 S / 13 R → 89 V / 0 F / 1 S / 14 R.** The review queue
for the pilot's past-paper bank is EMPTY. teacher_validation_events 0 throughout
(no teacher-validation forgery; all flips carry operator-delegated provenance).
Serving pool (Task-60 formula) 2,581 → **2,646** rev2-embedded chunks (+65 = the
four newly-VALIDATED docs' chunks; rev1 backlog 267 untouched).

## A. 4CH1/1C June 2019 — OCR lane (green-lit)

The Task-60 blocker: attribution 8/15 = 0.53 — 7 of 15 banked stems sit on pages
the deterministic lane could not read.

**O0 probe (read-only).** Live state re-verified: paper FLAGGED, links = the two
0-chunk shells, events 0, no concurrent audit writes.

**O1 deterministic OCR.** QP sha re-verified (`0254a736…`). 9 pages have <150
text-layer chars: [1,2,4,12,16,18,20,26,28]. Rasterized @300dpi (PyMuPDF),
tesseract 5.5.0 psm 3; per-page mean word confidence 0.84–0.92 on content pages
(p2 instruction sheet 0.56 — not content). All PNG/TXT sha256s frozen in
`ocr61/qp/ocr_manifest.json`.

**O2 verification + marks reconciliation.**
- Baseline reproduced: 8/15 stems attribute into the 1.2.0 doc's chunks.
- **6 of the 7 failing stems attribute into their OCR page text at coverage
  1.00** (Q1→p4, Q7→p12, Q11→p16, Q12→p18, Q13→p20, Q15→p26).
- The 7th (Q8, ethene→chloroethene) is NOT on a scanned page: **page 13 has a
  full text layer** — the 1.2.0 question slicer missed it (tab-formatted start).
  The bank stem carries LaTeX (`$\mathrm{C}_{2}\mathrm{H}_{4}$`) vs the print's
  plain `C2H4`; under a uniformly-applied math-span-insensitive mode
  (`$...$` stripped on BOTH sides) it attributes at 1.00 into the page-13 text.
- **Marks reconciliation (printed 110 vs banked 104) — SOLVED:** per-question
  printed totals (pdflane G1 MS layout sequence, QP-side echo OCR-verified on
  p12: "Total for Question 7 = 6 marks") vs bank rows mapped per question:
  every question matches EXCEPT **Q10 (7 printed / 1 banked)**. Q10 = "three
  isomers of C5H12" — the bank holds only the 1-mark part-(a) row; parts (b)–(d)
  (draw an isomer / complete the bromine equation / name the reaction type = 6
  marks) were never banked. 110 = 104 + 6, exactly. Disposition: bank-repair
  backlog (adding rows is a bank lane / operator action — review lanes never
  invent bank content). Also recorded: only 2/15 qv carry scheme rows (bank
  sparsity; Task-59/60 precedent validated papers with 0 scheme rows).
- COVID duplicate check: 6/6 non-empty stems of 4CH1/2C June-2020 attribute
  into the live chunks of the VALIDATED Nov-2020 2C QP (the 7th row is an
  empty-stem row — the known bank-quality class).

**O3 OCR-augmented canonical (engine `pdflane-atoms-ocr` 1.3.0).** Base 1.2.0
canonical never modified; added 7 sections/blocks: 6 OCR pages (verbatim minus a
conservative furniture filter: PMT, DO-NOT-WRITE prints incl. observed OCR-mangled
variants, P58561A barcodes, "Total for Question" echoes per the bridge G3 policy)
+ the page-13 text-layer text for Q8 (provenance `pdftotext-layout`). Source =
the assembled transcription markdown (new checksum space → no dedupe collision
with the 1.2.0 doc); documentId re-derived from (md sha `e3d19a37…`, engine,
1.3.0) via the audited glmocr mirror. Leakage guard clean.

**O4/O4b gates.** Preview mirror AND live chunks (core ChunkingService is the
authority; server P-6 derivation verified byte-exact at ingest):
precedent 14/15 = **0.933** (R4 was 8/15 = 0.53) · math-span 15/15 = **1.000**
→ PASS both modes.

**O5 ingest.** `POST /documents?kind=QUESTION_PAPER` → 201 fresh doc
`98622045` (18 chunks), `/embed` → 18/18 `gemini-embedding-001` @ rev2.

**O6 apply (one fail-closed tx, dry-run first) — COMMITTED 21:19:52Z.**
PLACE QP shell cf68cf74 → `98622045`; PLACE MS shell 39935310 → `02e4c38c`
(genuine corpus MS ingested in Task 60); UNFLAG+VALIDATE paper; VALIDATE
15 qv + 2 schemes + 2 docs. 50 audit rows, in-tx post-asserts green.

**O6b remediation — COMMITTED 21:21:27Z (honest defect record).** The
independent O7 verify caught that O6 wrote the four doc-VALIDATE audit rows but
omitted the documents UPDATE itself. Guarded remediation tx performed the
update (pre-asserts, rowcount 4, post-asserts) and appended 4 corrective audit
rows — the original rows recorded a transition that had not landed; the ledger
keeps both, append-only, with cross-references. (Also caught in dry-run: a
post-assert census dict included `FLAGGED: 0`, which a group-by never emits —
the same class of bug Task 60 hit and fixed pre-commit.)

**O7 independent verify (fresh connection): 0 failures** — census, links,
doc states (VALIDATED, embedded, rev2), shells inert, retired candidates
untouched, 2C children untouched, audit chain 54 rows all
operator-provenanced, events 0.

## B. 4CH1/1C + 4CH1/2C June 2020 — COVID decision (delegated)

**Web research (6 saved searches, `covid_research/s*.json`):**
1. Pearson Edexcel cancelled the Summer (May/June) 2020 International GCSE/IAL
   examinations worldwide (COVID-19; UK schools closed from 20 March 2020;
   Pearson COVID update, qualifications.pearson.com, Apr-2020: "cancellation of
   exams this summer… exams would not take place this summer").
2. An **Oct/Nov-2020 international series took place** (British Council Edexcel
   information sheet Oct-2020-V7: International GCSE timetable & pricing;
   genuine "November 2020" 4CH1 papers/MS in circulation).
3. Papers printed for June were examined in the autumn series: a November-2020
   maths paper circulating publicly still carries "Thursday 4 June 2020"
   timetabling — matching the harness's own evidence.

**Harness evidence (independent of the web):** Task-60 R5 dedupe records prove
the raw-repo "June 2020" bytes ARE the November-2020 print: 2C QP+MS deduped to
`6087c43e`/`45dad920` — the exact linked docs of the VALIDATED Nov-2020 2C row;
1C MS deduped to `c4cd01d6` (uri `4CH1-1C-202011/ms.pdf`).

**Decisions (asymmetric, because the bank state is asymmetric):**
- **4CH1/2C June 2020 → REJECT.** The sitting never happened and the content
  already serves under the VALIDATED Nov-2020 row — validating the June row
  would serve identical content under two sitting labels. Links and children
  untouched; the audit row carries the full evidence + sources.
- **4CH1/1C June 2020 → VALIDATE with supersession context.** The June-printed
  paper examined in Nov-2020 has NO other bank row (no Nov-2020 1C paper row
  exists) — rejecting would orphan the only record of a real examined paper.
  QP = June-printed cover (G6 PASS_WITH_FLAGS, attribution 9/10), MS bytes =
  the genuine 202011 MS. Caveat recorded for the operator: the row's
  session_label says "June 2020" (bank metadata; the sitting was the
  Oct/Nov-2020 series) — renaming/re-mapping is a metadata-lane follow-up.

## Honest wrinkles

- The O6 doc-batch defect (caught by independent verify, remediated, ledger
  append-only) — see above.
- Legacy base-identity URIs on 16 CR docs (Task-60 note) unchanged — immutable
  post-ingestion; content proven by checksum + attribution.
- Q10 parts (b)–(d) (6 marks) + 2 missing scheme rows + 1 empty-stem 10-mark
  row (2C-2020) remain bank-completeness items for the bank-repair queue.
- `Jan-2021 supersession sign-off` remains OPERATOR-owned (not delegated by
  this trace) — the COVID research above is likely relevant to it.
- §D1 retire queue grew: 91 swapped-away shells (Tasks 59+60) + 4 retired
  candidates here (`bbedea1b`, `2c7fb229`, `b0a9f0f8`, `db39d41b`, `f9211ea5`
  — 5 rows incl. the Task-59 1.2.0 QP candidate) — all SUGGESTED, inert.

## Files

`ocr_O0_probe.json` · `ocr_O2_verify.json` (stems, mapping, reconciliation,
COVID duplicate check) · `ocr_O3_build.json` · `ocr_O4_gate.json` ·
`ocr_O4b_live_gate.json` · `ocr_O5_ingest.json` · `ocr_O6_report.json` ·
`ocr_O6b_remediation_report.json` · `ocr_O7_verify.json` ·
`covid_research/s1–s6` (+ `workspace/ocr61/qp/` OCR artifacts with
`ocr_manifest.json`) · `workspace/reingest60/canonical/4CH1-1C-201906-ocr/`
(qp.ocr-augmented.md, qp.canonical.json, chunks_preview.json)
