# Completeness ledger: what each author's sources name, what is built, what is missing

Kept as work lands (2026-09-17 night). Columns: the object or play as the sources name it (citation), where it is built, the gap and its closing action. "Feature" means the object layer computes it at a decision (`grading_features.py`); "level set" means a scanner draws it and admits entries on it; "record" means the dated examples file. The inventory of terms per author is `OBJECT_INVENTORY_2026-09-17.md`; the definitions are `OBJECT_LAYER_2026-09-17.md`.

## Jumbo (JJumboFX)

| the sources name | built | gap and action |
| --- | --- | --- |
| the 6-9 box, quadrants, range open, projections, -0.5, 1.33-1.66 band (TBR; JR) | level set (jumbo.py) | none |
| London and Asia highs and lows, D-1/D-2/D-3 highs and lows, prior RTH high/low and value (audit ledger) | level set (Judas sweeps any drawn liquidity level) | none |
| P-zones snapped to VP nodes or the shelf next to an LVN (FIND p.8) | level set from the fitted percentile recipe; the node/ledge snap against the profile built from 18:00 to the zone's anchor is the candidate `JJ-pzone-node-snap` (`jumbo.PZONE_NODE_SNAP`, v3 queue), nodes and ledges from the shared `method_pack/profile_nodes.py` (topographic prominence 20% of the peak, ledge at half the shelf's peak) | recall measured: the two printed zones (2026-01-02, 01-09) sit on nodes of the overnight profile and their tickets stay; the generated zone of 2026-05-20 (his 09:46 long at 29,170) is dropped at tolerances 5, 10 and 15 points, so the candidate's recall is 44 of 45 against the pinned 45; the fold result decides whether it is worth one dated ticket |
| SessionStat envelope (SS) | computed when asked | none |
| RTH session VP and delta profile (JR 2077828415923581206) | feature (rth_* profile, nodes, ledges, delta print, delta at level) | as a level set: not yet (his P-zone snap and "absorption at the midpoint" use it); candidate |
| overnight profile shelves, ledges, nodes; prior-day and weekly delta-print bands (S1 ledger) | feature (overnight_*, prior_day_*, weekly_delta_*: the prior five sessions' merged delta profile, its print, sign and same-signed band) | none for features |
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
| VAH/POC/VAL, profile shapes, double-distribution shelves (RTVP) | feature (value edges, nodes, ledges); the shape read (`profile_nodes.shape`: balanced, double distribution, trending, P, B) as `prior_day_shape` and `developing_shape` | the shelves as levels for Saint's entries; the read is not yet in a fitted dataset (v6) |
| HTF balance redrawn until it fits (WIC), intraday level break-departure-retest | generated (saint.py): `composite_balance` = the 70% value area of the composite of the prior five full sessions with each edge snapped to the nearest composite ledge within 40 points (2026-08-11: 29,576.5-29,950 against his drawn 29,600-29,960); the levels inside it = the composite's nodes and ledges plus the last session's 68% VAH/POC/VAL of the RTH and of the whole session (his 29,740 = the prior RTH VAL 29,738.5; his 29,840 = the prior session VAH 29,840.5), adjacent prices merged within 2 points; the balance's own profile (the composite's volume inside it) is what F04 classifies (the whole composite reads as trending by construction: the balance is its value area). The scanner now walks every break-and-retest cycle of every level with the shared `break_retest.py` rule the ticket replay was accepted on (a break after a close inside, a 24-point departure, the retest within 14 points from the broken side, a close back through ends the cycle), fills at the retest extreme and stops a tick through the broken level (his stop box 29,729-29,736.75 under the 29,740 line, not the balance edge). One retest per cycle (TRAP: 'one retest'; RR-22): on his drawn 29,740 the 18:30 break has exactly one retest, 19:47 at 29,726.75, his ticket. On the fixture-free 2026-08-11 scan the generated line is 29,738.5 (the prior RTH VAL), 1.5 points under his; the same 18:30 cycle then counts the 19:20 pullback high 29,725.0 as its retest (14 points from 29,738.5, 15 from 29,740), so the generated-structure entry is 19:21 short 29,725.0: 4.25 points and 30 minutes from his fill, the same cycle and the earlier pullback. The retest band (14 points, the replay's constant) against a 1.5-point line offset decides it; it is a fit question for the population, not a knob to turn for one ticket. The earlier first-break-only loop acted on the failed 18:21 break and never reached the 18:30 break at all | the density (all-stage passes a session on generated levels) is measured by the plausibility gate and justified in the family JSON as the candidate list; his choice among them is the grading layer |
| records | 1 dated ticket | the remaining Saint sources carry no dated tickets |

## Member (K10)

| the sources name | built | gap and action |
| --- | --- | --- |
| prior reaction areas + minor HVN of the HTF profile, KG1 level (K10 pp.6-7) | generated (member.py): reactions = prior five-minute pivots with a 4-tick reaction, minor HVNs = local maxima within 2 ticks of the composite of the prior ten sessions (`HTF_SESSIONS`; the prior single day traded below both of his pairs on the ES tape), paired within 2 ticks. On the ES tape of 2026-08-03 through the adapter's own path (ten prior ES sessions supplied as `b02_prior_sessions`) the generated pairs land on both drawn pairs before he traded them: shorts 7,559.75-7,560.5 on the 7,560 node (known 22:40-05:40), longs 7,543.5-7,547.5 on the 7,543.25-7,547 nodes (known 18:30-04:30); the replay script is `scratchpad/member_es_adapter.py` (evidence copied to the report) | the NQ population of the family on generated pairs is the next run; an ES market view in the framework is not needed for that |

## Keani

| the sources name | built | gap and action |
| --- | --- | --- |
| A period above prior value, rejection at POC/VAH, break on stacked imbalances, retest, a higher-timeframe objective (AVG pp.21-24) | adapter; trigger repaired (footprint rows), stop below the retest low; no objective above the entry now fails the objective stage (AVG p.21: "a clean break-and-retest into nothing is a clean entry into a losing trade"); 4 pass of 40 | no dated ticket exists; plausibility only; the objective set is the prior-day high, the prior VAH and the weekly high: naked POCs and composite nodes above are a candidate addition |

## Refill

| the sources name | built | gap and action |
| --- | --- | --- |
| zones of large aggressor prints, touches, holds (REF pp.5-8) | order-level zone construction; touch and hold rules are the study's own | the paper's definitions are unpublished; the order-level zones and their touches are grading rows, not a reproduction |

## Cross-strategy (the user's request of 2026-09-17)

The shared layer computes every object once per decision for every family, so any object can be tested as another family's filter or feature; the fold tool judges such a candidate like any other ("confluence" axis, one object per candidate, recall reported beside the score).
