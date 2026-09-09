# Source mechanisms → Phase 1 objects

One row per mechanism found in the sources. Citation → computable definition → outcome → family → faithful object → named upgrades → verdict. Verdicts: **measure** (Phase 1 computes it), **experiment** (comparison row against a faithful object), **defer** (Phase 2 context / Phase 3 location), **not-measurable** (data does not exist; printed as such). Full definitions live in the wiki page named in each row.

| # | mechanism | citation | computable definition | outcome | family | faithful object | named upgrades | verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | 6–9 overnight box with EQ, quadrants, open/close | TBR p.4–5, p.7–8; PINE 6 to 9 Session and Levels | H/L/O/C of 06:00–09:00, internals | first-touch, grid at each level, path class | RANGE | `range.6-9.published` | trade-level H/L; vol-elapsed and dollar bars | measure |
| 2 | −0.5 mean-reversal projection and reversal-at-projection stat | TBR p.5, p.8, p.12, p.30 | level beyond edge at 0.5·R; reject in 09:00–12:00 | recompute 86.46% and depth table on F and L | RANGE | `env.ext.050` | depth 0.1/0.2/0.3/0.5 rows | measure |
| 3 | Judas → 09:40–09:50 reversal window | TBR p.8; XF p.29, p.47 | sweep of an edge then close back through EQ; reversal-time bins | bin shares, 09:40–09:50 vs first 20 min | RANGE / FAIL | `judas.depth.any` | `judas.depth.-0.5`; bins | measure |
| 4 | Single-break scenarios (extended overnight; purged / compressed) | TBR p.12, p.24; DTM L44–49 (restating) | class by `w.rel-prior-rth` and Asia/London purge flags | class shares, mid-retrace, 1.33/1.66 reach | PATH | `path.6-9.published` labels | threshold variants 0.5 / 1.0 | measure |
| 5 | Range-size break classification table | XF p.24 (8 Jun 2026); XF p.23 | width buckets × {double, single high, single low, none} | recompute table, cell differences | PATH | his table | `w.pct.0859close` vs `w.pct.0930open`; window 10:30 / 12:00 / 16:00 | measure |
| 6 | Mid retrace ≈ 60.4% after a break | XF p.23 | break then touch of EQ within window | rate | PATH | `path.midretrace` | grid variants | measure |
| 7 | Small-range double-break % is skew, not edge | XF p.7; PACK L50 | same table, bucket 0–0.3 vs others | reported with n | PATH | — | — | measure (label) |
| 8 | "Any 5–9 window behaves like 6–9" | XF p.7; PACK L49 | grid rows 5–9, 7–9, 8–9 | faithful disagreements vs 6–9 | RANGE | `range.6-9.published` | `range.5-9`, `range.7-9`, `range.8-9` | experiment |
| 9 | Open-location switch (value / range / 6–9) and double-break expectancy split | XF p.8, p.11, p.16; PACK L38–44 | 27 cells at 09:30; double-break rate in-value vs in-range | recompute p.11 rows; per-cell class shares | OPEN | `open.switch.published` | VP source and VA % variants; RVOL flag | measure |
| 10 | ~76% one-way A-period when open outside both with RVOL | PACK L40 | open outside value and range, RVOL ≥ 1.5; no return to OR low by 10:00 | rate | OPEN | `open.oneway.A` | RVOL 1.0 / 1.5 | experiment |
| 11 | Balance vs imbalance of the overnight | FIND p.6; JJX L56 | box body / range and overnight VP shape | label shares by class | PATH | `balance.body-ratio` | `balance.vp-shape` | measure (label) |
| 12 | Clean edge / sister-index hunts | FIND p.3–4; CEX L105 | edges untouched by Asia/London; SMT events | label shares | PATH / FLOW | `edge.clean`, `flow.smt.ohlc.4` | `flow.smt.trade.nq`, level sets S1–S3 | measure |
| 13 | London TBR (box into 03:00) and London 1.33/1.66 | TBR p.7; FIND p.4–5; JJX L53; PACK L82 | 00:00–03:00 box, outcomes 03:00–06:00 | same as 6–9 | RANGE | `range.london.00-03` | `range.london.0300-0330` | experiment |
| 14 | Asia opening range 20:00–20:30; GB Asia 20:00–00:00 | TBR p.7; GB L35–38 | boxes | same as 6–9 | RANGE / FAIL | `range.asia.2000-2030`, `range.gb.asia` | — | experiment |
| 15 | EV range (AM expected move) | XF p.7; PACK L22–28 | band = ref ± estimator | reach, overshoot, reject, time-to-touch, in/out of value | ENV | `env.ev.mean60` | median / p75 / p90 / rv / gk / yz / har / iv / vix16; ref variants | measure |
| 16 | SessionStat 9–12 average / median H/L | SS p.3, p.6, p.9–11; FIND p.5; XF p.47 | 09:00 open ± mean or median excursion, 60 sessions | same as EV; coincidence with exhaustion levels | ENV | `env.ss.avgHL60` | `medHL60`, `minavg60`, lookbacks, weekday | measure |
| 17 | Extensions 1.33 / 1.66 | TBR p.21; PACK L66, L82 | edge ± k·R | touch by 12:00 / 16:00; grid; PM fork | ENV | `env.ext.133.from-edge`, `env.ext.166.from-edge` | from EQ; London box | measure |
| 18 | P-zones (unpublished) | PACK L81; FIND p.2, p.6; XF p.8, p.16 | time-anchored excursion quantile boxes | grid at box edges; closest-object ranking | ENV | `pz.approx.A` | `pz.approx.B`; quantiles; anchors; learned model | measure (approx) / defer (learned, Phase 3) |
| 19 | OR 5m / 15m mid as reference | XF p.14–15, p.25; PINE ORB files | 09:30–09:35 / 09:45 box mid | mid-retrace rate | RANGE | `range.or.5m`, `range.or.15m` | — | experiment (reference row) |
| 20 | IB stats "never sustainable edge" | XF p.8; PINE IB files | 09:30–10:30 box | recompute break tables | RANGE | `range.ib` | — | experiment (expected null) |
| 21 | Sessions correlation AM / Lunch / PM | TBR p.36 | direction of AM vs PM | sign agreement rates | PATH | `corr.am-pm` | — | experiment |
| 22 | 3-strike failure, extended bodies at projections | TBR p.37 | third touch without reject; body beyond level | rates | grid | `grid.jumbo.projection-reject` | — | measure (grid cells) |
| 23 | RTH-scoped VP, prior-day value, POC magnet | AMT1 p.4–5; RTVP p.4–5; MAMT p.4–7; C3 p.7 | 09:30–16:00 profile, 70% VA | grid at VAH / VAL / POC; open cells | VALUE | `value.vp.rth.trade` | `ohlc1m`; VA 68 / 40; TPO variant | measure |
| 24 | Delta profile beside VP (absorption at mid, taper at lows) | XF p.23; JJX L52; TRAP p.4 | per-price aggressor delta | extremes, taper flag | VALUE | `value.delta.rth.trade` | bin sizes | measure |
| 25 | Key zones: HVN / LVN / shelves / ledges; signature coin-flip at POC | ABS p.2, p.6–7; RD p.9 | profile extrema thresholds | reject rate at extreme vs POC | VALUE | `value.kz` | thresholds | measure |
| 26 | Absorption (effort, wall, no reward, confirmation; must refill) | ABS p.8–9; MATH p.8; STOP p.2–3 | `flow.absorption.A` (effort / no-reward) | reward rate; grid at event | FLOW | `flow.absorption.A` | `flow.absorption.B` (BBO reload); windows; location | measure |
| 27 | Refill / replenishment beyond the touch, icebergs, hidden book | REF p.5, p.10; JJX L157–159 | needs depth beyond BBO | — | FLOW | — | — | not-measurable (MBP-1 only) |
| 28 | BigTrades 100 NY / 75 London; footprint top 35%; "not absorption" | XF p.23, p.25; BIG p.3–6 | single prints ≥ threshold by side | counts, overlap with absorption events | FLOW | `flow.bigtrade.100ny/75ldn` | 30–60 Ethos; q99 | measure |
| 29 | CVD variants incl. participant-separated and gamma CVD | STOP p.3; VWAP p.5; DTM L23 | five named constructions | divergence flags, variant agreement | FLOW | `flow.cvd.trade` | `ohlc`, `part.trade`, `part.ohlc`, `gamma` | measure |
| 30 | SMT divergence, multi-scale, hypothesis not snapshot | FIND p.3; DTM L24; CEX L105 | `hunted(i, level)` across NQ / ES / YM / RTY | event counts, class conditional | FLOW | `flow.smt.ohlc.4` | `flow.smt.trade.nq`; lag; pairs | measure |
| 31 | Vol estimators GK / YZ / RV / HAR / IV / skew / VX | DTM L23; JJX L147; VIX4 p.4; INV L315, L566 | daily features, terciles on F | regime columns; EV calibration | VOL | `vol.gk20` etc. | windows | measure (features) |
| 32 | Options nodes (OI / gamma strikes) as levels; dealer identity | GEX p.2–5; DRFL L207–252; INV L297–380 | top-3 OI strikes → NQ coordinates | grid at nodes | VALUE | `value.node.oi.top3` | gamma-weighted; dte; QQQ | measure / not-measurable (dealer inventory, hidden book) |
| 33 | Skylit Heatseeker / Flowseeker / Atlas engines | README L27–30; DTM L27 | — | — | — | — | — | defer (Phase 2–3) |
| 34 | GB NYAM 09:00–10:00 failed breakout / breakdown, outcomes after 10:00 | GB L28–30, L86–89, L178 | `fail.gb.nyam.c5` | agreement vs Jumbo labels; post-event grid | FAIL | `fail.gb.nyam.gb.c5` | `b.c1`; depth | measure |
| 35 | GB previous-hour and 10–11 boxes | GB L32–33, L49, L79 | `fail.gb.hour`, `fail.gb.10-11` | same | FAIL | as named | — | measure |
| 36 | GB Asia / London H/L (inferred clocks) | GB L35–38, L48, L53–54 | boxes 20:00–00:00, 02:00–05:00 | same | FAIL | `fail.gb.asia`, `fail.gb.london` | Jumbo London row separate | measure |
| 37 | TDO 00:00 print + 5-minute close-back | GB L24–26; PINE hourly_stats_levels | level; `grid.gb.c5` | touch rate; fail-back rate | FAIL | `lvl.tdo` | — | measure |
| 38 | NWOG (Friday settle vs Sunday 18:00) as destination | GB L59–60, L68–69; PINE Sessions & VP (weekly open) | two lines; fill by 12:00 / 16:00 Monday | fill rates; reach after fail events | FAIL | `lvl.nwog` | — | measure |
| 39 | 9:30 cash-open sweep / reclaim | GB L56–57, L90 | `fail.0930open` | same as 34 | FAIL | `lvl.0930open` | — | measure |
| 40 | Golden pocket 50–61.8% of completed impulse | GB L73–76 | location band on the last impulse | flag on events | FAIL | `loc.gp` | — | measure (label only) |
| 41 | A+ = sweep happened | GB L93 | depth ≥ d | label counts | FAIL | `label.aplus` | d variants | measure (label only) |
| 42 | GB items not added: partials, fleet ops, DLL psychology, SMT-as-edge, 7:30 open, "above TDO = short", wickless bottom, CPI boxes | GB L50–51, L95, L158, L177; BRIEF | — | — | — | — | — | out |
| 43 | Hourly sweep / hourly open-mid hit tables, magic hours, 4H HOD/LOD, floor pivots, ORB / IB tables, engulfment tables | PINE (see wiki/sources-pine-archive) | recompute with the same buckets | cell differences | various | — | — | experiment |
| 44 | Range width table (6–9 H−L and prior RTH H−L) | BRIEF; XF p.24 | `w.pts`, `w.pct`, `w.rel-prior-rth` | bucket tables | PATH | — | — | measure |
| 45 | Locked account / risk targets ($2,000 avg net, $1,000 cap, one account, one NQ mini) | BRIEF; DTM L248 (assistant) | — | — | — | — | — | out (not a Phase 1 deliverable) |
