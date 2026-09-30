# Validated-Supersession Review: 4ch1-2c-202101 (4CH1/2C — January 2021)

## What this package proposes

Replace the teacher-VALIDATED bank rows (glmocr-era provenance, pre-pdflane)
with a fresh `pdflane-atoms-draft-v1` product parsed by parser main
`613c147` (G1.3-r2). The proposed atoms parse **VERIFIED: zero atom flags,
marksVerified=true**.

## Side-by-side

| dimension | current bank rows (VALIDATED) | proposed (pdflane draft) |
|---|---|---|
| provenance | glm-ocr-qp-v1+glm-ocr-ms-v1 | pdflane-atoms-draft-v1 |
| questions | 7 | 7 |
| marks multiset | [1, 1, 5, 5, 9, 14, 15] | [5, 5, 8, 9, 14, 14, 15] |
| sum | 50 | 70 |
| mark points | 28 | 39 |
| atom flags (n/a for glmocr) | — | NONE — VERIFIED |
| marksVerified (atoms side) | — | True |

- Bank version states: {'VALIDATED': 7}
- Attempt references: 3 | smart-mark results: 0
- Current rows archive: `current-rows-archive.json` (SHA-pinned below)
- Proposed draft: `proposed-draft.json` (SHA-pinned below)

## What supersession does (only on approval)

1. Archive the current rows (this package's export is re-verified byte-exact).
2. Guarded delete of the paper's bank chain — **including the 7
   teacher-VALIDATED version rows**. This is the step the standing convention
   forbids without explicit teacher approval; that is why this package exists.
3. POST the proposed draft (lands SUGGESTED, pdflane-atoms-draft-v1).
4. Poststate probe + arithmetic gate (bank=draft=atoms multiset EXACT).

The approval reference and approver are recorded in the drive report and the
records tracker.

## Sign-off block (fill in before running scripts/validated_supersede.py)

```
Paper:            4ch1-2c-202101 (4CH1/2C — January 2021)
Approver:         ____________________________
Approval ref:     ____________________________
Decision:         [ ] APPROVE supersession   [ ] REJECT (keep current rows)
Reviewer notes:   ______________________________________________
```
