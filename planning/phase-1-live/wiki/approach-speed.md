# How price arrives at the area

Object in [Saint — AMT on live markets](method-saint-amt.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md).

Saint reads aggressive arrival versus drift and whether that effort produces acceptance or rejection at the HTF extreme. Sires also interprets pace at the planned reaction band. [WIC] pp.4–6; [AMTL] pp.5–10; [DOM5] pp.3–7. The Refill study separately lists approach speed among pre-touch flow/state features. [REF] p.8.

**Not a standalone trade.** Arrival style is context/control evidence, not an automatic direction or a complete entry.

**Record before use.** Premarked area, approach start/end, elapsed price path, executed participation/pace, side, source qualitative class and known_at.

**Phase 1 observation.** Keep approach observations before the test and interpret them with the subsequent local response. A qualitative source annotation may be retained; an exact automatic class remains unknown without a declared detector.

**Current implementation (2026-09-12).** [O113 contract](../FORMULAS.md#o113) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure pre-touch path, duration, net/path speed, and aggressive volumes; exclude post-touch events and keep arrival interpretation supplied. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Speed of tape](tape-speed.md) · [Trapped aggression at an auction extreme](trapped-buyers.md) · [Higher- and lower-timeframe control alignment](htf-ltf-alignment.md) · [Aggressive effort versus price-response efficiency](response-efficiency.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DOM5]: </workspace/sources/documents/discretionary/dom-lesson-5.pdf>
[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[AMTL]: </workspace/sources/documents/discretionary/amt-on-live-markets.pdf>
[WIC]: </workspace/sources/documents/discretionary/whos-in-control.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
