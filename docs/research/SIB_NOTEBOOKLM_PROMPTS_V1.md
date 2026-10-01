# SIB NotebookLM Prompt Protocol v1

**Status:** PROPOSED  
**Protocol:** SIB-1.0

This document defines reusable prompts. Replace bracketed variables only. Do not rewrite the research contract per subject.

## 1. Master notebook instruction

Use this as the persistent instruction/context for the subject notebook:

```
You are the research engine for SyllabAI Subject Intelligence Build (SIB-1.0).

Subject: [SUBJECT]
Qualification: [QUALIFICATION]
Specification: [SPECIFICATION]
Current curriculum version: [VERSION]

Your task is to research this subject corpus systematically for a production adaptive-learning platform.

Source hierarchy:
1. current official specification;
2. current official assessment materials;
3. current authoritative textbook/resource;
4. official examiner reports;
5. legacy curriculum/assessment sources, explicitly historical;
6. supplementary sources.

Never silently mix current and legacy curriculum.
Always distinguish CURRENT from LEGACY.
Do not invent specification identifiers.
Do not treat question co-occurrence, semantic similarity, or frequency alone as proof of prerequisite or misconception relationships.

For each requested research artifact:
- follow its SIB artifact contract;
- cover the entire supplied corpus where relevant;
- identify source basis;
- identify important omissions or insufficient evidence;
- preserve temporal scope;
- use stable record IDs;
- produce structured Markdown suitable for downstream ingestion;
- do not produce generic motivational filler;
- prioritize concrete subject evidence and exam-relevant detail.

The output is research evidence for SyllabAI, not an instruction to modify SyllabAI's canonical educational graph or learner model.
```

## 2. Family prompt — Curriculum

```
Generate the requested CUR artifacts for [SUBJECT].

Analyze the current specification first, then connect the textbook, assessment corpus and supplementary resources to it.

For each artifact:
- cover the whole subject;
- identify important concepts and boundaries;
- distinguish explicit source statements from inferred relationships;
- identify gaps and ambiguous areas;
- preserve exact specification terminology where supported.

Artifacts:
[LIST CUR IDS]
```

## 3. Family prompt — Explanation

```
Generate the requested EXP artifacts for [SUBJECT].

For every major concept, analyze how it can be understood at beginner, standard and deeper levels.

Identify:
- core idea;
- mechanism/reasoning;
- conceptual distinctions;
- useful mental models;
- common student questions;
- alternative explanations;
- links to relevant specification points and assessment contexts.

Do not pad the report with generic pedagogy.
```

## 4. Family prompt — Misconceptions

```
Generate the requested MIS artifacts for [SUBJECT].

Use question papers, mark schemes, examiner reports, textbook explanations and the rest of the corpus to identify recurring student difficulties.

For each candidate misconception, provide:
- stable ID;
- concept/specification anchors;
- misconception statement;
- why it may occur;
- evidence;
- typical exam manifestation;
- likely diagnostic signals;
- intervention ideas;
- current/legacy scope.

Distinguish documented errors from inferred candidate misconceptions.
```

## 5. Family prompt — Assessment

```
Generate the requested ASM artifacts for [SUBJECT].

Analyze the complete available question-paper corpus, not a small sample.

Identify recurring:
- question structures;
- command words;
- mark allocations;
- contexts;
- concept combinations;
- progression patterns;
- difficulty characteristics;
- assessment coverage.

Where historical and current assessment differ, report the difference explicitly.
```

## 6. Family prompt — Mark Schemes

```
Generate the requested MS artifacts for [SUBJECT].

Analyze how marks are actually awarded.

Focus on:
- mark-point structures;
- required answer elements;
- acceptable alternatives;
- partial credit;
- recurring deductions;
- common mark-loss patterns;
- terminology and answer-quality expectations.

Use concrete mark-scheme evidence wherever possible.
```

## 7. Family prompt — Examiner

```
Generate the requested EXM artifacts for [SUBJECT].

Synthesize examiner reports across available sessions.

Identify recurring observations about:
- successful answers;
- weak answers;
- misconceptions;
- command words;
- terminology;
- common omissions;
- exam technique.

Separate repeated examiner observations from isolated observations.
```

## 8. Family prompt — Pedagogy

```
Generate the requested PED artifacts for [SUBJECT].

Using the subject corpus and previously generated SIB research where supplied, identify candidate:
- learning sequences;
- prerequisite paths;
- difficulty progression;
- explanation strategies;
- practice strategies;
- retrieval/interleaving opportunities;
- scaffolding;
- diagnostic interventions.

These are research candidates, not canonical SyllabAI pedagogy rules.
```

## 9. Family prompt — Practical / Procedural

```
Generate applicable PRA artifacts for [SUBJECT].

Analyze procedures, methods, technique choices, practical work, experimental reasoning, data handling and recurring procedural errors where relevant.

If an artifact is not meaningful for this subject, mark it NOT_APPLICABLE and explain why.
```

## 10. Family prompt — Problem Solving

```
Generate the requested PRO artifacts for [SUBJECT].

Identify recurring problem types and how successful solvers approach them.

Focus on:
- method selection;
- decision points;
- multi-step reasoning;
- common dead ends;
- worked reasoning patterns;
- transfer to unfamiliar contexts.

Use assessment evidence where available.
```

## 11. Family prompt — Historical

```
Generate the requested HIS artifacts for [SUBJECT].

Compare current and legacy sources.

Identify:
- specification changes;
- terminology changes;
- assessment changes;
- persistent concepts;
- recurring historical question patterns;
- what remains pedagogically useful.

Every historical conclusion must retain temporal scope.
Do not present legacy requirements as current requirements.
```

## 12. Family prompt — Tutor

```
Generate the requested TUT artifacts for [SUBJECT].

Design a subject-specific knowledge pack for a grounded tutor.

Identify:
- recurring student questions;
- useful follow-up questions;
- Socratic prompts;
- progressive hints;
- misconception-response patterns;
- exam-feedback patterns;
- concept comparisons;
- deep-dive explanations;
- subject-specific tutoring considerations.

The tutor must remain grounded in the subject corpus and should not invent unsupported curriculum requirements.
```

## 13. Family prompt — Gaps

```
Generate the requested GAP artifacts for [SUBJECT].

Red-team the complete subject corpus and the preceding SIB research.

Find:
- curriculum coverage gaps;
- potential KG gaps;
- assessment coverage gaps;
- misconception/intervention gaps;
- weak resources;
- retrieval ambiguity;
- tutor knowledge gaps;
- research priorities.

For each gap, identify evidence and explain what is missing.
```

## 14. Artifact QA prompt

Run after each family:

```
Audit the generated SIB artifacts against SIB-1.0.

Check:
1. required sections;
2. metadata completeness;
3. stable IDs;
4. current/legacy separation;
5. source basis;
6. specification anchors where supported;
7. absence of invented identifiers;
8. unsupported inference clearly labelled;
9. meaningful coverage of the supplied corpus;
10. explicit limitations/gaps.

Return:
- PASS/FAIL per artifact;
- missing sections;
- weakly supported claims;
- source-coverage concerns;
- duplicate records;
- current/legacy contamination;
- recommended regeneration targets.

Do not rewrite the artifacts unless explicitly asked.
```

## 15. Final notebook build audit

After all families:

```
Produce the SIB-1.0 final build audit for [SUBJECT].

Report:
- all 95 artifact IDs;
- REQUIRED / OPTIONAL / NOT_APPLICABLE;
- generated count;
- QA-passed count;
- QA-failed count;
- missing artifacts;
- major source gaps;
- current/legacy separation;
- major cross-family inconsistencies;
- research backlog.

Do not give an overall educational quality score.
This is a completeness and consistency audit.
```
