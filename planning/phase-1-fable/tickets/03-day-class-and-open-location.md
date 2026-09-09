# 03 — Day class + open-location switch

**Outcome.** Every F session carries the labels in `SPEC.md` §7 for path, day type, balance, clean edge and the 27-cell open location; the XF p.11 rows and the double-break expectancy split are recomputed.

**Wiki.** `wiki/range-path-class.md`, `wiki/open-location-switch.md`, `wiki/value-and-profiles.md` (prior-RTH VP only).

**Definition → compute → pass.**
1. Minimal prior-RTH value: `value.vp.rth.trade` (70% VA, 1-tick bins) and `value.vp.rth.ohlc1m`; PDH / PDL; 6–9 box from ticket 01.
2. Labels: `open_cell` (value × range × 6–9), `balance.body-ratio`, `balance.vp-shape`, `edge.clean` (Asia / London H/L untouched before 09:30), `day_type` (Judas / single-extended / single-purged / neither with named thresholds), `rvol_0930`.
3. Recompute XF p.11 rows ("below VAL, in range"; "below VAL & below PDL") on the 09:30–10:30 window and on 09:30–12:00; compute `open.dbx.in-value` vs `in-range-not-value` vs `outside-both`; `open.oneway.A` (the 76% claim) with RVOL 1.0 / 1.5.
4. Pass command: `... run_phase1_objects.py report --family path --family open`

**Acceptance criteria.**
- Label file has one row per F session, no nulls in the §7 label columns.
- 27 cells printed with `n` (sparse cells allowed), the two quoted rows beside recomputed values.
- `faithful disagreements` for `open.switch.published` under the OHLC-VP variant reported.

**Blocked by.** 01.
**Out of scope.** Training any predictor; Phase 2 context.
