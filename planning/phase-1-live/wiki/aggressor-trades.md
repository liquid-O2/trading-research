# Executed aggressor-side trades

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

An executed trade identifies participation actually consuming liquidity; its aggressor side, size and price must be preserved. The sources compare effort with price response and distinguish executed orders from resting display. [DOM5] pp.3–7; [FP8] pp.3–7; [MATH] pp.4–8.

**Not a standalone trade.** A large buy print is not automatically bullish reward, absorption or an entry. Price upticks are not a substitute for known trade-side delta.

**Record before use.** Instrument/contract, event timestamp and ordinal, trade price/size, side and provenance, quote association and any unknown-side flag.

**Phase 1 observation.** Preserve unknown side rather than manufacturing it from price change. Keep NQ, MNQ and ES units separate; only trades available by the stage may contribute to its evidence.

**Existing attachments.** mbp1_extract; [mbp1_objects.cvd_from_trades/footprint_4x](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); [FORMULAS] P3-04/P3-08 and R-F02/F04/F06. Source-compatible event joins are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [BigTrades aggression markers](big-trades.md) · [Cumulative volume delta and its source reference](cvd-variants.md) · [DOM at a planned location](dom.md) · [Signed volume-by-price profile](weekly-delta-profile.md) · [Provide, withdraw and consume events](order-participation-events.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DOM5]: </workspace/sources/documents/discretionary/dom-lesson-5.pdf>
[FP8]: </workspace/sources/documents/discretionary/fp-lesson-8.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
