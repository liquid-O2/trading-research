# Higher- and lower-timeframe control alignment

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md).

The larger auction frames the direction/reaction and objective; the lower timeframe must show present control at the relevant area. Saint calls this the whole alignment method and waits through free two-sided chop. Sires's several confirmations can express one HTF thesis. [WIC] pp.7–10; [TRAP] pp.5–9; [CONT] pp.4–12; [K10] pp.5–8; [AVG] pp.21–22.

**Not a standalone trade.** HTF bias alone is not an entry, and an LTF print cannot erase an invalidated larger thesis. Sharing alignment does not merge these authors' methods.

**Record before use.** HTF thesis/balance_id and known_at, LTF structure and source timeframe, observed control side, test/retest, confirmation and decision keys.

**Phase 1 observation.** Confirm the current LTF side rather than reusing an earlier historical failure. A late supported flip can revise the read; it must be observed before the new decision.

**Current implementation (2026-09-12).** [O097 contract](../FORMULAS.md#o097) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Require a live higher-timeframe thesis and current lower-timeframe control on the same area; preserve both availability clocks and reject free two-sided chop. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** Alignment fails for dead thesis, opposite side, different area, stale/future control, or free two-sided chop. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Thesis, validity band and death condition](thesis-lifecycle.md) · [Auction balance](auction-balance.md) · [Accepted break and defended boundary retest](break-retest.md) · [Trapped aggression at an auction extreme](trapped-buyers.md) · [Source-selected dealing range](dealing-range.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[WIC]: </workspace/sources/documents/discretionary/whos-in-control.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[K10]: </workspace/sources/documents/discretionary/10k-first-month.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
