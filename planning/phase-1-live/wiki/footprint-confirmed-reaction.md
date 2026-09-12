# Footprint-confirmed reaction

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The footprint lesson first locates the valid area, then reads candle/delta disagreement, local absorption, POC relocation within the candle and the selected DOM/delta confirmation. [FP9] pp.4–7.

**Not a standalone trade.** An intrabar POC flip or delta disagreement alone is not this branch; common thesis, auction, risk and objective gates still apply.

**Record before use.** Premarked level, native candle_id, disagreement/absorption observations, intrabar POC snapshots, flip_at, source flow confirmation and decision.

**Phase 1 observation.** Require level known ≤ absorption ≤ intrabar flip ≤ decision with the selected local flow read. Unavailable evolving candle data makes the faithful automatic check unknown.

**Current implementation (2026-09-12).** [O124 contract](../FORMULAS.md#o124) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Require delta disagreement, POC flip, absorption, and flow confirmation from one candle with ordered snapshot clocks. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/flow_sequences.py).

**Evidence limits.** Each required stage, side, parent band and source qualifier needs its own causal observation. Unpublished author classifications remain source limitations; a missing private stage or attempt record is not replaced by a supplied true flag. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Candle direction versus executed delta](candle-delta-disagreement.md) · [POC relocation within a candle](candle-poc-flip.md) · [DOM at a planned location](dom.md) · [Absorption: effort without price reward](absorption-and-big-trades.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[FP9]: </workspace/sources/documents/discretionary/fp-lesson-9.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
