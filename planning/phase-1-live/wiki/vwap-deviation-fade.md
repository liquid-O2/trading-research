# Confirmed VWAP deviation fade

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

In an appropriate auction context, price reaches the selected source VWAP deviation; absorption/rejection plus CVD and ladder confirmation permit a rotation toward VWAP or another named objective. [VWAP] pp.3–8.

**Not a standalone trade.** A blind ±2-band touch is not the entry. This fade is not Green Bird's separately disclosed VWAP continuation.

**Record before use.** Source VWAP/reset and band settings, band known_at, local touch/absorption, CVD/ladder confirmation, preselected objective and risk.

**Phase 1 observation.** Use the selected deviation and contemporaneous VWAP. Absorption at an unrelated later price does not confirm this touch; a missing reset remains unknown for an author-faithful construction.

**Existing attachments.** [formulas_flow.running_vwap/r_f01_vwap_fade/r_f03_convergence](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-F01/F03 with F02/F06. Exact source reset/deviation and at-band confirmation are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Session VWAP](vwap-session.md) · [VWAP deviation bands](vwap-deviations.md) · [Anchored VWAP](vwap-anchored.md) · [Cumulative volume delta and its source reference](cvd-variants.md) · [DOM at a planned location](dom.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VWAP]: </workspace/sources/documents/discretionary/vwap-lesson-10.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
