# New-week opening gap

Object in [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md).

NWOG is the area between the source's Friday-close and Sunday-open references. Green Bird uses it as a destination after an appropriate failure/reclaim, including the August 17 example. [GB] pp.35–39.

**Not a standalone trade.** The gap is an objective or confluence, not an entry at its edge. A chart's eventual gap fill is not evidence that it was the preplanned target.

**Record before use.** Source Friday-close convention, Sunday-open convention/time, endpoints, gap interval, known_at, target side and partial/full-fill observation.

**Phase 1 observation.** Do not silently replace Friday close with RTH close or settlement. Freeze the gap and chosen destination before entry; measure later contact/fill separately.

**Current implementation (2026-09-12).** [O051 contract](../FORMULAS.md#o051) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Construct a new-week gap from separate Friday-close and Sunday-open parents and distinguish contact from full fill. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Weekend conventions and objective-selection time are source policy; gap contact does not imply full fill. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Green Bird's midnight true-day open](true-day-open.md) · [Prior-session auction landmarks](prior-session-reference-levels.md) · [Remaining auction objectives](unfinished-business.md) · [Source-selected position management](position-management.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
