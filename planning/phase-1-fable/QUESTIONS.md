# QUESTIONS — closed variant grids and not-measurable rows

Nothing here blocks Phase 1. Each item was closed by a named default with the alternatives kept as variants; the user may override any default by editing the wiki page named. No decoding of unpublished formulas is requested.

## Closed by default (override optional)
1. **Frozen slice F** = 2024-01-02 → 2026-08-31; long slice L = 2010-09-07 → 2026-08-31 (1-minute bars only, recompute rows). Page: `wiki/data-coverage.md`.
2. **Break default** = 1-minute close beyond the edge (`b.c1`); wick and 5-minute variants always reported. Page: `wiki/touch-reject-hold-break-grid.md`.
3. **Width % basis** for the XF p.24 recompute: unpublished → `w.pct.0859close` (default) and `w.pct.0930open` both printed. Page: `wiki/range-path-class.md`.
4. **Day-type thresholds**: extended = `w.rel-prior-rth ≥ 1.0`, compressed = `≤ 0.5`, purged = Asia or London H/L taken before 09:30. Page: `wiki/range-path-class.md`.
5. **London TBR window**: `range.london.00-03` (box into 03:00, outcomes 03:00–06:00) as the Jumbo row; `range.london.0300-0330` (TBR p.7 opening range) as a second row. Page: `wiki/clock-grid-and-bars.md`.
6. **Green Bird inferred clocks**: Asia 20:00–00:00, London 02:00–05:00, tagged INFERRED; Jumbo London stays a separate row. Page: `wiki/session-fail-boxes.md`.
7. **EV range reference price**: `ref.0930open` default; `ref.eq69`, `ref.0900close`, `ref.tdo` as rows; estimator benchmark `env.ev.mean60`. Page: `wiki/ev-range-expected-move.md`.
8. **SessionStat minimum-average rule**: manual does not print the formula → approximation = average of the lower half of excursions, named `env.ss.minavg60`. Page: `wiki/sessionstat-9-12-envelope.md`.
9. **P-zone benchmark**: `pz.approx.A` (time-anchored excursion quantile boxes, 09:30 and 10:00 anchors, q25–q75 / q75–q90) and `pz.approx.B` (0.5·R and 1.0·R bands). Learned model deferred to Phase 3. Page: `wiki/p-zones-benchmark.md`.
10. **Participant proxies for CVD**: size buckets ≥ 100 / 20–99 / < 20 (100 = Jumbo's NY BigTrades threshold). Page: `wiki/cvd-variants.md`.
11. **Gamma CVD weights**: sign of net dealer gamma at the nearest strike node, ±1, declared in the report; no fitting. Page: `wiki/cvd-variants.md`.
12. **Open-location cells**: 27 (value × range × 6–9); prior value from trade-level VP at 70% by default; OHLC-VP and 68 / 40 % as rows. Page: `wiki/open-location-switch.md`.
13. **"76% one-way A-period" recompute**: one-way = no return to the 09:30–09:35 OR low (long case) / high by 10:00 after opening outside both prior value and prior range with RVOL ≥ 1.5. Page: `wiki/open-location-switch.md`.
14. **Absorption A / B constants**: q90 aggressive volume in 2 minutes, ≤ 2 ticks advance, ≥ 0.25·R reversal in 15 min; BBO reload ≥ 50% within 500 ms, ≥ 2 repeats. Page: `wiki/absorption-and-big-trades.md`.
15. **Key-zone thresholds**: HVN ≥ 1.5× median bin, LVN ≤ 0.5×, ledge = 3× step between 4-tick blocks. Page: `wiki/value-and-profiles.md`.
16. **Options nodes**: NDX + NDXP dte ≤ 14 chains, top 3 OI strikes per side at 09:25, mapped by NQ / NDX ratio. Page: `wiki/options-nodes.md`.
17. **Report location**: `trading-research/reports/phase1-fable/` (separate from any other tree's reports). Page: `SPEC.md` §6.
18. **Resource budget**: runs stay inside the current E0 envelope by chunking per month; a larger budget, if needed, goes through the existing budget-amendment path with a retained request. Page: `SPEC.md` §8.
19. **Coverage rule**: drop a session from a family when a needed window misses > 10% of expected 1-second bars. Page: `wiki/data-coverage.md`.
20. **Ambiguous "GB-10-11"**: read as the 10:00–11:00 hour box after the NYAM box (`[GB L49, L79]`). Page: `wiki/clock-grid-and-bars.md`.

## Not measurable with the data we hold (printed as rows, never estimated)
- Off-touch refill, icebergs, hidden book (needs MBP-10 / MBO; locked out) — `flow.refill.offtouch`, `value.hidden.book`.
- Dealer inventory and participant identity — `value.dealer.inventory`.
- Skylit Heatseeker / Flowseeker / Atlas node engines — `value.skylit.*` (Phase 2–3).
- ES trade-level objects inside F (ES MBP-1 ends 2024-08-30) — `flow.smt.trade.es`.
- Jumbo's actual P-zone formula and his EV estimator — benchmarked by disclosed approximations only.
- Sample provenance of Pine hardcoded tables — recomputed, never trusted.
