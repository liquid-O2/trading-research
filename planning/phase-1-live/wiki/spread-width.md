# Bid-ask spread

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

The spread is part of the liquidity and execution context read with DOM and pace. Changes in displayed liquidity can alter the meaning and cost of the same aggressive print. [DOM5] pp.3–7; [MATH] pp.4–8.

**Not a standalone trade.** A narrow or wide spread is not a trade signal, and no universal source spread threshold admits every method.

**Record before use.** Bid/ask prices, instrument tick unit, spread_ticks, timestamp/ordinal, quote quality and local event window.

**Phase 1 observation.** Compute from contemporaneous quotes and preserve invalid/crossed/missing quotes. Do not use a session summary as the spread faced at entry.

**Existing attachments.** mbp1_extract and quote fields; [FORMULAS] P3-08. Source-specific quantitative spread filters and order-linked costs are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [DOM at a planned location](dom.md) · [Provide, withdraw and consume events](order-participation-events.md) · [Refill-study fill assumption](fill-model.md) · [Trading and account costs](cost-model.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DOM5]: </workspace/sources/documents/discretionary/dom-lesson-5.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
