# Prior ETH profile and MPOC

## Definition
The previous ETH profile as Ethos draws it (`value.vp.eth.prior`): the p.15–16 drawings label its high and low OVN HIGH / OVN LOW, so the profile is the overnight session 18:00–09:30 ET (the window of [overnight-profile](overnight-profile.md)), with its landmarks high, low, VAH, VAL, POC and the profile mid, labelled MPOC (`lvl.mpoc.eth`) and drawn above the POC `[MAMT p.15–16, figures]`; the prior full session 18:00–16:00 is a named variant, not the drawn object. Ethos treats these as targeting areas, not the edge, and quotes: if RTH opens inside the previous ETH profile's balance, the session hits that profile's MPOC about 73% of the time `[MAMT p.16]`. Distinct from the prior RTH profile on [value-and-profiles](value-and-profiles.md) (09:30–16:00 scope).

## Citations
- Landmarks and the "areas of targeting" caveat `[MAMT p.15]`; the 73% MPOC statistic and its use (hold and trail rather than take VAL) `[MAMT p.16]`; the stability claim to be sceptical of `[MAMT p.17]`; opening-location and prior-value rows (ES) `[MAMT p.21–22]`.

## Faithful object
`value.vp.eth.prior`: trade-level profile over the overnight session 18:00:00–09:29:59 (the drawn window), 1-tick bins, POC, VA 70% from POC; `lvl.mpoc.eth` = (profile high + profile low) / 2 (the mid of the profile as labelled, above the POC in the drawings); `known_at` 09:30. Named variant `value.vp.eth.prior.full` over 18:00:00–15:59:59 of the prior session, `known_at` 16:00. Open-inside test: 09:30 open within [VAL, VAH] of this profile.

## Upgrades
- VA 68 / 40; OHLC-1m profile; MPOC as the VA midpoint instead of the range midpoint (named); window overnight 18:00–09:30 (drawn) vs the prior full session 18:00–16:00 (named).
- Landmark rows: high, low, VAH, VAL, POC each as its own touch row.

## Outcomes
- MPOC touch rate by 16:00 given open inside the prior ETH VA (the 73% claim on its own denominator, quoted beside recomputed); touch rates of every landmark; time-to-touch.
- Faithful disagreements: sessions whose open-inside label differs between trade and OHLC profiles.

## Links
[value-and-profiles](value-and-profiles.md) · [open-location-switch](open-location-switch.md) · [overnight-profile](overnight-profile.md) · [prior-session-reference-levels](prior-session-reference-levels.md)
