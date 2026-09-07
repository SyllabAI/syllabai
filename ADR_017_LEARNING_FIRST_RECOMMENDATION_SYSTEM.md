# ADR-017 — Learning-First Recommendation System

**Status:** Accepted  
**Date:** 2026-09-07

## Decision

SyllabAI will implement recommendations as a **learning-first adaptive action-selection system**, not as an engagement-maximizing social-media feed.

The objective is to maximize expected learning progress and appropriate syllabus coverage while respecting subject/curriculum, validation, authorization, prerequisite and teacher constraints.

## Canonical model

```text
Learner evidence/state
        +
Subject/specification graph
        ↓
Constrained candidate generation
        ↓
Content-based expansion
        ↓
Optional learned ranking
        ↓
Constrained exploration/diversification
        ↓
Explainable next-best learning action
        ↓
New learner evidence
```

## Rules

- Rule-based recommendations are the canonical baseline.
- Content-based similarity is a candidate-generation/expansion signal, not the sole objective.
- Collaborative filtering is a later experiment and can never override hard pedagogical/curriculum constraints.
- The old hard-coded `10%` random epsilon-greedy exploration proposal is rejected as a product rule.
- The old `0–5 / 5–20 / 20+ interactions` thresholds are heuristic examples, not scientific constants.
- Recommendation quality must ultimately be evaluated with learning outcomes, not CTR/watch time alone.
- Recommendations remain distinct from measured learner state.
- Recommendation reasons must be derived from structured evidence and reason codes.
- Educational videos are subject-scoped validated resources; generic YouTube recommendations are not SyllabAI's learning policy.
- Video watch time is telemetry, not automatic mastery.
- No recommendation microservice is needed under the current modular-monolith architecture.

## Existing feature IDs

This decision extends, rather than duplicates, the existing tracker rows:

- F-087 Rule-based Recommendations (MVP)
- F-088 Content-based Filtering
- F-089 Collaborative Filtering (future experiment)
- F-090 Hybrid Recommendation (canonical long-term architecture)
- F-091 Exploration
- F-092 Personalized Next Steps
- F-093 Recommendation Explanations
- F-025 Video Library / educational YouTube
- F-026 Video Watch Tracking

## Evidence integration

The recommendation engine consumes the Question Attempt / Learning Evidence subsystem. Subsequent attempts and other learning interactions provide outcome evidence for evaluating whether a recommendation helped.

## Scope

This is a long-term architecture decision and does not expand Cycle 1. Cycle 1 remains Edexcel IAL Chemistry with Tutor + Assessor focus under ADR-010.

The full design is canonical in `RECOMMENDATION_SYSTEM_ARCHITECTURE.md`; implementation rules are in `RECOMMENDATION_SYSTEM_AGENT_ADDENDUM.md`.
