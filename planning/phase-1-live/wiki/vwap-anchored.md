# Anchored VWAP

## Definition
A VWAP started at a moment that mattered rather than at the session start: from a major swing high or low (the average price of everyone who traded since the turn), from an event (CPI, FOMC, an earnings gap, the session open), or from weekly and monthly anchors; when session, weekly and an anchored VWAP converge, that is a heavyweight level `[VWAP p.7]`. The session VWAP and its bands stay on [value-and-profiles](value-and-profiles.md) (`env.vwap.rth.sd*`). Ids `env.vwap.anchored.{swing,event,session,weekly,monthly}`.

## Citations
- Anchor to the swing, anchor to the event, multiple timeframes, convergence `[VWAP p.7]`; VWAP median as the POC of the session so far; bands as premium / discount extremes `[VWAP p.3–4]`; a bulk of balance with VWAP's median through it as context `[BIG p.10]`; longs back toward the session's VWAP after a close above the balance `[CONT p.5]`.
- Event timestamps from the normalized event and release calendars `[INV L552–555, L580, L601–604]`.

## Faithful object
`env.vwap.anchored.swing`: trade-price VWAP from the last confirmed 5-bar fractal swing high (for a falling anchor) or low on 5-minute NQ bars, `known_at` = confirmation bar; `.event` from the timestamp of the last scheduled CPI / FOMC / NFP release; `.session` = the exchange session from 18:00 ET (the lesson's "Session" anchor, `env.vwap.eth`; the 09:30 cash open is the `.event` session-open anchor and `env.vwap.rth` the named RTH row); `.weekly` from Sunday 18:00; `.monthly` from the first session's 18:00. Convergence flag = ≥ 2 anchored VWAPs within `tR`.

## Upgrades
- HLC3 × bar-volume proxy; ±1 / 2 SD bands on each anchor; anchor at the 6–9 open or the 03:00 London analog.

## Outcomes
- Grid at each anchored VWAP; reject rate at convergences vs single anchors; coincidence with `value.kz` ledges and prior VA edges.

## Links
[value-and-profiles](value-and-profiles.md) · [dealing-range](dealing-range.md) · [absorption-and-big-trades](absorption-and-big-trades.md)
