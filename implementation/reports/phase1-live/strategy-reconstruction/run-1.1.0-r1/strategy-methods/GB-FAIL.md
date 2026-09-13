# GB-FAIL: strategy reconstruction

Observed entry candidates: 22 setup, 62 no setup, 0 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| nyam_box | entry_setup | GB pp.21,23,25,27,30–35,38–40,43: finished 09–10 box → contextual sweep → five-minute reclaim → opposing box liquidity |
| previous_hour | entry_setup | GB pp.21,23,25,27,30–35,38–40,43: finished prior clock-hour reference → contextual sweep → reclaim → opposing hour liquidity |
| asia_tdo_case | entry_setup | GB pp.21,23,25,27,30–35,38–40,43: completed Asia range + midnight TDO → sweep → reclaim with TDO confirmation |
| prior_day_level | entry_setup | GB pp.21,23,25,27,30–35,38–40,43: same-contract previous actual RTH reference → sweep/reclaim → selected opposing level |
| prior_week_level | entry_setup | GB pp.21,23,25,27,30–35,38–40,43: same-contract prior-week matching sessions → sweep/reclaim → selected opposing level |
| prior_month_level | entry_setup | GB pp.21,23,25,27,30–35,38–40,43: same-contract prior-month matching sessions → sweep/reclaim → selected opposing level |
| cash_open_reclaim_case | entry_setup | GB pp.21,23,25,27,30–35,38–40,43: 09:30 open → below-open manipulation → reclaim → retracement objective with low invalidation |
| mss_fvg_refinement | entry_setup | GB pp.21,23,25,27,30–35,38–40,43: completed parent reclaim → later three 2-minute candles → MSS plus actual wick FVG; annotation unit |

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |
| previous_hour | no_setup | box_return_ok | 25 |
| previous_hour | no_setup | confirm_close reference_px (>) | 14 |
| previous_hour | no_setup | confirm_close reference_px (<) | 9 |
| asia_tdo_case | no_setup | box_return_ok | 9 |
| asia_tdo_case | no_setup | NOT tdo_required | 8 |
| asia_tdo_case | no_setup | source_tdo_close_confirmed | 8 |
| prior_day_level | no_setup | box_return_ok | 7 |
| prior_week_level | no_setup | box_return_ok | 6 |
| nyam_box | no_setup | box_return_ok | 5 |
| prior_week_level | no_setup | confirm_close reference_px (>) | 5 |
| cash_open_reclaim_case | no_setup | confirm_close reference_px (>) | 5 |
| asia_tdo_case | no_setup | confirm_close reference_px (<) | 4 |
| asia_tdo_case | no_setup | confirm_close reference_px (>) | 4 |
| prior_day_level | no_setup | confirm_close reference_px (>) | 4 |
| nyam_box | no_setup | confirm_close reference_px (>) | 3 |
| prior_day_level | no_setup | confirm_close reference_px (<) | 3 |
| mss_fvg_refinement | no_setup | source_hold_confirmed | 3 |
| nyam_box | no_setup | confirm_close reference_px (<) | 2 |
| previous_hour | no_setup | objective_fixed | 2 |
| asia_tdo_case | no_setup | objective_fixed | 1 |
| prior_week_level | no_setup | confirm_close reference_px (<) | 1 |
| prior_month_level | no_setup | confirm_close reference_px (<) | 1 |
| prior_month_level | no_setup | box_return_ok | 1 |
| cash_open_reclaim_case | no_setup | objective_fixed | 1 |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/methods/GB-FAIL.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json).
