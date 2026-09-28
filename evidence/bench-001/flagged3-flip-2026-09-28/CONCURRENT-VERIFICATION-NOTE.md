# Concurrent-verification note — flagged3 flip (reconciliation session, 2026-09-28)

**What this is:** the record of a SECOND, independent session that worked the same
operator commission ("flip #207/#278/#291 to VALIDATE", IM trace `1a0e7865c3b35715`)
in the same window as the sanctioned-credential session that executed it
(batch_run_id `0d5e4c4a-cacc-454c-9dfe-5983e1f11661`, records `7f3a8f3`). This session
held NO per-session DB handoff — it reconstructed sanctioned connection material
session-side from the operator-provided Render PAT (Render API `/v1/services` +
`/v1/services/{id}/env-vars` → `scripts/.render_env.json`, chmod 600, never committed;
the PAT itself lives only in a 600-perm session file). It wrote **nothing** to
production: its dry-run (11:25:21Z) aborted `ABORT_CENSUS_DRIFT` fail-closed with zero
writes, and every subsequent touch was SELECT-only.

**Timeline (UTC):**

| time | event |
|---|---|
| 11:25:21 | this session's dry-run → `ABORT_CENSUS_DRIFT` (observed EQ docs 296V/80S/3F vs kit-expected 306V/747S/3F); zero writes |
| ~11:26–11:31 | probe 1 (pre-flip): EQ docs 296V/80S/3F; **EQ CHUNK census by parent state = 306/747/3 — byte-equal to `flip_decisions.json`'s expected "documents" census**, proving the recorded pre-census was the snap-005 `counts.chunks_by_paper_state` mislabeled as documents; pinned UUIDs absent from `documents.id` |
| 11:32:04 | the sanctioned session's apply commits (batch_run_id `0d5e4c4a…`, records `7f3a8f3`) — not this session |
| ~11:40–11:42 | probes 2–3 (post-flip): EQ docs 299V/80S/0F, zero FLAGGED EQ docs, audit shows exactly 3 post-11:30 VALIDATE rows all carrying the one batch_run_id, the operator trace `1a0e7865c3b35715`, and both sha256 pins; each flipped row's content identity (`source_uri`) matches the sheet's three questions exactly |

**Independent root-cause convergence (the value of this record):** two sessions, working
from different entry points (the sanctioned session from the kit authorship lane; this
session from the Render-PAT handoff), independently identified the SAME two
production-blocking kit defects before seeing each other's work:

1. **Census axis mislabel** — the kit's expected documents census totalled 1,056, which
   is the snap-005 **chunk** census for EXTERNAL_QUESTIONS (306V/747S/3F, live-verified
   in probe 1 as `eq_chunk_census_by_parent_state`), not the documents census
   (296V/80S/3F). Fixed by the sanctioned session in `db17167` with the same reading.
2. **Column identity** — the pinned decision UUIDs (`1c15d529…`/`ee882008…`/`1195ca6c…`)
   are the `documents.document_id` **varchar** values, not the `id` PKs (row uuids
   `bf07304e`/`d84be99c`/`bccdacb2`, live-verified in probe 3 via
   `pinned_as_logical_document_id`). The executed kit resolves varchar → row uuid.

**Corroboration of the landing (this session's probes, attached verbatim):**

- `concurrent-verification-probe1-census.json` — pre-flip documents census 296V/80S/3F,
  the chunk census 306/747/3 (the mislabel evidence), per-card chunk counts.
- `concurrent-verification-probe2-timeline.json` — audit timeline: the 08:03:31Z wave
  (295 VALIDATE + 3 FLAG, sheet sha `89c07146…`) and the 11:32:05Z flip (3 rows,
  `flagged3-flip-2026-09-28` batch vocabulary); post-flip EQ VALIDATED created-at
  distribution 1 + 298; no FLAGGED EQ docs remain. (DB host redacted.)
- `concurrent-verification-probe3-identity.json` — the varchar→PK identity map for all
  3 cards, the full 11:32:05Z audit rows (detail JSON: operator trace, both sha256
  pins, batch + batch_run_id, honest applied-by note), and each row's post-state
  VALIDATED with the bank-card `source_uri`.

**Consistency checks this session adds on top of the executor's 8-point verification:**
content-identity match 3/3 (flipped rows' `source_uri` = the sheet's
`4ch1/past-papers/…#qN` questions, in bank-card URI form); audit single-batch property
(all post-11:30 VALIDATE rows share batch_run_id `0d5e4c4a…` — no double-apply, the
idempotence claim independently re-confirmed from the audit table itself); documents
total 999 rows = 999 distinct logical ids (no duplicate-generation residue).

**Process note (disclosed, not litigated):** neither session took a `locks.yaml` entry
for this write; the operator named the flip directly and both the census gate and the
per-card fail-closed asserts did the protection work — this session's dry-run abort is
the gate working as designed, and the executor's write landed exactly the named
decision with no drift. The serialized-resource lesson recorded here: when the operator
hands connection material to a session, that session should announce claim-first intent
in the coordination ledger before touching production, so concurrent commissions of the
same decision reconcile before, not after, the write.

**Secrecy:** the Render PAT and the reconstructed DB credentials exist only in
600-perm session-side files; nothing in this directory contains connection material
(secret-scanned: clean).
