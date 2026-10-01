# VERIFY OUTPUTS — three-lane-20261002 (verbatim session captures)

## Lane A apply — COMMITTED run (2026-10-02, post dry-run)

```
plan sha256=7a131db17940c12a5d1a874af1a6e83864c9146a38d40f7e10f7c342cabacb80
pre-pins OK: {'qsp': 2637, 'qt': 1725, 'schemes': 1455, 'mp': 5558, 'audit_max': 4047, 'tve': 0}
  q03-6d968517 Q3: 1 -> 7 OK
  q04-8d584ee1 Q4: 1 -> 9 OK
  q11-8d584ee1 Q11: 1 -> 14 OK
  q06-1da77322 Q6: 1 -> 6 OK
  q15-1da77322 Q15: 1 -> 15 OK
  q05-e280d9c6 Q5: 1 -> 15 OK
  q08-e280d9c6 Q8: 1 -> 14 OK
COMMITTED
```

## Lane A independent verify (fresh read-only connection, immediately after commit)

```
V1 values+immutability: PASS
V2 banked sums: PASS
V3 census pins: {'qsp': 2637, 'qt': 1725, 'schemes': 1455, 'mp': 5558, 'audit': 4047, 'tve': 0, 'qv_pool': 1533, 'kn': 492}
V4 L1 active: (509, 509)
V5 plan sha: 7a131db17940c12a

VERDICT: ALL PASS
```

Note (ordering artifact if re-run after Lane B): the laneA_verify script
pins schemes=1455/mp=5558, so a post-Lane-B re-run reports `V3 pin
schemes=1468 != 1455` — that is Lane B's documented delta (+13/+94), not a
Lane A failure. The values/stems/banked-sum checks (V1/V2) remain PASS at
any ordering.

## Lane B apply — COMMITTED run (dry-run green first, identical counts)

```
plan sha256=f4e1d2e114d9d2d0e5134e4ebf7cf997098b8d989fd6afde9307333501b11e29
pre-pins OK: {'qsp': 2637, 'qt': 1725, 'schemes': 1455, 'mp': 5558, 'audit': 4047, 'tve': 0}
  + q07-5273dfa3 Q7: scheme 77cb4d45 points=5 sum=12 (ms-chunk-qp-gated-extraction-v2)
  + q04-8d584ee1 Q4: scheme 818e40f2 points=9 sum=9 (ms-chunk-gated-extraction-v2)
  + q11-8d584ee1 Q11: scheme c87c7557 points=14 sum=14 (ms-chunk-gated-extraction-v2)
  + q03-6d968517 Q3: scheme 79dbbdde points=7 sum=7 (ms-chunk-gated-extraction-v2)
  + q06-1da77322 Q6: scheme b71a384d points=6 sum=6 (ms-chunk-gated-extraction-v2)
  + q15-1da77322 Q15: scheme d5dbba3c points=15 sum=15 (ms-chunk-gated-extraction-v2)
  + q05-e280d9c6 Q5: scheme 2e20a0fc points=12 sum=15 (ms-chunk-gated-extraction-v2)
  + q08-e280d9c6 Q8: scheme 26b553d6 points=9 sum=14 (ms-chunk-gated-extraction-v2)
  + q02-e6ec2168 Q2: scheme 1eb8ec85 points=3 sum=5 (ms-chunk-qp-gated-extraction-v2)
  + q08-e6ec2168 Q8: scheme adb17f80 points=3 sum=6 (ms-chunk-qp-gated-extraction-v2)
  + q09-e6ec2168 Q9: scheme ac7fec00 points=4 sum=9 (ms-chunk-qp-gated-extraction-v2)
  + q07-cf68cf74 Q7: scheme ef65f915 points=3 sum=6 (ms-print-gated-extraction-v1)
  + q08-0ee12447 Q8: scheme 4b209083 points=4 sum=7 (ms-chunk-gated-extraction-v2)
COMMITTED: +13 schemes, +94 points (SUGGESTED census 108)
```

## Lane B independent verify (fresh read-only connection)

```
V1 census: {'schemes': 1468, 'mp': 5652, 'sug': 108, 'val': 1360, 'audit': 4047, 'tve': 0, 'qsp': 2637, 'qt': 1725}
V2 per-entry: PASS
V3 sparse recount: 43 (expect 43)
V4 fidelity: PASS
V5 Lane A qv with schemes: 7 (expect 7)
V6 plan sha: f4e1d2e114d9d2d0

VERDICT: ALL PASS
```

## Lane C — CI + merge

```
check-runs on head 36c66b6: build:completed:success
PUT /pulls/42/merge -> merged: True | sha: 93850118819053a8a7404902d5a7a83ab09d0dbd
```
