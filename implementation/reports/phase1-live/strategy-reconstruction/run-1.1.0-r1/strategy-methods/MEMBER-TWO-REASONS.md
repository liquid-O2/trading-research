# MEMBER-TWO-REASONS: strategy reconstruction

Observed entry candidates: 1 setup, 6 no setup, 0 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| resistance_short | entry_setup | K10 pp.5–7,12: prior reaction + independently observed nearby minor HVN → current rejection → stop above rejection |
| planned_return_long | entry_setup | K10 pp.6–8,12: planned prior structure + independent minor HVN → second/distinct return → buyers absorb/hold → structural stop |

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |
| planned_return_long | no_setup | buyers_absorb_and_hold | 4 |
| resistance_short | no_setup | resistance_rejection | 2 |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/methods/MEMBER-TWO-REASONS.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json).
