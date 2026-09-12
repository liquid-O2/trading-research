# Late small resistance-fade case

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The later NYAM case describes a premarked resistance area, upward approach losing aggression candle by candle, a small short near the session objective and ending the session. [NYAM] pp.10–11.

**Not a standalone trade.** The example does not publish a universal exhaustion threshold or complete automatic fade rule. Caption shorthand cannot override the actual direction of the chart sequence.

**Record before use.** Premarked resistance, approach/candle sequence, observed participation loss, side/entry time, small-risk choice and session end.

**Phase 1 observation.** Retain the observed case and its uncertainty. Do not relabel a generic later high or final-session reversal as this entry, or force the strict reward-retest branch onto it.

**Current implementation (2026-09-12).** [O135 contract](../FORMULAS.md#o135) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Require resistance marked before entry, an upward approach, source exhaustion, short side, and explicit small risk; selector remains unknown. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/flow_sequences.py).

**Evidence limits.** Each required stage, side, parent band and source qualifier needs its own causal observation. Unpublished author classifications remain source limitations; a missing private stage or attempt record is not replaced by a supplied true flag. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [How price arrives at the area](approach-speed.md) · [Speed of tape](tape-speed.md) · [Source setup quality and exposure](quality-grade.md) · [Source-selected position management](position-management.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[NYAM]: </workspace/sources/documents/discretionary/ny-am-session.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
