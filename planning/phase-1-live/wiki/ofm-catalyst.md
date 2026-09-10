# OFM catalyst (squeeze catalyst)

## Definition
The cluster of absorbed aggression that sets a squeeze up, drawn at the lowest (or highest) first aggression `[OFM p.2, p.5]`: buyers hit the market repeatedly and get absorbed at the same area; every failed order is still there waiting to reload (the refill clock) `[OFM p.5]`. The origin of the move is the trade on the other side of the first squeeze's failure: release, failure back through the catalyst, refill, then the re-squeeze entered on the retest `[OFM p.6]`. Id `flow.ofm.catalyst` (the location); the stage sequence `flow.ofm.sequence` stays on [absorption-and-big-trades](absorption-and-big-trades.md).

## Citations
- Language: catalyst, refill clock, squeeze, OFM `[OFM p.2]`; aggression on the wick = absorbed, in the body = paid `[OFM p.4]` `[BIG p.6]`; squeeze and refill clock `[OFM p.5]`; full sequence, entries and the stop below the aggression `[OFM p.6]`; examples with the catalyst drawn at the lowest aggression `[OFM p.7–10]`; no short until price reclaims above the catalyst and fails again `[OFM p.11]`; passive variant `[OFM p.14]`.
- The failure of the squeeze is not the entry; the drive is `[BIG p.7–8]`; OFM retaken after a failed squeeze; a squeeze with no failure is a different case `[CONT p.10–11]`.

## Faithful object
`flow.ofm.catalyst`: ≥ 2 same-side aggressive prints ≥ 30 lots (Ethos 30–60 on NQ; 100 named) whose fill price sits in the wick of their 1-minute bar (absorbed), within 5 minutes and within 0.1·R of a swing extreme (the 5-minute window and 0.1·R are named; the 30-lot minimum is printed `[OFM p.4]`); box = from the first absorbed print to the extreme; `known_at` = close of the bar after the last print. Stage flags: release (1-minute close beyond the extreme with a `flow.tape.speed` spike), failure (`b.c1` back through the catalyst), refill (return into the box), re-squeeze (retest of the failure area then `b.c1` in the squeeze direction). `[unmeasured]` tape object.

## Upgrades
- Print threshold 60 / 100; wick vs body classification by fill price vs bar body; window 3 / 10 min; passive variant (release with tape speed at or below the session median).

## Outcomes
- Stage-transition counts; share of catalysts whose failure is followed by a retest; continuation after the re-squeeze; overlap with `flow.refill.zone`.

## Links
[absorption-and-big-trades](absorption-and-big-trades.md) · [refill-zone](refill-zone.md) · [tape-speed](tape-speed.md) · [footprint-imbalance-zones](footprint-imbalance-zones.md)
