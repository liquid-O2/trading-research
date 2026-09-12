# The 1.33–1.66 extension area

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

Jumbo reads the extended area on either side after expansion and looks for reaction plus a still-relevant destination. The September 9 long combines session-average lows, the extension area and equal highs as its objective. [TBR] pp.20–21; [JR] pp.23–26, 57, 71.

**Not a standalone trade.** Touching an extension, making a daily extreme there and entering a confirmed reversal are separate events. The band is not a P-zone.

**Record before use.** Source parent range/inner span, W, side, coordinates, source label, formation time, touch/reaction times and preselected objective.

**Phase 1 observation.** For an identified beyond-edge ladder use H+kW or L−kW, k=1.33/1.66. Preserve the source's coordinate/anchor convention; do not project every chart with outer 6–9 or EV width.

**Current implementation (2026-09-12).** [O015 contract](../FORMULAS.md#o015) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Project the 1.33-1.66 extension bands from the same selected parent width and reject width substitution. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Projection is arithmetic and does not prove a trade setup or select which range should control. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Nested source range geometry](nested-range-geometry.md) · [Range exhaustion and mean-reversal area](range-exhaustion-area.md) · [SessionStat+ envelopes](sessionstat-9-12-envelope.md) · [Remaining auction objectives](unfinished-business.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
