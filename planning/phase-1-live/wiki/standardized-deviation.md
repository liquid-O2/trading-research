# Historical-average and standardized-deviation comparison

Object in [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md).

Stoic discusses position relative to historical averages and standard deviations as quantitative context. The exact series, history window and decision cutoffs are not disclosed. [DATA] p.5.

**Not a standalone trade.** An extreme standardized value is not itself the data-engine's entry rule or a replacement for C-score.

**Record before use.** Series/vintage, baseline window and its end, mean/deviation convention, value/as_of, transform if supplied and source interpretation.

**Phase 1 observation.** Freeze the comparison history before the evaluated observation. A conventional standardized deviation may be named explicitly, but cannot claim to reproduce an unpublished author score.

**Current implementation (2026-09-12).** [O160 contract](../FORMULAS.md#o160) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Compute selected prior-record mean, sample/population scale, raw deviation and standardized deviation with distinct series IDs, causal vintages and a zero-scale case. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/process_observations.py).

**Evidence limits.** The source baseline and variance convention must be observed; no fitted baseline search is performed. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Stoic's macro indicator set](macro-indicators.md) · [Economic observation and release vintage](economic-release-vintage.md) · [Stoic's custom C-score](c-score.md) · [Frozen observation cohort](research-cohort.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
