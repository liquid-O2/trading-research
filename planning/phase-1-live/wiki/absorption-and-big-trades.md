# Absorption: effort without price reward

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

Absorption requires aggressive effort making little progress against liquidity that actually holds/replenishes. The ensuing action depends on the branch: Sires's strict reversal additionally needs own-side reward and a defended reward retest, while his long-gamma balance fade does not require that reward sequence. [ABS] pp.5–13; [BIG] pp.14–15; [MATH] pp.6–8. Jumbo also describes absorption in his footprint/range read, without publishing the complete detector used there. [JR] pp.48–50. The member case records buyers absorbing and holding on the planned return; it does not publish the same four-check entry gate. [K10] pp.7–8.

**Not a standalone trade.** Large volume alone is not absorption; absorption alone is not every method's entry. Jumbo's small-body candle is a separate candle proxy.

**Record before use.** Band/price, aggressor side and volume, price-response interval, opposing passive evidence, replenishment, known times and selected branch.

**Phase 1 observation.** Evaluate effort and response locally, before the decision. Preserve missing passive evidence; do not use the future reversal itself as proof of the earlier entry prerequisite.

**Current implementation (2026-09-12).** [O101 contract](../FORMULAS.md#o101) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Keep aggressive effort, price response, passive defense, and source absorption as separate evidence; later decline cannot repair missing passive proof. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Executed passive replenishment](passive-replenishment.md) · [Aggressive effort versus price-response efficiency](response-efficiency.md) · [Four-check absorption reversal](absorption-reward-retest.md) · [Failure of aggression in long-gamma balance](balance-failure-fade.md) · [Jumbo Absorption Zone+ candle](absorption-candle-jumbo.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[ABS]: </workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>
[BIG]: </workspace/sources/documents/discretionary/only-trade-big-trades.pdf>
[K10]: </workspace/sources/documents/discretionary/10k-first-month.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
