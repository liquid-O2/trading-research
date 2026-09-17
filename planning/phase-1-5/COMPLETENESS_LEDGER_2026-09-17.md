# Completeness ledger: what each author's sources name, what is built, what is missing

Kept as work lands (2026-09-17 night). Columns: the object or play as the sources name it (citation), where it is built, the gap and its closing action. "Feature" means the object layer computes it at a decision (`grading_features.py`); "level set" means a scanner draws it and admits entries on it; "record" means the dated examples file. The inventory of terms per author is `OBJECT_INVENTORY_2026-09-17.md`; the definitions are `OBJECT_LAYER_2026-09-17.md`.

## Jumbo (JJumboFX)

| the sources name | built | gap and action |
| --- | --- | --- |
| the 6-9 box, quadrants, range open, projections, -0.5, 1.33-1.66 band (TBR; JR) | level set (jumbo.py) | none |
| London and Asia highs and lows, D-1/D-2/D-3 highs and lows, prior RTH high/low and value (audit ledger) | level set (Judas sweeps any drawn liquidity level) | none |
| P-zones snapped to VP nodes or the shelf next to an LVN (FIND p.8) | level set from the fitted percentile recipe; node snap not applied | apply the node/ledge snap as a rescan candidate (drops bands in air) |
| SessionStat envelope (SS) | computed when asked | none |
| RTH session VP and delta profile (JR 2077828415923581206) | feature (rth_* profile, nodes, ledges, delta print, delta at level) | as a level set: not yet (his P-zone snap and "absorption at the midpoint" use it); candidate |
| overnight profile shelves, ledges, nodes; prior-day and weekly delta-print bands (S1 ledger) | feature (overnight_*, prior_day_*); weekly delta-print band: no | build the weekly delta print band (delta profile over the prior week, its print price ±) |
| composite profile, naked POCs (VP2 p.6, used by Sires; Jumbo's "3-day liquidity map") | feature (composite_*, naked_poc_*) | none for features |
| BigTrades ≥100 NY / ≥75 London as confirmation; absorption candle = small body + volume spike at a mapped level (FIND pp.9, 12) | confirmation modes: signature/rejection/orderblock/absorption on 2/3/5-minute bars; the print threshold is not part of any fill | add the print-at-level confirmation (an aggressor order ≥100 within 2 points of the level in the confirmation bar) as a rescan candidate; JJ-2026-05-19's -1.33 long (282-lot) is the dated case that misses |
| Plays: Judas fade, single break (EQ/quadrant/OR-mid/projection retest), rotation, London, P-zone, extension reaction | branches judas_reversal, judas_outbound, single_extended, single_purged, internal_rotation, other_session, timed_pzone_reversal, extension_reaction | the single-break windows end 10:30 (EQ) and 12:00 (purged); his afternoon expansion entries on the same range ("same ranges, different layers", JJ-2026-05-15 at 12:46 and 12:55 on the +0.33 projection) are outside them: extend the projection-retest play through the PM as a rescan candidate; the PM/other-clock ranges (13:00 formation, AM consolidation then PM expansion, TBR remaining clocks) are not scanned |
| records | 26 dated examples + 4 added tonight (2025-10-14, 2026-05-15, 05-19, 05-20; 10-14 and 05-20 reproduce, 05-19's band lines sit 20-30 points from our 6-9 band on the tape, so its range clock is unidentified like 05-15's); 2026-05-15's afternoon range (29,152-29,283, 'same ranges, different layers') matches no window of the 05-15 tape within 2 points (the 08:00-09:30 window is 29,142.5-29,288.25), so its clock is unidentified and the two tickets stay labelled misses until it is | 11 dated chart posts in the archive have no image on disk (2025-01-30, 06-27, 09-24, 11-04, 11-21, 11-25; 2026-02-23 schematic only; 06-08 stats; 06-10, 06-12, 07-07, 07-21, 07-23): fetch the images or leave unlabelled; 2026-02-23 is a teaching schematic (London high + range high + 9am P-zone → absorption → delta profile), no ticket |

## Green Bird

| the sources name | built | gap and action |
| --- | --- | --- |
| 9-10 box, previous hour, Asia and London boxes, prior day/week extremes, TDO, golden pocket, cash-open manipulation (GB manual) | level set (green_b02.py) | none |
| objectives at the drawn levels ("target opposing liquidity") | next drawn level | his printed targets skip nearer box edges to the prior day/week extremes, the session extremes and the Asia low on 6 of 10 tickets: the major-level objective is a rescan candidate (GB-O-major, running) |
| the profile and delta bands beside the box on every chart (audit) | feature (shared layer) | his own profile set is not transcribed from the charts: read the 17 chart pages for the profile type and the bands, add as level kinds if he trades off them |
| records | 17 dated examples + 2026-04-16, 2026-05-01 and 2026-05-04 dated tonight from GB pp.44 and 46 (the wiki's "2026-06 (two sessions)" were these two May charts; p.47 holds only the 06-26 and 06-29 dashboards, no charts) | the 2026-09-08 to 09-15 examples are outside the tape |

## Sires

| the sources name | built | gap and action |
| --- | --- | --- |
| aggression boxes (BigTrades bubbles, absorbed aggression; BIG p.3) | box table over the whole tape (edge-chained, adaptive cut, consumption); population runner | the top of a band where a drive began (2026-08-06) is a construction fit still open |
| dealing range, balance, microbalance, OFM line, wick box, refill boxes (K18, BIG, OFM, K2345) | drawn in the record only | generate: the balance from the profile shape (VP2/AMT1), the OFM line from the failed-squeeze structure, the refill boxes from repeated absorbed prints; then replay the 20 tickets on generated structure |
| delta profile, delta print, protected low (DELTA) | feature (delta print, delta at level); protected low: no | build the protected-low object (a low with buy aggression that stopped being retested) for management, P15-19 |
| naked POCs, composite HVN/LVN, shelves and ledges (VP2, AMT1) | feature | as level sets for Sires' entries: candidate |
| overnight inventory: net delta, the LVN between two overnight distributions, the ETH mid pull (MAMT pp.14, 16) | feature (net delta, ETH mid, open inside ETH value); the overnight LVN as the decision level: no | add the overnight double-distribution LVN as a level |
| records | 10 dated examples, 19 tickets (18 reproduced on generated boxes, the pre-file documented as discretion) | none pending |

## Saint

| the sources name | built | gap and action |
| --- | --- | --- |
| VAH/POC/VAL, profile shapes, double-distribution shelves (RTVP) | feature (value edges, nodes, ledges); shapes: no | classify the prior session's shape (balanced, double distribution, trending, P, B) as a read; the shelves as levels |
| HTF balance redrawn until it fits (WIC), intraday level break-departure-retest | drawn in the record; mechanics reproduce the one ticket | generate the HTF balance from the composite profile's shelves |
| records | 1 dated ticket | the remaining Saint sources carry no dated tickets |

## Member (K10)

| the sources name | built | gap and action |
| --- | --- | --- |
| prior reaction areas + minor HVN of the HTF profile, KG1 level (K10 pp.6-7) | drawn pairs in the record; both tickets reproduce on the ES tape | generate the reaction areas (prior 5-minute pivots with a reaction) and the HTF HVNs (composite profile nodes) and require both at one price; an ES market view in the framework |

## Keani

| the sources name | built | gap and action |
| --- | --- | --- |
| A period above prior value, rejection at POC/VAH, break on stacked imbalances, retest (AVG pp.21-24) | adapter; trigger repaired (footprint rows), stop below the retest low; 4 pass of 40 | no dated ticket exists; plausibility only; the higher-timeframe objective is missing on 4 of 40 sessions (objective stage unknown): define it from the source |

## Refill

| the sources name | built | gap and action |
| --- | --- | --- |
| zones of large aggressor prints, touches, holds (REF pp.5-8) | order-level zone construction; touch and hold rules are the study's own | the paper's definitions are unpublished; the order-level zones and their touches are grading rows, not a reproduction |

## Cross-strategy (the user's request of 2026-09-17)

The shared layer computes every object once per decision for every family, so any object can be tested as another family's filter or feature; the fold tool judges such a candidate like any other ("confluence" axis, one object per candidate, recall reported beside the score).
