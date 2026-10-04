# T-C75 follow-on act (a) — doc-side VALIDATION of the 6 new 2026-06 docs (2026-10-04)

**Batch:** `tc75-doc-validation-20261004` · **run** `db46ba93-d0bb-4c5a-a4c3-eeb072c5a308`
· **Status: DRY_RUN_OK → APPLIED 12:21:31Z → ALREADY_APPLIED proven → independent
read-only post-verify 15/15 PASS.**

**Operator word (the card-protocol word for this batch), verbatim:**
"(a) doc-side VALIDATION" — IM trace `1a106d1f681a80ad`, 2026-10-04. The agent
asserts no validation of its own; every audit row names the operator
(`Nawaf Al Hussain Khondokar`) as deciding actor.

## 1. What the act is

The T-C75 card's first `next_safe_action`: "doc-side VALIDATION of the 6 new
2026-06 SUGGESTED docs (unlocks subject-side serving on top of the ep-side
serving delivered today)". The W2 ingest landed the 6 documents SUGGESTED by
design; the W2 governed ep batch made them serve ep-side (via the 4 VALIDATED
exam_papers rows, gate 4,593 → 4,661). This act flips the documents themselves:

  documents.validation_state: SUGGESTED → VALIDATED, 6 rows (3 QP + 3 MS),
  one content_review_audit VALIDATE/document row each.

**Instrument shape:** the T-C54 wave-2 governed doc-validation batch
(`bench/review/wave2-validation-2026-10-02/apply_wave2_validation.py`, 297
docs APPLIED 2026-10-02) narrowed to the wave's own 6 documents — identity
gate, idempotence, ACTIVE-cv scope guard, live drift rule, per-doc fidelity
(kind/state/doc_version/checksum/chunks/embedded/subject-scope), census
snapshot shift check, chunks immutability, tve Δ0, ep immutability, exact
`searchServingEligible` replica, no DDL, single transaction, DRY_RUN default.

## 2. Serving semantics — the honest difference vs the wave-2 act

The wave-2 batch predicted `gate_post == gate_pre + actionable_chunks` because
its 297 docs were NOT ep-linked. The 6 wave docs ARE ep-linked from the W2 ep
batch, so their 68 chunks already serve via the PAPER branch and the predicted
gate delta here is **exactly 0** (4,661 → 4,661). What the flip adds is the
SUBJECT branch (`d.validation_state='VALIDATED'` + chunk subject in the ACTIVE
cv) for the same 68 chunks: **subject-branch count 0 → 68** (per-doc
11/18/9/10/9/11) — subject-side serving unlocked, gate count unchanged. Both
numbers are asserted in-transaction and re-derived independently post-hoc.

## 3. Worklist (pins == staging inventory / ingest report / ep-batch pins)

| Paper | Side | documentId | kind | chunks | checksum (sha256) |
|---|---|---|---|---|---|
| 4CH1-1C-202606 | qp | `c6fbb3ac-4056…` | QUESTION_PAPER | 11 | `231c0574…` |
| 4CH1-1C-202606 | ms | `a03447d8-7c1b…` | MARK_SCHEME | 18 | `d4febc16…` |
| 4CH1-2C-202606 | qp | `ea685722-b453…` | QUESTION_PAPER | 9 | `713f1fcc…` |
| 4CH1-2C-202606 | ms | `b5742cb1-c413…` | MARK_SCHEME | 10 | `a42a22c4…` |
| 4CH1-2CR-202606 | qp | `b0660052-3ecc…` | QUESTION_PAPER | 9 | `5ee0d5b4…` |
| 4CH1-2CR-202606 | ms | `e3252e22-9c18…` | MARK_SCHEME | 11 | `a005acd5…` |

All 6 asserted live: SUGGESTED, doc_version 1, checksum == pin, chunk count ==
pin, 68/68 chunks embedded rev2 and subject-resolved into the ACTIVE cv.

## 4. Gates run (single transaction, all PASS)

identity (neondb/neondb_owner/T-C04-CAMPAIGN) → idempotence (0 prior batch
rows; no wave doc VALIDATED without this batch's audit rows) → exactly-one-
ACTIVE cv `356840e6…` (`4CH1-2017`) + subject `e56dc9ee…` in cv → live drift
rule (the SUGGESTED QP/MS-with-chunks surface == exactly the 6 wave ids) →
per-doc fidelity 6/6 → prestate census == W2 poststate pins (docs 1023,
ep 108 = 95V/13R, chunks 4740/4740 rev2, audit 2829, tve 0, gate 4,661) →
subject-branch pre == 0 → constraint pre-read (`ck_cra_action` VALIDATE;
`ck_cra_target_type` includes 'document' — no DDL performed) → 6 flips
(rowcount==1 each, `WHERE validation_state='SUGGESTED' AND doc_version=1`) →
6 audit rows → post-asserts (census shifted exactly by the flips — 0 SUGGESTED,
QP 112V/79R, MS 112V/67R; chunks snapshot equal; audit 2835 = 2829+6; tve 0;
ep 108 unchanged; gate 4,661 delta 0; subject-branch 68; 6/6 docs VALIDATED).

**Dry-run discipline caught one real runner bug with zero production effect**
(the wave-2 precedent's pattern): the expected post-census builder
double-counted per-kind flips (dict comprehension overwrote, then re-added →
219 vs the correct 112). First DRY_RUN aborted ABORTED_ASSERT on exactly that
compare; fix applied; second DRY_RUN DRY_RUN_OK; the executed run passed
everything first try. The aborted dry run rolled back and touched zero rows.

## 5. Independent post-verify (separate script, READ-ONLY, driver-enforced)

15/15 PASS (`tc75_doc_validate_postverify_result.json`):

- census: docs 1023, **0 SUGGESTED**, QP 112V/79R, MS 112V/67R, other kinds unchanged
- the 6 wave docs: VALIDATED, doc_version 1, checksums == staging pins (6/6)
- audit trail re-derivation: exactly 6 VALIDATE/document rows carrying this
  batch_run_id; SUGGESTED→VALIDATED ×6; one per wave document_id;
  decision_text "(a) doc-side VALIDATION" + operator trace `1a106d1f681a80ad`
  verbatim; operator named as deciding actor; audit total 2829 → 2835 (+6)
- non-interference: ep 108 = 95V/13R; paper-branch links intact (all 6 wave
  docs still linked from ep rows); chunks 4740/4740 rev2; tve 0
- serving gate == 4,661 (delta 0 exactly as predicted); subject-branch
  re-derived live: 68/68 wave chunks serve subject-side (11/18/9/10/9/11)
- app-side (production core, read-only GETs): the 6 docs present on the list
  surface with pinned checksum + chunkCount; search regression probe
  ('ammonium carbonate' QP) still returns the new 1C-2026 QP.

**Honest disclosure — app-side state reads:** the teacher API exposes NO
document-state read: `GET /documents/{id}` is a real 404 (probed) and the
list DTO carries no `validationState` field. The authoritative state proof is
the DB live-read + the audit-trail re-derivation; the serving-semantics proof
is the subject-branch count (the deployed core's own `searchServingEligible`
leg 2 — the same predicate ChunkVectorRepository ships).

## 6. Machine evidence (this directory)

`tc75_doc_validate.py` (the instrument; plan_sha256 d151ac424fbf87fc…) ·
`tc75_doc_validate_report.json` (APPLIED run report) ·
`tc75_doc_validate_postverify.py` (independent read-only verifier) ·
`tc75_doc_validate_postverify_result.json` (15/15). Secrets: none committed —
credentials live in 0600 files under `.secrets/` (git-ignored) and are never
printed; raw key values never reach any report.

## 7. State after act (a)

| Surface | State |
|---|---|
| documents | 1023 = 871+6 wave VALIDATED / 0 SUGGESTED / 146 REJECTED (census map in §4) |
| serving gate | 4,661 (unchanged — the wave chunks were already ep-side-served) |
| subject-side serving | the 6 wave docs' 68 chunks now serve subject-side too |
| ep rows | 108 = 95V/13R (untouched) |
| audit | 2,835 (+6 VALIDATE/document, batch `tc75-doc-validation-20261004`) |
| teacher_validation_events | 0 (untouched) |

Remaining honest gaps (unchanged, per the card): the 2 G1 FAIL parse-flag
review lanes (2025-06 1C Q5/Q7 totals; 2026-06 2CR ms_total_rows=0) stay with
the disclosed review-flag ledger / the optional future S2 llm-structured card.
