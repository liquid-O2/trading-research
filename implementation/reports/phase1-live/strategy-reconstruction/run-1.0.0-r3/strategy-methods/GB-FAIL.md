# GB-FAIL: strategy reconstruction

Observed entry candidates: 18 setup, 54 no setup, 10 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

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
| previous_hour | no_setup | box_return_ok | 23 |
| previous_hour | no_setup | confirm_close reference_px (>) | 12 |
| previous_hour | no_setup | confirm_close reference_px (<) | 9 |
| asia_tdo_case | no_setup | box_return_ok | 8 |
| asia_tdo_case | no_setup | NOT tdo_required | 8 |
| asia_tdo_case | no_setup | source_tdo_close_confirmed | 6 |
| prior_day_level | no_setup | box_return_ok | 5 |
| nyam_box | no_setup | box_return_ok | 4 |
| asia_tdo_case | no_setup | confirm_close reference_px (>) | 4 |
| prior_day_level | no_setup | confirm_close reference_px (>) | 4 |
| prior_week_level | no_setup | confirm_close reference_px (>) | 4 |
| prior_week_level | no_setup | box_return_ok | 4 |
| cash_open_reclaim_case | no_setup | confirm_close reference_px (>) | 4 |
| nyam_box | no_setup | confirm_close reference_px (>) | 3 |
| previous_hour | data_unavailable | risk_defined | 3 |
| previous_hour | data_unavailable | objective_fixed | 3 |
| previous_hour | data_unavailable | confirm_close | 3 |
| previous_hour | data_unavailable | confirm_close reference_px | 3 |
| previous_hour | data_unavailable | box_return_ok | 3 |
| previous_hour | data_unavailable | complete_clock_five_minute_bar | 3 |
| asia_tdo_case | no_setup | confirm_close reference_px (<) | 3 |
| mss_fvg_refinement | no_setup | source_hold_confirmed | 3 |
| previous_hour | no_setup | objective_fixed | 2 |
| prior_week_level | data_unavailable | risk_defined | 2 |
| prior_week_level | data_unavailable | objective_fixed | 2 |
| prior_week_level | data_unavailable | confirm_close | 2 |
| prior_week_level | data_unavailable | confirm_close reference_px | 2 |
| prior_week_level | data_unavailable | box_return_ok | 2 |
| prior_week_level | data_unavailable | complete_clock_five_minute_bar | 2 |
| prior_month_level | data_unavailable | reference_frozen | 2 |
| prior_month_level | no_setup | confirm_close reference_px (>) | 2 |
| prior_month_level | no_setup | box_return_ok | 2 |
| nyam_box | no_setup | confirm_close reference_px (<) | 1 |
| nyam_box | data_unavailable | risk_defined | 1 |
| nyam_box | data_unavailable | objective_fixed | 1 |
| nyam_box | data_unavailable | confirm_close | 1 |
| nyam_box | data_unavailable | confirm_close reference_px | 1 |
| nyam_box | data_unavailable | box_return_ok | 1 |
| nyam_box | data_unavailable | complete_clock_five_minute_bar | 1 |
| asia_tdo_case | data_unavailable | risk_defined | 1 |
| asia_tdo_case | data_unavailable | objective_fixed | 1 |
| asia_tdo_case | data_unavailable | confirm_close | 1 |
| asia_tdo_case | data_unavailable | confirm_close reference_px | 1 |
| asia_tdo_case | data_unavailable | box_return_ok | 1 |
| asia_tdo_case | data_unavailable | complete_clock_five_minute_bar | 1 |
| asia_tdo_case | data_unavailable | source_tdo_close_confirmed | 1 |
| asia_tdo_case | no_setup | objective_fixed | 1 |
| prior_day_level | data_unavailable | risk_defined | 1 |
| prior_day_level | data_unavailable | objective_fixed | 1 |
| prior_day_level | data_unavailable | confirm_close | 1 |
| prior_day_level | data_unavailable | confirm_close reference_px | 1 |
| prior_day_level | data_unavailable | box_return_ok | 1 |
| prior_day_level | data_unavailable | complete_clock_five_minute_bar | 1 |
| prior_day_level | no_setup | confirm_close reference_px (<) | 1 |
| prior_month_level | data_unavailable | risk_defined | 1 |
| prior_month_level | data_unavailable | objective_fixed | 1 |
| prior_month_level | data_unavailable | confirm_close | 1 |
| prior_month_level | data_unavailable | confirm_close reference_px | 1 |
| prior_month_level | data_unavailable | box_return_ok | 1 |
| prior_month_level | data_unavailable | complete_clock_five_minute_bar | 1 |
| cash_open_reclaim_case | no_setup | objective_fixed | 1 |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/methods/GB-FAIL.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/registry/STRATEGY_POLICY.json).
