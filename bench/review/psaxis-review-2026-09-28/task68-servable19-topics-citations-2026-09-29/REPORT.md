# Task 68 — SERVABLE-19 TOPIC MAPPINGS + STALE-CITATION RE-POINT (2026-09-29)

**Authorization:** operator IM trace `1a0eb3255bd898c9` — "cosmetic re-points,
topic mappings for the 19 newly-servable question" — the two non-operator open
items named in the Task-67 close-out. Agent-performed under operator
delegation; both lanes are data repairs (Task-66/T-QSP2 class): no code change,
no audit rows (mechanics precedent — display-only metadata and mapping rows,
no validation-state flips anywhere in this task), teacher_validation_events 0
throughout.

## Lane A — by-topic mappings for the 19 newly-servable questions

### Probe findings (corrected the close-out's wording)

Task 67's honesty note said the 19 "carry zero topic mappings". Measured live:
the 19 (4CH1/1C Jan-2022 ×11 + 4CH1/2C Jun-2019 ×8, all qv+ms VALIDATED) carry
**45 question_spec_points rows** (AI_VALIDATED) but **zero real topic anchors**:
18 of 19 have synthetic `ING-*` primary anchors (`ING-4CH12CJUNE2019` ×8,
`ING-4CH11CJANUARY2022` ×10) and no `question_topics` rows; exactly one
(2022 q5, `867c9a42`) was already house-mapped (primary 4CH1-S1-c + 2 topic
rows). This is the T-QSP3 profile scoped to the newly-servable cohort.

### Derivation (mechanical, mirrors T-QSP2 / mapQuestionTopics §10)

PRIMARY topic = parent TOPIC of the question's PRIMARY spec point via the
canonical KG `PART_OF` edges (all 43 distinct spec points have TOPIC parents —
zero orphans); SECONDARY topics = distinct parent TOPICs of the SECONDARY
points, cap 4. Consistency proof: the mechanical derivation reproduces the
pre-existing 2022-q5 rows EXACTLY (S1-c primary + S1-e secondary). Plan
cross-checked per question against the independent stage-2 derivation — 18/18
match before any write.

### Execution — single fail-closed tx (dry-run ROLLBACK first), COMMITTED

18 guarded primary UPDATEs (`... WHERE id=%s AND primary_topic_node_id=<ING
anchor> RETURNING`, rowcount 1 each) + 21 `question_topics` rows (18 primary +
3 secondary: 2019-q6→S4-b Crude oil, 2019-q8→S1-e Chemical formulae/equations,
2022-q7→S2-g Acids/bases/salt preparations), uq-guarded. In-tx asserts: ING
census 302 → 284, question_topics 745 → 766, question_spec_points 2578
unchanged, exactly one primary row per question for all 19, every new topic
node a real 4CH1 TOPIC, no ING anchors left on the 19. Notable derivations:
2019-q8 (2.37 P + 1.34C/1.35C S) → S2-g + S1-e; 2022-q7 (1.4 P + 2.34 S) →
S1-a States of matter + S2-g.

## Lane B — stale-citation re-point (cosmetic)

### Probe findings (scope corrected vs the Task-63 framing)

Citations (`mark_schemes`/`question_versions.source_document_id`) store the
CANONICAL `documents.document_id` (uuid-v5), not the row uuid — Task 63's "88
of 96 cited" measured on the then-96 shells. Measured live today: **106
REJECTED docs cited by 949 rows (381 ms + 568 qv)** — the Task-63 88 plus
Task-64/65/OCR-lane rejects. 1,263 further citation rows are unresolvable
(sme-eq-* pilot refs ×1,186, `audit-ms-*` synthetics, 71 deleted-era uuids) —
no authoritative target exists, untouched. Resolution census: 0 rows resolve
via row-uuid; all via canonical id.

### Target assignment (ledger-first, current-link-wins)

PLACE ledger parsed across ALL three detail formats (57 "link repair" +
34 "re-ingest link" + 2 OCR-lane "re-link" + 2 COVID-decision "re-link"
fragments = 95 pairs, + the Jan-2021 supersession pair from audit 3871 detail:
glmocr shells 0751cabc/f2237b67 → corpus-wave a4a8a5e1/d74802bc) = 97 unique
from-docs. Target = the owning paper's CURRENT same-kind linked doc (not the
historical to-doc — handles the OCR/COVID re-links cleanly); every target
asserted VALIDATED + kind-match. 4 cited docs covered via Task-65 SUPERSEDED
pointers (paper-title → linked doc). **12 OWNER-REJECTED docs (99 rows) left
untouched** — their sittings' owning papers are all REJECTED, no serving
target exists, citations stay historically-true and resolvable; each carries
its OWNER-REJECTED audit row (asserted).

### Execution — single fail-closed tx (dry-run ROLLBACK first), COMMITTED

850 rows re-pointed across 94 docs (per-doc rowcount equality asserted against
pre-counts: e.g. e06585b7→8 qv, ca0bce24→8 ms). In-tx asserts: total 850 ==
plan; post-census only the 12 OWNER-REJECTED docs still cited (7 ms + 92 qv);
REJECTED doc census unchanged (147, rows retained); audit tail untouched
(4014). Rows citing VALIDATED docs moved 493 → 1,343 (+850); 22 SUGGESTED-cited
rows untouched; unresolvable 667 ms / 596 qv untouched.

## Verification — 3 layers, VERIFIED

1. **DB (fresh connection, 24/24 PASS):** censuses (active 946, qt 766, qsp
   2578, ING 284, audit 4014, docs 567V/305S/147R); all 19 primaries = the
   exact expected TOPIC codes; 23 topic rows over the 19 (1 primary each, row
   counts per-question exact); citation landscape (12 left docs, 99 rows, +850
   moved, shell-zero spot checks, unresolvable untouched); mirror invariant 0.
2. **Serve path (prod API):** GET /exam-papers for both papers — 11/11 and 8/8
   questions render, all with specPoints; Jan-2022 q6 exposes 4CH1-1.40/1.41.
3. **Evidence path (prod e2e, fresh probe learner):** structured attempt +
   full self-mark on 4CH1/1C Jan-2022 q6 (Ionic bonding, 9/9) →
   evidenceFired=true → /learners/me/state carries 3 skillStates at 0.357:
   **4CH1-S1-f "Ionic bonding" (the REAL topic anchor — node dcc1c814, the
   delta this lane exists for)** + spec points 4CH1-1.40 / 1.41.

## Observations (no action taken)

- T-QSP3 remains open for the rest of the cohort: ING-anchored active questions
  302 → 284 after this lane; the 284 remaining all have spec-point mappings
  and can be cleared by the same mechanical derivation.
- The 12 OWNER-REJECTED docs' 99 citations + 1,263 unresolvable citations
  (sme-eq-*/audit-*/deleted-era) stay as-is: display-only, never joined,
  historically true or without any resolvable target.
- Probe learners created for the e2e (3 registrations; one earlier attempt
  stayed PENDING from a pre-fix payload — disposable probe data, documented).

## Files

`task68_topics_exec.json` (plan + per-question derivation) ·
`task68_citations_exec.json` (94-doc re-point plan) · `task68_verify_db.json`
· `task68_verify_api.json` · `SHA256SUMS`

## Remaining open (updated)

- Sibling supersession sign-offs 4ch1-2cr-202001 / 4ch0-2c-201701 (operator
  per-package APPROVE; destroy teacher-VALIDATED rows).
- Sheet-generator regex fallback fix (code lane).
- T-QSP3: real primary topics for the 284 remaining ING-anchored questions.
- Bank-scheme sparsity (91 qv without scheme rows on VALIDATED papers).
