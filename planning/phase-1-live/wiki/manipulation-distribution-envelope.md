# Manipulation / distribution envelope (Pine statistical OHLC projections)

## Definition
Levels projected from a session open using the average and median of two excursions measured on prior session candles: manipulation = the excursion from the open against the candle's eventual close direction (open − low on an up-close, high − open on a down-close), distribution = the excursion in the close direction (high − open on an up-close, open − low on a down-close) `[PINE Statistical OHLC Projections HTF.txt:322–326]`; averages, medians and 25 / 75 percentiles `[:141–158, 343–355]`; like-for-like slot filters in the sibling files ([sources-pine-archive](sources-pine-archive.md)). Ids `env.pine.manip.{avg,median,p25,p75}` (the distribution twin printed beside each). It is the AMD phase read as an envelope; the phase labels are on [amd-phase-labels](amd-phase-labels.md).

## Citations
- Manipulation wick length and distribution distance functions `[PINE Statistical OHLC Projections HTF.txt:322–326]`; max range from open, high / low range from open `[:328–341]`; percentile helper `[:141–158]`; drawn as manipulation high / low and distribution high / low, average and median `[:35–43]`.
- Siblings: `Daily statistical range and levels.txt`, `Statmap HTF no like for like lookback.txt`, `Session Based Statmap with closing stats.txt` (like-for-like slot filter) per [sources-pine-archive](sources-pine-archive.md).
- Jumbo frames 09:00–12:00 as a 3-hour PO3 candle `[TBR p.16, p.19]`.

## Faithful object
`env.pine.manip.avg`: over the prior 60 sessions, for the candle the file draws — the daily candle anchored at 18:00 by default, with 4H / 8H / 12H and the NY-midnight daily as its options `[PINE Statistical OHLC Projections HTF.txt:8–15]` (the RTH 09:30–16:00 candle is a named variant, not the default) — compute manipulation and distribution per the functions above over the last 60 same-slot candles; levels at that candle's open ± mean manipulation (both sides drawn) and ± mean distribution; `.median`, `.p25`, `.p75` likewise; `known_at` 09:30.

## Upgrades
- Candle = RTH 09:30–16:00 (named), 09:00–12:00 window (Jumbo PO3) or the 6–9 → 12:00 path; lookback 20 / 250; like-for-like filter by weekday.

## Outcomes
- Reach, overshoot, reject at each level; share of sessions whose adverse excursion stays inside the manipulation band (calibration); coincidence with −0.5 and EV bands (≤ `tR`).

## Links
[ev-range-expected-move](ev-range-expected-move.md) · [amd-phase-labels](amd-phase-labels.md) · [sources-pine-archive](sources-pine-archive.md)
