# Kernel, moving-average and ratcheted price bands

Family: **volatility**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[Confluence Suite.txt, L1–936](../../../sources/documents/indicators/Pinescript-indicators--main.zip) defines HMA/double-WMA trail, SuperSmoother, Donchian, rational-quadratic kernel24/h8/r2 HLC3 bands at 1.5/2.5 hybrid absolute-deviation/ATR scale and NeoCloud ATR 365 ratchets. Its “reversal zone” is unrelated to Jumbo P-zones. confluence_suite is itsL1–578 prefix. [MTF Bollinger Bands Trend Stop.txt, L1–86](../../../sources/documents/indicators/Pinescript-indicators--main.zip) has two separate direction states: prior-band close cross and current-buffer high/low cross, with different tie precedence. [MTF HTF market analysis toolkit.txt, L508–534](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses ZLEMA70±1.2maxATR70 over 210 bars. [HMM Enhanced Regime Probability.txt, L1–382](../../../sources/documents/indicators/Pinescript-indicators--main.zip) supplies WMA/TR trail features; its model is treated separately.

## Computability and faithful reconstruction

OHLC/volume histories support causal raw bands and states. Completed HTF and developing versions must not be conflated.

Emit each band formula/scale, ratchet state, initialization and known_at. Keep two source Bollinger states separate. Risk buffers are geometric source parameters here, not stop orders.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **closed-HTF versus developing**, **lagged robust dispersion**, **symmetric/asymmetric scales**, **time/activity-bar sampling**, **simultaneous-cross unknown**.
- Compare source kernel versus VWAP/empirical bands on the same outcomes and density.

## Phase 1 outcomes

Contact, dwell, reversion, band walking, crossing, state duration and yearly stability. Do not infer causal support from a hindsight-smoothed plot.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

None specific. Use the common measurement definitions.

## Related

[momentum oscillator features](momentum-oscillator-features.md), [vwap deviation bands](vwap-deviation-bands.md), [adaptive indicator states](adaptive-indicator-states.md)

Review findings: ZIP-11, ZIP-17, ZIP-20, ZIP-34, ZIP-35, ZIP-79. [Review ledger](../REVIEW_LEDGER.md).
