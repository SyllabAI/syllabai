# RESIDUE-CLOSURE LANE — BANK-SCHEME SPARSITY + ING NODE CLEANUP + CENSUS REGENERATION (2026-10-01)

**Authorization:** operator IM trace `1a0f5fdf6226bdc9` — "Proceed with
bank-scheme sparsity (91 qv), ING orphan node cleanup (104), census
regeneration" — exactly the three open-residue items named by the
sme-eq-499 closeout (commit `e7ed272`). All three executed in one session;
every write fail-closed (dry-run first), every disposition grounded in
measured evidence.

Pre-state pins all reproduced before any write: qsp 2637, qt 1725, active
961, L1 961/961/0, sme-eq mirrors 593/593, past-paper 368/368, qsp15 cohort
15/59/36, papers 90V/14R, docs 567V/305S/147R, schemes 1420 (1360 V / 60 S),
mark_points 5315, knowledge_nodes 539 (104 ING), edges 734, audit tail 4047,
teacher_validation_events 0.

## A. Bank-scheme sparsity — 91 → 56, 35 evidence-clean extractions (COMMITTED)

**Measurement.** The recorded "91 qv without scheme rows on VALIDATED papers"
re-measured EXACTLY 91 across 22 papers — all four candidate definitions
(any-state / VALIDATED-state / latest-per-question / non-rejected) return the
same 91, so the set is stable and unambiguous. Every affected paper carries a
MARK_SCHEME document with 8–26 chunks (the RAG substrate exists).

**Extraction design (gated, anti-fabrication).** The Task-66 Q10 precedent
governs: the corpus md tables are lossy flattenings; building rows from them
where structure is damaged would invent content. Per question-number group of
each paper's MS chunks (chunks merged by header QN — long questions span
multiple chunks):

- rows parsed from printed `QN REF (M marks): text` lines (first line only;
  `allow:`/`note:`/`ignore:` continuation fragments excluded);
- G1 printed total present and not pipeline-flagged `(verification FAILED)`
  — both total formats recognized (2019-style line + older flattened tail
  `(Total for Question N = M marks)`);
- G2 sum(row marks) == printed total; G4 sum == qv.marks (independent
  QP-derived bank value); G3 exactly one sparse qv maps to the QN;
- duplicate refs NOT treated as damage (sub-parts legitimately restart P/M
  numbering in the print) — the sum gates discriminate clean parses from
  mangled ones (v1 parser's uniqueness gate would have wrongly rejected 15
  clean groups; corrected before any write).

**Result: 35 of 91 fillable under the gates — 35 mark_schemes + 243
mark_points COMMITTED** in one fail-closed tx (dry-run all green first).
Inserted shape matches house conventions: version_label '1',
validation_state **SUGGESTED** (no self-validation — these join the 60
existing SUGGESTED schemes awaiting the teacher lane), source_document_id =
the paper's MS document id, extraction_method `ms-chunk-gated-extraction-v1`,
question_part_id/acceptance_criteria NULL (no honest part mapping from the
flattened MS), point refs and texts verbatim from the chunks. NO state flips,
NO content_review_audit rows, teacher_validation_events 0 (TX-B mechanics
precedent: provenance = this pack + plan sha `a5d77ac4b79…` + the frozen
merged chunk texts embedded per entry in `bank_scheme_plan.json`).
Every entry's full merged source text is sha-pinned in the plan and re-verified
verbatim against the live chunks (verify V5).

**Residue: 56 qv documented, by measured class** (`skipped` array in the
plan): 24 no-printed-total (truncated/mangled chunk tails), 16 pipeline
`(verification FAILED)` flags honored, 8 sum≠printed (mangled duplication),
4 no MS chunk at all (page-coverage gaps in the ingested docs), 1 stub chunk,
**7 bank-side defects where the MS is internally consistent (rows sum ==
printed total) but the bank's qv.marks differs** (e.g. 4CH0/1C Jun-2013 Q3:
MS 7/7, bank 1) — that is the Task-66-TX-B marks-arithmetic defect class and
needs its own printed-QP-evidence repair lane; filling schemes against a
wrong marks value would compound the defect.

## B. ING node cleanup — 47 orphan nodes deleted, 57 retained with proof (COMMITTED)

**Premise correction (measured).** The recorded "104 orphaned nodes" were not
fully orphaned. Serving bank: clean (0 refs from active questions / qsp / qt —
consistent with Tasks 59–69). But the nodes were referenced by:

- **4 knowledge_edges** (ING-`<paper>` PART_OF → the 4CH1 SUBJECT node);
- **13 skill_states + 13 review_schedules rows** of 6 accounts — all verified
  test/demo fixtures (5× "V20 Battery", 1× "qsp-e2e-probe", all STUDENT role,
  all `@syllabai-test.dev`, created 2026-09-14/29; the schedules were PENDING
  and overdue since 2026-09-21 against dead placeholder topics);
- **538 archived (inactive) questions' primary_topic_node_id** — an app-level
  reference (no FK), 57 distinct nodes.

**Dry-run catch (fail-closed working as designed):** `questions.
primary_topic_node_id` carries a **NOT NULL constraint** — archive anchors
cannot be NULLed, so anchored ING nodes are not deletable by a DB lane
(re-pointing them to any real topic would fabricate, and deleting archived
questions is out of scope). Disposition v2, all guarded in one tx:

- DELETE the 4 edges (rowcount-gated);
- DELETE the 26 fixture learner rows (in-tx fixture guard re-asserted per
  learner: STUDENT role + created ≤ 2026-09-30; row-id-set equality);
- **DELETE the 47 truly-orphaned ING nodes** (not anchored by any question;
  pin==47; full name-pattern re-sweep over the deleted set = 0 dangling refs);
- **RETAIN 57 nodes** (archive anchors; before-images of all 104 nodes + all
  deleted rows are in `ing_plan.json`, sha `9d53e3fa06…`, making the whole
  operation reversible by INSERT).

Post-state: knowledge_nodes 539→492, edges 734→730, skill_states 198→185,
review_schedules 133→120; zero references to any deleted node anywhere;
L1/qsp/qt/mirrors/cohort all pinned unchanged. **Full ING removal is now an
app-migration item** (anchor-column semantics for archived questions), not a
DB maintenance lane.

## C. Census regeneration — final bundle, ALL PINS MATCH

`census_bundle.json` captures the complete post-state: papers {VALIDATED 90,
REJECTED 14}; qv 1533; questions 961 active / 1533 total; qsp 2637; qt 1725;
L1 961/961/0; sme-eq mirrors 593/593 + past-paper 368/368; bank-wide qt
primary conflicts 0; qsp15 cohort 15/59/36; schemes 1455 (1360 VALIDATED /
95 SUGGESTED), mark_points 5558, scheme-sparse qv 56; knowledge_nodes 492
(ING remaining 57, all archive-anchored; serving refs 0/0/0/0/0/0); edges
730; skill_states 185; review_schedules 120; docs 567V/305S/147R; audit tail
4047; teacher_validation_events 0. **Every fingerprint matches the expected
post-state — no drift.**

## Independent verification (fresh connections, both items)

- `bank_scheme_verify.json` — V1 sparse 56 + lane census; V2 per-entry
  point-counts/marks-sums vs plan (0 mismatches); V3 state censuses + audit
  tail + events untouched; V4 bank pins incl. L1 961/961/0; V5 verbatim text
  fidelity spot-checks; V6 plan sha. **ALL PASS.**
- `ing_verify.json` — V1 ING residue state (57 retained, all archive-anchored,
  all ⊆ plan pre-image); V2 zero dangling refs to the 47 deleted; V3 zero
  learner/edge/active-anchors referencing any plan node; V4 bank pins incl.
  mirrors + cohort; V5 bank-scheme lane intact; V6 plan sha. **ALL PASS.**

## Files

`probe_residue.json` · `probe2_residue.json` (regenerated POST-apply: its
definition matrix reads 56/56/56/56 — the post-extraction sparse census;
the pre-apply 91/91/91/91 measurement is pinned in `bank_scheme_plan.json`
pre_state and was printed in-session) · `probe3_residue.json` ·
`probe4_residue.json` · `probe5_residue.json` ·
`probe6_extraction_yield.json` (gated sweep, v2 gates) ·
`bank_scheme_plan.json` + `.sha256` · `bank_scheme_verify.json` ·
`ing_plan.json` + `.sha256` · `ing_verify.json` · `census_bundle.json` ·
`SHA256SUMS`

## Remaining open (updated)

- **Bank-scheme residue (56 qv)** — structural: needs re-OCR of the printed
  MS pages (4 missing-page docs, 1 stub, 24 truncated-tail, 16
  pipeline-flagged, 8 mangled) — an OCR-lane item; PLUS the new
- **qv marks-vs-printed defects (7 qv identified)** — Task-66-TX-B class,
  printed-QP-evidence-gated repair lane.
- **ING full removal (57 archive-anchored nodes)** — app-migration item
  (anchor-column semantics); before-images ready in `ing_plan.json`.
- §C children VALIDATE_ALL; sibling supersession sign-offs — unchanged.
