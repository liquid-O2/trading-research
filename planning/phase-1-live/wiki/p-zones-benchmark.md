# Time-anchored P-zones

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The source shows P-zones with session anchors, learning-window/percentile controls and invalidation settings. The January low → range-open and December 10 am P-zone → London-low examples describe directed paths. [JR] pp.16–18, 53–55, 58–62.

**Not a standalone trade.** A settings panel does not disclose the proprietary formula. A time anchor does not prove an entry at that time; a path arrow is not a price inequality.

**Record before use.** Source band bounds and anchor, configuration/version, known_at, active/invalidated state, selected path and actual touch/confirmation times.

**Phase 1 observation.** A source-annotated zone may support a fixture. Automatic author-faithful qualification is unknown without the engine. Preserve time-specific reversal evidence instead of forcing every zone into 09:40–09:50.

**Current implementation (2026-09-12).** [O019 contract](../FORMULAS.md#o019) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Track an anchored P-zone through dated state and path events, separating active-at-use from the source zone label. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Zone bounds/anchor/state history must be supplied; no automatic P-zone detector is implemented. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source range-open and range-close references](range-open-close.md) · [Jumbo reversal and action windows](reversal-time-window.md) · [Remaining auction objectives](unfinished-business.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
