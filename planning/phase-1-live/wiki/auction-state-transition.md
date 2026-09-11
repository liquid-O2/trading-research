# Conditioned next-state transition

Object in [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

The framework considers the next auction state conditional on current liquidity and pace, distinguishing persistence from change. The 20,000-event AAPL example and its matrix illustrate the process; they are not universal NQ probabilities. [MATH] pp.9–11.

**Not a standalone trade.** A matrix cell or persistent absorption state is not an entry, and absorption must be reconsidered when replenishment fails.

**Record before use.** Current/next state IDs and times, native instrument/depth, conditioning variables available at the current state, cohort and transition count/denominator.

**Phase 1 observation.** Require state_at < next_state_at and conditioning known_at ≤ state_at. Keep source sample/depth and heuristic definitions attached; no new classifier, matrix or trading signal is trained here.

**Existing attachments.** No source-compatible state-transition/cohort implementation exists in [FORMULAS]. Generic rate tables do not reconstruct the state definitions. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [B–A–D–E–W auction-state alphabet](auction-state.md) · [Speed of tape](tape-speed.md) · [Executed passive replenishment](passive-replenishment.md) · [Frozen observation cohort](research-cohort.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
