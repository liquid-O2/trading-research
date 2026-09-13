# JETBUNDLE-STATES: strategy reconstruction

Observed entry candidates: 0 setup, 0 no setup, 0 unavailable market input. Separately retained context/process observations: 35. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| B | context_or_research | MATH pp.4–11: native provide/withdraw/consume and response observations → supplied B label/qualitative criteria; no invented classifier |
| A | context_or_research | MATH pp.4–11: native provide/withdraw/consume and response observations → supplied A label/qualitative criteria; no invented classifier |
| D | context_or_research | MATH pp.4–11: native provide/withdraw/consume and response observations → supplied D label/qualitative criteria; no invented classifier |
| E | context_or_research | MATH pp.4–11: native provide/withdraw/consume and response observations → supplied E label/qualitative criteria; no invented classifier |
| W | context_or_research | MATH pp.4–11: native provide/withdraw/consume and response observations → supplied W label/qualitative criteria; no invented classifier |
| transition_observation | context_or_research | FORMULAS:M10: transition_observation process/management unit |

Operational model (auction): `{'source': 'the-math-behind-auction-market-theory.pdf pp.4–11', 'window_seconds': 120, 'high_effort_multiple': 1.5, 'low_efficiency': 0.2, 'high_efficiency': 0.6, 'replenishment_stop_fraction': 0.25, 'response': 'difference of first/last quarter-window execution VWAP; efficiency divided by window range', 'inventory': 'displayed depth-one additions/removals; removal less executions is an estimate, not identified cancels'}`

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/methods/JETBUNDLE-STATES.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/registry/STRATEGY_POLICY.json).
