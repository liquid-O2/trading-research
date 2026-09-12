# Bid-ask spread

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

The spread is part of the liquidity and execution context read with DOM and pace. Changes in displayed liquidity can alter the meaning and cost of the same aggressive print. [DOM5] pp.3–7; [MATH] pp.4–8.

**Not a standalone trade.** A narrow or wide spread is not a trade signal, and no universal source spread threshold admits every method.

**Record before use.** Bid/ask prices, instrument tick unit, spread_ticks, timestamp/ordinal, quote quality and local event window.

**Phase 1 observation.** Compute from contemporaneous quotes and preserve invalid/crossed/missing quotes. Do not use a session summary as the spread faced at entry.

**Current implementation (2026-09-12).** [O112 contract](../FORMULAS.md#o112) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Compute BBO spread in points and instrument ticks, retaining locked/crossed/stale state and rejecting crossed quotes. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [DOM at a planned location](dom.md) · [Provide, withdraw and consume events](order-participation-events.md) · [Refill-study fill assumption](fill-model.md) · [Trading and account costs](cost-model.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DOM5]: </workspace/sources/documents/discretionary/dom-lesson-5.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
