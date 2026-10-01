# sme-eq-94 Reconciliation — the 94 anchor-vs-qsp disagreements (2026-10-01)

**Trace:** `1a0f5b2b7bf5bf7d` — operator instruction "Proceed with 94 sme-eq-\* disagreements"
**Lane:** data (production Neon via Render-fetched DSN, in-memory only)
**Authority model:** same as qsp15 (Task 55) — operator-directed, agent-derived plan pinned before any write, fail-closed guarded execution, fresh-connection verification.

## 1. What the 94 are

Task 55's pre-write L1 validation reproduced every active question's primary-topic
anchor mechanically from its `question_spec_points` PRIMARY row (expected anchor =
PART_OF parent TOPIC of the role=PRIMARY spec point) and found **94 disagreements,
all `sme-eq-*`** (the 2026-09-19 SME corpus import lane) — recorded then as a
pre-existing unreconciled pool, out of scope. The pinned counts (qsp15_plan.json
`repro_L1`): checked=946 agree=852 disagreements=94 qt_anchor_conflicts=0.

## 2. Re-derivation (pin-validated)

The Task-55 scripts were lost in the 2026-10-01 sandbox rollbacks; the rule was
re-implemented from the REPORT definition and validated by **reproducing the pin
exactly**: today (post-qsp15) checked=961, agree=867 (852 past-paper + 15 qsp15
cohort), disagree=94, all 94 `sme-eq-*`, 0 ambiguous, 0 qt conflicts
(`l1_census_detail.json`, script `scripts/sme94_census.py`).

## 3. Ground-truth facts on the 94 (all measured, live DB)

- **F1 (94/94):** the existing anchor is the **plurality-winner** of the
  parent-TOPIC distribution of the question's own spec points — i.e. the SME
  import filed topics by plurality while flagging qsp roles independently.
  The 94 are exactly the questions where the import's two internal rules
  (plurality filing vs PRIMARY flag) diverge.
- **F2 (94/94):** the expected anchor (parent TOPIC of the single PRIMARY
  point) is a real `4CH1-S*` TOPIC node, unambiguous (no multi/zero-parent
  points anywhere in the population).
- **F3 (shape):** all 94 have **no qt PRIMARY row** (the sme-eq lane has 0/593
  qt-primary mirrors; the past-paper lane 368/368); the anchor is absent from
  `question_topics` for all 94; the expected topic already sits as a SECONDARY
  qt row for 92, and is absent for the 2 qsp-repair twins
  (`sme-eq-2-7-acids-bases-and-salt-preparations-q3-p1` / `-q3-s`, whose qsp
  rows were created 2026-09-29 and whose qt rows never were).
- **Content reading (samples):** e.g. `sme-eq-1-6-ionic-bonding-q1-p2` ("Choose
  a substance that is a liquid at 25 °C") has PRIMARY point 4CH1-1.1 (States of
  matter) under an "Ionic bonding" filing — the flag reflects the assessed
  content; the filing reflects the SME section/plurality artifact.

## 4. Disposition (D1) and why

**Anchor moves to the parent TOPIC of the PRIMARY point; the old anchor is
preserved as a SECONDARY `question_topics` row. The qsp content coding is
untouched byte-for-byte.**

- It completes the bank-wide house rule (T-QSP2 semantics: filing = topic of
  the dominant assessed point) that the other 867 questions already obey,
  making the L1 reproduction 961/961.
- The old filing is content-real (F1: parent of a genuine SECONDARY point) and
  survives as a qt SECONDARY row — nothing deleted.
- The alternative (re-flagging qsp roles to match filings) was rejected: it
  would rewrite assessed-content coding without mark-block evidence and
  fabricate the PRIMARY semantics that the past-paper lane grounds in mark
  dominance.
- The qt-primary mirror added here aligns the 94 with the past-paper lane's
  shape (anchor mirrored by a qt PRIMARY row).

## 5. Execution

- Plan pinned before any write: `sme94_plan.json`
  (sha256 `cb4cb2cba97a208e635dd640aa3c1ff40c03f0715f4075931acabdca9419a7d0`),
  per-question from-state guards for every write.
- **Dry-run** (full tx, all asserts, ROLLBACK): first attempt exposed that
  `question_topics.id`/`created_at` have no DB defaults — fixed client-side
  (uuid4 + now(), qsp15 convention); second dry-run ALL GREEN.
- **Execute** (single tx, COMMIT): 94 guarded anchor UPDATEs (rowcount 1 each)
  + 94 NOT-EXISTS-guarded qt secondary INSERTs (old anchors)
  + 92 qt secondary→primary flips (rowcount 1 each)
  + 2 NOT-EXISTS-guarded qt primary INSERTs (the twins).
- In-tx asserts all green at commit: L1 961/961/0; qsp_total 2637; qt_total 1226;
  cohort qt-primary==anchor 94/94; bank-wide qt-primary-vs-anchor conflicts 0;
  the 94's qsp rows byte-identical to the pre-tx snapshot.

## 6. Verification (fresh connection, `sme94_verify.json`)

| Pin | Result |
|---|---|
| P1 L1 census | checked=961 agree=961 disagree=0 |
| P2 qsp_total / active / ING refs | 2637 / 961 / 0-0-0 (unchanged) |
| P3 qt_total | 1226 exact (1130 + 96) |
| P4 the 94 | qt-primary==anchor 94/94; old anchor secondary 94/94 |
| P5 lane mirrors | sme-eq 94/593 (was 0/593); past-paper 368/368 intact |
| P6 qsp15 cohort | 15 active / 59 qsp / 36 qt — intact |

## 7. Impact notes (honest)

- Practice-pool membership moves: the 94 questions are now filed under the
  topic of their dominant assessed point; the previous filing remains attached
  as a secondary topic (qt + qsp secondaries both still credit it).
- No attempts, marks, evidence, or BKT rows were touched; no state flips; no
  `teacher_validation_events` rows; qsp rows byte-identical (assert 6).
- The hub bridge joins by `external_ref` family and is unaffected by anchor
  moves; its slug-based topic pages are a separate surface (recorded, out of
  scope).
- Split-MCQ caveat (recorded, upstream data-lane item): for split MCQ
  families (`-pN` refs) the qsp PRIMARY flag is a question-level artifact of
  the import, not per-part content coding; per-part refinement belongs to the
  package owner lane, not this reconciliation.
- DSN provenance: fetched in-memory from the Render API (Task-58 path; the
  env DSN turned out to be a host-only JDBC URL — credentials spliced from the
  separate env vars). No secret printed, logged, or persisted anywhere.

## 8. Open items carried

- sme-eq lane qt-primary backfill for the remaining 499 agreeing questions
  (they satisfy the L1 rule; only the qt mirror is missing — cosmetic/serve-shape gap).
- Bank-scheme sparsity (91 qv); ING anchor node cleanup (104 orphaned nodes);
  census evidence bundle re-generation (optional, needs keys).
- Records push for this evidence bundle (see commit note — PAT availability).

## Files

- `l1_census_detail.json` — pin-validated re-derivation + the 94 enumerated
- `disagreements_detail.json` — per-question qsp/qt/stem detail + slug-family summary
- `sme94_plan.json` — the pinned plan (sha256 above)
- `sme94_verify.json` — fresh-connection post-state pins
- `SHA256SUMS` — digests of this bundle
- Scripts (agent-side, SELECT-only except the apply): `scripts/sme94_lib.py`,
  `sme94_probe_schema.py`, `sme94_census.py`, `sme94_detail.py`,
  `sme94_build_plan.py`, `sme94_apply.py` (dry|execute), `sme94_verify.py`
