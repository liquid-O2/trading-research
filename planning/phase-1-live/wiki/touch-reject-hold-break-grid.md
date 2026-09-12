# Touch, reject, hold and break measurements

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — VWAP continuation](method-green-bird-vwap-continuation.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md) · [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md) · [Stoic — asymmetric compounding](method-stoic-asymmetric-compounding.md).

The authors distinguish arrival, failure, acceptance and defended retest; their observation durations and confirmations differ. The common repository grid is a measurement convention for comparing those events, not a universal author rule. [TBR] pp.8–15, 27–29; [GB] pp.25, 27; [AMT1] pp.7–9.

**Not a standalone trade.** A touch or grid rejection cannot replace the method's context and complete confirmation. A profitability label cannot repair an absent prerequisite.

**Record before use.** Level/band identity, own range width, tolerance and units, source clock, ordered touch/break/close/retest times, measurement window and side.

**Phase 1 observation.** Freeze the level before use. A completed bar is known at its close; a same-bar sequence unresolved by OHLC stays unknown. Record target-first, invalidation-first and no-hit/censored outcomes after the decision, with full coverage.

**Current implementation (2026-09-12).** [O002 contract](../FORMULAS.md#o002) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure contact, overlap, strict break side, and sweep depth from native events/bars against an actual parent band; keep literal close return separate from audited source reject/hold labels. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Tape proves geometric overlap and literal closes; discretionary reject/hold meaning still requires an admitted source record. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Evidence and data coverage](data-coverage.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Sweep, failure and reclaim](sweep-reclaim.md) · [Accepted break and defended boundary retest](break-retest.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
