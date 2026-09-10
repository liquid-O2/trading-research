# Value areas, RTH-scoped volume profile, delta profile, key zones

## Definition
The RTH-scoped volume profile (09:30–16:00) with POC, VAH and VAL; prior-day value as the reference for the open-location switch `[XF p.8 L118]`; the delta profile drawn beside it (absorption at mid, taper at lows) `[XF p.23 L292]` `[JJX L52]`; key zones = profile extremes (shelves, ledges, high- and low-volume nodes) where an order-flow signature is meaningful, versus POC where it is a coin flip `[ABS p.6 L87–98, p.7 L114]`. All are Phase 1 objects with upgrades `[BRIEF]`.

## Citations
- Value area = band holding roughly 70% of volume around POC; POC = busiest price `[AMT1 p.5 L86–95]`; 68% wording `[RTVP p.4 L45–47]`; POC as magnet, VAH / VAL targets decided by POC behaviour `[RTVP p.5 L58–64]`; balance rule ≈ 80% inside balance, "stop using VAH / VAL as levels", P-day / b-day shapes `[MAMT p.4 L51–58, p.5 L72–83, p.7 L106]`; 40% value area for intraday `[C3 p.7 L105]`; balance / imbalance engine `[AMT1 p.4 L74–80]`; value is a process not fixed lines `[MATH p.9 L137]`.
- Delta profile: heavy one-sided delta print at an extreme = trapped side to watch `[TRAP p.4 L50–57]`; delta print / CVD definitions `[STOP p.3 L40–44]`; absorption signature is a coin flip at POC, a signal at a real extreme `[ABS p.2 L17, p.6 L87]`.
- Jumbo screenshots: NinjaTrader RTH profile + BigTrades + 6–9 box `[PACK L70]`; "absorption happening at the key levels of the 6-9" `[XF p.27 L361]`; Absorption Zone+ features `[XF p.44 L563–568]`.
- Pine VP construction (body / wick weighted bar distribution, 70% VA expansion from POC) `[PINE Sessions & VP with prev session VP & daily weekly opens.txt:216–289]`; `[PINE VP History Widget.txt]`.
- HVN / LVN / shelf / ledge / naked POC `[vp-lesson-2.pdf p.3–9]`; two-sided LVN `[the-math-behind-auction-market-theory.pdf p.12–14]`.
- VWAP ±1/2/2.5/3, session and event anchors `[vwap-lesson-10.pdf p.3–8]`.

## Faithful object
- `value.vp.rth.trade` : profile from NQ trades (aggressor-tagged) 09:30–16:00, 1-tick bins, POC = max-volume bin, VA = 70% expanded from POC alternating sides; prior-day version used at the next open.
- `value.delta.rth.trade`: per-price (aggressive buy − aggressive sell) over the same window; `dp.max`, `dp.min` prices; taper = monotone decline of |delta| into the extreme over the last 10% of the range.
- `value.kz`: HVN = local maxima of the smoothed profile ≥ 1.5 × median bin volume and LVN = local minima ≤ 0.5 × median, each carried as a **band** (the run of adjacent bins meeting the test; the charts draw HVN and LVN as horizontal bands `[VP2 p.3]`) with the peak / trough price as the line variant, plus a **two-sided** LVN variant requiring a supported peak on both sides `[MATH p.12–14]`; ledge = the line where the build-up starts or the fade-away begins, drawn on both sides of the POC ("four ledges around the POC" `[VP2 p.5]`; a sharp volume step ≥ 3× between adjacent 4-tick blocks is the named approximation); shelf = the body between two ledges (text `[VP2 p.4]`) or the thin band at the transition (figures `[VP2 p.4]` `[MATH p.13]`; thickness unprinted, so the touch tolerance is a grid value); naked prior-session POC as its own id until first defined revisit `[VP2 p.3–9]`.
- `env.vwap.eth.sd{1,2}` (faithful) and `env.vwap.rth.sd2`: trade-price VWAP ± volume-weighted SD on both sides, known as-of each minute `[VWAP p.3–8]`; the lesson's settings tab reads Anchor Period = Session with bands #1 = 1 and #2 = 2 ticked and #3 off, and its chart runs the bands through the overnight, so the drawn object is the exchange-session (18:00 ET) VWAP with ±1 / ±2 (`[VWAP p.3, p.8]` figures); the 09:30 anchor and the 2.5 / 3 multipliers are named from the text. HLC3×bar-volume is a named proxy. Not an EV range.

## Upgrades
- `value.vp.rth.ohlc1m` (Pine-style bar distribution) vs trade-level; VA 70 vs 68 vs 40; bin 1 tick vs 4 ticks; scope RTH vs 18:00–16:00 vs overnight-only (for balance / imbalance of the box).
- Developing (intraday) vs completed prior-day profile.
- VWAP anchors: ETH / RTH / fixed-06; dispersion SD / MAD / RMS; bands 1 / 2 / 2.5 / 3 as `env.vwap.rth.sd1`, `env.vwap.rth.sd2.5`, `env.vwap.rth.sd3` beside `env.vwap.rth.sd2` `[VWAP p.3–8]`; swing / event / weekly / monthly anchors → [vwap-anchored](vwap-anchored.md).
- TPO / AMT labels → [tpo-ib-auction](tpo-ib-auction.md), not duplicated here.

## Outcomes
- Grid at VAH / VAL / POC; POC return rate after open outside value (magnet claim); open-location cells feed [open-location-switch](open-location-switch.md).
- Key-zone rows: touch / reject at HVN vs LVN vs POC; absorption-signature reject rate at extreme vs at POC (the coin-flip claim `[ABS p.6]`).
- Faithful disagreements: sessions whose open-location cell differs between `value.vp.rth.trade` and `value.vp.rth.ohlc1m`.

## Links
[open-location-switch](open-location-switch.md) · [absorption-and-big-trades](absorption-and-big-trades.md) · [cvd-variants](cvd-variants.md) · [options-nodes](options-nodes.md) · [tpo-ib-auction](tpo-ib-auction.md)
