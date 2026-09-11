# Clean squeeze continuation

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

A fast release leaves the catalyst without the prior failed-squeeze sequence. On the first pullback, opposing aggression is absorbed and continuation confirms the thesis direction. [CONT] p.11; [OFM] p.5.

**Not a standalone trade.** A fast move alone is not entry, and no-failure refers only to history through the decision, not future survival.

**Record before use.** Known catalyst, release/pace, absence of earlier failure through decision, first pullback, opposing absorption and continuation confirmation.

**Phase 1 observation.** Require catalyst < release < first pullback ≤ confirmation ≤ decision. Do not replace the source first pullback with any later favorable retest or use a future 15-minute survival filter.

**Existing attachments.** [formulas_flow.r_f18_squeeze/tape_speed_pps](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-F18. The current helper can ignore supplied catalyst/release flags. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Origin-of-the-Move catalyst](ofm-catalyst.md) · [Speed of tape](tape-speed.md) · [Absorption: effort without price reward](absorption-and-big-trades.md) · [Fresh defense of a continuation band](defended-band-continuation.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[OFM]: </workspace/sources/documents/discretionary/origin-of-the-move.pdf>
[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
