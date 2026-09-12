# Stoic's printed asymmetric risk ladder

Object in [Stoic — asymmetric compounding](method-stoic-asymmetric-compounding.md).

The printed example risks one baseline unit for 3R, then after that win risks four units for 3R; after the second win it resets to one. The page heading instead says activation on a two-trade winning streak, so the discrepancy remains visible. [DATA] pp.7–8.

**Not a standalone trade.** This overlay consumes trades admitted by another validated process; it does not create entries or guarantee a favorable sequence.

**Record before use.** Fixed baseline/equity convention, base risk≤1%, stage, closed prior results, risk units, planned reward and next/reset state.

**Phase 1 observation.** Audit the printed ladder separately: first risk=1 / reward=3R; second only after +3 baseline units, risk=4 / reward=3R; second win adds12 and resets. The printed arithmetic is 3−4=−1 or 3+12=15. Other-outcome handling and general rebasing remain unspecified.

**Current implementation (2026-09-12).** [O155 contract](../FORMULAS.md#o155) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Apply the documented STOIC stage ladder to fixed baseline equity/R units and dated prior results without retroactive activation. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py).

**Evidence limits.** Actual thesis, instruction, fill, management, account or state records are required for a historical instance. Scoped source policies and supplied interpretations cannot manufacture missing private records or a contemporaneous cohort. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Prior loss-streak validation for Stoic's overlay](loss-streak-validation.md) · [Exposure fitted to source risk constraints](position-sizing.md) · [Outcome distribution of a declared process](outcome-metrics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
