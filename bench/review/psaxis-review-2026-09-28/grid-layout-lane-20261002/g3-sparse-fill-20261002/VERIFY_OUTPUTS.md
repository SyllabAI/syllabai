# VERIFY OUTPUTS — T-C55 (G3 lane, 2026-10-02) — verbatim session captures

## 1. Protocol-② live probe (g3_probe_20261002.py, SELECT-only, fresh conn)

```
== target qv states ==
  q03-51fea326: qv.marks=8 state=VALIDATED q.active=False q_id=edf71550-ddb7-4521-9c20-053d3048ee16 q.marks=8 schemes=0
  q10-5273dfa3: qv.marks=15 state=VALIDATED q.active=False q_id=36a8c9cd-c0cb-40e7-8934-9d1d634559b7 q.marks=15 schemes=0
== MS documents ==
  2C Jan 2013 MS: kind=MARK_SCHEME sha=1e9c53b548acbd20…
  1CR Jun 2016 MS: kind=MARK_SCHEME sha=cfe40a1bb0954221…
== census pins (expect ruling_v57 bundle) ==
  qsp_total              = 2620 (expect 2637) DRIFT
  qt_total               = 1717 (expect 1725) DRIFT
  schemes_total          = 1502 (expect 1509) DRIFT
  mark_points_total      = 5867 (expect 5902) DRIFT
  schemes_suggested      = 142 (expect 149) DRIFT
  schemes_validated      = 1360 (expect 1360) OK
  audit_max_id           = 4049 (expect 4048) DRIFT
  tve                    = 0 (expect 0) OK
  qv_pool                = 1526 (expect 1533) DRIFT
  questions_active       = 954 (expect 961) DRIFT
  kn                     = 435 (expect 435) OK
  edges                  = 730 (expect 730) OK
  ing_nodes              = 0 (expect 0) OK
  papers_validated       = 90 (expect 90) OK
  papers_rejected        = 13 (expect 14) DRIFT
```

## 2. Drift root-cause (g3_drift_investigate.py, SELECT-only)

```
(4049, datetime.datetime(2026, 10, 2, 7, 34, 18, 759274, tzinfo=datetime.timezone.utc),
 None, 'wave2-prep-agent(Super Z)', 'REJECT', 'exam_paper',
 '7d40476f-13b3-436b-9e0d-f2877fe2ba0e', 'REJECTED', 'REJECTED',
 'F-PROD-4 governed removal: ingest-era shell (1 paper + 2 REJECTED docs + 7-question
  SUGGESTED skeleton) removed under the operator wave-2-prep directive; full row
  archive retained in sylla[bai records]')
== recent deletions: schemes whose qv is gone ==
  orphan schemes (qv missing): 0
```

## 3. The source defect — coordinate-level marks-column scan (page 19, x>700)

```
words with x0>700 (marks column region), sorted by y:
  x0= 816.5 y0=   1.1 'PMT'
  x0= 716.1 y0=  67.9 'Marks'
  x0= 726.9 y0= 128.5 '3'          <- a(i)'s cell; the WHOLE a(ii) block: none
```

## 4. Engine gates (G3 parse of the full 1CR-2016 MS with qp_totals)

```
OK  Q 1: sum=7  echo=7   ...  OK  Q 9: sum=13 echo=13
OK  Q10: sum=15 echo=15 pts=8      <- was 13 under G2
OK  Q11: sum=15 echo=15        (Q7 13-vs-echo-12 is G2-identical, pre-existing,
OK  Q12: sum=13 echo=13         outside this lane's mandate)
Q10 FINAL:
  M1 (a,i)  marks=3 text='n(Na2S2O3) = 0.300 × 20'
  M1 (a,ii) marks=2 text='mass of SO2 in 1 dm3 = 0.38(4) × 1000'   <- G3.3 residual
  P1 (b,None)  marks=1 text='as the (hydrochloric) acid/HCl is added'  <- G3.1
  P2 (c,i)     marks=1 text='timer started too late / stopped too early'
  P3 (c,ii)    marks=1 text='19.5 (s)'
  M1 (d,i)  marks=2 / M1 (d,ii) marks=2 / M4 (e,None) marks=3
```

## 5. Suite + corpus regression

```
pdflane suite: Ran 196 tests in 0.051s — OK (skipped=1)
  (tests_g3_grid_layout.py 6/6 first)
CI on parser main 0fc5c32: content-package-proof success / conformance success
  / build success
g3_corpus_regression.py: TOTAL DIFFS: 13 — all justified:
  201606_ms_R[_layout] Q10 (4 sites)  : the mandate (13->15 with-qp; b/c(i)
                                        attributed in both conditions)
  201701_ms [with-qp] Q5              : 16->17, G3.3 recovered b(v) 'OH— / HO—'
                                        (printed row '(v)   OH— / HO—   Ignore
                                        name   1'; QP echo 17 confirms G3)
  201606_ms_R[_layout] Q5 (2 sites)   : sum 9=9, c:'CQ on M1'->d:(real answer)
  201906_1cr_ms_R[_layout] Q4 (2 sites): sum 13=13, b(ii):'in either order'->c
```

## 6. Apply — dry-run (g3_apply_fill.py)

```
[pin] plan sha OK (2b7f433f39254934…); entries=2 points=16 marks=23
== pre-asserts (post-F-PROD-4 baseline, probed this lane) ==
  qsp_total=2620 OK  qt_total=1717 OK  schemes_total=1502 OK
  mark_points_total=5867 OK  audit_max_id=4049 OK  tve=0 OK
  qv_pool=1526 OK  questions_active=954 OK
  document resolution OK (2 MARK_SCHEME docs)
  2 qv marks + no-scheme checks OK
[DRY-RUN] all gates green — NO writes performed. Re-run with --commit.
```

## 7. Apply — commit

```
== COMMIT ==
  inserted scheme for q03-51fea326: 8 pts / 8 marks OK
  inserted scheme for q10-5273dfa3: 8 pts / 15 marks OK
  inserted 2 schemes / 16 points
== in-tx post-asserts ==
  qsp_total=2620 OK  qt_total=1717 OK  schemes_total=1504 OK
  mark_points_total=5883 OK  schemes SUGGESTED=144 OK  audit_max_id=4049 OK
  tve=0 OK
[COMMITTED] one fail-closed tx landed
```

## 8. Fresh-conn verify + census re-pin (g3_verify_and_census.py)

```
  q03-51fea326: 8 pts / 8 marks / SUGGESTED / ms-print-gated-extraction-v4 /
                doc-sha 1e9c53b548ac… OK    per-point re-verify: 8/8
  q10-5273dfa3: 8 pts / 15 marks / SUGGESTED / ms-print-gated-extraction-v4 /
                doc-sha cfe40a1bb095… OK    per-point re-verify: 8/8
== lane-universe sparse recount ==
  VALIDATED 4CH-scheme-paper qv with zero schemes: 0
  schemes on the 2 targets: 2
== census re-pin (census-last) == 18 pins — DRIFT: NONE
  qsp 2620 / qt 1717 / schemes 1504 (1360V+144S) / mp 5883 / audit 4049 /
  tve 0 / qv_pool 1526 / questions_active 954 / questions_total 1526 /
  papers 90V+13R / docs 567V+305S+145R / kn 435 / edges 730 / ING 0
VERIFY: ALL CLEAN
```
