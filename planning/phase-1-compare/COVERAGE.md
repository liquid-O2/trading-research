# Phase 1 coverage audit

Trees compared (read-only):

- **A** = `planning/phase-1-from-scratch/`
- **B** = `planning/phase-1-fable/`

Sources used: A/B wiki pages that claim each object; packs under `planning/phase-1-fable/references/`; raw evidence under `sources/documents/`. Archive plans are not authority. Chat transcript is not a source.

Quality rule: a page counts only if it has a definition, a citation (PDF page / tweet ID / pack line), a faithful object, named upgrades, and outcomes. File count is not quality. If B omitted a sourced object that A still has, that is a miss. If A has a page with no citation and no distinct outcome, that is bloat.

Verdict tokens: `Present-A` / `Present-B` / `Missing-both` / `Bloat-only-A`. `thin` means the claiming page lacks a citation or an upgrade grid, or collapses a sourced object into a one-line mention.

---

## Checklist

| object | A path | B path | verdict | info lost if we keep only B |
|---|---|---|---|---|
| 6–9 box, internals, width table on 6–9 **and** prior RTH | `wiki/time-based-ranges.md`, `wiki/range-break-paths.md`, SPEC Q02 | `wiki/tbr-6-9-range.md`, `wiki/range-path-class.md` | Present-A, Present-B | Minor. B has internals (EQ, Q25/Q75, O/C, −0.5, 1.0, 1.33/1.66), XF p.24 % bins, and `w.rel-prior-rth`. A’s lock that ratio bins must not be relabeled as the source’s price-% claims is clearer; B can mix the two widths if implementers are careless. |
| Path class high-only / low-only / both / neither + break order | `wiki/range-break-paths.md` | `wiki/range-path-class.md` | Present-A, Present-B | Tweet IDs on XF p.24 (`2064008375751311653`). B cites XF p.24 + PACK lines and has the same table. Order-unknown on OHLC is stronger in A. |
| Judas / extended single-break / purged single-break | `wiki/jumbo-day-classes.md` | `wiki/range-path-class.md` (same page as path class) | Present-A, Present-B | A’s dedicated page keeps class evidence as separate booleans before an exclusive label. B names the three classes with thresholds (`w.rel-prior-rth`, Asia/London already taken). Not a miss. |
| Open vs prior value **and** vs prior range **and** vs 6–9 (switch) | `wiki/jumbo-day-classes.md#2026-open-location-switch`, `wiki/session-geometry.md` | `wiki/open-location-switch.md` | Present-A, Present-B | B’s 27-cell object is the better operational page. A’s tweet IDs (10 Jul, 28 Jul, 9 Jul) are more precise than PACK-only lines. |
| In-value vs in-range double-break expectancy | `wiki/range-break-paths.md`, `wiki/jumbo-day-classes.md` | `wiki/open-location-switch.md` | Present-A, Present-B | **Partial miss on the 76% claim.** A splits A-period 09:30–10:00 one-way from later return to a frozen 5m/15m OR edge. B QUESTIONS #13 collapses those into one `open.oneway.A` definition. |
| EV range own envelope + estimator grid (not SessionStat, not P-zone) | `wiki/ev-range-expected-move.md` | `wiki/ev-range-expected-move.md` | Present-A, Present-B | **None; B is stronger.** Own page, own estimator grid (mean/median/p75/p90, RV/GK/YZ/HAR/IV/VIX16), own midpoint ID. A’s default 09:00 anchor vs B’s `ref.0930open` is a closed variant, not a miss. |
| SessionStat 9–12 as a comparison row | `wiki/sessionstat-envelopes.md` | `wiki/sessionstat-9-12-envelope.md` | Present-A, Present-B | A keeps 23:59 overnight workaround and same-day timestamp limits from SS p.7–12. B already cites choppy/low-vol failure (SS p.11). Small. |
| 1.33 / 1.66 from the 6–9 (and London box) | `wiki/extension-projections.md` | `wiki/extensions-1-33-1-66.md` | Present-A, Present-B | **Coordinate convention.** A records two sourced geometries: beyond-edge (`H+kW` / `L−kW`) vs range-origin (`L+kW` / `H−kW` from MTF OHLC Lines). B only has from-edge vs from-EQ. London box row exists in B. |
| P-zone disclosed approximation + upgrades (formula unavailable) | `wiki/jumbo-p-zones.md` | `wiki/p-zones-benchmark.md` | Present-A, Present-B | **Upgrade grid thinner in B.** Screenshot UI is 500-session, T1–T4, vol/volume filters, invalidation (`xfcmg2` pp.34–39). A names those upgrades. B’s `pz.approx.A` is 60-session q25/q75 boxes. Formula still unavailable in both. |
| 5–9 clock family; 9:40–9:50 vs first 20 min vs volume-elapsed vs dollar/trade bars | `wiki/time-based-ranges.md` | `wiki/clock-grid-and-bars.md` | Present-A, Present-B | **None; B is stronger.** Fixed grid, GB clocks, reversal-time bins, bar types, merge-if-indistinguishable. A’s 15-minute neighbor search is an extra experiment, not a missing object. |
| Jumbo London TBR (separate from GB London) | `wiki/time-based-ranges.md` (Q03 left open) | `wiki/clock-grid-and-bars.md` `range.london.00-03` + `range.london.0300-0330`; `wiki/session-fail-boxes.md` `box.jumbo.london` | Present-A, Present-B | **None; B is stronger.** A left the London formation interval unresolved. B closed two Jumbo London rows and kept GB-London inferred 02:00–05:00 separate. |
| BigTrades 100 NY / 75 London ≠ absorption | `wiki/big-print-zones.md`, `wiki/absorption-stages.md` | `wiki/absorption-and-big-trades.md` | Present-A, Present-B | Ethos 30–60 on a 40-range chart is in both. A’s size-normalized / cluster / 100ms-aggregate variants are richer. B states the “bubbles are not absorption” check as an overlap table. Not a miss. |
| RTH VP / value / delta / key zones / absorption | `wiki/value-profiles.md`, `wiki/delta-profiles.md`, `wiki/nodes-shelves-ledges.md`, `wiki/absorption-stages.md` | `wiki/value-and-profiles.md`, `wiki/absorption-and-big-trades.md` | Present-A, Present-B | **Stage sequence and two-sided LVN.** A’s absorption stages (aggression → replenishment → fade → opposite reward) and two-sided LVN / naked POC are sourced. B has A/B absorption proxies and HVN/LVN/ledge thresholds. Distinct objects still present. |
| GB 9:00–10:00 after 10:00 | `wiki/session-fail-boxes.md` | `wiki/session-fail-boxes.md`, `wiki/clock-grid-and-bars.md` | Present-A, Present-B | None. Both tag HIS WORDS and forbid 09:45 events. |
| GB 10:00–11:00 | `wiki/session-fail-boxes.md` | same | Present-A, Present-B | None. Both: HIS CHART / “9–11 best time” as the hour after NYAM. |
| Last completed 60m | `wiki/session-fail-boxes.md` | same | Present-A, Present-B | Cadence: A leaves sampling in SPEC; B steps every 5 minutes 09:30–12:00. A named upgrade, not a miss. |
| Asia ~20:00–00:00 (inferred) | `wiki/session-fail-boxes.md` | same | Present-A, Present-B | None. Both INFERRED, HIS CHART pink box. |
| London H/L (inferred 02:00–05:00 unless a screenshot says otherwise) | `wiki/session-fail-boxes.md` | same | Present-A, Present-B | None. Both: levels HIS CHART, clock INFERRED, not Jumbo London TBR. |
| TDO 00:00 + 5m close-back | `wiki/session-fail-boxes.md` | same | Present-A, Present-B | None. |
| NWOG Friday settle vs Sunday 18:00 | `wiki/session-fail-boxes.md` | same | Present-A, Present-B | Pack file says Friday close; both lock settlement as the endpoint and store both. Destination not entry. |
| 9:30 cash-open sweep/reclaim | `wiki/session-fail-boxes.md` | same | Present-A, Present-B | None. Separate from unfinished 9–10 box. |
| Sweep + fail-back inside | `wiki/session-fail-boxes.md` | same | Present-A, Present-B | A’s hold-outside variants (`hold-outside-print` / `close5`) are more explicit. B has fail-back on the shared grid. Small. |
| Golden pocket 50–61.8 of the completed impulse | `wiki/session-fail-boxes.md` | same | Present-A, Present-B | A’s extrema-order / NYAM-height / 6–9-height variants are more explicit. B emits `loc.gp` as location only. Not a miss. |
| A+ = sweep happened | `wiki/session-fail-boxes.md` | `wiki/session-fail-boxes.md` | Present-A, Present-B (thin-B on the faithful line) | **Drift.** Definition in B says A+ = a sweep happened `[GB L93]`. Faithful object then sets `label.aplus` = sweep depth ≥ `d`. A keeps sweep-only, no grade, no depth gate. |
| FVG / body gaps | `wiki/fvg-body-gap-structures.md` | pine mention only (`wiki/sources-pine-archive.md`, grid candidates) | Present-A | **Miss.** TBR pp.32–35 first-presented FVG / H1/M15 imbalances; Pine first-presented FVG and body-gap “volume imbalance” (no volume). Not inside B ticket 07 as an object. |
| Sweep / CISD / blocks | `wiki/sweep-cisd-blocks.md` | confirmation variants on `wiki/touch-reject-hold-break-grid.md` and pine citations | Present-A, Present-B (thin-B) | **Candle-block / CISD object miss.** TBR pp.25–29 three-candle sweep + rejection blocks; Open Source Fractal CISD. B uses HTF wick/close-back as grid cells, not as a family with formation/invalidation. GB sweep+fail-back is a different object and is present. |
| TPO / IB / auction day labels | `wiki/tpo-structures.md`, `wiki/opening-range-and-ib.md`, `wiki/auction-day-open-types.md` | IB as `range.ib` / `range.or.*` comparison rows; `value.tpo` named in B SPEC only, no wiki definition; no AMT day labels | Present-A, Present-B (thin-B on IB only) | **TPO and AMT labels miss.** tpo-lesson-3.pdf (30m letters, single prints, excess, poor extremes). amt-lesson-1.pdf (trend / normal / normal-variation / neutral / non-trend; drive / test-drive / rejection-reverse / auction). Jumbo 2026 demotes OR/IB as the main box; that demotion is correct and already in B. |
| Footprint imbalance / large prints | `wiki/footprint-imbalances.md`, `wiki/big-print-zones.md` | `wiki/absorption-and-big-trades.md` (BigTrades + Jumbo “top 35% of transactions”) | Present-A, Present-B (thin-B on footprint) | **Diagonal footprint is not the same object as absorption or BigTrades.** fp-lesson-8.pdf: ask(p)/bid(p−tick) 3–4×, stacked ≥2–3 rows. B covers large prints correctly and separates them from absorption. Footprint diagonal/same-price imbalance is the miss. |
| Not-GB: FVG, CISD, SMT-as-GB, 7:30 NY true open, “above TDO = short”, 25-pt partials, fleet/DLL | A keeps FVG/CISD as non-GB families; does not force the rest onto GB pages | `wiki/session-fail-boxes.md` “Not added” list | Present-A, Present-B | None on the exclusion. B is explicit. A still measures FVG/CISD as Jumbo/Pine objects (see rows above). |
| NDX + NDXP native nodes | `wiki/options-chain-availability.md`, `wiki/options-exposure-nodes.md` | `wiki/options-nodes.md` faithful = NDX+NDXP only | Present-A, Present-B | Faithful row exists in B. Native vs mapped fields are not a table. |
| SPX + SPXW native nodes | `wiki/options-chain-availability.md`, `wiki/options-exposure-nodes.md`, screenshot `reference-images/zerano-charts-SPX-…webp` | mentioned in B definition/citations; **no faithful or upgrade row** | Present-A | **Miss.** SPX screenshot is native SPX nodes. Inventory has Theta SPX/SPXW contracts, EOD, OI, quote-1m. B must not collapse this to QQQ/SPY or to NDX-only. |
| QQQ, SPY, NQ.OPT as named variants | A: GEX QQQ-for-NQ / SPY-for-ES; inventory QQQ/SPY 1m; NQ.OPT CME | B upgrades: NQ.OPT-only, QQQ-derived; **SPY absent** | Present-A, Present-B (thin-B) | SPY variant missing. QQQ and NQ.OPT exist as upgrades, not first-class product rows. |
| Each row: product \| native \| mapped_nq \| map_known_at \| OI_vintage | `wiki/cross-market-price-mapping.md`, `wiki/options-chain-availability.md` | no table | Present-A | **Miss.** Mapping known-at and OI vintage are not fields in B. |
| Cash NDX/SPX minutes are not assumed | `wiki/inventory-and-availability.md`, `wiki/cross-market-price-mapping.md` (NDX/SPX cash **daily**; QQQ/SPY **1m**) | `wiki/data-coverage.md` lists QQQ/SPY 1m and Theta option quotes; does not state the cash-index minute prohibition | Present-A, Present-B (thin-B) | Implementers can invent NDX/SPX cash minutes. Inventory does not have them. |
| Five CVD constructions | `wiki/cvd-constructions.md` | `wiki/cvd-variants.md` | Present-A, Present-B | None on the five names (trade, OHLC, part-trade, part-OHLC, gamma). A’s size-bucket / gamma-unit grids are richer; B’s buckets are named. |
| SMT trade-level NQ + OHLC 3–4 assets | `wiki/smt-extreme-nonconfirmation.md` | `wiki/smt-divergence.md` | Present-A, Present-B | A’s faithful is the Open Source Fractal 3/3 pivot matcher (code-score unit errors kept as diagnostics). B’s faithful is a continuous hunted-level flag on four 1-minute books. Both required constructions exist; the Pine matcher identity is the loss. |
| GK / YZ / RV-HAR / IV | `wiki/realized-volatility.md`, `wiki/implied-vx-curve.md` | `wiki/vol-estimators.md`, EV estimator grid | Present-A, Present-B | VIX-lesson annualization / VX curve / VOLI-unavailable is fuller in A. B has the four estimators plus skew and VX slope. Not a miss. |

---

## Extra sourced objects (not on the numbered checklist)

| object | A path | B path | verdict | info lost if we keep only B |
|---|---|---|---|---|
| VWAP ±SD bands (vwap-lesson-10.pdf) | `wiki/vwap-deviation-bands.md` | SPEC row `env.vwap.sd2` only | Present-A, Present-B (thin-B) | Anchors (ETH/RTH/fixed-06/swing), trade vs HLC3, SD vs MAD/RMS. Object is computable. |
| Origin-of-move / control sequence (origin-of-the-move.pdf, whos-in-control.pdf) | `wiki/origin-control-role-flips.md` | WIC cited under absorption only | Present-A | Catalyst → release → return → refill as a timestamped sequence. Not the same as absorption A/B. |
| Refill-zone memory (refill-effect.pdf) | `wiki/refill-memory.md` | `flow.refill.offtouch` printed **not-measurable** | Present-A, Present-B | B is honest that off-touch icebergs need MBP-10. A’s on-touch cluster-return memory is still computable from MBP-1 trades. That on-touch memory is the miss. |
| AMT 80% / failed-auction populations | `wiki/auction-acceptance-and-failure.md` | 80% balance wording cited on value page | Present-A, Present-B (thin-B) | Distinct denominators (hold-inside vs open-outside two-period vs older-POC). One thin family, not 20 pages. |
| Timed retracements / session raids / HOD-LOD checkpoints / candle curves / range-probability maps / floor pivots / flow clusters / kernel bands / oscillators / adaptive HMM | many A wiki pages | pine archive as recompute or “out of scope” | Bloat-only-A (where B already recomputes the quoted table or Jumbo 2026 demotes the object) | Hardcoded Pine LUTs. B correctly recomputes them as comparison rows or drops generic TA. No distinct sourced object beyond the clock/fail/EV pages. |
| Options flow revisions, higher Greeks, node lifecycle, cross-asset object arrivals, event calendar | A options/CVD-SMT extras | nodes + SMT + data-coverage calendars | mixed: Present-A extras; not required for Phase 1 live if nodes carry known_at/OI vintage | Lifecycle/flow-revision is useful later; not a checklist miss if options rows carry `map_known_at` and `OI_vintage`. |
| A pages: `research-contract.md`, `measurement-contract.md`, `deferred-context-location.md`, 51 tickets, open QUESTIONS.md | A | B folds contract into SPEC §3–7 | Bloat-only-A as *pages* | The *rules* are not bloat. B already has one outcome grid and emitted columns. A’s open Q01–Q23 as blockers is obsolete relative to A’s own `QUESTIONS_RESOLVED.md`. |

No A wiki page was found with **zero** citation. Bloat here means no *distinct* Phase 1 outcome, not “uncited.”

---

## Discretionary PDF skim (`sources/documents/discretionary/`, 35 files)

Computable named objects vs trees:

| PDF | named computable object | in A? | in B? |
|---|---|---|---|
| amt-lesson-1.pdf, mastering-amt-vp.pdf, amt-on-live-markets.pdf | VP 70%, day/open labels, 80% claims | yes | VP yes; labels/80% thin or missing |
| tpo-lesson-3.pdf | TPO letters, IB A+B, single prints, excess, poor extremes | yes | IB comparison row only |
| vp-lesson-2.pdf, reading-the-volume-profile.pdf | HVN/LVN/shelf/ledge, 68% VA | yes | key zones + VA 70/68/40 |
| code-3-orderflow.pdf | 40% VA, unfilled single prints | yes | 40% as VA upgrade; single prints missing |
| gex-framework.pdf | GEX walls/flip; QQQ/SPY origin | yes | nodes, QQQ variant; SPY missing |
| vwap-lesson-10.pdf | VWAP ± bands | yes | SPEC row only |
| fp-lesson-8.pdf, fp-lesson-9.pdf | diagonal / same-price imbalance | yes | no |
| only-trade-big-trades.pdf | BigTrades thresholds, 350% same-price | yes | BigTrades yes; 350% no |
| your-mistakes-with-absorption.pdf, stop-re-entering.pdf, the-math-behind-auction-market-theory.pdf, reading-delta.pdf, dom-lesson-5/6/7.pdf | absorption stages, delta, CVD | yes | absorption A/B + CVD |
| refill-effect.pdf | cluster-zone return memory | yes | off-touch not-measurable only |
| origin-of-the-move.pdf, whos-in-control.pdf | OFM / control sequence | yes | citation only |
| trapped-buyers-one-retest.pdf | same-zone retest identity | folded into A refill/auction | trapped crowds cited in CVD |
| vix-lesson-4.pdf | VIX/√252, VX curve | yes | vol estimators |
| code-1-thesis.pdf | SMT leader/laggard | yes | SMT page |
| ny-am-session.pdf, average-unprofitable-trader.pdf, 10k/18k/2345/anatomy/clean-continuation | worked examples, not new objects | examples | not needed |
| emotion.pdf, code-2-risk.pdf, data-engine.pdf | not Phase 1 market objects | correctly out | correctly out |

**Missing-both:** none of the computable PDF objects are absent from *both* trees. Every miss is B dropping an object A still has (or thinning it).

---

## Quality, not file count

B (20 wiki pages) is the better *template*: one concept per page; Definition / Citations / Faithful / Upgrades / Outcomes; GB HIS WORDS / HIS CHART / INFERRED tags; Jumbo 2026 EV as its own envelope; pine hardcoded tables as recompute, not truth.

A (57 wiki pages) is the better *object catalog* for options products, FVG/CISD/TPO, footprint diagonal, P-zone upgrade axes, and extension coordinates. Many A pages are Pine LUT dumps or later-phase state machines. Those are bloat relative to Phase 1, not extra coverage of the checklist.

Thin-B rows that fail the quality bar if left as-is: options (no four-product table), A+ faithful line, P-zone 60-session-only approx, 76% claim collapsed, FVG/CISD/TPO/footprint as objects.
