# RULES.md — sourced recipe rules for Phase 1 objects

Planning only. This file names, from the sources, every location, operating framework, trigger, filter and invalidation that is computable on the data we hold, every recipe an author actually states, the one-slot swaps allowed off each recipe, and the gate that keeps discovery behind scores. It does not start the runner and it does not add a ticket. Inventory rule: if a source (live wiki, Jumbo PDFs and tweets, Green Bird pack, discretionary PDFs, conversation user turns, Pine and indicator files) states it and it is computable, it is here; anything not traceable to a source is not here.

## Source-fidelity audit (2026-09-10)

Every recipe in section B was checked against the citations on its row (PDF page, wiki page, pack line, Pine line). Verdicts: faithful = the row states the source's own location, trigger, filter and invalidation; compressed = the row dropped or substituted part of the source's setup; unsourced = no source states it; blocked = the source's trigger is a tape flag that FINDINGS marks untrusted or that MBP-1 cannot measure. Rows marked compressed were rewritten below; none was deleted; no row is unsourced.

| recipe id | verdict | action |
|---|---|---|
| R-J01–R-J24 | faithful | keep (R-J13 rests on the X pack, tier 3; R-J17 on the findings reconstruction of screenshots, tier 2) |
| R-J25 | compressed | rewritten as an observation row: the tweet describes retraces to swing midpoints, it states no setup, so no trigger is claimed |
| R-G01–R-G09, R-G11 | faithful | keep |
| R-G10 | faithful (pack inference from a chart, HIS CHART) | keep, tagged |
| R-A01–R-A18 | faithful | keep |
| R-F01, R-F03–R-F05, R-F10–R-F18 | faithful | keep |
| R-F02 | blocked | CVD divergence trigger; kept as blocked until CVD is rebuilt |
| R-F06 | compressed | rewritten: the source's absorption is no-follow-through + reloading size + delta; the reload part is blocked, the other two are scored |
| R-F07 | blocked | iceberg reload trigger; kept as blocked |
| R-F08 | compressed | rewritten: the invented stand-in for the CVD-median check is removed; that component is blocked |
| R-F09 | compressed | rewritten: stage 2 replenishment is BBO reload and is blocked; stages 1, 3, 4 stay pending |
| R-R01–R-R03 | faithful | keep |
| R-R04 | blocked | SMT trigger; kept as blocked until SMT is rebuilt |
| R-S01, R-S02, R-S04–R-S09 | faithful | keep |
| R-S03 | compressed | rewritten: the refresh-consistency tell is split into its print side (pending) and its reload side (blocked) |
| R-P01–R-P04, R-P07–R-P20 | faithful | keep (recompute rows; every hardcoded table was opened in the Pine file) |
| R-P05 | faithful | line cite corrected to the counter loop `:875–960` |
| R-P06 | compressed (citation) | the first-hit numbers live in `NQ Statistical Mapper.txt:283–366`, not in the levels file; citation and quoted cells corrected |

## 0. Contract

### 0.1 The five slots

| slot | what it is | what it is not |
|---|---|---|
| **LC Location (price)** | a price, band or box computable before the touch, with a `known_at` | a behaviour rule, a day label, a regime |
| **OF Operating framework** | how a source says to behave at a location (accept vs reject, initiative vs responsive, open type, balance vs imbalance, sweep + fail-back, delta divergence, profile rotation, and every other distinct rule below) | a price; a single flag that compresses several authors |
| **TR Trigger** | the event, computable from bars or tape, that says "now" | a location or a filter |
| **FL Filter** | a per-session or per-touch condition that admits or excludes the recipe | a trigger |
| **IV Invalidation** | the rule that ends the idea: close through, hold outside, opposite edge, time, print broken | a target by itself (targets are outcomes in Phase 1) |

Kept distinct on purpose: AMT is an operating framework and is never listed as a location; TPO poor high / low, excess and single prints are **structures** (locations of a specific kind); prior-day, IB, session and RTH profiles are **profile locations**; day types, open types, gamma regime and VIX bands are **filters**.

### 0.2 Tags and the trigger-eligibility gate

- `[wiki:id]` id already defined on a wiki page (`wiki/index.md`, `SPEC.md` §5). `[new:id]` computable from a source but not yet registered; registering it is a wiki edit, listed in A7. `[not-measurable]` per `QUESTIONS_RESOLVED.md`. `[tier N]` follows the wiki citation key; assistant proposals in conversations are tier 4 and only ever appear in D3.
- **Tape-trust gate (from `FINDINGS.md`).** A tape-derived flag whose FINDINGS row says `tape trusted? = no` cannot occupy the TR slot until it is rebuilt and re-measured. Rows: `flow.cvd.trade` (sign nonzero every session), `flow.smt.trade.nq`, `flow.smt.ohlc.4` (fire every session), `flow.absorption.B` (fires every session), `flow.bigtrade.q90` (q90 = 3 lots). Eligible tape triggers today: `flow.absorption.A`, `flow.bigtrade.100ny`, `flow.bigtrade.75ldn` (`tape trusted? = yes`). Tape objects with no FINDINGS row (`value.delta.rth.trade`, `flow.footprint.diag.4x`, `flow.refill.ontouch`, `flow.ofm.sequence`, `flow.cvd.{ohlc,part.*,gamma}`, trade-visited `value.tpo.rth.30m`, and every `[new:flow.*]` below) are `[unmeasured]`: usable as locations, blocked as triggers until they print a FINDINGS row. Bar-grid events (touch / reject / hold / break / fail-back on 1-second and 1-minute bars, `wiki/touch-reject-hold-break-grid.md`) are not tape objects; their FINDINGS rows read `no` only because the column asks about Phase 2 tape promotion. They stay eligible triggers. If the stricter reading is intended, every recipe below still stands with its bar-grid trigger replaced by one of the three trusted tape triggers, which is a listed swap.

### 0.3 Citation key

Keys from `wiki/index.md` are reused unchanged: `[TBR p.N]`, `[XF p.N]`, `[SS p.N]`, `[FIND p.N]`, `[JJX L#]`, `[GB L#]`, `[PACK L#]`, `[PINE file:L#]`, `[INV L#]`, `[DTM L#]`, `[DRFL L#]`, `[CEX L#]`, `[CRAW A#]`. Page numbers are PDF page indices (cover = p.1); on the Ether / Ethos PDFs they equal the printed footer.

| key | file under `sources/documents/discretionary/` |
|---|---|
| `[AMT1]` | amt-lesson-1.pdf (14 pp) |
| `[AMTL]` | amt-on-live-markets.pdf (14 pp) |
| `[MAMT]` | mastering-amt-vp.pdf (27 pp) |
| `[MATH]` | the-math-behind-auction-market-theory.pdf (16 pp) |
| `[TPO]` | tpo-lesson-3.pdf (10 pp) |
| `[VP2]` | vp-lesson-2.pdf (9 pp) |
| `[RTVP]` | reading-the-volume-profile.pdf (13 pp) |
| `[FP8]` / `[FP9]` | fp-lesson-8.pdf / fp-lesson-9.pdf (8 pp each) |
| `[VWAP]` | vwap-lesson-10.pdf (9 pp) |
| `[DOM5]` / `[DOM6]` / `[DOM7]` | dom-lesson-5/6/7.pdf (8 pp each) |
| `[ABS]` | your-mistakes-with-absorption.pdf (14 pp) |
| `[STOP]` | stop-re-entering.pdf (17 pp) |
| `[RD]` | reading-delta.pdf (11 pp) |
| `[WIC]` | whos-in-control.pdf (12 pp) |
| `[TRAP]` | trapped-buyers-one-retest.pdf (13 pp) |
| `[BIG]` | only-trade-big-trades.pdf (19 pp) |
| `[OFM]` | origin-of-the-move.pdf (19 pp) |
| `[REF]` | refill-effect.pdf (24 pp) |
| `[GEX]` | gex-framework.pdf (22 pp) |
| `[VIX4]` | vix-lesson-4.pdf (10 pp) |
| `[C1]` / `[C2]` / `[C3]` | code-1-thesis.pdf / code-2-risk.pdf / code-3-orderflow.pdf (8 pp each) |
| `[NYAM]` | ny-am-session.pdf (12 pp) |
| `[K18]` | 18k-payout-session.pdf (15 pp) |
| `[K2345]` | 2345-funded-session.pdf (11 pp) |
| `[K10]` | 10k-first-month.pdf (16 pp) |
| `[ANAT]` | anatomy-of-a-losing-start.pdf (12 pp) |
| `[CONT]` | a-clean-continuation-short.pdf (14 pp) |
| `[AVG]` | average-unprofitable-trader.pdf (33 pp) |
| `[DATA]` / `[EMO]` | data-engine.pdf / emotion.pdf (process only; no price objects) |
| `[MVFL L#]` | `sources/documents/indicators/momentum-volume-flow-levels.txt` (the "institutional indicator" of `[CEX L17]`, tier 2) |
| `[OSF L#]` | `sources/documents/indicators/Open Source Fractal - Customized.txt` (same file as `[PINE Open Source Fractal - Customized.txt]`) |

### 0.4 Reading rules

1. Every recipe in B is one author's own framework + location + trigger (+ filter + invalidation as the author states them). Nothing is combined across authors inside B.
2. C changes exactly one slot of one recipe at a time. Variants add, they do not multiply.
3. D happens only after every B recipe and every C variant has a score line. Learned P-zones, free-form clocks, two-slot swaps, and every tier-4 proposal live in D3 until then.
4. Phase 1 scores are descriptive (touch / reject / hold / break / fail-back, reach of the author's target, time-to-touch, MFE / MAE in points from the author's invalidation distance), with `n` and Wilson 95% per `SPEC.md` §10. No P&L, no sizing, no account rules; management rows are recorded as invalidation and outcome definitions only.

---

## A. Slot inventories

### A1. Locations (LC)

#### A1.1 Clock boxes (H, L, open, close, EQ, Q25, Q75, and the projections of A1.2 on every box)

| id | window (ET) | source | status |
|---|---|---|---|
| `range.6-9.published` | 06:00–09:00 ONS, main NY model | `[TBR p.7, p.8]` `[XF p.7]` | wiki |
| `range.5-9`, `range.7-9`, `range.8-9` | 5–9 family, "any window 5–9 behaves similarly" | `[XF p.7]` `[PACK L49]` (08:00 line per `wiki/clock-grid-and-bars.md`) | wiki |
| `range.asia.2000-2030` | Asia opening range | `[TBR p.7]` | wiki |
| `range.midnight.0000-0030` | midnight opening range | `[TBR p.7]` | **new** |
| `range.london.0300-0330` | London opening range | `[TBR p.7]` | wiki |
| `range.london.00-03` | London TBR box into 03:00, same internals; 03:00 open analog, 06:00 handoff line | `[FIND p.4–5]` `[JJX L53]` `[XF p.40]` | wiki |
| `range.rth.0930-1000` | equities opening range (A period) | `[TBR p.7]` `[TBR p.16]` | **new** (outcome row `open.oneway.A.0930-1000` exists; the box itself does not) |
| `range.rth.1000-1030` | RTH AM second window | `[TBR p.7]` | **new** |
| `range.lunch.1200-1230` | lunch opening range | `[TBR p.7]` | **new** (comparison only; lunch is a documented leak `[XF p.21]` `[FIND p.5]`) |
| `range.moc.1500-1530` | MOC macro session | `[TBR p.7]` | **new** (comparison only) |
| `range.or.5m`, `range.or.15m` | 09:30–09:35 / 09:30–09:45, mid only | `[XF p.25, p.15]` | wiki |
| `range.ib` | 09:30–10:30 initial balance (A+B) | `[TPO p.8]` `[XF p.8]` (no edge) `[MAMT p.19, p.23]` | wiki, comparison row |
| `range.gb.nyam` | 09:00–10:00, events counted from 10:00 | `[GB L28–30, L178, L195–196]` | wiki |
| `range.gb.10-11` | 10:00–11:00 second NY box | `[GB L49, L449, L671]` | wiki |
| `range.gb.hour` | last completed 60 minutes | `[GB L32–33, L439–441, L685–687]` | wiki |
| `range.gb.asia` | ≈20:00–00:00 (HIS CHART, INFERRED) | `[GB L35–40]` | wiki |
| `range.gb.london` | ≈02:00–05:00 (INFERRED) | `[GB L48, L53–54]` | wiki |
| `range.on.1800-0930` | overnight high / low (ONH, ONL) | `[MAMT p.15, p.21]` | **new** |
| `range.dealing` | dealing range: band bounded by the last failed swing on each side (fractal swing, named approximation); the failure areas at each end are drawn as bands a few points tall, not lines (the shelf where a side held, the print span of the absorption there) `[ANAT p.7–9]` `[NYAM p.4]` | `[ANAT p.3]` `[K18 p.4]` `[CONT p.9]` | **new** |
| `range.4h.{18,22,02,06,10,14}` | 4H candle boxes | `[PINE 4H HOD LOD Checkpoint Analysis.txt:49–61]` | grid candidate only |
| gold 08:20 / Sunday 18:00, CL 09:00 | not NQ | `[XF p.8, p.34]` `[FIND p.6, p.10]` | not run (NQ only) |
| JJX families: NY end 09:30 starts {00,03,05,06,07,08,09}; London end 03:00 starts {20:00 prior,00,01,02} | derived-range search inside named families | `[JJX L177–199]` (assistant, tier 4) `[JJX L148]` (user) | D3 only beyond the rows above |

#### A1.2 Box internals and projections (per box)

| id / level | definition | source |
|---|---|---|
| H, L, EQ, Q25, Q75, range open (first print), range close (last print) | box internals | `[TBR p.4]` `[FIND p.12]` |
| `±0.5` each side (`-0.5` below the low, `+0.5` above the high) | half the range beyond either edge: H + 0.5·W / L − 0.5·W; every chart in the manual draws both sides (+0.5 … +2 above the high, −0.5 … −2 below the low) and the p.30 console labels the stat "Extended Range: ±0.5"; the reversal examples come from both sides (p.9 Trade #2 and p.13 Scenario #1 reverse from above the high, p.10 Trade #1 from below the low) | `[TBR p.5, p.8, p.30]` `[TBR p.9–10, p.13, p.20 chart labels]` `[FIND p.16]` |
| `lvl.mr.{0.1,0.2,0.3}` each side + `area.mr` | the "mean reversal levels": three lines between each edge and its ±0.5 at 0.1 / 0.2 / 0.3 of the range beyond the edge (H + k·W / L − k·W; the depths on the p.30 bar chart "Reversal % by Projection (Upper vs Lower)", the three dotted lines on the p.9–10 charts) and the shaded "area of mean reversal" from the edge to ±0.5 (p.20 shades the reversal between the high and +0.5); the exhaustion location is this area on the swept side, not only the ±0.5 line | `[TBR p.5, p.8, p.30]` `[TBR p.9–10, p.13, p.20 charts]` |
| `±1.0` each side | measured move, drawn as +1 / −1 on his charts | `[TBR p.10, p.13, p.21 chart labels]` `[FIND p.7]` |
| `env.ext.133.from-edge`, `env.ext.166.from-edge`, `band.133-166` each side | retracement / reversal **area** beyond either edge: the two levels and the shaded band between them, from the 6–9 box (London box when London is the clock); drawn below the low (`[TBR p.21]` band −1.33 … −1.66 with the reversal wick poking through −1.66; `[XF p.31, p.33]`; `[PACK L66]`) and above the high (`[TBR p.10]` +1.33 / +1.66; `[XF p.48]` "1.33 1.66 end of day max expansion" band above the high) | `[TBR p.21]` `[XF p.9, p.25, p.31, p.33, p.48]` `[PACK L66]` |
| `env.ext.133.from-origin`, `env.ext.133.from-eq` | coordinate alternatives read literally from the FIND replication fib list; not drawn on any Jumbo chart (named comparison only) | `[FIND p.16]` |
| `±2.0` each side (−2.5, −3 also printed) | outer ladder drawn by his indicator (+2 on p.10 Trade #2; −2 / −2.5 / −3 on p.13 Scenario #2) | `[TBR p.10, p.13 chart labels]` |
| `proj.overshoot.δ` | small overshoot past a printed level before the reversal: the charts draw the wick through −0.5 (p.10 Trade #1), through +0.5 (p.20 top-left), through −1.66 (p.21 reversal panel; XF p.31); no tolerance is printed → a touch counts with excursion ≤ δ, δ ∈ {2 ticks (`t2`), 0.1·W (the spacing of his mean-reversal ladder)} as named grid values | `[TBR p.10, p.20, p.21]` `[XF p.31, p.33]` |
| `proj.width.{w.69, w.london, w.own, w.ev}` | width base of every projection: `w.69` = H−L of the 6–9 box (faithful — every printed level is a multiple of it, "the coordinates are based on the 06:00 - 09:00 range and its levels"); `w.london` = the London box height when London is the clock; `w.own` = the clock's own box for the other published ranges; `w.ev` = the EV band width — **no source states an EV-width projection**; the only hint is the chart label "EVrange −60%" whose meaning is unverified, so `w.ev` is a named test variant, never the faithful row | `[XF p.47]` `[XF p.25]` `[FIND p.4]` `[TBR p.6–7]` `[PACK L24]` |
| `proj.level.{0.5, 1.33, 1.66, band.133-166, overshoot.δ}` each side | the explicit level test set for every Jumbo reversal recipe (RULES §C SL-proj); the faithful row of each recipe names which of these the source draws | this table |
| `bin.0940-0950`, `bin.0930-0950`, `bin.0950-1000`, `bin.1000-1030`, `bin.1030-1200` | reversal-time bins | `[TBR p.8, p.30]` `[XF p.15, p.47]` |
| windows 09:00–12:00 (3-hour "PO3"), AM 09:30–12:00, lunch 12:00–13:00, PM 13:00–16:00 | framing windows | `[TBR p.16, p.19, p.36]` `[SS p.10]` |

#### A1.3 Profiles (locations built from volume or time at price)

| id | scope | levels | source | status |
|---|---|---|---|---|
| `value.vp.rth.trade` / `value.vp.rth.ohlc1m` | prior RTH 09:30–16:00 | VAH, VAL, POC; VA 70 / 68 / 40 | `[AMT1 p.5]` `[RTVP p.4]` `[C3 p.7]` `[XF p.14]` `[TBR p.32–33]` | wiki |
| developing RTH VP | current session, known as-of each minute; VAH / VAL flagged lagging | `[MAMT p.4]` `[ABS p.7]` `[MATH p.9]` | wiki (developing variant) |
| `value.vp.eth.prior` + `lvl.mpoc.eth` | the previous ETH profile as the p.15–16 drawings define it: its high and low are labelled OVN HIGH / OVN LOW, so the profile is the overnight session 18:00–09:30 (the window of `value.vp.on`) with high, low, VAH, VAL, POC and the profile mid (MPOC, drawn above the POC as (high + low) / 2); the prior full-session 18:00–16:00 profile is a named variant, not the drawn object; the RTH profile carries the same landmarks | `[MAMT p.15–16, figures]` | **new** |
| `value.vp.on` | overnight 18:00–09:30 profile: single vs double distribution, ON LVN, ON shelf, ONVAH / ONVAL / ONVPOC | `[MAMT p.14, p.21]` | **new** |
| `value.vp.box69` | range profile of the 6–9 box (balance shape input) | `[XF p.44]` `[FIND p.8]` | wiki (overnight-only scope upgrade) |
| `value.vp.dealing` | VP of the current dealing range; its POC | `[CONT p.9]` `[RD p.9]` | **new** |
| `value.vp.composite.{5d,20d,250d}` | weekly / monthly / yearly composite HVN, LVN, shelves | `[VP2 p.6]` `[BIG p.10]` `[CONT p.7]` `[K10 p.12]` | **new** |
| `value.kz` | HVN, LVN, two-sided LVN, ledge (instant cut-off), shelf (taper), minor volume node, naked prior POC | `[VP2 p.3–6]` `[MATH p.13]` `[ABS p.6–7]` `[BIG p.10]` `[CONT p.4]` `[FIND p.7–8]` | wiki (minor volume node = local LVN; keep the name) |
| `value.tpo.rth.30m` | TPO POC / VAH / VAL; IB H/L at 10:30 | `[TPO p.3–4, p.8]` | wiki |
| TPO structures: `tpo.single`, `tpo.excess`, `tpo.poor.{high,low}` | single prints, ≥2 tail rows of one letter, weak / no tail | `[TPO p.5–7]` `[C3 p.6]` `[AVG p.30]` | wiki flags on `value.tpo.rth.30m` |
| `value.delta.rth.trade` | per-price aggressive buy − sell; `dp.max` / `dp.min` (delta print), taper into the extreme | `[XF p.14, p.23]` `[RD p.6–7]` `[TRAP p.4]` `[STOP p.9]` | wiki, `[unmeasured]` |
| `value.delta.weekly` | weekly delta profile print (who got trapped, who is covering) | `[K18 p.4]` `[K2345 p.4]` | **new**, `[unmeasured]` |
| `flow.delta.spike` | per-price delta spike at VAH / VAL where control changed hands, recorded as spike sign × extreme × outcome direction (the lesson's two examples are both buy-delta spikes: absorbed at VAH, regaining control at VAL, so the sign does not identify the absorbed side) | `[ABS p.10–11]` | **new**, `[unmeasured]` |
| `lvl.prior-rth.q{25,50,75}` | prior-day RTH quadrants | `[DTM L19]` (user; no DRFL user turn states the quadrants — the earlier `[DRFL L906]` pointed at a file-attachment stub) `[TBR p.32]` | **new** |
| `lvl.pclose`, `lvl.popen`, `lvl.halfgap`, `lvl.pib.{high,low}` | prior close / open; the half gap of the *session* gap — the p.22–23 rows are "1/2 Gap of pHOD Touched" for opens above the prior range and "1/2 Gap of pLOD Touched" for opens below it, i.e. (pHOD + open) / 2 and (pLOD + open) / 2, with the close-based half gap as a named variant; prior IB | `[MAMT p.21–23]` | **new** (touch-rate rows) |
| `lvl.owed.nearest` | nearest unfinished business above / below: naked POC, single print, poor extreme, leftover session H/L | `[TPO p.5–9]` `[VP2 p.6]` `[FIND p.5, p.9]` `[ANAT p.10]` `[K10 p.12]` | **new** (derived list) |

#### A1.4 Envelopes

| id | construction | source | status |
|---|---|---|---|
| `env.ev.{mean60,median60,p75,p90,rv20,gk20,yz20,har,iv,vix16}` × `ref.*` | AM expected-move band | `[XF p.7]` `[PACK L17–31]` | wiki |
| `env.ss.{avgHL60,medHL60,minavg60}` + projections | SessionStat 09:00–12:00 | `[SS p.6, p.10]` `[XF p.19, p.45]` | wiki |
| `env.ss.rth.avgHL60` | SessionStat 09:30–16:00 | `[SS p.10]` | **new** |
| `env.ss.weighted60` | weighted-average variant (formula not printed) | `[SS p.3, p.6]` | wiki (named variant) |
| `pz.approx.A`, `pz.approx.B` | disclosed P-zone approximations | `[XF p.28–30]` `[FIND p.7–8]` | wiki |
| `env.tbr.sigma025` | ±0.25σ of 20-day daily % stdev, touch → reversion to open by 12:00 | `[PINE AM TBR - NQ Stats.txt]` | **new** (tier-2 recompute) |
| `env.pine.manip.{avg,median,p25,p75}` | manipulation / distribution excursion from the open (AMD phase envelope) | `[PINE Statistical OHLC Projections HTF.txt:141–158, 322–341]` | **new** (tier-2 recompute) |
| `env.pine.sessionstat.P10-P90` | Session Statistical Levels percentile bands | `[PINE Session Statistical Levels.txt]` | grid candidate |
| `env.vwap.eth.sd{1,2}` (faithful) / `env.vwap.rth.sd{1,2,2.5,3}` | session VWAP ± volume-weighted SD on both sides (upper band = premium, lower = discount); median = "POC of the session so far"; the lesson's settings tab reads Anchor Period = Session with bands #1 = 1 and #2 = 2 ticked and #3 off, and its chart runs the bands through the overnight hours, so the drawn object is the exchange-session (18:00 ET reset) VWAP with ±1 / ±2; the 09:30 anchor and the 2.5 / 3 multipliers are named from the text; no Pine file is a source for this object | `[VWAP p.3–4, p.7–8]` (p.3 chart, p.8 screenshot) | wiki (`sd2`), **new** (eth anchor; 1, 2.5, 3) |
| `env.vwap.anchored.{swing,event,session,weekly,monthly}` | VWAP anchored at a swing, an event (CPI / FOMC / open), or a week / month | `[VWAP p.7]` | **new** |
| VIX → expected daily move: Expected Daily Move (%) = VIX / √252 (p.3 figure) with the ES point anchors 12.5 ≈ 30, 16 ≈ 50, 22 ≈ 95 (p.4, "typical") | expected daily range in % of price, applied to NQ as price × VIX / √252 (VXN, the Nasdaq-100 twin, named `[INV L610]`) | `[VIX4 p.3–4]` | filter input, not a level |

#### A1.5 Flow-built prints (tape locations)

| id | construction | source | status |
|---|---|---|---|
| `flow.absorption.A` price | q90 2-min aggressive volume at a level, ≤2-tick advance, ≥0.25R reversal | `[ABS p.8–9]` `[MATH p.8]` `[TBR p.31]` | wiki, trusted |
| `flow.absorption.B` price | BBO reload ≥50% within 500 ms, ≥2 repeats | `[DOM6 p.6]` `[DOM7 p.4]` `[JJX L159]` | wiki, tape-trusted no |
| `flow.absorption.candle.jumbo` | small body + volume ≥ k × 14-period average (k unpublished → named grid; MVFL uses 2.5 × avg20) | `[TBR p.31, p.35]` `[XF p.44–46]` `[MVFL L40–41]` | **new** (bar object) |
| `flow.bigtrade.100ny` / `75ldn` / `30-60` / `q99` | single prints ≥ threshold; Ethos 30–60 on a 40-range chart, adjusted with session volume | `[XF p.25]` `[BIG p.3]` `[OFM p.4]` | wiki, 100/75 trusted |
| `flow.refill.zone` | band built by a burst of large aggressive prints ("sixty, eighty, a hundred contracts hitting in seconds"; per-print and burst-total readings both printed; the paper pools NQ and MNQ and its only sized figure is MNQ with prints ≥ 40 shown, so the contract unit is unstated); width, print count, session location | `[REF p.5, p.7–8, p.23]` `[OFM p.2]` | **new** (the wiki has the event `flow.refill.ontouch`) |
| `flow.ofm.catalyst` | the OFM line at the lowest (highest) first absorbed aggression print, with the cluster of absorbed aggression boxed behind it; long and short both drawn | `[OFM p.2, p.5–10, p.14]` `[BIG p.7]` `[CONT p.10]` | **new**, `[unmeasured]` |
| `flow.footprint.diag.4x` (3×), `flow.footprint.stack3` (stack ≥3, 2 named) | diagonal imbalance ask(p) vs bid(p−tick); stacked = unfinished auction magnet | `[FP8 p.5–6]` | wiki / **new** |
| `flow.footprint.imb350` | same-price 350% buyer / seller divergence line (sell and buy mirrors); marked only where it sits at the same price as aggression; the live tool prints it as a box with a height (the price span of the rows meeting the condition, named), a line is the reduced form `[K2345 p.5]`; on the BigTrades charts the marked level is a small box around the print's candle with the line running off it `[BIG p.3, p.5]` | `[BIG p.3, p.5]` `[K2345 p.5]` | **new** |
| `flow.candle.poc`, `flow.candle.poc.flip` | per-candle max-volume price; flip = POC jumps to the other side of the candle | `[FP9 p.5]` `[FP8 p.6]` | **new** |
| `lvl.protected.{high,low}` | swing extreme whose defending delta print held and that price has stopped retesting | `[RD p.4–5]` `[K18 p.8]` `[ANAT p.3]` | **new** |
| `flow.delta.zone.kmeans` | k-means (k=4 per side) zones of delta events ≥6× avg-50 delta (floor 3000), min thickness 0.4 ATR-14 | `[MVFL L19–37, L181–411]` | **new** (tier-2 rebuild on aggressor delta `[CEX L33]` (assistant, tier 4) after the user's upgrade mandate `[CEX L17]`) |
| `flow.vol.anomaly.zone` | bar volume >2.5× avg-20 → zone 0.2% of price, merged within 0.5% | `[MVFL L39–46, L98–176]` | **new** (bar object) |

#### A1.6 Candle objects

| id | construction | source | status |
|---|---|---|---|
| `block.sweep.tbr.3m` (2 / 3 / 5 m) | C2 sweeps C1, C3 closes beyond C2; block = C2 wick; aggressive stop at OB midpoint, conservative at OB low | `[TBR p.27–28]` | wiki |
| rejection block | sweep-candle wick; closure above the sweep candle confirms | `[TBR p.29]` | wiki (block page) |
| `cisd.fractal.literal` | opposing-run change in state of delivery as coded, causal replay | `[OSF L1–118, L306–342, L523–951]` `[PINE HTF Sweep Model with CISD Table.txt:112–179]` | wiki |
| `gap.fvg.first.clock`, `gap.body.adjacent` | first three-bar wick gap per hour; body gap ≥4 ticks | `[TBR p.33, p.35]` `[PINE First presented FVG…:81–85,148–170]` `[PINE 8020 System.txt]` | wiki |
| H1 / M15 imbalances as draw | PD RTH Range+ confluence | `[TBR p.33]` | wiki (HTF FVG variant) |

#### A1.7 Green Bird levels

| id | definition | source | status |
|---|---|---|---|
| `box.gb.nyam`, `box.gb.10-11`, `box.gb.hour`, `box.gb.asia`, `box.gb.london` | box edges as in A1.1 | `[GB L28–54]` | wiki |
| `box.prior-rth` (PDH / PDL) | previous day high / low, confluence | `[GB L64, L141]` `[TBR p.32–34]` | wiki |
| `lvl.tdo` | first print of 00:00 ET | `[GB L24–26, L142]` | wiki |
| `lvl.nwog` | Friday close (the session's last 1-minute close before 17:00, "Friday's close" `[GB L60, L69]`) vs Sunday 18:00 open; the 15:59 RTH close and the 17:00 settlement are named endpoint variants; destination, not entry | `[GB L59–60, L68–69, L155, L615–621]` | wiki |
| `lvl.0930open` | cash open; 9:30 manipulation reference | `[GB L30, L56–57, L90]` | wiki |
| `loc.gp` | 50–61.8% of the completed impulse (NYAM high→low or HTF swing) | `[GB L73–76, L255–263]` | wiki |
| `loc.pd50` | 50% premium / discount split of the impulse | `[GB L144, L292–296]` `[XF p.44]` (PD RTH box, demoted) | **new** (location variant of `loc.gp`) |
| `lvl.1800open` | 18:00 daily open (NWOG endpoint; Pine daily-open line) | `[PINE Sessions & VP with prev session VP & daily weekly opens.txt]` `[GB L60]` | **new** |
| CPI high / low boxes, 7:30 NY true open, "above TDO = short" | excluded | `[GB L50–51, L310]` `QUESTIONS_RESOLVED §45` | excluded |

#### A1.8 Options nodes

| id | definition | source | status |
|---|---|---|---|
| `value.node.oi.{ndx,ndxp,spx,spxw}.top3` (+ qqq, spy, nqopt) | top-3 OI strikes above / below spot at 09:25, dte ≤14 | `[GEX p.14, p.16]` `[DRFL L10, L325, L906]` `[INV L297–380]` | wiki |
| `value.node.gamma.<product>.top3` | \|gamma × OI\| nodes | `[GEX p.16]` `[DTM L21–22]` | wiki |
| `value.node.flip.<product>` | zero-gamma level: the text says "where net dealer gamma crosses from positive to negative" and the p.7 bar chart marks GFlip where the per-strike bars change sign (red → green); three named readings printed side by side — aggregate net GEX root as spot moves, cumulative-sum-over-strikes root (the retained code), per-strike sign change (the chart) — sign scenario named | `[GEX p.7, p.15]` `[DTM L21–22]` (user) `[CEX L86]` (assistant) | wiki upgrade |
| `value.node.{callwall,putwall,maxpain}.<product>` (+ `.rank{1,2,3}`) | text: largest call gamma above, largest put gamma below, min option value strike; the p.13 chart draws three ranked call walls (▲ 740, ▲▲ 732, ▲▲▲ 730 against spot 731.98 — the third sits below spot) and the p.15 panel prints put wall = max pain (715 = 715), so the drawn object is the ranked top-3 set per option side on either side of spot and the one-per-side text rule is its faithful reduction; the p.7 / p.15 panels also mark a "Vol Trigger" level and print OI-GEX beside VOL-GEX (volume-weighted) and a dealer hedge flow "per 1 % move" — none defined in the text, recorded, not built | `[GEX p.7, p.13, p.15]` | **new** |
| KG1 levels, GEXRADAR hedging-pressure gauge, Vol Signals nodes, Skylit | vendor engines | `[K10 p.6]` `[GEX p.15, p.22]` `[DTM L21–25]` | not-measurable; our nodes are the disclosed substitute |

#### A1.9 AMD as area or phase

No source draws an "AMD zone" box. Sourced uses: (a) phase framing, 09:00–12:00 read as a 3-hour PO3 candle with accumulation = build window, manipulation = Judas leg, distribution = move to projections `[TBR p.6, p.16, p.19]`; (b) the 9:30 manipulation sweep below the open `[GB L30, L90]`; (c) "walking the dog" = manipulation of the box, then the real move `[FIND p.11]` `[XF p.31]`; (d) manipulation / distribution excursion statistics from the open `[PINE Statistical OHLC Projections HTF.txt]`. Computable objects: phase labels `phase.amd.{acc,manip,dist}` on the 6–9 → 09:30 → projection path (a relabel of `path_class` + `judas.depth.*`, no new geometry) and the envelope `env.pine.manip.*` in A1.4. Nothing else is claimed.

### A2. Operating frameworks (OF)

One row per distinct behaviour rule a source states. Each produces a computable per-session or per-touch label (right column) so recipes in B can name it.

| id | author | rule (as stated) | label / object it produces | source |
|---|---|---|---|---|
| OF-J1 | Jumbo | Judas / false-breakout reversal: sweep of a box edge extends into the exhaustion area beyond **that** edge — the mean-reversal lines 0.1 / 0.2 / 0.3 and the ±0.5 projection (`area.mr`), or a P-zone / SessionStat / EV level sitting there, with a small overshoot allowed — then reverses through EQ toward the untouched edge; drawn on both sides (reversal from above the high on p.9 Trade #2 and p.13 Scenario #1, from below the low on p.10 Trade #1); A+ = done before 10:00 | `judas.depth.any`, `judas.depth.mr` (excursion enters the mean-reversal area), `judas.depth.-0.5`, side label, reversal-bin label | `[TBR p.5, p.6, p.8, p.20]` `[TBR p.9–10, p.13 charts]` `[FIND p.4, p.7]` `[XF p.29, p.48]` |
| OF-J2 | Jumbo | Single break: one edge taken, opposite edge clean; entries from EQ / quadrants / range open; 09:40–09:50 is continuation or add, not a fade | `path_class` single-high / single-low, `single-extended` / `single-purged` | `[TBR p.12]` `[FIND p.4, p.7]` `[XF p.12]` |
| OF-J3 | Jumbo | Open-location switch: RTH open inside prior value / range → mean-reversion morning (fade, EQ / EV targets); outside both with above-average RVOL → discard mean reversion and double-break fade | `open_cell` (27), `rvol_0930` | `[XF p.8, p.10, p.16–17]` `[PACK L35–44]` `[FIND p.6–7]` |
| OF-J4 | Jumbo | Range-size / balance classifier: width % bins drive double vs single break; balanced vs imbalanced overnight; already-purged edges; sister indices | `width_pct`, `balance`, `edge_clean`, `day_type` | `[XF p.7, p.23–24]` `[FIND p.6–7]` `[JJX L56]` |
| OF-J5 | Jumbo | AM / PM rotation and the 1.33–1.66 fork: AM consolidation → PM expansion to higher projections; AM expansion → PM consolidation between AM levels; the 1.33–1.66 **area** (both levels and the shaded band between them, on whichever side the AM leg ran — below the low on p.21 / XF p.31 / p.33, above the high on XF p.48) continues AM or reverses the whole AM through PM; the reversal wick may overshoot 1.66 slightly (p.21 reversal panel) | `corr.am-pm`, `ext_133_touch`, `ext_166_touch`, `band_133_166_touch` after 12:00, side label | `[TBR p.10, p.21, p.36]` `[XF p.31, p.33, p.48]` `[FIND p.5–6]` |
| OF-J6 | Jumbo | Market conditions: CPI / NFP / FOMC weeks lower expectations; extended overnight → targets limited to range H/L until lunch; range-bound → inner levels, scalps; expansive → higher projections, re-entry plausible; unfavourable days AM off-limits, PM has the moves | `cal.redfolder`, `cond.{extended,rangebound,expansive}` | `[TBR p.22–24]` |
| OF-J7 | Jumbo | Delayed cycle 2: on 10:00 release days the real reversal comes after the release, not 09:40–09:50 | `cal.1000release`, reversal bin shift | `[TBR p.18]` `[FIND p.10]` |
| OF-J8 | Jumbo | Failure recognition: no rejection signature at the projection, continuous momentum, extended bodies, time-window violations, 3-strike rule, volume divergence → setup failed, exit and observe, switch to single-break or PM | `fail.{norejection,extendedbody,3strike,window}` | `[TBR p.37]` |
| OF-J9 | Jumbo | London TBR: same geometry ending at 03:00 with the London box height as the width base (`w.london`): ±0.5 area each side, London 1.33–1.66 area each side ("London range exhaustion (1.33-1.66) longs" = the band below the London low); London H4 SessionStat + absorption at the reversal; which session is clean this cycle is an input | `range.london.00-03` labels, `label.clean.session.rollingN` | `[FIND p.4–5, p.9]` `[XF p.25, p.40, p.46]` |
| OF-J10 | Jumbo | Unfinished business: leftover Asia / London / RTH highs and lows are the draw after the 09:40 reverse; lines deleted once purged; not an entry | `lvl.owed.nearest`, purge deletion | `[TBR p.11, p.33–34]` `[XF p.30, p.33, p.48]` `[FIND p.5, p.9]` |
| OF-J11 | Jumbo | PD RTH Range+: only RTH price action counts; ETH sweeps are disregarded; wait for RTH open to show direction; prior RTH H/L and M15 / H1 imbalances are draws on liquidity | `box.prior-rth` reach labels | `[TBR p.32–34]` |
| OF-J12 | Jumbo | Confirmation stack at location: reclaim / 3-candle, absorption candle or imbalance in it, delta taper, VP shelf, BigTrades ≥ threshold; one alone is not a trade | confirmation count at the touch | `[TBR p.31, p.35]` `[XF p.23, p.25, p.27, p.45]` `[FIND p.3, p.9, p.12]` |
| OF-J13 | Jumbo | Management leaks (recorded as invalidation / exit definitions): front-run exit at range-mid rejection; one-and-done in the first 20 min; flip after the first idea dies at the level; lunch is not A+; BE at 09:50 while location is valid is a leak | exit-reason labels | `[XF p.3, p.15, p.21, p.26]` `[FIND p.10–12]` |
| OF-J14 | Jumbo | Statistical framing: all stats inside 09:00–12:00; 86.46% is a location stat, not P(win), and it is two-sided — the p.30 console labels it "Reversal Percentage from Extended Range (±0.5)" while the text says "at the -0.5 projection", and the p.30 bar chart prints reversal % per depth 0.1 / 0.2 / 0.3 / 0.5 for the upper and the lower side separately (lower ≈ 87 / 82 / 78 / 70, upper ≈ 85 / 80 / 74 / 66, read from the render) with two average reversal times (original range 09:47:36, extended range 09:51:05); the recompute prints both readings (reversal at the ±0.5 line; reversal from inside the edge → ±0.5 area) on both sides | recompute rows (per side, per depth) | `[TBR p.30]` `[XF p.47]` `[FIND p.10]` |
| OF-G1 | Green Bird | Failed breakout / failed breakdown of a session or hour box: sweep, cannot hold, back inside → trade toward the opposite edge; a sweep alone is not a signal | `fail.<box>.gb.c5`, `label.aplus` | `[GB L85–88, L109–119, L188–246]` |
| OF-G2 | Green Bird | Wait for the box to close: NYAM traded only after 10:00; 09:45 entry called early | event clock ≥10:00 | `[GB L29–30, L178, L195–196, L633]` |
| OF-G3 | Green Bird | Confirmation = 5-minute close back through the level (box edge, TDO, PDL), then "wait a few points" | `grid.gb.c5` | `[GB L26, L89, L210, L324, L503]` |
| OF-G4 | Green Bird | 9:30 manipulation: sweep below the open, reclaim, long toward discount | reclaim label at `lvl.0930open` | `[GB L30, L56–57, L90]` |
| OF-G5 | Green Bird | TDO is confirmation and magnet, never a standalone long / short switch; failures that close through TDO on the 5m are the ones he takes | `tdo_touch`, close-through label | `[GB L24–26, L51, L612]` |
| OF-G6 | Green Bird | NWOG is the destination: fresh gap Sunday 18:00; close the trade when the gap is tagged; Monday = NWOG day | `nwog_fill` | `[GB L59–60, L68–69, L615–621, L673–675]` |
| OF-G7 | Green Bird | Golden pocket: bias first, retrace into 50–61.8%, clean rejection / failure, then the trade; invalidation above the zone | `loc.gp` touch + reject | `[GB L73–81, L249–296]` |
| OF-G8 | Green Bird | Overnight sweep-and-reclaim sets next-day bias; during NYAM buy pullbacks into discount / pocket rather than fading a fresh range | overnight reclaim label | `[GB L313, L443–450, L543–544]` |
| OF-G9 | Green Bird | Confluence stacking: PDH / PDL, TDO close, golden pocket, MTF agreement raise the grade; B+ (no sweep) is not the model | confluence count | `[GB L146–147, L242–245]` |
| OF-G10 | Green Bird | Path of least resistance on chop days: repeat the fade at every failed pop on the heavy side | one-way-pressure label | `[GB L91, L669–671]` |
| OF-G11 | Green Bird | Bodies tell the story, wicks do the damage: body closes decide failure; wickless bottom is suspicious | body-vs-wick break variants | `[GB L92, L158, L622]` |
| OF-A1 | AMT (Sires / Saint) | Balance vs imbalance; rule one: inside balance the extremes hold, fade edges toward POC until acceptance outside; the charts draw the extremes as bands touched on both sides (`[AMT1 p.9]` rule-one chart) and every failed auction as a red box at an excursion beyond VAH or beyond VAL that comes back inside, no hold (`[MAMT p.5, p.8, p.10]`) | balance state, `label.amt.day`, excursion-return share per side | `[AMT1 p.4, p.9]` `[AMTL p.3]` `[MATH p.14]` |
| OF-A2 | AMT | Rule two: out of balance, the ledges of the prior balance carry the move (support becomes resistance) | ledge retest label | `[AMT1 p.9]` `[MAMT p.12]` |
| OF-A3 | AMT | Acceptance vs rejection at an extreme: acceptance builds volume outside and holds the retest; failed auction is quiet on the break, wicks, snaps back within a few rotations | accept / reject label (grid hold vs reject) | `[AMT1 p.8]` `[AMTL p.5–6, p.13]` |
| OF-A4 | AMT | Failed auction, loose 80%: break out, re-enter prior value → traverse to the other side about 80% (72–80%) | traverse outcome | `[AMT1 p.7]` `[AMTL p.8–9]` `[ABS p.12]` `[MAMT p.5]` |
| OF-A5 | AMT | Failed auction, strict rule: open outside prior VA, two consecutive 30-minute periods inside → 80% full traverse | `label.amt.80pct.two-period` | `[MAMT p.18]` |
| OF-A6 | AMT | POC tell for 80 / 20: repeated failure to hold through POC → the chop case; aggressive push through POC with a retest that holds → the traverse case | POC-hold count | `[AMTL p.9]` `[RTVP p.5]` |
| OF-A7 | AMT (MAMT) | The Failed Auction setup, narrow: balance → break → tag a prior balance's POC → rejection (MAMT: instant; `[AMTL p.10]`: a deep dip into the prior balance that still fails to hold) → target the *far* boundary of the established balance: its VAH after a downside break and a tag from above (`[MAMT p.11]` chart 1 marks "vah = target"), its VAL after an upside break and a tag from below; both directions drawn on `[MAMT p.10]` | setup flag with older-POC tag, tag-depth column | `[MAMT p.9–11, p.26]` |
| OF-A8 | AMT | Three entries on a balance boundary: break + retest → continuation; come back inside and re-accept → fade to the other side; traverse straight through → that side priced in | break-retest / re-accept / traverse labels | `[MAMT p.12]` `[RTVP p.6]` |
| OF-A9 | AMT | Higher-timeframe auction outranks the lower-timeframe trigger; inside balance near the lower boundary a short gets less leniency | HTF balance position | `[MAMT p.13]` `[MATH p.14]` `[WIC p.10]` |
| OF-A10 | AMT | Day types: trend (continuation only), normal (fade extremes to POC), normal variation (one push then fade), neutral (small size), non-trend (stand down); six-type Steidlmayer original | `label.amt.day` | `[AMT1 p.10]` `[MAMT p.18, p.20]` |
| OF-A11 | AMT | Open types in the first 30 minutes: drive (never fade), test-drive (level behind the risk), rejection-reverse (two-sided, rejection extreme is the reference), auction (balance day, fade early extremes) | `label.amt.open.30m` | `[AMT1 p.11]` |
| OF-A12 | AMT | Profile shape: D fade edges; P late in a rally / b late in a sell-off are warnings not signals; double distribution → each hump its own value, the bridge is the line; trending profile → nothing to trade; P / B shapes → read the range at the top / bottom for continuation (RTVP); `[MAMT p.7]` draws the opposite resolution — a P day "resolves with price breaking down out of the bottom", a B day higher — so the resolution direction is scored per author, never pooled | `balance.vp-shape` (D / P / b / B / trend / double), resolution direction per author | `[AMT1 p.6]` `[RTVP p.7–11]` `[MAMT p.7–8]` |
| OF-A13 | AMT | Overnight inventory: net long / short 18:00–09:30 carries into the open; the overnight LVN (double distribution) or shelf is respected or disrespected at the open | `on_inventory_sign`, `on_lvn_respected` | `[MAMT p.14, p.26]` |
| OF-A14 | AMT | Overnight statistics as timing context: ONH or ONL touched ~94%; open inside the prior ETH balance → that ETH profile's MPOC hit ~73% (the ETH profile of the p.15–16 drawings is the overnight session, its extremes labelled OVN HIGH / OVN LOW; MPOC is drawn as the profile mid above the POC); use as reasons not to take a level early | touch rows for A1.3 | `[MAMT p.15–16, p.21]` |
| OF-A15 | AMT / TPO | Unfinished vs finished business: fresh single prints and poor extremes pull; excess holds on first test; stack TPO with a VP shelf | structure touch outcomes | `[TPO p.5–9]` `[C3 p.6]` |
| OF-A16 | AMT / TPO | IB read: range extension = one side in control; IB holds all day = rotational (fade IB edges to POC); early one-sided break = trend | IB extension label | `[TPO p.8]` `[MAMT p.19]` |
| OF-A17 | VP2 | Trade the ledge, not the middle of the shelf; shelves and ledges are fixed, VAH / VAL / POC drift; naked POCs are targets; composite HVNs are heavyweight; stack with VWAP / VA edge / old POC | `value.kz` roles | `[VP2 p.4–8]` |
| OF-A18 | MATH | Participation = provide + withdraw + consume; imbalance is not an oracle, replenishment is the question; don't fade discovery; absorption needs high aggression + low response efficiency + holding-and-refilling opposite side; exhaustion = replenishment stops | state labels B / A / D / E / W at the touch (proxy) | `[MATH p.5–8, p.10]` |
| OF-A19 | MATH | Real extremes need a second transition: an LVN, shelf or ledge counts only with a return to balance behind it; VAH / VAL are lagging; trade the current auction, not last week's; HTF cycle first, LTF trigger second | `kz.two-transition` flag | `[MATH p.9, p.12–14]` |
| OF-A20 | C3 | Price stays in a balance, leaves it, or returns to a previous one; objectives are single prints and balances; avoid levels inside a balance; rejection from a balance with an unfilled single print above → bullish bias; acceptance below a balance → bearish; 40% VA intraday | bias label, `value.vp` VA 40 | `[C3 p.6–7]` |
| OF-F1 | Ethos DOM | Aggressive vs passive; delta is the running score; aggression with movement = continuation, aggression without movement = absorption | delta-vs-displacement label | `[DOM5 p.4–5, p.7]` |
| OF-F2 | Ethos DOM | Speed of tape and spread: fast tape into a level that holds = absorption worth trading; spread widening = liquidity pulling, do not lean on the level | `flow.tape.speed`, `flow.spread.width` (**new**, MBP-1) | `[DOM5 p.6]` `[OFM p.5]` |
| OF-F3 | Ethos DOM | Absorption vs exhaustion: big volume with no movement (someone is there, reverses harder) vs shrinking volume with no movement (nobody left, drifts); stopping volume | volume-at-stall label | `[DOM6 p.7]` |
| OF-F4 | Ethos DOM | Stacking shows intent, pulling shows fluff; iceberg reloads, spoof vanishes; behind-the-touch behaviour is not measurable with MBP-1, at-touch reload is `flow.absorption.B` | at-touch reload only | `[DOM6 p.5–6]` `[DOM7 p.4–7]` `[JJX L298–346]` |
| OF-F5 | Ethos footprint | Diagonal read; 3–4× imbalance; three or more stacked = unfinished auction magnet; candle POC is a magnet on the retest; prints matter only at your levels | A1.5 footprint ids | `[FP8 p.4–7]` |
| OF-F6 | Ethos footprint | Absorption = candle and delta disagree; POC flip = control changed hands; delta divergence (regular, exhaustion print); full stack = level → absorption → flip | `flow.candle.poc.flip`, divergence flags | `[FP9 p.3–7]` |
| OF-F7 | Ethos VWAP / CVD | Premium / discount by deviation: trades live beyond ±1, ideally at ±2, only with absorption (the lesson's chart draws the ±1 / ±2 bands on the exchange-session VWAP, upper = premium, lower = discount, both faded); CVD grades every move (divergence, breakout on flat CVD = fakeout, stall with CVD climbing = absorption zone); anchored VWAP convergence | VWAP band touch + absorption | `[VWAP p.4–7, p.9]` |
| OF-F8 | Ethos absorption (ABS) | Four checks: reward system (3-tick move within 3 ticks of the print; opposing side not refreshing; correct side of the CVD median); absorption only fades, never continues; location must be a real extreme (shelf, ledge, LVN, minor node, prior-day VA), never POC; effort → passive wall → no reward → second aggression; enter on the retest of the reward system; delta spike at VAH / VAL marks control change — in the lesson both spikes are buy-delta spikes, absorbed at VAH and regaining control at VAL, so the spike's sign does not identify the absorbed side | `flow.reward.3tick` (**new**), location class at print, spike sign × extreme × outcome | `[ABS p.3–13]` |
| OF-F9 | Ethos STOP | Three-step read: location → reward vs result → delta filter; absorption confirms in four stages (initial defence, replenishment ≥3 ticks, exhaustion of the aggressor's prints, lift-off); entry within 1–2 ticks of confirmation; re-entry passes every box from zero; 27% of absorptions fail without pacing confirmation | stage labels; `flow.digits.thinning` (**new**) | `[STOP p.6–15]` `[AVG p.24–26]` |
| OF-F10 | Ethos Reading Delta | Protected low / high: partial below the sellers who last defended, trail behind each new protected level; the highest delta print is the rewarded side; a large delta print at an LVN / minor node extreme gives repeatable intra-wick reactions | `lvl.protected.*`, dp.max side | `[RD p.4–9]` |
| OF-F11 | Ethos Who's In Control | How price arrives at the extreme (aggressive → expect defence; slow drift → expect break); a previous balance's break + retest confirms control; an aggressive push that fades on delta = trapped side that fuels the reverse; drop to 15 m for confirmation | `flow.approach.speed` (**new**), break-retest label | `[WIC p.3–10]` |
| OF-F12 | Ethos Trapped Buyers | Balance redrawn to fit price; extreme reached, not exceeded; heavy one-sided delta at the extreme = trapped positioning; a level that failed twice in prior sessions; intraday breakout then retest; target inside the session's normal range | prior-failure count, retest label | `[TRAP p.3–12]` |
| OF-F13 | Ethos BigTrades | Aggression = effort, the next candle = reward; body print = paid, wick print = absorbed; both sides absorbed = nobody in control, wait for the break; imbalance (350%) counts only at the same price as aggression; passive moves (no aggression on your side) are short-term swings | body / wick print class | `[BIG p.4–6, p.13, p.18]` |
| OF-F14 | Ethos BigTrades | Regime split: origin-of-the-move (drive after a failed squeeze, entered on the retest, thin volume behind, HTF rejecting) only in short gamma; balance-day fade (extreme where aggression failed, enter on the test back into it, target where the other side last had control) is the 80% case in long gamma | gamma regime × recipe | `[BIG p.7–11, p.14–16, p.18]` |
| OF-F15 | Ethos OFM | Squeeze catalyst (drawn as the OFM line at the lowest / highest first absorbed aggression, the cluster boxed) → release (speed of tape) → failure back through the catalyst → refill below (above) → re-squeeze entry on the retest of the failure area; stop beyond the aggression that built it; both directions drawn (longs OFM p.9 / p.14, shorts OFM p.7 / p.8 / p.10); passive variant (tape dies at the failure) | `flow.ofm.catalyst` line + box, `flow.ofm.sequence` stages | `[OFM p.4–14]` `[CONT p.10–11]` |
| OF-F16 | Ethos Refill (research) | Zone memory decides the touch: memory + location carry the signal (flow alone AUC 0.54); fade-every-touch loses; winners dip 18 ticks past the touch; be the resting order inside the zone, not the chase; the zone is a band built by a burst of large prints ("sixty, eighty, a hundred contracts hitting in seconds") on pooled NQ / MNQ data, the contract unit unstated | touch-grading features (memory, construction, location, flow) | `[REF p.8–12, p.16, p.23]` `[OFM p.15–16]` |
| OF-R1 | Ethos GEX | Gamma regime before the open, read two ways the lesson uses interchangeably and both printed — the sign of net GEX (positive = long gamma, p.6) and spot above / below the flip (p.7, p.19): above the flip = range / mean reversion (fade toward walls with absorption), below = trend / expansion (trade the break through walls with aggression); 0DTE drives the session; re-check after big impulses; vanna / charm drift toward high-OI strikes; at a wall the lesson names two location states — price approaching the strike (reject = pin and chop vs accept = break and squeeze) and price already at the strike (contained rotations vs trending away), read on both sides (p.14) | `gamma_regime`, distance to flip | `[GEX p.6–14, p.18–20]` |
| OF-R2 | Ethos VIX | VIX level sets expected range (the p.3 figure prints Expected Daily Move (%) = VIX / √252; the p.4 point anchors are "typical") and risk band; intraday ES-vs-VIX direction reads; pre-event rise, post-event crush; contango vs backwardation, VVIX; balance + VIX dropping → rotations, balance + VIX rising → expect the range break; range-completion (realized vs implied) → chop | `vix_band`, `vx_slope`, range-fuel | `[VIX4 p.3–9]` |
| OF-R3 | Ethos thesis (C1 / C3) | A bias needs an invalidation; it dies on structure break, value shift, or new information; thesis box validity; no direction in the thesis, only areas of reaction and an owed objective | `thesis.alive` band | `[C1 p.3–4]` `[C3 p.7]` `[ANAT p.4, p.10]` |
| OF-R4 | Ethos triad (C1) | IØD: a sister takes the AMT object first, the weaker index falls faster on the rejection; RFZ: a sister fills your single print first, read the reaction; correlated divergence = fade the over-extended leg | SMT at AMT objects (blocked until rebuilt) | `[C1 p.5, p.7]` `[CEX L129]` (user definition) |
| OF-S1 | Sires live | Refill trade: sellers absorbed at the bottom of the range, stop just below the buyers in control, target the HTF objective | absorption at range bottom + HTF owed level | `[NYAM p.4–5]` `[K18 p.11]` |
| OF-S2 | Sires live | A level rejected twice with no defence on the third retest is a low-risk trade that can still fail; refreshing size on the second defence is the tell that separates the two | refresh consistency count | `[NYAM p.6–7]` `[K18 p.7, p.11]` |
| OF-S3 | Sires live | Pre-file entry: small, deliberate, before confirmation, as buffer; not a conviction trade | entry class label | `[K18 p.5–6, p.14]` |
| OF-S4 | Sires live | Protected-high trailing (trailing convexity): stop moves only after price closes beyond the prior swing with real aggression; low starting R:R is not a reason to skip a strong level | `lvl.protected.*` sequence | `[K18 p.8–9, p.14]` `[NYAM p.8–9]` `[K10 p.9]` |
| OF-S5 | Sires live | Extreme absorption at resistance: CVD dying while price holds or drifts up = passive limits consumed and reloaded; a level currently being tested, not merely one that worked before | CVD-vs-price stall (blocked until CVD rebuilt) | `[K2345 p.6]` |
| OF-S6 | Sires live | All-time-high environment: neutral objective, wait for the pullback, trade within the directional push; 350% divergence box + small imbalance flags an OFM long where sellers were trapped before | `flow.footprint.imb350` + `value.delta.weekly` | `[K2345 p.4–5]` |
| OF-S7 | Sires live | Two independent reasons at one price (marked resistance + minor HVN, or own level + gamma level); stop above the rejection high; second-tap absorption long | confluence pair | `[K10 p.6–8]` |
| OF-S8 | Sires live | Thesis order: current auction (imbalance → new balance forming) → looked-left reaction history → objective at the HTF HVN / yearly POC; do not short into a demand level where sellers were absorbed | HTF-bias veto | `[K10 p.12–13]` |
| OF-S9 | Sires live | Re-entry only if price returns to the level; stop just past the level where the reason is gone; target = the HTF level owed; daily objective then stop; max loss half the objective | re-entry gate; `lvl.owed.nearest` | `[ANAT p.6–11]` |
| OF-S10 | Sires live | Continuation filter: every entry agrees with the HTF thesis; minor volume node + delta stacking against it; established balance top = default shorts unless a close above with extreme buying flips to retest longs toward VWAP; refill zone = same side winning more than once; squeeze (no failure) vs OFM re-entry (after a failed squeeze) | HTF bias, refill count, squeeze class | `[CONT p.4–5, p.8, p.10–13]` |
| OF-S11 | Sires (AVG) | Open above value: TPO opens fully above prior VAH, wait ~10:00 for the day type, break of the current VAH on aggressive buying imbalances, retest defended → long; still subject to time of day, DOM at the retest, and an HTF objective | `open_cell` above-value × VAH break-retest | `[AVG p.21–22]` |
| OF-S12 | Sires (AVG) | DOM in three reads: location (who should be in control; price seeks value 60–80%) → pacing (effort vs reward) → digits (thinning to singles vs building to triples) | `flow.digits.thinning` | `[AVG p.25–26, p.28]` |
| OF-P1 | Pine tier 2 | Hardcoded statistics are claims to recompute on F and L: σ-band reversion, hourly sweeps, magic hours, raids, engulfment first-hits, ORB / IB tables, FVG effectiveness, midnight-open hit | recompute rows | `wiki/sources-pine-archive.md` |
| OF-P2 | Indicator (MVFL) | Bias by vote with hysteresis (4 of 7 votes to flip): SMA200 trend, delta events ≥6× average, SQA vs SMA50, delta-zone break / rejection, MTF confirmation, SMA5 cross, volume-anomaly break / rejection; London and NY session filter | `bias.mvfl` (rebuild on aggressor delta per `[CEX L33]`, assistant, after the user's upgrade mandate `[CEX L17]`) | `[MVFL L2–56, L58–70, L79–102, L139–150, L414–432]` |

### A3. Triggers (TR)

| id | event | data | eligibility | source |
|---|---|---|---|---|
| TR-1 | touch `t0 / t2 / tR` of a level in the window | 1 s bars / trades | eligible | grid page; `[TBR p.20]` |
| TR-2 | reject `r ∈ {0.25, 0.5}` within `k ∈ {5, 15, 30}` min after touch or wick break, no `b.c1` (`grid.jumbo.projection-reject`) | 1 m bars | eligible | grid page; `[TBR p.20, p.30]` |
| TR-3 | break `b.wick d ∈ {2 ticks, 5 pts, 0.1R}`, `b.c1`, `b.c5` | bars | eligible | grid page; `[GB L89]` `[PINE Session Raid Stats.txt:36–37]` |
| TR-4 | hold `h ∈ {15, 30}` after `b.c1` (acceptance) | bars | eligible | grid page; `[AMT1 p.8]` |
| TR-5 | fail-back: `b.wick` then `b.c1` or `b.c5` back inside within `k` (`grid.gb.c5`) | bars | eligible | `[GB L89, L210]` `[TBR p.8]` |
| TR-6 | reclaim: back through the level and hold on the original side (`b.c1` + `h`) | bars | eligible | `[GB L88, L90]` `[FIND p.7, p.10]` |
| TR-7 | mid-retrace: after a break, return to EQ / range open, then hold | bars | eligible | `[XF p.12, p.15, p.23]` `[FIND p.4]` |
| TR-8 | time trigger: inside `bin.0940-0950`; after 10:00 (GB); after the 10:00 release; IB close 10:30; two consecutive 30 m periods inside prior VA | clock | eligible | `[TBR p.8, p.18]` `[GB L29]` `[TPO p.8]` `[MAMT p.18]` |
| TR-9 | 3-candle OB / rejection block on 2 / 3 / 5 m (`block.sweep.tbr.3m`) | bars | eligible | `[TBR p.27–29]` |
| TR-10 | CISD as coded (`cisd.fractal.literal`) | bars | eligible | `[OSF]` |
| TR-11 | first-presented FVG formed (3rd bar close) / filled | bars | eligible | `[PINE First presented FVG…]` |
| TR-12 | absorption candle (`flow.absorption.candle.jumbo`): small body + volume ≥ k × SMA14 | bars | eligible (bar object; k is a named grid) | `[TBR p.31, p.35]` `[MVFL L40–41]` |
| TR-13 | `flow.absorption.A` at the level | MBP-1 | eligible (trusted) | `[ABS p.8–9]` `[MATH p.8]` |
| TR-14 | `flow.bigtrade.100ny` / `75ldn` print at the level | MBP-1 | eligible (trusted) | `[XF p.25]` |
| TR-15 | `flow.reward.3tick`: after an absorption print, ≥3-tick move toward the absorbed side within 3 ticks / short window, opposing side not refreshing | MBP-1 | `[unmeasured]` | `[ABS p.4]` `[STOP p.10, p.14]` `[AVG p.24]` |
| TR-16 | 4-stage absorption: initial defence → replenishment ≥3 ticks → aggressor prints thinning (`flow.digits.thinning`) → lift-off (2–4 upticks with aggression) | MBP-1 | `[unmeasured]` (replenishment uses at-touch reload only) | `[STOP p.10, p.12]` |
| TR-17 | footprint diagonal imbalance 3× / 4×; stack ≥3 (2); candle-vs-delta disagreement; candle POC flip | trades | `[unmeasured]` | `[FP8 p.5–6]` `[FP9 p.3–5]` |
| TR-18 | same-price 350% imbalance at the same price as aggression | trades | `[unmeasured]` | `[BIG p.5]` `[K2345 p.5]` |
| TR-19 | delta spike at VAH / VAL; highest delta print side; per-candle delta vs candle direction | trades | `[unmeasured]` | `[ABS p.10–11]` `[RD p.6–7]` `[FP9 p.4]` |
| TR-20 | refill touch: return into `flow.refill.zone`, penetration depth (12 ticks in, 18-tick median dip; the paper's tested grid runs stops 25–65 and targets 20–100 ticks), hold | trades | `[unmeasured]` | `[REF p.10–12, p.17–18]` |
| TR-21 | OFM sequence: catalyst → release → fail through catalyst → refill → re-squeeze retest; passive variant (tape speed dies) | trades | `[unmeasured]` | `[OFM p.5–6, p.14]` |
| TR-22 | `flow.tape.speed` spike / death; `flow.spread.width` widening | MBP-1 | `[unmeasured]` (**new**) | `[DOM5 p.6]` `[OFM p.5]` |
| TR-23 | `flow.approach.speed`: aggressive vs drifting arrival at the extreme | trades / bars | `[unmeasured]` (**new**) | `[WIC p.4]` `[REF p.8]` |
| TR-24 | CVD divergence / breakout on flat CVD / stall with CVD climbing; CVD median side | trades | **blocked** (`flow.cvd.trade` tape-trusted no) | `[VWAP p.6]` `[ABS p.5]` `[STOP p.8]` `[FP9 p.6]` |
| TR-25 | SMT / IØD / RFZ: sister takes the level first, other does not | 1 m sisters | **blocked** (`flow.smt.*` tape-trusted no) | `[FIND p.3]` `[C1 p.5]` `[CEX L78]` |
| TR-26 | BBO reload ≥50% within 500 ms ×2 (`flow.absorption.B`); iceberg reload | MBP-1 | **blocked** (fires every session) | `[DOM7 p.4]` `[JJX L171]` |
| TR-27 | intraday cross of the gamma flip; price at call / put wall | daily OI + spot | eligible as daily-known level events; intraday gamma is a lag proxy | `[GEX p.7, p.13, p.19]` |
| TR-28 | ES-vs-VIX intraday divergence | VIX minutes | not in inventory (daily VIX / VX only) → filter, not trigger | `[VIX4 p.6]` |
| TR-29 | stacking / pulling behind the touch; spoof vanish | depth | not-measurable (MBP-1) | `[DOM6 p.5]` `[DOM7 p.5–7]` |

### A4. Filters (FL)

| id | filter | values | source |
|---|---|---|---|
| FL-1 | year | 2024 / 2025 / 2026 (and L for recompute rows) | `FINDINGS.md` |
| FL-2 | realized-vol tercile | `vol.rv20`, `vol.gk20`, `vol.yz20`, `vol.har`; windows 10 / 20 / 60; overnight RV | `[DTM L23]` `[JJX L149]` (user) `[JJX L205–216]` (assistant list, tier 4) |
| FL-3 | implied-vol regime | `vol.iv.atm`, `vol.skew25`, `vol.vx.slope`, VVIX; contango / backwardation | `[VIX4 p.8]` `[CEX L309, L320]` (assistant; no user turn mentions the curve) |
| FL-4 | VIX band | printed cut points: <13 no edge, <14 scalps only, 15–18 the sweet spot, >20 widen stops; the 14–15 and 18–20 bins are named fillers the lesson prints no rule for; anchors 12.5 / 16 / 22 (ES 30 / 50 / 95 pts, "typical") | `[VIX4 p.4–5]` |
| FL-5 | session | NY AM / London / Asia / PM; clean-session rolling label | `[FIND p.9, p.11]` `[XF p.40]` `[MVFL L51–56]` |
| FL-6 | RVOL 09:30–09:35 vs 60-session median | ≥1.0, ≥1.5 | `[PACK L40]` `[XF p.7]` |
| FL-7 | width bin | `w.pct` bins {0–0.3, 0.3–0.5, 0.5–0.8, 0.8–1.2, 1.2+}; `w.rel-prior-rth` bins | `[XF p.23–24]` |
| FL-8 | day type | Judas / single-extended / single-purged / neither; `balance`; `edge_clean` | `[TBR p.12]` `[FIND p.7]` |
| FL-9 | open cell | 27 cells; in-value / in-range-not-value / outside-both | `[XF p.8, p.11]` |
| FL-10 | AMT labels | `label.amt.open.30m`, `label.amt.day`, profile shape D / P / b / B / trend / double | `[AMT1 p.6, p.10–11]` `[RTVP p.7–11]` |
| FL-11 | overnight inventory | net delta sign 18:00–09:30 (trade-level); ON LVN respected / disrespected | `[MAMT p.14]` |
| FL-12 | gamma regime | above / below flip per product; long / short; distance to flip; near-flip ambiguous | `[GEX p.7, p.10]` `[BIG p.14]` `[K18 p.4]` `[CONT p.6]` |
| FL-13 | calendar | CPI / NFP / FOMC week and day; 10:00 release; pre-event / post-crush; OPEX; contract roll; DST mismatch weeks; half days | `[TBR p.22–23]` `[VIX4 p.7]` `[GB L177, L693]` `[CEX L151]` (assistant: contract roll, quarter-end, DST mismatch weeks; tier 4) |
| FL-14 | weekday | Monday (NWOG), Friday (GB preference, contradictory), Sunday Globex | `[GB L176, L179, L621, L673]` |
| FL-15 | window fuel | realized range / expected range so far; range completion | `[VIX4 p.3, p.5]` (implied range = price × VIX / √252 per the p.3 figure) `[CEX L86]` (assistant) |
| FL-16 | prior-failure count at the level | 0 / 1 / 2+ prior-session failures; held earlier this session; prior-day defence (memory) | `[TRAP p.5]` `[NYAM p.6]` `[REF p.8]` |
| FL-17 | location class of the print | extreme (shelf / ledge / LVN / minor node / prior-day VA) vs POC / inside balance | `[ABS p.6–7]` `[C3 p.6]` |
| FL-18 | sister-index hunt / relative strength | blocked until SMT rebuilt; `edge_clean` and purged labels stand in | `[FIND p.3, p.7]` `[TBR p.12]` |
| FL-19 | CVD median side | blocked until CVD rebuilt | `[ABS p.5]` `[BIG p.12]` |
| FL-20 | coverage flags | per dataset present / partial / missing; >10% rule | `wiki/data-coverage.md` |
| FL-21 | instrument scope | NQ execute, ES / SPX complex as information; no overnight hold | `[DTM L266–268]` `[JJX L465]` |

### A5. Invalidations (IV)

| id | rule | source |
|---|---|---|
| IV-1 | 1-minute close through the level (`b.c1`) | grid page |
| IV-2 | 5-minute close through the level (`b.c5`) | `[GB L89]` `[GB L26]` |
| IV-3 | hold outside `h ∈ {15, 30}` = acceptance = true breakout | grid page; `[AMT1 p.8]` `[GB L245]` |
| IV-4 | opposite edge reached (first objective = other side of the box; trade complete) | `[GB L213, L363–366]` `[TBR p.12]` |
| IV-5 | time: reversal window missed (no reversal by 10:00 in `bin.0940-0950` recipes); position closed at the start of the reversal window (Judas rider); no interest after 10:00 on extended days; cancel after 30 min (refill); lunch not A+ | `[TBR p.8, p.12, p.37]` `[REF p.12]` `[FIND p.12]` |
| IV-6 | beyond the sweep wick / beyond the pocket / stop right above PDL | `[GB L94, L212, L353–358]` |
| IV-7 | OB midpoint (aggressive) / OB low (conservative) / rejection-block midpoint | `[TBR p.27–29]` |
| IV-8 | beyond the aggression print that built the entry (OFM); below the absorption (refill) | `[OFM p.6–7, p.12]` `[NYAM p.4]` |
| IV-9 | protected low / high broken (highest-delta protected level) | `[RD p.5]` `[K18 p.8]` |
| IV-10 | 3-strike rule; extended bodies through the projection; no rejection signature; volume divergence | `[TBR p.37]` |
| IV-11 | band retirement: 1-minute close beyond the P-zone far edge; liquidity line deleted once purged | `[TBR p.11]` `wiki/p-zones-benchmark.md` |
| IV-12 | bias death: structure break, value shift, new information; thesis box violated | `[C1 p.4]` `[C3 p.7]` |
| IV-13 | replenishment stops (exhaustion) / pull at the touch | `[MATH p.8]` `[STOP p.10]` `[JJX L338–342]` |
| IV-14 | regime flip after a large impulse (re-read gamma) | `[GEX p.19–20]` |
| IV-15 | re-entry only if price returns inside the same band where the side previously held ("Not near it, and not on a different level that looks similar"); otherwise the idea is finished | `[ANAT p.7]` `[STOP p.14]` |
| IV-16 | −4R daily stop; daily objective reached; max loss half the objective; consistency cap | `[REF p.21]` `[STOP p.15]` `[ANAT p.11]` `[K2345 p.9]` (account rules: recorded, not Phase 1 objects) |

### A6. Not computable or excluded

| item | reason | source |
|---|---|---|
| hidden book, off-touch refill, icebergs, stacking / pulling behind the touch, spoof detection | needs MBP-10 / MBO | `QUESTIONS_RESOLVED` §35; `[JJX L310–314]` |
| dealer inventory, customer vs dealer identity | not in data | `[DRFL L207–224]` (assistant, tier 4) `[INV L297–380]` |
| Skylit Heatseeker / Flowseeker / Atlas, KG1, GEXRADAR, Vol Signals, DeepCharts Big Trades settings for other instruments | vendor engines; only disclosed substitutes | `[K10 p.6]` `[GEX p.15]` `[BIG p.3]` `[FIND p.13]` |
| P-zone auto-learn weights, London build-window start, delta-profile row size, SessionStat lookback rationale, London reversal histogram, win-rate ledger | unpublished | `[FIND p.13]` |
| cash NDX / SPX minute bars; VIX intraday | not in inventory | `wiki/data-coverage.md` |
| "kg one retest" model, trailing-convexity full rule set | not defined in the public PDFs | `[NYAM p.9]` `[OFM p.13]` |
| 3-day liquidity map | named, undefined | `[FIND p.3]` |
| ES trade-level objects inside F | ES MBP-1 ends 2024-08-30 | `[INV L142–148]` |
| 25-pt partials, fleet / DLL, 7:30 true open, "above TDO = short", wickless model, CPI boxes as a family, premium / discount box as a standalone signal, IB stats as edge, always-fade 6–9, TradingView OF POC, bubbles-as-absorption, 86.46% as a win rate | excluded by source or by closed decision | `QUESTIONS_RESOLVED` §45; `[PACK L86–92]` `[FIND p.11]` `[XF p.8, p.25–26]` |

### A7. Wiki coverage delta

New ids to register (each has a source row above; registering is a wiki edit, not a ticket): `range.midnight.0000-0030`, `range.rth.0930-1000`, `range.rth.1000-1030`, `range.lunch.1200-1230`, `range.moc.1500-1530`, `range.on.1800-0930`, `range.dealing`, `value.vp.eth.prior`, `lvl.mpoc.eth`, `value.vp.on`, `value.vp.dealing`, `value.vp.composite.*`, `value.delta.weekly`, `flow.delta.spike`, `lvl.prior-rth.q*`, `lvl.pclose`, `lvl.popen`, `lvl.halfgap`, `lvl.pib.*`, `lvl.owed.nearest`, `env.ss.rth.avgHL60`, `env.tbr.sigma025`, `env.pine.manip.*`, `env.vwap.rth.sd{1,2.5,3}`, `env.vwap.anchored.*`, `flow.absorption.candle.jumbo`, `flow.refill.zone`, `flow.ofm.catalyst`, `flow.footprint.stack3`, `flow.footprint.imb350`, `flow.candle.poc`, `flow.candle.poc.flip`, `lvl.protected.*`, `flow.delta.zone.kmeans`, `flow.vol.anomaly.zone`, `flow.reward.3tick`, `flow.digits.thinning`, `flow.tape.speed`, `flow.spread.width`, `flow.approach.speed`, `loc.pd50`, `lvl.1800open`, `value.node.{callwall,putwall,maxpain}.*`, `phase.amd.*`, `label.clean.session.rollingN`, `label.amt.80pct.two-period`, `bias.mvfl`.

Wiki ids with no author recipe of their own (they enter only through swaps in C): `range.gb.london` as a Jumbo clock, `range.ib` (comparison), `env.ext.133.from-origin`, `env.ext.133.from-eq`, `flow.cvd.part.*`, `flow.cvd.gamma`, `flow.smt.pine.3-3`, `vol.*` as levels, `value.node.oi.nqopt.top3`.

---

## B. Sourced recipes

Format: **id** · OF · LC · TR · FL · IV · Score (what Phase 1 prints for it) · Cites · Status (`ready` = every slot on eligible objects; `ready-bar` = bar trigger stands in for a blocked tape trigger the author names; `pending` = trigger unmeasured; `blocked` = trigger tape-trusted no; `context` = a gate, scored as a label table).

### B1. Jumbo (Time-Based Ranges manual, X archive, findings, X pack, conversation)

How the Jumbo files say to operate, before any row: one loop per clock, build → classify → trade the next clock → confirm at location, and "one of these alone is not a trade" `[FIND p.3]`. The two core sequences are the single break (one edge taken, opposite edge clean, return to range open or mid, continuation) and the Judas / double (one edge swept, extension into the exhaustion area beyond that edge — the mean-reversal lines 0.1 / 0.2 / 0.3, the ±0.5 projection, a small overshoot, or a P-zone / EV / SessionStat level sitting there — then reversal through mid toward the untouched edge) `[FIND p.4]` `[TBR p.5, p.6, p.8, p.12]`. The manual draws the fade on both sides: from above the high (p.9 Trade #2, p.13 Scenario #1, p.20) and from below the low (p.10 Trade #1); its stats are labelled "±0.5" and split upper vs lower `[TBR p.30]`, so every reversal row below is scored on the swept side, whichever it is. The 6–9 high and low are rails: on a fade day the sweep magnet and then the invalidation, on a single-break day the first target `[FIND p.7]`; no row below enters on a tag of the 6–9 high or low, and "always fade 6–9" is discarded `[FIND p.11]` `[XF p.7]`. Every reversal row also carries the explicit test variants of A1.2 (`proj.width.*`: `w.69` faithful | `w.ev` | `w.london` | `w.own`; `proj.level.*`: ±0.5 | ±1.33 | ±1.66 | band 1.33–1.66 | overshoot δ), listed in C3 as SL-proj and SL-width; no source states an EV-width projection, so `w.ev` never becomes the faithful row. Entries are taken only after the 09:30 open (RTH candles from 09:30) `[TBR p.12]`, the setups are framed inside 09:00–12:00 with the two time-defined zones at the open and at 09:40–09:50 `[TBR p.16]`, and the 2026 frame is context → location → confirmation: double-break expectancy in value / in range, overnight high / low, the AM vol expected range, then confluence with levels `[XF p.7]`.

**R-J01 Judas reversal, trade #2 (fade at exhaustion, 09:40–09:50)** · OF-J1 + OF-J12 · LC the exhaustion area beyond the swept edge of `range.6-9.published`, on either side: the mean-reversal levels `lvl.mr.0.1 / 0.2 / 0.3` and the ±0.5 projection (`area.mr`, edge → ±0.5; "levels of interest will be the mean reversal levels or -0.5 projection") `[TBR p.5, p.8, p.30]` `[TBR p.9–10, p.13, p.20 charts]`, a small overshoot past the printed level allowed (`proj.overshoot.δ`) `[TBR p.10, p.20]`, with confluence levels that must sit in it or within `tR`: `pz.approx.A` band, SessionStat 9–12 extreme, EV band edge, the overnight-session liquidity line (Asia / London / midnight H / L, deleted once purged) `[TBR p.11]` `[XF p.7, p.19, p.29]` `[FIND p.4, p.7]`; pass-through EQ; draw = the untouched (red) edge, then leftover Asia / London highs or lows `[FIND p.4–5]` `[XF p.30, p.48]` · TR the sequence: one edge swept after 09:30 (`b.wick`, not a close-through), extension enters the exhaustion area inside `bin.0940-0950` (the depth reached — 0.1 / 0.2 / 0.3 / 0.5 / beyond — is a printed column, not a filter), then a rejection signature there (constant rejection, multiple wicks `[TBR p.20]`, `grid.jumbo.projection-reject`), confirmed by a 3-candle orderblock or rejection block on 2 / 3 / 5 m `[TBR p.27–29]` or an absorption / imbalance candle at the level `[TBR p.31]` `[XF p.45]` (R-J14), reclaim of the range open after the sweep `[FIND p.7, p.10]` · FL pre-open Model A written from the classifier: mid-sized range (not tiny, not ≥ 1.2%), balanced overnight with both edges meaningful, RTH open inside prior-day value / range, in-value double-break expectancy, sister indices same side still live (stand-in labels `edge_clean`, purged), no 10:00 release `[FIND p.6–7, p.11]` `[XF p.7, p.16, p.23–24]` `[TBR p.12–13, p.18]`; market conditions not "unfavourable" `[TBR p.22–23]` · IV no rejection signature or extended bodies at the projection, continuous momentum, 3-strike, volume divergence, reversal well before or after the window `[TBR p.37]`; `b.c1` beyond ±0.5 + δ (the far edge of the area); A+ closed before 10:00 unless the day is expansive `[TBR p.8]` `[FIND p.4]` · Score: reject rate at each depth 0.1 / 0.2 / 0.3 / 0.5 per side (the p.30 "Reversal % by Projection (Upper vs Lower)" chart recomputed), the 86.46% in both readings (reversal at the ±0.5 line; reversal from inside the extended range) on both sides, reversal-time histogram (09:40–09:50 share, average time, original vs extended range), EQ reach, clean-edge reach, leftover-extreme reach by 10:00 / 12:00, 80–120 pt yield distribution `[TBR p.8, p.30]` `[XF p.47]` · Variants: SL-width (`w.69` faithful | `w.ev` | `w.london` | `w.own`) × SL-proj level (±0.5 | ±1.33 | ±1.66 | band 1.33–1.66 | overshoot δ), one slot at a time (C3) · ready.

**R-J02 Judas rider, trade #1 (09:30 open into the projections)** · OF-J1 · LC the 09:30 open print, target "the projections of the range where the reversal will take place" on the side being swept: the mean-reversal area up to ±0.5 beyond that edge (his p.10 Trade #1 example runs through −0.5 with a small overshoot before the reverse; p.9 Trade #1 runs above the high into the +0.5 side) `[TBR p.8]` `[TBR p.9–10 charts]` · TR the 09:30 open itself (time trigger), positioned "right at the open" in the direction of the false breakout toward the projections; the manual gives no rule for choosing the side, so the score prints both sides and, as named rows, the side of the first edge taken after 09:30 and the side nearer to the open `[TBR p.8]` `[TBR p.5]` (projection-direction plotting exists in the indicator, formula unpublished) · FL as R-J01 (Model A day) · IV positions closed as the 09:40–09:50 reversal window arrives; the projection reached earlier; yield judged against the distance from open to the projection `[TBR p.8]` · Score: share of Model A sessions where price travels from the 09:30 open to ±0.5 (either side) before 09:40, and to each mean-reversal depth 0.1 / 0.2 / 0.3; excursion from the open by 09:40 in points and in R; by side rule · Variants: SL-width × SL-proj level as R-J01 · ready.

**R-J03 Single break, extended overnight range (scenario 1)** · OF-J2 + OF-J6 · LC EQ and the 25 / 75 quadrants of `range.6-9.published` as the levels of interest; range open as the pullback magnet `[TBR p.12]` `[FIND p.4, p.7]`; targets limited to the 6–9 high / low until lunch, projections off the table `[TBR p.12, p.24]` · TR one edge taken by `b.c1` after 09:30 with the opposite edge still clean, then a return to EQ / quadrant / range open and a hold (`h=15`) in the break direction; in before 10:00, close around 09:40–09:50 `[TBR p.12]` · FL extended overnight = `w.rel-prior-rth ≥ 1.0` or an 8:30 red-folder day `[TBR p.24]`; range-size table consulted before the open `[TBR p.12–13]`; Model B written pre-open `[FIND p.7]` · IV `b.c1` back through EQ against the break; after 10:00 no interest in a position; price grindy with deep retracements, invalidations larger than usual `[TBR p.12, p.24]` · Score: single-break rate by width class, retrace-to-mid rate (60.4% recomputed) `[XF p.23]`, hold rate at EQ / quadrant / OP, reach of the broken edge by 10:00 / 12:00, consolidation through lunch / PM share `[TBR p.12]` · ready.

**R-J04 Single break, overnight already purged (scenario 2)** · OF-J2 + OF-J4 · LC the inner range levels EQ and quadrants as expansion entries `[TBR p.12]` `[FIND p.7]`; targets raised in the break direction: 1.0, then the 1.33 / 1.66 area (single-break-day flatten area, "end of day max expansion"; drawn above the high on XF p.48 and below the low on TBR p.13 Scenario #2, where the run continues to −2 / −2.5 / −3) `[TBR p.13, p.21]` `[XF p.48]` `[FIND p.7]` · TR expansion from the inner level (`b.c1` beyond EQ / quadrant in the break direction after 09:30); 09:40–09:50 is continuation, add to the position, not a reversal window `[TBR p.12]` `[FIND p.7, p.12]` · FL purged: every significant overnight liquidity taken before 09:30 (Asia / London H / L purged), stop hunts / swing failures overnight, relative strength divergence between indices done (stand-in labels until SMT is rebuilt), shrunk overnight range `w.rel-prior-rth ≤ 0.5` `[TBR p.12]` `[FIND p.7]`; expansive conditions: compound, runners, re-entry plausible `[TBR p.24]` · IV `b.c1` back through EQ; the 1.33–1.66 fork after 12:00 (R-J08) · Score: expansion reach of 1.0 / 1.33 / 1.66 by 10:30 / 12:00 / 16:00 conditional on purged; 09:40–09:50 continuation share; re-entry count after a knock-out on expansive days · ready.

**R-J05 Single break, range-open and mid retrace (2026 use)** · OF-J2 · LC range open (OP) of `range.6-9.published` and its EQ; the 15-minute (5-minute named) OR mid as the second retrace stat `[XF p.12, p.14–15, p.25]` `[FIND p.4–5]` · TR after the A-period single break, price returns to OP or mid and holds; "the open is an entry magnet, not a fade" `[FIND p.4]`; one-and-done in the first 20 minutes is the preferred exit `[XF p.15]` · FL Model B context: open outside prior value and range with above-average RVOL (the 76% claim, two denominators on [open-location-switch](wiki/open-location-switch.md)) `[XF p.8, p.10]` `[PACK L40, L44]`; mean-reversion days instead take 50–70 point series, "not chasing home runs or continuations" `[XF p.14]` · IV `b.c1` back through OP against the break; the trade ends at the opposite projection or at the first-20-minute exit · Score: OP / mid retrace rate after the first break (60.4% recomputed by class), hold rate at OP vs at the 15m OR mid, reach after the hold `[XF p.15, p.23]` · ready.

**R-J06 The 2026 context gate (open location, overnight H / L, EV range)** · OF-J3 · LC `open_cell` (RTH open vs prior-day value / range and vs the current 6–9) `[XF p.8]`, the overnight high / low status (still clean or already purged) `[XF p.7]` `[TBR p.11]`, the AM vol expected range `env.ev.*` `[XF p.7]` `[PACK L13–31]` · TR none: written before 09:30 as Model A (fade) or Model B (single break) in one line `[FIND p.11]` · FL RVOL ≥ 1.0 / ≥ 1.5 for the outside-both cell `[PACK L40]` · IV n/a · Score: path-class shares per cell (XF p.11 rows recomputed), `open.dbx.in-value` vs `in-range-not-value` vs `outside-both`, `open.oneway.A.0930-1000` and `open.oneway.OR.5m/15m`, and the "discard mean reversion when these align" days: outside both + RVOL → double-break rate `[XF p.10–11, p.16–17]` `[FIND p.5–6]` · context.

**R-J07 Range-size and balance classifier** · OF-J4 · LC `w.pct.0859close` / `w.pct.0930open` bins, `w.rel-prior-rth`, `balance.body-ratio`, `balance.vp-shape` (range profile), `edge_clean`, purged flags `[XF p.7, p.23–24, p.44]` `[TBR p.12–13]` `[JJX L56]` · TR none (pre-open) · FL none · IV n/a · Score: XF p.24 break-classification table recomputed on F and L (double falls from 55.5% to 17.8% by width), ~45% single-break base rate, small-range double-break share flagged as skewed not edge, double vs single by balanced / imbalanced overnight `[XF p.7, p.17, p.23]` `[FIND p.6–7]` · context.

**R-J08 1.33 / 1.66 retracement-reversal fork (AM into PM)** · OF-J5 · LC the 1.33–1.66 retracement / reversal **area** beyond the edge the AM leg ran through, on either side: `env.ext.133.from-edge`, `env.ext.166.from-edge` and the shaded `band.133-166` between them, of the 6–9 box (London box when London is the clock, `w.london`); drawn below the low on `[TBR p.21]` (reversal wick poking through −1.66), `[XF p.31, p.33]` and `[PACK L66]`, above the high on `[TBR p.10]` (+1.33 / +1.66) and `[XF p.48]` ("1.33 1.66 end of day max expansion" band above the high) `[XF p.9, p.25]` · TR interaction at the area after the AM leg: reject inside the band or at either level, with a small overshoot past 1.66 allowed (`proj.overshoot.δ`) (reverse the whole AM through PM) vs hold beyond 1.66 + δ (continue the AM direction); PM 13:00–16:00 window `[TBR p.21, p.36]` · FL AM class: AM consolidation → PM expansion to the higher projections; AM expansion → PM consolidation between AM levels; compressed AM as the fork condition `[TBR p.36]` `[FIND p.5–6]` · IV `b.c5` beyond 1.66 + δ; time pivots ignored `[TBR p.37]` · Score: touch by 12:00 / 16:00 per side; reject vs continue shares at 1.33, inside the band, at 1.66 and with overshoot; PM reach of 1.33 / 1.66 on compressed-AM sessions; "end of day max expansion" share (RTH extreme inside the band) `[XF p.48]` · Variants: SL-width (`w.69` faithful | `w.london` | `w.own` | `w.ev`) × SL-proj level (±0.5 | ±1.33 | ±1.66 | band | overshoot δ), one slot at a time · ready.

**R-J09 London TBR (same logic at 03:00)** · OF-J9 + OF-J1 / OF-J2 · LC `range.london.00-03` internals with the London box height as the width base (`w.london`): the mean-reversal area and ±0.5 on either side, the 1.33 / 1.66 area on either side ("London range exhaustion (1.33-1.66) longs" = the band below the London low `[XF p.25]`), 03:00 open analog, 06:00 handoff; London H4 SessionStat extreme and an absorption zone at the reversal `[FIND p.4–5]` `[XF p.25, p.40, p.46]` `[JJX L53]` · TR as R-J01 / R-J03 with the 03:00 open in place of 09:30 and no published reversal cluster (structure, not a clock, decides) `[FIND p.10]` · FL London-clean cycle (`label.clean.session.rollingN`) `[XF p.40]` `[FIND p.9, p.11]` · IV as R-J01 / R-J03; 06:00 handoff · Score: same table as 6–9 for the London box, per side and per depth; London 1.33–1.66 reject rate (at 1.33, inside the band, at 1.66, with overshoot); H4 SessionStat coincidence · Variants: SL-width (`w.london` faithful | `w.69` | `w.ev`) × SL-proj level · ready.

**R-J10 Draws after the reversal (leftover session extremes, RTH highs, daily high / low)** · OF-J10 + OF-J11 · LC untouched Asia / London / midnight H / L (time-based liquidity, deleted once purged) `[TBR p.11]` `[XF p.30, p.33]` `[FIND p.5]`; prior RTH high / low as draw on liquidity `[TBR p.33]` `[XF p.48]`; the daily high / low as the cycle-2 target after a 10:00 continuation `[XF p.27]` `[FIND p.7]` · TR none (targets after R-J01 / R-J04 fire) · FL the level still untouched at fire time · IV purge deletion `[TBR p.11]` · Score: reach of the nearest untouched session extreme, RTH high / low and daily high / low by 10:30 / 12:00 / 16:00 after a reversal from the exhaustion area on either side (R-J01) or a 10:00 expansion · ready.

**R-J11 SessionStat 9–12 as the target map and confluence** · OF-J12 · LC `env.ss.avgHL60` / `medHL60` / `minavg60` of the 09:00–12:00 session, plus projections that extend the average range `[SS p.6, p.10]`; A+ when today's ±0.5 area or 1.33–1.66 area, on either side, sits on the 9–12 average / median extreme (the 6 Jul 2026 chart shades the coincidence boxes above and below the session) `[XF p.19]` `[FIND p.5, p.7]`; the minimum-average range as a hit-rate target `[XF p.45]` · TR reject at the coincidence (not a trade clock by itself) `[FIND p.5]` · FL choppy and low-volatility failure conditions `[SS p.11]` · IV hold beyond the boundary · Score: reach, overshoot, reject at the coincidence vs at either level alone; minimum-average reach rate; calibration by vol tercile `[SS p.11]` · ready.

**R-J12 P-zone at the range edge with the range open** · OF-J1 + OF-J12 · LC `pz.approx.A` band (anchors 09:00, 09:30, 10:00) overlapping either 6–9 edge and the mean-reversal area beyond it, with the session extreme held inside the range open (the 2 Jan 2026 example is the low side, "P-zone, low > range open"; the high-side mirror, band on the 6–9 high with the session high below the range open, is the same object on the other side) `[XF p.28–29, p.35, p.8, p.16]` `[FIND p.7–8]`; a P-zone in air with no TBR level and no VP node is not his trade `[FIND p.8]` · TR full reversal during 09:40–09:50 (R-J01 sequence at the band) `[XF p.29]` · FL as R-J01 · IV band retirement · Score: reversal-inside-band rate; the "10 am p-zone > London low" draw reach `[XF p.28]`; distance ranking of EV vs the ±0.5 / mean-reversal area vs P-zone to the AM extreme, per side · Variants: SL-width × SL-proj level (the reject scored inside the band, at ±0.5, at the ladder depths, with overshoot) · ready.

**R-J13 EV range to EQ (mean-reversion morning)** · OF-J3 · LC `env.ev.*` band edges above and below the open (the 28 Aug 2026 chart draws the EVRange line above and below the 6–9 box, sell limits parked at the upper line beside the overnight high, the fade marked at the lower line), target `ev.mid.*` and the 6–9 EQ; on a large 6–9, the EQ itself as the long / short level; the band's own width is its width base — no source projects the 6–9 levels in EV width, so `w.ev` appears only as a named variant of the projection rows `[PACK L22–31]` `[XF p.7]` · TR reject at either band edge (a small overshoot past it allowed, `proj.overshoot.δ`); chasing the high is the named loss `[PACK L26]` · FL open inside prior value / range, "range breakouts likely to fail fast" `[XF p.16]` `[PACK L38, L43]` · IV hold beyond the band · Score: reach, overshoot, reject at the band; EQ reach after the band touch; in-value tag share · ready.

**R-J14 Absorption at the 6–9 key levels (confirmation row)** · OF-J12 · LC the 6–9 edges, EQ and the projections on either side (mean-reversal area, ±0.5, 1.33–1.66 area) paired with Absorption Zone+ `[TBR p.31]` `[XF p.27, p.46]` · TR the absorption candle (small body, volume above the 14-period average by the multiplier) and the imbalance inside it `[TBR p.31, p.35]` `[XF p.44–45]` · FL scored only at an R-J01 / R-J03 location; alone it is not a trade `[FIND p.3]` · IV `b.c1` through the level · Score: reject rate at the level with vs without the candle; overlap with `flow.absorption.A` (must not be identical) `[XF p.25]` · ready.

**R-J15 BigTrades at the level (confirmation row)** · OF-J12 · LC any pre-written level · TR a print ≥ 100 (NY) / ≥ 75 (London) at the level, read as "participants intentions"; not absorption bubbles `[XF p.25]` `[FIND p.9, p.12]`; large-lot dunks as the observation `[XF p.13]` · FL as R-J14 · IV `b.c1` · Score: reject rate given a print at the touch; overlap with `flow.absorption.A` · ready (trusted).

**R-J16 RTH VP and delta profile shapes (confirmation row)** · OF-J12 · LC absorption at the midpoint of the range (two-sided delta) and taper at the lows; RTH session VP and delta profile, footprint filtered to the top 35% of transactions `[XF p.14, p.23]` `[FIND p.8]` · TR the shape present at the touch · FL as R-J14 · IV `b.c1` · Score: shape shares at EQ and at the low; reject rate given the shape · pending.

**R-J17 VP node under a TBR level (the unspoken box)** · OF-J12 · LC a `value.kz` LVN slot or the shelf beside an HVN within `tR` of a TBR level; the range profile of the box itself `[FIND p.7–8]` `[XF p.44]` · TR reject at the TBR level · FL a level must sit on a node `[FIND p.7]` · IV `b.c1` · Score: reject at the TBR level with vs without a node under it · ready.

**R-J18 Entry models at the reversal (3-candle OB, rejection block)** · OF-J1 · LC the reversal location on either side — the mean-reversal area / ±0.5 (small overshoot allowed), the 1.33–1.66 area, a P-zone band or a leftover extreme — for the 3-candle OB ("i usually wait for during reversals"), or the inner level on a single break (rejection block) `[TBR p.27–29]` `[TBR p.9–10 charts]` · TR candle 2 sweeps candle 1, candle 3 closes beyond candle 2 (2 / 3 / 5 m); rejection block confirmed by the close above the sweep candle · FL used during reversals `[TBR p.27–28]` · IV aggressive stop at the block midpoint, conservative at the block low `[TBR p.27–29]` `[TBR p.37]` · Score: formation rate at each level and side; reject vs continuation after confirmation; midpoint vs low invalidation hit rates · Variants: SL-width × SL-proj level (the block is scored at whichever ladder level the sweep candle touches) · ready.

**R-J19 PD RTH Range+ (prior RTH high / low as the daily direction reference)** · OF-J11 · LC PDH / PDL of the prior 09:30–16:00 and the M15 / H1 first-presented imbalance (FVG) `[TBR p.32–35]` · TR the RTH open shows direction; ETH is disregarded, no engagement before the RTH open; trade toward the untaken prior RTH extreme `[TBR p.34]` · FL none · IV acceptance beyond the extreme · Score: touch of PDH / PDL by 12:00 / 16:00 given the RTH open direction; HTF FVG fill · ready.

**R-J20 Delayed cycle 2 on 10:00 news days** · OF-J7 · LC as R-J01 · TR the real reversal after the 10:00 release instead of 09:40–09:50 `[TBR p.18]` `[FIND p.10]` · FL 10:00 release day ("do not force 09:40") `[FIND p.11]` · IV as R-J01 · Score: reversal-bin shift on release days · ready.

**R-J21 Market conditions and expectations** · OF-J6 · LC targets per condition: extended overnight → 6–9 high / low until lunch; range-bound into news → high / low or inner levels when the open is outside the range, scalps; expansive → higher projections, compound, runners, re-entry plausible `[TBR p.24]`; CPI / NFP / FOMC week table, AM off-limits on unfavourable days, PM has the moves `[TBR p.22–23]` · TR none · FL calendar `[TBR p.22]` · IV larger invalidations on grindy days `[TBR p.24]` · Score: projection reach by condition class; knock-out and re-entry counts · context.

**R-J22 Failure protocol** · OF-J8 · LC the projection / exhaustion levels on either side (the p.37 list says "projection levels", plural: the mean-reversal area, ±0.5, the 1.33–1.66 area, whichever the session reached) · TR none · FL none · IV the object: no rejection signature, continuous momentum, extended bodies, daily-direction misread, window missed, extended moves, premature reversal, 3-strike, volume divergence; then exit and observe, switch to the single-break model or PM `[TBR p.37]` · Score: 3-strike count, extended-body share, share of failed reversals that became single-break sessions · context.

**R-J23 The other published clocks** · OF-J1 / OF-J2 on `range.midnight.0000-0030`, `range.asia.2000-2030`, `range.london.0300-0330`, `range.rth.0930-1000`, `range.rth.1000-1030`, `range.lunch.1200-1230`, `range.moc.1500-1530`: "this logic can be applied to multiple ranges present throughout the day" `[TBR p.6–7]` · same slots as R-J01 / R-J03 with the box swapped and the box's own height as the width base (`w.own`: the same ladder — mean-reversal lines, ±0.5, ±1, 1.33–1.66 area, ±2 — on both sides of each box) · lunch and MOC expected weak `[XF p.21]` `[FIND p.5–6]` · ready (comparison rows).

**R-J24 Management as exit and add definitions** · OF-J13 · per window: take profits, add, or close at the 09:30 and 09:40–09:50 zones with take-profit points along the way `[TBR p.16]`; compound toward the higher projections after the reversal `[TBR p.8]`; front-run the target at a clear mid rejection `[XF p.26]`; one-and-done in the first 20 minutes `[XF p.15]`; flip when the first idea dies at the level `[XF p.3]`; lunch is not a second A+ `[XF p.21]`; BE at 09:50 while location is valid is a named leak `[FIND p.11–12]` · Score: outcome rows only (MFE / MAE at those exit rules) · context.

**R-J25 Trend-day swing-mid retraces (observation row)** · OF-J2 · LC the midpoint of each completed swing on a trend day, down to an older gap `[XF p.26]` · TR none: the tweet describes what price did ("clean retraces to midpoint of every swing"); it states no setup, so no entry trigger is claimed · FL trend-day sessions (single-break class with expansion continuing after 10:00) · IV n/a · Score: retrace-to-swing-mid rate and hold rate on trend-day sessions, a descriptive row only · `[XF p.26]` · context.

### B2. Green Bird

**R-G01 NYAM failed breakout / breakdown** · OF-G1 + OF-G2 + OF-G3 · LC `box.gb.nyam` edges; bonus PDH / PDL · TR-5 sweep after 10:00 then `grid.gb.c5` back inside · FL after 10:00; `label.aplus` = sweep observed · IV-3 hold outside (true breakout); IV-6 beyond the wick (read on bodies, not wicks, as the named variant: "The bodies tell the story. The wicks do the damage" `[GB L92, L622]`); IV-4 opposite edge · both sides as stated ("Exact mirror" `[GB L216–227]`); ticket stops the pack reads off his screenshots are illustrative, "not a formula — structure" (~32–35 pts NYAM, ~49.75 pts above PDL, ~17 pts Asia) `[GB L356–358, L606]` · Score: `fail.box.gb.nyam.c5` counts per side, opposite-edge reach, PDH / PDL confluence share, agreement with Judas labels · `[GB L28–30, L188–246, L395–422]` · ready.

**R-G02 Asia / midnight failure** · OF-G1 + OF-G5 · LC `box.gb.asia` H / L, `lvl.tdo` · TR-5 sweep of the Asia edge, then 5 m close back inside and / or through TDO · FL overnight session · IV-3; IV-6 · Score: fail-back counts, TDO close-through share, Asia-low reach · `[GB L35–40, L424–437, L612–613]` · ready.

**R-G03 Previous-hour box** · OF-G1 · LC `box.gb.hour` · TR-5 · FL 09:30–12:00 (5-minute steps) and PM · IV-3, IV-6, IV-4 · Score: events per hour box; repeat-fade counts; reach of the box's opposite edge and of PDH / PDL / TDO after the fail (the 27 Aug ticket sells back through TDO with limits laddered toward PDH, stop 19.25 pts above the wick `[GB L687]`) · `[GB L32–33, L439–441, L685–687]` · ready.

**R-G04 9:30 manipulation reclaim** · OF-G4 · LC `lvl.0930open` · TR-6 sweep below the open, reclaim and hold · FL none · IV-1 · side: the pack states the below-the-open long only (`[GB L30, L90]`); the above-the-open short is a named side variant, not a faithful row · Score: reclaim rate; reach of discount / pocket after reclaim · `[GB L30, L56–57, L90]` · ready.

**R-G05 TDO close-through** · OF-G5 · LC `lvl.tdo` · TR-5 with `b.c5` through TDO after a sweep · FL none · IV-2 · Score: `tdo_touch` in 09:30–12:00 (tier-2 midnight-open hit 73.75%), close-through rate · `[GB L24–26, L142, L612]` `[PINE nq_stats_mapper:311–313]` · ready.

**R-G06 NWOG destination** · OF-G6 · LC `lvl.nwog` (settle and close endpoints) · TR none (target) · FL-14 Monday · IV n/a · Score: `nwog_fill` by 12:00 / 16:00 on Mondays; fill after a midnight / open sweep failure (direction-agnostic; every printed example is a gap-below short, ~300 pts on two Mondays `[GB L621, L675]`) · `[GB L59–60, L68–69, L615–621, L673–675]` · ready.

**R-G07 Golden pocket continuation** · OF-G7 · LC `loc.gp` (NYAM impulse or HTF swing) · TR-2 rejection in the pocket, or TR-5 sweep + `b.c5` at a level inside it ("10 am hourly low reclaim + pocket") · FL bias from OF-G8 · IV-6 beyond the zone · Score: touch of the pocket, reject vs traverse, reach of the impulse extreme · `[GB L73–81, L249–296, L537–547]` · ready.

**R-G08 Overnight PDL / PDH sweep-and-reclaim bias** · OF-G8 · LC `box.prior-rth` · TR-6 overnight sweep + reclaim · FL none · IV-1 · Score: next-morning path class conditional on the overnight reclaim; NYAM pullback-to-discount reach · `[GB L313, L443–450, L543–544]` · ready.

**R-G09 Stacked sweep to NWOG** · OF-G9 + OF-G6 · LC PDH + Asia high + London high within `tR`; target `lvl.nwog` · TR-5 failed breakout under `grid.gb.c5` · FL Monday / unfilled gap below · IV-3 · side: the high-side stack is the only printed case; the low-side mirror (PDL + Asia low + London low, failed breakdown, gap above) is a named variant · Score: gap tag rate after the stacked failure · `[GB L156, L615–620]` · ready.

**R-G10 Chop-day repeated fade** · OF-G10 · LC `box.gb.nyam`, `box.gb.10-11` · TR-5 repeated · FL one-way-pressure label (`label.amt.day` normal / neutral with a directional lean) · IV-3 · Score: fade count per session and reject share · `[GB L669–671]` · ready.

**R-G11 A+ vs B+ label** · OF-G9 · `label.aplus` true iff a sweep of the traded range **plus** the failure back inside was observed ("A+ | Sweep of the relevant range plus failure back inside" `[GB L242]`); sweep-only is the necessary condition he states ("No sweep = not A+" `[GB L93, L147]`) and the named weaker label `label.aplus.sweep-only`; depth `d` a separate upgrade · Score: outcome shares by label · `[GB L93, L147, L244]` · context.

### B3. AMT and profile lessons

**R-A01 Balance-rule fade** · OF-A1 + OF-A3 · LC prior-day VAH and VAL (fixed, both edges; the extremes are drawn as bands of unprinted thickness `[AMT1 p.9 chart]`, so the touch tolerance is a grid value) toward POC; current-day VAH / VAL flagged lagging · TR-2 reject at the edge + TR-13 at the edge · FL-10 normal / neutral day, FL-17 · IV-3 acceptance outside · Score: grid at VAH / VAL / POC, POC reach after an edge touch; the `[MAMT p.5]` general failed-auction share (an excursion beyond either edge that returns inside without a hold) as its own denominator, per side · `[AMT1 p.5, p.9, p.13–14]` `[AMTL p.6]` `[MAMT p.4]` `[ABS p.7]` · ready.

**R-A02 Ledge continuation** · OF-A2 · LC `value.kz` ledge of the prior balance / broken VA edge · TR-3 `b.c1` beyond then TR-1 retest + TR-4 hold · FL out-of-balance state · IV-1 close back inside · Score: retest hold rate; continuation reach to the next node · `[AMT1 p.9]` `[MAMT p.12]` · ready.

**R-A03 Failed-auction traverse (loose 80%)** · OF-A4 · LC prior VA edge re-entered · TR-3 `b.c1` back inside + TR-4 hold · FL none · IV-1 back out · Score: traverse to the opposite edge given re-entry (72–80% claim; separate denominator) · `[AMT1 p.7–8]` `[AMTL p.8–9]` `[ABS p.12]` · ready.

**R-A04 Strict 80% rule** · OF-A5 · LC prior-day VA · TR-8 open outside VA then two consecutive 30 m periods inside · FL open outside VA · IV-1 · Score: full-traverse rate (`label.amt.80pct.two-period`) · `[MAMT p.18]` · ready.

**R-A05 POC tell** · OF-A6 · LC POC of the balance · TR: ≥2 touches without `h` hold (chop case) vs `b.c1` through + retest hold (traverse case) · FL inside balance after re-entry · IV n/a · Score: VAL / VAH reach split by POC behaviour · `[AMTL p.9]` `[RTVP p.5]` · ready.

**R-A06 MAMT Failed Auction setup** · OF-A7 · LC older balance's POC (naked prior POC) after a break from the established balance · TR-2 rejection at that POC — instant (r=0.5, k=5, the MAMT reading) or after a deep dip into the prior balance that still fails to hold (`[AMTL p.10]`), the tag depth a printed column · FL balance → break sequence present · IV-3 acceptance at the older POC · Score: reach of the *far* boundary of the established balance (VAH after a downside break, VAL after an upside break; both directions `[MAMT p.10–11]`), the 80% claim on its own denominator · `[MAMT p.9–11, p.26]` · ready.

**R-A07 Break-retest continuation** · OF-A8 · LC broken balance boundary (VAH / VAL, shelf, IB edge) · TR-3 `b.c1` + TR-1 retest + TR-4 hold · FL HTF direction agrees (OF-A9) · IV-1 back inside · Score: hold rate on the retest; reach of the next value area · `[RTVP p.6, p.8]` `[MAMT p.12]` `[WIC p.5, p.8]` `[TRAP p.6–7]` · ready.

**R-A08 Re-accept flips bias** · OF-A8 · LC balance boundary · TR-3 back inside + TR-4 hold · IV-1 · Score: opposite-edge reach · `[MAMT p.12]` · ready (same objects as R-A03; kept as MAMT's own row).

**R-A09 Traverse without hold** · OF-A8 · LC whole balance · TR: `b.c1` through both edges with no `h` hold inside · Score: continuation share on later retests · `[MAMT p.12]` · ready.

**R-A10 Open-type / day-type gate** · OF-A10 + OF-A11 · LC prior value / range references for the test-drive · TR-8 first 30 minutes · Score: `label.amt.open.30m` vs `label.amt.day` transition matrix; the MAMT four-class set `label.amt.day.mamt4` (trend = beyond IB×2, neutral extreme, neutral, normal `[MAMT p.20]`) as a second, separate label with its ES shares as the recompute claim; fade vs continuation outcome by label; agreement with Jumbo `day_type` · `[AMT1 p.10–11]` `[MAMT p.18, p.20, p.23]` · context.

**R-A11 Profile-shape gate** · OF-A12 · LC `balance.vp-shape` of prior RTH / overnight / composite · Score: next-session path class and edge-reject rate by shape *and by direction*, P and b both scored, so that the three authors' claims print separately — AMT1 "expect balance after", RTVP "continuation in the drive direction once the range at the top / bottom resolves", MAMT "P resolves down, B resolves up" `[AMT1 p.6]` `[RTVP p.10–11]` `[MAMT p.7]`; trending-profile "no trade" share · `[AMT1 p.6]` `[RTVP p.7–11]` `[MAMT p.7–8]` · context.

**R-A12 Overnight inventory and LVN** · OF-A13 · LC `value.vp.on` LVN / shelf — both drawn as bands on the `[MAMT p.14]` schematic (the LVN box spans the low-volume stretch between the two humps, the shelf box sits at the edge of the hump nearest the open, a red "POC alignment" line marks the RTH POC inside the LVN box); the net-long example is drawn, the net-short mirror is the same object · TR-4 hold vs TR-3 break at the open · FL-11 net overnight delta sign · IV-1 · Score: respected / disrespected shares; open direction vs inventory sign · `[MAMT p.14, p.26]` · pending (delta sign needs trades; bar proxy is a named variant).

**R-A13 Overnight touch statistics** · OF-A14 · LC `range.on.1800-0930` H / L, ONVAH / ONVAL / ONVPOC, `lvl.mpoc.eth`, `lvl.pib.*`, `lvl.pclose`, `lvl.halfgap` · TR-1 touch in RTH · Score: MAMT p.21–23 tables recomputed on NQ (94% ONH-or-ONL, 73% MPOC given open inside the prior ETH balance) · `[MAMT p.15–16, p.21–23]` · ready.

**R-A14 TPO unfinished business** · OF-A15 · LC `tpo.single`, `tpo.poor.*` (targets), `tpo.excess` (holds) · TR-1 touch · IV-1 · Score: single-print fill / repair, poor-extreme revisit, excess hold on first test — at both extremes (`[TPO p.6]` draws Excess Low and Excess High; `[TPO p.7]` draws the poor low as an extreme two letters wide with no tail); the presence flags are not the score · `[TPO p.5–9]` `[C3 p.6]` · ready.

**R-A15 IB extension read** · OF-A16 · LC `range.ib` · TR-3 `b.c1` beyond IB after 10:30 · Score: continuation share after a single-side extension (the printed definition is the close beyond the broken edge: "Closes Above IBH / Below IBL (Single IB Break)" `[MAMT p.23]`); rotation share when IB holds; comparison to `range.6-9.published` (expected null) · `[TPO p.8]` `[MAMT p.19, p.23]` `[XF p.8]` · ready.

**R-A16 Ledge trade with confluence** · OF-A17 · LC `value.kz` ledge stacked with VWAP band, prior VA edge or naked POC · TR-2 + TR-13 · FL-17 · IV-3 · Score: reject at a stacked ledge vs a lone ledge · `[VP2 p.4–8]` · ready.

**R-A17 Two-transition extremes** · OF-A19 · LC LVN / shelf / ledge with a return to balance behind it vs tails · TR-2 · Score: reject rate with vs without the second transition · `[MATH p.13, p.15]` · ready.

**R-A18 C3 balance-position bias** · OF-A20 · LC balance edges; single print above / below · TR-2 rejection from the balance (bullish with an unfilled single above; the mirror — rejection with an unfilled single below → bearish — is the same object) or TR-4 acceptance below (bearish; acceptance above → bullish as the mirror); the source prints one example each way `[C3 p.6]` · FL avoid levels inside the balance · IV-12 · Score: single-print reach after rejection · `[C3 p.6–7]` · ready.

### B4. Flow lessons

**R-F01 VWAP deviation fade with absorption** · OF-F7 · LC `env.vwap.eth.sd1 / sd2` (the exchange-session VWAP the lesson's settings and chart draw; `env.vwap.rth.*` and the 2.5 / 3 multipliers are named variants), upper band = premium (fade short), lower band = discount (fade long) · TR-1 touch beyond ±1 (ideally ±2) + TR-13 · FL draw beyond the band not still open (`lvl.owed.nearest` beyond the band) · IV-3 · Score: reversal to the VWAP median given touch + absorption vs touch alone · `[VWAP p.3–4, p.9]` · ready.

**R-F02 CVD three-step** · OF-F7 · LC any level · TR-24 · blocked (`flow.cvd.trade` tape-trusted no; rebuild spec: divergence = price new extreme vs CVD not, within the grid window, per construction) · `[VWAP p.6]` `[FP9 p.6]` · blocked.

**R-F03 Anchored VWAP convergence** · OF-F7 · LC `env.vwap.anchored.*` where session, weekly and swing / event anchors converge (≤ `tR`) · TR-2 + TR-13 · Score: reject rate at convergences · `[VWAP p.7]` · ready.

**R-F04 Footprint stacked-imbalance magnet** · OF-F5 · LC `flow.footprint.stack3` zone · TR-1 return + TR-17 · Score: revisit and hold rate; overlap with `flow.absorption.A` (must not be identical) · `[FP8 p.6–7]` · pending.

**R-F05 Footprint absorption stack** · OF-F6 · LC VP ledge / value edge / old POC · TR-17 candle-vs-delta disagreement, then candle POC flip · FL location class · IV-1 · Score: reversal share after disagreement; after disagreement + flip · `[FP9 p.3–7]` · pending.

**R-F06 DOM absorption at a level** · OF-F1 + OF-F3 · LC shelf / ledge / value edge / old high or low, marked first `[DOM6 p.4]` · TR the source's read has three parts `[DOM6 p.6]`: (1) aggression into the level with no follow-through, measurable as `flow.absorption.A` over a zone of up to 3 ticks `[DOM6 p.4]`, with a fast tape into the level `[DOM5 p.6]` (TR-22, pending); (2) stacked size that stays and reloads: at the touch this is `flow.absorption.B` (blocked, fires every session), behind the touch it is not measurable with MBP-1 `[DOM6 p.5–6]` `[JJX L310–314]`; (3) delta agreeing, positive delta with no upward progress = trapped buyers, a per-bar delta read (TR-19, pending). Phase 1 scores part (1) alone and (1) + (3); part (2) is blocked · FL none · IV-13 · Score: reversal ≥ 0.25·R share after (1) and after (1) + (3); absorption vs exhaustion split by volume at the stall `[DOM6 p.7]` · `[DOM5 p.6–7]` `[DOM6 p.3–7]` · ready for (1), pending for (3), blocked for (2).

**R-F07 Iceberg reload** · OF-F4 · LC level · TR-26 · blocked (`flow.absorption.B` fires every session; iceberg inference is a weak flag per `[JJX L171]`) · `[DOM7 p.4]` · blocked.

**R-F08 ABS four-check absorption** · OF-F8 · LC a real extreme only (shelf / ledge / LVN / minor node / prior-day VA), never POC `[ABS p.6–7]` · TR `flow.absorption.A` (effort into a passive wall, no reward), then the reward system `flow.reward.3tick` `[ABS p.4]`, then a second, opposite aggression `[ABS p.8–9]`; entry on the retest of the reward system, not on the wall `[ABS p.9]` · FL reversal-only use `[ABS p.5]`; the CVD-median check `[ABS p.5]` is blocked until CVD is rebuilt and has no stand-in; the time-and-sales refresh read of the opposing side `[ABS p.4]` is the digit read (TR-16, pending) · IV-13 · Score: failure share without the reward system (the 27% claim) vs with; reject at an extreme vs at POC (the coin-flip claim `[ABS p.6]`); delta-spike rows at VAH / VAL recorded as spike sign × extreme × outcome (both of the lesson's examples are buy spikes) `[ABS p.10–11]`; the wall and the reward retest are drawn as a band, not a price `[ABS p.4, p.9]` · `[ABS p.3–13]` · pending (CVD-median component blocked).

**R-F09 STOP three-step read with the four absorption stages** · OF-F9 · LC the level from the thesis; the HTF auction position decides who should be in control `[STOP p.6]` · TR stage 1 initial defence = `flow.absorption.A`; stage 2 replenishment, the level refreshing as it is hit with ≥ 3 ticks of replenishment `[STOP p.10]`, is BBO reload at the touch, which is `flow.absorption.B` (blocked) and behind the touch not measurable; stage 3 exhaustion = the aggressor's prints shrinking (`flow.digits.thinning`, pending) and delta turning (TR-19, pending); stage 4 lift-off = the absorber turns aggressive, 2–4 upticks (`flow.reward.3tick`, pending); entry within 1–2 ticks of stage 4 `[STOP p.12, p.14]`; the digit classes are read off ES clips (MotiveWave EPZ25 on p.11–13), so on NQ `flow.digits.thinning` names its classes per instrument · FL location first `[STOP p.6]`; a re-entry passes every box from zero `[STOP p.14]` · IV-15, IV-16 · Score: stage 1 → 3 → 4 transition counts without stage 2; outcome by stage entered; the 27% figure recomputed as its complement `[STOP p.10]` · `[STOP p.6–15]` · pending (stage 2 blocked).

**R-F10 Protected-low trailing** · OF-F10 · LC `lvl.protected.low` / `high` · TR-19 highest delta print side confirms · IV-9 · Score: break rate of protected levels; MFE after each new protected level · `[RD p.4–5]` `[K18 p.8]` · pending.

**R-F11 Delta print at an LVN extreme** · OF-F10 · LC `value.kz` LVN / minor node with `dp.max` at it · TR-1 touch → wick reaction (TR-2 with k=5) · Score: repeat-reaction count per zone · `[RD p.9]` · pending.

**R-F12 Who's-in-control arrival read** · OF-F11 · LC balance extreme · TR-23 approach speed (aggressive vs drift) then TR-2 / TR-4 · FL prior balance break-retest state · IV-1 · Score: defence rate by arrival class · `[WIC p.3–5, p.8–9]` · pending.

**R-F13 Trapped buyers, one retest** · OF-F12 · LC redrawn balance extreme with the trapped print at it (`dp.max` at the high, `dp.min` at the low; the source's example is the high, its checklist reads "heavy one sided volume at an extreme"); intraday range off the session open · TR-3 intraday breakout + TR-1 retest + TR-4 hold, in either direction · FL-16 two prior-session failures at the level · IV-6 · Score: retest-hold rate given the trap print and prior failures; reach inside the normal session range (SessionStat Asia) · `[TRAP p.3–12]` · pending.

**R-F14 BigTrades body-vs-wick and 350% line** · OF-F13 · LC `flow.footprint.imb350` at the same price as a BigTrades print (sell and buy mirrors; the chart marks it as a small box around the print's candle) · TR-14 + TR-18; wait for the retest · FL both sides absorbed → wait for the break · IV-8 · Score: retest reaction rate; body vs wick print outcome split · `[BIG p.4–6]` · ready for TR-14, pending for TR-18.

**R-F15 Origin of the move (short gamma)** · OF-F14 + OF-F15 · LC `flow.ofm.catalyst` (the OFM line at the first absorbed aggression, the cluster boxed; long and short both drawn), refill area below (above), wicks above (below) · TR-21 drive takes out the wicks after the failed squeeze; entry on the retest of the failure area / the OFM line · FL-12 short gamma; HTF: balance left, thin volume behind, level that should reject; CVD not against (blocked, stand-in none) · IV-8 · Score: A+ frequency; retest availability; reach 1–3R in points · `[BIG p.7–11, p.18]` `[OFM p.6–14]` `[CONT p.10]` · pending.

**R-F16 Balance-day fade (long gamma)** · OF-F14 · LC extreme where aggression failed to get paid (top or bottom of the range; drawn as a box from the first absorbed print to the retest) · TR-1 test back into it + TR-13 · FL-12 long gamma · IV-3 · Score: reach of where the other side last had control · `[BIG p.15–16, p.18]` · ready.

**R-F17 Refill-zone touch** · OF-F16 · LC `flow.refill.zone` (per-print ≥ 60 and burst-total ≥ 60 readings; NQ-vs-MNQ contract unit unstated) · TR-20 touch with penetration ≤ 32 ticks, resting 12 ticks inside, cancel 30 min (the paper's tested grid: stops 25–65, targets 20–100 ticks) · FL memory (held earlier / prior day), construction, location, flow-state features · IV-5 30 min; IV-8 · Score: hold rate (42% base), by memory decile; median dip past the touch (18 ticks); PF 1.80 vs 0.81 is an execution claim, recorded as penetration-depth outcomes only · `[REF p.5, p.8–12, p.23]` · pending.

**R-F18 Squeeze without failure** · OF-S10 · LC catalyst; entry where buyers hit the move and get absorbed · TR-21 fast release (tape speed; the charts print "Speed of Tape (10)", the unit of the 10 unstated) with no failure, then TR-13 · IV-8 · Score: continuation after a non-failing squeeze · `[CONT p.11]` `[OFM p.5]` · pending.

### B5. Regime lessons

**R-R01 GEX regime gate** · OF-R1 · LC `value.node.flip.<product>` (three named readings, A1.2), call / put walls (text: one per side; chart: the ranked top-3 on either side of spot), max pain · TR-27 · FL-12 (regime by net-GEX sign and by spot vs flip, both printed) · IV-14 · Score: path class, edge-reject rate and range / expected range by regime (expected range = price × VIX / √252, the VIX4 p.3 formula); wall hold rate at the call wall and at the put wall, each on its own side, split by regime and by the p.14 location state (approaching the strike: reject vs accept; already at the strike: contained vs trending away); pin distance at close to the nearest of call wall / put wall / max pain · `[GEX p.6–16, p.18–20]` `[DTM L21–22]` `[CEX L166–168, L455–456]` (user) · context (daily-known levels; 0DTE intraday is a lag proxy).

**R-R02 VIX regime gate** · OF-R2 · LC none · FL-4 (the printed cut points 13 / 14 / 15–18 / 20), FL-3, FL-13 · Score: realized range by VIX band and against the printed implied range (Expected Daily Move (%) = VIX / √252, p.3 figure; VXN, the Cboe Nasdaq-100 twin in the inventory `[INV L610]`, as the named variant `vol.vxn`); edge-reject rate by contango / backwardation (VX curve, unscored until joined); fade vs break shares by VIX direction (daily; the four intraday combos of p.6 need intraday VIX, not in the inventory); balance-day rotation share by VIX falling vs rising (p.9) · `[VIX4 p.3–9]` · context.

**R-R03 Thesis validity** · OF-R3 · LC thesis box (validity band) · IV-12 · Score: label table only · `[C1 p.3–4]` `[C3 p.7]` · context.

**R-R04 Triad IØD / RFZ** · OF-R4 · TR-25 · blocked until SMT is rebuilt with `[CEX L129]` (prior H / L taken on one index but not another, multi-timeframe) at level set S1 ∪ {VAH, VAL, single prints} · `[C1 p.5, p.7]` · blocked.

### B6. Live-session case studies (Sires)

**R-S01 Refill long at the range bottom** · OF-S1 · LC the failure band at either end of the dealing range where the arriving side was absorbed: the printed long is sellers absorbed at the bottom (a grey band with the two absorption prints circled; ticket stop 13.0 pts under the entry) `[NYAM p.4–5]`, the printed short is "Buyers are being absorbed. I want these buys to be absorbed. They are, okay, I'm in" `[K18 p.10]`; "Same mechanism, read on both sides of the market" `[K18 p.11]` · TR-13 · IV-8 · Score: reach of the HTF objective, per side · `[NYAM p.4–5]` `[K18 p.10–11]` · ready.

**R-S02 Third-retest short** · OF-S2 · LC a support band under price that sellers have hit twice with no aggressive buyers stepping in (the NYAM p.6–7 figure: a two-line band under a falling market, tested from above three times; the mirror is a resistance band hit twice with no aggressive sellers) · TR-1 third test from the same side with no defence (no `flow.absorption.A` for the other side), then continuation through the band with the sellers — the trade is not a fade of the band · FL-16 · IV-6 just beyond the band (the ticket: 12.75 pts above the entry, inside the band) · Score: give-way vs hold rate on third tests (the printed case is the hold, "stopped for −$100, the level held anyway") · `[NYAM p.6–7]` `[K18 p.11]` · ready.

**R-S03 OFM level defended a second time** · OF-S2 + OF-F15 · LC the OFM level (`flow.ofm.catalyst`) `[K18 p.7]` · TR the second defence of the level with real selling participation; the source's tell is refreshing size at a steady pace and steady size across the second and third refresh `[K18 p.7, p.11]`: the print side of that tell is `flow.digits.thinning` (pending), the resting-size side is BBO reload (`flow.absorption.B`, blocked) · FL gamma near the flip allowed `[K18 p.4]` · IV-9 protected highs · Score: outcome by refresh-consistency class on the print side only · the mirror (buyers defending an OFM level a second time from above: "these buyers are failing, they're refilling again" `[K18 p.11]`) is the same object on the long side · `[K18 p.7–8, p.11, p.14]` · pending (reload component blocked).

**R-S04 ATH pullback OFM long** · OF-S6 · LC where sellers were trapped on the weekly delta profile; `flow.footprint.imb350` box (printed with a height on the live chart, a few points tall `[K2345 p.5]`) · TR-18 + TR-21 · side: the long is printed; the short mirror of this box is a named variant (K2345 p.9's short is the microbalance read of R-S05) · FL sellers failed to reclaim the prior range (repeated) · IV-9 · Score: continuation after the flagged box · `[K2345 p.4–5]` · pending.

**R-S05 Microbalance breakout** · OF-S10 · LC short-term microbalance (a price-defined box, ≈ 7 pts tall on the 40-tick range chart) · TR-3 `b.c1` beyond it, up for the printed long `[K2345 p.7]` and down for the printed short "on a lower push after the same kind of microbalance read" `[K2345 p.9]` · IV-9 protected low / high · Score: reach of the HTF level, per side · `[K2345 p.7–9]` · ready.

**R-S06 Two-reason level** · OF-S7 · LC a marked reaction area drawn as a band between two prior-reaction prices (`[K10 p.7]` two red lines; `[K10 p.12]` the "red rejection area" rectangle) + minor HVN (or + gamma node) within `tR` · TR-2 short from below (p.7) and the printed long mirror from above with absorption at the same band (p.8) · IV-6 beyond the rejection extreme (the tickets print 20 ES ticks and R:R 1.00 against the text's 1.5R) · Score: reject rate with two reasons vs one; 1.5R reach in points beside the tickets' 1:1 · the source charts are ES (ES-202609, 2-minute); the NQ recompute is a labelled transfer · `[K10 p.6–8, p.12]` · ready.

**R-S07 Areas-not-direction thesis** · OF-S9 · LC reaction areas both sides, each a band (the shelf where a side held, composite minor HVNs; drawn as rectangles a few points tall `[ANAT p.7–9]`) + owed objective (the written thesis still names it: "my overall goal is price to push higher" `[ANAT p.4]`) · TR-13 "something is holding" · IV-15 (re-entry only while price is back inside the same band `[ANAT p.7]`), IV-16 · Score: 44%-win-rate-shaped outcome distribution (MFE / MAE) at the printed tickets 35 / 188 (long), 15 / 211 (short) and 115 / 248 ticks, both sides; nine trades 10:14–10:32 `[ANAT p.6]` · `[ANAT p.4–11]` · ready.

**R-S08 Continuation short at a minor node** · OF-S10 · LC 5 m minor volume node (drawn as a band ≈ 20 pts tall `[CONT p.4]`) with negative delta stacking; established balance top (the failed-auction wicks, a red band `[CONT p.5]`); yearly-composite low-participation zone · TR-2 at the node; TR-3 + retest for re-entry (the refill zone, a red band ≈ 5 pts; ticket SELL 1, R:R 6.11, 9.00-pt stop, 55-pt target `[CONT p.8]`) · FL HTF bias short; the printed flip: "unless price closes above it with real, extreme buying pressure. If that pressure shows up, the read flips to a retest and longs back toward the session's VWAP" `[CONT p.5]` · FL-12 gamma (exit rule) · IV-15 re-entry gate · Score: same-side control count at the refill zone; slice-through vs stall at composite LVNs · `[CONT p.4–9, p.12–13]` · coincidence (named): CONT p.8 / p.10 print SD+1 / SD+2 beside the refill zone and the OFM level → overlap with `env.vwap.*` (R-F01) printed as a column · pending (delta stacking) / ready (node geometry).

**R-S09 Open above value** · OF-S11 · LC prior VAH, current-day developing VAH · TR-8 wait ~10:00, then TR-3 `b.c1` above the current VAH with buy imbalances (TR-17) and TR-1 retest + TR-4 hold · FL open cell above value · IV-1 · Score: retest-hold rate; reach of the HTF objective; time-of-day split · side: the open-above-value long is the drawn setup (`[AVG p.22]` sketch); the open-below-value mirror is a named variant, not printed · `[AVG p.21–22]` · ready-bar (imbalance add pending).

### B7. Pine and indicator tier-2 claims (recompute rows; frameworks OF-P1 / OF-P2)

**R-P01** σ-band ±0.25σ touch → reversion to open by 12:00 (hour-8 78.4% n=732) · LC `env.tbr.sigma025` · TR-1 / TR-2 · `[PINE AM TBR - NQ Stats.txt]`.
**R-P02** Hourly sweep of prior-hour H / L by NY hour, conditioned on open vs prior open; retrace to the swept level ≈90–95% · LC `range.gb.hour` · TR-3 / TR-7 · `[PINE NQ Hourly Retracements 12y Stats with Levels.txt:185–313]`.
**R-P03** Magic-hour box break → mid target (07:00 82.8 … 23:00 68.5); zones Z1–Z6 by extension % · LC hour boxes · TR-3 then TR-7 · `[PINE magic_hours:55–184]`.
**R-P04** Raid ≥5 pts with 120-min close-back · LC any range · TR-5 (`grid.pine.raid5-120`) · `[PINE Session Raid Stats.txt:36–37]`.
**R-P05** London 25%-body level: NY low below the London 25% level then NY close back above it (and the bear mirror), counted per regime · `[PINE Session Range Candles + 25% Level.txt:875–960]`.
**R-P06** London-vs-Asia and NY-vs-London first-hit tables (e.g. London opens above the Asia mid → Asia high first 73.84%; NY opens above the London mid → London high first 76.68%; Asia high hit in NY 78.41% if hit in London else 59.69%; Asia low 78.54% / 54.64%, both sides printed at `:363–368`) · LC Asia / London H / L / mid · `[PINE NQ Statistical Mapper.txt:283–366]` (also `nq_stats_mapper`; `NY vs Asia Statistical Levels.txt` draws the levels, the numbers sit in the mapper).
**R-P07** ORB 5 m / 15 m extreme-first → next break; midpoint retest 81.8–88.4% · LC `range.or.*` · `[PINE NY 5m and & 15m Orb Statistics & LTF Candle structure.txt:141–144, 873–1189]`.
**R-P08** IB break combos; the script's midpoint retest is a band, not a touch: price must first leave the IB mid by more than 0.1 % of the mid price and the retest counts when a later bar's high or low comes back within 0.1 % (`:279–286`) · LC `range.ib` · `[PINE Initial Balance Statistical Mapping.txt]`.
**R-P09** Open vs prior RTH → no-break rates (84.11 / 81.82; inside 14.30 / 72.66 / 13.04) · LC `box.prior-rth` · `[PINE NQ Stats RTH Breaks with stats.txt]`.
**R-P10** Floor-pivot gap context (context rows only, not a family); "GZ" in its table is the file's daily Golden Zone, 0.5–0.618 of the prior daily range measured from the low (`:321–330`; from the high as an option), not a gap · `[PINE Daily Floor Pivots.txt:321–330, 1159–1196]`.
**R-P11** First-presented FVG per hour and hardcoded effectiveness · LC `gap.fvg.first.clock` · `[PINE First presented FVG…:254–304, 342–353]`.
**R-P12** HTF sweep + CISD screener; body / wick / close variants · LC `block.*`, `cisd.*` · `[PINE HTF Sweep Model with CISD Table.txt:136–142, 300–408]` `[OSF]`.
**R-P13** Midnight-open hit 73.75% · LC `lvl.tdo` · `[PINE nq_stats_mapper:311–313]`.
**R-P14** 4H HOD / LOD checkpoint elimination (10:00 checkpoint HOD-in 68.90% n=582) · column `hod_lod_time` · `[PINE 4H HOD LOD Checkpoint Analysis.txt:556–730]`.
**R-P15** Session percentile bands P10–P90; RE×1…6; manipulation / distribution from the open · LC `env.pine.*` · `[PINE Session Statistical Levels.txt]` `[PINE Session Range Projections with stats.txt]` `[PINE Statistical OHLC Projections HTF.txt]`.
**R-P16** VIX/16 daily bands; 75.2% inside ±1 SD · LC `env.ev.vix16` · `[PINE Expected Volatility .txt]` `[PINE NQ Stats Price Distributions.txt]`.
**R-P17** Bar-distributed VP, 70% VA, daily 18:00 and Sunday weekly open lines · LC `value.vp.rth.ohlc1m`, `lvl.1800open`, `lvl.nwog` · `[PINE Sessions & VP with prev session VP & daily weekly opens.txt:216–289]`.
**R-P18** OHLC delta proxy · `flow.cvd.ohlc` · blocked as trigger with the other CVD rows · `[PINE Confluence Suite.txt:243–255]`.
**R-P19** Body gap ≥4 ticks near-edge fill · `gap.body.adjacent` · `[PINE 8020 System.txt]`.
**R-P20** MVFL bias vote: delta events ≥6× avg-50 (floor 3000) k-means zones as break / rejection levels; volume-anomaly zones (2.5× avg-20) as break / rejection levels; hysteresis 4 of 7 · LC `flow.delta.zone.kmeans`, `flow.vol.anomaly.zone` · TR-3 / TR-2 at those zones · rebuild on aggressor delta before scoring `[CEX L33]` (assistant) per the user's upgrade mandate `[CEX L17]` · `[MVFL L19–46, L139–150, L181–432]` · pending.

### B8. Conversation-sourced definitions (user turns; tier 1; no recipes beyond the authors above)

- SMT definition: a prior high / low taken on one index but not another, at multiple timeframes `[CEX L129]`; sister indices as a classify input `[FIND p.3]` → rebuild spec for `flow.smt.*` before any TR-25 use.
- Single-break days trade continuation inside the range at EQ / 75 / 25, or prior-day RTH 25 / 50 / 75 `[DTM L19]` (the earlier `[DRFL L906]` cite pointed at a file-attachment stub and is dropped) → `lvl.prior-rth.q*` as a location swap on R-J03 / R-J04.
- Gamma levels complement the 6–9; NDX levels felt better than QQQ on NQ; cross-asset reactions (SPX hits, NQ reverses without its own level) `[DRFL L327, L1096]` `[CEX L565, L455–456]` (user turns; the earlier line numbers pointed at turn headers or blank lines) → native + mapped node rows on `wiki/options-nodes.md`; cross-asset zone mapping is D3.
- Regime from GK / YZ / HAR-RV, not VIX alone `[DTM L23]` `[JJX L149]` → FL-2.
- Derived ranges inside named families; no free-form box `[JJX L148]` (user) → A1.1 grid; free-form search is D3.
- Absorption confirmation by pulling and stacking `[JJX L294]` → not measurable behind the touch; at-touch proxies only (OF-F4).
- Execute NQ, ES / SPXW as context, no overnight holds, prop firms `[DTM L266–268]` → FL-21.

---

## C. Swaps (one slot at a time)

### C1. Rules

1. A swap changes exactly one slot of one B recipe; the other four stay at the author's values. Two-slot changes are D.
2. Swapped values come only from the A inventories. The tape-trust gate applies to every TR swap.
3. Variants add: for recipe R with admissible sets of sizes `|L|, |O|, |T|, |F|, |I|`, the count is `|L| + |O| + |T| + |F| + |I|`, never the product.
4. An OF swap is admitted only where the second framework is stated by a source at the same location kind (listed per recipe); it is still one slot.
5. Rows whose coverage tables cannot be told apart are merged and the merge listed (`[METHOD]`, `wiki/clock-grid-and-bars.md`).
6. Every variant prints the same score line as its parent, with `faithful_of = parent`.

### C2. Named swap sets

| set | members | size |
|---|---|---|
| **SL-clock** | `range.5-9`, `range.7-9`, `range.8-9`, `range.london.00-03`, `range.london.0300-0330`, `range.asia.2000-2030`, `range.midnight.0000-0030`, `range.gb.asia`, `range.gb.london`, `range.gb.nyam`, `range.gb.10-11`, `range.gb.hour`, `range.rth.0930-1000`, `range.rth.1000-1030`, `range.lunch.1200-1230`, `range.moc.1500-1530`, `range.or.5m`, `range.or.15m`, `range.ib`, `range.on.1800-0930` | 20 |
| **SL-bar** | `bars.vol-elapsed`, `bars.dollar`, `bars.trade-count`, trade-level H / L | 4 |
| **SL-proj** | ±0.5, `lvl.mr.0.1` / `0.2` / `0.3`, ±1.0, 1.33, 1.66, `band.133-166`, `proj.overshoot.δ` (δ = 2 ticks, 0.1·W), 1.33 from-origin, 1.33 from-eq, ±2.0 — each level on both sides of the box (A1.2) | 13 |
| **SL-width** | `w.69`, `w.london`, `w.own`, `w.ev` — the width base of the projection ladder (A1.2); `w.ev` is a test variant only, no source draws it | 4 |
| **SL-inner** | EQ, Q25, Q75, range open, range close, `lvl.prior-rth.q{25,50,75}` | 8 |
| **SL-env** | `env.ev.*` (10 estimators × 5 refs), `env.ss.{avgHL60, medHL60, minavg60, weighted60, rth.avgHL60}`, `pz.approx.{A,B}`, `env.tbr.sigma025`, `env.pine.manip.*` (4), `env.pine.sessionstat.P10-P90`, `env.vwap.rth.sd{1,2,2.5,3}`, `env.vwap.anchored.*` (5) | 72 |
| **SL-value** | prior VAH / VAL / POC (trade VP; OHLC VP; VA 70 / 68 / 40), developing VAH / VAL, `value.vp.eth.prior` (+ MPOC), `value.vp.on` (ONVAH / ONVAL / ONVPOC / ON LVN / ON shelf), `value.vp.composite.{5d,20d,250d}`, `value.vp.box69`, `value.vp.dealing`, TPO VAH / VAL / POC | 25 |
| **SL-kz** | HVN, LVN, two-sided LVN, ledge, shelf, minor volume node, naked POC, `kz.two-transition` | 8 |
| **SL-tpo** | `tpo.single`, `tpo.excess`, `tpo.poor.high`, `tpo.poor.low`, IB H / L | 5 |
| **SL-flow** | `flow.absorption.A` price, `flow.bigtrade.100ny` cluster, `flow.refill.zone`, `flow.ofm.catalyst`, `flow.footprint.stack3`, `flow.footprint.imb350`, `dp.max` / `dp.min`, `flow.delta.spike`, `lvl.protected.{high,low}`, `flow.delta.zone.kmeans`, `flow.vol.anomaly.zone`, `flow.absorption.candle.jumbo` | 13 |
| **SL-candle** | `block.sweep.tbr.{2,3,5}m`, rejection block, `cisd.fractal.literal`, `gap.fvg.first.clock` (1 / 3 / 5 / 15 m), `gap.body.adjacent` | 10 |
| **SL-gb** | `lvl.tdo`, `lvl.nwog` (2 endpoints), `lvl.0930open`, PDH, PDL, `loc.gp`, `loc.pd50`, `lvl.1800open` | 9 |
| **SL-node** | OI top3 × 7 products, gamma top3 × 4, flip × 4, call wall / put wall / max pain × 4 | 35 |
| **SL-owed** | `lvl.owed.nearest` above / below | 2 |
| **ST-grid** | touch {t0, t2, tR}; reject r {0.25, 0.5} × k {5, 15, 30}; break {b.wick d ∈ 3, b.c1, b.c5}; hold h {15, 30}; fail-back {b.c1, b.c5} × k {15, 30}; reclaim; mid-retrace | 21 |
| **ST-candle** | `block.sweep.tbr.{2,3,5}m`, rejection block, `cisd.fractal.literal`, FVG formed / filled, `flow.absorption.candle.jumbo` k ∈ {1.5, 2.0, 2.5} | 10 |
| **ST-tape-ok** | `flow.absorption.A`, `flow.bigtrade.100ny`, `flow.bigtrade.75ldn` | 3 |
| **ST-tape-pending** | TR-15 … TR-23 objects (reward 3-tick, four stages, footprint diag 3× / 4×, stack, candle-delta disagreement, POC flip, 350% line, delta spike, dp.max side, refill touch, OFM sequence, tape speed, spread, approach speed, digits) | 16 |
| **ST-time** | `bin.0940-0950`, `bin.0930-0950`, `bin.0950-1000`, `bin.1000-1030`, after 10:00, after the 10:00 release, 10:30 IB close, two 30 m periods, 03:00–06:00 London, PM 13:00–16:00 | 10 |
| **ST-blocked** | CVD (5 constructions), SMT (3 rows), `flow.absorption.B`, `flow.bigtrade.q90` | 10 (listed, not run) |
| **SO** | second-framework swaps admitted at the same location kind: {OF-J1 ↔ OF-G1 on any box edge; OF-J2 ↔ OF-A8 break-retest on any box edge; OF-A1 ↔ OF-F7 at value edges vs VWAP bands; OF-A4 ↔ OF-A7 at prior value; OF-F8 ↔ OF-F9 at any absorption print; OF-F14 short-gamma ↔ long-gamma leg} | 6 pairs |
| **SF** | FL-1 … FL-17, FL-20, FL-21 (each as a slice, one at a time) | 19 |
| **SI** | IV-1 … IV-15 (IV-16 recorded, not swapped) | 15 |

### C3. Admissible swaps per recipe

| recipe | LC | OF | TR | FL | IV | variants |
|---|---|---|---|---|---|---|
| R-J01 | SL-clock (20) + SL-bar (4) + SL-proj (13) + SL-width (4) + SL-env (72) + SL-flow (13) | SO: OF-G1 (1) | ST-grid (21) + ST-candle (10) + ST-tape-ok (3) + ST-time (10) | SF (19) | SI (15) | 205 |
| R-J02 | SL-clock (20) + SL-proj (13) + SL-width (4) | — | side rule (both / first-edge / nearer-edge) (3) + ST-time (10) | SF (19) | SI (15) | 84 |
| R-J03 | SL-clock (20) + SL-inner (8) + SL-value (25) | SO: OF-A8 (1) | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 112 |
| R-J04 | SL-clock (20) + SL-inner (8) + SL-proj (13) + SL-width (4) | SO: OF-A8 (1) | ST-grid (21) + ST-tape-ok (3) + ST-time (10) | SF (19) | SI (15) | 114 |
| R-J05 | SL-clock (20) + SL-inner (8) | — | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 86 |
| R-J06 | SL-value (25) (value source / VA % / range reference) | — | — | SF (19) | — | 44 |
| R-J07 | width metrics `w.pct.0859close` / `w.pct.0930open` / `w.rel-prior-rth`; balance metrics (2) | — | — | SF (19) | — | 24 |
| R-J08 | SL-clock (20) + SL-proj (13) + SL-width (4) + SL-env (72) | — | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 167 |
| R-J09 | JJX London starts (4) + SL-proj (13) + SL-width (4) + SL-env (72) | SO: OF-G1 (1) | ST-grid (21) + ST-candle (10) + ST-tape-ok (3) | SF (19) | SI (15) | 162 |
| R-J10 | SL-owed (2) + SL-tpo (5) + SL-kz (8) + SL-gb (9) | — | — | SF (19) | SI (15) | 58 |
| R-J11 | SL-env (72) + SL-proj (13) + SL-width (4) | — | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 147 |
| R-J12 | P-zone upgrades (history-60, vol-scaled, volume-filter, VP-node-snap, `pz.approx.B`, anchors 09:00 / 09:30 / 10:00 / 18:00) (9) + SL-env (72) + SL-proj (13) + SL-width (4) | — | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 156 |
| R-J13 | SL-env (72) + SL-inner (8) + SL-width (4) + overshoot δ (2) | — | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 144 |
| R-J14 | SL-inner (8) + SL-proj (13) + SL-kz (8) | — | ST-candle k grid (3) + ST-tape-ok (3) + ST-tape-pending (16) | SF (19) | SI (15) | 85 |
| R-J15 | SL-inner (8) + SL-proj (13) + SL-kz (8) + SL-gb (9) | — | thresholds {100, 75, 50, 30–60, q99} (5) | SF (19) | SI (15) | 77 |
| R-J16 | SL-inner (8) | — | ST-tape-pending (16) | SF (19) | SI (15) | 58 |
| R-J17 | SL-kz (8) × distance tR | — | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 66 |
| R-J18 | SL-proj (13) + SL-width (4) + SL-env (72) + SL-owed (2) | — | ST-candle (10) | SF (19) | IV-7 variants (2) | 122 |
| R-J19 | SL-gb (9) + SL-candle (10) | — | ST-grid (21) | SF (19) | SI (15) | 74 |
| R-J20 | as R-J01 | — | ST-time (10) | FL-13 variants (3) | SI (15) | 28 |
| R-J23 | (each of the 7 boxes is itself the swap of R-J01 / R-J03) + SL-proj (13) + SL-width (4) per box, `w.own` faithful | — | — | — | — | 14 + 17 = 31 |
| R-J25 | fractal 3 / 5 / 7 swings (3) + SL-inner (8) | — | ST-grid (21) | SF (19) | SI (15) | 66 |
| R-G01 | SL-clock (20) + SL-gb (9) | SO: OF-J1 (1) | ST-grid (21) + ST-tape-ok (3) + depth d (3) + cap k (3) | SF (19) | SI (15) | 94 |
| R-G02 | SL-clock (20) + SL-gb (9) | SO: OF-J1 (1) | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 88 |
| R-G03 | step 5 / 15 / 30 min (3) + SL-clock (20) | SO: OF-J1 (1) | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 82 |
| R-G04 | `lvl.0930open` → `lvl.1800open`, TDO, range open (3) | — | ST-grid (21) | SF (19) | SI (15) | 58 |
| R-G05 | SL-gb (9) | — | ST-grid (21) | SF (19) | SI (15) | 64 |
| R-G06 | endpoint settle / close (2) | — | — | FL-14 (3) | — | 5 |
| R-G07 | impulse source NYAM / 6–9 height / HTF swing (3) + `loc.pd50` (1) | — | ST-grid (21) + ST-candle (10) + ST-tape-ok (3) | SF (19) | SI (15) | 72 |
| R-G08 | SL-gb (9) + SL-clock (20) | — | ST-grid (21) | SF (19) | SI (15) | 84 |
| R-G09 | stack members from SL-gb + SL-clock edges (any 3 within tR) | — | ST-grid (21) | SF (19) | SI (15) | 55 |
| R-G10 | SL-clock (20) | — | ST-grid (21) | SF (19) | SI (15) | 75 |
| R-A01 | SL-value (25) + SL-kz (8) | SO: OF-F7 (1) | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 92 |
| R-A02 | SL-kz (8) + SL-value (25) | — | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 91 |
| R-A03 | SL-value (25) | SO: OF-A7 (1) | ST-grid (21) | SF (19) | SI (15) | 81 |
| R-A04 | SL-value (25) | — | period 15 / 30 / 60 m (3) | SF (19) | SI (15) | 62 |
| R-A05 | POC source trade / OHLC / TPO (3) | — | touch counts {2, 3} (2) | SF (19) | SI (15) | 39 |
| R-A06 | naked-POC age (1 / 3 / 5 sessions) (3) + SL-value (25) | SO: OF-A4 (1) | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 87 |
| R-A07 | SL-value (25) + SL-kz (8) + SL-clock (20) | SO: OF-J2 (1) | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 112 |
| R-A08 / R-A09 | SL-value (25) | — | ST-grid (21) | SF (19) | SI (15) | 80 each |
| R-A10 / R-A11 | label sources (prior RTH / overnight / composite) (3) | — | — | SF (19) | — | 22 each |
| R-A12 | ON profile scope 18:00–09:30 vs 20:00–09:30 (2) | — | ST-grid (21) | SF (19) | SI (15) | 57 |
| R-A13 | SL-value (25) + SL-clock (20) | — | ST-grid touch (3) | SF (19) | — | 67 |
| R-A14 | period 15 / 30 / 60 m, row 1 pt / 4 ticks, trade-visited / OHLC (6) | — | ST-grid (21) | SF (19) | SI (15) | 61 |
| R-A15 | `range.ib` → SL-clock (20) | — | ST-grid (21) | SF (19) | SI (15) | 75 |
| R-A16 | SL-kz (8) + confluence partner from SL-env / SL-value (2 sets) | — | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 68 |
| R-A17 | SL-kz (8) | — | ST-grid (21) | SF (19) | SI (15) | 63 |
| R-A18 | SL-tpo (5) + SL-value (25) | — | ST-grid (21) | SF (19) | SI (15) | 85 |
| R-F01 | band 1 / 2 / 2.5 / 3, anchor ETH / RTH / fixed-06, dispersion SD / MAD / RMS (10) + SL-value (25) | SO: OF-A1 (1) | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 94 |
| R-F03 | anchor pairs (5) | — | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 63 |
| R-F04 / R-F05 | stack 2 / 3, ratio 3× / 4× (4) + SL-kz (8) | — | ST-tape-pending (16) | SF (19) | SI (15) | 62 each |
| R-F06 | SL-kz (8) + SL-value (25) + SL-gb (9) | — | ST-tape-ok (3) + ST-tape-pending (16) | SF (19) | SI (15) | 95 |
| R-F08 | SL-kz (8) + SL-value (25) (prior-day VA) | SO: OF-F9 (1) | ST-tape-ok (3) + ST-tape-pending (16) | SF (19) | SI (15) | 87 |
| R-F09 | thesis level from SL-value / SL-kz (33) | SO: OF-F8 (1) | stage entered 1 / 2 / 3 / 4 (4) | SF (19) | SI (15) | 72 |
| R-F10 / R-F11 | SL-kz (8) | — | ST-tape-pending (16) | SF (19) | SI (15) | 58 each |
| R-F12 / R-F13 | SL-value (25) + `range.dealing` (1) | — | ST-grid (21) + ST-tape-pending (16) | SF (19) | SI (15) | 97 each |
| R-F14 | SL-flow (13) | — | thresholds (5) + ST-tape-pending (16) | SF (19) | SI (15) | 68 |
| R-F15 | SL-flow (13) | SO: long-gamma leg (1) | ST-tape-pending (16) | SF (19) | SI (15) | 64 |
| R-F16 | SL-flow (13) + SL-kz (8) | SO: short-gamma leg (1) | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 80 |
| R-F17 | zone print threshold 60 / 80 / 100, per print or per burst (6) + depth 12 / 18 / 32 ticks and the printed grid bounds 25 / 65 (5) | — | ST-tape-pending (16) | memory / construction / location / flow (4) + SF (19) | cancel 15 / 30 / 60 min (3) + SI (15) | 68 |
| R-F18 | SL-flow (13) | — | ST-tape-pending (16) | SF (19) | SI (15) | 63 |
| R-R01 | products (7) + node kinds (4) + flip reading (3) + wall rank (3) + GEX weighting OI / volume (2) | — | TR-27 variants (2) | SF (19) | SI (15) | 55 |
| R-R02 | — | — | — | FL-3 / FL-4 / FL-13 variants (8) | — | 8 |
| R-S01 … R-S09 | SL-kz (8) + SL-value (25) + SL-flow (13) per recipe | — | ST-grid (21) + ST-tape-ok (3) | SF (19) | SI (15) | 104 each |
| R-P01 … R-P20 | one location family each (as listed) | — | ST-grid (21) | FL-1 (year) + slice L (2) | — | 23 + family size each |

Totals are sums; they are printed by the runner, not fixed here. SL-width (width base) and SL-proj (level) are two different slots of the same location: swapping one keeps the other at the faithful value (`w.69` and the level the source draws); a row that changes both is a two-slot change (D). The R-J02 total was corrected here (the earlier 58 omitted SI). Side mirrors: where a Green Bird or Sires recipe is stated on one side only, the mirror is a one-slot swap `side` (2) on that recipe — R-G04, R-G09, R-S04, R-S09 (named, not printed); R-S01, R-S02, R-S03, R-S05, R-S06, R-S07 and R-S08 print both sides and are scored on both as the faithful row (`[K18 p.11]`: "Same mechanism, read on both sides of the market"). Merges by indistinguishable coverage tables are expected to collapse most SL-env and SL-clock members (`wiki/clock-grid-and-bars.md`).

---

## D. Discovery only after scores

### D1. Score line (per recipe and per variant)

`recipe | variant | faithful_of | n | year | slice | touch | reject|touch | hold|break | fail-back|wick | target1 reach | target2 reach | time-to-touch p50 | MFE p50 | MAE p50 | grid-flip count | status`

- Every share carries `n` and a Wilson 95% interval; `better` only when intervals do not overlap the parent (`SPEC.md` §6).
- Slices: year (FL-1), day type (FL-8), open cell (FL-9), vol tercile (FL-2), gamma regime (FL-12), session (FL-5). One slice per line; no pooled multi-slice claims.
- Recompute rows (R-J06, R-J07, R-A13, R-P*) print the quoted source cell beside the recomputed cell.
- MFE / MAE are in points from the author's invalidation distance (`[C2 p.4]`); no P&L, no R-multiples on account size.

### D2. Gate

Discovery starts only when all four hold: (1) every `ready` and `ready-bar` recipe in B has a score line on F; (2) every C variant of those recipes has a score line or a listed merge; (3) every `pending` trigger has a FINDINGS row (measured, and a trust verdict); (4) every `blocked` object (CVD, SMT, absorption B, bigtrade q90) has either a rebuilt definition with a new FINDINGS row or a `not-measurable` row. Until then, no discovery row is run.

### D3. Discovery queue (sourced, deferred, in this order)

1. Rebuilds: CVD divergence as an event (five constructions, divergence at box edges within the grid window) `[VWAP p.6]` `wiki/cvd-variants.md`; SMT as prior-H/L-taken-on-one-index-not-another, multi-scale, at S1 ∪ AMT objects `[CEX L78]` `[C1 p.5]`; absorption B with a tighter reload rule; BigTrades on the tape's own size distribution (per-ticker thresholds) `[FIND p.10]` `[JJX L220]`; MVFL zones on aggressor delta `[CEX L16]`.
2. Two-slot swaps, only on recipes whose one-slot variants printed `better`.
3. Derived ranges: starts on a 15-minute grid inside the NY (end 09:30) and London (end 03:00) families, regularized toward 06:00 / 03:00 `[JJX L177–199]` (tier 4); Jumbo's "any 5–9 window" `[XF p.7]` is the null.
4. Learned P-zones (Phase 3) `wiki/p-zones-benchmark.md`; P-zone as "several generators agree" `[JJX L231]` (tier 4).
5. Cross-asset zone mapping (beta-adjusted, residual-width zones) and basket non-confirmation `[CEX L290–295]` (tier 4); native + mapped node disagreement stays a Phase 1 column.
6. Gamma density, vanna / charm, 0DTE share, implied-hedging-flow tests `[CEX L109–111, L145–148]` (tier 4); `[GEX p.17]` is the only tier-2 source for vanna / charm.
7. Exit-hazard model and regime clustering `[CEX L116, L125]` (tier 4); session picker `[CEX L93]` (tier 4) — the rolling clean-session label (OF-J9) is the Phase 1 stand-in.
8. Dealer positioning inference from next-day OI as a retrospective calibration label `[DRFL L279, L318, L815]`.
9. Skylit / KG1 / GEXRADAR reproductions: not before 1–8; disclosed substitutes only.

### D4. Stop

This file is complete when every slot value above has a source, every recipe has its author's five slots and a status, every recipe has a bounded one-slot swap list, and the discovery queue holds every tier-4 idea and every unmeasured tape flag. Nothing here starts a run; `PHASE.md` remains the stop for measurement.
