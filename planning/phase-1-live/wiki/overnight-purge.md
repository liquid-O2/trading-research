# Chronological liquidity purges

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

In the purged single-break case, the overnight auction has already taken relevant earlier highs/lows before the later expansion decision. Later source settings keep named session and prior-day liquidity references and can retire them after use. [TBR] pp.11–15; [JR] pp.16–18, 33–39.

**Not a standalone trade.** Containment of two completed boxes does not prove when liquidity was taken. The RTH-only destination application deliberately has a different consumption scope.

**Record before use.** Reference_id and session scope, formation/known_at, first qualifying sweep_at, side, active/retired state and the decision using that state.

**Phase 1 observation.** For purged context, the relevant sweep must precede the entry decision. Do not retire the RTH-only objective because of an ETH sweep, and do not use a later day's first hit to rewrite earlier state.

**Current implementation (2026-09-12).** [O012 contract](../FORMULAS.md#o012) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Retire a selected liquidity reference only after an ordered qualifying native visit in the declared consumption scope. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** The visit rule and consumption scope are source policy; absent policy keeps retirement unknown. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Remaining auction objectives](unfinished-business.md) · [PD RTH Range+ destinations](pd-rth-range-plus.md) · [Overnight high, low and width](overnight-range.md) · [Range width and expectations](range-width-context.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
