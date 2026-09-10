# Ingest log

Format: date · what was read · how · notes. Raw sources are immutable; this log records the compile, not edits to sources.

## 2026-09-09 — live compile from coverage audit

This tree is a merge of two planning wikis. Neither prior tree was edited. Inputs:

1. A = `planning/phase-1-from-scratch/` wiki index and every page that claims a checklist object.
2. B = `planning/phase-1-fable/` wiki index and every page that claims a checklist object.
3. Packs (already in B/references, not rewritten): `jumbo-x-wiki-pack.md`, `greenbirdtrader-trading-framework.md`, `agent-method-matt-wiki.md`.
4. Raw evidence: `sources/documents/` (jumbo PDFs, 35 discretionary PDFs by filename, conversations user turns, inventory, indicators, reference-images). Archive plans not used.
5. Coverage table: `planning/phase-1-compare/COVERAGE.md`. Verdict: `planning/phase-1-compare/VERDICT.md`.

Rule applied: if B already has the object with definition, citation, faithful row, upgrades, outcomes → keep B’s page. If B dropped a sourced object A still has → take A’s section or write a short page from the source. Options pages must list NDX, NDXP, SPX, SPXW.

## Pages in this tree

Kept from B (patched where the audit marked a miss or drift): index, data-coverage, touch-reject-hold-break-grid, tbr-6-9-range, range-path-class, open-location-switch, clock-grid-and-bars, ev-range-expected-move, sessionstat-9-12-envelope, extensions-1-33-1-66, p-zones-benchmark, session-fail-boxes, value-and-profiles, absorption-and-big-trades, cvd-variants, smt-divergence, vol-estimators, options-nodes, sources-pine-archive.

Written short from A/source: fvg-body-gaps, sweep-cisd-blocks, tpo-ib-auction.

Not rebuilt: A’s 51-ticket catalog, Pine LUT families, higher-Greeks family, BBO family, adaptive HMM, floor-pivots-as-family.

## 2026-09-10 — thin pages from `../RULES.md` A7

Read: `../RULES.md` §A7 and the source rows it points at (TBR, XF, FIND, GB pack, the discretionary PDFs, the Pine archive, `momentum-volume-flow-levels.txt`, conversation user turns). How: one page per concept where an A7 id had a citation and no page; ids that are variants of an existing page's concept were named on that page instead of duplicated. Every A7 id carried a citation, so no id is blocked; none is listed here as blocked.

Pages written (31): tbr-remaining-clocks, overnight-range, overnight-profile, dealing-range, prior-eth-profile, composite-profiles, weekly-delta-profile, delta-spike, prior-rth-quadrants, prior-session-reference-levels, unfinished-business, sigma-band-reversion, manipulation-distribution-envelope, vwap-anchored, absorption-candle-jumbo, refill-zone, ofm-catalyst, footprint-imbalance-zones, candle-poc-flip, protected-high-low, mvfl-indicator-zones, reward-system-3tick, digit-thinning, tape-speed, spread-width, approach-speed, premium-discount-50, daily-open-1800, gex-walls-and-max-pain, amd-phase-labels, clean-session-label.

Ids folded into existing pages (one line each): `env.ss.rth.avgHL60` on sessionstat-9-12-envelope; `env.vwap.rth.sd1` / `sd2.5` / `sd3` on value-and-profiles; `label.amt.80pct.two-period` on tpo-ib-auction. Index: new section plus two citation-key rows.

Not paged (not A7 ids; grid candidates or tier-4 proposals only): `range.4h.*`, `env.pine.sessionstat.P10-P90`, the JJX derived-range families. Tape objects on the new pages keep the `[unmeasured]` tag from RULES.md §0.2: locations now, triggers only after a FINDINGS row. No tickets added, no runner started, RULES.md unchanged.


## 2026-09-10 — FORMULAS.md source check (wiki ≠ source patches)

Read: every source cited by `../RULES.md` section B and by the live pages (TBR, XF, FIND, SS, GB pack, X pack, the discretionary PDFs through the archived per-page text, the Pine archive, MVFL, user conversation turns), then `../RULES.md`, `../RULES_SCORES.md`, `../CONSTRUCTION_AUDIT.md`, and the Python under `implementation/src/trading_research/research/phase1_live/`. Output: `../FORMULAS.md` (105 R- blocks plus the shared primitives). Patches, one sentence each:

- session-fail-boxes: `lvl.nwog` endpoint changed from "Friday 17:00 settle" to Friday close per `[GB L60, L69]`, with the 15:59 RTH close and the 17:00 settlement kept only as named variants.
- absorption-candle-jumbo: removed the MVFL 2.5 × SMA20 borrowing; multiplier, body ratio and timeframe are source-unspecified for this Jumbo object and the 14-period average is trailing `[TBR p.35]`.
- tpo-ib-auction: `label.amt.open.30m` now carries the `[AMT1 p.11]` open-type definitions (drive = never trades back through the 09:30 open) and records that the retained code labels drive against the prior value area instead.
- manipulation-distribution-envelope: the Pine object is the HTF / daily candle anchored at 18:00 (NY-midnight option) with lookback 60 `[PINE Statistical OHLC Projections HTF.txt:8–15]`; the RTH 09:30–16:00 candle is a named variant, not the default.
- extensions-1-33-1-66: the beyond-edge coordinate now rests on Jumbo's own chart labels `[PACK L66]` and `[TBR p.21]`; the Pine 6–9 file is no longer cited as a source for a Jumbo object; the FIND fib-list reading is the named from-origin alternative.
- tbr-6-9-range: the Pine "restatement" line is marked as a third-party file that is not Jumbo's script and serves comparison rows only.
- sessionstat-9-12-envelope: `env.ss.minavg60` now states that `[SS p.6]` prints no formula and names both readings (lower-half average; min of the two one-sided means) with no default.
- refill-zone, delta-spike, tape-speed, approach-speed, candle-poc-flip, protected-high-low, weekly-delta-profile, ofm-catalyst: every constant the page names but no source prints is tagged "(named; not printed by the source)"; the printed ones (60 / 80 / 100-lot clusters `[REF p.5]`, the 30-lot minimum `[OFM p.4]`) stay as printed.

Rule recorded in `../FORMULAS.md` §0.1: Jumbo geometry comes from Jumbo's materials only (manuals, X archive, findings, X pack, user turns); the Pine archive holds no Jumbo script and its "6–9"-style files are cited only in the `R-P` rows. No tickets added, no Phase 2 work, no Python written.


## 2026-09-10 — Jumbo projections and reversals read on both sides (RULES / FORMULAS amendment)

Read: the two Jumbo manuals (`[TBR]`, `[SS]`), the raw X archive (`[XF]`), the findings reconstruction (`[FIND]`), the X pack (`[PACK]`) and the user's conversation turns, including the chart pages through the archived page renders (`archive/2026-09-pre-reset/…/pdf-render/jumbo/`): TBR p.9–10, p.13, p.20–21, p.30; XF p.7, p.9, p.19, p.25, p.31, p.33, p.47–48; FIND p.4–5. Output: `../RULES.md` A1.2 / A2 / B1 / C2 / C3 and the matching `../FORMULAS.md` blocks (R-J01, J02, J08, J09, J12, J13, J18, J22, J23, P3-01, P3-02, P3-09, Part 4); no Python, no Phase 2, no tickets. Wiki patches, one sentence each:

- tbr-6-9-range: the projections are drawn on both sides of every chart (+0.5 … +2 above the high, −0.5 … −2 below the low) with the mean-reversal ladder 0.1 / 0.2 / 0.3 and its shaded area, so the exhaustion location is the area beyond the swept edge whichever side that is `[TBR p.5, p.9–10, p.13, p.20, p.30]`; the depth table's citation is corrected from "p.12" to the p.30 bar chart "Reversal % by Projection (Upper vs Lower)" and the console's "Extended Range: ±0.5" and two reversal times are recorded; the overshoot reading and the width-base variants (`w.ev` never faithful) are named.
- extensions-1-33-1-66: the object is an area on both sides (`band.133-166`), drawn below the low on TBR p.21 / XF p.31 / p.33 and above the high on TBR p.10 / XF p.48, with the overshoot reading and the width-base variants; the from-EQ anchor is a named comparison, no longer justified by Pine files.
- ev-range-expected-move: the EV lines are drawn above and below the box (XF p.7 chart); no source projects the 6–9 ladder in EV width, the "EVrange −60%" label is unexplained, `w.ev` is a test variant only.
- tbr-remaining-clocks: every published clock carries the full two-sided ladder in its own height (`w.own`), citing the p.13 Scenario #2 drawing.
- range-path-class: `judas.depth.mr` added between `any` and `-0.5`; the labels are scored on the swept side with the side as a column.
- clock-grid-and-bars: the box internals list names the two-sided ladder.
- clean-session-label: the clean-session reject is at ±0.5 on the swept side, not at −0.5 only.
- sessionstat-9-12-envelope: the coincidence rows use the ±0.5 / mean-reversal area and the 1.33–1.66 area on either side (XF p.19 chart shades both).
- p-zones-benchmark: the distance ranking and the edge overlap are stated per side (the 2 Jan 2026 example is the low side; the mirror is the same object).
- touch-reject-hold-break-grid: `grid.jumbo.projection-reject` is the reject at the projection ladder on the swept side (both sides, overshoot allowed), not "at −0.5" only.

Verified against the sources, not treated as law: reversals are drawn at ±0.5, at the mean-reversal lines between the edge and ±0.5, and at the 1.33–1.66 area, with small overshoot, above and below the box, every level a multiple of the range height. Not verified: any switch of the projections to EV width — no manual, tweet, chart label or user turn states it, so `w.ev` is a named test variant. `../FORMULAS.md` §0.3 and Part 4 record that the 2026-09-10 rescoring moved ten Jumbo rows to pass; only the Jumbo headers and verdicts were refreshed.


## 2026-09-10 — the other families read against their figures (Green Bird, Sires, AMT, flow, regime, Pine)

Read: every PDF the non-Jumbo rows cite, text and rendered page (`archive/2026-09-pre-reset/…/pdf-render/discretionary/`), the Green Bird pack, the Pine scripts at the cited lines, and the conversation files at the cited lines; the same classes of miss as the Jumbo pass (one side written where the source draws both, an area written as a line, overshoot / depth drawn but unprinted, unit base, figure-only constants, wrong citations). Output: `../RULES.md` A / B2–B8 / C3 rows and the matching `../FORMULAS.md` blocks, Part 4; no Python, no Phase 2, no tickets. Wiki patches, one sentence each:

- session-fail-boxes: `label.aplus` is a sweep of the traded box plus the failure back inside `[GB L242]`, with sweep-only as the named weaker label `[GB L93, L147]`; the body-vs-wick invalidation variant, the illustrative ticket stops and the one-sided triggers (9:30 manipulation, stacked sweep) are recorded `[GB L92, L622, L356–358, L606, L687]`.
- dealing-range: the failure areas and minor volume nodes are drawn as bands on the live charts, not lines, and re-entry is only live inside the band `[K18 p.4]` `[CONT p.4–5]` `[NYAM p.4]` `[ANAT p.7–9]`.
- footprint-imbalance-zones: the 350% flag prints as a box with a height on the live chart; the line is the reduced form `[K2345 p.5]`.
- clock-grid-and-bars: `bars.range40` (40-tick range bars) added as the named bar type of the Sires execution charts `[NYAM p.4]` `[K18 p.7]` `[K2345 p.5]` `[CONT p.5]`.
- RULES / FORMULAS Green Bird and Sires rows read against the figures: R-S02 rebuilt as a support band tested from above with a continuation short (was written as a resistance fade); both sides stated where printed (S01, S03, S05, S06, S07, S08) and named as variants where not (G04, G09, S04, S09); areas as bands; R-S06 marked as an ES example with 20-tick / 1:1 tickets beside the text's 1.5R; R-S08 flip-to-long rule added; R-G11 A+ = sweep + fail-back; `lvl.nwog` endpoint aligned; working-tree code verdicts noted without changing headers.
- prior-eth-profile: the "previous ETH profile" of the 94% / 73% statistics is the overnight session 18:00–09:30 — the p.15–16 drawings label its extremes OVN HIGH / OVN LOW and draw MPOC above the POC — so `value.vp.eth.prior` now carries that window and the prior full session 18:00–16:00 is the named variant `value.vp.eth.prior.full` `[MAMT p.15–16]`.
- prior-session-reference-levels: `lvl.halfgap` is the half of the session gap ((pHOD + open) / 2 above the prior range, (pLOD + open) / 2 below it) per the p.22–23 rows "1/2 Gap of pHOD / pLOD Touched", the close-based half gap is a named variant, and the pHOD cells equal the "Opens Above pHOD" shares to the digit, so both readings are recomputed `[MAMT p.21–23]`.
- overnight-profile: the ON LVN is the band of bridge bins between the humps and the ON shelf the ledge band at the edge of the hump nearest the open, both drawn as boxes on p.14 (the minimum-volume price and the VA edge stay line variants), and the drawn "POC alignment" of the RTH POC inside the LVN box is recorded `[MAMT p.14]`.
- value-and-profiles: `value.kz` HVN / LVN are carried as bands with the peak / trough price as the line variant, ledges as lines drawn on both sides of the POC ("four ledges around the POC"), and the shelf keeps the lesson's two readings (body between the lines; thin band at the transition) with an unprinted thickness `[VP2 p.3–5]` `[MATH p.13]`.
- tpo-ib-auction: premium / discount is also read against the TPO value area `[TPO p.4, p.9]`; the MAMT four-class day set (trend beyond IB×2, neutral extreme, neutral, normal) is a second label never pooled with AMT1's five `[MAMT p.20]`; single prints are interior rows and the poor / excess flags are emitted at both extremes with the two poor readings kept separate because every extreme is one of the three by construction `[TPO p.5–7]`.
- gex-walls-and-max-pain: the p.13 chart draws three ranked call walls on either side of spot and the p.15 panel prints put wall = max pain, so the ranked top-3 set is recorded beside the one-per-side text rule; the flip is stated in its three readings and the regime in its two; the Vol Trigger, VOL-GEX and the hedging-pressure gauge are recorded as drawn-but-undefined `[GEX p.6–7, p.13–15, p.19]`.
- options-nodes: the "NDX levels feel more accurate than QQQ" cite moved from a blank line to the user's `[CEX L565]`; the sister-index gamma remark `[CEX L455–456]` added.
- vol-estimators: the VIX4 p.3 figure's formula Expected Daily Move (%) = VIX / √252 recorded beside the ES point anchors; VXN named as the Nasdaq-100 twin `[INV L610]`.
- sources-pine-archive: the Asia-low mirror of the London-hit conditional (78.54 / 54.64) added; "GZ" in the floor-pivot file identified as the daily Golden Zone 0.5–0.618; the IB file's 0.1 % leave-and-return midpoint-retest band noted.
- mvfl-indicator-zones: the indicator cite moved from the turn header `[CEX L7]` to the user's `[CEX L17]`; the aggressor-delta rebuild cite from `[CEX L16]` to the assistant's `[CEX L33]`.
- prior-rth-quadrants: the `[DRFL L906]` cite (a file-attachment stub) dropped; `[DTM L19]` stands alone.
- absorption-and-big-trades: the BigTrades figures mark the print-plus-350%-line level as a small box around the candle, the balance-day fade area as a box from the first absorbed print to the retest, and the OFM level as a line at the first absorbed aggression `[BIG p.3, p.5, p.7, p.15]` `[CONT p.10]`.
- reward-system-3tick: the passive wall and the reward retest are drawn as a band and the CVD median as a line `[ABS p.4, p.9]`; the digit-read clips are ES (EPZ25) `[STOP p.11–13]`.
- refill-zone: the zone's contract unit is unstated (the paper pools NQ and MNQ, its sized figure is MNQ with ≥ 40 shown) and "hitting in seconds" reads as a burst, so per-print and per-burst readings are both named `[REF p.5, p.23]`; the penetration variants come from the printed grid (stops 25–65, targets 20–100 ticks) `[REF p.17–18]`.
- ofm-catalyst: the OFM is drawn as a line at the first absorbed aggression print (lowest for a long, highest for a short) with the cluster boxed, in both directions `[OFM p.2, p.5–10, p.14]` `[BIG p.7]` `[CONT p.10]`; the faithful location is the line, the box is the named area.
- footprint-imbalance-zones: `flow.footprint.imb350` has a buy mirror and is marked on the chart as a small box around the print's candle `[BIG p.3, p.5]`; the stack-of-2 at a level is printed `[FP8 p.7]`.
- delta-spike: both of the lesson's spikes are buy-delta spikes (absorbed at VAH, regaining control at VAL; the p.11 figure duplicates the VAH label), so the spike's sign is recorded with the extreme and the outcome and never read as the absorbed side `[ABS p.11]`.
- digit-thinning: the digit classes are literal on the ES clips `[STOP p.11–13]`; NQ session-quantile classes are named beside the 10 / 100-lot reading.
- tape-speed: the charts label the panel "Speed of Tape (10)" with the unit unstated, so a 10-unit window is a named variant `[BIG p.3]` `[OFM p.7]`.
- candle-poc-flip: the p.5 schematic moves the POC ≈ 0.17 → 0.83 of the candle, satisfying halves and thirds `[FP9 p.5]`.
- vwap-anchored: the `.session` anchor is the exchange session from 18:00 (the lesson's "Session" setting), the 09:30 cash open the session-open event anchor `[VWAP p.7–8]`.
- value-and-profiles: the drawn VWAP object is the exchange-session (18:00) VWAP with ±1 / ±2 (settings tab: Anchor Period = Session, bands 1 and 2 ticked, #3 off; the chart runs through the overnight), so `env.vwap.eth.sd{1,2}` is the faithful row and the 09:30 anchor and 2.5 / 3 are named `[VWAP p.3, p.8]`.
- protected-high-low: the protected low is drawn as a small band around the sellers' delta cluster with the stop below it and the delta print as a box `[RD p.4, p.7]`.
- cvd-variants: the "CVD median" is a plotted line whose construction no source states `[ABS p.5]` `[BIG p.12]` `[STOP p.8]`; named variant when CVD is rebuilt.

Verified against the figures, not the text alone: the mirrors the case studies print (Sires), the session-anchored VWAP settings, the buy-side delta spikes at both value extremes, the overnight scope of the MAMT 94% / 73% stats, the far-boundary failed-auction target, the ranked GEX walls on either side of spot, the VIX / √252 formula and the 13 / 14 / 15–18 / 20 cut points. Not verified and left named: the VWAP chart's time zone (the 18:00 reset is inferred from TradingView's "Session" anchor), the refill paper's per-print unit on NQ vs MNQ, the shelf / band thicknesses, the Speed-of-Tape unit, the CVD median construction, the R-R02 fixture for 2025-09-15 (needs VIXCLS of 2025-09-12). Statuses: every `../FORMULAS.md` block header and the Part 4 status column now carry the committed `RULES_SCORES.md` status (99 pass / 2 gap / 4 blocked at 40017dd); blocks not re-audited say so in their Code bullet.
