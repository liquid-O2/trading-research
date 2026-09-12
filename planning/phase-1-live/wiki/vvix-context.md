# VVIX context

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

VVIX appears in the volatility lesson's broader read of changing volatility conditions. It modifies the context in which risk and expected movement are assessed. [VIX4] pp.6–9.

**Not a standalone trade.** The supplied material does not turn one VVIX value into a disclosed standalone entry algorithm.

**Record before use.** Source observation/time, unit, publication availability, relation to the chosen volatility read and uncertainty.

**Phase 1 observation.** Record the available value and source interpretation without inventing a universal threshold or borrowing a later observation.

**Current implementation (2026-09-12).** [O045 contract](../FORMULAS.md#o045) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Select the actual available VVIX vintage and retain context and interpretation with no backward use of later releases. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/context_observations.py).

**Evidence limits.** Missing availability and conflicting release ties remain data limitations. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [VIX and volatility context](vix-context.md) · [Volatility term structure and event change](volatility-curve.md) · [Exposure fitted to source risk constraints](position-sizing.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VIX4]: </workspace/sources/documents/discretionary/vix-lesson-4.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
