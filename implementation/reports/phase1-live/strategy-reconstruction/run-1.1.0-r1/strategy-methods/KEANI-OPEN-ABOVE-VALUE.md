# KEANI-OPEN-ABOVE-VALUE: strategy reconstruction

Observed entry candidates: 0 setup, 6 no setup, 0 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| source_long | entry_setup | AVG pp.21–22: whole A above prior VAH → higher developing value/rejection → aggressive VAH imbalance break → defended same-imbalance retest |

Operational model (calendar): `{'model': 'regular NQ schedule with inferred New Year/Christmas RTH closures', 'scope': 'fixed-date New Year/Christmas closures, including Monday observance; Friday before Saturday New Year remains regular, corroborated by 390 native 2021-12-31 RTH minute records; other unverified holidays remain unavailable', 'interpretation': 'reconstruction calendar assumption, not newly recovered CME schedule evidence'}`

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |
| source_long | no_setup | aggressive_buy_imbalance_break | 6 |
| source_long | no_setup | buyers_defend_same_imbalance_band | 6 |
| source_long | no_setup | dom_supports_long | 6 |
| source_long | no_setup | time_of_day_allowed | 6 |
| source_long | no_setup | developing_value_builds_higher | 4 |
| source_long | no_setup | source_rejection_observed | 4 |
| source_long | no_setup | a_low prior_vah (>) | 3 |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/methods/KEANI-OPEN-ABOVE-VALUE.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json).
