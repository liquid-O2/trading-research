# Source-conditioned reference statistics

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The sources present path and landmark statistics with particular windows and conditions. MAMT explicitly says the 94% either-overnight-edge and 73% MPOC claims are context after HTF understanding, not an edge by themselves. Its appendix is a separately scoped historical ES sample. [MAMT] pp.15–26; [TBR] p.30; [JR] pp.48–49.

**Not a standalone trade.** Either is not both; a reference hit is not a method win. A printed percentage with an unresolved definition cannot justify an unconditional trade probability.

**Record before use.** Source claim, instrument, dates/sample_n, eligible condition, event definition, window, side, denominator and unresolved construction; later measurements stored separately.

**Phase 1 observation.** Compare like denominators only. Preserve source claims as claims until their event/cohort is reconstructable; do not transfer an ES appendix percentage to NQ or reinterpret an eventual range path as an opening signal.

**Current implementation (2026-09-12).** [O088 contract](../FORMULAS.md#o088) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Keep a literal source claim separate from a comparable observed cohort and report both/either hit counts and rates without relabeling them as trade win rate. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** Literal source percentages are not treated as measured trade performance and incomparable cohorts remain marked. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Retrospective range path](range-path-class.md) · [Opening location and participation](open-location-switch.md) · [Overnight high, low and width](overnight-range.md) · [MPOC: the profile midpoint](mpoc.md) · [Prior-session auction landmarks](prior-session-reference-levels.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
