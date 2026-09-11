# Sweep, failure and reclaim

Object in [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

Green Bird shorts after a high is swept and price fails back below, or buys after a low is swept and reclaimed. Selected PDL and Asia/TDO cases explicitly wait for a completed five-minute close. Jumbo's range reversal also needs a sweep/reaction but keeps its own selected block/flow confirmation. [GB] pp.21, 23, 25, 27, 30–35; [TBR] pp.8–11, 27–29.

**Not a standalone trade.** A sweep alone is not confirmation. The five-minute rule from one author/case must not silently become a universal rule for every range reversal.

**Record before use.** Frozen reference, side, sweep extreme/time, confirmation mode and complete bar close, return inside a box when applicable, retest/decision time and structural invalidation.

**Phase 1 observation.** Require reference_known_at ≤ sweep_at < confirm_at ≤ decision_at. If the source uses reclaim/hold without a specified duration, retain that source observation or mark its automatic detector unknown; do not invent a universal 30-minute cap.

**Existing attachments.** [family_fail._failback](/workspace/implementation/src/trading_research/research/phase1_live/family_fail.py); [formulas.reclaim_5m](/workspace/implementation/src/trading_research/research/phase1_live/formulas.py); [grid.failback_wick_c5](/workspace/implementation/src/trading_research/research/phase1_live/grid.py); [FORMULAS] R-G01–G05/G08 and R-J01. Grouping five observed rows and stamping their start is not a clock-aligned five-minute close. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Green Bird's finished session references](session-fail-boxes.md) · [Green Bird's midnight true-day open](true-day-open.md) · [Measured 50–61.8% retracement](golden-pocket.md) · [Jumbo orderblocks](sweep-cisd-blocks.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
