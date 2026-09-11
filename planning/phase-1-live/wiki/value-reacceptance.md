# Re-acceptance into value

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md).

When price leaves or opens outside accepted value and then re-enters with acceptance, the directional read can rotate toward another part of that balance. Two-period-inside and general re-entry claims have separate definitions. [AMT1] p.7; [MAMT] pp.12, 18; [AMTL] pp.8–11.

**Not a standalone trade.** One wick inside value does not prove acceptance or an 80% traversal trade. A compiler's 30-minute hold is not a universal source rule.

**Record before use.** Original value/balance ID and bounds, opening/departure side, re-entry time, source acceptance criterion and known_at, selected target and local control.

**Phase 1 observation.** Require the actual original area and completed source acceptance before changing the trade read. Preserve different conditions and target denominators rather than pooling them into a single probability.

**Existing attachments.** [formulas_jumbo.a03_reentry_traverse/a08_reaccept](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [FORMULAS] R-A03/A04/A08. Testing only one value boundary can wrongly count excursions outside the other side as inside. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Profile value area](value-area.md) · [POC failure versus efficient passage](poc-traversal.md) · [Saint's failed auction and return to value](failed-auction-saint.md) · [Source-conditioned reference statistics](reference-statistics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[AMTL]: </workspace/sources/documents/discretionary/amt-on-live-markets.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
