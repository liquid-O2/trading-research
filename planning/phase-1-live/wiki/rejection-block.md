# Jumbo rejection blocks

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The rejection block is the rejection wick used as a chosen reversal-entry area, distinct from the full-candle orderblock. It sits inside the context/location/confirmation loop. [TBR] pp.27–29.

**Not a standalone trade.** A wick alone is not a complete TBR entry, and a rejection-block boundary is not automatically an orderblock boundary.

**Record before use.** Source candle/timeframe, body and wick bounds, rejection side, complete-candle known_at, associated range location, entry and stop choice.

**Phase 1 observation.** Require the selected source rejection at the allowed location before entry. Preserve which block was actually used; do not merge the two to choose a better stop afterward.

**Existing attachments.** family_gap and [formulas_jumbo.j18_ob_bull/j18_ob_bear](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py) are related; [FORMULAS] R-J18. Distinct source rejection-wick execution is partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Jumbo orderblocks](sweep-cisd-blocks.md) · [Range exhaustion and mean-reversal area](range-exhaustion-area.md) · [Entry-side structural invalidation](structural-risk.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
