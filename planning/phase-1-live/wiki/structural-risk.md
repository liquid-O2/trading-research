# Entry-side structural invalidation

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — VWAP continuation](method-green-bird-vwap-continuation.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md).

Where the source supplies it, controlling structure determines invalidation before size is chosen. Sires explicitly works from stop structure to account risk and real HTF objective; Jumbo and Green Bird keep case-specific block/swing stops. Some cases disclose only an example distance or an incomplete rule. [ANAT] pp.8–10; [TBR] pp.27–29; [GB] pp.25, 31–34, 40; [TRAP] pp.8–10; [K10] pp.7–9; [AVG] pp.21–22.

**Not a standalone trade.** An attractive R:R does not justify inventing a structure. A ticket's 30-point stop or a screenshot boundary is not a universal stop for that method.

**Record before use.** Candidate/entry side, source controlling band/extreme, invalidation rule and known_at, order versus drawn ticket, entry price, tick distance and unresolved source policy.

**Phase 1 observation.** Risk must be defined before decision. Keep wick versus close invalidation and actual source stop identity explicit; missing general stop rules remain unknown rather than borrowing another case.

**Existing attachments.** [formulas_jumbo.j18_ob_bull/j18_ob_bear](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [formulas_flow.r_s01_refill_long/r_s01_refill_short/r_s07_areas](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-J18/R-S01/R-S07 and GB ingredients. Complete source-linked risk records are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Exposure fitted to source risk constraints](position-sizing.md) · [Objective selected before entry](trade-objective.md) · [Confirmed protected high or low](protected-high-low.md) · [Source-selected position management](position-management.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[ANAT]: </workspace/sources/documents/discretionary/anatomy-of-a-losing-start.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[K10]: </workspace/sources/documents/discretionary/10k-first-month.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
