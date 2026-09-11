# Price-defined microbalance continuation

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Inside the larger directional auction a small price balance forms, then strength breaks it in the thesis direction. The opposite side supplies structural risk; the pre-existing HTF objective remains the destination and later protected structure guides management. [K2345] pp.4–7.

**Not a standalone trade.** The microbalance is an execution structure in the wider thesis, not a standalone opening-range system.

**Record before use.** Microbalance_id/bounds, formation end/known_at, larger thesis, strength/breakout evidence, entry, stop behind structure and pre-existing objective.

**Phase 1 observation.** Freeze the actual small balance before its break. Do not select a later winning box or replace it with a fixed clock box; qualification requires the parent auction/thesis gates.

**Existing attachments.** [formulas_flow.r_s05_microbalance](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-S05. Current price-run detection can retain the last box and final-AM close instead of the source episode. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Auction balance](auction-balance.md) · [Thesis, validity band and death condition](thesis-lifecycle.md) · [Entry-side structural invalidation](structural-risk.md) · [Confirmed protected high or low](protected-high-low.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[K2345]: </workspace/sources/documents/discretionary/2345-funded-session.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
