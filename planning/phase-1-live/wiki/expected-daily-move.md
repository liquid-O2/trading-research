# Volatility-implied daily-move estimate

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The lesson figure displays expected daily move (%) = VIX / √252 and also discusses instrument-specific point-range examples. This is a volatility/range framing estimate used before deciding target ambition. [VIX4] pp.3–5.

**Not a standalone trade.** The estimate is not a guaranteed daily range, a confidence-certified target, or a standalone fade at completion.

**Record before use.** Index observation/time, percent-versus-point unit, conversion price/instrument if used, source calculation and known_at, elapsed realized movement.

**Phase 1 observation.** Keep the displayed formula separate from a fixed ES point-anchor table or an NQ estimate. Do not use later realized range to set the pre-entry expectation.

**Existing attachments.** family_vol; [formulas.vix_band](/workspace/implementation/src/trading_research/research/phase1_live/formulas.py); [FORMULAS] R-R02. Exact source example-to-instrument mapping and event-time update are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [VIX and volatility context](vix-context.md) · [Volatility term structure and event change](volatility-curve.md) · [Source-selected position management](position-management.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VIX4]: </workspace/sources/documents/discretionary/vix-lesson-4.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
