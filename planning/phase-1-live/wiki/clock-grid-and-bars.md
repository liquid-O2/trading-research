# Clock grid and bar types

## Definition
A fixed, pre-declared set of windows. Each window yields a box with the same internals as the 6–9 box (H, L, open, close, EQ, Q25, Q75, and the projection ladder on both sides in the box's own height: mean-reversal 0.1 / 0.2 / 0.3, ±0.5, ±1, the 1.33–1.66 area, ±2) and reports the same outcome table. The grid is regularized toward published clocks; no free-form morning box is searched `[BRIEF]`. The question Phase 1 answers is "which clock family wins by session, regime, and day class" as a measured table, not a deployed selector `[BRIEF]` `[JJX L157: derived ranges = a search over clocks, not a free-form box]`.

## Citations
- Jumbo published: 06:00–09:00 ONS `[TBR p.7 L111]`; Asia opening range 20:00–20:30, London opening range 03:00–03:30 `[TBR p.7 L108–110]`; London TBR = same internals with 03:00 and 06:00 lines `[FIND p.4–5 L86–95]`, "box into 03:00, same geometry" `[JJX L53]`; gold clocks GC 08:20, CL 09:00 `[XF p.8 L111–112]` (not run in Phase 1; NQ only).
- "Any window 5:00–9:00 behaves like 6–9" `[XF p.7 L93]` `[PACK L49]`; 9:40–9:50 is a sourced cluster, not the only window `[XF p.47 L624]` `[PACK L84]`; first ~20 minutes is where he prefers to finish `[XF p.15 L205]`; OR 5m/15m mid is reference only `[XF p.25 L317, p.15 L204]`; IB stats "never sustainable edge… curve fit" `[XF p.8 L106–107]`.
- Green Bird clocks: NYAM 09:00–10:00, outcomes only after 10:00 `[GB L28–30, L178]`; previous completed hour `[GB L32–33]`; Asia ≈ 20:00–00:00 (HIS CHART, inferred) `[GB L35–38, L46]`; London 02:00–05:00 (ICT clock, inferred; his levels) `[GB L48, L53–54]`; "9–11 AM EST best time" `[GB L49]` → the 10:00–11:00 hour box.
- User: derived ranges, adapt to regimes / assets / sessions `[DTM L19]` `[JJX L146–147]`.
- Pine tier-2 clock sources (grid candidates only, no stats trusted): DTT 13 named sessions `[PINE DTT Time Based Ranges.txt]`; 12-session variant `[PINE Time based ranges with stats.txt]`; Session Range Projections 02:00–02:15 / 09:00–09:15 / 13:00–13:15 `[PINE Session Range Projections with stats.txt]`; magic hours 07:00 / 08:00 / 06:00 / 00:00 / 01:00 / 02:00 / 23:00 with hardcoded win rates 82.8 / 80.6 / 77.7 / 77.1 / 73.6 / 71.2 / 68.5 `[PINE magic_hours:55–85]`; hourly sweep tables by NY hour `[PINE NQ Hourly Retracements 12y Stats with Levels.txt:185–313]`; 4H candles 18/22/02/06/10/14 `[PINE 4H HOD LOD Checkpoint Analysis.txt:49–61]`.

## Faithful object
`range.6-9.published` is the benchmark row. Grid rows (all NQ, all ET):

| id | window | note |
|---|---|---|
| `range.5-9` | 05:00–09:00 | 5–9 family `[XF p.7]` |
| `range.7-9` | 07:00–09:00 | 5–9 family |
| `range.8-9` | 08:00–09:00 | 5–9 family; 08:00 futures-open line `[GB L38 chart]` |
| `range.london.00-03` | 00:00–03:00 | box into 03:00 `[JJX L53]`, outcomes 03:00–06:00 |
| `range.london.0300-0330` | 03:00–03:30 | TBR London opening range `[TBR p.7 L110]` |
| `range.asia.2000-2030` | 20:00–20:30 | TBR Asia opening range `[TBR p.7 L108]` |
| `range.gb.asia` | 20:00–00:00 | GB inferred `[GB L38]` |
| `range.gb.london` | 02:00–05:00 | GB inferred `[GB L48]` |
| `range.gb.nyam` | 09:00–10:00 | GB HIS WORDS; outcomes 10:00–12:00 only `[GB L29]` |
| `range.gb.10-11` | 10:00–11:00 | GB hour after NYAM `[GB L49, L79]` |
| `range.gb.hour` | last completed 60 min at each 5-min step 09:30–12:00 | GB HIS WORDS `[GB L33]` |
| `range.or.5m` / `range.or.15m` | 09:30–09:35 / 09:30–09:45 | reference variant only (mid) `[XF p.25]` |
| `range.ib` | 09:30–10:30 | comparison row only; expected null `[XF p.8]` |

Reversal-time bins (for the 6–9 box outcomes): `bin.0940-0950`, `bin.0930-0950` (first 20 min), `bin.0950-1000`, `bin.1000-1030`, `bin.1030-1200`.

## Upgrades
- Bar type: `bars.time-1s` (default), `bars.vol-elapsed` (box closes after the 60-session median window volume), `bars.dollar` (notional), `bars.trade-count`, `bars.range40` (40-tick range bars — the bar type of the Sires execution charts, chart header "40 Range" `[NYAM p.4]` `[K18 p.7]` `[K2345 p.5]`, "the 40 range or 1 minute" `[CONT p.5]`; a named row for the Sires recipes, built from 1-second bars). Each clock row × bar type is a variant; rows whose coverage table cannot be told apart from another row are merged in the report (`[BRIEF]`: if two variants cannot be told apart by a coverage table, keep one).
- Regime slices as columns only: vol tercile from [vol-estimators](vol-estimators.md), day class from [range-path-class](range-path-class.md).

## Outcomes
- Same table as [tbr-6-9-range](tbr-6-9-range.md) for every row.
- Faithful disagreements = sessions whose path class under the row differs from `range.6-9.published`.
- Reversal-time bin shares per row; win-by-slice table (which clock has the highest reject-at-projection rate per regime × day class), reported, not deployed.

## Links
[tbr-6-9-range](tbr-6-9-range.md) · [session-fail-boxes](session-fail-boxes.md) · [sources-pine-archive](sources-pine-archive.md) · [vol-estimators](vol-estimators.md)
