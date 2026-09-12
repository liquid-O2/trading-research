# Executed aggressor-side trades

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

An executed trade identifies participation actually consuming liquidity; its aggressor side, size and price must be preserved. The sources compare effort with price response and distinguish executed orders from resting display. [DOM5] pp.3–7; [FP8] pp.3–7; [MATH] pp.4–8.

**Not a standalone trade.** A large buy print is not automatically bullish reward, absorption or an entry. Price upticks are not a substitute for known trade-side delta.

**Record before use.** Instrument/contract, event timestamp and ordinal, trade price/size, side and provenance, quote association and any unknown-side flag.

**Phase 1 observation.** Preserve unknown side rather than manufacturing it from price change. Keep NQ, MNQ and ES units separate; only trades available by the stage may contribute to its evidence.

**Current implementation (2026-09-12).** [O098 contract](../FORMULAS.md#o098) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Preserve each executed print, B/A/N aggressor volume, exact delta bounds, and timestamp-order quality without treating quotes as trades. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [BigTrades aggression markers](big-trades.md) · [Cumulative volume delta and its source reference](cvd-variants.md) · [DOM at a planned location](dom.md) · [Signed volume-by-price profile](weekly-delta-profile.md) · [Provide, withdraw and consume events](order-participation-events.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DOM5]: </workspace/sources/documents/discretionary/dom-lesson-5.pdf>
[FP8]: </workspace/sources/documents/discretionary/fp-lesson-8.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
