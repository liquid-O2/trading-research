# Four-check absorption reversal

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The strict reversal starts at a fixed real extreme: opposing aggression is absorbed by a passive wall, the new side earns price reward near that origin, and price retests the rewarded area with renewed defense/aggression and supportive CVD. [ABS] pp.5–13.

**Not a standalone trade.** This source pattern is a fade/local reversal, not a continuation of the same push. The long-gamma failure fade is a different branch with no compulsory own-reward stage.

**Record before use.** Real extreme and known_at, local passive/effort evidence, reward side/time/distance, same-area retest/defense, CVD reference and decision.

**Phase 1 observation.** Require absorption < own reward < defended reward retest ≤ decision, all at the fixed source extreme. Moving today's value edge or picking the first AM print as origin does not pass.

**Existing attachments.** [formulas_flow.reward_3tick/r_f08_abs_four_check](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-F08 with F02/F06/F07. Source CVD reference, reward window and same-event stages remain incomplete. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Absorption: effort without price reward](absorption-and-big-trades.md) · [Price reward near the absorption origin](reward-system-3tick.md) · [Cumulative volume delta and its source reference](cvd-variants.md) · [Executed passive replenishment](passive-replenishment.md) · [Failure of aggression in long-gamma balance](balance-failure-fade.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[ABS]: </workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
