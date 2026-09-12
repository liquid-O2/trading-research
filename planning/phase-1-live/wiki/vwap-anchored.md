# Anchored VWAP

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The lesson anchors VWAP to a relevant swing, event or weekly/monthly context and uses it as confluence with the current auction read. The anchor must be meaningful before the trade. [VWAP] pp.7–8.

**Not a standalone trade.** An anchor selected after seeing the best reaction is not contemporaneous evidence. Anchored VWAP is not another complete system.

**Record before use.** Anchor event/swing ID, price/time and confirmation known_at, instrument, weighting/reset convention, as_of value and source reason.

**Phase 1 observation.** Distinguish the swing's price time from when that swing became confirmed. Do not backdate a future-confirmed anchor or treat every weekly/monthly reset as the same object.

**Current implementation (2026-09-12).** [O031 contract](../FORMULAS.md#o031) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Derive an anchored VWAP from the selected real anchor parent and every eligible execution/bar; anchor availability and snapshot cutoff both constrain use. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/context_observations.py).

**Evidence limits.** A source anchor needs an identified selected parent; unavailable author selection remains a case record limitation. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Session VWAP](vwap-session.md) · [VWAP deviation bands](vwap-deviations.md) · [Thesis, validity band and death condition](thesis-lifecycle.md) · [Prior defended reaction area](prior-reaction-area.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VWAP]: </workspace/sources/documents/discretionary/vwap-lesson-10.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
