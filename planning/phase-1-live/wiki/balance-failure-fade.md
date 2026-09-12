# Failure of aggression in long-gamma balance

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

In long-gamma balance, aggression at an extreme repeatedly goes unpaid; price leaves and returns to that failed area; the aggression remains unpaid. The fade targets where the opposite side previously had control. [BIG] pp.14–15, 18.

**Not a standalone trade.** This branch does not require an own-side aggressive squeeze/reward sequence. It still requires balance, the real extreme, retest, risk and the source objective.

**Record before use.** Long-gamma/balance context, fixed extreme, failed effort, leave/retest events, continued lack of reward and earlier opposite-control target.

**Phase 1 observation.** Require failure < leave < same-area retest ≤ decision with aggression still unpaid. Do not promote a touch without the retest or add the strict absorption-reversal reward gate.

**Current implementation (2026-09-12).** [O129 contract](../FORMULAS.md#o129) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Audit long-gamma balance-extreme failure, departure, same-area retest, and prior opposite-control target without inheriting another branch gate. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/flow_sequences.py).

**Evidence limits.** Each required stage, side, parent band and source qualifier needs its own causal observation. Unpublished author classifications remain source limitations; a missing private stage or attempt record is not replaced by a supplied true flag. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source gamma regime](gex-regime.md) · [Auction balance](auction-balance.md) · [Absorption: effort without price reward](absorption-and-big-trades.md) · [Four-check absorption reversal](absorption-reward-retest.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[BIG]: </workspace/sources/documents/discretionary/only-trade-big-trades.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
