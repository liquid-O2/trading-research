# Profile ledge

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

A ledge is the edge/cutoff of the relevant shelf or accepted volume area. Sires contrasts stable structural ledges with value-area lines that can change with calculation/settings. [VP2] pp.4–8; [MATH] p.13.

**Not a standalone trade.** A ledge is a location. Breaking it still requires the chosen acceptance/retest and flow sequence; it is not another system.

**Record before use.** Profile and shelf IDs, edge price/band, neighboring volume contrast, source scale, as_of and known_at.

**Phase 1 observation.** Check that the traded retest returns to the same previously broken ledge. Proximity to a final-profile boundary does not implement the sequence.

**Current implementation (2026-09-12).** [O069 contract](../FORMULAS.md#o069) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Derive ledge and retest arithmetic only from selected parent objects; preserve stable lineage separately from equal price and deny late or unrelated retests. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/profile_integration.py).

**Evidence limits.** Same price alone cannot substitute for stable ledge identity across snapshots. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Profile shelf](profile-shelf.md) · [Accepted break and defended boundary retest](break-retest.md) · [Profile value area](value-area.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
