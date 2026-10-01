# T-C17 execution evidence — 2026-09-17 (Session 92)

First execution of `CLEAN_VERIFY_PROTOCOL_QP_MS_MARKDOWN.md` v1.1 (Stage B
clean-and-verify) against a REAL GLM-OCR session, plus the gate negative-control
suite. Executed in a sandbox copy of `Past-Papers/paper 1/2012-Jan`; the canonical
corpus clone was never modified (verified by B.0 anchors at every re-run).

## Exact versions

- protocol: `CLEAN_VERIFY_PROTOCOL_QP_MS_MARKDOWN.md` v1.1 (grammar contract RATIFIED)
- tooling under test: syllabai-parser `8d2e4db` (T-C16 implementation, CI green run 35159090681)
- strengthenings applied during this execution (both discovered by negative controls,
  both test-covered, pushed as syllabai-parser `c9ad722` + `7b8bcba`):
  - `c9ad722` corpus_ops verify: pair-completeness now fails closed when a
    manifest-listed QP/MS file is missing ON DISK (was listing-only), + document
    checksum verification against the manifest
  - `7b8bcba` clean_diff G3.2b: question-level printed-total identity (a mutated
    `(Total for Question N = M marks)` line slipped past part-level G3.2)
- final gate suite executed with the byte-identical tree that became `7b8bcba`
- local test suites: corpus_ops 40/40, glmocr 41/41, Java↔Python conformance FULL PASS

## Input bundle

- session: `Past-Papers/paper 1/2012-Jan` (real GLM-OCR output, Stage-A'd:
  11 assets, manifest current, operator cleanup recorded)
- raw QP sha256 `136b500f077e97400fa8509adecf11e0161389a87bff0d9e17a1c2061fa0a639`
- raw MS sha256 `f2afa60dc10c541d44c3a1f98b13bae7820f370935d024117005722f06f3369b`
- both match `paper 1/MANIFEST.json` documents (B.0 anchor verified)

## Files

- `clean-report.json` — clean-report-1.0: B.0 captured totals + identity, operations
  ledger (52 QP + 40 MS lines removed, per-class), 4 escalations (awaiting_operator),
  gate_results {G1 pass, G2 FAIL, G3 pass, G4 pass, G5 pass}, verbatim gate evidence
- `gate-G3-clean-diff.json` — the positive-control G3 report (G3.1–G3.5 all pass)
- `negative-controls.log` — 8/8 unsafe transforms DETECTED/REJECTED
- `verify-real-paper1.log` / `verify-real-paper2.log` — read-only `corpus_ops verify`
  over the FULL live corpora (paper 1: 41 sessions / paper 2: 41 sessions,
  164 documents checksum-verified): 0 FAIL, 0 WARN each

---

## Second execution — 2026-09-17 (operator-directed fresh parse; session CLEANED)

Operator directive ("You can parse the pdf version add it. Make it complete yourself")
triggered a fresh full-document OCR of the official 2012-Jan PDFs and a second, complete
T-C17 execution. Session 2012-Jan is now **CLEANED** (G1–G5 pass, determinism verified,
negative controls 6/6 DETECTED + 2 N/A cross-referenced above); the canonical corpus was
superseded verify-green at SyllabAI/Past-Papers `9746af8` (prior raw archived, checksums
verified). Full detail, exact SHAs, engine provenance (honest deviation: gateway vision,
not ocr.z.ai), discrepancies, and the re-runnable scripts:
`second-execution-20260917/README-second-execution.md`.
