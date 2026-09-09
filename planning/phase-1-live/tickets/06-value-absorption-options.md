# 06 — Value, absorption, BigTrades, options (four index products)

**Outcome.** Volume- and OI-derived location objects print grid outcomes on F. Options nodes are native on **NDX, NDXP, SPX, SPXW**. Objects we cannot compute print `not-measurable`.

**Wiki.** `wiki/value-and-profiles.md`, `wiki/absorption-and-big-trades.md`, `wiki/options-nodes.md`, `wiki/data-coverage.md`.

**Definition → compute → pass.**
1. VP: `value.vp.rth.trade` 70% VA, plus 68 / 40, 4-tick bins, scope variants; `value.delta.rth.trade`; `value.kz` (HVN / two-sided LVN / ledge / naked POC); `env.vwap.rth.sd2`.
2. `flow.bigtrade.100ny` / `75ldn` / `30-60` / `q99`; `flow.absorption.A` and `flow.absorption.B` with location conditioning (extreme vs POC vs 6–9); overlap of BigTrades with absorption (must not be identical).
3. `flow.footprint.diag.4x` (and 3× / stack-2); `flow.refill.ontouch`; `flow.ofm.sequence`. Off-touch refill stays `not-measurable`.
4. Nodes: `value.node.oi.{ndx,ndxp,spx,spxw}.top3` and gamma twins at 09:25. Each row: product, native, mapped_nq, map_known_at, OI_vintage. Variants: QQQ, SPY, NQ.OPT. Cash NDX/SPX minutes are not inputs.
5. Rows `flow.refill.offtouch`, `value.dealer.inventory`, `value.hidden.book`, `value.skylit.*` printed `not-measurable` / `deferred`.
6. Pass command: `... run_phase1_objects.py report --family value --family flow`

**Acceptance criteria.**
- Grid outcomes at VAH / VAL / POC, key zones, absorption events, footprint zones, node levels with `n` and intervals.
- Options report lists NDX, NDXP, SPX, SPXW as separate product rows; QQQ/SPY/NQ.OPT present as named variants; no row assumes cash-index minutes.
- Reject rate at extreme vs at POC printed for the absorption signature `[ABS p.6]`.
- The four not-measurable rows exist with that status.

**Blocked by.** 03 (prior-RTH VP).
**Out of scope.** MBP-10 / MBO; iceberg detection; Skylit.
