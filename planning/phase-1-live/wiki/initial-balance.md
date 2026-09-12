# Initial balance

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The initial balance is the early completed opening range used to read later range extension and day structure. Its eventual relationship to the whole day is descriptive context. [TPO] pp.3–9; [MAMT] pp.18–23.

**Not a standalone trade.** An IB statistic alone is not an entry edge or permission to trade before the initial interval has finished.

**Record before use.** Source session and initial interval, H/L/W, period membership, completion/known_at and later extension/return times.

**Phase 1 observation.** Use the source initial interval; distinguish its high/low from a prior day's IB. A final-day extension cannot label the initial opening decision.

**Current implementation (2026-09-12).** [O082 contract](../FORMULAS.md#o082) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Build initial balance only after complete A and B periods and keep later upper/lower extensions separate from IB geometry. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** Incomplete A/B periods cannot certify IB; later extensions do not revise IB bounds. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Time-price-opportunity profile](tpo-ib-auction.md) · [Developing auction day structure](day-type.md) · [Prior-session auction landmarks](prior-session-reference-levels.md) · [Source-conditioned reference statistics](reference-statistics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TPO]: </workspace/sources/documents/discretionary/tpo-lesson-3.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
