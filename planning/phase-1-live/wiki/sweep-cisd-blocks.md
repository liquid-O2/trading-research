# Jumbo orderblocks

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The manual's personal reversal entry choice uses a short-timeframe three-candle structure and the second candle's full range as the orderblock. Immediate versus retracement execution and risk choices are distinguished. [TBR] pp.27–29.

**Not a standalone trade.** The author expressly treats these as preferred entries, not a fixed universal component of every TBR trade. The orderblock is not the rejection wick.

**Record before use.** Source timeframe, three candle identities and closing times, C2 full high-low band, confirming event, entry choice, midpoint and actual stop geometry.

**Phase 1 observation.** Do not replace the full C2 range with a wick. Page 29's midpoint/conservative stop captions and drawings do not settle one universal stop rule; retain the fixture geometry and unresolved policy.

**Existing attachments.** [formulas_jumbo.j18_ob_bull/j18_ob_bear](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); family_gap; [FORMULAS] R-J18. Full source entry, timing and management linkage is partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Jumbo rejection blocks](rejection-block.md) · [Range exhaustion and mean-reversal area](range-exhaustion-area.md) · [Source execution bars](execution-bars.md) · [Entry-side structural invalidation](structural-risk.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
