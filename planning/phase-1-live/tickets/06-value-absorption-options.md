# 06 — Value, absorption, BigTrades, footprint, VWAP

**Outcome.** RTH VP / value / delta / key zones / absorption / BigTrades / footprint / on-touch refill / VWAP ±2SD print grid outcomes on F. Options ids do not appear.

**Wiki.** `wiki/value-and-profiles.md`, `wiki/absorption-and-big-trades.md`.

**Definition → compute → pass.**
1. VP: `value.vp.rth.trade` 70% VA, plus 68 / 40, 4-tick bins, scope variants; `value.delta.rth.trade`; `value.kz` (HVN / two-sided LVN / ledge / naked POC); `env.vwap.rth.sd2`.
2. `flow.bigtrade.100ny` / `75ldn` / `30-60` / `q99`; `flow.absorption.A` and `flow.absorption.B` with location conditioning (extreme vs POC vs 6–9); overlap of BigTrades with absorption (must not be identical).
3. `flow.footprint.diag.4x` (and 3× / stack-2); `flow.refill.ontouch`. Off-touch refill stays `not-measurable`.
4. Pass command: `... run_phase1_objects.py report --family value --family flow`

**Acceptance criteria.**
- Grid outcomes at VAH / VAL / POC, key zones, absorption events, footprint zones, VWAP ±2SD, on-touch refill with `n` and intervals.
- No options / node / NDX / NDXP / SPX / SPXW / QQQ / SPY / NQ.OPT variant id in this ticket’s reports.
- Reject rate at extreme vs at POC printed for the absorption signature `[ABS p.6]`.
- `flow.refill.offtouch` printed `not-measurable`.

**Blocked by.** 03 (prior-RTH VP).
**Out of scope.** Options nodes (ticket 09); MBP-10 / MBO; iceberg detection; OFM sequence.
