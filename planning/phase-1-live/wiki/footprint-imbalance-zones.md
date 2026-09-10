# Footprint imbalance zones (stacked diagonal, same-price 350%)

## Definition
Two footprint objects used as locations. A stacked imbalance: three or more diagonal imbalances in a row build an unfinished auction the market tends to return to and finish, a demand zone (stacked buying) or a supply zone (stacked selling) `[FP8 p.6]`. A same-price imbalance line: a price where one side traded 350% more than the other, interesting only where it sits at the same price as an aggression print; the level is marked as a small box around that print's candle with the line running off it and price is expected to come back and retest it `[BIG p.3, p.5]` (figures); the buy mirror (buyers 350% over sellers at a buy print) is the same object; the same 350% divergence with a small imbalance prints as a box in a live session `[K2345 p.5]`. Ids `flow.footprint.stack3`, `flow.footprint.imb350`. The single diagonal ratio `flow.footprint.diag.4x` stays on [absorption-and-big-trades](absorption-and-big-trades.md).

## Citations
- Diagonal read, 3× to 4× flag `[FP8 p.4–5]`; stacked imbalances, three or more, unfinished business `[FP8 p.6–7]`; same-price 350% and the pairing with aggression `[BIG p.5, p.18]`; 350% divergence box as the flag that fired `[K2345 p.5]`; Jumbo's footprint filtered to the top 35% of transactions `[XF p.23]`.

## Faithful object
`flow.footprint.stack3`: within one 1-minute NQ candle, ≥ 3 consecutive price rows with ask(p) / bid(p − tick) ≥ 4 (buy stack) or bid(p) / ask(p + tick) ≥ 4 (sell stack); zone = price span of the stack; `known_at` = candle close. `flow.footprint.imb350`: a price where ask volume ≥ 3.5 × bid volume (or the reverse) inside one candle and a print ≥ the `flow.bigtrade.100ny` threshold traded at that price; a line until first revisit (the live tool prints it as a box a few points tall `[K2345 p.5]`; box height = the price span of the rows meeting the condition, named; the line is the reduced form). `[unmeasured]` tape objects.

## Upgrades
- 3× ratio; stack of 2 ("two or three in a row at a level" `[FP8 p.7]`); candle 5-minute or 40-tick range bars; top-35%-of-transactions filter; threshold 30–60 for the aggression pairing; box variant for `imb350` = the print's candle body or range as the area (drawn, size unprinted).

## Outcomes
- Revisit rate; hold vs slice on revisit; overlap with `flow.absorption.A` and `flow.refill.zone` (must not be identical); count per session.

## Links
[absorption-and-big-trades](absorption-and-big-trades.md) · [candle-poc-flip](candle-poc-flip.md) · [ofm-catalyst](ofm-catalyst.md) · [refill-zone](refill-zone.md)
