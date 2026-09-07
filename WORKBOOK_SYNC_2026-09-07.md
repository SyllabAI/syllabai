# Workbook Synchronization Record — 2026-09-07

## Status

The project tracker has been consolidated and cleaned against the 2026-09-07 architecture decisions. The local canonical workbook artifact is:

`SyllabAI_Master_Project_Canonical_2026-09-07.xlsx`

## Synchronized architecture extensions

- Subject-first / SpecificationPoint: F-164..F-170
- Mock Exam Generator support: F-171..F-176
- Teacher/classroom architecture: TFA-01..TFA-08 and existing teacher feature families
- Question Attempt & Learning Evidence: F-055..F-059 and integrations
- Learning-first Recommendation System: existing F-087..F-093 family plus architecture/evaluation constraints

## Cleanup performed

- Removed duplicate legacy feature rows for F-059, F-078 and F-154 from the consolidated tracker.
- Preserved the richer/canonical row for each duplicated feature ID.
- Confirmed F-169/F-170 are the subject-architecture rows; mock supporting features use F-171..F-176.
- Consolidated repository mapping to the five-repository architecture: `syllabai`, `syllabai-web`, `syllabai-core`, `syllabai-parser`, `Past-Papers`.
- Kept former knowledge/assessment/learner-model/AI/research areas as modules inside `syllabai-core`.
- Corrected dashboard counts after duplicate removal: 168 unique feature rows.
- Removed the duplicated Governance architecture-sync entry.
- Formula/error scan: no `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, or `#N/A` matches.

## Source-of-truth rule

The definitive tracker remains the project workbook. The committed TSV addenda remain text-form controlled inputs for architecture-specific changes; they must not be treated as competing feature inventories. When the repository binary workbook is refreshed in Git, the workbook and TSV representation must be synchronized in the same controlled change.

## Binary artifact note

The cleaned canonical workbook is generated and verified in the current workspace. The GitHub connector available to this session does not provide a direct local-file upload operation for binary XLSX content, so this synchronization record is committed now rather than falsely claiming that the binary workbook has been pushed to GitHub.
