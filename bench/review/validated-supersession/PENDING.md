# Pending Validated-Supersession Reviews

Two papers carry teacher-VALIDATED glmocr-era bank rows whose pdflane
replacements now parse VERIFIED (zero atom flags, marksVerified=true,
parser main `613c147`). The standing convention forbids destroying
teacher-validated rows without explicit teacher approval — these packages
stage the decision; nothing is executed until sign-off.

| slug | paper | current rows (VALIDATED) | proposed (pdflane) | package |
|---|---|---|---|---|
| 4ch1-2c-202101 | 4CH1/2C January 2021 | 7q / **50 marks** (glmocr, incomplete vs printed 70) | 7q / 70 marks, VERIFIED | [4ch1-2c-202101/REVIEW.md](4ch1-2c-202101/REVIEW.md) |
| 4ch1-2cr-202001 | 4CH1/2CR January 2020 | 7q / **43 marks** (glmocr, incomplete vs printed 70) | 7q / 70 marks, VERIFIED | [4ch1-2cr-202001/REVIEW.md](4ch1-2cr-202001/REVIEW.md) |

## Process

1. Reviewer opens the package's REVIEW.md (side-by-side + SHA-pinned
   archive of current rows + proposed draft) and spot-checks content.
2. Reviewer fills the sign-off block (approver + approval ref + decision).
3. On APPROVE, the operator runs:

   ```
   python3 scripts/validated_supersede.py --slug <slug> \
       --approved-by "<name>" --approval-ref "<ref>"
   ```

   The tool re-verifies the package SHAs and the live prestate, re-archives,
   performs the guarded delete (the VALIDATED rows it replaces are exactly
   the archived ones), POSTs the draft, and gates on arithmetic
   (bank=draft=atoms multiset EXACT). The approval rides in
   `g14_validated_supersede_report.json`.
4. The operator mirrors the decision into the records tracker.

On REJECT: keep the current rows; file the reason in the package's
REVIEW.md sign-off block and record it in the tracker.
