# RESTAMP267 REPORT — rev1→rev2 paired re-stamp on VALIDATED docs (open item #1)

- **Date:** 2026-09-28 · **Task:** 62 · **IM trace:** `1a0e9e9407a8e239` ("Proceed with next")
- **Actor/provenance:** agent-performed, operator-delegated (actor label Nawaf Al Hussain
  Khondokar); no teacher session; `teacher_validation_events` 0 throughout.
- **Scope:** the "rev1 chunk paired re-stamp backlog (267 chunks)" — first item on the
  open list carried verbatim since Task 58.

## What the backlog was (proven, not assumed)

Live probe at task start: 267 embedded rev1 chunks sat on exactly 20 VALIDATED QP/MS
documents (sittings 202001–202306; corpus wave 2026-09-25). These docs were validated in
waves AFTER the Task-55 cut-over, so their chunks were never carried by the 965-chunk
re-stamp — and the CURRENT_EMBED_REV=2 serving filter made them **invisible to serving**:
a real serving gap on already-validated content. Separately, 22 embedded rev1 chunks sit
on the 2 SUGGESTED docs `4ch1-2c-202101/{qp,ms}` (the Jan-2021 paper row) — those stay
rev1 by design (Task-55 follow-up (a): their re-stamp belongs IN-TX with the operator's
supersession sign-off) and were **out of scope** here.

## Gates (preflight, 11/11 PASS — preflight_task62.json)

T1 census 89V/1S/14R · T2 backlog == 267 · T3 single embedding model on the set
(gemini-embedding-001 → stamp-only change legitimate, vectors untouched) · T4 no
unembedded rev1 rows · T5 remainder-after == Jan-2021 pair (22) · T6 20 docs, G6
metadata truth clean · T7 pre-eligible 2,646 + disjoint · T8 events 0, audit tail id
3733 · T9 Jan-2021 row still SUGGESTED.

## Apply (one fail-closed tx — apply_task62_report.json)

In-tx pre-asserts (backlog set byte-identical, eligible-set SHA unchanged, census, rev1
total 289) → guarded UPDATE `embed_rev 1→2` on embedded chunks of VALIDATED docs →
rowcount gate 267 → post-asserts (rev1 remainder 22 = the 202101 pair; eligible 2,913
with the 267 ⊆; events 0) → **COMMITTED 2026-09-28T21:36:07Z** → post-commit ANALYZE.

- **Defect caught + fixed en route (honest):** the first EXECUTE attempt crashed at the
  audit-row step on `ck_cra_action` (the review-ledger constraint only admits
  VALIDATE/VALIDATE_ALL/REJECT/FLAG/UNFLAG/PLACE/MAP_TOPICS). The crash was INSIDE the
  tx → fail-closed rollback, zero partial writes (re-proven by the fresh-gate re-run:
  backlog set + rev1 total unchanged). Decision per Task-55 precedent ("audit
  untouched" for the 965-chunk stamp flip): stamp mechanics are NOT review actions and
  borrowing a review verb would be provenance forgery → **0 audit rows**; the honest
  record is this pack + the records commit + the worklog.
- A dry-run (rolled back, zero writes) passed all asserts before the first EXECUTE.

## Independent landing verify (fresh connection — verify_task62.json)

V1 census unchanged · V2/V2b rev1 remainder 22 = 202101 pair only, embedded · V3 zero
rev1-on-VALIDATED (gap closed) · V4/V4b eligible 2,913, backlog ⊆ · V5 the 267 all
rev2/embedded/gemini-embedding-001 · V6 events 0 · V7 audit ledger untouched (max id
still 3733) · V8/V8b G6 truth clean · L1 live app probe 5/5 queries, 10 hits each,
gemini-embedding-001.

## Effect

- Serving-eligible pool **2,646 → 2,913 rev2-embedded chunks (+267)**; additive-only —
  no previously-served row changed, no state flip, no validation semantics touched.
- 20 VALIDATED QP/MS docs (202001–202306) now serve their full content at rev2.
- rev1 backlog item **CLOSED**; remaining rev1 = the 22 Jan-2021 chunks, correctly
  parked for the operator's supersession sign-off (in-tx re-stamp at that flip).

## Still open (unchanged by this task)

Jan-2021 supersession sign-off (operator-owned) · §D1 retire decisions (96 inert
SUGGESTED rows: 91 shells + 5 retired candidates — probe census 70 MS + 80 QP incl.
older waves) · bank-repair queue (Q10 b–d 6 marks, 2 scheme rows, empty-stem rows) ·
sheet-generator regex fallback fix · rev1-epoch sme-bank cards re-stamp stays paired to
their future validation wave.

## Files

`preflight_task62.json` · `apply_task62_report.json` · `verify_task62.json` ·
`SHA256SUMS` — local copies in `download/psaxis-review/`; scripts under
`scripts/task62_kit/` (preflight / apply / verify, persisted + re-runnable).
