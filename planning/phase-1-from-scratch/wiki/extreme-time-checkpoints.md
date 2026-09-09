# High/low timing and checkpoint survival

Family: **day-type**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[4H HOD LOD Checkpoint Analysis.txt, L49–61,128–191,388–730](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses six NY slots 18–22,22–02,02–06,06–10,10–14,14–17 and extreme-elimination patterns. Rates are hardcoded; source omits the day’s first bar. [Historical High and Lows Statistical Analysis 30min bins.txt, L1–140](../../../sources/documents/indicators/Pinescript-indicators--main.zip) bins first strict final extremes by bar-close time in an exchange-time session. [Key levels, MTF swing highs, lows & 4h candle boxes.txt, L543–579](../../../sources/documents/indicators/Pinescript-indicators--main.zip) shares first-bar omission and a 14–18 label over a 14–17 box. [Time-Based ranges Framework (JJumbo).pdf, p.30](../../../sources/documents/jumbo/Time-Based%20ranges%20Framework%20%28JJumbo%29.pdf#page=30) and [xfcmg2.pdf, pp.47–48](../../../sources/documents/jumbo/xfcmg2.pdf#page=47) give reversal-time averages with an unspecified event population.

## Computability and faithful reconstruction

OHLC supports final-extreme slot counts. Trades improve time and tie resolution. Final HOD/LOD is available only after the outcome horizon.

At each checkpoint store rails already formed and which have been breached. Later final extreme and surviving rail are outcomes. Keep HOD and LOD separate, first/last equal-extreme times explicit and partial sessions labeled.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **first-bar-included / exact-NY-calendar**, **trade-timestamp**, **first-versus-last tie**, **full categorical support**.
- **discovery-only shrunk checkpoint frequencies** and fixed-grid/formation-bar variants. Prediction of remaining extremes is Phase 2.

## Phase 1 outcomes

Extreme-time histogram, checkpoint rail survival, future breach, elimination-pattern support and yearly stability. No source percentage is inherited as a result.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

None specific. Use the common measurement definitions.

## Related

[candle curves](candle-curves.md), [range break paths](range-break-paths.md), [deferred context location](deferred-context-location.md)

Review findings: J-TBR-08, J-X-15, ZIP-01, ZIP-24, ZIP-32. [Review ledger](../REVIEW_LEDGER.md).
