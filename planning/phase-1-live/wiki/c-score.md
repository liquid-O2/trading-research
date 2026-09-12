# Stoic's custom C-score

Object in [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md).

The quantifying-fundamentals discussion names custom C-scores among its ways of turning context into comparable data, but supplies no complete formula. [DATA] p.5.

**Not a standalone trade.** A named score is not a disclosed trade trigger and must not be replaced silently by a generic z-score.

**Record before use.** Source metric name, intended variable/context, score if supplied, timestamp/vintage, source definition and missing-formula flag.

**Phase 1 observation.** A supplied source value can be retained with provenance. Otherwise exact scoring is unknown; do not invent weights, normalization or cutoffs.

**Current implementation (2026-09-12).** [O159 contract](../FORMULAS.md#o159) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Retain an attributed custom C-score, source unit and context and reject substitution of a z-score. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/process_observations.py).

**Evidence limits.** The custom score formula is undisclosed. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Stoic's macro indicator set](macro-indicators.md) · [Historical-average and standardized-deviation comparison](standardized-deviation.md) · [Stoic's trend-strength measure](trend-strength.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
