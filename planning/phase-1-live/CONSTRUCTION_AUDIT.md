# Construction audit

Reference for Phase 1 live object construction. Not a score of `RULES.md`. Not Phase 2.

## Checks

1. Function matches SPEC/wiki (clock, reset, side, multiplier, bar type).
2. Fixture on synthetic or one dated session.
3. `leakage_count` is 0.
4. Spike rule. Range H/L is not a one-tick isolated explosion versus the 1s median. Options `mapped_nq` ratio is not a one-print jump.
5. Range H/L from the intended bars. RTH-only objects do not include ETH.
6. Delta/CVD reset matches SPEC (`flow.cvd.trade` resets 18:00 ET).
7. Session bounds are America/New_York. QuantPad OHLCV `t` is UTC ms. QuantPad trades/MBP-1 `t` is UTC ns. Yahoo cash and Theta OI are civil NY session dates. Mixing a naive ET wall integer with a UTC epoch is a fail. Assumed stored TZ is in `implementation/src/trading_research/research/phase1_live/vendor_tz.py`.

Options follow `wiki/options-nodes.md` as it is now. Faithful is native-on-native. `mapped_nq` is experiment only. QQQ/SPY spot is ETF 1-minute. NQ.OPT spot is NQ. Index products use EOD daily cash and sister ETF rows labeled `sister_of`. Missing quotes are holes. The product row stays. Skylit is not-measurable.

## How to rerun

```
PYTHONPATH=implementation/src /tmp/trading-research-venv/bin/python implementation/tools/construction_audit.py
PYTHONPATH=implementation/src /tmp/trading-research-venv/bin/python implementation/tools/run_phase1_objects.py report --family <family>
```

Dated spike check used NY session 2024-01-02 on `cov.nq.ohlc1s` for `range.6-9.published`. Isolated one-tick high is false. Table H/L match the 1s window.

## Fixes in this pass

- Options rows are native-on-native with `spot_at_t`, distance points and ATR, tagged/near, `known_at`, `OI_vintage`. Index mapped_nq is not-measurable (no cash minutes). QQQ/SPY use ETF 1m. Skylit is not-measurable. OI is summed by strike, dte <= 14, top 3 above and below spot.
- SessionStat `env.ss.avgHL60` is one-sided from the 09:00 open.
- CVD trade resets 18:00 and samples at 12:00.
- SMT OHLC uses S1 Asia/London/6-9 hunt.
- Value delta is aggressor delta vs POC, not a VP alias. VWAP uses 09:30-12:00 only. KZ is the AM extreme within 2 ticks of the *prior* session VAL/VAH, not the same-session full-RTH VA.
- FVG is first 5m wick gap on the 09:00 hour. 3m TBR sweep is new-extreme continuation. CISD is 15m close-through, not the 3m sweep.
- NWOG is Friday close vs Sunday 18:00. Prior-RTH fail box uses the previous session. Iceberg reports are not-measurable.
- MBP-1 tape objects are scored from QuantPad `cme__nq-continuous-futures__mbp-1` week extracts. `incomplete_spans` requires a readable parquet whose row count matches the json. Extract default is 20 workers on this 21 vCPU / 80 GiB box. Absorption/footprint/iceberg inner loops are numba or bincount. The trades-tape fallback is gone.
- `vol.rv20` / `gk20` / `har` / terciles use only prior sessions. VIX gate uses the prior VIXCLS close. Absorption candle is trailing SMA14 at a 6-9 level on 3m bars. Previous-hour boxes are completed clock hours. `footprint_stack3` equals `footprint_4x`. `smt_s1` equals `smt_trade_nq`. A+ is a sweep of NYAM, Asia, or the 10-11 box, not the 6-9 H/L.

## Table

family | id | audit | fixture | leakage | spike_flag | notes
---|---|---|---|---|---|---
range | bin.0930-0950 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
range | bin.0940-0950 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
range | bin.0950-1000 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
range | bin.1000-1030 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
range | bin.1030-1200 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
range | range.5-9 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.6-9.dollar-bars | pass | pass | 0 | clean | 1m close*vol*20 vs 60-median
range | range.6-9.published | pass | pass | 0 | clean | 06:00-09:00 1s H/L; 2024-01-02 H=16976.5 L=16817.0 matches 1s, not an isolated spike; prior RTH 09:30-16:00
range | range.6-9.trade-count | pass | pass | 0 | n/a | two-pass cut at 60-session median trade count; 647 sessions, 24 disagreements vs 1s 6-9
range | range.6-9.trade-level | pass | pass | 0 | clean | trades 06:00-09:00 H/L; 2024-01-02 matches 1s
range | range.6-9.vol-elapsed | pass | pass | 0 | clean | causal 60-session median 1m volume; leakage 0
range | range.7-9 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.8-9 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.asia.2000-2030 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.gb.10-11 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.gb.asia | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.gb.hour | pass | pass | 0 | clean | completed clock hours, not 5-minute steps
range | range.gb.london | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.gb.nyam | pass | pass | 0 | clean | 09:00-10:00, outcomes from 10:00; nyam_violation=0
range | range.ib | pass | pass | 0 | clean | 09:30-10:30; 2024-01-02 IB high is not ETH-inclusive
range | range.london.00-03 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.london.0300-0330 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.or.15m | pass | pass | 0 | clean | 09:30-09:45 RTH only
range | range.or.5m | pass | pass | 0 | clean | 09:30-09:35 RTH only
range | range.midnight.0000-0030 | pass | pass | 0 | n/a | 00:00-00:30, outcomes 00:30-03:00
range | range.rth.0930-1000 | pass | pass | 0 | n/a | 09:30-10:00 A period, outcomes 10:00-12:00
range | range.rth.1000-1030 | pass | pass | 0 | n/a | 10:00-10:30, outcomes 10:30-12:00
range | range.lunch.1200-1230 | pass | pass | 0 | n/a | lunch comparison, outcomes 12:30-16:00
range | range.moc.1500-1530 | pass | pass | 0 | n/a | MOC comparison, outcomes 15:30-16:00
range | range.on.1800-0930 | pass | pass | 0 | n/a | overnight 18:00-09:30 H/L
range | onh_or_onl | pass | pass | 0 | n/a | RTH touch of overnight high or low
path | balance.body-ratio | pass | pass | 0 | n/a | body/W69 >= 0.5 on the 6-9 box
path | balance.vp-shape | fail | pass | 0 | n/a | 6-9 OHLC peak test returns double on every F session; not a shape
path | corr.am-pm | unbuilt | none | 0 | n/a | SPEC upgrade; no function
path | edge.clean | pass | pass | 0 | n/a | not purged (Asia/London H/L still off the 6-9 extremes)
path | grid.jumbo.projection-reject | pass | pass | 0 | n/a | G-default reject at -0.5 of 6-9, r=0.5 k=15, not a 6-9 H/L tag
path | judas.depth.-0.5 | pass | pass | 0 | n/a | m05 then close through EQ
path | path.6-9.published | pass | pass | 0 | n/a | b.c1 09:30-12:00 on 6-9 H/L; width tables not mixed
path | path.midretrace | pass | pass | 0 | n/a | measured inside path.6-9.published.json summary.midretrace
path | w.pct.0859close | pass | pass | 0 | n/a | width table in range.6-9.published.json; not mixed with rel-prior-rth
path | w.pct.0930open | pass | pass | 0 | n/a | XF bins of W69/09:30 open in range.6-9.published.json width_tables.w_pct_0930open; not mixed with rel-prior-rth
path | w.rel-prior-rth | pass | pass | 0 | n/a | separate table, not the XF p.24 price-percent bins
path | window.1030 | unbuilt | none | 0 | n/a | SPEC 09:30-10:30 path table; no report
path | window.1600 | unbuilt | none | 0 | n/a | SPEC 09:30-16:00 path table; no report
open | open.dbx.in-range-not-value | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
open | open.dbx.in-value | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
open | open.dbx.outside-both | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
open | open.oneway.A.0930-1000 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
open | open.oneway.OR.15m | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
open | open.oneway.OR.5m | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
open | open.switch.ohlc-vp | pass | pass | 0 | n/a | Pine body-wick H-L distribution; 45 disagreements vs prior-RTH trade VP
open | open.switch.published | pass | pass | 0 | n/a | 27 cells; prior RTH trade VP 09:30-16:00, no ETH
env | env.ev.gk20 | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.har | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.iv | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.mean60 | pass | pass | 0 | n/a | ref.0930open ± prior-60 AM one-sided means; EV mid is not 6-9 EQ
env | env.ev.median60 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
env | env.ev.p75 | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.p90 | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.rv20 | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.vix16 | pass | pass | 0 | n/a | 09:30 open ± (VIX/16) percent; daily VIX, no strike IV
env | env.ev.yz20 | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ext.050 | unbuilt | none | 0 | n/a | SPEC upgrade; no env report
env | env.ext.100 | pass | pass | 0 | n/a | H+1.0*W69 / L-1.0*W69 AM reach
env | env.ext.133.from-edge | pass | pass | 0 | n/a | H+1.33*W69 / L-1.33*W69
env | env.ext.133.from-edge.london | pass | pass | 0 | n/a | 1.33 of range.london.00-03, outcome 03:00-06:00
env | env.ext.133.from-eq | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ext.133.from-origin | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ext.166.from-edge | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
env | env.ss.avgHL60 | pass | pass | 0 | n/a | 09:00 open + mean(H-open) / open - mean(open-L) over prior 60
env | env.ss.medHL60 | pass | pass | 0 | n/a | 09:00 open ± 60-session median one-sided excursions
env | env.ss.minavg60 | pass | pass | 0 | n/a | 09:00 open ± min(mean up, mean down)
env | pz.approx.A | pass | pass | 0 | n/a | T1-T4 adjacent bands from 500-session history; primary is T1 reach (excursion >= p50); 573/647
env | pz.learned | unbuilt | pass | 0 | n/a | Phase 3 learned P-zone; deferred on purpose
vol | vol.gk20 | pass | pass | 0 | n/a | prior-session-only mean of gk
vol | vol.har | pass | pass | 0 | n/a | prior-session-only HAR weights 0.5/0.3/0.2 on rv history
vol | vol.iv.atm | not-measurable | pass | 0 | n/a | ATM IV not built as a session object
vol | vol.rv20 | pass | pass | 0 | n/a | prior-session-only rv20/gk20/har; terciles exclude the session being scored
vol | vol.skew25 | unbuilt | none | 0 | n/a | SPEC faithful; no report
vol | vol.vx.slope | unbuilt | none | 0 | n/a | SPEC faithful; no report
vol | vol.yz20 | unbuilt | none | 0 | n/a | SPEC faithful; no report
flow | flow.absorption.A | pass | pass | 0 | n/a | 2m q90 at 6-9 H/L, <=2 ticks, 0.25R / 15m
flow | flow.absorption.candle.jumbo | pass | pass | 0 | n/a | 3m trailing SMA14 at a 6-9 level, body/range <=0.3, k=2.5
flow | flow.absorption.A.q75 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.absorption.A.w1m | pass | pass | 0 | n/a | 1m roll vs own-window q90, not frozen 2m; 37/429, 36 disagreements vs A
flow | flow.absorption.A.w5m | pass | pass | 0 | n/a | 5m roll vs own-window q90, not frozen 2m; 38/429, 43 disagreements vs A
flow | flow.absorption.B | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.bigtrade.100ny | pass | pass | 0 | n/a | size>=100 on 09:30-16:00
flow | flow.bigtrade.30-60 | unbuilt | none | 0 | n/a | wiki Ethos comparison; no report
flow | flow.bigtrade.75ldn | pass | pass | 0 | n/a | size>=75 on 02:00-05:00
flow | flow.bigtrade.q50 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.bigtrade.q75 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.bigtrade.q90 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.bigtrade.q99 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.cvd.gamma | not-measurable | pass | 0 | n/a | gamma weight table not built
flow | flow.cvd.ohlc | pass | pass | 0 | n/a | Pine close-in-range 18:00-12:00 1m; PHASE rate is non-zero sign
flow | flow.cvd.part.ohlc | pass | pass | 0 | n/a | high-volume tercile, same Pine close-in-range 18:00-12:00
flow | flow.cvd.part.q75 | pass | pass | 0 | n/a | session q75 on 18:00-12:00 trades, second pass; not full-extract size
flow | flow.cvd.part.q90 | pass | pass | 0 | n/a | session q90 on 18:00-12:00 trades, second pass; not full-extract size
flow | flow.cvd.part.trade | pass | pass | 0 | n/a | three signed streams >=100 / 20-99 / <20; published flag is the >=100 stream; 75 disagreements vs total
flow | flow.cvd.trade | pass | pass | 0 | n/a | 18:00 reset, sample at 12:00, aggressor side; terminal sign not a 1s series
flow | flow.footprint.diag.4x | pass | pass | 0 | n/a | stacked >=3 adjacent 4x imbalances on MBP-1 AM trades; 247/429, not saturating
flow | flow.iceberg.touch.infer | not-measurable | pass | 0 | n/a | wiki iceberg detection is not measurable with MBP-1
flow | flow.iceberg.touch.k15 | not-measurable | pass | 0 | n/a | not-measurable as printed
flow | flow.iceberg.touch.k20 | not-measurable | pass | 0 | n/a | not-measurable as printed
flow | flow.ofm.sequence | unbuilt | none | 0 | n/a | wiki OFM stages; no report
flow | flow.refill.offtouch | not-measurable | pass | 0 | n/a | needs MBP-10/MBO
flow | flow.refill.ontouch | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.smt.ohlc.4 | pass | pass | 0 | n/a | S1 Asia/London/6-9 hunt on 1m; PDH/PDL not in this S1 set
flow | flow.smt.pine.3-3 | pass | pass | 0 | n/a | Open Source Fractal 3/3, lookback 200, min 2 ticks, 12-bar merge vs sister 1m; fires 429/429
flow | flow.smt.trade.es | not-measurable | pass | 0 | n/a | ES MBP-1 ends 2024-08-30; not-measurable in F
flow | flow.smt.trade.nq | pass | pass | 0 | n/a | tick-precise S1 hunt on MBP-1 vs sister 1m Asia/London/6-9/PDH/PDL; 320/429, 63 disagreements vs OHLC S1
value | env.vwap.rth.sd2 | pass | pass | 0 | n/a | 09:30-12:00 HLC3 VWAP ±2SD, no 16:00 lookahead
value | value.dealer.inventory | not-measurable | pass | 0 | n/a | not-measurable as printed
value | value.delta.rth.trade | pass | pass | 0 | n/a | RTH aggressor delta vs POC; 45 disagreements with VP
value | value.hidden.book | not-measurable | pass | 0 | n/a | not-measurable as printed
value | value.kz | pass | pass | 0 | n/a | AM extreme within 2 ticks of prior-session VAL/VAH, not same-session full-RTH VA
value | value.vp.rth.ohlc1m | unbuilt | none | 0 | n/a | SPEC upgrade; no report
value | value.vp.rth.trade | pass | pass | 0 | n/a | RTH 09:30-16:00 trade VP; VAL present flag
fail | fail.box.6-9.gb.c5 | pass | pass | 0 | n/a | 06:00-09:00 box, wick then 5m close-back k=30
fail | fail.box.gb.10-11.gb.c5 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
fail | fail.box.gb.asia.gb.c5 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
fail | fail.box.gb.hour.gb.c5 | pass | pass | 0 | n/a | 60-min box at 5m steps 09:30-12:00; session-any saturates; score uses per-box rate
fail | fail.box.gb.london.gb.c5 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
fail | fail.box.gb.nyam.gb.c5 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
fail | fail.box.jumbo.london.gb.c5 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
fail | fail.box.prior-rth.gb.c5 | pass | pass | 0 | n/a | prior session 09:30-16:00 PDH/PDL, AM fail-back
fail | label.aplus | pass | pass | 0 | n/a | sweep of NYAM, Asia, or 10-11 (traded range), not 6-9
fail | loc.gp | pass | pass | 0 | n/a | NYAM 0.382-0.5 band, outcomes from 10:00
fail | lvl.tdo.c5 | pass | pass | 0 | n/a | wick of 00:00 print then 5m close back through
fail | lvl.0930open.below | pass | pass | 0 | n/a | sweep below 09:30 open then reclaim by 09:45
fail | lvl.0930open | pass | pass | 0 | n/a | 09:30-09:45 sweep >=2 ticks then reclaim; 503/647, not AM through-touch
fail | lvl.nwog | pass | pass | 0 | n/a | Monday Friday 16:00 close vs Sunday 18:00 open, AM overlap
fail | lvl.tdo | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
gap | gap.body.adjacent | pass | pass | 0 | n/a | 5m body gaps on the 09 hour; 597/647, 103 disagreements vs FVG
gap | gap.fvg.first.clock | pass | pass | 0 | n/a | first 5m wick gap on the 09:00 hour; 574/647, not all-day
block | block.sweep.tbr.3m | pass | pass | 0 | n/a | 3m new-extreme continuation on IB; 508/647, not saturating
block | cisd.fractal.literal | pass | pass | 0 | n/a | 15m C2 takes extreme, C3 closes through far side; 526/647, 220 disagreements vs 3m sweep. Not the Pine fractal matcher.
tpo | label.amt.80pct.two-period | pass | pass | 0 | n/a | open outside prior VA, A and B period closes inside
tpo | label.amt.day | pass | pass | 0 | n/a | exclusive labels trend/normal/normal-variation/neutral/non-trend; PHASE flag is trend; 409/647
tpo | label.amt.open.30m | pass | pass | 0 | n/a | exclusive labels drive/test-drive/rejection-reverse/auction from first 30m vs prior VA; PHASE flag is drive; 265/647
tpo | value.tpo.rth.30m | pass | pass | 0 | n/a | 30m periods, 1-point poor extreme = single-period high or low row
tpo | value.tpo.rth.30m.trade | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
options | value.dealer.inventory | not-measurable | pass | 0 | n/a | not-measurable as printed
options | value.hidden.book | not-measurable | pass | 0 | n/a | not-measurable as printed
options | value.node.gamma.ndx.top3 | unbuilt | none | 0 | n/a | wiki/SPEC gamma upgrade; no function
options | value.node.oi.ndx.top3 | pass | pass | 0 | n/a | native NDX, EOD cash spot, dte<=14, top3 OI strikes above and below, no cash minutes
options | value.node.oi.ndx.top3.mapped_nq | not-measurable | pass | 0 | n/a | not-measurable as printed
options | value.node.oi.ndxp.top3 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
options | value.node.oi.ndxp.top3.mapped_nq | not-measurable | pass | 0 | n/a | not-measurable as printed
options | value.node.oi.nq.opt.top3 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
options | value.node.oi.nqopt.top3 | pass | pass | 0 | n/a | NQ spot; OI_vintage unavailable (CME statistics are DBN); product row kept
options | value.node.oi.qqq.top3 | pass | pass | 0 | n/a | QQQ 1m spot, sister_of=NDX, native-on-native
options | value.node.oi.qqq.top3.mapped_nq | pass | pass | 0 | clean | experiment; prior-session median contemporaneous 1m ratio; 17 sessions unavailable_map
options | value.node.oi.spx.top3 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
options | value.node.oi.spx.top3.mapped_nq | not-measurable | pass | 0 | n/a | not-measurable as printed
options | value.node.oi.spxw.top3 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
options | value.node.oi.spxw.top3.mapped_nq | not-measurable | pass | 0 | n/a | not-measurable as printed
options | value.node.oi.spy.top3 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
options | value.node.oi.spy.top3.mapped_nq | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
options | value.node.oi.top3.index | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
options | value.skylit.atlas | not-measurable | pass | 0 | n/a | not-measurable as printed
options | value.skylit.flowseeker | not-measurable | pass | 0 | n/a | not-measurable as printed
options | value.skylit.heatseeker | not-measurable | pass | 0 | n/a | unpublished; stays not-measurable

## Counts

n = 164. pass = 124. fail = 1. unbuilt = 21. not-measurable = 18. The fail is `balance.vp-shape` (always double).

## Why 21 are still unbuilt

Unbuilt means SPEC or wiki names the id and there is no function and no report. It is not a failed build. These remaining rows are named upgrades that no faithful RULES.md section B recipe required this turn, or a later-phase object.

| group | n | ids |
|---|---|---|
| path upgrades unused by B | 3 | `corr.am-pm`, `window.1030`, `window.1600` |
| EV / extension unused by B | 10 | `env.ev.{p75,p90,rv20,gk20,yz20,har,iv}`, `env.ext.{050,133.from-eq,133.from-origin}` |
| Phase 3 | 1 | `pz.learned` (deferred on purpose) |
| vol SPEC faithful with no report | 3 | `vol.yz20`, `vol.skew25`, `vol.vx.slope` |
| flow extras | 2 | `flow.bigtrade.30-60`, `flow.ofm.sequence` |
| value upgrade | 1 | `value.vp.rth.ohlc1m` |
| options gamma | 1 | `value.node.gamma.ndx.top3` (no strike IV; not approximated from OI) |

Faithful objects that do have reports are not in this list. `vol.rv20`, `vol.gk20`, and `vol.har` are built. The three missing vol rows are in SPEC §5 as faithful and were never implemented. `value.vp.rth.ohlc1m` is named by R-P17 and stays unbuilt this turn.

