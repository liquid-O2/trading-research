# 01 — 6–9 box and path class

**Outcome.** One registered runner exists, the slice is frozen, the shared grid is implemented, and the faithful 6–9 object prints its PHASE line with a real report: internals, both width tables, path class, break order.

**Wiki.** `wiki/tbr-6-9-range.md`, `wiki/range-path-class.md`, `wiki/touch-reject-hold-break-grid.md`, `wiki/data-coverage.md`.

**Definition → compute → pass.**
1. Register `trading-research/tools/run_phase1_objects.py` (modes `check`, `run`, `report`) following `SPEC.md` §8; `check` validates F and L date lists against the trading calendar and the coverage rule and prints dropped sessions.
2. Build the per-session 1-second NQ table for F (and 1-minute for L) from the inventory datasets; retain per month.
3. Compute `range.6-9.published` (H/L, EQ, Q25/Q75, O/C, −0.5 / 1.0 / 1.33 / 1.66) and `path.6-9.published` (high-only / low-only / both / neither, break order, Judas / extended / purged with named thresholds).
4. Width tables, never mixed: XF p.24 price-% on `w.pct.0859close` and `w.pct.0930open`; `W69` and `WpriorRTH` in points; `w.rel-prior-rth` bins as a separate table.
5. Recompute TBR p.30 and p.12 inside 09:00–12:00; mid-retrace 60.4% `[XF p.23]`; reversal-time bins.
6. Pass command: `/tmp/trading-research-venv/bin/python trading-research/tools/run_phase1_objects.py report --family range --family path`

**Acceptance criteria.**
- Prints `range | range.6-9.published | n | 0 | measured | <path>` and `path | path.6-9.published | n | 0 | measured | <path>`; `n` equals the JSON.
- Both width tables present; ratio bins not labeled as XF p.24 %.
- Every quoted source cell has a recomputed cell with `n` and interval on F and on L.
- Sensitivity block present; dropped sessions listed.
- No file under the must-not-change list modified.

**Blocked by.** None.
**Out of scope.** Any other clock; predictions.
