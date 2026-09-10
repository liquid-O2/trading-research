# Speed of tape

## Definition
How fast prints are hitting: a tape that rips at a level is urgency arriving, a tape that freezes is hesitation or a big passive order soaking everything up; fast tape into a level that still holds is absorption worth trading, and if it breaks the speed carries the continuation `[DOM5 p.6]`. It spikes when a squeeze releases and dies when one fails passively `[OFM p.2, p.5, p.14]`; a jump in speed at a level says the level is being contested `[ANAT p.3]`. Ethos reads only CVD and speed of tape as indicators `[NYAM p.3]` `[K18 p.3]`. Id `flow.tape.speed`.

## Citations
- Speed of tape and the spread `[DOM5 p.6]`; squeeze release / passive failure `[OFM p.2, p.5, p.14]`; contested level `[ANAT p.3]`; the read stack `[NYAM p.3]` `[K18 p.3, p.8]`.

## Faithful object
`flow.tape.speed`: NQ trade events per second and lots per second from MBP-1, rolling 5-second and 30-second windows; spike = window rate ≥ q90 of the session so far, death = ≤ q10; sampled at first touch of a level and over the 60 seconds after a `b.c1` break. `[unmeasured]` tape object.

## Upgrades
- Windows 1 / 10 / 60 s; per-side rate; normalized by the time-of-day median across the prior 20 sessions.

## Outcomes
- Hold vs break at a level given a fast arrival vs a slow one; release detection agreement with the OFM stages on [ofm-catalyst](ofm-catalyst.md); speed after breaks that hold vs fail back.

## Links
[spread-width](spread-width.md) · [approach-speed](approach-speed.md) · [ofm-catalyst](ofm-catalyst.md) · [absorption-and-big-trades](absorption-and-big-trades.md)
