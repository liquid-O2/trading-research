# TPO single-print structure

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Single prints are interior thin time structure left by directional movement between accepted areas. Their location can remain a future auction reference. [TPO] pp.5–7; [MAMT] pp.18–20.

**Not a standalone trade.** An outer excess tail or any price with one observed trade is not automatically an interior single-print zone or a trade.

**Record before use.** TPO profile and letter identities, interior band bounds, surrounding distributions, formation/known_at and later repair/visit history.

**Phase 1 observation.** Exclude merely outer tails from an interior-single-print definition. Never fabricate the band from an unrelated fixed-price offset or use final-day membership before it is known.

**Current implementation (2026-09-12).** [O079 contract](../FORMULAS.md#o079) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Find source-selected interior single-print rows and evaluate later repair without treating outer tails as single prints. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** Interior band and repair convention are source selections; outer tails are excluded by contract. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Time-price-opportunity profile](tpo-ib-auction.md) · [TPO excess at auction extremes](excess.md) · [Remaining auction objectives](unfinished-business.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TPO]: </workspace/sources/documents/discretionary/tpo-lesson-3.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
