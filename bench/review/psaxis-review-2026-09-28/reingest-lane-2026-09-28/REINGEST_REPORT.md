# T-PS1 RE-INGEST LANE — 17 of the 20 remaining FLAGGED papers re-ingested & validated (2026-09-28)

**Authorization:** operator IM trace `1a0e99217a715a19` "Proceed with Re-ingest lane" (extends the Task-58/59 delegation chain; same honest provenance on all audit rows — agent-performed, operator-delegated, NOT an in-app teacher session).

## Root cause (proven, not inferred)

The 12 "divergent-candidate" June sittings failed Task-59 attribution because the §D1 orphan
candidates were ingested from **pre-F10-repair corpus bytes** — regional-variant (CR) prints
pinned under base identities. The repaired corpus dirs' `manifest.yaml` records the exact
`previous_sha256` values that match the DB candidates' checksums (e.g. `4CH0-2C-201406`:
previous `aa1b11cf…` = DB doc `712f005c`; promoted `8822a16a…` = the genuine 2C bytes).
Against the repaired bytes the same stems attribute at **0.88–1.00** (vs 0.07–0.29 against
the wrong-variant bytes). The corpus is right; the DB docs were stale bytes.

## Lane (phases R0–R7, all scripts persisted, every write guarded)

| Phase | What | Result |
|---|---|---|
| R0 | enumerate the 20 (12 divergent + 8 4CH0-CR no-content) | 20 papers, 198 qv, 143 schemes, all children SUGGESTED |
| R1 | download 18 corpus sittings (sha-checked vs manifest.yaml) + 2 raw-repo sittings | all 20 sourced |
| R2 | pdflane parse (G6 printed-identity gate) | G6 pass everywhere; 4CH1-2C-202006 PASS_WITH_FLAGS (COVID cover) |
| R3 | atoms→canonical (engine `pdflane-atoms 1.2.0`, P-6 docId re-derivation) | 40 canonical docs, retrieval blocks present |
| R4 | Task-59 attribution gate vs fresh QP chunks | **19/20 PASS** (12 perfect 1.00); only 4CH1/1C Jun-2019 FAIL 0.53 |
| R5 | POST canonical → `/api/v1/teacher/content/documents` + `/embed` (V46 `ver` claim needed) | 19 fresh docs + 21 checksum-dedupe hits; 610 chunks embedded `gemini-embedding-001` rev2 |
| R6 | one fail-closed tx (dry-run first): 34 PLACE swaps + 17×(UNFLAG+VALIDATE) + children | **COMMITTED 20:36:57Z**, 392 audit rows, in-tx post-asserts green |
| R7 | independent landing verify (fresh connection) | **92 checks, 0 failures** |

## Flips (17 papers: +166 qv +124 schemes +34 docs VALIDATED)

All 12 divergent June sittings minus the 2 COVID rows (below), plus all 8 4CH0-CR sittings
2013–2017. Live G5 re-run on the post-swap chunks: ≥0.80 everywhere (1.00 on 15 papers).
Papers census **70→87 VALIDATED / 20→3 FLAGGED / 1 SUGGESTED / 13 REJECTED**.
Serving-eligible pool 2,020 → **2,581** rev2-embedded chunks.

## The 3 that stay FLAGGED (evidence-based, operator-decidable)

1. **4CH1/1C · June 2019** — attribution 8/15 = 0.53. The 7 failing stems sit on 5 scanned
   content pages (no text layer; pymupdf <150 chars/page); the corpus QP is the genuine
   complete paper (28 pp, "TOTAL FOR PAPER = 110 MARKS") vs 104 banked marks. Needs the
   OCR/vision lane + a marks reconciliation before any flip.
2. **4CH1/1C · June 2020** — COVID June/Nov pairing: the raw-repo "June 2020 MS" is
   byte-identical to the `4ch1-1c-202011` MS doc; the fresh June-printed QP ingested fine
   (attribution 9/10) but the MS-side sitting identity is unsettled. Jan-2021-style
   supersession decision belongs to the operator.
3. **4CH1/2C · June 2020** — the raw-repo "June 2020" QP+MS are byte-identical to the
   November-2020 2C docs already linked to the VALIDATED Nov-2020 paper row (the June-printed
   paper was the one examined in November). The June row is a COVID phantom of the same exam;
   merger/supersession = operator decision. Nothing was linked or flipped.

## Honest wrinkles recorded

- **Legacy URIs on 16 CR docs:** the CR sittings' corpus bytes are byte-identical to old DB
  docs ingested pre-repair under base-identity URIs (`4CH0-2C-201406/qp.pdf` on a doc whose
  content is the 2CR print). `source_uri` is immutable post-ingestion; content identity is the
  checksum, and attribution 1.00 + G6 (`--paper-code 4CH0/2CR`) prove the pairing. The
  canonicals with correct CR URIs were deduped away (never stored) — no DB row carries the
  wrong content; 16 rows carry legacy URI labels.
- **ODL second-opinion unavailable** in this harness (missing jar) — recorded per parse as
  `ODL-SECOND-OPINION-UNAVAILABLE`; primary deterministic lanes ran everywhere and the
  attribution gates prove extraction quality.
- **2 empty-stem qv** (4CH0/2C Jun-2014) validated with siblings per Task-59 precedent;
  flagged here for the next bank-quality pass.
- Old 0-chunk shell docs (34) remain SUGGESTED and inert — §D1 retire queue.
- 3 fresh docs stay SUGGESTED orphans: 4CH1-1C-201906 QP+MS, 4CH1-1C-202006 QP (their papers
  did not flip).

## Files

reingest_phase0.json · reingest_R1_state.json · reingest_R2_state.json · reingest_R3_state.json ·
reingest_R4_state.json · reingest_R5_report.json · reingest_R6_report.json · reingest_R7_verify.json
(+ staging tree under agent workspace `workspace/reingest60/` with all canonicals and gate outputs)
