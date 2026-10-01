# Card review-sheet header parser — Task-54 regex-fallback fix (code lane)

Date: 2026-10-01. Operator directive: "sheet-generator regex" (IM trace `1a0f589bdf33b151`).
Lane: T-C27 card review-sheet tooling.

## Provenance (honest)

The original sheet generator (`scripts/generate_teacher_card_review_sheet_20260928.py`)
was an **agent-side sandbox script** — it never lived in a repo and was **lost in the
sandbox rollbacks of 2026-10-01**. It is not recoverable byte-for-byte. What survives:

- the defect analysis (Task 54, `bench/evidence/flagged3-source-verify-2026-09-28/REPORT.md`);
- the 3 affected cards' canonical JSON (same dir, `flagged3_canonical.json`) with their
  verbatim true header lines;
- the pinned sheet itself (`teacher_card_review_sheet_2026-09-28_completed.md`,
  sha256 `89c07146…d67e`) showing the broken renderings `#### #207 · Q? · 0 marks · ?`
  (sheet lines 1589/2112/2209 for #207/#278/#291).

This bundle therefore **reconstructs the parser core** (the defective part) with the fix,
not the whole 298-card generator (whose remaining pipeline is DB-coupled and out of scope;
the pinned sheet and the DB wave it drove are historical records and are untouched).

## The defect (Task 54 finding, verbatim basis)

The generator's header regex **required a `spec:` segment**. The 3 honest no-linkage
cards omit that segment, so the **whole match failed** and the fallback fabricated
`qnum="?"`, `marks=0`, `qtype="?"` → `Q? · 0 marks · ?` on the sheet — discarding
`Q3 / 11 / STRUCTURED`, `Q1 / 5 / STRUCTURED`, `Q1 / 4 / STRUCTURED`, which the cards'
own textBlocks carry (bank-verified in Task 54: leaf sums 11=2+2+1+2+4, 5=4+1, 4=4×1).

## The fix (this bundle)

`card_sheet_header_parser.py`:

1. **Segment-scanning parser** (`parse_card_header`) instead of one monolithic regex —
   every field parses independently; one missing optional segment can never nuke the rest.
2. **`spec:` is optional** (absent or empty → `spec=None`), rendered via
   `render_spec_segment` as `(none — card has no spec linkage)` (the en-route wording
   already used by the lane for these cards).
3. **Fail-closed**: a header missing a required field raises `HeaderParseError`.
   The renderer has **no fallback path** — `render_sheet_header` requires fully parsed
   fields, so `Q? · 0 marks · ?` can never be emitted again (also AST-guarded in tests).

Header grammar (pipe-delimited, from the live card corpus):
`Q-Card | <code> | <session> | Q<num> | marks: <int> | type: <qtype> [| spec: <codes>] | stem: <text>`

## Verification

`python3 test_card_sheet_header_parser.py` → **16/16 OK** (see `test_output.txt`):

- the 3 REAL no-linkage headers (verbatim from `flagged3_canonical.json`) parse to their
  bank-verified true values, and the renderer output differs from the pinned broken lines
  exactly as intended (`#1: #### #1 · Q3 · 11 marks · STRUCTURED`);
- spec-present headers parse unchanged (format regression guard);
- fail-closed on missing marks/qnum/type, wrong marker, duplicate/non-integer marks,
  unrecognized segments, unparsed renderer input;
- stem content containing `|` survives; empty `spec:` maps to the honest no-linkage note;
- AST-based guard: no `Q?` fabrication path exists in module code constants.

## Usage

```python
from card_sheet_header_parser import parse_card_header, render_sheet_header, render_spec_segment
f = parse_card_header(header_line)          # raises HeaderParseError on bad input
render_sheet_header(seq, f)                 # '#### #207 · Q3 · 11 marks · STRUCTURED'
render_spec_segment(f)                      # codes, or the honest no-linkage note
```

CLI smoke: `python3 card_sheet_header_parser.py [headers.txt]`

## Rollback-proofing note

The original script's loss to a sandbox rollback is exactly why this kit is committed to
the records repo now: future sheet work should import from this location, not from
agent-side `scripts/`.
