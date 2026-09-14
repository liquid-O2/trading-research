# Baseline repair delta preview

Preview for the orchestrator, not a receipt. B0 is native_discovery.scan_branch; B0.1 is scan_branch_repaired. No files were written under implementation/reports/phase1-live.

- B0: `B0` via `native_discovery.scan_branch`
- B0.1: `B0.1-2026-09-14` via `scan_branch_repaired`
- Dates: 40 (2020-01-01 .. 2026-09-03)
- Date source: extract_b.py even spacing: idx=round(i*(N-1)/39) over 1742 run-1.0.1 jobs/evaluation session dates
- Branches: 38
- Wall seconds (sum of per-date worker elapsed): 4681.4275

| branch | dates | ep B0 | ep B0.1 | pass B0 | pass B0.1 | fail B0 | fail B0.1 | unknown B0 | unknown B0.1 | no-setup B0 | no-setup B0.1 | verdict changed | directions | pass to unknown (C7) | wall s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| `GB-FAIL:branch:asia_tdo_case` | 40 | 58 | 58 | 6 | 13 | 52 | 45 | 0 | 0 | 52 | 45 | 7 | fail->pass:7 | 0 | 4.0 |
| `GB-FAIL:branch:cash_open_reclaim_case` | 40 | 35 | 35 | 3 | 17 | 32 | 18 | 0 | 0 | 32 | 18 | 14 | fail->pass:14 | 0 | 5.2 |
| `GB-FAIL:branch:mss_fvg_refinement` | 40 | 23 | 48 | 0 | 2 | 23 | 46 | 0 | 0 | 23 | 46 | 0 | — | 0 | 2.6 |
| `GB-FAIL:branch:nyam_box` | 40 | 56 | 56 | 24 | 50 | 32 | 6 | 0 | 0 | 32 | 6 | 26 | fail->pass:26 | 0 | 2.9 |
| `GB-FAIL:branch:previous_hour` | 40 | 267 | 267 | 113 | 198 | 154 | 69 | 0 | 0 | 154 | 69 | 85 | fail->pass:85 | 0 | 19.9 |
| `GB-FAIL:branch:prior_day_level` | 40 | 39 | 39 | 16 | 31 | 23 | 8 | 0 | 0 | 23 | 8 | 15 | fail->pass:15 | 0 | 2.3 |
| `GB-FAIL:branch:prior_month_level` | 40 | 20 | 20 | 1 | 4 | 18 | 14 | 1 | 2 | 18 | 14 | 4 | fail->pass:3, fail->unknown:1 | 0 | 636.6 |
| `GB-FAIL:branch:prior_week_level` | 40 | 24 | 24 | 6 | 14 | 18 | 9 | 0 | 1 | 18 | 9 | 9 | fail->pass:8, fail->unknown:1 | 0 | 162.6 |
| `GB-VWAP:branch:source_long` | 40 | 27 | 27 | 10 | 10 | 17 | 0 | 0 | 17 | 17 | 0 | 17 | fail->unknown:17 | 0 | 97.2 |
| `JJ-TBR:branch:extension_reaction` | 40 | 49 | 25 | 6 | 4 | 43 | 21 | 0 | 0 | 43 | 21 | 0 | — | 0 | 6.2 |
| `JJ-TBR:branch:internal_rotation` | 40 | 38 | 28 | 1 | 1 | 37 | 27 | 0 | 0 | 37 | 27 | 0 | — | 0 | 0.8 |
| `JJ-TBR:branch:judas_outbound` | 40 | 38 | 38 | 35 | 35 | 3 | 3 | 0 | 0 | 3 | 3 | 0 | — | 0 | 61.2 |
| `JJ-TBR:branch:judas_reversal` | 40 | 32 | 37 | 3 | 5 | 29 | 32 | 0 | 0 | 29 | 32 | 0 | — | 0 | 12.9 |
| `JJ-TBR:branch:other_session` | 40 | 304 | 304 | 55 | 55 | 249 | 249 | 0 | 0 | 249 | 249 | 0 | — | 0 | 32.8 |
| `JJ-TBR:branch:single_extended` | 40 | 19 | 14 | 0 | 0 | 19 | 14 | 0 | 0 | 19 | 14 | 0 | — | 0 | 5.6 |
| `JJ-TBR:branch:single_purged` | 40 | 19 | 14 | 1 | 0 | 18 | 14 | 0 | 0 | 18 | 14 | 0 | — | 0 | 0.6 |
| `JJ-TBR:branch:timed_pzone_reversal` | 40 | 63 | 63 | 7 | 7 | 56 | 56 | 0 | 0 | 56 | 56 | 0 | — | 0 | 185.7 |
| `KEANI-OPEN-ABOVE-VALUE:branch:source_long` | 40 | 38 | 38 | 0 | 2 | 36 | 35 | 2 | 1 | 36 | 35 | 2 | fail->pass:1, unknown->pass:1 | 0 | 54.6 |
| `MEMBER-TWO-REASONS:branch:planned_return_long` | 40 | 18 | 18 | 8 | 8 | 10 | 10 | 0 | 0 | 10 | 10 | 0 | — | 0 | 60.1 |
| `MEMBER-TWO-REASONS:branch:resistance_short` | 40 | 15 | 15 | 4 | 4 | 11 | 11 | 0 | 0 | 11 | 11 | 0 | — | 0 | 55.7 |
| `REFILL-STUDY:branch:touch_record` | 40 | 9 | 9 | 9 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 0 | 482.9 |
| `SAINT-AMT:branch:continuation_retest` | 40 | 58 | 58 | 1 | 0 | 57 | 56 | 0 | 2 | 57 | 56 | 2 | fail->unknown:1, pass->unknown:1 | 1 | 6.0 |
| `SAINT-AMT:branch:failed_auction_return` | 40 | 62 | 62 | 9 | 0 | 53 | 52 | 0 | 10 | 53 | 52 | 10 | fail->unknown:1, pass->unknown:9 | 9 | 1.5 |
| `SAINT-AMT:branch:poc_traversal` | 40 | 62 | 62 | 7 | 0 | 55 | 53 | 0 | 9 | 55 | 53 | 9 | fail->unknown:2, pass->unknown:7 | 7 | 0.9 |
| `SAINT-AMT:branch:trapped_buyers_retest` | 40 | 28 | 28 | 0 | 0 | 28 | 28 | 0 | 0 | 28 | 28 | 0 | — | 0 | 1.6 |
| `SIRES:branch:absorption_reward_retest` | 40 | 54 | 54 | 1 | 1 | 53 | 53 | 0 | 0 | 53 | 53 | 0 | — | 0 | 204.9 |
| `SIRES:branch:balance_failure_fade` | 40 | 54 | 54 | 0 | 0 | 54 | 54 | 0 | 0 | 54 | 54 | 0 | — | 0 | 205.5 |
| `SIRES:branch:clean_squeeze` | 40 | 54 | 54 | 0 | 0 | 54 | 54 | 0 | 0 | 54 | 54 | 0 | — | 0 | 206.6 |
| `SIRES:branch:defended_band_continuation` | 40 | 17 | 17 | 1 | 1 | 16 | 16 | 0 | 0 | 16 | 16 | 0 | — | 0 | 230.5 |
| `SIRES:branch:dom_rejection` | 40 | 54 | 54 | 6 | 6 | 48 | 48 | 0 | 0 | 48 | 48 | 0 | — | 0 | 224.7 |
| `SIRES:branch:footprint_confirmed_reaction` | 40 | 54 | 54 | 0 | 0 | 54 | 54 | 0 | 0 | 54 | 54 | 0 | — | 0 | 206.5 |
| `SIRES:branch:kg1_retest` | 40 | 42 | 42 | 11 | 11 | 31 | 31 | 0 | 0 | 31 | 31 | 0 | — | 0 | 162.6 |
| `SIRES:branch:microbalance_break` | 40 | 107 | 107 | 40 | 38 | 67 | 69 | 0 | 0 | 67 | 69 | 2 | pass->fail:2 | 0 | 0.8 |
| `SIRES:branch:ofm_aggressive` | 40 | 54 | 54 | 0 | 0 | 54 | 54 | 0 | 0 | 54 | 54 | 0 | — | 0 | 293.4 |
| `SIRES:branch:ofm_passive` | 40 | 26 | 26 | 0 | 0 | 26 | 26 | 0 | 0 | 26 | 26 | 0 | — | 0 | 97.0 |
| `SIRES:branch:stop_four_stage` | 40 | 54 | 54 | 0 | 0 | 54 | 54 | 0 | 0 | 54 | 54 | 0 | — | 0 | 207.1 |
| `SIRES:branch:vwap_deviation_fade` | 40 | 62 | 62 | 2 | 2 | 60 | 60 | 0 | 0 | 60 | 60 | 0 | — | 0 | 452.0 |
| `STOIC-DATA:branch:macro_application` | 40 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 0 | 94.5 |
