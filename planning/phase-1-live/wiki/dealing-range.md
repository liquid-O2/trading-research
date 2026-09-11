# Source-selected dealing range

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md).

The dealing range is the actual swing/auction band framing the thesis, control and objective. Session examples draw reaction/defense as areas; re-entry is considered only when price returns to the same area and produces fresh evidence. [K18] p.4; [CONT] pp.4–10; [ANAT] pp.7–9; [TRAP] pp.3–4.

**Not a standalone trade.** A future-selected swing box or an arbitrary opening clock box is not the source dealing range. Remaining somewhere nearby is not a defended re-entry.

**Record before use.** Auction/band_id, bounds, rationale/scale, source observation time, thesis side, controlling extreme and known_at.

**Phase 1 observation.** Require the band to be defined before the attempted reaction. Keep microbalance, larger dealing range and prior profile separate; stop-out alone does not redraw the band.

**Existing attachments.** [formulas_flow.r_s07_areas/r_s08_minor_node](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py) and profile ingredients; [FORMULAS] R-S07/S08, R-A16/A17. Stable band identity and source selection are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Auction balance](auction-balance.md) · [Prior defended reaction area](prior-reaction-area.md) · [Fresh defense of a continuation band](defended-band-continuation.md) · [Freshly qualified re-entry](reentry.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[ANAT]: </workspace/sources/documents/discretionary/anatomy-of-a-losing-start.pdf>
[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
