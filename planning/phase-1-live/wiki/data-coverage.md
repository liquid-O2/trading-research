# Data coverage

## Definition
The acquired datasets Phase 1 may touch, the frozen slice every comparison runs on, and the caveats that decide which object variants are computable. Dataset roots are `/workspace/data/<dataset ID>` `[INV L9]`. Acquired ≠ pull list `[README sources/documents/README.md L13]`.

## Citations
- NQ continuous front: MBP-1 2020-01-01 → 2026-09-03 (142 files, 11.5 B rows) `[INV L174–178]`; trades 2021-09-01 → 2026-09-02 `[INV L198–202]`; OHLCV-1m 2010-09-06 → 2026-09-02 `[INV L180–184]`; OHLCV-1s 2010-09-06 → 2026-09-02 `[INV L186–190]`; statistics `[INV L192]`; roll maps `[INV L743]`.
- ES continuous: MBP-1 2020-01-01 → **2024-08-30 only** `[INV L142–148]`; trades 2020 → 2026-09-03 `[INV L162–166]`; OHLCV-1m 2010 → 2026 `[INV L150–154]`.
- YM: OHLCV-1m 2010 → 2026 `[INV L235]`, trades 2020 → 2026 `[INV L247]`; RTY: OHLCV-1m 2017-07 → 2026 `[INV L211]`, trades 2020 → 2026 `[INV L223]`. No MBP-1 on YM/RTY.
- QQQ / SPY **1-minute** 2018-09 → 2026-09 `[INV L253, L259]`. NDX / SPX **cash minutes are not acquired**; cash index in inventory is daily. Do not invent NDX/SPX minute bars. Map option nodes with the product table on [options-nodes](options-nodes.md).
- Options: NQ.OPT and ES.OPT definition / OHLCV-1m / statistics / trades 2020-01 → 2026-09-01 `[INV L98–120, L38–60]`; ThetaData OPRA **NDX, NDXP, SPX, SPXW** contracts, EOD, open interest, quote-1m (dte ≤ 14 wide strikes; dte ≤ 60 ATM ±10), trade-quote dte ≤ 7 `[INV L297–380, L422–500]`; VIX options OI and quotes dte ≤ 60 full chain 2020-01-02 → 2026-09-03 `[INV L538–547]`.
- Volatility and calendars: Cboe VX futures normalized 2020-01-02 → 2026-09-03 `[INV L566–569]`; VVIX `[INV L559]`; FRED volatility indices `[INV L685]`; BLS release calendars 2021 → 2026-07 `[INV L552–555]`; FOMC/BoJ calendars `[INV L580]`; normalized event calendar `[INV L601–604]`; Nasdaq trading calendars 2020–2025 `[INV L699–702]`.
- Locked: MBP-1 only, no MBP-10, no MBO `[JJX L16, L146–157]` `[BRIEF]`. Execute NQ, ES is information `[BRIEF]`.

## Faithful object
- Frozen slice **F** = NY trade dates 2024-01-02 → 2026-08-31, all families, all variants. NQ MBP-1 and NQ trades both cover F.
- Long slice **L** = 2010-09-07 → 2026-08-31, OHLCV-1m only, used only to recompute published tables as a comparison row (his samples: 20 y / 4,537 days `[TBR p.30]`, 15 y `[XF p.47]`, n = 3,249 `[XF p.24]`).
- Session key = NY trade date; session spans 18:00 ET prior day → 17:00 ET; all clocks America/New_York; holidays and early closes from the trading calendar; a session is dropped when any window in the object is missing more than 10% of its expected 1-second bars.

## Upgrades
Named coverage variants:
- `cov.nq.mbp1` (trade events from MBP-1, 2020→) vs `cov.nq.trades` (trades schema, 2021-09→): the two must agree on aggressor side and size inside F; disagreement count is a report column.
- `cov.es.ohlc` only for cross-index work in F; ES trade-level objects are out of F for 2024-09 → 2026-08 and are marked `not-measurable` in F.

## Outcomes
- Per session: coverage flags per dataset (present / partial / missing), used as report columns, never as a filter beyond the 10% rule.

## Links
[touch-reject-hold-break-grid](touch-reject-hold-break-grid.md) · [smt-divergence](smt-divergence.md) · [options-nodes](options-nodes.md) · `../SPEC.md`
