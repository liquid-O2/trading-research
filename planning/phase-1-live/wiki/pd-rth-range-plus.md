# PD RTH Range+ destinations

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The RTH-only application uses prior 09:30–16:00 highs/lows and M15/H1 imbalances, waits for current RTH direction and then pursues the named objective within the range framework. An ETH sweep does not consume this expressly RTH-only objective. [TBR] pp.32–35.

**Not a standalone trade.** Prior extremes and gaps are context/destinations, not an entry on contact or a separate system. This scope does not erase overnight purge information in another branch.

**Record before use.** Prior RTH range ID, high/low, named imbalance timeframe/bounds, known_at, consumption scope, observed current direction and selected destination.

**Phase 1 observation.** Direction and target must be selected before entry. Measure subsequent destination reach in the declared RTH scope; preserve ETH hits separately.

**Current implementation (2026-09-12).** [O020 contract](../FORMULAS.md#o020) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure the prior RTH range from the exact 09:30-16:00 ET native window and retain destination/context fields as separate source information. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Native range geometry is available; source destination selection and directional draw remain separate qualitative evidence. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Prior-session auction landmarks](prior-session-reference-levels.md) · [Fair-value gaps and higher-timeframe imbalances](fvg-body-gaps.md) · [Chronological liquidity purges](overnight-purge.md) · [Remaining auction objectives](unfinished-business.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
