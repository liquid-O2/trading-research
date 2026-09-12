# Same-price 350% imbalance display

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The BigTrades charts show a 350% imbalance display and a small band around the associated candle/print area. It contributes evidence at a catalyst or defended level. [BIG] pp.3–5; [K2345] p.5.

**Not a standalone trade.** This is not the diagonal footprint ratio and is not an entry by itself. A large bubble sharing the line does not prove absorption.

**Record before use.** Instrument, native bar, side, same-price buy/sell values, stated percentage convention, source band and known_at.

**Phase 1 observation.** Retain the literal display and ratio ambiguity. Do not silently set one numeric ratio as author-exact or use the final candle band before it is known.

**Current implementation (2026-09-12).** [O110 contract](../FORMULAS.md#o110) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Disambiguate 350-percent-of from 350-percent-more and require an explicit zero-denominator rule. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Diagonal footprint imbalance stacks](footprint-imbalance-zones.md) · [BigTrades aggression markers](big-trades.md) · [Origin-of-the-Move catalyst](ofm-catalyst.md) · [Aggressive Origin of the Move](ofm-aggressive-branch.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[BIG]: </workspace/sources/documents/discretionary/only-trade-big-trades.pdf>
[K2345]: </workspace/sources/documents/discretionary/2345-funded-session.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
