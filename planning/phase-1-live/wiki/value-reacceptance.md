# Re-acceptance into value

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md).

When price leaves or opens outside accepted value and then re-enters with acceptance, the directional read can rotate toward another part of that balance. Two-period-inside and general re-entry claims have separate definitions. [AMT1] p.7; [MAMT] pp.12, 18; [AMTL] pp.8–11.

**Not a standalone trade.** One wick inside value does not prove acceptance or an 80% traversal trade. A compiler's 30-minute hold is not a universal source rule.

**Record before use.** Original value/balance ID and bounds, opening/departure side, re-entry time, source acceptance criterion and known_at, selected target and local control.

**Phase 1 observation.** Require the actual original area and completed source acceptance before changing the trade read. Preserve different conditions and target denominators rather than pooling them into a single probability.

**Current implementation (2026-09-12).** [O092 contract](../FORMULAS.md#o092) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Require a return from outside and two consecutive complete whole-range-inside half-hours before certifying value re-acceptance. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** Point-in-band prints or incomplete periods cannot certify whole-range re-acceptance. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Profile value area](value-area.md) · [POC failure versus efficient passage](poc-traversal.md) · [Saint's failed auction and return to value](failed-auction-saint.md) · [Source-conditioned reference statistics](reference-statistics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[AMTL]: </workspace/sources/documents/discretionary/amt-on-live-markets.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
