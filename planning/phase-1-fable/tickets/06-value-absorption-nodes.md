# 06 — Value areas, delta profile, key zones, absorption, BigTrades, options nodes

**Outcome.** All volume- and OI-derived location objects print grid outcomes on F; every object that needs data we do not have prints `not-measurable`.

**Wiki.** `wiki/value-and-profiles.md`, `wiki/absorption-and-big-trades.md`, `wiki/options-nodes.md`.

**Definition → compute → pass.**
1. Extend ticket 03's VP: VA 68 / 40, 4-tick bins, scope variants, `value.tpo`; `value.delta.rth.trade` with extremes and taper flag; `value.kz` (HVN / LVN / ledge thresholds).
2. `flow.bigtrade.100ny` / `75ldn` / `30-60` / `q99`; `flow.absorption.A` (effort / no-reward) and `flow.absorption.B` (BBO reload proxy) with location conditioning (extreme vs POC vs 6–9 edge / mid); overlap of BigTrades prints with absorption events.
3. `value.node.oi.top3` and `value.node.gamma.top3` (NDX + NDXP dte ≤ 14, mapped to NQ at 09:25), zero-gamma row; declared gamma weight table exported for ticket 05.
4. Rows `flow.refill.offtouch`, `value.dealer.inventory`, `value.hidden.book`, `value.skylit.*` printed `not-measurable` / `deferred`.
5. Pass command: `... run_phase1_objects.py report --family value --family flow`

**Acceptance criteria.**
- Grid outcomes at VAH / VAL / POC, key zones, absorption events, node levels with `n` and intervals.
- Reject rate at extreme vs at POC printed for the absorption signature (the coin-flip claim `[ABS p.6]`).
- The four not-measurable rows exist with that status.

**Blocked by.** 03.
**Out of scope.** MBP-10 / MBO; iceberg detection; Skylit.
