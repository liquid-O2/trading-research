# Accepted break and defended boundary retest

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Keani — open above value](method-keani-open-above-value.md).

The auction leaves balance or a ledge with participation and acceptance, then returns to that same broken boundary. Defense and renewed initiative can confirm continuation. Saint additionally requires the lower-timeframe control to agree with his HTF read; Keani's own retest is of the buying-imbalance band after the VAH break. [AMT1] pp.8–9; [MAMT] p.12; [WIC] pp.7–10; [TRAP] pp.6–9; [AVG] pp.21–22.

**Not a standalone trade.** A break, retest and confirmation from unrelated times or boundaries do not compose a trade. Do not make every source use the same hold duration.

**Record before use.** Balance/ledge and retest-band IDs, side, known_at, breakout/acceptance, departure, retest, local defense and decision times.

**Phase 1 observation.** Require known boundary < breakout < retest ≤ confirmation ≤ decision. The selected parent's thesis, regime, risk and objective gates still apply; a missed retest is not permission to chase.

**Current implementation (2026-09-12).** [O091 contract](../FORMULAS.md#o091) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Require break, acceptance, departure, same-boundary retest, defense, and initiative in order, with source-held retest and stable boundary identity. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** Different-boundary retests or initiative before defense invalidate the sequence; source-held meaning stays source-bound. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Profile ledge](profile-ledge.md) · [Auction balance](auction-balance.md) · [Higher- and lower-timeframe control alignment](htf-ltf-alignment.md) · [Diagonal footprint imbalance stacks](footprint-imbalance-zones.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[WIC]: </workspace/sources/documents/discretionary/whos-in-control.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
