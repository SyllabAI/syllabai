# Wave-2 validation worklist — LIVE census × gold-v5 (T-C41 ②, 2026-10-02)

**Status:** RECORDED — deterministic, offline, generated from the live census + gold-v5 bytes
(no writes, no keys beyond the sanctioned read path). **No validation is asserted here**
(AGENT.md core rule 6): this is a priority instrument, not an authorization.

## Why wave-2 is NOT the wave-1 surface (F-PROD-3, probe-verified)

Wave-1 composed from snap-006 on the QP/MS paper axis; production had already
executed that unlock. The live truth: the paper axis (owner=PAPER) has **zero
SUGGESTED chunks**; every actionable chunk is SUBJECT_BRANCH-owned:

| surface | chunks | docs | gate | in ACTIVE scope |
|---|---:|---:|---|---|
| EXTERNAL_QUESTIONS | 747 | 80 | SUGGESTED | yes |
| SYLLABUS | 162 | 162 | SUGGESTED | yes |
| QUESTION_PAPER (orphaned) | 369 | 28 | SUGGESTED | yes (via chunk subject) |
| MARK_SCHEME (orphaned) | 395 | 27 | SUGGESTED | yes (via chunk subject) |

- Combined actionable: **1673 chunks / 297 documents** — every one a
  single document-validation act away from serving (subject-branch gate).
- "Orphaned": these QP/MS documents have NO exam_papers row (never had —
  ingest-era partial imports); no paper placement or repair is needed, the
  subject branch serves them once their document is VALIDATED.
- The 64 REJECTED chunks (30 MS + 34 QP) are dead by teacher decision —
  excluded from wave-2 by construction.

## The instrument gap (decision required before execution)

`documents.validation_state` has NO write path on core main: the teacher
surface validates papers/versions/schemes only. Corpus documents are born
SUGGESTED (V29) and nothing on main flips them. Wave-2 execution options:

1. **Governed SQL batch** (notes-axis precedent, 09-28): operator authorizes,
   batch_run_id recorded, flip SUGGESTED->VALIDATED per document, fail-closed
   prestate/poststate, zero chunks mutated. Reusable for the full 297.
2. **New teacher endpoint** (`POST /teacher/content/documents/{id}/validate`
   + audit row): the durable instrument; product work on core before wave-2.

## Where the zero-recall gold classes are locked

Run-005-c-r8 measured recall@10 = 0.00 on mark_scheme, misconception,
multi_spec_point (standing arm-C §8.1 verdict). Wave-2's reach into that:

| class | gold queries | reachable from today's VALIDATED supply | unlockable by wave-2 doc-validate |
|---|---:|---:|---:|
| mark_scheme | 8 | 0 | 7 |

| misconception | 10 | 0 | 7 |

| multi_spec_point | 7 | 0 | 5 |

## Priority rows (top 20 of 297 actionable)

| document | kind | chunks | tier1 unlocks | tier2 unlocks | gold classes | spec codes |
|---|---|---:|---:|---:|---|---:|
| 2864752a-15ba… | QUESTION_PAPER | 13 | 3 | 2 | calculation, exam_question, factual | 0 |

| be45b0bc-d3ca… | QUESTION_PAPER | 11 | 3 | 2 | factual, why_wrong | 0 |

| 4a5b9118-cc96… | QUESTION_PAPER | 9 | 1 | 1 | exam_question | 0 |

| d7425adb-7159… | MARK_SCHEME | 10 | 6 | 0 | mark_scheme, why_wrong | 0 |

| 6c9ae70c-3ea6… | QUESTION_PAPER | 12 | 5 | 0 | conceptual, factual, prerequisite, vague_learner | 0 |

| aef3f019-04ec… | MARK_SCHEME | 13 | 5 | 0 | conceptual, multi_spec_point, prerequisite | 0 |

| a6b87bd9-8265… | EXTERNAL_QUESTIONS | 5 | 4 | 0 | conceptual, factual, misconception, multi_spec_point | 0 |

| 2ce67e31-2f7a… | EXTERNAL_QUESTIONS | 10 | 3 | 0 | misconception, multi_spec_point | 0 |

| 8e805176-f2d0… | MARK_SCHEME | 15 | 3 | 0 | calculation, mark_scheme | 0 |

| bb59e1af-6efd… | MARK_SCHEME | 15 | 3 | 0 | misconception, prerequisite | 0 |

| 3627b533-ef8e… | QUESTION_PAPER | 19 | 2 | 0 | conceptual, prerequisite | 0 |

| 3be30cc2-2f3d… | MARK_SCHEME | 19 | 2 | 0 | factual, prerequisite | 0 |

| 40d34459-e45c… | QUESTION_PAPER | 16 | 2 | 0 | conceptual, prerequisite | 0 |

| 63182543-35b3… | MARK_SCHEME | 13 | 2 | 0 | mark_scheme, misconception | 0 |

| 99d16dc5-fd4d… | EXTERNAL_QUESTIONS | 9 | 2 | 0 | multi_spec_point, prerequisite | 0 |

| 9b51cf89-ff6d… | QUESTION_PAPER | 16 | 2 | 0 | factual, multi_spec_point | 0 |

| e6aa0775-09fa… | EXTERNAL_QUESTIONS | 10 | 2 | 0 | factual, multi_spec_point | 0 |

| 39a7499c-389c… | MARK_SCHEME | 22 | 2 | 0 | prerequisite | 0 |

| acc7d673-0bf6… | MARK_SCHEME | 17 | 2 | 0 | prerequisite | 0 |

| c04c3f7c-9d7c… | QUESTION_PAPER | 8 | 2 | 0 | conceptual | 0 |

## Reading

- Priority = (tier2 unlocks, tier1 unlocks, class diversity, spec coverage).
- The full ordered list is in `worklist2.json` (`rows`), every row traceable to
  the census bytes + gold refs (chunk_ref contract identical to snap-006).
- Expected effect, honestly bounded: document validation moves the REACHABLE
  pool (2935 -> up to 2935 + 1673); it does not move vector quality. The
  §8.1 VALIDATED bars are the first bars a validated-corpus generation can
  legitimately clear; the Run005C re-record after wave-2 measures it.
