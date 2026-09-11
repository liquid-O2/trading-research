# Measured 50–61.8% retracement

Object in [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md).

Green Bird's golden pocket is the 50–61.8% retracement of the explicitly measured impulse. The September 1 illustration combines it with a PDL sweep and five-minute failure; the July example combines fib pullback and hourly-low reclaim. [GB] pp.25, 31–35.

**Not a standalone trade.** The band is entry location/confluence inside the failure method. A fib touch alone is not another system.

**Record before use.** Completed impulse ID, direction, H/L and known_at, measured retracement coordinates, later touch and associated sweep/reclaim event.

**Phase 1 observation.** For the illustrated down-impulse retracement the band is [L+0.50(H−L), L+0.618(H−L)]. Fix the impulse before the touch; do not choose it from a later favorable extreme.

**Existing attachments.** [formulas.gp_band_impulse](/workspace/implementation/src/trading_research/research/phase1_live/formulas.py); [FORMULAS] R-G05. The algebra exists, but the caller's 9–10 net-candle impulse is not necessarily the source's larger measured impulse. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Premium / discount within a selected range](premium-discount-50.md) · [Sweep, failure and reclaim](sweep-reclaim.md) · [Prior day, week and month extremes](prior-day-week-month-levels.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
