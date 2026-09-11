# Gamma-flip reference

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The flip is a source regime/location reference read with current price and the relevant gamma map. The materials use more than one sign/flip description, and a recap records disagreement near it without changing the plan. [GEX] pp.6–7, 13–19; [K18] p.4.

**Not a standalone trade.** A calculated zero of an assumed aggregate gamma curve does not automatically reproduce the proprietary flip or dictate an entry.

**Record before use.** Source flip label/value, product and expiry, snapshot/known_at, sign/model convention, spot relation and uncertainty.

**Phase 1 observation.** Retain the source read or a named scenario; do not combine price-versus-flip and aggregate-sign interpretations opportunistically. The next impulse may require a reread before a new decision.

**Existing attachments.** [family_gex._gex_day/build_gex_table](/workspace/implementation/src/trading_research/research/phase1_live/family_gex.py); [FORMULAS] R-R01. The exact source flip algorithm and consistent dealer-position assumptions are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Source gamma regime](gex-regime.md) · [Native options-chain identity](options-nodes.md) · [Gamma call and put walls](gex-walls-and-max-pain.md) · [Thesis, validity band and death condition](thesis-lifecycle.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
