# 02 — Clock / bar / volume-window grid

**Outcome.** Every row of `wiki/clock-grid-and-bars.md` (5–9 family, London, Asia, GB clocks, OR / IB reference rows, reversal-time bins) and the bar-type variants of the 6–9 box print the same outcome table as the faithful row, with faithful disagreements counted against `range.6-9.published`.

**Wiki.** `wiki/clock-grid-and-bars.md`, `wiki/tbr-6-9-range.md`.

**Definition → compute → pass.**
1. Implement the fixed window list and bar types (`bars.time-1s`, `bars.vol-elapsed`, `bars.dollar`, `bars.trade-count`) as named variants; no free-form windows.
2. Compute each row on F; GB-NYAM outcomes start at 10:00; `range.gb.hour` steps every 5 minutes 09:30–12:00.
3. Merge rows whose coverage tables are indistinguishable (identical path-class and touch tables on F) and list merges.
4. Emit the win-by-slice table (reject-at-projection rate by vol tercile × day class) as a report table only.
5. Pass command: `... run_phase1_objects.py report --family range`

**Acceptance criteria.**
- One line per unmerged row with `faithful disagreements` = sessions whose path class differs from the 6–9 row.
- `range.ib` and `range.or.*` present with status from the pre-declared metric (expected `null`).
- Reversal-time bin shares printed for 6–9 (`bin.0940-0950` vs `bin.0930-0950` vs others).

**Blocked by.** 01.
**Out of scope.** Selecting or deploying a winning clock.
