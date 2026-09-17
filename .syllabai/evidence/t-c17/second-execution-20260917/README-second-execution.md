# T-C17 SECOND EXECUTION — 2026-09-17 — operator-directed fresh parse + clean of 2012-Jan

**Trigger (operator, verbatim):** "You can parse the pdf version add it. Make it complete yourself"
— answering session-92's open escalations (E-001 missing Q5/Q11 totals, E-002 content
completeness 120≠98, E-003 MS total absent, E-004 in-table OCR artifacts) by directing a
fresh parse of the official PDFs instead of awaiting the next ocr.z.ai batch.

**Chain of custody:** implemented tooling (syllabai-parser `7b8bcba`) → real conversion
batch (28+28 pages, official PDFs) → corpus_ops intake/verify (rollout-gate dogfood) →
Stage B protocol execution (B.0→B.4) → gates G1–G5 PASS → determinism verified →
negative controls 6/6 DETECTED (+2 recorded N/A) → canonical corpus supersession
(Past-Papers `d31ca91..9746af8`, verify 0 FAIL / 0 WARN).

## 1. Exact versions and SHAs

| Artifact | Value |
|---|---|
| protocol | `CLEAN_VERIFY_PROTOCOL_QP_MS_MARKDOWN.md` v1.1 (central `4fef9c9` tree) |
| corpus-ops / glmocr tooling | syllabai-parser `7b8bcba` (clean_diff G3.2b present; `c9ad722` fail-closed verify present) |
| source QP PDF | `January 2012 QP - Paper 1C Edexcel Chemistry IGCSE.pdf` sha256 `708de70d0823854858069268087cfedbe6f4aba9ba915ddde4799800933dcfff` |
| source MS PDF | `January 2012 MS - Paper 1C Edexcel Chemistry IGCSE.pdf` sha256 `ddf0444b528cf551cbaf2bbcc1f7aa212c902eda53fbb918c2edd83fee1e32c8` |
| raw QP.md (fresh) | `bdb8127872e118abb19ecd4dfe4a1d76772b6fde5082b4715d22c4de9070df98` |
| raw MS.md (fresh) | `1a22f26071e9d67e46a925e5fac9e23d2b7f5cb1bc4be18faabc3ae8507a0cc2` |
| clean QP.md | `66e878691c25e1c410e5e5735570474c0142e2e27bf7b5a8ced0dc54d9827038` |
| clean MS.md | `59e4abd48482fa996089dda764275646a4b49851e835c0c8c4cea2b5aa92fa33` |
| canonical corpus commit | SyllabAI/Past-Papers `9746af8` (supersession; prior raw `136b500f…`/`f2afa60d…` archived + checksum-verified) |

## 2. OCR engine — HONEST DEVIATION

The batch was produced by the **internal-gateway vision endpoint**
(`POST {baseUrl}/chat/completions/vision`, served model **`glm-5v-turbo`**), NOT the
ocr.z.ai `layout_parsing` service (no PAAS key exists in the sandbox; `api.z.ai` returns
401 with the internal JWT). Consequences, all recorded in `ocr-batch-manifest.json`:

- **no layout stage → no crop figures**; the fresh raw carries zero image islands
  (the prior raw's 11 assets are retained in the canonical session folder, referenced by
  the archived raw). The `ollama`-backend precedent ("model-only inference has no layout
  stage; the manifest records this honestly") applies.
- per-page markdown frozen as received; **downstream-only determinism** (same discipline
  as every OCR batch: the original GLM-OCR website batch is not byte-reproducible either).
- prompt sha256 per document recorded (`engine.prompt_sha256_per_document`); the MS pages
  were re-transcribed under a strengthened prompt (rule 12: keep M-codes and marks values
  as their own cells) after the first pass shifted the extractor's column layout —
  an engine-definition fix at the source, never a post-hoc document edit.
- one page (MS p6) first returned an ```` ```html ````-fenced table → re-transcribed
  (fail-loud backend contract: fenced output = malformed → retry, never hand-edited).
- **the true "next ocr.z.ai batch" rollout gate (T-C16 §10.2) remains owner-held** — a
  batch from THAT engine still does not exist. What this execution dogfooded is the
  corpus_ops + protocol chain on a real, complete, operator-directed batch.

## 3. Gates (executed with the real tools; python twin for G1 — Java 25/mvn unavailable)

| Gate | Result | Evidence |
|---|---|---|
| G1 pair end-to-end, five-file bundle | pass (deviation: conformance-verified python twin, parity CI-enforced; Java unavailable in sandbox) | clean/bundle/* |
| G2 health, zero FAIL | pass — 0 FAIL findings (REVIEW-only: extractor part-marks attribution ×11 + MS paper total absent-as-printed) | gate-G2-clean-health.json |
| G3 raw-vs-clean diff | PASS — G3.1 11=11; G3.2 37 shared entries 0 mismatches; G3.2b 11 totals 0 mismatches (Q5=11, Q11=11 survive); G3.3 0=0; G3.4 no new warning classes (numbering-gap warnings 16→8); G3.5 no conflict | gate-G3-clean-diff.json |
| G4 provenance completeness | pass — B.0 anchors vs MANIFEST; ledger line-math exact (846−98−3=745; 1256−56−2=1198); 0 escalations | clean-report.json |
| G5 honesty counters | pass — `unterminatedTableBlocks`/`orphanMathFences`/`unclosedCenterDivs`/`greedyMathLines` absent from clean parses (counter key: `provenance.extractionParams`); `signedUrlFigureRefs` 0=0; `entityDecodedLines` 0→0 | ocr-batch-manifest.json + canonical parses |
| determinism | verified — clean re-run content-identical (report modulo `generated_at_utc`); clean_diff re-run byte-identical | scripts/tc17_gate_runner.py |
| negative controls | 6/6 DETECTED: part-mark mutation→G3.2 FAIL; phantom question+minted total→G3.1+G3.2b FAIL; orphan `$$`→`orphanMathFences=1`; QWC `*(c)`→`* (c)`→list_item reclassification; tampered raw→B.0 HARD STOP; new warning class→G3.4 FAIL. 2 N/A recorded with session-92 cross-refs (image-island reformat, entity pre-decode — no islands/entities in this parse; both DETECTED on the real pair in session-92 evidence) | negative-controls.json |

## 4. Completeness recovered (the point of the execution)

- printed per-question totals now present for **all 11 questions**:
  10, 8, 13, 8, **11**, 14, 9, 10, 18, 8, **11** — sum **120** = printed paper total;
  witnesses kept verbatim in the raw: "The total mark for this paper is 120." +
  "TOTAL FOR PAPER = 120 MARKS".
- raw-pair health BEFORE cleaning: **REVIEW-only, zero FAIL** (the prior raw FAILED here
  at 120 vs 98) — raw-pair-health.json.
- raw QP draft extracts **exactly 11 questions** (the prior raw's OCR produced 27 draft
  questions from boilerplate spillover); after cleaning: 11 questions, no spillover.
- prior in-table OCR artifacts (E-004, e.g. the fused `H2O和O2` cell) are gone — the
  fresh transcription is clean.
- printed MS "Total 11 marks" for Q3 vs QP "(Total for Question 3 = 13 marks)" is a
  **property of the printed documents** (present in the prior raw too, line 48); recorded
  as observation N-001 in the clean report — nothing changed, nothing reconstructed.

## 5. Protocol↔implementation discrepancies found in this execution

1. **G2 sidecar-witness integration remains unimplemented** (session-92 finding,
   unchanged): health.py reads only pair-CLI drafts. Non-blocking here: the printed
   totals live in the raw/clean text itself, so the paperTotal check fires on real
   witnesses.
2. **Honesty counters live at `provenance.extractionParams`**, not `provenance.params`
   — the first G5/NC-4 probe read the wrong key and produced a FALSE NOT-DETECTED /
   false-pass impression. Tooling-adjacent lesson recorded here; no code change.
3. **An orphan `$$` at EOF** does not increment `orphanMathFences` in the python twin
   (the bounded scan counts the orphan only when a structural boundary or a later
   fence is met before EOF; at EOF the scan exits through the same `closed=False`
   path — verified: mid-document control DETECTED, EOF variant silent). Recorded for
   the parser owner; the ratified control (mid-document) is unaffected.
4. G1 Java CLI could not run in this sandbox (no maven; Java 21 vs required 25) —
   executed via the python behavioral twin whose Java parity is fixture-pinned 16/16
   in CI; recorded as an environment limitation, not a product result.

## 6. Where everything lives

- canonical corpus (raw + clean + manifest + archived prior raw): **SyllabAI/Past-Papers
  `9746af8`** — `paper 1/2012-Jan/{QP.md,MS.md,clean/*}` + `*.raw-superseded-20260911.md`;
  `corpus_ops verify` over the full tree: **0 FAIL / 0 WARN / 0 informational**.
- this evidence directory: gate reports, negative controls, raw health, OCR batch
  manifest, and the five execution scripts (deterministic, re-runnable).
- tracker: TODO.md T-C17 row (second-execution append); PROGRESS.md session finding.
