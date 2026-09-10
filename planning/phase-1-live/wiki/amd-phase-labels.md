# AMD phase labels (accumulation, manipulation, distribution)

## Definition
A per-session relabel of the path objects, no new geometry. Jumbo describes the range as order accumulation, the false breakout or Judas swing as the move that hits trapped stops, and the distribution to post-breakout targets `[TBR p.6]`, and frames 09:00–12:00 as a 3-hour "PO3" candle `[TBR p.16, p.19]`; Green Bird's 9:30 manipulation is the sweep below the open before the reclaim `[GB L30, L90]`; "walking the dog" is the manipulation of the box, then the real move `[FIND p.11]` `[XF p.31]`. No source draws an AMD price box; the excursion envelope is on [manipulation-distribution-envelope](manipulation-distribution-envelope.md). Ids `phase.amd.acc`, `phase.amd.manip`, `phase.amd.dist`.

## Citations
- Accumulation / false breakout / distribution language `[TBR p.6]`; PO3 framing of the 3-hour window `[TBR p.16, p.19]`; 9:30 manipulation `[GB L30, L90]`; walking the dog `[FIND p.11]` `[XF p.31]`; manipulation and distribution as excursions from the open `[PINE Statistical OHLC Projections HTF.txt:322–326]`.

## Faithful object
Per session on `range.6-9.published`: `phase.amd.acc` = the build window 06:00–09:00; `phase.amd.manip` = the first excursion beyond an edge after 09:30 that is followed by a 1-minute close back through EQ (identical to `judas.depth.any` on [range-path-class](range-path-class.md)), with its end time and depth in R; `phase.amd.dist` = the subsequent leg to the projection or the opposite edge. Single-break sessions: `manip` = the adverse excursion from the 09:30 open before the break leg (the Pine manipulation measure), `dist` = the break leg. Sessions with no manipulation leg stay unlabelled.

## Upgrades
- Window 09:00–12:00 (PO3) vs 09:30–12:00; London analog on `range.london.00-03` with the 03:00 open.

## Outcomes
- Manipulation end-time histogram (5-minute bins, 09:40–09:50 share); depth distribution; share of sessions with no manipulation leg; agreement with `label.amt.open.30m` rejection-reverse on [tpo-ib-auction](tpo-ib-auction.md).

## Links
[range-path-class](range-path-class.md) · [manipulation-distribution-envelope](manipulation-distribution-envelope.md) · [tbr-6-9-range](tbr-6-9-range.md) · [session-fail-boxes](session-fail-boxes.md)
