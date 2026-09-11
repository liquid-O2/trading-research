# POC relocation within a candle

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The footprint schematic moves POC within the evolving candle after the local absorption read. It is not simply comparing two different candles' POCs. [FP9] pp.4–7.

**Not a standalone trade.** A POC flip alone is not the complete footprint reaction; the valid level, candle/delta disagreement and selected local confirmation must also exist.

**Record before use.** Native candle_id, event-time volume-by-price snapshots, before/after POC, side/location within the candle, flip known_at and local confirmation.

**Phase 1 observation.** Require both POC observations to belong to the same candle and to be available before decision. Adjacent-candle POCs or a whole morning treated as one candle do not pass.

**Existing attachments.** [formulas_flow.r_f05_absorption_stack](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-F05. An event-time intrabar POC series and same-candle flip detector are missing or partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Source execution bars](execution-bars.md) · [Profile point of control](profile-poc.md) · [Candle direction versus executed delta](candle-delta-disagreement.md) · [Footprint-confirmed reaction](footprint-confirmed-reaction.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[FP9]: </workspace/sources/documents/discretionary/fp-lesson-9.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
