# Stoic's trend-strength measure

Object in [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md).

Trend strength is another quantified context item named in the data-engine macro discussion. The source supplies the question, not a complete detector. [DATA] p.5.

**Not a standalone trade.** The phrase does not authorize a particular moving-average, regression or momentum strategy.

**Record before use.** Source series/instrument, intended horizon, observations/vintages, supplied strength reading and unknown formula/threshold.

**Phase 1 observation.** Preserve a supplied source reading or leave exact computation unknown. Do not choose a detector after seeing the trend outcome.

**Current implementation (2026-09-12).** [O161 contract](../FORMULAS.md#o161) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Retain source strength, horizon and scale separately from an explicitly labeled regression slope. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/process_observations.py).

**Evidence limits.** The strength formula is unpublished. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Stoic's macro indicator set](macro-indicators.md) · [Historical-average and standardized-deviation comparison](standardized-deviation.md) · [Declared model and review version](model-definition.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
