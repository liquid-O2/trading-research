# Options nodes (four index products, native-on-native)

## Definition
Strike-level open interest and scenario-gamma nodes from **NDX, NDXP, SPX, SPXW**, plus named variants **QQQ, SPY, NQ.OPT**. **Faithful levels are native-on-native**: a product's strike is measured against that product's own spot, in that product's own points and ATR. `mapped_nq` (a strike converted onto NQ) is a **named experiment row only**, never the faithful row and never the spot for distance. Cash NDX / SPX **minutes are not assumed and are not invented**; the index products fall to the EOD rule below when no intraday underlying exists `[INV L713–718]`. Hidden book, dealer inventory, and unpublished node engines are not measurable `[DRFL L207–224]` `[README sources/documents/README.md L27–30]`.

This page must not collapse to QQQ / SPY, and no QQQ / SPY print is ever labeled as NDX / SPX spot.

## Citations
- Dealer hedging, long / short gamma, gamma flip, GEX as regime filter, strikes as where gamma lives `[GEX p.2 L17–39, p.5 L90–94]`; QQQ / SPY as *origin complexes*, not the only underlyings `[GEX p.4 L77]`.
- Native SPX node screenshot (0DTE colored nodes, strength, persistence) `[reference-images/zerano-charts-SPX-2026-08-24T18-51-29-251Z.webp]`. No formula in the image → disclosed peak construction, not a reconstructed engine `[Q23]`.
- Theta OPRA: NDX contracts / EOD / OI from 2016, NDXP from 2018, SPX / SPXW from 2016; quote-1m dte ≤ 14 wide strikes (NDX and SPX dte-14 files observed to 2026-08-20; dte-60 ATM ±10 files to 2026-09-03); trade-quote dte ≤ 7 `[INV L297–380, L422–500]`. OI observations land about 06:22–06:30 ET on the exchange date `[INV L312, L352]`.
- The acquired Theta files carry **no underlying price column**: `quote-1m` = symbol, expiration, strike, right, bid / ask size / exchange / price / condition, request_date, ts_event, osi_symbol; `trade_quote` adds the trade fields and ts_quote; `eod` adds OHLC, volume, count, closing NBBO (`/workspace/data/thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70`, same for SPX; schema read from the stored parquet). So the "OPRA quote underlying" spot source is absent for NDX, NDXP, SPX, SPXW.
- Acquired daily cash: `free-sources/yahoo__cash-daily__normalized` = QQQ, SPY, NDX, SPX daily OHLCV, 2010-01-04 → 2026-09-04, date-only `[INV L713–718]`.
- CME NQ.OPT definition / OHLCV-1m / statistics / trades 2020-01 → 2026-09 `[INV L98–120]`; QQQ / SPY 1-minute from 2018-09 `[INV L253–263]`.
- User: levels from gamma / OI heat maps, multi-asset `[DTM L22, L24]`; NDX levels felt better than QQQ on NQ `[CEX L348]` (user).

## Spot for distance-to-level (`spot_at_t`)

| product | spot source | `t` grid | ATR unit for the distance |
|---|---|---|---|
| QQQ, SPY | that ETF's own 1-minute close `[INV L253–263]` | RTH minutes 09:30–16:00; pre-open reference = the prior session's last 1-minute close | ATR-14 of the ETF's daily bars built from its 1-minute data |
| NQ.OPT | NQ (front, 1-second bars; 1-minute named) | any session minute; 09:25 pre-open snapshot | NQ ATR-14 (daily 18:00–17:00) |
| NDX, NDXP, SPX, SPXW | OPRA 1-minute quote underlying **if** the Theta quote has it; it does not (schema above) → **EOD distance to the acquired daily cash only** (`yahoo__cash-daily__normalized` NDX / SPX) | `t` ∈ {prior daily close (pre-open reference, `known_at` = prior close), same-day daily close}; no intraday `t` | ATR-14 of the daily cash series |
| sister rows (named) | the QQQ native row carried beside the NDX / NDXP rows, the SPY native row beside SPX / SPXW, tagged `sister_of = NDX` or `SPX`; each keeps its **own** strikes and its own ETF spot; no unit conversion | ETF RTH minutes | ETF ATR |

Rules: the sister row is never labeled as NDX / SPX spot and never fills an NDX / SPX cell; converting an index strike into ETF or NQ units is a mapped experiment row (Upgrades), not a spot rule; a missing spot print at `t` leaves `spot_at_t = unavailable` and keeps the row.

## Row format (every printed node row)

`product | strike | spot_at_t | distance (points and ATR) | tagged or near | known_at | OI_vintage`

- `product`: NDX, NDXP, SPX, SPXW, QQQ, SPY, NQ.OPT (sister rows add `sister_of`).
- `strike`: native strike in the product's own points.
- `spot_at_t`: the value from the table above at `t`, or `unavailable`.
- `distance`: `strike − spot_at_t` in native points, and the same divided by the product's ATR-14; sign kept.
- `tagged or near`: `tagged` = the product's spot series traded to the strike inside the outcome window (ETF / NQ: 1-minute high–low spans the strike; index products: the daily cash high–low spans the strike); `near` = |distance| ≤ a **named band**, both bands printed: `near.025` (0.25 ATR) and `near.050` (0.5 ATR); otherwise `far`. Near is a band in the product's own ATR, **not an overlay onto NQ**.
- `known_at`: when the strike set was fixed (09:25 ET from the OI file for intraday products; prior close for the EOD reference) and when `spot_at_t` was known (`t`).
- `OI_vintage`: the exchange date of the Theta `open_interest` file used (about 06:22–06:30 ET availability `[INV L312, L352]`); a one-session lag proxy is a named row; a missing OI file prints `OI_vintage = unavailable` and keeps the row.
- Missing quotes or missing spot = **coverage hole**; the product row prints with the hole flagged, the product is never dropped (example: NDX and SPX dte-14 quote files end 2026-08-20 inside F).

## Product table (every node row)

| product | native | spot for distance | mapped_nq (experiment row) | known_at | OI_vintage |
|---|---|---|---|---|---|
| NDX | Theta OPRA NDX strike in NDX points | daily cash NDX (EOD rule); no intraday | `nq = ndx × ratio(NQ, NDX)`, experiment only | 09:25 strike set; `t` = prior / same-day cash close | Theta `open_interest` as-of exchange date |
| NDXP | Theta OPRA NDXP strike in NDX points (weekly) | daily cash NDX (EOD rule) | same ratio, tagged `product=NDXP`, experiment only | same | same, NDXP file vintage |
| SPX | Theta OPRA SPX strike in SPX points | daily cash SPX (EOD rule) | `nq = spx × ratio(NQ, SPX)` or two-step SPX→ES→NQ, both experiment only | same | Theta SPX OI as-of date |
| SPXW | Theta OPRA SPXW strike in SPX points (weekly) | daily cash SPX (EOD rule) | same as SPX, tagged `product=SPXW`, experiment only | same | same, SPXW file vintage |
| QQQ | named variant; ETF strike in QQQ points | QQQ 1-minute close | `nq = qqq × ratio(NQ, QQQ)`, experiment only | 09:25 strike set; `t` on the RTH minute grid | Theta / OPRA QQQ OI as-of date |
| SPY | named variant; ETF strike in SPY points | SPY 1-minute close | `nq = spy × ratio(NQ, SPY)`, experiment only | same | Theta / OPRA SPY OI as-of date |
| NQ.OPT | CME NQ futures-option strike, **already NQ** | NQ | none needed (`mapped_nq = native`) | contract known_at; `t` any minute | CME statistics OI as-of; no option MBP-1 acquired |

`ratio(A, B)` for the experiment rows = prior-session median of the last available contemporaneous prints; additive basis is a named variant; a missing ratio does not borrow a later print. Native events and experiment events are counted separately and never pooled.

## Faithful object
- `value.node.oi.ndx.top3` / `value.node.oi.ndxp.top3` / `value.node.oi.spx.top3` / `value.node.oi.spxw.top3`: at 09:25 ET, the top 3 OI strikes above and below the product's own reference spot (prior daily cash close for the index products), dte ≤ 14, from that product's chain; every row printed in the row format above with `spot_at_t` from the EOD rule.
- `value.node.oi.qqq.top3`, `value.node.oi.spy.top3` (ETF 1-minute spot), `value.node.oi.nqopt.top3` (NQ spot): named variants, same row format, intraday `t`.
- Combined display row `value.node.oi.top3.index` = union of the four index products, identities preserved, still native-on-native.

## Upgrades
- `value.node.gamma.<product>.top3`: |gamma × OI| from reconstructed Greeks; dte ≤ 7 vs ≤ 14. Zero-gamma flip per product (aggregate exposure root under a named sign scenario). Call wall, put wall, max pain → [gex-walls-and-max-pain](gex-walls-and-max-pain.md).
- Experiment rows `value.node.oi.<product>.top3.mapped_nq`: the strike converted onto NQ by `ratio(NQ, product)` (rolling-median ratio vs additive basis; 09:25 vs 16:00 prior close), measured against NQ with NQ ATR; printed beside the native row, never in its place.
- Sister rows: QQQ for the NDX family, SPY for the SPX family, as defined above (no conversion).
- OI vintage: last available EOD vs one-session lag proxy (labeled). Missing release time stays unavailable.
- Node geometry: 1 / 3 / 5-strike smoothing, top1 / top5 / all local peaks, one-strike-neighbor vs half-height bounds `[Q23]`.
- Near bands: 0.25 ATR and 0.5 ATR are the faithful pair; 0.1 ATR and 1.0 ATR named.
- `not-measurable`: dealer inventory, hidden book, Skylit Heatseeker / Flowseeker / Atlas; intraday underlying for the index products (absent from the acquired files).

## Outcomes
- Per row: `tagged` share, `near.025` and `near.050` shares, distance distribution (points and ATR), time-to-tag for intraday products; shared grid at native levels for QQQ, SPY, NQ.OPT (1-minute spot) and at the EOD rule for the index products (daily high–low).
- Distance from the AM extreme to the nearest node, ranked against EV, −0.5, P-zone: intraday products only; index products report the EOD distance from the cash close and the daily high–low tag.
- Coverage: quote fraction, missing strikes, stale OI, missing spot prints, sessions where cash-index minutes would have been required (must be zero; those sessions use the EOD rule).
- Faithful disagreements: sessions whose top-3 set differs between OI and gamma; native vs experiment (mapped_nq) tag disagreement is an experiment column, not a faithful disagreement.

## Links
[gex-walls-and-max-pain](gex-walls-and-max-pain.md) · [value-and-profiles](value-and-profiles.md) · [cvd-variants](cvd-variants.md) · [data-coverage](data-coverage.md) · `../SPEC.md`
