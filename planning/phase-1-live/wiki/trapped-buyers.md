# Trapped aggression at an auction extreme

Object in [Saint — AMT on live markets](method-saint-amt.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Saint's short example shows aggressive buying at an upper HTF extreme repeatedly failing, then requires current intraday break/retest and repeated body selling for entry. Two prior AM/PM failures support the thesis; they do not replace today's confirmation. Sires also distinguishes trapped participation from a responsive absorption fade. [TRAP] pp.3–10; [WIC] pp.4–10; [AVG] p.19.

**Not a standalone trade.** Large positive delta or one failed push is not the full short. A generic trapped-trader pattern does not merge the authors' methods.

**Record before use.** Fixed HTF area, buying/price-response evidence, distinct prior failures and known times, current LTF break/retest, repeated body aggression and decision.

**Phase 1 observation.** Do not duplicate today's AM high to create two failures. If buyers instead take and defend the area, the current read must change before any new trade. A short mirror is not assumed without evidence.

**Existing attachments.** [formulas_flow.r_f13_trapped_buyers](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-F13. Local concentration, separate historical attempts and same-boundary current confirmation are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Local delta concentration at an extreme](delta-spike.md) · [Higher- and lower-timeframe control alignment](htf-ltf-alignment.md) · [Accepted break and defended boundary retest](break-retest.md) · [Executed aggressor-side trades](aggressor-trades.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[WIC]: </workspace/sources/documents/discretionary/whos-in-control.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
