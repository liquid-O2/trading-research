# Databento pull list

"Included" = inside the Standard plan you already pay for. "Per GB" = pay-as-you-go on top (Databento's own example: ~$125 of credit ≈ 12 months of MBP-1 or 16 months of trades for one CME product).

Request all large tick pulls as **batch jobs**, not streaming. Read Databento's July 2026 CME-normalization note and August 2026 batch-API note before writing loaders.

---

## 1. CME Globex — `GLBX.MDP3` (history from ~June 2010)

Symbology: `stype_in="parent"` → `NQ.FUT`, `ES.FUT`, `YM.FUT`, `RTY.FUT`, `NQ.OPT`.
Optional: `stype_in="continuous"` → `NQ.c.0` (front by OI) / `NQ.v.0` (front by volume) for quick bar work. For tick layers pull outrights and stitch yourself.

| # | Symbols | Schema | History | Plan | Purpose |
|---|---|---|---|---|---|
| 1 | NQ, ES, YM, RTY (.FUT) | `ohlcv-1m` | all (2010→) | included | C0/C1 training, window discovery, Jumbo audit, SMT |
| 2 | NQ.FUT | `ohlcv-1s` | all | included | finer window/session stats |
| 3 | NQ, ES, YM, RTY (.FUT) | `statistics` | all | included | settlement, session H/L, daily OI/volume |
| 4 | NQ, ES, YM, RTY (.FUT) | `definition` | all | included | roll dates, tick size, expiries |
| 5 | NQ.FUT | `trades` | 5 years | 12 mo included, rest per GB | aggressor delta, delta profile, big prints |
| 6 | NQ.FUT | `mbp-1` | 3–5 years (3 already held) | 12 mo included, rest per GB | BBO reload/vanish, hidden-size proxy, spread, pace |
| 7 | NQ.FUT | `mbp-10` | last 1 month | included | sanity-check L1 proxies; decide later on buying more |
| 8 | ES, YM, RTY (.FUT) | `trades` | 3 years | per GB | cross-index delta / SMT at trade level (Phase 2+, optional) |
| 9 | NQ.OPT | `definition`, `statistics` | all | included | strikes/expiries, daily OI, settlement → OI-based gamma |
| 10 | NQ.OPT | `trades` | 12 months | included | signed flow (aggressor side provided) → flow-based gamma |
| 11 | NQ.OPT | `mbp-1` or `ohlcv-1m` | 12 months | included | option mids → IV / greeks |

---

## 2. OPRA — `OPRA.PILLAR`

Symbology: `stype_in="parent"` → `QQQ.OPT`, `NDX.OPT`, `NDXP.OPT`, `SPX.OPT`, `SPXW.OPT`, `SPY.OPT`, `VIX.OPT`.
Pull all strikes; filter later. 2013–2023 gives the OI-based gamma only; that is enough for C1.

| # | Schema | History | Plan | Purpose |
|---|---|---|---|---|
| 12 | `statistics` | Apr 2013→ | included | daily OI, settlement → OI-based dealer gamma, PCR by OI, 0DTE OI share |
| 13 | `definition` | 2013→ | included | chain construction |
| 14 | `cbbo-1m` | 2013→ | included | 1-min NBBO mids → IV surface, skew, term, vanna/charm, GEX |
| 15 | `ohlcv-1d` | 2013→ | included | volume PCR history |
| 16 | `trades` | Mar 2023→ | 12 mo included, rest per GB | flow-based positioning |
| 17 | `tcbbo` | Mar 2023→ | same | NBBO before each trade → sign the trades (at ask = buy, at bid = sell) |
| 18 | `cmbp-1` | Mar 2023→ | same | full NBBO stream; only for second-resolution 0DTE surface, skip for v1 |

Priority underlyings for v1: QQQ, NDX, NDXP. Add SPX/SPXW/SPY for cross-index later.

---

## 3. CFE — `XCBF.PITCH` (VIX futures)

Symbol: `VX.FUT` (parent).

| # | Schema | History | Purpose |
|---|---|---|---|
| 19 | `ohlcv-1m` | all available (check start date in portal) | VX term structure: contango/backwardation, front vs second |
| 20 | `statistics`, `definition` | all | settlement, expiries |
| 21 | `trades` | optional | intraday curve moves |

---

## 4. Underlying levels for greeks

OPRA carries no underlying price.

| # | Dataset | Symbols | Schema | History | Plan | Purpose |
|---|---|---|---|---|---|---|
| 22 | `XNAS.ITCH` | QQQ, SPY | `ohlcv-1m` | 2013→ | per GB (tiny) | spot for QQQ/SPY greeks |

For NDX/SPX cash: scale QQQ/SPY, or use NQ/ES futures minus a fitted basis.

---

## 5. Not on Databento

| Item | Source |
|---|---|
| Cash VIX, VXN, VIX3M | FRED: `VIXCLS`, `VXNCLS`, `VXVCLS` |
| VVIX | CBOE site / yfinance `^VVIX` |
| Event calendar (CPI, NFP, FOMC, opex, mega-cap earnings, roll days, half-days) | hand-maintained table |
| Alternative | compute an NDX vol index from OPRA `cbbo-1m` and drop the cash-index dependency |

---

## Pull order

1. `GLBX.MDP3` `ohlcv-1m` + `statistics` + `definition` for NQ/ES/YM/RTY, full history (rows 1–4). Phases 0–2 run on this.
2. `OPRA.PILLAR` `statistics` + `definition` + `cbbo-1m` for QQQ/NDX/NDXP, full history (rows 12–14).
3. `NQ.OPT` `definition` / `statistics` / `trades` / `mbp-1`, included window (rows 9–11).
4. `NQ.FUT` `trades` to 5 years, per GB (row 5).
5. `XCBF.PITCH` VX bars (rows 19–20).
6. `OPRA.PILLAR` `trades` + `tcbbo` beyond the included window only after flow-based gamma beats OI-based gamma on the overlap year (rows 16–17).
