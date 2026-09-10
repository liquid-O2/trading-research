# Dealing range and its profile

## Definition
The band price is currently rotating inside, bounded by where it last failed at each end `[ANAT p.3]` (`range.dealing`), and the volume profile drawn over exactly that band (`value.vp.dealing`) `[CONT p.9]` `[RD p.9]`. Ethos marks the prior dealing range and the minor volume nodes inside it that already produced reactions `[K18 p.4]`, reads its POC as fair value `[CONT p.5, p.9]`, and calls the settled shapes dealing ranges `[MAMT p.7]`. Distinct from a clock box: its edges are swing failures, not times. On the live charts the failure areas and the minor volume nodes inside the range are drawn as bands, not lines: grey bands about 10–20 pts tall for the nodes on the 5-minute thesis charts `[K18 p.4]` `[CONT p.4–5]`, a grey band with the absorption prints circled at the range bottom `[NYAM p.4]`, white or green rectangles a few points tall for the reaction areas `[ANAT p.7–9]`; the band's price span, not a single bin, is the location, and re-entry is only live inside it `[ANAT p.7]`.

## Citations
- Definition `[ANAT p.3]`; prior dealing range with three minor volume nodes marked `[K18 p.4]`; dealing-range VP aligning POC with the refill zone on the 1-minute `[CONT p.9]`; the dealing range's own VP for LVN / minor-node extremes `[RD p.9]`; "he calls them dealing ranges" `[MAMT p.7]`.
- Redraw the balance until it fits price before trading off it `[TRAP p.3, p.12]`.

## Faithful object
`range.dealing`: the band between the last confirmed swing high and swing low on 5-minute NQ bars (5-bar fractal from `[PINE Key levels, MTF swing highs, lows & 4h candle boxes.txt:150–164]`), where "last failed" = the swing whose extreme was not exceeded by a later 1-minute close; `known_at` = the confirming bar close; a new band forms when a `b.c1` break of either edge is followed by a new confirmed swing. `value.vp.dealing`: trade-level profile over the band's bars, POC, VA 70%, `value.kz` nodes.

## Upgrades
- Fractal 3 / 7; timeframe 1 / 15 m; edge confirmation `b.c5`.
- OHLC profile; VA 68 / 40.

## Outcomes
- Grid at the band edges; POC touch and hold; count of sessions where the `value.vp.dealing` POC sits within `tR` of a `flow.refill.zone` (the CONT alignment, descriptive).
- Edge reject rate by arrival class from [approach-speed](approach-speed.md).

## Links
[value-and-profiles](value-and-profiles.md) · [refill-zone](refill-zone.md) · [protected-high-low](protected-high-low.md) · [approach-speed](approach-speed.md)
