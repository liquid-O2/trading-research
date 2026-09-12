# Prior day, week and month extremes

Object in [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

Green Bird uses prior-day levels, the previous weekly candle's extremes and previous-month extremes as sweep/reclaim references or objectives. Jumbo's liquidity maps retain named prior-day highs/lows with a configurable lookback. [GB] pp.25, 31–35; [JR] pp.16–18, 33–39.

**Not a standalone trade.** A prior extreme supplies location or bias; it is not automatically the 9–10 range trade, and prior RTH is not a substitute for every PDH/PDL label.

**Record before use.** Period kind, full-session versus RTH scope, source calendar/week convention, high/low, period end/known_at, active state and reference_id.

**Phase 1 observation.** Identify the exact prior period from the source. The reclaim may establish bias for a later aligned pullback, but the bias must exist before that entry; a later sweep cannot explain an earlier trade.

**Current implementation (2026-09-12).** [O048 contract](../FORMULAS.md#o048) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure prior-period high/low from native members and preserve period identity, scope, end, active state, and retirement policy. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Native extrema do not by themselves determine source retirement policy or active state. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Prior-session auction landmarks](prior-session-reference-levels.md) · [Chronological liquidity purges](overnight-purge.md) · [Remaining auction objectives](unfinished-business.md) · [Sweep, failure and reclaim](sweep-reclaim.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
