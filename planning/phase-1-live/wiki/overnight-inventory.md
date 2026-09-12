# Overnight directional inventory

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Inventory describes the overnight auction's net directional positioning and location, then asks how RTH responds at its LVN/shelf. It changes expectations through the hold or aggressive break. [MAMT] p.14; [AMT1] pp.12–13.

**Not a standalone trade.** An inventory label is context, not a direction to trade regardless of the opening response.

**Record before use.** Overnight auction/profile scope, direction evidence, open location, shelf/LVN selected before RTH, known_at and subsequent response.

**Phase 1 observation.** Freeze inventory from overnight observations. Keep a later correction/continuation outcome separate from the initial label and from the source's either-edge statistic.

**Current implementation (2026-09-12).** [O074 contract](../FORMULAS.md#o074) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Preserve the source overnight inventory label and measured profile evidence; later opening response cannot rewrite the frozen inventory. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/profile_integration.py).

**Evidence limits.** Inventory direction is a source label; profile totals alone do not create an automatic classifier. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Overnight volume structure](overnight-profile.md) · [Overnight high, low and width](overnight-range.md) · [Developing auction open type](open-type.md) · [Source-conditioned reference statistics](reference-statistics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
