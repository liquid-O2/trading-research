# Entry-side structural invalidation

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — VWAP continuation](method-green-bird-vwap-continuation.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md).

Where the source supplies it, controlling structure determines invalidation before size is chosen. Sires explicitly works from stop structure to account risk and real HTF objective; Jumbo and Green Bird keep case-specific block/swing stops. Some cases disclose only an example distance or an incomplete rule. [ANAT] pp.8–10; [TBR] pp.27–29; [GB] pp.25, 31–34, 40; [TRAP] pp.8–10; [K10] pp.7–9; [AVG] pp.21–22.

**Not a standalone trade.** An attractive R:R does not justify inventing a structure. A ticket's 30-point stop or a screenshot boundary is not a universal stop for that method.

**Record before use.** Candidate/entry side, source controlling band/extreme, invalidation rule and known_at, order versus drawn ticket, entry price, tick distance and unresolved source policy.

**Phase 1 observation.** Risk must be defined before decision. Keep wick versus close invalidation and actual source stop identity explicit; missing general stop rules remain unknown rather than borrowing another case.

**Current implementation (2026-09-12).** [O139 contract](../FORMULAS.md#o139) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Bind the planned stop to the actual selected invalidation reference, side, method, clock, tick size, and adverse-side price comparison. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py).

**Evidence limits.** Actual thesis, instruction, fill, management, account or state records are required for a historical instance. Scoped source policies and supplied interpretations cannot manufacture missing private records or a contemporaneous cohort. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Exposure fitted to source risk constraints](position-sizing.md) · [Objective selected before entry](trade-objective.md) · [Confirmed protected high or low](protected-high-low.md) · [Source-selected position management](position-management.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[ANAT]: </workspace/sources/documents/discretionary/anatomy-of-a-losing-start.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[K10]: </workspace/sources/documents/discretionary/10k-first-month.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>


### September 12 source binding

**Scoped excursion research record (2026-09-12):** [C2] p.4 recommends collecting 40–80 trades before inspecting MFE/MAE distributions. Keep original entry/exit or observation-end windows, price units, long/short direction, native coverage and censoring in O146/O153 research records. Collect all observed outcomes. Stop/target optimization remains deferred; this count is not a universal validation threshold.

[C2]: </workspace/sources/documents/discretionary/code-2-risk.pdf>
