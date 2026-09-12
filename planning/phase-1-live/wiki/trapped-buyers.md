# Trapped aggression at an auction extreme

Object in [Saint — AMT on live markets](method-saint-amt.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Saint's short example shows aggressive buying at an upper HTF extreme repeatedly failing, then requires current intraday break/retest and repeated body selling for entry. Two prior AM/PM failures support the thesis; they do not replace today's confirmation. Sires also distinguishes trapped participation from a responsive absorption fade. [TRAP] pp.3–10; [WIC] pp.4–10; [AVG] p.19.

**Not a standalone trade.** Large positive delta or one failed push is not the full short. A generic trapped-trader pattern does not merge the authors' methods.

**Record before use.** Fixed HTF area, buying/price-response evidence, distinct prior failures and known times, current LTF break/retest, repeated body aggression and decision.

**Phase 1 observation.** Do not duplicate today's AM high to create two failures. If buyers instead take and defend the area, the current read must change before any new trade. A short mirror is not assumed without evidence.

**Current implementation (2026-09-12).** [O119 contract](../FORMULAS.md#o119) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Require two distinct prior failed pushes known before the current test and keep current body-selling evidence separate. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Local delta concentration at an extreme](delta-spike.md) · [Higher- and lower-timeframe control alignment](htf-ltf-alignment.md) · [Accepted break and defended boundary retest](break-retest.md) · [Executed aggressor-side trades](aggressor-trades.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[WIC]: </workspace/sources/documents/discretionary/whos-in-control.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
