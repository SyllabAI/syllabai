# snap-006 FREEZE RECORD — the r7 serving-set eval freeze (2026-09-28)

**What ran.** `bench/r7-staging/snap006_export.py` (adapted from the snap-005
post-F5/F6 provenance exporter; ALL producer queries preserved verbatim;
comparison base snap-004 → snap-005) executed FOR REAL against production at
2026-09-28 ~15:5xZ via the sanctioned session-env read path — SELECT-only,
`set_session(readonly=True)`, rolled back (SNAP3-M1/SNAP4-M1/SNAP5-M1 lineage
unchanged). **ALL VERIFICATIONS PASS.** Commission: operator directive
"Proceed with (1) eval" (trace `1a0e88bb060ed3b5`) — item (1) of the corrected
standing menu (`evidence/serving-rev2-flipback-refutation-2026-09-28/REPORT.md`).

**What this freeze captures.** Today's production serving truth — two operator
decisions landed after snap-005 and are in via programmatically verified
deltas (SNAP6-F1, 353 chunk up-flips, zero down-flips SNAP6-D1):

- **flagged3 flip**: 3 EXTERNAL_QUESTIONS cards FLAGGED→VALIDATED
  (decision trace `1a0e7865c3b35715`, batch_run_id
  `0d5e4c4a-cacc-454c-9dfe-5983e1f11661`, 2026-09-28T11:32:05Z, records
  `7f3a8f3` + `35b5166`) — promoted chunks: 4CH1/2C ×1, 4CH1/2CR ×2.
- **notes-axis promotion**: 350 EXTERNAL_NOTES chunks SUGGESTED→VALIDATED
  across 112 documents (operator trace `1a0e88af08e12df5` "pursue (a)",
  batch `notes-axis-promotion-2026-09-28`, batch_run_id
  `ef4c1fe4-1b18-4697-b3bd-074e4e0f582b`, 2026-09-28T15:22Z, records
  `9ea54e1`; the promotion also re-stamped those chunks embed_rev 2→1 —
  vectors untouched, and embed_rev is not a snapshot column).

**Census at freeze** (chunks_by_paper_state): EQ 309 VALIDATED / 747 SUGGESTED /
0 FLAGGED · EN 350 VALIDATED · QP 145 VALIDATED / 1136 SUGGESTED ·
MS 161 VALIDATED / 1333 SUGGESTED. Serving-eligible VALIDATED pool =
309 + 350 + 145 + 161 = **965 chunks** (615 → 965, purely additive; matches the
notes-axis run report's gate replica).

**Fidelity anchors (all PASS).** Zero chunks added/removed; contents, kinds and
spec_codes byte-identical on the carried set; spec_points / graph_edges /
misconceptions / question_anchors (superset +0) / concept_attachments
BYTE-IDENTICAL to snap-005; graph_code rows set-equal (source.date differs by
design); the HV drift gate re-verified every mapping over the frozen chunk
bytes against the pinned resources store (`1245df009`, sha256_16
`e8b58a7109104bb7`, git-blob `9247ccdf…` re-verified at staging download):
anchor census 205 CLEAN / 4 MULTI / 0 SPAN / 1 MISS, projection census
210/209/164/181 — byte-stable.

**Artifacts.** Staging tree + SHA256SUMS (8 artifacts) frozen at
`evidence/bench-001/snapshots/snap-006/` (this commit; the exporter bytes are
the provenance copy `snap006_export.py` beside this record) and staged as
`bench/inputs/snapshot-r7/`. Gold re-pair: `bench/gold-v5` (class files
byte-identical to gold-v4; pairing pins re-issued to snap-006) staged as
`bench/inputs/gold-r7/`; `gold_check.py snapshot-r7 gold-r7` PASS (120
records, quotas ok, all anchors resolve). Preload: `preload-r7` staged from
the frozen r6 vector rows with re-issued manifest pins (see its manifest notes).

**Honest scope.** Zero production writes; zero serving-semantics changes; the
exporter asserts nothing about flips in advance — it captures what the live
state holds at run time. Menu items (2) (eval-gated re-stamp) and (3) stay
operator-gated and untouched.
