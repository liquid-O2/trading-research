# POC relocation within a candle

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The footprint schematic moves POC within the evolving candle after the local absorption read. It is not simply comparing two different candles' POCs. [FP9] pp.4–7.

**Not a standalone trade.** A POC flip alone is not the complete footprint reaction; the valid level, candle/delta disagreement and selected local confirmation must also exist.

**Record before use.** Native candle_id, event-time volume-by-price snapshots, before/after POC, side/location within the candle, flip known_at and local confirmation.

**Phase 1 observation.** Require both POC observations to belong to the same candle and to be available before decision. Adjacent-candle POCs or a whole morning treated as one candle do not pass.

**Current implementation (2026-09-12).** [O108 contract](../FORMULAS.md#o108) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Compare at least two visible POC snapshots sharing one candle identity and reject cross-candle rewrites. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source execution bars](execution-bars.md) · [Profile point of control](profile-poc.md) · [Candle direction versus executed delta](candle-delta-disagreement.md) · [Footprint-confirmed reaction](footprint-confirmed-reaction.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[FP9]: </workspace/sources/documents/discretionary/fp-lesson-9.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
