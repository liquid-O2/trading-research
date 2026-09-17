# The shared object layer: each author's profile, delta and level objects, from their own words

Addition to the pack (2026-09-17). These are the objects the grading study (Phase 2) and the confluence candidates (Phase 1.5) draw on; every one is cited to the author who uses it, and each family is read with its own set. Implementation: `implementation/tools/grading_features.py`.

## Jumbo (JJumboFX)

- **Single-break days on the profile**: "retrace to midpoint stays at 60.4%; on the VP and OF side easy spot absorption at midpoint of the range and taper at lows; footprint only highlighting top 35% of transactions" (JR 2064008375751311653, 2026-06-08): the quadrant and midpoint entries are read with the same profile and absorption objects as the fades.

- **Profiles on the chart**: "Just RTH session VP and delta profile" (reply 2077828415923581206, 2026-07-16); the profile is scoped to the session under study, RTH for NY execution, not an ETH composite (FIND p.8).
- **Levels drawn every day** (FIDELITY_AUDIT §Jumbo, from the charts): the box with quadrants, open and close, the projections; London and Asia highs and lows (deleted when purged); D-1, D-2, D-3 highs and lows; prior RTH high, low and value (pRTHVAH, pRTHVAL, POC); P-zones; the SessionStat envelope; the 15-minute opening range mid on single-break days.
- **Profile nodes and ledges**: P-zones are kept only where the band "sits on an HVN or on the shelf next to an LVN" (FIND p.8); the S1 level ledger names "the prior RTH and overnight profiles' shelves, ledges, LVNs and minor nodes, prior-day and weekly delta-print bands". A ledge is the edge of a high-volume shelf next to a low-volume node.
- **Delta and prints**: BigTrades threshold 100 contracts in NY, 75 in London, "anything below 100 during NY is noise" (FIND p.9); absorption = small body with a volume spike at a mapped level, optionally the imbalance inside the bar (FIND p.12); "note the absorption happening at the key levels of the 6-9" (2026-01-09).

## Sires (Ethos)

- **Delta profile and the delta print**: the highest point of the delta profile is "the single most load-bearing piece of information on the chart: whichever side produced it is the side that was rewarded" (DELTA p.7); a wick print against the profile's highest point is the trap, the print wins (p.6).
- **Protected low / high**: a low where buying aggression trapped the sellers and price stopped retesting it; partial below the sellers who last defended it, trail behind each new one (DELTA pp.4-5).
- **Delta print at a VP extreme**: a large delta print at a low-volume node or minor node of the dealing range's own profile gives repeatable intra-wick reactions (DELTA p.9).
- **Aggression boxes**: clusters of large aggressor orders, the bubble scale adjusted with the session's volume (BIG p.3); the order-level table `sires_box_table.py` with formation and consumption times.
- **Structure**: dealing range, balance, microbalance, OFM line, wick box, refill boxes (K18, BIG, OFM).

- **Shelves, ledges, naked POCs, the composite (VP2, AMT1)**: an HVN is "a price where volume built up ... price gets drawn back to these shelves and slows down inside them"; an LVN "a price where volume fell away ... price tends to react at these and traverse them quickly" (VP2 p.3). A naked POC is "a prior session's POC that price has not traded back to yet ... a ready made target list"; a composite profile merges several days or weeks and "the HVNs and LVNs that survive across all that data are the levels the whole market respects" (VP2 p.6). "Out of balance the ledges carry the move: when price leaves a balance, the ledges of the prior balance are what hold for the move to continue" (AMT1 p.9).
- **Overnight inventory (MAMT pp.14, 16)**: the overnight profile from 18:00 to 09:30 nets long or short and that carries into the open; in a double distribution the LVN between the humps is the level respected or disrespected at the open; an RTH open inside the previous ETH balance reaches that profile's mid 73% of the time.

## Saint (Ethos)

- **Value**: VAH, POC, VAL at 68% of the session's volume (VP p.4); POC as the magnet, the behaviour at POC decides the VAL or VAH target (p.5).
- **Shapes**: balanced, double distribution (two shelves and the leg between them), trending (nothing to trade), P and B (VP pp.7-11); the double distribution's shelves are the levels he plans on before price gets there (p.8).
- **Higher-timeframe balance** drawn on the daily or weekly profile, redrawn until it fits (WIC).

## Member (K10)

- Prior reaction areas lined up with a minor high-volume node of the higher-timeframe profile, or a KG1 level when no node is near; two independent reasons at one price (K10 pp.6-7).

## Green Bird

- The 9-10 box, the previous hour, the Asia and London boxes, the prior day and week extremes, the TDO, the golden pocket (GB manual; fidelity-round8 REPORT). The profile and delta bands beside his boxes on the charts are read for confluence; his own profile set is to be transcribed from the chart images before it is used as a level set.

## What the layer computes at a decision (nothing after it)

For the level in question: distance to the RTH session profile's POC, nearest HVN, LVN and ledge, and to the overnight profile's; the delta print of each window, its distance and whether its side agrees with the trade; the delta at the level; the prior RTH profile's value edges, nodes and ledges; the aggression boxes alive within five points, their contracts and whether one was carried in; touches of the level earlier in the session; the level against the RTH open and the session's range; the room to the next major level in the trade's direction.
