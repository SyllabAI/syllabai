# Corpus validation worklist — snap-006 × gold-v5 (T-C40 ①, 2026-10-01)

**Status:** RECORDED — deterministic, offline, generated from the committed snapshot/gold bytes (no DB, no keys).
**Purpose:** the review's order item 1 ("validate corpus") as an actionable instrument. It does NOT validate anything:
content flips stay operator-gated (AGENT.md core rule 6; S8D §6 "no agent may assert the validation").

## Census

- Chunks: **965/4181 VALIDATED (23.1%)**, 3216 SUGGESTED
- SUGGESTED by kind: {"EXTERNAL_QUESTIONS": 747, "MARK_SCHEME": 1333, "QUESTION_PAPER": 1136}
- Batches (document × kind): 132 total, 112 already fully VALIDATED

## Where the zero-recall gold classes are locked

Run-005-c-r7 measured recall@10 = 0.00 on mark_scheme, misconception, multi_spec_point. This worklist shows why:

| class | gold queries | reachable from today's VALIDATED supply | locked behind SUGGESTED |
|---|---:|---:|---:|
| mark_scheme | 8 | 2 | 6 |

| misconception | 10 | 5 | 5 |

| multi_spec_point | 7 | 3 | 4 |

## Priority rows (top 15 of 132)

| batch | kind | chunks | SUGGESTED | tier1 unlocks | tier2 unlocks | gold classes |
|---|---|---:|---:|---:|---:|---|
| 4CH1/2C | QUESTION_PAPER | 207 | 164 | 26 | 4 | calculation, conceptual, exam_question, factual, misconception, multi_spec_point, prerequisite, vague_learner |

| 4CH0/2C | QUESTION_PAPER | 218 | 178 | 11 | 4 | calculation, conceptual, exam_question, factual, prerequisite, vague_learner, why_wrong |

| 4CH1/2CR | QUESTION_PAPER | 123 | 103 | 17 | 2 | calculation, conceptual, exam_question, factual, misconception, multi_spec_point, prerequisite |

| 4CH1/1C | QUESTION_PAPER | 259 | 231 | 17 | 1 | conceptual, factual, misconception, multi_spec_point, prerequisite, why_wrong |

| 4CH1/1CR | QUESTION_PAPER | 146 | 146 | 10 | 1 | conceptual, factual, misconception, multi_spec_point, prerequisite, vague_learner, why_wrong |

| 4CH1/2C | MARK_SCHEME | 232 | 186 | 30 | 0 | calculation, conceptual, factual, mark_scheme, multi_spec_point, prerequisite, why_wrong |

| 4CH1/1C | MARK_SCHEME | 307 | 274 | 28 | 0 | calculation, factual, misconception, multi_spec_point, prerequisite, why_wrong |

| 4CH1/2CR | MARK_SCHEME | 176 | 152 | 24 | 0 | calculation, conceptual, factual, mark_scheme, misconception, multi_spec_point, prerequisite, why_wrong |

| 4CH0/1C | MARK_SCHEME | 358 | 342 | 20 | 0 | conceptual, factual, mark_scheme, misconception, multi_spec_point, prerequisite, vague_learner |

| 4CH0/1C | QUESTION_PAPER | 328 | 314 | 18 | 0 | conceptual, factual, misconception, multi_spec_point, prerequisite, vague_learner |

| 4CH0/2C | MARK_SCHEME | 218 | 176 | 18 | 0 | conceptual, mark_scheme, misconception, multi_spec_point, prerequisite, why_wrong |

| 4CH1/1CR | MARK_SCHEME | 203 | 203 | 12 | 0 | conceptual, factual, misconception, multi_spec_point, prerequisite |

| 4CH1/1C | EXTERNAL_QUESTIONS | 212 | 120 | 7 | 0 | factual, misconception, multi_spec_point, prerequisite |

| 4CH0/2C | EXTERNAL_QUESTIONS | 143 | 117 | 5 | 0 | conceptual, factual, misconception, multi_spec_point |

| 4CH1/2C | EXTERNAL_QUESTIONS | 168 | 87 | 4 | 0 | factual, multi_spec_point, prerequisite |

## Reading

- Priority = (tier2 unlocks, tier1 unlocks, class diversity) — validating a top batch makes gold
  evidence REACHABLE by the serving gate, which is the precondition for any recall movement the
  next §8.1-governed run can even measure.
- The full ordered list is in `worklist.json` (`rows`), every row traceable to snapshot bytes.
- Expected effect, honestly bounded: validation moves the REACHABLE pool; it does not by itself
  move vector quality (embeddings already exist for the rev corpus). The §8.1 VALIDATED bars
  (0.0734/0.1184/0.1683) are the first bars a validated-corpus generation can legitimately clear.
