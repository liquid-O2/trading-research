# Delta spike at a value edge

## Definition
A single outsized delta print at an extreme, read as the moment control changed hands: at value area high a high delta spike of buyers marks the opposition losing control and being absorbed passively, at value area low the mirror; it is visible before the price reaction that follows `[ABS p.10–11]`. Related reads: the exhaustion print (a huge delta bar at the extreme with no extension) `[FP9 p.6]`, outsized delta prints at the highs as trapped buyers with the trigger below the print zone `[STOP p.9]`, and the highest delta print as the rewarded side `[RD p.6–7]`. Id `flow.delta.spike`.

## Citations
- Delta spike at VAH and VAL, same tell opposite direction `[ABS p.10–11, p.13]`; exhaustion print `[FP9 p.6]`; delta as a filter, print zones at the highs `[STOP p.9]`; delta print = highest point of the delta profile `[RD p.6–7]`.

## Faithful object
`flow.delta.spike`: per-price delta from trades aggregated per 1-minute bar; spike = |delta| ≥ q95 of that session's per-bar |delta| so far (q95, `tR`, the 2-tick advance and the 3-bar window are named; the source prints no numbers, only "a high Delta spike" `[ABS p.11]`), located within `tR` of a VAH / VAL (prior-day fixed by default) or of any level under test, with price advance beyond the level ≤ 2 ticks in the next 3 bars; side = sign. `[unmeasured]` tape object.

## Upgrades
- q90 / q99; per-price instead of per-bar; current-day VAH / VAL (lagging) as a named row; combined with the reward system on [reward-system-3tick](reward-system-3tick.md).

## Outcomes
- Reversal ≥ 0.25·R within 15 min after a spike at VAH / VAL vs at POC (the location claim); continuation after `b.c1` through the print zone (STOP); overlap with `flow.absorption.A` events.

## Links
[absorption-and-big-trades](absorption-and-big-trades.md) · [value-and-profiles](value-and-profiles.md) · [weekly-delta-profile](weekly-delta-profile.md) · [reward-system-3tick](reward-system-3tick.md)
