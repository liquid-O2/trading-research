# Jumbo EVRange

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

EVRange is a separately named expected-range reference in the raw examples, used alongside the time-based range to frame rotations and targets. Its bands and midpoint are distinct from 6–9 EQ. [JR] pp.3, 38–43 and the late-August/early-September 2026 charts.

**Not a standalone trade.** EVRange does not define an independent entry, and a generic historical-average envelope is not automatically the author’s EVRange.

**Record before use.** Literal source band/midpoint labels, date, side, source value, anchor/time, available_at, version and whether the value is annotated or reconstructed.

**Phase 1 observation.** Check contact with an identified source band and the chosen TBR branch. Do not rename an inner profile box EV or substitute EV width for an unrelated range projection.

**Current implementation (2026-09-12).** [O018 contract](../FORMULAS.md#o018) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Carry a versioned, anchored EVRange observation and expose supplied midpoint geometry without auto-deriving unpublished bounds. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Unpublished EVRange construction is not reconstructed from midpoint or nearby price data. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Nested source range geometry](nested-range-geometry.md) · [Range EQ and quadrants](range-internals.md) · [SessionStat+ envelopes](sessionstat-9-12-envelope.md) · [Time-anchored P-zones](p-zones-benchmark.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
