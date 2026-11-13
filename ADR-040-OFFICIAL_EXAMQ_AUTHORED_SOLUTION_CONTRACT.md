# ADR-040: Official exam-question solutions are SyllabAI-authored teaching explanations, with official marking evidence kept separate

**Status:** **ACCEPTED — product requirement explicitly confirmed 2026-11-14.** The semantic contract is accepted; implementation and corpus migration are not yet verified.

**Date:** 2026-11-14

**Scope:** `SyllabAI/syllabai-resources/Official-ExamQuestion/`, its extraction/enrichment/export/validation pipeline, and the official-paper learner surface in `SyllabAI/syllabai-v2`. Initial lanes: Edexcel International GCSE Chemistry 4CH1, Physics 4PH1, and Mathematics B 4MB1.

**Related:** ADR-037 (official-paper extraction/serving boundary); ADR-039 (correct-first, disclose-always); `Official-ExamQuestion/AGENTS.md`; `Official-ExamQuestion/SOLUTION-ENRICH.json`; G7/G8/G9.

---

## 1. Decision

For every learner-servable official exam-question part that has a solution:

**`solution_md` is the SyllabAI-authored teaching explanation.**

It teaches how to understand, approach, and solve the actual question at the appropriate qualification level. It must be correct against the question, official mark scheme, and applicable curriculum context.

It is not a storage slot for the raw extracted mark-scheme answer block. It must not be replaced by a verbatim mark-scheme cell or a lightly reformatted/rephrased copy of that cell.

A SyllabAI explanation may quote, reproduce, or adapt a specific official marking detail where educationally useful. Such use does not remove the requirement that the field as a whole is a genuine teaching explanation, and the source/provenance of adapted material must remain disclosed. Mark-scheme fragments alone do not satisfy the contract.

This is a semantic contract, not a requirement for uniform solution length. An MCQ explanation may be concise; a multi-step calculation may need a worked derivation.

## 2. Three distinct responsibilities

| Artifact | Canonical meaning | Responsibility |
|---|---|---|
| `solution_md` | SyllabAI-authored teaching explanation | Teaches the learner how to reach and understand the answer |
| Official mark-scheme evidence | Original official marking material, with source/page and correction provenance | Authoritative grading evidence; independently recoverable |
| `mark_points[]` | Structured official awardable criteria, marks, conditions and dependencies | Marking and mark accounting; not a substitute for a worked explanation |

The official mark scheme remains authoritative for grading. SyllabAI authorship does not authorize changing official marks, accepted alternatives, conditions, or awardable criteria. Corrections to graded values continue to require ADR-039 evidence and disclosure.

The official source archive remains byte-frozen and authoritative for source identity. SME-ExamQuestion remains a secondary cross-check/pedagogical reference, not the official grading authority.

## 3. Provenance and serving readiness

Authorship, extraction, correction, review, and serving readiness are separate dimensions.

A record is not SyllabAI-authored merely because it has been edited, enriched, generated, or placed in an enrichment file. Authorship and review must be explicit and supported by an auditable workflow. Generated but unreviewed explanations are not verified teaching content.

A part without a valid SyllabAI-authored explanation must not silently fall back to raw official mark-scheme text as the learner-facing worked solution. It must be explicitly withheld, marked incomplete, or handled by an approved product state until a valid explanation exists. Question readiness and solution readiness are distinct.

Where the old `solution_md` contains extracted/adapted official mark-scheme material, migration must preserve it as separately identifiable official marking evidence or a provenance-backed reference to the canonical source. It must never be silently discarded or relabelled as SyllabAI-authored.

## 4. Existing enrichment is a migration source, not a permanent exception

The current pipeline has a separate `SOLUTION-ENRICH.json` authored-answer layer. Its repository record contains 2,607 entries labelled `authored-r0` for Chemistry at drafting time. The exporter prefers this layer where an entry exists, but its documented behavior falls back to mark-scheme-derived `solution_md` for parts without an authored entry.

Preserve and reuse this existing authored work. The target is to materialize each verified authored explanation into canonical `solution_md`, with authorship/review provenance, while retaining official mark-scheme evidence independently. The enrichment ledger may remain as a historical source/audit record; it must no longer be required as an undocumented runtime override for canonical solution semantics.

The 2,607-entry count is a repository observation, not proof of current complete learner-serving coverage. Re-census it against the current corpus and serving bundles before making migration claims.

## 5. Gate responsibilities

**G7 — solution contract:** prove each learner-servable solution is a SyllabAI-authored teaching explanation with acceptable authorship/review provenance; official marking evidence remains traceable; mark points are valid and total the part marks; and the explanation is correct for the actual question part. Non-empty text, non-empty mark points, or matching mark totals alone do not constitute PASS. Reject raw/lightly adapted mark-scheme blocks presented as teaching explanations, ambiguous provenance, unreviewed generated text, missing official evidence linkage, incorrect answers, and mark arithmetic defects. Similarity checks may flag candidates but cannot prove authorship.

**G8 — educational product audit:** measure full-corpus authorship coverage, provenance completeness, correctness, pedagogical adequacy, missing/ambiguous records, and course/series readiness. Process completion and export success are not educational validation.

**G9 — learner surface:** verify the actual official-paper path in `syllabai-v2`: learners receive authored `solution_md`, not a mark-scheme fallback; the correct solution is attached to the correct part; rendering and reveal behavior work. Mandatory NOT_RUN checks never count as PASS.

## 6. Exporter and learner-surface law

The official-paper plane is distinct from the ordinary SME Exam Questions topic bank. Trace the official-paper path end-to-end; do not assume the ordinary question-bank player and official-paper reconstruction have identical content contracts.

The official-paper learner experience uses the validated SyllabAI teaching explanation for its worked-solution experience. Official marking evidence and structured mark points remain separate for internal assessment/marking workflows as permitted by product policy. No exporter precedence rule may reintroduce a mark-scheme fallback as though it were an authored solution.

## 7. Phased migration

1. **Contract and baseline census:** inventory every part across all Official-ExamQuestion lanes; classify source `solution_md`, authored overlays, provenance, official evidence, and actual serving behavior. Publish machine-readable and human-readable receipts.
2. **Schema and gate enforcement:** add only the provenance/evidence representation required by the existing model; update G7/G8 and negative controls; retain backward readability during migration but fail closed for new non-compliant learner-serving solutions.
3. **Chemistry migration:** use the existing authored layer as the primary source after a fresh verifier run; materialize only verified entries; preserve prior official marking evidence; close all fallback paths.
4. **Physics and Mathematics B:** run separate full-corpus censuses and author/review in bounded batches. Do not manufacture coverage or label mark-scheme text as authored. Missing/unreviewed parts remain explicitly incomplete.
5. **v2 integration:** update the official-paper exporter/bundle and learner surface; add exporter-precedence and rendered-surface regression tests.
6. **Full verification:** re-run corpus gates, exporter gates, G7/G8/G9 and CI; publish per-course coverage and remaining blockers.

Contract implementation and corpus migration coverage are separate statuses. A partially migrated corpus must not be described as fully learner-ready.

## 8. Safety and compatibility

- Preserve G0 source identity and the byte-frozen official archive.
- Preserve ADR-039 disclosure (`edit_status`, `edits[]`, `value_trace`) for serving-field departures.
- Never overwrite old mark-scheme-derived `solution_md` without first preserving its evidence/provenance.
- Preserve `mark_points[]`, marks, MCQ keys, source pages, figures, and correction history.
- Do not treat an LLM output as verified without required review/evidence checks.
- Do not weaken existing G7/G8/G9, exporter, asset, or cross-course gates.
- Keep provider/generation infrastructure out of the canonical educational data model.

## 9. Status at acceptance

- **ACCEPTED:** `solution_md` means a genuine SyllabAI-authored teaching explanation; official mark-scheme evidence and `mark_points[]` remain separate responsibilities.
- **IMPLEMENTED (existing, partial):** separate authored enrichment ledger and verifier; Chemistry exporter overlay for reviewed entries; official-paper serving plane and G9 surface checks.
- **UNVERIFIED:** full-corpus solution authorship coverage across Chemistry, Physics, and Mathematics B; current fallback exposure in every serving bundle; semantic quality of every authored explanation.
- **NOT IMPLEMENTED:** canonical in-place `solution_md` contract enforcement across all three lanes and prohibition of mark-scheme fallback as a learner-facing worked solution.

This ADR records the accepted target and does not promote historical receipts into current verification.

---

**Decision summary:** The official mark scheme tells SyllabAI what earns marks. The SyllabAI worked solution teaches the learner how to earn those marks. They must be independently identifiable, accurately linked to the same question, and preserved with provenance.
