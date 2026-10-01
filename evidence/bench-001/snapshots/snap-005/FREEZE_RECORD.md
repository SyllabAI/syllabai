# SNAP-005 r6 card-flip freeze record (2026-09-28) — T-C13 corpus snapshot discipline

Task: the r6 freeze — the at-flip execution owed when the operator/teacher card
validation wave lands (bench/r6-staging/R6_STAGING_STATE.md "Remaining AT THE
FLIP" step 2; bench/AT_FLIP_RUNBOOK.md trigger A). The wave landed 2026-09-28
~08:03Z: the operator (Nawaf Al Hussain Khondokar) completed the 298-card review
sheet (sha256 `89c0714681ecd710be0e2d4c402f4320b1c47faa545341f20d7ffdb5b861d67e`,
delivered via github.com/nawaf-al-hussain/FileUpload) and the recorded decisions —
295 VALIDATE + 3 FLAG (#207/#278/#291, the no-spec-linkage cards) — were applied
VERBATIM in a single fail-closed transaction (content_review_audit run
`a5d13c0a-2503-4d06-bb14-9397e9a1cf37`, 298 operator-labeled rows, sheet
sha256-pinned in every detail). No agent-asserted validation anywhere: every
decision carries the operator's named declaration. Import traces:
1a0e702ed9960375 (wave import), 1a0e71324fcdc119 (this freeze).

## What this is

The fifth versioned freeze in the snap-N series (snap-001 2026-09-17 → snap-002
2026-09-25 → snap-003 2026-09-26 → snap-004 2026-09-27 → snap-005 2026-09-28):
a fresh read-only capture of the serving database under the same evidence
discipline, taken AT the card-serving flip. SNAP5-H1 carries
`chunk_spec_hv.json` BYTE-IDENTICAL (sha256 `b5b20ffa96b620bd…`, pinned to
records `94d0d405c` `bench/evidence/chunk-sp-substrate-2026-09-27/`), which
flips §8(d) from NOT SCOREABLE to **scoreable-with-coverage** at this freeze —
the r6 runners (core `c91372c`+`64c71ff`+`670423a`+`b45b5d6`, CI green) score
§8(d) from HV rows only on the first snapshot that carries the artifact.

## The flip, verified first-hand before freezing

- Operator card wave (the r6 gate): 298 T-C27 card documents 2026-09-26 cohort —
  295 SUGGESTED → VALIDATED, 3 SUGGESTED → FLAGGED, 0 left SUGGESTED.
  Chunks mirror the documents: **295 up-flips + 3 flag decisions, 0 true
  regressions** (SNAP5-F1 + SNAP5-F5). documents census at freeze:
  EXTERNAL_QUESTIONS = 296 VALIDATED (295 new + the pre-existing 09-20-cohort
  4CH1/1C card doc) / 3 FLAGGED / 80 SUGGESTED neighbors untouched
  (created ≠ 2026-09-26, verified unchanged).
- The 3 FLAG decisions stay non-servable by the unchanged serving gate
  (`d.validation_state = 'VALIDATED'`) — the operator's review notes are
  preserved verbatim in content_review_audit.
- SNAP5-F4: the 350 EXTERNAL_NOTES chunks (112 notes documents) JOIN the
  corpus additively (SUGGESTED = production truth; VALIDATED-only serving
  views unchanged — they exist so the §8(d) chunk_ref join and the
  ALL-denominator resolution view work).
- SNAP5-F6 (app-side production truth, separate from the card wave):
  the VALIDATED question_versions anchor set grew 720 → 731 rows AFTER the
  snap-004 freeze via pilot.teacher@syllabai-test.dev using the app's teacher
  surface on the papers/schemes axis (content_review_audit 2026-09-28: 11
  question_version VALIDATE + 1 exam_paper VALIDATE_ALL = the 11 new anchors,
  all `ING-4CH11CSPECIMEN2017` / 4CH1/1C). Multiset-superset verified: zero
  removal, zero mutation.
- No other corpus evolution: snap-004's 3,831 chunk_refs carried with
  IDENTICAL contents/kinds/spec_codes; spec_points (194), graph_edges (152),
  misconceptions (19), concept_attachments (117) all BYTE-IDENTICAL to
  snap-004; resources HEAD pin unchanged at `1245df009`; graph_code rows
  set-equal (embedded source.date differs by design).
- teacher_validation_events: 0 rows (its CHECK domain excludes documents —
  the wave's ledger is content_review_audit; constraint contract respected).

## Exporter amendments (manifest-bound deltas, never silent)

The staged exporter (records `9754e62a1`, dry-run ALL PASS ×2 pre-flip) assumed
an all-VALIDATE wave and a frozen anchor set. Production truth at the flip
required two narrowly-scoped, fail-closed amendments before the freeze re-run:

- **SNAP5-F5**: down-flips permitted ONLY as SUGGESTED→FLAGGED on
  EXTERNAL_QUESTIONS chunks (the operator's own FLAG decisions, audit-evidenced);
  any other down-flip — especially anything VALIDATED→* — still aborts.
- **SNAP5-F6**: question_anchors fidelity is now a multiset SUPERSET of
  snap-004 (zero removal/mutation) with the growth recorded as a delta;
  byte-identity was impossible against live production truth and the superset
  check preserves the anchor's intent.

Both amendments are recorded in the docstring, in `verification_deltas.json`,
and in the manifest. The amended exporter is carried here as export provenance.

## Method

- Read path: the sanctioned session-env production connection, opened
  READ-ONLY — `set_session(readonly=True)`, SELECT-only statements, rolled
  back and closed at export end. Zero production writes (SNAP5-M1 =
  SNAP4-M1 = SNAP3-M1).
- Exporter: `snap005_export.py` (carried here), producer queries preserved
  verbatim from the frozen `snap004_export.py`; comparison base snap-003 →
  snap-004; the two amendments above; nothing else.
- Determinism: gzip mtime=0; ORDER BY unchanged.

## Fidelity anchors (all PASS)

- chunk_ref set: snap-004's 3,831 carried IDENTICAL; additive delta == exactly
  the 350 notes chunks; no duplicates; content_sha256 self-consistency on all
  4,181 rows.
- Drift gate (§8(d) substrate): all 210 HV mappings re-verified over the FROZEN
  chunk bytes against the pinned resources store (`e8b58a7109104bb7` @
  `1245df009`): **0 divergences**; anchor-kind census 205 CLEAN / 4 MULTI /
  0 SPAN / 1 MISS; projection census 210/209/164/181 == the handoff §4 census.
- spec_points / graph_edges / misconceptions / concept_attachments:
  BYTE-IDENTICAL to snap-004.
- question_anchors: multiset superset, +11 rows, 0 removed/mutated (SNAP5-F6).
- graph_code: concepts rows set-equal; counts equal; resources pin unchanged.
- concept_attachments: 117 HV rows == ratified pair set == DB serving pairs.

## Counts

- chunks 4,181 = 3,831 carried (1,281 QP + 1,494 MS + 1,056 EQ) + 350 EN.
- chunks_by_paper_state: QP 145 VALIDATED / 1,136 SUGGESTED; MS 161 / 1,333;
  EQ 306 VALIDATED / 3 FLAGGED / 747 SUGGESTED; EN 350 SUGGESTED.
- question_anchors 731; spec_points 194; graph_edges 152; misconceptions 19;
  concept_attachments 117; hv_projection 210 rows / 209 with refs / 164
  distinct refs / 181 distinct codes.

## What remains for r6 (this freeze does NOT record run numbers)

gold re-pair (gold-v3 → snap-005 pins, files byte-identical, gold_check PASS)
→ preload-r6 → `ops-{embed-backfill,run003b,run004a,run005c}-r6.yml` dispatches
in runbook order → run records + R6-GENERATION-NOTES. The interpretation
pre-registration (records `09a624728`) binds the first §8(d) reading: (1)
gold-query leakage measured and flagged per arm; (2) a high §8(d) beside weak
(a)/(b)/(c) is a coverage signal, never "retrieval works"; no promotion claim
on (d) at r6.
