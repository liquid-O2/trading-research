# Prior-session auction landmarks

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md).

Known prior highs/lows, opens/closes, IB references and profile landmarks supply context or destinations. MAMT's appendix describes separately conditioned reference-hit statistics; Jumbo and Green Bird choose the reference relevant to their case. [MAMT] pp.15–26; [TBR] pp.16–24, 32–35; [GB] pp.25, 30–39.

**Not a standalone trade.** A landmark hit rate is not the win rate of a trade targeting it. Close-based and range-edge-based gap references are different constructions.

**Record before use.** Reference kind, source period/window and date, exact price/band, known_at, open-condition cohort, and use as location or target.

**Phase 1 observation.** Keep RTH versus ETH, prior versus current, and high-low midpoint versus volume POC separate. The appendix's half-gap of pHOD/pLOD cannot be silently replaced by half the prior-close gap.

**Current implementation (2026-09-12).** [O086 contract](../FORMULAS.md#o086) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Bind a prior-session landmark by stable identity and compute half-range gap, half-close gap, and opening relation as distinct quantities. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** Half-range and half-close gaps are distinct; landmark kind/role must be supplied. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Prior day, week and month extremes](prior-day-week-month-levels.md) · [Initial balance](initial-balance.md) · [Profile point of control](profile-poc.md) · [MPOC: the profile midpoint](mpoc.md) · [Source-conditioned reference statistics](reference-statistics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
