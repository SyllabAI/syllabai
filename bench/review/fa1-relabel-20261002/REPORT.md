# 4CH0 R-generation source_uri relabel — T-C68 (2026-10-02; renumbered from T-C66 at push time)

Operator mandate (IM trace `1a0fcf4d0a035c8d`): **"① Relabel source_uri on
line"** — executes the T-C62/F-A1 follow-up ruling #1, recorded in
`bench/review/fa1-retire-20261002/REPORT.md` §5.1 and `.syllabai/tasks/T-C62.yaml`:
the 16 ep-linked 4CH0 R-paper generations need `source_uri` corrected to their
true `4CH0-{1C,2C}R-*` identities (bytes already correct for the `4CH0/1CR|2CR`-titled
ep rows; data fix, no serving change). Scope note: the operator message is terse
and possibly truncated; the 16-row set is the only registered source_uri relabel
ruling in the records, and this lane executed exactly that registered scope —
nothing more. If the operator intended additional rows, none are recorded and
none were touched.

## 1. Protocol ①② recon (all first-hand)

- Authoritative worklog re-read: Sessions 156 (T-C62) → 157 (T-C65); the relabel
  ruling is the top remaining open of T-C62. Locks/TODO/task-registry re-read:
  T-C66 free, no active lease conflicts; latest audit row at probe time was
  T-C62's own 13:29:27Z batch — **zero concurrent DB writes** between the
  census re-pin and this lane's apply (census read back EXACTLY on the fa1
  baseline: docs 1017 = 871V/146R + 0 SUGGESTED, ep 104 = 91V/13R, chunks
  4,672/4,672 rev2, audit 2,798, gate 4,593).
- 16-row identity re-derived live (`fa_relabel_probe.py`): every row still
  VALIDATED at the old (pre-repair, plain-C) source_uri with the exact
  checksum pinned in `fa1_ep_topology.json`; each referenced by exactly one
  VALIDATED `exam_papers` row (`paper_code` `4CH0/1CR` or `4CH0/2CR`, sessions
  June 2013/2014/2016/2017, both QP+MS slots = 8 rows / 16 refs, correct join
  on `documents.document_id`).
- **Corpus proof at HEAD `f0ea3a1f9`** (`fa_relabel_plan.py`): all 16
  checksums pin at the 8 R-dir manifests (`4ch0/past-papers/<session>/4CH0-{1CR,2CR}/manifest.yaml`);
  each manifest's `paper.official_reference` (`4CH0/1CR`, `4CH0/2CR`) + `series.normalized`
  (`2013-06` …) + material path derive the target URI, and each manifest's
  `repair` block records the 09-25 F10 cure ("regional-variant bytes that
  previously sat in the 4CH0-1C dir moved here to their true identity,
  bytes_unchanged: true") with the same sha256s — the DB generations ARE the
  corpus R bytes, mis-URI'd at the 09-21/22 ingest era.
- **Target convention**: matches the live house style already carried by 42
  R-suffix rows (`4CH1-1CR-201906/qp.pdf`, `4CH1-2CR-202306/ms.pdf`, …):
  `<OFFICIAL_REF dashed>-<YYYYMM>/<qp|ms>.pdf`. Collision guard: **0 live rows**
  held any target URI (case-insensitive) at probe, re-asserted in-transaction.
- Generation topology: each of the 16 URIs carried TWO generations — the old
  R-byte generation (ep-linked, this batch's target) and the 09-28T20:18–20:24Z
  plain-byte generation from the repaired plain-C dirs. The relabel resolves
  that latent URI collision: after the batch each generation's `source_uri`
  names the paper its bytes actually are.

## 2. Mapping (16 rows, plan sha256 `ee6324c157d16449ec5a15892044b21c37d5ad1d9a34c95ea1d73f42e6debe1d`)

| old source_uri | new source_uri | kind | chunks |
|---|---|---|---|
| 4CH0-1C-201306/ms.pdf | 4CH0-1CR-201306/ms.pdf | MARK_SCHEME | 21 |
| 4CH0-1C-201306/qp.pdf | 4CH0-1CR-201306/qp.pdf | QUESTION_PAPER | 24 |
| 4CH0-1C-201406/ms.pdf | 4CH0-1CR-201406/ms.pdf | MARK_SCHEME | 17 |
| 4CH0-1C-201406/qp.pdf | 4CH0-1CR-201406/qp.pdf | QUESTION_PAPER | 20 |
| 4CH0-1C-201606/ms.pdf | 4CH0-1CR-201606/ms.pdf | MARK_SCHEME | 21 |
| 4CH0-1C-201606/qp.pdf | 4CH0-1CR-201606/qp.pdf | QUESTION_PAPER | 20 |
| 4CH0-1C-201706/ms.pdf | 4CH0-1CR-201706/ms.pdf | MARK_SCHEME | 24 |
| 4CH0-1C-201706/qp.pdf | 4CH0-1CR-201706/qp.pdf | QUESTION_PAPER | 21 |
| 4CH0-2C-201306/ms.pdf | 4CH0-2CR-201306/ms.pdf | MARK_SCHEME | 10 |
| 4CH0-2C-201306/qp.pdf | 4CH0-2CR-201306/qp.pdf | QUESTION_PAPER | 11 |
| 4CH0-2C-201406/ms.pdf | 4CH0-2CR-201406/ms.pdf | MARK_SCHEME | 9 |
| 4CH0-2C-201406/qp.pdf | 4CH0-2CR-201406/qp.pdf | QUESTION_PAPER | 12 |
| 4CH0-2C-201606/ms.pdf | 4CH0-2CR-201606/ms.pdf | MARK_SCHEME | 12 |
| 4CH0-2C-201606/qp.pdf | 4CH0-2CR-201606/qp.pdf | QUESTION_PAPER | 10 |
| 4CH0-2C-201706/ms.pdf | 4CH0-2CR-201706/ms.pdf | MARK_SCHEME | 12 |
| 4CH0-2C-201706/qp.pdf | 4CH0-2CR-201706/qp.pdf | QUESTION_PAPER | 13 |

(257 embedded-rev2 chunks total; row ids + document_ids + full sha256s in
`relabel_plan.json`.)

## 3. Executed — T-C54 wave-2 governed SQL-batch instrument

Single transaction, no DDL; `FLIP_DRY_RUN=1` first (**DRY_RUN_OK** on the
identical assert chain, run `168321e3-2698-4565-8234-162b79594928`), then
**APPLIED 2026-10-02T14:35:10Z, batch_run_id `bf3485f8-e504-47bc-b1ce-a29fbbdb725d`**:

- DB identity gate: `current_database() = neondb`, `campaign_db_identity` =
  `T-C04-CAMPAIGN`; ACTIVE cv pinned `4CH1-2017` (`356840e6-…`), exactly one;
- idempotence guard (batch marker in `content_review_audit` + rows-at-target probe);
- scope/drift guard: all 16 rows live-verified at expected old URI + checksum +
  VALIDATED + chunk count before any write;
- reference guard: exactly 1 VALIDATED ep ref per row (correct join on
  `documents.document_id`);
- collision guard: 0 other live rows at any target URI (case-insensitive);
- the relabel: per-row identity-guarded `UPDATE documents SET source_uri = %s
  WHERE id = %s AND source_uri = %s AND checksum = %s AND validation_state =
  'VALIDATED'` — rowcount exactly 1 × 16;
- 16 `content_review_audit` rows in the same transaction — action **PLACE**
  (the app's own definition of a factual association update leaving validation
  states and the serving boundary untouched — `ContentReviewService.placePaper`
  javadoc; the `ck_cra_action` vocabulary has no neutral "update" verb, and
  FLAG/REJECT/VALIDATE would each assert a state change that did not happen),
  target_type `document`, from_state = to_state = `VALIDATED` (states unchanged
  by design), actor_label names the operator + the lane task ID, detail carries the
  operator's trace `1a0fcf4d0a035c8d` + verbatim decision text + old/new URI +
  checksum + corpus pin path + corpus head + batch_run_id;
- in-transaction non-interference asserts ALL PASS: documents census
  (state×kind) unchanged, chunks snapshot unchanged (4,672/4,672 rev2),
  docs total 1017, ep 104, teacher_validation_events Δ0, audit 2,798→2,814
  (= +16), ep reference count 16 pre/post, **exact `searchServingEligible`
  gate replica 4,593 → 4,593 (delta exactly 0 — `source_uri` is not in the
  gate predicate and nothing else moved)**.

## 4. Independent verification (fresh READONLY connection, separate process)

`relabel_verify.json` — all checks PASS: 16/16 rows at target URIs with
byte-identical sha/state/kind/chunks; old URIs released (each now held only by
the 09-28 plain generation); exactly one holder per target URI; 16 PLACE audit
rows readable with verbatim operator trace + decision text; ep topology intact
(8 VALIDATED `4CH0/1CR|2CR` rows, both slots, 16 refs); target code tokens
equal the corpus manifests' `official_reference`s.

## 5. Census re-pin (census-last)

`census_bundle_fa1_relabel_20261002.json` — docs 1017 (871V/146R, 0 SUGGESTED),
chunks 4,672/4,672 rev2, ep 104 (91V/13R), audit 2,814, tve 0, gate 4,593,
mark_schemes 1504 (1360V/144S), mark_points 5,883, question_spec_points 2,620,
knowledge_nodes 435, ACTIVE cv `4CH1-2017`. Every pin equals the T-C62/fa1
baseline except audit (+16 from this batch's own audit rows).

## 6. ID-race note (renumber T-C66 -> T-C68, first-pushed protocol)

The governed batch applied at 14:35:10Z under the provisional lane ID T-C66.
At the pre-push collision guard (records push, ~14:5xZ) T-C66.yaml already
existed — claimed by the concurrent flashcard bridge-gate lane (operator trace
1a0fcf454aacec35), and T-C67 was claimed by the rank-quality tranche-4 lane.
Per the T-C49/T-C55/T-C59/T-C64/T-C65 first-pushed protocol this lane
renumbers to **T-C68**. The as-run artifacts in this pack
(`relabel_apply_report.json`, `fa_relabel_apply.py`, its SHA256SUMS) and the
16 in-DB `content_review_audit` rows intentionally remain byte-exact as run
and therefore carry the "T-C66" string in `actor_label`/`detail.authority`;
that string is a records-side label only. The authoritative, unambiguous join
keys on the DB rows are `batch_run_id bf3485f8-e504-47bc-b1ce-a29fbbdb725d`
and `operator_trace_id 1a0fcf4d0a035c8d`, both correct as written.

## 7. Pack

`REPORT.md` (this file) · `relabel_plan.json` (16 mappings + corpus proofs) ·
`relabel_apply_report.json` (dry-run + apply run reports) ·
`relabel_verify.json` (independent verify + census bundle) ·
`census_bundle_fa1_relabel_20261002.json` · `fa_relabel_probe.py` ·
`fa_relabel_plan.py` · `fa_relabel_apply.py` · `fa_relabel_verify.py` ·
`SHA256SUMS`. Secrets env-only (GH_PAT + RENDER_KEY), never on disk in any
git-tracked path, never in any commit.

## 8. Remaining opens

1. The 3 F-A2 unresolvable replacements (4EB0 2014-06 MS; 4PH1 2020-06 1P+2P)
   — await an authenticated DAM source (unchanged).
2. T-C60's remaining ingest wave (4 papers + 4 ep rows + 11 heals) — blocked
   on environment prerequisites, operator-held (unchanged).
3. Secrets revocation (GH_PAT + RENDER_KEY) — operator-held.
4. If the operator's "on line" carried additional scope beyond the registered
   16-row ruling, it is not recorded anywhere in the records/worklog and was
   not executed — re-issue with the row list and it will be scoped honestly.
   (Super Z, T-C68)
