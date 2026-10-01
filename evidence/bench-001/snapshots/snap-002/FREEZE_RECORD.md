# SNAP-002 re-freeze record (2026-09-25) — T-C13 corpus snapshot discipline

Task: T-C13 / bench lane — operator directive "Proceed with snap-002 re-freeze"
(delivered in-chat with the Neon management credential; credential used
ephemerally, never persisted into any repository).

## What this is

The versioned re-freeze named by the C19 downstream record: a fresh read-only
capture of the serving database, frozen under the same evidence discipline as
snap-001. No recorded run consumed it at freeze time; no gold file changed.

## Method

- The original snap-001 exporter was session-local (never persisted). It was
  reconstructed from first principles against the frozen snap-001 artifacts and
  is carried here as `snap002_export.py` (export provenance).
- Read path: Neon branch `bench-snap-002-ro` (byte-copy of branch `production`
  at export time) + a dedicated role dropped with the branch. Zero production
  writes; zero production roles created.
- Fidelity anchors: `graph_edges.json` (sha256 f4dc1ddd10df2fa8) and
  `misconceptions.json` (sha256 c659dbdc685a03a2) regenerated
  **byte-identical** to snap-001, proving the reconstructed predicates are the
  t0 predicates. `graph_code.json` rows are set-equal with one recorded
  order-only drift (SNAP2-F2).

## Findings (recorded, none silent)

1. **SNAP2-F1 — the serving corpus was fully re-ingested since snap-001**
   (2026-09-17 -> 2026-09-25): 0/2,333 chunk refs and 0/2,182 unique chunk
   contents survive; the QP+MS corpus grew 2,333 -> 2,517 chunks across
   345 documents (4CH0 series were already in scope at t0; no series filtering
   was introduced). Consequence: gold-v1 anchors do NOT resolve into snap-002.
   gold-v1 stays SHA-paired with snap-001 for the recorded runs; any recorded
   run on snap-002 requires a gold-v2 regeneration first (set+snapshot pair
   discipline, spec §3/§4). This falsifies the C19 record's implicit
   assumption that only concept_attachments would change — recorded here as
   the freeze's headline finding.
2. **The T-C19 prediction is fulfilled**: `concept_attachments.json` is `[]`
   no more — it carries exactly the 117 HUMAN_VALIDATED concept->SP rows,
   1:1 with `scripts/c19_promotions.yaml` (ratified store @ 1245df009712) AND 1:1 with
   the serving DB's PART_OF pair set (which still says SUGGESTED — status lag
   only, recorded honestly; the serving projection predates the promotion).
3. **Spec registry grew by the 12 practicals** (4CH1-PR-01..PR-12, all
   VALIDATED SUBTOPIC): 182 -> 194 rows under the unchanged t0 predicate.
4. **Question anchors grew 119 -> 720** VALIDATED versions (t0 anchor codes
   all still present). Ordering is now deterministic (recorded delta).
5. **Serving projection lag (context, not changed by this freeze)**: the
   serving DB carries the settled pilot graph (98 CONCEPT + 19 MISCONCEPTION,
   152 VALIDATED semantic edges) while the ratified store has advanced to
   193 nodes / 488 edges / 272 HV semantic (the closed T-C11 S1-S4 program).
   Re-projection/sync remains the pending operator-gated lane this freeze
   does NOT self-start.

## Boundaries respected

- gold-v1: byte-untouched (validator selftest 6/6 green post-freeze).
- No recorded run, no gold-v2, no serving re-projection, no core sync —
  none commissioned; all remain operator-held.
- Production: read-only via an isolated branch; branch + role dropped after
  the freeze; no production writes of any kind.

## Artifacts

| file | sha256 | bytes (uncompressed) |
|---|---|---|
| `chunks.jsonl.gz` | `f421e9f96216518cb454e5b5f2f16b3da8cc2f602ebc360504a52914d1727b1a` | 3059830 |
| `concept_attachments.json` | `bff866bc4d28edbaa1765af1a748d1aeebe47dab1ed97c354b329030467acd1b` | 10947 |
| `graph_code.json` | `422341a3a32b2f46a65c1c8412bf4ba1083638306e8dcb025f2ac52ee3a0c20f` | 31716 |
| `graph_edges.json` | `f4dc1ddd10df2fa8fe87d5f57e52fc7c3abc2cf44951ad22cd7b7854aadffa5a` | 15686 |
| `misconceptions.json` | `c659dbdc685a03a2c7ed4ac3cb6c00dc3d695a18046044a100219c661ba830c1` | 2264 |
| `question_anchors.json` | `11a53c11e6e35cec6f7bc436a0765a63a321a671f5c9e54be92a41e8571fc78f` | 154953 |
| `spec_points.json` | `b95361eff3ac5a70040e0bc79af7b5f5666704db350505830ca409ead607d6fb` | 39379 |

Manifest: `manifest.json` (counts, predicates, deltas, pairing, serialization
notes). SHA256SUMS covers the seven artifacts (t0 convention).
