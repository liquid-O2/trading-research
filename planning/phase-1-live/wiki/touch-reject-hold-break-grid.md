# Touch / reject / hold / break grid (shared)

## Definition
One named grid of event definitions used by every family, so rows are comparable and so a variant that only differs by tolerance is visible as such. Inputs: a level `L` (or box edge), a reference range `R` (default the object's own H−L; for single levels the 6–9 H−L), a window `W`, and NQ 1-second bars (`bars.time-1s`) or trades for tick precision.

- **touch**: price within `tol` of `L` inside `W`. `tol ∈ {t0: 0 ticks (trade prints at L), t2: 2 ticks, tR: 0.05·R}`.
- **break**: `b.wick`: excursion beyond `L` ≥ `d`, `d ∈ {2 ticks, 5 pts, 0.1·R}`; `b.c1`: 1-minute close beyond `L`; `b.c5`: 5-minute close beyond `L`.
- **reject**: after a touch (or a wick break), price returns ≥ `r·R` on the original side within `k` minutes without a `b.c1` break. `r ∈ {0.25, 0.5}`, `k ∈ {5, 15, 30}`.
- **hold**: after a `b.c1` break, all 1-minute closes stay beyond `L` for `h` minutes, `h ∈ {15, 30}`.
- **fail-back** (session-fail-boxes): a `b.wick` break followed by `b.c1` or `b.c5` close back inside within `k`.
- **time-to-touch**: minutes from window start to first touch; censored at window end.
- **reach / overshoot** (envelopes): reach = touch of either band; overshoot = max excursion beyond the band in band units.

Default set `G-default` = touch `t2`, break `b.c1`, reject `r=0.5, k=15`, hold `h=30`, fail-back `b.c5, k=30`. Sensitivity rows report the full grid.

## Citations
- Confirmation variants come from the sources, not invented: 5-minute close back through the level `[GB L89]`; reclaim = back through and hold `[GB L88]`; raid = ≥ 5 points beyond then close back inside within 120 minutes `[PINE Session Raid Stats.txt]`; HTF-candle sweep = wick beyond prior candle H/L and close back inside `[PINE HTF Sweep Model with CISD Table.txt:136–142]`; body-based close-back `[PINE HTF Sweeps & Liquidity Levels with CISD.txt:695–696]`; 3-strike failure at a level `[TBR p.37 L585]`; wick vs body rejection blocks `[TBR p.29 L443]`; "bodies tell the story, wicks do the damage" `[GB L158]` (label vocabulary only).
- User: touch/reject/hold/break = one shared named variant grid across families `[BRIEF]`.

## Faithful object
Each source's own confirmation is a named row: `grid.gb.c5` (5-minute close back), `grid.jumbo.projection-reject` (reject at −0.5 with `r=0.5`), `grid.pine.raid5-120` (5 pts, 120 min).

## Upgrades
None beyond the enumerated grid. Adding a cell requires a source citation or a QUESTIONS.md entry.

## Outcomes
- For every level row: touch rate, break rate (by variant), reject rate given touch, hold rate given break, fail-back rate given wick break, time-to-touch distribution (p25 / p50 / p75).
- Grid sensitivity: for each family, the count of sessions whose `G-default` label flips under any other cell = a report column.

## Links
[session-fail-boxes](session-fail-boxes.md) · [tbr-6-9-range](tbr-6-9-range.md) · [ev-range-expected-move](ev-range-expected-move.md) · `../SPEC.md`
