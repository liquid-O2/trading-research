# Market-structure shift after failure

Object in [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md).

A raw Green Bird chart labels the 9–10 high sweep/failed breakout, then MSS plus FVG for entry/risk, then opposing 9–10 lows. MSS is the selected execution refinement after the failure. [GB] p.43.

**Not a standalone trade.** MSS is not disclosed as a separate complete system here, and the chart does not make it compulsory in every Green Bird case.

**Record before use.** Source swing/boundary identities, when each was confirmed, failure event, structure-break/close observation, linked gap and decision time.

**Phase 1 observation.** Preserve the actual chart sequence: failure before structure confirmation before entry. Do not backdate a fractal pivot to its price bar before the confirming future bars exist.

**Current implementation (2026-09-12).** [O054 contract](../FORMULAS.md#o054) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Validate the ordered failure, confirmed swing, structural break, and entry sequence while preserving source break convention and episode identity. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Structural break convention and MSS label remain source inputs even when event order is measurable. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Sweep, failure and reclaim](sweep-reclaim.md) · [Fair-value gaps and higher-timeframe imbalances](fvg-body-gaps.md) · [Entry-side structural invalidation](structural-risk.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
