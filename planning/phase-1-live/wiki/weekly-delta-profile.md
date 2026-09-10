# Weekly delta profile

## Definition
The per-price delta profile over the trailing week, used before the open to see who got trapped and who is covering: a weekly delta footprint showing sellers trapped at the lows and exhausted on the way back up `[K18 p.4]`, or heavy buying aggression behind a grind higher with sellers trapped on the way up `[K2345 p.4–5]`. Id `value.delta.weekly`. The daily version is `value.delta.rth.trade` on [value-and-profiles](value-and-profiles.md).

## Citations
- Weekly delta print checked for who got trapped and who is covering `[K18 p.4, p.14]`; weekly delta profile showing heavy buying aggression; sellers previously trapped visible in the delta profile `[K2345 p.4–5]`.
- Heavy one-sided delta at an extreme read as trapped positioning, not strength `[TRAP p.4]`; an aggressive push that fades on delta = trapped side `[WIC p.6]`.

## Faithful object
`value.delta.weekly`: per-price (aggressive buy − aggressive sell) from NQ trades over the trailing 5 completed sessions (18:00–16:00 each), 1-tick bins; `dp.max` / `dp.min` prices; trapped-print flag = |delta| ≥ q90 of the profile at a price within `tR` of the weekly high or low that price has since left by ≥ 0.5·R (R = the weekly range). `known_at` = prior close. `[unmeasured]` tape object.

## Upgrades
- Calendar week (Sunday 18:00) vs trailing 5; 4-tick bins; bar-level proxy from `flow.cvd.ohlc`.

## Outcomes
- Grid at `dp.max` / `dp.min` prices; retest outcome of trapped-print prices (reject vs slice); agreement of the weekly trapped side with the next session's path class (label only).

## Links
[value-and-profiles](value-and-profiles.md) · [delta-spike](delta-spike.md) · [cvd-variants](cvd-variants.md)
