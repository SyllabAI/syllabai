# Agent Quickstart — the 5-minute version

Lean entry point (T-COORD-3 / P4). This file is a **router, not a substitute**:
it tells you where the canonical rules live and what the non-negotiables are.
When this file and a canonical doc disagree, the canonical doc wins.

## Your first 5 steps

1. Read `AGENT.md` (mission, source hierarchy, architecture invariants) — and the
   specific architecture addendum your lane touches (see AGENT.md §Mandatory reading).
2. Read `.syllabai/project-state.yaml` (truth tiers, invariants, claim vocabulary).
3. Read the open frontier: `TODO-CURRENT.md` (generated view) → the packet YAMLs
   in `.syllabai/tasks/` for anything you will touch.
4. Check contention: `.syllabai/locks.yaml` (active leases + history).
5. Claim your lane: copy `.syllabai/task-template.yaml` → `.syllabai/tasks/T-XXX.yaml`
   (next free id: highest existing T-Cxx + 1), record operator trace, status CLAIMED.

## Non-negotiables (the short list)

- **Claims are labeled**: VERIFIED / INFERRED / REPORTED / UNVERIFIED — only these
  four labels, ever (validator T3). No invented addendum labels; append dated items.
- **Leases are structured rows** in `locks.yaml` (`locks:` list) with resource, owner,
  task, base_commit, acquired_at, expires_at. Prose-only leases are legacy.
  Releases append a `history:` row (fulfilled_released | expired_reclaimed | superseded).
- **Operator words gate merges and DB writes.** Record the trace id in the packet
  and the commit message. No self-merging substantive PRs without the word.
- **Open lanes heartbeat**: update your packet's `last_seen` in
  `.syllabai/heartbeat.yaml` when you make progress (validator warns at >72h).
- **Never** modify an applied Flyway migration; never allocate migration versions
  without a `flyway-version` lease; never treat T3 suggestions as T0/T1 truth.
- **Statuses** (T-COORD-3 enum): READY | EXECUTING | BLOCKED | VERIFYING | DONE |
  CLAIMED | IN_PROGRESS | RUN-RECORDED.
- **New packets state acceptance up front.** `acceptance_legacy: true` exists only
  for pre-template packets — never set it on new work.
- **Think in code**: extract, don't dump (AGENT.md §Think in Code). If a script can
  process the bytes, the bytes do not belong in a conversation.

## Tools (run before pushing)

```bash
python3 .syllabai/tools/validate_coordination.py --repo-root . --mode warn
python3 .syllabai/tools/gen_views.py --repo-root . --mode check   # or regenerate
```

CI runs both (Coordination guard). Safe-merge pre-verifier posts an advisory
comment on every PR (never a gate — the operator word is the gate).

## Where the deep rules live

| Topic | Canonical owner |
|---|---|
| Mission, reading order, hierarchy | `AGENT.md` |
| Truth tiers, invariants, claim vocabulary | `.syllabai/project-state.yaml` |
| Surface ownership, shared resources | `.syllabai/agent-registry.yaml` |
| Lease schema + release history | `.syllabai/locks.yaml` |
| Packet schema | `.syllabai/task-template.yaml` |
| Durability / knowledge map | `KNOWLEDGE_DURABILITY_POLICY.md`, `PROJECT_KNOWLEDGE_MAP.md` |
| Decisions | `DECISIONS.md` + `ADR-*.md` (operator-gated flips) |
