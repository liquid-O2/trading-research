# Raw momentum, squeeze and oscillator nonconfirmation

Family: **volatility**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[ATR Breakout.txt, L1–43](../../../sources/documents/indicators/Pinescript-indicators--main.zip) and [Adaptive Volatility Adjusted Momentum Score.txt, L1–140](../../../sources/documents/indicators/Pinescript-indicators--main.zip) combine range percentile and momentum with source unit/loop quirks. [TTM Squeeze Divergence.txt, L7–65](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses BB20/2SD versus KC20/1.5 SMA(TR), linreg momentum and 5/5 confirmed regular/hidden oscillator divergences. These are not CVD or SMT. [Oscillator Suite.txt, L130–382](../../../sources/documents/indicators/Pinescript-indicators--main.zip) adds normalized price deviation, MFI 35, T3/ZEMA/KAMA/kernel smoothers, sign-separated flow, volume filters and body-extreme nonconfirmation. Its equal-weight composite is not calibrated probability.

[Deviation based reversion with Stats.txt, L6–175,213–279](../../../sources/documents/indicators/Pinescript-indicators--main.zip) signals directional continuation beyond regression despite its title; bull/bear defaults and 7/5-bar±20point outcomes differ. Its signal-bar extrema precede close confirmation, immature signals enter n and only the last signal is tracked. [Leptokurtic Directional Bias.txt, L97–178](../../../sources/documents/indicators/Pinescript-indicators--main.zip) combines source kurtosis, RSI and EMA/momentum. [Confluence Suite.txt, L1–936](../../../sources/documents/indicators/Pinescript-indicators--main.zip) contributes normalized trend/ATR/squeeze/flow; confluence_suite ends atL578.

## Computability and faithful reconstruction

OHLCV supports these descriptors. Actual trade delta is a shorter-sample comparator. No trained bias score is required.

Preserve raw component values, source smoothing/normalization and confirmed marker time. Keep source-as-coded versus mathematically intended formulas distinct. Oscillator divergence does not become participant flow.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **dimensionless return scaling**, **fixed-window MAD/kurtosis**, **lagged scales**, **separate-side divergence state**, **causal confirmed pivots**, **all-event mature outcomes**.
- **time/trade/volume/dollar bars**, **actual CVD comparison**, **single-component versus untrained source composite** descriptive ablations.

## Phase 1 outcomes

Feature coverage, marker count/delay, price-path separation, band reach/reversion/continuation, disagreements and year stability. No source alert/P&L or fitted classifier.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

None specific. Use the common measurement definitions.

## Related

[realized volatility](realized-volatility.md), [cvd divergence](cvd-divergence.md), [kernel trend bands](kernel-trend-bands.md), [adaptive indicator states](adaptive-indicator-states.md)

Review findings: ZIP-08, ZIP-09, ZIP-11, ZIP-17, ZIP-33, ZIP-50, ZIP-72, ZIP-79. [Review ledger](../REVIEW_LEDGER.md).
