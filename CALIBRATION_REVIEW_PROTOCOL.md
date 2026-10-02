# CALIBRATION_REVIEW_PROTOCOL

**Status:** DRAFT — the rules are in force as written; they bite only when the first
decision-grade report exists. Satisfies the ADR-033 precondition that the C4 protocol
("min samples, segments, decision rule") is defined **before the first real retune
request**. Drafted 2026-10-02 by the S2 red-team lane while the BKT_UPDATED stream
accumulates (S2/ADR-033 merged as PR #53 → main `b6b1c9b`).

**Governs:** any change to the constants that shift BKT emission or decay behavior —
`LearnerProperties.Bkt` (`slip`, `guess`, `learnRate`, `shortAnswerGuess`,
`structuredGuess`) and `LearnerProperties.Decay` (`tauLowDays`/`tauMidDays`/
`tauHighDays`, `lowBandCeiling`, `highBandFloor`, `floor`, `reviewBelow`) — plus any
claim that "the learner model is (or is not) calibrated" made in a PR, an ADR, a
review, or a dashboard annotation.

**Instrument:** `GET /api/v1/research/learner-model/calibration` (TEACHER/ADMIN;
`?nodeId=` filter) — Brier, ECE, ten equal-width bins over the *latent* forecast
(`decayedPrior`), each bin carrying `count`, `meanLatentPredicted`, the
emission-mapped `meanPredicted`, `observedAccuracy`, `meanBrier`, and the signed
`calibrationError` = meanPredicted − observedAccuracy. Whole-report `sampleCount`
and `skippedRows` ride beside it.

---

## 1. What the instrument can and cannot say (read before any citation)

These are properties of the measurement, restated from the service contract as rules,
not background:

1. **Rows are node-outcomes, not independent learners.** One marked attempt updates
   every node it honestly tests, so the stream over-represents multi-node attempts.
   The report is *descriptive statistics over a dependent sample*. Nothing in this
   protocol may be expressed as a confidence interval over learners, and no automated
   actor may move constants from this report (§9).
2. **The mapped prediction uses the CURRENT configured slip.** Guess is per-row and
   immune (resolved from the row's own `questionType`/`optionCount` through the same
   resolver the update path uses), but a slip retune rewrites the mapping itself.
   Any before/after comparison that spans a slip change must re-score one side under
   the other side's slip. Comparing mapped-before against mapped-after across a slip
   change without re-scoring is an invalid comparison and cannot gate anything.
3. **The gap axis (`gapDays`) is on the stream but not cut in the report yet.**
   Until the gap cut ships, τ-band and τ_s proposals have no gate and are frozen
   (§7). This is the ADR's own declared sequencing, not this protocol's invention.
4. **Empty bins are no evidence, never good evidence.** The service already reports
   `count` per bin and zeroes the means on empty bins; §3.2 turns that into
   admissibility rules.

## 2. Segments (a number is only a number within a segment)

Every citation must name its segment. The mandatory segment axes, in order of when
they become cuttable:

- **Deploy segment (already enforced by the stream itself).** Rows predating the
  C1/C2 contract carry no `decayedPrior` and land in `skippedRows` forever — they
  never leave the stream; they dilute it. Decision-grade work uses only contract
  rows (`sampleCount`). The legacy pool is not "wrong data", it is the pre-S2
  segment, and it is invisible to the report by construction.
- **Format axis (mandatory for per-format decisions).** `MCQ_SINGLE` bucketed by
  `optionCount` as {2–3, 4, 5+}, `SHORT_ANSWER`, `STRUCTURED`, untyped/legacy. A
  pooled ECE mixes populations priced by different guess constants and can hide
  offsetting bias — the exact failure C2 exposed. Per-format constant decisions are
  illegal on the pooled report.
- **Gap axis (mandatory for τ decisions).** Bands {0, 1–30, 31–90, 91–365, 366+}
  aligned to the τ bands, with **zero-gap as its own stratum** — it is the
  bit-identity leg between the decayed and raw priors, and a zero-gap stratum that
  stops matching the raw curve is a regression alarm.
- **Node axis (`?nodeId=`)** — available now; for drift forensics and §5 small-cell
  suppression. A node slice inherits NO admissibility from the pooled report.

**Simpson rule:** if a pooled number and its segments disagree, the segments win, and
the disagreement itself is a finding to record, not a rounding artifact.

## 3. Decision-grade thresholds (the teeth)

### 3.1 Sample floors

The arithmetic that sets them: a bin with true observed rate p̂ and n rows has
standard error `SE = sqrt(p̂(1−p̂)/n)`; the smallest shift detectable at 2σ is
`Δ ≈ 2·SE` (worst case p̂ ≈ 0.9 in the top bins, p̂ ≈ 0.5 mid-range).

| n (segment or bin) | SE @ p̂=0.9 | detectable Δ @ 2σ | admissibility |
|---|---|---|---|
| < 35 | > 5.1 pt | > 10 pt | **descriptive only** — may not be cited in a decision |
| 35–99 | ~3–5 pt | ~6–10 pt | **directional** — may inform a proposal, may not gate a merge |
| ≥ 100 | ~3 pt | ~6 pt | **actionable** — may gate a constant change whose predicted effect ≥ 6 pt |
| ≥ 400 | ~1.5 pt | ~3 pt | **tight** — required to act on residuals smaller than 6 pt |

- Whole-report floor: `sampleCount ≥ 300` before the report itself may be called
  decision-grade for any purpose. At Cycle-1 volume (255 r1 placeholder-marked
  answers + a handful of honest r2 events) the first weeks are *expected* to be
  descriptive-only — that is the protocol working, not the instrument failing.
- Floors apply to every segment independently. A slice never inherits admissibility
  from its parent; a 4,000-row report with a 40-row STRUCTURED slice has a
  *directional* STRUCTURED slice.

### 3.2 Coverage and empty bins

- A whole-report claim requires **≥ 6 of 10 bins non-empty**, and additionally that
  the bin band holding the operational anchor mass (bins 4–6, where decayed anchors
  concentrate) **and** the top band (bins 7+) are populated. Top-band claims
  ("over-prediction at the top") are impossible — and must not be inferred — when
  the top bins are empty.
- `ECE` is cited only with a coverage annotation: `ECE 2.1 pt @ 7/10 bins, n=412`.
  An ECE without its coverage footnote is not a report.
- Empty bins are never interpolated, never filled by pooling across segments, and
  never silently dropped from the JSON (the API already renders all ten; only the
  *citations* are governed here).

### 3.3 Noise floor on ECE (silence is not calibration)

Finite samples give ECE its own noise floor: a contributing bin's
`|calibrationError|` fluctuates by ~`2·SE` at 2σ. Operational rule: compute
`maxSE = max over contributing bins of sqrt(p̂(1−p̂)/n_b)`; any ECE below `2·maxSE`
is **unresolved** — it may be recorded, but "ECE is low, therefore calibrated" is a
forbidden sentence below the floor. At Cycle-1 densities (n ≈ 30–60 per occupied
bin) the floor sits around 5–9 pt, which means *most early ECE readings will be
indistinguishable from zero noise*. Expect to wait for volume before the word
"calibrated" is legal.

### 3.4 Skip-rate guard (deploy-segment health)

`skipShare = skippedRows / (sampleCount + skippedRows)`.

- `skipShare ≤ 0.20` is required for decision-grade status (it decays naturally as
  contract rows accumulate over a fixed legacy pool).
- A **rising** skip share is a contract-breakage alarm (upstream stopped writing
  `decayedPrior`/format fields): the report is disqualified for all decisions until
  explained, regardless of sample size.
- `sampleCount = 0` with `skippedRows > 0` means the stream is all-legacy: the
  report is a placeholder and every number in it is vacuous (the service zeroes
  them honestly; §5 keeps them out of human-readable summaries).

## 4. Suppression rules

Two different things are suppressed, for two different reasons; both render as `—`
in any human-readable artifact (review notes, PR descriptions, dashboards):

1. **Statistical suppression (C4):** segments below the descriptive floor (n < 35)
   may not be cited in decisions. The raw JSON keeps everything — the API is
   TEACHER/ADMIN and carries counts only; this protocol governs *citations*, not
   the wire format.
2. **Small-cell suppression (C7 hygiene, borrowed early):** any slice with **n < 5**
   is suppressed from all human-readable output, because a nodeId- or format-sliced
   band of 1–4 rows can be cross-read against class surfaces to infer an
   individual. The controller javadoc records the full C7 disposition
   (ADMIN-only vs class-scoped vs k-anonymity) as an open decision; the n < 5 floor
   here is a floor, not the answer, and does not resolve C7.

Every cited number must carry its **as-of timestamp and the constant set in effect**
(slip, guess table, τ bands) — a number without its configuration is unfalsifiable.
The report JSON + the config diff in the citing PR satisfy this jointly.

## 5. Pre-registered decision procedure (what a retune PR must show)

A constant-change PR (defaults in `LearnerProperties` or environment config) is
reviewable only with all of:

1. **The as-of report** — JSON linked or inlined, with coverage annotation and skip
   rate, taken at a stated timestamp.
2. **The affected segment at admissible n**, showing signed `calibrationError` per
   bin — the sign matters: over- vs under-prediction selects the direction of every
   constant move.
3. **One variable per PR.** No batch retunes. On a stream this thin, a multi-variable
   move is unfalsifiable: the post-change signature cannot be attributed.
4. **The predicted signature, written BEFORE the merge** — e.g. "SHORT_ANSWER bins
   show observed > predicted by ~7 pt at n ≥ 100; raising `shortAnswerGuess`
   0.05 → 0.08 raises mapped predictions by ≈ (1−P̄)·Δg, expected to close ≥ 4 pt
   of the gap on the affected bins". A PR that cannot state what the report should
   look like afterwards is not a retune, it is a guess.
5. **The post-change checkpoint** — after ≥ 300 new contract rows or 14 days,
   whichever is later, re-run the report and compare against the predicted
   signature. Hit → the change stays and the ledger line closes. Miss → revert
   (constants are config; revert is cheap and honest) and record the miss in the
   ledger. Two consecutive misses on the same constant freeze it until the
   instrument itself is re-examined.
6. **C5 trigger (scheduled):** the first SHORT_ANSWER slice reaching n ≥ 100
   triggers the `shortAnswerGuess = 0.05` review *regardless of direction* — "no
   actionable residual at n ≥ 100" is itself a decision (keep), and must be
   recorded like one.
7. **C6 answer (scheduled):** the first format-cut report must state whether slip
   residuals differ by format (directional until per-format slip is admissible).
   Per-format slip is a *design change* (it breaks slip's global framing in the
   paper design) and goes through a new ADR — this protocol deliberately does not
   have the authority to admit it.

## 6. Sequencing against the instrument's declared follow-ups

The report cuts by nodeId only, today. Honest order of operations:

1. **Accumulate.** Stream grows; nothing is gateable until §3 floors are met. The
   protocol is doing its job while everyone waits.
2. **Ship the format cut** (a small service change: group rows by `questionType`
   in the same pass) — until it ships, *no per-format constant decision is even
   expressible*, which includes the C5 review. This cut is the first implementation
   ask this protocol generates.
   **LANDED 2026-10-02** — core PR #56 merged as main @ `6a51839` (branch
   `feat/calibration-format-cut`, head `1586d7d`; CI 162 ITs green): the report
   now carries per-format `FormatSegments` in the fixed taxonomy
   MCQ_SINGLE{2-3, 4, 5+, malformed}/SHORT_ANSWER/STRUCTURED/UNTYPED beside the
   pooled numbers — pooled statistics bit-identical to the pre-cut report (same
   accumulation order), skipped/legacy rows counted globally and never
   attributed (pre-contract rows carry no honest format), empty segments render
   honest zeros (an empty segment is no evidence, per §2's coverage rule), the
   `nodeId` filter cuts segments too. The C3 guard's paper-path degradation is
   now observable as the `malformed` bucket. Item 3 is unblocked and fires on
   §7's trigger (`sampleCount ≥ 300` or 14 days post-deploy, whichever first).
3. **First report review** — C5 review trigger + C6 slip answer, per §5.6/5.7.
4. **Ship the gap cut before any τ-band or τ_s proposal** (already the ADR's
   precondition); zero-gap stratum must match the raw-latent curve or the decay
   path is regressed.
   **LANDED 2026-10-02** — core PR #60 merged as main @ `c4b67e8` (branch
   `feat/calibration-gap-cut`, head `b5284bb`; CI 162 ITs green): the report now
   carries per-gap-band `GapSegments` in the τ-aligned taxonomy {0, 1-30, 31-90,
   91-365, 366+} beside the format segments — zero-gap as its own stratum, with
   the bit-identity leg made readable by `meanAnchor` (the mean raw ADR-031
   anchor over the segment's rows; within zero-gap its divergence from the
   decayed latent mean IS the decay-path regression alarm, and a healthy
   divergence is bounded by same-day decay alone, since a gap < 1 day records as
   0 and first-practice rows are exact identity); UNKNOWN as the defensive tail
   for missing/unparseable/negative gapDays (the publisher always writes
   `gapDays` beside `decayedPrior`, so a populated UNKNOWN stratum is itself a
   contract finding); pooled statistics bit-identical (same accumulation order,
   existing pins untouched); gap segments partition the contract rows exactly as
   the format segments do, skipped/legacy rows never attributed. Both mandatory
   axes of §2 are now cuttable in one call — this sequencing's implementation
   asks are complete, and the first report review (item 3) fires on §7's trigger
   fully expressible.

## 7. Cadence and recording

- **First review:** when `sampleCount ≥ 300` or 14 days after the S2 deploy,
  whichever comes first — even if descriptive-only (an early review exists to catch
  contract breakage and to exercise the procedure, not to force decisions).
- **Subsequently:** monthly, and on demand with any retune PR.
- **The ledger:** every review appends one dated line to ADR-033's follow-up
  section — date, `sampleCount`/`skippedRows`, `ECE @ coverage`, decisions taken
  (including explicit "keep" decisions and misses). The ledger is the memory; a
  review that leaves no ledger line did not happen.

## 8. What this protocol deliberately does not do

- **No automated retuning.** The stream is dependent-sample descriptive statistics;
  an actor moving constants on it unattended is malpractice with extra steps. Every
  move is a human-reviewed PR.
- **No per-learner claims.** The report says nothing about any learner; slices are
  research surfaces.
- **No BDT/misconception gating.** Different stream, different emission; the
  pattern may be reused there later, under its own ADR.
- **No resolution of C7** (research-surface authorization and small-cell design) —
  §4.2 borrows the n < 5 floor only. C7's three-way choice (ADMIN-only,
  class-scoped, k-anonymity) stays open.

## Appendix: worked micro-example (the rules applied)

Report as-of 2026-11-01: `sampleCount=410, skippedRows=1,900`, pooled `ECE=3.8 pt`,
bins 2–9 non-empty (bins 0–1 empty). Segments: MCQ_SINGLE(N=4) n=260, STRUCTURED
n=95, SHORT_ANSWER n=55, untyped n=0.

- Skip share 1900/2310 = 0.82 → **disqualified for decisions** (legacy pool still
  dominates; this is expected early and self-heals as contract rows accumulate —
  the guard forces patience instead of a premature "first real" retune).
- Even at skip share ≤ 0.20: pooled ECE 3.8 pt with maxSE over contributing bins
  ≈ 2.6 pt (n ≈ 55–260, p̂ ≈ 0.7–0.9) → 2·maxSE ≈ 5.2 pt > 3.8 pt → ECE is
  **unresolved**; "well calibrated" is not yet a legal sentence.
- STRUCTURED slice at n=95 is **directional** (35–99): it may motivate a proposal
  and must appear in the PR as directional; it cannot merge a constant change. Wait
  for n ≥ 100 — one more week of structured traffic — then §5 applies with the
  predicted-signature discipline.
- SHORT_ANSWER at n=55 does **not** trigger the C5 review yet (needs n ≥ 100).
