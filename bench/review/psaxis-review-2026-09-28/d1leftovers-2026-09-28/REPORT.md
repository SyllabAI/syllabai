# Task 65 — §D1 Leftovers Pass EXECUTED (trace 1a0ea3c208e16699, "Proceed with next")

The standing open item "§D1 leftovers pass (57 zero-chunk SUGGESTED docs)"
from Tasks 62-64, executed under the operator's sequential delegation with
honest per-row audit provenance. Not an in-app teacher session;
`teacher_validation_events` 0.

## What the 57 are

Legacy md-lane corpus documents (`corpus/igcse-chemistry-4ch0-.../{QP,MS}.md`)
ingested in the pre-pdflane era: every one carries **0 actual chunks** (SUGGESTED
rows with no content), split into 43 unlinked + 14 paper-linked rows. The
`4ch0` corpus path prefix is a **mislabel for 2019+ content** — the sitting
content of those years belongs to the 4CH1 spec (proven by VALIDATED 4CH1/2CR
papers pointing at corpus/4ch0-... docs).

## Disposition rules (evidence-checked per row, decisions_task65.json)

- **SUPERSEDED** (37 rows, unlinked): the sitting (paper-code + variant-exact
  1C/1CR + year + month, spec prefix 4CH0 OR 4CH1) has a VALIDATED paper whose
  same-kind pointer doc is VALIDATED with real chunks (8-20 chunks each, all
  rev2 serving) — the 0-chunk md-lane row is redundant.
- **OWNER-REJECTED** (12 rows, paper-linked): every owning paper row is
  REJECTED (the R-variant/COVID phantom claims rejected in earlier waves) —
  0-chunk inert companions of dead claims.
- **KEEP** (8 rows): 2 owned by the VALIDATED "4CH1/1C Specimen 2017" paper
  (retiring would orphan a serving paper's declared QP/MS pointers — doc-repair
  lane owns) + 6 across three sittings (4CH0/1C Jan 2018, 4CH1/1CR Jan 2020,
  4CH1/1CR Jan 2021) whose VALIDATED papers have NO serving same-kind content
  (pointer-less) — the md-lane rows are those sittings' only doc records.

## Execution (one fail-closed tx, dry-run first)

In-tx pre-asserts (universe 57 frozen, 49 rows SUGGESTED+0-chunks, census/
audit-tail/events unchanged) → guarded `UPDATE documents SET
validation_state='REJECTED' WHERE validation_state='SUGGESTED' AND
document_id IN (49)` → rowcount gate 49 → 49 REJECT audit rows
**ids 3891-3939** (actor Nawaf Al Hussain Khondokar, trace + per-row rule and
evidence in every detail) → post-asserts → COMMITTED → ANALYZE documents.
Rule mix: SUPERSEDED 37 · OWNER-REJECTED 12.

## End state (independently verified, 12/12 + live probe 5/5)

- Documents census **567 VALIDATED / 305 SUGGESTED / 147 REJECTED**
  (−49 S, +49 R; every row retained queryable; display-only
  `source_document_id` citations remain resolvable per Task-63 precedent).
- Zero-chunk SUGGESTED universe: **57 → 8** (exactly the KEEP set).
- Papers census 90V/0F/0S/14R unchanged; serving pool **2,935 unchanged**
  (retire is serving-neutral by construction: 0-chunk rows never served);
  rev1 0; audit ledger the only write.
- Live probe 5/5 queries × 10 hits, single model gemini-embedding-001.

## Remaining open

Bank-repair queue (4CH1/1C Jun-2019 Q10 b–d 6 marks, 2 scheme rows,
empty-stem rows) · sheet-generator regex fallback fix · stale-citation
re-point (cosmetic) · sibling supersession sign-offs (4ch1-2cr-202001 /
4ch0-2c-201701 — per-package operator APPROVE required: they destroy
teacher-VALIDATED rows) · the 8 KEEP rows' sittings (doc-repair lane:
Specimen 2017 + three pointer-less VALIDATED 1CR/1C sittings).
