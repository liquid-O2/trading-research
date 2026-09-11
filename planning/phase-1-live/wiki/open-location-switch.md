# Opening location and participation

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Keani — open above value](method-keani-open-above-value.md).

Locate the opening auction against already-known prior value, prior price range and current frozen references. Jumbo's raw examples include continuation outside prior value while still inside the prior price range. Keani separately requires the whole current A period above prior VAH. [TBR] pp.16–24; [JR] pp.33–39, 48–49; [AVG] pp.21–22.

**Not a standalone trade.** Outside both range and value plus high RVOL is one context cell, not the only continuation permission. An opening cell alone supplies no entry.

**Record before use.** Opening price/time, prior profile and range identities, their bounds/known_at, cell label, and RVOL window/available_at if used.

**Phase 1 observation.** An RVOL statistic for 09:30–09:35 is unavailable at 09:30. Keep the source's cell denominator and outcome window; never label Keani from open > future current-day VAH.

**Existing attachments.** [family_open.build_open_table](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); [FORMULAS] R-J06/J21, R-A10 and R-S09. Current final-path direction and future participation inputs are not contemporaneous context. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Profile value area](value-area.md) · [Prior-session auction landmarks](prior-session-reference-levels.md) · [Developing profile snapshot](developing-profile.md) · [Time-price-opportunity profile](tpo-ib-auction.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
