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

## safe_merge_check.py

Advisory PR pre-verifier (T-COORD-2 P5). Posts/updates one comment with the
merge-safety facts: task-packet reference + status (R1), CI on head (R2),
mergeability (R3), base freshness (R4), active leases (R5). Never blocks —
the operator's merge word remains the gate. Repo-agnostic: portable to
`syllabai-core`/`syllabai-web`/`syllabai-hub` by copying the script +
`.github/workflows/safe-merge.yml` (repos without `.syllabai/` degrade
gracefully).

```bash
GITHUB_TOKEN=... GITHUB_REPOSITORY=SyllabAI/syllabai PR_NUMBER=42 \
  python3 .syllabai/tools/safe_merge_check.py --repo-root . --post
```

## CI

`.github/workflows/coordination.yml` runs the validator + view checks on
PRs/pushes touching `.syllabai/**` or `TODO.md`, weekly on a schedule, and
via `workflow_dispatch` — WARN-ONLY in phase 1, results in the job summary.

`.github/workflows/safe-merge.yml` runs the pre-verifier on every PR
(opened/synchronize/reopened) and updates its comment in place.

## Structured lease history (locks.yaml `history:`)

T-COORD-2 P2: fulfilled leases are recorded as structured rows in the
append-only `history:` block (required: resource, task, outcome,
released_at, receipt; outcome vocabulary: fulfilled_released |
expired_reclaimed | superseded). The prose release annotations remain legal
legacy records. Checked by the validator (H1–H5).
