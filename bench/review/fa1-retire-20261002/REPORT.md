# F-A1 orphan retirement — T-C62 (2026-10-02)

Operator mandate (trace `1a0fc4b91fc4c965`): "② F-A1 orphan retirement". T-C56's
registered disposition: governed retire (REJECTED/archive) with reference guards,
then census re-pin (F-PROD-4 precedent). Instrument: the T-C54 wave-2 governed
SQL-batch pattern — single transaction, identity gate, idempotence, scope/drift/
reference guards, in-transaction census/chunks/audit/events non-interference
asserts, exact `searchServingEligible` gate replica, one `content_review_audit`
row with batch_run_id + the operator's trace and decision text verbatim, no DDL.

## 1. Fail-closed divergence — T-C56's "0/18 referenced" does not hold

Protocol ② re-derivation found the register's ep-reference audit rested on the
**wrong join column** (`exam_papers.*_document_id = documents.id` — the row uuid —
yields 0 refs for everything; verified: joining on `documents.document_id` is the
correct shape). Live topology of the 18 registered rows:

- **16 × 4CH0** (`4CH0-{1C,2C}-{2013,2014,2016,2017}06 × qp/ms`): **NOT orphans.**
  Each is referenced by exactly one VALIDATED exam_papers row titled
  `4CH0/1CR|2CR June …` (both slots), and each row's bytes checksum-match the
  current corpus **R dirs** (`4CH0-1CR/2CR`) — they are the R-paper generations
  whose `source_uri` was inherited (mis-URI'd) from the pre-09-25-repair corpus.
  Retiring them would break live paper rows; the honest repair is a governed
  **source_uri relabel** — NOT in this mandate, recorded as the follow-up ruling.
- **2 × 4CH1 QP** — the true orphans the register described: bytes quarantined by
  the 09-25 repair (match no current corpus pin), 0 ep refs, superseded:
  `97f4da13…` (4CH1-1C-201906/qp) **already REJECTED** (terminal; no action) and
  `a7a0e028…` (4CH1-1C-202206/qp, VALIDATED, 15 chunks, 0 refs; the superseding
  generation `22201906…` is VALIDATED and ep-linked).

## 2. Executed — exactly the registered predicate

**APPLIED 2026-10-02T13:29:32Z, batch_run_id `cae83ab6-6ec9-4101-a780-fe59cf7862ec`:**

- flip `documents.validation_state` VALIDATED → REJECTED for `a7a0e028…` (rowcount 1);
- one `content_review_audit` row (action REJECT, target_type document,
  from VALIDATED to REJECTED; actor_label names the operator + trace
  `1a0fc4b91fc4c965`; detail carries the divergence note + gate arithmetic);
- in-tx asserts ALL PASS: reference guard (0 ep refs at flip), supersession,
  16-row non-interference, census delta exactly V−1/R+1 on QUESTION_PAPER,
  chunks snapshot byte-unchanged (4,672/4,672 rev2), audit 2,797→2,798,
  teacher_validation_events Δ0, gate replica 4,608 → 4,593 = exactly −15
  (the orphan's 15 embedded-rev2 in-scope chunks leave subject-path eligibility;
  nothing consumed them — 0 ep links — and the wrong-paper-front-matter class
  core `02664958a` already excludes them structurally in serving);
- dry-run first (`FLIP_DRY_RUN=1`): DRY_RUN_OK on the identical assert chain.

## 3. Independent verification (fresh READONLY connection)

Target REJECTED · audit row readable with batch_run_id + verbatim decision text ·
16 4CH0 rows still VALIDATED with exactly 1 ep ref each · gate 4,593 ·
census 1017 docs (871V/146R) · bank-axis pins unchanged from T-C55
(schemes 1504 = 1360V/144S, mark_points 5,883, question_spec_points 2,620,
knowledge_nodes 435).

## 4. Census re-pin (census-last) + concurrent drift note

`census_bundle_fa1_20261002.json` re-pins the full papers-axis + bank-axis census
post-retire. **Concurrent-lane drift captured between the lane's probe (13:20Z)
and the census read**: 8 chunkless SUGGESTED documents (4 QP + 4 MS) flipped to
VALIDATED by concurrent activity with no audit rows on this lane's instrument,
and exam_papers 103 → 104. T-C60 (papers-axis completion) is IN_PROGRESS with its
governed writes staged/landing — **when T-C60's batch lands, a further census
re-pin is owed** (recorded in the bundle).

## 5. Follow-up rulings recorded (not executed — outside this mandate)

1. **4CH0 R-generation relabel**: the 16 ep-linked generations need
   `source_uri` corrected to their true `4CH0-{1C,2C}R-*` identities (bytes
   already correct for the `1CR`-titled ep rows). Data fix, no serving change.
2. The 3 F-A2 unresolvable replacements (4EB0 2014-06 MS; 4PH1 2020-06 1P+2P)
   await an authenticated DAM source.
3. Secrets revocation (GH_PAT + RENDER_KEY) — operator-held.

## 6. Pack

`REPORT.md` (this file) · `fa1_probe.json` (18-row live derivation) ·
`fa1_ep_topology.json` (join-shape proof + per-row ep topology) ·
`fa1_apply_report.json` (transaction run report) · `census_bundle_fa1_20261002.json`
· `SHA256SUMS`. Scripts: `scripts/fa1_probe.py`, `fa1_ep_topology.py`,
`fa1_retire.py`, `fa1_verify_census.py`. (Super Z, T-C62)
