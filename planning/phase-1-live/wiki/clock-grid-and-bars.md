# Source clocks and availability

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — VWAP continuation](method-green-bird-vwap-continuation.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md) · [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md) · [Stoic — asymmetric compounding](method-stoic-asymmetric-compounding.md).

The clock identifies what has finished before a decision. Jumbo's main range forms 06:00–09:00 ET; Green Bird's NYAM box forms 09:00–10:00; TPO and opening observations have their own completed periods. These clocks cannot be interchanged. [TBR] p.7; [GB] pp.23, 30–31; [AVG] pp.21–22.

**Not a standalone trade.** A scheduled minute does not create a trade. A 09:45 candidate cannot use the final 09:00–10:00 range.

**Record before use.** Source timezone and exchange date, start/end and boundary convention, bar start/close timestamps, completed-window known_at, and event ordinal for ties.

**Phase 1 observation.** Use America/New_York wall time with date-aware conversion where ET is specified. Preserve a chart's unresolved axis/timezone as unknown. Do not reset every instrument, VWAP or profile at one assumed cash-open clock.

**Existing attachments.** clocks.CLOCKS/clock_bounds; [family_clocks.build_clock_table](/workspace/implementation/src/trading_research/research/phase1_live/family_clocks.py); [FORMULAS] P3-01/P3-06. Exact London bounds and some modern source clock configurations remain unresolved. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Source execution bars](execution-bars.md) · [Jumbo's 06:00–09:00 range](tbr-6-9-range.md) · [Other time-based range formations](tbr-remaining-clocks.md) · [Green Bird's finished session references](session-fail-boxes.md) · [Time-price-opportunity profile](tpo-ib-auction.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
