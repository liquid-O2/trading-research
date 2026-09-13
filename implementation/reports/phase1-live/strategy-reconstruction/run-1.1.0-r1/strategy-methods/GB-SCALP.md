# GB-SCALP: strategy reconstruction

Observed entry candidates: 12 setup, 0 no setup, 0 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| bearish_small_scalp | entry_setup | GB p.40 post 2095257805242446135: pre-existing bearish direction → pullback → supplied small exposure and limited management; entry rule unpublished |
| bullish_discount_pullback | entry_setup | GB p.40 post 2098075540607410229: NYAM direction → selected impulse discount pullback → small exposure/process audit; entry rule unpublished |
| automatic_admission | supplemental_observation | FORMULAS:M04: automatic_admission process/management unit |

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/methods/GB-SCALP.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json).
