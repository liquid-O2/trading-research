# 02 — Clocks, bars, windows

**Outcome.** Every row of `wiki/clock-grid-and-bars.md` (5–9 family, Jumbo London TBR, Asia TBR, GB clocks, OR/IB reference rows, reversal-time bins) and the bar-type variants of the 6–9 box print the same outcome table as the faithful row.

**Wiki.** `wiki/clock-grid-and-bars.md`, `wiki/tbr-6-9-range.md`.

**Definition → compute → pass.**
1. Implement the fixed window list and bar types (`bars.time-1s`, `bars.vol-elapsed`, `bars.dollar`, `bars.trade-count`); no free-form windows.
2. Compute each row on F; GB-NYAM outcomes start at 10:00; `range.gb.hour` steps every 5 minutes 09:30–12:00.
3. Jumbo London `range.london.00-03` and `range.london.0300-0330` are separate from `range.gb.london` (inferred 02:00–05:00).
4. Merge rows whose coverage tables are indistinguishable; list merges.
5. Reversal-time bins: `bin.0940-0950` vs `bin.0930-0950` (first 20 min) vs later bins.
6. Pass command: `... run_phase1_objects.py report --family range`

**Acceptance criteria.**
- One line per unmerged row with `faithful disagreements` = sessions whose path class differs from the 6–9 row.
- Jumbo London and GB-London both present as distinct ids.
- `range.ib` and `range.or.*` present (expected `null` vs 6–9).
- Reversal-time bin shares printed for 6–9.

**Blocked by.** 01.
**Out of scope.** Selecting or deploying a winning clock.
