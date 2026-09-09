# SPEC — Phase 1 measurement contract

## 1. Scope and slices
- Instrument: NQ continuous front (`quantpad/cme__nq-continuous-futures__*`), roll map from `derived/continuous-futures__instrument-and-roll-maps` `[INV L174–202, L743]`. Sisters (ES, YM, RTY) 1-minute bars only in F; ES MBP-1 ends 2024-08-30 `[INV L142–148]`.
- **F** (frozen): NY trade dates 2024-01-02 → 2026-08-31. **L** (long, 1-minute bars only): 2010-09-07 → 2026-08-31, used only to recompute published tables.
- Session = 18:00 ET (prior calendar day) → 17:00 ET; clocks in America/New_York; holidays and early closes from the trading calendar; nothing measured across 17:00 → 18:00.
- Coverage rule: a session is dropped from a family when any window the family needs is missing > 10% of its expected 1-second bars; dropped sessions are listed in the report.

## 2. Data schemas used
- `cov.nq.ohlc1s` (default bars), `cov.nq.ohlc1m` (L and OHLC-level variants), `cov.nq.mbp1` (trade events with aggressor side, size, order count), `cov.nq.trades` (2021-09 →, cross-check), sisters' `ohlcv-1m`, options as listed in `wiki/data-coverage.md`, VX / calendars from `free-sources`.

## 3. Object schema (one JSON document per variant)
```
{ "family": "range|path|open|env|flow|value|fail|vol",
  "variant": "range.6-9.published",
  "faithful_of": "range.6-9.published" | null,
  "params": { ...named constants only... },
  "window": {"start": "06:00", "end": "09:00", "outcome_start": "09:30", "outcome_end": "12:00"},
  "levels": ["H","L","EQ","Q25","Q75","open","close","-0.5","1.0","1.33","1.66"],
  "grid": "G-default",
  "slice": "F" | "L",
  "sessions": [ {"date": "...", "labels": {...}, "levels": {...}, "outcomes": {...}, "coverage": {...}} ],
  "summary": { "n": 0, "faithful_disagreements": 0, "status": "measured", "tables": {...} },
  "citations": ["TBR p.30", "XF p.24"] }
```
Every constant is a named parameter. No hidden thresholds.

## 4. Outcome grid
`wiki/touch-reject-hold-break-grid.md` is normative. `G-default` = touch `t2`, break `b.c1`, reject `r=0.5,k=15`, hold `h=30`, fail-back `b.c5,k=30`. Each report carries the sensitivity block (label flips under every other cell).

## 5. Family and variant registry
| family | faithful | upgrades (named) | wiki |
|---|---|---|---|
| range | `range.6-9.published` | `range.6-9.vol-elapsed`, `range.6-9.dollar-bars`, `range.6-9.trade-level`, `range.5-9`, `range.7-9`, `range.8-9`, `range.london.00-03`, `range.london.0300-0330`, `range.asia.2000-2030`, `range.gb.asia`, `range.gb.london`, `range.gb.nyam`, `range.gb.10-11`, `range.gb.hour`, `range.or.5m`, `range.or.15m`, `range.ib`; bins `bin.*` | tbr-6-9-range, clock-grid-and-bars |
| path | `path.6-9.published` | `judas.depth.-0.5`, width metrics `w.pct.0859close` / `w.pct.0930open` / `w.rel-prior-rth`, windows 10:30 / 12:00 / 16:00, `balance.body-ratio`, `balance.vp-shape`, `edge.clean`, `corr.am-pm`, `path.midretrace` | range-path-class |
| open | `open.switch.published` (27 cells) | VP source and VA % variants, `open.oneway.A`, `open.dbx.*` | open-location-switch |
| env | `env.ev.mean60`; `env.ss.avgHL60`; `env.ext.133.from-edge`, `env.ext.166.from-edge`; `pz.approx.A` | `env.ev.{median60,p75,p90,rv20,gk20,yz20,har,iv,vix16}` × `ref.{0930open,eq69,0900close,tdo}`; `env.ss.{medHL60,minavg60}`; `env.ext.{100,050,133.from-eq}` and London box; `pz.approx.B`; VWAP band row `env.vwap.sd2` | ev-range-expected-move, sessionstat-9-12-envelope, extensions-1-33-1-66, p-zones-benchmark |
| flow | `flow.cvd.trade`; `flow.smt.ohlc.4`; `flow.absorption.A`; `flow.bigtrade.100ny` / `75ldn` | `flow.cvd.{ohlc,part.trade,part.ohlc,gamma}`; `flow.smt.trade.nq`, level sets S1–S3, lags; `flow.absorption.B`; thresholds | cvd-variants, smt-divergence, absorption-and-big-trades |
| value | `value.vp.rth.trade`; `value.delta.rth.trade`; `value.kz`; `value.node.oi.top3` | `value.vp.rth.ohlc1m`, VA 68 / 40, bins, scope, `value.tpo`; `value.node.gamma.top3`, dte, QQQ, zero-gamma | value-and-profiles, options-nodes |
| fail | `fail.<box>.gb.c5` for every box; `lvl.tdo`, `lvl.nwog`, `lvl.0930open`; `loc.gp`; `label.aplus` | `b.c1`, depth `d`, cap `k` | session-fail-boxes |
| vol | `vol.rv20`, `vol.gk20`, `vol.yz20`, `vol.har`, `vol.iv.atm`, `vol.skew25`, `vol.vx.slope` | windows 10 / 60; overnight RV | vol-estimators |
Not-measurable rows (always printed): `flow.refill.offtouch`, `value.dealer.inventory`, `value.hidden.book`, `value.skylit.*`, `flow.smt.trade.es` (in F).

## 6. Report format and the PHASE line
- Path: `trading-research/reports/phase1-fable/<family>/<variant>.json` (canonical JSON via the repo's `operations.artifacts.canonical_json`) and `<variant>.md` twin.
- Line: `family | variant | n | faithful disagreements | experiment status | report path`.
- `n` = sessions in the slice after the coverage rule. `faithful disagreements` = sessions where the variant's primary label differs from its `faithful_of` row (0 for faithful rows; `-` for not-measurable). Primary label per family: range → path class; path → day type; open → open cell; env → reach label; flow → event-at-AM-extreme flag; value → open-location cell (VP) or top-3 node set; fail → fail-back present at the 6–9 edges; vol → tercile.
- `experiment status` ∈ {`measured`, `null`, `worse`, `better`, `deferred`, `not-measurable`}. `null` / `worse` / `better` apply only to upgrade rows and compare the pre-declared metric of the page (e.g. reject-at-level rate, calibration share) against the faithful row; "better" requires the Wilson 95% intervals not to overlap; otherwise `null`. No P&L anywhere.
- Every table cell prints `n` and a Wilson 95% interval for shares.

## 7. Columns Phase 1 must emit for later phases (the only later-phase design here)
Per session, in `sessions[].labels`: `path_class`, `break_order`, `day_type`, `open_cell`, `balance`, `edge_clean`, `width_pct`, `width_rel_prior_rth`, `rvol_0930`, `vol_tercile_{rv,gk,yz,iv}`, `ev_reach_{mean60,median60}`, `ss_reach`, `ext_133_touch`, `ext_166_touch`, `pz_reject`, `smt_event_S1`, `cvd_div_trade`, `absorption_A_at_extreme`, `bigtrade_count_ny`, `fail_events_by_box`, `tdo_touch`, `nwog_fill`, `hod_lod_time`, `am_extreme_time`, `am_extreme_nearest_object`. Phase 2 predicts from these; Phase 3 learns location from `levels` + `outcomes`. Nothing else is specified.

## 8. Runner and resource conventions
- One registered runner, `trading-research/tools/run_phase1_objects.py`, modes `check`, `run --family <f> --slice F|L`, `report`; it uses the repo's retained-artifact helpers and canonical JSON; it never writes outside `trading-research/reports/phase1-fable/` and the retained artifact store `[AGENTS.md]`.
- Runs execute under the applicable approved resource limits (E0 envelope today: CPU soft 180 s / hard 190 s, 4 GiB address space, 360 s wall per run `[src/trading_research/__main__.py L15–16]`). MBP-1 work is chunked per calendar month into retained per-session tables so no single run exceeds the envelope; a larger budget is requested through the existing budget path, not assumed `[AGENTS.md]`.
- Pinned interpreter `/tmp/trading-research-venv/bin/python`. Failures, elapsed time and CPU are retained, never reset.

## 9. Must not change
`sources/`, raw data under `/workspace/data`, `archive/`, `planning/phase-1-from-scratch/`.

## 10. Statistics conventions
Descriptive only. Shares with `n` and Wilson 95% intervals; distributions as p25 / p50 / p75; recompute rows print the quoted source number beside the recomputed one. Same buckets as the source when recomputing. No multiple-comparison claims; a table is a table.
