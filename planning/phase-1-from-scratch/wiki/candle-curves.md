# Quarter-window curves and AM-to-PM paths

Family: **day-type**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[4h Candle Curves.txt, L10–16,189–332,392–422](../../../sources/documents/indicators/Pinescript-indicators--main.zip) defines a curve when Q2 breaks Q1 high then the second half breaks Q1 low, mirrored down. Continuation is second-half movement beyond Q2 extreme. Both can happen; display precedence is not an exclusive class. The 14–17 slot has only three hours. [NQ Stats Noon Curve.txt, L127–131,270–279](../../../sources/documents/indicators/Pinescript-indicators--main.zip) instead uses 08–10/10–12/12–16, Q2 break direction and fixed-price AM/PM bands without PM outcome counting. [Time-Based ranges Framework (JJumbo).pdf, pp.15–21,36–38](../../../sources/documents/jumbo/Time-Based%20ranges%20Framework%20%28JJumbo%29.pdf#page=15) uses 09:30–12 AM,12–13 lunch,13–16 PM, with expansion/balance transitions.

## Computability and faithful reconstruction

OHLC supports complete period paths. Trades resolve break order; event time replaces assumed contiguous bar counts.

Name each clock partition and each curve/continuation definition. Count both and neither. Keep PM extrema and final candle wick/body decomposition as later outcomes, not AM predictors.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **clock-exact**, **RTH-quarter-grid**, **trade-order**, **width/RV-normalized expansion**, and **time/trade/activity-bar** variants.
- Compare source fixed-percent bands with discovery-only excursion quantiles.

## Phase 1 outcomes

First/second-half path contingency, curve/continuation/both/neither, AM→PM expansion/balance, final extreme timing, projection reach and no-event support.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q02 defines operational expansion/balance thresholds; raw continuous distances remain countable before labels resolve.

## Related

[extreme time checkpoints](extreme-time-checkpoints.md), [jumbo day classes](jumbo-day-classes.md), [extension projections](extension-projections.md)

Review findings: J-TBR-04, J-TBR-05, J-TBR-11, ZIP-02, ZIP-44. [Review ledger](../REVIEW_LEDGER.md).
