# Volatility-implied daily-move estimate

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The lesson figure displays expected daily move (%) = VIX / √252 and also discusses instrument-specific point-range examples. This is a volatility/range framing estimate used before deciding target ambition. [VIX4] pp.3–5.

**Not a standalone trade.** The estimate is not a guaranteed daily range, a confidence-certified target, or a standalone fade at completion.

**Record before use.** Index observation/time, percent-versus-point unit, conversion price/instrument if used, source calculation and known_at, elapsed realized movement.

**Phase 1 observation.** Keep the displayed formula separate from a fixed ES point-anchor table or an NQ estimate. Do not use later realized range to set the pre-entry expectation.

**Current implementation (2026-09-12).** [O043 contract](../FORMULAS.md#o043) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Calculate VIX daily percentage, fraction and optional points with the factor of 100 and explicit conversion instrument; propagate both input clocks. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/context_observations.py).

**Evidence limits.** A points estimate needs a contemporaneous instrument price and is not a must-travel price target. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [VIX and volatility context](vix-context.md) · [Volatility term structure and event change](volatility-curve.md) · [Source-selected position management](position-management.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VIX4]: </workspace/sources/documents/discretionary/vix-lesson-4.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
