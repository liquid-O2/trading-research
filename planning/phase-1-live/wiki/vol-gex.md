# Source VOL-GEX readout

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

VOL-GEX appears as a source gamma-panel readout; its exact construction is not published in the material. [GEX] pp.13–19.

**Not a standalone trade.** Its presence in the panel does not define a new method or justify substituting a generic volume-weighted gamma formula.

**Record before use.** Source panel/label, value/unit, native product/expiry, snapshot/known_at, source interpretation and missing-definition flag.

**Phase 1 observation.** Keep drawn evidence separate from computed approximations. Do not silently make an undefined readout a mandatory passing filter.

**Existing attachments.** family_gex and [FORMULAS] R-R01 provide related inputs. A source-compatible VOL-GEX object is missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Source gamma regime](gex-regime.md) · [Source Vol Trigger readout](volatility-trigger.md) · [Source hedging-pressure gauge](hedging-pressure.md) · [Native options-chain identity](options-nodes.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
