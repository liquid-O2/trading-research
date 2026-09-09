# 03 — Day class and open-location switch

**Outcome.** Every F session carries path, day type, balance, clean edge and the 27-cell open location; XF p.11 and the in-value / in-range double-break split are recomputed; the 76% claim uses two denominators.

**Wiki.** `wiki/range-path-class.md`, `wiki/open-location-switch.md`, `wiki/value-and-profiles.md` (prior-RTH VP only).

**Definition → compute → pass.**
1. Prior-RTH value: `value.vp.rth.trade` (70% VA) and `value.vp.rth.ohlc1m`; PDH/PDL; 6–9 box from ticket 01.
2. Labels: `open_cell` (value × range × 6–9), `balance.body-ratio`, `balance.vp-shape`, `edge.clean`, `day_type` (Judas / single-extended / single-purged / neither), `rvol_0930`.
3. Recompute XF p.11 rows on 09:30–10:30 and 09:30–12:00; `open.dbx.in-value` vs `in-range-not-value` vs `outside-both`.
4. 76% claim as two rows: `open.oneway.A.0930-1000` and `open.oneway.OR.5m` / `15m` after the OR is known. Long example uses OR low; short/high is a named mirror.
5. Pass command: `... run_phase1_objects.py report --family path --family open`

**Acceptance criteria.**
- One row per F session, no nulls in SPEC §7 label columns used here.
- 27 cells printed with `n`; the two quoted XF p.11 rows beside recomputed values.
- A-period one-way and OR-edge return printed separately; they are not one number.
- `faithful disagreements` for the OHLC-VP variant of the switch reported.

**Blocked by.** 01.
**Out of scope.** Training any predictor.
