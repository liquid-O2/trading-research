# SAINT-AMT: strategy reconstruction

Observed entry candidates: 0 setup, 18 no setup, 8 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| continuation_retest | entry_setup | RTVP pp.3–11;WIC pp.7–10: fitted HTF accepted balance → actual LTF balance break → same-boundary retest → repeated directional aggression |
| trapped_buyers_retest | entry_setup | TRAP pp.3–10;WIC pp.7–10: two distinct earlier upper buying failures → current LTF down break → same-boundary retest → repeated body selling |
| failed_auction_return | entry_setup | AMTL pp.8–10: original balance → distinct older value tested/rejected → original balance reacceptance → local control |
| poc_traversal | entry_setup | RTVP pp.5–8;AMTL pp.8–11: original balance reacceptance → aggressive POC passage → source hold → far-edge objective |

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |
| continuation_retest | no_setup | same_boundary_retest_held | 5 |
| failed_auction_return | no_setup | older_value_tested | 4 |
| failed_auction_return | data_unavailable | control_evidence_recorded | 4 |
| failed_auction_return | data_unavailable | alignment_ok | 4 |
| failed_auction_return | data_unavailable | risk_defined | 4 |
| failed_auction_return | data_unavailable | objective_fixed | 4 |
| failed_auction_return | data_unavailable | control_at | 4 |
| failed_auction_return | data_unavailable | arrival_at control_at | 4 |
| failed_auction_return | data_unavailable | control_at decision_at | 4 |
| failed_auction_return | data_unavailable | local_control_confirms_return | 4 |
| poc_traversal | data_unavailable | control_evidence_recorded | 4 |
| poc_traversal | data_unavailable | alignment_ok | 4 |
| poc_traversal | data_unavailable | risk_defined | 4 |
| poc_traversal | data_unavailable | objective_fixed | 4 |
| poc_traversal | data_unavailable | control_at | 4 |
| poc_traversal | data_unavailable | arrival_at control_at | 4 |
| poc_traversal | data_unavailable | control_at decision_at | 4 |
| poc_traversal | data_unavailable | source_poc_hold_confirmed | 4 |
| trapped_buyers_retest | no_setup | same_boundary_retest_held | 3 |
| poc_traversal | no_setup | objective_fixed | 3 |
| poc_traversal | data_unavailable | aggressive_poc_passage | 3 |
| poc_traversal | data_unavailable | poc_passage_at | 3 |
| poc_traversal | data_unavailable | poc_passage_at reaccept_at | 3 |
| poc_traversal | data_unavailable | decision_at poc_passage_at | 3 |
| continuation_retest | no_setup | risk_defined | 2 |
| failed_auction_return | no_setup | risk_defined | 2 |
| failed_auction_return | data_unavailable | original_balance_reaccepted | 2 |
| failed_auction_return | data_unavailable | reaccept_at | 2 |
| failed_auction_return | data_unavailable | reaccept_at rejection_at | 2 |
| failed_auction_return | data_unavailable | decision_at reaccept_at | 2 |
| poc_traversal | data_unavailable | original_balance_reaccepted | 2 |
| poc_traversal | data_unavailable | reaccept_at | 2 |
| poc_traversal | no_setup | risk_defined | 2 |
| poc_traversal | no_setup | source_poc_hold_confirmed | 2 |
| continuation_retest | no_setup | objective_fixed | 1 |
| trapped_buyers_retest | no_setup | objective_fixed | 1 |
| trapped_buyers_retest | no_setup | risk_defined | 1 |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/methods/SAINT-AMT.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/registry/STRATEGY_POLICY.json).
