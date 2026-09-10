# Premium / discount 50% split

## Definition
In an up-move, above 50% of the range is premium and below is discount; Green Bird wants shorts from premium and longs from discount when bias agrees, with the golden pocket sitting on the 50–61.8 band `[GB L144, L292–296]`; "mark off the 50% and there is your discount zone" `[GB L74]`. Jumbo's PD RTH Range+ added a dynamic premium and discount box in 2025 `[XF p.44]`, which the 2026 record downgrades to optional paint: location vs prior-day value is the part that keeps showing up `[FIND p.5, p.11]` `[PACK L90]`. Id `loc.pd50`, a location flag only, the 50% sibling of `loc.gp` on [session-fail-boxes](session-fail-boxes.md).

## Citations
- Premium / discount definition and use `[GB L144, L292–296]`; 50% as the discount zone `[GB L74–76]`; PD RTH Range+ dynamic premium & discount box `[XF p.44]`; downgrade of the painted box as a standalone signal `[FIND p.11]` `[PACK L90]`.

## Faithful object
`loc.pd50`: the 50% level of the last completed impulse (same impulse rule as `loc.gp`: from the last fail-event extreme to the subsequent extreme), with NYAM-height and 6–9-height as named impulse sources; side flag premium / discount for any event price; `known_at` = impulse completion. The prior-RTH 50% is `lvl.prior-rth.q50` on [prior-rth-quadrants](prior-rth-quadrants.md), cross-referenced, not duplicated.

## Upgrades
- Impulse source; dynamic box refreshed on each new swing (the PD RTH Range+ reading).

## Outcomes
- Share of fail events (`fail.<box>.gb.c5`) whose extreme sits in premium vs discount relative to the stated bias; reject at the 50% line under the grid.

## Links
[session-fail-boxes](session-fail-boxes.md) · [prior-rth-quadrants](prior-rth-quadrants.md) · [tbr-6-9-range](tbr-6-9-range.md)
