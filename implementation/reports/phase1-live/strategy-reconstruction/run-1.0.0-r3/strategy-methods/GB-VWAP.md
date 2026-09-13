# GB-VWAP: strategy reconstruction

Observed entry candidates: 2 setup, 0 no setup, 1 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| source_long | entry_setup | GB p.33 posts 2026329904690712970/2026386393820283204: both finished session highs → close above → later contemporaneous VWAP return → long risk/continuation observation |

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |
| source_long | data_unavailable | reference_frozen | 1 |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/methods/GB-VWAP.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/registry/STRATEGY_POLICY.json).
