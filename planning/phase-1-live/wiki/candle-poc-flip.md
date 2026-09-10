# Candle POC and the POC flip

## Definition
Every candle has its own point of control, the price where the most volume traded; a POC flip is that busiest price jumping to the other side of the candle, control changing hands; at a key level a flip in your direction is confirmation the level is being defended `[FP9 p.5]`. The candle POC behaves like a magnet on the retest `[FP8 p.6]`. Ids `flow.candle.poc`, `flow.candle.poc.flip`. Jumbo's note that POC migrates by timeframe (on M2 the POC sits on the upper side) applies `[XF p.26]`.

## Citations
- POC flip definition and read `[FP9 p.5]`; stack: level, then absorption, then flip `[FP9 p.7]`; per-candle value area and POC, magnet on the retest `[FP8 p.6]`; timeframe dependence `[XF p.26]`.

## Faithful object
`flow.candle.poc`: per 1-minute NQ candle, the max-volume price from trades; position = (POC − low) / (high − low). `flow.candle.poc.flip`: consecutive candles at a level (within `tR`) whose POC position moves from the lower third to the upper third (bullish flip) or the reverse; `known_at` = second candle close. `[unmeasured]` tape objects.

## Upgrades
- Halves instead of thirds; 2 / 5-minute candles; flip within one candle's sub-bars (1-second) as a named row; combined with the candle-vs-delta disagreement from [absorption-and-big-trades](absorption-and-big-trades.md).

## Outcomes
- Defence rate (reject at the level) after a flip vs no flip; retest magnet rate of the prior candle's POC; per-session counts.

## Links
[absorption-and-big-trades](absorption-and-big-trades.md) · [footprint-imbalance-zones](footprint-imbalance-zones.md) · [value-and-profiles](value-and-profiles.md)
