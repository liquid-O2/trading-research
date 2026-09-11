# Candle direction versus executed delta

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

A candle can move one way while executed aggression leans the other, revealing effort without proportional result at an appropriate location. The footprint lesson then looks for absorption, evolving POC and local confirmation. [FP9] pp.4–7; [RD] pp.3–8.

**Not a standalone trade.** Opposite candle and delta signs do not automatically identify a trade or a passive wall; location and the branch sequence still matter.

**Record before use.** Native candle_id and complete/as_of state, open/close and range, signed executed volume, price response, location and known_at.

**Phase 1 observation.** Keep the same candle and local area throughout. Do not use a final candle state before its observation time or infer executed delta solely from price movement.

**Existing attachments.** [formulas_flow.r_f05_absorption_stack](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); mbp1_objects footprint/delta ingredients; [FORMULAS] R-F05. Current whole-AM aggregation is not the native candle sequence. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [POC relocation within a candle](candle-poc-flip.md) · [Absorption: effort without price reward](absorption-and-big-trades.md) · [Footprint-confirmed reaction](footprint-confirmed-reaction.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[FP9]: </workspace/sources/documents/discretionary/fp-lesson-9.pdf>
[RD]: </workspace/sources/documents/discretionary/reading-delta.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
