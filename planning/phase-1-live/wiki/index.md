# Phase 1 wiki — index

Phase 1 = measurement and comparison of objects on a frozen slice. No trading, no predictor training, no P&L.
Every page: definition, citations, faithful object, upgrades, outcomes, links. One concept per page.
Raw evidence lives in `sources/documents/` and is never edited. This wiki is compiled from it.

## Citation key

| Key | Source (path relative to repo root) | Tier |
|---|---|---|
| `[DTM L#]` | `sources/documents/conversations/Develop Trading Model.md` (user turn = lines 13–31) | 1 |
| `[JJX L#]` | `sources/documents/jumbo/JJumbo_Conversation_Export.md` (user turns §1 L50–58, §7 L146–153) | 1 |
| `[DRFL L#]`, `[CEX L#]`, `[CRAW L#]` | `conversations/Design robust feature levels.md`, `conversation_export (1).md`, `conversation_raw_log.md` | 1 (user) / 4 (assistant) |
| `[TBR p.N]` | `sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf` page N (38 pp) | 2 |
| `[XF p.N]` / tweet id | `sources/documents/jumbo/xfcmg2.pdf` page N (48 pp, 66 posts, 2026 tweets) | 2 |
| `[SS p.N]` | `sources/documents/jumbo/SessionStat+.pdf` page N (12 pp) | 2 |
| `[FIND p.N]` | `sources/documents/jumbo/jjumbo-findings.pdf` page N (14 pp) | 2, secondary to TBR/SS/XF/JJX/PACK |
| `[ABS p.N]` etc. | `sources/documents/discretionary/<file>.pdf` page N | 2 |
| `[AMTL]` `[MAMT]` `[MATH]` `[TPO]` `[VP2]` `[RTVP]` `[FP8]` `[FP9]` `[VWAP]` `[DOM5–7]` `[ABS]` `[STOP]` `[RD]` `[WIC]` `[TRAP]` `[BIG]` `[OFM]` `[REF]` `[GEX]` `[VIX4]` `[C1–C3]` `[NYAM]` `[K18]` `[K2345]` `[K10]` `[ANAT]` `[CONT]` `[AVG]` | discretionary PDF keys; file map in `../RULES.md` §0.3; page = PDF page index (cover = 1) | 2 |
| `[MVFL L#]` | `sources/documents/indicators/momentum-volume-flow-levels.txt` line (the user-supplied indicator `[CEX L7]`) | 2 |
| `[PINE file:L#]` | `sources/documents/indicators/Pinescript-indicators--main.zip` → file, line | 2 |
| `[INV L#]` | `sources/documents/inventory/DATA_INVENTORY.md` line | 2 (acquired ≠ pull list) |
| `[GB L#]` | `planning/phase-1-fable/references/greenbirdtrader-trading-framework.md` line | 3 |
| `[PACK L#]` | `planning/phase-1-fable/references/jumbo-x-wiki-pack.md` line | 3 |
| `[METHOD]` | `planning/phase-1-fable/references/agent-method-matt-wiki.md` | 3 |

Ambiguous rule → named variants, never a guess presented as the rule.

## Pages

**Foundations**
- [log](log.md) — ingest record for this compile.
- [data-coverage](data-coverage.md) — what exists, frozen slice F and long slice L, cash-index minute prohibition.
- [touch-reject-hold-break-grid](touch-reject-hold-break-grid.md) — the one outcome grid every family reports with.

**Jumbo objects (Time-Based Ranges; 2026 use outranks older marketing)**
- [tbr-6-9-range](tbr-6-9-range.md) — published 06:00–09:00 box, internals, width tables on 6–9 **and** prior RTH.
- [range-path-class](range-path-class.md) — high-only / low-only / both / neither, break order, Judas / extended / purged.
- [open-location-switch](open-location-switch.md) — RTH open vs prior value, prior range, and the 6–9 box; double-break expectancy split.
- [clock-grid-and-bars](clock-grid-and-bars.md) — 5–9 family, Jumbo London TBR, Asia TBR, GB clocks, 9:40–9:50 vs first 20 min, volume-elapsed and dollar/trade bars.
- [ev-range-expected-move](ev-range-expected-move.md) — AM expected-move envelope, own page, own estimator grid.
- [sessionstat-9-12-envelope](sessionstat-9-12-envelope.md) — SessionStat+ 09:00–12:00, comparison row.
- [extensions-1-33-1-66](extensions-1-33-1-66.md) — 1.33 / 1.66 from the 6–9 (or London) range. Not P-zones. Not ATL.
- [p-zones-benchmark](p-zones-benchmark.md) — unpublished formula; disclosed approximation as benchmark; learned model is Phase 3.

**Green Bird objects and fail-back labels**
- [session-fail-boxes](session-fail-boxes.md) — sweep + fail-back inside across named boxes; GB-NYAM, GB-10-11, GB-hour, GB-Asia, GB-London, TDO, NWOG, 9:30 sweep, golden pocket, A+ = sweep happened.

**Flow, value, options**
- [value-and-profiles](value-and-profiles.md) — RTH VP, value areas, delta profile, key zones, VWAP row.
- [absorption-and-big-trades](absorption-and-big-trades.md) — absorption, BigTrades 100 NY / 75 London, footprint diagonal, on-touch refill, OFM sequence.
- [cvd-variants](cvd-variants.md) — five CVD constructions.
- [smt-divergence](smt-divergence.md) — trade-level on NQ, OHLC-level across NQ/ES/YM/RTY; Pine matcher as a named row. Not a GB edge.
- [vol-estimators](vol-estimators.md) — GK, YZ, RV/HAR, IV/skew/VX as features.
- [options-nodes](options-nodes.md) — native nodes for **NDX, NDXP, SPX, SPXW**; QQQ, SPY, NQ.OPT as named variants. Ticket 09, not 06.

**Discretionary families kept thin (sourced, not inside GB pages)**
- [fvg-body-gaps](fvg-body-gaps.md) — wick gaps, body gaps, first-presented FVG.
- [sweep-cisd-blocks](sweep-cisd-blocks.md) — three-candle sweep, CISD, rejection blocks.
- [tpo-ib-auction](tpo-ib-auction.md) — TPO single prints / excess / poor extremes; AMT day/open labels; IB is a comparison row only.

**Thin pages from `../RULES.md` A7 (added 2026-09-10; ids that had a source but no page)**
- Jumbo and clocks: [tbr-remaining-clocks](tbr-remaining-clocks.md) — midnight OR, 09:30–10:00, 10:00–10:30, lunch OR, MOC; [clean-session-label](clean-session-label.md) — which clock is clean this cycle; [amd-phase-labels](amd-phase-labels.md) — accumulation / manipulation / distribution as path relabels; [absorption-candle-jumbo](absorption-candle-jumbo.md) — Absorption Zone+ bar object; [prior-rth-quadrants](prior-rth-quadrants.md) — prior-day 25 / 50 / 75.
- Envelopes: [sigma-band-reversion](sigma-band-reversion.md) — Pine ±0.25σ band from the 08:00 open; [manipulation-distribution-envelope](manipulation-distribution-envelope.md) — Pine excursions from the open; [vwap-anchored](vwap-anchored.md) — swing / event / weekly / monthly anchors.
- Profiles and levels: [overnight-range](overnight-range.md) — ONH / ONL; [overnight-profile](overnight-profile.md) — 18:00–09:30 profile, LVN, inventory; [prior-eth-profile](prior-eth-profile.md) — prior 18:00–16:00 profile and MPOC; [prior-session-reference-levels](prior-session-reference-levels.md) — prior close / open / IB / half-gap touch tables; [composite-profiles](composite-profiles.md) — 5 / 20 / 250-day composites; [dealing-range](dealing-range.md) — swing-bounded band and its profile; [unfinished-business](unfinished-business.md) — nearest owed level; [premium-discount-50](premium-discount-50.md) — 50% split; [daily-open-1800](daily-open-1800.md) — 18:00 open and Sunday weekly open.
- Flow prints: [weekly-delta-profile](weekly-delta-profile.md); [delta-spike](delta-spike.md); [protected-high-low](protected-high-low.md); [refill-zone](refill-zone.md); [ofm-catalyst](ofm-catalyst.md); [footprint-imbalance-zones](footprint-imbalance-zones.md) — stack ≥3 and same-price 350%; [candle-poc-flip](candle-poc-flip.md); [reward-system-3tick](reward-system-3tick.md); [digit-thinning](digit-thinning.md); [tape-speed](tape-speed.md); [spread-width](spread-width.md); [approach-speed](approach-speed.md); [mvfl-indicator-zones](mvfl-indicator-zones.md) — the user-supplied indicator's zones and bias vote.
- Options: [gex-walls-and-max-pain](gex-walls-and-max-pain.md) — call wall, put wall, max pain per product.
- Ids folded into existing pages instead of new ones: `env.ss.rth.avgHL60` → [sessionstat-9-12-envelope](sessionstat-9-12-envelope.md); `env.vwap.rth.sd{1,2.5,3}` → [value-and-profiles](value-and-profiles.md); `label.amt.80pct.two-period` → [tpo-ib-auction](tpo-ib-auction.md).

**Sources**
- [sources-pine-archive](sources-pine-archive.md) — 84-file Pine archive: construction vs hardcoded tables to recompute.

## Phase boundaries

Phase 1 labels sessions and measures objects. Phase 2 predicts (context). Phase 3 learns location (reversal / P-zone model).
Skylit Heatseeker / Flowseeker / Atlas: Phase 2–3 `[README sources/documents/README.md L27–30]`.
Columns Phase 1 must emit for later phases: `../SPEC.md` §7.
