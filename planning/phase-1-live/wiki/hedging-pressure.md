# Source hedging-pressure gauge

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The source panel includes a hedging-pressure gauge as part of its regime/location read. Its exact gauge formula, unit and thresholds are not disclosed. [GEX] pp.13–19.

**Not a standalone trade.** The gauge is not an automatic buy/sell rule and is not identical to a simple net-gamma sign.

**Record before use.** Source gauge label/value, native product, snapshot/known_at, interpretation actually given and unresolved algorithm.

**Phase 1 observation.** A chart annotation can preserve what was visible; an automatic equivalent is unknown. Do not infer the gauge's threshold from later price behavior.

**Existing attachments.** family_gex and [FORMULAS] R-R01 are related. The faithful source gauge is missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Source gamma regime](gex-regime.md) · [Source VOL-GEX readout](vol-gex.md) · [Source Vol Trigger readout](volatility-trigger.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
