# Native options-chain identity

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The source gamma read uses the relevant native options complex, particularly QQQ/SPY 0DTE context for the Nasdaq/S&P application. Product, expiry and price units must remain attached to the resulting levels. [GEX] pp.4–19.

**Not a standalone trade.** An ETF strike, index strike and futures price are not interchangeable. A repository comparison chain is not a newly disclosed author method.

**Record before use.** Underlying/product, option class, expiry, strike, call/put, snapshot time, OI/volume/Greek provenance, native spot and any explicitly declared mapping.

**Phase 1 observation.** Preserve the source 0DTE cohort rather than silently pooling later expiries. Do not map strikes by an unstated ratio and then label the result author-exact; other native products are comparison variants unless source-bound.

**Current implementation (2026-09-12).** [O034 contract](../FORMULAS.md#o034) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Build a full dated option identity from product, class, expiry, strike, right and OSI key; calculate 0DTE from observation date and retain only a contemporaneous explicit mapping. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/context_observations.py).

**Evidence limits.** An absent contemporaneous index/option-to-futures mapping cannot be inferred from nearby price. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source gamma regime](gex-regime.md) · [Gamma-flip reference](gex-flip.md) · [Gamma call and put walls](gex-walls-and-max-pain.md) · [Source max-pain reference](max-pain.md) · [Source KG1 level](kg1-level.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
