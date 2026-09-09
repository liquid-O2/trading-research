# Options nodes (four index products, native then mapped)

## Definition
Strike-level open interest and scenario-gamma nodes from **NDX, NDXP, SPX, SPXW**, plus named variants **QQQ, SPY, NQ.OPT**. Each product keeps a native strike/price. Mapping onto NQ is a separate field with its own known-at. Cash NDX/SPX **minutes are not assumed** `[INV L249–263]` `[A wiki/cross-market-price-mapping.md]`. Hidden book, dealer inventory, and unpublished node engines are not measurable `[DRFL L207–224]` `[README sources/documents/README.md L27–30]`.

This page must not collapse to QQQ/SPY.

## Citations
- Dealer hedging, long/short gamma, gamma flip, GEX as regime filter, strikes as where gamma lives `[GEX p.2 L17–39, p.5 L90–94]`; QQQ / SPY as *origin complexes*, not the only underlyings `[GEX p.4 L77]`.
- Native SPX node screenshot (0DTE colored nodes, strength, persistence) `[reference-images/zerano-charts-SPX-2026-08-24T18-51-29-251Z.webp]`. No formula in the image → disclosed peak construction, not a reconstructed engine `[Q23]`.
- Theta OPRA: NDX contracts/EOD/OI from 2016, NDXP from 2018, SPX/SPXW from 2016; quote-1m dte ≤ 14 wide strikes / dte ≤ 60 ATM ±10; trade-quote dte ≤ 7 `[INV L297–380, L422–500]`.
- CME NQ.OPT definition / OHLCV-1m / statistics / trades 2020-01 → 2026-09 `[INV L98–120]`.
- QQQ / SPY 1-minute from 2018-09 `[INV L253–263]`. NDX/SPX cash in inventory is **daily**, not minute `[INV]` (A inventory page).
- User: levels from gamma / OI heat maps, multi-asset `[DTM L22, L24]`.

## Product table (every node row)

| product | native | mapped_nq | map_known_at | OI_vintage |
|---|---|---|---|---|
| NDX | Theta OPRA NDX strike in NDX points | `nq = ndx * ratio(NQ, NDX)` at snapshot | timestamp of the NQ and NDX prints used for the ratio; missing print → `unavailable` | Theta `open_interest` as-of that exchange date (EOD vintage); delayed OI is a named lag proxy |
| NDXP | Theta OPRA NDXP strike in NDX points (weekly) | same ratio as NDX, tagged `product=NDXP` | same | same, NDXP file vintage |
| SPX | Theta OPRA SPX strike in SPX points | `nq = spx * ratio(NQ, SPX)` **or** two-step SPX→ES→NQ; both named | timestamp of each leg; cash SPX **daily close is not an intraday map** | Theta SPX OI as-of date |
| SPXW | Theta OPRA SPXW strike in SPX points (weekly) | same as SPX, tagged `product=SPXW` | same | same, SPXW file vintage |
| QQQ | named variant; ETF 1-minute native | `nq = qqq * ratio(NQ, QQQ)` | snapshot of NQ and QQQ 1m | Theta/OPRA QQQ OI as-of date |
| SPY | named variant; ETF 1-minute native | `nq = spy * ratio(NQ, SPY)` | snapshot of NQ and SPY 1m | Theta/OPRA SPY OI as-of date |
| NQ.OPT | CME NQ futures-option strike, **already NQ** | `mapped_nq = native` | contract known_at | CME statistics OI as-of; no option MBP-1 acquired |

`ratio(A,B)` default = prior-session median of last available contemporaneous prints; additive basis is a named upgrade. Native events and mapped-NQ events are counted separately. A missing ratio does not borrow a later print.

## Faithful object
- `value.node.oi.ndx.top3` / `value.node.oi.ndxp.top3` / `value.node.oi.spx.top3` / `value.node.oi.spxw.top3`: at 09:25 ET (or first valid quote after), top 3 OI strikes above and below native spot, dte ≤ 14, from that product’s chain. Emit native strike, mapped NQ, `map_known_at`, `OI_vintage`.
- Combined display row `value.node.oi.top3.index` = union of the four index products, identities preserved.

## Upgrades
- `value.node.gamma.<product>.top3`: |gamma × OI| from reconstructed Greeks; dte ≤ 7 vs ≤ 14.
- `value.node.oi.qqq.top3`, `value.node.oi.spy.top3`, `value.node.oi.nqopt.top3`.
- Zero-gamma flip per product (aggregate exposure root under a named sign scenario, not a per-strike sign change).
- Map variants: rolling-median ratio vs additive basis; 09:25 vs 16:00 prior close.
- OI vintage: last available EOD vs one-session lag proxy (labeled). Missing release time stays unavailable.
- Node geometry: 1/3/5-strike smoothing, top1/top5/all local peaks, one-strike-neighbor vs half-height bounds `[Q23]`.
- `not-measurable`: dealer inventory, hidden book, Skylit Heatseeker / Flowseeker / Atlas.

## Outcomes
- Shared grid at each native level and at each mapped-NQ level (disagreement is a column).
- Distance from AM extreme to nearest node, ranked against EV, −0.5, P-zone.
- Coverage: quote fraction, missing strikes, stale OI, sessions where cash-index minutes would have been required (must be zero; those sessions use daily cash only for daily measures).
- Faithful disagreements: sessions whose top-3 set differs between OI and gamma, or between native and mapped.

## Links
[value-and-profiles](value-and-profiles.md) · [cvd-variants](cvd-variants.md) · [data-coverage](data-coverage.md) · `../SPEC.md`
