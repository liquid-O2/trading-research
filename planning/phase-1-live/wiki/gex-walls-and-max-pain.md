# Gamma call and put walls

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The gamma material marks call/put walls and also shows ranked wall references. Their native product, rank and position relative to spot must be preserved; the drawings do not reduce to one fixed wall on each side in every case. [GEX] pp.11–19.

**Not a standalone trade.** A wall touch is not a trade and a put-wall label is not universally identical to max pain.

**Record before use.** Source product/expiry, wall label/side/rank, native strike and any mapped price, snapshot and known_at, source algorithm or unknown flag.

**Phase 1 observation.** Use the source-selected wall set, then require local rejection/defense or aggressive break according to the branch. Do not substitute maximum OI for every wall definition.

**Existing attachments.** family_options/family_gex; [FORMULAS] R-R01/P3-05. Exact source wall ranking and positioning assumptions remain missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Source gamma regime](gex-regime.md) · [Native options-chain identity](options-nodes.md) · [Source max-pain reference](max-pain.md) · [DOM at a planned location](dom.md) · [Accepted break and defended boundary retest](break-retest.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
