# Measured 50–61.8% retracement

Object in [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md).

Green Bird's golden pocket is the 50–61.8% retracement of the explicitly measured impulse. The September 1 illustration combines it with a PDL sweep and five-minute failure; the July example combines fib pullback and hourly-low reclaim. [GB] pp.25, 31–35.

**Not a standalone trade.** The band is entry location/confluence inside the failure method. A fib touch alone is not another system.

**Record before use.** Completed impulse ID, direction, H/L and known_at, measured retracement coordinates, later touch and associated sweep/reclaim event.

**Phase 1 observation.** For the illustrated down-impulse retracement the band is [L+0.50(H−L), L+0.618(H−L)]. Fix the impulse before the touch; do not choose it from a later favorable extreme.

**Current implementation (2026-09-12).** [O052 contract](../FORMULAS.md#o052) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Project the directional 50-61.8 percent retracement band from one measured impulse with preserved failure linkage. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Impulse identity/direction are selected upstream; the band does not establish an entry or target. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Premium / discount within a selected range](premium-discount-50.md) · [Sweep, failure and reclaim](sweep-reclaim.md) · [Prior day, week and month extremes](prior-day-week-month-levels.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
