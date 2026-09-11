# Signed volume-by-price profile

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md).

Executed delta by price adds who traded aggressively to where volume was accepted. Weekly/daily delta is used in the larger thesis; current local delta at a range location is a separate snapshot. [K18] p.4; [K2345] pp.4–6; [RD] pp.3–9; [JR] pp.14, 48.

**Not a standalone trade.** A positive/negative weekly total is not a local entry, and a light profile side is not automatically a structural LVN.

**Record before use.** Instrument and aggressor convention, price bins, profile window/as_of, buy/sell volume, signed delta, source node pairing and known_at.

**Phase 1 observation.** Keep price-unit and delta-unit references distinct. A full-current-week or final-RTH delta profile cannot confirm an earlier trade; preserve the source's price/effort response.

**Existing attachments.** [family_tape.build_weekly_delta_table](/workspace/implementation/src/trading_research/research/phase1_live/family_tape.py); [family_value.scan_rth_delta](/workspace/implementation/src/trading_research/research/phase1_live/family_value.py); [formulas_flow.r_f11_delta_lvn](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-F10/F11, R-J16 and P3-08. Causal profile selection is partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Executed aggressor-side trades](aggressor-trades.md) · [Cumulative volume delta and its source reference](cvd-variants.md) · [Low-volume node](lvn.md) · [Confirmed protected high or low](protected-high-low.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[RD]: </workspace/sources/documents/discretionary/reading-delta.pdf>
[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[K2345]: </workspace/sources/documents/discretionary/2345-funded-session.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
