# Equal-high or equal-low liquidity objective

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The extension-reaction example points toward still-owed equal highs after the source location produces a long reaction. Repeated prices are a destination only when the source selects them. [JR] pp.23–26.

**Not a standalone trade.** Repeated-looking highs do not by themselves create an entry or a guaranteed liquidity run.

**Record before use.** Source reference points/band, side, tolerance if specified, all contributing times and known_at, source objective selection and later visit.

**Phase 1 observation.** Identify the objective before entry and retain an unspecified equality tolerance as unresolved or named. Do not choose whichever later double top/bottom makes the target look successful.

**Existing attachments.** family_levels and [formulas_jumbo.j10_draw](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py) are related; [FORMULAS] R-J10. Source-exact equality tolerance and target-selection ledger are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Remaining auction objectives](unfinished-business.md) · [Objective selected before entry](trade-objective.md) · [The 1.33–1.66 extension area](extensions-1-33-1-66.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
