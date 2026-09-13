# KEANI-OPEN-ABOVE-VALUE: strategy reconstruction

Observed entry candidates: 0 setup, 3 no setup, 3 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| source_long | entry_setup | AVG pp.21–22: whole A above prior VAH → higher developing value/rejection → aggressive VAH imbalance break → defended same-imbalance retest |

Operational model (calendar): `{'model': 'regular NQ schedule with inferred New Year/Christmas RTH closures', 'scope': 'fixed-date New Year/Christmas closures, including Monday observance; Friday before Saturday New Year remains regular, corroborated by 390 native 2021-12-31 RTH minute records; other unverified holidays remain unavailable', 'interpretation': 'reconstruction calendar assumption, not newly recovered CME schedule evidence'}`

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |
| source_long | data_unavailable | dev_vah_known_at | 3 |
| source_long | data_unavailable | breakout_at | 3 |
| source_long | data_unavailable | breakout_at dev_vah_known_at | 3 |
| source_long | data_unavailable | breakout_close | 3 |
| source_long | data_unavailable | dev_vah_at_break | 3 |
| source_long | data_unavailable | breakout_close dev_vah_at_break | 3 |
| source_long | data_unavailable | aggressive_buy_imbalance_break | 3 |
| source_long | data_unavailable | imbalance_band_known_at | 3 |
| source_long | data_unavailable | retest_at | 3 |
| source_long | data_unavailable | imbalance_band_known_at retest_at | 3 |
| source_long | data_unavailable | breakout_at retest_at | 3 |
| source_long | data_unavailable | defense_at | 3 |
| source_long | data_unavailable | defense_at retest_at | 3 |
| source_long | data_unavailable | buyers_defend_same_imbalance_band | 3 |
| source_long | data_unavailable | dom_supports_long | 3 |
| source_long | data_unavailable | time_of_day_allowed | 3 |
| source_long | data_unavailable | objective_fixed | 3 |
| source_long | data_unavailable | risk_defined | 3 |
| source_long | data_unavailable | breakout_at observation_at | 3 |
| source_long | data_unavailable | decision_at defense_at | 3 |
| source_long | no_setup | a_low prior_vah (>) | 3 |
| source_long | data_unavailable | developing_value_builds_higher | 2 |
| source_long | data_unavailable | source_rejection_observed | 2 |
| source_long | data_unavailable | observation_at | 2 |
| source_long | data_unavailable | a_end_at observation_at | 2 |
| source_long | data_unavailable | prior_value_fixed | 1 |
| source_long | data_unavailable | prior_vah | 1 |
| source_long | data_unavailable | a_low prior_vah | 1 |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/methods/KEANI-OPEN-ABOVE-VALUE.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/registry/STRATEGY_POLICY.json).
