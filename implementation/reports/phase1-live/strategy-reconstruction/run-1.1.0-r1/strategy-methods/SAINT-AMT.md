# SAINT-AMT: strategy reconstruction

Observed entry candidates: 0 setup, 26 no setup, 0 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| continuation_retest | entry_setup | RTVP pp.3–11;WIC pp.7–10: fitted HTF accepted balance → actual LTF balance break → same-boundary retest → repeated directional aggression |
| trapped_buyers_retest | entry_setup | TRAP pp.3–10;WIC pp.7–10: two distinct earlier upper buying failures → current LTF down break → same-boundary retest → repeated body selling |
| failed_auction_return | entry_setup | AMTL pp.8–10: original balance → distinct older value tested/rejected → original balance reacceptance → local control |
| poc_traversal | entry_setup | RTVP pp.5–8;AMTL pp.8–11: original balance reacceptance → aggressive POC passage → source hold → far-edge objective |

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |
| failed_auction_return | no_setup | control_evidence_recorded | 6 |
| failed_auction_return | no_setup | local_control_confirms_return | 6 |
| continuation_retest | no_setup | same_boundary_retest_held | 5 |
| failed_auction_return | no_setup | older_value_tested | 4 |
| failed_auction_return | no_setup | older_value_rejected | 4 |
| failed_auction_return | no_setup | original_balance_reaccepted | 4 |
| poc_traversal | no_setup | objective_fixed | 4 |
| poc_traversal | no_setup | control_evidence_recorded | 4 |
| trapped_buyers_retest | no_setup | same_boundary_retest_held | 3 |
| poc_traversal | no_setup | aggressive_poc_passage | 3 |
| continuation_retest | no_setup | objective_fixed | 2 |
| trapped_buyers_retest | no_setup | objective_fixed | 2 |
| trapped_buyers_retest | no_setup | prior_buying_at_upper_extreme | 2 |
| trapped_buyers_retest | no_setup | two_distinct_prior_failures | 2 |
| poc_traversal | no_setup | original_balance_reaccepted | 2 |
| continuation_retest | no_setup | control_evidence_recorded | 1 |
| continuation_retest | no_setup | repeated_aggression_in_trade_direction | 1 |
| continuation_retest | no_setup | risk_defined | 1 |
| trapped_buyers_retest | no_setup | control_evidence_recorded | 1 |
| trapped_buyers_retest | no_setup | repeated_body_selling | 1 |
| failed_auction_return | no_setup | risk_defined | 1 |
| failed_auction_return | no_setup | objective_fixed | 1 |
| poc_traversal | no_setup | risk_defined | 1 |
| poc_traversal | no_setup | source_poc_hold_confirmed | 1 |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/methods/SAINT-AMT.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json).
