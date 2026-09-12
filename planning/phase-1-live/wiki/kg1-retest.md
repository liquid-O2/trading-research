# KG1 retest and subsequent trailing

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The NYAM example uses a known KG1 level, an aggressive confirmed retest, entry and trailing convexity as the trade develops. [NYAM] pp.8–9.

**Not a standalone trade.** A scenario gamma wall is not necessarily KG1, and the displayed improvement in R:R is not a new entry method. The exact KG1 and trailing engine are not disclosed.

**Record before use.** Source KG1 level/version and known_at, retest/confirmation, initial ticket, later target/stop actions and their support.

**Phase 1 observation.** Check source level known ≤ retest ≤ aggressive confirmation ≤ decision. The figures show target expansion as well as trailing; do not attribute the entire 0.69→1.83 change to reduced initial risk.

**Current implementation (2026-09-12).** [O132 contract](../FORMULAS.md#o132) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Keep KG1 known before retest/confirmation, preserve original risk, and apply later management changes only after entry. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/flow_sequences.py).

**Evidence limits.** Each required stage, side, parent band and source qualifier needs its own causal observation. Unpublished author classifications remain source limitations; a missing private stage or attempt record is not replaced by a supplied true flag. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source KG1 level](kg1-level.md) · [Source-selected position management](position-management.md) · [Confirmed protected high or low](protected-high-low.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[NYAM]: </workspace/sources/documents/discretionary/ny-am-session.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
