# 01 — Runner + published 6–9 path report (tracer bullet)

**Outcome.** One registered runner exists, the slice is frozen, the shared grid is implemented, and the faithful 6–9 object prints its PHASE line with a real report behind it.

**Wiki.** `wiki/tbr-6-9-range.md`, `wiki/range-path-class.md`, `wiki/touch-reject-hold-break-grid.md`, `wiki/data-coverage.md`.

**Definition → compute → pass.**
1. Register `trading-research/tools/run_phase1_objects.py` (modes `check`, `run`, `report`) following `SPEC.md` §8; `check` validates F and L date lists against the trading calendar and the coverage rule and prints dropped sessions.
2. Build the per-session 1-second NQ table for F (and 1-minute for L) from the inventory datasets; retain per month.
3. Compute `range.6-9.published` (all internals and projections) and `path.6-9.published` (class, break order, day-type labels with named thresholds, width metrics) on F and L; implement `G-default` plus the sensitivity block.
4. Recompute: XF p.24 range-size table (same buckets, `w.pct.0859close` and `w.pct.0930open` rows), mid-retrace 60.4% `[XF p.23]`, TBR p.30 reversal-at-−0.5 rate and the TBR p.12 depth table inside 09:00–12:00, reversal-time bins.
5. Pass command: `/tmp/trading-research-venv/bin/python trading-research/tools/run_phase1_objects.py report --family range --family path`

**Acceptance criteria.**
- Prints `range | range.6-9.published | n | 0 | measured | <path>` and `path | path.6-9.published | n | 0 | measured | <path>`; `n` equals the count in the JSON.
- Report JSON validates against `SPEC.md` §3; every quoted source cell has a recomputed cell with `n` and interval on F and on L.
- Sensitivity block present; dropped sessions listed.
- No file under the must-not-change list modified.

**Blocked by.** None.
**Out of scope.** Any other clock; any upgrade row; predictions.
