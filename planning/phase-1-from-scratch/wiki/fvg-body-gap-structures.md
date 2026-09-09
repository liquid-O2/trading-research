# Wick gaps, body gaps and first-presented FVGs

Family: **auction-order-flow**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[Time-Based ranges Framework (JJumbo).pdf, pp.32–35](../../../sources/documents/jumbo/Time-Based%20ranges%20Framework%20%28JJumbo%29.pdf#page=32) retains first-presented FVG and H1/M15 imbalances. [First presented FVG (with stats) with statistical hourly ranges & bias.txt, L81–85,148–170,254–304,342–353](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses the first three-bar wick gap per hour on1/3/5/15m, but W1 code includes all 09hour despite09:30–10 label; hardcoded effectiveness rates and first 15 timing are not verified evidence. [Sweep, CISD, MTF FVG & Key Levels.txt, L551–638,985–999](../../../sources/documents/indicators/Pinescript-indicators--main.zip) creates outer-wick gaps and adjacent body gaps called “volume imbalance” without using volume. Value-change detection can miss identical candles; sharing one edge can wrongly deduplicate zones. [8020 System.txt, L1–489](../../../sources/documents/indicators/Pinescript-indicators--main.zip) defines a consecutive-body gap≥4 ticks and near-edge fill.

## Computability and faithful reconstruction

OHLC can reconstruct geometric gaps after the third/second bar closes. Trades support subsequent path; geometric gaps do not prove zero traded volume.

Persist wick gap, body gap and first-per-clock identities separately. Record near-edge, partial and far-edge fill/invalidation. Capture no-FVG periods and source-as-coded/labeled clock disagreement.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **timestamp-based formation**, **shared-edge independent IDs**, **wick/body/trade-volume-gap comparison**, **native-tick/vol-scaled size**, **1/3/5/15m plus activity bars**, **fixed-grid clocks**.

## Phase 1 outcomes

Formation coverage, first touch, partial/full fill, reject/accept, time to fill, no-return and later direction. Confirmation must precede every counted post-formation outcome.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

None specific. Use the common measurement definitions.

## Related

[sweep cisd blocks](sweep-cisd-blocks.md), [candle patterns round levels](candle-patterns-round-levels.md), [time based ranges](time-based-ranges.md)

Review findings: J-TBR-10, ZIP-05, ZIP-19, ZIP-71. [Review ledger](../REVIEW_LEDGER.md).
