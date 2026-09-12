# Premium / discount within a selected range

Object in [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Premium and discount describe position within a declared price range or value context. Green Bird's smaller directional longs buy pullbacks into discount; Sires's sources also discuss auction/value location. These references require the particular source's range identity. [GB] pp.35, 40; [TPO] pp.4, 9; [VWAP] pp.3–6.

**Not a standalone trade.** Being below a midpoint is not a buy rule, and VWAP-relative discount is not necessarily the same object as a 50% high-low split.

**Record before use.** Parent impulse/range/profile, low/high or source value reference, midpoint when applicable, direction, known_at and current location.

**Phase 1 observation.** For a literal price-range split, midpoint=(H+L)/2. Retain the source's alternative value/VWAP meaning explicitly; never use a completed-day range to qualify an earlier pullback.

**Current implementation (2026-09-12).** [O053 contract](../FORMULAS.md#o053) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Compute midpoint, normalized location, premium/discount, and optional value relation from selected range, price, and value parents. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Location is geometric context only and does not create a directional recommendation. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Measured 50–61.8% retracement](golden-pocket.md) · [Source-selected dealing range](dealing-range.md) · [Profile value area](value-area.md) · [Session VWAP](vwap-session.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TPO]: </workspace/sources/documents/discretionary/tpo-lesson-3.pdf>
[VWAP]: </workspace/sources/documents/discretionary/vwap-lesson-10.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
