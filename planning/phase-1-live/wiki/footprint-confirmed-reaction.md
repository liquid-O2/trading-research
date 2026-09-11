# Footprint-confirmed reaction

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The footprint lesson first locates the valid area, then reads candle/delta disagreement, local absorption, POC relocation within the candle and the selected DOM/delta confirmation. [FP9] pp.4–7.

**Not a standalone trade.** An intrabar POC flip or delta disagreement alone is not this branch; common thesis, auction, risk and objective gates still apply.

**Record before use.** Premarked level, native candle_id, disagreement/absorption observations, intrabar POC snapshots, flip_at, source flow confirmation and decision.

**Phase 1 observation.** Require level known ≤ absorption ≤ intrabar flip ≤ decision with the selected local flow read. Unavailable evolving candle data makes the faithful automatic check unknown.

**Existing attachments.** [formulas_flow.r_f05_absorption_stack](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-F05. Adjacent-candle POCs or an entire AM candle do not implement the source sequence. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Candle direction versus executed delta](candle-delta-disagreement.md) · [POC relocation within a candle](candle-poc-flip.md) · [DOM at a planned location](dom.md) · [Absorption: effort without price reward](absorption-and-big-trades.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[FP9]: </workspace/sources/documents/discretionary/fp-lesson-9.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
