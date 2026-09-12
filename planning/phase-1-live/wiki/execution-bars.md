# Source execution bars

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — VWAP continuation](method-green-bird-vwap-continuation.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

Bar construction changes what a candle, print cluster and confirmation mean. Jumbo illustrates 2/3/5-minute block entries; Green Bird specifies completed five-minute closes in selected cases; Sires uses NQ 40-range charts in the BigTrades material. [TBR] pp.27–29; [GB] pp.25, 27; [BIG] pp.3–5.

**Not a standalone trade.** A range bar or short timeframe is a display/observation unit, not an entry model.

**Record before use.** Instrument, bar kind and size, source settings, open/close event keys, trade membership, volume and aggressor side, plus unresolved intrabar order.

**Phase 1 observation.** Do not turn a whole morning into one candle, compare adjacent-candle POCs as an intrabar flip, or silently replace a native range bar with a minute bar. Record any replacement as a named approximation.

**Current implementation (2026-09-12).** [O004 contract](../FORMULAS.md#o004) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Construct the exact ET-aligned time bar from all complete finer bars or identified events, retaining native instrument, original member IDs, OHLCV and latest availability. Missing members prevent completeness. Same-price boundary batches have exact OHLC; differing prices without verified sequence leave boundary order unknown. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/native_boundary.py).

**Evidence limits.** Native range bars require source-compatible membership and construction settings; unavailable settings remain holes. No row-count time bars or fabricated zero-activity OHLC. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source clocks and availability](clock-grid-and-bars.md) · [POC relocation within a candle](candle-poc-flip.md) · [Diagonal footprint imbalance stacks](footprint-imbalance-zones.md) · [BigTrades aggression markers](big-trades.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[BIG]: </workspace/sources/documents/discretionary/only-trade-big-trades.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
