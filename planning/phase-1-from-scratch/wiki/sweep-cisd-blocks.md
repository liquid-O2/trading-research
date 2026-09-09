# Sweeps, CISD and confirmed candle blocks

Family: **auction-order-flow**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[Time-Based ranges Framework (JJumbo).pdf, pp.25–29](../../../sources/documents/jumbo/Time-Based%20ranges%20Framework%20%28JJumbo%29.pdf#page=25) uses a2/3/5m three-candle sequence: candle2 sweeps candle1; candle3 closes beyond candle2. Rejection blocks use the sweep wick. [Open Source Fractal - Customized.txt, L1–118,306–342,523–951](../../../sources/documents/indicators/Open%20Source%20Fractal%20-%20Customized.txt) has C2 sweep/close-back, CISD opposing-run scans, C3/C4 open-to-prior-mid spans and invalidation. Historical HTF lookahead cannot define causal availability.

[HTF Sweep Model with CISD Table.txt, L112–179,300–408,537–727](../../../sources/documents/indicators/Pinescript-indicators--main.zip) has different screener/close-inside/body-inside tests and delayed CISD close crossing. [HTF Sweeps & Liquidity Levels with CISD.txt, L694–696](../../../sources/documents/indicators/Pinescript-indicators--main.zip) tightens the whole-body test. [MTF HTF market analysis toolkit.txt, L636–763](../../../sources/documents/indicators/Pinescript-indicators--main.zip) mutates opposing-open levels. [Pivot Order Blocks.txt, L12–120](../../../sources/documents/indicators/Pinescript-indicators--main.zip) uses 25/25 close or wick pivots, unequal-left/right anchoring and near-edge “broken” labels. [Sweep, CISD, MTF FVG & Key Levels.txt, L652–724,917–929,1084–1440](../../../sources/documents/indicators/Pinescript-indicators--main.zip) adds log-wick midpoint, wick-lick, expansive, pro-trend and silver subtypes, plus opposing-body/wick-envelope CISD.

## Computability and faithful reconstruction

Completed OHLC and trades support causal replay. Heikin-Ashi is a separate synthetic-price variant, not actual traded price.

Retain every sweep test, block geometry, scan limit, confirmation and invalidation rule under its own source identity. Log backdrawn origin versus first knowable time. Store code-versus-causal disagreements; do not silently repair bundled indicators or run them.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **completed-HTF**, **wick/body/close sweep**, **arithmetic/log midpoint**, **body-envelope/wick-envelope CISD**, **touch versus far-edge breach**, **time/trade/activity-bar scales**.
- **all-event lifecycle** removes display-history truncation only as a named variant.

## Phase 1 outcomes

Formation/confirmation coverage and delay, block revisit, penetration, invalidation, rejection/continuation path and all failure/timeout counts.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q19 resolves qualitative source block/CISD choices if an intended rule differs from literal code. Source-specific literal tests can be measured without merging them.

## Related

[swing rails protected extremes](swing-rails-protected-extremes.md), [fvg body gap structures](fvg-body-gap-structures.md), [extension projections](extension-projections.md)

Review findings: J-TBR-07, PINE-FRACTAL-01, PINE-FRACTAL-02, ZIP-10, ZIP-22, ZIP-23, ZIP-35, ZIP-51, ZIP-71. [Review ledger](../REVIEW_LEDGER.md).
