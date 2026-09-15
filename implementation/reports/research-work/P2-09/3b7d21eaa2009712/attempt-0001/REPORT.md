# P2-09

Draft receipt. Orchestrator re-runs produce_receipts.py --finalize after merge.
See THROUGHPUT.json on this attempt for median/p90 seconds, dates, workers and peak RSS.

receipt_state=draft_pending_merge. Nothing finalized. No GATE_REVIEW.json.

## Board depth (per root, 20-date slice)

- ES: n_days=20 n_boards=18 n_live median/p10/p90=6.0/4.0/20.0 n_with_oi median/p10/p90=6.0/4.0/20.0 n_with_fresh_quote median/p10/p90=6.0/4.0/20.0
  - 2020-01-02: no_oi_vintage_before_asof
  - 2026-09-03: no_quotes
- NQ: n_days=20 n_boards=12 n_live median/p10/p90=1.0/1.0/3.0 n_with_oi median/p10/p90=1.0/0.0/3.0 n_with_fresh_quote median/p10/p90=1.0/1.0/3.0
  - 2020-01-02: no_oi_vintage_before_asof
  - 2020-06-01: no_fresh_midpoint_under_60s_age_rule
  - 2021-01-04: no_fresh_midpoint_under_60s_age_rule
  - 2021-04-01: no_fresh_midpoint_under_60s_age_rule
  - 2023-01-03: no_fresh_midpoint_under_60s_age_rule
  - 2023-11-06: no_fresh_midpoint_under_60s_age_rule
  - 2024-01-02: no_fresh_midpoint_under_60s_age_rule
  - 2026-09-03: no_quotes
- QQQ: n_days=20 n_boards=19 n_live median/p10/p90=883.0/242.0/1407.0 n_with_oi median/p10/p90=824.0/242.0/1293.0 n_with_fresh_quote median/p10/p90=994.0/277.0/1621.0
  - 2026-09-03: no_spot
- SPY: n_days=20 n_boards=19 n_live median/p10/p90=1125.0/697.0/1556.0 n_with_oi median/p10/p90=1031.0/829.0/1463.0 n_with_fresh_quote median/p10/p90=1213.0/857.0/1669.0
  - 2026-09-03: no_spot

