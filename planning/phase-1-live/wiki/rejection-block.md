# Jumbo rejection blocks

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The rejection block is the rejection wick used as a chosen reversal-entry area, distinct from the full-candle orderblock. It sits inside the context/location/confirmation loop. [TBR] pp.27–29.

**Not a standalone trade.** A wick alone is not a complete TBR entry, and a rejection-block boundary is not automatically an orderblock boundary.

**Record before use.** Source candle/timeframe, body and wick bounds, rejection side, complete-candle known_at, associated range location, entry and stop choice.

**Phase 1 observation.** Require the selected source rejection at the allowed location before entry. Preserve which block was actually used; do not merge the two to choose a better stop afterward.

**Current implementation (2026-09-12).** [O057 contract](../FORMULAS.md#o057) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure body and rejection wick geometry from one actual complete candle while keeping rejection, location, entry, and stop permissions source-bound. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Wick geometry does not prove rejection quality or allowed location without admitted source evidence. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Jumbo orderblocks](sweep-cisd-blocks.md) · [Range exhaustion and mean-reversal area](range-exhaustion-area.md) · [Entry-side structural invalidation](structural-risk.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
