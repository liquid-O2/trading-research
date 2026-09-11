# PD RTH Range+ destinations

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The RTH-only application uses prior 09:30–16:00 highs/lows and M15/H1 imbalances, waits for current RTH direction and then pursues the named objective within the range framework. An ETH sweep does not consume this expressly RTH-only objective. [TBR] pp.32–35.

**Not a standalone trade.** Prior extremes and gaps are context/destinations, not an entry on contact or a separate system. This scope does not erase overnight purge information in another branch.

**Record before use.** Prior RTH range ID, high/low, named imbalance timeframe/bounds, known_at, consumption scope, observed current direction and selected destination.

**Phase 1 observation.** Direction and target must be selected before entry. Measure subsequent destination reach in the declared RTH scope; preserve ETH hits separately.

**Existing attachments.** [formulas_jumbo.j19_draw/j19_pd_touch/j19_htf_fvg](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); family_levels; [FORMULAS] R-J19. Final morning direction or reach cannot establish an earlier setup. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Prior-session auction landmarks](prior-session-reference-levels.md) · [Fair-value gaps and higher-timeframe imbalances](fvg-body-gaps.md) · [Chronological liquidity purges](overnight-purge.md) · [Remaining auction objectives](unfinished-business.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
