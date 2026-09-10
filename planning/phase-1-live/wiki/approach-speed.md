# Approach speed (how price arrives at the extreme)

## Definition
The first read at an extreme is how price got there: an aggressive move, buyers pushing in hard and fast, signals that side wants higher prices and is likely to defend the balance; a slow, grinding move into the same extreme signals no real interest, which hands the opposition an opening `[WIC p.4]`. The refill research lists approach speed and delta into the touch among the flow features `[REF p.8]`; a move losing aggression candle by candle into resistance is the tell for a fade `[NYAM p.10]`. Id `flow.approach.speed`.

## Citations
- Aggressive vs slow arrival `[WIC p.4, p.11]`; flow-and-state features `[REF p.8]`; losing steam into resistance `[NYAM p.10]`; entering at the touch is early `[STOP p.7]`.

## Faithful object
`flow.approach.speed`: over the 5 minutes before first touch of a level: net displacement toward the level in ticks per minute (bars) and aggressive volume toward the level per minute (MBP-1) with its slope over the five 1-minute bins; class = aggressive if displacement ≥ q75 of the session's approach speeds so far and the volume slope ≥ 0, drift if ≤ q25 or the slope < 0. The bar-only row (displacement only) is named. `[unmeasured]` for the volume term.

## Upgrades
- Window 3 / 10 min; normalization by `vol.rv20` tercile; quantiles fixed on F.

## Outcomes
- Reject rate at the extreme by class (the WIC claim); break rate by class; interaction with `flow.absorption.A` at the touch.

## Links
[dealing-range](dealing-range.md) · [refill-zone](refill-zone.md) · [tape-speed](tape-speed.md) · [touch-reject-hold-break-grid](touch-reject-hold-break-grid.md)
