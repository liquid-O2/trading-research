# Prior ETH profile and MPOC

## Definition
The completed profile of the prior full session 18:00–16:00 ET (`value.vp.eth.prior`) with its landmarks high, low, VAH, VAL, POC and the profile mid, labelled MPOC (`lvl.mpoc.eth`) `[MAMT p.15]`. Ethos treats these as targeting areas, not the edge, and quotes: if RTH opens inside the previous ETH profile's balance, the session hits that profile's MPOC about 73% of the time `[MAMT p.16]`. Distinct from the prior RTH profile on [value-and-profiles](value-and-profiles.md) (09:30–16:00 scope).

## Citations
- Landmarks and the "areas of targeting" caveat `[MAMT p.15]`; the 73% MPOC statistic and its use (hold and trail rather than take VAL) `[MAMT p.16]`; the stability claim to be sceptical of `[MAMT p.17]`; opening-location and prior-value rows (ES) `[MAMT p.21–22]`.

## Faithful object
`value.vp.eth.prior`: trade-level profile over the prior session 18:00:00–15:59:59, 1-tick bins, POC, VA 70% from POC; `lvl.mpoc.eth` = (profile high + profile low) / 2 (the mid of the profile as labelled); `known_at` 16:00 prior day. Open-inside test: 09:30 open within [VAL, VAH] of this profile.

## Upgrades
- VA 68 / 40; OHLC-1m profile; MPOC as the VA midpoint instead of the range midpoint (named).
- Landmark rows: high, low, VAH, VAL, POC each as its own touch row.

## Outcomes
- MPOC touch rate by 16:00 given open inside the prior ETH VA (the 73% claim on its own denominator, quoted beside recomputed); touch rates of every landmark; time-to-touch.
- Faithful disagreements: sessions whose open-inside label differs between trade and OHLC profiles.

## Links
[value-and-profiles](value-and-profiles.md) · [open-location-switch](open-location-switch.md) · [overnight-profile](overnight-profile.md) · [prior-session-reference-levels](prior-session-reference-levels.md)
