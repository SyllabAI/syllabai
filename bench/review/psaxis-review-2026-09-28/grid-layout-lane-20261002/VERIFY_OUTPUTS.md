# GRID-LAYOUT LANE — VERIFY OUTPUTS (verbatim session captures, 2026-10-02)

## 1. PDF identity gate (24/24 sha256 == documents.checksum)

```
201301_2c_ms.pdf: downloaded 185KB sha OK      201606_ms.pdf: downloaded 549KB sha OK
201306_ms_R.pdf: downloaded 123KB sha OK       201606_ms_R.pdf: downloaded 378KB sha OK
201406_2c_ms_R.pdf: downloaded 141KB sha OK    201606_2c_ms_R.pdf: downloaded 272KB sha OK
201501_ms.pdf: downloaded 492KB sha OK         201701_ms.pdf: downloaded 523KB sha OK
201506_ms.pdf: downloaded 186KB sha OK         201906_1c_ms.pdf: downloaded 176KB sha OK
201306_qp_R.pdf ... 202206_1cr_qp_R.pdf: (QPs) — all sha OK
24/24 verified; bad: []
```

## 2. Concurrent-fill (20:25Z) verification

```
== 1) point-text containment in printed MS ==
  points: OK 75 / OK-WRAP 0 / MISS 11  (total 86)
== 2) arithmetic: per-scheme point sum == qv.marks ==
  17/17 sums OK
== 3) the 3 marks repairs vs printed QP echo ==
  q11-5273dfa3  4CH0/1CR June 2016 Q11: echo=15 db=15 -> OK
  q06-6ab313e4  4CH0/2CR June 2016 Q6:  echo=8  db=8  -> OK
  q09-5273dfa3  4CH0/1CR June 2016 Q9:  echo=13 db=13 -> OK
```

Miss classification (token-level, per-row):
```
q06-5273dfa3 p1/p4, q08-5273dfa3 p2/p4, q11-5273dfa3 p3/p5/p7,
q06-6ab313e4 p1/p2, q02-be73fe41 p0/p3
  tokens-not-in-print: NONE (no fabrication)   [11/11 — row-boundary merges]
```

Variant attribution of the 17 schemes: 1CR-2016 → doc b27f9358 (R MS, 28 pp,
sha cfe40a1b); 2CR-2016 → 9fcd9d72 (R MS); 1C qv → c224dfa3 / 2e30c99e / 93e4fee2
/ 02e4c38c; 1CR-2019 → aa079c51; 1CR-2022 → 3dca39e5 — 17/17 variant-correct.

## 3. Engine v1→v2 target table (fresh pdftotext pages)

```
v1: fill-ok 20 / new-defect cand 1 / short 6
v2 (G2.4+G2.5+G2.6, parser 5643689): fill-ok 24 / new-defect cand 1 / short 1
  2CR-2016 Q1: 2 -> 4   (G2.4 + G2.6)
  2CR-2016 Q3: 7 -> 9   (G2.4)
  1C-2015  Q7: 7 -> 9   (G2.4)
  1C-2015  Q11: 10 -> 11 (G2.5 — p29 furniture-skip cured)
  1CR-2016 Q10: 10 -> 13 (G2.5 — p20; a(ii) OR-route fraction block remains)
  2C-2013  Q3: sum 8 == echo 8 vs bank 1 (NEW-DEFECT candidate, not repaired)
```

Parser suite: `Ran 85 tests ... OK` (77 pre-existing + 8 new `tests_g2_grid_layout`).
Corpus scan of the loosened furniture guard: exactly one page flips (201606_ms_R p20).

## 4. Plan pin

```
plan: fill 24 qv / 164 points / 233 marks; excluded 0
plan_sha256 aa38b698c47a7ff86bb292772987331ce8d4f486b678f05dc63ea05bcfe03868
artifact-class rows (7): all no-fabrication (token-level)
attribution check: 24/24 OK
```

## 5. Apply — dry-run green, then COMMIT

```
[pin] plan sha OK (aa38b698c47a7ff8…); entries=24 points=164 marks=233
== pre-asserts ==
  qsp_total = 2637 OK · qt_total = 1725 OK · schemes_total = 1485 OK
  mark_points_total = 5738 OK · audit_max_id = 4048 OK · tve = 0 OK
  document_id resolution OK · 24 qv marks + no-scheme checks OK
[DRY-RUN] all gates green — NO writes performed.

== COMMIT ==
  inserted 24 schemes / 164 points
== in-tx post-asserts ==
  qsp_total = 2637 OK · qt_total = 1725 OK · schemes_total = 1509 OK
  mark_points_total = 5902 OK · schemes SUGGESTED = 149 OK
  audit_max_id = 4048 OK · tve = 0 OK
[COMMITTED] one fail-closed tx landed
```

## 6. Independent fresh-connection verify

```
== per-entry verify ==  -> 24/24 entries verified clean
   (counts / sums / verbatim byte-match / source doc / SUGGESTED state)
residues untouched: q10-5273dfa3 (15, 0 schemes); q03-51fea326 (1, 0 schemes)
== census ==
  schemes_total = 1509 (1360V/149S) · mark_points_total = 5902
  qsp_total = 2637 · qt_total = 1725 · qv_pool = 1533 · questions_active = 961
  audit_max_id = 4048 · tve = 0
lane-universe sparse: 26 -> 2 (q03-51fea326, q10-5273dfa3)
census_bundle_gridlayout_20261002.json: drift NONE
```
