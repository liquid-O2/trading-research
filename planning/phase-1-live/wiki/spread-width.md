# Spread width

## Definition
The gap between best bid and best ask: one tick when liquidity is deep and healthy, widening the instant liquidity thins, which is the earliest warning that a level is about to break or a fast move is coming; when the spread widens, liquidity is pulling, do not lean on the level and do not chase into the gap `[DOM5 p.6]`. Id `flow.spread.width`. Depth beyond the touch is not measurable with MBP-1 ([data-coverage](data-coverage.md)); the spread and the sizes at the touch are.

## Citations
- Speed of tape and the spread; spread widens = liquidity pulling `[DOM5 p.6]`; the four ladder reads (depth, delta, speed, spread) `[DOM5 p.6]`.
- At-touch features (absorbed, reload, pull at the touch) as the MBP-1 substitute for depth reads `[JJX L334–340]` (assistant, tier 4).

## Faithful object
`flow.spread.width`: best ask − best bid in ticks from every MBP-1 BBO update; widening event = spread > 1 tick for ≥ 250 ms (named) inside the touch window of a level; companion: time-weighted mean spread over the 60 seconds before first touch and BBO displayed sizes at the touch. `[unmeasured]` tape object.

## Upgrades
- Duration 100 / 500 ms; threshold 2 ticks; BBO size drop (displayed size at the touch falling by ≥ 50% without prints) as a named pull-at-touch row.

## Outcomes
- Break rate given a widening at the touch vs none; widening before fast moves (≥ 0.25·R in 5 min) vs not; false-widening share.

## Links
[tape-speed](tape-speed.md) · [absorption-and-big-trades](absorption-and-big-trades.md) · [data-coverage](data-coverage.md)
