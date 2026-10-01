# Task DAG

Tasks are dependency-aware units of work. Agents should select READY tasks whose dependencies are satisfied rather than treating the project as a single queue.

## Statuses

- `READY` — executable now.
- `EXECUTING` — owned by one agent.
- `BLOCKED` — dependency or hard gate prevents progress.
- `VERIFYING` — implementation complete; evidence/tests running.
- `DONE` — acceptance and evidence complete.

## Parallelism rule

Parallelize tasks when they do not share mutable resources or overlapping contracts. Coordinate or serialize tasks that touch:

- Flyway/schema history
- the same cross-repository contract
- authoritative educational truth
- destructive campaign tooling
- the same files when overlap is non-trivial

A successful independent task should not wait for unrelated manual approval.

## Stale-base rule

An agent records its base commit in its task packet. If main advances, the agent may continue when the changed files/contracts do not overlap. If overlap exists, it must reconcile with current main and rerun affected gates before claiming completion.
