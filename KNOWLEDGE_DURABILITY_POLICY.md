# SyllabAI Knowledge Durability Policy

**Status:** Accepted project operating policy  
**Date:** 2026-09-14  
**Owner:** Central `SyllabAI/syllabai` repository  
**Related:** `PROJECT_KNOWLEDGE_MAP.md`, `AGENT.md`, `PROJECT_CONTEXT.md`, `.syllabai/`

## 1. Principle

> **Important SyllabAI knowledge must not exist only in conversation.**

ChatGPT, Z.ai agents, GitHub discussions, PR conversations and temporary workspaces are working interfaces. They are not the project's canonical memory.

A durable project fact, decision, research conclusion, invariant or operational discovery is considered retained only after it has been written to an appropriate repository artifact and, where applicable, linked from `PROJECT_KNOWLEDGE_MAP.md`.

This policy exists to prevent knowledge loss when a conversation ends, an agent changes, a sandbox resets, a repository is rebuilt, or work moves to another chat.

## 2. What must be persisted

Persist knowledge when it can reasonably affect a future implementation, research interpretation, product behavior, data meaning, security boundary, deployment operation, or project decision.

This includes:

- architecture decisions and constraints;
- research findings that influence implementation;
- accepted or rejected product/technical directions;
- non-obvious engineering invariants;
- important root causes and their evidence status;
- schema, provenance, identity and validation semantics;
- curriculum/KG/learner-model semantics;
- RAG/retrieval and AI-runtime decisions;
- provider/model compatibility and operational findings;
- security, privacy and serving boundaries;
- deployment/reliability discoveries that future operators need;
- scope changes and explicit non-goals;
- benchmark definitions and acceptance criteria;
- important failures that establish a reusable guardrail;
- decisions made in conversation that another agent could otherwise reasonably forget or contradict.

## 3. What does not need persistence

Do not turn every conversation into documentation.

The following can remain ephemeral unless they reveal a durable lesson:

- casual brainstorming;
- discarded implementation alternatives;
- routine code discussion;
- temporary debugging hypotheses that were disproven;
- ordinary test output with no lasting significance;
- duplicated explanations of already-canonical material;
- one-off wording or UI polish discussion.

The goal is durable memory, **not documentation volume**.

## 4. Persist to the smallest correct artifact

Use the existing source-of-truth hierarchy before creating anything new.

Preferred order:

1. update an existing canonical architecture/research/decision document;
2. update the relevant agent implementation contract;
3. update operational evidence/state if the fact is implementation/deployment evidence;
4. create a new focused artifact only when no existing artifact has the correct ownership;
5. update `PROJECT_KNOWLEDGE_MAP.md` when a new cross-project canonical artifact is created or its discoverability materially changes.

Never create a duplicate document merely to record a conversation that belongs in an existing artifact.

## 5. Required workflow

For work that discovers potentially durable knowledge:

```text
Discover
   ↓
Classify
   ↓
Durability test
   ↓
Find existing owner
   ↓
Update existing artifact OR create smallest correct artifact
   ↓
Preserve status/provenance/evidence
   ↓
Update Knowledge Map / Project Context when needed
   ↓
Commit / PR
```

This is a normal engineering completion step, not a human approval gate.

## 6. Status discipline

Durable knowledge must not blur intent, implementation and evidence.

Use the most appropriate status from:

- `PROPOSED`
- `ACCEPTED`
- `IMPLEMENTED`
- `VERIFIED`
- `INFERRED`
- `REPORTED`
- `UNVERIFIED`
- `REJECTED`

Examples:

- A research idea discussed in a meeting is `PROPOSED` until adopted.
- An accepted ADR is `ACCEPTED` even if code is not implemented.
- A deployed feature may be `IMPLEMENTED` but `UNVERIFIED` for a particular production claim.
- An agent's diagnosis without independent evidence is `REPORTED` or `INFERRED`, not `VERIFIED`.

Historical records must not silently become current implementation truth.

## 7. Conversation handoff rule

When work moves from one conversation or agent to another, the next agent should be able to reconstruct the relevant project context from repository artifacts alone.

A handoff must therefore not depend on statements such as:

> “We discussed this in another chat.”

If that discussion contained durable information, its conclusion must already exist in the repository.

Conversation context can accelerate work, but it must not be a prerequisite for understanding an accepted architecture or binding implementation rule.

## 8. Agent behavior

Agents should:

1. consult `PROJECT_KNOWLEDGE_MAP.md` for unfamiliar cross-cutting work;
2. read the referenced canonical artifact before changing the affected subsystem;
3. preserve the artifact's terminology and status labels;
4. update the existing owner when discovering durable information;
5. create a new artifact only when ownership is genuinely missing;
6. update the Knowledge Map when a new canonical cross-project artifact is introduced;
7. record important root causes and evidence status rather than merely fixing symptoms;
8. never treat chat memory as a substitute for repository state;
9. continue ordinary work without waiting for human approval merely because a durable documentation update is needed.

## 9. Anti-patterns

### Conversation-only architecture

```text
Important decision
      ↓
Chat history
      ↓
Next session forgets it
```

**Rejected.**

### Duplicate-summary sprawl

```text
One architecture
  ├── canonical doc
  ├── chat summary
  ├── agent summary
  ├── another research summary
  └── another “final” plan
```

**Rejected.** Prefer one owner plus indexed references.

### Documentation as a merge gate

```text
Code complete
  ↓
wait for human to update docs
  ↓
stop all throughput
```

**Rejected.** Agents should persist durable knowledge as part of normal completion and continue when safe.

### Historical-state promotion

```text
Old proposal / old deployment
        ↓
agent assumes current truth
```

**Rejected.** Preserve status and provenance.

## 10. Definition of done for durable knowledge

A durable knowledge change is complete when:

- the correct canonical owner has been updated or created;
- status and provenance are clear;
- relevant agent implementation rules are updated when behavior is binding;
- the feature tracker is updated when feature scope/state changes;
- `PROJECT_KNOWLEDGE_MAP.md` is updated when discoverability requires it;
- the change is committed and reviewable;
- no competing source of truth has been introduced.

Routine code changes that discover no durable project knowledge do not require documentation changes merely to satisfy this policy.
