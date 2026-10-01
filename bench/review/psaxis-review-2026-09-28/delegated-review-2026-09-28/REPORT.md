# T-PS1 DELEGATED AGENT REVIEW — APPLIED 2026-09-28

**Authorization:** operator IM order, trace `1a0e95af0892f059`: "I want you to act as human and review it for now. I ORDER YOU. I am doing this because I dont want to throttle development."

**Provenance boundary (stated to the operator before execution):** the agent cannot impersonate a human or fabricate teacher provenance. Executed instead as an **agent-performed review under explicit operator delegation**, recorded honestly on every audit row: actor `Nawaf Al Hussain Khondokar` + `operator-delegated agent review (IM trace 1a0e95af0892f059) … NOT an in-app teacher session`. Downstream consumers of `VALIDATED` on these rows should read it as **"agent-reviewed, operator-delegated"**, distinct from the pilot.teacher in-app validations.

## Method

Five-gate battery per paper (`phase2b_battery.py`, pre-registered before verdicts):
- **G1** paper has question_versions (sheet counts include deactivated questions — verified against sheet detail: 40 papers have all questions deactivated by upstream lane work; noted, not gated)
- **G2** ≤50% of qv stems null/empty
- **G4** all qv marks non-null, positive
- **G5** sampled qv stems trace into the paper's own linked QP doc content (12-token shingle hit or ≥0.85 token coverage) — extraction-attribution guard
- **G6** linked QP/MS docs actually CONTAIN their claimed chunks (documents.chunk_count metadata vs real document_chunks rows)

Phase-1 pre-flight: live DB matched the sheet 100% (77 papers / 722 qv / 631 schemes / 132 docs, zero drift, zero concurrent audit writes). Dry-run then execute in one fail-closed transaction (guarded per-row UPDATE … AND validation_state='SUGGESTED' RETURNING; abort on any anomaly). A mid-run client timeout caused one clean server-side rollback; verified zero partial state, then re-executed.

## Verdicts

| Verdict | n | What it means |
|---|---|---|
| **VALIDATED** | **27 papers + 246 qv + 246 schemes + 32 docs** | all gates green; 15 papers verified by stem→QP-doc attribution (e.g. 5/5, 4/4), 12 linkless papers by structure-only review (no claimed source doc to misattribute) |
| **FLAGGED** | **49 papers** (paper row only; children/docs untouched) | G6 failure: linked QP/MS docs are **metadata shells** — `chunk_count` claims 8–26, actual `document_chunks` rows = 0 (98 of 132 linked docs; 10 papers additionally had zero stem attribution vs their empty QP docs) |

Excluded from both: **4CH1/2C January 2021** — the sheet's own §C instruction ("do not bare-flip; resolve the staged supersession package first"); stays SUGGESTED (its qv/schemes were already VALIDATED).

## Key data-quality finding

The G6 gate caught **systemic shell-doc corruption**: 98 linked docs (49 papers' QP+MS pairs, minus one real MS) claim chunks in metadata that do not exist in the chunk layer. The T-PS1 sheet faithfully reported this lying metadata ("SUG·1p·10c" etc.). Validating these papers would have stamped VALIDATED on non-existent print evidence. The real chunk content for several of these sittings exists in the **§D1 orphan docs** (pdflane lane) — the deferred §D1 promotion decisions are the fix path.

## Net state effect

- exam_papers: 14 VALIDATED → **41** (+27) · 0 FLAGGED → **49** · 77 SUGGESTED → **1** (Jan-2021 only)
- question_versions: +246 VALIDATED (all under the 27) · mark_schemes: +246 VALIDATED
- documents: +32 VALIDATED (all with verified real chunks)
- Serving pool (rev2-embedded VALIDATED-doc chunks): 965 → **1,118** (+153; 267 rev1 chunks on the same docs stay unserved until the proven paired re-stamp pattern is run — deliberate non-bundling)
- `teacher_validation_events`: 0 throughout; audit ledger 477 → **1,077** (+600 rows, single operator label, honest delegation provenance on every row)
- FLAGGED never serves; FLAG is reversible (UNFLAG) — the 49 are inert until their doc shells are repaired.

## Verification

Independent landing verify (`phase4_landing_verify.py`, fresh connection, 14 assertions): **ALL PASS** — census exact, VALIDATE set fully flipped, FLAG set children provably untouched, exclusion honored, 32 docs validated with real chunks, 600 audit rows single-actor with provenance present, events 0.

## Files

- `phase1_census.json` — sheet-vs-live drift check (zero drift)
- `phase2b_battery.json` — per-paper gate results and verdicts (the review itself)
- `phase3_apply_report.json` — transaction report (plan counts, pre/post asserts, commit time)
- `psaxis_detail.json` — sheet input (pinned from the original sheet generation)
- Scripts: `phase1_census.py`, `phase2b_battery.py`, `phase3_apply.py`, `phase4_landing_verify.py` (agent workspace `scripts/psaxis_review/`)

## Open follow-ups

1. **49 FLAGGED papers**: repair path = re-ingest/point the shell docs at real chunk content (several already exist as §D1 pdflane orphans) → then a named re-review.
2. **267 rev1 chunks** on the newly VALIDATED docs: paired rev re-stamp (Task-55 pattern) when the operator wants them serving.
3. **4CH1/2C Jan 2021**: supersession sign-off still pending (unchanged).
4. The `VALIDATED`-means-delegation caveat is recorded here and in the audit rows; codify in docs if this becomes the standing policy.
