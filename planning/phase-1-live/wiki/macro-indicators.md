# Stoic's macro indicator set

Object in [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md).

The macro application identifies the cycle, examines leverage/credit/housing/valuation evidence, compares it with history and reaches a data-based verdict. These are examples inside the data-engine process, not a separate intraday model. [DATA] pp.5–6.

**Not a standalone trade.** One unusual series or the source's historical bubble conclusion is not a current trade instruction.

**Record before use.** Series identity, units/frequency, source vintage/release time, selected historical baseline, transformation and source question being tested.

**Phase 1 observation.** Use the series/vintages available by the historical decision and a previously declared comparison. Missing series or decision rules leave exact outputs unknown; no fresh macro verdict is inferred here.

**Current implementation (2026-09-12).** [O157 contract](../FORMULAS.md#o157) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Retain explicitly selected leverage/credit/housing/valuation series and causal vintages; preserve a supplied historical verdict without making a current classifier. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/process_observations.py).

**Evidence limits.** Macro collection is deferred and required source series definitions must be supplied. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Economic observation and release vintage](economic-release-vintage.md) · [Stoic's macro-cycle classification](macro-cycle.md) · [Stoic's custom C-score](c-score.md) · [Historical-average and standardized-deviation comparison](standardized-deviation.md) · [Stoic's trend-strength measure](trend-strength.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
