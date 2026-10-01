# sme-eq qt-primary backfill — the other 499 L1-agreeing questions (2026-10-01)

**Trace:** `1a0f5eba1935f439` — operator instruction "proceed with one of the open
items" (selection: the 499 backfill, staged in the previous task under trace
`1a0f5de1684a7045`); Render key supplied in chat, env-only.
**Lane:** data (production Neon via Render-fetched DSN, in-memory only).
**Authority model:** same as qsp15/94 (Tasks 55/59) — operator-directed,
agent-derived plan pinned before any write, fail-closed guarded execution,
fresh-connection verification.

## 1. What the 499 are

After the SME-94 reconciliation (commit `72a4f70`) the bank-wide L1 house rule
(filing = parent TOPIC of the dominant/PRIMARY assessed point) holds 961/961,
but the **serve shape** still lagged: the sme-eq lane had qt-primary mirror rows
for only the fixed 94 (94/593); the past-paper lane is 368/368. The remaining
**499 sme-eq questions agree with the L1 rule** (their `questions.primary_topic_node_id`
anchor already equals the parent TOPIC of their single PRIMARY spec point) yet
had **no `question_topics` is_primary row** — a pure serve-shape gap, recorded
as an open item in the 94 REPORT and TODO.md.

## 2. State validation before any write

The staged plan builder initially asserted the PRE-fix L1 pin (961/867) and
**failed closed** — a pin-authoring error, not a state change. A read-only
diagnostic (scripts/sme499_diag.py) then measured the live bank and confirmed
the exact post-Task-59 state before anything was touched:

- L1 census: checked=961 agree=961 disagree=0
- qsp_total=2637, questions_active=961, qt_total=1226
- mirrors: sme-eq 94/593, past-paper 368; bank-wide qt-primary coverage
  failures = 499 (exactly the target set)

The builder pin was corrected to (961, 961) with a comment; the diagnostic ran
BEFORE any write existed in the session. Zero DB writes preceded the pinned plan.

## 3. Ground-truth facts on the 499 (all measured, live DB)

- **F1 (499/499):** every target agrees under L1 — anchor == parent TOPIC of
  its single PRIMARY spec point (no multi/zero-parent points in the target set).
- **F2 (499/499):** the anchor is a real `4CH1-S*` TOPIC node.
- **F3 (shape):** all 499 have **zero qt rows for the anchor node** — the
  anchor is entirely absent from `question_topics` (same shape as the 94's
  anchors pre-fix). Mechanics: **499 INSERTs, 0 flips** (measured, not assumed).
- **Non-agree guard:** sme-eq questions without a qt primary row but NOT
  L1-agreeing = 0 (must be 0 post-94; asserted).

## 4. Disposition and mechanics

**ADDITIVE serve-shape backfill only.** For each of the 499: INSERT
`question_topics (id, question_id, anchor, is_primary=true, created_at)` with
explicit uuid4 + now() (the table has no DB-side defaults — qsp15/94
convention), guarded by NOT-EXISTS (question_id, node_id) and per-row rowcount=1.
**NO questions updates** (anchors already correct), **NO qsp changes**, **no
deletions**, no other rows touched.

Plan pinned before any write: `sme499_plan.json`
sha256 `7a1eb14ba797599abd9c50fde764b339526e7ce14f50ee2d571d76dfea9bf0e3`
(499 entries: question_id, external_ref, anchor_code, primary_point_code,
mechanics, from-state guards).

## 5. Execution (single fail-closed tx, scripts/sme499_apply.py)

- **Dry run:** 499/499 guarded inserts rowcount=1; in-tx asserts 1-6 all green
  (L1 961/961/0; qsp 2637; qt 1226+499=1725; 499-cohort qt-primary==anchor
  mismatches 0; bank-wide coverage failures 0; qsp rows byte-identical to the
  pre-tx snapshot) → ROLLBACK, zero persistence.
- **EXECUTE:** identical tx → **COMMITTED** (all asserts green at commit).

## 6. Fresh-connection verification (scripts/sme499_verify.py) — ALL PINS PASS

- **P1** L1 census 961/961/0 (unchanged — by design nothing but qt rows moved)
- **P2** qsp 2637 / active 961 / ING 0-0-0 unchanged
- **P3** qt_total **1725** = 1226 + 499 inserts (exact)
- **P4** 499/499 qt primary == anchor; **94-cohort regression intact**
  (primary==anchor 94/94, old anchors preserved as SECONDARY 94/94)
- **P5** sme-eq mirrors **593/593** (was 94/593); past-paper 368/368 intact
- **P6** qsp15 cohort fingerprints intact (15/59/36)
- **P7** bank-wide: every active question has exactly one qt primary row and it
  equals the anchor — **961/961, 0 failures**

## 7. Impact

The bank-wide serve shape is now uniform: every active question (961) exposes
exactly one primary-topic filing equal to its anchor, aligned with the
past-paper lane's shape. No content coding changed (qsp byte-identical), no
anchors moved, no rows deleted; attempts/marks/evidence/BKT surfaces untouched.
This closes the serve-shape residue recorded at Tasks 59/60; remaining opens:
bank-scheme sparsity (91 qv), ING anchor node cleanup (104 orphaned nodes),
census bundle re-generation (optional).

## 8. Honesty notes

- The initial build-plan assert used a stale PRE-fix pin (961/867) and failed
  closed; the diagnostic probe re-measured the live state before any write and
  the pin was corrected. No data was touched at any point before the pinned
  dry-run/execute sequence.
- The plan JSON records question uuids, external refs and node codes only —
  no credentials; the evidence bundle was leak-scanned before commit.
