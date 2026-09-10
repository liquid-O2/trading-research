# Reward system (3-tick confirmation after absorption)

## Definition
The confirmation Ethos requires after an absorption print before it counts: price moves in your direction within three ticks of the absorption, with the time and sales or speed of tape showing the opposing side not being refreshed; without it roughly 27% of absorptions fail `[ABS p.3–4]` `[AVG p.24]`. Enter on the test of the reward system, not on the wall itself `[ABS p.9]`. The STOP version: effort is what the losing side shows, reward is what the winning side gets; two upticks minimum, two to four, and an entry six to eight ticks late means probably no reward system `[STOP p.7, p.12–13]`. Id `flow.reward.3tick`.

## Citations
- 27% failure without a reward system; the three-tick rule read on time and sales, speed of tape or CVD `[ABS p.3–5, p.13]`; the retest of the reward system as the entry `[ABS p.9]`; reward vs result, 18-tick median dip `[STOP p.7]`; upticks 2–4, entry within a tick or two `[STOP p.12, p.14]`; delayed reward `[STOP p.13]`; 3-tick aggression toward the absorbed side or fails 27% `[AVG p.24, p.28–29]`.
- The 27% figure is the presenter's own record, not an audited statistic `[ABS p.14]` `[STOP p.16]`.

## Faithful object
`flow.reward.3tick`: after a `flow.absorption.A` event at price P with absorbed side A, reward = the first ≥ 3-tick displacement against A that starts within 3 ticks of P, within 5 minutes (named), while A's aggressive prints in that span are smaller than in the absorption window (no refresh; see [digit-thinning](digit-thinning.md)); late reward = a qualifying displacement that starts 6–8 ticks from P, counted as none. `[unmeasured]` tape object.

## Upgrades
- 2 / 4 ticks; window 2 / 10 min; uptick count 2–4 (STOP) instead of tick distance; CVD-median side as a named add once CVD is rebuilt ([cvd-variants](cvd-variants.md)).

## Outcomes
- Share of absorption events with a reward (recompute of the 27% claim as its complement); reversal ≥ 0.25·R given reward vs none; late-reward outcome row.

## Links
[absorption-and-big-trades](absorption-and-big-trades.md) · [digit-thinning](digit-thinning.md) · [delta-spike](delta-spike.md) · [tape-speed](tape-speed.md)
