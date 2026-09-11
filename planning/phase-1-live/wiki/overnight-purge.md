# Chronological liquidity purges

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

In the purged single-break case, the overnight auction has already taken relevant earlier highs/lows before the later expansion decision. Later source settings keep named session and prior-day liquidity references and can retire them after use. [TBR] pp.11–15; [JR] pp.16–18, 33–39.

**Not a standalone trade.** Containment of two completed boxes does not prove when liquidity was taken. The RTH-only destination application deliberately has a different consumption scope.

**Record before use.** Reference_id and session scope, formation/known_at, first qualifying sweep_at, side, active/retired state and the decision using that state.

**Phase 1 observation.** For purged context, the relevant sweep must precede the entry decision. Do not retire the RTH-only objective because of an ETH sweep, and do not use a later day's first hit to rewrite earlier state.

**Existing attachments.** [sessions._purged](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py); family_levels; [formulas_jumbo.j10_draw](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [FORMULAS] R-J04/J10/J19. A persistent source-scoped consumption ledger is missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Remaining auction objectives](unfinished-business.md) · [PD RTH Range+ destinations](pd-rth-range-plus.md) · [Overnight high, low and width](overnight-range.md) · [Range width and expectations](range-width-context.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
