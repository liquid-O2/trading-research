# Stoic's printed asymmetric risk ladder

Object in [Stoic — asymmetric compounding](method-stoic-asymmetric-compounding.md).

The printed example risks one baseline unit for 3R, then after that win risks four units for 3R; after the second win it resets to one. The page heading instead says activation on a two-trade winning streak, so the discrepancy remains visible. [DATA] pp.7–8.

**Not a standalone trade.** This overlay consumes trades admitted by another validated process; it does not create entries or guarantee a favorable sequence.

**Record before use.** Fixed baseline/equity convention, base risk≤1%, stage, closed prior results, risk units, planned reward and next/reset state.

**Phase 1 observation.** Audit the printed ladder separately: first risk=1 / reward=3R; second only after +3 baseline units, risk=4 / reward=3R; second win adds12 and resets. The printed arithmetic is 3−4=−1 or 3+12=15. Other-outcome handling and general rebasing remain unspecified.

**Existing attachments.** No corresponding risk-state object exists in [FORMULAS] or current implementation. Generic return arithmetic is not the complete overlay. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Prior loss-streak validation for Stoic's overlay](loss-streak-validation.md) · [Exposure fitted to source risk constraints](position-sizing.md) · [Outcome distribution of a declared process](outcome-metrics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
