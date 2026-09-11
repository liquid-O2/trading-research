# Profile ledge

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

A ledge is the edge/cutoff of the relevant shelf or accepted volume area. Sires contrasts stable structural ledges with value-area lines that can change with calculation/settings. [VP2] pp.4–8; [MATH] p.13.

**Not a standalone trade.** A ledge is a location. Breaking it still requires the chosen acceptance/retest and flow sequence; it is not another system.

**Record before use.** Profile and shelf IDs, edge price/band, neighboring volume contrast, source scale, as_of and known_at.

**Phase 1 observation.** Check that the traded retest returns to the same previously broken ledge. Proximity to a final-profile boundary does not implement the sequence.

**Existing attachments.** [formulas_jumbo.profile_ledges](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [formulas_jumbo.a02_ledge_retest_hold](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [FORMULAS] R-A02/A16/A17 and P3-07. Exact source edge-selection thresholds are unpublished. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Profile shelf](profile-shelf.md) · [Accepted break and defended boundary retest](break-retest.md) · [Profile value area](value-area.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
