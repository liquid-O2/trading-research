# Green Bird's finished session references

Object in [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — VWAP continuation](method-green-bird-vwap-continuation.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md).

NYAM is the completed 09:00–10:00 box; the previous-hour trade uses the completed hour. Asia is drawn approximately 20:00–00:00, while exact London bounds are not published. Those session highs/lows also frame the separately stated VWAP continuation. [GB] pp.23, 27, 30–35, 38–40.

**Not a standalone trade.** A box is a reference, not the failed-breakout system. A sweep while the box is still forming does not qualify as a sweep of its finished boundary.

**Record before use.** Source session and clock confidence, formation start/end, H/L, known_at, traded boundary, opposing boundary and contextual direction.

**Phase 1 observation.** Check formation before sweep or breakout. Preserve each hour as an episode; data coverage cannot be replaced by a hard-coded number of hours. The scalp posts do not acquire a trigger just because boxes are present.

**Current implementation (2026-09-12).** [O046 contract](../FORMULAS.md#o046) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Build a finished local/session box from complete contiguous members, with identified boundaries, measurable width, explicit clock verification, and coverage state. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** An unverified clock or incomplete member interval produces a hole even when observed extrema are measurable. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source clocks and availability](clock-grid-and-bars.md) · [Sweep, failure and reclaim](sweep-reclaim.md) · [Prior day, week and month extremes](prior-day-week-month-levels.md) · [Green Bird's midnight true-day open](true-day-open.md) · [Session VWAP](vwap-session.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
