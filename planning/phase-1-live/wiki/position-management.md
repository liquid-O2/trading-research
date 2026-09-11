# Source-selected position management

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — VWAP continuation](method-green-bird-vwap-continuation.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md).

Management follows the entry and the chosen source policy: static objectives, partials, breakeven, trailing or justified additions. Sires distinguishes account-dependent exit policies; NYAM shows target expansion as well as trailing, with the original risk box still drawn. [C2] pp.3–7; [C3] p.4; [NYAM] pp.8–9; [K18] pp.8–14; [TBR] pp.24, 36–37; [GB] pp.30–40; [REF] p.12.

**Not a standalone trade.** Management is not another entry system, and a later stop/target adjustment cannot rewrite the original ticket. No universal algorithm is inferred where the source gives only a case.

**Record before use.** Entry_id, initial stop/target and policy, each action/time, known supporting structure, partial size, exposure before/after and exit reason.

**Phase 1 observation.** Require action after entry and supporting evidence known by that action. Trail only confirmed structure when that policy requires it; add risk only after earlier risk is secured. Whole-AM excursions are not post-entry management evidence.

**Existing attachments.** [formulas_jumbo.j24_management](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [formulas_flow.r_f10_protected_low](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py) and related R-S helpers; [FORMULAS] R-J24/R-F10/R-S01/S05/S07. Complete action and position-exposure ledgers are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Confirmed protected high or low](protected-high-low.md) · [Objective selected before entry](trade-objective.md) · [Exposure fitted to source risk constraints](position-sizing.md) · [Observed order lifecycle](order-lifecycle.md) · [Freshly qualified re-entry](reentry.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[C2]: </workspace/sources/documents/discretionary/code-2-risk.pdf>
[C3]: </workspace/sources/documents/discretionary/code-3-orderflow.pdf>
[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[NYAM]: </workspace/sources/documents/discretionary/ny-am-session.pdf>
[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
