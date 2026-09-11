# Relative-volume context at the open

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The opening-location discussion uses participation to frame continuation versus rotation, alongside prior value/range location and overnight condition. It does not make one high-RVOL cell the only continuation case. [TBR] pp.16–24; [JR] pp.33–39, 48–49.

**Not a standalone trade.** Relative volume is context, not an entry trigger; a first-five-minute measure cannot be known at the cash-open instant.

**Record before use.** Instrument, current measurement window, baseline sessions/time-of-day, volume statistic/ratio, baseline availability and window-end known_at.

**Phase 1 observation.** Keep the stated source cell and named normalization. Do not compare an incomplete current interval with an incompatible full-session baseline or leak 09:30–09:35 volume into a 09:30 decision.

**Existing attachments.** [family_open.build_open_table](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); [FORMULAS] R-J06/J21. Source-exact baseline/threshold and early-decision availability are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Opening location and participation](open-location-switch.md) · [Range width and expectations](range-width-context.md) · [Source clocks and availability](clock-grid-and-bars.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
