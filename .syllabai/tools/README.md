# Coordination tooling

Machine checks for the coordination state in `.syllabai/` — additive tooling
(T-COORD-1); nothing here changes the coordination protocol itself.

## validate_coordination.py

Validates `locks.yaml` (lease schema, expiry, resource vocabulary, task
references, serialized-resource exclusivity), `agent-registry.yaml`
(shared-resource cross-references and policy contradictions) and
`tasks/*.yaml` (id/filename match, status enum, claim-label vocabulary,
acceptance/owner presence for VERIFYING|DONE). Read-only.

```bash
python3 .syllabai/tools/validate_coordination.py --repo-root . --mode warn
```

`--mode warn` (default): report findings, exit 0 — phase 1.
`--mode strict`: exit 1 on any finding — enable after two clean weeks.

## gen_views.py

Generates `TODO-CURRENT.md` (compact open-packet frontier from the task
packets) and prints a parity report vs `TODO.md` checkbox items. `TODO.md`
stays the full canonical queue; the generated file is a lens, never a
replacement. Read-only over all coordination inputs.

```bash
python3 .syllabai/tools/gen_views.py --repo-root . --mode write   # regenerate
python3 .syllabai/tools/gen_views.py --repo-root . --mode check   # drift + parity report
```

## CI

`.github/workflows/coordination.yml` runs both on PRs/pushes touching
`.syllabai/**` or `TODO.md`, weekly on a schedule, and via
`workflow_dispatch` — WARN-ONLY in phase 1, results in the job summary.
