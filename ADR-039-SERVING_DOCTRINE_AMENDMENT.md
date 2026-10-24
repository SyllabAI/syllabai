# ADR-039: Serving content is CORRECTED, not canonized — ADR-037's verbatim-first and no-LLM constraints are superseded by the fix-and-disclose doctrine: any tool may improve any serving field, every departure from the source layer is machine-disclosed, and graded values must corroborate the mark scheme of record

**Status:** **ACCEPTED — operator directive 2026-10-24** (chat trace `1a16ad28dae2ab99`: "We changed doctrine. No verbatim needed, and no zero llm rule. We can fix and make things better."). This file is the drafted law of record (authoring dispatch trace `1a16ad80f7574299`); the implementation clauses below (§4–§8) are the drafted transition, the two §7 operator adjudication points were adjudicated 2026-10-24 (marking carve-out CONFIRMED, trace `1a16cdc9eda1a645`; regeneration timing = dedicated receipt run, trace `1a16ce03e8a9fe35`) — the code wave may proceed. Where this ADR conflicts with ADR-037, **this ADR wins**; ADR-037 remains the historical record of the extraction era and its gates, ledgers and corpus evidence carry forward except as amended here.

**Date:** 2026-10-24
**Scope:** `syllabai-resources/Official-ExamQuestion/` (docs, gates, ledgers, canaries), the converter `official_examq_extract.py` (G2 semantics, negative controls, schema emission), the serving schema `syllabai.official-paper-questions/x.y`, and downstream v2 exporter laws. **No change to `syllabai-pastpapers`** (still the byte-frozen archive of record), **no change to SME-ExamQuestion's role** (independent cross-check reference), no change to G0 identity law or the one-way derivation `pastpapers → resources`.
**Related:** ADR-037 (superseded in part — see §3 for the exact clause map); ADR-021 (Markdown interchange, unchanged); wave-15 UX doctrine (SOLUTION-ENRICH — subsumed by §6); C71 v2 export law (kept, see §8); T-C17 fail-closed precedent (generalized to fail-disclosed).

---

## 1. Why amend (evidence, not vibes)

ADR-037 was written against a real enemy: the §1 audit showed free-form LLM generation fabricating question text, marks and context while answer-only checks passed. Verbatim-first was the correct counter for a **one-shot generation** failure mode. Eighteen converter versions later (v0.1 → v0.14.1), the corpus record shows the doctrine's cost has outgrown its protection:

- **The doctrine already bent under product needs.** Wave-15 sanctioned "non-verbatim for presentation; values never invented" (STEM-RESTORE doctrine string); SOLUTION-ENRICH now carries **1,275 LLM-authored worked answers** served to learners; MS-LINK-OVERRIDES and MCQ-KEYS exist precisely because the printed sources are sometimes *wrong or defective* and verbatimness would serve defects to students. The corpus is no longer verbatim; it is verbatim-plus-undisciplined-exceptions.
- **Honest refusals became permanent process.** Every source defect now costs a full human ledger cycle with rendered-page evidence (2020-01 Q7(a) keys, 2019-06 3(d)(ii) image answer, 4 manual-crop rounds). Correct in spirit; heavyweight in mechanism — and the heaviness exists to protect a rule (verbatimness) that the product no longer wants.
- **Known defects were shipped because fixing them was unlawful.** PUA glyphs served as invisible garbage for multiple waves (F48: ~2.4k occurrences) because the fix "must not be done ad hoc inside the converter" — a correct call *under* verbatim doctrine, an absurd one under fix-and-disclose. The 2020-01 printed MS typo ("C is incorrect as iodine is dark grey") survived in serving text because correcting it required a ledger ceremony.
- **61 of 61 ledger findings are parsing scars, not content scars.** F1–F61 catalogue layout drift, marker degenerations and anchoring bugs — the deterministic parser's own failure surface. Meanwhile the *content-quality* complaints (terse MS cells, median 149 chars vs SME's 732) were only resolvable by doctrine exception (F60/F61).
- **The gates that actually protect the product never depended on verbatimness.** G0 identity (registry sha wins over printed text), G1 structure (marks add up), G5 answer linkage, G6 registry, and the negative-control discipline are all orthogonal to whether text is copied or improved. What verbatim uniquely bought was *change detection* — and change detection is better bought by **mandatory disclosure** than by prohibition.

Verdict: keep the verification spine, retire the prohibition. The pipeline's job is no longer "prove nothing changed" but **"prove everything that changed is disclosed, evidenced, and value-safe."**

## 2. The one-sentence rule

**The pipeline improves; provenance discloses.** Every serving field may be corrected, clarified, or enriched by any tool — deterministic script or LLM — provided that (a) every departure from the extracted source layer is machine-readably disclosed in the document itself, (b) every graded value (marks, mark_points, MCQ keys) traces to the mark scheme of record or carries explicit evidence for its correction, and (c) the archive stays byte-frozen and G0 identity holds. An edit that cannot be disclosed is not an edit; it is a defect.

## 3. Clause map — what ADR-039 keeps, amends, and retires from ADR-037

| ADR-037 clause | Disposition | Notes |
|---|---|---|
| G0 identity (registry wins, sha256 match) | **KEEP unchanged** | Identity is not a verbatim concern; the "June 2020" mislabel law stands |
| G1 structure (Σ parts = printed total = paper total) | **KEEP unchanged** | Structural integrity of marks; corrections to *printed* errors must be disclosed (§4) but sums must still reconcile or carry a documented defect note |
| G2 verbatim (5-gram overlap ≥ 0.95) | **AMEND → G2-D disclosure** | See §4. The 5-gram machinery is retained but inverted: it now verifies *disclosure completeness*, not prohibition |
| G3 MCQ integrity (option set + exactly one key) | **AMEND** | Options match the printed set **or** carry a disclosed, evidenced correction (e.g., the 2020-01 rebuttal typo may now be fixed in place with provenance instead of only via ledger). "Unresolved → review, never auto-keyed" stands |
| G4 figures (every mention resolves to an asset) | **KEEP unchanged** | Unaffected by doctrine |
| G5 answer linkage (positional MS linkage) | **KEEP unchanged** | Positional linkage remains the *starting point* and the evidence base; it is what makes disclosure verifiable |
| G6 registry (no fabricated spec codes) | **KEEP unchanged** | Labels are still registry-validated or documented gaps |
| G7 solutions (mark_points sum to part marks) | **KEEP, with disclosure** | Enrichment of solution text is now ordinary (not a wave exception); mark_points sums still reconcile |
| "LLM confined to tagging and linking" | **RETIRE** | LLM may touch any serving field under disclosure (§4) |
| "The converter extracts; it never authors" | **RETIRE** (replaced by §2) | The extraction *layer* remains the deterministic baseline that disclosure is measured against — the converter still extracts first; improving passes run *on top of* the extraction with provenance |
| Negative controls N1/N2/N3 | **RE-SPECIFY** (§5) | Detection target shifts from "mutation" to "undisclosed mutation" |
| Byte-frozen archive, one-way derivation | **KEEP unchanged** | Unaffected |
| Human review queues ("agents must not decide") | **KEEP, narrowed** | Graded values and figure verdicts still require eyeball evidence; text corrections no longer require a ledger ceremony when disclosure is complete and value-safe |
| Wave-15 UX doctrine (non-verbatim presentation OK) | **SUBSUMED** | Presentation-layer freedom is now corpus-wide law; the values-never-invented clause generalizes into the value_trace contract (§4) |

## 4. The disclosure contract (G2-D)

The serving schema bumps to `syllabai.official-paper-questions/0.2`. Every part carries:

```
provenance: {
  paper_id, qp_sha256, ms_sha256,          // unchanged from 0.1
  source_pages: [...],                      // unchanged
  edit_status: "extracted" | "corrected" | "enriched",
  edits: [                                  // absent = extracted (0.1 corpora load as extracted)
    {
      field: "problem_md" | "stem_md" | "solution_md" | "choices[].text_md" | "mark_points[]" | ...,
      kind: "typo-fix" | "clarification" | "notation" | "enrichment" | "structural-repair" | ...,
      tool: "official_examq_extract.py v0.15.0" | "llm:<model>" | "agent:<lane>" | "human",
      evidence_ref: "..."                   // rendered-page ref, MS row, chemistry note, verifier receipt
    }
  ],
  value_trace: {                            // graded values: numbers, keys, marks
    keys: "ms-positional" | "ledger:MCQ-KEYS" | "corrected:<evidence_ref>",
    marks: "ms-printed" | "corrected:<evidence_ref>",
    numbers: "verifier:official_examq_enrich_verify.py PASS" | "source-printed"
  }
}
```

**G2-D passes when:**
1. parts with `edit_status: "extracted"` still 5-gram-match their source region (the old G2 check, demoted from law to *provenance correctness assertion* — it now catches a mislabeled `edit_status`, not an edit);
2. every part with `edit_status: "corrected"|"enriched"` carries a complete `edits[]` whose fields and kinds are in the vocabulary, with non-empty `evidence_ref`;
3. every numeric token and every MCQ key in edited text either appears in the source evidence (QP text, MS cell, mark points) or verifies as correct arithmetic on printed values — the F60/F61 verifier (`official_examq_enrich_verify.py`, exit 1 on any problem) becomes the **corpus-wide build-time standard**, not an enrichment-only harness;
4. `value_trace` is consistent with the actual emission (a part whose key came from the ledger may not claim `ms-positional`).

**Fail-disclosed, not fail-closed:** a gate that cannot prove disclosure is a failure — but the *response* to a provable defect is now "fix it with disclosure" (converter or authored pass, tool of choice), not "freeze it and queue a human." The human queue narrows to what genuinely needs eyeballs: figure verdicts (CROP-REVIEW keeps its role), graded-value corrections without printed-MS evidence, and anything the verifier refuses.

## 5. Negative controls (re-specified, still mandatory every run)

| Control | Injection | Old pass condition | New pass condition |
|---|---|---|---|
| N1 | +1 mark bump on a part | G1 DETECTS the drift | G1 DETECTS the drift **as an undisclosed mutation** — the run must surface it as a value_trace violation, not serve it |
| N2 | one-word paraphrase of a served line | G2 DETECTS the overlap drop (prohibition) | the pipeline DETECTS that the line is no longer `extracted` **without a matching `edits[]` entry** — the run must surface it as a disclosure violation (the paraphrase itself is now legal *when disclosed*) |
| N3 | fake spec code | G6 refuses | unchanged |

All three MUST be DETECTED 3/3, else the run is void — the discipline stands; its target is now the *disclosure machinery* instead of the *prohibition machinery*.

## 6. The ledgers under the new doctrine

- **MCQ-KEYS.json / MS-LINK-OVERRIDES.json** — remain the evidence records of record for their existing entries (nothing is rewritten; corpus values already derive from them and canaries C28–C31, C52 keep that binding). New corrections may land **either** through the ledgers (when the printed MS is defective) **or** directly in the corpus as a disclosed `corrected` edit with rendered-page evidence — the ledger is no longer the only lawful path, but graded-value corrections always require the evidence bar (§7, adjudication point 1).
- **CROP-REVIEW.json** — unchanged in role (figure verdicts stay an eyeball domain; `manual_crop` machinery unchanged).
- **STEM-RESTORE.json / SOLUTION-ENRICH.json** — their *content* carries forward; their doctrine strings are amended (§ DOC-AMENDMENTS). SOLUTION-ENRICH's pending tranche 2 (1,332 parts) proceeds under §2 as ordinary enrichment — the "withheld until verified" gate stays, now expressed as verifier-pass-or-withheld rather than doctrine exception.
- **LEDGER.md** — unchanged (append-only parser history; F1–F61 stand as the record of the extraction era).
- **CHANGELOG.md** — appends v0.15.0 (see DOC-AMENDMENTS); history is never rewritten.

## 7. Operator adjudication points (ADJUDICATED 2026-10-24 — both resolved; the code wave may proceed)

1. **Marking integrity carve-out. Law CONFIRMED as proposed** (operator word, chat trace `1a16cdc9eda1a645`): `marks`, `mark_points[]`, and MCQ keys are graded values — LLM may *propose* corrections, and the pipeline may *apply* a correction only with printed-MS or rendered-page evidence recorded in `evidence_ref`; no free invention of keys or marks, ever. The v2 C71 separation (authored learner narrative vs verbatim-MS marking data) is **kept** — marking data stays corroborated to the MS of record even under fix-and-disclose.
2. **Corpus regeneration timing. DEDICATED RECEIPT RUN (option A)** (operator word, chat trace `1a16ce03e8a9fe35`): the 54 committed slices carry `edit_status: extracted` by consumer-side default until regenerated; after converter v0.15.0 lands, one full `run_all.sh` receipt run re-issues all 54 slices with explicit `/0.2` provenance fields (byte-identical content, provenance blocks only). The transition diff must be **pure provenance additions** — any content delta in that diff is a defect to be ledgered, never folded in.

## 8. Transition plan (the receipt chain)

1. **Docs first** (this package): ADR-039 standalone + DECISIONS.md entry + `Official-ExamQuestion/` amendments (DOC-AMENDMENTS.md) + CHANGELOG v0.15.0 entry — committed together per the outputs-and-pipeline law's doc analogue.
2. **Converter v0.15.0**: G2 → G2-D (disclosure checks), N1/N2 re-specified, `edits[]/value_trace` emission, schema `/0.2`. Canaries re-baselined: C9 re-worded to the new controls; C49/C52/C56 stand (they assert recovery/cleanliness, not doctrine); the "all gates PASS" matrix regenerates with G2-D receipts.
3. **Verifier promotion**: `official_examq_enrich_verify.py` runs corpus-wide at build time (was: enrichment-slice scope).
4. **Receipt run**: full-corpus re-run, validation reports re-issued, MULTI-SERIES-REPORT refreshed, canaries hold — the transition's proof of record.
5. **v2 follow-through**: exporter laws unchanged except C71's note gains the ADR-039 citation; hub learner-facing copy drops "verbatim" framing where it conflicts (stub notes already corrected in v0.14.1).

## 9. Consequences

- **Gets better:** known source defects become fixable in place (PUA residue, printed typos, terse MS cells) without ledger ceremonies or doctrine exceptions; the enrichment backlog (1,332 parts) proceeds as ordinary work; review queues shrink to genuinely human items; the SME-vs-official quality gap (732 vs 149 chars) closes corpus-wide.
- **Gets riskier:** silent drift — a "fix" that changes meaning, an enrichment that invents a value, a correction that corrupts a key. Mitigations are mechanical, not aspirational: G2-D disclosure completeness, the corpus-wide verifier, value_trace consistency, the marking carve-out (§7.1), and the standing canary suite. The 54-slice regeneration receipt makes the before/after diff auditable in both directions.
- **Culture:** ADR-037's §1 audit remains the founding evidence — free-form generation without disclosure is still disqualified. What changed is the response: the pipeline no longer forbids authorship; it *receipts* it.
