# Source Verification — the 3 FLAGGED cards (#207 / #278 / #291)

**Date:** 2026-09-28 · **Trigger:** operator instruction "Source verify the 3" (trace 1a0e75e9cd346a15)
**Scope:** the 3 cards the operator FLAGGED in the T-C27 card wave (run `a5d13c0a-2503-4d06-bb14-9397e9a1cf37`, sheet sha256 `89c07146…d67e`), whose flag note reads verbatim: *"0 marks, no syllabus spec linkage, and Q? / unknown question sequence; needs source verification."*
**Method:** SELECT-only DB probes (rolled back) + primary-source comparison across four independent layers: card `canonical_json` → bank row (`questions`/`question_versions`/`question_parts`) → question spec linkage (`question_spec_points`) → real paper text (`document_chunks` of the sitting's QP/MS documents). Zero production writes.

## The 3 cards

| sheet # | documents.document_id | state | bank row (`external_ref`) | bank marks | spec points |
|---|---|---|---|---|---|
| 207 | `1c15d529-661b-53a7-a8ed-a934328e6afb` | FLAGGED | `4ch1/past-papers/2020-01/4CH1-2C#q3` | 11 | 0 |
| 278 | `ee882008-88ca-5952-af9c-5505c8f76661` | FLAGGED | `4ch1/past-papers/2020-06/4ch1-2CR#q1` | 5 | 0 |
| 291 | `1195ca6c-0ecd-5890-b63e-4c2df7ebddba` | FLAGGED | `4ch1/past-papers/2023-01/4CH1-2CR#q1` | 4 | 0 |

All three are EXTERNAL_QUESTIONS documents created 2026-09-26 by `tc27-card-bridge` (engineVersion 1.0.0), each carrying `source.uri` + `source.checksum` (SHA-256) in canonical_json.

## Finding 1 — "0 marks / Q?" was a sheet-renderer artifact, not card content

The review-sheet generator parses each card's header line with a regex that **requires a `spec:` segment**:

```
Q-Card | <paper> | <session> | Q<n> | marks: N | type: T | spec: <codes> | stem: …
```

These 3 cards — and only these 3, because they are the no-linkage cards — have a header **without** the `spec:` segment (e.g. `… | type: STRUCTURED | stem: This question is about copper and its compounds.`). The regex fails, the generator falls back to `qnum="?"`, `marks=0`, `qtype="?"`, and the sheet renders `#207 · Q? · 0 marks · ?`. The cards' own header text carries the true values: **Q3 / 11 marks**, **Q1 / 5 marks**, **Q1 / 4 marks** — matching the bank rows exactly. The review sheet itself is sha256-pinned and stays untouched; this note records the artifact for any future sheet generation.

## Finding 2 — every card is a faithful bridge of its bank row

Normalized (whitespace-collapsed, lowercased) comparison of card stem vs `question_versions.stem`:

- **#207**: card stem (48 ch) == bank stem (48 ch), byte-equal after normalization.
- **#278**: card stem (75 ch) == bank stem (75 ch), byte-equal after normalization.
- **#291**: card stem (155 ch) is a strict **prefix** of the bank stem (246 ch) — consistent with the documented "token-subset of print" emission rule; the bank stem continues `…answer, put a line through the box 1 In this question the answer to each part is a number.`

Bank-side marks corroborate independently of the stem header via `question_parts` (leaf-level sums):

- **#207**: parts a(2), b(5, parent of b-i/b-ii/b-iii), b-i(2), b-ii(1), b-iii(2), c(4). Naive sum is 16 because parent part b double-counts its children; **leaf sum = 2+2+1+2+4 = 11 = bank marks**.
- **#278**: parts a(4) + b(1) = **5 = bank marks**.
- **#291**: parts a(1)+b(1)+c(1)+d(1) = **4 = bank marks**.

## Finding 3 — anchor to the real paper text

- **#207 — FULLY ANCHORED.** QP document `a3d8186e…` (4CH1/2C Jan 2020) chunk 3 reads: *"…4ch1/2c | paper 2c | q3 | pp.6–7 this question is about copper and its compounds. copper is a metal used for electrical wiring. explain why copper is a good conductor of electricity. this apparatus is used to investigate the electrolysis of copper(ii) s…"* — the stem, qnum, page anchor, and the real 11-mark copper question all present. The thin stem is the bank's intro-line granularity (same style as sibling bank rows, e.g. `#q2 "Crude oil is a mixture of hydrocarbons."`), not a data fault.
- **#291 — FULLY ANCHORED.** MS document `d5c83de2…` chunk 0: *"mark scheme for question 1 q1 p1 (1 mark): 7 … note: (total for question 1 = 4 marks)"* — independent mark-scheme confirmation of 4 marks. QP document `1fd28254…` chunk 0 carries the same instruction-block text the bank stem inherited (*"…and then mark your new answer with a cross . answer, put a line through the box 1 in this question the answer to each part is a number…"*) plus the real Q1 opener. The instruction block ("Answer ALL questions. Some questions must be answered with a cross in a box…") is genuine page chrome of the paper's front page, swept into the bank row's stem span by the `pdflane-atoms-draft-v1` extraction and faithfully inherited by the card.
- **#278 — PARTIALLY ANCHORED (DB cross-check unavailable).** The sitting's QP (`2ad68057…`) and MS (`d110adef…`) documents have **0 rows in `document_chunks`**, so no DB paper-text cross-check is possible for this sitting. What is verified: card == bank row byte-for-byte; parts a(4)+b(1)=5 with real apparatus question prompts ("Complete the table by giving the name of each piece of apparatus." / "Which piece of apparatus can be used to measure the volume of a liquid? A B C D"); extraction confidence 1.0. The stem's "Answer ALL questions." prefix is the same front-matter chrome pattern as #291.

## Finding 4 — the spec linkage is genuinely absent (the "3 honest skips")

`question_spec_points` contains **0 rows** for all 3 bank questions. This matches the T-C27 record verbatim: *"specCodes in retrieval block 295/298 … 3 honest skips"*. These ARE the 3 skips. Their retrieval blocks carry `specCodes: null` and their card headers omit the `spec:` segment — which is also what tripped the sheet-renderer regex (Finding 1).

## Verdict

| card | content faithful to bank | bank marks correct | paper-text anchor | spec linkage | verdict |
|---|---|---|---|---|---|
| #207 | yes (exact) | yes (11; leaf parts sum 11) | QP chunk 3 ✓ | none (honest skip) | **SOURCE-VERIFIED — genuine question, thin stem (bank granularity)** |
| #278 | yes (exact) | yes (5; parts 4+1) | no DB chunks for sitting; parts corroborate | none (honest skip) | **SOURCE-VERIFIED (partial anchor) — genuine question + front-matter chrome in stem** |
| #291 | yes (prefix, token-subset rule) | yes (4; parts 4×1; MS confirms "total for question 1 = 4 marks") | QP chunk 0 + MS chunk 0 ✓ | none (honest skip) | **SOURCE-VERIFIED — genuine question opener + front-matter chrome in stem** |

None of the 3 is fabricated, mis-quoted, or wrong-paper content. Their honest weaknesses: (a) zero spec linkage — by design an honest skip; (b) stems that are thin (#207) or carry page chrome (#278, #291) — inherited from the bank extraction, uniform risk class for the card corpus; (c) #291's card stem in particular contains no actual question text beyond the instruction block — the real Q1 opener lives in the bank stem and the paper, not in the card.

## Disposition (operator-owned, per the standing boundary)

The agent does not assert validation. Options, all legitimate given these findings:

1. **Keep FLAGGED** (no action) — they never serve (serving gate excludes FLAGGED), zero risk. Recommended if corpus hygiene for serving is the only concern; they are already inert.
2. **Operator-named flip to VALIDATE** — content is genuine and faithful to source; the flag drivers (renderer artifact + honest skip) are now explained. Would require a named operator decision (reply in chat or a mini-sheet with the 3 seqs); the importer path (target_type='question' vocabulary) is proven.
3. **Repair direction (data lane, later)** — if the corpus should carry fuller stems, the fix is upstream in the bank (`pdflane-atoms-draft-v1` stem spans swallowing front-matter) and the bridge's emission, not in these documents.

## Evidence

- `flagged3_canonical.json` — the 3 cards' full canonical_json (live DB, SELECT-only)
- `verify_matrix.json` — machine-readable verification matrix (containment, marks, parts, spec counts, chunk hits)
- `bank_rows.json` — bank rows + sitting context for the 3
- Scripts: `scripts/flagged3_source_probe_20260928.py`, `scripts/flagged3_bank_probe_20260928.py`, `scripts/flagged3_verify_matrix_20260928.py`, `scripts/flagged3_close_loose_ends_20260928.py` (all SELECT-only, rolled back)
- Prior records: run `a5d13c0a-2503-4d06-bb14-9397e9a1cf37` (import_report.json), T-C27.yaml landed block ("3 honest skips"), snap-005 freeze, R6-GENERATION-NOTES.md
