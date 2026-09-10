# Absorption candle (Jumbo Absorption Zone+)

## Definition
Jumbo's bar-level absorption object: a small-body candle with high volume at a key level, read as large players absorbing opposing pressure before a move `[TBR p.31]`; the indicator flags candles whose volume exceeds a "Volume Multiplier" times a 14-period volume average `[TBR p.35]`, colours them bullish / bearish, isolates them, and marks imbalances inside the absorption candle `[XF p.44]`, which he has used as the entry signal `[XF p.45]`. Id `flow.absorption.candle.jumbo`. It is a bar object, distinct from `flow.absorption.A` / `B` on [absorption-and-big-trades](absorption-and-big-trades.md) and from BigTrades bubbles `[XF p.25]`.

## Citations
- Concept and the small-body / high-volume signature `[TBR p.31]`; multiplier against a 14-period average, first-presented FVG display in the same settings `[TBR p.35]`; update: bull / bear colouring, isolation, absorption imbalances, MTF imbalance selection `[XF p.44]`; "used the imbalance in the absorption candle" `[XF p.45]`; absorption at the key levels of the 6–9 `[XF p.27]`; absorption zone at the reversal `[XF p.46]`; stack description `[FIND p.9, p.12]`.
- The multiplier value is not printed; the only sourced bar-volume multiplier in the files is 2.5 × a 20-bar average `[MVFL L40–41]`.

## Faithful object
`flow.absorption.candle.jumbo`: on 3-minute NQ bars (2 and 5 named `[TBR p.27]`), body / range ≤ 0.3 (named) and volume ≥ k × SMA14(volume), k ∈ {1.5, 2.0, 2.5} as named rows; located within `tR` of a 6–9 level; bullish / bearish by close vs open; isolation = no other flagged candle within 5 bars (named). Imbalance-inside-candle = a diagonal footprint imbalance (`flow.footprint.diag.4x`) inside that candle, a tape add.

## Upgrades
- Timeframe; body ratio; k; isolation window; at any level from the clock grid or `value.kz`.

## Outcomes
- Reject rate at a level given a flagged candle vs none; overlap with `flow.absorption.A` events (must not be identical); count per session.

## Links
[absorption-and-big-trades](absorption-and-big-trades.md) · [tbr-6-9-range](tbr-6-9-range.md) · [fvg-body-gaps](fvg-body-gaps.md) · [footprint-imbalance-zones](footprint-imbalance-zones.md)
