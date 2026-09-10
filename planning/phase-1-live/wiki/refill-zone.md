# Refill zone (level built by large aggressive prints)

## Definition
A price area where a burst of large aggressive market orders traded, sixty, eighty, a hundred contracts hitting in seconds; somebody with size chose to fight there. When price returns, the only question is whether the defenders are still there `[REF p.5]`. Everything that defines the zone is known before the next touch: print sizes, width, location in the session's structure, whether it held an earlier touch `[REF p.6]`. Id `flow.refill.zone` (the location). The touch event `flow.refill.ontouch` stays on [absorption-and-big-trades](absorption-and-big-trades.md).

## Citations
- Zone definition and the two outcomes of a touch `[REF p.5]`; measurable before the fact `[REF p.6]`; level built early and tested twice `[REF p.7]`; feature families memory / construction / location / flow, 42% of touches hold `[REF p.8]`; memory and location carry the signal, flow alone AUC 0.54 `[REF p.9]`; median winner dips 18 ticks past the touch `[REF p.10]`; deployed configuration 12 ticks inside, stop 32, target 96, cancel 30 min `[REF p.12]`; stat sheet `[REF p.23]`.
- Refill area where sellers previously failed `[BIG p.8]`; refill zone = the same side winning the argument more than once `[CONT p.8]`; refill clock `[OFM p.2, p.5]`.

## Faithful object
`flow.refill.zone`: a cluster of ≥ 3 aggressive prints on the same side, each ≥ 60 lots (80 and 100 named; 100 = Jumbo's NY BigTrades threshold), within 30 seconds; bounds = min / max trade price of the cluster; `known_at` = last print. Per later touch, frozen features: memory (held earlier this session, defended on the prior day), construction (print count, total size, width), location (distance to prior VA edges, session extremes, the open), flow (delta into the touch, [approach-speed](approach-speed.md)). `[unmeasured]` tape object.

## Upgrades
- Size 80 / 100; cluster window 10 / 60 s; merge zones overlapping by ≥ 50%; prior-day memory on / off.

## Outcomes
- Hold rate per touch (42% base), by memory decile; penetration depth distribution (18-tick median claim); time in zone; no execution or P&L rows (the PF 1.80 vs 0.81 claim is an execution effect, recorded as depth outcomes only).

## Links
[absorption-and-big-trades](absorption-and-big-trades.md) · [ofm-catalyst](ofm-catalyst.md) · [approach-speed](approach-speed.md) · [dealing-range](dealing-range.md)
