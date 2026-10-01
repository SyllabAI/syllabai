# VERIFY_OUTPUTS — bank-defect repair lane (2026-10-02, trace 1a0f8d54ffe8d93d)

## 1. Builder dry-run (SELECT-only) — classification matrix

```
q08-57202de4     bank= 8 attr={'R': 0.967, 'reg': 0.567} -> NO-DEFECT
q09-57202de4     bank= 1 attr={'R': 0.961, 'reg': 0.804} -> REPAIR repair->9
q03-d5815b70     bank= 5 attr={'R': 0.949, 'reg': 0.359} -> NO-DEFECT
q11-22184324     bank= 1 attr={'R': 0.95} -> REPAIR repair->10
q01-5273dfa3     bank= 1 attr={'R': 1.0, 'reg': 0.69} -> REPAIR repair->7
q02-5273dfa3     bank= 6 attr={'R': 0.946, 'reg': 0.811} -> NO-DEFECT
q03-5273dfa3     bank= 4 attr={'R': 0.968, 'reg': 0.581} -> NO-DEFECT
q04-5273dfa3     bank= 8 attr={'R': 0.983, 'reg': 0.7} -> NO-DEFECT
q05-5273dfa3     bank= 9 attr={'R': 0.967, 'reg': 0.417} -> NO-DEFECT
q08-5273dfa3     bank= 8 attr={'R': 0.958, 'reg': 0.708} -> NO-DEFECT
q09-5273dfa3     bank= 1 attr={'R': 0.967, 'reg': 0.817} -> UNRESOLVED
q10-5273dfa3     bank=15 attr={'R': 0.967, 'reg': 0.7} -> NO-DEFECT
q11-5273dfa3     bank= 1 attr={'R': 0.917, 'reg': 0.6} -> UNRESOLVED
q12-5273dfa3     bank=13 attr={'R': 0.95, 'reg': 0.533} -> NO-DEFECT
q10-2701ad3c     bank= 1 attr={'R': 0.756, 'reg': 1.0} -> REPAIR repair->6
q01-6ab313e4     bank= 4 attr={'R': 0.98, 'reg': 0.5} -> NO-DEFECT
q02-6ab313e4     bank= 8 attr={'R': 1.0, 'reg': 0.4} -> NO-DEFECT
q04-6ab313e4     bank= 6 attr={'R': 1.0, 'reg': 0.765} -> NO-DEFECT
q06-6ab313e4     bank= 1 attr={'R': 0.9, 'reg': 0.575} -> UNRESOLVED

REPAIR entries: 4 | non-repairs: 15
plan -> /home/z/my-project/workspace/psaxis/laneD_plan.json
  sha256=51a7480544014c02f9d091818349e4a53147d8f9c5e3b806001d81c51b44a835
```

## 2. Apply — first dry-run (fail-closed trip on audit pin)

```
AssertionError: pre-pin drift: {'audit_max': (4048, 4047)}
```

Investigated read-only: audit row 4048 = `pilot.teacher@syllabai-test.dev`,
action VALIDATE_ALL, target exam_paper `fd1bf331…` (4CH1/1C Specimen 2017),
`from_state=VALIDATED to_state=VALIDATED`, detail `0 versions + 0 schemes,
force=false`, occurred_at 2026-10-01T19:16:19Z — benign no-op after the
three-lane census read. Re-pinned audit_max=4048 with explanation inlined.

## 3. Apply — second dry-run (green)

```
plan sha256=51a7480544014c02f9d091818349e4a53147d8f9c5e3b806001d81c51b44a835
pre-pins OK: {'qsp': 2637, 'qt': 1725, 'schemes': 1468, 'mp': 5652, 'audit_max': 4048, 'tve': 0}
  q09-57202de4 Q9: 1 -> 9 (own=R echo=9) OK
  q11-22184324 Q11: 1 -> 10 (own=R echo=10) OK
  q01-5273dfa3 Q1: 1 -> 7 (own=R echo=7) OK
  q10-2701ad3c Q10: 1 -> 6 (own=reg echo=6) OK
DRY-RUN OK — rolled back (re-run with --commit to finalize)
```

## 4. Apply — commit

```
plan sha256=51a7480544014c02f9d091818349e4a53147d8f9c5e3b806001d81c51b44a835
pre-pins OK: {'qsp': 2637, 'qt': 1725, 'schemes': 1468, 'mp': 5652, 'audit_max': 4048, 'tve': 0}
  q09-57202de4 Q9: 1 -> 9 (own=R echo=9) OK
  q11-22184324 Q11: 1 -> 10 (own=R echo=10) OK
  q01-5273dfa3 Q1: 1 -> 7 (own=R echo=7) OK
  q10-2701ad3c Q10: 1 -> 6 (own=reg echo=6) OK
COMMITTED
```

## 5. Independent fresh-connection verify — ALL PASS

```
=== repaired qv after-state ===
  q09-57202de4     qv.marks=9 q.marks=9 (expect 9) PASS
  q11-22184324     qv.marks=10 q.marks=10 (expect 10) PASS
  q01-5273dfa3     qv.marks=7 q.marks=7 (expect 7) PASS
  q10-2701ad3c     qv.marks=6 q.marks=6 (expect 6) PASS
=== non-repair qv untouched ===
  15 non-repairs: ALL UNTOUCHED
=== per-paper banked-sum deltas (sum q.marks over paper) ===
  4CH0/1C   June 2016 : delta +5 expect +5 PASS
  4CH0/1CR  June 2013 : delta +8 expect +8 PASS
  4CH0/1CR  June 2016 : delta +6 expect +6 PASS
  4CH0/2CR  June 2014 : delta +0 expect +0 PASS
  4CH0/2CR  June 2016 : delta +0 expect +0 PASS
  4CH1/1CR  June 2022 : delta +9 expect +9 PASS
=== census pins ===
  qsp        =   2637 expect   2637 PASS
  qt         =   1725 expect   1725 PASS
  schemes    =   1468 expect   1468 PASS
  mp         =   5652 expect   5652 PASS
  sparse     =     43 expect     43 PASS
  kn         =    492 expect    492 PASS
  ing        =     57 expect     57 PASS
  edges      =    730 expect    730 PASS
  audit      =   4048 expect   4048 PASS
  tve        =      0 expect      0 PASS

VERIFY: ALL PASS
```

## 6. Post-lane census bundle

```
drift: NONE — ALL PINS MATCH
saved -> /home/z/my-project/workspace/psaxis/census_bundle_bankdefect_20261002.json
```
