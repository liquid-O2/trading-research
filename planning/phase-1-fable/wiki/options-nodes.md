# Options nodes (OI / gamma strikes as levels)

## Definition
Strike-level open interest and dealer-gamma estimates from the NDX / NDXP / SPX chains and NQ.OPT, converted to NQ price coordinates and treated as candidate levels `[GEX p.2–5]` `[DRFL L241–252, assistant]`. Measurable with acquired data: OI-by-strike nodes and Greeks reconstructed from the 1-minute NBBO surface. Not measurable: dealer inventory and participant identity `[DRFL L207–224]`, the hidden book, and unpublished node engines (Skylit Heatseeker / Flowseeker / Atlas, Phase 2–3) `[README sources/documents/README.md L27–30]` `[DTM L25]`. Rows for those print `not-measurable` / `deferred` `[BRIEF]`.

## Citations
- Dealer hedging, long / short gamma, gamma flip, GEX as regime filter, strikes as where gamma lives `[GEX p.2 L17–39, p.5 L90–94]`; QQQ / SPY as origin complexes `[GEX p.4 L77]`.
- Data: OPRA NDX / NDXP contracts, EOD, OI, quote-1m dte ≤ 14, trade-quote dte ≤ 7 `[INV L297–380]`; SPX / SPXW `[INV L422–500]`; NQ.OPT definition / OHLCV-1m / statistics / trades `[INV L98–120]`.
- User wants levels from gamma / OI heat maps improved and multi-asset `[DTM L22, L24]`; open interest as the overnight structural prior `[DRFL L37]` (assistant turn, tier 4).

## Faithful object
`value.node.oi.top3`: at 09:25 ET, top 3 OI strikes above and below spot from the NDX + NDXP dte ≤ 14 chains, mapped to NQ by the 09:25 NQ / NDX ratio; levels held for the session.

## Upgrades
- `value.node.gamma.top3`: |gamma × OI| weighting from reconstructed Greeks; dte ≤ 7 vs ≤ 14; NQ.OPT-only variant; QQQ-derived variant (data present `[INV L253]`).
- Zero-gamma flip level as a single row.

## Outcomes
- Grid at node levels (touch / reject / hold / break, time-to-touch) exactly as for value levels; distance from AM extreme to the nearest node (ranked against EV, −0.5, P-zone rows).
- Faithful disagreements: sessions where the top-3 node set differs between OI and gamma weighting.
- `not-measurable` rows: dealer inventory, hidden book, Skylit engines.

## Links
[value-and-profiles](value-and-profiles.md) · [cvd-variants](cvd-variants.md) · [data-coverage](data-coverage.md)
