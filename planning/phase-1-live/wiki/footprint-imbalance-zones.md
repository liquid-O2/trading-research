# Diagonal footprint imbalance stacks

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Keani — open above value](method-keani-open-above-value.md).

The lesson compares ask volume at a price with bid volume one tick below, and the sell-side diagonal in the opposite direction. Runs of about 3–4× with stacked rows are the illustrated evidence; the source also shows two-row versus three-row cases at a level. [FP8] pp.3–7. Keani returns to the actual aggressive-buying imbalance band. [AVG] pp.21–22.

**Not a standalone trade.** A stack is neither absorption nor a complete breakout method. A same-price 350% display is another construction.

**Record before use.** Candle/instrument/price step, diagonal side and ratio convention, per-row buy/sell volume, actual consecutive row band, known_at, departure and retest.

**Phase 1 observation.** Preserve zero-denominator handling and exact selected threshold/run length. The highlighted cells in the source do not consistently resolve every ratio detail; do not collapse gaps in price rows into one stack.

**Existing attachments.** [mbp1_objects.footprint_4x](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); [formulas_flow.r_f04_candle_stack/r_f04_revisit_hold](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-F04/R-S09. Native candle membership and defended revisit are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Same-price 350% imbalance display](same-price-imbalance.md) · [Source execution bars](execution-bars.md) · [Accepted break and defended boundary retest](break-retest.md) · [Executed aggressor-side trades](aggressor-trades.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[FP8]: </workspace/sources/documents/discretionary/fp-lesson-8.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
