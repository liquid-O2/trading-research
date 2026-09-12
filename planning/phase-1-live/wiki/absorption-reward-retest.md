# Four-check absorption reversal

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The strict reversal starts at a fixed real extreme: opposing aggression is absorbed by a passive wall, the new side earns price reward near that origin, and price retests the rewarded area with renewed defense/aggression and supportive CVD. [ABS] pp.5–13.

**Not a standalone trade.** This source pattern is a fade/local reversal, not a continuation of the same push. The long-gamma failure fade is a different branch with no compulsory own-reward stage.

**Record before use.** Real extreme and known_at, local passive/effort evidence, reward side/time/distance, same-area retest/defense, CVD reference and decision.

**Phase 1 observation.** Require absorption < own reward < defended reward retest ≤ decision, all at the fixed source extreme. Moving today's value edge or picking the first AM print as origin does not pass.

**Current implementation (2026-09-12).** [O122 contract](../FORMULAS.md#o122) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Require the strict absorption-reward-return-renewed-defense sequence and independent CVD/delta filters. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/flow_sequences.py).

**Evidence limits.** Each required stage, side, parent band and source qualifier needs its own causal observation. Unpublished author classifications remain source limitations; a missing private stage or attempt record is not replaced by a supplied true flag. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Absorption: effort without price reward](absorption-and-big-trades.md) · [Price reward near the absorption origin](reward-system-3tick.md) · [Cumulative volume delta and its source reference](cvd-variants.md) · [Executed passive replenishment](passive-replenishment.md) · [Failure of aggression in long-gamma balance](balance-failure-fade.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[ABS]: </workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
