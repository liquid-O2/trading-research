# TPO poor high and poor low

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

A poor extreme indicates incomplete auction structure under the selected TPO reading and can remain an unfinished reference. It is distinct from an excess extreme. [TPO] pp.5–7; [MAMT] pp.18–20.

**Not a standalone trade.** A poor-high flag is not a short trigger, and a poor low is not a long trigger. A label does not guarantee repair.

**Record before use.** TPO profile/as_of, high/low side, extreme price and period membership, criterion, known_at and later repair event.

**Phase 1 observation.** Do not combine distinct poor readings into one always-true flag. Evaluate each extreme under the selected definition and preserve unknown coverage.

**Current implementation (2026-09-12).** [O081 contract](../FORMULAS.md#o081) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Evaluate poor-high/poor-low structure only under the instrument-specific adjacent-row criterion and compatible source grid. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** The one-row NQ criterion is instrument-specific; incompatible grids leave the label unknown. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Time-price-opportunity profile](tpo-ib-auction.md) · [TPO excess at auction extremes](excess.md) · [Remaining auction objectives](unfinished-business.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TPO]: </workspace/sources/documents/discretionary/tpo-lesson-3.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
