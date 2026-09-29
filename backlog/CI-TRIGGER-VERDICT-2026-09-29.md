# CI Trigger Verdict — 2026-09-29 (T-C36, operator directive "fix the triggers")

**Verdict: the push triggers were never broken. No YAML change is made, because
making one would encode a lie in the diff.** The `branches: ain]` reading that
has been carried as a standing infra item since T-C33 is a terminal-display
artifact, not repository state. This file is the evidence bundle so no future
session has to re-derive it.

## 1. Byte-level proof (the YAML is intact)

Fetched 2026-09-29 (T-C36 session), then `git show origin/main:.github/workflows/ci.yml | head -12 | od -c`:

**syllabai-core @ origin/main `5b946ba`** — trigger block bytes:

```
n   a   m   e   :       c   o   r   e   -   c   i  \n  \n   o
n   :  \n           p   u   s   h   :  \n                   b
r   a   n   c   h   e   s   :       [   m   a   i   n   ]  \n
                p   a   t   h   s   :  \n
```

**syllabai-hub @ origin/main `235f5cd`** — trigger block bytes:

```
n   a   m   e   :       h   u   b   -   c   i  \n  \n   o   n
:  \n           p   u   s   h   :  \n                   b   r
a   n   c   h   e   s   :       [   m   a   i   n   ]  \n
p   u   l   l   _   r   e   q   u   e   s   t   :  \n  \n   j
o   b   s   :  \n
```

Both render `branches: [main]` — the `[`, `m`, `a`, `i`, `n`, `]` bytes are all
present. There is no corruption to fix.

## 2. Behavioral proof (push runs fire on main, and succeed)

GitHub Actions API, 2026-09-29 (`GET /repos/SyllabAI/<repo>/actions/runs`):

**syllabai-core**

| event | head_branch | head_sha | status | conclusion | created_at |
|---|---|---|---|---|---|
| push | main | 5b946ba | completed | **success** | 2026-09-29T08:23:41Z |
| push | main | ae43c1a | completed | cancelled (superseded by the next push, concurrency group) | 2026-09-29T08:23:36Z |
| push | main | 546c03f | completed | cancelled (same) | 2026-09-29T08:23:07Z |

**syllabai-hub**

| event | head_branch | head_sha | status | conclusion | created_at |
|---|---|---|---|---|---|
| push | main | 235f5cd | completed | **success** | 2026-09-29T08:49:29Z |
| push | main | b02178e | completed | **success** | 2026-09-29T08:47:16Z |
| push | main | 9c3c74d | completed | **success** | 2026-09-29T08:35:27Z |
| push | main | 50ca841 | completed | **success** | 2026-09-29T08:21:49Z |
| push | main | f9130b3 | completed | **success** | 2026-09-29T07:48:57Z |
| push | main | 43c1fde | completed | **success** | 2026-09-29T07:44:47Z |
| push | main | 0bc6ee9 | completed | **success** | 2026-09-29T07:17:57Z |

Every recent main push fired a push-triggered run and every non-superseded run
was green — including `50ca841`, the exact commit the T-C35-merge record
describes as "pushed direct to main, push-CI broken". That characterization was
wrong: the run exists and succeeded. The earlier quiet period with no main runs
was the Actions-minutes quota blackout documented in
`CI-RECOVERY-RUNBOOK-2026-09-27.md` (billing anchor 2026-09-27), not a YAML
defect. Core's `paths:` filter (src/pom/mvnw/workflow file only) also remains
intentional: docs-only main pushes correctly do not consume minutes.

## 3. Root cause of the phantom (a display artifact that ate its own correction)

`[m` inside `[main]` is a valid ANSI/SGR escape tail (`ESC[m` is the canonical
reset; stripping layers that match `[<numbers>]*m` or `\[m` **without requiring
the ESC byte** will also consume the literal `[m` in ordinary text). Colorized
tool output (rg/gh with a TTY) piped through the session's ANSI-stripping layer
therefore rendered the real line

    branches: [main]

as

    branches: ain]

The artifact then survived its own debunking: a previous CI-audit session wrote
into TODO.md that the workflow lines "are clean `[main]` — the 'mangled ain]'
reading was a terminal display artifact", but the stored sentence's own
`[main]` got mangled to `ain]` in the record, and an adjacent row even reads
"reads mangled `branches: ain]` (expected `ain]`)" — the *expected* string was
itself eaten. Every later reader (the T-C33/T-C34/T-C35 worklogs and the
T-C35-merge standing reminder) faithfully propagated the mangled record.

## 4. Disposition

- **No `ci.yml` edit in either repo.** The correct fix for a phantom is a
  corrected record, not a diff.
- Reading rules for future sessions: when a file is suspected of containing
  bracket-square content that looks mangled (`ain]`, `expected ain]`, `clean
  ain]`), re-read it byte-level (`od -c`, or strip colors at the source with
  `--color=never`/`NO_COLOR=1`) before believing it.
- The T-C36 hub font work (next PR) ends with a merge push to main; its
  push-triggered run is the ongoing live proof of this verdict.

## 5. Font flake (part ② of the directive) — pointer

The recurring `next/font/google` Turbopack build flake (3 occurrences on
2026-09-29; green on every retry, local build, and Vercel build) is real and
has a real fix: hub's `src/app/layout.tsx` loads **8 Google families at build
time** from `fonts.googleapis.com`/`fonts.gstatic.com`, so every cold CI runner
re-fetches them over the network. The fix (T-C36, hub PR): vendor the exact
served woff2 files into `src/fonts/` with a pin manifest, and switch to
`next/font/local` with identical CSS variable names, display, and preload
semantics — builds become hermetic by construction. See
`.syllabai/tasks/T-C36.yaml` for scope.
