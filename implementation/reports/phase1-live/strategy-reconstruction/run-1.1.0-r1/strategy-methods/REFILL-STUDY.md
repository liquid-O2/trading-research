# REFILL-STUDY: strategy reconstruction

Observed entry candidates: 0 setup, 0 no setup, 0 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| touch_record | context_or_research | REF pp.5–9;OFM pp.15–18: large execution cluster → immutable zone → departure → distinct return with pre-touch memory → later label |
| supplied_selected_order | personal_execution_out_of_scope | REF p.12,16;OFM p.18: actual supplied model selection → 12/32/96 tick configuration → 30 minute cancel → one position → actual lifecycle/cost audit |
| selected_order_configuration | personal_execution_out_of_scope | FORMULAS:M09: selected_order_configuration process/management unit |

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/methods/REFILL-STUDY.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json).
