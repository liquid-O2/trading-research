# Anchored VWAP

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The lesson anchors VWAP to a relevant swing, event or weekly/monthly context and uses it as confluence with the current auction read. The anchor must be meaningful before the trade. [VWAP] pp.7–8.

**Not a standalone trade.** An anchor selected after seeing the best reaction is not contemporaneous evidence. Anchored VWAP is not another complete system.

**Record before use.** Anchor event/swing ID, price/time and confirmation known_at, instrument, weighting/reset convention, as_of value and source reason.

**Phase 1 observation.** Distinguish the swing's price time from when that swing became confirmed. Do not backdate a future-confirmed anchor or treat every weekly/monthly reset as the same object.

**Existing attachments.** [formulas_flow.running_vwap](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py) provides cumulative ingredients; [FORMULAS] R-F03/P3-02. Source event/swing anchors and confirmation-time joins are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Session VWAP](vwap-session.md) · [VWAP deviation bands](vwap-deviations.md) · [Thesis, validity band and death condition](thesis-lifecycle.md) · [Prior defended reaction area](prior-reaction-area.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VWAP]: </workspace/sources/documents/discretionary/vwap-lesson-10.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
