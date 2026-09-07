# Agent Addendum — Learning-First Recommendation System

This document is mandatory reading for work involving recommendation ranking, personalized next steps, educational video discovery, resource discovery, learning playlists, syllabus pacing, exploration/exploitation, recommendation telemetry, or recommendation evaluation.

## Canonical documents

- `RECOMMENDATION_SYSTEM_ARCHITECTURE.md` — canonical recommendation architecture.
- `QUESTION_ATTEMPT_AND_LEARNING_EVIDENCE.md` — canonical question-level evidence source.
- `LEARNING_EVIDENCE_AGENT_ADDENDUM.md` — evidence-layer rules.
- `SUBJECT_ARCHITECTURE.md` — subject/specification-point boundary.
- `TEACHER_ARCHITECTURE.md` — teacher/classroom constraints.
- `DECISIONS.md` — architecture decisions.

## Non-negotiable rules

1. The recommender optimizes expected learning progress and appropriate syllabus coverage, not watch time, clicks or session duration.
2. Hard constraints execute before learned ranking: enrolled subject, curriculum version, content validation state, authorization, prerequisite safety and teacher constraints.
3. `SpecificationPoint` is a canonical learning anchor; recommendations must preserve its subject/curriculum provenance.
4. Rule-based candidate generation is the safe baseline. Content similarity expands candidates. Learned/collaborative ranking is a later experiment.
5. Do not make collaborative popularity a hard requirement or allow it to override prerequisites or teacher requirements.
6. Do not hard-code the old `10% random exploration` rule. Exploration must be constraint-aware and learning-relevant.
7. Do not treat the old `0–5 / 5–20 / 20+ interactions` thresholds as scientific constants. Data-regime eligibility must be evidence-based and evaluable.
8. Keep recommendation output distinct from measured learner facts.
9. Recommendation explanations must use structured reason codes/evidence, never invented LLM statistics or unsupported causal claims.
10. Do not recommend unvalidated/draft content to learners.
11. Do not use generic YouTube home/recommendation feeds as SyllabAI's learning policy.
12. Video watch time is telemetry/evidence, not automatic mastery.
13. Use the Question Attempt / Learning Log as the canonical question-level downstream outcome signal.
14. Preserve a deterministic baseline so future recommendation models can be evaluated against it.
15. Do not create a recommendation microservice without a genuine runtime/lifecycle boundary. The current application boundary is the `recommendation` module in `syllabai-core`.
16. Recommendation experiments must record policy/version, candidate/ranking policy, eligible population, subject/curriculum scope, outcome metrics and observation window.

## Important interpretation

The product is not "YouTube for studying." The product is an **adaptive learning-action selector** that can sometimes surface a video, but can just as legitimately surface a prerequisite concept, question set, Target Test, Tutor intervention, revision note, due retrieval, or teacher assignment.

## Educational YouTube

F-025 is a video-content capability, not a generic entertainment/discovery feed. Videos must be subject-scoped, provenance-aware, educationally relevant and servable under the platform's content validation policy. Approved-source/channel restrictions are allowed. The recommender may rank videos based on the learner's diagnosed need.

## Scope

This architecture is long-term. It does not expand Cycle 1 beyond Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010.
