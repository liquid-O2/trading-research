# 09:30 cash-open price

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Keani — open above value](method-keani-open-above-value.md).

The cash-open price anchors the opening read. Green Bird's September 1 example describes a move below the open, reclaim and long; it is a 09:30 manipulation branch, not an already finished 9–10 box. Sires's open-drive read asks whether price crosses back through this open. [GB] p.40; [TBR] pp.8–10; [AMT1] p.11; [AVG] pp.21–22.

**Not a standalone trade.** A move through the open does not automatically qualify a trade. A partial early-session example cannot borrow a later box's final high/low.

**Record before use.** Opening price/time, instrument, available_at, below/above excursions and returns, source branch and actual confirmation duration.

**Phase 1 observation.** Keep source-specific direction and timing. Do not fabricate a short mirror of a one-sided example or force an unstated five-minute duration onto it.

**Existing attachments.** family_open; family_levels; [FORMULAS] R-G04, R-J02, R-A10 and R-S09. Green Bird's exact opening confirmation detector remains incomplete. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Opening location and participation](open-location-switch.md) · [Developing auction open type](open-type.md) · [Green Bird's finished session references](session-fail-boxes.md) · [Green Bird's midnight true-day open](true-day-open.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
