# All required CVD constructions

Family: **CVD-SMT**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[dom-lesson-5.pdf, pp.3–7](../../../sources/documents/discretionary/dom-lesson-5.pdf#page=3) and [vwap-lesson-10.pdf, pp.5–7](../../../sources/documents/discretionary/vwap-lesson-10.pdf#page=5) define cumulative aggressive buy minus sell volume. [momentum-volume-flow-levels.txt, L1–107](../../../sources/documents/indicators/momentum-volume-flow-levels.txt) sums signed1m subbar volume (close>open positive, close<open negative, doji0), with chart-bar fallback; detections are session-gated but history does not reset. [Confluence Suite.txt, L1–936](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses close-location/body/previous-close sign alternatives. [Oscillator Suite.txt, L102–210,298–337](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses money-flow proxies; “smart money” is a label, not identity. The user requires trade, OHLC, participant-separated trade, participant-separated OHLC and gamma CVD. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md) [Design robust feature levels.md, user turns L682–700,904–924,1560–1854](../../../sources/documents/conversations/Design%20robust%20feature%20levels.md).

## Computability and faithful reconstruction

Futures trades/MBP-1 support actual aggressor delta; OHLC supports longer proxy history. Options trade_quote requires explicit signing and product/underlying mapping. Neither futures print size nor OHLC identifies actual participants.

Emit five separately named families: **trade-cvd**, **ohlc-cvd**, **participant-proxy-trade-cvd**, **participant-proxy-ohlc-cvd**, **gamma-cvd**. Store increments and cumulative values, resets, unknown-side volume and units. Source OHLC logic stays intact as a benchmark. Q20 must define participant proxy and gamma weighting; do not quietly drop either branch or substitute MFI.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **session/day/rolling-reset**, **trade-sign confidence**, **volume-normalized CVD**, **time/trade/volume/dollar aggregation**.
- **size-bucket participant proxy** and **bar-activity participant proxy** are candidate definitions pending Q20, not observed institutional/retail flow.
- **raw gamma / delta-equivalent / position-sign scenario weighting** remain explicitly named candidates pending Q20; no unapproved meaning is called faithful.

## Phase 1 outcomes

Coverage and unknown-sign mass, increment reconciliation, pairwise construction disagreement, divergence frequency, touch-conditioned subsequent path and stability. Compare all five on honest samples; missing definitions receive blocked rows, never omitted rows.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q20 defines participant separation, gamma-CVD formula, units, reset and cross-product mapping. OHLC participant identity cannot be recovered; a proxy definition is required.

## Related

[cvd divergence](cvd-divergence.md), [delta profiles](delta-profiles.md), [options flow oi calibration](options-flow-oi-calibration.md), [smt extreme nonconfirmation](smt-extreme-nonconfirmation.md)

Review findings: USER-01, USER-04, USER-05, D-DOM-01, D-VWAP-02, PINE-BIAS-01, ZIP-11, ZIP-50. [Review ledger](../REVIEW_LEDGER.md).
