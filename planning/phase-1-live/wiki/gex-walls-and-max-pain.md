# Gamma call and put walls

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The gamma material marks call/put walls and also shows ranked wall references. Their native product, rank and position relative to spot must be preserved; the drawings do not reduce to one fixed wall on each side in every case. [GEX] pp.11–19.

**Not a standalone trade.** A wall touch is not a trade and a put-wall label is not universally identical to max pain.

**Record before use.** Source product/expiry, wall label/side/rank, native strike and any mapped price, snapshot and known_at, source algorithm or unknown flag.

**Phase 1 observation.** Use the source-selected wall set, then require local rejection/defense or aggressive break according to the branch. Do not substitute maximum OI for every wall definition.

**Current implementation (2026-09-12).** [O036 contract](../FORMULAS.md#o036) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Preserve every wall identity, dated price/band, units and selected wall; compute same-unit spot relations and prevent max-pain identity aliasing. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/context_observations.py).

**Evidence limits.** Wall generation requires the unpublished source engine or actual attributed readouts. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source gamma regime](gex-regime.md) · [Native options-chain identity](options-nodes.md) · [Source max-pain reference](max-pain.md) · [DOM at a planned location](dom.md) · [Accepted break and defended boundary retest](break-retest.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
