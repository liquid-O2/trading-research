# SessionStat+ 9–12 envelope

## Definition
SessionStat+ draws average and median session highs and lows over a lookback, "minimum average" levels, and projections that extend the average range `[SS p.3 L24–39, p.6 L83–89]`. Key sessions: 09:00–12:00 New York AM high/low and 09:30–16:00 RTH `[SS p.9 L147, p.10 L151–159]`. Jumbo uses the 9–12 boundaries as extremity confluence with range exhaustion levels; compatible with the EV range but a different object `[PACK L83]` `[FIND p.5 L104]`.

## Citations
- Two average types plus median; minimum-average levels `[SS p.4–5 L58–71, p.6]`; sessions are midnight-bounded, use 23:59 for overnight `[SS p.8 L123–141]`; timeframes below 2 minutes by design `[SS p.7 L94]`; failure potential in choppy and low-volatility markets `[SS p.11 L178–216]`.
- "range exhaustion levels and 9–12 statistical session boundaries both meeting up" (6 Jul 2026) `[FIND p.5 L104]`; "average time of reversal in the 9–12 time window over 15 years" `[XF p.47 L624]`; London H4 stats + absorption zone at the reversal `[FIND p.4 L89–90]`.
- Pine restatements: pre-market 06:00–09:00 levels with 09:00–12:00 stats, σ-levels, fib 0.236/0.382/0.618, per-weekday first-hit counts `[PINE Pre-market session levels and stats.txt]` and `[PINE session_statmap]`; Session Statistical Levels percentile bands P10–P90 `[PINE Session Statistical Levels.txt]`.

## Faithful object
`env.ss.avgHL60`: session open at 09:00; upper = open + mean(H − open), lower = open − mean(open − L) over the prior 60 sessions of the 09:00–12:00 window. `env.ss.medHL60` uses medians. `env.ss.minavg60`: the manual says only "the minimum average of the session, which reflects price movements of shorter swings" `[SS p.6]` and prints no formula; two named readings, no default: (a) the average of the lower half of the excursions, (b) min(mean up-excursion, mean down-excursion) applied to both sides (the retained code). Neither is the source's formula. Projection rows extend by one average range beyond each level `[SS p.6 L89]`.

## Upgrades
- Lookback 20 / 60 / 250; weighted average variant `[SS p.3 L28]`; per-weekday variant `[PINE Pre-market session levels and stats.txt]`.
- Anchor 09:00 open (faithful) vs 09:30 open (comparison with EV rows).
- Session 09:30–16:00 RTH high / low as its own row `env.ss.rth.avgHL60` (medians and minimum-average likewise) `[SS p.10]`.

## Outcomes
Same table as [ev-range-expected-move](ev-range-expected-move.md): reach, overshoot, reject, time-to-touch, in/out of prior value; coincidence counts with 1.33 / 1.66 and −0.5 projections; calibration by vol tercile (his choppy / low-vol failure claim `[SS p.11]`).

## Links
[ev-range-expected-move](ev-range-expected-move.md) · [extensions-1-33-1-66](extensions-1-33-1-66.md) · [clock-grid-and-bars](clock-grid-and-bars.md)
