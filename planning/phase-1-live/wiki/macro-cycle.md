# Stoic's macro-cycle classification

Object in [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md).

The macro example locates the current cycle before interpreting leverage, credit, housing and valuation against historical episodes. The source does not disclose a complete cycle-classification algorithm. [DATA] pp.5–6.

**Not a standalone trade.** A cycle label is not an entry or proof that a historical outcome must recur.

**Record before use.** Source cycle label, decision/as_of time, input series/vintages, source rationale and explicit unknown classifier/threshold fields.

**Phase 1 observation.** Retain the historical source conclusion as a case; automatic classification is unknown without supplied rules and vintage data.

**Current implementation (2026-09-12).** [O158 contract](../FORMULAS.md#o158) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Preserve the source cycle label, rationale and actual available input vintages instead of a majority-vote substitute. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/process_observations.py).

**Evidence limits.** Source cycle classification is unpublished and no new classifier is invented. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Stoic's macro indicator set](macro-indicators.md) · [Economic observation and release vintage](economic-release-vintage.md) · [Frozen observation cohort](research-cohort.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
