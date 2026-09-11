# KG1 retest and subsequent trailing

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The NYAM example uses a known KG1 level, an aggressive confirmed retest, entry and trailing convexity as the trade develops. [NYAM] pp.8–9.

**Not a standalone trade.** A scenario gamma wall is not necessarily KG1, and the displayed improvement in R:R is not a new entry method. The exact KG1 and trailing engine are not disclosed.

**Record before use.** Source KG1 level/version and known_at, retest/confirmation, initial ticket, later target/stop actions and their support.

**Phase 1 observation.** Check source level known ≤ retest ≤ aggressive confirmation ≤ decision. The figures show target expansion as well as trailing; do not attribute the entire 0.69→1.83 change to reduced initial risk.

**Existing attachments.** Generic gamma, level and refill ingredients attach; [FORMULAS] R-S01 and R-R01 are partial surroundings. The KG1 engine and full trailing-convexity algorithm are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Source KG1 level](kg1-level.md) · [Source-selected position management](position-management.md) · [Confirmed protected high or low](protected-high-low.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[NYAM]: </workspace/sources/documents/discretionary/ny-am-session.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
