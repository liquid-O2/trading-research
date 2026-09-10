# Overnight profile and inventory

## Definition
The volume profile of 18:00–09:30 ET (`value.vp.on`): its shape (one distribution vs double distribution), the low-volume node between the two humps, the overnight shelf, and ONVAH / ONVAL / ONVPOC; plus the net overnight inventory, whether aggressive buying or selling dominated the window `[MAMT p.14]`. Ethos reads the LVN or shelf as the decision point at the open: respected if the open continues the overnight direction, disrespected if not; a shelf held keeps price inside the overnight range, a shelf broken with real aggression sends price to the overnight extreme `[MAMT p.14]`.

## Citations
- Overnight inventory 6 pm–9:30, net long / short carries into the open; single vs double distribution; LVN respected / disrespected; shelf hold vs break `[MAMT p.14]`; checklist rows `[MAMT p.26]`.
- ES touch rows ONVAH 74–79%, ONVAL 69–75%, ONVPOC 86–90% `[MAMT p.21]`.
- Overnight VP shape as a balance metric for the 6–9 box already sits on [range-path-class](range-path-class.md); this page is the full 18:00–09:30 profile.

## Faithful object
`value.vp.on`: trade-level profile 18:00–09:29:59, 1-tick bins, POC, VA 70% expanded from POC; double distribution = two local maxima each ≥ 1.5× the median bin separated by a bin ≤ 0.5× the median, else single (named approximation using the [value-and-profiles](value-and-profiles.md) thresholds); the ON LVN is the band of bridge bins ≤ 0.5× the median (the p.14 drawing boxes the whole low-volume stretch between the humps; the minimum-volume price is the line variant); the ON shelf = the ledge band at the edge of the hump nearest the open (the p.14 box at the upper hump's edge; the VA edge is a named alternative); `poc_alignment` = the developing RTH POC inside the LVN band (drawn on p.14, not defined); inventory sign = sign of Σ(aggressive buy − aggressive sell) over the window (`[unmeasured]` tape object; bar proxy `flow.cvd.ohlc` named). `known_at` 09:30.

## Upgrades
- OHLC-1m profile; VA 68 / 40; 4-tick bins; window 20:00–09:30.
- Respected = 1-minute closes stay on the inventory side of the LVN for `h=30` after 09:30; disrespected = `b.c1` through it.

## Outcomes
- Shape shares; ONVAH / ONVAL / ONVPOC touch rates (MAMT p.21 recompute); LVN respected rate; open direction and path class conditional on inventory sign.
- Faithful disagreements: sessions whose shape label differs between trade-level and OHLC profiles.

## Links
[overnight-range](overnight-range.md) · [value-and-profiles](value-and-profiles.md) · [range-path-class](range-path-class.md) · [cvd-variants](cvd-variants.md)
