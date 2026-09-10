# QUESTIONS_RESOLVED — closed variant grids

Nothing here blocks Phase 1. Each item is closed by a named default; alternatives stay as variants. Unpublished formulas are disclosed approximations, not user-decoding tasks.

## Closed by default (override = edit the named wiki page)

1. **Frozen slice F** = 2024-01-02 → 2026-08-31; long slice L = 2010-09-07 → 2026-08-31 (1-minute bars only, recompute rows). `wiki/data-coverage.md`.
2. **Break default** = 1-minute close beyond the edge (`b.c1`); wick and 5-minute variants always reported. `wiki/touch-reject-hold-break-grid.md`.
3. **Width tables.** `W69` and `WpriorRTH` stored in points. XF p.24 uses `w.pct.0859close` (default) and `w.pct.0930open`. Ratio bins of `W69/WpriorRTH` are a different table and are not relabeled as the source price-% claims. `wiki/tbr-6-9-range.md`.
4. **Day-type thresholds.** Extended = `w.rel-prior-rth ≥ 1.0`; compressed = `≤ 0.5`; purged = Asia or London H/L taken before 09:30. Judas = first break then return through EQ. Classes are flags plus an exclusive label; unmatched stays unmatched. `wiki/range-path-class.md`.
5. **London TBR.** Jumbo rows: `range.london.00-03` (box into 03:00) and `range.london.0300-0330` (TBR p.7 opening range). GB-London inferred 02:00–05:00 is a different id. `wiki/clock-grid-and-bars.md`.
6. **Green Bird inferred clocks.** Asia 20:00–00:00, London 02:00–05:00, tagged INFERRED unless a screenshot names another clock. `wiki/session-fail-boxes.md`.
7. **EV range.** Benchmark `env.ev.mean60` at `ref.0930open`; also print `ref.0900open`, `ref.eq69`, `ref.0900close`, `ref.tdo`. Estimator grid as on the EV page. Midpoint of EV ≠ 6–9 EQ. `wiki/ev-range-expected-move.md`.
8. **SessionStat minimum-average.** Manual does not print the formula → approximation = average of the lower half of excursions, named `env.ss.minavg60`. `wiki/sessionstat-9-12-envelope.md`.
9. **P-zone benchmark.** Formula unavailable. `pz.approx.A` = last 500 completed matching-horizon sessions, nearest-rank 50/75/90/95/99 excursion bands from the clock anchor (T1–T4 = approximation tiers). Upgrades: history-60, vol-scaled, volume-filter, VP-node-snap, `pz.approx.B`. Learned model deferred to Phase 3. `wiki/p-zones-benchmark.md`.
10. **Extension coordinates.** Faithful = beyond-edge `H+kW` / `L−kW`. Named upgrade = range-origin `L+kW` / `H−kW`. Width from 6–9 (or London box). Not P-zones, not ATL. `wiki/extensions-1-33-1-66.md`.
11. **Open-location cells.** 27 (value × range × 6–9). Prior value from trade-level VP at 70% by default; OHLC-VP and 68 / 40 % as rows. `wiki/open-location-switch.md`.
12. **76% one-way claim.** Two rows, not one: A-period 09:30–10:00 one-way, and return to a frozen 5m/15m OR edge after that OR’s known_at. RVOL ≥ 1.0 and ≥ 1.5 named. Neither percentage is a pass target. `wiki/open-location-switch.md`.
13. **A+.** Sweep observed = true; no sweep = false; insufficient coverage = unknown. Depth `d` is a separate upgrade. Not a full grade. `wiki/session-fail-boxes.md`.
14. **TDO.** First print of the 00:00 ET minute. Confirmation = 5-minute close back through it after a sweep. Minute-bar-open substitute is tagged INFERRED. `wiki/session-fail-boxes.md`.
15. **NWOG.** Friday **settlement** vs Sunday 18:00 ET Globex open. File also says Friday close; store both endpoints. Destination, not entry. `wiki/session-fail-boxes.md`.
16. **Golden pocket.** 50.0–61.8% of the completed impulse (HIS WORDS). NYAM-height and 6–9-height are named location variants. Location only. `wiki/session-fail-boxes.md`.
17. **Participant proxies for CVD.** Size buckets ≥ 100 / 20–99 / < 20 (100 = Jumbo NY BigTrades). `wiki/cvd-variants.md`.
18. **Gamma CVD weights.** Sign of net dealer gamma at the nearest strike node, ±1, declared in the report; no fitting. `wiki/cvd-variants.md`.
19. **Absorption A / B constants.** q90 aggressive volume in 2 minutes, ≤ 2 ticks advance, ≥ 0.25·R reversal in 15 min; BBO reload ≥ 50% within 500 ms, ≥ 2 repeats. `wiki/absorption-and-big-trades.md`.
20. **Footprint.** Diagonal ask(p)/bid(p−tick) 4× (3× named), stacked run ≥ 3 (2 named). Same-price 350% is a different row. Not absorption, not BigTrades. `wiki/absorption-and-big-trades.md`.
21. **Key-zone thresholds.** HVN ≥ 1.5× median bin; LVN ≤ 0.5×; two-sided LVN named; ledge = 3× step between 4-tick blocks. `wiki/value-and-profiles.md`.
22. **Options nodes.** Native products NDX, NDXP, SPX, SPXW. Variants QQQ, SPY, NQ.OPT. Fields: native, mapped_nq, map_known_at, OI_vintage. Map default = prior-session median price ratio. Cash NDX/SPX minutes are not inputs. `wiki/options-nodes.md`.
23. **SMT.** Faithful continuous object = `flow.smt.ohlc.4`. Trade-level NQ = `flow.smt.trade.nq`. Pine 3/3 matcher = `flow.smt.pine.3-3`. Not a GB edge. `wiki/smt-divergence.md`.
24. **FVG / CISD / TPO.** Measured as their own families (ticket 08). Not added to GB pages. IB stays a clock-grid comparison row. `wiki/fvg-body-gaps.md`, `wiki/sweep-cisd-blocks.md`, `wiki/tpo-ib-auction.md`.
25. **Coverage rule.** Drop a session from a family when a needed window misses > 10% of expected 1-second bars. `wiki/data-coverage.md`.
26. **Report location.** `implementation/reports/phase1-live/`. `SPEC.md` §6.
27. **Resource budget.** Runs stay inside the current E0 envelope by chunking per month; a larger budget goes through the existing budget-amendment path. `SPEC.md` §8.

## Not measurable with the data we hold (printed as rows, never estimated)
- Off-touch refill, icebergs, hidden book (needs MBP-10 / MBO; locked out) — `flow.refill.offtouch`, `value.hidden.book`.
- Dealer inventory and participant identity — `value.dealer.inventory`.
- Skylit Heatseeker / Flowseeker / Atlas node engines — `value.skylit.*` (Phase 2–3).
- ES trade-level objects inside F (ES MBP-1 ends 2024-08-30) — `flow.smt.trade.es`.
- Jumbo's actual P-zone formula and his EV estimator — disclosed approximations only.
- Sample provenance of Pine hardcoded tables — recomputed, never trusted.
- Cash NDX/SPX minute bars — not in inventory; do not invent them.

## Explicitly not Green Bird (do not add to ticket 07)
FVG, CISD-as-GB, SMT-as-GB, 7:30 NY true open, “above TDO = short”, 25-point partials, fleet/DLL, wickless-bottom as a model, CPI boxes as a family.
