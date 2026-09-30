# Pre-flight REFUTATION of the `CURRENT_EMBED_REV` 1→2 flip-back — 2026-09-28

**Commission + provenance.** The operator's "Proceed" (IM trace `1a0e7e245416ef65`,
2026-09-28) answered the recorded proposal "the `CURRENT_EMBED_REV` 1→2 flip-back will
bring the new corpus live — awaiting your go" — i.e., the standing-menu item recorded in
`d523f57`'s javadoc: "interim until rev2-era papers are teacher-validated, at which point
this flips back to 2". This session executed the commission as a **read-only pre-flight
first** (zero writes, zero code changes) and the pre-flight **REFUTED the flip**: the
revert condition's premise is false in production. The flip was **NOT executed**.

## The refutation (exact serving-gate replica)

The probe SQL mirrors `searchServingEligible`'s `SCOPE_EXISTS_VALIDATED` fragment
verbatim (embed_rev = :rev AND (exam_papers-VALIDATED paper branch OR
subject-scoped doc-VALIDATED branch), scope resolved to the sole ACTIVE curriculum
version `4CH1-2017`). Verified faithful: at rev=1 it returns exactly the serving set the
naive census implies.

| gate | eligible chunks | of them embedded |
|---|---|---|
| rev=1 (today's serving) | **615** | 615 |
| rev=2 (after the flip) | **0** | 0 |

Flipping the constant would regress serving **615 → 0** — a recurrence of the exact
T-C23 0-hit anomaly that Option B (session 129) was executed to end. **Not executed.**

Artifact: `preflight_exact_gate.json` (full supply matrix + both exact-gate runs).

## Mechanism — why the premise failed (probe-verified)

`document_chunks.embed_rev` is stamped at INGEST time with the constant's then-value.
`d523f57` rolled the constant 2→1 on 2026-09-25; **every ingest after that stamped rev1**:

- **09-25 papers re-ingest** (13 QP + 13 MS docs, `4ch1-…/qp.pdf`/`ms.pdf` naming,
  145+161 chunks): stamped **rev1** → validated by the 09-27 papers-axis wave.
- **09-26 card import** (298 EQ cards, 1 chunk each): stamped **rev1** → validated by
  the 09-28 card wave (295) + the flagged3 flip (3).
- The only pre-wave VALIDATED EQ doc (09-20 cohort, 11 chunks): rev1.

Result: **the ENTIRE VALIDATED corpus is rev1-stamped (615 chunks)**, while the actual
rev2 bridge corpus (the 09-20/21/22 ingest: 747 EQ chunks under 80 SUGGESTED docs, plus
the bridge QP/MS/notes/syllabus chunks) is **still 100% SUGGESTED**. The teacher waves
validated *content* — but that content's chunks carry rev1 stamps, so
"rev2-era papers are teacher-validated" never became true in the only sense the serving
gate reads (`embed_rev=2` ∧ VALIDATED).

Supporting artifact: `mechanism_probe.json` (per-cohort chunk/doc counts, card chunk
counts, paper-chunk source_uri samples). `embed_model_check.json`: both revs embed with
`gemini-embedding-001` @ 768 dims, 100% embedded — the rev stamp is a
corpus-content-generation marker, **not** a model marker (so a future re-stamp would not
mix vector models).

## Correction to this session's own prior record

The previous session summary stated "the papers axis wave validated rev2-era papers
09-27". **Wrong**: it validated rev1-stamped docs (the 09-25 re-ingest). Recorded here
as a correction; the wrong line exists only in IM conversation summary text, not in any
committed record.

## Corrected standing menu (supersedes the d523f57 revert condition as written)

The flip-back's real precondition is: **rev2-stamped VALIDATED serving supply > 0**.
Paths to that state (all operator-gated, none executed):

1. **Evaluate first (recommended, no production writes):** the 09-25/26 rev1-stamped
   VALIDATED corpus (cards + re-ingested papers) has NEVER been eval'd — the 0/9
   hit@10 was the OLD 09-14 glmocr corpus. Run the bench harness (run-004-a pattern)
   against today's serving set. If it scores bridge-quality, the corpus question
   dissolves: what serves today may already be good.
2. **Re-stamp path:** if (1) scores well, a controlled `embed_rev` re-stamp of the 615
   VALIDATED chunks (1→2, same model — no model mix) + the constant flip would serve
   them under the rev2 semantics. Production data write + core change, operator-gated,
   eval-gated.
3. **Original path (unchanged):** teacher-validate the actual rev2 bridge corpus
   (still 100% SUGGESTED) — then the constant flips back with a large VALIDATED rev2
   supply, exactly as d523f57 originally envisioned.

## Honest-absent

- No live serving probe was repeated for this record (no change deployed; production
  health re-verified `200 UP` ~11:5xZ after the flagged3 flip; the tc28 sweep
  (10:53Z, 6/6 GREEN) remains the latest full live check).
- The r6 §8(d) honest-0.0 reading is unaffected (it was anchored on SUGGESTED notes
  chunks excluded by the VALIDATED gate — unchanged by any of this).
- This session made **zero** production writes for this commission; the only 09-28
  production writes remain the sanctioned ones already recorded (wave `a5d13c0a`,
  flagged3 flip `0d5e4c4a`).
