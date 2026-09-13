# STOIC-DATA: strategy reconstruction

Observed entry candidates: 0 setup, 0 no setup, 0 unavailable market input. Separately retained context/process observations: 3. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| process_review | context_or_research | DATA pp.3–4: frozen declared process → uniform inclusion → all observations → winner/loser comparison → prior-sample revision |
| macro_application | context_or_research | DATA pp.5–6: actual vintage admission → selected indicator historical comparison → supplied custom cycle/C-score/trend interpretation |
| macro_application | context_or_research | DATA pp.5–6: actual vintage admission → selected indicator historical comparison → supplied custom cycle/C-score/trend interpretation |

Operational model (macro): `{'source': 'data-engine.pdf pp.5–6', 'model': 'equal mean of signed initial-release z scores: payroll positive, CPI negative; 12 prior initial observations', 'output': 'research context only; not proprietary C-score or an entry'}`

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/methods/STOIC-DATA.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json).
