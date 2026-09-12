# Green Bird's directional read

Object in [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — VWAP continuation](method-green-bird-vwap-continuation.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md).

A prior day/week/month or session reclaim can establish direction for later aligned trades; the explicit VWAP continuation instead follows a close above both session highs. The smaller scalp posts retain a directional read with limited ambition. [GB] pp.25, 31–35, 40.

**Not a standalone trade.** A directional opinion is not an entry, and a later NYAM sweep is not required to explain a separately cited earlier prior-level reclaim.

**Record before use.** Source reference/context, side, start/known_at, supporting reclaim or break, source change-of-view evidence and linked candidates.

**Phase 1 observation.** Direction must be recorded before entry; do not derive it from the eventual profitable side. The scalp trigger and complete invalidation algorithm remain unpublished.

**Current implementation (2026-09-12).** [O136 contract](../FORMULAS.md#o136) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Bind directional bias to a dated support/origin identity and candidate side; later events cannot explain an earlier bias. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/flow_sequences.py).

**Evidence limits.** Each required stage, side, parent band and source qualifier needs its own causal observation. Unpublished author classifications remain source limitations; a missing private stage or attempt record is not replaced by a supplied true flag. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Prior day, week and month extremes](prior-day-week-month-levels.md) · [Sweep, failure and reclaim](sweep-reclaim.md) · [Green Bird's finished session references](session-fail-boxes.md) · [Source setup quality and exposure](quality-grade.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
