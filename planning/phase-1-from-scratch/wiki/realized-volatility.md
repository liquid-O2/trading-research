# Realized volatility and lagged scale features

Family: **volatility**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

The user requests Garman–Klass, Yang–Zhang, realized volatility and richer volatility features. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md) [conversation_raw_log.md, L40–48](../../../sources/documents/conversations/conversation_raw_log.md) [conversation_export (1).md, Turns1–4](../../../sources/documents/conversations/conversation_export%20%281%29.md). [ATR Breakout.txt, L1–43](../../../sources/documents/indicators/Pinescript-indicators--main.zip) supplies ATR 14 percentile100 and 6bar-open momentum versus4ATR. [Adaptive Volatility Adjusted Momentum Score.txt, L1–140](../../../sources/documents/indicators/Pinescript-indicators--main.zip) adapts a clipped lookback using ATR mean/SD, but normalizes percent ROC by price SD. [Leptokurtic Directional Bias.txt, L97–178](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses rolling-centered ATR/price/volume fourth moments, not fixed-window return kurtosis. [NQ Stats Price Distributions.txt, L408–428](../../../sources/documents/indicators/Pinescript-indicators--main.zip) scales excursion bands with prior daily close-return SD, distinct from its stated open-close RMS.

## Computability and faithful reconstruction

OHLC supports GK/YZ and daily returns; trades/minutes support RV at named sampling intervals. Gaps, roll jumps and overnight returns need explicit treatment. No options intersection is required.

Proposed mathematical contract: GK per bar =0.5·log(H/L)^2−(2log2−1)·log(C/O)^2. YZ combines overnight-return sample variance, open-close sample variance and Rogers–Satchell variance with the standard finite-sample k; store window length and exact formula version. RV is the sum of squared sampled log returns. HAR inputs are lagged1/5/22-session RV averages, without fitting a forecast. Store units, sampling interval and known_at; never use current incomplete daily volatility as a completed-day feature.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **GK / YZ / RV / close-return / ATR** scales; **1s/1m/5m RV**, **session versus full-day**, **overnight-separated**, **noise-robust subsampling**.
- **fixed-window return kurtosis**, **dimensionless momentum**, **lagged robust scale**, **time/volume/dollar sampling**. These are proposed measurement alternatives.

## Phase 1 outcomes

Coverage, estimator agreement, realized next-horizon range descriptors, normalized zone/rail touch and overshoot, conditional path separation and yearly stability. Descriptive comparison is not a deployed forward-vol product.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q03 fixes day/roll/gap boundaries. Exact estimator conventions are versioned before computation; no user trading meaning is inferred.

## Related

[implied vx curve](implied-vx-curve.md), [distribution envelopes](distribution-envelopes.md), [momentum oscillator features](momentum-oscillator-features.md)

Review findings: USER-01, USER-02, USER-05, ZIP-08, ZIP-09, ZIP-33, ZIP-45. [Review ledger](../REVIEW_LEDGER.md).
