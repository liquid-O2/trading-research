# STOIC-RISK: strategy reconstruction

Observed entry candidates: 0 setup, 0 no setup, 0 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| first | personal_execution_out_of_scope | DATA pp.7–8: prior process/100+ sample and validation → printed first stage arithmetic; no historical ledger reconstructed |
| second | personal_execution_out_of_scope | DATA pp.7–8: prior process/100+ sample and validation → printed second stage arithmetic; no historical ledger reconstructed |
| reset_after_second_win | personal_execution_out_of_scope | DATA pp.7–8: prior process/100+ sample and validation → printed reset_after_second_win stage arithmetic; no historical ledger reconstructed |

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/methods/STOIC-RISK.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json).
