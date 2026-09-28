# SNAP-006 notes-axis-promotion freeze record (2026-09-28) — T-C13 corpus snapshot discipline

Task: the r7 freeze — the measured consequence of the operator's named decision
(IM trace `1a0e88af08e12df5`, verbatim "pursue (a). And check current state, and
other agents' work. Check if they completed these or not", where option (a) was
presented in trace `1a0e88d81372240d`): flip the 112 EXTERNAL_NOTES documents
SUGGESTED → VALIDATED so the 210 human-validated chunk→spec-point mappings enter
the served denominator and §8(d) moves off its r6 0.0 baseline. The decision was
applied 2026-09-28 as batch `notes-axis-promotion-2026-09-28`
(content_review_audit batch_run_id `ef4c1fe4-1b18-4697-b3bd-074e4e0f582b`; dry-run
DRY_RUN_OK → one fail-closed transaction; independent post-verify on a fresh
readonly connection; records commit `9ea54e1e2` kit + evidence). Named outcome:
"350 notes chunks enter the pool". This freeze is the snapshot of that
production truth; the r7 runs measure §8(d) over it — the exact value is the
run's measurement, not asserted here.

## What this is

The sixth versioned freeze in the snap-N series (snap-001 2026-09-17 → snap-002
2026-09-25 → snap-003 2026-09-26 → snap-004 2026-09-27 → snap-005 2026-09-28 →
snap-006 2026-09-28): a fresh read-only capture of the serving database under
the same evidence discipline. Row-set identity with snap-005 is verified
programmatically (4,181 chunk_refs; zero added, zero removed; contents, kinds
and spec_codes byte-identical). `chunk_spec_hv.json` carries BYTE-IDENTICAL
(sha256 `b5b20ffa96b620bd…`, pinned to records `94d0d405c`
`bench/evidence/chunk-sp-substrate-2026-09-27/`); what changes at snap-006 is
the SERVING STATE of the chunks those 164 refs anchor.

## The two sanctioned flip cohorts, verified first-hand before freezing

1. **Notes-axis promotion (the r7 gate, operator-named):** 112 EXTERNAL_NOTES
   documents SUGGESTED → VALIDATED + their 350 chunks embed_rev 2 → 1.
   Chunks mirror the documents: **350 EXTERNAL_NOTES chunks SUGGESTED →
   VALIDATED** (SNAP6-F1i). Serving-gate replica 615 → 965, purely additive;
   notes serving set was empty before; same model gemini-embedding-001@768
   both revs. `teacher_validation_events` untouched (0 rows before and after —
   the audit-trail rule stands; the agent applied the operator's named
   instruction and asserted no validation of its own).
2. **Flagged-3 flip (operator-named, applied after snap-005 froze):** the 3
   T-C27 cards #207/#278/#291 — source-verified faithful that morning
   (records `3b36d78af9`), disposition named by the operator (trace
   `1a0e7865c3b35715`), applied by the sanctioned-credential session
   (records `7f3a8f3ec`, 2026-09-28T11:34Z) — **3 EXTERNAL_QUESTIONS chunks
   FLAGGED → VALIDATED** (SNAP6-F1ii).

Zero down-flips; zero other up-flips (the exporter whitelists exactly these two
cohorts and aborts otherwise — SNAP6-F1). documents census at freeze:
EXTERNAL_NOTES 112V/0S · EXTERNAL_QUESTIONS 299V/80S/0F · MARK_SCHEME 13V/156S ·
QUESTION_PAPER 13V/164S · SYLLABUS 162S (out of scope, excluded from the
snapshot as at every prior freeze).

## §8(d) consequence (the reason this freeze exists)

At r6 the runner recorded §8(d) full-coverage 0.0 · micro-average 0.0 over 84
gold points on 89 scored queries, both views — honest production truth: the
210 HUMAN_VALIDATED chunk→SP mappings anchor on notes chunks, notes were
SUGGESTED, and the T-C05/T-C20 VALIDATED-only serving gate excluded exactly the
chunks that carry the mappings. At snap-006 the notes chunks are VALIDATED +
rev1 in production truth, so the served view contains the mapped chunks and
§8(d) is measured with coverage. The VALIDATION_BOUNDARY_VIOLATION contract is
unchanged (the served view is the production gate; anything it serves is
VALIDATED by definition). The r6 interpretation pre-registration (records
`09a624728`) binds the reading: leakage check + attribution caveat — a non-zero
(d) beside weak (a)/(b)/(c) is a coverage signal, not a retrieval-quality
signal, and must be read as such.

## Deltas vs snap-005 (manifest-bound; `verification_deltas.json` has the detail)

| id | delta | value |
|---|---|---|
| SNAP6-F1 | notes-axis promotion flips (SUGGESTED→VALIDATED, kind EXTERNAL_NOTES) | 350 |
| SNAP6-F1 | flagged-3 flip (FLAGGED→VALIDATED, kind EXTERNAL_QUESTIONS) | 3 |
| SNAP6-F2 | metadata-only paper_code stamps | 0 |
| SNAP6-F3 | question_anchors movement vs snap-005 | +0 rows (731 → 731, superset) |
| SNAP6-H1 | chunk_spec_hv.json | byte-identical, drift gate 0 divergences |
| SNAP6-M1 | read path | SELECT-only, readonly session, rolled back |

DRIFT GATE: all 210 HV mappings re-verified over the FROZEN chunk bytes against
the pinned resources store (`1245df009…`, store sha256_16 `e8b58a7109104bb7`);
anchor kinds recomputed 205 CLEAN / 4 MULTI / 0 SPAN / 1 MISS = the recorded
bridge census; projection census 210 rows / 209 with refs / 164 distinct refs /
181 distinct codes = the handoff §4 census (both enforced fail-closed at export
AND at harness load time).

Fidelity: spec_points / graph_edges / misconceptions / concept_attachments
BYTE-IDENTICAL to snap-005; question_anchors superset (+0); graph_code rows
set-equal with counts equal (source.date differs by design, embedded); resources
HEAD pin unchanged (`1245df009…`).

## Files (SHA256SUMS)

`chunks.jsonl.gz` `4181e5987f3a9c76…` · `spec_points.json` `b95361eff3ac5a70…` ·
`graph_edges.json` `f4dc1ddd10df2fa8…` · `misconceptions.json` `c659dbdc685a03a2…` ·
`question_anchors.json` `d22eef80d197090d…` · `graph_code.json` `63ddb20ca7e80dc5…` ·
`concept_attachments.json` `bff866bc4d28edba…` · `chunk_spec_hv.json` `b5b20ffa96b620bd…`

Exporter provenance: `snap006_export.py` (this directory), ALL VERIFICATIONS
PASS 2026-09-28 — 353 flips captured exactly as whitelisted, 0 drifts.
