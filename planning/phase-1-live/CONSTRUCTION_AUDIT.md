# Construction audit

Reference for Phase 1 live object construction. Not a score of `RULES.md`. Not Phase 2.

## Checks

1. Function matches SPEC/wiki (clock, reset, side, multiplier, bar type).
2. Fixture on synthetic or one dated session.
3. `leakage_count` is 0.
4. Spike rule. Range H/L is not a one-tick isolated explosion versus the 1s median. Options `mapped_nq` ratio is not a one-print jump.
5. Range H/L from the intended bars. RTH-only objects do not include ETH.
6. Delta/CVD reset matches SPEC (`flow.cvd.trade` resets 18:00 ET).

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
- Value delta is aggressor delta vs POC, not a VP alias. VWAP uses 09:30-12:00 only. KZ is an HVN local max.
- FVG is first-per-hour. 3m TBR sweep is resampled 3m. CISD is a distinct 1m close-back.
- NWOG is Friday close vs Sunday 18:00. Prior-RTH fail box uses the previous session. Iceberg reports are not-measurable.

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
range | range.6-9.trade-count | fail | pass | 0 | n/a | path clones 6-9; closed_early stored but box is not cut to median count family_clocks.py:251-265
range | range.6-9.trade-level | pass | pass | 0 | clean | trades 06:00-09:00 H/L; 2024-01-02 matches 1s
range | range.6-9.vol-elapsed | pass | pass | 0 | clean | causal 60-session median 1m volume; leakage 0
range | range.7-9 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.8-9 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.asia.2000-2030 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.gb.10-11 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.gb.asia | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.gb.hour | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.gb.london | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.gb.nyam | pass | pass | 0 | clean | 09:00-10:00, outcomes from 10:00; nyam_violation=0
range | range.ib | pass | pass | 0 | clean | 09:30-10:30; 2024-01-02 IB high is not ETH-inclusive
range | range.london.00-03 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.london.0300-0330 | pass | pass | 0 | clean | clock matches wiki; leakage 0; fixture pass.
range | range.or.15m | pass | pass | 0 | clean | 09:30-09:45 RTH only
range | range.or.5m | pass | pass | 0 | clean | 09:30-09:35 RTH only
path | balance.body-ratio | unbuilt | none | 0 | n/a | SPEC upgrade; no path report
path | balance.vp-shape | unbuilt | none | 0 | n/a | SPEC upgrade; no function
path | corr.am-pm | unbuilt | none | 0 | n/a | SPEC upgrade; no function
path | edge.clean | unbuilt | none | 0 | n/a | SPEC upgrade; no path report
path | judas.depth.-0.5 | pass | pass | 0 | n/a | m05 then close through EQ
path | path.6-9.published | pass | pass | 0 | n/a | b.c1 09:30-12:00 on 6-9 H/L; width tables not mixed
path | path.midretrace | pass | pass | 0 | n/a | measured inside path.6-9.published.json summary.midretrace
path | w.pct.0859close | pass | pass | 0 | n/a | width table in range.6-9.published.json; not mixed with rel-prior-rth
path | w.pct.0930open | fail | pass | 0 | n/a | session field exists; no XF-style width table in the range/path reports
path | w.rel-prior-rth | pass | pass | 0 | n/a | separate table, not the XF p.24 price-percent bins
path | window.1030 | unbuilt | none | 0 | n/a | SPEC 09:30-10:30 path table; no report
path | window.1600 | unbuilt | none | 0 | n/a | SPEC 09:30-16:00 path table; no report
open | open.dbx.in-range-not-value | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
open | open.dbx.in-value | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
open | open.dbx.outside-both | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
open | open.oneway.A.0930-1000 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
open | open.oneway.OR.15m | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
open | open.oneway.OR.5m | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
open | open.switch.ohlc-vp | fail | pass | 0 | n/a | 1m close x vol bins, not Pine body/wick H-L distribution
open | open.switch.published | pass | pass | 0 | n/a | 27 cells; prior RTH trade VP 09:30-16:00, no ETH
env | env.ev.gk20 | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.har | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.iv | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.mean60 | pass | pass | 0 | n/a | ref.0930open ± prior-60 AM one-sided means; EV mid is not 6-9 EQ
env | env.ev.median60 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
env | env.ev.p75 | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.p90 | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.rv20 | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.vix16 | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ev.yz20 | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ext.050 | unbuilt | none | 0 | n/a | SPEC upgrade; no env report
env | env.ext.100 | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ext.133.from-edge | pass | pass | 0 | n/a | H+1.33*W69 / L-1.33*W69
env | env.ext.133.from-edge.london | unbuilt | none | 0 | n/a | London box source; no report
env | env.ext.133.from-eq | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ext.133.from-origin | unbuilt | none | 0 | n/a | SPEC upgrade; no report
env | env.ext.166.from-edge | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
env | env.ss.avgHL60 | pass | pass | 0 | n/a | 09:00 open + mean(H-open) / open - mean(open-L) over prior 60
env | env.ss.medHL60 | unbuilt | none | 0 | n/a | wiki upgrade; no report
env | env.ss.minavg60 | unbuilt | none | 0 | n/a | wiki named min-average; no report
env | pz.approx.A | fail | pass | 0 | n/a | single p90 envelope from 09:30 open, not T1-T4 adjacent 50/75/90/95/99 bands
env | pz.learned | unbuilt | pass | 0 | n/a | Phase 3 learned P-zone; deferred on purpose
vol | vol.gk20 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
vol | vol.har | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
vol | vol.iv.atm | not-measurable | pass | 0 | n/a | ATM IV not built as a session object
vol | vol.rv20 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
vol | vol.skew25 | unbuilt | none | 0 | n/a | SPEC faithful; no report
vol | vol.vx.slope | unbuilt | none | 0 | n/a | SPEC faithful; no report
vol | vol.yz20 | unbuilt | none | 0 | n/a | SPEC faithful; no report
flow | flow.absorption.A | pass | pass | 0 | n/a | 2m q90 at 6-9 H/L, <=2 ticks, 0.25R / 15m
flow | flow.absorption.A.q75 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.absorption.A.w1m | fail | pass | 0 | n/a | 1m roll scored against frozen 2m q90
flow | flow.absorption.A.w5m | fail | pass | 0 | n/a | 5m roll scored against frozen 2m q90
flow | flow.absorption.B | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.bigtrade.100ny | pass | pass | 0 | n/a | size>=100 on 09:30-16:00
flow | flow.bigtrade.30-60 | unbuilt | none | 0 | n/a | wiki Ethos comparison; no report
flow | flow.bigtrade.75ldn | pass | pass | 0 | n/a | size>=75 on 02:00-05:00
flow | flow.bigtrade.q50 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.bigtrade.q75 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.bigtrade.q90 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.bigtrade.q99 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.cvd.gamma | not-measurable | pass | 0 | n/a | gamma weight table not built
flow | flow.cvd.ohlc | fail | pass | 0 | n/a | sign(c-o) on 09:30-12:00 1m, not Pine close-in-range; no 18:00 reset
flow | flow.cvd.part.ohlc | fail | pass | 0 | n/a | 1m volume tercile still uses sign(c-o), not close-in-range
flow | flow.cvd.part.q75 | fail | pass | 0 | n/a | still MBP-1 full-extract size cut; not 18:00-12:00 reset
flow | flow.cvd.part.q90 | fail | pass | 0 | n/a | still MBP-1 full-extract size cut; not 18:00-12:00 reset
flow | flow.cvd.part.trade | fail | pass | 0 | n/a | one >=100 sign, not three CVD streams >=100 / 20-99 / <20
flow | flow.cvd.trade | pass | pass | 0 | n/a | 18:00 reset, sample at 12:00, aggressor side; terminal sign not a 1s series
flow | flow.footprint.diag.4x | fail | pass | 0 | n/a | AM-session 4x aggregate; stacked >=3 skipped; rate 1.0
flow | flow.iceberg.touch.infer | not-measurable | pass | 0 | n/a | wiki iceberg detection is not measurable with MBP-1
flow | flow.iceberg.touch.k15 | not-measurable | pass | 0 | n/a | not-measurable as printed
flow | flow.iceberg.touch.k20 | not-measurable | pass | 0 | n/a | not-measurable as printed
flow | flow.ofm.sequence | unbuilt | none | 0 | n/a | wiki OFM stages; no report
flow | flow.refill.offtouch | not-measurable | pass | 0 | n/a | needs MBP-10/MBO
flow | flow.refill.ontouch | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
flow | flow.smt.ohlc.4 | pass | pass | 0 | n/a | S1 Asia/London/6-9 hunt on 1m; PDH/PDL not in this S1 set
flow | flow.smt.pine.3-3 | fail | pass | 0 | n/a | first3 vs last3 AM HH/HL, not Open Source Fractal 3/3 matcher
flow | flow.smt.trade.es | not-measurable | pass | 0 | n/a | ES MBP-1 ends 2024-08-30; not-measurable in F
flow | flow.smt.trade.nq | fail | pass | 0 | n/a | MBP-1 running H/L vs sister 1m, not tick-precise S1 hunt
value | env.vwap.rth.sd2 | pass | pass | 0 | n/a | 09:30-12:00 HLC3 VWAP ±2SD, no 16:00 lookahead
value | value.dealer.inventory | not-measurable | pass | 0 | n/a | not-measurable as printed
value | value.delta.rth.trade | pass | pass | 0 | n/a | RTH aggressor delta vs POC; 45 disagreements with VP
value | value.hidden.book | not-measurable | pass | 0 | n/a | not-measurable as printed
value | value.kz | fail | pass | 0 | n/a | HVN local-max on 1m close-volume fires 429/429; not trade-profile HVN/LVN
value | value.vp.rth.ohlc1m | unbuilt | none | 0 | n/a | SPEC upgrade; no report
value | value.vp.rth.trade | pass | pass | 0 | n/a | RTH 09:30-16:00 trade VP; VAL present flag
fail | fail.box.6-9.gb.c5 | pass | pass | 0 | n/a | 06:00-09:00 box, wick then 5m close-back k=30
fail | fail.box.gb.10-11.gb.c5 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
fail | fail.box.gb.asia.gb.c5 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
fail | fail.box.gb.hour.gb.c5 | unbuilt | none | 0 | n/a | wiki last completed hour fail event; no fail report
fail | fail.box.gb.london.gb.c5 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
fail | fail.box.gb.nyam.gb.c5 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
fail | fail.box.jumbo.london.gb.c5 | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
fail | fail.box.prior-rth.gb.c5 | pass | pass | 0 | n/a | prior session 09:30-16:00 PDH/PDL, AM fail-back
fail | label.aplus | fail | pass | 0 | n/a | OR of every box sweep; eligible rate 1.0; never unknown
fail | loc.gp | unbuilt | none | 0 | n/a | wiki 50-61.8% location flag; no function
fail | lvl.0930open | fail | pass | 0 | n/a | AM 09:30-12:00 through-touch of 09:30 open is nearly tautological
fail | lvl.nwog | pass | pass | 0 | n/a | Monday Friday 16:00 close vs Sunday 18:00 open, AM overlap
fail | lvl.tdo | pass | pass | 0 | n/a | clock matches wiki; leakage 0; fixture pass.
gap | gap.body.adjacent | fail | pass | 0 | n/a | session flag 647/647 and identical to fvg (0 disagreements)
gap | gap.fvg.first.clock | fail | pass | 0 | n/a | any-hour 00:00-16:00 session flag saturates 647/647; not per-clock events
block | block.sweep.tbr.3m | fail | pass | 0 | n/a | AM 3m pattern saturates 647/647 and matches cisd (0 disagreements)
block | cisd.fractal.literal | fail | pass | 0 | n/a | 1m C2 sweep then C3 close-back, not Pine fractal opposing-run
tpo | label.amt.day | fail | pass | 0 | n/a | boolean from path class, not AMT trend/normal/normal-variation/neutral/non-trend
tpo | label.amt.open.30m | fail | pass | 0 | n/a | boolean from first 30m vs prior VA, not drive/test-drive/rejection-reverse/auction labels
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

n = 152. pass = 80. fail = 23. unbuilt = 31. not-measurable = 18.

## Why 31 are unbuilt

Unbuilt means SPEC or wiki names the id and there is no function and no report. It is not a failed build. The 31 rows are named upgrades (or a later-phase object) that tickets 01–09 never wrote.

| group | n | ids |
|---|---|---|
| path upgrades | 6 | `balance.body-ratio`, `balance.vp-shape`, `corr.am-pm`, `edge.clean`, `window.1030`, `window.1600` |
| EV / extension / SessionStat upgrades | 15 | `env.ev.{p75,p90,rv20,gk20,yz20,har,iv,vix16}`, `env.ext.{050,100,133.from-eq,133.from-origin,133.from-edge.london}`, `env.ss.{medHL60,minavg60}` |
| Phase 3 | 1 | `pz.learned` (deferred on purpose) |
| vol SPEC faithful with no report | 3 | `vol.yz20`, `vol.skew25`, `vol.vx.slope` |
| flow extras | 2 | `flow.bigtrade.30-60`, `flow.ofm.sequence` |
| value upgrade | 1 | `value.vp.rth.ohlc1m` |
| fail extras | 2 | `fail.box.gb.hour.gb.c5`, `loc.gp` |
| options gamma | 1 | `value.node.gamma.ndx.top3` |

Faithful objects that do have reports are not in this list. `vol.rv20`, `vol.gk20`, and `vol.har` are built. The three missing vol rows are in SPEC §5 as faithful and were never implemented.

