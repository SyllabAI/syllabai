# VERIFY_OUTPUTS — T-C48: ruling defect fix + V57 deployment + census re-pin (2026-10-02, trace 1a0fb59f90143ad1)

## 1. Protocol-② live-state probe (SELECT-only, rolled back) — target untouched

```
== defect target (bank current state) ==
  qv+q row                                     = ('q03-51fea326', '4CH0/2C', 'January 2013', 1, 1, 'VALIDATED', False, 'e6a160c7-cb91-46dc-bc3d-cbe15c3df826')
  schemes on qv (expect 0)                     = (0,)
== printed-doc identity (checksum pin) ==
  doc by MS sha                                = ('2b53b180-78d6-5ca8-bbf5-46e3e86033a5', 'MARK_SCHEME')
  doc by QP sha                                = ('ba3b57e8-0dd1-5939-a2f2-ae06a583f880', 'QUESTION_PAPER')
== census pins (T-C45 baseline) ==
  qsp 2637 / qt 1725 / schemes 1509 / mp 5902 / audit 4048 / tve 0 / qv_pool 1533
  kn 492 / ING 57 / review_schedules 154
== flyway ==  latest applied: 55   (V56+ not yet applied — deploy gate broken)
```

## 2. First-hand evidence re-verification (build-time gates)

```
== QP echo line (Total for Question 3) ==
268:                    (Total for Question 3 = 8 marks)
== engine rerun (pdflane parse_ms G2 on baseline/201301_2c_ms-pages.json) ==
Q3 sum_points: 8
  part=ai marks=1 :: - at least two layers of circles drawn with the
  part=ai marks=1 :: - no regular pattern overall
  part=aii marks=1 :: (particles/they are) more closely packed
  part=bi marks=1 :: - bright/brilliant/blinding/white flame
  part=bi marks=1 :: - white powder / solid / smoke / ash
  part=bii marks=1 :: MgO
  part=ci marks=1 :: base/alkali
  part=cii marks=1 :: OH⎯ / hydroxide
== printed MS block total (layout text, Q3 block end) ==
        (ii) OH⎯ / hydroxide          1
                                       Total    8
== src sha256 (src_pdf_SHA256SUMS.txt, byte-match asserted in plan builder) ==
1e9c53b5…  201301_2c_ms.pdf     == documents 2b53b180 (MARK_SCHEME)
fe7ab065…  201301_2c_qp.pdf     == documents ba3b57e8 (QUESTION_PAPER)
```

## 3. Plan build + dry-run (fail-closed)

```
plan built: engine_sum=8 qp_echo=True ms_total=True sha_match=True
plan_sha256 5fa4222f3b653c55cd9258476166e9f4d95bcd3ab11ec72a0d852b67cc0c54ea
[pin] plan sha OK (5fa4222f3b653c55…)
== pre-asserts ==
  qsp_total 2637 OK · qt_total 1725 OK · schemes_total 1509 OK · mark_points_total 5902 OK
  audit_max_id 4048 OK · tve 0 OK · qv_pool 1533 OK · kn pre-V57 492 OK · ING pre-V57 57 OK
  target row (before-values + identity) = 1 OK · schemes on qv 0 OK
  q.id resolved = edf71550-ddb7-4521-9c20-053d3048ee16
[DRY-RUN] all gates green — NO writes performed.
```

## 4. Apply — COMMIT + independent fresh-connection verify

```
== COMMIT ==
  guarded UPDATE questions.marks 1->8 (rowcount 1)
  guarded UPDATE question_versions.marks 1->8 (rowcount 1)
== in-tx post-asserts ==
  target after-values + states unchanged = 1 OK
  qsp 2637 · qt 1725 · schemes 1509 · mp 5902 · audit 4048 · tve 0 · qv_pool 1533 · schemes-on-qv 0 — all OK
[COMMITTED] one fail-closed tx landed
== verify (fresh connection) ==
  row: ('q03-51fea326', '4CH0/2C', 'January 2013', 8, 8, 'VALIDATED', False)
  census pins all OK (unchanged) · sibling spot: 1CR-2016 Q9 = 13 (intact)
[verify done — SELECT-only] ALL CLEAN
```

## 5. V56 boot-failure root cause (Render logs, failed deploys 05:09–06:52Z ×5)

```
[06:52:50.449] Caused by: org.flywaydb.core.internal.sqlscript.FlywaySqlScriptException:
               Failed to execute script V56__hnsw_filtered_scan_settings.sql
[06:52:50.449] Message    : ERROR: permission denied to set parameter "hnsw.iterative_scan"
[06:52:50.449] Where: SQL statement "ALTER DATABASE neondb SET hnsw.iterative_scan = 'strict_order'"
[06:52:50.449]           PL/pgSQL function inline_code_block line 3 at EXECUTE
[06:52:51.959] ==> Exited with status 1
deploys: dep-davjotidails738r7kig 5eed5976 update_failed 05:09Z
         dep-davkd7lckfvc73bs43ug 98bc88a6 update_failed 05:52Z
         dep-davke4n9nhgc7383h250 6a52613f update_failed 05:54Z
         dep-davkjt5g1s2s73fpcgcg 51f5db8c update_failed 06:06Z
         dep-davl893tqb8s73ffq090 038d201a update_failed 06:50Z
last live: dep-dav0vvm0tbcc73e92v40 6d2c8808 live 2026-10-01T07:47Z
```

Production DB pin state re-verified (fresh connections): `current_setting('hnsw.iterative_scan') = 'strict_order'`,
`current_setting('hnsw.ef_search', true) = NULL` (unset = pgvector default 40 — the value V56 records).

## 6. Patch rehearsal on production (rollback tx, patched bytes verbatim)

```
[rehearsal] DO block executed without error        # privileged TRY path (owner role)
[rehearsal] rolled back — no writes
post-rollback fresh-connection check: iterative_scan='strict_order', ef_search=NULL (pin intact)
```

## 7. Deploy watch (after core main cd5288f4a — V56 tolerant unblock)

```
deploy fired: dep-davlig8ae00c73dmg5fg | status build_in_progress
  [07:12:18] build_in_progress … [07:13:34] update_in_progress …
  [07:16:30] live
FINAL: dep-davlig8ae00c73dmg5fg live | commit cd5288f4ab8c
```

## 8. Post-deploy verification (fresh connections)

```
== flyway (post-deploy) ==
   ('56', 'hnsw filtered scan settings', True, 2026-10-02 07:14:19.376475)
   ('57', 'ing node removal',            True, 2026-10-02 07:14:21.895819)
   ('58', 'smart mark attempt batching', True, 2026-10-02 07:14:23.888534)
== V57 effects ==
  kn (expect 435)                                  = (435,)
  ING nodes (expect 0)                             = (0,)
  questions with NULL anchor (expect 538)          = (538,)
  questions anchoring ING (expect 0)               = (0,)
  knowledge_edges (expect 730)                     = (730,)
  anchor column nullable (expect 1)                = (1,)
== census pins ==
  qsp 2637 · qt 1725 · schemes 1509 (1360V/149S) · mp 5902 · audit 4048 · tve 0
  qv_pool 1533 · questions_active 961 · papers 90V/14R · review_schedules 154
== marks repair intact ==
  q03-51fea326 marks (expect 8/8) = (8, 8)
== health ==  /actuator/health -> 200
```

## 9. Census re-pin bundle (census_bundle_ruling_v57_20261002.json)

```
drift: {}
knowledge_nodes 435 · ing_nodes_remaining 0 · knowledge_edges 730
qsp_total 2637 · qt_total 1725 · schemes_total 1509 (SUGGESTED 149 / VALIDATED 1360)
mark_points_total 5902 · audit_max_id 4048 · tve 0 · qv_pool 1533 · questions_active 961
review_schedules_total 154 · lane_universe_sparse [q03-51fea326, q10-5273dfa3]
```
