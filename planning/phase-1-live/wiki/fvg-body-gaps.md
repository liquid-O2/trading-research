# Fair-value gaps and higher-timeframe imbalances

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md).

Jumbo's PD RTH Range+ uses M15/H1 imbalance destinations; Green Bird's chart uses an FVG after a confirmed failure/MSS for execution. The gap's timeframe and role belong to the source case. [TBR] pp.32–35; [GB] p.43.

**Not a standalone trade.** A gap is an area or refinement, not an independent trade. A body-only gap or first-presented variant must not be borrowed from another source without evidence.

**Record before use.** Instrument, timeframe/bar kind, defining completed candles, source gap bounds, known_at, active/fill state and role as entry area or destination.

**Phase 1 observation.** The gap becomes known only after its defining confirmation. Keep wick-bound and body-bound constructions distinct if the source does not resolve them; implemented geometry alone does not establish the source's complete entry sequence.

**Current implementation (2026-09-12).** [O055 contract](../FORMULAS.md#o055) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Preserve an identified three-candle imbalance/FVG, active-state history, direction, and actual defining candle parent IDs; measure contact/fill separately. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Automatic gap discovery is not admitted from caller summaries; active/fill state needs complete defining candles and path evidence. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [PD RTH Range+ destinations](pd-rth-range-plus.md) · [Market-structure shift after failure](market-structure-shift.md) · [Remaining auction objectives](unfinished-business.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
