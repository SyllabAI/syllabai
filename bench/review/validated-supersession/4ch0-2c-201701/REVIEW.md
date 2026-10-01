# Validated-Supersession Review: 4ch0-2c-201701 (4CH0/2C — January 2017)

## What this package proposes

Replace the teacher-VALIDATED bank rows (glmocr-era provenance, pre-pdflane)
with a fresh `pdflane-atoms-draft-v1` product parsed at round-3 parser
`bench/g13-r3-letter-review` (a7f481f, G1.3-r3 mechanisms on top of main
`613c147`). The proposed atoms parse **VERIFIED: zero atom flags,
marksVerified=true**. Discovered during the round-3 drive prestate probe
(the paper was slated for REPLACE and skipped fail-closed on the
zero-teacher-validated-rows-destroyed gate).

## Side-by-side

| dimension | current bank rows (VALIDATED) | proposed (pdflane draft) |
|---|---|---|
| provenance | glm-ocr-qp-v1+glm-ocr-ms-v1 | pdflane-atoms-draft-v1 |
| questions | 8 | 8 |
| marks multiset (per part) | [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2] | [5, 5, 6, 7, 8, 8, 8, 13] |
| sum (parts) | 2 | 60 |
| mark points | 34 (sum 54) | 37 (sum 60) |
| atom flags (n/a for glmocr) | — | NONE — VERIFIED |
| marksVerified (atoms side) | — | True |

- Bank version states: {'VALIDATED': 8}
- Attempt references: 0 | smart-mark results: 0
- Current rows archive: `current-rows-archive.json` (SHA-pinned below)
- Proposed draft: `proposed-draft.json` (SHA-pinned below)

## What supersession does (only on approval)

1. Archive the current rows (this package's export is re-verified byte-exact).
2. Guarded delete of the paper's bank chain — **including the
   8 VALIDATED versions being replaced** (this is
   the step that requires teacher sign-off).
3. POST the proposed draft (all rows SUGGESTED,
   extraction_method=pdflane-atoms-draft-v1).
4. Arithmetic gate: bank=draft=atoms multiset EXACT.

## Sign-off block (fill to approve)

```
approver:
approval-ref:
decision (APPROVE / REJECT):
date:
```
