# Confirmed swing midpoint retrace

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The January 14 post describes clean retraces to each swing's midpoint on a trend toward the January 4 gap. It reports an observation, not a new exact swing-entry algorithm. [JR] p.51, post 2011483105089974551; [XF] p.26.

**Not a standalone trade.** A swing midpoint is not the 6–9 EQ, and no universal fractal length or trend-day detector is supplied.

**Record before use.** Source swing endpoints, their observation/confirmation times, mid=(high+low)/2, known_at, later contact and current directional context.

**Phase 1 observation.** Measure the retrace after the swing becomes known. Label any fractal detector as a named construction; a final trend-day label cannot select an earlier trade.

**Current implementation (2026-09-12).** [O026 contract](../FORMULAS.md#o026) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Compute a swing midpoint from two confirmed, identified endpoints and record a later midpoint contact without selecting pivots automatically. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Pivot endpoints and timeframe are selections, so midpoint arithmetic does not certify an automatic swing. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Range EQ and quadrants](range-internals.md) · [Fair-value gaps and higher-timeframe imbalances](fvg-body-gaps.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Retrospective range path](range-path-class.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[XF]: </workspace/sources/documents/jumbo/xfcmg2.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
