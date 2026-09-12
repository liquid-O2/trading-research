# Opening-range midpoint reference

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The July 21 raw post describes adapting with the 6–9 range and OR-mid retracements, taking nearer results and breakevens rather than assuming continuation. The OR is a separate source-selected reference. [JR] p.40, post 2079574963640512677; [TBR] pp.7, 24.

**Not a standalone trade.** OR midpoint is not 6–9 EQ or a standalone opening-range system. The source example does not disclose a universal OR duration for every chart.

**Record before use.** Source OR window and confidence, H/L, midpoint, formation end/known_at, later retrace, selected TBR branch and risk/target policy.

**Phase 1 observation.** Only use the completed selected OR. Do not infer its clock from the presence of a midpoint line or pick a later favorable opening interval.

**Current implementation (2026-09-12).** [O025 contract](../FORMULAS.md#o025) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure opening-range high, low, and midpoint from an identified native interval while keeping later midpoint retrace evidence distinct. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Opening-range clock must be identified; later retrace absence needs its own covered observation interval. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Other time-based range formations](tbr-remaining-clocks.md) · [Range EQ and quadrants](range-internals.md) · [Source-selected position management](position-management.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
