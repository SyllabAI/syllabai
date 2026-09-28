# §D1 RETIRE REPORT — 91 swapped-away shells + 5 retired candidates REJECTED

- **Date:** 2026-09-28 · **Task:** 63 · **IM trace:** `1a0ea024489b3ee9`
  ("Proceed with next", the second sequential delegation)
- **Scope:** open item #2 after Task 62 — "§D1 retire decisions (91 shells + 5
  retired candidates)". The T-PS1 sheet's §D1 was all-DEFER and filled by
  "ChatGPT — document completion only" (Task 57: zero mutations authorized, not
  an operator validation session) — so these decisions did NOT exist; the
  operator's sequential "Proceed with next" instruction is the delegation under
  which they are now made, with every row carrying honest audit provenance.

## Who the 96 are (authoritative, cross-verified)

- **91 swapped-away shells** = the `from`-ids of the PLACE swaps in the two
  repair lanes, extracted from the audit ledger itself (the primary record):
  Task-59 trace `1a0e95af0892f059` → 57 rows / 57 ids (cross-checked vs
  `phaseC_report.json` plan: delta EMPTY); Task-60 trace `1a0e99217a715a19` →
  34 rows / 34 ids. Overlap 0 → 91. All are legacy corpus md-lane docs
  (`corpus/igcse-chemistry-*/QP.md|MS.md`), SUGGESTED, **0 chunks**, zero
  exam_papers links (the swaps moved paper links to content-proven docs).
- **5 retired candidates** (OCR report): `bbedea1b` (4CH1-1C-201906/qp 1.2.0
  candidate, 13 chunks), `2c7fb229` (10), `b0a9f0f8` (19), `db39d41b` (11),
  `f9211ea5` (11) — superseded by better-proven content in the OCR lane;
  SUGGESTED (non-serving), zero paper links.

## Why retiring is serving-neutral AND provenance-honest (code-verified)

- Serving = VALIDATED docs × embedded × rev2 chunks; all 96 are non-serving
  today → the pool stays **2,913** (asserted in-tx and after).
- 88 of 96 are cited by ms/qv rows via `source_document_id`. Core code check
  (`ContentReviewService` projection, entities, ingestion services): the field
  is a **display-only provenance uuid — no read path joins documents on it**.
  The citation is historically TRUE (the draft came from that md-lane doc) and
  the doc row is RETAINED (REJECTED, queryable), so the reference stays
  resolvable. Re-pointing citations to the swap `to`-docs is cosmetic bank
  metadata hygiene — logged as a follow-up, not a retire prerequisite.
- NOT in scope: the **59** remaining 0-chunk SUGGESTED leftovers (the original
  §D1 rows the sheet deferred — need their own operator-visible pass), and the
  Jan-2021 pair (chunk-ful, operator supersession sign-off, untouched).

## Execution (fail-closed discipline)

- Preflight v3 gate OPEN (13/13) — two earlier gate-CLOSED iterations caught
  (a) 5 shells still cited → invariant corrected to paper-links-only after the
  code check, (b) R-variant sitting normalization over-matching (36≠34) →
  replaced by the audit-ledger extraction, which is authoritative.
- Dry-run PASS → single tx **COMMITTED 2026-09-28T22:06:57Z**: guarded UPDATE
  (SUGGESTED + no-paper-links + id ∈ set) rowcount 96; post-asserts (96
  REJECTED, Jan-2021 intact, pool 2,913, leftovers 59); 96 `REJECT` audit rows
  (allowed verb, append-only, actor Nawaf Al Hussain Khondokar +
  operator-delegated trace, no teacher session, events 0).
- Audit id gap at 3734 explained: burned by the rolled-back Task-62 insert
  attempt (sequence NEXTVAL is not transactional); Task-63 rows span
  3735..3830 contiguous.

## Independent verify (fresh connection) — 10/10 PASS

96 REJECTED + retained · papers census unchanged 89V/1S/14R · Jan-2021 intact ·
pool 2,913 · leftovers 59 · 96 traced REJECT audit rows · tail 3830 · events 0 ·
documents census now **565 VALIDATED / 358 SUGGESTED / 96 REJECTED** · the 5
candidates' 64 chunks retained.

## Still open

Jan-2021 supersession sign-off (operator-owned) · §D1 leftovers pass (59
0-chunk SUGGESTED docs, older §C/§D rows) · bank-repair queue (Q10 b–d 6
marks, 2 scheme rows, empty-stem rows) · sheet-generator regex fallback fix ·
stale `source_document_id` re-point (cosmetic, 88 docs' citations).

## Files

`preflight_task63.json` · `apply_task63_report.json` · `verify_task63.json` ·
`swap_from_ids.json` (ledger extraction) · `SHA256SUMS` — local copies in
`download/psaxis-review/`; scripts in `scripts/task63_kit/`.
