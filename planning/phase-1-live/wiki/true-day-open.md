# Green Bird's midnight true-day open

Object in [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md).

TDO is the midnight opening price used as confluence, reclaim confirmation or destination. It is not an instruction to sell simply because price is above it. Some Asia examples combine their failure with a close through TDO; that requirement belongs to that selected case. [GB] pp.21, 27, 30–33, 38.

**Not a standalone trade.** A TDO touch is not a complete trade, and TDO is not a universal extra AND condition for every Green Bird failure.

**Record before use.** Date/timezone, midnight price and known_at, reference_id, role in this case, required confirmation if any and target identity.

**Phase 1 observation.** Distinguish the midnight open from an 18:00 session open, range open or 09:30 cash open. When TDO is required, its relevant close must be complete before entry.

**Current implementation (2026-09-12).** [O049 contract](../FORMULAS.md#o049) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Resolve the midnight true-day-open from the first causally ordered execution and evaluate any required close-through only from an actual complete five-minute bar. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Tied first executions without unique sequence leave the opening price unknown; close-through requires an actual five-minute bar. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Green Bird's finished session references](session-fail-boxes.md) · [Sweep, failure and reclaim](sweep-reclaim.md) · [09:30 cash-open price](cash-open-reference.md) · [New-week opening gap](new-week-opening-gap.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
