# Native options-chain identity

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The source gamma read uses the relevant native options complex, particularly QQQ/SPY 0DTE context for the Nasdaq/S&P application. Product, expiry and price units must remain attached to the resulting levels. [GEX] pp.4–19.

**Not a standalone trade.** An ETF strike, index strike and futures price are not interchangeable. A repository comparison chain is not a newly disclosed author method.

**Record before use.** Underlying/product, option class, expiry, strike, call/put, snapshot time, OI/volume/Greek provenance, native spot and any explicitly declared mapping.

**Phase 1 observation.** Preserve the source 0DTE cohort rather than silently pooling later expiries. Do not map strikes by an unstated ratio and then label the result author-exact; other native products are comparison variants unless source-bound.

**Existing attachments.** family_options and family_gex; [FORMULAS] R-R01/P3-05. Native ingredients exist; faithful dealer-position signs, complete source expiry selection and level mapping are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Source gamma regime](gex-regime.md) · [Gamma-flip reference](gex-flip.md) · [Gamma call and put walls](gex-walls-and-max-pain.md) · [Source max-pain reference](max-pain.md) · [Source KG1 level](kg1-level.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
