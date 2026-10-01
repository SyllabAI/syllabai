# A1 bank backfill — execution evidence (2026-09-22)

Lane: retrieval/parser G1 chain, Task 37–38. Operator directive: "proceed with
A1" (atoms→draft-1.0 converter, zero core change) after the scoping pass
verified that the G1 parser upgrade itself had already landed
(parser `9f38dda` + `dffeb1d`, corpus landing `26d4e028`).

## What shipped

1. **Converter** (parser `4bdab55`): `tools/pdflane/atoms_to_draft.py` —
   deterministic atoms/1.1 → past-paper-draft.json/1.0 bridge, 12 tests
   (`tests_atoms_to_draft.py`). Fidelity rules pinned in the module docstring:
   marks=0 alternatives merged (core's `Math.max(marks,1)` would inflate),
   pool caps teacher-visible on the head row, levels flattened to one point at
   maxMarks, allow/reject/ignore/guidance → prefixed acceptance entries,
   `confidence=1.0` + `reviewRequired=true` (everything lands SUGGESTED).
   `extraction_method = pdflane-atoms-draft-v1` (≤120 chars, bank-queriable).
2. **Corpus regeneration** (sandbox): all 86 paper dirs re-parsed with current
   parser main (13–35 s/paper), converted, gated per paper. Gate report:
   `a1_batch_gate_report.json` (86 slugs).
3. **Drive** (`a1_drive_report.json`): 4 papers (3 REPLACE + 1 NEW) through
   archive → guarded delete → POST `POST /api/v1/teacher/content/past-papers`
   (201). Auth: 10-min ADMIN/TEACHER JWT minted from SYLLABAI_JWT_SECRET +
   identity.json — the sanctioned g1-finish pattern. No pipeline/code change.

## Drive results (all counts_match_draft = true, all subject 4CH1, all SUGGESTED)

| slug | class | old rows deleted | new q/parts/points |
|---|---|---|---|
| igcse-chemistry-4ch0-1c-2012jan | REPLACE | 11 q / 25 mp / 1 bridge | 11 / 85 / 119 |
| igcse-chemistry-4ch1-1cr-2023jun | REPLACE | 11 q / 39 mp / 1 bridge | 11 / 72 / 59 |
| igcse-chemistry-4ch1-2cr-2023jan | REPLACE | 8 q / 36 mp / 1 bridge | 8 / 48 / 40 |
| igcse-chemistry-4ch1-2cr-2025jun | NEW | — | 7 / 47 / 37 |

Bank totals: questions 1,447→1,454; mark_points 4,294→4,449; exam_papers
94→95 (deleted 3, added 4). Archived old rows were ALL SUGGESTED — **zero
teacher-validated rows destroyed**. `glm_ocr_bridge_records` rows (1/paper)
archived byte-exact then deleted WITH their papers per the G7 supersession
precedent (the G1 documents landing's archive-before-delete pattern); the
glmocr drafts remain fully recoverable from the archives.

## Archives

`download/a1_bank_archive/<slug>/archive.json` + SHA256SUMS: full row export
(exam_papers, questions, question_versions, question_parts, mark_schemes,
mark_points, question_topics, question_spec_points, question_options,
glm_ocr_bridge_records) written BEFORE any delete. Delete transaction
asserted prestate (attempts=0, smart_mark_results=0, agreement_evals=0) and
poststate (0 rows remain) before commit.

## Honest gate report (the real G8 flag state)

- 86 corpus dirs = 83 qp+ms + 3 ms-only (SKIP-MS-ONLY — bank stays docs-only
  per scope B: no QP ⇒ no stems ⇒ no questions, by construction).
- **77/83 HOLD-FLAGS**: atoms `marksVerified=false` (PART-MARKS-MISMATCH /
  MS-POINTS-DONT-CLOSE / MS-PART-NO-POINTS / MS-POINT-UNKNOWN-PART /
  MS-QUESTION-MISSING). The G1 landing verified the SAMPLE (4CH0/1C jan2012)
  and cleared MS-UNCLASSIFIED-ROW corpus-wide; corpus-wide MARK-CLOSURE was
  never claimed and is not done. These 77 keep their glmocr bank rows until a
  mark-closure lane fixes the products (the true "G8 flag clearance").
- 2 HOLD-NO-DOC (4ch1 1CR/2CR 2024jun): verified atoms but the doc lane has
  no QP documents for them (MS only) — doc-lane ingest first.
- 1 FAIL-PARSE (4ch0-2c-2012jan): emit gate V1 escalation — needs parser
  attention, disclosed.
- 6 verified-of-83 = the honest baseline the mark-closure lane starts from.
- Identity preservation: `resolveSubject` sanitizes `qualification+subject`;
  drafts craft it back to each paper's existing subject code (91 papers sit
  under 4CH1, 3 under IGCSECHEMISTRY) — zero subject-row drift, no new
  subjects/curriculum versions created.
- Doc-map discovery: two corpus URI generations exist
  (`corpus/igcse-chemistry-<slug>/(QP|MS).md` and `4CH1-2CR-202301/qp.pdf`);
  legacy engine-1.0.0 duplicate-uri docs referenced by REJECTED null-code
  exam_papers are excluded by version preference.

## Post-drive state

- 4 new papers verified live: subject_code=4CH1, validation_state=SUGGESTED,
  QP+MS doc pointers both live (the 13 pre-existing dead MS pointers are
  untouched — pre-existing hygiene, not this lane's).
- Bank provenance now carries `pdflane-atoms-draft-v1` (37 question_versions);
  glmocr rows for superseded papers are gone (archived).
- Serving lane untouched (assessment tables only); app up, auth surfaces
  behave (401 not 5xx) post-drive.
- parser-ci on `4bdab55`: run 35768987248.

## NOT claimed / NOT done

- No mark-closure work on the 77 flagged papers (separate lane).
- No contract-1.1 upgrade (A2) — pool caps remain text-encoded, not structural.
- No teacher validation of the new SUGGESTED rows (operator/pilot activity).
- No changes to retrieval lane, chunks, or embeddings.
